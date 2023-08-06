from typing import Optional, Type

from pyappconf import BaseConfig
from pydantic import BaseModel


class CLIConfSettings(BaseModel):
    """
    Settings for the CLI configuration that are specific to cliconf
    """

    generate_config_option_name: str = "config-gen"
    base_cls: Optional[Type[BaseConfig]] = None
    make_fields_optional: bool = True
    recursive_loading: bool = False
    inject_model: bool = False


DEFAULT_SETTINGS = CLIConfSettings()
