from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query

from models.movie import MovieResponse
from services.movie_service import MovieService


router = APIRouter(prefix="/movies", tags=["movies"])
movie_service = MovieService()


@router.get("/", response_model=List[MovieResponse])
async def get_movies(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    search: Optional[str] = Query(None, description="Search movies by title or genre")
):
    """Get all movies with optional filtering."""
    try:
        if search:
            movies = movie_service.search_movies(search)
        elif genre and genre.lower() != "all genres":
            movies = movie_service.get_movies_by_genre(genre)
        else:
            movies = movie_service.get_all_movies()
        
        return [MovieResponse(**movie) for movie in movies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve movies"
        )


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: str):
    """Get a specific movie by ID."""
    movie = movie_service.get_movie_by_id(movie_id)
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return MovieResponse(**movie)