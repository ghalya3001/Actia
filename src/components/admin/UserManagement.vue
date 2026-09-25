<!--
=============================================================================
Composant : UserManagement.vue
Description : Module d'administration des utilisateurs et validation des comptes (RBAC).
Design : Harmonisé à 100% avec le design system du Dashboard HSE (HseDashboard.vue) :
         - Bandeau d'en-tête dégradé profond avec badges néons et boutons de contrôle.
         - Scorecards exécutives avec typographie monospace, jauges et compteurs.
         - Panneau opérationnel glassmorphism sombre avec filtres intégrés.
         - Filtre par plage de dates (« Du » et « Au ») avec support de la date unique.
         - Tableau moderne aux bordures subtiles et rangées interactives.
         - Modales sombres glassmorphism avec badges et bannières d'avertissement.
=============================================================================
-->

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Users,
  Clock,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  ShieldCheck,
  UserMinus,
  Search,
  Calendar,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Info,
  RotateCcw,
  Mail,
  AlertTriangle,
  X,
  Check,
  ChevronRight,
  Layers,
  Award
} from 'lucide-vue-next'

const props = defineProps({
  token: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['showToast'])

// --- États réactifs statistiques ---
const stats = ref({
  total_users: 0,
  pending_users: 0,
  approved_users: 0,
  rejected_users: 0,
  suspended_users: 0
})

// --- États réactifs de liste et filtrage ---
const users = ref([])
const isLoading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('ALL')
const selectedRole = ref('ALL')
const dateFrom = ref('')
const dateTo = ref('')

// --- Modales d'action ---
const showRejectModal = ref(false)
const userToReject = ref(null)
const rejectionReason = ref('')
const isRejecting = ref(false)

const showSuspendModal = ref(false)
const userToSuspend = ref(null)
const isSuspending = ref(false)

const showRoleModal = ref(false)
const userToChangeRole = ref(null)
const targetRole = ref('ADMIN')
const isChangingRole = ref(false)

const API_ADMIN = window.location.origin + '/api/v1/admin'

/**
 * Indique si un ou plusieurs filtres personnalisés sont actifs.
 */
const hasActiveFilters = computed(() => {
  return (
    searchQuery.value.trim() !== '' ||
    selectedStatus.value !== 'ALL' ||
    selectedRole.value !== 'ALL' ||
    dateFrom.value !== '' ||
    dateTo.value !== ''
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
    return `Inscriptions du ${formatDateSimple(dateFrom.value)} uniquement.`
  }
  if (dateFrom.value && dateTo.value) {
    return `Période du ${formatDateSimple(dateFrom.value)} au ${formatDateSimple(dateTo.value)}.`
  }
  if (!dateFrom.value && dateTo.value) {
    return `Inscriptions jusqu'au ${formatDateSimple(dateTo.value)}.`
  }
  return null
})

/**
 * Récupère les compteurs statistiques globaux.
 */
const fetchStats = async () => {
  try {
    const res = await fetch(`${API_ADMIN}/stats`, {
      headers: { 'Authorization': `Bearer ${props.token}` }
    })
    if (res.ok) {
      stats.value = await res.json()
    }
  } catch (err) {
    console.error('Erreur chargement stats admin:', err)
  }
}

/**
 * Récupère la liste des utilisateurs depuis le backend avec tous les filtres actifs.
 */
const fetchUsers = async () => {
  isLoading.value = true
  try {
    let url = `${API_ADMIN}/users?`
    if (selectedStatus.value !== 'ALL') {
      url += `status=${selectedStatus.value}&`
    }
    if (selectedRole.value !== 'ALL') {
      url += `role=${selectedRole.value}&`
    }
    if (searchQuery.value.trim()) {
      url += `search=${encodeURIComponent(searchQuery.value.trim())}&`
    }
    if (dateFrom.value) {
      url += `date_from=${dateFrom.value}&`
    }
    if (dateTo.value) {
      url += `date_to=${dateTo.value}&`
    }

    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${props.token}` }
    })
    if (res.ok) {
      users.value = await res.json()
    } else {
      emit('showToast', 'Erreur lors du chargement des utilisateurs', 'error')
    }
  } catch (err) {
    emit('showToast', 'Impossible de joindre le serveur', 'error')
  } finally {
    isLoading.value = false
  }
}

/**
 * Réinitialise tous les filtres de recherche.
 */
const resetFilters = () => {
  searchQuery.value = ''
  selectedStatus.value = 'ALL'
  selectedRole.value = 'ALL'
  dateFrom.value = ''
  dateTo.value = ''
  fetchUsers()
}

/**
 * Réinitialise uniquement les filtres de date.
 */
const resetDateFilter = () => {
  dateFrom.value = ''
  dateTo.value = ''
  fetchUsers()
}

/**
 * Approuve un utilisateur en tant qu'utilisateur standard.
 */
const handleApprove = async (user) => {
  try {
    const res = await fetch(`${API_ADMIN}/users/${user.id}/approve`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${props.token}` }
    })
    if (res.ok) {
      emit('showToast', `Compte ${user.email} approuvé avec succès.`)
      await fetchStats()
      await fetchUsers()
    } else {
      const errData = await res.json()
      emit('showToast', errData.detail || 'Erreur lors de l\'approbation', 'error')
    }
  } catch (err) {
    emit('showToast', 'Erreur réseau', 'error')
  }
}

/**
 * Ouvre la modale pour renseigner le motif de rejet.
 */
const openRejectModal = (user) => {
  userToReject.value = user
  rejectionReason.value = ''
  showRejectModal.value = true
}

/**
 * Confirme le rejet du compte avec le motif saisi.
 */
const handleConfirmReject = async () => {
  if (!rejectionReason.value.trim()) {
    emit('showToast', 'Le motif de rejet est obligatoire.', 'error')
    return
  }
  isRejecting.value = true
  try {
    const res = await fetch(`${API_ADMIN}/users/${userToReject.value.id}/reject`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${props.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rejection_reason: rejectionReason.value.trim() })
    })
    if (res.ok) {
      emit('showToast', `Compte ${userToReject.value.email} rejeté.`)
      showRejectModal.value = false
      userToReject.value = null
      await fetchStats()
      await fetchUsers()
    } else {
      const errData = await res.json()
      emit('showToast', errData.detail || 'Erreur lors du rejet', 'error')
    }
  } catch (err) {
    emit('showToast', 'Erreur réseau', 'error')
  } finally {
    isRejecting.value = false
  }
}

/**
 * Ouvre la modale personnalisée de suspension de compte.
 */
const openSuspendModal = (user) => {
  userToSuspend.value = user
  showSuspendModal.value = true
}

/**
 * Confirme la suspension du compte via l'API.
 */
const handleConfirmSuspend = async () => {
  if (!userToSuspend.value) return
  isSuspending.value = true
  try {
    const res = await fetch(`${API_ADMIN}/users/${userToSuspend.value.id}/suspend`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${props.token}` }
    })
    if (res.ok) {
      emit('showToast', `Compte ${userToSuspend.value.email} suspendu avec succès.`)
      showSuspendModal.value = false
      userToSuspend.value = null
      await fetchStats()
      await fetchUsers()
    } else {
      const errData = await res.json()
      emit('showToast', errData.detail || 'Erreur lors de la suspension', 'error')
    }
  } catch (err) {
    emit('showToast', 'Erreur réseau', 'error')
  } finally {
    isSuspending.value = false
  }
}

/**
 * Ouvre la modale pour changer le rôle d'un utilisateur (USER <-> ADMIN).
 */
const openRoleModal = (user, newRole) => {
  userToChangeRole.value = user
  targetRole.value = newRole
  showRoleModal.value = true
}

/**
 * Confirme la mise à jour du rôle utilisateur via l'API.
 */
const handleConfirmChangeRole = async () => {
  if (!userToChangeRole.value) return
  isChangingRole.value = true
  try {
    if (userToChangeRole.value.status === 'PENDING') {
      await fetch(`${API_ADMIN}/users/${userToChangeRole.value.id}/approve`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${props.token}` }
      })
    }

    const res = await fetch(`${API_ADMIN}/users/${userToChangeRole.value.id}/role`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${props.token}`
      },
      body: JSON.stringify({ role: targetRole.value })
    })

    if (res.ok) {
      emit('showToast', `Le compte ${userToChangeRole.value.email} est désormais ${targetRole.value}.`)
      showRoleModal.value = false
      userToChangeRole.value = null
      await fetchUsers()
      await fetchStats()
    } else {
      const errData = await res.json()
      emit('showToast', errData.detail || 'Erreur lors du changement de rôle', 'error')
    }
  } catch (err) {
    emit('showToast', 'Erreur réseau', 'error')
  } finally {
    isChangingRole.value = false
  }
}

/**
 * Décompose une date ISO en objet lisible { date, time }.
 */
const formatDateTime = (dateStr) => {
  if (!dateStr) return { date: '-', time: '' }
  const d = new Date(dateStr)
  return {
    date: d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }),
    time: d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  }
}

onMounted(() => {
  fetchStats()
  fetchUsers()
})
</script>

<template>
  <div class="user-management-wrapper page-anim">
    
    <!-- ===================================================================== -->
    <!-- 1. BANDEAU D'EN-TÊTE SUPÉRIEUR (IDENTIQUE AU DASHBOARD HSE)            -->
    <!-- ===================================================================== -->
    <div class="dashboard-banner">
      <div>
        <div class="banner-tagline">
          <span class="badge-portal">
            <Sparkles :size="12" /> Administration RBAC
          </span>
          <span class="banner-bullet">•</span>
          <span class="banner-site">Site CIPI ACTIA Tunisie · Espace Gouvernance</span>
        </div>
        <h1 class="banner-title">
          Gestion des Utilisateurs & Contrôle d'Accès
        </h1>
        <p class="banner-subtitle">
          Supervisez les habilitations, validez les nouvelles inscriptions et pilotez les rôles d'accès à la plateforme HSE.
        </p>
      </div>

      <div class="banner-actions">
        <button
          @click="() => { fetchStats(); fetchUsers(); }"
          :disabled="isLoading"
          class="btn-dashboard-action"
          title="Recharger toutes les données d'administration"
        >
          <RefreshCw :size="15" :class="{ 'spin-anim': isLoading }" />
          <span>{{ isLoading ? 'Actualisation...' : 'Actualiser les Données' }}</span>
        </button>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- 2. SCORECARDS DE SYNTHÈSE STATISTIQUE (STYLE EXACT DASHBOARD HSE)     -->
    <!-- ===================================================================== -->
    <div class="scorecards-grid">
      
      <!-- CARTE 1 : Total Utilisateurs -->
      <div 
        class="glass-card scorecard-card"
        :class="{ 'card-active-border': selectedStatus === 'ALL' }"
        @click="() => { selectedStatus = 'ALL'; fetchUsers(); }"
      >
        <div class="card-top">
          <div>
            <span class="card-label">Total Utilisateurs</span>
            <div class="card-sublabel">Comptes enregistrés</div>
          </div>
          <div class="icon-wrapper icon-box-blue">
            <Users :size="20" />
          </div>
        </div>

        <div class="card-value-box">
          <div class="card-value font-mono">{{ stats.total_users }}</div>
          <span class="card-unit">comptes</span>
        </div>

        <div class="card-footer">
          <span class="footer-trend text-blue">
            Tous statuts confondus
          </span>
          <span class="badge-mini badge-mini-blue">Global</span>
        </div>
      </div>

      <!-- CARTE 2 : En attente (PENDING) - Surbriance alerte comme le dashboard -->
      <div 
        class="glass-card scorecard-card"
        :class="[
          stats.pending_users > 0 ? 'alert-card-pulsing' : '',
          selectedStatus === 'PENDING' ? 'card-active-border-amber' : ''
        ]"
        @click="() => { selectedStatus = 'PENDING'; fetchUsers(); }"
      >
        <div class="card-top">
          <div>
            <span class="card-label" :class="stats.pending_users > 0 ? 'text-amber-light' : ''">
              En attente de validation
            </span>
            <div class="card-sublabel" :class="stats.pending_users > 0 ? 'text-amber-dim' : ''">
              Validation requise
            </div>
          </div>
          <div class="icon-wrapper icon-box-amber">
            <Clock :size="20" />
          </div>
        </div>

        <div class="card-value-box">
          <div class="card-value font-mono text-amber" :class="{ 'glow-amber': stats.pending_users > 0 }">
            {{ stats.pending_users }}
          </div>
          <span class="card-unit" :class="stats.pending_users > 0 ? 'text-amber-light' : ''">
            à approuver
          </span>
        </div>

        <div class="card-footer" :style="stats.pending_users > 0 ? 'border-top-color: rgba(245,158,11,0.25);' : ''">
          <span class="footer-trend text-amber">
            <Clock :size="13" /> Action requise
          </span>
          <span class="badge-mini badge-mini-amber">
            {{ stats.pending_users > 0 ? 'À TRAITER' : 'À jour' }}
          </span>
        </div>
      </div>

      <!-- CARTE 3 : Comptes Approuvés (APPROVED) -->
      <div 
        class="glass-card scorecard-card card-green-accent"
        :class="{ 'card-active-border-green': selectedStatus === 'APPROVED' }"
        @click="() => { selectedStatus = 'APPROVED'; fetchUsers(); }"
      >
        <div class="card-top">
          <div>
            <span class="card-label text-green-light">Comptes Approuvés</span>
            <div class="card-sublabel">Accès autorisés</div>
          </div>
          <div class="icon-wrapper icon-box-green">
            <CheckCircle2 :size="20" />
          </div>
        </div>

        <div class="card-value-box">
          <div class="card-value font-mono text-green">{{ stats.approved_users }}</div>
          <span class="card-unit">actifs</span>
        </div>

        <div class="card-footer">
          <span class="footer-trend text-green">
            Opérationnels
          </span>
          <span class="badge-mini badge-mini-green">Validés</span>
        </div>
      </div>

      <!-- CARTE 4 : Comptes Rejetés (REJECTED) -->
      <div 
        class="glass-card scorecard-card"
        :class="{ 'card-active-border-red': selectedStatus === 'REJECTED' }"
        @click="() => { selectedStatus = 'REJECTED'; fetchUsers(); }"
      >
        <div class="card-top">
          <div>
            <span class="card-label">Comptes Rejetés</span>
            <div class="card-sublabel">Demandes refusées</div>
          </div>
          <div class="icon-wrapper icon-box-red">
            <XCircle :size="20" />
          </div>
        </div>

        <div class="card-value-box">
          <div class="card-value font-mono text-red">{{ stats.rejected_users }}</div>
          <span class="card-unit">refusés</span>
        </div>

        <div class="card-footer">
          <span class="footer-trend text-red">
            Motif notifié
          </span>
          <span class="badge-mini badge-mini-red">Rejetés</span>
        </div>
      </div>

      <!-- CARTE 5 : Comptes Suspendus (SUSPENDED) -->
      <div 
        class="glass-card scorecard-card"
        :class="{ 'card-active-border-orange': selectedStatus === 'SUSPENDED' }"
        @click="() => { selectedStatus = 'SUSPENDED'; fetchUsers(); }"
      >
        <div class="card-top">
          <div>
            <span class="card-label">Comptes Suspendus</span>
            <div class="card-sublabel">Sessions révoquées</div>
          </div>
          <div class="icon-wrapper icon-box-orange">
            <ShieldAlert :size="20" />
          </div>
        </div>

        <div class="card-value-box">
          <div class="card-value font-mono text-orange">{{ stats.suspended_users }}</div>
          <span class="card-unit">bloqués</span>
        </div>

        <div class="card-footer">
          <span class="footer-trend text-orange">
            Accès coupés
          </span>
          <span class="badge-mini badge-mini-orange">Suspendus</span>
        </div>
      </div>

    </div>

    <!-- ===================================================================== -->
    <!-- 3. TABLEAU OPÉRATIONNEL & PANNEAU DE CONTRÔLE (STYLE DASHBOARD HSE)    -->
    <!-- ===================================================================== -->
    <div class="glass-card operational-panel">
      
      <!-- En-tête du tableau opérationnel avec titre & filtres -->
      <div class="panel-header">
        <div>
          <div class="header-badge-row">
            <span class="badge-priority">RBAC & SÉCURITÉ</span>
            <h3 class="panel-title">
              <Users :size="20" color="var(--color-primary)" />
              Tableau Opérationnel : Gestion des Comptes Utilisateurs
            </h3>
          </div>
          <p class="panel-subtitle">
            Filtrage dynamique multicritère · Supervision des statuts, habilitations et historique d'approbation
          </p>
        </div>

        <!-- Outils de recherche et filtres de premier niveau -->
        <div class="primary-controls">
          <!-- Recherche textuelle -->
          <div class="search-wrapper">
            <Search :size="14" class="search-icon-pos" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher nom, email..."
              class="form-input search-input-dashboard"
              @input="fetchUsers"
            />
            <button 
              v-if="searchQuery" 
              class="search-clear-btn" 
              @click="() => { searchQuery = ''; fetchUsers(); }"
              title="Effacer"
            >
              <X :size="13" />
            </button>
          </div>

          <!-- Filtre Rôle -->
          <select
            v-model="selectedRole"
            class="form-input select-dashboard"
            @change="fetchUsers"
          >
            <option value="ALL">Tous les rôles</option>
            <option value="USER">Rôle : USER</option>
            <option value="ADMIN">Rôle : ADMIN</option>
          </select>

          <!-- Onglets rapides de statut -->
          <div class="tabs-pill-box">
            <button 
              class="pill-tab" 
              :class="{ 'pill-tab-active': selectedStatus === 'ALL' }"
              @click="() => { selectedStatus = 'ALL'; fetchUsers(); }"
            >
              Tous ({{ stats.total_users }})
            </button>
            <button 
              class="pill-tab" 
              :class="{ 'pill-tab-active': selectedStatus === 'PENDING' }"
              @click="() => { selectedStatus = 'PENDING'; fetchUsers(); }"
            >
              <span>En attente</span>
              <span v-if="stats.pending_users > 0" class="badge-tab-count">{{ stats.pending_users }}</span>
            </button>
            <button 
              class="pill-tab" 
              :class="{ 'pill-tab-active': selectedStatus === 'APPROVED' }"
              @click="() => { selectedStatus = 'APPROVED'; fetchUsers(); }"
            >
              Approuvés
            </button>
            <button 
              class="pill-tab" 
              :class="{ 'pill-tab-active': selectedStatus === 'REJECTED' }"
              @click="() => { selectedStatus = 'REJECTED'; fetchUsers(); }"
            >
              Rejetés
            </button>
            <button 
              class="pill-tab" 
              :class="{ 'pill-tab-active': selectedStatus === 'SUSPENDED' }"
              @click="() => { selectedStatus = 'SUSPENDED'; fetchUsers(); }"
            >
              Suspendus
            </button>
          </div>
        </div>
      </div>

      <!-- LIGNE SECONDAIRE : Filtre par plage de dates (« Du » / « Au ») -->
      <div class="secondary-controls-bar">
        <div class="date-filter-group">
          <div class="date-filter-tag">
            <Calendar :size="14" class="date-tag-icon" />
            <span>Date d'inscription :</span>
          </div>

          <div class="date-pickers-row">
            <div class="date-field-container">
              <span class="date-field-prefix">Du</span>
              <input 
                type="date" 
                class="form-input date-picker-input"
                v-model="dateFrom"
                @change="fetchUsers"
                title="Date de début (si seule date renseignée, filtre uniquement cette journée)"
              />
            </div>

            <ArrowRight :size="13" class="date-arrow" />

            <div class="date-field-container">
              <span class="date-field-prefix">Au</span>
              <input 
                type="date" 
                class="form-input date-picker-input"
                v-model="dateTo"
                @change="fetchUsers"
                title="Date de fin"
              />
            </div>

            <button 
              v-if="dateFrom || dateTo" 
              class="btn-date-clear" 
              @click="resetDateFilter"
              title="Effacer la sélection de date"
            >
              <X :size="13" />
              <span>Effacer</span>
            </button>
          </div>

          <div v-if="dateFilterHint" class="date-hint-pill">
            <Info :size="13" />
            <span>{{ dateFilterHint }}</span>
          </div>
        </div>

        <button 
          v-if="hasActiveFilters" 
          class="btn-reset-filters-dash" 
          @click="resetFilters"
          title="Réinitialiser tous les filtres"
        >
          <RotateCcw :size="13" />
          <span>Réinitialiser les filtres</span>
        </button>
      </div>

      <!-- TABLEAU DES UTILISATEURS -->
      <div class="table-scrollable">
        <table class="dashboard-table">
          <thead>
            <tr>
              <th style="min-width: 240px;">Utilisateur</th>
              <th style="min-width: 110px;">Rôle</th>
              <th style="min-width: 130px;">Statut</th>
              <th style="min-width: 140px;">Date d'inscription</th>
              <th style="min-width: 160px;">Revue par</th>
              <th style="min-width: 140px;">Date de revue</th>
              <th style="min-width: 210px; text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody>
            <!-- État vide -->
            <tr v-if="users.length === 0">
              <td colspan="7" class="table-empty-cell">
                <CheckCircle2 :size="32" color="#10b981" style="margin: 0 auto 8px;" />
                <div class="empty-msg-title">Aucun utilisateur ne correspond à ces critères.</div>
                <div class="empty-msg-sub">Modifiez les filtres pour afficher d'autres comptes.</div>
                <button v-if="hasActiveFilters" class="btn-dash-reset-link" @click="resetFilters">
                  <RotateCcw :size="13" /> Réinitialiser les filtres
                </button>
              </td>
            </tr>

            <!-- Lignes utilisateurs -->
            <tr
              v-for="u in users"
              :key="u.id"
              class="table-row-hover"
              :class="{ 'row-highlight-pending': u.status === 'PENDING' }"
            >
              <!-- 1. Utilisateur (Nom + Email) -->
              <td>
                <div class="user-info-cell">
                  <div 
                    class="user-avatar-circle"
                    :class="u.role === 'ADMIN' ? 'avatar-admin-dash' : 'avatar-user-dash'"
                  >
                    {{ u.full_name?.charAt(0)?.toUpperCase() || 'U' }}
                  </div>
                  <div>
                    <div class="user-name-text">{{ u.full_name }}</div>
                    <div class="user-email-text">
                      <Mail :size="12" style="opacity: 0.6;" />
                      <span>{{ u.email }}</span>
                    </div>
                  </div>
                </div>
              </td>

              <!-- 2. Rôle -->
              <td>
                <span :class="['badge-role', u.role === 'ADMIN' ? 'badge-role-admin' : 'badge-role-user']">
                  <ShieldCheck v-if="u.role === 'ADMIN'" :size="13" />
                  <Users v-else :size="13" />
                  {{ u.role }}
                </span>
              </td>

              <!-- 3. Statut -->
              <td>
                <div class="status-cell-box">
                  <span :class="['badge-status', `badge-status-${u.status.toLowerCase()}`]">
                    <span class="status-dot"></span>
                    {{ u.status }}
                  </span>
                  <span 
                    v-if="u.status === 'REJECTED' && u.rejection_reason" 
                    class="rejection-hint-dash" 
                    :title="u.rejection_reason"
                  >
                    Motif : {{ u.rejection_reason }}
                  </span>
                </div>
              </td>

              <!-- 4. Date d'inscription -->
              <td>
                <div class="date-duo-cell">
                  <span class="date-day">{{ formatDateTime(u.created_at).date }}</span>
                  <span class="date-time">{{ formatDateTime(u.created_at).time }}</span>
                </div>
              </td>

              <!-- 5. Revue par -->
              <td>
                <div v-if="u.reviewer_name" class="reviewer-tag-dash" :title="u.reviewer_email || ''">
                  <ShieldCheck :size="13" color="var(--color-primary)" />
                  <span>{{ u.reviewer_name }}</span>
                </div>
                <span v-else-if="u.reviewed_by" class="text-dim">Admin #{{ u.reviewed_by }}</span>
                <span v-else class="text-dim">—</span>
              </td>

              <!-- 6. Date de revue -->
              <td>
                <div v-if="u.reviewed_at" class="date-duo-cell">
                  <span class="date-day">{{ formatDateTime(u.reviewed_at).date }}</span>
                  <span class="date-time">{{ formatDateTime(u.reviewed_at).time }}</span>
                </div>
                <span v-else class="text-dim">—</span>
              </td>

              <!-- 7. Boutons d'action -->
              <td style="text-align: right;">
                <div class="actions-wrapper">
                  
                  <!-- PENDING : Approuver Standard, Approuver Admin, Rejeter -->
                  <template v-if="u.status === 'PENDING'">
                    <button 
                      class="btn-dash-action btn-dash-approve"
                      title="Approuver comme Utilisateur standard"
                      @click="handleApprove(u)"
                    >
                      <Check :size="13" />
                      <span>Approuver</span>
                    </button>
                    <button 
                      class="btn-dash-action btn-dash-promote"
                      title="Approuver et donner immédiatement les droits Administrateur"
                      @click="openRoleModal(u, 'ADMIN')"
                    >
                      <ShieldCheck :size="13" />
                      <span>Approuver Admin</span>
                    </button>
                    <button 
                      class="btn-dash-action btn-dash-reject"
                      title="Rejeter la demande"
                      @click="openRejectModal(u)"
                    >
                      <X :size="13" />
                      <span>Rejeter</span>
                    </button>
                  </template>

                  <!-- APPROVED : Nommer Admin / Passer en User + Suspendre -->
                  <template v-else-if="u.status === 'APPROVED'">
                    <button 
                      v-if="u.role === 'USER'"
                      class="btn-dash-action btn-dash-promote"
                      title="Accorder les privilèges Administrateur"
                      @click="openRoleModal(u, 'ADMIN')"
                    >
                      <ShieldCheck :size="13" />
                      <span>Nommer Admin</span>
                    </button>
                    <button 
                      v-else-if="u.role === 'ADMIN'"
                      class="btn-dash-action btn-dash-demote"
                      title="Retirer les droits Administrateur"
                      @click="openRoleModal(u, 'USER')"
                    >
                      <UserMinus :size="13" />
                      <span>Passer en User</span>
                    </button>

                    <button 
                      class="btn-dash-action btn-dash-suspend"
                      title="Suspendre les accès de ce compte"
                      @click="openSuspendModal(u)"
                    >
                      <ShieldAlert :size="13" />
                      <span>Suspendre</span>
                    </button>
                  </template>

                  <!-- REJECTED ou SUSPENDED : Réactiver -->
                  <template v-else-if="u.status === 'REJECTED' || u.status === 'SUSPENDED'">
                    <button 
                      class="btn-dash-action btn-dash-reactivate"
                      title="Réactiver / Approuver ce compte"
                      @click="handleApprove(u)"
                    >
                      <Check :size="13" />
                      <span>Réactiver</span>
                    </button>
                  </template>

                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- FOOTER TABLEAU : COMPTEUR D'ACTIONS ET DE RESPONSABLES -->
      <div class="panel-footer">
        <div>
          Affichage de <strong style="color: #fff">{{ users.length }}</strong> utilisateur(s) sur <strong style="color: #fff">{{ stats.total_users }}</strong> au total.
          <span v-if="hasActiveFilters" style="color: var(--color-primary); margin-left: 6px;">(filtres actifs)</span>
        </div>
        <div class="footer-stats-badges">
          <span>En attente : <strong style="color: #fbbf24">{{ stats.pending_users }}</strong></span>
          <span>Approuvés : <strong style="color: #10b981">{{ stats.approved_users }}</strong></span>
          <span>Admins : <strong style="color: var(--color-primary)">{{ users.filter(u => u.role === 'ADMIN').length }}</strong></span>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- MODALES D'ACTION (DESIGN GLASSMORPHISM HOMOGÈNE)                      -->
    <!-- ===================================================================== -->

    <!-- Modale de Rejet -->
    <div v-if="showRejectModal" class="modal-overlay page-anim">
      <div class="glass-card modal-container border-danger">
        <div class="modal-header">
          <div class="modal-title-box">
            <div class="icon-circle icon-circle-danger">
              <AlertTriangle :size="20" />
            </div>
            <div>
              <h3 class="modal-heading">Rejeter la demande d'accès</h3>
              <p class="modal-subheading">Compte : <strong>{{ userToReject?.email }}</strong></p>
            </div>
          </div>
          <button class="modal-close-btn" @click="showRejectModal = false"><X :size="18" /></button>
        </div>

        <div class="modal-body">
          <label class="form-label" style="margin-bottom: 8px; display: block;">Motif du rejet (obligatoire) :</label>
          <textarea 
            class="form-input modal-textarea" 
            rows="4" 
            placeholder="Ex : Profil incomplet, adresse e-mail non reconnue..." 
            v-model="rejectionReason"
          ></textarea>
          <div class="modal-help-text">Ce motif sera notifié à l'utilisateur lors de sa tentative de connexion.</div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRejectModal = false" :disabled="isRejecting">Annuler</button>
          <button class="btn btn-danger" @click="handleConfirmReject" :disabled="isRejecting || !rejectionReason.trim()">
            <X :size="16" /> {{ isRejecting ? 'Rejet en cours...' : 'Confirmer le rejet' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modale de Suspension -->
    <div v-if="showSuspendModal" class="modal-overlay page-anim">
      <div class="glass-card modal-container border-warning">
        <div class="modal-header">
          <div class="modal-title-box">
            <div class="icon-circle icon-circle-warning"><ShieldAlert :size="22" /></div>
            <div>
              <h3 class="modal-heading">Suspendre le compte</h3>
              <p class="modal-subheading">Utilisateur : <strong style="color: #fff">{{ userToSuspend?.full_name }}</strong></p>
            </div>
          </div>
          <button class="modal-close-btn" @click="showSuspendModal = false"><X :size="18" /></button>
        </div>

        <div class="modal-body">
          <div class="warning-callout">
            <AlertTriangle :size="20" class="callout-icon" />
            <div class="callout-text">
              <strong>Action immédiate :</strong> La suspension révoque immédiatement tous les jetons actifs. L'utilisateur sera déconnecté sur le champ.
            </div>
          </div>
          <p class="modal-confirm-prompt">Confirmez-vous la suspension d'accès pour <strong>{{ userToSuspend?.full_name }}</strong> ?</p>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showSuspendModal = false" :disabled="isSuspending">Annuler</button>
          <button class="btn btn-warning-action" @click="handleConfirmSuspend" :disabled="isSuspending">
            <ShieldAlert :size="16" /> {{ isSuspending ? 'Suspension...' : 'Confirmer la suspension' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modale de Changement de Rôle -->
    <div v-if="showRoleModal" class="modal-overlay page-anim">
      <div class="glass-card modal-container" :class="targetRole === 'ADMIN' ? 'border-primary' : 'border-amber'">
        <div class="modal-header">
          <div class="modal-title-box">
            <div class="icon-circle" :class="targetRole === 'ADMIN' ? 'icon-circle-promote' : 'icon-circle-demote'">
              <ShieldCheck v-if="targetRole === 'ADMIN'" :size="22" />
              <UserMinus v-else :size="22" />
            </div>
            <div>
              <h3 class="modal-heading">
                {{ targetRole === 'ADMIN' ? 'Accorder les privilèges Administrateur' : 'Rétrograder en Utilisateur simple' }}
              </h3>
              <p class="modal-subheading">Utilisateur : <strong style="color: #fff">{{ userToChangeRole?.full_name }}</strong></p>
            </div>
          </div>
          <button class="modal-close-btn" @click="showRoleModal = false"><X :size="18" /></button>
        </div>

        <div class="modal-body">
          <div v-if="targetRole === 'ADMIN'" class="role-callout callout-promote">
            <ShieldCheck :size="20" class="callout-icon text-primary" />
            <div class="callout-text text-green">
              <strong>Privilèges accordés :</strong> Cet utilisateur aura un accès complet aux formulaires HSE, à l'historique d'audit et à la gestion administrative des utilisateurs.
            </div>
          </div>
          <div v-else class="role-callout callout-demote">
            <UserMinus :size="20" class="callout-icon text-amber" />
            <div class="callout-text text-amber">
              <strong>Privilèges restreints :</strong> L'accès aux formulaires HSE, aux audits et à l'administration sera retiré. L'accès sera limité à l'Accueil, au Dashboard et à son Profil.
            </div>
          </div>
          <p class="modal-confirm-prompt">
            Confirmez-vous le passage du compte au rôle 
            <span :class="targetRole === 'ADMIN' ? 'badge-role-admin' : 'badge-role-user'">{{ targetRole }}</span> ?
          </p>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRoleModal = false" :disabled="isChangingRole">Annuler</button>
          <button 
            :class="['btn', targetRole === 'ADMIN' ? 'btn-promote-confirm' : 'btn-demote-confirm']"
            @click="handleConfirmChangeRole" 
            :disabled="isChangingRole"
          >
            <ShieldCheck v-if="targetRole === 'ADMIN'" :size="16" />
            <UserMinus v-else :size="16" />
            {{ isChangingRole ? 'Mise à jour...' : (targetRole === 'ADMIN' ? 'Confirmer la promotion' : 'Confirmer la rétrogradation') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* =============================================================================
   CONTENEUR & BANDEAU DASHBOARD
============================================================================= */
.user-management-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dashboard-banner {
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
}

.banner-tagline {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.badge-portal {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.3);
  font-size: 0.72rem;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.banner-bullet {
  color: var(--text-dim);
  font-size: 0.8rem;
}

.banner-site {
  font-size: 0.8rem;
  color: var(--color-accent-light);
  font-weight: 600;
}

.banner-title {
  font-size: 1.65rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
}

.banner-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.btn-dashboard-action {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  color: #001c24;
  padding: 8px 18px;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 201, 150, 0.3);
  transition: all 0.2s ease;
}

.btn-dashboard-action:hover:not(:disabled) {
  box-shadow: 0 6px 18px rgba(0, 201, 150, 0.45);
  transform: translateY(-1px);
}

.btn-dashboard-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* =============================================================================
   SCORECARDS DE SYNTHÈSE (STYLE EXACT DASHBOARD)
============================================================================= */
.scorecards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1.25rem;
}

.scorecard-card {
  padding: 1.25rem 1.4rem;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

.scorecard-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.2);
}

.card-active-border {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 16px rgba(0, 201, 150, 0.25);
}

.card-active-border-amber {
  border-color: #f59e0b !important;
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.3);
}

.card-active-border-green {
  border-color: #10b981 !important;
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.3);
}

.card-active-border-red {
  border-color: #f43f5e !important;
  box-shadow: 0 0 16px rgba(244, 63, 94, 0.3);
}

.card-active-border-orange {
  border-color: #f97316 !important;
  box-shadow: 0 0 16px rgba(249, 115, 22, 0.3);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-label {
  font-size: 0.76rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-sublabel {
  font-size: 0.72rem;
  color: var(--text-dim);
  margin-top: 2px;
}

.icon-wrapper {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-box-blue { background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.25); }
.icon-box-amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
.icon-box-green { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.icon-box-red { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }
.icon-box-orange { background: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3); }

.card-value-box {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 12px;
}

.card-value {
  font-size: 2.1rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -1px;
}

.font-mono {
  font-family: var(--font-mono);
}

.card-unit {
  font-size: 0.75rem;
  color: var(--text-dim);
  font-weight: 600;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.footer-trend {
  font-size: 0.74rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.text-blue { color: #38bdf8; }
.text-amber { color: #fbbf24; }
.text-green { color: #10b981; }
.text-red { color: #f43f5e; }
.text-orange { color: #f97316; }

.badge-mini {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 6px;
  letter-spacing: 0.3px;
}

.badge-mini-blue { background: rgba(56, 189, 248, 0.12); color: #38bdf8; }
.badge-mini-amber { background: #f59e0b; color: #00141a; font-weight: 800; }
.badge-mini-green { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.badge-mini-red { background: rgba(244, 63, 94, 0.15); color: #f43f5e; }
.badge-mini-orange { background: rgba(249, 115, 22, 0.15); color: #f97316; }

/* Animation d'alerte pour les comptes en attente */
.alert-card-pulsing {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(180, 83, 9, 0.28) 100%) !important;
  border: 1px solid #f59e0b !important;
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.35);
}

.glow-amber {
  text-shadow: 0 0 10px rgba(245, 158, 11, 0.7);
}

.text-amber-light { color: #fde68a !important; }
.text-amber-dim { color: #fef3c7 !important; }

.card-green-accent {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(0, 32, 42, 0.85) 100%) !important;
  border: 1px solid rgba(16, 185, 129, 0.35) !important;
}

.text-green-light { color: #6ee7b7 !important; }

/* =============================================================================
   PANNEAU OPÉRATIONNEL & TABLEAU (STYLE EXACT DASHBOARD)
============================================================================= */
.operational-panel {
  padding: 1.5rem;
  border: 1px solid rgba(0, 201, 150, 0.3);
  background: linear-gradient(180deg, rgba(0, 32, 42, 0.85) 0%, rgba(0, 20, 28, 0.85) 100%);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
  border-radius: var(--radius-lg);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge-priority {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
  font-size: 0.72rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid rgba(0, 201, 150, 0.3);
  letter-spacing: 0.5px;
}

.panel-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-subtitle {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Contrôles de premier niveau */
.primary-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon-pos {
  position: absolute;
  left: 10px;
  color: var(--text-dim);
  pointer-events: none;
}

.search-input-dashboard {
  background: rgba(0, 28, 36, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  color: #fff !important;
  padding: 7px 12px 7px 30px !important;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  width: 200px;
}

.search-clear-btn {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
}

.select-dashboard {
  background: rgba(0, 28, 36, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  color: #fff !important;
  padding: 7px 12px !important;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.tabs-pill-box {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  padding: 3px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pill-tab {
  padding: 6px 11px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
}

.pill-tab:hover {
  color: #ffffff;
}

.pill-tab-active {
  background: var(--color-primary);
  color: #00141a !important;
  font-weight: 800;
}

.badge-tab-count {
  background: #f59e0b;
  color: #00141a;
  padding: 1px 5px;
  border-radius: 8px;
  font-size: 0.68rem;
  font-weight: 800;
}

.pill-tab-active .badge-tab-count {
  background: #00141a;
  color: var(--color-primary);
}

/* Ligne secondaire : Contrôles de Date */
.secondary-controls-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.date-filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.date-filter-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.date-tag-icon {
  color: var(--color-primary);
}

.date-pickers-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-field-container {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 28, 36, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
}

.date-field-prefix {
  font-size: 0.74rem;
  font-weight: 800;
  color: var(--text-dim);
}

.date-picker-input {
  background: transparent !important;
  border: none !important;
  color: #ffffff !important;
  padding: 4px 6px !important;
  font-size: 0.78rem;
  height: 28px;
  outline: none;
}

.date-picker-input::-webkit-calendar-picker-indicator {
  filter: invert(0.85);
  cursor: pointer;
}

.date-arrow {
  color: var(--text-dim);
}

.btn-date-clear {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: #f43f5e;
  padding: 4px 9px;
  border-radius: var(--radius-sm);
  font-size: 0.74rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-date-clear:hover {
  background: rgba(244, 63, 94, 0.22);
}

.date-hint-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #38bdf8;
  font-size: 0.74rem;
  padding: 3px 9px;
  border-radius: 6px;
}

.btn-reset-filters-dash {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-muted);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-reset-filters-dash:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
}

/* =============================================================================
   TABLEAU OPÉRATIONNEL DES UTILISATEURS (STYLE DASHBOARD)
============================================================================= */
.table-scrollable {
  overflow-x: auto;
}

.dashboard-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.85rem;
}

.dashboard-table th {
  padding: 10px 14px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 800;
  background: rgba(0, 32, 42, 0.9);
}

.dashboard-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  vertical-align: middle;
  transition: background 0.15s ease;
}

.table-row-hover:hover td {
  background: rgba(255, 255, 255, 0.025);
}

.row-highlight-pending td {
  background: rgba(245, 158, 11, 0.045);
}
.row-highlight-pending:hover td {
  background: rgba(245, 158, 11, 0.075);
}

/* Cellule Utilisateur */
.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.avatar-admin-dash {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.35);
}

.avatar-user-dash {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.user-name-text {
  font-weight: 700;
  color: #ffffff;
  font-size: 0.9rem;
}

.user-email-text {
  font-size: 0.76rem;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Badges de Rôle */
.badge-role {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.3px;
}

.badge-role-admin {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.35);
}

.badge-role-user {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

/* Badges de Statut */
.status-cell-box {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.badge-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 0.74rem;
  font-weight: 800;
  width: fit-content;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.badge-status-pending {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.35);
}
.badge-status-pending .status-dot { background: #fbbf24; }

.badge-status-approved {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}
.badge-status-approved .status-dot { background: #34d399; }

.badge-status-rejected {
  background: rgba(244, 63, 94, 0.15);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.35);
}
.badge-status-rejected .status-dot { background: #f43f5e; }

.badge-status-suspended {
  background: rgba(249, 115, 22, 0.15);
  color: #fb923c;
  border: 1px solid rgba(249, 115, 22, 0.35);
}
.badge-status-suspended .status-dot { background: #fb923c; }

.rejection-hint-dash {
  font-size: 0.7rem;
  color: var(--text-dim);
  max-width: 170px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Date Cell */
.date-duo-cell {
  display: flex;
  flex-direction: column;
}

.date-day {
  font-size: 0.84rem;
  font-weight: 700;
  color: #ffffff;
}

.date-time {
  font-size: 0.72rem;
  color: var(--text-dim);
}

/* Reviewer Tag */
.reviewer-tag-dash {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(0, 201, 150, 0.08);
  border: 1px solid rgba(0, 201, 150, 0.22);
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #ffffff;
}

/* Actions */
.actions-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-dash-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-dash-approve {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #34d399;
}
.btn-dash-approve:hover {
  background: rgba(16, 185, 129, 0.25);
}

.btn-dash-promote {
  background: rgba(0, 201, 150, 0.15);
  border: 1px solid rgba(0, 201, 150, 0.35);
  color: var(--color-primary);
}
.btn-dash-promote:hover {
  background: rgba(0, 201, 150, 0.25);
}

.btn-dash-demote {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #fbbf24;
}
.btn-dash-demote:hover {
  background: rgba(245, 158, 11, 0.25);
}

.btn-dash-reject {
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: #f43f5e;
}
.btn-dash-reject:hover {
  background: rgba(244, 63, 94, 0.22);
}

.btn-dash-suspend {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.btn-dash-suspend:hover {
  background: rgba(239, 68, 68, 0.25);
}

.btn-dash-reactivate {
  background: rgba(0, 201, 150, 0.15);
  border: 1px solid rgba(0, 201, 150, 0.35);
  color: var(--color-primary);
}
.btn-dash-reactivate:hover {
  background: rgba(0, 201, 150, 0.25);
}

/* État vide */
.table-empty-cell {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-dim);
}

.empty-msg-title {
  font-weight: 700;
  color: #fff;
  font-size: 0.95rem;
  margin-top: 4px;
}

.empty-msg-sub {
  font-size: 0.8rem;
  margin-top: 2px;
}

.btn-dash-reset-link {
  margin-top: 0.75rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-muted);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Footer opérationnel */
.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.78rem;
  color: var(--text-dim);
  flex-wrap: wrap;
  gap: 8px;
}

.footer-stats-badges {
  display: flex;
  gap: 14px;
}

/* =============================================================================
   MODALES GLASSMORPHISM
============================================================================= */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.25rem;
}

.modal-container {
  max-width: 500px;
  width: 100%;
  padding: 1.75rem;
  border-radius: 14px;
}

.border-danger { border: 1px solid rgba(244, 63, 94, 0.35); }
.border-warning { border: 1px solid rgba(249, 115, 22, 0.35); }
.border-amber { border: 1px solid rgba(245, 158, 11, 0.35); }
.border-primary { border: 1px solid rgba(0, 201, 150, 0.35); }

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.modal-title-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-circle-danger { background: rgba(244, 63, 94, 0.15); color: #f43f5e; }
.icon-circle-warning { background: rgba(249, 115, 22, 0.15); color: #fb923c; }
.icon-circle-promote { background: rgba(0, 201, 150, 0.15); color: var(--color-primary); }
.icon-circle-demote { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.modal-heading {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
}

.modal-subheading {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 2px;
}

.modal-body {
  margin-bottom: 1.5rem;
}

.modal-textarea {
  width: 100%;
  resize: vertical;
  font-size: 0.85rem;
}

.modal-help-text {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-top: 6px;
  line-height: 1.4;
}

.warning-callout, .role-callout {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
}

.warning-callout {
  background: rgba(249, 115, 22, 0.08);
  border: 1px solid rgba(249, 115, 22, 0.25);
}

.callout-promote {
  background: rgba(0, 201, 150, 0.08);
  border: 1px solid rgba(0, 201, 150, 0.25);
}

.callout-demote {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.callout-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.callout-text {
  font-size: 0.85rem;
  line-height: 1.5;
}

.modal-confirm-prompt {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 1.25rem;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.btn-danger {
  background: #f43f5e;
  color: #ffffff;
  border: none;
  font-weight: 700;
}
.btn-danger:hover:not(:disabled) {
  background: #e11d48;
}

.btn-warning-action {
  background: #ea580c;
  color: #ffffff;
  border: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-warning-action:hover:not(:disabled) {
  background: #c2410c;
}

.btn-promote-confirm {
  background: var(--color-primary);
  color: #00141a;
  border: none;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-promote-confirm:hover:not(:disabled) {
  background: #00b383;
}

.btn-demote-confirm {
  background: #f59e0b;
  color: #00141a;
  border: none;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-demote-confirm:hover:not(:disabled) {
  background: #d97706;
}

.spin-anim {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
