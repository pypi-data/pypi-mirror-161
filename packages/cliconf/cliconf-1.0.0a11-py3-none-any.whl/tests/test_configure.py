from typing import Callable, Optional

import pytest
import typer
from pydantic import ValidationError

from cliconf import CLIConf, CLIConfSettings, configure
from tests.fixtures.app_settings import SETTINGS_TWO_PY
from tests.fixtures.cliconfs import default_func_for_single_command_py


def test_configure_creates_dynamic_model():
    cliconf_settings = CLIConfSettings(make_fields_optional=False)

    @configure(SETTINGS_TWO_PY, cliconf_settings=cliconf_settings)
    def my_cli_func(
        a: int,
        b: str = "b",
        c: Optional[str] = None,
        *,
        d: float,
        e: Optional[int],
        f: str = "f",
        g: Optional[str] = None
    ):
        pass

    model_cls = my_cli_func.model_cls
    model = model_cls(a=10, d=30, e=40)
    assert model.a == 10
    assert model.b == "b"
    assert model.c is None
    assert model.d == 30
    assert model.e == 40
    assert model.f == "f"
    assert model.g is None

    # Fields are required, so shouldn't be able to construct without args
    with pytest.raises(ValidationError):
        model_cls()


def test_configure_creates_dynamic_model_with_optional_fields():
    @configure(SETTINGS_TWO_PY)
    def my_cli_func(
        a: int,
        b: str = "b",
        c: Optional[str] = None,
        *,
        d: float,
        e: Optional[int],
        f: str = "f",
        g: Optional[str] = None
    ):
        pass

    model_cls = my_cli_func.model_cls
    model = model_cls(a=10, d=30, e=40)
    assert model.a == 10
    assert model.b == "b"
    assert model.c is None
    assert model.d == 30
    assert model.e == 40
    assert model.f == "f"
    assert model.g is None

    # Fields are not requires, so should be able to construct without args
    empty = model_cls()
    assert empty.a is None
    assert empty.b == "b"
    assert empty.c is None
    assert empty.d is None
    assert empty.e is None
    assert empty.f == "f"
    assert empty.g is None


def test_configure_creates_dynamic_model_with_typer():
    cliconf_instance = CLIConf(name="dynamic_model_with_typer")

    @cliconf_instance.command()
    @configure(pyappconf_settings=SETTINGS_TWO_PY)
    def my_cli_func(
        a: str,
        b: int = typer.Argument(..., help="b help"),
        c: float = typer.Option(3.2, help="c help"),
        d: Callable[[float], None] = default_func_for_single_command_py,
    ):
        print(a, b, c, d(c))

    model_cls = my_cli_func.model_cls
    model = model_cls(a="a", b=1000)
    assert model.a == "a"
    assert model.b == 1000
    assert model.c == 3.2
    assert model.d == default_func_for_single_command_py
