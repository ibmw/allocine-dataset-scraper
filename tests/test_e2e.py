"""End-to-end integration tests for the Allocine scraper.

These tests hit the live Allocine.fr website to ensure that the network clients,
HTML parsing structure, and file-writing modules integrate and work perfectly
against the current live site design.
"""

from pathlib import Path

import pandas as pd
import pytest

from allocine_dataset_scraper.config import ScraperConfig
from allocine_dataset_scraper.scraper import AllocineScraper


@pytest.mark.e2e
def test_scraping_movies_e2e(tmp_path):
    """Run an end-to-end scrape of one page from Allocine.fr without mocks.

    Verifies that the HTTP requests connect successfully, the HTML parsing logic
    is completely valid against the live layout, and movies are successfully
    extracted and written to the CSV file.
    """
    output_dir = tmp_path / "data"
    output_csv = "allocine_movies_e2e.csv"

    config = ScraperConfig(
        number_of_pages=1,
        from_page=1,
        output_dir=output_dir,
        output_csv_name=output_csv,
        pause_scraping=(1, 3),  # Be polite, but quick for testing
        append_result=False,
        auto_retry=False,
    )

    scraper = AllocineScraper(config)
    
    # Run the full scraping process unmocked
    scraper.scraping_movies()

    # Assertions
    full_csv_path = config.full_output_path
    assert full_csv_path.exists(), f"E2E Output CSV was not created at {full_csv_path}"

    df = pd.read_csv(full_csv_path)
    assert len(df) > 0, "No movies were scraped or written to the CSV file"
    assert "id" in df.columns, "Output CSV is missing the 'id' column"
    assert "title" in df.columns, "Output CSV is missing the 'title' column"

    # Verify we successfully parsed titles for the movies
    assert not bool(df["title"].isna().all()), "All scraped movie titles were parsed as NaN"
    assert not bool(df["id"].isna().all()), "All scraped movie IDs were parsed as NaN"
