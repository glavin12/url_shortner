import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <nav className="w-full py-6 px-8 flex items-center justify-between bg-charcoal border-b border-white/5">
      <Link to="/" className="text-3xl font-bold text-coral tracking-tight">
        SNIPlink
      </Link>

      <div className="flex items-center gap-8">
        <Link 
          to="/dashboard" 
          className={`text-sm font-medium transition-colors ${location.pathname === '/dashboard' ? 'text-cream border-b-2 border-coral pb-1' : 'text-cream/70 hover:text-cream'}`}
        >
          Dashboard
        </Link>
        
        {user ? (
          <div className="flex items-center gap-6">
            <span className="text-sm text-cream/50">{user.email}</span>
            <button 
              onClick={logout}
              className="text-sm font-medium text-cream/70 hover:text-cream transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-6">
            <Link 
              to="/login" 
              className="text-sm font-medium text-cream/70 hover:text-cream transition-colors"
            >
              Login
            </Link>
            <Link 
              to="/register" 
              className="bg-coral text-cream text-sm font-semibold py-2 px-6 rounded-lg hover:bg-coral/90 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
