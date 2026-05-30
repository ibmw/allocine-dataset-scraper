"""Module for scraping movie information from Allocine.fr website.

This module provides functionality to scrape movie data including titles, ratings,
cast information, and other metadata from the Allocine.fr website. The scraper
handles pagination, rate limiting, and data export to CSV format.

Classes:
    AllocineScraper: Main scraper class that handles all scraping operations.

Example:
    >>> from allocine_dataset_scraper.scraper import AllocineScraper
    >>> from allocine_dataset_scraper.config import ScraperConfig
    >>> config = ScraperConfig(number_of_pages=5)
    >>> scraper = AllocineScraper(config)
    >>> scraper.scraping_movies()
"""

import datetime
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from random import randrange
from typing import Any, Dict, List, Optional, Union

import bs4
import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm.auto import tqdm

from allocine_dataset_scraper.config import ScraperConfig, Settings, settings
from allocine_dataset_scraper.validation import validate_movie

logger.remove()
logger.add("scraper.log", rotation="100 MB")
logger.add(sys.stderr, level=settings.log_level)


class AllocineScraper:
    """A scraper for collecting movie information from Allocine.fr.

    This class handles the scraping of movie information from Allocine.fr,
    including pagination, data parsing, and CSV export functionality. It implements
    rate limiting and can either create new datasets or append to existing ones.

    Attributes:
        movie_infos (List[str]): List of movie attributes to collect.
        df (pd.DataFrame): DataFrame storing the collected movie information.
        config (ScraperConfig): Configuration object containing scraping parameters.
        settings (Settings): Settings object containing global settings.
        exclude_ids (List[int]): List of movie IDs to skip during scraping.

    Example:
        >>> config = ScraperConfig(number_of_pages=5)
        >>> scraper = AllocineScraper(config)
        >>> scraper.scraping_movies()
    """

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

    df: pd.DataFrame = pd.DataFrame(columns=movie_infos)  # type: ignore

    def __init__(self, config: ScraperConfig, settings: Settings = settings) -> None:
        """Initialize the Allocine scraper.

        Args:
            config: Scraper configuration object
            settings: Optional settings object. If None, uses global settings.

        Raises:
            FileNotFoundError: If append_result is True and the CSV file doesn't exist.
        """
        self.config = config
        self.settings = settings
        self.exclude_ids: List[int] = []
        self.staged_errors: List[Dict[str, Any]] = []

        logger.info("Initializing Allocine Scraper...")
        logger.info(f"- Number of pages to scrap: {self.config.number_of_pages}")
        logger.info(
            f"""- Time to wait between pages between:
            {self.config.pause_scraping[0]} sec and {self.config.pause_scraping[1]} sec"""
        )
        logger.info(f"- Results will be stored in: <{self.config.full_output_path}>")

        if self.config.append_result:
            try:
                self.df = pd.read_csv(self.config.full_output_path)
                self.exclude_ids = self.df["id"].dropna().astype(int).tolist()  # type: ignore
                logger.info(
                    f"""- The list to exclude movies already fetch has been initialize
                    -- Total movie listed: {len(self.exclude_ids)}"""
                )
            except Exception as ex:
                logger.error(f"Failed to load the csv {self.config.full_output_path} -- {ex}")
                raise FileNotFoundError(f"Failed to load the csv {self.config.full_output_path} -- {ex}")

    def _get_page(self, page_number: int) -> requests.Response:
        """Fetch a movie listing page from Allocine.fr.

        Makes an HTTP GET request to retrieve a page of movie listings.
        Includes rate limiting and user agent spoofing for politeness.

        Args:
            page_number: The page number to fetch (1-based indexing).

        Returns:
            Response object containing the page content.

        Raises:
            requests.RequestException: If the page fetch fails due to network/HTTP errors.
        """
        headers = {"User-Agent": self.settings.user_agent}
        url = f"{self.settings.base_url}?page={page_number}"
        response = requests.get(url, headers=headers, timeout=self.settings.request_timeout)  # pragma: no cover
        return response

    def _get_movie(self, url: str) -> requests.Response:
        """Fetch a specific movie page from Allocine.fr.

        Makes an HTTP GET request to retrieve detailed information about a specific movie.
        Includes rate limiting and user agent spoofing for politeness.

        Args:
            url: The relative URL path to the movie page.

        Returns:
            Response object containing the movie page content.

        Raises:
            requests.RequestException: If the page fetch fails due to network/HTTP errors.
        """
        from urllib.parse import urljoin
        headers = {"User-Agent": self.settings.user_agent}
        full_url = urljoin(self.settings.base_url, url)
        response = requests.get(
            full_url, headers=headers, timeout=self.settings.request_timeout
        )  # pragma: no cover
        return response

    def _randomize_waiting_time(self) -> int:
        """Generate a random waiting time within the configured range.

        Used to implement polite scraping by adding random delays between requests.
        The range is specified in the scraper configuration.

        Returns:
            Number of seconds to wait, randomly chosen from the configured range.
        """
        return randrange(*self.config.pause_scraping)

    @staticmethod
    def _create_directory_if_not_exist(path_dir: Union[str, Path]) -> None:
        """Create a directory if it doesn't exist.

        Ensures the output directory exists before attempting to save files.
        Creates parent directories as needed.

        Args:
            path_dir: Path to the directory to create.

        Raises:
            OSError: If directory creation fails due to permissions or other IO errors.
        """
        if not os.path.exists(path_dir):
            logger.info(f"{path_dir} doesn't exist. We try to create it...")
            try:
                os.makedirs(path_dir)
            except Exception as ex:  # pragma: no cover
                logger.error(f"Failed to create {path_dir}: {ex}")
                raise OSError(f"Failed to create {path_dir}: {ex}")

    def _parse_page(self, page: requests.Response) -> List[str]:
        """Parse a movie listing page to extract movie URLs.

        Extracts all movie URLs from a listing page. If append mode is enabled,
        filters out movies that have already been scraped.

        Args:
            page: Response object containing the page content.

        Returns:
            List of relative URL paths to individual movie pages.
        """

        parser = BeautifulSoup(page.content, "html.parser")  # type: ignore
        urls = [url.a["href"] for url in parser.find_all("h2", class_="meta-title")]

        if self.config.append_result and self.exclude_ids:
            ori_urls_len = len(urls)
            urls = [url for url in urls if int(url.split("=")[-1].split(".")[0]) not in self.exclude_ids]
            urls_len = len(urls)
            logger.info(
                f"""{ori_urls_len - urls_len} / {ori_urls_len}
                movies has already been scraped"""
            )

        return urls

    def _parse_movie(self, page: requests.Response) -> None:
        """Parse a movie page and store the extracted information.

        Extracts all available movie information and stores it in the DataFrame.
        Automatically saves the updated DataFrame to CSV after each movie.

        Args:
            page: Response object containing the movie page content.
        """
        parser = BeautifulSoup(page.content, "html.parser")  # type: ignore
        parser_movie = parser.find("main", {"id": "content-layout"})

        if parser_movie is None:
            logger.error("Could not find 'content-layout' main element in movie page. Skipping.")
            m_id = 0
            if page.url:
                url_part = page.url.split("=")[-1].split(".")[0]
                try:
                    m_id = int(re.sub(r"\D", "", url_part))
                except Exception:
                    pass
            self.staged_errors.append(
                {
                    "movie_id": m_id,
                    "movie_title": f"Unknown (URL: {page.url})",
                    "error_type": "SCRAPE_FAILED",
                    "field": "page",
                    "value": "None",
                    "reason": "Could not find 'content-layout' main element",
                    "retry_count": 0,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            return

        self._create_directory_if_not_exist(self.config.output_dir)

        movie_datas: Dict = {}

        for info in self.movie_infos:
            try:
                scraped_info = getattr(self, "_get_movie_" + info)(parser_movie)
            except Exception as ex:  # pragma: no cover
                logger.error(f"<id:{movie_datas.get('id')}, info:{info}>: {ex}")
                scraped_info = None

            movie_datas[info] = [scraped_info]

        # Validate movie data
        flat_data = {k: v[0] for k, v in movie_datas.items()}
        validation_errors = validate_movie(flat_data)
        if validation_errors:
            logger.warning(f"Movie {flat_data.get('id')} ({flat_data.get('title')}) failed data validation:")
            for err in validation_errors:
                logger.warning(f"  - {err['field']}: {err['reason']} (value: {err['value']})")
                self.staged_errors.append(
                    {
                        "movie_id": flat_data.get("id", 0),
                        "movie_title": flat_data.get("title", "Unknown"),
                        "error_type": "BAD_DATA",
                        "field": err["field"],
                        "value": str(err["value"]),
                        "reason": err["reason"],
                        "retry_count": 0,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

        self.df = (
            pd.concat([self.df, pd.DataFrame(movie_datas)], ignore_index=True)
            if not self.df.empty
            else pd.DataFrame(movie_datas, columns=self.movie_infos)  # type: ignore
        ).drop_duplicates(subset=["id"], keep="last")

        self.df.to_csv(f"{self.config.full_output_path}", index=False)

    def scraping_movies(self) -> None:
        """Execute the movie scraping process.

        This method orchestrates the entire scraping process, including:
        - Fetching listing pages
        - Extracting movie URLs
        - Fetching and parsing individual movie pages
        - Saving results to CSV
        """
        if self.config.retry_errors:
            self.retry_failed_movies()
            return

        # Ensure directory is created or writeable before wasting requests
        self._create_directory_if_not_exist(self.config.output_dir)

        logger.info("Starting scraping movies from Allocine...")

        for number in tqdm(
            range(self.config.from_page, self.config.from_page + self.config.number_of_pages), desc="Pages"
        ):
            logger.info(f"Fetching Page {number}/{self.config.from_page + self.config.number_of_pages}")
            time.sleep(self._randomize_waiting_time())
            try:
                res_page = self._get_page(number)
                urls_to_parse = self._parse_page(res_page)
            except Exception as e:
                logger.error(f"Failed to fetch or parse listing page {number}: {e}")
                continue

            for url in tqdm(
                urls_to_parse,
                desc="Movies",
                leave=(number == (self.config.from_page + self.config.number_of_pages - 1)),
            ):
                logger.info(f"Fetching Movie {url}")
                url_id = int(url.split("=")[-1].split(".")[0])
                try:
                    res_movie = self._get_movie(url)
                except Exception as e:
                    logger.error(f"Failed to fetch movie {url}: {e}")
                    self.staged_errors.append(
                        {
                            "movie_id": url_id,
                            "movie_title": f"Unknown (URL: {url})",
                            "error_type": "SCRAPE_FAILED",
                            "field": "page",
                            "value": "None",
                            "reason": f"Request/fetch failed: {str(e)}",
                            "retry_count": 0,
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
                    continue

                self._parse_movie(res_movie)

                if url_id not in self.exclude_ids:
                    self.exclude_ids.append(url_id)

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

        # Write all staged errors to data_quality_report.csv
        if self.staged_errors:
            self._write_staged_errors()

        # Automatic end-of-run retry
        if self.config.auto_retry:
            report_path = self.config.full_quality_report_path
            if report_path.exists():
                try:
                    df_report = pd.read_csv(report_path)
                    fresh_failed_series = df_report[df_report["retry_count"] == 0]["movie_id"]  # type: ignore
                    fresh_failed_ids: List[int] = sorted(list({int(x) for x in fresh_failed_series if pd.notna(x)}))
                    if fresh_failed_ids:
                        logger.info(
                            f"Auto-retry enabled: Retrying {len(fresh_failed_ids)} movie(s) that failed in this run..."
                        )
                        self.retry_failed_movies(fresh_failed_ids)
                except Exception as e:  # pragma: no cover
                    logger.error(f"Failed to check for auto-retry movies: {e}")

        logger.info("Done scraping Allocine.")
        logger.info(f"Results are stored in {self.config.output_csv_name}.")

    def _write_staged_errors(self) -> None:
        """Write self.staged_errors to the quality report CSV, preserving existing retry_counts."""
        if not self.staged_errors:
            return

        self._create_directory_if_not_exist(self.config.output_dir)
        report_path = self.config.full_quality_report_path

        existing_report = pd.DataFrame()
        if report_path.exists():
            try:
                existing_report = pd.read_csv(report_path)
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to read existing quality report at {report_path}: {e}")

        new_errors_df = pd.DataFrame(self.staged_errors)

        if not existing_report.empty:
            for idx, row in new_errors_df.iterrows():
                match = existing_report[
                    (existing_report["movie_id"] == row["movie_id"]) & (existing_report["field"] == row["field"])
                ]
                if not match.empty:
                    new_errors_df.at[idx, "retry_count"] = int(match.iloc[0]["retry_count"])

            combined = pd.concat([existing_report, new_errors_df], ignore_index=True)
            final_report = combined.drop_duplicates(subset=["movie_id", "field"], keep="last")
        else:
            final_report = new_errors_df.drop_duplicates(subset=["movie_id", "field"], keep="last")

        try:
            final_report.to_csv(report_path, index=False)
            logger.info(f"Data quality report updated at: <{report_path}>")
        except Exception as e:  # pragma: no cover
            logger.error(f"Failed to write data quality report to {report_path}: {e}")

        self.staged_errors = []

    def retry_failed_movies(self, movie_ids: Optional[List[int]] = None) -> None:
        """Retry scraping failed or corrupted movies.

        Args:
            movie_ids: Optional list of movie IDs to retry.
                       If None, loads them from the quality report CSV.
        """
        report_path = self.config.full_quality_report_path

        if movie_ids is None:
            if not report_path.exists():
                logger.info(f"No quality report found at {report_path}. Nothing to retry.")
                return
            try:
                df_report = pd.read_csv(report_path)
                if df_report.empty:
                    logger.info("Quality report is empty. Nothing to retry.")
                    return
                df_to_retry = df_report[df_report["retry_count"] < self.config.max_retries]
                if df_to_retry.empty:
                    logger.info(
                        f"All reported movies have reached the maximum retry limit of {self.config.max_retries}."
                    )
                    return
                movie_ids = df_to_retry["movie_id"].unique().tolist()  # type: ignore
            except Exception as e:  # pragma: no cover
                logger.error(f"Failed to load movie IDs from quality report: {e}")
                return

        if not movie_ids:
            logger.info("No movie IDs to retry.")
            return

        logger.info(f"Starting retry phase for {len(movie_ids)} movie(s)...")

        for m_id in tqdm(movie_ids, desc="Retrying Movies"):
            movie_url = f"/film/fichefilm_gen_cfilm={m_id}.html"
            logger.info(f"Retrying Movie ID: {m_id} via URL: {movie_url}")

            time.sleep(self._randomize_waiting_time())

            try:
                res_movie = self._get_movie(movie_url)

                self._parse_movie(res_movie)

                staged_for_this_movie = [err for err in self.staged_errors if err["movie_id"] == m_id]

                if not staged_for_this_movie:
                    logger.info(f"Successfully corrected Movie ID: {m_id}!")
                    if report_path.exists():
                        try:
                            df_report = pd.read_csv(report_path)
                            df_report = df_report[df_report["movie_id"] != m_id]
                            df_report.to_csv(report_path, index=False)
                        except Exception as e:  # pragma: no cover
                            logger.error(f"Failed to remove resolved movie {m_id} from quality report: {e}")
                    if m_id not in self.exclude_ids:
                        self.exclude_ids.append(m_id)
                else:
                    logger.warning(f"Retry failed for Movie ID: {m_id}. Errors persist.")
                    if report_path.exists():
                        try:
                            df_report = pd.read_csv(report_path)
                            for err in staged_for_this_movie:
                                match = df_report[
                                    (df_report["movie_id"] == m_id) & (df_report["field"] == err["field"])
                                ]
                                existing_count = int(match.iloc[0]["retry_count"]) if not match.empty else 0
                                err["retry_count"] = existing_count + 1

                            new_err_df = pd.DataFrame(staged_for_this_movie)
                            combined = pd.concat([df_report, new_err_df], ignore_index=True)
                            final_report = combined.drop_duplicates(subset=["movie_id", "field"], keep="last")
                            final_report.to_csv(report_path, index=False)
                        except Exception as e:  # pragma: no cover
                            logger.error(f"Failed to update retry counts in quality report: {e}")
                    else:  # pragma: no cover
                        for err in staged_for_this_movie:
                            err["retry_count"] = 1
                        self._write_staged_errors()

                self.staged_errors = [err for err in self.staged_errors if err["movie_id"] != m_id]

            except Exception as e:
                logger.error(f"Exception during retry of Movie ID {m_id}: {e}")
                scrape_err = {
                    "movie_id": m_id,
                    "movie_title": f"Unknown (ID: {m_id})",
                    "error_type": "SCRAPE_FAILED",
                    "field": "page",
                    "value": "None",
                    "reason": f"Retry failed: {str(e)}",
                    "retry_count": 0,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                if report_path.exists():
                    try:
                        df_report = pd.read_csv(report_path)
                        match = df_report[(df_report["movie_id"] == m_id) & (df_report["field"] == "page")]
                        existing_count = int(match.iloc[0]["retry_count"]) if not match.empty else 0
                        scrape_err["retry_count"] = existing_count + 1

                        new_err_df = pd.DataFrame([scrape_err])
                        combined = pd.concat([df_report, new_err_df], ignore_index=True)
                        final_report = combined.drop_duplicates(subset=["movie_id", "field"], keep="last")
                        final_report.to_csv(report_path, index=False)
                    except Exception as ex:  # pragma: no cover
                        logger.error(f"Failed to log retry page failure: {ex}")
                else:  # pragma: no cover
                    scrape_err["retry_count"] = 1
                    self.staged_errors.append(scrape_err)
                    self._write_staged_errors()

    @staticmethod
    def _get_movie_id(movie: bs4.element.Tag) -> int:
        """Private method to extract the movie ID from the movie page.

        Args:
            movie: BeautifulSoup Tag object containing movie information.

        Returns:
            The movie's unique identifier.
        """

        span = movie.find("span", {"class": "home"})
        href = span["href"] if span and span.has_attr("href") else ""
        movie_id = re.sub(r"\D", "", href)

        return int(movie_id)

    @staticmethod
    def _get_movie_title(movie: bs4.element.Tag) -> str:
        """Private method to extract the movie title from the movie page.

        Args:
            movie: BeautifulSoup Tag object containing movie information.

        Returns:
            The movie's title.
        """

        title_div = movie.find("div", {"class": "titlebar-title"})
        movie_title = title_div.text.strip() if title_div else ""

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

        spacer = movie.find("span", {"class": "spacer"})
        sibling = spacer.next_sibling if spacer else None
        duration_str = sibling.strip() if sibling and isinstance(sibling, str) else ""
        if duration_str != "":
            duration_timedelta = pd.to_timedelta(duration_str).components  # type: ignore
            return duration_timedelta.hours * 60 + duration_timedelta.minutes

        return None

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
                review_span = ratings.find("span", {"class": "stareval-review"})
                if review_span:
                    text = review_span.text
                    match = re.search(r"^\s*([\d\s\xa0\u202f]+)", text)
                    if match:
                        return float(re.sub(r"\D", "", match.group(1)))
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
                review_span = ratings.find("span", {"class": "stareval-review"})
                if review_span:
                    text = review_span.text
                    match = re.search(r"^\s*([\d\s\xa0\u202f]+)", text)
                    if match:
                        return float(re.sub(r"\D", "", match.group(1)))
        return None

    @staticmethod
    def _get_movie_summary(movie: bs4.element.Tag) -> Optional[str]:
        """Private method to extract the movie summary.
        Args:
            movie: BeautifulSoup Tag object containing movie information.
        Returns:
            The movie's summary or None if not found.
        """

        synopsis_sec = movie.find("section", {"class": "section ovw ovw-synopsis"})
        movie_summary = synopsis_sec.find("div", {"class": "content-txt"}) if synopsis_sec else None

        if movie_summary:
            movie_summary = movie_summary.text.strip()
            return unicodedata.normalize("NFKC", movie_summary)
        return None
