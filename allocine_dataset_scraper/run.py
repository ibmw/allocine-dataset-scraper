from typing import Optional

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
    number_of_pages: Optional[int] = 10,
    from_page: Optional[int] = 1,
    output_dir: Optional[str] = "data",
    output_csv_name: Optional[str] = "allocine_movies.csv",
    pause_scraping: tuple = (2, 10),
    append_result: Optional[bool] = False,
) -> None:
    """Simple scraper that retrieve information about movie on AlloCine.fr."""
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
