"""Tests for the Allocine scraper module.

This module contains comprehensive tests for the AllocineScraper class,
covering movie data extraction, parsing, error handling, and file operations.
Tests use mocked responses to avoid actual web requests.
"""

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
    resp = scraper._get_page()
    assert resp.status_code == 200


def test__get_movie():
    """Test individual movie page request functionality.

    Verifies that the movie page request returns a valid response with 200 status code.
    Uses mocked response to avoid actual network requests.
    """
    config = ScraperConfig()
    scraper = AllocineScraper(config)
    resp = scraper._get_movie()
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
        output_dir=f"{path_dir}",
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
        output_dir=f"{path_dir}",
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
            number_of_pages="five",
        )


def test_from_page_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            from_page="one",
        )


def test_output_dir_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            output_dir=1,
        )


def test_output_csv_name_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            output_csv_name=1,
        )


def test_pause_scraping_exception():
    with pytest.raises(ValidationError):
        ScraperConfig(
            pause_scraping="pause",
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
            output_dir=f"{path_dir}",
            output_csv_name=output_csv_name,
            pause_scraping=(0, 1),
            append_result=True,
        )
        scraper = AllocineScraper(config)
        scraper.scraping_movies()


def test_parse_page_with_exclude_ids(response_page):
    """Test page parsing with excluded movie IDs.

    Verifies that movies in the exclude list are properly filtered out
    when in append mode.

    Args:
        response_page: Fixture providing mock page response.
    """
    config = ScraperConfig(append_result=True)
    scraper = AllocineScraper(config)
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
    assert scraper._get_movie_duration(bs4_movie_page) == ""


def test_config_validation_edge_cases():
    """Test configuration validation edge cases.

    Verifies that the configuration validator properly catches invalid
    values for number of pages, starting page, and pause duration range.
    """
    with pytest.raises(ValidationError):
        ScraperConfig(number_of_pages=0)  # Should be > 0

    with pytest.raises(ValidationError):
        ScraperConfig(from_page=0)  # Should be > 0

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
