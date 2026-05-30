"""Validation layer for Allocine scraper data using Pydantic.

This module provides boundary constraints and validations for movie metadata
to flag corrupted, missing, or absurd values collected during scraping.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class MovieValidationModel(BaseModel):
    """Pydantic validation model for movie data fields."""

    id: int = Field(gt=0, description="Unique movie ID")
    title: str = Field(min_length=1, description="Movie title")
    release_date: Optional[datetime] = Field(default=None, description="Release date")
    duration: Optional[int] = Field(default=None, gt=0, lt=600, description="Duration in minutes")
    genres: Optional[str] = Field(default=None, description="Genres")
    directors: Optional[str] = Field(default=None, description="Directors")
    actors: Optional[str] = Field(default=None, description="Actors")
    nationality: Optional[str] = Field(default=None, description="Nationality")
    press_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Press rating")
    number_of_press_rating: Optional[float] = Field(default=None, ge=0.0, lt=1000.0, description="Press reviews count")
    spec_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Spectator rating")
    number_of_spec_rating: Optional[float] = Field(
        default=None, ge=0.0, lt=500000.0, description="Spectator reviews count"
    )
    summary: Optional[str] = Field(default=None, description="Movie summary")

    @field_validator("release_date")
    @classmethod
    def validate_release_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that the release date is reasonable (e.g. not before 1880 or far future)."""
        if v is not None:
            if v.year < 1880:
                raise ValueError("Release date cannot be before the birth of cinema (1880)")
            current_year = datetime.now().year
            if v.year > current_year + 5:
                raise ValueError("Release date cannot be more than 5 years in the future")
        return v


def validate_movie(movie_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate movie data and return any found validation errors.

    Args:
        movie_data: Flat dictionary containing movie data attributes.

    Returns:
        List of dictionaries detailing any validation errors found.
        Each dictionary contains: "field", "value", and "reason".
    """
    errors: List[Dict[str, Any]] = []
    try:
        MovieValidationModel(**movie_data)
    except Exception as e:
        # Check if it's a Pydantic ValidationError
        from pydantic import ValidationError

        if isinstance(e, ValidationError):
            for err in e.errors():
                field_name = str(err["loc"][0])
                errors.append(
                    {
                        "field": field_name,
                        "value": movie_data.get(field_name),
                        "reason": err["msg"],
                    }
                )
        else:  # pragma: no cover
            errors.append(
                {
                    "field": "unknown",
                    "value": None,
                    "reason": str(e),
                }
            )
    return errors
