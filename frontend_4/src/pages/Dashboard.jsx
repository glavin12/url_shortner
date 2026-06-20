import { useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import {
  apiShortenUrl,
  apiGetAllUrls,
  apiDeleteUrl,
  apiDeleteAllUrls,
  apiGetAnalytics,
} from '../api';

const API_BASE = import.meta.env.VITE_API_URL || 'https://pretty-laughter-production.up.railway.app';

const parseUTC = (dateStr) => {
  if (!dateStr) return new Date();
  const normalized = dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : `${dateStr}Z`;
  return new Date(normalized);
};

export default function Dashboard() {
  const { user } = useAuth();
  const toast = useToast();

  const [urls, setUrls] = useState({});
  const [loading, setLoading] = useState(true);
  const [shortenInput, setShortenInput] = useState('');
  const [aliasInput, setAliasInput] = useState('');
  const [shortening, setShortening] = useState(false);
  const [lastShortened, setLastShortened] = useState(null);
  const [qrModal, setQrModal] = useState(null);
  const [analyticsModal, setAnalyticsModal] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);

  const [urlsPage, setUrlsPage] = useState(1);
  const [hasMoreUrls, setHasMoreUrls] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const urlsPageSize = 10;

  const fetchUrls = useCallback(async (page = 1, search = '') => {
    if (!user) return;
    try {
      setLoading(true);
      const data = await apiGetAllUrls(user.email, page, urlsPageSize, search);
      setUrls(data || {});
      setUrlsPage(page);
      setHasMoreUrls(Object.keys(data || {}).length === urlsPageSize);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }, [user, toast]);

  useEffect(() => {
    fetchUrls(1, searchInput);
  }, [fetchUrls]);

  if (!user) return <Navigate to="/login" replace />;

  const handleShorten = async (e) => {
    e.preventDefault();
    if (!shortenInput.trim()) return;

    setShortening(true);
    try {
      const res = await apiShortenUrl(shortenInput, aliasInput.trim() || null);
      if (res && res.short_url) {
        setLastShortened(res.short_url);
        setShortenInput('');
        setAliasInput('');
        toast.success('URL shortened successfully!');
        await fetchUrls(1);
      }
    } catch (err) {
      toast.error(err.message);
    } finally {
      setShortening(false);
    }
  };

  const copyLink = (shortUrl) => {
    navigator.clipboard.writeText(`${API_BASE}/${shortUrl}`);
    toast.info('Link copied to clipboard!');
  };

  const downloadQr = async (shortUrl) => {
    try {
      toast.info('Downloading QR code...');
      const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=${encodeURIComponent(`${API_BASE}/${shortUrl}`)}`;
      const response = await fetch(qrUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sniplink-qr-${shortUrl}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      toast.error('Failed to download QR code');
    }
  };

  const openAnalytics = async (shortUrl) => {
    setAnalyticsModal(shortUrl);
    setAnalyticsData(null);
    try {
      const res = await apiGetAnalytics(shortUrl, 1, 50);
      setAnalyticsData(res);
    } catch (err) {
      toast.error('Failed to load detailed analytics');
    }
  };

  const urlEntries = Object.entries(urls || {}).sort(([, a], [, b]) => parseUTC(b.created_at) - parseUTC(a.created_at));
  const totalUrls = urlEntries.length;
  const totalClicks = urlEntries.reduce((sum, [, v]) => sum + (v.clicks || 0), 0);

  return (
    <div className="min-h-[calc(100vh-80px)] bg-charcoal text-cream pb-20">
      <div className="max-w-5xl mx-auto px-6 pt-16">
        
        {/* Hero */}
        <div className="text-center mb-12 animate-fadeInDown">
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 text-cream">
            Shorten Your Links,<br/>
            <span className="text-coral">Amplify Your Reach</span>
          </h1>
          <p className="text-cream/60 max-w-2xl mx-auto text-lg font-light leading-relaxed">
            Powerful analytics and simple link management for marketers and developers.
            Engineered for speed and high-contrast utility.
          </p>
        </div>

        {/* Shorten Form */}
        <form onSubmit={handleShorten} className="max-w-2xl mx-auto mb-6 relative z-10 animate-fadeInUp">
          <div className="flex flex-col md:flex-row items-center bg-[#252525] border border-white/10 rounded-[16px] p-[6px] gap-2 transition-all focus-within:border-coral/50 shadow-2xl">
            <input
              type="url"
              className="w-full md:flex-1 bg-transparent border-none outline-none text-cream px-5 py-3 placeholder:text-cream/40"
              placeholder="Paste your long URL here..."
              value={shortenInput}
              onChange={(e) => setShortenInput(e.target.value)}
              required
            />
            <div className="w-full md:w-auto flex items-center bg-black/20 rounded-[10px] px-3 py-1">
              <span className="text-cream/40 text-sm">snip.link/</span>
              <input
                type="text"
                className="w-full md:w-28 bg-transparent border-none outline-none text-cream px-2 py-2 text-sm placeholder:text-cream/30"
                placeholder="custom-alias"
                value={aliasInput}
                onChange={(e) => setAliasInput(e.target.value)}
                pattern="[a-zA-Z0-9_-]+"
                title="Letters, numbers, hyphens, underscores only"
              />
            </div>
            <button 
              type="submit" 
              disabled={shortening}
              className="w-full md:w-auto bg-coral text-[#1a1a1a] font-bold px-6 py-3 rounded-[12px] flex items-center justify-center gap-2 hover:bg-coral/90 transition-colors disabled:opacity-70"
            >
              {shortening ? '...' : 'Shorten →'}
            </button>
          </div>
        </form>

        {/* Result Card */}
        {lastShortened && (
          <div className="max-w-2xl mx-auto mb-16 bg-[#222222] border border-white/5 rounded-[16px] p-4 flex items-center justify-between animate-fadeIn">
            <div className="flex items-center gap-4 overflow-hidden">
              <div className="bg-[#1A1A1A] p-3 rounded-full text-mustard flex-shrink-0 border border-white/5">
                🔗
              </div>
              <div className="truncate">
                <p className="text-cream/50 text-sm truncate max-w-[200px] sm:max-w-xs">{shortenInput || "Your long URL"}</p>
                <a href={`${API_BASE}/${lastShortened}`} target="_blank" rel="noreferrer" className="text-coral font-semibold hover:underline">
                  snip.link/{lastShortened}
                </a>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <button 
                type="button"
                onClick={() => setQrModal(lastShortened)}
                className="p-2 text-mustard hover:text-mustard/80 transition-colors"
                title="View QR Code"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
              </button>
              <button 
                onClick={() => copyLink(lastShortened)}
                className="bg-coral text-[#1A1A1A] px-4 py-2 rounded-lg font-bold text-sm flex items-center gap-2 hover:bg-coral/90 transition-colors"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Copy
              </button>
            </div>
          </div>
        )}

        {/* Dashboard grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-20">
          {/* Stats Column */}
          <div className="space-y-6">
            <div className="bg-[#222222] border border-white/5 rounded-[20px] p-6 shadow-xl relative overflow-hidden">
              <div className="text-cream/40 text-[11px] font-bold tracking-widest mb-4 flex justify-between items-center">
                TOTAL CLICKS <span className="text-coral">↗</span>
              </div>
              <div className="text-5xl font-extrabold text-cream mb-6 tracking-tight">{totalClicks.toLocaleString()}</div>
              <div className="absolute bottom-0 left-0 right-0 h-20 flex items-end gap-1 opacity-80 px-4">
                <svg viewBox="0 0 100 30" preserveAspectRatio="none" className="w-full h-full stroke-coral stroke-2 fill-transparent">
                  <path d="M0,25 L10,20 L20,24 L30,15 L40,18 L50,10 L60,14 L70,8 L80,12 L90,5 L100,10" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
            
            <div className="bg-[#222222] border border-white/5 rounded-[20px] p-6 shadow-xl relative overflow-hidden">
              <div className="text-cream/40 text-[11px] font-bold tracking-widest mb-4 flex justify-between items-center">
                TOTAL LINKS <span className="text-mustard">👥</span>
              </div>
              <div className="text-5xl font-extrabold text-cream mb-6 tracking-tight">{totalUrls.toLocaleString()}</div>
              <div className="absolute bottom-0 left-0 right-0 h-20 flex items-end gap-1 opacity-80 px-4">
                <svg viewBox="0 0 100 30" preserveAspectRatio="none" className="w-full h-full stroke-mustard stroke-2 fill-transparent">
                  <path d="M0,28 L10,25 L20,26 L30,18 L40,22 L50,14 L60,16 L70,10 L80,14 L90,6 L100,8" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
          </div>

          {/* History Table */}
          <div className="lg:col-span-2 bg-[#222222] border border-white/5 rounded-[20px] p-8 shadow-xl flex flex-col">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
              <h3 className="text-xl font-bold text-cream tracking-tight">Recent Links</h3>
              <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
                <input 
                  type="text" 
                  placeholder="Search URLs..." 
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchUrls(1, searchInput)}
                  className="bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-sm text-cream outline-none focus:border-coral/50 transition-colors w-full sm:w-auto"
                />
                <button 
                  onClick={() => fetchUrls(1, searchInput)}
                  className="bg-coral/20 text-coral text-sm font-medium px-4 py-2 rounded-lg hover:bg-coral/30 transition-colors flex-1 sm:flex-none"
                >
                  Search
                </button>
                <button 
                  onClick={() => fetchUrls(1, searchInput)}
                  disabled={loading}
                  className="text-mustard/80 text-sm font-medium hover:text-mustard flex items-center justify-center gap-2 transition-colors disabled:opacity-50 flex-1 sm:flex-none"
                  title="Refresh"
                >
                  {loading ? '...' : '↻'}
                </button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-cream/30 text-[10px] font-bold tracking-widest border-b border-white/5">
                    <th className="pb-4 font-medium uppercase">SHORT URL</th>
                    <th className="pb-4 font-medium uppercase">ORIGINAL URL</th>
                    <th className="pb-4 font-medium text-right uppercase">CLICKS</th>
                    <th className="pb-4 font-medium text-right uppercase">DATE</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {urlEntries.map(([id, data]) => (
                    <tr key={id} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors">
                      <td className="py-5 pr-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <span className="text-coral font-medium">snip.link/{data.short_url}</span>
                          <div className="flex items-center gap-1">
                            <button onClick={() => copyLink(data.short_url)} className="text-cream/30 hover:text-cream transition-colors p-1" title="Copy Link">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            </button>
                            <button onClick={() => setQrModal(data.short_url)} className="text-cream/30 hover:text-mustard transition-colors p-1" title="View QR Code">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                            </button>
                            <button onClick={() => openAnalytics(data.short_url)} className="text-cream/30 hover:text-coral transition-colors p-1" title="View Analytics">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20v-6M6 20V10M18 20V4"></path></svg>
                            </button>
                          </div>
                        </div>
                      </td>
                      <td className="py-5 text-cream/50 truncate max-w-[220px] pr-4 font-light" title={data.url}>{data.url}</td>
                      <td className="py-5 text-mustard font-medium text-right pr-4">{data.clicks.toLocaleString()}</td>
                      <td className="py-5 text-cream/40 text-right whitespace-nowrap font-light">
                        {parseUTC(data.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Pagination Controls */}
            {urlEntries.length > 0 && (
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-white/5">
                <button 
                  disabled={urlsPage === 1 || loading} 
                  onClick={() => fetchUrls(urlsPage - 1, searchInput)} 
                  className="text-sm bg-white/5 hover:bg-white/10 text-cream px-4 py-2 rounded-lg transition-colors disabled:opacity-30"
                >
                  ← Previous
                </button>
                <span className="text-sm text-cream/50 font-medium">Page {urlsPage}</span>
                <button 
                  disabled={!hasMoreUrls || loading} 
                  onClick={() => fetchUrls(urlsPage + 1, searchInput)} 
                  className="text-sm bg-white/5 hover:bg-white/10 text-cream px-4 py-2 rounded-lg transition-colors disabled:opacity-30"
                >
                  Next →
                </button>
              </div>
            )}
            {totalUrls === 0 && !loading && (
               <div className="text-center text-cream/30 py-12 font-light">No links created yet.</div>
            )}
            {loading && (
               <div className="text-center text-cream/30 py-12 font-light">Loading links...</div>
            )}
          </div>
        </div>
      </div>

      {/* QR Code Modal */}
      {qrModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="bg-[#222222] border border-white/10 rounded-[20px] p-8 max-w-sm w-full flex flex-col items-center relative shadow-2xl">
            <button 
              onClick={() => setQrModal(null)}
              className="absolute top-4 right-4 text-cream/50 hover:text-cream transition-colors p-2"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
            <h3 className="text-xl font-bold text-cream mb-6">Scan QR Code</h3>
            <div className="bg-white p-4 rounded-xl mb-6 shadow-inner">
              <img 
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(`${API_BASE}/${qrModal}`)}`} 
                alt="QR Code" 
                className="w-48 h-48 object-contain" 
              />
            </div>
            <div className="text-center mt-6">
              <div className="text-cream/50 text-sm mb-1">snip.link/<span className="text-cream font-medium">{qrModal}</span></div>
            </div>
            <div className="flex w-full gap-3">
              <button
                onClick={() => { copyLink(qrModal); setQrModal(null); }}
                className="flex-1 bg-white/5 border border-white/10 text-cream py-3 rounded-xl font-bold hover:bg-white/10 transition-colors flex items-center justify-center gap-2"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Copy
              </button>
              <button
                onClick={() => { downloadQr(qrModal); }}
                className="flex-[2] bg-coral text-[#1A1A1A] py-3 rounded-xl font-bold hover:bg-coral/90 transition-colors flex items-center justify-center gap-2"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Download QR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Modal */}
      {analyticsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="bg-[#222222] border border-white/10 rounded-[20px] p-8 max-w-2xl w-full flex flex-col relative shadow-2xl max-h-[80vh]">
            <button 
              onClick={() => setAnalyticsModal(null)}
              className="absolute top-4 right-4 text-cream/50 hover:text-cream transition-colors p-2"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
            <h3 className="text-xl font-bold text-cream mb-2">Detailed Analytics</h3>
            <p className="text-cream/50 text-sm mb-6">Showing recent clicks for snip.link/{analyticsModal}</p>
            
            <div className="overflow-y-auto flex-1 pr-2">
              {!analyticsData ? (
                <div className="text-center text-cream/30 py-12 font-light">Loading analytics...</div>
              ) : analyticsData.length === 0 ? (
                <div className="text-center text-cream/30 py-12 font-light">No clicks recorded yet.</div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-cream/30 text-[10px] font-bold tracking-widest border-b border-white/5">
                      <th className="pb-4 font-medium uppercase">Date & Time</th>
                      <th className="pb-4 font-medium uppercase">Browser</th>
                      <th className="pb-4 font-medium uppercase">OS</th>
                      <th className="pb-4 font-medium uppercase text-right">Referrer</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {analyticsData.map((click, idx) => (
                      <tr key={idx} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors">
                        <td className="py-4 text-cream/60 font-light whitespace-nowrap">
                          {parseUTC(click.clicked_at).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit' })}
                        </td>
                        <td className="py-4 text-cream/80">{click.browser || 'Unknown'}</td>
                        <td className="py-4 text-cream/80">{click.os || 'Unknown'}</td>
                        <td className="py-4 text-mustard/70 text-right truncate max-w-[150px]">{click.referrer || 'Direct'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
