"""Schema definitions for Allocine scraper and reporting DataFrames."""

from typing import Dict, List

MOVIE_SCHEMA: Dict[str, str] = {
    "id": "Int64",
    "title": "object",
    "release_date": "object",
    "duration": "Int64",
    "genres": "object",
    "directors": "object",
    "actors": "object",
    "nationality": "object",
    "press_rating": "float64",
    "number_of_press_rating": "float64",
    "spec_rating": "float64",
    "number_of_spec_rating": "float64",
    "summary": "object",
}

MOVIE_INFOS: List[str] = list(MOVIE_SCHEMA.keys())

REPORT_SCHEMA: Dict[str, str] = {
    "movie_id": "Int64",
    "movie_title": "object",
    "error_type": "object",
    "field": "object",
    "value": "object",
    "reason": "object",
    "retry_count": "Int64",
    "timestamp": "object",
}
