import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Mail, Lock, LogIn, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const userData = await login(email, password);
      if (userData?.role === 'customer') {
        navigate('/portal');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      const detail = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container animate-fade-in">
        <div className="auth-header">
          <ShieldCheck size={40} className="text-gold" />
          <h1>WarrantyGuard <span className="text-gold font-light">AI</span></h1>
          <p className="text-muted mt-2">Sign in to your account</p>
        </div>

        {error && (
          <div className="auth-error animate-fade-in">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label>
              <Mail size={14} className="text-muted" />
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="form-input"
              required
              autoFocus
            />
          </div>

          <div className="auth-field">
            <label>
              <Lock size={14} className="text-muted" />
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="form-input"
              required
            />
          </div>

          <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
            {loading ? (
              <>
                <div className="status-indicator warning" style={{ width: 12, height: 12, margin: 0 }}></div>
                Signing in...
              </>
            ) : (
              <>
                <LogIn size={18} />
                Sign In
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p className="text-muted text-sm">
            Don't have an account?{' '}
            <Link to="/register" className="auth-link">Create one</Link>
          </p>
        </div>

        <div className="auth-demo-hint">
          <p className="text-xs text-muted">Demo Accounts</p>
          <div className="auth-demo-accounts">
            <button type="button" className="auth-demo-btn" onClick={() => { setEmail('admin@warrantyguard.ai'); setPassword('admin123'); }}>
              Admin
            </button>
            <button type="button" className="auth-demo-btn" onClick={() => { setEmail('agent@warrantyguard.ai'); setPassword('agent123'); }}>
              Agent
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
