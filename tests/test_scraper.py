"""Tests for the Allocine scraper module.

This module contains comprehensive tests for the AllocineScraper class,
covering movie data extraction, parsing, error handling, and file operations.
Tests use mocked responses to avoid actual web requests.
"""

from pathlib import Path

import dateparser
import pandas as pd
import pytest
from pydantic import ValidationError

from allocine_dataset_scraper.config import ScraperConfig
from allocine_dataset_scraper.scraper import AllocineScraper


def test__get_page():
    """Test page request functionality.

    Verifies that the page request returns a valid response with 200 status code.
    Uses mocked response to avoid actual network requests.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    resp = scraper._get_page(1)
    assert resp.status_code == 200


def test__get_movie():
    """Test individual movie page request functionality.

    Verifies that the movie page request returns a valid response with 200 status code.
    Uses mocked response to avoid actual network requests.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    resp = scraper._get_movie("dummy")
    assert resp.status_code == 200


def test__randomize_waiting_time():
    """Test random wait time generation.

    Verifies that generated wait times fall within the configured range.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    pause_range = range(*config.pause_scraping)
    assert scraper._randomize_waiting_time() in pause_range


def test__create_directory_if_not_exist(tmp_path):
    """Test directory creation functionality.

    Verifies that directories are created when they don't exist and
    no errors occur when they already exist.

    Args:
        tmp_path: Pytest fixture providing temporary directory path.
    """
    path_dir = str(tmp_path / "data")
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    scraper._create_directory_if_not_exist(path_dir)
    assert len(list(tmp_path.iterdir())) == 1
    scraper._create_directory_if_not_exist(path_dir)
    assert len(list(tmp_path.iterdir())) == 1


def test__parse_page(response_page):
    """Test movie listing page parsing.

    Verifies that movie URLs are correctly extracted from the listing page.

    Args:
        response_page: Fixture providing mock page response.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    urls = scraper._parse_page(response_page)
    urls_expected = [
        "/film/fichefilm_gen_cfilm=251354.html",
        "/film/fichefilm_gen_cfilm=229831.html",
        "/film/fichefilm_gen_cfilm=275220.html",
        "/film/fichefilm_gen_cfilm=207825.html",
        "/film/fichefilm_gen_cfilm=251315.html",
        "/film/fichefilm_gen_cfilm=3393.html",
        "/film/fichefilm_gen_cfilm=256588.html",
        "/film/fichefilm_gen_cfilm=29718.html",
        "/film/fichefilm_gen_cfilm=249264.html",
        "/film/fichefilm_gen_cfilm=130203.html",
        "/film/fichefilm_gen_cfilm=124375.html",
        "/film/fichefilm_gen_cfilm=60164.html",
        "/film/fichefilm_gen_cfilm=338.html",
        "/film/fichefilm_gen_cfilm=283046.html",
        "/film/fichefilm_gen_cfilm=1532.html",
    ]
    assert urls == urls_expected


def test__get_movie_id(bs4_movie_page):
    """Test movie ID extraction from page.

    Verifies that the movie ID is correctly extracted from the HTML content.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_id(bs4_movie_page)
    val_expected = 275220
    assert val == val_expected


def test__get_movie_title(bs4_movie_page):
    """Test movie title extraction from page.

    Verifies that the movie title is correctly extracted and cleaned
    from the HTML content.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_title(bs4_movie_page)
    val_expected = "Minuit dans l'univers"
    assert val == val_expected


def test__get_movie_release_date(bs4_movie_page):
    """Test movie release date extraction and parsing.

    Verifies that the release date is correctly extracted and parsed
    into a datetime object.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_release_date(bs4_movie_page)
    val_expected = dateparser.parse("2020-12-23", date_formats=["%d %B %Y"])
    assert val == val_expected


def test__get_movie_duration(bs4_movie_page):
    """Test movie duration extraction and conversion.

    Verifies that the duration is correctly extracted and converted
    to minutes.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_duration(bs4_movie_page)
    val_expected = 122
    assert val == val_expected


def test__get_movie_genres(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie genres"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_genres(bs4_movie_page)
    val_expected = "Drame, Science Fiction"
    assert val == val_expected
    val = scraper._get_movie_genres(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_directors(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie directors"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_directors(bs4_movie_page)
    val_expected = "George Clooney"
    assert val == val_expected
    val = scraper._get_movie_directors(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_actors(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie actors"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_actors(bs4_movie_page)
    val_expected = "George Clooney, Felicity Jones, David Oyelowo"
    assert val == val_expected
    val = scraper._get_movie_actors(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_nationality(bs4_movie_page):
    """Test the page parser to retrieve movie nationality"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_nationality(bs4_movie_page)
    val_expected = "U.S.A."
    assert val == val_expected


def test__get_movie_press_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie press rating"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_press_rating(bs4_movie_page)
    val_expected = 2.5
    assert val == val_expected
    val = scraper._get_movie_press_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_number_of_press_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test press rating count extraction.

    Verifies that the number of press ratings is correctly extracted,
    and handles cases where ratings are missing.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
        bs4_movie_page_exception: Fixture providing page content with missing ratings.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_number_of_press_rating(bs4_movie_page)
    val_expected = 21.0
    assert val == val_expected
    val = scraper._get_movie_number_of_press_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_spec_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test spectator rating extraction.

    Verifies that the spectator rating is correctly extracted and converted
    to float, and handles cases where ratings are missing.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
        bs4_movie_page_exception: Fixture providing page content with missing ratings.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_spec_rating(bs4_movie_page)
    val_expected = 2.4
    assert val == val_expected
    val = scraper._get_movie_spec_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_number_of_spec_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie
    number of spec rating"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_number_of_spec_rating(bs4_movie_page)
    val_expected = 3015.0
    assert val == val_expected
    val = scraper._get_movie_number_of_spec_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_summary(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie summary"""
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    val = scraper._get_movie_summary(bs4_movie_page)
    val_expected = "Dans ce film post-apocalyptique, Augustine, scientifique solitaire basé en Arctique, tente l’impossible pour empêcher l'astronaute Sully et son équipage de rentrer sur Terre. Car il sait qu’une mystérieuse catastrophe planétaire est imminente...Inspiré du roman éponyme de Lily Brooks-Dalton, plébiscité par la critique."
    assert val == val_expected
    val = scraper._get_movie_summary(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test_scraping_movies_with_append(tmp_path, get_dataframe):
    path_dir = tmp_path / "data"
    path_dir.mkdir()
    output_csv_name = "allocine_movies.csv"
    full_dir = f"{path_dir}/{output_csv_name}"
    df = get_dataframe
    ori_shape = df.shape
    df.to_csv(full_dir, index=False)

    config = ScraperConfig(
        number_of_pages=1,
        from_page=1,
        output_dir=Path(path_dir),
        output_csv_name=output_csv_name,
        pause_scraping=(0, 1),
        append_result=True,
    )

    scraper = AllocineScraper(config)
    scraper.scraping_movies()
    df_scraper = pd.read_csv(full_dir)
    end_shape = df_scraper.shape
    end_ids = df_scraper["id"]
    assert ori_shape[0] + 1 == end_shape[0]
    assert ori_shape[1] == end_shape[1]
    assert list(end_ids) == list(set(end_ids))


def test_scraping_movies(tmp_path):
    path_dir = tmp_path / "data"
    path_dir.mkdir()
    output_csv_name = "allocine_movies.csv"
    full_dir = f"{path_dir}/{output_csv_name}"

    config = ScraperConfig(
        number_of_pages=1,
        from_page=1,
        output_dir=Path(path_dir),
        output_csv_name=output_csv_name,
        pause_scraping=(0, 1),
        append_result=False,
    )
    scraper = AllocineScraper(config)

    scraper.scraping_movies()
    df_scraper = pd.read_csv(full_dir)
    end_shape = df_scraper.shape
    assert end_shape[0] == 1


def test_number_of_page_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            number_of_pages="five",  # type: ignore
        )


def test_from_page_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            from_page="one",  # type: ignore
        )


def test_output_dir_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            output_dir=1,  # type: ignore
        )


def test_output_csv_name_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            output_csv_name=1,  # type: ignore
        )


def test_pause_scraping_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            pause_scraping="pause",  # type: ignore
        )


def test_append_result_exception(tmp_path):
    """Test error handling when appending to nonexistent file.

    Verifies that appropriate error is raised when trying to append
    to a file that doesn't exist.

    Args:
        tmp_path: Pytest fixture providing temporary directory path.
    """
    with pytest.raises(FileNotFoundError):
        path_dir = tmp_path / "data"
        output_csv_name = "allocine_movies.csv"

        config = ScraperConfig(
            number_of_pages=1,
            from_page=1,
            output_dir=Path(path_dir),
            output_csv_name=output_csv_name,
            pause_scraping=(0, 1),
            append_result=True,
        )
        scraper = AllocineScraper(config)
        scraper.scraping_movies()


def test_parse_page_with_exclude_ids(tmp_path, response_page):
    """Test page parsing with excluded movie IDs.

    Verifies that movies in the exclude list are properly filtered out
    when in append mode.

    Args:
        tmp_path: Pytest fixture providing temporary directory path.
        response_page: Fixture providing mock page response.
    """
    path_dir = tmp_path / "data"
    path_dir.mkdir()

    config = ScraperConfig(
        output_dir=Path(path_dir),
        append_result=False,
    )
    scraper = AllocineScraper(config)
    scraper.config.append_result = True
    scraper.exclude_ids = [251354, 229831]  # Exclude first two movies
    urls = scraper._parse_page(response_page)
    assert len(urls) == 13  # Original length minus 2
    assert "/film/fichefilm_gen_cfilm=251354.html" not in urls
    assert "/film/fichefilm_gen_cfilm=229831.html" not in urls


def test_randomize_waiting_time_bounds():
    """Test wait time generation bounds.

    Verifies that generated wait times strictly respect the configured
    minimum and maximum bounds.
    """
    config = ScraperConfig(pause_scraping=(5, 10))
    scraper = AllocineScraper(config)
    for _ in range(100):
        wait_time = scraper._randomize_waiting_time()
        assert 5 <= wait_time <= 10


def test_empty_dataframe_initialization():
    """Test DataFrame initialization.

    Verifies that the DataFrame is properly initialized with correct
    columns and empty state.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    assert list(scraper.df.columns) == scraper.movie_infos
    assert len(scraper.df) == 0


def test_parse_movie_with_missing_data(response_movie):
    """Test movie parsing with missing data.

    Verifies that the parser handles missing optional fields gracefully
    while still capturing required fields.

    Args:
        response_movie: Fixture providing mock movie response.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    response_movie._content = response_movie._content.replace(b"stareval-note", b"missing-note")
    scraper._parse_movie(response_movie)
    assert scraper.df.iloc[0]["press_rating"] is None
    assert scraper.df.iloc[0]["title"] is not None


def test_edge_case_movie_durations(bs4_movie_page):
    """Test edge cases in movie duration parsing.

    Verifies that the duration parser handles empty or missing
    duration information correctly.

    Args:
        bs4_movie_page: Fixture providing parsed BeautifulSoup movie page content.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)

    duration_tag = bs4_movie_page.find("span", {"class": "spacer"})
    duration_tag.next_sibling.replace_with("")
    assert scraper._get_movie_duration(bs4_movie_page) is None


def test_config_validation_edge_cases():
    """Test configuration validation edge cases.

    Verifies that the configuration validator properly catches invalid
    values for number of pages, starting page, and pause duration range.
    """
    with pytest.raises(ValidationError):
        ScraperConfig(number_of_pages=int("0"))  # Should be > 0

    with pytest.raises(ValidationError):
        ScraperConfig(from_page=int("0"))  # Should be > 0

    with pytest.raises(ValidationError):
        ScraperConfig(pause_scraping=(5, 3))  # Max should be > min


def test_parse_movie_duplicate_handling(response_movie):
    """Test handling of duplicate movie entries.

    Verifies that duplicate movies are properly handled when parsing,
    ensuring only one copy of each movie is kept in the DataFrame.

    Args:
        response_movie: Fixture providing mock movie response.
    """
    config = ScraperConfig(append_result=True)
    scraper = AllocineScraper(config)
    scraper._parse_movie(response_movie)
    scraper._parse_movie(response_movie)
    assert len(scraper.df) == 1


def test_parse_movie_invalid_html(response_movie):
    """Test movie parsing when page HTML is invalid (missing content-layout).

    Verifies that the parser returns early without crashing.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    response_movie._content = b"<html><body>No movie content here</body></html>"

    # Test fallback URL parsing success
    response_movie.url = "http://www.allocine.fr/film/fichefilm_gen_cfilm=12345.html"
    scraper._parse_movie(response_movie)
    assert len(scraper.df) == 0
    assert len(scraper.staged_errors) == 1
    assert scraper.staged_errors[0]["movie_id"] == 12345

    # Test fallback URL parsing failure (exception branch)
    scraper.staged_errors = []
    response_movie.url = "http://www.allocine.fr/no-id-here"
    scraper._parse_movie(response_movie)
    assert len(scraper.df) == 0
    assert len(scraper.staged_errors) == 1
    assert scraper.staged_errors[0]["movie_id"] == 0


def test_parse_movie_generic_exception(response_movie, monkeypatch):
    """Test movie parsing when a parser method raises a generic Exception.

    Verifies that the exception is caught, logged, and fields set to None instead of crashing.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)

    def mock_get_id(movie):
        raise ValueError("Mock extraction failure")

    monkeypatch.setattr(
        "allocine_dataset_scraper.scraper.AllocineScraper._get_movie_id",
        mock_get_id,
    )
    scraper._parse_movie(response_movie)
    assert len(scraper.df) == 1
    assert scraper.df.iloc[0]["id"] is None


def test_number_of_spec_rating_regex_fix():
    """Test that spectator rating count handles spaces, non-breaking spaces, and extra text (e.g. dont critiques) correctly."""
    from bs4 import BeautifulSoup

    # Test case 1: normal number with space thousands separator
    html = '<div class="rating-item">Spectateurs <span class="stareval-review"> 25 877 notes dont 1 686 critiques</span></div>'
    soup = BeautifulSoup(html, "html.parser")
    val = AllocineScraper._get_movie_number_of_spec_rating(soup)
    assert val == 25877.0

    # Test case 2: normal number with comma
    html = '<div class="rating-item">Spectateurs <span class="stareval-review"> 3015 notes, 301 critiques</span></div>'
    soup = BeautifulSoup(html, "html.parser")
    val = AllocineScraper._get_movie_number_of_spec_rating(soup)
    assert val == 3015.0

    # Test case 3: single note
    html = '<div class="rating-item">Spectateurs <span class="stareval-review"> 1 note</span></div>'
    soup = BeautifulSoup(html, "html.parser")
    val = AllocineScraper._get_movie_number_of_spec_rating(soup)
    assert val == 1.0


def test_movie_data_validation():
    """Test validation layer on clean and corrupt data."""
    from allocine_dataset_scraper.validation import validate_movie

    # Clean data
    clean_movie = {
        "id": 12345,
        "title": "Inception",
        "release_date": pd.to_datetime("2010-07-16"),
        "duration": 148,
        "genres": "Sci-Fi",
        "directors": "Christopher Nolan",
        "actors": "Leonardo DiCaprio",
        "nationality": "USA",
        "press_rating": 4.5,
        "number_of_press_rating": 45.0,
        "spec_rating": 4.7,
        "number_of_spec_rating": 12000.0,
        "summary": "A thief steals corporate secrets through the use of dream-sharing technology.",
    }
    errors = validate_movie(clean_movie)
    assert len(errors) == 0

    # Corrupted data (absurd spec rating, too long duration, etc.)
    corrupt_movie = {
        "id": -10,  # invalid id
        "title": "",  # too short
        "release_date": pd.to_datetime("1800-01-01"),  # too old
        "duration": 800,  # too long
        "genres": "Sci-Fi",
        "directors": "Christopher Nolan",
        "actors": "Leonardo DiCaprio",
        "nationality": "USA",
        "press_rating": 6.0,  # invalid rating
        "number_of_press_rating": 1500.0,  # too high
        "spec_rating": -1.0,  # invalid rating
        "number_of_spec_rating": 950572538.0,  # absurd Pulp Fiction-like rating count!
        "summary": "Short synopsis.",
    }
    errors = validate_movie(corrupt_movie)
    assert len(errors) > 0
    fields_with_errors = [e["field"] for e in errors]
    assert "id" in fields_with_errors
    assert "title" in fields_with_errors
    assert "release_date" in fields_with_errors
    assert "duration" in fields_with_errors
    assert "press_rating" in fields_with_errors
    assert "number_of_press_rating" in fields_with_errors
    assert "spec_rating" in fields_with_errors
    assert "number_of_spec_rating" in fields_with_errors

    # Too far future date (more than 5 years in the future)
    import datetime

    future_movie = clean_movie.copy()
    future_movie["release_date"] = pd.to_datetime(f"{datetime.datetime.now().year + 6}-01-01")
    errors2 = validate_movie(future_movie)
    assert len(errors2) > 0
    assert any(e["field"] == "release_date" for e in errors2)


def test_quality_report_logging_and_retry(tmp_path, response_movie):
    """Test validation failure stages SCRAPE_FAILED and BAD_DATA and verifies retry logic and count increments."""
    from requests import Response
    from allocine_dataset_scraper.utils import read_file

    path_dir = tmp_path / "data"
    path_dir.mkdir()

    config = ScraperConfig(
        output_dir=Path(path_dir), quality_report_csv_name="custom_quality_report.csv", auto_retry=False, max_retries=2
    )
    scraper = AllocineScraper(config)

    def response_corrupted_movie():
        txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
        txt = txt.replace(" 3015 notes", " 9999999 notes")
        resp = Response()
        resp.status_code = 200
        resp._content = str.encode(txt)
        return resp

    scraper._get_movie = lambda url: response_corrupted_movie()

    # 1. Test BAD_DATA: Parse a movie that has corrupted data (e.g. mock a highly corrupted rating count)
    response_movie._content = response_movie._content.replace(b" 3015 notes", b" 9999999 notes")
    scraper._parse_movie(response_movie)

    # Verify staged errors are populated
    assert len(scraper.staged_errors) > 0
    assert scraper.staged_errors[0]["error_type"] == "BAD_DATA"
    assert scraper.staged_errors[0]["field"] == "number_of_spec_rating"
    assert scraper.staged_errors[0]["movie_id"] == 275220

    # Write errors to CSV
    scraper._write_staged_errors()
    report_path = config.full_quality_report_path
    assert report_path.exists()

    # Verify CSV content
    df_report = pd.read_csv(report_path)
    assert len(df_report) == 1
    assert df_report.iloc[0]["error_type"] == "BAD_DATA"
    assert df_report.iloc[0]["retry_count"] == 0

    # 2. Test retry failure: Retry it, but it fails again! (Mock _get_movie to return same bad page)
    scraper.retry_failed_movies()
    df_report2 = pd.read_csv(report_path)
    assert len(df_report2) == 1
    assert df_report2.iloc[0]["retry_count"] == 1

    # Retry it again (hits limit of max_retries = 2)
    scraper.retry_failed_movies()
    df_report3 = pd.read_csv(report_path)
    assert len(df_report3) == 1
    assert df_report3.iloc[0]["retry_count"] == 2

    # Attempt to retry again, should not run because retry_count >= max_retries
    scraper.retry_failed_movies()
    # It remains 2, not incremented further
    df_report4 = pd.read_csv(report_path)
    assert df_report4.iloc[0]["retry_count"] == 2

    # 3. Test retry success: Update the response to be clean, reset retry_count on a new mock, and run retry!
    df_report_reset = pd.read_csv(report_path)
    df_report_reset.loc[0, "retry_count"] = 0
    df_report_reset.to_csv(report_path, index=False)

    def response_unique_clean_movie():
        txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
        resp = Response()
        resp.status_code = 200
        resp._content = str.encode(txt)
        return resp

    # Patch scraper _get_movie
    scraper._get_movie = lambda url: response_unique_clean_movie()

    scraper.retry_failed_movies()

    # Verify quality report is cleared of this movie
    df_report_success = pd.read_csv(report_path)
    assert len(df_report_success) == 0

    # Verify that the corrected movie data exists in the main CSV!
    df_movies = pd.read_csv(config.full_output_path)
    assert len(df_movies) == 1
    assert df_movies.iloc[0]["number_of_spec_rating"] == 3015.0


def test_auto_retry_integration(tmp_path, monkeypatch):
    """Test that auto_retry logic automatically executes at the end of scraping."""
    from allocine_dataset_scraper.utils import read_file

    path_dir = tmp_path / "data"
    path_dir.mkdir()

    config = ScraperConfig(
        output_dir=Path(path_dir),
        quality_report_csv_name="auto_retry_report.csv",
        number_of_pages=1,
        auto_retry=True,
        max_retries=2,
    )
    scraper = AllocineScraper(config)

    # Mock movie fetching to raise an exception on first try, but succeed on retry!
    call_count = 0

    def mock_get_movie(url):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("Temporary request failure")
        else:
            from requests import Response

            txt = read_file(str(Path(__file__).parent / "data/movie.txt"))
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode(txt)
            return resp

    monkeypatch.setattr(scraper, "_get_movie", mock_get_movie)

    # Execute scrape
    scraper.scraping_movies()

    # Check that it fetched on retry and succeeded, clearing the error log!
    report_path = config.full_quality_report_path
    if report_path.exists():
        df_report = pd.read_csv(report_path)
        assert len(df_report) == 0

    # Verify the movie was successfully merged into the final database
    assert len(scraper.df) == 1
    assert scraper.df.iloc[0]["id"] == 275220


def test_scraper_retry_boundary_cases(tmp_path, monkeypatch):
    """Test various boundary cases and error branches in retry logic to maximize coverage."""

    path_dir = tmp_path / "data"
    path_dir.mkdir()

    # 1. retry_errors is True inside scraping_movies (covers 299-300)
    config_retry = ScraperConfig(
        output_dir=Path(path_dir), quality_report_csv_name="boundary_quality_report.csv", retry_errors=True
    )
    scraper = AllocineScraper(config_retry)
    monkeypatch.setattr(scraper, "retry_failed_movies", lambda: setattr(scraper, "_retry_called", True))
    scraper.scraping_movies()
    assert getattr(scraper, "_retry_called", False) is True

    # 2. retry_failed_movies when report path does not exist (covers 415-416)
    config = ScraperConfig(
        output_dir=Path(path_dir), quality_report_csv_name="nonexistent_report.csv", retry_errors=False
    )
    scraper2 = AllocineScraper(config)
    scraper2.retry_failed_movies()

    # 3. retry_failed_movies when df_report is empty (covers 428-430)
    report_path = config.full_quality_report_path
    pd.DataFrame(
        data={
            c: []
            for c in ["movie_id", "movie_title", "error_type", "field", "value", "reason", "retry_count", "timestamp"]
        }
    ).to_csv(report_path, index=False)
    scraper2.retry_failed_movies()

    # 4. retry_failed_movies when df_report has only movies that reached max retries (covers 431-434)
    # Also tests _write_staged_errors when existing report is not empty (covers 391-394 and 400-408)
    existing_err = {
        "movie_id": 99999,
        "movie_title": "Max Retried Movie",
        "error_type": "BAD_DATA",
        "field": "duration",
        "value": "900",
        "reason": "too long",
        "retry_count": 3,
        "timestamp": "2026-05-30",
    }
    pd.DataFrame([existing_err]).to_csv(report_path, index=False)
    scraper2.staged_errors = [
        {
            "movie_id": 99999,
            "movie_title": "Max Retried Movie",
            "error_type": "BAD_DATA",
            "field": "duration",
            "value": "900",
            "reason": "too long",
            "retry_count": 0,
            "timestamp": "2026-05-30",
        }
    ]
    scraper2._write_staged_errors()
    scraper2.retry_failed_movies()

    # 5. retry_failed_movies when it raises an exception (covers 500-528)
    df = pd.read_csv(report_path)
    df.loc[0, "retry_count"] = 0
    df.to_csv(report_path, index=False)

    monkeypatch.setattr(scraper2, "_get_movie", lambda url: (_ for _ in ()).throw(ValueError("Critical retry error")))
    scraper2.retry_failed_movies()

    df_after_except = pd.read_csv(report_path)
    page_row = df_after_except[df_after_except["field"] == "page"]
    assert len(page_row) == 1
    assert page_row.iloc[0]["retry_count"] == 1

    # 6. listing page fetch failure inside scraping_movies (covers 315-317)
    scraper3 = AllocineScraper(ScraperConfig(output_dir=Path(path_dir), number_of_pages=1))
    monkeypatch.setattr(
        scraper3, "_get_page", lambda page: (_ for _ in ()).throw(ConnectionError("Listing fetch fail"))
    )
    scraper3.scraping_movies()


def test_scraper_empty_boundaries(tmp_path):
    """Test early returns and empty inputs in scraper functions."""
    config = ScraperConfig(output_dir=tmp_path / "data")
    scraper = AllocineScraper(config)

    # Test _write_staged_errors with empty self.staged_errors
    scraper.staged_errors = []
    scraper._write_staged_errors()
    assert not config.full_quality_report_path.exists()

    # Test retry_failed_movies with empty list
    scraper.retry_failed_movies(movie_ids=[])


def test_validate_scraped_data(tmp_path, monkeypatch):
    """Test the validate_scraped_data method with different scenarios."""
    path_dir = tmp_path / "data"
    path_dir.mkdir()
    csv_file = path_dir / "allocine_movies.csv"

    # Scenario 1: File does not exist
    config_missing = ScraperConfig(output_dir=path_dir)
    scraper_missing = AllocineScraper(config_missing)
    with pytest.raises(FileNotFoundError):
        scraper_missing.validate_scraped_data()

    # Scenario 2: File is empty (causes EmptyDataError)
    pd.DataFrame().to_csv(csv_file, index=False)
    scraper_empty = AllocineScraper(config_missing)
    scraper_empty.validate_scraped_data()
    # Should complete without error

    # Scenario 2b: File has columns but no rows (empty DataFrame success)
    pd.DataFrame(data={"id": [], "title": []}).to_csv(csv_file, index=False)
    scraper_empty_rows = AllocineScraper(config_missing)
    scraper_empty_rows.validate_scraped_data()

    # Scenario 3: Clean data
    clean_movie = {
        "id": 123,
        "title": "Clean Movie",
        "release_date": "2020-01-01 00:00:00",
        "duration": 120,
        "genres": "Drama",
        "directors": "John Doe",
        "actors": "Actor A",
        "nationality": "France",
        "press_rating": 4.0,
        "number_of_press_rating": 20.0,
        "spec_rating": 4.5,
        "number_of_spec_rating": 100.0,
        "summary": "This is a clean movie.",
    }
    pd.DataFrame([clean_movie]).to_csv(csv_file, index=False)
    scraper_clean = AllocineScraper(config_missing)
    scraper_clean.validate_scraped_data()
    assert len(scraper_clean.staged_errors) == 0
    assert not config_missing.full_quality_report_path.exists()

    # Scenario 4: Corrupt data (absurd values, NaN coercion, etc.)
    corrupt_movie = {
        "id": -5,  # Invalid ID
        "title": "Corrupt Movie",
        "release_date": "1800-01-01 00:00:00",  # Invalid date
        "duration": float("nan"),  # Missing but optional, should handle NaN coercion
        "genres": "Drama",
        "directors": "John Doe",
        "actors": "Actor A",
        "nationality": "France",
        "press_rating": 6.0,  # Invalid press rating
        "number_of_press_rating": 20.0,
        "spec_rating": 4.5,
        "number_of_spec_rating": 9999999.0,  # Too high rating count
        "summary": "This is a corrupt movie.",
    }
    pd.DataFrame([corrupt_movie]).to_csv(csv_file, index=False)
    scraper_corrupt = AllocineScraper(config_missing)
    scraper_corrupt.validate_scraped_data()

    # Should find validation errors by verifying the quality report file was created
    assert config_missing.full_quality_report_path.exists()
    df_report = pd.read_csv(config_missing.full_quality_report_path)
    assert len(df_report) > 0
    # Ensure ID and spec rating counts failed
    failed_fields = df_report["field"].tolist()
    assert "id" in failed_fields
    assert "release_date" in failed_fields
    assert "press_rating" in failed_fields
    assert "number_of_spec_rating" in failed_fields

    # Scenario 5: Non-numeric values for coercion failure exceptions
    coercion_movie = {
        "id": "not-an-int",
        "title": "Coercion Fail Movie",
        "release_date": "2020-01-01 00:00:00",
        "duration": "not-an-int",
        "genres": "Drama",
        "directors": "John Doe",
        "actors": "Actor A",
        "nationality": "France",
        "press_rating": 4.0,
        "number_of_press_rating": 20.0,
        "spec_rating": 4.5,
        "number_of_spec_rating": 100.0,
        "summary": "Coercion test",
    }
    pd.DataFrame([coercion_movie]).to_csv(csv_file, index=False)
    scraper_coercion = AllocineScraper(config_missing)
    scraper_coercion.validate_scraped_data()

    # Scenario 6: Exception when reading the CSV file (generic Exception block)
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("Mock read error")))
    scraper_error = AllocineScraper(config_missing)
    with pytest.raises(RuntimeError):
        scraper_error.validate_scraped_data()
