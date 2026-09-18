<!--
  =============================================================================
  Composant : DeleteModal.vue
  Description : Boîte de dialogue modale de confirmation pour la suppression définitive
                d'une fiche d'audit / formulaire HSE.
  Contexte : Empêche les suppressions accidentelles en demandant une confirmation
             explicite de l'utilisateur avec avertissement d'irréversibilité.
  =============================================================================
-->
<script setup>
// Importation des icônes Lucide pour l'avertissement et l'action de suppression
import { AlertTriangle, Trash2 } from 'lucide-vue-next'

// Propriétés entrantes (Props) :
// - audit : Objet représentant l'audit ou la fiche sélectionnée pour suppression
const props = defineProps(['audit'])

// Événements émis (Emits) vers le composant parent :
// - close : Fermeture de la modale sans action
// - confirm : Déclenchement effectif de la suppression côté API
const emit = defineEmits(['close', 'confirm'])
</script>

<template>
  <!-- Overlay sombre en arrière-plan (affiché uniquement si un audit est sélectionné) -->
  <div v-if="audit" class="modal-overlay">
    <!-- Conteneur centré de la carte modale -->
    <div class="modal-card" style="max-width: 440px;">
      
      <!-- Icône d'alerte stylisée en rouge danger -->
      <div style="width: 48px; height: 48px; border-radius: 50%; background: rgba(244,63,94,0.15); border: 1px solid #f43f5e; color: #f43f5e; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
        <AlertTriangle :size="24" />
      </div>

      <!-- Titre principal mentionnant l'identifiant de la fiche -->
      <h3 style="font-size: 1.25rem; font-weight: 800; color: #fff;">Suppression Fiche #ACTIA-{{ audit.id }}</h3>

      <!-- Message explicatif et avertissement de sécurité -->
      <p style="font-size: 0.88rem; color: var(--text-muted); margin: 10px 0; line-height: 1.6;">
        Êtes-vous sûr de vouloir supprimer définitivement la fiche <strong style="color: #fff;">#ACTIA-{{ audit.id }}</strong> ?<br/>
        <span style="color: #f43f5e; font-size: 0.8rem; display: inline-block; margin-top: 6px;">⚠️ Cette action est irréversible.</span>
      </p>

      <!-- Boutons d'action : Annuler ou Valider la suppression -->
      <div style="display: flex; gap: 12px; margin-top: 1.5rem;">
        <!-- Bouton Annuler : déclenche l'événement 'close' -->
        <button class="btn btn-secondary" style="flex: 1;" @click="emit('close')">Annuler</button>
        <!-- Bouton Supprimer : déclenche l'événement 'confirm' -->
        <button class="btn" style="flex: 1; background: #f43f5e; color: #fff;" @click="emit('confirm')">
          <Trash2 :size="16"/> Supprimer
        </button>
      </div>
    </div>
  </div>
</template>

