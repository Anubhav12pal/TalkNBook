import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthWrapper from './components/auth/AuthWrapper';
import Movies from './pages/Movies';
import Booking from './pages/Booking';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
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
        <div className="app">
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
