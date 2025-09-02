import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { bookingsAPI } from '../services/api';
import { AuthContext } from '../context/AuthContext';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
    if (!confirm('Are you sure you want to cancel this booking?')) {
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
                        onClick={() => handleCancelBooking(booking.id)}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default MyBookings;