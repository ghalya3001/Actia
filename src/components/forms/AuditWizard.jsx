import React, { useState, useEffect } from 'react';
import { ArrowLeft, ChevronRight, ChevronLeft, Upload, CheckCircle, AlertTriangle, FileText, Shield, Flame, HardHat } from 'lucide-react';

const AUDIT_QUESTIONS_DATA = [
  // SECTION 1
  { id: 1, sec: 1, text: "Les EPI sont ils à disposition des travailleurs dans la zone de travail ?" },
  { id: 2, sec: 1, text: "Le port des EPI (gant, lunette, masque respiratoire) est respecté ?" },
  { id: 3, sec: 1, text: "Les EPI ne sont pas endommagés ?" },
  { id: 4, sec: 1, text: "L'affichage des EPI est respecté ?" },
  { id: 5, sec: 1, text: "La fréquence du changement des EPI est-elle respectée ?" },
  { id: 6, sec: 1, text: "Contrôle de l'état de conditionnement des EPIs" },
  { id: 7, sec: 1, text: "Présence d'une armoire de stockage des EPIs" },
  // SECTION 2
  { id: 8, sec: 2, text: "L'opérateur sur poste est-il sensibilisé sur les risques dans la zone de travail ?" },
  { id: 9, sec: 2, text: "L'opérateur sur poste connaît-il les instructions et les pictogrammes de santé, sécurité (FDSS) ?" },
  { id: 10, sec: 2, text: "Les FDSS sont elles mises à disposition et affichées dans chaque poste de travail ?" },
  { id: 11, sec: 2, text: "L'opérateur sur poste connaît l'emploi correct de leurs EPI ?" },
  { id: 12, sec: 2, text: "L'opérateur sur poste sait intervenir lors d'un accident ?" },
  // SECTION 3
  { id: 13, sec: 3, text: "Standard 5 S est il respecté ?" },
  { id: 14, sec: 3, text: "L'aspiration et l'extraction à la source est-elle fonctionnelle ?" },
  { id: 15, sec: 3, text: "Les bacs de rétention sont présents et propres ?" },
  { id: 16, sec: 3, text: "Les bacs de sable sont présents, identifiés et dans son emplacement adéquat ?" },
  { id: 17, sec: 3, text: "Les poubelles existent elles dans la zone de travail selon le type de déchet ?" },
  { id: 18, sec: 3, text: "Les poubelles sont bien identifiées ?" },
  { id: 19, sec: 3, text: "Les poubelles de déchets dangereux sont équipées de leurs sachets ?" },
  { id: 20, sec: 3, text: "Le tri à la source est respecté ?" },
  { id: 21, sec: 3, text: "Le poids de stockage au niveau des palettiers est - il respecté ?" },
  { id: 22, sec: 3, text: "Les alentours sont nettoyés et la fréquence de nettoyage est respectée" },
  { id: 23, sec: 3, text: "Absence de mégots de cigarette" },
  { id: 24, sec: 3, text: "les toilettes sont nettoyées et la fréquence de nettoyage est respectée" },
  { id: 25, sec: 3, text: "les réfectoires sont nettoyés et la fréquence de nettoyage est respectée" },
  { id: 26, sec: 3, text: "les zones fumeurs sont bien respectées" },
  // SECTION 4
  { id: 27, sec: 4, text: "Les Équipements de travail sont conformes ?" },
  { id: 28, sec: 4, text: "Toutes les machines sont équipées de leurs caches de sécurité ?" },
  { id: 29, sec: 4, text: "Les modes opératoires sont-ils affichés et mis à disposition ?" },
  { id: 30, sec: 4, text: "Le planning et la maintenance préventive des machines sont ils respectés ?" },
  // SECTION 5
  { id: 31, sec: 5, text: "Les extincteurs sont identifiés ?" },
  { id: 32, sec: 5, text: "Les extincteurs sont vérifiés ?" },
  { id: 33, sec: 5, text: "Les extincteurs sont accessibles ?" },
  { id: 34, sec: 5, text: "Les RIA sont vérifiés et fonctionnel ?" },
  { id: 35, sec: 5, text: "Les RIA sont accessibles ?" },
  { id: 36, sec: 5, text: "les moyens de lutte contre l'incendie sont disponibles ?" },
  { id: 37, sec: 5, text: "les issues de secours sont dégagées ?" },
  { id: 38, sec: 5, text: "l'alarme de l'issue de secours est fonctionnelle ?" },
  { id: 39, sec: 5, text: "le BAES est en bonne état de fonctionnement !" },
  { id: 40, sec: 5, text: "Les panneaux d'évacuation sont visibles et disponible ?" },
  // SECTION 6
  { id: 41, sec: 6, text: "La boîte pharmacie est disponible et équipée ?" },
  { id: 42, sec: 6, text: "La liste des secouristes est affichée et à jour" },
  { id: 43, sec: 6, text: "La Liste des Guides file-Serres file est affiché et à jour" },
  // SECTION 7
  { id: 44, sec: 7, text: "Les postes de travail sont adaptés à la morphologie des opérateurs ?" },
  { id: 45, sec: 7, text: "Les mouvements répétitifs sont identifiés et évalués ?" },
  { id: 46, sec: 7, text: "Les manutentions manuelles sont évaluées ?" },
  { id: 47, sec: 7, text: "L'espace de travail permet des déplacements sécurisés ?" },
  { id: 48, sec: 7, text: "L'écran informatique est positionné à hauteur des yeux ?" },
  { id: 49, sec: 7, text: "Les outils et matériels sont rangés à portée de main ?" },
  { id: 50, sec: 7, text: "L'éclairage est suffisant et adapté ?" },
  { id: 51, sec: 7, text: "Les opérateurs bénéficient d'une formation aux gestes et postures ?" }
];

const TOURNEE_HSE_QUESTIONS_DATA = [
  { id: 101, sec: 1, text: "Port des EPI conforme" },
  { id: 102, sec: 1, text: "Présence et lisibilité de la signalisation" },
  { id: 103, sec: 1, text: "Voies de circulation dégagées" },
  { id: 104, sec: 1, text: "Équipements de protection collective fonctionnels" },
  { id: 105, sec: 1, text: "Respect des procédures internes" },
  { id: 106, sec: 2, text: "Stockage conforme des produits chimiques" },
  { id: 107, sec: 2, text: "FDS disponibles sur site" },
  { id: 108, sec: 2, text: "Bac de rétention présent et propre" },
  { id: 109, sec: 2, text: "Étiquetage CLP conforme" },
  { id: 110, sec: 2, text: "Manipulation avec EPI adaptés" },
  { id: 111, sec: 2, text: "Plan d'urgence ou douche/lave-œil disponible" },
  { id: 112, sec: 3, text: "Matériel certifié ATEX" },
  { id: 113, sec: 3, text: "Mise à la terre des équipements" },
  { id: 114, sec: 3, text: "Absence d'étincelles / sources d'ignition" },
  { id: 115, sec: 3, text: "Signalisation zone ATEX visible" },
  { id: 116, sec: 3, text: "Procédures spécifiques connues par le personnel" },
  { id: 117, sec: 4, text: "Verrouillage physique des sources d'énergie" },
  { id: 118, sec: 4, text: "Étiquettes de consignation en place" },
  { id: 119, sec: 4, text: "Formation et habilitation du personnel" },
  { id: 120, sec: 4, text: "Absence d'intervention sans autorisation" },
  { id: 121, sec: 5, text: "Extincteurs accessibles et vérifiés" },
  { id: 122, sec: 5, text: "RIA dégagés et opérants" },
  { id: 123, sec: 5, text: "Permis de feu obligatoire si travaux en flamme" },
  { id: 124, sec: 5, text: "Chemins d'évacuation dégagés" },
  { id: 125, sec: 5, text: "Surpresseur réseau RIA sous tension" },
  { id: 126, sec: 5, text: "Surpresseur réseau RIA en mode automatique" },
  { id: 127, sec: 5, text: "Niveau d'eau dans la bâche à eau" },
  { id: 128, sec: 6, text: "Les Issues de secours accessibles" },
  { id: 129, sec: 6, text: "Les issues de secours sont équipées de manettes anti-panique" },
  { id: 130, sec: 6, text: "Les sirènes des issues de secours sont fonctionnelles" },
  { id: 131, sec: 6, text: "Plan d'évacuation affiché" },
  { id: 132, sec: 7, text: "Postes adaptés" },
  { id: 133, sec: 7, text: "Gestes répétitifs identifiés" },
  { id: 134, sec: 7, text: "Aides à la manutention disponibles" },
  { id: 135, sec: 7, text: "Formation gestes et postures effectuée" },
  { id: 136, sec: 7, text: "L'écran informatique est positionné à hauteur des yeux" },
  { id: 137, sec: 7, text: "Les outils et matériels sont rangés à portée de hand" },
  { id: 138, sec: 8, text: "Tri conforme des déchets" },
  { id: 139, sec: 8, text: "Conteneurs de collectes adaptés et étiquetés" },
  { id: 140, sec: 8, text: "Stockage temporaire sécurisé" },
  { id: 141, sec: 8, text: "Traçabilité / registre des déchets" },
  { id: 142, sec: 8, text: "Absence de débordement / fuite" }
];

export default function AuditWizard({ formType, editingAudit, onClose, onSubmitSuccess, showToast }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [dateAudit, setDateAudit] = useState(new Date().toISOString().split('T')[0]);
  const [secteur, setSecteur] = useState('');
  const [intervenants, setIntervenants] = useState('');
  const [commentairesGeneraux, setCommentairesGeneraux] = useState('');

  // Permis de Travail numeric state
  const [planPrevention, setPlanPrevention] = useState(0);
  const [permisHauteur, setPermisHauteur] = useState(0);
  const [permisFeu, setPermisFeu] = useState(0);
  const [permisRemarques, setPermisRemarques] = useState('');

  // Checklist items answers state
  const [answers, setAnswers] = useState({});

  const isPermis = formType === 'permis_travail';
  const isTournee = formType === 'tournee_hse';

  const questionsData = isTournee ? TOURNEE_HSE_QUESTIONS_DATA : AUDIT_QUESTIONS_DATA;

  useEffect(() => {
    if (editingAudit) {
      setDateAudit(editingAudit.date_audit || new Date().toISOString().split('T')[0]);
      setSecteur(editingAudit.secteur || '');
      setIntervenants(editingAudit.intervenants || '');
      setCommentairesGeneraux(editingAudit.commentaires_generaux || '');

      if (isPermis) {
        const items = editingAudit.items_data || {};
        setPlanPrevention(items.plan_prevention || 0);
        setPermisHauteur(items.permis_hauteur || 0);
        setPermisFeu(items.permis_feu || 0);
        setPermisRemarques(items.remarques || '');
      } else {
        setAnswers(editingAudit.items_data || {});
      }
    } else {
      if (!isPermis) {
        const initialAnswers = {};
        questionsData.forEach(q => {
          initialAnswers[q.id] = { val: 1, constat: '', photo: '', action: '', resp: '', delai: '', etat: 'Non engagée', comm: '' };
        });
        setAnswers(initialAnswers);
      }
    }
  }, [editingAudit, formType]);

  const updateAnswer = (qId, field, val) => {
    setAnswers(prev => ({
      ...prev,
      [qId]: {
        ...(prev[qId] || { val: 1, constat: '', photo: '', action: '', resp: '', delai: '', etat: 'Non engagée', comm: '' }),
        [field]: val
      }
    }));
  };

  const handlePhotoUpload = (qId, file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      updateAnswer(qId, 'photo', e.target.result);
      showToast(`Photo "${file.name}" ajoutée.`);
    };
    reader.readAsDataURL(file);
  };

  const calculateScore = () => {
    if (isPermis) return { score: '100.0', confCount: 0, nconfCount: 0, naCount: 0 };
    let confCount = 0, nconfCount = 0, naCount = 0;
    questionsData.forEach(q => {
      const a = answers[q.id];
      if (a) {
        if (a.val === 1) confCount++;
        else if (a.val === 0) nconfCount++;
        else if (a.val === 'NA') naCount++;
      }
    });
    const total = confCount + nconfCount;
    const score = total > 0 ? ((confCount / total) * 100).toFixed(1) : '100.0';
    return { score, confCount, nconfCount, naCount };
  };

  const handleSubmit = async () => {
    if (!secteur || !intervenants || !dateAudit) {
      showToast("Veuillez renseigner la Date, le Secteur et les Intervenants / Responsables à l'Étape 1.", 'error');
      setCurrentStep(1);
      return;
    }

    const API_AUDITS = window.location.origin + "/api/v1/audits";
    const token = localStorage.getItem("access_token");

    let reference = isPermis ? 'FGSI-PERMIS' : (isTournee ? 'FGSI-010-Ind:A' : 'FGSI-001-Ind:F');
    let itemsPayload = answers;
    let scoreObj = { score: '100.0', confCount: 0, nconfCount: 0, naCount: 0 };
    let soldee = 0, non_engagee = 0, en_cours = 0, en_retard = 0;

    if (isPermis) {
      itemsPayload = {
        plan_prevention: parseInt(planPrevention || 0, 10),
        permis_hauteur: parseInt(permisHauteur || 0, 10),
        permis_feu: parseInt(permisFeu || 0, 10),
        remarques: permisRemarques
      };
    } else {
      scoreObj = calculateScore();
      questionsData.forEach(q => {
        const a = answers[q.id];
        if (a && a.val === 0) {
          if (a.etat === 'Soldée') soldee++;
          else if (a.etat === 'En cours') en_cours++;
          else if (a.etat === 'En retard') en_retard++;
          else non_engagee++;
        }
      });
    }

    const payload = {
      reference: reference,
      form_type: formType,
      secteur: secteur,
      intervenants: intervenants,
      date_audit: dateAudit,
      commentaires_generaux: commentairesGeneraux,
      taux_conformite: isPermis ? 100.0 : parseFloat(scoreObj.score),
      total_conforme: isPermis ? 0 : scoreObj.confCount,
      total_non_conforme: isPermis ? 0 : scoreObj.nconfCount,
      total_na: isPermis ? 0 : scoreObj.naCount,
      count_soldee: soldee,
      count_non_engagee: non_engagee,
      count_en_cours: en_cours,
      count_en_retard: en_retard,
      items_data: itemsPayload
    };

    try {
      const url = editingAudit ? `${API_AUDITS}/${editingAudit.id}` : `${API_AUDITS}/`;
      const method = editingAudit ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast(editingAudit ? `Fiche #ACTIA-${editingAudit.id} mise à jour avec succès !` : `Fiche ${isPermis ? 'Permis de Travail' : 'HSE'} enregistrée avec succès !`);
        onSubmitSuccess();
      } else {
        showToast("Erreur lors de la sauvegarde", 'error');
      }
    } catch (err) {
      showToast("Erreur de connexion", 'error');
    }
  };

  const nextStep = () => {
    if (isPermis && currentStep === 2) setCurrentStep(5);
    else if (currentStep < 5) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (isPermis && currentStep === 5) setCurrentStep(2);
    else if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const scoreObj = calculateScore();

  return (
    <div style={{ background: '#f8fafc', color: '#0f172a', borderRadius: '16px', padding: '2rem', boxShadow: '0 20px 40px rgba(0,0,0,0.4)', border: '1px solid #e2e8f0' }}>
      
      {/* HEADER TOP */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1.25rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0' }}>
        <button className="btn btn-secondary" onClick={onClose} style={{ background: '#e2e8f0', color: '#334155' }}>
          <ArrowLeft size={16} /> Retour aux Formulaires
        </button>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#0f172a' }}>
            {editingAudit ? `Modification ${isPermis ? 'Permis' : (isTournee ? 'Tournée' : 'Audit')} #ACTIA-${editingAudit.id}` : (isPermis ? 'Permis de Travail (FGSI-PERMIS)' : (isTournee ? 'Tournée HSE Terrain (FGSI-010)' : 'Audit HSE Terrain (FGSI-001)'))}
          </h2>
          <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '600' }}>CIPI ACTIA — Portail HSE Responsable</div>
        </div>
        <span style={{ background: '#003d4d', color: '#a8e063', padding: '6px 14px', borderRadius: '20px', fontWeight: '800', fontSize: '0.8rem' }}>
          {isPermis ? 'Permis FGSI-PERMIS' : (isTournee ? 'Tournée FGSI-010-Ind:A' : 'Audit FGSI-001-Ind:F')}
        </span>
      </div>

      {/* STEPPER BAR */}
      <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative', marginBottom: '2.25rem' }}>
        {[1, 2, 3, 4, 5].map(step => {
          if (isPermis && (step === 3 || step === 4)) return null;
          const isActive = currentStep === step;
          const isCompleted = currentStep > step;
          const label = step === 1 ? "Infos Générales" : (step === 2 ? (isPermis ? "Permis & Saisie" : (isTournee ? "Sécurité & Chimiques" : "EPI & Opérateurs")) : (step === 3 ? (isTournee ? "Maintenance & Incendie" : "5S & Machines") : (step === 4 ? (isTournee ? "Évacuation & Déchets" : "Incendie & Ergonomie") : "Synthèse & Validation")));
          
          return (
            <div key={step} onClick={() => setCurrentStep(step)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', zIndex: 2 }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: isActive ? '#00c996' : (isCompleted ? '#56ab2f' : '#ffffff'), border: '3px solid', borderColor: isActive ? '#00c996' : (isCompleted ? '#56ab2f' : '#cbd5e1'), color: isActive || isCompleted ? '#fff' : '#64748b', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {step === 5 && isPermis ? 3 : step}
              </div>
              <span style={{ fontSize: '0.78rem', fontWeight: '700', color: isActive ? '#0f172a' : '#64748b', marginTop: '8px' }}>{label}</span>
            </div>
          );
        })}
      </div>

      {/* STEP 1: INFOS */}
      {currentStep === 1 && (
        <div className="wizard-card" style={{ background: '#fff', borderRadius: '12px', padding: '1.5rem', border: '1px solid #e2e8f0' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: '#0f172a', marginBottom: '1.25rem', borderBottom: '1px dashed #e2e8f0', paddingBottom: '10px' }}>Étape 1 : Informations Générales</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: '700', color: '#334155', display: 'block', marginBottom: '4px' }}>Date d'Audit / Fiche</label>
              <input type="date" className="light-input" value={dateAudit} onChange={e => setDateAudit(e.target.value)} required />
            </div>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: '700', color: '#334155', display: 'block', marginBottom: '4px' }}>Secteur / Zone de travail</label>
              <input type="text" className="light-input" placeholder="ex: Ligne CMS / Production A" value={secteur} onChange={e => setSecteur(e.target.value)} required />
            </div>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: '700', color: '#334155', display: 'block', marginBottom: '4px' }}>Intervenants / Responsables</label>
              <input type="text" className="light-input" placeholder="ex: M. Responsable HSE / Equipe" value={intervenants} onChange={e => setIntervenants(e.target.value)} required />
            </div>
          </div>
        </div>
      )}

      {/* STEP 2: PERMIS DE TRAVAIL NUMERIC FORM */}
      {currentStep === 2 && isPermis && (
        <div className="wizard-card" style={{ background: '#fff', borderRadius: '12px', padding: '1.5rem', border: '1px solid #e2e8f0' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: '#3b82f6', marginBottom: '8px' }}><Shield size={20} style={{ display: 'inline', marginRight: '8px' }}/> Formulaire Permis de Travail (FGSI-PERMIS)</h3>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1.25rem' }}>Saisissez le nombre de permis délivrés pour les travaux planifiés :</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '10px', border: '1px solid #cbd5e1', borderTop: '4px solid #3b82f6' }}>
              <label style={{ fontSize: '0.88rem', fontWeight: '800', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}><FileText size={16} color="#3b82f6"/> Plan de Prévention</label>
              <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '8px' }}>Nombre de plans établis</span>
              <input type="number" className="light-input" min={0} value={planPrevention} onChange={e => setPlanPrevention(e.target.value)} style={{ fontSize: '1.3rem', fontWeight: '800', color: '#1d4ed8', textAlign: 'center' }} />
            </div>

            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '10px', border: '1px solid #cbd5e1', borderTop: '4px solid #ea580c' }}>
              <label style={{ fontSize: '0.88rem', fontWeight: '800', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}><HardHat size={16} color="#ea580c"/> Permis Travail en Hauteur</label>
              <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '8px' }}>Nombre de permis hauteur</span>
              <input type="number" className="light-input" min={0} value={permisHauteur} onChange={e => setPermisHauteur(e.target.value)} style={{ fontSize: '1.3rem', fontWeight: '800', color: '#c2410c', textAlign: 'center' }} />
            </div>

            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '10px', border: '1px solid #cbd5e1', borderTop: '4px solid #dc2626' }}>
              <label style={{ fontSize: '0.88rem', fontWeight: '800', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}><Flame size={16} color="#dc2626"/> Permis de Feu</label>
              <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '8px' }}>Nombre de permis feu délivrés</span>
              <input type="number" className="light-input" min={0} value={permisFeu} onChange={e => setPermisFeu(e.target.value)} style={{ fontSize: '1.3rem', fontWeight: '800', color: '#b91c1c', textAlign: 'center' }} />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.82rem', fontWeight: '700', color: '#334155', display: 'block', marginBottom: '4px' }}>Remarques & Précautions Spécifiques</label>
            <textarea className="light-input" rows={3} placeholder="Description des travaux, précautions..." value={permisRemarques} onChange={e => setPermisRemarques(e.target.value)}></textarea>
          </div>
        </div>
      )}

      {/* CHECKLIST ITEMS FOR AUDIT / TOURNÉE */}
      {!isPermis && (currentStep === 2 || currentStep === 3 || currentStep === 4) && (
        <div>
          {questionsData.map(q => {
            const isTargetStep = (currentStep === 2 && (q.sec === 1 || q.sec === 2 || (isTournee && q.sec === 3))) ||
                                 (currentStep === 3 && ((isTournee && (q.sec === 4 || q.sec === 5)) || (!isTournee && (q.sec === 3 || q.sec === 4)))) ||
                                 (currentStep === 4 && ((isTournee && (q.sec === 6 || q.sec === 7 || q.sec === 8)) || (!isTournee && (q.sec === 5 || q.sec === 6 || q.sec === 7))));

            if (!isTargetStep) return null;

            const a = answers[q.id] || { val: 1 };

            return (
              <div key={q.id} style={{ background: '#fff', borderRadius: '10px', padding: '1.25rem', marginBottom: '1rem', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.93rem', fontWeight: '700', color: '#1e293b' }}>{q.id}. {q.text}</div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                  <button type="button" onClick={() => updateAnswer(q.id, 'val', 1)} style={{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: '700', border: '1px solid', borderColor: a.val === 1 ? '#10b981' : '#cbd5e1', background: a.val === 1 ? '#10b981' : '#f8fafc', color: a.val === 1 ? '#fff' : '#475569', cursor: 'pointer' }}>✓ Conforme (1)</button>
                  <button type="button" onClick={() => updateAnswer(q.id, 'val', 0)} style={{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: '700', border: '1px solid', borderColor: a.val === 0 ? '#ef4444' : '#cbd5e1', background: a.val === 0 ? '#ef4444' : '#f8fafc', color: a.val === 0 ? '#fff' : '#475569', cursor: 'pointer' }}>✗ Non Conforme (0)</button>
                  <button type="button" onClick={() => updateAnswer(q.id, 'val', 'NA')} style={{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: '700', border: '1px solid', borderColor: a.val === 'NA' ? '#64748b' : '#cbd5e1', background: a.val === 'NA' ? '#64748b' : '#f8fafc', color: a.val === 'NA' ? '#fff' : '#475569', cursor: 'pointer' }}>N/A</button>
                </div>

                {a.val === 0 && (
                  <div style={{ marginTop: '12px', padding: '1rem', background: '#f8fafc', borderLeft: '4px solid #ef4444', borderRadius: '6px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div>
                        <label style={{ fontSize: '0.75rem', fontWeight: '700' }}>Constat détecté</label>
                        <input type="text" className="light-input" value={a.constat || ''} onChange={e => updateAnswer(q.id, 'constat', e.target.value)} />
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', fontWeight: '700' }}>Action à mener</label>
                        <input type="text" className="light-input" value={a.action || ''} onChange={e => updateAnswer(q.id, 'action', e.target.value)} />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* STEP 5: SYNTHÈSE & SUBMISSION */}
      {currentStep === 5 && (
        <div>
          <div style={{ background: 'linear-gradient(135deg, #003d4d 0%, #001c24 100%)', color: '#fff', borderRadius: '12px', padding: '1.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: '700', textTransform: 'uppercase', color: '#a8e063' }}>Synthèse de la Fiche</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', marginTop: '4px' }}>{isPermis ? 'Permis de Travail Enregistré' : 'Taux de Conformité HSE'}</div>
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', fontFamily: 'var(--font-mono)', color: '#00c996' }}>
              {isPermis ? 'FGSI-PERMIS' : `${scoreObj.score} %`}
            </div>
          </div>

          {isPermis ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '15px', background: '#fff', border: '1px solid #e2e8f0', borderLeft: '4px solid #3b82f6', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#64748b' }}>Plan de Prévention</div>
                <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#1d4ed8', marginTop: '4px' }}>{planPrevention}</div>
              </div>
              <div style={{ padding: '15px', background: '#fff', border: '1px solid #e2e8f0', borderLeft: '4px solid #ea580c', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#64748b' }}>Permis Hauteur</div>
                <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#c2410c', marginTop: '4px' }}>{permisHauteur}</div>
              </div>
              <div style={{ padding: '15px', background: '#fff', border: '1px solid #e2e8f0', borderLeft: '4px solid #dc2626', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#64748b' }}>Permis de Feu</div>
                <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#b91c1c', marginTop: '4px' }}>{permisFeu}</div>
              </div>
            </div>
          ) : null}

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ fontSize: '0.82rem', fontWeight: '700', color: '#334155', display: 'block', marginBottom: '4px' }}>Commentaires généraux des auditeurs / intervenants</label>
            <textarea className="light-input" rows={4} placeholder="Remarques finales..." value={commentairesGeneraux} onChange={e => setCommentairesGeneraux(e.target.value)}></textarea>
          </div>
        </div>
      )}

      {/* FOOTER ACTIONS */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem', paddingTop: '1.25rem', borderTop: '2px solid #e2e8f0' }}>
        <button className="btn btn-secondary" onClick={prevStep} style={{ visibility: currentStep === 1 ? 'hidden' : 'visible', background: '#e2e8f0', color: '#334155' }}>
          <ChevronLeft size={16} /> Étape Précédente
        </button>
        <button className="btn btn-primary" onClick={currentStep === 5 ? handleSubmit : nextStep} style={{ maxWidth: '260px' }}>
          {currentStep === 5 ? (editingAudit ? 'Mettre à jour la Fiche' : 'Soumettre la Fiche HSE') : <>Étape Suivante <ChevronRight size={16} /></>}
        </button>
      </div>

    </div>
  );
}
