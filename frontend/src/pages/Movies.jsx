import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import './Movies.css';

const Movies = () => {
  const [movies, setMovies] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Simulate fetching movies from API
    const fetchMovies = () => {
      const mockMovies = [
        {
          id: 1,
          title: "Avengers: Endgame",
          genre: "Action",
          duration: "181 min",
          rating: "8.4",
          image: "https://via.placeholder.com/300x450/333/fff?text=Avengers"
        },
        {
          id: 2,
          title: "Spider-Man: No Way Home",
          genre: "Action",
          duration: "148 min", 
          rating: "8.2",
          image: "https://via.placeholder.com/300x450/333/fff?text=Spider-Man"
        },
        {
          id: 3,
          title: "The Batman",
          genre: "Action",
          duration: "176 min",
          rating: "7.8",
          image: "https://via.placeholder.com/300x450/333/fff?text=Batman"
        },
        {
          id: 4,
          title: "Dune",
          genre: "Sci-Fi",
          duration: "155 min",
          rating: "8.0",
          image: "https://via.placeholder.com/300x450/333/fff?text=Dune"
        },
        {
          id: 5,
          title: "Top Gun: Maverick",
          genre: "Action",
          duration: "130 min",
          rating: "8.3",
          image: "https://via.placeholder.com/300x450/333/fff?text=Top+Gun"
        },
        {
          id: 6,
          title: "Black Panther",
          genre: "Action",
          duration: "134 min",
          rating: "7.3",
          image: "https://via.placeholder.com/300x450/333/fff?text=Black+Panther"
        }
      ];
      setMovies(mockMovies);
    };

    fetchMovies();
  }, []);

  const handleMovieClick = (movie) => {
    navigate(`/booking/${movie.id}`, { state: { movie } });
  };

  return (
    <Layout>
      <div className="movies-page">
        <div className="movies-header">
          <h1 className="page-title">Movies</h1>
          <div className="movies-filters">
            <select className="filter-select">
              <option>All Genres</option>
              <option>Action</option>
              <option>Comedy</option>
              <option>Drama</option>
              <option>Horror</option>
              <option>Sci-Fi</option>
            </select>
            <input 
              type="text" 
              className="search-box" 
              placeholder="Search movies..."
            />
          </div>
        </div>
        <div className="movies-grid">
          {movies.map((movie) => (
            <div 
              key={movie.id} 
              className="movie-card"
              onClick={() => handleMovieClick(movie)}
            >
              <div className="movie-poster">
                <img src={movie.image} alt={movie.title} />
                <div className="movie-rating">
                  ⭐ {movie.rating}
                </div>
              </div>
              <div className="movie-info">
                <h3 className="movie-title">{movie.title}</h3>
                <p className="movie-genre">{movie.genre}</p>
                <p className="movie-duration">{movie.duration}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default Movies;