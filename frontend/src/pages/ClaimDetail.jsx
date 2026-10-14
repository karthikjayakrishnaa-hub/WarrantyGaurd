import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, XCircle, AlertCircle, ShieldAlert, FileText, Download, User, Package, Clock, Activity, Upload, Zap, RotateCcw, ArrowUpDown, MessageSquare, Eye } from 'lucide-react';
import api from '../api';
import { useAuth } from '../context/AuthContext';

const ClaimDetail = () => {
  const { id } = useParams();
  const { isAgent } = useAuth();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewingImageLoading, setViewingImageLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [timelineOrder, setTimelineOrder] = useState('desc'); // 'desc' = Newest first, 'asc' = Chronological
  const [pipelineProgress, setPipelineProgress] = useState(null);

  const PIPELINE_STEPS = [
    { step: 1, name: 'Evidence Fetching' },
    { step: 2, name: 'Invoice OCR' },
    { step: 3, name: 'Label OCR' },
    { step: 4, name: 'NLP Complaint' },
    { step: 5, name: 'Rule Engine' },
    { step: 6, name: 'Duplicate Check' },
    { step: 7, name: 'Policy RAG' },
    { step: 8, name: 'AI Decision' },
  ];

  const intervalRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const pollStatus = async () => {
      try {
        const claimRes = await api.get(`/claims/${id}`);
        if (!isMounted) return;
        const currentClaim = claimRes.data;
        setClaim(currentClaim);

        // If claim is still processing or newly submitted, check pipeline progress
        if (currentClaim.status === 'processing' || currentClaim.status === 'submitted') {
          try {
            const pipeRes = await api.get(`/claims/${id}/pipeline/status`);
            if (!isMounted) return;
            setPipelineProgress(pipeRes.data);

            if (pipeRes.data.status === 'completed') {
              // Re-fetch full claim data to get triage_result
              const freshClaim = await api.get(`/claims/${id}`);
              if (isMounted) {
                setClaim(freshClaim.data);
                setPipelineProgress(null);
              }
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
              }
              return;
            } else if (pipeRes.data.status === 'failed') {
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
              }
              return;
            }
          } catch (e) {
            // Pipeline status endpoint might be temporarily unreachable
          }
        } else {
          // Claim is already in final state (triaged, approved, rejected, closed)
          setPipelineProgress(null);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } catch (error) {
        console.error("Failed to fetch claim", error);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    pollStatus();
    intervalRef.current = setInterval(pollStatus, 2000);

    return () => {
      isMounted = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [id]);

  const handleStatusUpdate = async (newStatus) => {
    try {
      setLoading(true);
      const response = await api.patch(`/claims/${id}/status`, { status: newStatus });
      setClaim(response.data);
    } catch (error) {
      console.error("Failed to update status", error);
      alert("Failed to update status. See console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleRedoTriage = async () => {
    try {
      setLoading(true);
      setPipelineProgress({ status: 'running', current_step: 0, total_steps: 8, step_name: 'Starting Pipeline...' });
      await api.post(`/claims/${id}/pipeline/run?force=true`);
      const response = await api.get(`/claims/${id}`);
      setClaim(response.data);

      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(async () => {
        try {
          const pipeRes = await api.get(`/claims/${id}/pipeline/status`);
          setPipelineProgress(pipeRes.data);
          if (pipeRes.data.status === 'completed' || pipeRes.data.status === 'failed') {
            const finalClaim = await api.get(`/claims/${id}`);
            setClaim(finalClaim.data);
            if (pipeRes.data.status === 'completed') setPipelineProgress(null);
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 2000);
    } catch (error) {
      console.error("Failed to redo triage", error);
      alert("Failed to redo triage.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (evidenceId) => {
    try {
      const response = await api.get(`/claims/${id}/evidence/${evidenceId}/download`);
      if (response.data.url) {
        window.open(response.data.url, "_blank");
      }
    } catch (error) {
      console.error("Failed to get download link", error);
      alert("Failed to get download link.");
    }
  };

  const handleViewImage = async (evidenceId) => {
    try {
      setViewingImageLoading(true);
      const response = await api.get(`/claims/${id}/evidence/${evidenceId}/download`);
      if (response.data.url) {
        setSelectedImage(response.data.url);
      }
    } catch (error) {
      console.error("Failed to load image", error);
      alert("Failed to load image.");
    } finally {
      setViewingImageLoading(false);
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center mt-20 animate-fade-in">
      <div className="status-indicator warning mb-4" style={{ width: 16, height: 16 }}></div>
      <p>Loading claim details...</p>
    </div>
  );
  if (!claim) return <div className="text-center mt-20 text-danger animate-fade-in">Claim not found in the system.</div>;

  const getTriageIcon = (category) => {
    switch (category) {
      case 'approved': return <CheckCircle2 className="text-success" size={28} />;
      case 'rejected': return <XCircle className="text-danger" size={28} />;
      case 'fraud_suspected':
      case 'duplicate_evidence': return <ShieldAlert className="text-danger" size={28} />;
      default: return <AlertCircle className="text-gold" size={28} />;
    }
  };

  const getTriageColor = (category) => {
    switch (category) {
      case 'approved': return 'var(--success)';
      case 'rejected':
      case 'fraud_suspected':
      case 'duplicate_evidence': return 'var(--danger)';
      default: return 'var(--accent-gold)';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const formatTimeAgo = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffMin < 1) return 'just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    if (diffDay < 7) return `${diffDay}d ago`;
    return formatDate(dateString);
  };

  const getAuditIcon = (action) => {
    switch (action) {
      case 'claim_created': return <FileText size={14} />;
      case 'evidence_uploaded': return <Upload size={14} />;
      case 'pipeline_started': return <Zap size={14} />;
      case 'pipeline_completed': return <CheckCircle2 size={14} />;
      case 'claim_approved': return <CheckCircle2 size={14} />;
      case 'claim_rejected': return <XCircle size={14} />;
      case 'status_changed': return <RotateCcw size={14} />;
      default: return <Activity size={14} />;
    }
  };

  const getAuditColor = (action) => {
    switch (action) {
      case 'claim_approved':
      case 'pipeline_completed': return 'var(--success)';
      case 'claim_rejected': return 'var(--danger)';
      case 'pipeline_started': return 'var(--info)';
      default: return 'var(--text-secondary)';
    }
  };

  const getAuditLabel = (action) => {
    return action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  const triage = claim.triage_result;
  const auditLogs = claim.audit_logs || [];
  const displayedLogs = timelineOrder === 'asc' ? [...auditLogs].reverse() : auditLogs;

  return (
    <div className="animate-fade-in pb-12">
      {/* Header Bar */}
      <div className="flex justify-between items-end mb-8 border-b border-primary/10 pb-6">
        <div>
          <div className="mb-4">
            <Link to="/" className="text-sm font-semibold text-primary/70 hover:text-primary transition-colors flex items-center gap-2">
              <ArrowLeft size={16} /> Back to Hub
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <h2 className="text-4xl font-black text-primary m-0 tracking-tight">Claim #{claim.id}</h2>
            <span className={`px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider
              ${claim.status === 'approved' ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20' : 
                claim.status === 'rejected' ? 'bg-red-500/10 text-red-600 border border-red-500/20' : 
                claim.status === 'triaged' ? 'bg-cyan-500/10 text-cyan-600 border border-cyan-500/20' : 
                'bg-orange-500/10 text-orange-600 border border-orange-500/20'}`}>
              {claim.status}
            </span>
          </div>
          <p className="text-muted-foreground font-medium mt-2">Filed on {formatDate(claim.created_at)}</p>
        </div>

        {isAgent && (
          <div className="flex gap-3">
            <button className="btn bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-700 border border-cyan-500/30 transition-all font-bold px-6 py-2" onClick={handleRedoTriage} disabled={loading || claim.status === 'processing'}>
              <RotateCcw size={18}/> Redo Triage
            </button>
            <button className="btn bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 border border-emerald-500/30 transition-all font-bold px-6 py-2" onClick={() => handleStatusUpdate('approved')} disabled={claim.status === 'approved' || claim.status === 'rejected'}>
              <CheckCircle2 size={18}/> Approve
            </button>
            <button className="btn bg-red-500/10 hover:bg-red-500/20 text-red-700 border border-red-500/30 transition-all font-bold px-6 py-2" onClick={() => handleStatusUpdate('rejected')} disabled={claim.status === 'approved' || claim.status === 'rejected'}>
              <XCircle size={18}/> Reject
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content (Left, 2 Columns Wide) */}
        <div className="lg:col-span-2 flex flex-col gap-8 animate-fade-in animate-delay-1">
          
          {/* Hero AI Decision Card - Visible for all claims and users */}
          <div className="glass-card relative overflow-hidden p-8 shadow-xl shadow-primary/5" style={triage ? { borderTop: `4px solid ${getTriageColor(triage.category)}` } : {}}>
            <div className="absolute top-0 right-0 p-8 opacity-10">
              {triage ? getTriageIcon(triage.category) : <AlertCircle size={120} />}
            </div>
            
            <div className="relative z-10">
              <h3 className="flex items-center gap-3 text-2xl font-black text-foreground mb-6">
                <ShieldAlert className="text-primary" size={28} /> AI Triage Intelligence
              </h3>
              
              {claim.status === 'processing' || (pipelineProgress && pipelineProgress.status === 'running') ? (
                <div className="p-6 rounded-2xl bg-primary/5 border border-primary/20 flex flex-col gap-5">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-3">
                      <div className="w-3.5 h-3.5 rounded-full bg-cyan-500 animate-ping" />
                      <span className="text-lg font-black text-primary">
                        AI Triage Pipeline in Progress
                      </span>
                    </div>
                    <span className="text-xs font-bold px-3 py-1 bg-cyan-500/10 text-cyan-700 rounded-full border border-cyan-500/20">
                      {pipelineProgress?.current_step ? `Step ${pipelineProgress.current_step} of 8` : 'Processing...'}
                    </span>
                  </div>

                  {/* Active Step Banner */}
                  <div className="bg-white/70 p-4 rounded-xl border border-white/80 shadow-sm flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Zap size={20} className="text-cyan-600 animate-bounce" />
                      <span className="font-bold text-foreground">
                        {pipelineProgress?.step_name || 'Executing ML models (OCR & Policy Evaluation)...'}
                      </span>
                    </div>
                    <span className="text-xs text-primary font-mono font-bold">
                      {pipelineProgress?.current_step ? `${Math.round((pipelineProgress.current_step / 8) * 100)}%` : '10%'}
                    </span>
                  </div>

                  {/* Animated Progress Bar */}
                  <div className="w-full bg-slate-200/80 rounded-full h-3 overflow-hidden shadow-inner">
                    <div
                      className="bg-gradient-to-r from-cyan-500 via-teal-500 to-emerald-500 h-3 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${Math.max(8, ((pipelineProgress?.current_step || 0) / 8) * 100)}%` }}
                    />
                  </div>

                  {/* 8 Step Mini Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
                    {PIPELINE_STEPS.map((s) => {
                      const stepNum = pipelineProgress?.current_step || 0;
                      const isDone = stepNum > s.step;
                      const isCurrent = stepNum === s.step;
                      return (
                        <div
                          key={s.step}
                          className={`p-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
                            isDone
                              ? 'bg-emerald-500/10 text-emerald-700 border border-emerald-500/20'
                              : isCurrent
                              ? 'bg-cyan-500/20 text-cyan-800 border border-cyan-500/40 shadow-sm animate-pulse'
                              : 'bg-slate-100/60 text-slate-400 border border-slate-200/40'
                          }`}
                        >
                          <span className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-black bg-white shadow-sm shrink-0">
                            {isDone ? '✓' : s.step}
                          </span>
                          <span className="truncate">{s.name}</span>
                        </div>
                      );
                    })}
                  </div>

                  <p className="text-xs text-muted-foreground text-center m-0">
                    Processing document OCR and reasoning models on CPU. The page updates automatically when complete.
                  </p>
                </div>
              ) : triage ? (
                <div className="flex flex-col gap-6">
                  {/* Triage 8-Step Verification Audit Status */}
                  <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 flex flex-col gap-3 shadow-sm">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={18} className="text-emerald-600" />
                        <span className="text-xs font-black uppercase tracking-wider text-emerald-800">
                          8-Step AI Triage Pipeline Verified
                        </span>
                      </div>
                      <span className="text-[11px] font-bold px-3 py-1 bg-emerald-500/15 text-emerald-800 rounded-full border border-emerald-500/20">
                        8 / 8 Steps Completed
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {PIPELINE_STEPS.map((s) => (
                        <div
                          key={s.step}
                          className="p-2 rounded-xl text-xs font-bold flex items-center gap-2 bg-white/80 text-emerald-800 border border-emerald-500/20 shadow-xs"
                        >
                          <span className="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-black bg-emerald-600 text-white shrink-0">
                            ✓
                          </span>
                          <span className="truncate">{s.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-sm font-bold text-muted-foreground uppercase tracking-wider mb-2 block">Determined Classification</span>
                    <div className="inline-block px-4 py-2 rounded-xl font-black text-lg tracking-wide shadow-inner"
                         style={{ backgroundColor: `${getTriageColor(triage.category)}20`, color: getTriageColor(triage.category), border: `1px solid ${getTriageColor(triage.category)}40` }}>
                      {triage.category.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-sm font-bold text-muted-foreground uppercase tracking-wider mb-2 block">Reasoning & Analysis</span>
                    <p className="text-xl font-medium text-foreground leading-relaxed">
                      {triage.reasoning_summary}
                    </p>
                  </div>
                  
                  <div className="mt-2 p-5 rounded-2xl bg-primary/5 border border-primary/10 shadow-inner">
                    <span className="text-sm font-bold text-primary uppercase tracking-wider mb-1 block">Recommended Action</span>
                    <p className="text-lg font-black text-primary m-0">{triage.recommended_action}</p>
                  </div>
                </div>
              ) : (
                <div className="p-8 border-2 border-dashed border-primary/20 rounded-2xl bg-white/10 flex flex-col items-center justify-center text-center">
                  <Clock size={40} className="text-primary/40 mb-3 animate-pulse" />
                  <p className="text-lg font-semibold text-primary/70">AI Analysis is currently pending or queued.</p>
                  <p className="text-sm text-muted-foreground mt-1">Check back shortly once the automated pipeline completes.</p>
                </div>
              )}
            </div>
          </div>


          {/* Customer Complaint */}
          <div className="glass-card p-8 shadow-lg shadow-primary/5">
            <h3 className="flex items-center gap-3 text-xl font-bold text-primary mb-4">
              <MessageSquare size={22} /> Customer Complaint
            </h3>
            <p className="text-lg text-foreground/80 leading-relaxed font-medium bg-white/40 p-6 rounded-2xl border border-white/60 shadow-inner">
              "{claim.complaint_text}"
            </p>
          </div>

          {/* Evidence Grid */}
          <div className="glass-card p-8 shadow-lg shadow-primary/5">
            <h3 className="flex items-center gap-3 text-xl font-bold text-primary mb-6">
              <FileText size={22} /> Provided Evidence
            </h3>
            
            {claim.evidence && claim.evidence.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {claim.evidence.map(ev => (
                  <div key={ev.id} className="group relative bg-white/40 p-5 rounded-2xl border border-white/60 hover:bg-white/60 hover:border-primary/30 transition-all shadow-sm flex flex-col">
                    <div className="flex justify-between items-center mb-4">
                      <span className="px-3 py-1 bg-primary/10 text-primary text-xs font-black uppercase tracking-wider rounded-lg border border-primary/20">
                        {ev.type.replace('_', ' ')}
                      </span>
                      <div className="flex gap-2">
                        <button onClick={() => handleViewImage(ev.id)} disabled={viewingImageLoading} className="text-primary hover:text-primary/70 transition-colors bg-white/80 p-2 rounded-full shadow-sm hover:shadow" title="View Image">
                          <Eye size={16}/>
                        </button>
                        <button onClick={() => handleDownload(ev.id)} className="text-primary hover:text-primary/70 transition-colors bg-white/80 p-2 rounded-full shadow-sm hover:shadow" title="Download">
                          <Download size={16}/>
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mt-auto">
                      <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">SHA-256 Checksum</span>
                        <span className="text-xs font-mono text-primary truncate" title={ev.file_hash}>
                          {ev.file_hash.substring(0, 24)}...
                        </span>
                      </div>
                      
                      {ev.phash && (
                        <div className="flex flex-col">
                          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Perceptual Hash</span>
                          <span className="text-xs font-mono text-primary truncate">
                            {ev.phash}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-primary/20 rounded-2xl bg-white/10 text-center">
                <FileText size={40} className="text-primary/30 mb-3" />
                <p className="text-lg font-semibold text-primary/60">No evidence attached to this claim.</p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar (Right, 1 Column Wide) */}
        <div className="lg:col-span-1 flex flex-col gap-8 animate-fade-in animate-delay-2">
          
          {/* Product & Customer Card */}
          <div className="glass-card p-6 shadow-lg shadow-primary/5">
            <h3 className="text-lg font-black text-foreground mb-6 uppercase tracking-wider flex items-center gap-2 border-b border-primary/10 pb-4">
              <Package size={18} className="text-primary" /> Device Info
            </h3>
            
            <div className="space-y-5">
              <div>
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block mb-1">Customer</span>
                <div className="text-base font-semibold text-foreground flex items-center gap-2">
                  <User size={16} className="text-primary/60" /> {claim.customer_name}
                </div>
              </div>
              
              <div>
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block mb-1">Model</span>
                <div className="text-base font-semibold text-foreground">
                  {claim.product_model}
                </div>
              </div>
              
              <div>
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider block mb-1">Serial Number</span>
                <div className="text-base font-mono font-bold text-primary bg-primary/5 inline-block px-3 py-1 rounded-lg border border-primary/10">
                  {claim.serial_number}
                </div>
              </div>
            </div>
          </div>

          {/* Activity Timeline */}
          <div className="glass-card p-6 shadow-lg shadow-primary/5 flex-1 max-h-[800px] overflow-y-auto">
            <div className="flex justify-between items-center mb-6 sticky top-0 bg-white/80 backdrop-blur-md z-10 py-2 -mx-6 px-6 border-b border-white">
              <h3 className="text-lg font-black text-foreground m-0 uppercase tracking-wider flex items-center gap-2">
                <Activity size={18} className="text-primary" /> History
              </h3>
              <button 
                onClick={() => setTimelineOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
                className="text-xs font-bold text-primary hover:text-primary/70 flex items-center gap-1 bg-white/50 px-2 py-1 rounded border border-white"
              >
                <ArrowUpDown size={12} /> {timelineOrder === 'desc' ? 'Newest' : 'Oldest'}
              </button>
            </div>

            {displayedLogs.length > 0 ? (
              <div className="relative pl-4 space-y-6 before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-primary/20 before:to-transparent">
                {displayedLogs.map((log) => (
                  <div key={log.id} className="relative flex items-center gap-4">
                    <div className="relative z-10 w-8 h-8 flex items-center justify-center bg-white border-2 rounded-full shadow-sm" style={{ borderColor: getAuditColor(log.action), color: getAuditColor(log.action) }}>
                      {getAuditIcon(log.action)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-foreground mb-0.5" style={{ color: getAuditColor(log.action) }}>
                        {getAuditLabel(log.action)}
                      </p>
                      {log.details && (
                        <p className="text-xs font-medium text-muted-foreground truncate" title={log.details}>
                          {log.details}
                        </p>
                      )}
                      <p className="text-[10px] font-bold text-primary/50 uppercase mt-1">
                        {formatTimeAgo(log.created_at)} • {log.user_name || 'System'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Activity size={32} className="text-muted/50 mx-auto mb-3" />
                <p className="text-sm font-medium text-muted-foreground">No activity recorded yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Image Viewer Modal */}
      {selectedImage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fade-in" onClick={() => setSelectedImage(null)}>
          <div className="relative max-w-4xl w-full max-h-[90vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="absolute -top-12 right-0">
              <button onClick={() => setSelectedImage(null)} className="text-white hover:text-gray-300 bg-black/50 p-2 rounded-full transition-colors">
                <XCircle size={24} />
              </button>
            </div>
            <img src={selectedImage} alt="Evidence Document" className="w-full h-full object-contain rounded-lg shadow-2xl bg-white/5" />
          </div>
        </div>
      )}
    </div>
  );
};

export default ClaimDetail;
