from pathlib import Path

import pytest

from allocine_dataset_scraper.utils import read_file


def test_read_file():
    test_read = read_file(str(Path(__file__).parent / "data/test_read.txt"))
    assert test_read == "Success"


def test_read_file_nonexistent():
    """Test reading nonexistent file"""
    with pytest.raises(FileNotFoundError):
        read_file("nonexistent_file.txt")


def test_read_file_empty(tmp_path):
    """Test reading empty file"""
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    content = read_file(str(empty_file))
    assert content == ""


def test_read_file_with_different_encodings(tmp_path):
    """Test reading files with different encodings"""
    test_file = tmp_path / "encoded.txt"
    test_content = "Test content with unicode: 你好"

    # Write with utf-8
    test_file.write_text(test_content, encoding="utf-8")
    content = read_file(str(test_file))
    assert content == test_content
