"""Scraping movies informations available on Allocine.fr

Attributes
----------
scraper (object):
    Instance of the main class.
"""

import datetime

# import os
import re
import time
import unicodedata
from random import randrange
from typing import List, Optional, Union

import bs4
import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

# from dotenv import find_dotenv, load_dotenv
from loguru import logger


class AllocineScraper(object):
    """Main class for scraping Allociné.fr

    Attributes
    ----------
    ALLOCINE_URL (str):
        Base URL where we will get movie attributes.

    df (pd.DataFrame):
        Pandas DataFrame with all the scraped informations.

    output_csv_name (str):
        CSV Filename of the Pandas DataFrame that hosts all our movie results.

    pause_scraping (list):
        Random time to wait before each page scraped.

    movie_infos (list):
        List of movie attributes we're interested in.

    number_of_pages (int):
        How many pages to scrap on Allociné.fr.

    from_page (int):
        first page number to scrape.
    """

    ALLOCINE_URL = "https://www.allocine.fr/films/?page="

    movie_infos = [
        "id",
        "title",
        "release_date",
        "duration",
        "genres",
        "directors",
        "actors",
        "nationality",
        "press_rating",
        "number_of_press_rating",
        "spec_rating",
        "number_of_spec_rating",
        "summary",
    ]

    df = pd.DataFrame(columns=movie_infos)

    def __init__(
        self,
        number_of_pages: Optional[int] = 10,
        from_page: Optional[int] = 1,
        output_csv_name: Optional[str] = "allocine_movies.csv",
        pause_scraping: Optional[List[int]] = [2, 10],
    ) -> None:
        """Initializes our Scraper class.

        Parameters
        ----------
        number_of_pages : Optional[int], Optional, Default = 10
            number of pages to scrape

        from_page : Optional[int], Optional, Default = 1
            first page number to scrape. default: 1

        output_csv_name : Optional[str], Optional, Default = allocine_movies.csv
            output csv name.

        pause_scraping : Optional[List[int]], default = [2, 10]
            Number of secondes to wait before scraping the next page.
            Use a fixe number of second or a list of two integer to get a random number of seconds.

        Raises
        ------
        Exception:
            Exits the scraper if the arguments are not appropriate.
        """

        if not isinstance(number_of_pages, int) or number_of_pages < 2:
            raise Exception("number_of_pages must be an integer superior to 1.")

        self.number_of_pages = number_of_pages

        if not isinstance(from_page, int) or from_page < 1:
            raise Exception("from_page must be an integer superior to 0.")

        self.from_page = from_page

        if not isinstance(output_csv_name, str) or output_csv_name[-4:] != ".csv":
            raise Exception("output file name must have a valid CSV name.")

        self.output_csv_name = output_csv_name

        if not isinstance(pause_scraping, list):
            raise Exception("pause_scraping must be an integer or a list of integer")

        self.pause_scraping = pause_scraping

        logger.info("Initializing Allocine Scraper...")
        logger.info(f"- Number of pages to scrap: {self.number_of_pages}")
        logger.info(
            f"- Time to wait between pages between : {self.pause_scraping[0]} sec and {self.pause_scraping[1]} sec"
        )
        logger.info(f"- Results will be stored in: {self.output_csv_name}")

    def _get_page(self, page_number: int) -> requests.models.Response:
        """Private method to get the full content of a webpage.

        Parameters
        ----------
        page_number (int):
            Number of the page on Allociné.fr.

        Returns
        -------
        requests.models.Response:
            Full source code of the asked webpage.
        """

        response = requests.get(self.ALLOCINE_URL + str(page_number))
        return response

    def _get_movie(self, url: str) -> requests.models.Response:
        """Private method to get the full content of a movie webpage.

        Parameters
        ----------
        url (str):
            movie url to scrape.

        Returns
        -------
        requests.models.Response:
            Full source code of the asked webpage.
        """
        response = requests.get(f"http://www.allocine.fr{url}")
        return response

    def _randomize_waiting_time(self) -> int:
        """Private method to get a random waiting time."""
        return randrange(*self.pause_scraping)

    def _parse_page(self, page: requests.models.Response) -> List[str]:
        """Private method to parse a single result page from Allociné.fr.

        Parameters
        ----------
        page (str):
            Source code of a Allocine.fr webpage.

        Returns
        -------
        List:
            list of movie page urls
        """

        parser = BeautifulSoup(page.content, "html.parser")
        urls = [url.a["href"] for url in parser.find_all("h2", class_="meta-title")]

        return urls

    def _parse_movie(self, page: requests.models.Response):
        parser = BeautifulSoup(page.content, "html.parser")
        parser_movie = parser.find("main", {"id": "content-layout"})

        # store temporarly all the movie datas
        movie_datas = {}

        # get every info we're interested in
        for info in self.movie_infos:

            # take care of unavailable infos for some movies
            try:
                scraped_info = getattr(self, "_get_movie_" + info)(parser_movie)
            except Exception as ex:
                logger.error(ex)
                scraped_info = None

            # store the movie attribute
            movie_datas[info] = [scraped_info]

        # add movie infos to the dataframe
        self.df = pd.concat([self.df, pd.DataFrame(movie_datas)], ignore_index=True)

        # just to be safe, save after every page
        self.df.to_csv("data/" + self.output_csv_name, index=False)

    def scraping_movies(self) -> None:
        """Starts the scraping process."""

        logger.info("Starting scraping movies from Allocine...")

        for number in range(self.from_page, self.from_page + self.number_of_pages):

            logger.info(
                f"Fetching Page {number}/{self.from_page + self.number_of_pages}"
            )
            time.sleep(self._randomize_waiting_time())
            res_page = self._get_page(number)
            urls_to_parse = self._parse_page(res_page)

            for url in urls_to_parse:
                logger.info(f"Fetching Movie {url}")
                res_movie = self._get_movie(url)
                self._parse_movie(res_movie)

                sleep_timer = self._randomize_waiting_time()
                logger.info(
                    f"Done Fetching {url}. Waiting {sleep_timer} sec before the next one..."
                )
                time.sleep(sleep_timer)

            sleep_timer = self._randomize_waiting_time()
            logger.info(
                f"Done scraping page #{number}. Waiting {sleep_timer} sec before the next one..."
            )
            time.sleep(sleep_timer)

        logger.info("Done scraping Allocine.")
        logger.info(f"Results are stored in {self.output_csv_name}.")

    def _get_movie_id(self, movie: bs4.element.Tag) -> int:
        """Private method to retrieve the movie ID according to Allociné.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            int: The movie ID according to Allociné.
        """

        movie_id = re.sub(
            r"\D", "", movie.find("nav", {"class": "third-nav"}).a["href"]
        )

        return int(movie_id)

    def _get_movie_title(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie title.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            str: The movie title.
        """

        movie_title = movie.find("div", {"class": "titlebar-title"}).text.strip()

        return movie_title

    def _get_movie_release_date(
        self, movie: bs4.element.Tag
    ) -> Union[datetime.datetime, None]:
        """Private method to retrieve the movie release date.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            datetime.datetime: The movie release date.
        """

        movie_date = movie.find("span", {"class": "date"}).text.strip()
        movie_date = dateparser.parse(movie_date, date_formats=["%d %B %Y"])
        return movie_date

    def _get_movie_duration(self, movie: bs4.element.Tag) -> int:
        """Private method to retrieve the movie duration.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            int: The movie duration in minutes.
        """

        movie_duration = movie.find("span", {"class": "spacer"}).next_sibling.strip()
        duration_timedelta = pd.to_timedelta(movie_duration).components
        movie_duration = duration_timedelta.hours * 60 + duration_timedelta.minutes

        return movie_duration

    def _get_movie_genres(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie genre(s).
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            str: The movie genre(s).
        """

        movie_genres = [
            genre.text
            for genre in movie.find(
                "div", {"class": "meta-body-item meta-body-info"}
            ).find_all("span", class_=re.compile(r".*==$"))
        ]

        return ", ".join(movie_genres)

    def _get_movie_directors(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie director(s).
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            str: The movie director(s).
        """

        movie_directors = [
            link.text
            for link in movie.find(
                "div", {"class": "meta-body-item meta-body-direction"}
            ).find_all(["a", "span"], class_=re.compile(r".*blue-link$"))
        ]

        return ", ".join(movie_directors)

    def _get_movie_actors(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie actor(s).
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            str: The movie actor(s).
        """

        movie_actors = [
            actor.text
            for actor in movie.find(
                "div", {"class": "meta-body-item meta-body-actor"}
            ).find_all(["a", "span"])
        ][1:]

        return ", ".join(movie_actors)

    def _get_movie_nationality(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie nationality.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            str: The movie nationality.
        """

        movie_nationality = [
            nationality.text
            for nationality in movie.find_all("span", class_="nationality")
        ]

        return ", ".join(movie_nationality)

    def _get_movie_press_rating(self, movie: bs4.element.Tag) -> Union[float, None]:
        """Private method to retrieve the movie rating according to the press.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            Union[float, None]: The movie rating according to the press.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:

            if "Presse" in ratings.text:
                return float(
                    re.sub(
                        ",", ".", ratings.find("span", {"class": "stareval-note"}).text
                    )
                )
        return None

    def _get_movie_number_of_press_rating(
        self, movie: bs4.element.Tag
    ) -> Union[float, None]:
        """Private method to retrieve number of ratings from the press.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            Union[float, None]: The movie rating according to the press.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:

            if "Presse" in ratings.text:
                return float(
                    re.sub(
                        r"\D",
                        "",
                        ratings.find("span", {"class": "stareval-review"}).text,
                    )
                )
        return None

    def _get_movie_spec_rating(self, movie: bs4.element.Tag) -> Union[float, None]:
        """Private method to retrieve the movie rating according to the spectators.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            Union[float, None]: The number of ratings from to the spectators.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:

            if "Spectateurs" in ratings.text:
                return float(
                    re.sub(
                        ",", ".", ratings.find("span", {"class": "stareval-note"}).text
                    )
                )

        return None

    def _get_movie_number_of_spec_rating(
        self, movie: bs4.element.Tag
    ) -> Union[float, None]:
        """Private method to retrieve number of ratings from the spectators.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            Union[float, None]: The number of ratings from according to the press.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:

            if "Spectateurs" in ratings.text:
                return float(
                    re.sub(
                        r"\D",
                        "",
                        ratings.find("span", {"class": "stareval-review"}).text,
                    )
                )
        return None

    def _get_movie_summary(self, movie: bs4.element.Tag) -> str:
        """Private method to retrieve the movie summary.
        Args:
            movie (bs4.element.Tag): Parser results with the movie informations.
        Returns:
            str: The movie summary.
        """

        movie_summary = (
            movie.find("section", {"class": "section ovw ovw-synopsis"})
            .find("div", {"class": "content-txt"})
            .text.strip()
        )

        return unicodedata.normalize("NFKC", movie_summary)
