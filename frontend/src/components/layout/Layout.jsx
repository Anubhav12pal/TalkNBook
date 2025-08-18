import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

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
    <div className="min-h-screen bg-dark-bg text-white flex flex-col">
      <header className="bg-dark-card border-b border-dark-border px-8 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex-shrink-0">
            <h1 
              className="text-3xl font-extrabold cursor-pointer select-none transition-transform hover:scale-105"
              onClick={() => navigate('/movies')}
            >
              <span className="text-brand-red drop-shadow-[0_0_10px_rgba(220,38,38,0.3)]">Talk</span>
              <span className="text-brand-yellow text-4xl mx-1 drop-shadow-[0_0_10px_rgba(251,191,36,0.3)]">N</span>
              <span className="text-brand-green drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]">Book</span>
            </h1>
          </div>
          
          {!isMobile && (
            <nav className="flex gap-4 flex-1 justify-center">
              <button 
                className={`bg-transparent border border-dark-border rounded-lg px-6 py-3 cursor-pointer text-sm font-medium transition-all flex items-center gap-2 ${
                  location.pathname === '/movies' 
                    ? 'bg-brand-red border-brand-red text-white' 
                    : 'text-gray-300 hover:bg-dark-border hover:text-white hover:border-gray-500'
                }`}
                onClick={() => navigate('/movies')}
              >
                🎬 Movies
              </button>
              <button 
                className="bg-transparent text-gray-300 border border-dark-border rounded-lg px-6 py-3 cursor-pointer text-sm font-medium transition-all flex items-center gap-2 hover:bg-dark-border hover:text-white hover:border-gray-500"
                onClick={() => navigate('/movies')}
              >
                🎟️ My Bookings
              </button>
              <button 
                className="bg-transparent text-gray-300 border border-dark-border rounded-lg px-6 py-3 cursor-pointer text-sm font-medium transition-all flex items-center gap-2 hover:bg-dark-border hover:text-white hover:border-gray-500"
                onClick={() => navigate('/movies')}
              >
                🔍 Search
              </button>
            </nav>
          )}

          <div className="flex items-center gap-4 flex-shrink-0">
            <span className="text-gray-300 text-sm">Welcome, {user?.name}</span>
            <button 
              onClick={handleLogout} 
              className="bg-gray-700 text-white border-none rounded-lg px-4 py-2 cursor-pointer text-sm transition-colors hover:bg-gray-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        {children}
      </main>

      {showNavigation && isMobile && (
        <nav className="fixed bottom-0 left-0 right-0 bg-dark-card flex justify-around py-3 border-t border-dark-border z-50">
          <div 
            className={`flex flex-col items-center gap-1 cursor-pointer transition-all p-1 rounded-lg ${
              location.pathname === '/movies' ? 'bg-dark-border text-brand-red' : 'hover:bg-dark-border'
            }`}
            onClick={() => navigate('/movies')}
          >
            <i className="text-xl">🎬</i>
            <span className={`text-xs ${location.pathname === '/movies' ? 'text-brand-red' : 'text-gray-300'}`}>Movies</span>
          </div>
          <div className="flex flex-col items-center gap-1 cursor-pointer transition-all p-1 rounded-lg hover:bg-dark-border">
            <i className="text-xl">🎟️</i>
            <span className="text-xs text-gray-300">Bookings</span>
          </div>
          <div className="flex flex-col items-center gap-1 cursor-pointer transition-all p-1 rounded-lg hover:bg-dark-border">
            <i className="text-xl">🔍</i>
            <span className="text-xs text-gray-300">Search</span>
          </div>
          <div className="flex flex-col items-center gap-1 cursor-pointer transition-all p-1 rounded-lg hover:bg-dark-border" onClick={handleLogout}>
            <i className="text-xl">🚪</i>
            <span className="text-xs text-gray-300">Logout</span>
          </div>
        </nav>
      )}
    </div>
  );
};

export default Layout;