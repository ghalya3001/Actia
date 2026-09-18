<!--
===============================================================================
BARRE SUPÉRIEURE D'EN-TÊTE (TOPBAR.VUE)
===============================================================================
Rôle :
  Composant d'en-tête supérieur de la plateforme :
  - Affiche dynamiquement le titre de la page actuelle avec mise en valeur colorée.
  - Affiche le point lumineux pulsant (pulse-dot) indiquant le statut actif du serveur.
  - Présente le badge utilisateur avec initiale stylisée et nom du manager connecté.
  - Permet d'accéder directement à la page de profil par un clic sur le badge.
===============================================================================
-->

<script setup>
import { computed } from 'vue'
import { User, ChevronDown } from 'lucide-vue-next'

// Props reçues depuis App.vue :
// - currentPage : page active pour adapter le titre
// - user : profil de l'utilisateur connecté (nom, email)
const props = defineProps(['currentPage', 'user'])

// Événement émis lors du clic sur le profil
const emit = defineEmits(['profileClick'])

// Dictionnaire des titres de page avec balisage HTML pour surbrillance de mot-clé
const titles = {
  home: `Page d'<span>Accueil</span>`,
  formulaire: `Formulaires <span style="color: var(--color-primary)">HSE</span>`,
  historique: `Historique des <span style="color: var(--color-primary)">Audits & Formulaires</span>`,
  dashboard: `Dashboard <span style="color: var(--color-primary)">HSE</span>`,
  profile: `Mon <span style="color: var(--color-primary)">Profil</span>`
}

/**
 * Titre HTML calculé dynamiquement selon la page en cours.
 */
const currentTitleHtml = computed(() => {
  return titles[props.currentPage] || props.currentPage
})

/**
 * Première lettre du prénom/nom de l'utilisateur pour l'avatar rond.
 */
const initial = computed(() => {
  return props.user?.full_name ? props.user.full_name.charAt(0).toUpperCase() : 'R'
})
</script>

<template>
  <header class="topbar">
    <!-- Côté gauche : Témoin serveur en ligne et titre de la page -->
    <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 12px">
      <div class="pulse-dot" title="Serveur Intranet Actif"></div>
      <div v-html="currentTitleHtml"></div>
    </div>

    <!-- Côté droit : Bouton de raccourci vers le profil utilisateur -->
    <div style="display: flex; align-items: center; gap: 12px">
      <button
        @click="emit('profileClick')"
        style="display: flex; align-items: center; gap: 10px; background: rgba(0,24,32,0.8); border: 1px solid var(--card-border); padding: 6px 14px; border-radius: 20px; color: #fff; cursor: pointer"
      >
        <!-- Avatar rond avec initiale -->
        <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--color-primary); color: #00141a; font-weight: 800; display: flex; align-items: center; justify-content: center">
          {{ initial }}
        </div>
        <!-- Nom complet du manager connecté -->
        <span style="font-size: 0.88rem; font-weight: 700">{{ user?.full_name || 'Responsable HSE' }}</span>
        <ChevronDown :size="14" style="color: var(--text-dim)" />
      </button>
    </div>
  </header>
</template>
