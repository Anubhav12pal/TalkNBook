import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { moviesAPI } from '../services/api';

const Movies = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState('All Genres');
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const fetchMovies = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await moviesAPI.getAllMovies(selectedGenre, searchQuery);
      setMovies(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch movies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies();
  }, [selectedGenre, searchQuery]);

  const handleGenreChange = (e) => {
    setSelectedGenre(e.target.value);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleMovieClick = (movie) => {
    navigate(`/booking/${movie.id}`, { state: { movie } });
  };

  return (
    <Layout>
      <div className="py-8">
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <h1 className="text-4xl font-bold text-white m-0">Movies</h1>
          <div className="flex gap-4 items-center">
            <select 
              value={selectedGenre}
              onChange={handleGenreChange}
              className="bg-dark-card text-white border border-dark-border rounded-lg px-4 py-2 cursor-pointer text-sm focus:outline-none focus:border-brand-red"
            >
              <option>All Genres</option>
              <option>Action</option>
              <option>Comedy</option>
              <option>Drama</option>
              <option>Horror</option>
              <option>Sci-Fi</option>
            </select>
            <input 
              type="text" 
              value={searchQuery}
              onChange={handleSearchChange}
              className="bg-dark-card text-white border border-dark-border rounded-lg px-4 py-2 text-sm w-52 focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Search movies..."
            />
          </div>
        </div>
        
        {loading && (
          <div className="text-center text-white py-8">
            <div className="text-lg">Loading movies...</div>
          </div>
        )}

        {error && (
          <div className="text-center text-red-400 py-8">
            <div className="text-lg">Failed to load movies: {error}</div>
            <button 
              onClick={fetchMovies}
              className="mt-4 bg-brand-red text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && movies.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <div className="text-lg">No movies found</div>
          </div>
        )}

        {!loading && !error && movies.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-8 mb-8">
            {movies.map((movie) => (
              <div 
                key={movie.id} 
                className="bg-dark-card rounded-xl overflow-hidden cursor-pointer transition-all duration-200 border border-dark-border hover:-translate-y-2 hover:shadow-xl hover:shadow-black/30"
                onClick={() => handleMovieClick(movie)}
              >
                <div className="relative w-full aspect-[2/3]">
                  <img src={movie.image} alt={movie.title} className="w-full h-full object-cover" />
                  <div className="absolute top-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-semibold">
                    ⭐ {movie.rating}
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-white mb-1 leading-tight">{movie.title}</h3>
                  <p className="text-gray-300 text-sm mb-1">{movie.genre}</p>
                  <p className="text-gray-500 text-xs">{movie.duration}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Movies;