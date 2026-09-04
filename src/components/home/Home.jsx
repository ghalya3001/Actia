import React, { useState, useEffect } from 'react';
import { ShieldCheck, RotateCw, Lightbulb, Flame, Award, GraduationCap, FileEdit, Clock, LineChart, Star, CheckCircle, ArrowRight } from 'lucide-react';

const hseQuotes = [
  { text: "“La sécurité ne se mesure pas à l'absence d’accidents, mais à la présence de défenses.”", author: "— Prof. James Reason (Modèle du fromage suisse)" },
  { text: "“Penser que la sécurité coûte cher, c'est oublier ce que coûte un accident.”", author: "— Sir Trevor Kletz" },
  { text: "“Le plus grand danger est de penser que nous sommes en sécurité là où nous ne le sommes pas.”", author: "— Principe de Vigilance Partagée" },
  { text: "“La sécurité n'est pas le fruit du hasard. C’est le résultat d'une attention constante et d'efforts répétés.”", author: "— Culture HSE Actia" },
  { text: "“Chaque presqu'accident évité aujourd'hui est une vie préservée demain.”", author: "— Règle d'Or ISO 45001" }
];

export default function Home({ onNavigate }) {
  const [quoteIndex, setQuoteIndex] = useState(0);
  const [fade, setFade] = useState(true);

  const nextQuote = () => {
    setFade(false);
    setTimeout(() => {
      setQuoteIndex(prev => (prev + 1) % hseQuotes.length);
      setFade(true);
    }, 200);
  };

  useEffect(() => {
    const timer = setInterval(() => {
      nextQuote();
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="page-anim">
      {/* HEADER */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#fff', letterSpacing: '-0.5px' }}>
          Bienvenue sur <span style={{ color: 'var(--color-primary)', textShadow: '0 0 20px rgba(0,201,150,0.4)' }}>PlatformActia HSE</span>
        </h1>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Hygiène · Sécurité · Environnement — Les fondamentaux du responsable HSE
        </p>
      </div>

      {/* HERO BANNER */}
      <div className="animated-hero" style={{ marginBottom: '1.75rem' }}>
        <div className="hero-icon-wrapper">🛡️</div>
        <div style={{ position: 'relative', zIndex: 2 }}>
          <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fff', marginBottom: '6px', letterSpacing: '-0.3px' }}>
            La Sécurité n’est pas une option — <span style={{ color: 'var(--color-accent-light)' }}>c’est une culture au quotidien.</span>
          </div>
          <div style={{ fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            En tant que responsable HSE, vous construisez un environnement d'excellence où chaque travailleur rentre chez lui en toute sécurité.
          </div>
        </div>
      </div>

      {/* ROTATING QUOTE & ENGAGEMENT GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.25rem', marginBottom: '1.75rem' }}>
        
        {/* QUOTE ROTATOR BOX */}
        <div className="quote-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Lightbulb size={16} /> Inspiration HSE du Jour
            </span>
            <button onClick={nextQuote} style={{ background: 'rgba(0,201,150,0.15)', border: '1px solid rgba(0,201,150,0.3)', borderRadius: '15px', color: 'var(--color-primary)', padding: '4px 12px', fontSize: '0.75rem', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.2s ease' }}>
              <RotateCw size={13} /> Suivant
            </button>
          </div>
          <div style={{ fontSize: '1.05rem', fontStyle: 'italic', color: 'var(--text-main)', lineHeight: '1.6', minHeight: '55px', display: 'flex', alignItems: 'center', transition: 'opacity 0.2s ease', opacity: fade ? 1 : 0 }}>
            {hseQuotes[quoteIndex].text}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--color-accent-light)', fontWeight: '700', marginTop: '8px', transition: 'opacity 0.2s ease', opacity: fade ? 1 : 0 }}>
            {hseQuotes[quoteIndex].author}
          </div>
        </div>

        {/* ENGAGEMENT COUNTER CARD */}
        <div className="pillar-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', background: 'linear-gradient(135deg, rgba(0,35,45,0.7), rgba(0,61,77,0.4))' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--color-primary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Flame size={16} color="#f59e0b" /> Engagement HSE
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: '800', color: '#fff', fontFamily: 'var(--font-mono)' }}>
            10 / 10
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Règles d’Or sous contrôle
          </div>
        </div>
      </div>

      {/* QUICK ACTION CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'pointer', transition: 'transform 0.2s ease, border-color 0.2s ease' }} onClick={() => onNavigate('formulaire')}>
          <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(0,201,150,0.15)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><FileEdit size={26}/></div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff' }}>Nouveau Formulaire</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Audit, Tournée & Permis</p>
          </div>
          <ArrowRight size={18} color="var(--color-primary)" />
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'pointer', transition: 'transform 0.2s ease, border-color 0.2s ease' }} onClick={() => onNavigate('historique')}>
          <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(168,224,99,0.15)', color: 'var(--color-accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Clock size={26}/></div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff' }}>Historique Audits</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Consulter les fiches</p>
          </div>
          <ArrowRight size={18} color="var(--color-accent-light)" />
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', cursor: 'pointer', transition: 'transform 0.2s ease, border-color 0.2s ease' }} onClick={() => onNavigate('dashboard')}>
          <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'rgba(59,130,246,0.15)', color: '#60a5fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><LineChart size={26}/></div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff' }}>Dashboard HSE</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Graphiques & KPIs</p>
          </div>
          <ArrowRight size={18} color="#60a5fa" />
        </div>
      </div>

      {/* 3 PILLARS OF HSE */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="pillar-card">
          <div style={{ fontSize: '2.2rem', marginBottom: '0.75rem' }}>🧼</div>
          <div style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--color-primary)', marginBottom: '8px' }}>1. Hygiène</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            Prévenir les maladies professionnelles et assurer la santé physique et mentale au poste de travail.
          </div>
        </div>

        <div className="pillar-card">
          <div style={{ fontSize: '2.2rem', marginBottom: '0.75rem' }}>⛑️</div>
          <div style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--color-accent-light)', marginBottom: '8px' }}>2. Sécurité</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            Éliminer les dangers à la source, sécuriser les machines et instaurer l'objectif « Zéro Accident ».
          </div>
        </div>

        <div className="pillar-card">
          <div style={{ fontSize: '2.2rem', marginBottom: '0.75rem' }}>🌿</div>
          <div style={{ fontSize: '1.1rem', fontWeight: '800', color: '#34d399', marginBottom: '8px' }}>3. Environnement</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            Réduire l'empreinte écologique, maîtriser les rejets et favoriser le développement durable.
          </div>
        </div>
      </div>

      {/* 10 RULES OF GOLD & METHODOLOGY PANELS */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', marginBottom: '2rem' }}>
        
        {/* 10 RÈGLES D'OR DE SÉCURITÉ */}
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Star size={18} color="#f59e0b" /> 10 Règles d’Or de Sécurité
            </span>
            <span className="panel-badge">Incontournables</span>
          </div>
          <div className="panel-body" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div className="rule-item"><div class="rule-num">1</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Travailler toujours avec les <strong style={{ color: '#fff' }}>autorisations de travail</strong> valides.</div></div>
              <div className="rule-item"><div class="rule-num">2</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Appliquer la <strong style={{ color: '#fff' }}>consignation LOTO</strong> avant toute maintenance.</div></div>
              <div className="rule-item"><div class="rule-num">3</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Porter impérativement les <strong style={{ color: '#fff' }}>EPI réglementaires</strong>.</div></div>
              <div className="rule-item"><div class="rule-num">4</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Ne jamais contourner un <strong style={{ color: '#fff' }}>dispositif de sécurité</strong>.</div></div>
              <div className="rule-item"><div class="rule-num">5</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Déclarer instantanément <strong style={{ color: '#fff' }}>tout incident ou risque</strong>.</div></div>
              <div className="rule-item"><div class="rule-num">6</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Respecter les <strong style={{ color: '#fff' }}>règles de circulation et vitesses</strong> sur site.</div></div>
              <div className="rule-item"><div class="rule-num">7</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Utiliser un <strong style={{ color: '#fff' }}>harnais antichute</strong> pour le travail en hauteur.</div></div>
              <div className="rule-item"><div class="rule-num">8</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Tester l’atmosphère avant d'entrer en <strong style={{ color: '#fff' }}>espace confiné</strong>.</div></div>
              <div className="rule-item"><div class="rule-num">9</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Tolérance zéro pour les <strong style={{ color: '#fff' }}>substances altérantes</strong>.</div></div>
              <div className="rule-item"><div class="rule-num">10</div><div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Trier et trier correctement les <strong style={{ color: '#fff' }}>déchets dangereux</strong>.</div></div>
            </div>
          </div>
        </div>

        {/* METHODOLOGIES & CERTIFICATIONS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <GraduationCap size={18} color="var(--color-primary)" /> Méthodologies Fondamentales
              </span>
            </div>
            <div className="panel-body" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ padding: '12px 14px', background: 'rgba(0,24,32,0.6)', borderRadius: '12px', borderLeft: '4px solid var(--color-primary)' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: '800', color: 'var(--color-primary)', marginBottom: '4px' }}>🔺 Pyramide de Bird</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                    Pour 1 accident grave, il y a 600 presqu'accidents. Agir sur le bas de la pyramide protège les vies.
                  </div>
                </div>
                <div style={{ padding: '12px 14px', background: 'rgba(0,24,32,0.6)', borderRadius: '12px', borderLeft: '4px solid var(--color-accent-light)' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: '800', color: 'var(--color-accent-light)', marginBottom: '4px' }}>🔄 Amélioration Continue (PDCA)</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                    Planifier → Réaliser → Vérifier → Agir. Le moteur de toute démarche ISO résiliente.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <span className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Award size={18} color="var(--color-primary)" /> Certifications Clés
              </span>
            </div>
            <div className="panel-body" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div style={{ padding: '10px', background: 'rgba(0,201,150,0.1)', border: '1px solid rgba(0,201,150,0.25)', borderRadius: '10px', textAlign: 'center' }}>
                  <div style={{ fontWeight: '800', color: 'var(--color-primary)', fontSize: '0.9rem' }}>ISO 45001</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>Santé & Sécurité</div>
                </div>
                <div style={{ padding: '10px', background: 'rgba(168,224,99,0.1)', border: '1px solid rgba(168,224,99,0.25)', borderRadius: '10px', textAlign: 'center' }}>
                  <div style={{ fontWeight: '800', color: 'var(--color-accent-light)', fontSize: '0.9rem' }}>ISO 14001</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>Environnement</div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
