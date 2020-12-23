import click

from allocine_dataset_scraper.allocine_dataset_scraper import AllocineScraper


@click.command()
@click.option("--number_of_pages", default=10, help="Number of page to scrape.")
@click.option("--from_page", default=1, help="First page to scrape.")
@click.option(
    "--output_csv_name", default="allocine_movies.csv", help="Output file name."
)
@click.option("--pause_scraping", default=[2, 10], help="Range to randomize pause.")
def exec_cli(
    number_of_pages: int, from_page: int, output_csv_name: str, pause_scraping: list
):
    """Simple program that greets NAME for a total of COUNT times."""
    scraper = AllocineScraper(
        number_of_pages, from_page, output_csv_name, pause_scraping
    )

    scraper.scraping_movies()


if __name__ == "__main__":
    exec_cli()
