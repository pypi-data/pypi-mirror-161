import os
import sys
import types
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union, cast

import click
from click.exceptions import Exit
from click.utils import _expand_args
from pyappconf import AppConfig, BaseConfig
from typer import Typer
from typer.main import get_command as typer_get_command
from typing_extensions import TypeGuard

from cliconf.arg_store import ARGS_STORE
from cliconf.command_name import get_command_name
from cliconf.logger import log
from cliconf.options import create_generate_config_option
from cliconf.settings import CLIConfSettings


class CLIConfCallable:
    pyappconf_settings: AppConfig
    cliconf_settings: CLIConfSettings
    model_cls: Type[BaseConfig]

    def __call__(self, *args, **kwargs):
        ...


def get_command(typer_instance: Typer) -> click.Command:
    """
    Extends typer's get_command function to modify the created click.Command instance
    to inspect the passed arguments and load from config.
    """
    command = cast(Union[click.Command, click.Group], typer_get_command(typer_instance))

    if _is_command_group(command):
        for subcommand in command.commands.values():
            _customize_command(subcommand)
        # Override the main function to load config
        command.main = types.MethodType(_cli_conf_main_multi_command, command)
        return command

    # Single command
    _customize_command(command)
    # Override the main function to load config
    command.main = types.MethodType(_cli_conf_main_single_command, command)

    return command


def _is_command_group(
    command: Union[click.Command, click.Group]
) -> TypeGuard[click.Group]:
    return hasattr(command, "commands")


def _is_cliconf_command(command: click.Command) -> bool:
    return hasattr(command.callback, "cliconf_settings")


def _is_cliconf_callable(fn: Callable) -> TypeGuard[CLIConfCallable]:
    return (
        hasattr(fn, "cliconf_settings")
        and hasattr(fn, "pyappconf_settings")
        and hasattr(fn, "model_cls")
        and callable(fn)
    )


def _customize_command(
    command: click.Command,
):
    if not _is_cliconf_command(command):
        log.debug(f"Not a cliconf command, skipping customization: {command.name}")
        return

    callback = command.callback

    if not _is_cliconf_callable(callback):
        return

    pyappconf_settings: AppConfig = callback.pyappconf_settings
    cliconf_settings: CLIConfSettings = callback.cliconf_settings
    model_cls: Type[BaseConfig] = callback.model_cls
    command.params.append(
        create_generate_config_option(
            pyappconf_settings.supported_formats,
            pyappconf_settings.default_format,
            model_cls,
            callback,  # type: ignore
            cliconf_settings.generate_config_option_name,
        )
    )


def _cli_conf_main_single_command(
    self: click.Command,
    args: Optional[Sequence[str]] = None,
    prog_name: Optional[str] = None,
    complete_var: Optional[str] = None,
    standalone_mode: bool = True,
    windows_expand_args: bool = True,
    **extra: Any,
):
    """
    A modified version of click.Command's main function that records which arguments were passed
    """
    use_args = _get_arguments_from_passed_or_argv(args)
    func_name = prog_name or get_command_name(self.callback.__name__)  # type: ignore
    params = _create_passed_param_dict_from_command(self, func_name, use_args)
    # It seems typer always provides prog_name, but for safety calculate a fallback
    ARGS_STORE.add_command(func_name, use_args, params)
    return super(type(self), self).main(  # type: ignore
        args, func_name, complete_var, standalone_mode, windows_expand_args, **extra
    )


def _cli_conf_main_multi_command(
    self: click.Group,
    args: Optional[Sequence[str]] = None,
    prog_name: Optional[str] = None,
    complete_var: Optional[str] = None,
    standalone_mode: bool = True,
    windows_expand_args: bool = True,
    **extra: Any,
):
    """
    A modified version of click.Group's main function that records which arguments were passed
    """

    def run_original():
        return super(type(self), self).main(  # type: ignore
            args, prog_name, complete_var, standalone_mode, windows_expand_args, **extra
        )

    use_args = _get_arguments_from_passed_or_argv(args)
    if len(use_args) == 0:
        # No arguments passed. No need to configure arguments
        return run_original()
    sub_command_name, sub_command_args = use_args[0], use_args[1:]
    sub_command = self.commands.get(sub_command_name)
    if sub_command is None:
        # First argument did not match a subcommand. Must be requesting help, no need to configure arguments
        return run_original()
    func_name = get_command_name(sub_command.callback.__name__)  # type: ignore
    params = _create_passed_param_dict_from_command(
        sub_command, func_name, sub_command_args
    )
    ARGS_STORE.add_command(func_name, sub_command_args, params)
    return super(type(self), self).main(  # type: ignore
        args, func_name, complete_var, standalone_mode, windows_expand_args, **extra
    )


def _create_passed_param_dict_from_command(
    command: click.Command,
    prog_name: str,
    args: Sequence[str],
) -> Dict[str, Any]:
    # Click's Command.make_context will raise Exit if the arguments are invalid
    # Now we are parsing the arguments before click does, so we must handle the Exit.
    # Here we just exit with the exit code, just as Click does in standalone_mode
    try:
        context = command.make_context(prog_name, [*args])
    except Exit as e:
        sys.exit(e.exit_code)
    parser = command.make_parser(context)
    opts, _, param_order = parser.parse_args(args=[*args])
    # Reorder the opts dict to match the order of the command's params
    out_opts: Dict[str, Any] = {}
    for argument in param_order:
        if argument.name in opts:
            out_opts[argument.name] = opts[argument.name]
    return out_opts


def _get_arguments_from_passed_or_argv(
    args: Optional[Sequence[str]] = None,
) -> List[str]:
    """
    Returns the arguments passed to the command.

    Note: Mostly adapted from click.BaseCommand.main
    :param args:
    :return:
    """
    if args is not None:
        return list(args)

    args = sys.argv[1:]

    if os.name == "nt":
        # It's not ideal to be using a private method, but want to make sure
        # it works exactly the same for param extraction as how Click handles it
        return _expand_args(args)
    return args
