import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import api from '../api';
import { useToast } from '../components/Toast';
import { Activity, Clock, CheckCircle, XCircle } from 'lucide-react';

const COLORS = ['#10B981', '#DC2626', '#EAB308', '#6366F1', '#EC4899'];

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const addToast = useToast();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await api.get('/stats');
        setStats(data);
      } catch (err) {
        addToast('Failed to load analytics', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [addToast]);

  if (loading || !stats) {
    return <div className="p-8 text-center text-muted">Loading Analytics...</div>;
  }

  const { overview, triage_categories, weekly_volume } = stats;

  return (
    <div>
      <div className="mb-6">
        <h2 className="flex items-center gap-2 m-0">
          <Activity className="text-primary" /> Analytics Dashboard
        </h2>
        <p className="mt-2">Monitor organization claim volume and AI triage performance.</p>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon bg-primary/10 text-primary">
            <Activity size={24} />
          </div>
          <div className="flex-col">
            <span className="stat-value">{overview.total}</span>
            <span className="stat-label">Total Claims</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon bg-warning/10" style={{color: '#EAB308'}}>
            <Clock size={24} />
          </div>
          <div className="flex-col">
            <span className="stat-value">{overview.pending}</span>
            <span className="stat-label">Pending Review</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon bg-success/10 text-success">
            <CheckCircle size={24} />
          </div>
          <div className="flex-col">
            <span className="stat-value">{overview.approved}</span>
            <span className="stat-label">Approved</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon bg-danger/10 text-danger">
            <XCircle size={24} />
          </div>
          <div className="flex-col">
            <span className="stat-value">{overview.rejected}</span>
            <span className="stat-label">Rejected</span>
          </div>
        </div>
      </div>

      <div className="flex gap-6 mb-6">
        <div className="card flex-1 min-w-[300px]">
          <h3 className="mb-6 text-sm uppercase tracking-wider text-muted">AI Triage Categories</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={triage_categories}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {triage_categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card flex-1 min-w-[500px]">
          <h3 className="mb-6 text-sm uppercase tracking-wider text-muted">Weekly Claim Volume</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weekly_volume} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EFE7FC" />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 12}} />
                <RechartsTooltip cursor={{fill: '#F7F3FD'}} />
                <Legend iconType="circle" wrapperStyle={{fontSize: '12px'}} />
                <Bar dataKey="claims" name="Total Claims" fill="#6366F1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="approved" name="Approved" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
