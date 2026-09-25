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
import { LogIn, UserPlus, ShieldAlert, Mail, Lock, User, Send, CheckCircle2, ArrowLeft, Eye, EyeOff } from 'lucide-vue-next'

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
const showLoginPassword = ref(false)

// Champs du formulaire d'inscription
const regFullName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const showRegPassword = ref(false)

// Champs du parcours de réinitialisation par code OTP
const forgotEmail = ref('')
const otpStep = ref(1)              // 1: Demande du code, 2: Saisie du code et nouveau mot de passe
const generatedOtp = ref('')        // Code OTP généré renvoyé par l'API
const otpCodeInput = ref('')        // Code saisi par l'utilisateur
const otpNewPassword = ref('')      // Nouveau mot de passe choisi
const showOtpNewPassword = ref(false)
const showOtpModal = ref(false)     // Affichage de la modale de démonstration du code OTP
const loading = ref(false)

/**
 * Traite la connexion de l'utilisateur (OAuth2 Password Flow).
 */
const handleLogin = async () => {
  loading.value = true
  const API_BASE = window.location.origin + "/api/v1/auth"
  try {
    const params = new URLSearchParams()
    params.append('username', loginEmail.value.trim().toLowerCase())
    params.append('password', loginPassword.value)

    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    })
    const data = await res.json()

    if (res.ok) {
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      emit('loginSuccess', data.access_token, data)
      emit('showToast', 'Connexion réussie ! Bienvenue sur PlatformActia.')
    } else {
      emit('showToast', data.detail || 'Identifiants invalides', 'error')
    }
  } catch (err) {
    emit('showToast', 'Impossible de joindre le serveur API.', 'error')
  } finally {
    loading.value = false
  }
}

/**
 * Traite l'inscription d'un nouvel utilisateur.
 */
const handleRegister = async () => {
  loading.value = true
  const API_BASE = window.location.origin + "/api/v1/auth"
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: regEmail.value.trim().toLowerCase(),
        full_name: regFullName.value.trim(),
        password: regPassword.value
      })
    })
    const data = await res.json()

    if (res.ok) {
      emit('showToast', 'Votre compte a été créé avec succès ! Votre demande est en attente d\'approbation par l\'administrateur.')
      activeTab.value = 'login'
      loginEmail.value = regEmail.value
      loginPassword.value = ''
      regFullName.value = ''
      regEmail.value = ''
      regPassword.value = ''
    } else {
      emit('showToast', data.detail || 'Erreur lors de la création du compte.', 'error')
    }
  } catch (err) {
    emit('showToast', 'Impossible de joindre le serveur API.', 'error')
  } finally {
    loading.value = false
  }
}

/**
 * Étape 1 : Demande de génération du code OTP par email.
 */
const handleSendOTP = async () => {
  loading.value = true
  const API_BASE = window.location.origin + "/api/v1/auth"
  try {
    const res = await fetch(`${API_BASE}/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: forgotEmail.value.trim().toLowerCase() })
    })
    const data = await res.json()

    if (res.ok) {
      emit('showToast', data.message)
      if (data.otp_code) {
        generatedOtp.value = data.otp_code
        showOtpModal.value = true
      } else {
        otpStep.value = 2
      }
    } else {
      emit('showToast', data.detail || 'Erreur lors de la demande du code.', 'error')
    }
  } catch (err) {
    emit('showToast', 'Impossible de joindre le serveur API.', 'error')
  } finally {
    loading.value = false
  }
}

/**
 * Étape 2 : Réinitialisation définitive du mot de passe avec le code OTP validé.
 */
const handleResetWithOTP = async () => {
  loading.value = true
  const API_BASE = window.location.origin + "/api/v1/auth"
  try {
    const res = await fetch(`${API_BASE}/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: forgotEmail.value.trim().toLowerCase(),
        otp_code: otpCodeInput.value.trim(),
        new_password: otpNewPassword.value
      })
    })
    const data = await res.json()

    if (res.ok) {
      emit('showToast', data.message)
      activeTab.value = 'login'
      loginEmail.value = forgotEmail.value
      loginPassword.value = ''
      forgotEmail.value = ''
      otpCodeInput.value = ''
      otpNewPassword.value = ''
      otpStep.value = 1
    } else {
      emit('showToast', data.detail || 'Code invalide ou expiré.', 'error')
    }
  } catch (err) {
    emit('showToast', 'Impossible de joindre le serveur API.', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrapper">
    <div class="glass-card auth-card">
      <div style="text-align: center; margin-bottom: 2rem">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 16px; background: rgba(0,201,150,0.15); color: var(--color-primary); margin-bottom: 12px; border: 1px solid rgba(0,201,150,0.3)">
          <Lock :size="28" />
        </div>
        <h1 style="font-size: 1.6rem; font-weight: 800; color: #fff; letter-spacing: -0.5px">Platform<span style="color: var(--color-primary)">Actia</span></h1>
        <p style="font-size: 0.85rem; color: var(--text-dim); margin-top: 4px">Portail Sécurisé HSE & Supervision d'Usine</p>
      </div>

      <div style="display: flex; gap: 8px; background: rgba(0,0,0,0.25); padding: 4px; border-radius: 10px; margin-bottom: 1.5rem">
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
          <div class="password-input-wrapper">
            <input 
              :type="showLoginPassword ? 'text' : 'password'" 
              class="form-input" 
              placeholder="Votre mot de passe" 
              autocomplete="new-password" 
              v-model="loginPassword" 
              required 
            />
            <button 
              type="button" 
              class="btn-toggle-pwd" 
              @click="showLoginPassword = !showLoginPassword"
              tabindex="-1"
              title="Afficher / Masquer le mot de passe"
            >
              <EyeOff v-if="showLoginPassword" :size="16" />
              <Eye v-else :size="16" />
            </button>
          </div>
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
          <div class="password-input-wrapper">
            <input 
              :type="showRegPassword ? 'text' : 'password'" 
              class="form-input" 
              placeholder="Choisissez un mot de passe" 
              minlength="8" 
              autocomplete="new-password" 
              v-model="regPassword" 
              required 
            />
            <button 
              type="button" 
              class="btn-toggle-pwd" 
              @click="showRegPassword = !showRegPassword"
              tabindex="-1"
              title="Afficher / Masquer le mot de passe"
            >
              <EyeOff v-if="showRegPassword" :size="16" />
              <Eye v-else :size="16" />
            </button>
          </div>
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
          <div class="password-input-wrapper">
            <input 
              :type="showOtpNewPassword ? 'text' : 'password'" 
              class="form-input" 
              placeholder="Min 8 caractères" 
              minlength="8" 
              v-model="otpNewPassword" 
              required 
            />
            <button 
              type="button" 
              class="btn-toggle-pwd" 
              @click="showOtpNewPassword = !showOtpNewPassword"
              tabindex="-1"
              title="Afficher / Masquer le mot de passe"
            >
              <EyeOff v-if="showOtpNewPassword" :size="16" />
              <Eye v-else :size="16" />
            </button>
          </div>
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

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-card {
  width: 100%;
  max-width: 440px;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  padding-right: 42px !important;
  width: 100%;
}

.btn-toggle-pwd {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.btn-toggle-pwd:hover {
  color: var(--color-primary);
}
</style>
