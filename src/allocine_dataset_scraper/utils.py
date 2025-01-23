from pathlib import Path
from typing import Union


def read_file(filepath: Union[str, Path]) -> str:
    """Read a file and return its content.

    Opens and reads a text file using UTF-8 encoding. Handles both string
    and Path-like objects for the filepath.

    Args:
        filepath: Path to the file to read, can be string or Path object.

    Returns:
        The content of the file as a string.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.
        IOError: If there are other IO-related errors.

    Example:
        >>> content = read_file("data/example.txt")
        >>> print(content)
        'File contents...'
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
