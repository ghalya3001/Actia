import React from 'react';
import { User, ChevronDown } from 'lucide-react';

export default function Topbar({ currentPage, user, onProfileClick }) {
  const titles = {
    home: <>Page d'<span>Accueil</span></>,
    formulaire: <>Formulaires <span style={{ color: 'var(--color-primary)' }}>HSE</span></>,
    historique: <>Historique des <span style={{ color: 'var(--color-primary)' }}>Audits & Formulaires</span></>,
    dashboard: <>Dashboard <span style={{ color: 'var(--color-primary)' }}>HSE</span></>,
    profile: <>Mon <span style={{ color: 'var(--color-primary)' }}>Profil</span></>
  };

  const initial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'R';

  return (
    <header className="topbar">
      <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="pulse-dot" title="Serveur Intranet Actif"></div>
        <div>{titles[currentPage] || currentPage}</div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={onProfileClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            background: 'rgba(0,24,32,0.8)',
            border: '1px solid var(--card-border)',
            padding: '6px 14px',
            borderRadius: '20px',
            color: '#fff',
            cursor: 'pointer'
          }}
        >
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-primary)', color: '#00141a', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {initial}
          </div>
          <span style={{ fontSize: '0.88rem', fontWeight: '700' }}>{user?.full_name || 'Responsable HSE'}</span>
          <ChevronDown size={14} style={{ color: 'var(--text-dim)' }} />
        </button>
      </div>
    </header>
  );
}
