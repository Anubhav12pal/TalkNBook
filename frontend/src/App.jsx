import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthWrapper from './components/auth/AuthWrapper';
import Movies from './pages/Movies';
import Booking from './pages/Booking';
import MyBookings from './pages/MyBookings';

const ProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-dark-bg text-white">
        <div className="w-8 h-8 border-2 border-dark-border border-t-brand-red rounded-full animate-spin mb-4"></div>
        <p>Loading...</p>
      </div>
    );
  }
  
  return user ? children : <AuthWrapper />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-dark-bg to-slate-900">
          <Routes>
            <Route 
              path="/auth" 
              element={<AuthWrapper />} 
            />
            <Route 
              path="/movies" 
              element={
                <ProtectedRoute>
                  <Movies />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/booking/:movieId" 
              element={
                <ProtectedRoute>
                  <Booking />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/my-bookings" 
              element={
                <ProtectedRoute>
                  <MyBookings />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/" 
              element={<Navigate to="/movies" replace />} 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
