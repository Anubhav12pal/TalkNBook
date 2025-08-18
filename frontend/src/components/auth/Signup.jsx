import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const Signup = ({ onSwitchToLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const { signup, isLoading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const result = await signup(username, email, password, confirmPassword);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-16 bg-gradient-to-br from-dark-bg to-dark-card">
      <div className="bg-dark-card/95 backdrop-blur-lg rounded-3xl p-20 w-full max-w-4xl border border-dark-border shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-red via-brand-yellow via-brand-green to-brand-blue"></div>
        
        <div className="text-center mb-16">
          <div className="text-8xl font-black mb-4 select-none">
            <span className="text-brand-red drop-shadow-[0_0_20px_rgba(220,38,38,0.4)]">Talk</span>
            <span className="text-brand-yellow text-9xl mx-2 drop-shadow-[0_0_20px_rgba(251,191,36,0.4)] inline-block animate-pulse-brand">N</span>
            <span className="text-brand-green drop-shadow-[0_0_20px_rgba(16,185,129,0.4)]">Book</span>
          </div>
          <div className="text-gray-400 text-xl font-light tracking-widest uppercase">Your Movie Experience</div>
        </div>
        
        <h1 className="text-6xl font-bold text-center mb-14 text-white relative">
          Signup
          <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-gradient-to-r from-brand-red to-brand-green rounded"></div>
        </h1>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-10">
          <div className="flex flex-col gap-4">
            <label htmlFor="username" className="text-xl text-gray-300 font-medium">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="p-6 border border-dark-border rounded-xl bg-dark-input text-white text-xl transition-colors focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Enter your username"
              required
            />
          </div>
          
          <div className="flex flex-col gap-4">
            <label htmlFor="email" className="text-xl text-gray-300 font-medium">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="p-6 border border-dark-border rounded-xl bg-dark-input text-white text-xl transition-colors focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="flex flex-col gap-4">
            <label htmlFor="password" className="text-xl text-gray-300 font-medium">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="p-6 border border-dark-border rounded-xl bg-dark-input text-white text-xl transition-colors focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Enter your password"
              required
            />
          </div>
          
          <div className="flex flex-col gap-4">
            <label htmlFor="confirmPassword" className="text-xl text-gray-300 font-medium">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="p-6 border border-dark-border rounded-xl bg-dark-input text-white text-xl transition-colors focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Confirm your password"
              required
            />
          </div>
          
          {error && <div className="bg-brand-red text-white p-5 rounded-xl text-lg text-center">{error}</div>}
          
          <button 
            type="submit" 
            className="bg-brand-red text-white border-none rounded-xl p-6 text-xl font-semibold cursor-pointer transition-colors hover:bg-red-700 disabled:opacity-60 disabled:cursor-not-allowed mt-4"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
        
        <p className="text-center mt-10 text-gray-300 text-lg">
          Already have an account?{' '}
          <button 
            onClick={onSwitchToLogin}
            className="text-brand-red bg-none border-none cursor-pointer underline text-lg hover:text-red-700"
          >
            Login
          </button>
        </p>
      </div>
    </div>
  );
};

export default Signup;