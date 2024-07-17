import dateparser
import pandas as pd
import pytest
from allocine_dataset_scraper.scraper import AllocineScraper


def test__get_page():
    """Test that requests page return code 200 (patch)."""
    scraper = AllocineScraper()
    resp = scraper._get_page()
    assert resp.status_code == 200


def test__get_movie():
    """Test that requests movie return code 200 (patch)."""
    scraper = AllocineScraper()
    resp = scraper._get_movie()
    assert resp.status_code == 200


def test__randomize_waiting_time():
    """Test that randomize waiting time return
    a value inside the range."""
    scraper = AllocineScraper()
    pause_range = range(*scraper.pause_scraping)
    assert scraper._randomize_waiting_time() in pause_range


def test__create_directory_if_not_exist(tmp_path):
    """Test that the directory are created, execute twice to check
    behavior when the directory exist."""
    path_dir = str(tmp_path / "data")
    scraper = AllocineScraper()
    scraper._create_directory_if_not_exist(path_dir)
    assert len(list(tmp_path.iterdir())) == 1
    scraper._create_directory_if_not_exist(path_dir)
    assert len(list(tmp_path.iterdir())) == 1


def test__parse_page(response_page) -> None:
    """Test the page parser to retrieve movie page url"""
    scraper = AllocineScraper()
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
    """Test the page parser to retrieve movie id"""
    scraper = AllocineScraper()
    val = scraper._get_movie_id(bs4_movie_page)
    val_expected = 275220
    assert val == val_expected


def test__get_movie_title(bs4_movie_page):
    """Test the page parser to retrieve movie title"""
    scraper = AllocineScraper()
    val = scraper._get_movie_title(bs4_movie_page)
    val_expected = "Minuit dans l'univers"
    assert val == val_expected


def test__get_movie_release_date(bs4_movie_page):
    """Test the page parser to retrieve movie release date"""
    scraper = AllocineScraper()
    val = scraper._get_movie_release_date(bs4_movie_page)
    val_expected = dateparser.parse("2020-12-23", date_formats=["%d %B %Y"])
    assert val == val_expected


def test__get_movie_duration(bs4_movie_page):
    """Test the page parser to retrieve movie duration."""
    scraper = AllocineScraper()
    val = scraper._get_movie_duration(bs4_movie_page)
    val_expected = 122
    assert val == val_expected


def test__get_movie_genres(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie genres"""
    scraper = AllocineScraper()
    val = scraper._get_movie_genres(bs4_movie_page)
    val_expected = "Drame, Science Fiction"
    assert val == val_expected
    val = scraper._get_movie_genres(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_directors(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie directors"""
    scraper = AllocineScraper()
    val = scraper._get_movie_directors(bs4_movie_page)
    val_expected = "George Clooney"
    assert val == val_expected
    val = scraper._get_movie_directors(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_actors(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie actors"""
    scraper = AllocineScraper()
    val = scraper._get_movie_actors(bs4_movie_page)
    val_expected = "George Clooney, Felicity Jones, David Oyelowo"
    assert val == val_expected
    val = scraper._get_movie_actors(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_nationality(bs4_movie_page):
    """Test the page parser to retrieve movie nationality"""
    scraper = AllocineScraper()
    val = scraper._get_movie_nationality(bs4_movie_page)
    val_expected = "U.S.A."
    assert val == val_expected


def test__get_movie_press_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie press rating"""
    scraper = AllocineScraper()
    val = scraper._get_movie_press_rating(bs4_movie_page)
    val_expected = 2.5
    assert val == val_expected
    val = scraper._get_movie_press_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_number_of_press_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie
    number of press rating"""
    scraper = AllocineScraper()
    val = scraper._get_movie_number_of_press_rating(bs4_movie_page)
    val_expected = 21.0
    assert val == val_expected
    val = scraper._get_movie_number_of_press_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_spec_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie spectator rating"""
    scraper = AllocineScraper()
    val = scraper._get_movie_spec_rating(bs4_movie_page)
    val_expected = 2.4
    assert val == val_expected
    val = scraper._get_movie_spec_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_number_of_spec_rating(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie
    number of spec rating"""
    scraper = AllocineScraper()
    val = scraper._get_movie_number_of_spec_rating(bs4_movie_page)
    val_expected = 3015.0
    assert val == val_expected
    val = scraper._get_movie_number_of_spec_rating(bs4_movie_page_exception)
    val_expected = None
    assert val == val_expected


def test__get_movie_summary(bs4_movie_page, bs4_movie_page_exception):
    """Test the page parser to retrieve movie summary"""
    scraper = AllocineScraper()
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

    scraper = AllocineScraper(
        number_of_pages=1,
        from_page=1,
        output_dir=f"{path_dir}",
        output_csv_name=output_csv_name,
        pause_scraping=[0, 1],
        append_result=True,
    )

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

    scraper = AllocineScraper(
        number_of_pages=1,
        from_page=1,
        output_dir=f"{path_dir}",
        output_csv_name=output_csv_name,
        pause_scraping=[0, 1],
        append_result=False,
    )

    scraper.scraping_movies()
    df_scraper = pd.read_csv(full_dir)
    end_shape = df_scraper.shape
    assert end_shape[0] == 1


def test_number_of_page_exception():
    with pytest.raises(ValueError):
        AllocineScraper(number_of_pages="5")


def test_from_page_exception():
    with pytest.raises(ValueError):
        AllocineScraper(from_page="1")


def test_output_dir_exception():
    with pytest.raises(ValueError):
        AllocineScraper(output_dir=1)


def test_output_csv_name_exception():
    with pytest.raises(ValueError):
        AllocineScraper(output_csv_name=1)


def test_pause_scraping_exception():
    with pytest.raises(ValueError):
        AllocineScraper(pause_scraping="pause")


def test_append_result_exception(tmp_path):
    with pytest.raises(FileNotFoundError):
        path_dir = tmp_path / "data"
        output_csv_name = "allocine_movies.csv"

        scraper = AllocineScraper(
            number_of_pages=1,
            from_page=1,
            output_dir=f"{path_dir}",
            output_csv_name=output_csv_name,
            pause_scraping=[0, 1],
            append_result=True,
        )

        scraper.scraping_movies()
