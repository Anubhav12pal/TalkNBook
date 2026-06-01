import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from models.movie import Movie


class MovieService:
    """Service for managing movies using JSON file storage."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.movies_file = self.data_dir / "movies.json"
    
    def _load_movies(self) -> List[Dict[str, Any]]:
        """Load movies from JSON file."""
        try:
            with open(self.movies_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_all_movies(self) -> List[Dict[str, Any]]:
        """
        Get all movies.
        
        Returns:
            List of all movies
        """
        return self._load_movies()
    
    def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a movie by its ID.
        
        Args:
            movie_id: ID of the movie
            
        Returns:
            Movie dict if found, None otherwise
        """
        movies = self._load_movies()
        for movie in movies:
            if movie["id"] == movie_id:
                return movie
        return None
    
    def search_movies(self, query: str) -> List[Dict[str, Any]]:
        import re
        movies = self._load_movies()

        def normalize(s):
            # Remove all non-alphanumeric chars so "Spider-Man" -> "spiderman"
            return re.sub(r"[^a-z0-9]", "", s.lower())

        q = normalize(query)
        if not q:
            return []
        return [
            m for m in movies
            if q in normalize(m["title"]) or q in normalize(m["genre"])
        ]
    
    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """
        Get movies by genre.
        
        Args:
            genre: Genre to filter by
            
        Returns:
            List of movies in the genre
        """
        movies = self._load_movies()
        return [movie for movie in movies if movie["genre"].lower() == genre.lower()]