<!--
=============================================================================
Composant : AccountRejectedScreen.vue
Description : Écran d'information pour les comptes avec status = 'REJECTED'.
Fonctionnalités :
  - Affiche l'alerte de refus et le motif précis saisi par l'administrateur.
  - Bouton de déconnexion.
=============================================================================
-->

<script setup>
import { XCircle, LogOut, AlertTriangle, Mail } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['logout'])
</script>

<template>
  <div class="rejected-screen-wrapper">
    <div class="glass-card rejected-card page-anim">
      <!-- Icône de refus -->
      <div class="icon-bubble">
        <XCircle :size="42" />
      </div>

      <div class="status-badge-rejected">
        Demande d'accès non approuvée
      </div>

      <h2 class="rejected-title">Votre compte n'a pas été validé</h2>

      <p class="rejected-desc">
        Votre demande d'inscription pour l'adresse <strong>{{ props.user?.email }}</strong> a été examinée 
        par l'administrateur de la plateforme et n'a pas pu être acceptée.
      </p>

      <!-- Encadré du motif de rejet -->
      <div class="reason-box">
        <div class="reason-header">
          <AlertTriangle :size="16" />
          <span>Motif renseigné par l'administrateur :</span>
        </div>
        <p class="reason-text">
          {{ props.user?.rejection_reason || "Aucun motif spécifique n'a été communiqué. Veuillez vérifier auprès de votre responsable hiérarchique." }}
        </p>
      </div>

      <!-- Action -->
      <button class="btn btn-logout-full" @click="emit('logout')">
        <LogOut :size="16" />
        Se déconnecter
      </button>

      <div class="contact-notice">
        <Mail :size="14" />
        <span>Pour toute question ou contestation, contactez le support HSE : <strong>hse@actia.com</strong></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rejected-screen-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: radial-gradient(circle at 50% 20%, rgba(244, 63, 94, 0.08) 0%, rgba(0, 20, 26, 0.95) 75%);
}

.rejected-card {
  max-width: 520px;
  width: 100%;
  padding: 2.5rem;
  text-align: center;
  border-radius: 16px;
  border: 1px solid rgba(244, 63, 94, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(244, 63, 94, 0.06);
}

.icon-bubble {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.25rem;
  border-radius: 50%;
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.4);
  color: #f43f5e;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-badge-rejected {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(244, 63, 94, 0.15);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.4);
  margin-bottom: 1rem;
}

.rejected-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 0.85rem;
}

.rejected-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.65;
  margin-bottom: 1.75rem;
}

.reason-box {
  background: rgba(244, 63, 94, 0.06);
  border: 1px solid rgba(244, 63, 94, 0.2);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 2rem;
  text-align: left;
}

.reason-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #f43f5e;
  margin-bottom: 0.5rem;
}

.reason-text {
  font-size: 0.88rem;
  color: #ffffff;
  line-height: 1.5;
  font-weight: 600;
}

.btn-logout-full {
  width: 100%;
  justify-content: center;
  background: rgba(244, 63, 94, 0.15);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.35);
  margin-bottom: 1.5rem;
}

.btn-logout-full:hover {
  background: rgba(244, 63, 94, 0.25);
}

.contact-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.76rem;
  color: var(--text-dim);
}
</style>
