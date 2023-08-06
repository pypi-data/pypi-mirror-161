from typer.main import get_command_name as typer_command_name


def get_command_name(name: str) -> str:
    return typer_command_name(name.strip())
