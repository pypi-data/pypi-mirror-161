from cliconf.configure import model_as_dict
from tests.fixtures.cliconfs import (
    my_cli_func_one_injected_model_yaml,
    my_cli_func_one_yaml,
)


def test_cliconf_decorated_executes_as_a_normal_python_function():
    result = my_cli_func_one_yaml("a", 2)
    assert result == ("a", 2, 3.2)


def test_cliconf_decorated_with_inject_model_executes_as_a_normal_python_function():
    mod = my_cli_func_one_injected_model_yaml.model_cls(a="a", b=2)
    result = my_cli_func_one_injected_model_yaml(mod, **model_as_dict(mod))
    assert result == mod
