<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { ShieldCheck, RotateCw, Lightbulb, Flame, Award, GraduationCap, FileEdit, Clock, LineChart, Star, CheckCircle, ArrowRight } from 'lucide-vue-next';

const emit = defineEmits(['navigate']);

const hseQuotes = [
  { text: "“La sécurité ne se mesure pas à l'absence d’accidents, mais à la présence de défenses.”", author: "— Prof. James Reason (Modèle du fromage suisse)" },
  { text: "“Penser que la sécurité coûte cher, c'est oublier ce que coûte un accident.”", author: "— Sir Trevor Kletz" },
  { text: "“Le plus grand danger est de penser que nous sommes en sécurité là où nous ne le sommes pas.”", author: "— Principe de Vigilance Partagée" },
  { text: "“La sécurité n'est pas le fruit du hasard. C’est le résultat d'une attention constante et d'efforts répétés.”", author: "— Culture HSE Actia" },
  { text: "“Chaque presqu'accident évité aujourd'hui est une vie préservée demain.”", author: "— Règle d'Or ISO 45001" }
];

const rules = [
  { num: 1, text: 'Travailler toujours avec les <strong style="color: #fff">autorisations de travail</strong> valides.' },
  { num: 2, text: 'Appliquer la <strong style="color: #fff">consignation LOTO</strong> avant toute maintenance.' },
  { num: 3, text: 'Porter impérativement les <strong style="color: #fff">EPI réglementaires</strong>.' },
  { num: 4, text: 'Ne jamais contourner un <strong style="color: #fff">dispositif de sécurité</strong>.' },
  { num: 5, text: 'Déclarer instantanément <strong style="color: #fff">tout incident ou risque</strong>.' },
  { num: 6, text: 'Respecter les <strong style="color: #fff">règles de circulation et vitesses</strong> sur site.' },
  { num: 7, text: 'Utiliser un <strong style="color: #fff">harnais antichute</strong> pour le travail en hauteur.' },
  { num: 8, text: 'Tester l’atmosphère avant d\'entrer en <strong style="color: #fff">espace confiné</strong>.' },
  { num: 9, text: 'Tolérance zéro pour les <strong style="color: #fff">substances altérantes</strong>.' },
  { num: 10, text: 'Trier et trier correctement les <strong style="color: #fff">déchets dangereux</strong>.' }
];

const actionCards = [
  { id: 'formulaire', title: 'Nouveau Formulaire', subtitle: 'Audit, Tournée & Permis', icon: FileEdit, bg: 'rgba(0,201,150,0.15)', color: 'var(--color-primary)' },
  { id: 'historique', title: 'Historique Audits', subtitle: 'Consulter les fiches', icon: Clock, bg: 'rgba(168,224,99,0.15)', color: 'var(--color-accent-light)' },
  { id: 'dashboard', title: 'Dashboard HSE', subtitle: 'Graphiques & KPIs', icon: LineChart, bg: 'rgba(59,130,246,0.15)', color: '#60a5fa' }
];

const pillars = [
  { emoji: '🧼', title: '1. Hygiène', color: 'var(--color-primary)', text: 'Prévenir les maladies professionnelles et assurer la santé physique et mentale au poste de travail.' },
  { emoji: '⛑️', title: '2. Sécurité', color: 'var(--color-accent-light)', text: 'Éliminer les dangers à la source, sécuriser les machines et instaurer l\'objectif « Zéro Accident ».' },
  { emoji: '🌿', title: '3. Environnement', color: '#34d399', text: 'Réduire l\'empreinte écologique, maîtriser les rejets et favoriser le développement durable.' }
];

const quoteIndex = ref(0);
const fade = ref(true);

const nextQuote = () => {
  fade.value = false;
  setTimeout(() => {
    quoteIndex.value = (quoteIndex.value + 1) % hseQuotes.length;
    fade.value = true;
  }, 200);
};

let timer;

onMounted(() => {
  timer = setInterval(() => {
    nextQuote();
  }, 10000);
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<template>
  <div class="page-anim">
    <!-- HEADER -->
    <div style="margin-bottom: 1.75rem">
      <h1 style="font-size: 1.8rem; font-weight: 800; color: #fff; letter-spacing: -0.5px">
        Bienvenue sur <span style="color: var(--color-primary); text-shadow: 0 0 20px rgba(0,201,150,0.4)">PlatformActia HSE</span>
      </h1>
      <p style="font-size: 0.9rem; color: var(--text-muted)">
        Hygiène · Sécurité · Environnement — Les fondamentaux du responsable HSE
      </p>
    </div>

    <!-- HERO BANNER -->
    <div class="animated-hero" style="margin-bottom: 1.75rem">
      <div class="hero-icon-wrapper">🛡️</div>
      <div style="position: relative; z-index: 2">
        <div style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 6px; letter-spacing: -0.3px">
          La Sécurité n’est pas une option — <span style="color: var(--color-accent-light)">c’est une culture au quotidien.</span>
        </div>
        <div style="font-size: 0.92rem; color: var(--text-muted); line-height: 1.6">
          En tant que responsable HSE, vous construisez un environnement d'excellence où chaque travailleur rentre chez lui en toute sécurité.
        </div>
      </div>
    </div>

    <!-- ROTATING QUOTE & ENGAGEMENT GRID -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.25rem; margin-bottom: 1.75rem">
      
      <!-- QUOTE ROTATOR BOX -->
      <div class="quote-box">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem">
          <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--color-primary); display: flex; align-items: center; gap: 6px">
            <Lightbulb :size="16" /> Inspiration HSE du Jour
          </span>
          <button @click="nextQuote" style="background: rgba(0,201,150,0.15); border: 1px solid rgba(0,201,150,0.3); border-radius: 15px; color: var(--color-primary); padding: 4px 12px; font-size: 0.75rem; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s ease">
            <RotateCw :size="13" /> Suivant
          </button>
        </div>
        <div :style="{ fontSize: '1.05rem', fontStyle: 'italic', color: 'var(--text-main)', lineHeight: '1.6', minHeight: '55px', display: 'flex', alignItems: 'center', transition: 'opacity 0.2s ease', opacity: fade ? 1 : 0 }">
          {{ hseQuotes[quoteIndex].text }}
        </div>
        <div :style="{ fontSize: '0.8rem', color: 'var(--color-accent-light)', fontWeight: '700', marginTop: '8px', transition: 'opacity 0.2s ease', opacity: fade ? 1 : 0 }">
          {{ hseQuotes[quoteIndex].author }}
        </div>
      </div>

      <!-- ENGAGEMENT COUNTER CARD -->
      <div class="pillar-card" style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: linear-gradient(135deg, rgba(0,35,45,0.7), rgba(0,61,77,0.4))">
        <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--color-primary); margin-bottom: 6px; display: flex; align-items: center; gap: 6px">
          <Flame :size="16" color="#f59e0b" /> Engagement HSE
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #fff; font-family: var(--font-mono)">
          10 / 10
        </div>
        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px">
          Règles d’Or sous contrôle
        </div>
      </div>
    </div>

    <!-- QUICK ACTION CARDS -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem; margin-bottom: 2rem">
      <div v-for="card in actionCards" :key="card.id" class="glass-card" style="display: flex; align-items: center; gap: 1.25rem; cursor: pointer; transition: transform 0.2s ease, border-color 0.2s ease" @click="emit('navigate', card.id)">
        <div :style="{ width: '50px', height: '50px', borderRadius: '12px', background: card.bg, color: card.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }">
          <component :is="card.icon" :size="26" />
        </div>
        <div style="flex: 1">
          <h3 style="font-size: 1.05rem; font-weight: 800; color: #fff">{{ card.title }}</h3>
          <p style="font-size: 0.8rem; color: var(--text-muted)">{{ card.subtitle }}</p>
        </div>
        <ArrowRight :size="18" :color="card.color" />
      </div>
    </div>

    <!-- 3 PILLARS OF HSE -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem; margin-bottom: 2rem">
      <div v-for="(pillar, idx) in pillars" :key="idx" class="pillar-card">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem">{{ pillar.emoji }}</div>
        <div :style="{ fontSize: '1.1rem', fontWeight: '800', color: pillar.color, marginBottom: '8px' }">{{ pillar.title }}</div>
        <div style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6">
          {{ pillar.text }}
        </div>
      </div>
    </div>

    <!-- 10 RULES OF GOLD & METHODOLOGY PANELS -->
    <div style="display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 1.5rem; margin-bottom: 2rem">
      
      <!-- 10 RÈGLES D'OR DE SÉCURITÉ -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title" style="display: flex; align-items: center; gap: 8px">
            <Star :size="18" color="#f59e0b" /> 10 Règles d’Or de Sécurité
          </span>
          <span class="panel-badge">Incontournables</span>
        </div>
        <div class="panel-body" style="padding: 1.25rem">
          <div style="display: flex; flex-direction: column; gap: 8px">
            <div v-for="rule in rules" :key="rule.num" class="rule-item">
              <div class="rule-num">{{ rule.num }}</div>
              <div style="font-size: 0.85rem; color: var(--text-muted)" v-html="rule.text"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- METHODOLOGIES & CERTIFICATIONS -->
      <div style="display: flex; flex-direction: column; gap: 1.5rem">
        
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title" style="display: flex; align-items: center; gap: 8px">
              <GraduationCap :size="18" color="var(--color-primary)" /> Méthodologies Fondamentales
            </span>
          </div>
          <div class="panel-body" style="padding: 1.25rem">
            <div style="display: flex; flex-direction: column; gap: 12px">
              <div style="padding: 12px 14px; background: rgba(0,24,32,0.6); border-radius: 12px; border-left: 4px solid var(--color-primary)">
                <div style="font-size: 0.85rem; font-weight: 800; color: var(--color-primary); margin-bottom: 4px">🔺 Pyramide de Bird</div>
                <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5">
                  Pour 1 accident grave, il y a 600 presqu'accidents. Agir sur le bas de la pyramide protège les vies.
                </div>
              </div>
              <div style="padding: 12px 14px; background: rgba(0,24,32,0.6); border-radius: 12px; border-left: 4px solid var(--color-accent-light)">
                <div style="font-size: 0.85rem; font-weight: 800; color: var(--color-accent-light); margin-bottom: 4px">🔄 Amélioration Continue (PDCA)</div>
                <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5">
                  Planifier → Réaliser → Vérifier → Agir. Le moteur de toute démarche ISO résiliente.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <span class="panel-title" style="display: flex; align-items: center; gap: 8px">
              <Award :size="18" color="var(--color-primary)" /> Certifications Clés
            </span>
          </div>
          <div class="panel-body" style="padding: 1.25rem">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px">
              <div style="padding: 10px; background: rgba(0,201,150,0.1); border: 1px solid rgba(0,201,150,0.25); border-radius: 10px; text-align: center">
                <div style="font-weight: 800; color: var(--color-primary); font-size: 0.9rem">ISO 45001</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px">Santé & Sécurité</div>
              </div>
              <div style="padding: 10px; background: rgba(168,224,99,0.1); border: 1px solid rgba(168,224,99,0.25); border-radius: 10px; text-align: center">
                <div style="font-weight: 800; color: var(--color-accent-light); font-size: 0.9rem">ISO 14001</div>
                <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px">Environnement</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
