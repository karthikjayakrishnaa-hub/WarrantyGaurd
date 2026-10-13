import React, { useState, useEffect } from 'react';
import api from '../api';
import { useToast } from '../components/Toast';
import { Settings, Save, CheckCircle2 } from 'lucide-react';

export default function AdminPanel() {
  const [org, setOrg] = useState(null);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const addToast = useToast();

  useEffect(() => {
    const fetchOrg = async () => {
      try {
        const { data } = await api.get('/organizations/me');
        setOrg(data);
        setName(data.name);
      } catch (err) {
        addToast('Failed to load organization settings', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchOrg();
  }, [addToast]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.patch('/organizations/me', { name });
      addToast('Organization settings updated successfully', 'success');
      setOrg(prev => ({ ...prev, name }));
    } catch (err) {
      addToast('Failed to update settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading settings...</div>;
  }

  return (
    <div>
      {/* Compact Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6 pb-4 border-b border-primary/10">
        <div>
          <h2 className="flex items-center gap-2 m-0 text-2xl font-heading font-extrabold text-foreground">
            <Settings className="text-primary" size={24} /> Organization Settings
          </h2>
          <p className="mt-1 text-muted-foreground font-medium text-sm">Manage your workspace, branding, and billing.</p>
        </div>
      </div>

      <div className="glass-card max-w-2xl p-8 relative overflow-hidden group">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-transparent blur-xl opacity-0 group-hover:opacity-100 transition duration-1000 -z-10"></div>
        <form onSubmit={handleSave} className="flex-col gap-6">
          <div className="flex-col gap-2 mb-6">
            <label className="font-semibold text-sm uppercase tracking-wider text-muted">Organization Name</label>
            <input 
              type="text" 
              className="form-input" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              required
            />
          </div>

          <div className="flex-col gap-2 mb-6">
            <label className="font-semibold text-sm uppercase tracking-wider text-muted">Workspace Slug</label>
            <input 
              type="text" 
              className="form-input" 
              value={org.slug} 
              disabled
              title="Slug cannot be changed"
            />
            <p className="text-xs">Your workspace URL identifier. Contact support to change this.</p>
          </div>

          <div className="flex-col gap-2 mb-6">
            <label className="font-semibold text-sm uppercase tracking-wider text-muted">Current Plan</label>
            <div className="flex items-center gap-2">
              <span className="badge badge-success">
                <CheckCircle2 size={12} /> {org.plan || 'ENTERPRISE'}
              </span>
            </div>
          </div>

          <div className="border-t border-color-border pt-6 flex justify-end">
            <button type="submit" className="btn btn-primary" disabled={saving || name === org.name}>
              <Save size={18} /> {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
