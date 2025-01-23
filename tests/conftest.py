"""Test fixtures and configuration for Allocine scraper tests.

This module provides pytest fixtures used across multiple test modules.
Includes fixtures for mocked responses, sample data, and test configurations.
"""

from pathlib import Path

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from requests import Response

from allocine_dataset_scraper.utils import read_file


@pytest.fixture(autouse=True)
def patch_tests(monkeypatch):
    """Patch Allocine scraper class for all tests.

    Automatically applied fixture that mocks network requests to avoid
    actual web scraping during tests.

    Args:
        monkeypatch: Pytest fixture for modifying objects
    """

    def response_page_same_movie_id(*arg):
        """Create mock response for movie listing page."""
        txt = read_file(str(Path(__file__).parent / "data/page_same_movie_id.txt"))
        resp = Response()
        resp.status_code = 200
        resp._content = str.encode(txt)
        return resp

    def response_unique_movie(*arg):
        """Create mock response for individual movie page."""
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
    """Provide mock response for a movie listing page.

    Returns:
        Response: Mocked requests.Response object containing sample page HTML
    """
    txt = read_file(str(Path(__file__).parent / "data/page.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)
    return resp


@pytest.fixture
def response_movie():
    """Provide mock response for an individual movie page.

    Returns:
        Response: Mocked requests.Response object containing sample movie HTML
    """
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
