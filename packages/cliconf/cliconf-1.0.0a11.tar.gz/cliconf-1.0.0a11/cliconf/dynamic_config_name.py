from types import FunctionType


def dynamic_model_class_name(func: FunctionType) -> str:
    # Convert the name of the function from snake_case to PascalCase
    func_in_class_style_name = "".join(
        part.title() for part in func.__name__.split("_")
    )
    return f"{func_in_class_style_name}Config"
