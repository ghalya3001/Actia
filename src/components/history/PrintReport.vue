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
const isStatAccidents = computed(() => props.audit?.form_type === 'statistiques_accidents' || props.audit?.reference === 'FGSI-STAT-ACCIDENTS')
const sheetTitle = computed(() => {
  if (isStatAccidents.value) return 'Statistiques Accidents & Santé — Suivi Mensuel'
  if (isPermis.value) return 'Permis de Travail'
  if (isTournee.value) return 'Tournée HSE'
  return 'Audit HSE Terrain'
})
const refCode = computed(() => {
  if (isStatAccidents.value) return 'FGSI-STAT-ACCIDENTS'
  if (isPermis.value) return 'FGSI-PERMIS'
  if (isTournee.value) return 'FGSI-010-Ind:A'
  return 'FGSI-001-Ind:F'
})
const items = computed(() => props.audit?.items_data || {})
const monthsList = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

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

const cellStyle = { padding: '5px 6px', borderBottom: '1px solid #cbd5e1', fontSize: '8pt', verticalAlign: 'middle' }
const thStyle = { padding: '6px 6px', borderBottom: '2px solid #cbd5e1', background: '#f1f5f9', fontWeight: '800', fontSize: '7.5pt', textTransform: 'uppercase', color: '#334155', textAlign: 'center' }
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
      <template v-if="!isPermis && !isStatAccidents">
        <div><strong>Taux de Conformité HSE :</strong> <span style="font-size: 1.1rem; font-weight: 800; color: #059669;">{{ audit.taux_conformite }} %</span></div>
        <div><strong>Évaluations :</strong> {{ audit.total_conforme }} Conforme · {{ audit.total_non_conforme }} Non Conforme · {{ audit.total_na }} N/A</div>
      </template>
      <template v-else-if="isStatAccidents">
        <div><strong>Année de Référence :</strong> <span style="font-size: 1.1rem; font-weight: 800; color: #d97706;">{{ items.annee || audit.secteur }}</span></div>
        <div><strong>Accidents Cumulés :</strong> {{ items.totaux?.nb_accidents_total ?? 0 }} total ({{ items.totaux?.nb_accidents_avec_arret ?? 0 }} avec arrêt) · <strong>Jours perdus :</strong> {{ items.totaux?.nb_jours_arret ?? 0 }}</div>
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

    <!-- STATISTIQUES ACCIDENTS TABLE -->
    <div v-if="isStatAccidents" style="margin-bottom: 20px; overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse; border: 1px solid #cbd5e1; font-size: 7.5pt; text-align: center;">
        <thead>
          <tr style="background: #f1f5f9; color: #1e293b; font-weight: 800;">
            <th :style="{ ...thStyle, textAlign: 'left', minWidth: '180px' }">Indicateurs HSE</th>
            <th v-for="m in monthsList" :key="m" :style="thStyle">{{ m.slice(0, 3) }}.</th>
            <th :style="{ ...thStyle, background: '#e2e8f0', fontWeight: '900' }">TOTAL</th>
          </tr>
        </thead>
        <tbody>
          <tr style="font-weight: 800; background: #f0fdf4;">
            <td :style="{ ...cellStyle, textAlign: 'left', color: '#166534' }">1. Nbr accident de travail (Total)</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_accidents_total ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '900', color: '#166534', background: '#dcfce7' }">{{ items.totaux?.nb_accidents_total ?? 0 }}</td>
          </tr>
          <tr>
            <td :style="{ ...cellStyle, textAlign: 'left' }">2. Nombre d'accident avec arrêt</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_accidents_avec_arret ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">{{ items.totaux?.nb_accidents_avec_arret ?? 0 }}</td>
          </tr>
          <tr>
            <td :style="{ ...cellStyle, textAlign: 'left' }">3. Nombre d'accident sans arrêt</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_accidents_sans_arret ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">{{ items.totaux?.nb_accidents_sans_arret ?? 0 }}</td>
          </tr>
          <tr style="background: #fefce8;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">4. Nombre de jours d'arrêt de travail</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_jours_arret ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">{{ items.totaux?.nb_jours_arret ?? 0 }}</td>
          </tr>
          <tr>
            <td :style="{ ...cellStyle, textAlign: 'left' }">5. Effectif moyen (Salariés)</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_salaries ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">—</td>
          </tr>
          <tr style="background: #fefce8;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">6. Nombre d'heures travaillées</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_heures_travaillees ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">{{ items.totaux?.nb_heures_travaillees ?? 0 }}</td>
          </tr>
          <tr style="background: #fefce8;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">7. Nombre de visites médicales</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_visites_medicales ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">{{ items.totaux?.nb_visites_medicales ?? 0 }}</td>
          </tr>
          <tr style="background: #fefce8;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">8. Nombre de maladies professionnelles</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.nb_maladies_professionnelles ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '800' }">{{ items.totaux?.nb_maladies_professionnelles ?? 0 }}</td>
          </tr>
          <tr style="border-top: 2px solid #cbd5e1; font-weight: 700; color: #0284c7;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">Taux de Fréquence (TF)</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.tf ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '900' }">{{ items.totaux?.tf_moyen ?? 0 }}</td>
          </tr>
          <tr style="font-weight: 700; color: #9333ea;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">Indice de Fréquence (IF) [Cible 2.5]</td>
            <td v-for="m in monthsList" :key="m" :style="{ ...cellStyle, color: (items.mois?.[m]?.if_val || 0) > 2.5 ? '#dc2626' : '#16a34a' }">
              {{ items.mois?.[m]?.if_val ?? 0 }}
            </td>
            <td :style="{ ...cellStyle, fontWeight: '900', color: (items.totaux?.if_moyen || 0) > 2.5 ? '#dc2626' : '#16a34a' }">
              {{ items.totaux?.if_moyen ?? 0 }}
            </td>
          </tr>
          <tr style="font-weight: 700; color: #ea580c;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">Taux de Gravité (TG)</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.tg ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '900' }">{{ items.totaux?.tg_moyen ?? 0 }}</td>
          </tr>
          <tr style="font-weight: 700; color: #db2777;">
            <td :style="{ ...cellStyle, textAlign: 'left' }">Indice de Gravité (IG)</td>
            <td v-for="m in monthsList" :key="m" :style="cellStyle">{{ items.mois?.[m]?.ig ?? 0 }}</td>
            <td :style="{ ...cellStyle, fontWeight: '900' }">{{ items.totaux?.ig_moyen ?? 0 }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CORRECTIVE ACTIONS TABLE -->
    <div v-if="!isPermis && !isStatAccidents && correctiveActions.length > 0" style="margin-bottom: 15px;">
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
    <div v-if="!isPermis && !isStatAccidents && correctiveActions.length === 0" style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 10px 14px; border-radius: 6px; margin-bottom: 15px; font-size: 9.5pt; color: #065f46;">
      ✓ Aucune non-conformité détectée — Toutes les questions ont été évaluées conformes ou N/A.
    </div>

    <!-- COMMENTS -->
    <div v-if="audit.commentaires_generaux" style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; border-left: 4px solid #003d4d; margin-bottom: 15px; font-size: 9.5pt;">
      <strong>Commentaires des intervenants :</strong><br/>{{ audit.commentaires_generaux }}
    </div>

    <!-- STATUS SUMMARY -->
    <div v-if="!isPermis && !isStatAccidents" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 20px;">
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
