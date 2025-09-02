const API_BASE_URL = 'http://localhost:8000';

// Get auth token from localStorage
const getAuthToken = () => {
  const token = localStorage.getItem('talknbook_token');
  return token ? `Bearer ${token}` : null;
};

// Generic API request handler
const apiRequest = async (url, options = {}) => {
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add auth token if available
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = token;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || 'API request failed');
  }
  
  return response.json();
};

// Auth API
export const authAPI = {
  login: async (email, password) => {
    return apiRequest('/auth/login-json', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  signup: async (username, email, password) => {
    return apiRequest('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
  },

  getCurrentUser: async () => {
    return apiRequest('/auth/me');
  },
};

// Movies API
export const moviesAPI = {
  getAllMovies: async (genre = null, search = null) => {
    const params = new URLSearchParams();
    if (genre && genre !== 'All Genres') params.append('genre', genre);
    if (search) params.append('search', search);
    
    const queryString = params.toString();
    const url = queryString ? `/movies?${queryString}` : '/movies';
    
    return apiRequest(url);
  },

  getMovieById: async (movieId) => {
    return apiRequest(`/movies/${movieId}`);
  },
};

// Bookings API
export const bookingsAPI = {
  createBooking: async (bookingData) => {
    return apiRequest('/bookings/', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  },

  getUserBookings: async () => {
    return apiRequest('/bookings/');
  },

  getBookedSeats: async (movieId, showtime) => {
    return apiRequest('/bookings/booked-seats', {
      method: 'POST',
      body: JSON.stringify({ movie_id: movieId, showtime }),
    });
  },

  getBookingById: async (bookingId) => {
    return apiRequest(`/bookings/${bookingId}`);
  },

  cancelBooking: async (bookingId) => {
    return apiRequest(`/bookings/${bookingId}`, {
      method: 'DELETE',
    });
  },
};