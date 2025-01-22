"""Command-line interface for the Allocine movie scraper.

This module provides a CLI interface to configure and run the Allocine
movie scraper with various options.
"""

import click
from loguru import logger

from allocine_dataset_scraper.config import ScraperConfig, Settings
from allocine_dataset_scraper.scraper import AllocineScraper


@click.command()
@click.option(
    "--number_of_pages",
    default=10,
    help="Number of page to scrape.",
    show_default=True,
)
@click.option(
    "--from_page",
    default=1,
    help="First page to scrape.",
    show_default=True,
)
@click.option(
    "--output_dir",
    default="data",
    help="Directory name to output csv files.",
    show_default=True,
)
@click.option(
    "--output_csv_name",
    default="allocine_movies.csv",
    help="Output file name (save in a data directory).",
    show_default=True,
)
@click.option(
    "--pause_scraping",
    nargs=2,
    type=int,
    default=(2, 10),
    help="Range to randomize pauses.",
    show_default=True,
)
@click.option(
    "--append_result",
    is_flag=True,
    default=False,
    help="Append result to the output csv file",
    show_default=True,
)
def cli(**kwargs) -> None:
    """Run the Allocine movie scraper with specified parameters.

    This function runs the Allocine movie scraper to collect movie data from allocine.fr.
    It scrapes movie details like title, release date, duration, genres, directors, actors,
    ratings, etc. from the specified number of pages and saves them to a CSV file.

    Args:
        number_of_pages: Number of pages to scrape. Must be positive. Defaults to 10.
        from_page: First page number to scrape. Must be positive. Defaults to 1.
        output_dir: Directory to save the CSV file. Will be created if it doesn't exist.
            Defaults to "data".
        output_csv_name: Name of the output CSV file. Defaults to "allocine_movies.csv".
        pause_scraping: Tuple of (min, max) seconds to pause between requests to avoid
            rate limiting. Min must be less than max. Defaults to (2, 10).
        append_result: Whether to append to existing CSV file. If True and file doesn't
            exist, raises error. Defaults to False.

    Raises:
        click.BadParameter: If number_of_pages or from_page is less than 1, or if
            pause_scraping min is greater than max.
        FileNotFoundError: If append_result is True and the output file doesn't exist.
        requests.RequestException: If there are network issues during scraping.
        Exception: Any other unexpected errors during scraping.

    Example:
        To scrape 5 pages starting from page 2:
        $ python -m allocine_dataset_scraper.run --number_of_pages 5 --from_page 2

    Note:
        Uses random delays between requests to avoid overloading the server.
        All errors are logged to stderr before being re-raised.
    """
    try:
        config = ScraperConfig(**kwargs)

        click.echo("Starting AlloCine scraper with parameters:")
        click.echo(f"- Pages to scrape: {config.number_of_pages} (starting from {config.from_page})")
        click.echo(f"- Output: {config.full_output_path}")
        click.echo(f"- Pause between requests: {config.pause_scraping[0]}-{config.pause_scraping[1]}s")
        click.echo(f"- Mode: {'Append' if config.append_result else 'Overwrite'}")

        settings = Settings()
        scraper = AllocineScraper(config, settings=settings)
        scraper.scraping_movies()

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
