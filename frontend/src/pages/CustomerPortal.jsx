import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Package, Clock, CheckCircle2, AlertCircle, ChevronRight, XCircle, FileText, Settings, LogOut, LifeBuoy, BookOpen, HeadphonesIcon, Plus } from 'lucide-react';
import api from '../api';
import { useAuth } from '../context/AuthContext';

export default function CustomerPortal() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMyClaims = async () => {
      try {
        const { data } = await api.get('/claims/', { params: { limit: 50, sort_by: 'created_at', sort_order: 'desc' } });
        setClaims(data.claims);
      } catch (err) {
        console.error("Failed to load claims", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMyClaims();
  }, []);

  const getStatusDisplay = (status) => {
    switch (status) {
      case 'submitted': return { color: 'text-muted-foreground', bg: 'bg-muted', icon: <Clock size={24} />, text: 'Submitted' };
      case 'processing': return { color: 'text-warning', bg: 'bg-warning/10', icon: <AlertCircle size={24} />, text: 'In Review' };
      case 'triaged': return { color: 'text-info', bg: 'bg-info/10', icon: <CheckCircle2 size={24} />, text: 'AI Analyzed' };
      case 'approved': return { color: 'text-success', bg: 'bg-success/10', icon: <CheckCircle2 size={24} />, text: 'Approved' };
      case 'rejected': return { color: 'text-danger', bg: 'bg-danger/10', icon: <XCircle size={24} />, text: 'Rejected' };
      default: return { color: 'text-muted', bg: 'bg-muted', icon: <Package size={24} />, text: status };
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, { 
      year: 'numeric', month: 'long', day: 'numeric' 
    });
  };

  if (loading) {
    return <div className="p-8 text-center text-muted">Loading your claims...</div>;
  }

  const activeClaimsCount = claims.filter(c => c.status !== 'approved' && c.status !== 'rejected').length;
  const resolvedClaimsCount = claims.filter(c => c.status === 'approved' || c.status === 'rejected').length;

  return (
    <div className="max-w-7xl mx-auto animate-fade-in grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      {/* Left Column: Main Content */}
      <div className="lg:col-span-2 flex flex-col gap-6">
        
        {/* Compact Header */}
        <div className="flex flex-wrap justify-between items-center gap-4 pb-4 border-b border-primary/10 mb-4">
          <div>
            <h2 className="flex items-center gap-2 m-0 text-2xl font-heading font-extrabold text-foreground">
              <FileText className="text-primary" size={24} /> My Service Portal
            </h2>
            <p className="mt-1 text-sm text-muted-foreground font-medium hidden sm:block">Track and manage your warranty requests.</p>
          </div>
          <Link to="/new-claim" className="btn btn-primary py-2.5 px-5 text-sm shadow-sm rounded-lg hover:-translate-y-0.5 transition-all flex items-center gap-2 shrink-0">
            <Plus size={16} /> New Claim
          </Link>
        </div>

        {/* Quick Stats Row */}
        <div className="grid grid-cols-3 gap-4">
          <div className="glass-card p-4 flex flex-col items-center justify-center text-center">
            <span className="text-3xl font-heading font-black text-foreground">{claims.length}</span>
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider mt-1">Total Claims</span>
          </div>
          <div className="glass-card p-4 flex flex-col items-center justify-center text-center bg-orange-500/5 border-orange-500/20">
            <span className="text-3xl font-heading font-black text-orange-600">{activeClaimsCount}</span>
            <span className="text-xs font-bold text-orange-600 uppercase tracking-wider mt-1">In Progress</span>
          </div>
          <div className="glass-card p-4 flex flex-col items-center justify-center text-center bg-emerald-500/5 border-emerald-500/20">
            <span className="text-3xl font-heading font-black text-emerald-600">{resolvedClaimsCount}</span>
            <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider mt-1">Resolved</span>
          </div>
        </div>

        {/* Claims List Header */}
        <div className="mt-2">
          <h3 className="text-xl font-heading font-bold text-foreground">Recent Requests</h3>
        </div>

        {/* Claims List */}
        {claims.length === 0 ? (
          <div className="glass-card text-center p-16 flex flex-col items-center justify-center relative overflow-hidden group border-dashed border-2 border-primary/20">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-primary/5 opacity-0 group-hover:opacity-100 transition duration-700"></div>
            <div className="w-24 h-24 mb-6 rounded-full bg-primary/10 flex items-center justify-center shadow-inner relative">
               <div className="absolute inset-0 rounded-full animate-ping bg-primary/20 opacity-20"></div>
               <Package size={40} className="text-primary opacity-80" />
            </div>
            <h3 className="mb-2 text-2xl font-heading text-foreground">No active claims</h3>
            <p className="mb-8 text-muted-foreground text-lg max-w-md">You haven't submitted any warranty claims yet. Whenever you have an issue, file a claim here.</p>
            <Link to="/new-claim" className="btn btn-primary px-8 py-3 shadow-lg shadow-primary/20 hover:scale-105 transition-transform z-10">Get Started</Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {claims.map(claim => {
              const display = getStatusDisplay(claim.status);
              return (
                <Link to={`/claims/${claim.id}`} key={claim.id} className="glass-card hover:-translate-y-1 transition-all duration-300 no-underline block p-6 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-white/40 to-transparent rounded-bl-full pointer-events-none -mr-4 -mt-4"></div>
                  <div className="flex flex-col gap-4 relative z-10">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-inner border border-white/40 ${display.bg} ${display.color}`}>
                          {display.icon}
                        </div>
                        <div>
                          <h4 className="m-0 text-foreground font-bold text-lg">{claim.product_model}</h4>
                          <p className="text-muted text-xs font-mono mt-1">Serial: {claim.serial_number}</p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                         <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${display.bg} ${display.color} border-current/20`}>{display.text}</span>
                         <span className="font-heading text-sm text-primary font-bold">#{claim.id}</span>
                      </div>
                    </div>
                    
                    <div className="pl-[4rem]">
                       <p className="text-muted-foreground text-sm line-clamp-2 leading-relaxed">{claim.complaint_text}</p>
                    </div>
                    
                    <div className="flex items-center justify-between border-t border-color-border pt-4 mt-2">
                      <span className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
                        <Clock size={14} className="opacity-70"/> {formatDate(claim.created_at)}
                      </span>
                      <span className="flex items-center gap-1 text-primary text-sm font-semibold group-hover:underline group-hover:translate-x-1 transition-transform">
                        View Details <ChevronRight size={16} />
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>

      {/* Right Column: Support Widget */}
      <div className="lg:col-span-1 flex flex-col gap-6">
        

        {/* Announcement / Tip Widget */}
        <div className="glass-card p-6 bg-primary/5 border-primary/20">
          <div className="flex items-center gap-2 mb-3 text-primary font-bold">
            <CheckCircle2 size={18} /> Quick Tip
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed m-0">
            Providing clear, well-lit photos of the defective item and a copy of your receipt can speed up the AI triage process by up to 50%.
          </p>
        </div>

      </div>
    </div>
  );
}
