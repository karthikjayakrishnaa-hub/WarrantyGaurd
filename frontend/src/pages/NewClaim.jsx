import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, AlertCircle, FileText, User, Package, Hash, MessageSquare, Upload, Plus, Trash2 } from 'lucide-react';
import api from '../api';

const NewClaim = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    customer_name: '',
    product_model: '',
    serial_number: '',
    complaint_text: ''
  });

  const [evidence, setEvidence] = useState({
    invoice: null,
    label_photo: null,
    product_photo: null
  });

  const handleEvidenceChange = (type, file) => {
    setEvidence(prev => ({ ...prev, [type]: file }));
  };

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const filesToUpload = [
      { file: evidence.invoice, type: 'invoice' },
      { file: evidence.label_photo, type: 'label_photo' },
      { file: evidence.product_photo, type: 'product_photo' }
    ].filter(ev => ev.file !== null);

    if (filesToUpload.length === 0) {
      setError("Please upload at least one evidence file (e.g., product photo).");
      setLoading(false);
      return;
    }

    // ── Pre-flight validation ──────────────────────────────────────────────────
    // Validate file types CLIENT-SIDE before hitting the API.
    // This prevents ghost claims (partial DB records) caused by the upload loop
    // failing mid-way on a bad file, which would leave orphaned evidence that
    // incorrectly triggers duplicate detection on the next attempt.
    const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    const ALLOWED_LABEL = 'JPG, PNG, or PDF';
    for (const ev of filesToUpload) {
      const mime = ev.file.type || '';
      const ext = ev.file.name.split('.').pop().toLowerCase();
      const extValid = ['jpg', 'jpeg', 'png', 'pdf'].includes(ext);
      if (!ALLOWED_TYPES.includes(mime) && !extValid) {
        setError(`"${ev.file.name}" has an unsupported format. Please upload a ${ALLOWED_LABEL} file.`);
        setLoading(false);
        return;
      }
    }
    // ──────────────────────────────────────────────────────────────────────────

    let claimId = null;
    try {
      // 1. Create the base claim
      const claimResponse = await api.post('/claims/', formData);
      claimId = claimResponse.data.id;

      // 2. Upload all evidence
      for (const ev of filesToUpload) {
        const formDataPayload = new FormData();
        formDataPayload.append('file', ev.file);
        
        await api.post(`/claims/${claimId}/evidence`, formDataPayload, {
          params: { type: ev.type },
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }

      // 3. Fire-and-forget the AI pipeline — DO NOT await.
      // The pipeline is a long-running ML task (OCR + NLP + GenAI).
      // Awaiting it here freezes the UI for the full duration.
      // The claim detail page polls /pipeline/status to show live progress.
      api.post(`/claims/${claimId}/pipeline/run`).catch(err =>
        console.error('Pipeline trigger failed (non-blocking):', err)
      );

      // 4. Redirect immediately — pipeline runs in background
      navigate(`/claims/${claimId}`);
    } catch (err) {
      console.error("Failed to submit claim:", err);

      // ── Ghost claim cleanup ────────────────────────────────────────────────
      // If the claim was created but evidence upload failed, delete the
      // orphaned claim so its partial evidence records don't trigger false
      // duplicate flags on the user's next submission attempt.
      if (claimId) {
        api.delete(`/claims/${claimId}`).catch(() => {});
      }
      // ──────────────────────────────────────────────────────────────────────

      if (err.response && err.response.data && err.response.data.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          setError(detail.map(d => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(', '));
        } else if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError(JSON.stringify(detail));
        }
      } else {
        setError("Failed to submit claim. Please check your connection and try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <Link to="/" className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
          <ArrowLeft size={16} /> Back to Overview
        </Link>
      </div>

      <div className="dashboard-header mb-6">
        <div>
          <h2 className="flex items-center gap-3">
            <FileText size={28} className="text-gold" />
            File a New Claim
          </h2>
          <p>Enter the details below to initialize a warranty claim.</p>
        </div>
      </div>

      <div className="glass-card" style={{ maxWidth: '800px', margin: '0 auto' }}>
        {error && (
          <div className="p-4 mb-6 rounded flex items-start gap-3" style={{ background: 'rgba(255, 92, 92, 0.1)', border: '1px solid rgba(255, 92, 92, 0.3)' }}>
            <AlertCircle className="text-danger mt-1" size={20} />
            <div className="text-danger">{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex-col gap-6">
          <div className="detail-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="form-group flex-col gap-2">
              <label className="text-sm text-muted uppercase tracking-wider flex items-center gap-2">
                <User size={14} /> Customer Name
              </label>
              <input
                type="text"
                name="customer_name"
                value={formData.customer_name}
                onChange={handleChange}
                required
                placeholder="e.g., Jane Doe"
                className="form-input"
              />
            </div>

            <div className="form-group flex-col gap-2">
              <label className="text-sm text-muted uppercase tracking-wider flex items-center gap-2">
                <Package size={14} /> Product Model
              </label>
              <input
                type="text"
                name="product_model"
                value={formData.product_model}
                onChange={handleChange}
                required
                placeholder="e.g., SmartWatch Pro X"
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group flex-col gap-2 mt-4">
            <label className="text-sm text-muted uppercase tracking-wider flex items-center gap-2">
              <Hash size={14} /> Serial Number
            </label>
            <input
              type="text"
              name="serial_number"
              value={formData.serial_number}
              onChange={handleChange}
              required
              placeholder="e.g., S/N-1029384756"
              className="form-input font-mono"
            />
          </div>

          <div className="form-group flex-col gap-2 mt-4">
            <label className="text-sm text-muted uppercase tracking-wider flex items-center gap-2">
              <MessageSquare size={14} /> Complaint Description
            </label>
            <textarea
              name="complaint_text"
              value={formData.complaint_text}
              onChange={handleChange}
              required
              rows="5"
              placeholder="Describe the issue in detail..."
              className="form-textarea"
            />
          </div>

          {/* Evidence Section */}
          <div className="mt-6 pt-6" style={{ borderTop: '1px solid var(--border-color)' }}>
            <div className="mb-4">
              <label className="text-lg text-foreground font-semibold flex items-center gap-2">
                <Upload size={20} className="text-primary" /> Required Evidence
              </label>
              <p className="text-sm text-muted mt-1">Please provide the following images to help us verify your claim.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mt-6">
              {/* Product Photo */}
              <div className="card p-4 flex flex-col gap-3 bg-muted/20 border border-color-border/50">
                <div className="flex items-center gap-2">
                  <Package size={18} className="text-info" />
                  <span className="font-semibold text-sm">Product Photo</span>
                </div>
                <p className="text-xs text-muted-foreground">Clear photo showing the overall condition and damage.</p>
                <div className="mt-auto">
                  <input 
                    type="file" 
                    onChange={(e) => handleEvidenceChange('product_photo', e.target.files[0])}
                    className="form-input text-xs w-full cursor-pointer file:mr-2 file:py-1 file:px-3 file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
                    accept="image/*"
                  />
                </div>
              </div>

              {/* Product Label */}
              <div className="card p-4 flex flex-col gap-3 bg-muted/20 border border-color-border/50">
                <div className="flex items-center gap-2">
                  <Hash size={18} className="text-warning" />
                  <span className="font-semibold text-sm">Product Label</span>
                </div>
                <p className="text-xs text-muted-foreground">Photo of the label showing the serial number clearly.</p>
                <div className="mt-auto">
                  <input 
                    type="file" 
                    onChange={(e) => handleEvidenceChange('label_photo', e.target.files[0])}
                    className="form-input text-xs w-full cursor-pointer file:mr-2 file:py-1 file:px-3 file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
                    accept="image/*"
                  />
                </div>
              </div>

              {/* Invoice / Bill */}
              <div className="card p-4 flex flex-col gap-3 bg-muted/20 border border-color-border/50">
                <div className="flex items-center gap-2">
                  <FileText size={18} className="text-success" />
                  <span className="font-semibold text-sm">Invoice / Bill</span>
                </div>
                <p className="text-xs text-muted-foreground">Original purchase receipt or invoice.</p>
                <div className="mt-auto">
                  <input 
                    type="file" 
                    onChange={(e) => handleEvidenceChange('invoice', e.target.files[0])}
                    className="form-input text-xs w-full cursor-pointer file:mr-2 file:py-1 file:px-3 file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
                    accept="image/*,.pdf"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end mt-6 pt-6" style={{ borderTop: '1px solid var(--border-color)' }}>
            <button type="submit" className="btn btn-primary" disabled={loading} style={{ padding: '0.8rem 2rem' }}>
              {loading ? (
                <>
                  <div className="status-indicator warning" style={{ width: 12, height: 12, margin: 0, marginRight: '8px' }}></div>
                  Submitting...
                </>
              ) : (
                <>
                  <Save size={18} /> Submit Claim
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewClaim;
