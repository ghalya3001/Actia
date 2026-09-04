import React from 'react';
import { ClipboardCheck, ClipboardList, Shield, PenSquare } from 'lucide-react';

export default function FormSelector({ onSelectForm }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
      
      {/* CARD 1: AUDIT HSE (FGSI-001) */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'rgba(0,201,150,0.15)', border: '1px solid var(--color-primary)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
            <ClipboardCheck size={28} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#fff', marginBottom: '8px' }}>Audit HSE — Grille d'évaluation terrain</h3>
          <p style={{ fontSize: '0.87rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '1.25rem' }}>
            Grille d'évaluation complète (EPI, Connaissances opérateurs, 5S, Sécurité machines, Incendie, Premier secours, Ergonomie).
          </p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: '700', padding: '4px 10px', borderRadius: '20px', background: 'rgba(255,255,255,0.06)', color: 'var(--color-accent-light)', border: '1px solid rgba(168,224,99,0.3)' }}>Ref: FGSI-001 - Ind: F</span>
            <span style={{ fontSize: '0.72rem', fontWeight: '700', padding: '4px 10px', borderRadius: '20px', background: 'rgba(255,255,255,0.06)', color: 'var(--color-accent-light)', border: '1px solid rgba(168,224,99,0.3)' }}>51 Points de contrôle</span>
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => onSelectForm('audit_hse')}>
          <PenSquare size={16} /> Remplir l'Audit HSE (FGSI-001)
        </button>
      </div>

      {/* CARD 2: TOURNÉE HSE (FGSI-010-Ind:A) */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'rgba(168,224,99,0.15)', border: '1px solid var(--color-accent-light)', color: 'var(--color-accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
            <ClipboardList size={28} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#fff', marginBottom: '8px' }}>Tournée HSE — Grille de contrôle terrain</h3>
          <p style={{ fontSize: '0.87rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '1.25rem' }}>
            Grille complète de Tournée HSE (Sécurité Générale, Produits Chimiques, Zone ATEX, Maintenance, Évacuation, Déchets).
          </p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: '700', padding: '4px 10px', borderRadius: '20px', background: 'rgba(255,255,255,0.06)', color: 'var(--color-accent-light)', border: '1px solid rgba(168,224,99,0.3)' }}>Ref: FGSI-010-Ind:A</span>
            <span style={{ fontSize: '0.72rem', fontWeight: '700', padding: '4px 10px', borderRadius: '20px', background: 'rgba(255,255,255,0.06)', color: 'var(--color-accent-light)', border: '1px solid rgba(168,224,99,0.3)' }}>42 Points de contrôle</span>
          </div>
        </div>
        <button className="btn" onClick={() => onSelectForm('tournee_hse')} style={{ background: 'rgba(168,224,99,0.15)', borderColor: 'var(--color-accent-light)', color: 'var(--color-accent-light)' }}>
          <PenSquare size={16} /> Remplir la Tournée HSE (FGSI-010)
        </button>
      </div>

      {/* CARD 3: PERMIS DE TRAVAIL (FGSI-PERMIS) */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'rgba(59,130,246,0.15)', border: '1px solid #3b82f6', color: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
            <Shield size={28} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#fff', marginBottom: '8px' }}>Permis de Travail — Fiche d'autorisation</h3>
          <p style={{ fontSize: '0.87rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '1.25rem' }}>
            Fiche de suivi et validation des permis de travail (Plan de prévention, Permis de travail en hauteur, Permis de feu).
          </p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: '700', padding: '4px 10px', borderRadius: '20px', background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.3)' }}>Ref: FGSI-PERMIS</span>
            <span style={{ fontSize: '0.72rem', fontWeight: '700', padding: '4px 10px', borderRadius: '20px', background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.3)' }}>3 Champs Numériques</span>
          </div>
        </div>
        <button className="btn" onClick={() => onSelectForm('permis_travail')} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', color: '#ffffff', boxShadow: '0 4px 15px rgba(59,130,246,0.35)' }}>
          <PenSquare size={16} /> Remplir le Permis de Travail (FGSI-PERMIS)
        </button>
      </div>

    </div>
  );
}
