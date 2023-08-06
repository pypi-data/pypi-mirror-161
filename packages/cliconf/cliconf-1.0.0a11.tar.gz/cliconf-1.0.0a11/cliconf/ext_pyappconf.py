from pathlib import Path
from types import FunctionType
from typing import Optional, Type

from pyappconf import AppConfig, BaseConfig, ConfigFormats
from pydantic import Extra

from cliconf.dynamic_config_name import dynamic_model_class_name


def create_cli_base_config_class(
    base_cls: Type[BaseConfig], settings: Optional[AppConfig] = None
) -> Type[BaseConfig]:
    settings = settings or base_cls._settings
    prefix = _create_default_env_prefix(settings)

    class CLIBaseConfig(base_cls):  # type: ignore
        class Config:
            env_prefix = prefix
            extra = Extra.ignore

    return CLIBaseConfig


class CLIAppConfig(AppConfig):
    """
    Overrides some of the default settings for pyappconf to be more reasonable
    for what users would typically want to use in a CLI application.

    - Updates default folder to be the current directory
    - Outputs stub file for Python config format
    """

    def __init__(self, **kwargs):
        if "custom_config_folder" not in kwargs:
            kwargs["custom_config_folder"] = Path(".")
        if "py_config_generate_model_class_in_stub" not in kwargs:
            kwargs["py_config_generate_model_class_in_stub"] = True
        super().__init__(**kwargs)


def save_model(model: BaseConfig, func: FunctionType) -> None:
    if model.settings.default_format != ConfigFormats.PY:
        # Custom handling is only needed for Python config format
        # Other formats, just let pyappconf handle it
        model.save()
        return

    # Python config format
    # For .py file, add the dynamic config import to get the model class from the
    # command function.
    # For .pyi file, output as-is as it will have the dynamic config class defined statically
    if model.settings.py_config_create_stub:
        file_path = model.settings.config_location.with_suffix(".pyi")
        model.to_py_config_stub(
            file_path, py_config_stub_kwargs=dict(generate_model_class=True)
        )
    settings_with_dynamic_import = _add_dynamic_config_import_to_settings(
        model.settings, func
    )
    temp_model = model.copy(update=dict(settings=settings_with_dynamic_import))
    temp_model.to_py_config(model.settings.config_location, include_stub_file=False)


def _create_default_env_prefix(settings: AppConfig) -> str:
    return settings.app_name.replace("-", "_").replace(" ", "_").upper() + "_"


def _add_dynamic_config_import_to_settings(
    pyappconf_settings: AppConfig, func: FunctionType
) -> AppConfig:
    model_class_name = dynamic_model_class_name(func)
    py_config_dynamic_config_import = f"{model_class_name} = {func.__name__}.model_cls"
    if pyappconf_settings.py_config_imports is None:
        new_py_config_imports = [py_config_dynamic_config_import]
    else:
        new_py_config_imports = [
            *pyappconf_settings.py_config_imports,
            py_config_dynamic_config_import,
        ]
    return pyappconf_settings.copy(py_config_imports=new_py_config_imports)
