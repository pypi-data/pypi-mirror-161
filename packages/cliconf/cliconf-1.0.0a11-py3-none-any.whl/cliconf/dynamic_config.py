import warnings
from types import FunctionType
from typing import Any, Dict, Optional, Sequence, Type, no_type_check

from pyappconf import AppConfig, BaseConfig
from pydantic import create_model

from cliconf.arg_store import ARGS_STORE
from cliconf.command_name import get_command_name
from cliconf.dynamic_config_name import dynamic_model_class_name
from cliconf.ext_inspect import get_function_params
from cliconf.ext_pyappconf import create_cli_base_config_class


@no_type_check
def create_dynamic_config_class_from_function(
    func: FunctionType,
    settings: AppConfig,
    base_cls: Optional[Type[BaseConfig]] = None,
    model_is_injected: bool = False,
    make_optional: bool = True,
) -> Type[BaseConfig]:
    """
    Create a BaseConfig class from a function.
    """
    base_cls = base_cls or create_cli_base_config_class(BaseConfig, settings)
    params = get_function_params(
        func, make_optional=make_optional, model_is_injected=model_is_injected
    )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            action="ignore",
            category=RuntimeWarning,
            message='fields may not start with an underscore, ignoring "_settings"',
        )

        model_cls = create_model(
            dynamic_model_class_name(func),
            __base__=base_cls,
            **params,
            settings=settings,
            _settings=settings,
        )
    return model_cls


def filter_func_args_and_kwargs_to_get_user_passed_data(
    func: FunctionType,
    func_args: Sequence[Any],
    func_kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    args_kwargs = dict(zip(func.__code__.co_varnames[1:], func_args))
    args_kwargs.update(func_kwargs)
    # Get user passed args from command line via args store
    args_store = ARGS_STORE[get_command_name(func.__name__)]
    user_kwargs = args_store.params
    return user_kwargs
