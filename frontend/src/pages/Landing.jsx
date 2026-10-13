import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Zap, CheckCircle, BarChart, Shield, Activity, Globe, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Landing = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  const handleDashboardRedirect = () => {
    if (user?.role === 'customer') {
      navigate('/portal');
    } else {
      navigate('/dashboard');
    }
  };

  // Smooth scroll handler
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden selection:bg-green-500/30">
      
      {/* Dynamic Light Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-green-400/20 blur-[150px] rounded-full animate-pulse" style={{ animationDuration: '8s' }} />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-green-500/10 blur-[150px] rounded-full animate-pulse" style={{ animationDuration: '12s', animationDelay: '2s' }} />
      </div>

      {/* Modern Sticky Navigation (Light) */}
      <header className="fixed top-0 w-full px-6 py-4 z-50 transition-all duration-300 bg-white/70 backdrop-blur-2xl border-b border-slate-200">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({top:0, behavior:'smooth'})}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg shadow-green-500/20">
              <ShieldCheck size={22} className="text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              WarrantyGuard <span className="text-green-600 font-medium">AI</span>
            </span>
          </div>
          
          <nav className="hidden md:flex gap-8 items-center bg-white px-6 py-2.5 rounded-full border border-slate-200 shadow-sm">
            <button onClick={() => scrollTo('features')} className="text-sm font-semibold text-slate-600 hover:text-green-600 transition-colors">Platform</button>
            <button onClick={() => scrollTo('how-it-works')} className="text-sm font-semibold text-slate-600 hover:text-green-600 transition-colors">Pipeline</button>
            <button onClick={() => scrollTo('stats')} className="text-sm font-semibold text-slate-600 hover:text-green-600 transition-colors">Impact</button>
          </nav>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <button 
                onClick={handleDashboardRedirect}
                className="group relative px-6 py-2.5 rounded-full font-bold text-white overflow-hidden shadow-lg shadow-green-500/20 hover:shadow-green-500/40 transition-all duration-300 border border-green-500/50"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-green-600 transition-transform group-hover:scale-105" />
                <span className="relative flex items-center gap-2 text-sm">Dashboard <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" /></span>
              </button>
            ) : (
              <>
                <Link to="/login" className="text-sm font-bold text-slate-600 hover:text-green-600 transition-colors px-4">
                  Log in
                </Link>
                <Link to="/register" className="group relative px-6 py-2.5 rounded-full font-bold text-white overflow-hidden shadow-lg shadow-green-500/20 hover:shadow-green-500/40 transition-all duration-300 border border-green-500/50">
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-green-600 transition-transform group-hover:scale-105" />
                  <span className="relative flex items-center gap-2 text-sm">Get Started</span>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="relative z-10 pt-32 pb-10">
        {/* HERO SECTION */}
        <section className="relative min-h-[85vh] flex flex-col items-center justify-center text-center px-6 overflow-visible">
          
          {/* Version Badge */}
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white border border-slate-200 shadow-sm mb-10 animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500 shadow-[0_0_10px_var(--tw-shadow-color)] shadow-green-500/50"></span>
            </span>
            <span className="text-xs font-black text-green-600 tracking-widest uppercase">AI Triage Engine v2.0 Live</span>
          </div>

          <h1 className="text-6xl md:text-[5.5rem] font-black tracking-tighter max-w-5xl leading-[1.05] mb-8 animate-fade-in text-slate-900" style={{ animationDelay: '0.2s' }}>
            The Future of <br className="hidden md:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-br from-green-500 to-green-700">
              Warranty Operations
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mb-12 font-medium leading-relaxed animate-fade-in" style={{ animationDelay: '0.3s' }}>
            Eliminate manual review, instantly detect fraud, and resolve claims in milliseconds. The intelligent copilot for modern hardware manufacturers.
          </p>

          <div className="flex flex-col sm:flex-row gap-5 items-center animate-fade-in" style={{ animationDelay: '0.4s' }}>
            {!isAuthenticated ? (
              <>
                <Link to="/register" className="group relative px-8 py-4 rounded-full font-black text-lg text-white overflow-hidden shadow-xl shadow-green-500/30 hover:shadow-green-500/50 transition-all duration-300 hover:-translate-y-1 w-full sm:w-auto">
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-green-600 transition-transform group-hover:scale-105" />
                  <span className="relative flex items-center justify-center gap-2">Start Free Trial <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" /></span>
                </Link>
                <Link to="/login" className="px-8 py-4 rounded-full font-bold text-lg border border-slate-200 hover:border-green-200 bg-white shadow-sm hover:shadow-md text-slate-700 transition-all duration-300 w-full sm:w-auto">
                  Customer Portal
                </Link>
              </>
            ) : (
              <button onClick={handleDashboardRedirect} className="group relative px-8 py-4 rounded-full font-black text-lg text-white overflow-hidden shadow-xl shadow-green-500/30 hover:shadow-green-500/50 transition-all duration-300 hover:-translate-y-1">
                <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-green-600 transition-transform group-hover:scale-105" />
                <span className="relative flex items-center justify-center gap-2">Enter Workspace <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" /></span>
              </button>
            )}
          </div>
          
          {/* Abstract Hero Visual (Light Glass Cards) */}
          <div className="w-full max-w-6xl mt-24 grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in relative z-20" style={{ animationDelay: '0.6s' }}>
            <div className="h-48 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl p-8 flex flex-col justify-end relative overflow-hidden group hover:border-green-300 transition-all shadow-xl shadow-slate-200/50">
              <div className="absolute top-6 right-6 w-14 h-14 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Zap className="text-green-500" size={24} />
              </div>
              <h3 className="text-2xl font-bold mb-1 text-slate-800">OCR Parsing</h3>
              <p className="text-slate-500 font-medium">Instant text extraction</p>
            </div>
            
            <div className="h-48 md:-translate-y-8 rounded-[2rem] bg-gradient-to-br from-green-50 to-white border border-green-200 backdrop-blur-xl p-8 flex flex-col justify-end relative overflow-hidden shadow-2xl shadow-green-500/10 group hover:border-green-300 transition-all z-10">
              <div className="absolute inset-0 bg-gradient-to-t from-white/90 to-transparent z-0" />
              <div className="absolute top-6 right-6 w-14 h-14 rounded-2xl bg-green-500 flex items-center justify-center shadow-lg shadow-green-500/30 group-hover:scale-110 transition-transform z-10">
                <Activity className="text-white" size={24} />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-1 z-10">GenAI Triage</h3>
              <p className="text-green-700 font-medium z-10">LLM-powered reasoning</p>
            </div>
            
            <div className="h-48 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl p-8 flex flex-col justify-end relative overflow-hidden group hover:border-green-300 transition-all shadow-xl shadow-slate-200/50">
              <div className="absolute top-6 right-6 w-14 h-14 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Shield className="text-green-500" size={24} />
              </div>
              <h3 className="text-2xl font-bold mb-1 text-slate-800">Fraud Shield</h3>
              <p className="text-slate-500 font-medium">Perceptual hashing</p>
            </div>
          </div>
        </section>

        {/* STATS SECTION */}
        <section id="stats" className="py-24 px-6 border-y border-slate-200 bg-slate-100/50 relative mt-12">
          <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-12 text-center">
            <div className="space-y-3">
              <h4 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-b from-green-500 to-green-700">80%</h4>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Faster Resolution</p>
            </div>
            <div className="space-y-3">
              <h4 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-b from-green-500 to-green-700">99%</h4>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Fraud Detection</p>
            </div>
            <div className="space-y-3">
              <h4 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-b from-green-500 to-green-700">24/7</h4>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Automated Review</p>
            </div>
            <div className="space-y-3">
              <h4 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-b from-green-500 to-green-700">&lt;2s</h4>
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Avg Triage Time</p>
            </div>
          </div>
        </section>

        {/* PLATFORM FEATURES (Bento Grid) */}
        <section id="features" className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="mb-20">
              <h2 className="text-4xl md:text-[3.5rem] font-black mb-6 tracking-tight leading-tight text-slate-900">
                The ultimate <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-green-700">command center</span>
              </h2>
              <p className="text-xl md:text-2xl text-slate-600 max-w-2xl font-medium leading-relaxed">Everything you need to manage warranties at scale, built into one seamless platform.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[320px]">
              {/* Feature 1 (Wide) */}
              <div className="md:col-span-2 rounded-[2rem] bg-white border border-slate-200 p-10 flex flex-col relative overflow-hidden group hover:border-green-300 transition-all shadow-xl shadow-slate-200/50">
                <div className="absolute -top-10 -right-10 p-8 opacity-5 group-hover:scale-110 group-hover:opacity-10 transition-all duration-700 text-green-600">
                  <BarChart size={300} />
                </div>
                <div className="mt-auto relative z-10 md:w-3/4">
                  <div className="w-14 h-14 rounded-2xl bg-green-50 flex items-center justify-center mb-6 border border-green-100">
                    <BarChart className="text-green-600" size={28} />
                  </div>
                  <h3 className="text-3xl font-bold mb-4 text-slate-900">Live Analytics</h3>
                  <p className="text-slate-600 text-lg leading-relaxed font-medium">Visualize your entire operation in real-time. Track SLA breaches, approval rates, and product defect clusters with interactive charts.</p>
                </div>
              </div>

              {/* Feature 2 (Square) */}
              <div className="rounded-[2rem] bg-white border border-slate-200 p-10 flex flex-col relative overflow-hidden group hover:border-green-300 transition-all shadow-xl shadow-slate-200/50">
                <div className="mt-auto relative z-10">
                  <div className="w-14 h-14 rounded-2xl bg-green-50 flex items-center justify-center mb-6 border border-green-100">
                    <Globe className="text-green-500" size={28} />
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-slate-900">Multi-Tenant</h3>
                  <p className="text-slate-600 font-medium text-lg leading-relaxed">Securely isolate data across different organizations, branches, or brands.</p>
                </div>
              </div>

              {/* Feature 3 (Square) */}
              <div className="rounded-[2rem] bg-white border border-slate-200 p-10 flex flex-col relative overflow-hidden group hover:border-green-300 transition-all shadow-xl shadow-slate-200/50">
                <div className="mt-auto relative z-10">
                  <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mb-6 border border-slate-200">
                    <Lock className="text-slate-700" size={28} />
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-slate-900">Enterprise Security</h3>
                  <p className="text-slate-600 font-medium text-lg leading-relaxed">Role-based access, JWT refresh tokens, and strict security policies.</p>
                </div>
              </div>

              {/* Feature 4 (Wide) */}
              <div className="md:col-span-2 rounded-[2rem] bg-white border border-slate-200 p-10 flex flex-col relative overflow-hidden group hover:border-green-300 transition-all shadow-xl shadow-slate-200/50">
                <div className="absolute top-1/2 -translate-y-1/2 right-10 opacity-[0.03] group-hover:scale-110 group-hover:opacity-5 transition-all duration-700 text-green-600">
                  <ShieldCheck size={250} />
                </div>
                <div className="mt-auto relative z-10 md:w-3/4">
                  <div className="w-14 h-14 rounded-2xl bg-green-50 flex items-center justify-center mb-6 border border-green-100">
                    <ShieldCheck className="text-green-600" size={28} />
                  </div>
                  <h3 className="text-3xl font-bold mb-4 text-slate-900">RAG Policy Parsing</h3>
                  <p className="text-slate-600 text-lg leading-relaxed font-medium">Upload your custom warranty PDFs. Our LLM cross-references every single customer claim directly against your terms and conditions.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section id="how-it-works" className="py-32 px-6 relative overflow-hidden bg-slate-50">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(34,197,94,0.05),transparent_70%)] pointer-events-none" />
          
          <div className="max-w-7xl mx-auto relative z-10">
            <div className="text-center mb-20">
              <h2 className="text-4xl md:text-[3.5rem] font-black mb-6 tracking-tight text-slate-900">The Live Pipeline</h2>
              <p className="text-xl md:text-2xl text-slate-600 font-medium">From messy receipts to instant decisions, fully automated.</p>
            </div>

            <div className="relative">
              {/* Connecting Horizontal Line (Desktop) */}
              <div className="hidden lg:block absolute top-[56px] left-[12%] right-[12%] h-1.5 bg-slate-200 rounded-full" />
              <div className="hidden lg:block absolute top-[56px] left-[12%] w-[76%] h-1.5 bg-green-400 rounded-full animate-pulse" />

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
                {[
                  { title: 'Customer Submit', desc: 'Secure upload of evidence and defect details via the mobile-friendly portal.', icon: ShieldCheck },
                  { title: 'Computer Vision', desc: 'Local ML models extract serial numbers and purchase dates from messy receipts.', icon: Zap },
                  { title: 'pHash Verification', desc: 'Cross-checking image perceptual hashes against databases to block recycled photos.', icon: Shield },
                  { title: 'LLM Triage', desc: 'The reasoning engine applies your policy rules to output a highly confident final decision.', icon: CheckCircle }
                ].map((step, idx) => (
                  <div key={idx} className="relative flex flex-col items-center text-center group">
                    
                    {/* Floating Icon/Node */}
                    <div className="relative mb-8 z-10">
                      <div className="w-28 h-28 rounded-full bg-white shadow-xl shadow-slate-200/50 flex items-center justify-center group-hover:-translate-y-2 group-hover:shadow-2xl group-hover:shadow-green-500/20 transition-all duration-300 relative z-10">
                        <div className="w-20 h-20 rounded-full bg-green-50 flex items-center justify-center">
                          <step.icon className="text-green-500" size={36} />
                        </div>
                      </div>
                      {/* Step Number Badge */}
                      <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-slate-900 text-white font-black flex items-center justify-center border-[3px] border-white z-20 shadow-sm">
                        {idx + 1}
                      </div>
                    </div>

                    {/* Card Content */}
                    <div className="bg-white p-6 rounded-[2rem] border border-slate-200 shadow-lg shadow-slate-200/50 group-hover:border-green-300 group-hover:shadow-xl transition-all w-full flex-1 flex flex-col">
                      <h4 className="text-xl font-bold mb-3 text-slate-900">{step.title}</h4>
                      <p className="text-slate-600 leading-relaxed font-medium text-sm md:text-base">{step.desc}</p>
                    </div>
                    
                    {/* Mobile/Tablet Connecting Arrow */}
                    {idx < 3 && (
                      <div className="lg:hidden w-1.5 h-12 bg-slate-200 my-4 rounded-full relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-full bg-green-400 opacity-80" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-200 py-12 px-6 bg-white relative z-10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center">
              <ShieldCheck size={16} className="text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-900">WarrantyGuard <span className="text-green-600 font-medium">AI</span></span>
          </div>
          <div className="text-sm text-slate-500 font-semibold">
            &copy; {new Date().getFullYear()} WarrantyGuard AI. All systems operational.
          </div>
          <div className="flex gap-8 text-sm font-semibold text-slate-500">
            <a href="#" className="hover:text-green-600 transition-colors">Documentation</a>
            <a href="#" className="hover:text-green-600 transition-colors">Privacy</a>
            <a href="#" className="hover:text-green-600 transition-colors">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
