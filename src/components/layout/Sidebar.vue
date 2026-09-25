<!--
===============================================================================
BARRE DE NAVIGATION LATÉRALE (SIDEBAR.VUE)
===============================================================================
Rôle :
  Composant de menu latéral fixe de l'application :
  - Affiche le logo officiel et le titre de la plateforme PlatformActia.
  - Fournit la liste des liens de navigation vers les 5 vues principales.
  - Met en surbrillance l'élément actif en fonction de la prop `currentPage`.
  - Intègre le bouton d'action de déconnexion sécurisée en pied de barre.

Équipe de maintenance :
  Pour ajouter une nouvelle entrée de menu, insérez simplement un nouvel objet
  dans le tableau `navItems` avec son identifiant, libellé et icône Lucide.
===============================================================================
-->

<script setup>
import { computed } from 'vue'
import { Home, FileEdit, Clock, LineChart, User, Users, LogOut } from 'lucide-vue-next'

// --- Props et Événements ---
// currentPage : nom de la page présentement visualisée (pour mise en surbrillance)
// user : profil utilisateur connecté (pour filtrage selon le rôle)
// pendingCount : nombre de comptes en attente de validation pour badge admin
const props = defineProps(['currentPage', 'user', 'pendingCount'])

// Événements émis vers le composant parent App.vue
const emit = defineEmits(['update:currentPage', 'logout'])

// Configuration dynamique des éléments de la barre de navigation
const navItems = computed(() => {
  const items = [
    { id: 'home', label: "Page d'Accueil", icon: Home }
  ]

  // Seuls les administrateurs (ADMIN) peuvent accéder aux Formulaires HSE et à l'Historique des Audits
  if (props.user?.role === 'ADMIN') {
    items.push(
      { id: 'formulaire', label: 'Formulaires HSE', icon: FileEdit },
      { id: 'historique', label: 'Historique Audits', icon: Clock }
    )
  }

  // Dashboard HSE accessible à tous les profils (USER et ADMIN)
  items.push({ id: 'dashboard', label: 'Dashboard HSE', icon: LineChart })

  // Menu de gestion des utilisateurs réservé aux administrateurs (ADMIN)
  if (props.user?.role === 'ADMIN') {
    items.push({
      id: 'admin-users',
      label: 'Gestion Utilisateurs',
      icon: Users,
      badge: props.pendingCount || 0
    })
  }

  // Profil personnel accessible à tous
  items.push({ id: 'profile', label: 'Mon Profil', icon: User })
  return items
})
</script>

<template>
  <aside class="sidebar">
    <!-- En-tête de la Sidebar : Logo et Identité visuelle PlatformActia -->
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(0,201,150,0.2)">
      <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--color-primary); color: #00141a; font-weight: 800; font-size: 1.4rem; display: flex; align-items: center; justify-content: center">P</div>
      <div>
        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff">PlatformActia</div>
        <div style="font-size: 0.75rem; color: var(--color-primary); font-weight: 700">
          {{ user?.role === 'ADMIN' ? 'Admin Portal' : 'Responsable Portal' }}
        </div>
      </div>
    </div>

    <!-- Navigation principale : Boutons de sélection de page -->
    <nav style="display: flex; flex-direction: column; gap: 8px; flex: 1">
      <div style="font-size: 0.72rem; font-weight: 800; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px">Navigation</div>
      <button
        v-for="item in navItems"
        :key="item.id"
        @click="emit('update:currentPage', item.id)"
        :style="{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '11px 14px',
          borderRadius: '8px',
          fontSize: '0.88rem',
          fontWeight: '700',
          cursor: 'pointer',
          border: 'none',
          background: currentPage === item.id ? 'rgba(0,201,150,0.15)' : 'transparent',
          color: currentPage === item.id ? 'var(--color-primary)' : 'var(--text-muted)',
          borderLeft: currentPage === item.id ? '3px solid var(--color-primary)' : '3px solid transparent',
          transition: 'all 0.2s ease',
          textAlign: 'left',
          width: '100%'
        }"
      >
        <component :is="item.icon" :size="18" />
        <span style="flex: 1">{{ item.label }}</span>
        <span
          v-if="item.badge > 0"
          style="background: #fbbf24; color: #00141a; font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 10px; line-height: 1"
          title="Comptes en attente"
        >
          {{ item.badge }}
        </span>
      </button>
    </nav>

    <!-- Pied de la Sidebar : Bouton de déconnexion -->
    <div style="padding-top: 1rem; border-top: 1px solid rgba(0,201,150,0.2)">
      <button
        @click="emit('logout')"
        style="display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 8px; font-size: 0.88rem; font-weight: 700; cursor: pointer; border: none; background: rgba(244,63,94,0.1); color: #f43f5e; width: 100%; transition: all 0.2s ease"
      >
        <LogOut :size="18" />
        Se Déconnecter
      </button>
    </div>
  </aside>
</template>
