import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';

export default function Login() {
  const { user, login } = useAuth();
  const toast = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (user) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      toast.success('Welcome back!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] bg-charcoal text-cream flex items-center justify-center p-6">
      <div className="w-full max-w-md animate-fadeInUp">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">Welcome Back</h1>
          <p className="text-cream/50">Sign in to access your dashboard</p>
        </div>

        <form className="bg-[#222222] border border-white/5 rounded-[20px] p-8 shadow-2xl" onSubmit={handleSubmit}>
          {error && <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl mb-6 text-sm">{error}</div>}

          <div className="mb-6">
            <label className="block text-cream/70 text-sm font-bold mb-2" htmlFor="login-email">Email</label>
            <input
              id="login-email"
              className="w-full bg-[#1a1a1a] border border-white/10 rounded-xl px-4 py-3 text-cream placeholder:text-cream/30 focus:border-coral/50 outline-none transition-colors"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="mb-8">
            <label className="block text-cream/70 text-sm font-bold mb-2" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              className="w-full bg-[#1a1a1a] border border-white/10 rounded-xl px-4 py-3 text-cream placeholder:text-cream/30 focus:border-coral/50 outline-none transition-colors"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              maxLength={26}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-coral text-[#1a1a1a] font-bold py-3 px-4 rounded-xl hover:bg-coral/90 transition-colors disabled:opacity-70"
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="text-center mt-8 text-cream/50 text-sm">
          Don't have an account?{' '}
          <Link to="/register" className="text-coral hover:underline font-medium">Create one</Link>
        </div>
      </div>
    </div>
  );
}
