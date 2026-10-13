import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, FileText, PlusCircle, Settings, Users, BarChart2, Package, Archive, LogOut } from 'lucide-react';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="text-primary font-heading">WarrantyGuard</h2>
      </div>
      
      <nav className="sidebar-nav">
        <div className="nav-group">
          <p className="nav-label">Main</p>
          {user.role !== 'customer' && (
            <NavLink to="/dashboard" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <LayoutDashboard size={20} /> Dashboard
            </NavLink>
          )}
          {user.role === 'customer' && (
            <NavLink to="/portal" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <FileText size={20} /> My Claims
            </NavLink>
          )}
          <NavLink to="/new-claim" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
            <PlusCircle size={20} /> New Claim
          </NavLink>
        </div>

        {(user.role === 'agent' || user.role === 'admin') && (
          <div className="nav-group mt-6">
            <p className="nav-label">Workspace</p>
            <NavLink to="/analytics" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <BarChart2 size={20} /> Analytics
            </NavLink>
            <NavLink to="/audit-logs" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Archive size={20} /> Audit Logs
            </NavLink>
          </div>
        )}

        {user.role === 'admin' && (
          <div className="nav-group mt-6">
            <p className="nav-label">Admin</p>
            <NavLink to="/admin" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Settings size={20} /> Org Settings
            </NavLink>
            <NavLink to="/admin/users" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Users size={20} /> Users
            </NavLink>
            <NavLink to="/admin/products" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Package size={20} /> Products
            </NavLink>
          </div>
        )}
      </nav>

      <div className="sidebar-footer">
        <NavLink to="/settings" className="nav-item">
          <Settings size={20} /> Settings
        </NavLink>
        <button className="nav-item text-danger" onClick={handleLogout} style={{width: '100%', background: 'transparent', border: 'none', cursor: 'pointer'}}>
          <LogOut size={20} /> Logout
        </button>
      </div>
    </aside>
  );
}
