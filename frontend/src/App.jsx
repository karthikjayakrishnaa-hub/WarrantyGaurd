import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ClaimDetail from './pages/ClaimDetail';
import NewClaim from './pages/NewClaim';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminPanel from './pages/AdminPanel';
import ProductCatalog from './pages/ProductCatalog';
import Analytics from './pages/Analytics';
import CustomerPortal from './pages/CustomerPortal';
import UserManagement from './pages/UserManagement';
import AuditLogs from './pages/AuditLogs';
import Settings from './pages/Settings';
import Landing from './pages/Landing';



const ProtectedRoute = ({ children, roles }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center mt-20 animate-fade-in">
        <div className="status-indicator warning mb-4" style={{ width: 16, height: 16 }}></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  
  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function AppContent() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<ProtectedRoute roles={['agent', 'admin']}><Dashboard /></ProtectedRoute>} />
          <Route path="/claims/:id" element={<ClaimDetail />} />
          <Route path="/new-claim" element={<NewClaim />} />
          <Route path="/settings" element={<Settings />} />

          {/* Customer Only */}
          <Route path="/portal" element={<ProtectedRoute roles={['customer']}><CustomerPortal /></ProtectedRoute>} />

          {/* Agent & Admin */}
          <Route path="/analytics" element={<ProtectedRoute roles={['agent', 'admin']}><Analytics /></ProtectedRoute>} />
          <Route path="/audit-logs" element={<ProtectedRoute roles={['agent', 'admin']}><AuditLogs /></ProtectedRoute>} />

          {/* Admin Only */}
          <Route path="/admin" element={<ProtectedRoute roles={['admin']}><AdminPanel /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute roles={['admin']}><UserManagement /></ProtectedRoute>} />
          <Route path="/admin/products" element={<ProtectedRoute roles={['admin']}><ProductCatalog /></ProtectedRoute>} />
        </Route>
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
