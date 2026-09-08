<script setup>
import { computed } from 'vue'
import { X, Printer } from 'lucide-vue-next'

const props = defineProps(['audit'])
const emit = defineEmits(['close', 'print'])

const isPermis = computed(() => props.audit?.form_type === 'permis_travail' || props.audit?.reference === 'FGSI-PERMIS')
const isTournee = computed(() => props.audit?.form_type === 'tournee_hse' || (props.audit?.reference && props.audit?.reference.includes('FGSI-010')))
const refTitle = computed(() => isPermis.value ? 'Permis de Travail (FGSI-PERMIS)' : (isTournee.value ? 'Tournée HSE (FGSI-010-Ind:A)' : 'Audit HSE (FGSI-001-Ind:F)'))

const items = computed(() => props.audit?.items_data || {})
</script>

<template>
  <div v-if="audit" class="modal-overlay">
    <div class="modal-card-large">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,201,150,0.2); padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
          <h2 style="font-size: 1.3rem; font-weight: 800; color: #fff;">Détail Fiche #ACTIA-{{ audit.id }}</h2>
          <div style="font-size: 0.8rem; color: var(--color-primary);">
            CIPI ACTIA · {{ refTitle }} | Secteur : {{ audit.secteur }} | Date : {{ audit.date_audit }}
          </div>
        </div>
        <button @click="emit('close')" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer;"><X :size="24" /></button>
      </div>

      <div v-if="isPermis">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem;">
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 16px; border-radius: 10px; text-align: center; border-top: 3px solid #3b82f6;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Plan de Prévention</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #60a5fa; font-family: var(--font-mono); margin-top: 4px;">{{ items.plan_prevention || 0 }}</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 16px; border-radius: 10px; text-align: center; border-top: 3px solid #ea580c;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Permis Travail Hauteur</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #fb923c; font-family: var(--font-mono); margin-top: 4px;">{{ items.permis_hauteur || 0 }}</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 16px; border-radius: 10px; text-align: center; border-top: 3px solid #dc2626;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Permis de Feu</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f87171; font-family: var(--font-mono); margin-top: 4px;">{{ items.permis_feu || 0 }}</div>
          </div>
        </div>

        <div v-if="items.remarques" style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 12px 16px; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
          <div style="font-size: 0.78rem; font-weight: 700; color: #60a5fa; text-transform: uppercase; margin-bottom: 4px;">Remarques spécifiques Permis :</div>
          <div style="font-size: 0.9rem; color: var(--text-main); line-height: 1.5;">{{ items.remarques }}</div>
        </div>
      </div>
      
      <div v-else>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem;">
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 12px; border-radius: 10px; text-align: center;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Taux de Conformité</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: var(--color-primary); font-family: var(--font-mono);">{{ audit.taux_conformite }} %</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 12px; border-radius: 10px; text-align: center;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Évaluations</div>
            <div style="font-size: 1rem; font-weight: 700; color: #fff; margin-top: 6px;">{{ audit.total_conforme }} ✓ / {{ audit.total_non_conforme }} ✗ / {{ audit.total_na }} N/A</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 12px; border-radius: 10px; text-align: center;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Actions Correctives</div>
            <div style="font-size: 1rem; font-weight: 700; color: var(--color-accent-light); margin-top: 6px;">{{ audit.count_soldee }} Soldée · {{ audit.count_en_cours }} En cours</div>
          </div>
        </div>
      </div>

      <div v-if="audit.commentaires_generaux" style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 12px 16px; border-radius: 10px; border-left: 4px solid var(--color-primary); margin-bottom: 1.5rem;">
        <div style="font-size: 0.78rem; font-weight: 700; color: var(--color-primary); text-transform: uppercase; margin-bottom: 4px;">Commentaires généraux :</div>
        <div style="font-size: 0.9rem; color: var(--text-main); line-height: 1.5;">{{ audit.commentaires_generaux }}</div>
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 12px; border-top: 1px solid rgba(0,201,150,0.2); padding-top: 1rem;">
        <button class="btn btn-secondary" @click="emit('print', audit)"><Printer :size="16"/> Imprimer la Fiche</button>
        <button class="btn btn-primary" @click="emit('close')">Fermer</button>
      </div>
    </div>
  </div>
</template>
