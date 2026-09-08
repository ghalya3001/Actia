<script setup>
import { ref, watch, onMounted } from 'vue'
import Home from './components/home/Home.vue'
import Sidebar from './components/layout/Sidebar.vue'
import Topbar from './components/layout/Topbar.vue'
import AuthScreen from './components/auth/AuthScreen.vue'
import FormSelector from './components/forms/FormSelector.vue'
import AuditWizard from './components/forms/AuditWizard.vue'
import HistoryTable from './components/history/HistoryTable.vue'
import AuditDetailModal from './components/history/AuditDetailModal.vue'
import DeleteModal from './components/history/DeleteModal.vue'
import PrintReport from './components/history/PrintReport.vue'
import HseDashboard from './components/dashboard/HseDashboard.vue'
import UserProfile from './components/profile/UserProfile.vue'

const getValidToken = () => {
  const t = localStorage.getItem('access_token')
  return (t && t !== 'null' && t !== 'undefined' && t.trim() !== '') ? t : null
}

const token = ref(getValidToken())
const user = ref(null)
const currentPage = ref('home')

const wizardMode = ref(false)
const selectedFormType = ref('audit_hse')
const editingAudit = ref(null)

const auditsList = ref([])
const viewingAudit = ref(null)
const deletingAudit = ref(null)
const printingAudit = ref(null)

const toasts = ref([])

const API_BASE = window.location.origin + '/api/v1/auth'
const API_AUDITS = window.location.origin + '/api/v1/audits'

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

const loadUserProfile = async (authToken) => {
  try {
    const res = await fetch(`${API_BASE}/me`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    const data = await res.json()
    if (res.ok) {
      user.value = data
    } else {
      handleLogout()
    }
  } catch (err) {
    handleLogout()
  }
}

const fetchAuditsHistory = async () => {
  if (!token.value) return
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

watch(token, (newToken) => {
  if (newToken) {
    loadUserProfile(newToken)
  }
}, { immediate: true })

watch([token, currentPage], ([t, page]) => {
  if (t && (page === 'historique' || page === 'home')) {
    fetchAuditsHistory()
  }
})

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  token.value = null
  user.value = null
  showToast('Déconnexion réussie.')
}

const handleLoginSuccess = (t) => {
  token.value = t
  loadUserProfile(t)
}

const handleOpenWizard = (formType, auditToEdit = null) => {
  selectedFormType.value = auditToEdit ? (auditToEdit.form_type || 'audit_hse') : formType
  editingAudit.value = auditToEdit
  wizardMode.value = true
}

const handleNavigate = (page) => {
  wizardMode.value = false
  currentPage.value = page
}

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
  <!-- AUTH SCREEN (not logged in) -->
  <template v-if="!token">
    <AuthScreen
      @login-success="handleLoginSuccess"
      @show-toast="showToast"
    />
    <div class="toast-container">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['toast', t.type === 'error' ? 'error' : '']"
      >{{ t.msg }}</div>
    </div>
  </template>

  <!-- MAIN APP LAYOUT (logged in) -->
  <template v-else>
    <div class="app-layout">
      <Sidebar
        :current-page="currentPage"
        @update:current-page="handleNavigate"
        @logout="handleLogout"
      />
      <Topbar
        :current-page="currentPage"
        :user="user"
        @profile-click="() => { wizardMode = false; currentPage = 'profile' }"
      />

      <main class="main-content">

        <!-- PAGE HOME -->
        <Home v-if="currentPage === 'home'" @navigate="handleNavigate" />

        <!-- PAGE FORMULAIRE -->
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

        <!-- PAGE HISTORIQUE -->
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

        <!-- PAGE DASHBOARD -->
        <div v-if="currentPage === 'dashboard'" class="page-anim">
          <HseDashboard />
        </div>

        <!-- PAGE PROFILE -->
        <div v-if="currentPage === 'profile'" class="page-anim">
          <UserProfile :user="user" @show-toast="showToast" />
        </div>

      </main>

      <!-- MODALS -->
      <AuditDetailModal
        v-if="viewingAudit"
        :audit="viewingAudit"
        @close="viewingAudit = null"
        @print="(audit) => { viewingAudit = null; printingAudit = audit }"
      />
      <DeleteModal
        v-if="deletingAudit"
        :audit="deletingAudit"
        @close="deletingAudit = null"
        @confirm="handleExecuteDelete"
      />

      <!-- TOAST CONTAINER -->
      <div class="toast-container">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="['toast', t.type === 'error' ? 'error' : '']"
        >{{ t.msg }}</div>
      </div>
    </div>

    <!-- PRINT REPORT — rendered OUTSIDE .app-layout so it stays visible during print -->
    <PrintReport
      v-if="printingAudit"
      :audit="printingAudit"
      @after-print="printingAudit = null"
    />
  </template>
</template>
