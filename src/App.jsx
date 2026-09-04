import React, { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar.jsx';
import Topbar from './components/layout/Topbar.jsx';
import AuthScreen from './components/auth/AuthScreen.jsx';
import FormSelector from './components/forms/FormSelector.jsx';
import AuditWizard from './components/forms/AuditWizard.jsx';
import HistoryTable from './components/history/HistoryTable.jsx';
import AuditDetailModal from './components/history/AuditDetailModal.jsx';
import DeleteModal from './components/history/DeleteModal.jsx';
import PrintReport from './components/history/PrintReport.jsx';
import HseDashboard from './components/dashboard/HseDashboard.jsx';
import UserProfile from './components/profile/UserProfile.jsx';
import { ShieldCheck, ArrowRight, Award, FileEdit, Clock, LineChart } from 'lucide-react';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('access_token') || null);
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');

  const [wizardMode, setWizardMode] = useState(false);
  const [selectedFormType, setSelectedFormType] = useState('audit_hse');
  const [editingAudit, setEditingAudit] = useState(null);

  const [auditsList, setAuditsList] = useState([]);
  const [viewingAudit, setViewingAudit] = useState(null);
  const [deletingAudit, setDeletingAudit] = useState(null);
  const [printingAudit, setPrintingAudit] = useState(null);

  const [toasts, setToasts] = useState([]);

  const API_BASE = window.location.origin + "/api/v1/auth";
  const API_AUDITS = window.location.origin + "/api/v1/audits";

  const showToast = (msg, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, msg, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const loadUserProfile = async (authToken) => {
    try {
      const res = await fetch(`${API_BASE}/me`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      const data = await res.json();
      if (res.ok) {
        setUser(data);
      } else if (res.status === 401) {
        handleLogout();
      }
    } catch (err) {}
  };

  const fetchAuditsHistory = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_AUDITS}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        setAuditsList(data);
      }
    } catch (err) {}
  };

  useEffect(() => {
    if (token) {
      loadUserProfile(token);
    }
  }, [token]);

  useEffect(() => {
    if (token && (currentPage === 'historique' || currentPage === 'home')) {
      fetchAuditsHistory();
    }
  }, [token, currentPage]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setUser(null);
    showToast("Déconnexion réussie.");
  };

  const handleOpenWizard = (formType, auditToEdit = null) => {
    setSelectedFormType(auditToEdit ? (auditToEdit.form_type || 'audit_hse') : formType);
    setEditingAudit(auditToEdit);
    setWizardMode(true);
  };

  const handleExecuteDelete = async () => {
    if (!deletingAudit) return;
    try {
      const res = await fetch(`${API_AUDITS}/${deletingAudit.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        showToast(`Fiche #ACTIA-${deletingAudit.id} supprimée.`);
        setDeletingAudit(null);
        fetchAuditsHistory();
      }
    } catch (err) {
      showToast("Erreur lors de la suppression", 'error');
    }
  };

  if (!token) {
    return (
      <>
        <AuthScreen onLoginSuccess={t => { setToken(t); loadUserProfile(t); }} showToast={showToast} />
        <div className="toast-container">
          {toasts.map(t => (
            <div key={t.id} className={`toast ${t.type === 'error' ? 'error' : ''}`}>{t.msg}</div>
          ))}
        </div>
      </>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar currentPage={currentPage} setCurrentPage={p => { setWizardMode(false); setCurrentPage(p); }} onLogout={handleLogout} />
      <Topbar currentPage={currentPage} user={user} onProfileClick={() => { setWizardMode(false); setCurrentPage('profile'); }} />

      <main className="main-content">
        
        {/* PAGE HOME */}
        {currentPage === 'home' && (
          <div className="page-anim">
            <div style={{ marginBottom: '2rem' }}>
              <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#fff' }}>Bienvenue sur <span style={{ color: 'var(--color-primary)' }}>PlatformActia HSE</span></h1>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Hygiène · Sécurité · Environnement — Portail Responsable</p>
            </div>

            <div className="glass-card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, rgba(0,61,77,0.8) 0%, rgba(0,28,36,0.9) 100%)' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fff', marginBottom: '8px' }}>
                La Sécurité n'est pas une option — <span style={{ color: 'var(--color-accent-light)' }}>c'est une culture au quotidien.</span>
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                Construisez un environnement d'excellence où chaque collaborateur travaille en toute sécurité.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
              <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'pointer' }} onClick={() => setCurrentPage('formulaire')}>
                <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(0,201,150,0.15)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><FileEdit size={26}/></div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff' }}>Nouveau Formulaire</h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Audit, Tournée & Permis</p>
                </div>
              </div>

              <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'pointer' }} onClick={() => setCurrentPage('historique')}>
                <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(168,224,99,0.15)', color: 'var(--color-accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Clock size={26}/></div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff' }}>Historique Audits</h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Consulter les fiches</p>
                </div>
              </div>

              <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'pointer' }} onClick={() => setCurrentPage('dashboard')}>
                <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(59,130,246,0.15)', color: '#60a5fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><LineChart size={26}/></div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff' }}>Dashboard HSE</h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Graphiques & KPIs</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PAGE FORMULAIRE */}
        {currentPage === 'formulaire' && (
          <div className="page-anim">
            {!wizardMode ? (
              <FormSelector onSelectForm={type => handleOpenWizard(type)} />
            ) : (
              <AuditWizard
                formType={selectedFormType}
                editingAudit={editingAudit}
                onClose={() => setWizardMode(false)}
                onSubmitSuccess={() => { setWizardMode(false); setCurrentPage('historique'); fetchAuditsHistory(); }}
                showToast={showToast}
              />
            )}
          </div>
        )}

        {/* PAGE HISTORIQUE */}
        {currentPage === 'historique' && (
          <div className="page-anim">
            <HistoryTable
              audits={auditsList}
              onRefresh={fetchAuditsHistory}
              onView={audit => setViewingAudit(audit)}
              onEdit={audit => { setCurrentPage('formulaire'); handleOpenWizard(audit.form_type, audit); }}
              onDelete={audit => setDeletingAudit(audit)}
              onPrint={audit => setPrintingAudit(audit)}
            />
          </div>
        )}

        {/* PAGE DASHBOARD */}
        {currentPage === 'dashboard' && <div className="page-anim"><HseDashboard /></div>}

        {/* PAGE PROFILE */}
        {currentPage === 'profile' && <div className="page-anim"><UserProfile user={user} showToast={showToast} /></div>}

      </main>

      {/* MODALS */}
      {viewingAudit && <AuditDetailModal audit={viewingAudit} onClose={() => setViewingAudit(null)} onPrint={audit => { setViewingAudit(null); setPrintingAudit(audit); }} />}
      {deletingAudit && <DeleteModal audit={deletingAudit} onClose={() => setDeletingAudit(null)} onConfirm={handleExecuteDelete} />}
      {printingAudit && <PrintReport audit={printingAudit} onAfterPrint={() => setPrintingAudit(null)} />}

      {/* TOAST CONTAINER */}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type === 'error' ? 'error' : ''}`}>{t.msg}</div>
        ))}
      </div>
    </div>
  );
}
