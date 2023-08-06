from types import FunctionType
from typing import Any

from cliconf.ext_inspect import get_function_args, get_function_params


def execute_cliconf_func_as_python_func(
    func: FunctionType, model_is_injected: bool, *args, **kwargs
) -> Any:
    """
    Execute a cliconf function as a normal python function.

    Unwraps any typer options and arguments that may be used as defaults.
    """
    arg_spec = get_function_args(func)
    user_passed_arg_names = [arg_name for arg, arg_name in zip(args, arg_spec)]
    params = get_function_params(func, model_is_injected=model_is_injected)
    defaults_from_func = {name: value for name, (_, value) in params.items()}
    defaults_without_args = {
        key: value
        for key, value in defaults_from_func.items()
        if key not in user_passed_arg_names
    }
    new_kwargs = {**defaults_without_args, **kwargs}
    return func(*args, **new_kwargs)
