<script setup>
import { computed } from 'vue'
import { X, Printer } from 'lucide-vue-next'

const props = defineProps(['audit'])
const emit = defineEmits(['close', 'print'])

const isPermis = computed(() => props.audit?.form_type === 'permis_travail' || props.audit?.reference === 'FGSI-PERMIS')
const isTournee = computed(() => props.audit?.form_type === 'tournee_hse' || (props.audit?.reference && props.audit?.reference.includes('FGSI-010')))
const isStatAccidents = computed(() => props.audit?.form_type === 'statistiques_accidents' || props.audit?.reference === 'FGSI-STAT-ACCIDENTS')
const refTitle = computed(() => {
  if (isStatAccidents.value) return 'Statistiques Accidents & Santé (FGSI-STAT-ACCIDENTS)'
  if (isPermis.value) return 'Permis de Travail (FGSI-PERMIS)'
  if (isTournee.value) return 'Tournée HSE (FGSI-010-Ind:A)'
  return 'Audit HSE (FGSI-001-Ind:F)'
})

const items = computed(() => props.audit?.items_data || {})
const monthsList = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
</script>

<template>
  <div v-if="audit" class="modal-overlay">
    <div class="modal-card-large" style="max-width: 95vw; max-height: 90vh; overflow-y: auto;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,201,150,0.2); padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
          <h2 style="font-size: 1.3rem; font-weight: 800; color: #fff;">Détail Fiche #ACTIA-{{ audit.id }}</h2>
          <div style="font-size: 0.8rem; color: var(--color-primary);">
            CIPI ACTIA · {{ refTitle }} | Secteur : {{ audit.secteur }} | Date : {{ audit.date_audit }}
          </div>
        </div>
        <button @click="emit('close')" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer;"><X :size="24" /></button>
      </div>

      <!-- STATISTIQUES ACCIDENTS VIEW -->
      <div v-if="isStatAccidents">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 1.5rem;">
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 14px; border-radius: 10px; text-align: center; border-top: 3px solid #f59e0b;">
            <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Total Accidents</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #fbbf24; font-family: var(--font-mono); margin-top: 4px;">{{ items.totaux?.nb_accidents_total ?? 0 }}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">{{ items.totaux?.nb_accidents_avec_arret ?? 0 }} avec arrêt / {{ items.totaux?.nb_accidents_sans_arret ?? 0 }} sans arrêt</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 14px; border-radius: 10px; text-align: center; border-top: 3px solid #ef4444;">
            <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Jours d'Arrêt Total</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #f87171; font-family: var(--font-mono); margin-top: 4px;">{{ items.totaux?.nb_jours_arret ?? 0 }}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Jours perdus cumulés</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 14px; border-radius: 10px; text-align: center; border-top: 3px solid #3b82f6;">
            <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Heures Travaillées</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #60a5fa; font-family: var(--font-mono); margin-top: 4px;">{{ (items.totaux?.nb_heures_travaillees ?? 0).toLocaleString() }}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">Année {{ items.annee || audit.secteur }}</div>
          </div>
          <div style="background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 14px; border-radius: 10px; text-align: center; border-top: 3px solid #10b981;">
            <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase;">Visites Médicales</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #34d399; font-family: var(--font-mono); margin-top: 4px;">{{ items.totaux?.nb_visites_medicales ?? 0 }}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">{{ items.totaux?.nb_maladies_professionnelles ?? 0 }} Maladie(s) prof.</div>
          </div>
        </div>

        <!-- 12-Month Table -->
        <div style="overflow-x: auto; background: rgba(0,24,32,0.9); border: 1px solid var(--card-border); border-radius: 10px; padding: 12px; margin-bottom: 1.5rem;">
          <table style="width: 100%; border-collapse: collapse; font-size: 0.78rem; text-align: center;">
            <thead>
              <tr style="background: rgba(0,201,150,0.15); color: var(--color-primary);">
                <th style="padding: 8px; text-align: left; min-width: 200px;">Indicateur</th>
                <th v-for="m in monthsList" :key="m" style="padding: 6px; min-width: 55px;">{{ m.slice(0, 4) }}.</th>
                <th style="padding: 8px; min-width: 70px; background: rgba(0,201,150,0.25); font-weight: 800;">TOTAL</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); font-weight: 800; background: rgba(0,201,150,0.08);">
                <td style="padding: 8px; text-align: left;">1. Nbr accident de travail (Total)</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_accidents_total ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800; color: var(--color-primary);">{{ items.totaux?.nb_accidents_total ?? 0 }}</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px; text-align: left;">2. Nombre d'accident avec arrêt</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_accidents_avec_arret ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.nb_accidents_avec_arret ?? 0 }}</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px; text-align: left;">3. Nombre d'accident sans arrêt</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_accidents_sans_arret ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.nb_accidents_sans_arret ?? 0 }}</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(253,224,71,0.08);">
                <td style="padding: 8px; text-align: left;">4. Nombre de jours d'arrêt de travail</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_jours_arret ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.nb_jours_arret ?? 0 }}</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px; text-align: left;">5. Effectif moyen (Salariés)</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_salaries ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">—</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(253,224,71,0.08);">
                <td style="padding: 8px; text-align: left;">6. Nombre d'heures travaillées</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_heures_travaillees ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.nb_heures_travaillees ?? 0 }}</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(253,224,71,0.08);">
                <td style="padding: 8px; text-align: left;">7. Nombre de visites médicales</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_visites_medicales ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.nb_visites_medicales ?? 0 }}</td>
              </tr>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(253,224,71,0.08);">
                <td style="padding: 8px; text-align: left;">8. Nombre de maladies professionnelles</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.nb_maladies_professionnelles ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.nb_maladies_professionnelles ?? 0 }}</td>
              </tr>
              <!-- INDICATORS TF / IF / TG / IG -->
              <tr style="border-top: 2px solid rgba(0,201,150,0.3); font-weight: 700; color: #38bdf8;">
                <td style="padding: 8px; text-align: left;">Taux de Fréquence (TF)</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.tf ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.tf_moyen ?? 0 }}</td>
              </tr>
              <tr style="font-weight: 700; color: #a855f7;">
                <td style="padding: 8px; text-align: left;">Indice de Fréquence (IF) [Cible: 2.5]</td>
                <td v-for="m in monthsList" :key="m" :style="{ padding: '6px', color: (items.mois?.[m]?.if_val || 0) > 2.5 ? '#ef4444' : '#10b981' }">
                  {{ items.mois?.[m]?.if_val ?? 0 }}
                </td>
                <td :style="{ padding: '8px', fontWeight: '800', color: (items.totaux?.if_moyen || 0) > 2.5 ? '#ef4444' : '#10b981' }">
                  {{ items.totaux?.if_moyen ?? 0 }}
                </td>
              </tr>
              <tr style="font-weight: 700; color: #f97316;">
                <td style="padding: 8px; text-align: left;">Taux de Gravité (TG)</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.tg ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.tg_moyen ?? 0 }}</td>
              </tr>
              <tr style="font-weight: 700; color: #ec4899;">
                <td style="padding: 8px; text-align: left;">Indice de Gravité (IG)</td>
                <td v-for="m in monthsList" :key="m" style="padding: 6px;">{{ items.mois?.[m]?.ig ?? 0 }}</td>
                <td style="padding: 8px; font-weight: 800;">{{ items.totaux?.ig_moyen ?? 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="isPermis">
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
