<script setup>
import { ref, computed } from 'vue'
import { Eye, Pen, Printer, Trash2, Search, Calendar, Layers, FolderOpen, RotateCcw } from 'lucide-vue-next'

const props = defineProps(['audits'])
const emit = defineEmits(['refresh', 'view', 'edit', 'delete', 'print'])

const filterType = ref('')
const filterDate = ref('')
const filterSecteur = ref('')

const handleResetFilters = () => {
  filterType.value = ''
  filterDate.value = ''
  filterSecteur.value = ''
}

const filteredAudits = computed(() => {
  return (props.audits || []).filter(audit => {
    const matchType = !filterType.value || (filterType.value === 'audit_hse' ? (audit.form_type === 'audit_hse' || audit.form_type === 'audit_hse_complet') : audit.form_type === filterType.value)
    const matchDate = !filterDate.value || audit.date_audit === filterDate.value
    const matchSecteur = !filterSecteur.value || (audit.secteur && audit.secteur.toLowerCase().includes(filterSecteur.value.toLowerCase())) || (audit.intervenants && audit.intervenants.toLowerCase().includes(filterSecteur.value.toLowerCase()))
    return matchType && matchDate && matchSecteur
  })
})
</script>

<template>
  <div>
    <!-- FILTER BAR -->
    <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap;">
      <div style="display: flex; flex-direction: column; gap: 6px;">
        <label style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">
          <Layers :size="14" style="display: inline; margin-right: 4px;" /> Type de Formulaire
        </label>
        <select class="form-input" v-model="filterType">
          <option value="">Tous les types de formulaires</option>
          <option value="audit_hse">Audit HSE (FGSI-001)</option>
          <option value="tournee_hse">Tournée HSE (FGSI-010-Ind:A)</option>
          <option value="permis_travail">Permis de Travail (FGSI-PERMIS)</option>
        </select>
      </div>

      <div style="display: flex; flex-direction: column; gap: 6px;">
        <label style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">
          <Calendar :size="14" style="display: inline; margin-right: 4px;" /> Date Audit
        </label>
        <input type="date" class="form-input" v-model="filterDate" />
      </div>

      <div style="display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 220px;">
        <label style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted);">
          <Search :size="14" style="display: inline; margin-right: 4px;" /> Recherche Secteur / Intervenant
        </label>
        <input type="text" class="form-input" placeholder="Filtrer instantanément..." v-model="filterSecteur" />
      </div>

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

    <!-- TABLE -->
    <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; overflow: hidden;">
      <table style="width: 100%; border-collapse: collapse; text-align: left;">
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
        <tbody>
          <tr v-if="filteredAudits.length === 0">
            <td colspan="7" style="text-align: center; padding: 3rem; color: var(--text-muted);">
              <FolderOpen :size="40" style="opacity: 0.5; margin-bottom: 10px;" />
              <div style="font-size: 1rem; font-weight: 700; color: #fff;">Aucune fiche trouvée</div>
              <div style="font-size: 0.85rem; margin-top: 4px;">Aucun enregistrement ne correspond aux critères.</div>
            </td>
          </tr>
          <tr v-for="audit in filteredAudits" :key="audit.id" style="border-bottom: 1px solid rgba(0,201,150,0.1);">
            <td style="padding: 14px 16px;">
              <strong :style="{ color: (audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS') ? '#60a5fa' : 'var(--color-primary)', fontFamily: 'var(--font-mono)' }">#ACTIA-{{ audit.id }}</strong>
              <div style="font-size: 0.72rem; color: var(--text-dim);">{{ audit.reference }}</div>
            </td>
            <td style="padding: 14px 16px;"><strong>{{ audit.date_audit }}</strong></td>
            <td style="padding: 14px 16px;"><span style="font-weight: 700; color: #fff;">{{ audit.secteur }}</span></td>
            <td style="padding: 14px 16px;"><span style="color: var(--text-muted); font-size: 0.85rem;">{{ audit.intervenants }}</span></td>
            <td style="padding: 14px 16px;">
              <span v-if="(audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS')" class="incident-badge" style="background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid #3b82f6;">FGSI-PERMIS</span>
              <span v-else :class="['incident-badge', audit.taux_conformite >= 85 ? 'badge-green' : (audit.taux_conformite >= 60 ? 'badge-orange' : 'badge-red')]">
                {{ audit.taux_conformite }} %
              </span>
            </td>
            <td style="padding: 14px 16px;">
              <div v-if="(audit.form_type === 'permis_travail' || audit.reference === 'FGSI-PERMIS')" style="font-size: 0.78rem; color: #60a5fa;">
                📋 Plan prev: <strong>{{ (audit.items_data || {}).plan_prevention || 0 }}</strong> · 🧗 Hauteur: <strong>{{ (audit.items_data || {}).permis_hauteur || 0 }}</strong> · 🔥 Feu: <strong>{{ (audit.items_data || {}).permis_feu || 0 }}</strong>
              </div>
              <div v-else style="font-size: 0.78rem;">
                <span style="color: #10b981;">✓ {{ audit.count_soldee }} Soldée</span> · <span style="color: #0284c7;">⚡ {{ audit.count_en_cours }} En cours</span> · <span style="color: #ef4444;">🔴 {{ audit.count_en_retard + audit.count_non_engagee }} À traiter</span>
              </div>
            </td>
            <td style="padding: 14px 16px; text-align: right;">
              <div style="display: flex; gap: 6px; justify-content: flex-end;">
                <button class="btn" @click="emit('view', audit)" style="background: rgba(0,201,150,0.15); color: var(--color-primary); border: 1px solid var(--color-primary); padding: 5px 10px; font-size: 0.78rem;"><Eye :size="14"/> Voir</button>
                <button class="btn" @click="emit('edit', audit)" style="background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid #f59e0b; padding: 5px 10px; font-size: 0.78rem;"><Pen :size="14"/> Éditer</button>
                <button class="btn" @click="emit('print', audit)" style="background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid #3b82f6; padding: 5px 10px; font-size: 0.78rem;"><Printer :size="14"/> Imprimer</button>
                <button class="btn" @click="emit('delete', audit)" style="background: rgba(244,63,94,0.15); color: #f43f5e; border: 1px solid #f43f5e; padding: 5px 10px; font-size: 0.78rem;"><Trash2 :size="14"/></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
