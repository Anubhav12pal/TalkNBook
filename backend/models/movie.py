from pydantic import BaseModel
from typing import List


class Movie(BaseModel):
    """Model for movie data."""
    id: str
    title: str
    genre: str
    duration: str
    rating: str
    description: str
    image: str
    showtimes: List[str]
    price: float


class MovieResponse(BaseModel):
    """Model for movie response."""
    id: str
    title: str
    genre: str
    duration: str
    rating: str
    description: str
    image: str
    showtimes: List[str]
    price: float