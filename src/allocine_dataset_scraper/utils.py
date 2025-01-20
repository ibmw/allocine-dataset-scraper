from pathlib import Path
from typing import Union


def read_file(filepath: Union[str, Path]) -> str:
    """Read a file and return its content.

    Args:
        filepath: Path to the file to read

    Returns:
        The content of the file as a string
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
