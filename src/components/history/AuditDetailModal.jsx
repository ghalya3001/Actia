import React from 'react';
import { X, Printer } from 'lucide-react';

export default function AuditDetailModal({ audit, onClose, onPrint }) {
  if (!audit) return null;

  const isPermis = (audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS');
  const isTournee = (audit.form_type === 'tournee_hse' || (audit.reference && audit.reference.includes('FGSI-010')));
  const refTitle = isPermis ? 'Permis de Travail (FGSI-PERMIS)' : (isTournee ? 'Tournée HSE (FGSI-010-Ind:A)' : 'Audit HSE (FGSI-001-Ind:F)');

  const items = audit.items_data || {};

  return (
    <div className="modal-overlay">
      <div className="modal-card-large">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(0,201,150,0.2)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#fff' }}>Détail Fiche #ACTIA-{audit.id}</h2>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-primary)' }}>
              CIPI ACTIA · {refTitle} | Secteur : {audit.secteur} | Date : {audit.date_audit}
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={24} /></button>
        </div>

        {isPermis ? (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '16px', borderRadius: '10px', textAlign: 'center', borderTop: '3px solid #3b82f6' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Plan de Prévention</div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#60a5fa', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>{items.plan_prevention || 0}</div>
              </div>
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '16px', borderRadius: '10px', textAlign: 'center', borderTop: '3px solid #ea580c' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Permis Travail Hauteur</div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#fb923c', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>{items.permis_hauteur || 0}</div>
              </div>
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '16px', borderRadius: '10px', textAlign: 'center', borderTop: '3px solid #dc2626' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Permis de Feu</div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#f87171', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>{items.permis_feu || 0}</div>
              </div>
            </div>

            {items.remarques ? (
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '12px 16px', borderRadius: '10px', borderLeft: '4px solid #3b82f6', marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: '700', color: '#60a5fa', textTransform: 'uppercase', marginBottom: '4px' }}>Remarques spécifiques Permis :</div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: '1.5' }}>{items.remarques}</div>
              </div>
            ) : null}
          </div>
        ) : (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '12px', borderRadius: '10px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Taux de Conformité</div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: 'var(--color-primary)', fontFamily: 'var(--font-mono)' }}>{audit.taux_conformite} %</div>
              </div>
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '12px', borderRadius: '10px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Évaluations</div>
                <div style={{ fontSize: '1rem', fontWeight: '700', color: '#fff', marginTop: '6px' }}>{audit.total_conforme} ✓ / {audit.total_non_conforme} ✗ / {audit.total_na} N/A</div>
              </div>
              <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '12px', borderRadius: '10px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Actions Correctives</div>
                <div style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--color-accent-light)', marginTop: '6px' }}>{audit.count_soldee} Soldée · {audit.count_en_cours} En cours</div>
              </div>
            </div>
          </div>
        )}

        {audit.commentaires_generaux && (
          <div style={{ background: 'rgba(0,24,32,0.8)', border: '1px solid var(--card-border)', padding: '12px 16px', borderRadius: '10px', borderLeft: '4px solid var(--color-primary)', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--color-primary)', textTransform: 'uppercase', marginBottom: '4px' }}>Commentaires généraux :</div>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: '1.5' }}>{audit.commentaires_generaux}</div>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', borderTop: '1px solid rgba(0,201,150,0.2)', paddingTop: '1rem' }}>
          <button className="btn btn-secondary" onClick={() => onPrint(audit)}><Printer size={16}/> Imprimer la Fiche</button>
          <button className="btn btn-primary" onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}
