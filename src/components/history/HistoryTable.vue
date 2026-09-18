<!--
  =============================================================================
  Composant : HistoryTable.vue
  Description : Tableau d'historique centralisé de tous les formulaires et audits HSE.
  Fonctionnalités :
    - Filtrage dynamique multicritère (Type de formulaire, Date, Secteur/Intervenant)
    - Réinitialisation instantanée des filtres avec indicateur visuel
    - Affichage adaptatif selon le type de formulaire (Audit, Tournée, Permis, Stats accidents)
    - Actions interactives par ligne : Consulter (View), Modifier (Edit), Imprimer (Print), Supprimer (Delete)
  =============================================================================
-->
<script setup>
import { ref, computed } from 'vue'
import { Eye, Pen, Printer, Trash2, Search, Calendar, Layers, FolderOpen, RotateCcw } from 'lucide-vue-next'

// Propriétés reçues du composant parent :
// - audits : Tableau complet des objets audits/formulaires récupérés depuis l'API backend
const props = defineProps(['audits'])

// Événements émis vers le parent :
// - refresh : Demande de rechargement des données
// - view : Ouverture de la modale de détail pour un audit spécifique
// - edit : Chargement de l'audit dans l'assistant de formulaire pour modification
// - delete : Ouverture de la boîte de confirmation de suppression
// - print : Déclenchement de l'affichage / impression du rapport officiel
const emit = defineEmits(['refresh', 'view', 'edit', 'delete', 'print'])

// --- ÉTATS RÉACTIFS DES FILTRES ---
const filterType = ref('')       // Filtre par type : 'audit_hse', 'tournee_hse', 'permis_travail', 'statistiques_accidents'
const filterDate = ref('')       // Filtre par date exacte d'audit (YYYY-MM-DD)
const filterSecteur = ref('')    // Filtre textuel insensible à la casse (Secteur ou Intervenants)

/**
 * Réinitialise tous les filtres de recherche à leur valeur par défaut (vide).
 */
const handleResetFilters = () => {
  filterType.value = ''
  filterDate.value = ''
  filterSecteur.value = ''
}

/**
 * Propriété calculée retournant la liste filtrée des audits en fonction des critères actifs :
 * - Correspondance de type (supporte le type étendu 'audit_hse_complet')
 * - Correspondance de date
 * - Correspondance partielle dans le libellé du secteur ou des intervenants
 */
const filteredAudits = computed(() => {
  return (props.audits || []).filter(audit => {
    // 1. Filtrage par type de formulaire
    const matchType = !filterType.value || (filterType.value === 'audit_hse' ? (audit.form_type === 'audit_hse' || audit.form_type === 'audit_hse_complet') : audit.form_type === filterType.value)
    // 2. Filtrage par date exacte
    const matchDate = !filterDate.value || audit.date_audit === filterDate.value
    // 3. Filtrage textuel sur le secteur ou les intervenants
    const matchSecteur = !filterSecteur.value || (audit.secteur && audit.secteur.toLowerCase().includes(filterSecteur.value.toLowerCase())) || (audit.intervenants && audit.intervenants.toLowerCase().includes(filterSecteur.value.toLowerCase()))
    
    return matchType && matchDate && matchSecteur
  })
})
</script>

<template>
  <div>
    <!-- ======================================================================= -->
    <!-- BARRE DE FILTRES ET DE RECHERCHE MULTICRITÈRE                          -->
    <!-- ======================================================================= -->
    <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap;">
      
      <!-- Sélecteur : Type de Formulaire -->
      <div style="display: flex; flex-direction: column; gap: 6px;">
        <label style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">
          <Layers :size="14" style="display: inline; margin-right: 4px;" /> Type de Formulaire
        </label>
        <select class="form-input" v-model="filterType">
          <option value="">Tous les types de formulaires</option>
          <option value="audit_hse">Audit HSE (FGSI-001)</option>
          <option value="tournee_hse">Tournée HSE (FGSI-010-Ind:A)</option>
          <option value="permis_travail">Permis de Travail (FGSI-PERMIS)</option>
          <option value="statistiques_accidents">Statistiques Accidents & Santé (FGSI-STAT)</option>
        </select>
      </div>

      <!-- Champ de saisie : Date de l'audit -->
      <div style="display: flex; flex-direction: column; gap: 6px;">
        <label style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">
          <Calendar :size="14" style="display: inline; margin-right: 4px;" /> Date Audit
        </label>
        <input type="date" class="form-input" v-model="filterDate" />
      </div>

      <!-- Champ de recherche libre : Secteur / Intervenants -->
      <div style="display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 220px;">
        <label style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">
          <Search :size="14" style="display: inline; margin-right: 4px;" /> Recherche Secteur / Intervenant
        </label>
        <input type="text" class="form-input" placeholder="Filtrer instantanément..." v-model="filterSecteur" />
      </div>

      <!-- Bouton d'action : Réinitialisation des filtres -->
      <div style="display: flex; align-items: center;">
        <button
          class="btn btn-secondary"
          @click="handleResetFilters"
          :disabled="!filterType && !filterDate && !filterSecteur"
          :style="{
            opacity: (!filterType && !filterDate && !filterSecteur) ? 0.5 : 1,
            cursor: (!filterType && !filterDate && !filterSecteur) ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '10px 16px',
            height: '42px'
          }"
          title="Réinitialiser tous les filtres de recherche"
        >
          <RotateCcw :size="14" /> Réinitialiser
        </button>
      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- TABLEAU DE DONNÉES (DATA TABLE)                                         -->
    <!-- ======================================================================= -->
    <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; overflow: hidden;">
      <table style="width: 100%; border-collapse: collapse; text-align: left;">
        
        <!-- En-tête des colonnes du tableau -->
        <thead>
          <tr style="background: rgba(0, 32, 42, 0.9); color: var(--color-primary); font-size: 0.8rem; font-weight: 800; text-transform: uppercase;">
            <th style="padding: 14px 16px;">Réf Fiche</th>
            <th style="padding: 14px 16px;">Date</th>
            <th style="padding: 14px 16px;">Secteur</th>
            <th style="padding: 14px 16px;">Intervenants</th>
            <th style="padding: 14px 16px;">Score / Type</th>
            <th style="padding: 14px 16px;">Détails Synthèse</th>
            <th style="padding: 14px 16px; text-align: right;">Actions</th>
          </tr>
        </thead>

        <!-- Corps du tableau -->
        <tbody>
          <!-- État vide si aucune fiche ne correspond aux filtres appliqués -->
          <tr v-if="filteredAudits.length === 0">
            <td colspan="7" style="text-align: center; padding: 3rem; color: var(--text-muted);">
              <FolderOpen :size="40" style="opacity: 0.5; margin-bottom: 10px;" />
              <div style="font-size: 1rem; font-weight: 700; color: #fff;">Aucune fiche trouvée</div>
              <div style="font-size: 0.85rem; margin-top: 4px;">Aucun enregistrement ne correspond aux critères.</div>
            </td>
          </tr>

          <!-- Lignes de fiches correspondantes -->
          <tr v-for="audit in filteredAudits" :key="audit.id" style="border-bottom: 1px solid rgba(0,201,150,0.1);">
            
            <!-- Colonne 1 : Référence unique et code document interne -->
            <td style="padding: 14px 16px;">
              <strong :style="{ color: audit.form_type === 'statistiques_accidents' ? '#fbbf24' : ((audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS') ? '#60a5fa' : 'var(--color-primary)'), fontFamily: 'var(--font-mono)' }">#ACTIA-{{ audit.id }}</strong>
              <div style="font-size: 0.72rem; color: var(--text-dim);">{{ audit.reference }}</div>
            </td>

            <!-- Colonne 2 : Date de réalisation -->
            <td style="padding: 14px 16px;"><strong>{{ audit.date_audit }}</strong></td>

            <!-- Colonne 3 : Secteur ou atelier audité -->
            <td style="padding: 14px 16px;"><span style="font-weight: 700; color: #fff;">{{ audit.secteur }}</span></td>

            <!-- Colonne 4 : Nom des auditeurs ou intervenants -->
            <td style="padding: 14px 16px;"><span style="color: var(--text-muted); font-size: 0.85rem;">{{ audit.intervenants }}</span></td>

            <!-- Colonne 5 : Badge visuel de score ou indicateur de formulaire -->
            <td style="padding: 14px 16px;">
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
            <td style="padding: 14px 16px;">
              <!-- Synthèse statistiques accidents (Totaux accidents, arrêts, heures) -->
              <div v-if="audit.form_type === 'statistiques_accidents'" style="font-size: 0.78rem; color: #fbbf24;">
                🚨 Acc: <strong>{{ (audit.items_data || {}).totaux?.nb_accidents_total ?? 0 }}</strong> · 🛑 Arrêt: <strong>{{ (audit.items_data || {}).totaux?.nb_accidents_avec_arret ?? 0 }}</strong> · ⏱️ H: <strong>{{ ((audit.items_data || {}).totaux?.nb_heures_travaillees ?? 0).toLocaleString() }}</strong>
              </div>
              <!-- Synthèse permis de travail (Plan de prévention, Hauteur, Feu) -->
              <div v-else-if="(audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS')" style="font-size: 0.78rem; color: #60a5fa;">
                📋 Plan prev: <strong>{{ (audit.items_data || {}).plan_prevention || 0 }}</strong> · 🧗 Hauteur: <strong>{{ (audit.items_data || {}).permis_hauteur || 0 }}</strong> · 🔥 Feu: <strong>{{ (audit.items_data || {}).permis_feu || 0 }}</strong>
              </div>
              <!-- Synthèse audits classiques (Actions soldées, en cours, à traiter) -->
              <div v-else style="font-size: 0.78rem;">
                <span style="color: #10b981;">✓ {{ audit.count_soldee }} Soldée</span> · <span style="color: #0284c7;">⚡ {{ audit.count_en_cours }} En cours</span> · <span style="color: #ef4444;">🔴 {{ audit.count_en_retard + audit.count_non_engagee }} À traiter</span>
              </div>
            </td>

            <!-- Colonne 7 : Boutons d'actions contextuels -->
            <td style="padding: 14px 16px; text-align: right;">
              <div style="display: flex; gap: 6px; justify-content: flex-end;">
                <!-- Bouton Consulter : émet 'view' avec la fiche sélectionnée -->
                <button class="btn" @click="emit('view', audit)" style="background: rgba(0,201,150,0.15); color: var(--color-primary); border: 1px solid var(--color-primary); padding: 5px 10px; font-size: 0.78rem;" title="Voir les détails complets"><Eye :size="14"/> Voir</button>
                <!-- Bouton Éditer : émet 'edit' avec la fiche sélectionnée -->
                <button class="btn" @click="emit('edit', audit)" style="background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid #f59e0b; padding: 5px 10px; font-size: 0.78rem;" title="Modifier les données"><Pen :size="14"/> Éditer</button>
                <!-- Bouton Imprimer : émet 'print' avec la fiche sélectionnée -->
                <button class="btn" @click="emit('print', audit)" style="background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid #3b82f6; padding: 5px 10px; font-size: 0.78rem;" title="Générer le rapport imprimable"><Printer :size="14"/> Imprimer</button>
                <!-- Bouton Supprimer : émet 'delete' avec la fiche sélectionnée -->
                <button class="btn" @click="emit('delete', audit)" style="background: rgba(244,63,94,0.15); color: #f43f5e; border: 1px solid #f43f5e; padding: 5px 10px; font-size: 0.78rem;" title="Supprimer la fiche"><Trash2 :size="14"/></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

