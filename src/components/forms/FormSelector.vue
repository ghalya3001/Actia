<script setup>
import { ClipboardCheck, ClipboardList, Shield, Activity, PenSquare } from 'lucide-vue-next';

const emit = defineEmits(['selectForm']);
</script>

<template>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
    
    <!-- CARD 1: AUDIT HSE (FGSI-001) -->
    <div class="glass-card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="width: 56px; height: 56px; border-radius: 12px; background: rgba(0,201,150,0.15); border: 1px solid var(--color-primary); color: var(--color-primary); display: flex; align-items: center; justify-content: center; margin-bottom: 1.25rem;">
          <ClipboardCheck :size="28" />
        </div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #fff; margin-bottom: 8px;">Audit HSE — Grille d'évaluation terrain</h3>
        <p style="font-size: 0.87rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.25rem;">
          Grille d'évaluation complète (EPI, Connaissances opérateurs, 5S, Sécurité machines, Incendie, Premier secours, Ergonomie).
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(255,255,255,0.06); color: var(--color-accent-light); border: 1px solid rgba(168,224,99,0.3);">Ref: FGSI-001 - Ind: F</span>
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(255,255,255,0.06); color: var(--color-accent-light); border: 1px solid rgba(168,224,99,0.3);">51 Points de contrôle</span>
        </div>
      </div>
      <button class="btn btn-primary" @click="emit('selectForm', 'audit_hse')">
        <PenSquare :size="16" /> Remplir l'Audit HSE (FGSI-001)
      </button>
    </div>

    <!-- CARD 2: TOURNÉE HSE (FGSI-010-Ind:A) -->
    <div class="glass-card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="width: 56px; height: 56px; border-radius: 12px; background: rgba(168,224,99,0.15); border: 1px solid var(--color-accent-light); color: var(--color-accent-light); display: flex; align-items: center; justify-content: center; margin-bottom: 1.25rem;">
          <ClipboardList :size="28" />
        </div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #fff; margin-bottom: 8px;">Tournée HSE — Grille de contrôle terrain</h3>
        <p style="font-size: 0.87rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.25rem;">
          Grille complète de Tournée HSE (Sécurité Générale, Produits Chimiques, Zone ATEX, Maintenance, Évacuation, Déchets).
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(255,255,255,0.06); color: var(--color-accent-light); border: 1px solid rgba(168,224,99,0.3);">Ref: FGSI-010-Ind:A</span>
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(255,255,255,0.06); color: var(--color-accent-light); border: 1px solid rgba(168,224,99,0.3);">42 Points de contrôle</span>
        </div>
      </div>
      <button class="btn" @click="emit('selectForm', 'tournee_hse')" style="background: rgba(168,224,99,0.15); border-color: var(--color-accent-light); color: var(--color-accent-light);">
        <PenSquare :size="16" /> Remplir la Tournée HSE (FGSI-010)
      </button>
    </div>

    <!-- CARD 3: PERMIS DE TRAVAIL (FGSI-PERMIS) -->
    <div class="glass-card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="width: 56px; height: 56px; border-radius: 12px; background: rgba(59,130,246,0.15); border: 1px solid #3b82f6; color: #3b82f6; display: flex; align-items: center; justify-content: center; margin-bottom: 1.25rem;">
          <Shield :size="28" />
        </div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #fff; margin-bottom: 8px;">Permis de Travail — Fiche d'autorisation</h3>
        <p style="font-size: 0.87rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.25rem;">
          Fiche de suivi et validation des permis de travail (Plan de prévention, Permis de travail en hauteur, Permis de feu).
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3);">Ref: FGSI-PERMIS</span>
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3);">3 Champs Numériques</span>
        </div>
      </div>
      <button class="btn" @click="emit('selectForm', 'permis_travail')" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: #ffffff; box-shadow: 0 4px 15px rgba(59,130,246,0.35);">
        <PenSquare :size="16" /> Remplir le Permis de Travail (FGSI-PERMIS)
      </button>
    </div>

    <!-- CARD 4: STATISTIQUES ACCIDENTS & SANTÉ (FGSI-STAT-ACCIDENTS) -->
    <div class="glass-card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="width: 56px; height: 56px; border-radius: 12px; background: rgba(245,158,11,0.15); border: 1px solid #f59e0b; color: #f59e0b; display: flex; align-items: center; justify-content: center; margin-bottom: 1.25rem;">
          <Activity :size="28" />
        </div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #fff; margin-bottom: 8px;">Statistiques Accidents & Santé — Suivi Mensuel</h3>
        <p style="font-size: 0.87rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.25rem;">
          Tableau de suivi des accidents du travail (avec et sans arrêt), heures travaillées, jours perdus, visites médicales et indicateurs TF/IF/TG.
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3);">Ref: FGSI-STAT-ACCIDENTS</span>
          <span style="font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3);">12 Mois · 8 Indicateurs</span>
        </div>
      </div>
      <button class="btn" @click="emit('selectForm', 'statistiques_accidents')" style="background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; box-shadow: 0 4px 15px rgba(217,119,6,0.35);">
        <PenSquare :size="16" /> Remplir le Suivi des Accidents
      </button>
    </div>

  </div>
</template>

