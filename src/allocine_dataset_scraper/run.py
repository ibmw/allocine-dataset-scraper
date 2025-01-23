"""Command-line interface for the Allocine movie scraper.

This module provides a CLI interface to configure and run the Allocine
movie scraper with various options. It handles parameter validation,
scraper initialization, and error reporting.

Functions:
    cli: Main CLI entry point that processes command line arguments.

Example:
    $ python -m allocine_dataset_scraper.run --number_of_pages 5 --from_page 1
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

    This function initializes and runs the Allocine movie scraper based on
    command line arguments. It handles configuration validation, scraper
    setup, and error reporting.

    Command Line Args:
        number_of_pages: Number of pages to scrape (default: 10)
        from_page: First page number to scrape (default: 1)
        output_dir: Directory to save results (default: "data")
        output_csv_name: Name of output CSV file (default: "allocine_movies.csv")
        pause_scraping: Min and max seconds between requests (default: 2 10)
        append_result: Whether to append to existing file (default: False)

    Raises:
        click.BadParameter: If any parameters are invalid
        FileNotFoundError: If append_result is True but file doesn't exist
        Exception: Any other unexpected errors during scraping

    Example:
        $ fetch-allocine --number_of_pages 5 --from_page 1
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
