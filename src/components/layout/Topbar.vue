<script setup>
import { computed } from 'vue'
import { User, ChevronDown } from 'lucide-vue-next'

const props = defineProps(['currentPage', 'user'])
const emit = defineEmits(['profileClick'])

const titles = {
  home: `Page d'<span>Accueil</span>`,
  formulaire: `Formulaires <span style="color: var(--color-primary)">HSE</span>`,
  historique: `Historique des <span style="color: var(--color-primary)">Audits & Formulaires</span>`,
  dashboard: `Dashboard <span style="color: var(--color-primary)">HSE</span>`,
  profile: `Mon <span style="color: var(--color-primary)">Profil</span>`
}

const currentTitleHtml = computed(() => {
  return titles[props.currentPage] || props.currentPage
})

const initial = computed(() => {
  return props.user?.full_name ? props.user.full_name.charAt(0).toUpperCase() : 'R'
})
</script>

<template>
  <header class="topbar">
    <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 12px">
      <div class="pulse-dot" title="Serveur Intranet Actif"></div>
      <div v-html="currentTitleHtml"></div>
    </div>
    <div style="display: flex; align-items: center; gap: 12px">
      <button
        @click="emit('profileClick')"
        style="display: flex; align-items: center; gap: 10px; background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 6px 14px; border-radius: 20px; color: #fff; cursor: pointer"
      >
        <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--color-primary); color: #00141a; font-weight: 800; display: flex; align-items: center; justify-content: center">
          {{ initial }}
        </div>
        <span style="font-size: 0.88rem; font-weight: 700">{{ user?.full_name || 'Responsable HSE' }}</span>
        <ChevronDown :size="14" style="color: var(--text-dim)" />
      </button>
    </div>
  </header>
</template>
