from typing import IO, Any, Mapping, Optional, Sequence, Text, Union

from click.testing import CliRunner as ClickCliRunner
from click.testing import Result
from typer.main import Typer

from cliconf.command import get_command


class CLIRunner(ClickCliRunner):
    def invoke(  # type: ignore
        self,
        app: Typer,
        args: Optional[Union[str, Sequence[str]]] = None,
        input: Optional[Union[bytes, Text, IO[Any]]] = None,
        env: Optional[Mapping[str, str]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result:
        use_cli = get_command(app)
        return super().invoke(
            use_cli,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )
