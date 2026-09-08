<script setup>
import { AlertTriangle, Trash2 } from 'lucide-vue-next'

const props = defineProps(['audit'])
const emit = defineEmits(['close', 'confirm'])
</script>

<template>
  <div v-if="audit" class="modal-overlay">
    <div class="modal-card" style="max-width: 440px;">
      <div style="width: 48px; height: 48px; border-radius: 50%; background: rgba(244,63,94,0.15); border: 1px solid #f43f5e; color: #f43f5e; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
        <AlertTriangle :size="24" />
      </div>
      <h3 style="font-size: 1.25rem; font-weight: 800; color: #fff;">Suppression Fiche #ACTIA-{{ audit.id }}</h3>
      <p style="font-size: 0.88rem; color: var(--text-muted); margin: 10px 0; line-height: 1.6;">
        Êtes-vous sûr de vouloir supprimer définitivement la fiche <strong style="color: #fff;">#ACTIA-{{ audit.id }}</strong> ?<br/>
        <span style="color: #f43f5e; font-size: 0.8rem; display: inline-block; margin-top: 6px;">⚠️ Cette action est irréversible.</span>
      </p>
      <div style="display: flex; gap: 12px; margin-top: 1.5rem;">
        <button class="btn btn-secondary" style="flex: 1;" @click="emit('close')">Annuler</button>
        <button class="btn" style="flex: 1; background: #f43f5e; color: #fff;" @click="emit('confirm')"><Trash2 :size="16"/> Supprimer</button>
      </div>
    </div>
  </div>
</template>
