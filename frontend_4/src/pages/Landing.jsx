import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="min-h-[calc(100vh-80px)] bg-charcoal text-cream flex flex-col items-center justify-center p-6">
      
      <div className="text-center max-w-3xl mx-auto animate-fadeInDown">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 text-cream leading-tight">
          Shorten Your Links,<br/>
          <span className="text-coral">Amplify Your Reach</span>
        </h1>
        
        <p className="text-cream/60 max-w-2xl mx-auto text-xl font-light leading-relaxed mb-12">
          Powerful analytics and simple link management for marketers and developers.
          Engineered for speed and high-contrast utility.
        </p>

        <div className="flex items-center justify-center gap-4 animate-fadeInUp">
          {user ? (
            <Link 
              to="/dashboard" 
              className="bg-coral text-charcoal font-bold px-8 py-4 rounded-xl hover:bg-coral/90 transition-colors shadow-lg shadow-coral/20"
            >
              Go to Dashboard →
            </Link>
          ) : (
            <>
              <Link 
                to="/register" 
                className="bg-coral text-charcoal font-bold px-8 py-4 rounded-xl hover:bg-coral/90 transition-colors shadow-lg shadow-coral/20"
              >
                Start For Free →
              </Link>
              <Link 
                to="/login" 
                className="bg-white/5 text-cream border border-white/10 font-bold px-8 py-4 rounded-xl hover:bg-white/10 transition-colors"
              >
                Sign In
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
