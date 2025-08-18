import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import './Booking.css';

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
      <div className="booking-page">
        <div className="booking-header">
          <button 
            onClick={() => navigate('/movies')}
            className="back-button"
          >
            ← Back to Movies
          </button>
          <h1 className="page-title">Book Your Seats</h1>
        </div>

        <div className="movie-details">
          <h2 className="movie-title">{movie.title}</h2>
          <p className="movie-info">{movie.genre} • {movie.duration}</p>
        </div>

        <div className="showtime-section">
          <h3>Select Showtime</h3>
          <div className="showtime-grid">
            {showTimes.map((time) => (
              <button
                key={time}
                onClick={() => setSelectedTime(time)}
                className={`showtime-button ${selectedTime === time ? 'selected' : ''}`}
              >
                {time}
              </button>
            ))}
          </div>
        </div>

        <div className="seating-section">
          <h3>Select Seats</h3>
          
          <div className="screen-indicator">
            <div className="screen">SCREEN</div>
          </div>

          <div className="seating-chart">
            {rows.map((row) => (
              <div key={row} className="seat-row">
                <div className="row-label">{row}</div>
                <div className="seats">
                  {Array.from({ length: seatsPerRow }, (_, index) => {
                    const seatNumber = index + 1;
                    const seatId = generateSeatId(row, seatNumber);
                    const status = getSeatStatus(seatId);
                    
                    return (
                      <button
                        key={seatId}
                        onClick={() => handleSeatClick(seatId)}
                        className={`seat ${status}`}
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

          <div className="seat-legend">
            <div className="legend-item">
              <div className="seat available small"></div>
              <span>Available</span>
            </div>
            <div className="legend-item">
              <div className="seat selected small"></div>
              <span>Selected</span>
            </div>
            <div className="legend-item">
              <div className="seat booked small"></div>
              <span>Booked</span>
            </div>
          </div>
        </div>

        {selectedSeats.length > 0 && (
          <div className="booking-summary">
            <div className="summary-content">
              <div className="selected-info">
                <span>Selected Seats: {selectedSeats.join(', ')}</span>
                <span>Total: ${totalPrice}</span>
              </div>
              <button 
                onClick={handleConfirmBooking}
                className="confirm-button"
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