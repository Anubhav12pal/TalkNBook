import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';

const Booking = () => {
  const { movieId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const movie = location.state?.movie;

  const [selectedSeats, setSelectedSeats] = useState([]);
  const [bookedSeats, setBookedSeats] = useState(['A3', 'A4', 'B5', 'C2', 'D7']);
  const [showTimes] = useState(['10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM', '10:00 PM']);
  const [selectedTime, setSelectedTime] = useState('7:00 PM');

  useEffect(() => {
    if (!movie) {
      navigate('/movies');
    }
  }, [movie, navigate]);

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

  const totalPrice = selectedSeats.length * 12;

  const handleConfirmBooking = () => {
    if (selectedSeats.length === 0) {
      alert('Please select at least one seat');
      return;
    }
    
    const bookingDetails = {
      movie: movie.title,
      seats: selectedSeats,
      time: selectedTime,
      total: totalPrice
    };
    
    alert(`Booking confirmed!\n\nMovie: ${bookingDetails.movie}\nSeats: ${bookingDetails.seats.join(', ')}\nTime: ${bookingDetails.time}\nTotal: $${bookingDetails.total}`);
    
    navigate('/movies');
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
            {showTimes.map((time) => (
              <button
                key={time}
                onClick={() => setSelectedTime(time)}
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
                className="bg-brand-red text-white border-none rounded-lg px-6 py-3 md:px-8 md:py-4 cursor-pointer font-semibold transition-colors hover:bg-red-700 text-sm md:text-base"
              >
                Confirm Booking
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Booking;