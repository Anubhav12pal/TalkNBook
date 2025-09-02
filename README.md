# TalkNBook - Movie Ticket Booking System

A full-stack movie ticket booking application built with FastAPI (Python) backend and React (Vite) frontend.

## 🎬 Features

- **User Authentication**: Secure login/signup with JWT tokens
- **Movie Browsing**: View movies with ratings, genres, and showtimes
- **Seat Selection**: Interactive seat map with real-time availability
- **Booking Management**: Create, view, and manage movie bookings
- **Selective Cancellation**: Cancel individual seats or entire bookings
- **Search & Filter**: Find movies by title or filter by genre
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with JSON file database
- **Frontend**: React with Vite, TailwindCSS for styling
- **Authentication**: JWT tokens with secure session management
- **Data Storage**: JSON files for users, movies, and bookings

## 📁 Project Structure

```
TalkNBook/
├── backend/
│   ├── data/
│   │   ├── users.json          # User accounts
│   │   ├── movies.json         # Movie database
│   │   └── bookings.json       # Booking records
│   ├── models/
│   │   ├── user.py            # User data models
│   │   ├── movie.py           # Movie data models
│   │   └── booking.py         # Booking data models
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── movies.py          # Movie endpoints
│   │   └── bookings.py        # Booking endpoints
│   ├── services/
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── movie_service.py   # Movie business logic
│   │   └── booking_service.py # Booking business logic
│   ├── virtual/               # Python virtual environment
│   └── main.py               # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # React context providers
│   │   ├── pages/            # Main application pages
│   │   ├── services/         # API service layer
│   │   └── App.jsx          # Main React component
│   └── package.json         # Frontend dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Activate virtual environment**
   ```bash
   source virtual/bin/activate
   ```

3. **Install dependencies** (if needed)
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies** (if needed)
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:5173

## 🔑 API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login-json` - Login with email/password
- `GET /auth/me` - Get current user info

### Movies
- `GET /movies/` - Get all movies (with optional genre/search filters)
- `GET /movies/{movie_id}` - Get specific movie details

### Bookings
- `POST /bookings/` - Create new booking (authenticated)
- `GET /bookings/` - Get user's bookings (authenticated)
- `POST /bookings/booked-seats` - Get booked seats for movie/showtime
- `GET /bookings/{booking_id}` - Get specific booking (authenticated)
- `DELETE /bookings/{booking_id}` - Cancel entire booking (authenticated)
- `POST /bookings/{booking_id}/cancel-seats` - Cancel specific seats (authenticated)

## 🎭 Usage

1. **Sign up** for a new account or **login** with existing credentials
2. **Browse movies** on the main page, filter by genre or search by title
3. **Click on a movie** to view showtimes and book tickets
4. **Select your seats** from the interactive seat map
5. **Confirm your booking** and view it in "My Bookings"
6. **Manage bookings** - view history, cancel individual seats, or cancel entire bookings

## 🧪 Test Users

The system includes a test user for demonstration:
- **Email**: test@example.com
- **Password**: testpassword

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **JWT** - Secure authentication tokens
- **bcrypt** - Password hashing
- **JSON** - File-based data storage

### Frontend
- **React** - UI library
- **Vite** - Build tool and development server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing

## 📊 Database Schema

### Users
```json
{
  "id": "unique-uuid",
  "username": "string",
  "email": "email@example.com",
  "hashed_password": "bcrypt-hash",
  "created_at": "2025-01-01T00:00:00"
}
```

### Movies
```json
{
  "id": "movie-1",
  "title": "Movie Title",
  "genre": "Action",
  "duration": "120 min",
  "rating": "8.5",
  "description": "Movie description",
  "image": "image-url",
  "showtimes": ["10:00 AM", "1:00 PM", "4:00 PM", "7:00 PM", "10:00 PM"],
  "price": 12.0
}
```

### Bookings
```json
{
  "id": "unique-uuid",
  "user_id": "user-uuid",
  "movie_id": "movie-1",
  "movie_title": "Movie Title",
  "showtime": "7:00 PM",
  "seats": ["A1", "A2"],
  "total_price": 24.0,
  "booking_date": "2025-01-01T00:00:00",
  "status": "confirmed"
}
```

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Pydantic models validate all API inputs
- **CORS Protection**: Configured for frontend domain only
- **Session Management**: Tokens stored securely in localStorage

## 🎨 UI Features

- **Responsive Design**: Works on all device sizes
- **Dark Theme**: Modern dark UI with brand colors
- **Interactive Elements**: Hover effects and smooth transitions
- **Real-time Updates**: Seat availability updates in real-time
- **User Feedback**: Loading states and error handling
- **Selective Cancellation Modal**: Interactive seat selection for partial cancellation

## ✨ Selective Seat Cancellation

The booking system supports granular seat management, allowing users to cancel individual seats from their bookings:

### Features
- **Individual Seat Selection**: Click on specific seats to toggle selection in the cancellation modal
- **Partial Cancellation**: Cancel only some seats while keeping others active
- **Price Recalculation**: Booking price automatically updates based on remaining seats  
- **Full Cancellation**: If all seats are cancelled, the booking status changes to "cancelled"
- **Validation**: Cannot cancel seats from already cancelled bookings

### User Interface
- **"Select Seats" Button**: Opens interactive modal for seat selection
- **"Cancel All" Button**: Maintains existing full booking cancellation
- **Visual Feedback**: Selected seats highlighted in red, counter shows selection count
- **Confirmation**: Different messages for partial vs full cancellation

### API Integration
```json
POST /bookings/{booking_id}/cancel-seats
{
  "booking_id": "booking-uuid",
  "seats_to_cancel": ["A1", "A2"]
}
```

## 🔧 Development

### Adding New Movies
Edit `backend/data/movies.json` to add new movies with the required schema.

### Customizing Seat Layout
Modify the seat generation logic in `frontend/src/pages/Booking.jsx`.

### Extending API
Add new endpoints in the respective route files and create corresponding service methods.

## 📝 License

This project is for educational/demonstration purposes.

## 🤝 Contributing

This is a personal project, but feedback and suggestions are welcome!