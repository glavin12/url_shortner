import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Landing.css';

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">
          <span className="dot"></span>
          Now with real-time analytics
        </div>

        <h1>
          Shorten. Share.
          <br />
          <span className="gradient-text">Track Everything.</span>
        </h1>

        <p className="hero-subtitle">
          Transform long, ugly URLs into clean, trackable links. Get detailed
          click analytics and manage all your links from one premium dashboard.
        </p>

        <div className="hero-cta">
          {user ? (
            <Link to="/dashboard" className="btn btn-primary btn-lg">
              Go to Dashboard →
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary btn-lg">
                Start For Free →
              </Link>
              <Link to="/login" className="btn btn-ghost btn-lg">
                Sign In
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="features-header">
          <h2>Why Sniplink?</h2>
          <p>Everything you need to manage and track your links</p>
        </div>

        <div className="features-grid">
          <div className="feature-card glass-card">
            <div className="feature-icon">🔗</div>
            <h3>Instant Shortening</h3>
            <p>
              Paste any URL and get a short, clean link in milliseconds. 
              Cached with Redis for blazing fast redirects.
            </p>
          </div>

          <div className="feature-card glass-card">
            <div className="feature-icon">📊</div>
            <h3>Click Analytics</h3>
            <p>
              Track every click with timestamps. See exactly when your 
              audience engages with your links.
            </p>
          </div>

          <div className="feature-card glass-card">
            <div className="feature-icon">🛡️</div>
            <h3>Secure & Protected</h3>
            <p>
              JWT authentication, rate limiting, and encrypted passwords. 
              Your data is always safe.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>Built with FastAPI, React & Redis — © {new Date().getFullYear()} Sniplink</p>
      </footer>
    </div>
  );
}
