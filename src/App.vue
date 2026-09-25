<!--
===============================================================================
COMPOSANT RACINE DE L'APPLICATION (APP.VUE)
===============================================================================
Rôle :
  Composant chef d'orchestre de l'application cliente PlatformActia :
  1. Gestion de l'état d'authentification :
     - Vérification et lecture du jeton JWT dans le localStorage.
     - Affichage conditionnel entre l'écran de connexion (`AuthScreen`) et l'application principale.
     - Chargement automatique du profil utilisateur (`loadUserProfile`).
  2. Routage interne dynamique (sans bibliothèque externe lourde) :
     - Pages gérées : 'home', 'formulaire', 'historique', 'dashboard', 'profile'.
     - Bascule fluide entre le sélecteur de formulaires et l'assistant de saisie pas-à-pas (`wizardMode`).
  3. Gestion centralisée des fenêtres modales et dialogues :
     - Visualisation détaillée d'un audit (`AuditDetailModal`).
     - Confirmation sécurisée de suppression (`DeleteModal`).
     - Modèle d'impression / export PDF (`PrintReport`).
  4. Système de notifications toasts temporaires (succès et erreurs).
===============================================================================
-->

<script setup>
import { ref, watch, onMounted } from 'vue'

// --- 1. Imports des Composants de Navigation et d'Agencement ---
import Home from './components/home/Home.vue'
import Sidebar from './components/layout/Sidebar.vue'
import Topbar from './components/layout/Topbar.vue'

// --- 2. Imports des Composants Métier HSE & Authentification / RBAC ---
import AuthScreen from './components/auth/AuthScreen.vue'
import PendingReviewScreen from './components/auth/PendingReviewScreen.vue'
import AccountRejectedScreen from './components/auth/AccountRejectedScreen.vue'
import AccountSuspendedScreen from './components/auth/AccountSuspendedScreen.vue'
import UserManagement from './components/admin/UserManagement.vue'
import FormSelector from './components/forms/FormSelector.vue'
import AuditWizard from './components/forms/AuditWizard.vue'
import HistoryTable from './components/history/HistoryTable.vue'
import AuditDetailModal from './components/history/AuditDetailModal.vue'
import DeleteModal from './components/history/DeleteModal.vue'
import PrintReport from './components/history/PrintReport.vue'
import HseDashboard from './components/dashboard/HseDashboard.vue'
import UserProfile from './components/profile/UserProfile.vue'

/**
 * Récupère le jeton JWT depuis le localStorage en filtrant les valeurs corrompues ('null', 'undefined', vide).
 * @returns {string|null} Le jeton valide ou null si absent.
 */
const getValidToken = () => {
  const t = localStorage.getItem('access_token')
  return (t && t !== 'null' && t !== 'undefined' && t.trim() !== '') ? t : null
}

// --- 3. États Réactifs Globaux de l'Application ---
// Jeton d'accès JWT pour authentifier les requêtes API
const token = ref(getValidToken())

// Informations du profil utilisateur connecté (nom, email, rôle, statut)
const user = ref(null)

// Compteur des comptes en attente pour badge d'administration
const pendingUsersCount = ref(0)

// Page actuellement active dans la vue ('home', 'formulaire', 'historique', 'dashboard', 'admin-users', 'profile')
const currentPage = ref('home')

// Indicateur d'affichage de l'assistant de formulaire pas-à-pas (Wizard)
const wizardMode = ref(false)

// Type de formulaire sélectionné ('audit_hse', 'tournee_hse', 'permis_travail', etc.)
const selectedFormType = ref('audit_hse')

// Fiche d'audit chargée en mode édition (null si nouvelle création)
const editingAudit = ref(null)

// Liste des audits récupérés pour l'historique
const auditsList = ref([])

// Fiche en cours de consultation dans la modale de détail
const viewingAudit = ref(null)

// Fiche ciblée pour demande de confirmation de suppression
const deletingAudit = ref(null)

// Fiche sélectionnée pour impression ou génération de rapport PDF
const printingAudit = ref(null)

// File d'attente des messages d'alerte temporaires (toasts)
const toasts = ref([])

// --- 4. URLs de Base des Endpoints Backend ---
const API_BASE = window.location.origin + '/api/v1/auth'
const API_AUDITS = window.location.origin + '/api/v1/audits'
const API_ADMIN = window.location.origin + '/api/v1/admin'

/**
 * Affiche une notification toast temporaire avec disparition automatique après 4 secondes.
 * @param {string|object|Array} msg - Message texte ou objet d'erreur retourné par FastAPI.
 * @param {'success'|'error'} type - Type visuel de la notification.
 */
const showToast = (msg, type = 'success') => {
  const id = Date.now()
  let displayMsg = 'Une erreur est survenue'
  if (typeof msg === 'string') {
    displayMsg = msg
  } else if (Array.isArray(msg) && msg.length > 0) {
    displayMsg = msg[0]?.msg || JSON.stringify(msg[0])
  } else if (typeof msg === 'object' && msg !== null) {
    displayMsg = msg.msg || msg.detail || JSON.stringify(msg)
  }
  toasts.value.push({ id, msg: displayMsg, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 4000)
}

/**
 * Récupère les statistiques d'administration (notamment le nombre de comptes en attente).
 */
const fetchAdminStats = async () => {
  if (!token.value || user.value?.role !== 'ADMIN') return
  try {
    const res = await fetch(`${API_ADMIN}/stats`, {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })
    if (res.ok) {
      const data = await res.json()
      pendingUsersCount.value = data.pending_users || 0
    }
  } catch (err) {
    console.error('Erreur récupération stats admin:', err)
  }
}

/**
 * Charge les informations du profil utilisateur depuis le backend via /api/v1/auth/me.
 * @param {string} authToken - Le jeton d'accès JWT.
 */
const loadUserProfile = async (authToken) => {
  try {
    const res = await fetch(`${API_BASE}/me`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    const data = await res.json()
    if (res.ok) {
      user.value = data
      if (data.role === 'ADMIN') {
        fetchAdminStats()
      }
    } else {
      handleLogout()
    }
  } catch (err) {
    handleLogout()
  }
}

/**
 * Récupère l'historique complet des soumissions de formulaires depuis le backend.
 */
const fetchAuditsHistory = async () => {
  if (!token.value || user.value?.status !== 'APPROVED') return
  try {
    const res = await fetch(`${API_AUDITS}/`, {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })
    const data = await res.json()
    if (res.ok) {
      auditsList.value = data
    }
  } catch (err) {}
}

// --- 5. Écouteurs Réactifs (Watchers) ---
// Déclenche le rechargement du profil dès que le token change ou à l'initialisation
watch(token, (newToken) => {
  if (newToken) {
    loadUserProfile(newToken)
  }
}, { immediate: true })

// Rafraîchit l'historique quand l'utilisateur navigue vers les pages 'historique' ou 'home'
watch([token, currentPage], ([t, page]) => {
  if (t && (page === 'historique' || page === 'home') && user.value?.status === 'APPROVED') {
    fetchAuditsHistory()
  }
})

// --- 6. Gestionnaires d'Événements de l'Application ---
/**
 * Déconnecte l'utilisateur, nettoie le localStorage et réinitialise l'état réactif.
 */
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  token.value = null
  user.value = null
  pendingUsersCount.value = 0
  currentPage.value = 'home'
  showToast('Déconnexion réussie.')
}

/**
 * Traite la réussite de connexion : enregistre le jeton, charge le profil et oriente vers le bon tableau de bord.
 * @param {string} t - Le nouveau token d'accès JWT.
 */
const handleLoginSuccess = async (t) => {
  token.value = t
  await loadUserProfile(t)
  currentPage.value = 'home'
}

/**
 * Ouvre l'assistant de formulaire (Wizard) en mode création ou modification.
 * @param {string} formType - Identifiant du formulaire ('audit_hse', 'tournee_hse', etc.).
 * @param {object|null} auditToEdit - Données de l'audit existant si modification.
 */
const handleOpenWizard = (formType, auditToEdit = null) => {
  selectedFormType.value = auditToEdit ? (auditToEdit.form_type || 'audit_hse') : formType
  editingAudit.value = auditToEdit
  wizardMode.value = true
}

/**
 * Navigue vers une page donnée avec contrôle d'accès RBAC et réinitialise le mode Wizard.
 * @param {string} page - Nom de la page cible.
 */
const handleNavigate = (page) => {
  // Garde client RBAC pour la page d'administration réservée au rôle ADMIN
  if (page === 'admin-users' && user.value?.role !== 'ADMIN') {
    showToast('Accès refusé : Privilèges Administrateur requis.', 'error')
    currentPage.value = 'home'
    return
  }
  wizardMode.value = false
  currentPage.value = page
}

/**
 * Exécute l'appel API DELETE pour supprimer définitivement une fiche d'audit.
 */
const handleExecuteDelete = async () => {
  if (!deletingAudit.value) return
  try {
    const res = await fetch(`${API_AUDITS}/${deletingAudit.value.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token.value}` }
    })
    if (res.ok) {
      showToast(`Fiche #ACTIA-${deletingAudit.value.id} supprimée.`)
      deletingAudit.value = null
      fetchAuditsHistory()
    }
  } catch (err) {
    showToast('Erreur lors de la suppression', 'error')
  }
}
</script>

<template>
  <!-- ======================================================================= -->
  <!-- CAS 1 : UTILISATEUR NON AUTHENTIFIÉ — ÉCRAN DE CONNEXION / INSCRIPTION -->
  <!-- ======================================================================= -->
  <template v-if="!token">
    <AuthScreen
      @login-success="handleLoginSuccess"
      @show-toast="showToast"
    />
  </template>

  <!-- ======================================================================= -->
  <!-- CAS 2 : CHARGEMENT EN COURS DU PROFIL                                  -->
  <!-- ======================================================================= -->
  <template v-else-if="!user">
    <div style="min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--bg-dark); color: #fff; gap: 16px;">
      <div class="pulse-dot" style="width: 24px; height: 24px;"></div>
      <div style="font-weight: 700; color: var(--text-muted); font-size: 0.95rem;">Chargement du profil PlatformActia...</div>
    </div>
  </template>

  <!-- ======================================================================= -->
  <!-- CAS 3 : COMPTE EN ATTENTE DE VALIDATION (PENDING)                       -->
  <!-- ======================================================================= -->
  <template v-else-if="user.status === 'PENDING'">
    <PendingReviewScreen
      :user="user"
      @check-status="() => loadUserProfile(token)"
      @logout="handleLogout"
    />
  </template>

  <!-- ======================================================================= -->
  <!-- CAS 4 : COMPTE REJETÉ (REJECTED)                                       -->
  <!-- ======================================================================= -->
  <template v-else-if="user.status === 'REJECTED'">
    <AccountRejectedScreen
      :user="user"
      @logout="handleLogout"
    />
  </template>

  <!-- ======================================================================= -->
  <!-- CAS 5 : COMPTE SUSPENDU (SUSPENDED)                                     -->
  <!-- ======================================================================= -->
  <template v-else-if="user.status === 'SUSPENDED'">
    <AccountSuspendedScreen
      :user="user"
      @logout="handleLogout"
    />
  </template>

  <!-- ======================================================================= -->
  <!-- CAS 6 : COMPTE APPROUVÉ (APPROVED) — APPLICATION PRINCIPALE            -->
  <!-- ======================================================================= -->
  <template v-else>
    <div class="app-layout">
      <!-- Barre de navigation latérale -->
      <Sidebar
        :current-page="currentPage"
        :user="user"
        :pending-count="pendingUsersCount"
        @update:current-page="handleNavigate"
        @logout="handleLogout"
      />
      <!-- Barre supérieure d'en-tête et statut profil -->
      <Topbar
        :current-page="currentPage"
        :user="user"
        @profile-click="() => { wizardMode = false; currentPage = 'profile' }"
        @show-toast="showToast"
      />

      <!-- Zone d'affichage du contenu dynamique de la page courante -->
      <main class="main-content">

        <!-- 1. Page d'Accueil : vue d'ensemble et accès rapides -->
        <Home v-if="currentPage === 'home'" :user="user" @navigate="handleNavigate" />

        <!-- 2. Page des Formulaires : Sélecteur de grille OU Assistant pas-à-pas -->
        <div v-if="currentPage === 'formulaire'" class="page-anim">
          <FormSelector
            v-if="!wizardMode"
            @select-form="(type) => handleOpenWizard(type)"
          />
          <AuditWizard
            v-else
            :form-type="selectedFormType"
            :editing-audit="editingAudit"
            @close="wizardMode = false"
            @submit-success="() => { wizardMode = false; currentPage = 'historique'; fetchAuditsHistory() }"
            @show-toast="showToast"
          />
        </div>

        <!-- 3. Page Historique : Tableau de bord de recherche et filtrage centralisé -->
        <div v-if="currentPage === 'historique'" class="page-anim">
          <HistoryTable
            :audits="auditsList"
            @refresh="fetchAuditsHistory"
            @view="(audit) => viewingAudit = audit"
            @edit="(audit) => { currentPage = 'formulaire'; handleOpenWizard(audit.form_type, audit) }"
            @delete="(audit) => deletingAudit = audit"
            @print="(audit) => printingAudit = audit"
          />
        </div>

        <!-- 4. Page Dashboard : Graphiques et indicateurs analytiques -->
        <div v-if="currentPage === 'dashboard'" class="page-anim">
          <HseDashboard @show-toast="showToast" />
        </div>

        <!-- 5. Page Administration : Gestion Utilisateurs & Validation Comptes (ADMIN) -->
        <div v-if="currentPage === 'admin-users' && user.role === 'ADMIN'" class="page-anim">
          <UserManagement
            :token="token"
            @show-toast="showToast"
          />
        </div>

        <!-- 6. Page Profil : Informations du compte et changement de mot de passe -->
        <div v-if="currentPage === 'profile'" class="page-anim">
          <UserProfile
            :user="user"
            :audits="auditsList"
            @show-toast="showToast"
            @user-updated="(updated) => { user = updated }"
          />
        </div>

      </main>

      <!-- =================================================================== -->
      <!-- DIALOGUES ET MODALES SYSTÈME                                        -->
      <!-- =================================================================== -->
      <!-- Fenêtre modale de consultation détaillée d'un audit -->
      <AuditDetailModal
        v-if="viewingAudit"
        :audit="viewingAudit"
        @close="viewingAudit = null"
        @print="(audit) => { viewingAudit = null; printingAudit = audit }"
      />
      <!-- Fenêtre modale de confirmation de suppression -->
      <DeleteModal
        v-if="deletingAudit"
        :audit="deletingAudit"
        @close="deletingAudit = null"
        @confirm="handleExecuteDelete"
      />
    </div>

    <!-- ===================================================================== -->
    <!-- RAPPORT D'IMPRESSION / EXPORT PDF                                     -->
    <!-- Positionné hors de .app-layout pour éviter tout masquage CSS print    -->
    <!-- ===================================================================== -->
    <PrintReport
      v-if="printingAudit"
      :audit="printingAudit"
      @after-print="printingAudit = null"
    />
  </template>

  <!-- ======================================================================= -->
  <!-- CONTENEUR GLOBAL DES NOTIFICATIONS TOASTS                              -->
  <!-- ======================================================================= -->
  <div class="toast-container">
    <div
      v-for="t in toasts"
      :key="t.id"
      :class="['toast', t.type === 'error' ? 'error' : '']"
    >{{ t.msg }}</div>
  </div>
</template>
