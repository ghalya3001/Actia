/**
 * ===============================================================================
 * POINT D'ENTRÉE PRINCIPAL DU FRONTEND VUE 3 (MAIN.JS)
 * ===============================================================================
 * Rôle :
 *   Initialise et monte l'application racine Vue 3 sur le conteneur DOM `#app`
 *   défini dans `index.html`.
 * 
 * Imports clés :
 *   - `createApp` : Fonction d'amorçage officielle de Vue 3 Composition API.
 *   - `App` : Composant racine de l'application orchestrant la navigation et l'état.
 *   - `index.css` : Feuille de styles globale (design system PlatformActia, variables CSS,
 *     effets de glassmorphism, classes utilitaires pour les boutons et cartes).
 * ===============================================================================
 */

import { createApp } from 'vue'
import App from './App.vue'
import './index.css'

// Instanciation de l'application Vue et accrochage sur la balise <div id="app">
createApp(App).mount('#app')
