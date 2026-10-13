import React, { useState, useEffect } from 'react';
import { Archive, Search, FileText } from 'lucide-react';
import api from '../api';
import { useToast } from '../components/Toast';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const addToast = useToast();

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      // Assuming GET /claims/ fetches audit logs as well if expanded, but let's mock the endpoint for org logs
      const { data } = await api.get('/claims/', { params: { limit: 10 } });
      
      // Extract all audit logs from all claims for this demo view
      let allLogs = [];
      data.claims.forEach(c => {
        if (c.audit_logs) {
          allLogs = [...allLogs, ...c.audit_logs.map(log => ({...log, claim_id: c.id, claim_product: c.product_model}))];
        }
      });
      // Sort by descending
      allLogs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setLogs(allLogs);
    } catch (err) {
      addToast('Failed to load audit logs', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit', second:'2-digit'
    });
  };

  const filteredLogs = logs.filter(l => 
    l.details.toLowerCase().includes(searchTerm.toLowerCase()) || 
    (l.user_name && l.user_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="max-w-5xl mx-auto animate-fade-in flex flex-col gap-6">
      
      {/* Compact Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 pb-4 border-b border-primary/10 mb-4">
        <div>
          <h2 className="flex items-center gap-2 m-0 text-2xl font-heading font-extrabold text-foreground">
            <Archive className="text-primary" size={24} /> Audit Logs
          </h2>
          <p className="mt-1 text-muted-foreground font-medium text-sm">Organization-wide immutable audit trail.</p>
        </div>
      </div>

      <div className="glass-card p-4 flex items-center bg-white/40 shadow-sm">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={18} />
          <input 
            type="text" 
            placeholder="Search logs..." 
            className="form-input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="glass-card p-8">
        {loading ? (
          <div className="text-center text-muted">Loading audit trail...</div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-center text-muted">No logs found.</div>
        ) : (
          <div className="flex flex-col gap-0 border-l-2 border-primary/20 ml-4 pl-6 relative">
            {filteredLogs.map((log, idx) => (
              <div className="relative pb-8" key={log.id}>
                <div className="absolute -left-[37px] top-0 w-8 h-8 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center shadow-sm">
                  <FileText size={14} className="text-primary" />
                </div>
                <div className="glass-card p-4 hover:-translate-y-1 transition-all duration-300">
                  <div className="flex justify-between items-start mb-2">
                    <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-primary/10 text-primary border border-primary/20">
                      {log.action.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-muted-foreground font-medium">{formatDate(log.created_at)}</span>
                  </div>
                  <p className="text-sm text-foreground mt-2 mb-3 leading-relaxed">
                    <span className="font-bold text-primary mr-1">Claim #{log.claim_id}</span> 
                    <span className="text-muted-foreground">({log.claim_product})</span> &mdash; {log.details}
                  </p>
                  <span className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5 border-t border-color-border/50 pt-2 mt-2">
                    <div className="w-5 h-5 rounded-full bg-muted-foreground flex items-center justify-center text-[10px] text-white">
                      {log.user_name ? log.user_name[0].toUpperCase() : 'S'}
                    </div>
                    By {log.user_name || 'System'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
