<script setup>
import { Home, FileEdit, Clock, LineChart, User, LogOut } from 'lucide-vue-next'

const props = defineProps(['currentPage'])
const emit = defineEmits(['update:currentPage', 'logout'])

const navItems = [
  { id: 'home', label: "Page d'Accueil", icon: Home },
  { id: 'formulaire', label: 'Formulaires HSE', icon: FileEdit },
  { id: 'historique', label: 'Historique Audits', icon: Clock },
  { id: 'dashboard', label: 'Dashboard HSE', icon: LineChart },
  { id: 'profile', label: 'Mon Profil', icon: User },
]
</script>

<template>
  <aside class="sidebar">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(0,201,150,0.2)">
      <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--color-primary); color: #00141a; font-weight: 800; font-size: 1.4rem; display: flex; align-items: center; justify-content: center">P</div>
      <div>
        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff">PlatformActia</div>
        <div style="font-size: 0.75rem; color: var(--color-primary); font-weight: 700">Responsable Portal</div>
      </div>
    </div>

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
          textAlign: 'left'
        }"
      >
        <component :is="item.icon" :size="18" />
        {{ item.label }}
      </button>
    </nav>

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
