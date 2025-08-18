import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';

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
      <div className="py-8">
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <h1 className="text-4xl font-bold text-white m-0">Movies</h1>
          <div className="flex gap-4 items-center">
            <select className="bg-dark-card text-white border border-dark-border rounded-lg px-4 py-2 cursor-pointer text-sm focus:outline-none focus:border-brand-red">
              <option>All Genres</option>
              <option>Action</option>
              <option>Comedy</option>
              <option>Drama</option>
              <option>Horror</option>
              <option>Sci-Fi</option>
            </select>
            <input 
              type="text" 
              className="bg-dark-card text-white border border-dark-border rounded-lg px-4 py-2 text-sm w-52 focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Search movies..."
            />
          </div>
        </div>
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
      </div>
    </Layout>
  );
};

export default Movies;