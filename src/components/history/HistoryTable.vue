<!--
  =============================================================================
  Composant : HistoryTable.vue
  Description : Tableau d'historique centralisé de tous les formulaires et audits HSE.
  Design : Interface alignée sur les standards ergonomiques de la gestion utilisateurs.
  Fonctionnalités :
    - Filtrage dynamique multicritère (Type de formulaire, Plage de dates Du/Au, Secteur/Intervenant)
    - Prise en charge du filtrage sur une journée unique si seule la date « Du » est renseignée
    - Réinitialisation instantanée des filtres avec indicateur visuel
    - Affichage adaptatif selon le type de formulaire (Audit, Tournée, Permis, Stats accidents)
    - Actions interactives par ligne : Consulter (View), Modifier (Edit), Imprimer (Print), Supprimer (Delete)
  =============================================================================
-->
<script setup>
import { ref, computed } from 'vue'
import {
  Eye,
  Pen,
  Printer,
  Trash2,
  Search,
  Calendar,
  Layers,
  FolderOpen,
  RotateCcw,
  ArrowRight,
  Info,
  X,
  User
} from 'lucide-vue-next'

// Propriétés reçues du composant parent :
// - audits : Tableau complet des objets audits/formulaires récupérés depuis l'API backend
const props = defineProps(['audits'])

// Événements émis vers le parent :
const emit = defineEmits(['refresh', 'view', 'edit', 'delete', 'print'])

// --- ÉTATS RÉACTIFS DES FILTRES ---
const filterType = ref('')       // Filtre par type : 'audit_hse', 'tournee_hse', 'permis_travail', 'statistiques_accidents'
const filterSecteur = ref('')    // Filtre textuel insensible à la casse (Secteur ou Intervenants)
const dateFrom = ref('')         // Date de début (YYYY-MM-DD)
const dateTo = ref('')           // Date de fin (YYYY-MM-DD)

/**
 * Indique si un ou plusieurs filtres personnalisés sont actifs.
 */
const hasActiveFilters = computed(() => {
  return (
    filterType.value !== '' ||
    dateFrom.value !== '' ||
    dateTo.value !== '' ||
    filterSecteur.value.trim() !== ''
  )
})

/**
 * Formatage simple d'une date (YYYY-MM-DD -> DD/MM/YYYY).
 */
const formatDateSimple = (val) => {
  if (!val) return ''
  const parts = val.split('-')
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`
  }
  return val
}

/**
 * Texte explicatif dynamique du filtre de date.
 */
const dateFilterHint = computed(() => {
  if (dateFrom.value && !dateTo.value) {
    return `Affichage des fiches du ${formatDateSimple(dateFrom.value)} uniquement.`
  }
  if (dateFrom.value && dateTo.value) {
    return `Période du ${formatDateSimple(dateFrom.value)} au ${formatDateSimple(dateTo.value)}.`
  }
  if (!dateFrom.value && dateTo.value) {
    return `Fiches jusqu'au ${formatDateSimple(dateTo.value)}.`
  }
  return null
})

/**
 * Réinitialise tous les filtres de recherche à leur valeur par défaut.
 */
const handleResetFilters = () => {
  filterType.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  filterSecteur.value = ''
}

/**
 * Réinitialise uniquement les filtres de date.
 */
const resetDateFilter = () => {
  dateFrom.value = ''
  dateTo.value = ''
}

/**
 * Propriété calculée retournant la liste filtrée des audits en fonction des critères actifs :
 * - Correspondance de type (supporte le type étendu 'audit_hse_complet')
 * - Plage de dates ou date unique stricte si seule dateFrom est fournie
 * - Correspondance textuelle dans le libellé du secteur ou des intervenants
 */
const filteredAudits = computed(() => {
  return (props.audits || []).filter(audit => {
    // 1. Filtrage par type de formulaire
    const matchType = !filterType.value || (filterType.value === 'audit_hse' ? (audit.form_type === 'audit_hse' || audit.form_type === 'audit_hse_complet') : audit.form_type === filterType.value)

    // 2. Filtrage par plage de dates ou date unique
    let matchDate = true
    if (dateFrom.value && dateTo.value) {
      matchDate = audit.date_audit >= dateFrom.value && audit.date_audit <= dateTo.value
    } else if (dateFrom.value) {
      // Si seule la date 'Du' est renseignée, filtrer exactement sur cette journée
      matchDate = audit.date_audit === dateFrom.value
    } else if (dateTo.value) {
      matchDate = audit.date_audit <= dateTo.value
    }

    // 3. Filtrage textuel sur le secteur, les intervenants ou l'auteur
    const query = (filterSecteur.value || '').toLowerCase().trim()
    const matchSecteur = !query || 
      (audit.secteur && audit.secteur.toLowerCase().includes(query)) || 
      (audit.intervenants && audit.intervenants.toLowerCase().includes(query)) ||
      (audit.author_name && audit.author_name.toLowerCase().includes(query))
    
    return matchType && matchDate && matchSecteur
  })
})
</script>

<template>
  <div>
    <!-- ======================================================================= -->
    <!-- BARRE DE FILTRES ET DE RECHERCHE MULTICRITÈRE (DESIGN USER MANAGEMENT)   -->
    <!-- ======================================================================= -->
    <div class="control-panel glass-card">
      
      <!-- Ligne 1 : Type de formulaire + Recherche Secteur / Intervenant / Auteur -->
      <div class="filters-row-primary">
        <!-- Sélecteur Type de Formulaire -->
        <div class="type-filter-box">
          <label class="filter-label">
            <Layers :size="14" class="label-icon" /> Type de Formulaire
          </label>
          <select class="form-input type-select" v-model="filterType">
            <option value="">Tous les types de formulaires</option>
            <option value="audit_hse">Audit HSE (FGSI-001)</option>
            <option value="tournee_hse">Tournée HSE (FGSI-010-Ind:A)</option>
            <option value="permis_travail">Permis de Travail (FGSI-PERMIS)</option>
            <option value="statistiques_accidents">Statistiques Accidents & Santé (FGSI-STAT)</option>
          </select>
        </div>

        <!-- Recherche textuelle Secteur / Intervenant / Auteur -->
        <div class="search-box">
          <label class="filter-label">
            <Search :size="14" class="label-icon" /> Recherche Secteur / Intervenant / Auteur
          </label>
          <div class="search-input-wrapper">
            <Search :size="15" class="search-icon-inside" />
            <input 
              type="text" 
              class="form-input search-input" 
              placeholder="Filtrer par secteur, intervenant, auteur..." 
              v-model="filterSecteur" 
            />
            <button 
              v-if="filterSecteur" 
              class="clear-input-btn" 
              @click="filterSecteur = ''" 
              title="Effacer"
            >
              <X :size="14" />
            </button>
          </div>
        </div>
      </div>

      <!-- Ligne 2 : Filtre de Date par Plage (Du / Au) identique à UserManagement -->
      <div class="filters-row-secondary">
        <div class="date-filter-wrapper">
          <div class="date-filter-label">
            <Calendar :size="15" class="calendar-icon" />
            <span>Date de réalisation :</span>
          </div>

          <div class="date-inputs-group">
            <div class="date-input-field">
              <span class="date-sublabel">Du</span>
              <input 
                type="date" 
                class="form-input date-input"
                v-model="dateFrom"
                title="Date de début (si seule date renseignée, filtre uniquement cette journée)"
              />
            </div>

            <ArrowRight :size="14" class="date-separator" />

            <div class="date-input-field">
              <span class="date-sublabel">Au</span>
              <input 
                type="date" 
                class="form-input date-input"
                v-model="dateTo"
                title="Date de fin"
              />
            </div>

            <button 
              v-if="dateFrom || dateTo" 
              class="btn-clear-date" 
              @click="resetDateFilter"
              title="Effacer le filtre par date"
            >
              <X :size="14" />
              <span>Effacer date</span>
            </button>
          </div>

          <!-- Note explicative conviviale -->
          <div v-if="dateFilterHint" class="date-hint-badge">
            <Info :size="13" />
            <span>{{ dateFilterHint }}</span>
          </div>
        </div>

        <!-- Bouton de réinitialisation générale -->
        <button 
          v-if="hasActiveFilters" 
          class="btn-reset-all" 
          @click="handleResetFilters"
          title="Réinitialiser tous les filtres"
        >
          <RotateCcw :size="13" />
          <span>Réinitialiser les filtres</span>
        </button>
      </div>

    </div>

    <!-- ======================================================================= -->
    <!-- TABLEAU DE DONNÉES (DATA TABLE)                                         -->
    <!-- ======================================================================= -->
    <div class="table-container glass-card">
      <div class="table-scroll">
        <table class="modern-table">
          <!-- En-tête des colonnes -->
          <thead>
            <tr>
              <th style="padding: 14px 18px;">Réf Fiche</th>
              <th style="padding: 14px 18px;">Date</th>
              <th style="padding: 14px 18px;">Secteur</th>
              <th style="padding: 14px 18px;">Intervenants</th>
              <th style="padding: 14px 18px;">Score / Type</th>
              <th style="padding: 14px 18px;">Détails Synthèse</th>
              <th style="padding: 14px 18px; text-align: right;">Actions</th>
            </tr>
          </thead>

          <!-- Corps du tableau -->
          <tbody>
            <!-- État vide si aucune fiche ne correspond aux filtres -->
            <tr v-if="filteredAudits.length === 0">
              <td colspan="7" class="table-empty-td">
                <div class="empty-icon-circle">
                  <FolderOpen :size="32" />
                </div>
                <div class="empty-title">Aucune fiche trouvée</div>
                <div class="empty-subtitle">Aucun enregistrement ne correspond à vos critères de recherche.</div>
                <button v-if="hasActiveFilters" class="btn btn-secondary" style="margin-top: 1rem;" @click="handleResetFilters">
                  <RotateCcw :size="14" /> Réinitialiser les filtres
                </button>
              </td>
            </tr>

            <!-- Lignes de fiches correspondantes -->
            <tr v-for="audit in filteredAudits" :key="audit.id">
              
              <!-- Colonne 1 : Référence unique et code document interne -->
              <td style="padding: 14px 18px;">
                <strong :style="{ color: audit.form_type === 'statistiques_accidents' ? '#fbbf24' : ((audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS') ? '#60a5fa' : 'var(--color-primary)'), fontFamily: 'var(--font-mono)' }">#ACTIA-{{ audit.id }}</strong>
                <div style="font-size: 0.72rem; color: var(--text-dim);">{{ audit.reference }}</div>
                <div v-if="audit.author_name" style="font-size: 0.72rem; color: #a5b4fc; display: flex; align-items: center; gap: 4px; margin-top: 3px;" :title="'Saisi par ' + audit.author_name">
                  <User :size="11" />
                  <span>{{ audit.author_name }}</span>
                </div>
              </td>

              <!-- Colonne 2 : Date de réalisation -->
              <td style="padding: 14px 18px;">
                <strong style="color: #ffffff;">{{ formatDateSimple(audit.date_audit) }}</strong>
              </td>

              <!-- Colonne 3 : Secteur ou atelier audité -->
              <td style="padding: 14px 18px;">
                <span style="font-weight: 700; color: #fff;">{{ audit.secteur }}</span>
              </td>

              <!-- Colonne 4 : Nom des auditeurs ou intervenants -->
              <td style="padding: 14px 18px;">
                <span style="color: var(--text-muted); font-size: 0.85rem;">{{ audit.intervenants }}</span>
              </td>

              <!-- Colonne 5 : Badge visuel de score ou indicateur de formulaire -->
              <td style="padding: 14px 18px;">
                <!-- Cas Statistiques Accidents -->
                <span v-if="audit.form_type === 'statistiques_accidents'" class="incident-badge" style="background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid #f59e0b;">
                  FGSI-STAT
                </span>
                <!-- Cas Permis de Travail -->
                <span v-else-if="(audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS')" class="incident-badge" style="background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid #3b82f6;">FGSI-PERMIS</span>
                <!-- Cas Audits / Tournées avec taux de conformité calculé -->
                <span v-else :class="['incident-badge', audit.taux_conformite >= 85 ? 'badge-green' : (audit.taux_conformite >= 60 ? 'badge-orange' : 'badge-red')]">
                  {{ audit.taux_conformite }} %
                </span>
              </td>

              <!-- Colonne 6 : Synthèse rapide adaptée au type de formulaire -->
              <td style="padding: 14px 18px;">
                <!-- Synthèse statistiques accidents -->
                <div v-if="audit.form_type === 'statistiques_accidents'" style="font-size: 0.78rem; color: #fbbf24;">
                  🚨 Acc: <strong>{{ (audit.items_data || {}).totaux?.nb_accidents_total ?? 0 }}</strong> · 🛑 Arrêt: <strong>{{ (audit.items_data || {}).totaux?.nb_accidents_avec_arret ?? 0 }}</strong> · ⏱️ H: <strong>{{ ((audit.items_data || {}).totaux?.nb_heures_travaillees ?? 0).toLocaleString() }}</strong>
                </div>
                <!-- Synthèse permis de travail -->
                <div v-else-if="(audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS')" style="font-size: 0.78rem; color: #60a5fa;">
                  <template v-if="(audit.items_data || {}).dynamic_fields && (audit.items_data || {}).dynamic_fields.length > 0">
                    📋 <strong>{{ (audit.items_data || {}).dynamic_fields.length }} champ(s)</strong> :
                    <span style="color: var(--text-muted); margin-left: 4px;">
                      {{ (audit.items_data || {}).dynamic_fields.slice(0, 3).map(f => `${f.label}: ${f.value !== '' && f.value !== null && f.value !== undefined ? f.value : '—'}`).join(' · ') }}<span v-if="(audit.items_data || {}).dynamic_fields.length > 3">...</span>
                    </span>
                  </template>
                  <template v-else>
                    📋 Plan prev: <strong>{{ (audit.items_data || {}).plan_prevention || 0 }}</strong> · 🧗 Hauteur: <strong>{{ (audit.items_data || {}).permis_hauteur || 0 }}</strong> · 🔥 Feu: <strong>{{ (audit.items_data || {}).permis_feu || 0 }}</strong>
                  </template>
                </div>
                <!-- Synthèse audits classiques -->
                <div v-else style="font-size: 0.78rem;">
                  <span style="color: #10b981;">✓ {{ audit.count_soldee }} Soldée</span> · <span style="color: #0284c7;">⚡ {{ audit.count_en_cours }} En cours</span> · <span style="color: #ef4444;">🔴 {{ audit.count_en_retard + audit.count_non_engagee }} À traiter</span>
                </div>
              </td>

              <!-- Colonne 7 : Boutons d'actions contextuels -->
              <td style="padding: 14px 18px; text-align: right;">
                <div style="display: flex; gap: 6px; justify-content: flex-end;">
                  <button class="btn-tbl btn-tbl-view" @click="emit('view', audit)" title="Voir les détails complets">
                    <Eye :size="14"/> <span>Voir</span>
                  </button>
                  <button class="btn-tbl btn-tbl-edit" @click="emit('edit', audit)" title="Modifier les données">
                    <Pen :size="14"/> <span>Éditer</span>
                  </button>
                  <button class="btn-tbl btn-tbl-print" @click="emit('print', audit)" title="Générer le rapport imprimable">
                    <Printer :size="14"/> <span>Imprimer</span>
                  </button>
                  <button class="btn-tbl btn-tbl-delete" @click="emit('delete', audit)" title="Supprimer la fiche">
                    <Trash2 :size="14"/>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pied de tableau avec compteur -->
      <div v-if="filteredAudits.length > 0" class="table-footer">
        <span class="footer-count">
          Affichage de <strong>{{ filteredAudits.length }}</strong> fiche(s) sur {{ (props.audits || []).length }}
          <span v-if="hasActiveFilters" class="footer-filter-tag">(résultats filtrés)</span>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* =============================================================================
   PANNEAU DE FILTRES (DESIGN ALIGNÉ USER MANAGEMENT)
============================================================================= */
.control-panel {
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filters-row-primary {
  display: flex;
  align-items: flex-end;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.type-filter-box {
  min-width: 260px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.label-icon {
  color: var(--color-primary);
}

.type-select {
  height: 38px;
  font-size: 0.84rem;
}

.search-box {
  flex: 1;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon-inside {
  position: absolute;
  left: 12px;
  color: var(--text-dim);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 36px;
  padding-right: 32px;
  height: 38px;
  font-size: 0.85rem;
}

.clear-input-btn {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 2px;
}
.clear-input-btn:hover {
  color: #fff;
}

/* Ligne 2 : Filtres de Date */
.filters-row-secondary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  flex-wrap: wrap;
}

.date-filter-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.date-filter-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.calendar-icon {
  color: var(--color-primary);
}

.date-inputs-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input-field {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 2px 8px;
}

.date-sublabel {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--text-dim);
}

.date-input {
  background: transparent !important;
  border: none !important;
  color: #ffffff !important;
  padding: 4px 6px !important;
  font-size: 0.8rem;
  height: 30px;
  outline: none;
}

.date-input::-webkit-calendar-picker-indicator {
  filter: invert(0.8);
  cursor: pointer;
}

.date-separator {
  color: var(--text-dim);
}

.btn-clear-date {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.25);
  color: #f43f5e;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-clear-date:hover {
  background: rgba(244, 63, 94, 0.2);
}

.date-hint-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  font-size: 0.74rem;
  padding: 4px 10px;
  border-radius: 6px;
}

.btn-reset-all {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: var(--text-muted);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-reset-all:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* =============================================================================
   TABLEAU
============================================================================= */
.table-container {
  padding: 0;
  overflow: hidden;
  border-radius: 14px;
}

.table-scroll {
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.modern-table th {
  background: rgba(0, 32, 42, 0.9);
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modern-table td {
  border-bottom: 1px solid rgba(0, 201, 150, 0.08);
  font-size: 0.88rem;
  vertical-align: middle;
  transition: background 0.15s ease;
}

.modern-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.table-empty-td {
  text-align: center;
  padding: 3.5rem 1.5rem;
  color: var(--text-muted);
}

.empty-icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
  margin: 0 auto 10px;
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
}

.empty-subtitle {
  font-size: 0.85rem;
  margin-top: 4px;
}

/* Boutons d'action */
.btn-tbl {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-tbl-view {
  background: rgba(0, 201, 150, 0.12);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.3);
}
.btn-tbl-view:hover {
  background: rgba(0, 201, 150, 0.22);
}

.btn-tbl-edit {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.btn-tbl-edit:hover {
  background: rgba(245, 158, 11, 0.22);
}

.btn-tbl-print {
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}
.btn-tbl-print:hover {
  background: rgba(59, 130, 246, 0.22);
}

.btn-tbl-delete {
  background: rgba(244, 63, 94, 0.12);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.3);
}
.btn-tbl-delete:hover {
  background: rgba(244, 63, 94, 0.22);
}

.table-footer {
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.015);
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.footer-count {
  font-size: 0.78rem;
  color: var(--text-dim);
}

.footer-filter-tag {
  color: var(--color-primary);
  margin-left: 4px;
}
</style>
