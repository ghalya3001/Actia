import Home from './components/home/Home.jsx';
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
        {currentPage === 'home' && <Home onNavigate={setCurrentPage} />}

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
