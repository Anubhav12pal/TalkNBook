import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Layout.css';

const Layout = ({ children, showNavigation = true }) => {
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  useEffect(() => {
    const checkDevice = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <div className="layout">
      <header className="layout-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="app-logo" onClick={() => navigate('/movies')}>
              <span className="logo-talk">Talk</span>
              <span className="logo-n">N</span>
              <span className="logo-book">Book</span>
            </h1>
          </div>
          
          <nav className="desktop-nav">
            <button 
              className={`nav-button ${location.pathname === '/movies' ? 'active' : ''}`}
              onClick={() => navigate('/movies')}
            >
              🎬 Movies
            </button>
            <button 
              className="nav-button"
              onClick={() => navigate('/movies')}
            >
              🎟️ My Bookings
            </button>
            <button 
              className="nav-button"
              onClick={() => navigate('/movies')}
            >
              🔍 Search
            </button>
          </nav>

          <div className="user-section">
            <span className="welcome-text">Welcome, {user?.name}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="layout-content">
        {children}
      </main>

      {showNavigation && isMobile && (
        <nav className="mobile-nav">
          <div 
            className={`nav-item ${location.pathname === '/movies' ? 'active' : ''}`}
            onClick={() => navigate('/movies')}
          >
            <i className="nav-icon">🎬</i>
            <span className="nav-label">Movies</span>
          </div>
          <div className="nav-item">
            <i className="nav-icon">🎟️</i>
            <span className="nav-label">Bookings</span>
          </div>
          <div className="nav-item">
            <i className="nav-icon">🔍</i>
            <span className="nav-label">Search</span>
          </div>
          <div className="nav-item" onClick={handleLogout}>
            <i className="nav-icon">🚪</i>
            <span className="nav-label">Logout</span>
          </div>
        </nav>
      )}
    </div>
  );
};

export default Layout;