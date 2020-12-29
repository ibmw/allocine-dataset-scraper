import dateparser

from allocine_dataset_scraper.allocine_dataset_scraper import AllocineScraper


def test__parse_page(response_page) -> None:
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
    scraper = AllocineScraper()
    val = scraper._get_movie_id(bs4_movie_page)
    val_expected = 275220
    assert val == val_expected


def test__get_movie_title(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_title(bs4_movie_page)
    val_expected = "Minuit dans l'univers"
    assert val == val_expected


def test__get_movie_release_date(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_release_date(bs4_movie_page)
    val_expected = dateparser.parse("2020-12-23", date_formats=["%d %B %Y"])
    assert val == val_expected


def test__get_movie_duration(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_duration(bs4_movie_page)
    val_expected = 122
    assert val == val_expected


def test__get_movie_genres(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_genres(bs4_movie_page)
    val_expected = "Drame, Science fiction"
    assert val == val_expected


def test__get_movie_directors(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_directors(bs4_movie_page)
    val_expected = "George Clooney"
    assert val == val_expected


def test__get_movie_actors(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_actors(bs4_movie_page)
    val_expected = "George Clooney, Felicity Jones, David Oyelowo"
    assert val == val_expected


def test__get_movie_nationality(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_nationality(bs4_movie_page)
    val_expected = "américain"
    assert val == val_expected


def test__get_movie_press_rating(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_press_rating(bs4_movie_page)
    val_expected = 2.4
    assert val == val_expected


def test__get_movie_number_of_press_rating(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_number_of_press_rating(bs4_movie_page)
    val_expected = 18.0
    assert val == val_expected


def test__get_movie_spec_rating(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_spec_rating(bs4_movie_page)
    val_expected = 2.2
    assert val == val_expected


def test__get_movie_number_of_spec_rating(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_number_of_spec_rating(bs4_movie_page)
    val_expected = 488101.0
    assert val == val_expected


def test__get_movie_summary(bs4_movie_page):
    scraper = AllocineScraper()
    val = scraper._get_movie_summary(bs4_movie_page)
    val_expected = "Dans ce film post-apocalyptique, Augustine, scientifique solitaire basé en Arctique, tente l’impossible pour empêcher l'astronaute Sully et son équipage de rentrer sur Terre. Car il sait qu’une mystérieuse catastrophe planétaire est imminente...Inspiré du roman éponyme de Lily Brooks-Dalton, plébiscité par la critique."
    assert val == val_expected
