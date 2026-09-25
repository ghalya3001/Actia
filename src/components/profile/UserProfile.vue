<!--
===============================================================================
PAGE DE PROFIL UTILISATEUR & SÉCURITÉ DU COMPTE (USERPROFILE.VUE)
===============================================================================
Design moderne, premium et intuitif avec :
  1. Header Hero Glassmorphic avec avatar holographique, badges de rôle & statut
  2. Navigation ergonomique par onglets :
     - Vue d'ensemble & Informations (avec modification du nom en direct)
     - Sécurité & Mot de passe (avec jauge de robustesse temps réel et confirmation)
     - Habilitations & Rôles Système (matrice de contrôle d'accès)
  3. Bilan d'activité personnelle (audits réalisés, conformité, statut du compte)
===============================================================================
-->

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  User,
  Mail,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Lock,
  Key,
  Save,
  Eye,
  EyeOff,
  Edit3,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Building2,
  Calendar,
  Clock,
  Award,
  FileText,
  Check,
  Copy,
  ChevronRight,
  Activity,
  Sparkles
} from 'lucide-vue-next'

// --- Props et Événements ---
const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  },
  audits: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['showToast', 'userUpdated'])

// --- Onglet actif ---
const activeTab = ref('overview') // 'overview' | 'security' | 'permissions'

// --- États du changement de mot de passe ---
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const isUpdatingPassword = ref(false)

// --- États de modification du Nom ---
const isEditingName = ref(false)
const editedFullName = ref('')
const isSavingName = ref(false)

// Copie du lien/email
const copiedEmail = ref(false)

onMounted(() => {
  // Prévention stricte des autofills intempestifs du navigateur
  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  setTimeout(() => {
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  }, 150)
})

// --- Propriétés calculées du profil ---
const userInitials = computed(() => {
  if (!props.user?.full_name) return 'U'
  const parts = props.user.full_name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return props.user.full_name.substring(0, 2).toUpperCase()
})

const isAdmin = computed(() => props.user?.role === 'ADMIN')

const formattedRegistrationDate = computed(() => {
  if (!props.user?.created_at) return 'Récemment'
  try {
    const d = new Date(props.user.created_at)
    return d.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch (e) {
    return props.user.created_at
  }
})

// --- Calculs d'activité de l'utilisateur sur la plateforme ---
const userAuditsCount = computed(() => {
  if (!props.audits || props.audits.length === 0) return 0
  const myId = props.user?.id
  const myName = props.user?.full_name?.toLowerCase().trim()
  return props.audits.filter(a => {
    return a.user_id === myId || (a.author_name && a.author_name.toLowerCase().trim() === myName)
  }).length
})

const userAvgConformity = computed(() => {
  if (!props.audits || props.audits.length === 0) return 0
  const myId = props.user?.id
  const myName = props.user?.full_name?.toLowerCase().trim()
  const myAudits = props.audits.filter(a => {
    return a.user_id === myId || (a.author_name && a.author_name.toLowerCase().trim() === myName)
  })
  if (myAudits.length === 0) return 0
  const total = myAudits.reduce((acc, curr) => acc + (curr.taux_conformite || 0), 0)
  return Math.round((total / myAudits.length) * 10) / 10
})

const lastAuditDate = computed(() => {
  if (!props.audits || props.audits.length === 0) return 'Aucun'
  const myId = props.user?.id
  const myName = props.user?.full_name?.toLowerCase().trim()
  const myAudits = props.audits.filter(a => {
    return a.user_id === myId || (a.author_name && a.author_name.toLowerCase().trim() === myName)
  })
  if (myAudits.length === 0) return 'Aucun audit'
  const sorted = [...myAudits].sort((a, b) => new Date(b.date_audit) - new Date(a.date_audit))
  const d = sorted[0].date_audit
  const parts = d.split('-')
  return parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : d
})

// --- Robustesse du mot de passe en temps réel ---
const passwordCriteria = computed(() => {
  const p = newPassword.value || ''
  return {
    length: p.length >= 8,
    hasUpper: /[A-Z]/.test(p),
    hasNumber: /[0-9]/.test(p),
    hasSpecial: /[^A-Za-z0-9]/.test(p),
    match: p.length > 0 && p === confirmPassword.value
  }
})

const passwordStrengthScore = computed(() => {
  const c = passwordCriteria.value
  let score = 0
  if (c.length) score += 25
  if (c.hasUpper) score += 25
  if (c.hasNumber) score += 25
  if (c.hasSpecial) score += 25
  return score
})

const passwordStrengthLabel = computed(() => {
  const s = passwordStrengthScore.value
  if (!newPassword.value) return { text: 'Non renseigné', color: 'var(--text-dim)' }
  if (s <= 25) return { text: 'Très Faible', color: '#ef4444' }
  if (s <= 50) return { text: 'Moyen', color: '#f59e0b' }
  if (s <= 75) return { text: 'Robuste', color: '#3b82f6' }
  return { text: 'Excellent', color: '#10b981' }
})

const isPasswordFormValid = computed(() => {
  return (
    oldPassword.value.trim().length > 0 &&
    newPassword.value.length >= 8 &&
    confirmPassword.value === newPassword.value
  )
})

// --- Copie dans le presse-papier ---
const copyEmailToClipboard = () => {
  if (!props.user?.email) return
  navigator.clipboard.writeText(props.user.email)
  copiedEmail.value = true
  emit('showToast', 'Adresse e-mail copiée dans le presse-papier')
  setTimeout(() => {
    copiedEmail.value = false
  }, 2500)
}

// --- Mode Édition du Nom ---
const startEditingName = () => {
  editedFullName.value = props.user?.full_name || ''
  isEditingName.value = true
}

const cancelEditingName = () => {
  isEditingName.value = false
  editedFullName.value = ''
}

const saveFullName = async () => {
  if (!editedFullName.value || editedFullName.value.trim().length < 2) {
    emit('showToast', 'Le nom doit comporter au moins 2 caractères.', 'error')
    return
  }

  isSavingName.value = true
  const API_BASE = window.location.origin + '/api/v1/auth'
  const token = localStorage.getItem('access_token')

  try {
    const res = await fetch(`${API_BASE}/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        full_name: editedFullName.value.trim()
      })
    })

    if (res.ok) {
      const updatedUser = await res.json()
      emit('showToast', 'Votre nom a été mis à jour avec succès !')
      emit('userUpdated', updatedUser)
      isEditingName.value = false
    } else {
      const err = await res.json()
      emit('showToast', err.detail || 'Erreur lors de la mise à jour du profil.', 'error')
    }
  } catch (err) {
    emit('showToast', 'Impossible de contacter le serveur.', 'error')
  } finally {
    isSavingName.value = false
  }
}

// --- Soumission du mot de passe ---
const handleChangePassword = async () => {
  if (!isPasswordFormValid.value) {
    if (newPassword.value !== confirmPassword.value) {
      emit('showToast', 'La confirmation ne correspond pas au nouveau mot de passe.', 'error')
    } else if (newPassword.value.length < 8) {
      emit('showToast', 'Le mot de passe doit comporter au moins 8 caractères.', 'error')
    }
    return
  }

  isUpdatingPassword.value = true
  const API_BASE = window.location.origin + '/api/v1/auth'
  const token = localStorage.getItem('access_token')

  try {
    const res = await fetch(`${API_BASE}/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        old_password: oldPassword.value,
        new_password: newPassword.value
      })
    })
    const data = await res.json()

    if (res.ok) {
      emit('showToast', 'Mot de passe sécurisé et mis à jour avec succès !')
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      emit('showToast', data.detail || 'Ancien mot de passe incorrect.', 'error')
    }
  } catch (err) {
    emit('showToast', 'Erreur de connexion au serveur.', 'error')
  } finally {
    isUpdatingPassword.value = false
  }
}
</script>

<template>
  <div class="profile-container">

    <!-- ======================================================================= -->
    <!-- 1. HERO HEADER PROFILE CARD (DESIGN PREMIUM ACTIA)                     -->
    <!-- ======================================================================= -->
    <div class="hero-profile-card">
      <div class="hero-glow-orb orb-primary"></div>
      <div class="hero-glow-orb orb-secondary"></div>

      <div class="hero-content">
        <!-- Avatar avec halo & indicateur de présence -->
        <div class="avatar-wrapper">
          <div class="avatar-ring">
            <div class="avatar-core">
              {{ userInitials }}
            </div>
          </div>
          <div class="presence-badge" title="Session active et authentifiée">
            <span class="presence-dot"></span>
          </div>
        </div>

        <!-- Informations d'identité principales -->
        <div class="identity-info">
          <div class="identity-header-row">
            <div class="name-edit-group" v-if="!isEditingName">
              <h1 class="user-display-name">{{ props.user?.full_name || 'Utilisateur PlatformActia' }}</h1>
              <button class="btn-icon-subtle" @click="startEditingName" title="Modifier le nom affiché">
                <Edit3 :size="16" />
              </button>
            </div>

            <!-- Mode édition inline du nom -->
            <div class="name-inline-form" v-else>
              <input
                type="text"
                v-model="editedFullName"
                class="form-input inline-name-input"
                placeholder="Votre nom complet"
                @keyup.enter="saveFullName"
                @keyup.esc="cancelEditingName"
                autofocus
              />
              <button class="btn-inline-action btn-save" @click="saveFullName" :disabled="isSavingName">
                <Check :size="15" /> <span>{{ isSavingName ? '...' : 'Valider' }}</span>
              </button>
              <button class="btn-inline-action btn-cancel" @click="cancelEditingName">
                <span>Annuler</span>
              </button>
            </div>

            <!-- Badges de rôle & statut -->
            <div class="role-status-badges">
              <span v-if="isAdmin" class="badge-role-admin">
                <ShieldAlert :size="13" />
                <span>Administrateur Système</span>
              </span>
              <span v-else class="badge-role-user">
                <ShieldCheck :size="13" />
                <span>Responsable / Collaborateur HSE</span>
              </span>

              <span class="badge-status-approved">
                <CheckCircle2 :size="13" />
                <span>Compte Validé</span>
              </span>
            </div>
          </div>

          <!-- Ligne méta : Identifiant, Email, Entreprise -->
          <div class="identity-meta-row">
            <div class="meta-item email-meta" @click="copyEmailToClipboard" title="Cliquer pour copier l'e-mail">
              <Mail :size="14" class="meta-icon" />
              <span class="meta-text">{{ props.user?.email || 'email@actia.com' }}</span>
              <Copy :size="12" class="copy-icon" :class="{ 'copied': copiedEmail }" />
            </div>

            <div class="meta-separator">·</div>

            <div class="meta-item">
              <Building2 :size="14" class="meta-icon" />
              <span class="meta-text">CIPI ACTIA · Usine de Tunis</span>
            </div>

            <div class="meta-separator">·</div>

            <div class="meta-item">
              <Calendar :size="14" class="meta-icon" />
              <span class="meta-text">Inscrit le {{ formattedRegistrationDate }}</span>
            </div>

            <div class="meta-separator">·</div>

            <div class="meta-item id-badge-item">
              <span class="id-mono-tag">#ACTIA-{{ props.user?.id || '1' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation par onglets moderne -->
      <div class="profile-tabs-bar">
        <button
          class="tab-btn"
          :class="{ 'active': activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          <User :size="16" />
          <span>Vue d'ensemble</span>
        </button>

        <button
          class="tab-btn"
          :class="{ 'active': activeTab === 'security' }"
          @click="activeTab = 'security'"
        >
          <Lock :size="16" />
          <span>Sécurité & Mot de passe</span>
        </button>

        <button
          class="tab-btn"
          :class="{ 'active': activeTab === 'permissions' }"
          @click="activeTab = 'permissions'"
        >
          <Shield :size="16" />
          <span>Habilitations & Accès</span>
        </button>
      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- 2. ONGLET 1 : VUE D'ENSEMBLE & ACTIVITÉ                                 -->
    <!-- ======================================================================= -->
    <div v-if="activeTab === 'overview'" class="tab-content-anim">
      <!-- Grille des statistiques personnelles de participation -->
      <div class="kpi-summary-grid">
        <div class="kpi-mini-card">
          <div class="kpi-icon-bubble bubble-emerald">
            <FileText :size="20" />
          </div>
          <div class="kpi-mini-details">
            <span class="kpi-mini-label">Fiches Soumises</span>
            <div class="kpi-mini-val">{{ userAuditsCount }}</div>
            <span class="kpi-mini-sub">Contribué sur la plateforme</span>
          </div>
        </div>

        <div class="kpi-mini-card">
          <div class="kpi-icon-bubble bubble-teal">
            <Award :size="20" />
          </div>
          <div class="kpi-mini-details">
            <span class="kpi-mini-label">Moyenne de Conformité</span>
            <div class="kpi-mini-val" :style="{ color: userAvgConformity >= 80 ? '#10b981' : '#f59e0b' }">
              {{ userAvgConformity > 0 ? userAvgConformity + ' %' : '—' }}
            </div>
            <span class="kpi-mini-sub">Sur vos évaluations enregistrées</span>
          </div>
        </div>

        <div class="kpi-mini-card">
          <div class="kpi-icon-bubble bubble-indigo">
            <Clock :size="20" />
          </div>
          <div class="kpi-mini-details">
            <span class="kpi-mini-label">Dernière Évaluation</span>
            <div class="kpi-mini-val font-sm">{{ lastAuditDate }}</div>
            <span class="kpi-mini-sub">Dernière saisie terrain</span>
          </div>
        </div>

        <div class="kpi-mini-card">
          <div class="kpi-icon-bubble bubble-purple">
            <ShieldCheck :size="20" />
          </div>
          <div class="kpi-mini-details">
            <span class="kpi-mini-label">Intégrité & Statut</span>
            <div class="kpi-mini-val text-emerald">100 %</div>
            <span class="kpi-mini-sub">Compte vérifié & actif</span>
          </div>
        </div>
      </div>

      <!-- Détails structurés du profil -->
      <div class="profile-details-grid">
        <!-- Carte Informations Personnelles -->
        <div class="glass-card detail-section-card">
          <div class="section-card-header">
            <div class="section-header-title">
              <User :size="18" class="text-primary" />
              <h3>Informations du Collaborateur</h3>
            </div>
            <button class="btn-action-small" @click="startEditingName" v-if="!isEditingName">
              <Edit3 :size="13" /> Modifier
            </button>
          </div>

          <div class="info-rows-list">
            <div class="info-row-item">
              <span class="info-label">Nom et Prénom</span>
              <span class="info-val-highlight">{{ props.user?.full_name || '—' }}</span>
            </div>

            <div class="info-row-item">
              <span class="info-label">Adresse Électronique</span>
              <div class="info-val-with-badge">
                <span class="info-val">{{ props.user?.email || '—' }}</span>
                <span class="pill-verified">✓ Vérifié</span>
              </div>
            </div>

            <div class="info-row-item">
              <span class="info-label">Identifiant Unique</span>
              <span class="info-val font-mono">#ACTIA-{{ props.user?.id }}</span>
            </div>

            <div class="info-row-item">
              <span class="info-label">Rôle Attribué</span>
              <span class="info-val">{{ isAdmin ? 'Administrateur HSE (Plein Accès)' : 'Responsable / Auditeur HSE' }}</span>
            </div>
          </div>
        </div>

        <!-- Carte Organisation & Rattachement Usine -->
        <div class="glass-card detail-section-card">
          <div class="section-card-header">
            <div class="section-header-title">
              <Building2 :size="18" class="text-accent" />
              <h3>Rattachement & Établissement</h3>
            </div>
            <span class="pill-plant">Site Certifié ISO 45001</span>
          </div>

          <div class="info-rows-list">
            <div class="info-row-item">
              <span class="info-label">Entreprise</span>
              <span class="info-val">CIPI ACTIA</span>
            </div>

            <div class="info-row-item">
              <span class="info-label">Département</span>
              <span class="info-val">Qualité, Hygiène, Sécurité & Environnement (QHSE)</span>
            </div>

            <div class="info-row-item">
              <span class="info-label">Emplacement</span>
              <span class="info-val">Zone Industrielle Chotrana, Tunis</span>
            </div>

            <div class="info-row-item">
              <span class="info-label">Base de données</span>
              <span class="info-val text-primary">Données Centralisées Usine (Multi-utilisateurs)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- 3. ONGLET 2 : SÉCURITÉ & MOT DE PASSE                                   -->
    <!-- ======================================================================= -->
    <div v-if="activeTab === 'security'" class="tab-content-anim">
      <div class="security-split-layout">
        
        <!-- Formulaire de Changement de mot de passe -->
        <div class="glass-card security-form-card">
          <div class="section-card-header">
            <div class="section-header-title">
              <Key :size="18" class="text-primary" />
              <h3>Changer le mot de passe</h3>
            </div>
          </div>

          <p class="form-instruction-text">
            Pour garantir la sécurité de votre compte et des audits de l'usine, choisissez un mot de passe robuste d'au moins 8 caractères.
          </p>

          <form @submit.prevent="handleChangePassword" autocomplete="off" class="security-form">
            <!-- Champs leurres anti-autofill intempestif -->
            <input type="text" style="display:none" aria-hidden="true" />
            <input type="password" style="display:none" aria-hidden="true" />

            <!-- 1. Ancien mot de passe -->
            <div class="form-group-modern">
              <label class="form-label-modern">
                <Lock :size="14" /> Mot de passe actuel
              </label>
              <div class="input-with-eye-wrapper">
                <input
                  :type="showOldPassword ? 'text' : 'password'"
                  class="form-input-modern"
                  placeholder="Saisissez votre mot de passe actuel"
                  v-model="oldPassword"
                  autocomplete="new-password"
                  required
                />
                <button
                  type="button"
                  class="toggle-eye-btn"
                  @click="showOldPassword = !showOldPassword"
                  tabindex="-1"
                >
                  <EyeOff v-if="showOldPassword" :size="16" />
                  <Eye v-else :size="16" />
                </button>
              </div>
            </div>

            <!-- 2. Nouveau mot de passe -->
            <div class="form-group-modern">
              <label class="form-label-modern">
                <Key :size="14" /> Nouveau mot de passe
              </label>
              <div class="input-with-eye-wrapper">
                <input
                  :type="showNewPassword ? 'text' : 'password'"
                  class="form-input-modern"
                  placeholder="Minimum 8 caractères"
                  v-model="newPassword"
                  autocomplete="new-password"
                  required
                />
                <button
                  type="button"
                  class="toggle-eye-btn"
                  @click="showNewPassword = !showNewPassword"
                  tabindex="-1"
                >
                  <EyeOff v-if="showNewPassword" :size="16" />
                  <Eye v-else :size="16" />
                </button>
              </div>
            </div>

            <!-- Jauge visuelle de robustesse -->
            <div class="strength-meter-box" v-if="newPassword">
              <div class="strength-header">
                <span class="strength-title">Force du mot de passe :</span>
                <span class="strength-status" :style="{ color: passwordStrengthLabel.color }">
                  {{ passwordStrengthLabel.text }}
                </span>
              </div>
              <div class="meter-bar-track">
                <div
                  class="meter-bar-fill"
                  :style="{
                    width: passwordStrengthScore + '%',
                    backgroundColor: passwordStrengthLabel.color
                  }"
                ></div>
              </div>
            </div>

            <!-- 3. Confirmation du nouveau mot de passe -->
            <div class="form-group-modern">
              <label class="form-label-modern">
                <CheckCircle2 :size="14" /> Confirmer le nouveau mot de passe
              </label>
              <div class="input-with-eye-wrapper">
                <input
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-input-modern"
                  :class="{
                    'input-success': confirmPassword && newPassword === confirmPassword,
                    'input-error': confirmPassword && newPassword !== confirmPassword
                  }"
                  placeholder="Confirmez à l'identique"
                  v-model="confirmPassword"
                  autocomplete="new-password"
                  required
                />
                <button
                  type="button"
                  class="toggle-eye-btn"
                  @click="showConfirmPassword = !showConfirmPassword"
                  tabindex="-1"
                >
                  <EyeOff v-if="showConfirmPassword" :size="16" />
                  <Eye v-else :size="16" />
                </button>
              </div>

              <!-- Message de validation en direct -->
              <div v-if="confirmPassword" class="validation-message">
                <span v-if="newPassword === confirmPassword" class="val-match text-emerald">
                  ✓ Les mots de passe correspondent parfaitement.
                </span>
                <span v-else class="val-mismatch text-rose">
                  ✗ Les mots de passe ne correspondent pas.
                </span>
              </div>
            </div>

            <!-- Bouton d'action -->
            <button
              type="submit"
              class="btn-submit-password"
              :disabled="!isPasswordFormValid || isUpdatingPassword"
            >
              <Save :size="17" />
              <span>{{ isUpdatingPassword ? 'Mise à jour en cours...' : 'Enregistrer le nouveau mot de passe' }}</span>
            </button>
          </form>
        </div>

        <!-- Volet latéral : Recommandations & Normes -->
        <div class="security-standards-column">
          <div class="glass-card advice-card">
            <h4 class="advice-title">
              <ShieldCheck :size="18" class="text-primary" /> Standards de Sécurité Actia
            </h4>
            <ul class="checklist-items">
              <li :class="{ 'checked': passwordCriteria.length }">
                <Check v-if="passwordCriteria.length" :size="14" class="check-icon" />
                <span v-else class="circle-bullet"></span>
                <span>8 caractères minimum</span>
              </li>
              <li :class="{ 'checked': passwordCriteria.hasUpper }">
                <Check v-if="passwordCriteria.hasUpper" :size="14" class="check-icon" />
                <span v-else class="circle-bullet"></span>
                <span>Au moins une lettre majuscule (A-Z)</span>
              </li>
              <li :class="{ 'checked': passwordCriteria.hasNumber }">
                <Check v-if="passwordCriteria.hasNumber" :size="14" class="check-icon" />
                <span v-else class="circle-bullet"></span>
                <span>Au moins un chiffre (0-9)</span>
              </li>
              <li :class="{ 'checked': passwordCriteria.hasSpecial }">
                <Check v-if="passwordCriteria.hasSpecial" :size="14" class="check-icon" />
                <span v-else class="circle-bullet"></span>
                <span>Au moins un caractère spécial (@#$%!*&...)</span>
              </li>
            </ul>
          </div>

          <div class="glass-card crypto-info-card">
            <h4 class="crypto-title">
              <Sparkles :size="16" class="text-accent" /> Protection Cryptographique
            </h4>
            <p class="crypto-desc">
              Tous les mots de passe sont hachés de manière irréversible via l'algorithme robuste <strong>Bcrypt (Salt 12 rounds)</strong>. Aucune clé n'est conservée en clair dans le système.
            </p>
          </div>
        </div>

      </div>
    </div>

    <!-- ======================================================================= -->
    <!-- 4. ONGLET 3 : HABILITATIONS & ACCÈS                                     -->
    <!-- ======================================================================= -->
    <div v-if="activeTab === 'permissions'" class="tab-content-anim">
      <div class="glass-card permissions-card">
        <div class="section-card-header">
          <div class="section-header-title">
            <Shield :size="18" class="text-primary" />
            <h3>Matrice des Droits et Habilitations Système</h3>
          </div>
          <span class="role-badge-pill" :class="isAdmin ? 'pill-admin' : 'pill-user'">
            Rôle Actuel : {{ isAdmin ? 'ADMIN' : 'USER' }}
          </span>
        </div>

        <p class="permissions-intro">
          Récapitulatif des modules et privilèges opérationnels associés à votre compte au sein de l'usine :
        </p>

        <div class="permissions-matrix-list">
          <!-- Module 1 : Saisie Formulaires -->
          <div class="perm-row">
            <div class="perm-info">
              <div class="perm-icon-box box-emerald">
                <FileText :size="18" />
              </div>
              <div>
                <strong class="perm-name">Formulaires & Contrôles Terrain HSE</strong>
                <p class="perm-desc">Création et enregistrement des Audits HSE (FGSI-001), Tournées (FGSI-010), Permis de travail et Statistiques SST.</p>
              </div>
            </div>
            <div v-if="isAdmin" class="perm-status-tag tag-granted">
              <CheckCircle2 :size="14" /> Accès Autorisé (ADMIN)
            </div>
            <div v-else class="perm-status-tag tag-locked">
              <Lock :size="14" /> Réservé Administrateur
            </div>
          </div>

          <!-- Module 2 : Historique Centralisé -->
          <div class="perm-row">
            <div class="perm-info">
              <div class="perm-icon-box" :class="isAdmin ? 'box-teal' : 'box-gray'">
                <Clock :size="18" />
              </div>
              <div>
                <strong class="perm-name">Historique Centralisé des Audits</strong>
                <p class="perm-desc">Recherche multicritère, filtrage par date/secteur, consultation unitaire et impression de toutes les fiches d'usine.</p>
              </div>
            </div>
            <div v-if="isAdmin" class="perm-status-tag tag-granted">
              <CheckCircle2 :size="14" /> Accès Autorisé (ADMIN)
            </div>
            <div v-else class="perm-status-tag tag-locked">
              <Lock :size="14" /> Réservé Administrateur
            </div>
          </div>

          <!-- Module 3 : Dashboard & KPIs -->
          <div class="perm-row">
            <div class="perm-info">
              <div class="perm-icon-box box-blue">
                <Activity :size="18" />
              </div>
              <div>
                <strong class="perm-name">Tableau de Bord & Indicateurs KPIs</strong>
                <p class="perm-desc">Visualisation des taux de conformité, répartition des plans d'action et graphiques analytiques en temps réel.</p>
              </div>
            </div>
            <div class="perm-status-tag tag-granted">
              <CheckCircle2 :size="14" /> Accès Autorisé
            </div>
          </div>

          <!-- Module 4 : Administration Utilisateurs -->
          <div class="perm-row">
            <div class="perm-info">
              <div class="perm-icon-box" :class="isAdmin ? 'box-purple' : 'box-gray'">
                <ShieldAlert :size="18" />
              </div>
              <div>
                <strong class="perm-name">Gestion Administrative des Utilisateurs</strong>
                <p class="perm-desc">Validation des nouveaux comptes, attribution des rôles ADMIN/USER, suspensions et audits de conformité.</p>
              </div>
            </div>
            <div v-if="isAdmin" class="perm-status-tag tag-granted">
              <CheckCircle2 :size="14" /> Administrateur Actif
            </div>
            <div v-else class="perm-status-tag tag-locked">
              <Lock :size="14" /> Réservé Administrateur
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* =============================================================================
   CONTENEUR PRINCIPAL DU PROFIL
============================================================================= */
.profile-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 2rem;
}

/* =============================================================================
   1. HERO PROFILE CARD
============================================================================= */
.hero-profile-card {
  position: relative;
  background: rgba(0, 24, 32, 0.82);
  border: 1px solid rgba(0, 201, 150, 0.28);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  padding: 2.25rem 2.5rem 0 2.5rem;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.45);
  overflow: hidden;
}

/* Orbes lumineux en arrière-plan */
.hero-glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(65px);
  pointer-events: none;
  opacity: 0.22;
}

.orb-primary {
  width: 280px;
  height: 280px;
  background: var(--color-primary);
  top: -80px;
  right: 5%;
}

.orb-secondary {
  width: 240px;
  height: 240px;
  background: #6366f1;
  bottom: 0;
  left: 2%;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 2rem;
  padding-bottom: 2rem;
}

@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 1.25rem;
  }
}

/* --- Avatar & Halo --- */
.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar-ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #3b82f6 50%, #a855f7 100%);
  box-shadow: 0 0 25px rgba(0, 201, 150, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-core {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #00171f;
  color: var(--color-primary);
  font-size: 2.25rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  letter-spacing: -1px;
}

.presence-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  background: #001217;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.presence-dot {
  width: 10px;
  height: 10px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 8px #10b981;
}

/* --- Identité & Métadonnées --- */
.identity-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.identity-header-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

@media (max-width: 768px) {
  .identity-header-row {
    justify-content: center;
  }
}

.name-edit-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-display-name {
  font-size: 1.65rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  margin: 0;
}

.btn-icon-subtle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon-subtle:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(0, 201, 150, 0.1);
}

/* Édition de nom inline */
.name-inline-form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.inline-name-input {
  font-size: 1.1rem;
  font-weight: 700;
  padding: 6px 12px;
  max-width: 260px;
}

.btn-inline-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-save {
  background: var(--color-primary);
  color: #00171f;
}

.btn-save:hover {
  background: var(--color-accent-light);
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* Badges rôle & statut */
.role-status-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge-role-admin {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge-role-user {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(0, 201, 150, 0.12);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.35);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge-status-approved {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}

/* Ligne des métadonnées */
.identity-meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .identity-meta-row {
    justify-content: center;
  }
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.meta-icon {
  color: var(--color-primary);
}

.email-meta {
  cursor: pointer;
  padding: 3px 6px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.email-meta:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.copy-icon {
  color: var(--text-dim);
  transition: all 0.2s ease;
}

.copy-icon.copied {
  color: #10b981;
  transform: scale(1.2);
}

.meta-separator {
  color: var(--text-dim);
  font-weight: 700;
}

.id-mono-tag {
  font-family: var(--font-mono);
  background: rgba(0, 201, 150, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.25);
  padding: 2px 7px;
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 700;
}

/* --- Barre d'onglets intégrée au Hero --- */
.profile-tabs-bar {
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 0.5rem;
  overflow-x: auto;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 1rem 1.25rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  position: relative;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #fff;
}

.tab-btn.active {
  color: var(--color-primary);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--color-primary);
  border-radius: 3px 3px 0 0;
  box-shadow: 0 0 10px var(--color-primary);
}

/* =============================================================================
   ANIMATION D'ENTRÉE DES ONGLETS
============================================================================= */
.tab-content-anim {
  animation: tabFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@keyframes tabFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* =============================================================================
   2. GRILLE DES KPIS MINI (STATISTIQUES PERSONNELLES)
============================================================================= */
.kpi-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.kpi-mini-card {
  background: rgba(0, 32, 42, 0.7);
  border: 1px solid rgba(0, 201, 150, 0.2);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.1rem;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  transition: transform 0.25s ease, border-color 0.25s ease;
}

.kpi-mini-card:hover {
  transform: translateY(-3px);
  border-color: rgba(0, 201, 150, 0.45);
}

.kpi-icon-bubble {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bubble-emerald {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.3);
}

.bubble-teal {
  background: rgba(168, 224, 99, 0.15);
  color: var(--color-accent-light);
  border: 1px solid rgba(168, 224, 99, 0.3);
}

.bubble-indigo {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.bubble-purple {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.kpi-mini-details {
  display: flex;
  flex-direction: column;
}

.kpi-mini-label {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.4px;
}

.kpi-mini-val {
  font-size: 1.55rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.2;
}

.kpi-mini-val.font-sm {
  font-size: 1.15rem;
}

.kpi-mini-sub {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* =============================================================================
   GRILLE DES DÉTAILS DE PROFIL (VUE D'ENSEMBLE)
============================================================================= */
.profile-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1.5rem;
}

.detail-section-card {
  padding: 1.75rem;
}

.section-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.section-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-header-title h3 {
  font-size: 1.05rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
}

.btn-action-small {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(0, 201, 150, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.3);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action-small:hover {
  background: var(--color-primary);
  color: #00171f;
}

.pill-plant {
  background: rgba(168, 224, 99, 0.12);
  color: var(--color-accent-light);
  border: 1px solid rgba(168, 224, 99, 0.3);
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 700;
}

.info-rows-list {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.info-row-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.info-label {
  font-size: 0.73rem;
  color: var(--text-dim);
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.info-val {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
}

.info-val-highlight {
  font-size: 1.05rem;
  font-weight: 800;
  color: #fff;
}

.info-val-with-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pill-verified {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* =============================================================================
   3. ONGLET SÉCURITÉ : DISPOSITION & FORMULAIRE
============================================================================= */
.security-split-layout {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .security-split-layout {
    grid-template-columns: 1fr;
  }
}

.security-form-card {
  padding: 2rem;
}

.form-instruction-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.security-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group-modern {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label-modern {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #cbd5e1;
}

.input-with-eye-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input-modern {
  width: 100%;
  padding: 11px 44px 11px 14px;
  background: rgba(0, 18, 24, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  color: #fff;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.form-input-modern:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 201, 150, 0.18);
  background: rgba(0, 24, 32, 0.9);
}

.form-input-modern.input-success {
  border-color: #10b981;
}

.form-input-modern.input-error {
  border-color: #ef4444;
}

.toggle-eye-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.toggle-eye-btn:hover {
  color: var(--color-primary);
}

/* Jauge de mot de passe */
.strength-meter-box {
  background: rgba(0, 24, 32, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}

.strength-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.75rem;
}

.strength-title {
  color: var(--text-muted);
}

.strength-status {
  font-weight: 800;
}

.meter-bar-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.meter-bar-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 3px;
}

.validation-message {
  font-size: 0.78rem;
  font-weight: 600;
  margin-top: 2px;
}

.btn-submit-password {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--color-primary);
  color: #00141a;
  border: none;
  padding: 13px 20px;
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-weight: 800;
  cursor: pointer;
  margin-top: 0.5rem;
  box-shadow: 0 4px 15px rgba(0, 201, 150, 0.25);
  transition: all 0.25s ease;
}

.btn-submit-password:hover:not(:disabled) {
  background: var(--color-accent-light);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(168, 224, 99, 0.35);
}

.btn-submit-password:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Colonne Recommandations */
.security-standards-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.advice-card, .crypto-info-card {
  padding: 1.5rem;
}

.advice-title, .crypto-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 1rem;
}

.checklist-items {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checklist-items li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.82rem;
  color: var(--text-muted);
  transition: color 0.2s ease;
}

.checklist-items li.checked {
  color: #34d399;
  font-weight: 700;
}

.circle-bullet {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1.5px solid var(--text-dim);
  display: inline-block;
  flex-shrink: 0;
}

.check-icon {
  color: #10b981;
  flex-shrink: 0;
}

.crypto-desc {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* =============================================================================
   4. ONGLET HABILITATIONS
============================================================================= */
.permissions-card {
  padding: 2rem;
}

.permissions-intro {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.role-badge-pill {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 20px;
}

.pill-admin {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.pill-user {
  background: rgba(0, 201, 150, 0.18);
  color: var(--color-primary);
  border: 1px solid rgba(0, 201, 150, 0.4);
}

.permissions-matrix-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.perm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  background: rgba(0, 18, 24, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.perm-row:hover {
  background: rgba(0, 24, 32, 0.8);
  border-color: rgba(0, 201, 150, 0.25);
  transform: translateX(4px);
}

.perm-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.perm-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.box-emerald {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
}

.box-teal {
  background: rgba(168, 224, 99, 0.15);
  color: var(--color-accent-light);
}

.box-blue {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

.box-purple {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
}

.box-gray {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-dim);
}

.perm-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #fff;
  display: block;
  margin-bottom: 2px;
}

.perm-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0;
}

.perm-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 8px;
  white-space: nowrap;
}

.tag-granted {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.tag-locked {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-dim);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* =============================================================================
   COULEURS UTILITAIRES
============================================================================= */
.text-primary { color: var(--color-primary); }
.text-accent { color: var(--color-accent-light); }
.text-emerald { color: #10b981; }
.text-rose { color: #f43f5e; }
.font-mono { font-family: var(--font-mono); }
</style>
