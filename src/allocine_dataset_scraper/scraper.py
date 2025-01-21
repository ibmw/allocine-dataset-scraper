"""Module for scraping movie information from Allocine.fr website.

This module provides functionality to scrape movie data including titles, ratings,
cast information, and other metadata from the Allocine.fr website.
"""

import datetime
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from random import randrange
from typing import Dict, List, Optional, Tuple, Union

import bs4
import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm.auto import tqdm

logger.remove()
logger.add("scraper.log", rotation="100 MB")
logger.add(sys.stderr, level="CRITICAL")


class AllocineScraper:
    """A scraper for collecting movie information from Allocine.fr.

    This class handles the scraping of movie information from Allocine.fr,
    including pagination, data parsing, and CSV export functionality.

    Attributes
        ALLOCINE_URL: Base URL for the movie listing pages.
        movie_infos: List of movie attributes to collect.
        df: DataFrame storing the collected movie information.
        exclude_ids: List of movie IDs to skip during scraping.
        output_dir: Directory where results will be saved.
        output_csv_name: Name of the output CSV file.
        full_path_csv: Complete path to the output CSV file.
        number_of_pages: Number of pages to scrape.
        from_page: Starting page number.
        pause_scraping: Tuple of min/max seconds to pause between requests.
        append_result: Whether to append to existing results.
    """

    ALLOCINE_URL: str = "https://www.allocine.fr/films/?page="

    movie_infos: List[str] = [
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

    df: pd.DataFrame = pd.DataFrame(columns=movie_infos)

    def __init__(
        self,
        number_of_pages: int = 10,
        from_page: int = 1,
        output_dir: str = "data",
        output_csv_name: str = "allocine_movies.csv",
        pause_scraping: Tuple[int, int] = (2, 10),
        append_result: bool = False,
    ) -> None:
        """Initialize the Allocine scraper.

        Args:
            number_of_pages: Number of pages to scrape. Defaults to 10.
            from_page: First page number to scrape. Defaults to 1.
            output_dir: Directory to save the CSV file. Defaults to "data".
            output_csv_name: Name of the output CSV file. Defaults to "allocine_movies.csv".
            pause_scraping: Tuple of (min, max) seconds to pause between requests.
                Defaults to (2, 10).
            append_result: Whether to append to existing CSV file. Defaults to False.

        Raises:
            ValueError: If any input parameters are invalid.
            FileNotFoundError: If append_result is True and the CSV file doesn't exist.
        """

        if not isinstance(number_of_pages, int) or number_of_pages < 1:
            raise ValueError(f"<{number_of_pages=}> must be an integer superior to 1.")

        self.number_of_pages = number_of_pages

        if not isinstance(from_page, int) or from_page < 1:
            raise ValueError(f"<{from_page=}> must be an integer superior to 0.")

        self.from_page = from_page

        if not isinstance(output_dir, str):
            raise ValueError(f"<{output_dir=}> must have a valid name.")

        self.output_dir = output_dir

        if not isinstance(output_csv_name, str) or output_csv_name[-4:] != ".csv":
            raise ValueError(f"<{output_csv_name=}> must have a valid CSV name.")

        self.output_csv_name = output_csv_name

        if not pause_scraping:
            pause_scraping = (2, 10)

        if not isinstance(pause_scraping, tuple):
            raise ValueError(f"<{pause_scraping=}> must be an Tuple of two integers")

        self.pause_scraping = pause_scraping
        self.append_result = append_result
        self.full_path_csv = f"{self.output_dir}/{self.output_csv_name}"

        logger.info("Initializing Allocine Scraper...")
        logger.info(f"- Number of pages to scrap: {self.number_of_pages}")
        logger.info(
            f"""- Time to wait between pages between :
            {self.pause_scraping[0]} sec and {self.pause_scraping[1]} sec"""
        )
        logger.info(f"- Results will be stored in: <{self.full_path_csv}>")

        if self.append_result:
            try:
                self.df = pd.read_csv(self.full_path_csv)
                self.exclude_ids = self.df["id"].dropna().astype(int).tolist()
                logger.info(
                    f"""- The list to exclude movies already fetch has been initialize
                    -- Total movie listed: {len(self.exclude_ids)}"""
                )
            except Exception as ex:
                logger.error(f"Failed to load the csv {self.full_path_csv} -- {ex}")
                raise FileNotFoundError(f"Failed to load the csv {self.full_path_csv} -- {ex}")
        else:
            self.exclude_ids = []

    def _get_page(self, page_number: int) -> requests.Response:
        """Private method to fetch a movie listing page from Allocine.fr.

        Args:
            page_number: The page number to fetch.

        Returns:
            Response object containing the page content.

        Raises:
            requests.RequestException: If the page fetch fails.
        """

        response = requests.get(self.ALLOCINE_URL + str(page_number))  # pragma: no cover
        return response

    @staticmethod
    def _get_movie(url: str) -> requests.Response:
        """Private method to fetch a specific movie page from Allocine.fr.

        Args:
            url: The movie page URL to fetch.

        Returns:
            Response object containing the movie page content.

        Raises:
            requests.RequestException: If the page fetch fails.
        """
        response = requests.get(f"http://www.allocine.fr{url}")  # pragma: no cover
        return response

    def _randomize_waiting_time(self) -> int:
        """Private method to generate a random waiting time within the configured range.

        Returns:
            Number of seconds to wait.
        """
        return randrange(*self.pause_scraping)

    @staticmethod
    def _create_directory_if_not_exist(path_dir: Union[str, Path]) -> None:
        """Create a directory if it doesn't exist.

        Args:
            path_dir: Path to the directory to create.

        Raises:
            OSError: If directory creation fails.
        """
        if not os.path.exists(path_dir):
            logger.info(f"{path_dir} doesn't exist. We try to create it...")
            try:
                os.makedirs(path_dir)
            except Exception as ex:  # pragma: no cover
                logger.error(f"Failed to create {path_dir}: {ex}")
                raise OSError(f"Failed to create {path_dir}: {ex}")

    def _parse_page(self, page: requests.Response) -> List[str]:
        """Private method to parse a movie listing page to extract movie URLs.

        Args:
            page: Response object containing the page content.

        Returns:
            List of movie page URLs found on the page.
        """

        parser = BeautifulSoup(page.content, "html.parser")
        urls = [url.a["href"] for url in parser.find_all("h2", class_="meta-title")]

        if self.append_result and self.exclude_ids:
            ori_urls_len = len(urls)
            urls = [url for url in urls if int(url.split("=")[-1].split(".")[0]) not in self.exclude_ids]
            urls_len = len(urls)
            logger.info(
                f"""{ori_urls_len - urls_len} / {ori_urls_len}
                movies has already been scraped"""
            )

        return urls

    def _parse_movie(self, page: requests.Response) -> None:
        """Private method to parse a movie page and store the extracted information.

        Args:
            page: Response object containing the movie page content.
        """
        parser = BeautifulSoup(page.content, "html.parser")
        parser_movie = parser.find("main", {"id": "content-layout"})

        self._create_directory_if_not_exist(self.output_dir)

        movie_datas: Dict = {}

        for info in self.movie_infos:
            try:
                scraped_info = getattr(self, "_get_movie_" + info)(parser_movie)
            except AttributeError as ex:  # pragma: no cover
                logger.error(f"<id:{movie_datas.get('id')}, info:{info}>: {ex}")
                scraped_info = None

            movie_datas[info] = [scraped_info]

        self.df = pd.concat([self.df, pd.DataFrame(movie_datas)], ignore_index=True)

        self.df.drop_duplicates(subset=["id"]).to_csv(f"{self.full_path_csv}", index=False)

    def scraping_movies(self) -> None:
        """Execute the movie scraping process.

        This method orchestrates the entire scraping process, including:
        - Fetching listing pages
        - Extracting movie URLs
        - Fetching and parsing individual movie pages
        - Saving results to CSV
        """

        logger.info("Starting scraping movies from Allocine...")

        for number in tqdm(range(self.from_page, self.from_page + self.number_of_pages), desc="Pages"):
            logger.info(f"Fetching Page {number}/{self.from_page + self.number_of_pages}")
            time.sleep(self._randomize_waiting_time())
            res_page = self._get_page(number)
            urls_to_parse = self._parse_page(res_page)

            for url in tqdm(
                urls_to_parse,
                desc="Movies",
                leave=(number == (self.from_page + self.number_of_pages - 1)),
            ):
                logger.info(f"Fetching Movie {url}")
                res_movie = self._get_movie(url)
                self._parse_movie(res_movie)

                self.exclude_ids.append(int(url.split("=")[-1].split(".")[0]))
                sleep_timer = self._randomize_waiting_time()
                logger.info(
                    f"""Done Fetching {url}.
                    Waiting {sleep_timer} sec before the next one..."""
                )
                time.sleep(sleep_timer)

            sleep_timer = self._randomize_waiting_time()
            logger.info(
                f"""Done scraping page #{number}.
                Waiting {sleep_timer} sec before the next one..."""
            )
            time.sleep(sleep_timer)

        logger.info("Done scraping Allocine.")
        logger.info(f"Results are stored in {self.output_csv_name}.")

    @staticmethod
    def _get_movie_id(movie: bs4.element.Tag) -> int:
        """Private method to extract the movie ID from the movie page.

        Args:
            movie: BeautifulSoup Tag object containing movie information.

        Returns:
            The movie's unique identifier.
        """

        movie_id = re.sub(r"\D", "", movie.find("span", {"class": "home"})["href"])

        return int(movie_id)

    @staticmethod
    def _get_movie_title(movie: bs4.element.Tag) -> str:
        """Private method to extract the movie title from the movie page.

        Args:
            movie: BeautifulSoup Tag object containing movie information.

        Returns:
            The movie's title.
        """

        movie_title = movie.find("div", {"class": "titlebar-title"}).text.strip()

        return movie_title

    @staticmethod
    def _get_movie_release_date(
        movie: bs4.element.Tag,
    ) -> Optional[datetime.datetime]:
        """Private method to extract the movie release date from the movie page.

        Args:
            movie: BeautifulSoup Tag object containing movie information.

        Returns:
            The movie's release date or None if not found.
        """

        movie_date = movie.find("span", {"class": "date"})
        if movie_date:
            movie_date = movie_date.text.strip()
            movie_date = dateparser.parse(movie_date, date_formats=["%d %B %Y"])
        return movie_date

    @staticmethod
    def _get_movie_duration(movie: bs4.element.Tag) -> Optional[int]:
        """Private method to extract the movie duration.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's duration in minutes or None if not found.
        """

        movie_duration = movie.find("span", {"class": "spacer"}).next_sibling.strip()
        if movie_duration != "":
            duration_timedelta = pd.to_timedelta(movie_duration).components
            movie_duration = duration_timedelta.hours * 60 + duration_timedelta.minutes

        return movie_duration

    @staticmethod
    def _get_movie_genres(movie: bs4.element.Tag) -> Optional[str]:
        """Private method to extract the movie genre(s).
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's genres or None if not found.
        """
        div_genres = movie.find("div", {"class": "meta-body-item meta-body-info"})

        if div_genres:
            movie_genres = [
                genre.text
                for genre in div_genres.find_all(["a", "span"], class_=re.compile(r".*-link$"))
                if "\n" not in genre.text
            ]

            return ", ".join(movie_genres)

        return None

    @staticmethod
    def _get_movie_directors(movie: bs4.element.Tag) -> Optional[str]:
        """Private method to extract the movie director(s).
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's directores or None if not found.
        """
        div_directors = movie.find_all("div", {"class": "meta-body-item meta-body-direction meta-body-oneline"})

        if div_directors:
            movie_directors = [
                director.text for director in div_directors[0].find_all(["a", "span"], class_=re.compile(r".*-link$"))
            ]

            return ", ".join(movie_directors)

        return None

    @staticmethod
    def _get_movie_actors(movie: bs4.element.Tag) -> Optional[str]:
        """Private method to extract the movie actor(s).
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's actors or None if not found.
        """
        div_actors = movie.find("div", {"class": "meta-body-item meta-body-actor"})

        if div_actors:
            movie_actors = [actor.text for actor in div_actors.find_all(["a", "span"])][1:]

            return ", ".join(movie_actors)

        return None

    @staticmethod
    def _get_movie_nationality(movie: bs4.element.Tag) -> str:
        """Private method to extract the movie nationality.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
           The movie's nationalities or None if not found.
        """

        movie_nationality = [
            nationality.text.strip() for nationality in movie.find_all(["a", "span"], class_="nationality")
        ]

        return ", ".join(movie_nationality)

    @staticmethod
    def _get_movie_press_rating(movie: bs4.element.Tag) -> Optional[float]:
        """Private method to extract the movie rating according to the press.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's rating according to the press or None if not found.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:
            if "Presse" in ratings.text:
                return float(re.sub(",", ".", ratings.find("span", {"class": "stareval-note"}).text))
        return None

    @staticmethod
    def _get_movie_number_of_press_rating(movie: bs4.element.Tag) -> Optional[float]:
        """Private method to extract the number of ratings from the press.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's number of ratings from the press or None if not found.
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

    @staticmethod
    def _get_movie_spec_rating(movie: bs4.element.Tag) -> Optional[float]:
        """Private method to extract the movie rating according to the spectators.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's rating according to the spectators or None if not found.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:
            if "Spectateurs" in ratings.text:
                return float(re.sub(",", ".", ratings.find("span", {"class": "stareval-note"}).text))

        return None

    @staticmethod
    def _get_movie_number_of_spec_rating(movie: bs4.element.Tag) -> Optional[float]:
        """Private method to extract the number of ratings from the spectators.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's number of ratings according to the spectators or None if not found.
        """

        # get all the available ratings
        movie_ratings = movie.find_all("div", class_="rating-item")

        for ratings in movie_ratings:
            if "Spectateurs" in ratings.text:
                return float(
                    re.sub(
                        r"\D",
                        "",
                        (ratings.find("span", {"class": "stareval-review"}).text.split(",")[0]),
                    )
                )
        return None

    @staticmethod
    def _get_movie_summary(movie: bs4.element.Tag) -> Optional[str]:
        """Private method to extract the movie summary.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's summary or None if not found.
        """

        movie_summary = movie.find("section", {"class": "section ovw ovw-synopsis"}).find(
            "div", {"class": "content-txt"}
        )

        if movie_summary:
            movie_summary = movie_summary.text.strip()
            return unicodedata.normalize("NFKC", movie_summary)
        return None
