<script setup>
import { ShieldCheck, AlertCircle, Clock, CheckCircle2, TrendingUp, Award, Layers } from 'lucide-vue-next'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement } from 'chart.js'
import { Doughnut, Bar, Line } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement)

// Chart 1: Répartition des actions correctives (Doughnut)
const doughnutData = {
  labels: ['Actions Soldées (65%)', 'En cours (20%)', 'Non engagées (10%)', 'En retard (5%)'],
  datasets: [
    {
      data: [65, 20, 10, 5],
      backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
      borderColor: ['#001c24', '#001c24', '#001c24', '#001c24'],
      borderWidth: 3,
    },
  ],
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 12, weight: '700' } }
    }
  }
}

// Chart 2: Taux de conformité par secteur (Bar)
const barData = {
  labels: ['Ligne Production CMS A', 'Zone Stockage PDR', 'Ligne Assemblage B', 'Local Chimie', 'Maintenance'],
  datasets: [
    {
      label: 'Taux de Conformité HSE (%)',
      data: [94.5, 88.0, 91.2, 79.5, 86.4],
      backgroundColor: 'rgba(0, 201, 150, 0.75)',
      borderColor: '#00c996',
      borderWidth: 2,
      borderRadius: 8,
    },
  ],
}

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { backgroundColor: '#001c24', titleColor: '#00c996', bodyColor: '#fff', borderWidth: 1, borderColor: '#00c996' }
  },
  scales: {
    x: { ticks: { color: '#94a3b8', font: { weight: '700' } }, grid: { display: false } },
    y: { ticks: { color: '#94a3b8', font: { weight: '700' } }, min: 50, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } }
  }
}

// Chart 3: Tendance temporelle du score HSE (Line)
const lineData = {
  labels: ['Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août'],
  datasets: [
    {
      label: 'Score Global HSE (%)',
      data: [82.0, 85.4, 84.8, 89.1, 91.5, 93.8],
      borderColor: '#a8e063',
      backgroundColor: 'rgba(168, 224, 99, 0.15)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#a8e063',
      pointRadius: 6,
    },
  ],
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: { ticks: { color: '#94a3b8', font: { weight: '700' } }, grid: { display: false } },
    y: { ticks: { color: '#94a3b8', font: { weight: '700' } }, min: 70, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } }
  }
}
</script>

<template>
  <div style="display: flex; flex-direction: column; gap: 1.5rem;">
    
    <!-- BANNER HEADER -->
    <div style="background: linear-gradient(135deg, #003d4d 0%, #001c24 100%); border-radius: 16px; padding: 1.5rem 2rem; border: 1px solid var(--card-border); display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: var(--color-accent-light); letter-spacing: 1px;">Dashboard HSE Analytics</div>
        <h2 style="font-size: 1.5rem; font-weight: 800; color: #ffffff; margin-top: 2px;">Vue Synthétique des Performance Sécurité & Environnement</h2>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin-top: 4px;">CIPI ACTIA · Indicateurs clés de conformité et suivi des plans d'action</p>
      </div>
      <div style="background: rgba(0,201,150,0.15); border: 1px solid var(--color-primary); border-radius: 12px; padding: 10px 18px; text-align: center;">
        <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700;">Score Global HSE</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: var(--color-primary); font-family: var(--font-mono);">91.5 %</div>
      </div>
    </div>

    <!-- KPI CARDS GRID -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem;">
      
      <div class="glass-card" style="padding: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Audits Réalisés</span>
          <div style="width: 36px; height: 36px; border-radius: 8px; background: rgba(0,201,150,0.15); color: var(--color-primary); display: flex; align-items: center; justify-content: center;"><ShieldCheck :size="20"/></div>
        </div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #fff; margin-top: 8px; font-family: var(--font-mono);">28</div>
        <div style="font-size: 0.75rem; color: #10b981; margin-top: 4px; font-weight: 700;">+12% par rapport au mois dernier</div>
      </div>

      <div class="glass-card" style="padding: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Actions Soldées</span>
          <div style="width: 36px; height: 36px; border-radius: 8px; background: rgba(16,185,129,0.15); color: #10b981; display: flex; align-items: center; justify-content: center;"><CheckCircle2 :size="20"/></div>
        </div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #10b981; margin-top: 8px; font-family: var(--font-mono);">142</div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Taux de résolution : 85%</div>
      </div>

      <div class="glass-card" style="padding: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Actions En Retard</span>
          <div style="width: 36px; height: 36px; border-radius: 8px; background: rgba(239,68,68,0.15); color: #ef4444; display: flex; align-items: center; justify-content: center;"><AlertCircle :size="20"/></div>
        </div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #ef4444; margin-top: 8px; font-family: var(--font-mono);">8</div>
        <div style="font-size: 0.75rem; color: #ef4444; margin-top: 4px; font-weight: 700;">Action requise sous 48h</div>
      </div>

      <div class="glass-card" style="padding: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Permis Valides</span>
          <div style="width: 36px; height: 36px; border-radius: 8px; background: rgba(59,130,246,0.15); color: #60a5fa; display: flex; align-items: center; justify-content: center;"><Layers :size="20"/></div>
        </div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #60a5fa; margin-top: 8px; font-family: var(--font-mono);">15</div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Hauteur, Feu & Prévention</div>
      </div>

    </div>

    <!-- CHARTS ROW 1 -->
    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 1.25rem;">
      
      <!-- DOUGHNUT CHART -->
      <div class="glass-card">
        <h3 style="font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
          <Award :size="18" color="var(--color-primary)"/> État des Actions Correctives
        </h3>
        <div style="height: 260px;">
          <Doughnut :data="doughnutData" :options="doughnutOptions" />
        </div>
      </div>

      <!-- BAR CHART -->
      <div class="glass-card">
        <h3 style="font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
          <ShieldCheck :size="18" color="var(--color-primary)"/> Conformité par Secteur d'Activité
        </h3>
        <div style="height: 260px;">
          <Bar :data="barData" :options="barOptions" />
        </div>
      </div>

    </div>

    <!-- CHARTS ROW 2 -->
    <div class="glass-card">
      <h3 style="font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
        <TrendingUp :size="18" color="var(--color-accent-light)"/> Évolution Temporelle de la Conformité HSE (6 Derniers Mois)
      </h3>
      <div style="height: 240px;">
        <Line :data="lineData" :options="lineOptions" />
      </div>
    </div>

  </div>
</template>
