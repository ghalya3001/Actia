<!--
===============================================================================
ÉCRAN D'AUTHENTIFICATION ET GESTION DE COMPTE (AUTHSCREEN.VUE)
===============================================================================
Rôle :
  Interface d'accueil sécurisée pour les utilisateurs non connectés :
  1. Onglet 'Connexion' :
     - Formulaire de saisie (Email / Mot de passe).
     - Transmission `application/x-www-form-urlencoded` vers `/api/v1/auth/login`.
     - Stockage local des jetons JWT (`access_token` et `refresh_token`).
  2. Onglet 'Inscription' :
     - Création d'un nouveau compte Manager (Nom, Email, Mot de passe 8 car. min).
     - Appel JSON vers `/api/v1/auth/register`.
  3. Onglet 'Mot de passe oublié' (Parcours OTP à 2 étapes) :
     - Étape 1 : Saisie de l'adresse email et génération d'un code OTP à 6 chiffres.
     - Dialogue modal présentant le code OTP avec pré-remplissage immédiat.
     - Étape 2 : Saisie du code OTP et définition du nouveau mot de passe.
===============================================================================
-->

<script setup>
import { ref } from 'vue'
import { LogIn, UserPlus, ShieldAlert, Mail, Lock, User, Send, CheckCircle2, ArrowLeft } from 'lucide-vue-next'

// --- Événements émis vers App.vue ---
// - loginSuccess : transmet le token JWT d'accès pour initialiser la session
// - showToast    : demande l'affichage d'un message temporaire d'information ou d'erreur
const emit = defineEmits(['loginSuccess', 'showToast'])

// --- États Réactifs de Navigation dans l'Écran d'Auth ---
// Onglet actif : 'login' (Connexion), 'register' (Inscription), 'forgot' (Mot de passe oublié)
const activeTab = ref('login')

// Champs du formulaire de connexion
const loginEmail = ref('')
const loginPassword = ref('')

// Champs du formulaire d'inscription
const regFullName = ref('')
const regEmail = ref('')
const regPassword = ref('')

// Champs du parcours de réinitialisation par code OTP
const forgotEmail = ref('')
const otpStep = ref(1)              // 1: Demande du code, 2: Saisie du code et nouveau mot de passe
const generatedOtp = ref('')        // Code OTP généré renvoyé par l'API
const otpCodeInput = ref('')        // Code saisi par l'utilisateur
const otpNewPassword = ref('')      // Nouveau mot de passe choisi
const showOtpModal = ref(false)     // Affichage de la modale de démonstration du code OTP

// Indicateur de chargement pour bloquer les clics multiples
const loading = ref(false)

// URL de base du module d'authentification
const API_BASE = window.location.origin + "/api/v1/auth"

/**
 * Formate les messages d'erreur renvoyés par FastAPI (chaîne simple, tableau Pydantic ou objet).
 * @param {string|Array|object} detail - Détail de l'erreur HTTP.
 * @param {string} defaultMsg - Message de secours par défaut.
 * @returns {string} Le message d'erreur lisible.
 */
const formatErrorDetail = (detail, defaultMsg) => {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0]?.msg ? `Erreur: ${detail[0].msg}` : defaultMsg
  }
  if (typeof detail === 'object' && detail !== null) {
    return detail.msg || detail.detail || defaultMsg
  }
  return defaultMsg
}

/**
 * Traite la soumission du formulaire de connexion via l'endpoint /login.
 */
const handleLogin = async () => {
  if (loading.value) return
  loading.value = true

  // Préparation du payload sous forme URLSearchParams conforme OAuth2 standard
  const formData = new URLSearchParams()
  formData.append('username', loginEmail.value)
  formData.append('password', loginPassword.value)

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    const data = await res.json()

    if (res.ok) {
      // Stockage sécurisé des jetons dans le localStorage du navigateur
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      emit('showToast', "Connexion réussie ! Bienvenue sur PlatformActia.")
      emit('loginSuccess', data.access_token)
    } else {
      emit('showToast', formatErrorDetail(data.detail, "Email ou mot de passe incorrect"), 'error')
    }
  } catch (err) {
    emit('showToast', "Erreur de connexion au serveur", 'error')
  } finally {
    loading.value = false
  }
}

/**
 * Traite l'enregistrement d'un nouveau compte via /register.
 */
const handleRegister = async () => {
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: regFullName.value,
        email: regEmail.value,
        password: regPassword.value
      })
    })
    const data = await res.json()

    if (res.ok) {
      emit('showToast', "Compte Responsable créé avec succès ! Connectez-vous.")
      regFullName.value = ''
      regEmail.value = ''
      regPassword.value = ''
      activeTab.value = 'login'
    } else {
      emit('showToast', formatErrorDetail(data.detail, "Erreur d'inscription"), 'error')
    }
  } catch (err) {
    emit('showToast', "Erreur de connexion au serveur", 'error')
  }
}

/**
 * Étape 1 : Demande l'émission d'un code OTP à 6 chiffres via /forgot-password.
 */
const handleSendOTP = async () => {
  try {
    const res = await fetch(`${API_BASE}/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: forgotEmail.value })
    })
    const data = await res.json()

    if (res.ok && data.otp_code) {
      generatedOtp.value = data.otp_code
      showOtpModal.value = true // Ouvre le dialogue affichant le code généré
    } else {
      emit('showToast', formatErrorDetail(data.detail, "Aucun compte associé à cet email"), 'error')
    }
  } catch (err) {
    emit('showToast', "Erreur lors de l'envoi de l'OTP", 'error')
  }
}

/**
 * Étape 2 : Valide le code OTP et applique le nouveau mot de passe via /reset-password.
 */
const handleResetWithOTP = async () => {
  try {
    const res = await fetch(`${API_BASE}/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: forgotEmail.value,
        otp_code: otpCodeInput.value,
        new_password: otpNewPassword.value
      })
    })
    const data = await res.json()

    if (res.ok) {
      emit('showToast', "Mot de passe réinitialisé ! Vous pouvez vous connecter.")
      otpStep.value = 1
      forgotEmail.value = ''
      otpCodeInput.value = ''
      otpNewPassword.value = ''
      activeTab.value = 'login'
    } else {
      emit('showToast', formatErrorDetail(data.detail, "Code OTP invalide"), 'error')
    }
  } catch (err) {
    emit('showToast', "Erreur de réinitialisation", 'error')
  }
}
</script>

<template>
  <div style="min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem">
    
    <!-- En-tête : Titre et Logo de l'application -->
    <div style="text-align: center; margin-bottom: 2rem">
      <div style="width: 60px; height: 60px; border-radius: 16px; background: var(--color-primary); color: #00141a; font-weight: 800; font-size: 2rem; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px">P</div>
      <h1 style="font-size: 2rem; font-weight: 800; color: #fff">PlatformActia</h1>
      <p style="font-size: 0.9rem; color: var(--text-muted)">Portail Sécurisé Responsable HSE · CIPI ACTIA</p>
    </div>

    <!-- Carte principale translucide (Glassmorphism) -->
    <div class="glass-card" style="width: 100%; max-width: 440px">
      
      <!-- Barre d'onglets de sélection (Connexion / Inscription / Oublié) -->
      <div style="display: flex; gap: 8px; border-bottom: 1px solid rgba(0,201,150,0.2); padding-bottom: 1rem; margin-bottom: 1.5rem">
        <button type="button" @click="activeTab = 'login'" :style="{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: activeTab === 'login' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'login' ? '#00141a' : 'var(--text-muted)', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }"><LogIn :size="16"/> Connexion</button>
        <button type="button" @click="activeTab = 'register'" :style="{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: activeTab === 'register' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'register' ? '#00141a' : 'var(--text-muted)', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }"><UserPlus :size="16"/> Inscription</button>
        <button type="button" @click="activeTab = 'forgot'" :style="{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: activeTab === 'forgot' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'forgot' ? '#00141a' : 'var(--text-muted)', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }"><ShieldAlert :size="16"/> Oublié</button>
      </div>

      <!-- =================================================================== -->
      <!-- FORMULAIRE 1 : CONNEXION OAUTH2                                     -->
      <!-- =================================================================== -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" autocomplete="off">
        <div class="form-group">
          <label class="form-label">Email Responsable</label>
          <input type="email" class="form-input" placeholder="ex: hamed@gmail.com" autocomplete="off" v-model="loginEmail" required />
        </div>
        <div class="form-group">
          <label class="form-label">Mot de passe</label>
          <input type="password" class="form-input" placeholder="Votre mot de passe" autocomplete="new-password" v-model="loginPassword" required />
        </div>
        <button type="submit" :disabled="loading" class="btn btn-primary" :style="{ width: '100%', marginTop: '1rem', opacity: loading ? 0.7 : 1 }">
          <LogIn :size="18"/> {{ loading ? "Connexion en cours..." : "Se Connecter" }}
        </button>
      </form>

      <!-- =================================================================== -->
      <!-- FORMULAIRE 2 : INSCRIPTION D'UN NOUVEAU COMPTE                      -->
      <!-- =================================================================== -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" autocomplete="off">
        <div class="form-group">
          <label class="form-label">Nom complet</label>
          <input type="text" class="form-input" placeholder="ex: Jean Dupont" autocomplete="off" v-model="regFullName" required />
        </div>
        <div class="form-group">
          <label class="form-label">Adresse Email</label>
          <input type="email" class="form-input" placeholder="ex: responsable@actia.com" autocomplete="off" v-model="regEmail" required />
        </div>
        <div class="form-group">
          <label class="form-label">Mot de passe (Min 8 caractères)</label>
          <input type="password" class="form-input" placeholder="Choisissez un mot de passe" minlength="8" autocomplete="new-password" v-model="regPassword" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem"><UserPlus :size="18"/> Créer le compte</button>
      </form>

      <!-- =================================================================== -->
      <!-- FORMULAIRE 3 : MOT DE PASSE OUBLIÉ (ÉTAPE 1 : DEMANDE OTP)          -->
      <!-- =================================================================== -->
      <form v-if="activeTab === 'forgot' && otpStep === 1" @submit.prevent="handleSendOTP">
        <div class="form-group">
          <label class="form-label">Adresse Email enregistrée</label>
          <input type="email" class="form-input" placeholder="ex: responsable@actia.com" v-model="forgotEmail" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem"><Send :size="18"/> Obtenir le code OTP</button>
      </form>

      <!-- =================================================================== -->
      <!-- FORMULAIRE 4 : MOT DE PASSE OUBLIÉ (ÉTAPE 2 : VALIDATION & NOUVEAU) -->
      <!-- =================================================================== -->
      <form v-if="activeTab === 'forgot' && otpStep === 2" @submit.prevent="handleResetWithOTP">
        <div class="form-group">
          <label class="form-label">Code OTP à 6 chiffres</label>
          <input type="text" class="form-input" placeholder="ex: 123456" maxlength="6" v-model="otpCodeInput" required />
        </div>
        <div class="form-group">
          <label class="form-label">Nouveau mot de passe</label>
          <input type="password" class="form-input" placeholder="Min 8 caractères" minlength="8" v-model="otpNewPassword" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem"><CheckCircle2 :size="18"/> Réinitialiser le mot de passe</button>
        <button type="button" class="btn btn-secondary" style="width: 100%; margin-top: 10px" @click="otpStep = 1"><ArrowLeft :size="16"/> Recommencer</button>
      </form>
    </div>

    <!-- ===================================================================== -->
    <!-- DIALOGUE MODAL : AFFICHAGE DU CODE OTP GÉNÉRÉ                         -->
    <!-- ===================================================================== -->
    <div v-if="showOtpModal" class="modal-overlay">
      <div class="modal-card" style="text-align: center">
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #fff">Code OTP de Sécurité</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin: 10px 0">Voici votre code temporaire pour la réinitialisation :</p>
        <!-- Boîte de mise en valeur du code à 6 chiffres -->
        <div style="background: rgba(0,201,150,0.15); border: 2px dashed var(--color-primary); border-radius: 12px; padding: 1rem; font-size: 1.8rem; font-weight: 800; color: var(--color-primary); letter-spacing: 4px; margin: 1rem 0">
          {{ generatedOtp }}
        </div>
        <button class="btn btn-primary" @click="otpCodeInput = generatedOtp; showOtpModal = false; otpStep = 2;">Continuer</button>
      </div>
    </div>
  </div>
</template>
