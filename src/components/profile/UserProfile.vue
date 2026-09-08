<script setup>
import { ref, computed } from 'vue';
import { User, Mail, Shield, Lock, Save } from 'lucide-vue-next';

const props = defineProps(['user']);
const emit = defineEmits(['showToast']);

const oldPassword = ref('');
const newPassword = ref('');

const handleChangePassword = async () => {
  const API_BASE = window.location.origin + "/api/v1/auth";
  const token = localStorage.getItem("access_token");

  try {
    const res = await fetch(`${API_BASE}/change-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ old_password: oldPassword.value, new_password: newPassword.value })
    });
    const data = await res.json();
    if (res.ok) {
      emit('showToast', "Mot de passe mis à jour avec succès !");
      oldPassword.value = '';
      newPassword.value = '';
    } else {
      emit('showToast', data.detail || "Ancien mot de passe incorrect", 'error');
    }
  } catch (err) {
    emit('showToast', "Erreur lors de la mise à jour", 'error');
  }
};

const initial = computed(() => {
  return props.user?.full_name ? props.user.full_name.charAt(0).toUpperCase() : 'R';
});
</script>

<template>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem">
    
    <!-- PROFILE CARD -->
    <div class="glass-card">
      <div style="text-align: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(0,201,150,0.2)">
        <div style="width: 80px; height: 80px; border-radius: 50%; background: var(--color-primary); color: #00141a; font-weight: 800; font-size: 2.5rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px">
          {{ initial }}
        </div>
        <h2 style="font-size: 1.3rem; font-weight: 800; color: #fff">{{ props.user?.full_name || 'Responsable HSE' }}</h2>
        <div style="font-size: 0.85rem; color: var(--color-primary); font-weight: 700; margin-top: 2px">Responsable HSE · CIPI ACTIA</div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 1rem">
        <div>
          <span style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700">Identifiant Responsable</span>
          <div style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-top: 2px">#ACTIA-{{ props.user?.id || '1' }}</div>
        </div>
        <div>
          <span style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700">Adresse Email</span>
          <div style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-top: 2px">{{ props.user?.email || 'responsable@actia.com' }}</div>
        </div>
        <div>
          <span style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700">Site / Organisation</span>
          <div style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-top: 2px">CIPI ACTIA</div>
        </div>
      </div>
    </div>

    <!-- SECURITY CARD -->
    <div class="glass-card">
      <h3 style="font-size: 1.1rem; font-weight: 800; color: #fff; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px">
        <Shield :size="20" color="var(--color-primary)" /> Sécurité du Compte
      </h3>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem">
        Modifiez votre mot de passe pour sécuriser l'accès à vos données HSE.
      </p>

      <form @submit.prevent="handleChangePassword">
        <div class="form-group">
          <label class="form-label">Ancien mot de passe</label>
          <input type="password" class="form-input" placeholder="Mot de passe actuel" v-model="oldPassword" required />
        </div>
        <div class="form-group">
          <label class="form-label">Nouveau mot de passe (Min 8 caractères)</label>
          <input type="password" class="form-input" placeholder="Minimum 8 caractères" minlength="8" v-model="newPassword" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem">
          <Save :size="18" /> Mettre à jour le mot de passe
        </button>
      </form>
    </div>

  </div>
</template>
