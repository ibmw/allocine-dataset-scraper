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


def pytest_addoption(parser):
    """Register custom command line options."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="run real end-to-end integration tests that hit the network",
    )


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as a real end-to-end integration test that hits Allocine.fr"
    )


def pytest_collection_modifyitems(config, items):
    """Modify collected tests to skip e2e tests unless --run-e2e flag is provided."""
    if config.getoption("--run-e2e"):
        # Option is set: do not skip E2E tests
        return

    skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run live network tests")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


@pytest.fixture(autouse=True)
def patch_tests(monkeypatch, request):
    """Patch Allocine scraper class for all tests except E2E.

    Automatically applied fixture that mocks network requests to avoid
    actual web scraping during tests.

    Args:
        monkeypatch: Pytest fixture for modifying objects
        request: Pytest sub-request object
    """
    if "e2e" in request.keywords:
        return

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
    monkeypatch.setattr("time.sleep", lambda *args, **kwargs: None)
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

    parser = BeautifulSoup(resp.content, "html.parser")  # type: ignore
    parser_movie = parser.find("main", {"id": "content-layout"})

    return parser_movie


@pytest.fixture
def bs4_movie_page_exception():
    """Fixture to movie page exception."""
    txt = read_file(str(Path(__file__).parent / "data/movie_exception.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)

    parser = BeautifulSoup(resp.content, "html.parser")  # type: ignore
    parser_movie = parser.find("main", {"id": "content-layout"})

    return parser_movie


@pytest.fixture
def get_dataframe():
    """Fixture to get DataFrame."""
    csv_path = str(Path(__file__).parent / "data/test_dataframe.csv")
    return pd.read_csv(csv_path)
