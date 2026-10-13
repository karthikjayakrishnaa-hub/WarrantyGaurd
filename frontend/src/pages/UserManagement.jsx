import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Shield, User, Edit3, Trash2 } from 'lucide-react';
import api from '../api';
import { useToast } from '../components/Toast';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const addToast = useToast();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      // In a real app, this would be a specific endpoint like /organizations/me/users
      // For now, let's assume we have it or mock it
      const { data } = await api.get('/auth/users'); // Mock endpoint
      setUsers(data);
    } catch (err) {
      addToast('Failed to load users', 'error');
      // Mock data for demo if endpoint doesn't exist
      setUsers([
        { id: 1, full_name: 'Admin User', email: 'admin@warrantyguard.ai', role: 'admin', is_active: true },
        { id: 2, full_name: 'Support Agent', email: 'agent@warrantyguard.ai', role: 'agent', is_active: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadge = (role) => {
    switch(role) {
      case 'admin': return <span className="badge badge-danger"><Shield size={12}/> Admin</span>;
      case 'agent': return <span className="badge badge-warning"><Shield size={12}/> Agent</span>;
      default: return <span className="badge badge-neutral"><User size={12}/> Customer</span>;
    }
  };

  return (
    <div>
      {/* Compact Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6 pb-4 border-b border-primary/10">
        <div>
          <h2 className="flex items-center gap-2 m-0 text-2xl font-heading font-extrabold text-foreground">
            <Users className="text-primary" size={24} /> User Management
          </h2>
          <p className="mt-1 text-muted-foreground font-medium text-sm hidden sm:block">Manage roles, permissions, and team invitations.</p>
        </div>
        <button className="btn btn-primary py-2.5 px-5 rounded-lg shadow-sm hover:-translate-y-0.5 transition-all flex items-center gap-2 shrink-0 text-sm">
          <UserPlus size={16} /> Invite User
        </button>
      </div>

      <div className="data-table-container">
        {loading ? (
          <div className="p-8 text-center text-muted">Loading users...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td className="font-medium">{u.full_name}</td>
                  <td className="text-muted">{u.email}</td>
                  <td>{getRoleBadge(u.role)}</td>
                  <td>
                    {u.is_active ? 
                      <span className="badge badge-success">Active</span> : 
                      <span className="badge badge-neutral">Inactive</span>
                    }
                  </td>
                  <td className="text-right">
                    <button className="btn btn-secondary mr-2" style={{padding: '6px 12px'}} title="Edit Role">
                      <Edit3 size={14} />
                    </button>
                    <button className="btn btn-danger" style={{padding: '6px 12px'}} title="Deactivate">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
