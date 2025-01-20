"""Command-line interface for the Allocine movie scraper.

This module provides a CLI interface to configure and run the Allocine
movie scraper with various options.
"""

from typing import Tuple

import click

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
def cli(
    number_of_pages: int = 10,  # Remove Optional as these have defaults
    from_page: int = 1,
    output_dir: str = "data",
    output_csv_name: str = "allocine_movies.csv",
    pause_scraping: Tuple[int, int] = (2, 10),  # Use proper tuple typing
    append_result: bool = False,
) -> None:
    """Run the Allocine movie scraper with specified parameters.

    Args:
        number_of_pages: Number of pages to scrape. Defaults to 10.
        from_page: First page number to scrape. Defaults to 1.
        output_dir: Directory to save the CSV file. Defaults to "data".
        output_csv_name: Name of the output CSV file. Defaults to "allocine_movies.csv".
        pause_scraping: Tuple of (min, max) seconds to pause between requests.
            Defaults to (2, 10).
        append_result: Whether to append to existing CSV file. Defaults to False.

    Example:
        To scrape 5 pages starting from page 2:
        $ python -m allocine_dataset_scraper.run --number_of_pages 5 --from_page 2
    """
    click.echo(f"{number_of_pages=}")
    click.echo(f"{from_page=}")
    click.echo(f"{output_dir=}")
    click.echo(f"{output_csv_name=}")
    click.echo(f"{pause_scraping=}")
    click.echo(f"{append_result=}")
    scraper = AllocineScraper(
        number_of_pages,
        from_page,
        output_dir,
        output_csv_name,
        list(pause_scraping),
        append_result,
    )

    scraper.scraping_movies()


if __name__ == "__main__":
    cli()
