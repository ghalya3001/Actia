import React from 'react';
import { Home, FileEdit, Clock, LineChart, User, LogOut } from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage, onLogout }) {
  const navItems = [
    { id: 'home', label: "Page d'Accueil", icon: Home },
    { id: 'formulaire', label: 'Formulaires HSE', icon: FileEdit },
    { id: 'historique', label: 'Historique Audits', icon: Clock },
    { id: 'dashboard', label: 'Dashboard HSE', icon: LineChart },
    { id: 'profile', label: 'Mon Profil', icon: User },
  ];

  return (
    <aside class="sidebar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(0,201,150,0.2)' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--color-primary)', color: '#00141a', fontWeight: '800', fontSize: '1.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>P</div>
        <div>
          <div style={{ fontSize: '1.05rem', fontWeight: '800', color: '#ffffff' }}>PlatformActia</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-primary)', fontWeight: '700' }}>Responsable Portal</div>
        </div>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
        <div style={{ fontSize: '0.72rem', fontWeight: '800', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>Navigation</div>
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '11px 14px',
                borderRadius: '8px',
                fontSize: '0.88rem',
                fontWeight: '700',
                cursor: 'pointer',
                border: 'none',
                background: isActive ? 'rgba(0,201,150,0.15)' : 'transparent',
                color: isActive ? 'var(--color-primary)' : 'var(--text-muted)',
                borderLeft: isActive ? '3px solid var(--color-primary)' : '3px solid transparent',
                transition: 'all 0.2s ease',
                textAlign: 'left'
              }}
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(0,201,150,0.2)' }}>
        <button
          onClick={onLogout}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '11px 14px',
            borderRadius: '8px',
            fontSize: '0.88rem',
            fontWeight: '700',
            cursor: 'pointer',
            border: 'none',
            background: 'rgba(244,63,94,0.1)',
            color: '#f43f5e',
            width: '100%',
            transition: 'all 0.2s ease'
          }}
        >
          <LogOut size={18} />
          Se Déconnecter
        </button>
      </div>
    </aside>
  );
}
