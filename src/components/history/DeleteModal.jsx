import React from 'react';
import { AlertTriangle, Trash2 } from 'lucide-react';

export default function DeleteModal({ audit, onClose, onConfirm }) {
  if (!audit) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxWidth: '440px' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(244,63,94,0.15)', border: '1px solid #f43f5e', color: '#f43f5e', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
          <AlertTriangle size={24} />
        </div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fff' }}>Suppression Fiche #ACTIA-{audit.id}</h3>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: '10px 0', lineHeight: '1.6' }}>
          Êtes-vous sûr de vouloir supprimer définitivement la fiche <strong style={{ color: '#fff' }}>#ACTIA-{audit.id}</strong> ?<br/>
          <span style={{ color: '#f43f5e', fontSize: '0.8rem', display: 'inline-block', marginTop: '6px' }}>⚠️ Cette action est irréversible.</span>
        </p>
        <div style={{ display: 'flex', gap: '12px', marginTop: '1.5rem' }}>
          <button className="btn btn-secondary" style={{ flex: 1 }} onClick={onClose}>Annuler</button>
          <button className="btn" style={{ flex: 1, background: '#f43f5e', color: '#fff' }} onClick={onConfirm}><Trash2 size={16}/> Supprimer</button>
        </div>
      </div>
    </div>
  );
}
