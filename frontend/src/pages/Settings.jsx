import React, { useState } from 'react';
import { Settings as SettingsIcon, User, Lock, Bell, Save } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';

export default function Settings() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const addToast = useToast();

  const [saving, setSaving] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      addToast('Settings saved successfully', 'success');
    }, 800);
  };

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h2 className="flex items-center gap-2 m-0">
          <SettingsIcon className="text-primary" /> Settings
        </h2>
        <p className="mt-2 text-muted">Manage your personal profile, security, and preferences.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar Nav */}
        <div className="w-full md:w-64 flex flex-col gap-2">
          <button 
            className={`flex items-center gap-3 p-3 rounded text-left font-semibold ${activeTab === 'profile' ? 'bg-primary/10 text-primary' : 'hover:bg-muted text-muted-foreground'}`}
            onClick={() => setActiveTab('profile')}
          >
            <User size={18} /> Profile
          </button>
          <button 
            className={`flex items-center gap-3 p-3 rounded text-left font-semibold ${activeTab === 'security' ? 'bg-primary/10 text-primary' : 'hover:bg-muted text-muted-foreground'}`}
            onClick={() => setActiveTab('security')}
          >
            <Lock size={18} /> Security
          </button>
          <button 
            className={`flex items-center gap-3 p-3 rounded text-left font-semibold ${activeTab === 'notifications' ? 'bg-primary/10 text-primary' : 'hover:bg-muted text-muted-foreground'}`}
            onClick={() => setActiveTab('notifications')}
          >
            <Bell size={18} /> Notifications
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1">
          <form className="card p-6" onSubmit={handleSave}>
            {activeTab === 'profile' && (
              <div className="flex-col gap-6 animate-fade-in">
                <h3 className="mb-4 pb-2 border-b border-color-border">Profile Information</h3>
                
                <div className="flex-col gap-2">
                  <label className="text-sm font-semibold text-muted uppercase tracking-wider">Full Name</label>
                  <input type="text" className="form-input max-w-md" defaultValue={user.full_name} required />
                </div>
                
                <div className="flex-col gap-2">
                  <label className="text-sm font-semibold text-muted uppercase tracking-wider">Email Address</label>
                  <input type="email" className="form-input max-w-md" defaultValue={user.email} disabled />
                  <p className="text-xs text-muted">Your email is managed by your organization administrator.</p>
                </div>
                
                <div className="flex-col gap-2">
                  <label className="text-sm font-semibold text-muted uppercase tracking-wider">Role</label>
                  <div><span className="badge badge-neutral">{user.role}</span></div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="flex-col gap-6 animate-fade-in">
                <h3 className="mb-4 pb-2 border-b border-color-border">Change Password</h3>
                
                <div className="flex-col gap-2">
                  <label className="text-sm font-semibold text-muted uppercase tracking-wider">Current Password</label>
                  <input type="password" className="form-input max-w-md" required />
                </div>
                
                <div className="flex-col gap-2">
                  <label className="text-sm font-semibold text-muted uppercase tracking-wider">New Password</label>
                  <input type="password" className="form-input max-w-md" required />
                  <p className="text-xs text-muted">Must be at least 8 characters with 1 uppercase, 1 lowercase, 1 number, and 1 symbol.</p>
                </div>
                
                <div className="flex-col gap-2">
                  <label className="text-sm font-semibold text-muted uppercase tracking-wider">Confirm New Password</label>
                  <input type="password" className="form-input max-w-md" required />
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="flex-col gap-6 animate-fade-in">
                <h3 className="mb-4 pb-2 border-b border-color-border">Email Notifications</h3>
                
                <label className="flex items-start gap-3 cursor-pointer">
                  <input type="checkbox" className="mt-1" defaultChecked />
                  <div>
                    <div className="font-semibold text-foreground">Claim Status Updates</div>
                    <div className="text-sm text-muted">Receive an email when a claim's status changes.</div>
                  </div>
                </label>
                
                {user.role !== 'customer' && (
                  <>
                    <label className="flex items-start gap-3 cursor-pointer">
                      <input type="checkbox" className="mt-1" defaultChecked />
                      <div>
                        <div className="font-semibold text-foreground">New Claim Assignments</div>
                        <div className="text-sm text-muted">Receive an email when a claim is assigned to you.</div>
                      </div>
                    </label>
                    <label className="flex items-start gap-3 cursor-pointer">
                      <input type="checkbox" className="mt-1" defaultChecked />
                      <div>
                        <div className="font-semibold text-foreground">SLA Warnings</div>
                        <div className="text-sm text-muted">Receive an email when a claim is approaching its SLA limit.</div>
                      </div>
                    </label>
                  </>
                )}
              </div>
            )}

            <div className="mt-8 pt-6 border-t border-color-border flex justify-end">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                <Save size={18} /> {saving ? 'Saving...' : 'Save Preferences'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
