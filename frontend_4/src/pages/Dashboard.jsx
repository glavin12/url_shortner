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
import './Dashboard.css';

const API_BASE = 'http://localhost:8000';

export default function Dashboard() {
  const { user } = useAuth();
  const toast = useToast();

  const [urls, setUrls] = useState({});
  const [loading, setLoading] = useState(true);
  const [shortenInput, setShortenInput] = useState('');
  const [shortening, setShortening] = useState(false);

  // Analytics modal
  const [analyticsModal, setAnalyticsModal] = useState(null);
  const [analyticsData, setAnalyticsData] = useState([]);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  // Confirm modal
  const [confirmModal, setConfirmModal] = useState(null);

  const fetchUrls = useCallback(async () => {
    if (!user) return;
    try {
      const data = await apiGetAllUrls(user.email);
      setUrls(data);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }, [user, toast]);

  useEffect(() => {
    fetchUrls();
  }, [fetchUrls]);

  if (!user) return <Navigate to="/login" replace />;

  /* --- Shorten URL --- */
  const handleShorten = async (e) => {
    e.preventDefault();
    if (!shortenInput.trim()) return;

    setShortening(true);
    try {
      await apiShortenUrl(shortenInput.trim());
      setShortenInput('');
      toast.success('URL shortened successfully!');
      await fetchUrls();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setShortening(false);
    }
  };

  /* --- Delete URL --- */
  const handleDelete = async (shortUrl) => {
    setConfirmModal({
      message: `Delete the short link /${shortUrl}? This cannot be undone.`,
      onConfirm: async () => {
        setConfirmModal(null);
        try {
          await apiDeleteUrl(shortUrl);
          toast.success('URL deleted');
          await fetchUrls();
        } catch (err) {
          toast.error(err.message);
        }
      },
    });
  };

  /* --- Delete All URLs --- */
  const handleDeleteAll = () => {
    setConfirmModal({
      message:
        'Delete ALL your shortened URLs? This is permanent and cannot be undone.',
      onConfirm: async () => {
        setConfirmModal(null);
        try {
          await apiDeleteAllUrls(user.email);
          toast.success('All URLs deleted');
          setUrls({});
        } catch (err) {
          toast.error(err.message);
        }
      },
    });
  };

  /* --- Analytics --- */
  const openAnalytics = async (shortUrl) => {
    setAnalyticsModal(shortUrl);
    setAnalyticsLoading(true);
    setAnalyticsData([]);
    try {
      const data = await apiGetAnalytics(shortUrl);
      setAnalyticsData(data);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  /* --- Copy link --- */
  const copyLink = (shortUrl) => {
    navigator.clipboard.writeText(`${API_BASE}/${shortUrl}`);
    toast.info('Link copied to clipboard!');
  };

  /* --- Compute stats --- */
  const urlEntries = Object.entries(urls);
  const totalUrls = urlEntries.length;
  const totalClicks = urlEntries.reduce(
    (sum, [, v]) => sum + (v.clicks || 0),
    0
  );
  const avgClicks = totalUrls > 0 ? Math.round(totalClicks / totalUrls) : 0;

  return (
    <div className="dashboard">
      <div className="dashboard-inner">
        {/* Header */}
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Manage and track all your shortened URLs</p>
        </div>

        {/* Stats */}
        <div className="stats-row">
          <div className="stat-card glass-card">
            <div className="stat-label">Total Links</div>
            <div className="stat-value">{totalUrls}</div>
          </div>
          <div className="stat-card glass-card">
            <div className="stat-label">Total Clicks</div>
            <div className="stat-value">{totalClicks}</div>
          </div>
          <div className="stat-card glass-card">
            <div className="stat-label">Avg. Clicks</div>
            <div className="stat-value">{avgClicks}</div>
          </div>
        </div>

        {/* Shorten Form */}
        <div className="shorten-form glass-card">
          <h2>Shorten a URL</h2>
          <form className="shorten-input-row" onSubmit={handleShorten}>
            <input
              className="input"
              type="url"
              placeholder="https://example.com/your-long-url"
              value={shortenInput}
              onChange={(e) => setShortenInput(e.target.value)}
              required
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={shortening}
            >
              {shortening ? <span className="spinner"></span> : 'Shorten'}
            </button>
          </form>
        </div>

        {/* URL List */}
        <div className="url-section">
          <div className="url-section-header">
            <h2>Your Links</h2>
            {totalUrls > 0 && (
              <button
                className="btn btn-danger btn-sm"
                onClick={handleDeleteAll}
              >
                Delete All
              </button>
            )}
          </div>

          {loading ? (
            <div className="url-list">
              {[1, 2, 3].map((i) => (
                <div key={i} className="skeleton skeleton-card" />
              ))}
            </div>
          ) : totalUrls === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔗</div>
              <h3>No links yet</h3>
              <p>Paste a URL above to create your first short link</p>
            </div>
          ) : (
            <div className="url-list">
              {urlEntries
                .sort(([, a], [, b]) => new Date(b.created_at) - new Date(a.created_at))
                .map(([id, data]) => (
                  <div key={id} className="url-card glass-card">
                    <div className="url-card-info">
                      <div
                        className="url-card-short"
                        onClick={() => copyLink(data.short_url)}
                        title="Click to copy"
                      >
                        {API_BASE}/{data.short_url}
                        <span className="copy-icon">📋</span>
                      </div>
                      <div className="url-card-original" title={data.url}>
                        {data.url}
                      </div>
                      <div className="url-card-meta">
                        <span className="clicks">
                          ▲ {data.clicks} click{data.clicks !== 1 ? 's' : ''}
                        </span>
                        <span>
                          {new Date(data.created_at).toLocaleDateString(
                            'en-US',
                            {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            }
                          )}
                        </span>
                      </div>
                    </div>
                    <div className="url-card-actions">
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => openAnalytics(data.short_url)}
                      >
                        Analytics
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(data.short_url)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Analytics Modal */}
      {analyticsModal && (
        <div
          className="modal-overlay"
          onClick={() => setAnalyticsModal(null)}
        >
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Click Analytics — /{analyticsModal}</h2>
              <button
                className="modal-close"
                onClick={() => setAnalyticsModal(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              {analyticsLoading ? (
                <div className="analytics-empty">
                  <div className="spinner" style={{ width: 28, height: 28 }}></div>
                </div>
              ) : analyticsData.length === 0 ? (
                <div className="analytics-empty">
                  <div className="empty-icon">📭</div>
                  <p>No clicks recorded yet</p>
                </div>
              ) : (
                <div className="analytics-list">
                  {analyticsData.map((click, i) => (
                    <div key={click.id || i} className="analytics-item">
                      <span className="click-number">#{i + 1}</span>
                      <span className="click-time">
                        {new Date(click.clicked_at).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                        })}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Confirm Modal */}
      {confirmModal && (
        <div
          className="modal-overlay"
          onClick={() => setConfirmModal(null)}
        >
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Confirm Action</h2>
              <button
                className="modal-close"
                onClick={() => setConfirmModal(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p className="confirm-message">{confirmModal.message}</p>
              <div className="confirm-actions">
                <button
                  className="btn btn-ghost"
                  onClick={() => setConfirmModal(null)}
                >
                  Cancel
                </button>
                <button
                  className="btn btn-danger"
                  onClick={confirmModal.onConfirm}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
