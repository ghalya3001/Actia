<!--
  =============================================================================
  Composant : HseDashboard.vue
  Description : Tableau de bord décisionnel et opérationnel HSE (Health, Safety, Environment)
                de la plateforme CIPI ACTIA.
  Fonctionnalités :
    - 4 Scorecards exécutives de synthèse : TF mensuel, Taux de conformité, Actions en retard, Jours sans accident
    - Studio de KPIs personnalisés avec stockage local et croisement multi-données
    - Visualisations graphiques avancées (Chart.js / vue-chartjs) :
        * Courbe combinée TF & IF vs Cible réglementaire 2.50
        * Évolution hebdomadaire du taux de conformité
        * Radar d'évaluation des 7 thématiques de sécurité (FGSI-001 / FGSI-010)
        * Donut de répartition des statuts d'actions correctives
    - Tableau opérationnel de pilotage des actions correctives en retard avec filtrage multicritère
  =============================================================================
-->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  ShieldCheck,
  AlertCircle,
  AlertOctagon,
  Clock,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Award,
  Layers,
  Filter,
  Search,
  RefreshCw,
  Calendar,
  MapPin,
  User,
  ExternalLink,
  Flame,
  Activity,
  Zap,
  SlidersHorizontal,
  ChevronRight,
  Plus,
  Trash2,
  Sparkles,
  BarChart2,
  PieChart,
  Info
} from 'lucide-vue-next'

// Importations optimisées des composants Chart.js
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
import { Doughnut, Line, Radar, Bar } from 'vue-chartjs'
import KpiDefinitionModal from './KpiDefinitionModal.vue'

// Enregistrement global des composants Chart.js requis pour les 4 types de graphiques
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

// Définition des événements émis (toasts de confirmation et notifications)
const emit = defineEmits(['showToast'])

// ============================================================================
// 0. STUDIO DE KPIS PERSONNALISÉS (DÉFINITIONS UTILISATEUR & MULTI-DONNÉES)
// ============================================================================

// Contrôle l'ouverture/fermeture de la modale de définition de KPI
const showKpiModal = ref(false)

/**
 * Catalogue initial des KPIs personnalisés fournis par défaut lors du premier lancement
 */
const DEFAULT_CUSTOM_KPIS = [
  {
    id: 101,
    title: 'Croisement Accidents Avec Arrêt vs Sans Arrêt',
    description: 'Comparatif mensuel des 2 types d\'accidents de travail (Table 1 Accident_Travail)',
    chartType: 'bar',
    periodicity: 'monthly',
    metrics: [
      { id: 'accidents_arret', label: 'Accidents Avec Arrêt', color: '#ec4899', unit: 'accidents' },
      { id: 'accidents_sans_arret', label: 'Accidents Sans Arrêt', color: '#a855f7', unit: 'accidents' }
    ],
    chartData: {
      labels: ['Janv', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept'],
      datasets: [
        {
          label: 'Accidents Avec Arrêt (Table 1)',
          data: [2, 1, 1, 1, 0, 1, 0, 0, 0],
          backgroundColor: '#ec4899b3',
          borderColor: '#ec4899',
          borderWidth: 2,
          borderRadius: 6,
        },
        {
          label: 'Accidents Sans Arrêt (Table 1)',
          data: [3, 2, 2, 1, 2, 1, 1, 1, 1],
          backgroundColor: '#a855f7b3',
          borderColor: '#a855f7',
          borderWidth: 2,
          borderRadius: 6,
        }
      ]
    },
    chartOptions: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', size: 11, weight: '700' }, usePointStyle: true, boxWidth: 8 }
        },
        tooltip: {
          backgroundColor: '#001c24',
          titleColor: '#00c996',
          borderColor: 'rgba(0, 201, 150, 0.3)',
          borderWidth: 1
        }
      },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
        y: { ticks: { color: '#94a3b8', font: { weight: '600', size: 11 }, stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 0 }
      }
    },
    createdAt: '10/09/2026'
  },
  {
    id: 102,
    title: 'Conformité Audits vs Tournées par Secteur',
    description: 'Croisement des scores de conformité (FGSI-001 Audits vs FGSI-010 Tournées)',
    chartType: 'line',
    periodicity: 'sector',
    metrics: [
      { id: 'conformite_tournees', label: 'Conformité Tournées (FGSI-010)', color: '#a8e063', unit: '%' },
      { id: 'conformite_audits', label: 'Conformité Audits (FGSI-001)', color: '#10b981', unit: '%' }
    ],
    chartData: {
      labels: ['CMS A', 'Stockage PDR', 'Assemblage B', 'Local Chimie', 'Maintenance'],
      datasets: [
        {
          label: 'Conformité Tournées (%)',
          data: [94.5, 88.0, 91.2, 82.5, 89.0],
          borderColor: '#a8e063',
          backgroundColor: 'rgba(168, 224, 99, 0.18)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#a8e063',
          pointRadius: 5,
          borderWidth: 2,
        },
        {
          label: 'Conformité Audits (%)',
          data: [92.0, 85.0, 89.5, 79.5, 86.4],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#10b981',
          pointRadius: 5,
          borderWidth: 2,
        }
      ]
    },
    chartOptions: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', size: 11, weight: '700' }, usePointStyle: true, boxWidth: 8 }
        },
        tooltip: {
          backgroundColor: '#001c24',
          titleColor: '#00c996',
          borderColor: 'rgba(0, 201, 150, 0.3)',
          borderWidth: 1
        }
      },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
        y: { ticks: { color: '#94a3b8', font: { weight: '600', size: 11 }, callback: (val) => `${val}%` }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 70, max: 100 }
      }
    },
    createdAt: '10/09/2026'
  }
]

// Liste réactive des KPIs personnalisés configurés
const customKpis = ref([])

// ============================================================================
// 1. ÉTAT RÉACTIF — DONNÉES RÉELLES DEPUIS L'API BACKEND
// ============================================================================

// État de chargement
const isLoading = ref(true)
const isRefreshing = ref(false)
const loadError = ref('')

// Filtres de date
const filterYear = ref(null)
const filterDateDebut = ref('')
const filterDateFin = ref('')
const availableYears = ref([])

// Scorecards
const totalAudits = ref(0)
const avgConformite = ref(0)
const actionsEnRetard = ref(0)
const joursSansAccident = ref(0)
const dernierAccidentDate = ref('')
const tfCourant = ref(0)
const tfVariation = ref(0)
const conformiteDerniereTournee = ref(0)
const conformiteVariation = ref(0)
const totalPermis = ref(0)

// Donut actions
const actionsSoldee = ref(0)
const actionsEnCours = ref(0)
const actionsNonEngagee = ref(0)
const actionsRetardCount = ref(0)

// Filtres du tableau opérationnel des actions
const selectedSecteur = ref('all')
const selectedResponsable = ref('all')
const searchQuery = ref('')

// Données graphiques réactives
const monthlyLabels = ref([])
const monthlyTF = ref([])
const monthlyIF = ref([])
const targetTF = ref(2.5)

const conformiteLabels = ref([])
const conformiteValues = ref([])

const radarLabels = ref([])
const radarScores = ref([])

const secteurLabels = ref([])
const secteurValues = ref([])

// Actions en retard détaillées (depuis la BDD)
const rawActionsEnRetard = ref([])

// ============================================================================
// 2. FONCTION : CHARGEMENT DES DONNÉES DEPUIS L'API /dashboard/stats
// ============================================================================

const API_BASE = 'http://127.0.0.1:8000/api/v1'

/**
 * Récupère le token JWT depuis le localStorage
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

/**
 * Charge toutes les données du dashboard depuis le backend
 */
const fetchDashboardStats = async () => {
  try {
    loadError.value = ''

    // Construire les query params
    const params = new URLSearchParams()
    if (filterYear.value) params.append('year', filterYear.value)
    if (filterDateDebut.value) params.append('date_debut', filterDateDebut.value)
    if (filterDateFin.value) params.append('date_fin', filterDateFin.value)

    const url = `${API_BASE}/dashboard/stats?${params.toString()}`
    const response = await fetch(url, { headers: getAuthHeaders() })

    if (!response.ok) {
      throw new Error(`Erreur ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()

    // --- Scorecards ---
    totalAudits.value = data.total_audits || 0
    avgConformite.value = data.avg_conformite || 0
    actionsEnRetard.value = data.actions_en_retard || 0
    joursSansAccident.value = data.jours_sans_accident || 0
    dernierAccidentDate.value = data.dernier_accident_date || ''
    tfCourant.value = data.tf_courant || 0
    tfVariation.value = data.tf_variation || 0
    conformiteDerniereTournee.value = data.conformite_derniere_tournee || 0
    conformiteVariation.value = data.conformite_variation || 0
    totalPermis.value = data.total_permis || 0

    // --- Années disponibles ---
    availableYears.value = data.available_years || []

    // --- Donut actions ---
    actionsSoldee.value = data.actions_soldee || 0
    actionsEnCours.value = data.actions_en_cours || 0
    actionsNonEngagee.value = data.actions_non_engagee || 0
    actionsRetardCount.value = data.actions_retard_count || 0

    // --- Courbe TF & IF ---
    monthlyLabels.value = data.monthly_labels || []
    monthlyTF.value = data.monthly_tf || []
    monthlyIF.value = data.monthly_if || []
    targetTF.value = data.target_tf || 2.5

    // --- Conformité évolution ---
    conformiteLabels.value = data.conformite_labels || []
    conformiteValues.value = data.conformite_values || []

    // --- Radar thématique ---
    radarLabels.value = data.radar_labels || []
    radarScores.value = data.radar_scores || []

    // --- Conformité par secteur ---
    secteurLabels.value = data.secteur_labels || []
    secteurValues.value = data.secteur_values || []

    // --- Actions en retard ---
    rawActionsEnRetard.value = data.actions_retard_details || []

  } catch (err) {
    console.error('[Dashboard] Erreur de chargement:', err)
    loadError.value = err.message
  }
}

/**
 * Actualisation des données (bouton refresh)
 */
const handleRefreshSnapshots = async () => {
  isRefreshing.value = true
  await fetchDashboardStats()
  isRefreshing.value = false
  emit('showToast', 'Données du tableau de bord actualisées avec succès.')
}

/**
 * Appliquer les filtres de date
 */
const applyDateFilters = async () => {
  isLoading.value = true
  await fetchDashboardStats()
  isLoading.value = false
}

/**
 * Réinitialiser les filtres de date
 */
const resetDateFilters = () => {
  filterYear.value = null
  filterDateDebut.value = ''
  filterDateFin.value = ''
  applyDateFilters()
}

/**
 * Au montage du composant : chargement initial
 */
onMounted(async () => {
  // Charger les KPIs personnalisés depuis le localStorage navigateur
  const saved = localStorage.getItem('actia_custom_kpis')
  if (saved) {
    try {
      customKpis.value = JSON.parse(saved)
    } catch (e) {
      customKpis.value = [...DEFAULT_CUSTOM_KPIS]
    }
  } else {
    customKpis.value = [...DEFAULT_CUSTOM_KPIS]
    localStorage.setItem('actia_custom_kpis', JSON.stringify(DEFAULT_CUSTOM_KPIS))
  }

  // Charger les données réelles du dashboard
  await fetchDashboardStats()
  isLoading.value = false
})

/**
 * Enregistre un nouveau KPI configuré dans le studio et met à jour le localStorage
 */
const handleSaveCustomKpi = (newKpi) => {
  customKpis.value.unshift(newKpi)
  localStorage.setItem('actia_custom_kpis', JSON.stringify(customKpis.value))
  emit('showToast', `KPI "${newKpi.title}" défini et ajouté avec succès !`)
}

/**
 * Supprime un KPI personnalisé par son identifiant unique
 */
const handleDeleteCustomKpi = (id) => {
  customKpis.value = customKpis.value.filter((k) => k.id !== id)
  localStorage.setItem('actia_custom_kpis', JSON.stringify(customKpis.value))
  emit('showToast', 'KPI supprimé du tableau de bord.')
}

// ============================================================================
// 3. CONFIGURATION DES GRAPHIQUES (COMPUTED depuis données API)
// ============================================================================

// --- GRAPHIQUE 1 : Courbe mensuelle combinée : TF & IF vs Objectif ---
const monthlyKpiData = computed(() => ({
  labels: monthlyLabels.value.length > 0 ? monthlyLabels.value : ['Aucune donnée'],
  datasets: [
    {
      label: 'Taux de Fréquence (TF)',
      data: monthlyTF.value,
      borderColor: '#00c996',
      backgroundColor: 'rgba(0, 201, 150, 0.15)',
      fill: true,
      tension: 0.35,
      pointBackgroundColor: '#00c996',
      pointBorderColor: '#001c24',
      pointBorderWidth: 2,
      pointRadius: 5,
      pointHoverRadius: 7,
      yAxisID: 'y',
    },
    {
      label: 'Indice de Fréquence (IF / 10)',
      data: monthlyIF.value,
      borderColor: '#38bdf8',
      backgroundColor: 'transparent',
      borderDash: [4, 4],
      tension: 0.35,
      pointBackgroundColor: '#38bdf8',
      pointRadius: 4,
      yAxisID: 'y',
    },
    {
      label: `Objectif Cible Max (Target ${targetTF.value})`,
      data: monthlyLabels.value.map(() => targetTF.value),
      borderColor: '#ef4444',
      backgroundColor: 'transparent',
      borderWidth: 2,
      borderDash: [6, 6],
      pointRadius: 0,
      yAxisID: 'y',
    },
  ],
}))

const monthlyKpiOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'top',
      labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11, weight: '700' }, usePointStyle: true, boxWidth: 8 },
    },
    tooltip: {
      backgroundColor: '#001c24',
      titleColor: '#00c996',
      bodyColor: '#e2e8f0',
      borderColor: 'rgba(0, 201, 150, 0.4)',
      borderWidth: 1,
      padding: 10,
    },
  },
  scales: {
    x: { ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
    y: {
      type: 'linear', display: true, position: 'left', min: 0,
      suggestedMax: 4.0,
      ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } },
      grid: { color: 'rgba(255,255,255,0.05)' },
      title: { display: true, text: 'Valeur TF & IF', color: '#64748b', font: { size: 10, weight: '700' } },
    },
  },
}

// --- GRAPHIQUE 2 : Évolution du Taux de Conformité ---
const weeklyConformiteData = computed(() => ({
  labels: conformiteLabels.value.length > 0 ? conformiteLabels.value : ['Aucune donnée'],
  datasets: [
    {
      label: 'Taux Conformité Global (%)',
      data: conformiteValues.value,
      borderColor: '#a8e063',
      backgroundColor: 'rgba(168, 224, 99, 0.18)',
      fill: true,
      tension: 0.35,
      pointBackgroundColor: '#a8e063',
      pointBorderColor: '#001c24',
      pointBorderWidth: 2,
      pointRadius: 5,
    },
  ],
}))

const weeklyConformiteOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#001c24', titleColor: '#a8e063', bodyColor: '#fff', borderColor: '#a8e063', borderWidth: 1,
      callbacks: { label: (context) => ` Conformité : ${context.parsed.y} %` },
    },
  },
  scales: {
    x: { ticks: { color: '#94a3b8', font: { weight: '600', size: 11 } }, grid: { display: false } },
    y: {
      min: 0, max: 100,
      ticks: { color: '#94a3b8', font: { weight: '600', size: 11 }, stepSize: 10, callback: (val) => `${val}%` },
      grid: { color: 'rgba(255,255,255,0.05)' },
    },
  },
}

// --- GRAPHIQUE 3 : Radar des 7 Thématiques ---
const radarThematiqueData = computed(() => ({
  labels: radarLabels.value.length > 0 ? radarLabels.value : ['Aucune donnée'],
  datasets: [
    {
      label: 'Score Réel Obtenu (%)',
      data: radarScores.value,
      backgroundColor: 'rgba(0, 201, 150, 0.25)',
      borderColor: '#00c996',
      pointBackgroundColor: '#00c996',
      pointBorderColor: '#fff',
      pointRadius: 4,
      borderWidth: 2,
    },
    {
      label: 'Seuil Minimum Exigé (85%)',
      data: radarLabels.value.map(() => 85),
      backgroundColor: 'transparent',
      borderColor: 'rgba(239, 68, 68, 0.65)',
      borderDash: [3, 3],
      pointRadius: 0,
      borderWidth: 1.5,
    },
  ],
}))

const radarThematiqueOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 10, weight: '700' }, boxWidth: 8 },
    },
    tooltip: { backgroundColor: '#001c24', titleColor: '#00c996', borderColor: 'rgba(0, 201, 150, 0.3)', borderWidth: 1 },
  },
  scales: {
    r: {
      min: 0, max: 100,
      ticks: { display: false, stepSize: 10 },
      angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
      grid: { color: 'rgba(255, 255, 255, 0.06)' },
      pointLabels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', size: 10.5, weight: '700' } },
    },
  },
}

// --- GRAPHIQUE 4 : Donut du Statut des Actions Correctives ---
const totalActions = computed(() => actionsSoldee.value + actionsEnCours.value + actionsRetardCount.value + actionsNonEngagee.value)
const pctSoldee = computed(() => totalActions.value > 0 ? Math.round(actionsSoldee.value / totalActions.value * 100) : 0)

const actionsDonutData = computed(() => ({
  labels: [
    `Soldées (${pctSoldee.value}%)`,
    `En cours (${totalActions.value > 0 ? Math.round(actionsEnCours.value / totalActions.value * 100) : 0}%)`,
    `En retard (${totalActions.value > 0 ? Math.round(actionsRetardCount.value / totalActions.value * 100) : 0}%)`,
    `Non engagées (${totalActions.value > 0 ? Math.round(actionsNonEngagee.value / totalActions.value * 100) : 0}%)`
  ],
  datasets: [
    {
      data: [actionsSoldee.value, actionsEnCours.value, actionsRetardCount.value, actionsNonEngagee.value],
      backgroundColor: ['#10b981', '#3b82f6', '#ef4444', '#f59e0b'],
      borderColor: ['#001c24', '#001c24', '#001c24', '#001c24'],
      borderWidth: 3,
      hoverOffset: 4,
    },
  ],
}))

const actionsDonutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 10.5, weight: '700' }, padding: 12, usePointStyle: true, boxWidth: 8 },
    },
    tooltip: { backgroundColor: '#001c24', titleColor: '#fff', bodyColor: '#cbd5e1', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 },
  },
  cutout: '68%',
}

// ============================================================================
// 4. FILTRAGE RÉACTIF DES ACTIONS EN RETARD
// ============================================================================

/**
 * Filtrage dynamique réactif selon le secteur, le responsable et la recherche libre
 */
const filteredActions = computed(() => {
  return rawActionsEnRetard.value.filter((item) => {
    const matchSecteur = selectedSecteur.value === 'all' || item.secteur === selectedSecteur.value
    const matchResponsable = selectedResponsable.value === 'all' || item.responsable === selectedResponsable.value
    const query = searchQuery.value.toLowerCase().trim()
    const matchSearch =
      !query ||
      (item.ref || '').toLowerCase().includes(query) ||
      (item.constat || '').toLowerCase().includes(query) ||
      (item.action || '').toLowerCase().includes(query) ||
      (item.responsable || '').toLowerCase().includes(query) ||
      (item.secteur || '').toLowerCase().includes(query)

    return matchSecteur && matchResponsable && matchSearch
  })
})

// Liste des secteurs disponibles pour le filtre déroulant (dynamique depuis les données)
const secteursList = computed(() => {
  const set = new Set(rawActionsEnRetard.value.map(a => a.secteur).filter(Boolean))
  return [...set]
})

// Liste des responsables opérationnels pour le filtre déroulant (dynamique depuis les données)
const responsablesList = computed(() => {
  const set = new Set(rawActionsEnRetard.value.map(a => a.responsable).filter(Boolean))
  return [...set]
})

// Label du filtre actif pour l'affichage
const filterLabel = computed(() => {
  const parts = []
  if (filterYear.value) parts.push(`Année ${filterYear.value}`)
  if (filterDateDebut.value) parts.push(`Du ${filterDateDebut.value}`)
  if (filterDateFin.value) parts.push(`Au ${filterDateFin.value}`)
  return parts.length > 0 ? parts.join(' · ') : 'Toutes les données'
})

// Mois en cours en français
const moisCourant = computed(() => {
  const mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
  return mois[new Date().getMonth()]
})

// Max retard jours
const maxRetardJours = computed(() => {
  if (rawActionsEnRetard.value.length === 0) return 0
  return Math.max(...rawActionsEnRetard.value.map(a => a.retardJours || 0))
})

// Secteurs impactés
const secteursImpactes = computed(() => {
  const set = new Set(rawActionsEnRetard.value.map(a => a.secteur).filter(Boolean))
  return set.size
})

// Responsables notifiés
const responsablesNotifies = computed(() => {
  const set = new Set(rawActionsEnRetard.value.map(a => a.responsable).filter(Boolean))
  return set.size
})

// Points forts et point de vigilance du radar thématique (calculés dynamiquement)
const radarPointsForts = computed(() => {
  if (!radarLabels.value.length || !radarScores.value.length) return 'Données en cours...'
  const items = radarLabels.value.map((label, idx) => ({ label, score: radarScores.value[idx] || 0 }))
  const sorted = [...items].sort((a, b) => b.score - a.score)
  const top = sorted.slice(0, 2).filter(i => i.score > 0)
  if (!top.length) return 'Données en cours...'
  return top.map(i => `${i.label} (${i.score}%)`).join(', ')
})

const radarVigilance = computed(() => {
  if (!radarLabels.value.length || !radarScores.value.length) return 'Aucun'
  const items = radarLabels.value.map((label, idx) => ({ label, score: radarScores.value[idx] || 0 }))
  const sorted = [...items].sort((a, b) => a.score - b.score)
  const low = sorted.slice(0, 1)
  if (!low.length) return 'Aucun'
  return `${low[0].label} (${low[0].score}%)`
})
</script>


<template>
  <div style="display: flex; flex-direction: column; gap: 1.5rem;" class="page-anim">

    <!-- ===================================================================== -->
    <!-- BANDEAU D'EN-TÊTE : CONCEPTION BDD & PILOTAGE STRATÉGIQUE              -->
    <!-- ===================================================================== -->
    <div
      style="
        background: linear-gradient(135deg, rgba(0, 61, 77, 0.9) 0%, rgba(0, 28, 36, 0.95) 100%);
        border-radius: var(--radius-lg);
        padding: 1.5rem 2rem;
        border: 1px solid var(--card-border);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1.25rem;
      "
    >
      <div>
        <!-- Badges d'identification du portail -->
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
          <span
            style="
              background: rgba(0, 201, 150, 0.15);
              color: var(--color-primary);
              border: 1px solid rgba(0, 201, 150, 0.3);
              font-size: 0.72rem;
              font-weight: 800;
              padding: 3px 10px;
              border-radius: 20px;
              letter-spacing: 0.8px;
              text-transform: uppercase;
            "
          >
            Dashboard HSE Analytics
          </span>
          <span style="color: var(--text-dim); font-size: 0.8rem;">•</span>
          <span style="font-size: 0.8rem; color: var(--color-accent-light); font-weight: 600;">
            Site CIPI ACTIA Tunisie
          </span>
        </div>
        <!-- Titre principal du dashboard -->
        <h1 style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
          Tableau de Bord & Indicateurs de Performance HSE
        </h1>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin-top: 4px;">
          Indicateurs clés de performance et suivi opérationnel des plans d'action sécurité & environnement.
        </p>
      </div>

      <!-- Boutons d'actions rapides de l'en-tête -->
      <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
        <!-- Bouton Définir un Nouveau KPI (Studio) : ouvre la modale KpiDefinitionModal -->
        <button
          @click="showKpiModal = true"
          style="
            background: linear-gradient(135deg, rgba(0, 201, 150, 0.25) 0%, rgba(56, 189, 248, 0.25) 100%);
            border: 1.5px solid var(--color-primary);
            color: #ffffff;
            padding: 8px 18px;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            box-shadow: 0 0 16px rgba(0, 201, 150, 0.35);
            transition: all 0.2s ease;
          "
        >
          <Sparkles :size="16" color="var(--color-primary)" />
          <span>+ Définir un Nouveau KPI</span>
        </button>

        <!-- Bouton Refresh : déclenche l'actualisation visuelle des données -->
        <button
          @click="handleRefreshSnapshots"
          :disabled="isRefreshing"
          style="
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
            border: none;
            color: #001c24;
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(0, 201, 150, 0.3);
          "
        >
          <RefreshCw :size="15" :class="{ 'spin-anim': isRefreshing }" />
          {{ isRefreshing ? 'Actualisation...' : 'Actualiser les Données' }}
        </button>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- BARRE DE FILTRES DE DATE                                               -->
    <!-- ===================================================================== -->
    <div
      class="glass-card"
      style="
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
        border: 1px solid rgba(0, 201, 150, 0.2);
      "
    >
      <div style="display: flex; align-items: center; gap: 6px; color: var(--color-primary); font-weight: 800; font-size: 0.82rem;">
        <Calendar :size="16" />
        <span>Filtrer par période</span>
      </div>

      <!-- Filtre par Année -->
      <div style="display: flex; align-items: center; gap: 6px;">
        <label style="font-size: 0.78rem; color: var(--text-muted); font-weight: 700;">Année :</label>
        <select
          v-model="filterYear"
          @change="applyDateFilters"
          class="form-input"
          style="background: rgba(0,28,36,0.9); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 6px 10px; border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 600; cursor: pointer; min-width: 90px;"
        >
          <option :value="null">Toutes</option>
          <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>

      <!-- Filtre Date de Début -->
      <div style="display: flex; align-items: center; gap: 6px;">
        <label style="font-size: 0.78rem; color: var(--text-muted); font-weight: 700;">Du :</label>
        <input
          v-model="filterDateDebut"
          @keyup.enter="applyDateFilters"
          type="date"
          class="form-input"
          style="background: rgba(0,28,36,0.9); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 6px 10px; border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 600; cursor: pointer;"
        />
      </div>

      <!-- Filtre Date de Fin -->
      <div style="display: flex; align-items: center; gap: 6px;">
        <label style="font-size: 0.78rem; color: var(--text-muted); font-weight: 700;">Au :</label>
        <input
          v-model="filterDateFin"
          @keyup.enter="applyDateFilters"
          type="date"
          class="form-input"
          style="background: rgba(0,28,36,0.9); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 6px 10px; border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 600; cursor: pointer;"
        />
      </div>

      <!-- Boutons Appliquer / Réinitialiser -->
      <button
        @click="applyDateFilters"
        style="background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%); border: none; color: #001c24; padding: 7px 16px; border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 5px;"
      >
        <Filter :size="14" />
        Appliquer
      </button>

      <button
        v-if="filterYear || filterDateDebut || filterDateFin"
        @click="resetDateFilters"
        style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: var(--text-muted); padding: 6px 12px; border-radius: var(--radius-sm); font-size: 0.78rem; font-weight: 700; cursor: pointer;"
      >
        Réinitialiser
      </button>

      <!-- Label du filtre actif -->
      <span style="margin-left: auto; font-size: 0.75rem; color: var(--text-dim); font-weight: 600;">
        📊 {{ filterLabel }}
      </span>
    </div>

    <!-- ===================================================================== -->
    <!-- BANDEAU SUPÉRIEUR (SCORECARDS DE SYNTHÈSE STRATÉGIQUE)                 -->
    <!-- ===================================================================== -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem;">
      
      <!-- CARTE 1 : Taux de Fréquence (TF) du mois en cours -->
      <div class="glass-card scorecard-card" style="padding: 1.25rem 1.4rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <span style="font-size: 0.76rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">
              Taux de Fréquence (TF)
            </span>
            <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">
              Mois en cours ({{ moisCourant }})
            </div>
          </div>
          <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(0,201,150,0.12); color: var(--color-primary); display: flex; align-items: center; justify-content: center;">
            <Activity :size="20" />
          </div>
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 12px;">
          <div style="font-size: 2.1rem; font-weight: 800; color: #ffffff; font-family: var(--font-mono); letter-spacing: -1px;">
            {{ tfCourant.toFixed(2) }}
          </div>
          <span style="font-size: 0.75rem; color: var(--text-dim); font-weight: 600;">accidents / 10⁶ h</span>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06);">
          <span :style="{ color: tfVariation <= 0 ? '#10b981' : '#ef4444' }" style="display: flex; align-items: center; gap: 4px; font-size: 0.74rem; font-weight: 700;">
            <TrendingDown v-if="tfVariation <= 0" :size="14" />
            <TrendingUp v-else :size="14" />
            {{ tfVariation >= 0 ? '+' : '' }}{{ tfVariation.toFixed(2) }} vs mois préc.
          </span>
          <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 6px;">
            Cible &le; {{ targetTF }}
          </span>
        </div>
      </div>

      <!-- CARTE 2 : Taux de Conformité Global de la dernière tournée -->
      <div class="glass-card scorecard-card" style="padding: 1.25rem 1.4rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <span style="font-size: 0.76rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">
              Conformité Tournée
            </span>
            <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">
              Dernière tournée FGSI-010A
            </div>
          </div>
          <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(168, 224, 99, 0.15); color: var(--color-accent-light); display: flex; align-items: center; justify-content: center;">
            <ShieldCheck :size="20" />
          </div>
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 12px;">
          <div style="font-size: 2.1rem; font-weight: 800; color: var(--color-accent-light); font-family: var(--font-mono); letter-spacing: -1px;">
            {{ conformiteDerniereTournee.toFixed(1) }} %
          </div>
          <span style="font-size: 0.75rem; color: var(--text-dim); font-weight: 600;">{{ totalAudits }} fiches</span>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06);">
          <span :style="{ color: conformiteVariation >= 0 ? 'var(--color-accent-light)' : '#ef4444' }" style="display: flex; align-items: center; gap: 4px; font-size: 0.74rem; font-weight: 700;">
            <TrendingUp v-if="conformiteVariation >= 0" :size="14" />
            <TrendingDown v-else :size="14" />
            {{ conformiteVariation >= 0 ? '+' : '' }}{{ conformiteVariation.toFixed(1) }}% vs précédente
          </span>
          <span style="background: rgba(0, 201, 150, 0.12); color: var(--color-primary); font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 6px;">
            Moy. {{ avgConformite.toFixed(1) }}%
          </span>
        </div>
      </div>

      <!-- CARTE 3 : Nombre d'actions en retard (EN SURBRILLANCE ROUGE VIF AVEC ANIMATION) -->
      <div
        class="glass-card scorecard-card alert-card-pulsing"
        style="
          padding: 1.25rem 1.4rem;
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.18) 0%, rgba(153, 27, 27, 0.28) 100%);
          border: 1px solid #ef4444;
          box-shadow: 0 0 20px rgba(239, 68, 68, 0.35);
        "
      >
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <span style="font-size: 0.76rem; font-weight: 800; color: #fca5a5; text-transform: uppercase; letter-spacing: 0.5px;">
              Actions En Retard
            </span>
            <div style="font-size: 0.72rem; color: #fecaca; margin-top: 2px; font-weight: 600;">
              Échéance dépassée
            </div>
          </div>
          <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(239, 68, 68, 0.3); color: #ef4444; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(239, 68, 68, 0.5);">
            <AlertOctagon :size="20" />
          </div>
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 12px;">
          <div style="font-size: 2.1rem; font-weight: 800; color: #ffffff; font-family: var(--font-mono); letter-spacing: -1px; text-shadow: 0 0 10px rgba(239,68,68,0.7);">
            {{ actionsEnRetard }}
          </div>
          <span style="font-size: 0.75rem; color: #fca5a5; font-weight: 700;">actions critiques</span>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(239,68,68,0.25);">
          <span style="display: flex; align-items: center; gap: 4px; font-size: 0.74rem; color: #fca5a5; font-weight: 700;">
            <Clock :size="14" /> Dépassement max : {{ maxRetardJours }}j
          </span>
          <span v-if="actionsEnRetard > 0" style="background: #ef4444; color: #fff; font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 6px; letter-spacing: 0.4px;">
            URGENT
          </span>
        </div>
      </div>

      <!-- CARTE 4 : Jours sans accident (Compteur d'accidentologie) -->
      <div
        class="glass-card scorecard-card"
        style="
          padding: 1.25rem 1.4rem;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(0, 32, 42, 0.85) 100%);
          border: 1px solid rgba(16, 185, 129, 0.35);
        "
      >
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <span style="font-size: 0.76rem; font-weight: 800; color: #6ee7b7; text-transform: uppercase; letter-spacing: 0.5px;">
              Jours Sans Accident
            </span>
            <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">
              Compteur d'Accidentologie
            </div>
          </div>
          <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(16, 185, 129, 0.2); color: #10b981; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(16, 185, 129, 0.4);">
            <Award :size="20" />
          </div>
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 12px;">
          <div style="font-size: 2.1rem; font-weight: 800; color: #10b981; font-family: var(--font-mono); letter-spacing: -1px;">
            {{ joursSansAccident }}
          </div>
          <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Jours consécutifs</span>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06);">
          <span style="font-size: 0.74rem; color: var(--text-muted); font-weight: 600;">
            {{ dernierAccidentDate || 'Aucun enregistrement' }}
          </span>
          <span style="background: rgba(168, 224, 99, 0.15); color: var(--color-accent-light); font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 6px;">
            Record : 365 j
          </span>
        </div>
      </div>

    </div>

    <!-- ===================================================================== -->
    <!-- SECTION : MES INDICATEURS PERSONNALISÉS (STUDIO DE DÉFINITION DE KPIS) -->
    <!-- ===================================================================== -->
    <div
      class="glass-card"
      style="
        padding: 1.5rem 1.75rem;
        background: linear-gradient(135deg, rgba(0, 36, 48, 0.9) 0%, rgba(0, 20, 26, 0.95) 100%);
        border: 1px solid rgba(0, 201, 150, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      "
    >
      <!-- En-tête de la section Studio KPI -->
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span
              style="
                background: linear-gradient(135deg, rgba(0, 201, 150, 0.25) 0%, rgba(56, 189, 248, 0.2) 100%);
                border: 1px solid rgba(0, 201, 150, 0.4);
                color: var(--color-primary);
                font-size: 0.72rem;
                font-weight: 800;
                padding: 3px 10px;
                border-radius: 20px;
                letter-spacing: 0.6px;
                text-transform: uppercase;
                display: flex;
                align-items: center;
                gap: 5px;
              "
            >
              <Sparkles :size="12" /> Studio KPI & Personnalisation
            </span>
            <span style="color: var(--text-dim); font-size: 0.8rem;">•</span>
            <span style="font-size: 0.78rem; color: #38bdf8; font-weight: 700;">
              Croisement de 2 ou 3 types de données
            </span>
          </div>
          <h2 style="font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
            Mes Indicateurs Personnalisés Définis par l'Utilisateur
          </h2>
          <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 2px;">
            Visualisations sur-mesure : sélectionnez votre type de graphique (courbe, barres, donut, radar) et croisez 2 ou 3 types de données HSE.
          </p>
        </div>

        <!-- Bouton pour ouvrir la modale de création -->
        <button
          @click="showKpiModal = true"
          style="
            background: linear-gradient(135deg, var(--color-primary) 0%, #0284c7 100%);
            border: none;
            color: #001c24;
            padding: 9px 18px;
            border-radius: var(--radius-sm);
            font-size: 0.84rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(0, 201, 150, 0.35);
            transition: all 0.2s ease;
          "
        >
          <Plus :size="16" stroke-width="3" />
          <span>Définir un Nouveau KPI</span>
        </button>
      </div>

      <!-- Grille des widgets de KPIs Personnalisés enregistrés -->
      <div
        v-if="customKpis.length > 0"
        style="display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 1.5rem;"
      >
        <div
          v-for="kpi in customKpis"
          :key="kpi.id"
          class="glass-card"
          style="
            background: rgba(0, 20, 26, 0.75);
            border: 1px solid rgba(0, 201, 150, 0.2);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
          "
        >
          <!-- Haut de la carte : Titre, Badges des données croisées & Action de suppression -->
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 8px;">
              <div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <h3 style="font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                    {{ kpi.title }}
                  </h3>
                  <span
                    style="
                      background: rgba(0, 201, 150, 0.15);
                      color: var(--color-primary);
                      font-size: 0.68rem;
                      font-weight: 800;
                      padding: 2px 7px;
                      border-radius: 6px;
                      text-transform: uppercase;
                    "
                  >
                    Format {{ kpi.chartType }}
                  </span>
                </div>
                <p style="font-size: 0.76rem; color: var(--text-dim); margin-top: 3px;">
                  {{ kpi.description }}
                </p>
              </div>

              <!-- Bouton supprimer ce KPI personnalisé -->
              <button
                @click="handleDeleteCustomKpi(kpi.id)"
                title="Supprimer ce KPI personnalisé"
                style="
                  background: rgba(239, 68, 68, 0.1);
                  border: 1px solid rgba(239, 68, 68, 0.25);
                  color: #ef4444;
                  width: 32px;
                  height: 32px;
                  border-radius: 8px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  cursor: pointer;
                  transition: all 0.2s;
                "
              >
                <Trash2 :size="15" />
              </button>
            </div>

            <!-- Badges des 2 ou 3 types de données croisés -->
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
              <span
                v-for="m in kpi.metrics"
                :key="m.id"
                :style="{
                  color: m.color,
                  borderColor: `${m.color}55`,
                  background: `${m.color}15`
                }"
                style="font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; border-width: 1px; border-style: solid;"
              >
                ● {{ m.label }} ({{ m.unit }})
              </span>
            </div>

            <!-- Rendu du graphique selon le type choisi -->
            <div style="height: 250px; position: relative;">
              <!-- Cas Scorecard Card -->
              <div
                v-if="kpi.chartType === 'card'"
                style="
                  height: 100%;
                  display: flex;
                  flex-direction: column;
                  justify-content: center;
                  align-items: center;
                  gap: 10px;
                  background: rgba(0, 0, 0, 0.25);
                  border-radius: 10px;
                "
              >
                <div style="font-size: 0.8rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase;">
                  Valeur Actuelle
                </div>
                <div style="font-size: 3rem; font-weight: 800; color: var(--color-primary); font-family: var(--font-mono);">
                  {{ kpi.metrics[0]?.monthlyData?.slice(-1)[0] || '1.82' }}
                </div>
                <div style="font-size: 0.82rem; color: #fff; font-weight: 700;">
                  {{ kpi.metrics[0]?.label }}
                </div>
              </div>

              <!-- Cas Line Chart -->
              <Line
                v-else-if="kpi.chartType === 'line'"
                :data="kpi.chartData"
                :options="kpi.chartOptions"
              />

              <!-- Cas Bar Chart -->
              <Bar
                v-else-if="kpi.chartType === 'bar'"
                :data="kpi.chartData"
                :options="kpi.chartOptions"
              />

              <!-- Cas Doughnut Chart -->
              <Doughnut
                v-else-if="kpi.chartType === 'doughnut'"
                :data="kpi.chartData"
                :options="kpi.chartOptions"
              />

              <!-- Cas Radar Chart -->
              <Radar
                v-else-if="kpi.chartType === 'radar'"
                :data="kpi.chartData"
                :options="kpi.chartOptions"
              />
            </div>
          </div>

          <!-- Pied de carte : axe d'agrégation et date de création -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.72rem; color: var(--text-dim);">
            <span>Axe : <strong style="color: #cbd5e1; text-transform: capitalize;">{{ kpi.periodicity === 'monthly' ? 'Mensuel' : kpi.periodicity === 'weekly' ? 'Hebdomadaire' : 'Par Secteur' }}</strong></span>
            <span>{{ kpi.metrics.length }} types de données croisés · Créé le {{ kpi.createdAt }}</span>
          </div>
        </div>
      </div>

      <!-- État vide si aucun KPI personnalisé n'a encore été défini -->
      <div
        v-else
        style="
          text-align: center;
          padding: 3rem 1.5rem;
          background: rgba(0, 20, 26, 0.4);
          border: 1px dashed rgba(0, 201, 150, 0.3);
          border-radius: var(--radius-md);
        "
      >
        <Sparkles :size="36" color="var(--color-primary)" style="margin: 0 auto 12px;" />
        <h3 style="font-size: 1.1rem; font-weight: 800; color: #fff; margin-bottom: 6px;">
          Aucun KPI personnalisé configuré pour le moment
        </h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); max-width: 520px; margin: 0 auto 1.25rem;">
          Cliquez sur <strong>« Définir un Nouveau KPI »</strong> pour choisir votre graphique et croiser 2 ou 3 types de données (TF, IF, TG, accidents, conformité).
        </p>
        <button
          @click="showKpiModal = true"
          style="
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
            border: none;
            color: #001c24;
            padding: 9px 20px;
            border-radius: var(--radius-sm);
            font-size: 0.84rem;
            font-weight: 800;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
          "
        >
          <Plus :size="16" />
          <span>Lancer le Studio KPI</span>
        </button>
      </div>

    </div>

    <!-- ===================================================================== -->
    <!-- ZONE CENTRALE : 2 COLONNES (ÉVOLUTION À GAUCHE, THÉMATIQUE À DROITE)   -->
    <!-- ===================================================================== -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 1.5rem;">
      
      <!-- ========================================== -->
      <!-- ZONE CENTRALE GAUCHE : GRAPHIQUES ÉVOLUTION -->
      <!-- ========================================== -->
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        
        <!-- Graphique G1 : Courbe mensuelle combinée TF & IF vs Target 2.5 -->
        <div class="glass-card" style="padding: 1.4rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
              <div style="font-size: 0.74rem; font-weight: 800; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.5px;">
                Tendance Fréquence Annuelle
              </div>
              <h3 style="font-size: 1.05rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                <Activity :size="18" color="var(--color-primary)" />
                Courbe Combinée : TF & IF vs Objectif Target 2,5
              </h3>
            </div>
            <span style="background: rgba(0, 201, 150, 0.1); border: 1px solid rgba(0, 201, 150, 0.25); color: var(--color-primary); font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
              Indicateur Fréquence
            </span>
          </div>
          <div style="height: 250px;">
            <Line :data="monthlyKpiData" :options="monthlyKpiOptions" />
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.75rem; color: var(--text-dim); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
            <span>TF {{ moisCourant }} : <strong style="color: var(--color-primary)">{{ tfCourant.toFixed(2) }}</strong></span>
            <span>Target Maximale : <strong style="color: #ef4444">{{ targetTF }}</strong></span>
            <span>Statut : <strong :style="{ color: tfCourant <= targetTF ? '#10b981' : '#ef4444' }">{{ tfCourant <= targetTF ? 'Conforme à la Cible' : 'Non conforme' }}</strong></span>
          </div>
        </div>

        <!-- Graphique G2 : Évolution du Taux de Conformité au fil des semaines -->
        <div class="glass-card" style="padding: 1.4rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
              <div style="font-size: 0.74rem; font-weight: 800; color: var(--color-accent-light); text-transform: uppercase; letter-spacing: 0.5px;">
                Suivi Hebdomadaire Terrain
              </div>
              <h3 style="font-size: 1.05rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                <TrendingUp :size="18" color="var(--color-accent-light)" />
                Évolution du Taux de Conformité au fil des Semaines
              </h3>
            </div>
            <span style="background: rgba(168, 224, 99, 0.1); border: 1px solid rgba(168, 224, 99, 0.25); color: var(--color-accent-light); font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
              7 Dernières Semaines
            </span>
          </div>
          <div style="height: 220px;">
            <Line :data="weeklyConformiteData" :options="weeklyConformiteOptions" />
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.75rem; color: var(--text-dim); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
            <span>Moyenne Période : <strong style="color: #fff">{{ avgConformite.toFixed(1) }}%</strong></span>
            <span>{{ totalAudits }} soumissions dans la période</span>
          </div>
        </div>

      </div>

      <!-- ========================================== -->
      <!-- ZONE CENTRALE DROITE : ANALYSES THÉMATIQUES -->
      <!-- ========================================== -->
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        
        <!-- Graphique D1 : Radar des 7 Thématiques HSE -->
        <div class="glass-card" style="padding: 1.4rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div>
              <div style="font-size: 0.74rem; font-weight: 800; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.5px;">
                Cartographie des Risques
              </div>
              <h3 style="font-size: 1.05rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                <Layers :size="18" color="var(--color-primary)" />
                Radar des 7 Thématiques d'Audit & Tournées
              </h3>
            </div>
            <span style="background: rgba(0, 201, 150, 0.1); border: 1px solid rgba(0, 201, 150, 0.25); color: var(--color-primary); font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
              Grille FGSI-001/010
            </span>
          </div>
          <div style="height: 250px;">
            <Radar :data="radarThematiqueData" :options="radarThematiqueOptions" />
          </div>
          <div style="margin-top: 10px; font-size: 0.74rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; display: flex; justify-content: space-between;">
            <span style="color: #10b981;">Points forts : {{ radarPointsForts }}</span>
            <span style="color: #ef4444;">Point de vigilance : {{ radarVigilance }}</span>
          </div>
        </div>

        <!-- Graphique D2 : Donut du Statut des Actions Correctives -->
        <div class="glass-card" style="padding: 1.4rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div>
              <div style="font-size: 0.74rem; font-weight: 800; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.5px;">
                Résolution des Écarts
              </div>
              <h3 style="font-size: 1.05rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                <Award :size="18" color="#60a5fa" />
                Donut du Statut des Actions (Soldée, En cours, En retard)
              </h3>
            </div>
            <span style="background: rgba(96, 165, 250, 0.1); border: 1px solid rgba(96, 165, 250, 0.25); color: #60a5fa; font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
              Total : {{ totalActions }} Actions
            </span>
          </div>
          <div style="height: 220px; position: relative;">
            <Doughnut :data="actionsDonutData" :options="actionsDonutOptions" />
            <!-- Compteur central en pourcentage de résolution -->
            <div
              style="
                position: absolute;
                top: 43%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                pointer-events: none;
              "
            >
              <div style="font-size: 1.6rem; font-weight: 800; color: #fff; font-family: var(--font-mono);">{{ pctSoldee }}%</div>
              <div style="font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700;">Soldées</div>
            </div>
          </div>
          <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 10px; font-size: 0.74rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
            <span style="color: #10b981; font-weight: 700;">● {{ actionsSoldee }} Soldées</span>
            <span style="color: #3b82f6; font-weight: 700;">● {{ actionsEnCours }} En cours</span>
            <span style="color: #ef4444; font-weight: 700;">● {{ actionsRetardCount }} En retard</span>
            <span style="color: #f59e0b; font-weight: 700;">● {{ actionsNonEngagee }} Non engagées</span>
          </div>
        </div>

      </div>

    </div>

    <!-- ===================================================================== -->
    <!-- BAS DE PAGE : TABLEAU OPÉRATIONNEL DES ACTIONS EN RETARD               -->
    <!-- ===================================================================== -->
    <div
      class="glass-card"
      style="
        padding: 1.5rem;
        border: 1px solid rgba(239, 68, 68, 0.35);
        background: linear-gradient(180deg, rgba(0, 32, 42, 0.85) 0%, rgba(20, 10, 15, 0.85) 100%);
      "
    >
      <!-- En-tête du tableau opérationnel avec titre & filtres -->
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="background: rgba(239, 68, 68, 0.2); color: #ef4444; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 6px; border: 1px solid rgba(239,68,68,0.3);">
              PRIORITÉ 1
            </span>
            <h3 style="font-size: 1.15rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px;">
              <AlertCircle :size="20" color="#ef4444" />
              Tableau Opérationnel : Actions Correctives en Retard
            </h3>
          </div>
          <p style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
            Filtrage dynamique par secteur et responsable · Actions issues des formulaires FGSI-001 et FGSI-010
          </p>
        </div>

        <!-- Zone des Filtres dynamiques -->
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
          
          <!-- Filtre Secteur -->
          <div style="position: relative;">
            <select
              v-model="selectedSecteur"
              class="form-input"
              style="
                background: rgba(0, 28, 36, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #fff;
                padding: 7px 12px;
                border-radius: var(--radius-sm);
                font-size: 0.82rem;
                font-weight: 600;
                cursor: pointer;
              "
            >
              <option value="all">Tous les secteurs</option>
              <option v-for="s in secteursList" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <!-- Filtre Responsable -->
          <div style="position: relative;">
            <select
              v-model="selectedResponsable"
              class="form-input"
              style="
                background: rgba(0, 28, 36, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #fff;
                padding: 7px 12px;
                border-radius: var(--radius-sm);
                font-size: 0.82rem;
                font-weight: 600;
                cursor: pointer;
              "
            >
              <option value="all">Tous les responsables</option>
              <option v-for="r in responsablesList" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <!-- Recherche textuelle -->
          <div style="position: relative;">
            <Search :size="14" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-dim);" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher action..."
              class="form-input"
              style="
                background: rgba(0, 28, 36, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #fff;
                padding: 7px 12px 7px 30px;
                border-radius: var(--radius-sm);
                font-size: 0.82rem;
                width: 170px;
              "
            />
          </div>

          <!-- Bouton de réinitialisation des filtres si actifs -->
          <button
            v-if="selectedSecteur !== 'all' || selectedResponsable !== 'all' || searchQuery !== ''"
            @click="() => { selectedSecteur = 'all'; selectedResponsable = 'all'; searchQuery = '' }"
            style="
              background: rgba(255, 255, 255, 0.08);
              border: 1px solid rgba(255, 255, 255, 0.15);
              color: var(--text-muted);
              padding: 6px 10px;
              border-radius: var(--radius-sm);
              font-size: 0.75rem;
              cursor: pointer;
            "
          >
            Réinitialiser
          </button>
        </div>
      </div>

      <!-- TABLEAU DES ACTIONS EN RETARD -->
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem;">
          <thead>
            <tr style="border-bottom: 2px solid rgba(255, 255, 255, 0.08); color: var(--text-muted); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.6px;">
              <th style="padding: 10px 12px;">Réf & Formulaire</th>
              <th style="padding: 10px 12px;">Secteur</th>
              <th style="padding: 10px 12px;">Constat Non-Conformité</th>
              <th style="padding: 10px 12px;">Action Corrective</th>
              <th style="padding: 10px 12px;">Responsable</th>
              <th style="padding: 10px 12px;">Échéance / Retard</th>
              <th style="padding: 10px 12px; text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in filteredActions"
              :key="item.id"
              style="
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
                transition: background 0.15s ease;
              "
              class="table-row-hover"
            >
              <!-- Réf & Source -->
              <td style="padding: 12px; font-family: var(--font-mono); font-weight: 700; color: #fff;">
                <div>{{ item.ref }}</div>
                <div style="font-size: 0.68rem; color: var(--text-dim); font-family: var(--font-sans); font-weight: 500;">
                  {{ item.source }}
                </div>
              </td>

              <!-- Secteur -->
              <td style="padding: 12px; color: #e2e8f0; font-weight: 600;">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <MapPin :size="14" color="var(--color-primary)" />
                  <span>{{ item.secteur }}</span>
                </div>
              </td>

              <!-- Constat Non-Conforme -->
              <td style="padding: 12px; color: #fca5a5; max-width: 250px; line-height: 1.35;">
                {{ item.constat }}
              </td>

              <!-- Action Corrective Engagée -->
              <td style="padding: 12px; color: #e2e8f0; max-width: 260px; line-height: 1.35; font-weight: 500;">
                {{ item.action }}
              </td>

              <!-- Responsable désigné -->
              <td style="padding: 12px; color: #cbd5e1; font-weight: 600;">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <User :size="14" color="#60a5fa" />
                  <span>{{ item.responsable }}</span>
                </div>
              </td>

              <!-- Échéance & Dépassement en jours -->
              <td style="padding: 12px;">
                <div style="display: flex; flex-direction: column; gap: 3px;">
                  <span style="color: var(--text-muted); font-size: 0.78rem;">Prévu : {{ item.delai }}</span>
                  <span
                    style="
                      background: rgba(239, 68, 68, 0.2);
                      color: #ef4444;
                      border: 1px solid rgba(239, 68, 68, 0.4);
                      font-size: 0.72rem;
                      font-weight: 800;
                      padding: 2px 6px;
                      border-radius: 4px;
                      display: inline-block;
                      width: fit-content;
                    "
                  >
                    +{{ item.retardJours }} jours de retard
                  </span>
                </div>
              </td>

              <!-- Bouton Relancer -->
              <td style="padding: 12px; text-align: right;">
                <button
                  style="
                    background: rgba(239, 68, 68, 0.15);
                    border: 1px solid rgba(239, 68, 68, 0.4);
                    color: #fca5a5;
                    padding: 5px 10px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 700;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    transition: all 0.2s ease;
                  "
                  title="Relancer le responsable par notification"
                >
                  <span>Relancer</span>
                  <ChevronRight :size="13" />
                </button>
              </td>
            </tr>

            <!-- Ligne d'état si aucun résultat ne correspond aux filtres appliqués -->
            <tr v-if="filteredActions.length === 0">
              <td colspan="7" style="padding: 2rem; text-align: center; color: var(--text-dim);">
                <CheckCircle2 :size="28" color="#10b981" style="margin: 0 auto 8px;" />
                <div style="font-weight: 700; color: #fff;">Aucune action en retard ne correspond à ces critères.</div>
                <div style="font-size: 0.8rem; margin-top: 2px;">Toutes les actions du filtre sont à jour.</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- FOOTER TABLEAU : COMPTEUR D'ACTIONS ET DE RESPONSABLES -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 0.78rem; color: var(--text-dim);">
        <div>
          Affichage de <strong style="color: #fff">{{ filteredActions.length }}</strong> action(s) en retard sur <strong style="color: #fff">{{ rawActionsEnRetard.length }}</strong> au total.
        </div>
        <div style="display: flex; gap: 12px;">
          <span>Secteurs impactés : <strong style="color: #fca5a5">{{ secteursImpactes }}</strong></span>
          <span>Responsables notifiés : <strong style="color: #fca5a5">{{ responsablesNotifies }}</strong></span>
        </div>
      </div>
    </div>

    <!-- MODAL DU STUDIO DE DÉFINITION DE KPIS -->
    <KpiDefinitionModal
      v-if="showKpiModal"
      @close="showKpiModal = false"
      @save-kpi="handleSaveCustomKpi"
      @show-toast="(msg, type) => emit('showToast', msg, type)"
    />

  </div>
</template>

<style scoped>
/* Effets de survol sur les cartes de scorecards */
.scorecard-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.scorecard-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
}

/* Survol des lignes du tableau opérationnel */
.table-row-hover:hover {
  background: rgba(255, 255, 255, 0.025);
}

/* Animation de rotation de l'icône de rafraîchissement */
.spin-anim {
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Animation d'impulsion lumineuse (Glow) pour les alertes critiques */
.alert-card-pulsing {
  animation: pulseGlow 3s infinite ease-in-out;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 18px rgba(239, 68, 68, 0.3);
    border-color: rgba(239, 68, 68, 0.7);
  }
  50% {
    box-shadow: 0 0 28px rgba(239, 68, 68, 0.55);
    border-color: rgba(239, 68, 68, 1);
  }
}
</style>
