import re
import shlex
from pathlib import Path
from typing import Sequence, Tuple

from click.testing import Result

from cliconf.main import CLIConf
from cliconf.testing import CLIRunner
from tests import ext_click
from tests.config import CONFIGS_DIR, NESTED_OVERRIDES_CONFIGS_DIR, PLAIN_CONFIGS_DIR
from tests.dirutils import change_directory_to
from tests.fixtures.cliconfs import (
    multi_command_shared_config_yaml_cliconf,
    single_command_injected_model_yaml_cliconf,
    single_command_multi_format_cliconf,
    single_command_nested_config_yaml_cliconf,
    single_command_py_cliconf,
    single_command_py_cliconf_in_temp_dir,
    single_command_recursive_yaml_cliconf,
    single_command_yaml_cliconf,
    single_command_yaml_cliconf_in_temp_dir,
)

runner = CLIRunner()

ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)


def strip_all_ansi(string: str) -> str:
    return ansi_escape.sub("", string)


class CLIRunnerException(Exception):
    pass


def run(instance: CLIConf, args: Sequence[str]) -> Result:
    result = runner.invoke(instance, args)
    if result.exit_code != 0:
        output = ext_click.result_to_message(result)
        command = shlex.join([instance.info.name, *args])
        raise CLIRunnerException(
            f"{command} with exited with code {result.exit_code}.\n{output}"
        )
    return result


def test_single_command_cliconf_reads_from_yaml_config():
    result = run(single_command_yaml_cliconf, ["a", "2"])
    assert result.stdout == "a 2 45.6\n"


def test_recursive_single_command_cliconf_reads_recursively_from_yaml_config():
    with change_directory_to(NESTED_OVERRIDES_CONFIGS_DIR):
        result = run(single_command_recursive_yaml_cliconf, ["a", "2"])
        assert result.stdout == "a 2 45.6\n"


def test_recursive_single_command_cliconf_loads_default_config_when_none_found():
    with change_directory_to(CONFIGS_DIR):
        result = run(single_command_recursive_yaml_cliconf, ["a", "2"])
        assert result.stdout == "a 2 3.2\n"


def test_single_command_multi_format_cliconf_reads_from_yaml_config():
    result = run(single_command_multi_format_cliconf, ["a", "2"])
    assert result.stdout == "a 2 45.6\n"


def test_single_command_cliconf_reads_nested_config_from_yaml_config():
    result = run(single_command_nested_config_yaml_cliconf, ["a"])
    assert result.stdout == "a na='abc' nb=123.0\n"


def test_multi_command_shared_config_cliconf_reads_from_yaml_config():
    result_one = run(multi_command_shared_config_yaml_cliconf, ["one", "a", "2"])
    result_two = run(multi_command_shared_config_yaml_cliconf, ["two", "a", "2"])
    assert result_one.stdout == "a 2 45.6\n"
    assert result_two.stdout == "13.2 2 a\n"


def _has_line_containing_each(text: str, *segments: Sequence[str]) -> bool:
    lines = strip_all_ansi(text).splitlines()
    for line in lines:
        match = True
        for segment in segments:
            if segment not in line:
                match = False
                continue

        if match:
            # Must have all segments in text
            return True
    return False


def test_single_command_cliconf_prints_help():

    result = run(single_command_yaml_cliconf, ["--help"])

    def has(*segments: Sequence[str]) -> bool:
        found = _has_line_containing_each(result.stdout, *segments)
        if not found:
            print(segments, "not found in")
            print(result.stdout)
        return found

    assert has("a", "TEXT", "[default: None]", "[required]")
    assert has("b", "INTEGER", "b help", "[default: None]", "[required]")
    assert has("--c", "FLOAT")
    assert has("c help", "[default: 3.2]")
    assert has("--help")


def test_multi_command_cliconf_prints_help():

    result = run(multi_command_shared_config_yaml_cliconf, ["--help"])

    def has(*segments: Sequence[str]) -> bool:
        found = _has_line_containing_each(result.stdout, *segments)
        if not found:
            print(segments, "not found in")
            print(result.stdout)
        return found

    assert has("one", "one help")
    assert has("two", "two help")


def test_single_command_cliconf_reads_py_config():
    result = run(single_command_py_cliconf, ["a", "2"])
    assert result.stdout == "a 2 123.4 custom 123.4\n"


def test_single_command_cliconf_reads_from_environment_over_config(monkeypatch):
    monkeypatch.setenv("MYAPP_C", "98.3")
    result = run(single_command_yaml_cliconf, ["a", "2"])
    assert result.stdout == "a 2 98.3\n"


def test_single_command_cliconf_writes_config_file_py(
    single_command_py_cliconf_in_temp_dir: Tuple[CLIConf, Path]
):
    cliconf_obj, temp_path = single_command_py_cliconf_in_temp_dir
    result = run(cliconf_obj, ["--config-gen"])
    assert "Saving config to" in result.stdout

    # Check that generated files are the same as in input_files
    for file_name in ("two.py", "two.pyi"):
        input_file = PLAIN_CONFIGS_DIR / file_name
        output_file = temp_path / file_name
        assert input_file.read_text() == output_file.read_text()


def test_single_command_cliconf_writes_config_file_yaml(
    single_command_yaml_cliconf_in_temp_dir: Tuple[CLIConf, Path]
):
    cliconf_obj, temp_path = single_command_yaml_cliconf_in_temp_dir
    result = run(cliconf_obj, ["--config-gen"])
    assert "Saving config to" in result.stdout

    # Check that generated files are the same as in input_files
    file_name = "one.yaml"
    input_file = PLAIN_CONFIGS_DIR / file_name
    output_file = temp_path / file_name
    assert input_file.read_text() == output_file.read_text()


def test_cliconf_injects_model():
    result = run(single_command_injected_model_yaml_cliconf, ["a", "2"])
    assert "a 2 45.6" in result.stdout
    assert "a='a' b=2 c=45.6" in result.stdout
