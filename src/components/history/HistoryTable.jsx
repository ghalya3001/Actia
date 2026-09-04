import React, { useState, useEffect } from 'react';
import { Eye, Pen, Printer, Trash2, Search, Calendar, Layers, FolderOpen, RotateCcw } from 'lucide-react';

export default function HistoryTable({ audits, onRefresh, onView, onEdit, onDelete, onPrint }) {
  const [filterType, setFilterType] = useState('');
  const [filterDate, setFilterDate] = useState('');
  const [filterSecteur, setFilterSecteur] = useState('');

  const handleResetFilters = () => {
    setFilterType('');
    setFilterDate('');
    setFilterSecteur('');
  };

  const filteredAudits = audits.filter(audit => {
    const matchType = !filterType || (filterType === 'audit_hse' ? (audit.form_type === 'audit_hse' || audit.form_type === 'audit_hse_complet') : audit.form_type === filterType);
    const matchDate = !filterDate || audit.date_audit === filterDate;
    const matchSecteur = !filterSecteur || audit.secteur.toLowerCase().includes(filterSecteur.toLowerCase()) || audit.intervenants.toLowerCase().includes(filterSecteur.toLowerCase());
    return matchType && matchDate && matchSecteur;
  });

  return (
    <div>
      {/* FILTER BAR */}
      <div style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '14px', padding: '1.25rem 1.5rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--text-muted)' }}><Layers size={14} style={{ display: 'inline', marginRight: '4px' }}/> Type de Formulaire</label>
          <select className="form-input" value={filterType} onChange={e => setFilterType(e.target.value)}>
            <option value="">Tous les types de formulaires</option>
            <option value="audit_hse">Audit HSE (FGSI-001)</option>
            <option value="tournee_hse">Tournée HSE (FGSI-010-Ind:A)</option>
            <option value="permis_travail">Permis de Travail (FGSI-PERMIS)</option>
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--text-muted)' }}><Calendar size={14} style={{ display: 'inline', marginRight: '4px' }}/> Date Audit</label>
          <input type="date" className="form-input" value={filterDate} onChange={e => setFilterDate(e.target.value)} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, minWidth: '220px' }}>
          <label style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--text-muted)' }}><Search size={14} style={{ display: 'inline', marginRight: '4px' }}/> Recherche Secteur / Intervenant</label>
          <input type="text" className="form-input" placeholder="Filtrer instantanément..." value={filterSecteur} onChange={e => setFilterSecteur(e.target.value)} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center' }}>
          <button
            className="btn btn-secondary"
            onClick={handleResetFilters}
            disabled={!filterType && !filterDate && !filterSecteur}
            style={{
              opacity: (!filterType && !filterDate && !filterSecteur) ? 0.5 : 1,
              cursor: (!filterType && !filterDate && !filterSecteur) ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 16px',
              height: '42px'
            }}
            title="Réinitialiser tous les filtres de recherche"
          >
            <RotateCcw size={14} /> Réinitialiser
          </button>
        </div>
      </div>

      {/* TABLE */}
      <div style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '16px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'rgba(0, 32, 42, 0.9)', color: 'var(--color-primary)', fontSize: '0.8rem', fontWeight: '800', textTransform: 'uppercase' }}>
              <th style={{ padding: '14px 16px' }}>Réf Fiche</th>
              <th style={{ padding: '14px 16px' }}>Date</th>
              <th style={{ padding: '14px 16px' }}>Secteur</th>
              <th style={{ padding: '14px 16px' }}>Intervenants</th>
              <th style={{ padding: '14px 16px' }}>Score / Type</th>
              <th style={{ padding: '14px 16px' }}>Détails Synthèse</th>
              <th style={{ padding: '14px 16px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAudits.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  <FolderOpen size={40} style={{ opacity: 0.5, marginBottom: '10px' }} />
                  <div style={{ fontSize: '1rem', fontWeight: '700', color: '#fff' }}>Aucune fiche trouvée</div>
                  <div style={{ fontSize: '0.85rem', marginTop: '4px' }}>Aucun enregistrement ne correspond aux critères.</div>
                </td>
              </tr>
            ) : (
              filteredAudits.map(audit => {
                const isPermis = (audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS');
                const items = audit.items_data || {};

                const confBadge = isPermis ? (
                  <span className="incident-badge" style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid #3b82f6' }}>FGSI-PERMIS</span>
                ) : (
                  <span className={`incident-badge ${audit.taux_conformite >= 85 ? 'badge-green' : (audit.taux_conformite >= 60 ? 'badge-orange' : 'badge-red')}`}>
                    {audit.taux_conformite} %
                  </span>
                );

                const detailsCol = isPermis ? (
                  <div style={{ fontSize: '0.78rem', color: '#60a5fa' }}>
                    📋 Plan prev: <strong>{items.plan_prevention || 0}</strong> · 🧗 Hauteur: <strong>{items.permis_hauteur || 0}</strong> · 🔥 Feu: <strong>{items.permis_feu || 0}</strong>
                  </div>
                ) : (
                  <div style={{ fontSize: '0.78rem' }}>
                    <span style={{ color: '#10b981' }}>✓ {audit.count_soldee} Soldée</span> · <span style={{ color: '#0284c7' }}>⚡ {audit.count_en_cours} En cours</span> · <span style={{ color: '#ef4444' }}>🔴 {audit.count_en_retard + audit.count_non_engagee} À traiter</span>
                  </div>
                );

                return (
                  <tr key={audit.id} style={{ borderBottom: '1px solid rgba(0,201,150,0.1)' }}>
                    <td style={{ padding: '14px 16px' }}><strong style={{ color: isPermis ? '#60a5fa' : 'var(--color-primary)', fontFamily: 'var(--font-mono)' }}>#ACTIA-{audit.id}</strong><div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{audit.reference}</div></td>
                    <td style={{ padding: '14px 16px' }}><strong>{audit.date_audit}</strong></td>
                    <td style={{ padding: '14px 16px' }}><span style={{ fontWeight: '700', color: '#fff' }}>{audit.secteur}</span></td>
                    <td style={{ padding: '14px 16px' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{audit.intervenants}</span></td>
                    <td style={{ padding: '14px 16px' }}>{confBadge}</td>
                    <td style={{ padding: '14px 16px' }}>{detailsCol}</td>
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                        <button className="btn" onClick={() => onView(audit)} style={{ background: 'rgba(0,201,150,0.15)', color: 'var(--color-primary)', border: '1px solid var(--color-primary)', padding: '5px 10px', fontSize: '0.78rem' }}><Eye size={14}/> Voir</button>
                        <button className="btn" onClick={() => onEdit(audit)} style={{ background: 'rgba(245,158,11,0.15)', color: '#f59e0b', border: '1px solid #f59e0b', padding: '5px 10px', fontSize: '0.78rem' }}><Pen size={14}/> Éditer</button>
                        <button className="btn" onClick={() => onPrint(audit)} style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid #3b82f6', padding: '5px 10px', fontSize: '0.78rem' }}><Printer size={14}/> Imprimer</button>
                        <button className="btn" onClick={() => onDelete(audit)} style={{ background: 'rgba(244,63,94,0.15)', color: '#f43f5e', border: '1px solid #f43f5e', padding: '5px 10px', fontSize: '0.78rem' }}><Trash2 size={14}/></button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
