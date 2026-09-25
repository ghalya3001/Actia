<!--
=============================================================================
Composant : AccountSuspendedScreen.vue
Description : Écran d'information pour les comptes avec status = 'SUSPENDED'.
Fonctionnalités :
  - Affiche l'avis de suspension temporaire du compte.
  - Bouton de déconnexion.
=============================================================================
-->

<script setup>
import { ShieldAlert, LogOut, Mail } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['logout'])
</script>

<template>
  <div class="suspended-screen-wrapper">
    <div class="glass-card suspended-card page-anim">
      <!-- Icône de suspension -->
      <div class="icon-bubble">
        <ShieldAlert :size="42" />
      </div>

      <div class="status-badge-suspended">
        Compte suspendu
      </div>

      <h2 class="suspended-title">Accès temporairement suspendu</h2>

      <p class="suspended-desc">
        Le compte associé à l'adresse <strong>{{ props.user?.email }}</strong> a été suspendu 
        par la direction de la plateforme CIPI ACTIA. Toutes les autorisations d'accès aux formulaires 
        et indicateurs ont été temporairement révoquées.
      </p>

      <div class="notice-card">
        Pour toute demande de réactivation ou pour connaître les modalités de rétablissement de vos accès, 
        veuillez contacter directement le Responsable HSE ou l'administrateur système.
      </div>

      <!-- Action -->
      <button class="btn btn-logout-full" @click="emit('logout')">
        <LogOut :size="16" />
        Se déconnecter
      </button>

      <div class="contact-notice">
        <Mail :size="14" />
        <span>Contact administrateur : <strong>admin@actia.com</strong></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.suspended-screen-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: radial-gradient(circle at 50% 20%, rgba(249, 115, 22, 0.08) 0%, rgba(0, 20, 26, 0.95) 75%);
}

.suspended-card {
  max-width: 520px;
  width: 100%;
  padding: 2.5rem;
  text-align: center;
  border-radius: 16px;
  border: 1px solid rgba(249, 115, 22, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(249, 115, 22, 0.06);
}

.icon-bubble {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.25rem;
  border-radius: 50%;
  background: rgba(249, 115, 22, 0.12);
  border: 1px solid rgba(249, 115, 22, 0.4);
  color: #f97316;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-badge-suspended {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.4);
  margin-bottom: 1rem;
}

.suspended-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 0.85rem;
}

.suspended-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.65;
  margin-bottom: 1.5rem;
}

.notice-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  font-size: 0.84rem;
  color: #cbd5e1;
  line-height: 1.5;
  margin-bottom: 2rem;
  text-align: left;
}

.btn-logout-full {
  width: 100%;
  justify-content: center;
  background: rgba(249, 115, 22, 0.15);
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.35);
  margin-bottom: 1.5rem;
}

.btn-logout-full:hover {
  background: rgba(249, 115, 22, 0.25);
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
