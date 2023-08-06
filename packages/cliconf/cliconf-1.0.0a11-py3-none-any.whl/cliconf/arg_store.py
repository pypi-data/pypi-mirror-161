from typing import Any, Dict, List, Sequence

from pydantic import BaseModel, Field


class CommandArgs(BaseModel):
    prog_name: str
    passed_args: List[Any]
    params: Dict[str, Any]


class ArgumentStore(BaseModel):
    """
    This class is used to store the arguments that are passed to the CLI.
    """

    commands: Dict[str, CommandArgs] = Field(default_factory=dict)

    def add_command(self, prog_name: str, args: Sequence[str], params: Dict[str, Any]):
        self.commands[prog_name] = CommandArgs(
            prog_name=prog_name, passed_args=list(args), params=params
        )

    def remove_command(self, prog_name: str):
        del self.commands[prog_name]

    def args_are_stored_for(self, prog_name: str) -> bool:
        return prog_name in self.commands

    def __getitem__(self, item):
        return self.commands[item]


ARGS_STORE = ArgumentStore()
