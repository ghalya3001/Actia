/**
 * =============================================================================
 * Configuration Vite : vite.config.js
 * Description : Configuration de l'outillage de build et du serveur de développement
 *               pour le frontend Vue 3 de PlatformActia.
 * =============================================================================
 */
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  // Plugin Vue officiel pour compiler les Single File Components (.vue)
  plugins: [vue()],

  // Paramètres de compilation pour la production
  build: {
    outDir: 'dist',       // Répertoire de destination du bundle statique
    emptyOutDir: true,    // Nettoyage automatique du dossier de sortie avant chaque build
  },

  // Configuration du serveur de développement local
  server: {
    port: 3000,           // Port d'écoute du serveur de dev Vite (http://localhost:3000)
    // Configuration du reverse proxy pour rediriger les appels API vers le backend FastAPI
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Adresse locale de l'API FastAPI
        changeOrigin: true,              // Modifie l'en-tête Origin pour éviter les blocages CORS
      },
    },
  },
});

