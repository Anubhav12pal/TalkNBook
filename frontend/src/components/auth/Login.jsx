import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

const Login = ({ onSwitchToSignup }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const result = await login(email, password);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="h-screen flex items-center border border-white justify-center bg-gradient-to-br from-dark-bg to-dark-card p-4">
      <div className="bg-dark-card/95 h-full backdrop-blur-lg rounded-3xl px-20 py-8 w-full max-w-5xl border border-dark-border shadow-2xl relative overflow-y-auto flex justify-center flex-col">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-red via-brand-yellow via-brand-green to-brand-blue"></div>

        <div className="text-center mb-6">
          <div className="text-5xl font-black mb-3 select-none">
            <span className="text-brand-red drop-shadow-[0_0_20px_rgba(220,38,38,0.4)]">
              Talk
            </span>
            <span className="text-brand-yellow text-6xl mx-2 drop-shadow-[0_0_20px_rgba(251,191,36,0.4)] inline-block animate-pulse-brand">
              N
            </span>
            <span className="text-brand-green drop-shadow-[0_0_20px_rgba(16,185,129,0.4)]">
              Book
            </span>
          </div>
          <div className="text-gray-400 text-base font-light tracking-widest uppercase">
            Your Movie Experience
          </div>
        </div>

        <h1 className="text-3xl font-bold text-center mb-6 text-white relative">
          Login
          <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-gradient-to-r from-brand-red to-brand-green rounded"></div>
        </h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label
              htmlFor="email"
              className="text-base text-gray-300 font-medium"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="p-3 border border-dark-border rounded-xl bg-dark-input text-white text-base transition-colors focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="flex flex-col gap-2">
            <label
              htmlFor="password"
              className="text-base text-gray-300 font-medium"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="p-3 border border-dark-border rounded-xl bg-dark-input text-white text-base transition-colors focus:outline-none focus:border-brand-red placeholder-gray-500"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="bg-brand-red text-white p-3 rounded-xl text-base text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="bg-brand-red text-white border-none rounded-xl p-3 text-base font-semibold cursor-pointer transition-colors hover:bg-red-700 disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            disabled={isLoading}
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="text-center mt-4 text-gray-300 text-sm">
          Don't have an account?{" "}
          <button
            onClick={onSwitchToSignup}
            className="text-brand-red bg-none border-none cursor-pointer underline text-sm hover:text-red-700"
          >
            Signup
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
