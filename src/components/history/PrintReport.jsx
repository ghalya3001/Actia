import React, { useEffect } from 'react';

export default function PrintReport({ audit, onAfterPrint }) {
  useEffect(() => {
    if (audit) {
      setTimeout(() => {
        window.print();
        if (onAfterPrint) onAfterPrint();
      }, 300);
    }
  }, [audit]);

  if (!audit) return null;

  const isPermis = (audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS');
  const isTournee = (audit.form_type === 'tournee_hse' || (audit.reference && audit.reference.includes('FGSI-010')));
  const sheetTitle = isPermis ? 'CIPI ACTIA — Permis de Travail' : (isTournee ? 'CIPI ACTIA — Tournée HSE' : 'CIPI ACTIA — Audit HSE');
  const items = audit.items_data || {};

  return (
    <div className="print-area" style={{ background: '#fff', color: '#000', padding: '20px', fontSize: '10pt', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '3px solid #003d4d', paddingBottom: '12px', marginBottom: '15px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: '800', color: '#003d4d', margin: 0 }}>{sheetTitle}</h1>
          <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#059669' }}>Fiche d'Évaluation & Suivi ({audit.reference})</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.1rem', fontWeight: '800', color: '#003d4d' }}>Fiche N° #ACTIA-{audit.id}</div>
          <div style={{ fontSize: '0.85rem', color: '#475569' }}>Date : <strong>{audit.date_audit}</strong></div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', background: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #cbd5e1', marginBottom: '15px' }}>
        <div><strong>Secteur / Zone :</strong> {audit.secteur}</div>
        <div><strong>Intervenants / Responsables :</strong> {audit.intervenants}</div>
        {!isPermis && <div><strong>Taux de Conformité HSE :</strong> <span style={{ fontSize: '1.1rem', fontWeight: '800', color: '#059669' }}>{audit.taux_conformite} %</span></div>}
      </div>

      {isPermis ? (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '15px', border: '1px solid #cbd5e1' }}>
          <thead>
            <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #cbd5e1' }}>
              <th style={{ padding: '8px', textAlign: 'left' }}>Type de Permis / Autorisation</th>
              <th style={{ padding: '8px', textAlign: 'center' }}>Nombre Émis / Validés</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
              <td style={{ padding: '8px' }}><strong>1. Plan de Prévention</strong></td>
              <td style={{ padding: '8px', textAlign: 'center', fontWeight: '800', color: '#1d4ed8' }}>{items.plan_prevention || 0}</td>
            </tr>
            <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
              <td style={{ padding: '8px' }}><strong>2. Permis de Travail en Hauteur</strong></td>
              <td style={{ padding: '8px', textAlign: 'center', fontWeight: '800', color: '#c2410c' }}>{items.permis_hauteur || 0}</td>
            </tr>
            <tr>
              <td style={{ padding: '8px' }}><strong>3. Permis de Feu</strong></td>
              <td style={{ padding: '8px', textAlign: 'center', fontWeight: '800', color: '#b91c1c' }}>{items.permis_feu || 0}</td>
            </tr>
          </tbody>
        </table>
      ) : null}

      {audit.commentaires_generaux && (
        <div style={{ background: '#f1f5f9', padding: '10px', borderRadius: '6px', borderLeft: '4px solid #003d4d', marginBottom: '15px' }}>
          <strong>Commentaires des intervenants :</strong><br/>{audit.commentaires_generaux}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '40px', paddingTop: '15px', borderTop: '1px dashed #cbd5e1', fontSize: '9pt' }}>
        <div>Signature Auditeur / Intervenant :<br/><br/><br/>____________________</div>
        <div>Signature Responsable HSE :<br/><br/><br/>____________________</div>
      </div>
    </div>
  );
}
