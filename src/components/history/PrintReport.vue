<script setup>
import { onMounted, watch, computed } from 'vue'

const props = defineProps(['audit'])
const emit = defineEmits(['afterPrint'])

const triggerPrint = () => {
  if (props.audit) {
    setTimeout(() => {
      window.print()
      emit('afterPrint')
    }, 400)
  }
}

onMounted(() => {
  triggerPrint()
})

watch(() => props.audit, () => {
  triggerPrint()
})

const isPermis = computed(() => props.audit?.form_type === 'permis_travail' || props.audit?.reference === 'FGSI-PERMIS')
const isTournee = computed(() => props.audit?.form_type === 'tournee_hse' || (props.audit?.reference && props.audit?.reference.includes('FGSI-010')))
const sheetTitle = computed(() => isPermis.value ? 'Permis de Travail' : (isTournee.value ? 'Tournée HSE' : 'Audit HSE Terrain'))
const refCode = computed(() => isPermis.value ? 'FGSI-PERMIS' : (isTournee.value ? 'FGSI-010-Ind:A' : 'FGSI-001-Ind:F'))
const items = computed(() => props.audit?.items_data || {})

const correctiveActions = computed(() => {
  const actions = []
  if (!props.audit || !props.audit.answers) return actions
  
  Object.entries(props.audit.answers).forEach(([qId, ans]) => {
    if (ans && (ans.status === 'nc' || ans.status === 'non_conforme') && (ans.constat || ans.action)) {
      actions.push({ qId, ...ans })
    }
  })
  return actions
})

const cellStyle = { padding: '6px 10px', borderBottom: '1px solid #e2e8f0', fontSize: '9pt', verticalAlign: 'top' }
const thStyle = { padding: '8px 10px', borderBottom: '2px solid #cbd5e1', background: '#f1f5f9', fontWeight: '800', fontSize: '8pt', textTransform: 'uppercase', color: '#334155', textAlign: 'left' }
</script>

<template>
  <div v-if="audit" class="print-area" style="background: #fff; color: #000; padding: 20px; font-size: 10pt; font-family: Arial, sans-serif;">
    
    <!-- HEADER -->
    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #003d4d; padding-bottom: 12px; margin-bottom: 15px;">
      <div>
        <div style="font-size: 0.75rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;">CIPI ACTIA — Portail Responsable HSE</div>
        <h1 style="font-size: 1.5rem; font-weight: 800; color: #003d4d; margin: 0 0 4px 0;">{{ sheetTitle }}</h1>
        <div style="font-size: 0.88rem; font-weight: 600; color: #475569;">Fiche d'Évaluation & Suivi · Réf: {{ refCode }}</div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 1.1rem; font-weight: 800; color: #003d4d;">Fiche N° #ACTIA-{{ audit.id }}</div>
        <div style="font-size: 0.85rem; color: #475569;">Date : <strong>{{ audit.date_audit }}</strong></div>
        <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">{{ audit.reference }}</div>
      </div>
    </div>

    <!-- METADATA GRID -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #cbd5e1; margin-bottom: 15px; font-size: 9.5pt;">
      <div><strong>Secteur / Zone :</strong> {{ audit.secteur }}</div>
      <div><strong>Intervenants / Responsables :</strong> {{ audit.intervenants }}</div>
      <template v-if="!isPermis">
        <div><strong>Taux de Conformité HSE :</strong> <span style="font-size: 1.1rem; font-weight: 800; color: #059669;">{{ audit.taux_conformite }} %</span></div>
        <div><strong>Évaluations :</strong> {{ audit.total_conforme }} Conforme · {{ audit.total_non_conforme }} Non Conforme · {{ audit.total_na }} N/A</div>
      </template>
    </div>

    <!-- PERMIS DE TRAVAIL -->
    <table v-if="isPermis" style="width: 100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #cbd5e1;">
      <thead>
        <tr>
          <th :style="thStyle">Type de Permis / Autorisation</th>
          <th :style="{ ...thStyle, textAlign: 'center' }">Nombre Émis / Validés</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td :style="cellStyle"><strong>1. Plan de Prévention</strong></td>
          <td :style="{ ...cellStyle, textAlign: 'center', fontWeight: '800', color: '#1d4ed8' }">{{ items.plan_prevention || 0 }}</td>
        </tr>
        <tr>
          <td :style="cellStyle"><strong>2. Permis de Travail en Hauteur</strong></td>
          <td :style="{ ...cellStyle, textAlign: 'center', fontWeight: '800', color: '#c2410c' }">{{ items.permis_hauteur || 0 }}</td>
        </tr>
        <tr>
          <td :style="cellStyle"><strong>3. Permis de Feu</strong></td>
          <td :style="{ ...cellStyle, textAlign: 'center', fontWeight: '800', color: '#b91c1c' }">{{ items.permis_feu || 0 }}</td>
        </tr>
      </tbody>
    </table>

    <!-- CORRECTIVE ACTIONS TABLE -->
    <div v-if="!isPermis && correctiveActions.length > 0" style="margin-bottom: 15px;">
      <div style="font-size: 10pt; font-weight: 800; color: #b91c1c; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
        ⚠ Tableau Récapitulatif des Actions Correctives ({{ correctiveActions.length }})
      </div>
      <table style="width: 100%; border-collapse: collapse; border: 1px solid #cbd5e1;">
        <thead>
          <tr>
            <th :style="thStyle">Constat</th>
            <th :style="thStyle">Action Proposée</th>
            <th :style="thStyle">Responsable</th>
            <th :style="thStyle">Délai</th>
            <th :style="thStyle">État</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(ac, i) in correctiveActions" :key="i">
            <td :style="cellStyle">{{ ac.constat || '—' }}</td>
            <td :style="cellStyle">{{ ac.action || '—' }}</td>
            <td :style="cellStyle">{{ ac.resp || '—' }}</td>
            <td :style="cellStyle">{{ ac.delai || '—' }}</td>
            <td :style="{ ...cellStyle, fontWeight: '700', color: ac.etat === 'Soldée' ? '#059669' : (ac.etat === 'En cours' ? '#1d4ed8' : '#b91c1c') }">
              {{ ac.etat || 'Non engagée' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- NO CORRECTIVE ACTIONS -->
    <div v-if="!isPermis && correctiveActions.length === 0" style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 10px 14px; border-radius: 6px; margin-bottom: 15px; font-size: 9.5pt; color: #065f46;">
      ✓ Aucune non-conformité détectée — Toutes les questions ont été évaluées conformes ou N/A.
    </div>

    <!-- COMMENTS -->
    <div v-if="audit.commentaires_generaux" style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; border-left: 4px solid #003d4d; margin-bottom: 15px; font-size: 9.5pt;">
      <strong>Commentaires des intervenants :</strong><br/>{{ audit.commentaires_generaux }}
    </div>

    <!-- STATUS SUMMARY -->
    <div v-if="!isPermis" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 20px;">
      <div style="text-align: center; padding: 8px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px;">
        <div style="font-size: 1.2rem; font-weight: 800; color: #059669;">{{ audit.count_soldee || 0 }}</div>
        <div style="font-size: 7.5pt; color: #065f46; font-weight: 700;">Soldée</div>
      </div>
      <div style="text-align: center; padding: 8px; background: #dbeafe; border: 1px solid #93c5fd; border-radius: 6px;">
        <div style="font-size: 1.2rem; font-weight: 800; color: #1d4ed8;">{{ audit.count_en_cours || 0 }}</div>
        <div style="font-size: 7.5pt; color: #1e40af; font-weight: 700;">En cours</div>
      </div>
      <div style="text-align: center; padding: 8px; background: #fee2e2; border: 1px solid #fca5a5; border-radius: 6px;">
        <div style="font-size: 1.2rem; font-weight: 800; color: #b91c1c;">{{ audit.count_en_retard || 0 }}</div>
        <div style="font-size: 7.5pt; color: #991b1b; font-weight: 700;">En retard</div>
      </div>
      <div style="text-align: center; padding: 8px; background: #fef3c7; border: 1px solid #fcd34d; border-radius: 6px;">
        <div style="font-size: 1.2rem; font-weight: 800; color: #92400e;">{{ audit.count_non_engagee || 0 }}</div>
        <div style="font-size: 7.5pt; color: #78350f; font-weight: 700;">Non engagée</div>
      </div>
    </div>

    <!-- SIGNATURES -->
    <div style="display: flex; justify-content: space-between; margin-top: 30px; padding-top: 15px; border-top: 1px dashed #cbd5e1; font-size: 9pt;">
      <div>Signature Auditeur / Intervenant :<br/><br/><br/>____________________</div>
      <div style="text-align: center;">Date de Validation :<br/><br/><br/>____/____/________</div>
      <div>Signature Responsable HSE :<br/><br/><br/>____________________</div>
    </div>

    <!-- FOOTER -->
    <div style="margin-top: 20px; text-align: center; font-size: 7.5pt; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 8px;">
      Document généré automatiquement — PlatformActia CIPI ACTIA · Portail Responsable HSE · {{ audit.date_audit }}
    </div>
  </div>
</template>
