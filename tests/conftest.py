from pathlib import Path

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from requests.models import Response

from allocine_dataset_scraper.utils import read_file


@pytest.fixture(autouse=True)
def patch_tests(monkeypatch):
    """Patch Allocine class for all tests."""

    def response_page_same_movie_id(*arg):
        txt = read_file(str(Path(__file__).parent / "data/page_same_movie_id.txt"))
        resp = Response()
        resp.status_code = 200
        resp._content = str.encode(txt)
        return resp

    def response_unique_movie(*arg):
        txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
        resp = Response()
        resp.status_code = 200
        resp._content = str.encode(txt)
        return resp

    monkeypatch.delattr("requests.sessions.Session.request")
    monkeypatch.setattr(
        "allocine_dataset_scraper.scraper.AllocineScraper._get_page",
        response_page_same_movie_id,
    )
    monkeypatch.setattr(
        "allocine_dataset_scraper.scraper.AllocineScraper._get_movie",
        response_unique_movie,
    )


@pytest.fixture
def response_page():
    """Fixture to response page."""
    txt = read_file(str(Path(__file__).parent / "data/page.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)
    return resp


@pytest.fixture
def response_movie():
    """Fixture to response movie."""
    txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)
    return resp


@pytest.fixture
def bs4_movie_page():
    """Fixture to movie page."""
    txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)

    parser = BeautifulSoup(resp.content, "html.parser")
    parser_movie = parser.find("main", {"id": "content-layout"})

    return parser_movie


@pytest.fixture
def bs4_movie_page_exception():
    """Fixture to movie page exception."""
    txt = read_file(str(Path(__file__).parent / "data/movie_exception.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)

    parser = BeautifulSoup(resp.content, "html.parser")
    parser_movie = parser.find("main", {"id": "content-layout"})

    return parser_movie


@pytest.fixture
def get_dataframe():
    """Fixture to get DataFrame."""
    csv_path = str(Path(__file__).parent / "data/test_dataframe.csv")
    return pd.read_csv(csv_path)
