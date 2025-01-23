"""Tests for the utils module.

This module contains tests for utility functions in allocine_dataset_scraper.utils.
Tests cover file reading functionality with various scenarios including error cases.
"""

from pathlib import Path

import pytest

from allocine_dataset_scraper.utils import read_file


def test_read_file():
    """Test successful file reading with valid UTF-8 content."""
    test_read = read_file(str(Path(__file__).parent / "data/test_read.txt"))
    assert test_read == "Success"


def test_read_file_nonexistent():
    """Test error handling when trying to read a nonexistent file.

    Should raise FileNotFoundError when file doesn't exist.
    """
    with pytest.raises(FileNotFoundError):
        read_file("nonexistent_file.txt")


def test_read_file_empty(tmp_path):
    """Test reading an empty file.

    Verifies that reading an empty file returns an empty string.

    Args:
        tmp_path: Pytest fixture providing temporary directory path.
    """
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    content = read_file(str(empty_file))
    assert content == ""


def test_read_file_with_different_encodings(tmp_path):
    """Test reading files with different character encodings.

    Verifies that UTF-8 encoded content including unicode characters
    is read correctly.

    Args:
        tmp_path: Pytest fixture providing temporary directory path.
    """
    test_file = tmp_path / "encoded.txt"
    test_content = "Test content with unicode: 你好"

    # Write with utf-8
    test_file.write_text(test_content, encoding="utf-8")
    content = read_file(str(test_file))
    assert content == test_content
