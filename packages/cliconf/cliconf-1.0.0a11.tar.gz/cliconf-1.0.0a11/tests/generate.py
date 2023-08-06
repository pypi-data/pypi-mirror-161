from typing import Callable, Optional

from pyappconf import BaseConfig

from cliconf.ext_pyappconf import save_model
from tests.config import OVERRIDES_CONFIGS_DIR, PLAIN_CONFIGS_DIR
from tests.fixtures.app_settings import (
    SETTINGS_NESTED_CONFIG_YAML,
    SETTINGS_ONE_YAML,
    SETTINGS_TWO_PY,
)
from tests.fixtures.cliconfs import (
    NestedConfig,
    default_func_for_single_command_py,
    my_cli_func_two_py,
)


class ConfigOne(BaseConfig):
    a: str
    b: int
    c: float = 3.2

    _settings = SETTINGS_ONE_YAML


class ConfigOneOptional(ConfigOne):
    a: Optional[str] = None
    b: Optional[int] = None


def generate_config_one():
    settings = ConfigOne._settings.copy(custom_config_folder=PLAIN_CONFIGS_DIR)
    ConfigOneOptional(settings=settings).save()


def generate_config_one_with_overrides():
    ConfigOne(a="a from config", b=1000, c=45.6).save()


def custom_d_func(c: float) -> str:
    return f"custom {c}"


def generate_config_two_py():
    ConfigTwo = my_cli_func_two_py.model_cls
    settings = ConfigTwo._settings.copy(custom_config_folder=PLAIN_CONFIGS_DIR)
    obj = ConfigTwo(settings=settings)
    save_model(obj, my_cli_func_two_py)


def generate_config_two_py_with_overrides():
    ConfigTwo = my_cli_func_two_py.model_cls
    current_imports = ConfigTwo._settings.py_config_imports
    new_imports = [*current_imports, "from tests.generate import custom_d_func"]
    settings = ConfigTwo._settings.copy(
        py_config_imports=new_imports, custom_config_folder=OVERRIDES_CONFIGS_DIR
    )
    obj = ConfigTwo(c=123.4, d=custom_d_func, settings=settings)
    save_model(obj, my_cli_func_two_py)


class ConfigWithNestingOptional(BaseConfig):
    a: Optional[str] = None
    b: Optional[NestedConfig] = None

    _settings = SETTINGS_NESTED_CONFIG_YAML


def generate_config_with_nesting():
    settings = ConfigWithNestingOptional._settings.copy(
        custom_config_folder=PLAIN_CONFIGS_DIR
    )
    ConfigWithNestingOptional(settings=settings).save()


if __name__ == "__main__":
    generate_config_one()
    generate_config_one_with_overrides()
    generate_config_two_py()
    generate_config_two_py_with_overrides()
    generate_config_with_nesting()
