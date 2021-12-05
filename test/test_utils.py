from pathlib import Path

from allocine_dataset_scraper.utils import read_file


def test_read_file():
    test_read = read_file(str(Path(__file__).parent / "data/test_read.txt"))
    assert test_read == "Success"
