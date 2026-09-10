<script setup>
import { ref, computed, watch } from 'vue'
import {
  X,
  Plus,
  Check,
  SlidersHorizontal,
  TrendingUp,
  BarChart2,
  PieChart,
  Layers,
  Activity,
  Award,
  AlertCircle,
  Sparkles,
  Info,
  ChevronRight
} from 'lucide-vue-next'

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
} from 'chart.js'
import { Doughnut, Bar, Line, Radar } from 'vue-chartjs'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
)

const emit = defineEmits(['close', 'saveKpi', 'showToast'])

// ============================================================================
// 1. ÉTAT DU FORMULAIRE DE DÉFINITION DE KPI
// ============================================================================

const kpiLabel = ref('Mon KPI Combiné Personnalisé')
const kpiDescription = ref('Croisement multi-sources des indicateurs de sécurité')
const selectedChartType = ref('line')
const selectedPeriodicity = ref('monthly') // 'monthly', 'weekly', 'sector'

// Types de graphiques disponibles
const chartTypes = [
  { id: 'line', label: 'Courbe (Évolution)', icon: TrendingUp, desc: 'Tendance temporelle' },
  { id: 'bar', label: 'Barres (Comparatif)', icon: BarChart2, desc: 'Histogramme comparatif' },
  { id: 'doughnut', label: 'Donut (Proportions)', icon: PieChart, desc: 'Répartition & ratios' },
  { id: 'radar', label: 'Radar (Multi-Axes)', icon: Layers, desc: 'Cartographie thématique' },
  { id: 'card', label: 'Scorecard (Chiffre)', icon: Award, desc: 'Carte numérique clé' },
]

// Catalogue des métriques disponibles (issues de notre conception BDD)
const availableMetrics = [
  {
    id: 'tf',
    label: 'Taux de Fréquence (TF)',
    source: 'Table 2 (Taux_Frequence)',
    color: '#00c996',
    unit: 'acc/10⁶h',
    monthlyData: [3.10, 2.85, 2.60, 2.25, 2.10, 1.98, 1.92, 1.88, 1.82],
    weeklyData: [2.10, 2.05, 1.98, 1.95, 1.90, 1.85, 1.82],
    sectorData: [1.2, 2.4, 1.8, 2.8, 1.1],
  },
  {
    id: 'if',
    label: 'Indice de Fréquence (IF)',
    source: 'Table 2 (Taux_Frequence)',
    color: '#38bdf8',
    unit: 'indice',
    monthlyData: [2.10, 1.95, 1.80, 1.65, 1.50, 1.42, 1.35, 1.28, 1.20],
    weeklyData: [1.45, 1.40, 1.35, 1.30, 1.28, 1.24, 1.20],
    sectorData: [1.1, 1.6, 1.3, 1.9, 0.9],
  },
  {
    id: 'target',
    label: 'Objectif Cible Max (Target 2.5)',
    source: 'Seuil Réglementaire',
    color: '#ef4444',
    unit: 'cible',
    monthlyData: [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
    weeklyData: [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
    sectorData: [2.5, 2.5, 2.5, 2.5, 2.5],
  },
  {
    id: 'tg',
    label: 'Taux de Gravité (TG)',
    source: 'Table 3 (Taux_Gravite)',
    color: '#f59e0b',
    unit: 'tg',
    monthlyData: [0.18, 0.16, 0.15, 0.14, 0.12, 0.11, 0.10, 0.09, 0.08],
    weeklyData: [0.12, 0.11, 0.10, 0.10, 0.09, 0.08, 0.08],
    sectorData: [0.05, 0.12, 0.08, 0.14, 0.06],
  },
  {
    id: 'accidents_arret',
    label: 'Accidents Avec Arrêt',
    source: 'Table 1 (Accident_Travail)',
    color: '#ec4899',
    unit: 'accidents',
    monthlyData: [2, 1, 1, 1, 0, 1, 0, 0, 0],
    weeklyData: [1, 0, 0, 0, 0, 0, 0],
    sectorData: [0, 1, 0, 1, 0],
  },
  {
    id: 'accidents_sans_arret',
    label: 'Accidents Sans Arrêt',
    source: 'Table 1 (Accident_Travail)',
    color: '#a855f7',
    unit: 'accidents',
    monthlyData: [3, 2, 2, 1, 2, 1, 1, 1, 1],
    weeklyData: [1, 1, 0, 1, 0, 1, 1],
    sectorData: [1, 2, 1, 2, 1],
  },
  {
    id: 'conformite_tournees',
    label: 'Conformité Tournées (FGSI-010)',
    source: 'Tournee_HSE_Submission',
    color: '#a8e063',
    unit: '%',
    monthlyData: [84.5, 86.0, 87.2, 88.5, 89.4, 90.1, 91.0, 91.8, 92.4],
    weeklyData: [88.0, 89.2, 90.1, 90.8, 91.5, 91.9, 92.4],
    sectorData: [94.5, 88.0, 91.2, 82.5, 89.0],
  },
  {
    id: 'conformite_audits',
    label: 'Conformité Audits (FGSI-001)',
    source: 'Audit_HSE_Submission',
    color: '#10b981',
    unit: '%',
    monthlyData: [82.0, 84.1, 85.0, 86.8, 88.2, 89.0, 89.5, 90.2, 91.5],
    weeklyData: [86.5, 87.8, 88.4, 89.2, 90.0, 90.8, 91.5],
    sectorData: [92.0, 85.0, 89.5, 79.5, 86.4],
  },
  {
    id: 'actions_retard',
    label: 'Actions en Retard',
    source: 'Items Actions (Retard)',
    color: '#f87171',
    unit: 'actions',
    monthlyData: [12, 11, 9, 8, 7, 6, 6, 5, 5],
    weeklyData: [7, 7, 6, 6, 5, 5, 5],
    sectorData: [1, 1, 1, 1, 1],
  },
]

// Séries actuellement sélectionnées (par défaut 2 séries choisies : TF et Objectif)
const selectedMetricIds = ref(['tf', 'target'])

// Toggle une métrique (permet d'en choisir 1, 2 ou 3)
const toggleMetric = (metricId) => {
  const index = selectedMetricIds.value.indexOf(metricId)
  if (index > -1) {
    if (selectedMetricIds.value.length === 1) {
      emit('showToast', 'Vous devez conserver au moins 1 type de données sélectionné.', 'error')
      return
    }
    selectedMetricIds.value.splice(index, 1)
  } else {
    if (selectedMetricIds.value.length >= 3) {
      emit('showToast', 'Vous pouvez sélectionner au maximum 3 types de données combinés.', 'error')
      return
    }
    selectedMetricIds.value.push(metricId)
  }
}

// ============================================================================
// 2. GÉNÉRATION DYNAMIQUE DE L'APERÇU EN DIRECT (LIVE PREVIEW)
// ============================================================================

const labels = computed(() => {
  if (selectedPeriodicity.value === 'monthly') {
    return ['Janv', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept']
  } else if (selectedPeriodicity.value === 'weekly') {
    return ['Sem 30', 'Sem 31', 'Sem 32', 'Sem 33', 'Sem 34', 'Sem 35', 'Sem 36']
  } else {
    return ['CMS A', 'Stockage PDR', 'Assemblage B', 'Local Chimie', 'Maintenance']
  }
})

// Datasets pour Line / Bar
const previewChartData = computed(() => {
  const activeMetrics = availableMetrics.filter((m) => selectedMetricIds.value.includes(m.id))

  // Pour le Radar
  if (selectedChartType.value === 'radar') {
    return {
      labels: ['EPI', 'ATEX', 'Incendie', 'Ergonomie', '5S', 'Chimie', 'Machines'],
      datasets: activeMetrics.map((m, idx) => ({
        label: m.label,
        data: [94 - idx * 5, 88 + idx * 3, 96 - idx * 4, 76 + idx * 8, 91 - idx * 2, 82 + idx * 6, 89],
        backgroundColor: `${m.color}33`,
        borderColor: m.color,
        pointBackgroundColor: m.color,
        borderWidth: 2,
      })),
    }
  }

  // Pour le Donut
  if (selectedChartType.value === 'doughnut') {
    return {
      labels: activeMetrics.map((m) => m.label),
      datasets: [
        {
          data: activeMetrics.map((m, idx) => [60, 25, 15][idx] || 20),
          backgroundColor: activeMetrics.map((m) => m.color),
          borderColor: '#001c24',
          borderWidth: 3,
        },
      ],
    }
  }

  // Pour Line ou Bar
  return {
    labels: labels.value,
    datasets: activeMetrics.map((m) => {
      let series = m.monthlyData
      if (selectedPeriodicity.value === 'weekly') series = m.weeklyData
      if (selectedPeriodicity.value === 'sector') series = m.sectorData

      const isTarget = m.id === 'target'

      return {
        label: `${m.label} (${m.unit})`,
        data: series,
        borderColor: m.color,
        backgroundColor:
          selectedChartType.value === 'bar'
            ? `${m.color}b3`
            : `${m.color}20`,
        borderDash: isTarget ? [5, 5] : undefined,
        fill: selectedChartType.value === 'line' && !isTarget,
        tension: 0.35,
        borderRadius: selectedChartType.value === 'bar' ? 6 : undefined,
        pointBackgroundColor: m.color,
        pointRadius: 4,
        borderWidth: 2,
      }
    }),
  }
})

const previewChartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#cbd5e1',
          font: { family: 'Plus Jakarta Sans', size: 11, weight: '700' },
          usePointStyle: true,
          boxWidth: 8,
        },
      },
      tooltip: {
        backgroundColor: '#001c24',
        titleColor: '#00c996',
        bodyColor: '#fff',
        borderColor: 'rgba(0, 201, 150, 0.3)',
        borderWidth: 1,
      },
    },
    scales:
      selectedChartType.value === 'doughnut'
        ? {}
        : selectedChartType.value === 'radar'
        ? {
            r: {
              angleLines: { color: 'rgba(255,255,255,0.08)' },
              grid: { color: 'rgba(255,255,255,0.06)' },
              pointLabels: { color: '#cbd5e1', font: { size: 10, weight: '700' } },
            },
          }
        : {
            x: {
              ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } },
              grid: { color: 'rgba(255,255,255,0.03)' },
            },
            y: {
              ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } },
              grid: { color: 'rgba(255,255,255,0.05)' },
            },
          },
  }
})

// ============================================================================
// 3. ENREGISTREMENT DU KPI
// ============================================================================

const handleSave = () => {
  if (!kpiLabel.value.trim()) {
    emit('showToast', 'Veuillez saisir un nom pour votre KPI.', 'error')
    return
  }

  const activeMetrics = availableMetrics.filter((m) => selectedMetricIds.value.includes(m.id))

  const newKpiDef = {
    id: Date.now(),
    title: kpiLabel.value,
    description: kpiDescription.value,
    chartType: selectedChartType.value,
    periodicity: selectedPeriodicity.value,
    metrics: activeMetrics,
    chartData: previewChartData.value,
    chartOptions: previewChartOptions.value,
    createdAt: new Date().toLocaleDateString('fr-FR'),
  }

  emit('saveKpi', newKpiDef)
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div
      class="glass-card modal-container page-anim"
      style="
        max-width: 960px;
        width: 95%;
        max-height: 90vh;
        overflow-y: auto;
        padding: 2rem;
        background: linear-gradient(160deg, rgba(0, 36, 48, 0.98) 0%, rgba(0, 16, 22, 0.98) 100%);
        border: 1px solid rgba(0, 201, 150, 0.35);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
        border-radius: var(--radius-lg);
      "
    >
      <!-- HEADER MODAL -->
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="background: rgba(0, 201, 150, 0.15); color: var(--color-primary); font-size: 0.72rem; font-weight: 800; padding: 3px 10px; border-radius: 20px; text-transform: uppercase;">
              Studio de Définition des KPIs
            </span>
            <span style="color: var(--text-dim); font-size: 0.8rem;">•</span>
            <span style="font-size: 0.78rem; color: var(--color-accent-light); font-weight: 600;">
              Croisement Multi-Données
            </span>
          </div>
          <h2 style="font-size: 1.4rem; font-weight: 800; color: #fff;">
            Définir et Personnaliser un Nouveau KPI
          </h2>
          <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 2px;">
            Sélectionnez votre type de visualisation puis croisez 2 ou 3 types de données de vos grilles HSE.
          </p>
        </div>

        <button
          @click="emit('close')"
          style="
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-muted);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
          "
        >
          <X :size="18" />
        </button>
      </div>

      <!-- CORPS DU STUDIO (GRID 2 COLONNES : CONFIGURATION À GAUCHE, LIVE PREVIEW À DROITE) -->
      <div style="display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.5rem;" class="studio-grid">
        
        <!-- ================================================================= -->
        <!-- COLONNE GAUCHE : OPTIONS DE CONFIGURATION DU KPI                  -->
        <!-- ================================================================= -->
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
          
          <!-- ÉTAPE 1 : NOM DU KPI -->
          <div class="config-block">
            <label style="font-size: 0.78rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">
              1. Titre & Descriptif du KPI
            </label>
            <input
              v-model="kpiLabel"
              type="text"
              class="form-input"
              placeholder="Ex: Croisement TF & IF vs Cible..."
              style="width: 100%; background: rgba(0, 20, 26, 0.8); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 9px 12px; border-radius: var(--radius-sm); font-size: 0.88rem; font-weight: 600;"
            />
          </div>

          <!-- ÉTAPE 2 : CHOIX DU TYPE DE GRAPHIQUE -->
          <div class="config-block">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <label style="font-size: 0.78rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">
                2. Type de Graphique
              </label>
              <span style="font-size: 0.72rem; color: var(--color-primary); font-weight: 700;">
                {{ chartTypes.find(c => c.id === selectedChartType)?.label }}
              </span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px;">
              <div
                v-for="c in chartTypes"
                :key="c.id"
                @click="selectedChartType = c.id"
                :style="{
                  background: selectedChartType === c.id ? 'rgba(0, 201, 150, 0.18)' : 'rgba(0, 20, 26, 0.7)',
                  borderColor: selectedChartType === c.id ? 'var(--color-primary)' : 'rgba(255,255,255,0.08)',
                  boxShadow: selectedChartType === c.id ? '0 0 12px rgba(0,201,150,0.25)' : 'none'
                }"
                style="
                  padding: 10px;
                  border-radius: 8px;
                  border-width: 1.5px;
                  border-style: solid;
                  cursor: pointer;
                  transition: all 0.2s ease;
                  display: flex;
                  align-items: center;
                  gap: 8px;
                "
              >
                <component :is="c.icon" :size="16" :color="selectedChartType === c.id ? 'var(--color-primary)' : '#94a3b8'" />
                <div>
                  <div style="font-size: 0.78rem; font-weight: 700; color: #fff;">{{ c.label.split(' ')[0] }}</div>
                  <div style="font-size: 0.65rem; color: var(--text-dim);">{{ c.desc }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- ÉTAPE 3 : CHOIX DES 2 OU 3 TYPES DE DONNÉES -->
          <div class="config-block">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <label style="font-size: 0.78rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">
                3. Sélection des Données à Croiser
              </label>
              <span
                :style="{
                  color: selectedMetricIds.length >= 2 ? 'var(--color-primary)' : '#f59e0b',
                  background: selectedMetricIds.length >= 2 ? 'rgba(0,201,150,0.12)' : 'rgba(245,158,11,0.12)'
                }"
                style="font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 12px;"
              >
                {{ selectedMetricIds.length }} / 3 sélectionnées
              </span>
            </div>
            <p style="font-size: 0.74rem; color: var(--text-dim); margin-bottom: 10px;">
              Cochez <strong>2 ou 3 types de données</strong> pour les superposer sur le même graphique.
            </p>

            <!-- LISTE DES MÉTRIQUES AVEC BADGES CLIQUABLES -->
            <div style="display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto; padding-right: 4px;">
              <div
                v-for="m in availableMetrics"
                :key="m.id"
                @click="toggleMetric(m.id)"
                :style="{
                  background: selectedMetricIds.includes(m.id) ? 'rgba(0, 201, 150, 0.12)' : 'rgba(0, 20, 26, 0.6)',
                  borderColor: selectedMetricIds.includes(m.id) ? m.color : 'rgba(255,255,255,0.06)'
                }"
                style="
                  padding: 8px 12px;
                  border-radius: 8px;
                  border-width: 1px;
                  border-style: solid;
                  cursor: pointer;
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  transition: all 0.15s ease;
                "
              >
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span
                    :style="{
                      background: selectedMetricIds.includes(m.id) ? m.color : 'transparent',
                      borderColor: m.color
                    }"
                    style="
                      width: 16px;
                      height: 16px;
                      border-radius: 4px;
                      border-width: 1.5px;
                      border-style: solid;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                    "
                  >
                    <Check v-if="selectedMetricIds.includes(m.id)" :size="11" color="#001c24" stroke-width="3" />
                  </span>
                  <div>
                    <span style="font-size: 0.8rem; font-weight: 700; color: #fff;">{{ m.label }}</span>
                    <span style="font-size: 0.68rem; color: var(--text-dim); margin-left: 6px;">{{ m.source }}</span>
                  </div>
                </div>

                <span :style="{ color: m.color }" style="font-size: 0.74rem; font-weight: 800; font-family: var(--font-mono);">
                  {{ m.unit }}
                </span>
              </div>
            </div>
          </div>

          <!-- ÉTAPE 4 : AXE TEMPOREL / REGROUPEMENT -->
          <div class="config-block">
            <label style="font-size: 0.78rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">
              4. Axe d'Agrégation
            </label>
            <div style="display: flex; gap: 8px;">
              <button
                type="button"
                @click="selectedPeriodicity = 'monthly'"
                :style="{
                  background: selectedPeriodicity === 'monthly' ? 'var(--color-primary)' : 'rgba(0, 20, 26, 0.7)',
                  color: selectedPeriodicity === 'monthly' ? '#001c24' : '#fff'
                }"
                style="flex: 1; padding: 7px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.1); cursor: pointer;"
              >
                Mensuel (Janv-Sept)
              </button>
              <button
                type="button"
                @click="selectedPeriodicity = 'weekly'"
                :style="{
                  background: selectedPeriodicity === 'weekly' ? 'var(--color-primary)' : 'rgba(0, 20, 26, 0.7)',
                  color: selectedPeriodicity === 'weekly' ? '#001c24' : '#fff'
                }"
                style="flex: 1; padding: 7px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.1); cursor: pointer;"
              >
                Hebdomadaire (Semaines)
              </button>
              <button
                type="button"
                @click="selectedPeriodicity = 'sector'"
                :style="{
                  background: selectedPeriodicity === 'sector' ? 'var(--color-primary)' : 'rgba(0, 20, 26, 0.7)',
                  color: selectedPeriodicity === 'sector' ? '#001c24' : '#fff'
                }"
                style="flex: 1; padding: 7px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.1); cursor: pointer;"
              >
                Par Secteur (5 zones)
              </button>
            </div>
          </div>

        </div>

        <!-- ================================================================= -->
        <!-- COLONNE DROITE : APERÇU EN DIRECT (LIVE PREVIEW) DU GRAPHIQUE    -->
        <!-- ================================================================= -->
        <div
          style="
            background: rgba(0, 20, 26, 0.85);
            border: 1px solid rgba(0, 201, 150, 0.25);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
          "
        >
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-size: 0.72rem; font-weight: 800; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.5px;">
                Aperçu en Temps Réel
              </span>
              <span style="background: rgba(0, 201, 150, 0.15); color: var(--color-primary); font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 10px;">
                Rendu dynamique
              </span>
            </div>

            <h4 style="font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 2px;">
              {{ kpiLabel || 'Sans titre' }}
            </h4>
            <p style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 1rem;">
              Croisement de {{ selectedMetricIds.length }} série(s) de données · Format {{ chartTypes.find(c => c.id === selectedChartType)?.label }}
            </p>

            <!-- ZONE DU CHART PREVIEW -->
            <div style="height: 300px; position: relative;">
              <!-- Scorecard simple si Card choisie -->
              <div
                v-if="selectedChartType === 'card'"
                style="
                  height: 100%;
                  display: flex;
                  flex-direction: column;
                  justify-content: center;
                  align-items: center;
                  gap: 12px;
                  background: rgba(0, 0, 0, 0.2);
                  border-radius: 12px;
                  border: 1px dashed rgba(0, 201, 150, 0.3);
                  padding: 1rem;
                "
              >
                <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">
                  Valeur Actuelle (Dernier Mois)
                </div>
                <div style="font-size: 3.2rem; font-weight: 800; color: var(--color-primary); font-family: var(--font-mono);">
                  {{ availableMetrics.find(m => m.id === selectedMetricIds[0])?.monthlyData.slice(-1)[0] || '1.82' }}
                </div>
                <div style="font-size: 0.8rem; color: var(--color-accent-light); font-weight: 700;">
                  {{ availableMetrics.find(m => m.id === selectedMetricIds[0])?.label }}
                </div>
              </div>

              <!-- Line Chart -->
              <Line
                v-else-if="selectedChartType === 'line'"
                :data="previewChartData"
                :options="previewChartOptions"
              />

              <!-- Bar Chart -->
              <Bar
                v-else-if="selectedChartType === 'bar'"
                :data="previewChartData"
                :options="previewChartOptions"
              />

              <!-- Doughnut Chart -->
              <Doughnut
                v-else-if="selectedChartType === 'doughnut'"
                :data="previewChartData"
                :options="previewChartOptions"
              />

              <!-- Radar Chart -->
              <Radar
                v-else-if="selectedChartType === 'radar'"
                :data="previewChartData"
                :options="previewChartOptions"
              />
            </div>

            <!-- LÉGENDE RÉCAPITULATIVE DES DONNÉES CHOISIES -->
            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06); display: flex; flex-wrap: wrap; gap: 8px;">
              <span
                v-for="mId in selectedMetricIds"
                :key="mId"
                :style="{
                  borderColor: availableMetrics.find(m => m.id === mId)?.color,
                  color: availableMetrics.find(m => m.id === mId)?.color
                }"
                style="background: rgba(0,0,0,0.3); font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; border-width: 1px; border-style: solid;"
              >
                ● {{ availableMetrics.find(m => m.id === mId)?.label }}
              </span>
            </div>
          </div>

          <!-- FOOTER ACTIONS DE LA MODAL -->
          <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 1.25rem;">
            <button
              type="button"
              @click="emit('close')"
              style="
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: var(--text-main);
                padding: 10px 18px;
                border-radius: var(--radius-sm);
                font-size: 0.85rem;
                font-weight: 700;
                cursor: pointer;
              "
            >
              Annuler
            </button>

            <button
              type="button"
              @click="handleSave"
              style="
                background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
                border: none;
                color: #001c24;
                padding: 10px 22px;
                border-radius: var(--radius-sm);
                font-size: 0.85rem;
                font-weight: 800;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(0, 201, 150, 0.35);
              "
            >
              <Sparkles :size="16" />
              <span>Ajouter ce KPI au Dashboard</span>
            </button>
          </div>

        </div>

      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 10, 14, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.config-block {
  background: rgba(0, 24, 32, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 12px 14px;
}

@media (max-width: 768px) {
  .studio-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>
