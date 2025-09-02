import { useState, useEffect, useContext } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { bookingsAPI, moviesAPI } from '../services/api';
import { AuthContext } from '../context/AuthContext';

const Booking = () => {
  const { movieId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  
  const [movie, setMovie] = useState(location.state?.movie || null);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [bookedSeats, setBookedSeats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTime, setSelectedTime] = useState('7:00 PM');

  // Fetch movie details if not provided via navigation
  const fetchMovieDetails = async () => {
    if (!movie && movieId) {
      try {
        const movieData = await moviesAPI.getMovieById(movieId);
        setMovie(movieData);
      } catch (err) {
        setError('Failed to load movie details');
        setTimeout(() => navigate('/movies'), 3000);
      }
    }
  };

  // Fetch booked seats for current movie and showtime
  const fetchBookedSeats = async () => {
    if (!movie) return;
    
    try {
      const data = await bookingsAPI.getBookedSeats(movie.id, selectedTime);
      setBookedSeats(data.booked_seats);
    } catch (err) {
      console.error('Failed to fetch booked seats:', err);
      setBookedSeats([]);
    }
  };

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    fetchMovieDetails();
  }, [movieId, user, navigate]);

  useEffect(() => {
    fetchBookedSeats();
  }, [movie, selectedTime]);

  if (!movie) {
    return null;
  }

  const rows = ['A', 'B', 'C', 'D', 'E', 'F'];
  const seatsPerRow = 8;

  const generateSeatId = (row, number) => `${row}${number}`;

  const handleSeatClick = (seatId) => {
    if (bookedSeats.includes(seatId)) return;

    setSelectedSeats(prev => 
      prev.includes(seatId) 
        ? prev.filter(id => id !== seatId)
        : [...prev, seatId]
    );
  };

  const getSeatStatus = (seatId) => {
    if (bookedSeats.includes(seatId)) return 'booked';
    if (selectedSeats.includes(seatId)) return 'selected';
    return 'available';
  };

  const totalPrice = selectedSeats.length * (movie?.price || 12);

  const handleConfirmBooking = async () => {
    if (selectedSeats.length === 0) {
      alert('Please select at least one seat');
      return;
    }

    if (!user) {
      alert('Please log in to make a booking');
      navigate('/login');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const bookingData = {
        movie_id: movie.id,
        movie_title: movie.title,
        showtime: selectedTime,
        seats: selectedSeats,
        total_price: totalPrice
      };
      
      await bookingsAPI.createBooking(bookingData);
      
      alert(`Booking confirmed!\n\nMovie: ${movie.title}\nSeats: ${selectedSeats.join(', ')}\nTime: ${selectedTime}\nTotal: $${totalPrice}`);
      
      navigate('/movies');
    } catch (err) {
      setError(err.message || 'Failed to create booking');
      alert(`Booking failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeChange = (newTime) => {
    setSelectedTime(newTime);
    setSelectedSeats([]); // Clear selected seats when changing time
  };

  return (
    <Layout>
      <div className="py-8 min-h-[calc(100vh-200px)]">
        <div className="flex items-center gap-6 mb-8">
          <button 
            onClick={() => navigate('/movies')}
            className="bg-gray-700 text-white border-none rounded-lg px-6 py-3 cursor-pointer text-base font-medium transition-all flex items-center gap-2 hover:bg-gray-600 hover:-translate-y-0.5"
          >
            ← Back to Movies
          </button>
          <h1 className="text-4xl font-bold text-white m-0">Book Your Seats</h1>
        </div>

        <div className="bg-dark-card rounded-xl p-4 mb-6 border border-dark-border">
          <h2 className="text-xl font-semibold text-white mb-2">{movie.title}</h2>
          <p className="text-gray-300 text-sm">{movie.genre} • {movie.duration}</p>
        </div>

        <div className="mb-8">
          <h3 className="text-white mb-4 text-lg">Select Showtime</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2 md:gap-4">
            {movie?.showtimes?.map((time) => (
              <button
                key={time}
                onClick={() => handleTimeChange(time)}
                className={`border border-dark-border rounded-lg px-4 py-3 md:py-4 cursor-pointer transition-all text-sm md:text-base ${
                  selectedTime === time 
                    ? 'bg-brand-red border-brand-red text-white' 
                    : 'bg-dark-card text-white hover:bg-dark-border'
                }`}
              >
                {time}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <h3 className="text-white mb-4 text-lg">Select Seats</h3>
          
          <div className="flex justify-center mb-8">
            <div className="bg-gradient-to-r from-dark-border via-gray-500 to-dark-border text-white px-8 py-2 rounded-2xl text-sm font-semibold text-center">
              SCREEN
            </div>
          </div>

          <div className="flex flex-col gap-2 mb-6 items-center">
            {rows.map((row) => (
              <div key={row} className="flex items-center gap-2 md:gap-4">
                <div className="w-6 text-center text-white font-semibold text-sm">{row}</div>
                <div className="flex gap-1 md:gap-2">
                  {Array.from({ length: seatsPerRow }, (_, index) => {
                    const seatNumber = index + 1;
                    const seatId = generateSeatId(row, seatNumber);
                    const status = getSeatStatus(seatId);
                    
                    return (
                      <button
                        key={seatId}
                        onClick={() => handleSeatClick(seatId)}
                        className={`w-8 h-8 md:w-10 md:h-10 border rounded text-xs md:text-sm cursor-pointer transition-all ${
                          status === 'available' 
                            ? 'bg-dark-card border-dark-border text-white hover:bg-dark-border hover:border-gray-500'
                            : status === 'selected'
                            ? 'bg-brand-red border-brand-red text-white'
                            : 'bg-gray-600 border-gray-600 text-gray-400 cursor-not-allowed'
                        }`}
                        disabled={status === 'booked'}
                      >
                        {seatNumber}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-center gap-4 mb-8 flex-wrap">
            <div className="flex items-center gap-1 text-white text-xs">
              <div className="w-4 h-4 bg-dark-card border border-dark-border rounded"></div>
              <span>Available</span>
            </div>
            <div className="flex items-center gap-1 text-white text-xs">
              <div className="w-4 h-4 bg-brand-red border border-brand-red rounded"></div>
              <span>Selected</span>
            </div>
            <div className="flex items-center gap-1 text-white text-xs">
              <div className="w-4 h-4 bg-gray-600 border border-gray-600 rounded"></div>
              <span>Booked</span>
            </div>
          </div>
        </div>

        {selectedSeats.length > 0 && (
          <div className="md:relative fixed bottom-0 left-0 right-0 md:static bg-dark-card border-t md:border md:border-dark-border md:rounded-xl p-4 md:mt-8 z-50">
            <div className="flex justify-between items-center max-w-5xl mx-auto">
              <div className="flex flex-col md:flex-row md:gap-8 gap-1 text-white text-sm md:text-base">
                <span>Selected Seats: {selectedSeats.join(', ')}</span>
                <span>Total: ${totalPrice}</span>
              </div>
              <button 
                onClick={handleConfirmBooking}
                disabled={loading}
                className={`text-white border-none rounded-lg px-6 py-3 md:px-8 md:py-4 cursor-pointer font-semibold transition-colors text-sm md:text-base ${
                  loading 
                    ? 'bg-gray-600 cursor-not-allowed' 
                    : 'bg-brand-red hover:bg-red-700'
                }`}
              >
                {loading ? 'Booking...' : 'Confirm Booking'}
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Booking;