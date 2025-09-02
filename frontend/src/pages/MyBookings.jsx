import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { bookingsAPI } from '../services/api';
import { AuthContext } from '../context/AuthContext';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSeats, setSelectedSeats] = useState({});
  const [showCancelModal, setShowCancelModal] = useState(null);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const fetchBookings = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await bookingsAPI.getUserBookings();
      setBookings(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, [user]);

  const handleCancelBooking = async (bookingId) => {
    if (!confirm('Are you sure you want to cancel this entire booking?')) {
      return;
    }

    try {
      await bookingsAPI.cancelBooking(bookingId);
      alert('Booking cancelled successfully');
      fetchBookings(); // Refresh the bookings list
    } catch (err) {
      alert(`Failed to cancel booking: ${err.message}`);
    }
  };

  const openCancelModal = (booking) => {
    setShowCancelModal(booking);
    setSelectedSeats({ [booking.id]: [] });
  };

  const closeCancelModal = () => {
    setShowCancelModal(null);
    setSelectedSeats({});
  };

  const toggleSeatSelection = (bookingId, seat) => {
    setSelectedSeats(prev => {
      const currentSeats = prev[bookingId] || [];
      const isSelected = currentSeats.includes(seat);
      
      return {
        ...prev,
        [bookingId]: isSelected 
          ? currentSeats.filter(s => s !== seat)
          : [...currentSeats, seat]
      };
    });
  };

  const handleCancelSelectedSeats = async () => {
    const bookingId = showCancelModal.id;
    const seatsToCancel = selectedSeats[bookingId] || [];

    if (seatsToCancel.length === 0) {
      alert('Please select at least one seat to cancel');
      return;
    }

    const confirmMessage = seatsToCancel.length === showCancelModal.seats.length 
      ? 'This will cancel all seats and the entire booking. Continue?'
      : `Cancel ${seatsToCancel.length} seat(s): ${seatsToCancel.join(', ')}?`;

    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      await bookingsAPI.cancelSeats(bookingId, seatsToCancel);
      alert('Seats cancelled successfully');
      closeCancelModal();
      fetchBookings(); // Refresh the bookings list
    } catch (err) {
      alert(`Failed to cancel seats: ${err.message}`);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'text-green-400';
      case 'cancelled':
        return 'text-red-400';
      default:
        return 'text-yellow-400';
    }
  };

  if (!user) {
    return (
      <Layout>
        <div className="py-8 text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Please Login</h1>
          <p className="text-gray-300 mb-8">You need to be logged in to view your bookings.</p>
          <button
            onClick={() => navigate('/login')}
            className="bg-brand-red text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
          >
            Go to Login
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">My Bookings</h1>
          <button
            onClick={() => navigate('/movies')}
            className="bg-brand-red text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
          >
            Book More Movies
          </button>
        </div>

        {loading && (
          <div className="text-center text-white py-8">
            <div className="text-lg">Loading your bookings...</div>
          </div>
        )}

        {error && (
          <div className="text-center text-red-400 py-8">
            <div className="text-lg">Failed to load bookings: {error}</div>
            <button 
              onClick={fetchBookings}
              className="mt-4 bg-brand-red text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && bookings.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <div className="text-lg mb-4">No bookings found</div>
            <p className="mb-8">You haven't made any movie bookings yet.</p>
            <button
              onClick={() => navigate('/movies')}
              className="bg-brand-red text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
            >
              Browse Movies
            </button>
          </div>
        )}

        {!loading && !error && bookings.length > 0 && (
          <div className="space-y-6">
            {bookings.map((booking) => (
              <div
                key={booking.id}
                className="bg-dark-card border border-dark-border rounded-xl p-6"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="text-xl font-semibold text-white">
                        {booking.movie_title}
                      </h3>
                      <span className={`text-sm font-medium ${getStatusColor(booking.status)}`}>
                        {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-300">
                      <div>
                        <span className="text-gray-500">Showtime:</span>
                        <div className="text-white">{booking.showtime}</div>
                      </div>
                      
                      <div>
                        <span className="text-gray-500">Seats:</span>
                        <div className="text-white">{booking.seats.join(', ')}</div>
                      </div>
                      
                      <div>
                        <span className="text-gray-500">Total:</span>
                        <div className="text-white font-semibold">${booking.total_price}</div>
                      </div>
                      
                      <div>
                        <span className="text-gray-500">Booked on:</span>
                        <div className="text-white">{formatDate(booking.booking_date)}</div>
                      </div>
                    </div>
                  </div>
                  
                  {booking.status === 'confirmed' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => openCancelModal(booking)}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                      >
                        Select Seats
                      </button>
                      <button
                        onClick={() => handleCancelBooking(booking.id)}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
                      >
                        Cancel All
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Seat Selection Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-dark-card border border-dark-border rounded-xl p-6 max-w-md w-full mx-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-white">
                  Select Seats to Cancel
                </h3>
                <button
                  onClick={closeCancelModal}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-300 mb-2">
                  Movie: <span className="text-white">{showCancelModal.movie_title}</span>
                </p>
                <p className="text-gray-300 mb-4">
                  Showtime: <span className="text-white">{showCancelModal.showtime}</span>
                </p>
                <p className="text-gray-300 mb-3">Select seats to cancel:</p>
                
                <div className="grid grid-cols-3 gap-2">
                  {showCancelModal.seats.map((seat) => {
                    const isSelected = selectedSeats[showCancelModal.id]?.includes(seat);
                    return (
                      <button
                        key={seat}
                        onClick={() => toggleSeatSelection(showCancelModal.id, seat)}
                        className={`
                          px-3 py-2 rounded text-sm font-medium transition-colors
                          ${isSelected 
                            ? 'bg-red-600 text-white' 
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }
                        `}
                      >
                        {seat}
                      </button>
                    );
                  })}
                </div>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={handleCancelSelectedSeats}
                  disabled={!selectedSeats[showCancelModal.id]?.length}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel Selected ({selectedSeats[showCancelModal.id]?.length || 0})
                </button>
                <button
                  onClick={closeCancelModal}
                  className="flex-1 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default MyBookings;