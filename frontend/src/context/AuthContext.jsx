import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export { AuthContext };

const API_BASE_URL = 'http://localhost:8000';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('talknbook_user');
    const savedToken = localStorage.getItem('talknbook_token');
    
    if (savedUser && savedToken) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login-json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        const { access_token, user: userData } = data;
        setUser(userData);
        localStorage.setItem('talknbook_user', JSON.stringify(userData));
        localStorage.setItem('talknbook_token', access_token);
        return { success: true };
      } else {
        return { success: false, error: data.detail || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (username, email, password, confirmPassword) => {
    setIsLoading(true);
    try {
      if (password !== confirmPassword) {
        setIsLoading(false);
        return { success: false, error: 'Passwords do not match' };
      }

      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        const { access_token, user: userData } = data;
        setUser(userData);
        localStorage.setItem('talknbook_user', JSON.stringify(userData));
        localStorage.setItem('talknbook_token', access_token);
        return { success: true };
      } else {
        return { success: false, error: data.detail || 'Signup failed' };
      }
    } catch (error) {
      console.error('Signup error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('talknbook_user');
    localStorage.removeItem('talknbook_token');
  };

  const value = {
    user,
    isLoading,
    login,
    signup,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};