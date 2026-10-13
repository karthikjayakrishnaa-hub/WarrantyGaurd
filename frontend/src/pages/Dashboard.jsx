import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Clock, ChevronRight, Plus, Search, Filter, ChevronLeft, XCircle, BarChart3, ArrowUpDown, CheckSquare } from 'lucide-react';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';

const STATUSES = [
  { value: '', label: 'All Statuses' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'processing', label: 'Processing' },
  { value: 'triaged', label: 'Triaged' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'closed', label: 'Closed' },
];

const PAGE_SIZE = 10;

const Dashboard = () => {
  const { user } = useAuth();
  const [claims, setClaims] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const addToast = useToast();

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(0);

  // Bulk Selection
  const [selectedIds, setSelectedIds] = useState([]);
  const [bulkLoading, setBulkLoading] = useState(false);

  // Stats
  const [stats, setStats] = useState({ total: 0, submitted: 0, triaged: 0, approved: 0, rejected: 0 });

  const fetchClaims = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;

      const response = await api.get('/claims/', { params });
      setClaims(response.data.claims);
      setTotal(response.data.total);
    } catch (error) {
      addToast("Failed to fetch claims", 'error');
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, dateFrom, dateTo, sortBy, sortOrder, page, addToast]);

  const fetchStats = useCallback(async () => {
    try {
      const [all, submitted, triaged, approved, rejected] = await Promise.all([
        api.get('/claims/', { params: { limit: 1 } }),
        api.get('/claims/', { params: { status: 'submitted', limit: 1 } }),
        api.get('/claims/', { params: { status: 'triaged', limit: 1 } }),
        api.get('/claims/', { params: { status: 'approved', limit: 1 } }),
        api.get('/claims/', { params: { status: 'rejected', limit: 1 } }),
      ]);
      setStats({
        total: all.data.total,
        submitted: submitted.data.total,
        triaged: triaged.data.total,
        approved: approved.data.total,
        rejected: rejected.data.total,
      });
    } catch (err) {
      console.error("Failed to fetch stats", err);
    }
  }, []);

  useEffect(() => {
    fetchClaims();
    // Reset selection when page changes
    setSelectedIds([]);
  }, [fetchClaims]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const [searchInput, setSearchInput] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
      setPage(0);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleBulkUpdate = async (status) => {
    if (selectedIds.length === 0) return;
    setBulkLoading(true);
    try {
      await api.post('/claims/bulk-update', { claim_ids: selectedIds, status });
      addToast(`Successfully updated ${selectedIds.length} claims to ${status}`, 'success');
      setSelectedIds([]);
      fetchClaims();
      fetchStats();
    } catch (err) {
      addToast('Failed to update claims', 'error');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(claims.map(c => c.id));
    } else {
      setSelectedIds([]);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'submitted': return <span className="badge badge-neutral"><Clock size={14}/> Submitted</span>;
      case 'processing': return <span className="badge badge-warning" style={{color: '#EAB308', borderColor: '#FEF08A', backgroundColor: '#FEF9C3'}}><AlertCircle size={14}/> Processing</span>;
      case 'triaged': return <span className="badge badge-success" style={{backgroundColor: '#ECFEFF', color: '#06B6D4', borderColor: '#CFFAFE'}}><CheckCircle2 size={14}/> Triaged</span>;
      case 'approved': return <span className="badge badge-success"><CheckCircle2 size={14}/> Approved</span>;
      case 'rejected': return <span className="badge badge-danger"><XCircle size={14}/> Rejected</span>;
      default: return <span className="badge badge-neutral">{status}</span>;
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setPage(0);
  };

  const SortIcon = ({ field }) => {
    if (sortBy !== field) return <ArrowUpDown size={12} className="text-muted" style={{ opacity: 0.3 }} />;
    return <ArrowUpDown size={12} className="text-primary" />;
  };

  return (
    <div className="animate-fade-in grid grid-cols-1 xl:grid-cols-4 gap-8">
      {/* Main Content Area */}
      <div className="xl:col-span-3 flex flex-col gap-6">
        <div className="flex flex-wrap justify-between items-center gap-4 pb-4 border-b border-primary/10 mb-4">
          <div>
            <h2 className="text-2xl m-0 font-heading font-black text-foreground">Claims Hub</h2>
            <p className="text-muted-foreground mt-1 font-medium text-sm hidden sm:block">Manage, monitor, and resolve warranty claims efficiently.</p>
          </div>
          <Link to="/new-claim" className="btn btn-primary py-2.5 px-5 shadow-sm rounded-lg hover:-translate-y-0.5 transition-all flex items-center gap-2 shrink-0 text-sm">
            <Plus size={16} /> New Claim
          </Link>
        </div>

        {/* Bulk Action Bar */}
        {selectedIds.length > 0 && user.role !== 'customer' && (
          <div className="glass-card flex justify-between items-center p-4 border border-primary bg-primary/5 shadow-md">
            <div className="flex items-center gap-2 text-primary font-semibold">
              <CheckSquare size={18} /> {selectedIds.length} claims selected
            </div>
            <div className="flex gap-2">
              <button className="btn btn-success" onClick={() => handleBulkUpdate('approved')} disabled={bulkLoading}>
                <CheckCircle2 size={16} /> Approve
              </button>
              <button className="btn btn-danger" onClick={() => handleBulkUpdate('rejected')} disabled={bulkLoading}>
                <XCircle size={16} /> Reject
              </button>
            </div>
          </div>
        )}

        {/* Filters Bar */}
        <div className="glass-card flex flex-wrap gap-4 items-center p-4">
          <div className="relative flex-1 min-w-[250px]">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-primary/50" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search claims..."
              className="form-input pl-12 bg-white/40 border-white/60 focus:bg-white/80 transition-all"
            />
          </div>
          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex items-center gap-2">
              <Filter size={16} className="text-primary/50" />
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
                className="form-input py-2 bg-white/40 border-white/60"
              >
                {STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => { setDateFrom(e.target.value); setPage(0); }}
                className="form-input py-2 w-[140px] bg-white/40 border-white/60"
              />
              <span className="text-primary/50 font-semibold text-xs uppercase">to</span>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => { setDateTo(e.target.value); setPage(0); }}
                className="form-input py-2 w-[140px] bg-white/40 border-white/60"
              />
            </div>
            {(search || statusFilter || dateFrom || dateTo) && (
              <button
                className="btn btn-secondary py-2 px-4 text-sm bg-white/40 border-white/60 hover:bg-white/70"
                onClick={() => { setSearchInput(''); setSearch(''); setStatusFilter(''); setDateFrom(''); setDateTo(''); setPage(0); }}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="data-table-container">
          {loading ? (
            <div className="flex flex-col items-center justify-center p-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
              <p className="text-primary font-semibold">Loading claims...</p>
            </div>
          ) : (
            <>
              <table className="data-table">
                <thead>
                  <tr>
                    {user.role !== 'customer' && (
                      <th style={{width: 40}}>
                        <input 
                          type="checkbox" 
                          className="accent-primary w-4 h-4"
                          checked={claims.length > 0 && selectedIds.length === claims.length} 
                          onChange={handleSelectAll} 
                        />
                      </th>
                    )}
                    <th className="cursor-pointer hover:bg-white/20 transition-colors group" onClick={() => handleSort('id')}>
                      <div className="flex items-center gap-1">ID <SortIcon field="id" /></div>
                    </th>
                    <th>Customer</th>
                    <th>Product Model</th>
                    <th className="cursor-pointer hover:bg-white/20 transition-colors group" onClick={() => handleSort('status')}>
                      <div className="flex items-center gap-1">Status <SortIcon field="status" /></div>
                    </th>
                    <th className="cursor-pointer hover:bg-white/20 transition-colors group" onClick={() => handleSort('created_at')}>
                      <div className="flex items-center gap-1">Created <SortIcon field="created_at" /></div>
                    </th>
                    <th className="text-right">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {claims.length === 0 ? (
                    <tr>
                      <td colSpan={user.role !== 'customer' ? 7 : 6} className="p-12 text-center text-muted-foreground font-medium">
                        {search || statusFilter || dateFrom || dateTo
                          ? 'No claims match your current filters.'
                          : 'No active claims found in the system.'}
                      </td>
                    </tr>
                  ) : (
                    claims.map((claim) => (
                      <tr key={claim.id} className={selectedIds.includes(claim.id) ? 'bg-primary/5' : ''}>
                        {user.role !== 'customer' && (
                          <td>
                            <input 
                              type="checkbox" 
                              className="accent-primary w-4 h-4"
                              checked={selectedIds.includes(claim.id)} 
                              onChange={() => toggleSelect(claim.id)} 
                            />
                          </td>
                        )}
                        <td className="font-heading font-bold text-primary">#{claim.id}</td>
                        <td className="font-semibold text-foreground/80">{claim.customer_name}</td>
                        <td className="text-muted-foreground font-medium">{claim.product_model}</td>
                        <td>{getStatusBadge(claim.status)}</td>
                        <td className="text-sm font-medium text-muted-foreground">{formatDate(claim.created_at)}</td>
                        <td className="text-right">
                          <Link to={`/claims/${claim.id}`} className="btn btn-secondary py-1 px-3 text-sm">
                            Review <ChevronRight size={14} />
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-between items-center p-4 border-t border-white/30 bg-white/10">
                  <span className="text-primary/70 font-semibold text-sm">
                    Showing {page * PAGE_SIZE + 1} to {Math.min((page + 1) * PAGE_SIZE, total)} of {total} entries
                  </span>
                  <div className="flex gap-2">
                    <button className="btn btn-secondary py-1.5 px-3 text-sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
                      <ChevronLeft size={16} /> Prev
                    </button>
                    <button className="btn btn-secondary py-1.5 px-3 text-sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>
                      Next <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              )}
              {totalPages <= 1 && total > 0 && (
                <div className="p-4 border-t border-white/30 bg-white/10 text-center">
                  <span className="text-primary/70 font-semibold text-sm">{total} total entry{total !== 1 ? 's' : ''}</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Right Sidebar: Stats */}
      <div className="xl:col-span-1 flex flex-col gap-4">
        <h3 className="text-xl m-0 mb-2 text-primary font-bold px-1">Quick Insights</h3>
        
        <div className="glass-card flex items-center gap-4 p-5 hover:-translate-y-1 transition-transform cursor-default">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary shadow-inner border border-primary/20">
            <BarChart3 size={24} />
          </div>
          <div>
            <div className="text-3xl font-heading font-black text-foreground leading-none">{stats.total}</div>
            <div className="text-xs font-bold text-primary uppercase tracking-wider mt-1">Total Claims</div>
          </div>
        </div>

        <div className="glass-card flex items-center gap-4 p-5 hover:-translate-y-1 transition-transform cursor-default">
          <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center text-orange-500 shadow-inner border border-orange-500/20">
            <Clock size={24} />
          </div>
          <div>
            <div className="text-3xl font-heading font-black text-foreground leading-none">{stats.submitted}</div>
            <div className="text-xs font-bold text-orange-500 uppercase tracking-wider mt-1">Pending</div>
          </div>
        </div>

        <div className="glass-card flex items-center gap-4 p-5 hover:-translate-y-1 transition-transform cursor-default">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-600 shadow-inner border border-cyan-500/20">
            <CheckCircle2 size={24} />
          </div>
          <div>
            <div className="text-3xl font-heading font-black text-foreground leading-none">{stats.triaged}</div>
            <div className="text-xs font-bold text-cyan-600 uppercase tracking-wider mt-1">AI Triaged</div>
          </div>
        </div>

        <div className="glass-card flex items-center gap-4 p-5 hover:-translate-y-1 transition-transform cursor-default">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-600 shadow-inner border border-emerald-500/20">
            <CheckCircle2 size={24} />
          </div>
          <div>
            <div className="text-3xl font-heading font-black text-foreground leading-none">{stats.approved}</div>
            <div className="text-xs font-bold text-emerald-600 uppercase tracking-wider mt-1">Approved</div>
          </div>
        </div>

        <div className="glass-card flex items-center gap-4 p-5 hover:-translate-y-1 transition-transform cursor-default">
          <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center text-red-600 shadow-inner border border-red-500/20">
            <XCircle size={24} />
          </div>
          <div>
            <div className="text-3xl font-heading font-black text-foreground leading-none">{stats.rejected}</div>
            <div className="text-xs font-bold text-red-600 uppercase tracking-wider mt-1">Rejected</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
