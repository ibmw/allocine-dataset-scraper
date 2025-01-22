"""Configuration management for the Allocine scraper."""

from pathlib import Path
from typing import Tuple

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperConfig(BaseModel):
    """Configuration for the Allocine scraper.

    Attributes:
        number_of_pages: Number of pages to scrape
        from_page: First page to scrape from
        output_dir: Directory to save output files
        output_csv_name: Name of the CSV output file
        pause_scraping: Tuple of (min, max) seconds to pause between requests
        append_result: Whether to append to existing CSV file
    """

    number_of_pages: int = Field(default=10, gt=0, description="Number of pages to scrape")
    from_page: int = Field(default=1, gt=0, description="First page to scrape from")
    output_dir: Path = Field(default=Path("data"), description="Output directory path")
    output_csv_name: str = Field(default="allocine_movies.csv", pattern=r".*\.csv$", description="Output CSV filename")
    pause_scraping: Tuple[int, int] = Field(
        default=(2, 10), description="Min and max seconds to pause between requests"
    )
    append_result: bool = Field(default=False, description="Whether to append to existing CSV file")

    @field_validator("pause_scraping")
    def validate_pause_range(cls, v: Tuple[int, int]) -> Tuple[int, int]:
        """Validate that min pause is less than max pause."""
        if v[0] > v[1]:
            raise ValueError("Minimum pause must be less than maximum pause")
        return v

    @property
    def full_output_path(self) -> Path:
        """Get the full path to the output CSV file."""
        return self.output_dir / self.output_csv_name


class Settings(BaseSettings):
    """Global settings for the Allocine scraper.

    Attributes:
        base_url: Base URL for Allocine website
        user_agent: User agent string for requests
        log_level: Logging level
    """

    base_url: str = Field(default="http://www.allocine.fr/films/", description="Base URL for Allocine website")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User agent string for requests",
    )
    log_level: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Logging level"
    )

    model_config = SettingsConfigDict(
        env_prefix="ALLOCINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global instances
settings = Settings()
