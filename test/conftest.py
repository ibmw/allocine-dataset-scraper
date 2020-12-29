from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from requests.models import Response

from allocine_dataset_scraper.utils import read_file


@pytest.fixture
def response_page():
    txt = read_file(str(Path(__file__).parent / "data/page.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)
    return resp


@pytest.fixture
def response_movie():
    txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)
    return resp


@pytest.fixture
def bs4_movie_page():
    txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
    resp = Response()
    resp.status_code = 200
    resp._content = str.encode(txt)

    parser = BeautifulSoup(resp.content, "html.parser")
    parser_movie = parser.find("main", {"id": "content-layout"})

    return parser_movie
