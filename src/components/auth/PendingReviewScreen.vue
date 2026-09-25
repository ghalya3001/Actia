<!--
=============================================================================
Composant : PendingReviewScreen.vue
Description : Écran d'attente d'approbation pour les comptes avec status = 'PENDING'.
Fonctionnalités :
  - Message explicatif bienveillant pour l'utilisateur.
  - Récapitulatif des informations du compte soumis.
  - Bouton "Actualiser le statut" (interroge /api/v1/auth/me).
  - Bouton de déconnexion sécurisée.
=============================================================================
-->

<script setup>
import { ref } from 'vue'
import { Clock, RefreshCw, LogOut, ShieldCheck, Mail, User, AlertCircle } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['checkStatus', 'logout', 'showToast'])

const isChecking = ref(false)

const handleCheck = async () => {
  isChecking.value = true
  try {
    await emit('checkStatus')
  } finally {
    setTimeout(() => {
      isChecking.value = false
    }, 600)
  }
}
</script>

<template>
  <div class="pending-screen-wrapper">
    <div class="glass-card pending-card page-anim">
      <!-- En-tête : Badge et Icône Horloge animée -->
      <div class="icon-bubble">
        <Clock :size="40" class="clock-icon" />
      </div>

      <div class="status-badge-pending">
        Compte en attente de validation
      </div>

      <h2 class="pending-title">Votre compte est en cours d'examen</h2>

      <p class="pending-desc">
        Merci pour votre inscription sur la plateforme <strong>CIPI ACTIA</strong>. 
        Pour garantir la sécurité et la conformité des données du site, chaque nouvelle demande d'accès 
        doit être validée par un administrateur HSE avant ouverture des droits.
      </p>

      <!-- Carte d'informations du profil -->
      <div class="user-info-box">
        <div class="info-row">
          <div class="info-label"><User :size="15" /> Nom complet :</div>
          <div class="info-val">{{ props.user?.full_name || 'Utilisateur' }}</div>
        </div>
        <div class="info-row">
          <div class="info-label"><Mail :size="15" /> Adresse e-mail :</div>
          <div class="info-val">{{ props.user?.email || 'N/A' }}</div>
        </div>
        <div class="info-row">
          <div class="info-label"><ShieldCheck :size="15" /> Rôle sollicité :</div>
          <div class="info-val role-tag">{{ props.user?.role || 'USER' }}</div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-group">
        <button 
          class="btn btn-primary"
          :disabled="isChecking"
          @click="handleCheck"
          style="flex: 1; justify-content: center;"
        >
          <RefreshCw :size="16" :class="{ 'spin-anim': isChecking }" />
          {{ isChecking ? 'Vérification...' : 'Vérifier mon statut' }}
        </button>

        <button 
          class="btn btn-logout"
          @click="emit('logout')"
          style="justify-content: center;"
        >
          <LogOut :size="16" />
          Se déconnecter
        </button>
      </div>

      <!-- Note de bas de carte -->
      <div class="notice-footer">
        <AlertCircle :size="14" />
        <span>Si votre demande est urgente, contactez le Responsable HSE de votre secteur.</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pending-screen-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: radial-gradient(circle at 50% 20%, rgba(0, 201, 150, 0.08) 0%, rgba(0, 20, 26, 0.95) 75%);
}

.pending-card {
  max-width: 540px;
  width: 100%;
  padding: 2.5rem;
  text-align: center;
  border-radius: 16px;
  border: 1px solid rgba(251, 191, 36, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(251, 191, 36, 0.05);
}

.icon-bubble {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.25rem;
  border-radius: 50%;
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.4);
  color: #fbbf24;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-badge-pending {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.4);
  margin-bottom: 1rem;
}

.pending-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 0.85rem;
}

.pending-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.65;
  margin-bottom: 1.75rem;
}

.user-info-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 2rem;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
}

.info-label {
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.info-val {
  color: #ffffff;
  font-weight: 700;
}

.role-tag {
  background: rgba(0, 201, 150, 0.15);
  color: var(--color-primary);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
}

.actions-group {
  display: flex;
  gap: 12px;
  margin-bottom: 1.5rem;
}

.btn-logout {
  background: rgba(244, 63, 94, 0.1);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.3);
}

.btn-logout:hover {
  background: rgba(244, 63, 94, 0.2);
}

.notice-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.76rem;
  color: var(--text-dim);
}

.spin-anim {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
