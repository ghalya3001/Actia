<script setup>
import { ref, reactive, watch, computed } from 'vue';
import { ArrowLeft, ChevronRight, ChevronLeft, Upload, CheckCircle, AlertTriangle, FileText, Shield, Flame, HardHat, Camera, X, Activity, TrendingUp, BarChart3 } from 'lucide-vue-next';


const props = defineProps(['formType', 'editingAudit']);
const emit = defineEmits(['close', 'submitSuccess', 'showToast']);

const AUDIT_QUESTIONS_DATA = [
  // SECTION 1
  { id: 1, sec: 1, text: "Les EPI sont ils à disposition des travailleurs dans la zone de travail ?" },
  { id: 2, sec: 1, text: "Le port des EPI (gant, lunette, masque respiratoire) est respecté ?" },
  { id: 3, sec: 1, text: "Les EPI ne sont pas endommagés ?" },
  { id: 4, sec: 1, text: "L'affichage des EPI est respecté ?" },
  { id: 5, sec: 1, text: "La fréquence du changement des EPI est-elle respectée ?" },
  { id: 6, sec: 1, text: "Contrôle de l'état de conditionnement des EPIs" },
  { id: 7, sec: 1, text: "Présence d'une armoire de stockage des EPIs (masque à cartouche, gants, lunette et etc)" },
  // SECTION 2
  { id: 8, sec: 2, text: "L'opérateur sur poste est-il sensibilisé sur les risques dans la zone de travail ?" },
  { id: 9, sec: 2, text: "L'opérateur sur poste connaît-il les instructions et les pictogrammes de santé, sécurité et environnement (FDSS) dans la zone de travail ?" },
  { id: 10, sec: 2, text: "Les FDSS sont elles mises à disposition et affichées dans chaque poste de travail ?" },
  { id: 11, sec: 2, text: "L'opérateur sur poste connaît l'emploi correct de leurs équipements de protection individuelle ?" },
  { id: 12, sec: 2, text: "L'opérateur sur poste sait intervenir lors d'un accident (Exemple : Déversement d'un produit chimique...)" },
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
  { id: 27, sec: 4, text: "Les Équipements de travail sont conformes (présence des béchers , pinceau...) ?" },
  { id: 28, sec: 4, text: "Toutes les machines sont équipées de leurs caches de sécurité ?" },
  { id: 29, sec: 4, text: "Les modes opératoires sont-ils affichés et mis à disposition des travailleurs ?" },
  { id: 30, sec: 4, text: "Le planning et la maintenance préventive des machines sont ils respectés ?" },
  // SECTION 5
  { id: 31, sec: 5, text: "Les extincteurs sont identifiés ?" },
  { id: 32, sec: 5, text: "Les extincteurs sont vérifiés ?" },
  { id: 33, sec: 5, text: "Les extincteurs sont accessibles (Hauteur, Dans un emplacement dégagé...)" },
  { id: 34, sec: 5, text: "Les RIA sont vérifiés et fonctionnel (avec débit d'eau...)?" },
  { id: 35, sec: 5, text: "Les RIA sont accessibles (Hauteur, Dans un emplacement dégagé...)" },
  { id: 36, sec: 5, text: "les moyens de lutte contre l'incendie sont disponibles selon le plan d'évacuation ?" },
  { id: 37, sec: 5, text: "les issues de secours sont dégagées ?" },
  { id: 38, sec: 5, text: "l'alarme de l'issue de secours est fonctionnelle ?" },
  { id: 39, sec: 5, text: "le BAES est en bonne état de fonctionnement !" },
  { id: 40, sec: 5, text: "Les panneaux d'évacuation sont visibles et disponible selon le plan d'évacuation ?" },
  // SECTION 6
  { id: 41, sec: 6, text: "La boîte pharmacie est disponible et équipée ?" },
  { id: 42, sec: 6, text: "La liste des secouristes est affichée et à jour" },
  { id: 43, sec: 6, text: "La Liste des Guides file-Serres file est affiché et à jour" },
  // SECTION 7
  { id: 44, sec: 7, text: "Les postes de travail sont adaptés à la morphologie des opérateurs (hauteur de table, siège, plans de travail réglables) ?" },
  { id: 45, sec: 7, text: "Les mouvements répétitifs sont identifiés et évalués (répétitivité) ?" },
  { id: 46, sec: 7, text: "Les manutentions manuelles sont évaluées (poids, fréquence, posture) ?" },
  { id: 47, sec: 7, text: "L'espace de travail permet des déplacements sécurisés et sans contorsions ?" },
  { id: 48, sec: 7, text: "L'écran informatique est positionné à hauteur des yeux, à distance adéquate ?" },
  { id: 49, sec: 7, text: "Les outils et matériels sont rangés à portée de main pour éviter les contraintes posturales ?" },
  { id: 50, sec: 7, text: "L'éclairage est suffisant et adapté (pas d'éblouissement, pas d'effet d'ombre) ?" },
  { id: 51, sec: 7, text: "Les opérateurs bénéficient d'une formation aux gestes et postures ?" }
];

const TOURNEE_HSE_QUESTIONS_DATA = [
  // SECTION 1: Sécurité Générale
  { id: 101, sec: 1, text: "Port des EPI conforme (casque, chaussures, lunettes, gants, etc.)" },
  { id: 102, sec: 1, text: "Présence et lisibilité de la signalisation" },
  { id: 103, sec: 1, text: "Voies de circulation dégagées" },
  { id: 104, sec: 1, text: "Équipements de protection collective fonctionnels" },
  { id: 105, sec: 1, text: "Respect des procédures internes" },
  // SECTION 2: Produits Chimiques
  { id: 106, sec: 2, text: "Stockage conforme (Local produits chimique, magasin PDR, Armoires Vagues)" },
  { id: 107, sec: 2, text: "FDS disponibles sur site" },
  { id: 108, sec: 2, text: "Bac de rétention présent et propre" },
  { id: 109, sec: 2, text: "Étiquetage CLP conforme" },
  { id: 110, sec: 2, text: "Manipulation avec EPI adaptés" },
  { id: 111, sec: 2, text: "Plan d'urgence ou douche/lave-œil disponible" },
  // SECTION 3: Zone ATEX
  { id: 112, sec: 3, text: "Matériel certifié ATEX" },
  { id: 113, sec: 3, text: "Mise à la terre des équipements" },
  { id: 114, sec: 3, text: "Absence d'étincelles / sources d'ignition" },
  { id: 115, sec: 3, text: "Signalisation zone ATEX visible" },
  { id: 116, sec: 3, text: "Procédures spécifiques connues par le personnel" },
  // SECTION 4: Maintenance
  { id: 117, sec: 4, text: "Verrouillage physique des sources d'énergie" },
  { id: 118, sec: 4, text: "Étiquettes de consignation en place" },
  { id: 119, sec: 4, text: "Formation et habilitation du personnel" },
  { id: 120, sec: 4, text: "Absence d'intervention sans autorisation" },
  // SECTION 5: Sécurité Incendie
  { id: 121, sec: 5, text: "Extincteurs accessibles et vérifiés" },
  { id: 122, sec: 5, text: "RIA dégagés et opérants" },
  { id: 123, sec: 5, text: "Permis de feu obligatoire si travaux en flamme" },
  { id: 124, sec: 5, text: "Chemins d'évacuation dégagés" },
  { id: 125, sec: 5, text: "Surpresseur réseau RIA sous tension" },
  { id: 126, sec: 5, text: "Surpresseur réseau RIA en mode automatique" },
  { id: 127, sec: 5, text: "Niveau d'eau dans la bâche à eau" },
  // SECTION 6: Évacuation
  { id: 128, sec: 6, text: "Les Issues de secours accessibles" },
  { id: 129, sec: 6, text: "Les issues de secours sont équipées par les manettes anti-panique" },
  { id: 130, sec: 6, text: "Les sirènes des issues de secours sont fonctionnelles" },
  { id: 131, sec: 6, text: "Plan d'évacuation affiché" },
  // SECTION 7: Ergonomie
  { id: 132, sec: 7, text: "Postes adaptés (hauteur / support)" },
  { id: 133, sec: 7, text: "Gestes répétitifs identifiés" },
  { id: 134, sec: 7, text: "Aides à la manutention disponibles" },
  { id: 135, sec: 7, text: "Formation gestes et postures effectuée" },
  { id: 136, sec: 7, text: "L'écran informatique est positionné à hauteur des yeux, à distance adéquate ?" },
  { id: 137, sec: 7, text: "Les outils et matériels sont rangés à portée de main pour éviter les contraintes posturales ?" },
  // SECTION 8: Gestion des Déchets
  { id: 138, sec: 8, text: "Tri conforme (DIB, Carton, Plastique, dangereux, etc.)" },
  { id: 139, sec: 8, text: "Conteneurs de collectes des déchets sont adaptés et étiquetés" },
  { id: 140, sec: 8, text: "Stockage temporaire sécurisé" },
  { id: 141, sec: 8, text: "Traçabilité / registre des déchets" },
  { id: 142, sec: 8, text: "Absence de débordement / fuite" }
];

const currentStep = ref(1);
const dateAudit = ref(new Date().toISOString().split('T')[0]);
const secteur = ref('');
const intervenants = ref('');
const commentairesGeneraux = ref('');

// Permis de Travail numeric state
const planPrevention = ref(0);
const permisHauteur = ref(0);
const permisFeu = ref(0);
const permisRemarques = ref('');

// Statistiques Accidents state
const selectedAnnee = ref(2026);
const targetIF = ref(2.5);
const targetTF = ref(0.0);
const targetTG = ref(0.0);
const targetIG = ref(0.0);

const MONTHS_KEYS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const MONTHS_LABELS = ['janv.-26', 'févr.-26', 'mars-26', 'avr.-26', 'mai-26', 'juin-26', 'juil.-26', 'août-26', 'sept.-26', 'oct.-26', 'nov.-26', 'déc.-26'];

const accidentData = reactive({});
const initAccidentData = () => {
  MONTHS_KEYS.forEach(m => {
    accidentData[m] = {
      nb_accidents_avec_arret: 0,
      nb_accidents_sans_arret: 0,
      nb_heures_travaillees: 0,
      nb_jours_perdus: 0,
      nb_travailleurs: 0,
      nb_visites_medicales: 0,
      nb_maladies_pro: 0,
      incapacite_permanente: 0,
    };
  });
};
initAccidentData();

// Checklist items answers state
const answers = reactive({});

const isPermis = computed(() => props.formType === 'permis_travail');
const isTournee = computed(() => props.formType === 'tournee_hse');
const isStatAccidents = computed(() => props.formType === 'statistiques_accidents' || props.formType === 'accident_travail');

const questionsData = computed(() => isTournee.value ? TOURNEE_HSE_QUESTIONS_DATA : AUDIT_QUESTIONS_DATA);

// RÈGLE MÉTIER FORMULAIRE UTILISATEUR :
// La première ligne qui contient nombre d'accident de travail doit afficher la somme entre sans arrêt et avec arrêt
const getAccidentTotal = (m) => {
  const avec = Number(accidentData[m]?.nb_accidents_avec_arret) || 0;
  const sans = Number(accidentData[m]?.nb_accidents_sans_arret) || 0;
  return avec + sans;
};

const getTotalAnnuel = (field) => {
  if (field === 'total_accidents') {
    return MONTHS_KEYS.reduce((acc, m) => acc + getAccidentTotal(m), 0);
  }
  return MONTHS_KEYS.reduce((acc, m) => acc + (Number(accidentData[m]?.[field]) || 0), 0);
};

const getDernierEffectif = () => {
  for (let i = MONTHS_KEYS.length - 1; i >= 0; i--) {
    const sal = Number(accidentData[MONTHS_KEYS[i]]?.nb_travailleurs) || 0;
    if (sal > 0) return sal;
  }
  return 0;
};

const getTF = (m) => {
  const avec = Number(accidentData[m]?.nb_accidents_avec_arret) || 0;
  const h = Number(accidentData[m]?.nb_heures_travaillees) || 0;
  return h > 0 ? Math.round((avec / h) * 1000000) : 0;
};

const getIF = (m) => {
  const avec = Number(accidentData[m]?.nb_accidents_avec_arret) || 0;
  const sal = Number(accidentData[m]?.nb_travailleurs) || 0;
  return sal > 0 ? ((avec / sal) * 1000).toFixed(2) : '0.00';
};

const getTG = (m) => {
  const jp = Number(accidentData[m]?.nb_jours_perdus) || 0;
  const h = Number(accidentData[m]?.nb_heures_travaillees) || 0;
  return h > 0 ? ((jp * 1000) / h).toFixed(4) : '0.0000';
};

const getIG = (m) => {
  const inc = Number(accidentData[m]?.incapacite_permanente) || 0;
  const h = Number(accidentData[m]?.nb_heures_travaillees) || 0;
  return h > 0 ? ((inc * 1000) / h).toFixed(4) : '0.0000';
};

watch(
  () => [props.editingAudit, props.formType],
  () => {
    if (props.editingAudit) {
      dateAudit.value = props.editingAudit.date_audit || new Date().toISOString().split('T')[0];
      secteur.value = props.editingAudit.secteur || '';
      intervenants.value = props.editingAudit.intervenants || '';
      commentairesGeneraux.value = props.editingAudit.commentaires_generaux || '';

      if (isPermis.value) {
        const items = props.editingAudit.items_data || {};
        planPrevention.value = items.plan_prevention || 0;
        permisHauteur.value = items.permis_hauteur || 0;
        permisFeu.value = items.permis_feu || 0;
        permisRemarques.value = items.remarques || '';
      } else if (isStatAccidents.value) {
        const items = props.editingAudit.items_data || {};
        selectedAnnee.value = items.annee || 2026;
        targetIF.value = items.target_if !== undefined ? items.target_if : 2.5;
        targetTF.value = items.target_tf !== undefined ? items.target_tf : 0.0;
        targetTG.value = items.target_tg !== undefined ? items.target_tg : 0.0;
        targetIG.value = items.target_ig !== undefined ? items.target_ig : 0.0;
        const months = items.months || {};
        MONTHS_KEYS.forEach(m => {
          const mData = months[m] || months[String(m)] || {};
          accidentData[m] = {
            nb_accidents_avec_arret: mData.nb_accidents_avec_arret || 0,
            nb_accidents_sans_arret: mData.nb_accidents_sans_arret || 0,
            nb_heures_travaillees: mData.nb_heures_travaillees || 0,
            nb_jours_perdus: mData.nb_jours_perdus || 0,
            nb_travailleurs: mData.nb_travailleurs || 0,
            nb_visites_medicales: mData.nb_visites_medicales || 0,
            nb_maladies_pro: mData.nb_maladies_pro || 0,
            incapacite_permanente: mData.incapacite_permanente || 0,
          };
        });
      } else {
        Object.keys(answers).forEach(k => delete answers[k]);
        Object.assign(answers, props.editingAudit.items_data || {});
      }
    } else {
      if (isStatAccidents.value) {
        initAccidentData();
      } else if (!isPermis.value) {
        Object.keys(answers).forEach(k => delete answers[k]);
        questionsData.value.forEach(q => {
          answers[q.id] = { val: 1, constat: '', photo: '', action: '', resp: '', delai: '', etat: 'Non engagée', comm: '' };
        });
      }
    }
  },
  { immediate: true }
);

const updateAnswer = (qId, field, val) => {
  if (!answers[qId]) {
    answers[qId] = { val: 1, constat: '', photo: '', action: '', resp: '', delai: '', etat: 'Non engagée', comm: '' };
  }
  answers[qId][field] = val;
};

const handlePhotoUpload = (qId, file) => {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    updateAnswer(qId, 'photo', e.target.result);
    emit('showToast', `Photo "${file.name}" ajoutée.`);
  };
  reader.readAsDataURL(file);
};

const calculateScore = () => {
  if (isPermis.value || isStatAccidents.value) return { score: '100.0', confCount: 0, nconfCount: 0, naCount: 0 };
  let confCount = 0, nconfCount = 0, naCount = 0;
  questionsData.value.forEach(q => {
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
  if (!secteur.value || !intervenants.value || !dateAudit.value) {
    emit('showToast', "Veuillez renseigner la Date, le Secteur et les Intervenants / Responsables à l'Étape 1.", 'error');
    currentStep.value = 1;
    return;
  }

  const API_AUDITS = window.location.origin + "/api/v1/audits";
  const token = localStorage.getItem("access_token");

  let reference = isStatAccidents.value ? 'FGSI-STAT-ACCIDENTS' : (isPermis.value ? 'FGSI-PERMIS' : (isTournee.value ? 'FGSI-010-Ind:A' : 'FGSI-001-Ind:F'));
  let itemsPayload = { ...answers };
  let scoreObject = { score: '100.0', confCount: 0, nconfCount: 0, naCount: 0 };
  let soldee = 0, non_engagee = 0, en_cours = 0, en_retard = 0;

  if (isPermis.value) {
    itemsPayload = {
      plan_prevention: parseInt(planPrevention.value || 0, 10),
      permis_hauteur: parseInt(permisHauteur.value || 0, 10),
      permis_feu: parseInt(permisFeu.value || 0, 10),
      remarques: permisRemarques.value
    };
  } else if (isStatAccidents.value) {
    const monthsPayload = {};
    MONTHS_KEYS.forEach(m => {
      const item = accidentData[m] || {};
      const avec = Number(item.nb_accidents_avec_arret) || 0;
      const sans = Number(item.nb_accidents_sans_arret) || 0;
      monthsPayload[m] = {
        nb_accidents_total: avec + sans,
        nb_accidents_avec_arret: avec,
        nb_accidents_sans_arret: sans,
        nb_heures_travaillees: Number(item.nb_heures_travaillees) || 0,
        nb_jours_perdus: Number(item.nb_jours_perdus) || 0,
        nb_travailleurs: Number(item.nb_travailleurs) || 0,
        nb_visites_medicales: Number(item.nb_visites_medicales) || 0,
        nb_maladies_pro: Number(item.nb_maladies_pro) || 0,
        incapacite_permanente: Number(item.incapacite_permanente) || 0,
      };
    });
    itemsPayload = {
      annee: selectedAnnee.value,
      target_if: targetIF.value,
      target_tf: targetTF.value,
      target_tg: targetTG.value,
      target_ig: targetIG.value,
      months: monthsPayload,
    };
  } else {
    scoreObject = calculateScore();
    questionsData.value.forEach(q => {
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
    form_type: props.formType,
    secteur: secteur.value,
    intervenants: intervenants.value,
    date_audit: dateAudit.value,
    commentaires_generaux: commentairesGeneraux.value,
    taux_conformite: (isPermis.value || isStatAccidents.value) ? 100.0 : parseFloat(scoreObject.score),
    total_conforme: (isPermis.value || isStatAccidents.value) ? 0 : scoreObject.confCount,
    total_non_conforme: (isPermis.value || isStatAccidents.value) ? 0 : scoreObject.nconfCount,
    total_na: (isPermis.value || isStatAccidents.value) ? 0 : scoreObject.naCount,
    count_soldee: soldee,
    count_non_engagee: non_engagee,
    count_en_cours: en_cours,
    count_en_retard: en_retard,
    items_data: itemsPayload
  };

  try {
    const url = props.editingAudit ? `${API_AUDITS}/${props.editingAudit.id}` : `${API_AUDITS}/`;
    const method = props.editingAudit ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      emit('showToast', props.editingAudit ? `Fiche #ACTIA-${props.editingAudit.id} mise à jour avec succès !` : `Fiche ${isStatAccidents.value ? 'Statistiques Accidents SST' : (isPermis.value ? 'Permis de Travail' : 'HSE')} enregistrée avec succès !`);
      emit('submitSuccess');
    } else {
      emit('showToast', "Erreur lors de la sauvegarde", 'error');
    }
  } catch (err) {
    emit('showToast', "Erreur de connexion", 'error');
  }
};

const nextStep = () => {
  if ((isPermis.value || isStatAccidents.value) && currentStep.value === 2) currentStep.value = 5;
  else if (currentStep.value < 5) currentStep.value++;
};

const prevStep = () => {
  if ((isPermis.value || isStatAccidents.value) && currentStep.value === 5) currentStep.value = 2;
  else if (currentStep.value > 1) currentStep.value--;
};

const scoreObj = computed(() => calculateScore());
const nonConformingActions = computed(() => questionsData.value.filter(q => answers[q.id] && answers[q.id].val === 0));

const steps = [1, 2, 3, 4, 5];

const getStepLabel = (step) => {
  if (step === 1) return "Infos Générales";
  if (step === 2) return isPermis.value ? "Permis & Saisie" : (isStatAccidents.value ? "Grille Mensuelle SST" : (isTournee.value ? "Sécurité & Chimiques" : "EPI & Opérateurs"));
  if (step === 3) return isTournee.value ? "ATEX & Maintenance" : "5S & Machines";
  if (step === 4) return isTournee.value ? "Incendie & Déchets" : "Incendie & Ergonomie";
  return "Synthèse & Validation";
};

const isTargetStepForQuestion = (q, step) => {
  if (step === 2 && (q.sec === 1 || q.sec === 2 || (isTournee.value && q.sec === 3))) return true;
  if (step === 3 && ((isTournee.value && (q.sec === 4 || q.sec === 5)) || (!isTournee.value && (q.sec === 3 || q.sec === 4)))) return true;
  if (step === 4 && ((isTournee.value && (q.sec === 6 || q.sec === 7 || q.sec === 8)) || (!isTournee.value && (q.sec === 5 || q.sec === 6 || q.sec === 7)))) return true;
  return false;
};

</script>

<template>
  <div style="background: #f8fafc; color: #0f172a; border-radius: 16px; padding: 2rem; box-shadow: 0 20px 40px rgba(0,0,0,0.4); border: 1px solid #e2e8f0;">
    
    <!-- EDIT MODE BANNER -->
    <div v-if="editingAudit" style="background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; padding: 14px 22px; border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 15px rgba(217,119,6,0.3); flex-wrap: wrap; gap: 12px;">
      <div style="display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 0.95rem;">
        <FileText :size="22" color="#fef08a" />
        <div>
          <div>Mode Modification : Fiche <strong style="color: #fef08a;">#ACTIA-{{ editingAudit.id }}</strong></div>
          <div style="font-size: 0.78rem; opacity: 0.9; font-weight: 500;">Modifiez les champs ci-dessous puis validez votre mise à jour.</div>
        </div>
      </div>
      <button type="button" @click="emit('close')" style="background: rgba(0,0,0,0.3); color: #ffffff; padding: 8px 18px; font-size: 0.85rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; cursor: pointer;">
        Annuler la modification
      </button>
    </div>

    <!-- HEADER TOP -->
    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 1.25rem; margin-bottom: 1.5rem; border-bottom: 2px solid #e2e8f0;">
      <button class="btn btn-secondary" @click="emit('close')" style="background: #e2e8f0; color: #334155;">
        <ArrowLeft :size="16" /> Retour aux Formulaires
      </button>
      <div style="text-align: center;">
        <h2 style="font-size: 1.3rem; font-weight: 800; color: #0f172a;">
          <template v-if="editingAudit">
            Modification {{ isStatAccidents ? 'Statistiques Accidents' : (isPermis ? 'Permis' : (isTournee ? 'Tournée' : 'Audit')) }} #ACTIA-{{ editingAudit.id }}
          </template>
          <template v-else>
            {{ isStatAccidents ? 'Suivi Mensuel des Accidents & Santé (FGSI-STAT-ACCIDENTS)' : (isPermis ? 'Permis de Travail (FGSI-PERMIS)' : (isTournee ? 'Tournée HSE Terrain (FGSI-010-Ind:A)' : 'Audit HSE Terrain (FGSI-001-Ind:F)')) }}
          </template>
        </h2>
        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">CIPI ACTIA — Portail HSE Responsable</div>
      </div>
      <span style="background: #003d4d; color: #a8e063; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;">
        {{ isStatAccidents ? 'Réf: FGSI-STAT-ACCIDENTS' : (isPermis ? 'Permis FGSI-PERMIS' : (isTournee ? 'Tournée FGSI-010-Ind:A' : 'Audit FGSI-001-Ind:F')) }}
      </span>
    </div>

    <!-- STEPPER BAR -->
    <div style="display: flex; justify-content: space-between; position: relative; margin-bottom: 2.25rem;">
      <template v-for="step in steps" :key="step">
        <div v-if="!((isPermis || isStatAccidents) && (step === 3 || step === 4))" @click="currentStep = step" style="display: flex; flex-direction: column; align-items: center; cursor: pointer; z-index: 2;">
          <div :style="{ width: '40px', height: '40px', borderRadius: '50%', background: currentStep === step ? '#00c996' : (currentStep > step ? '#56ab2f' : '#ffffff'), border: '3px solid', borderColor: currentStep === step ? '#00c996' : (currentStep > step ? '#56ab2f' : '#cbd5e1'), color: currentStep === step || currentStep > step ? '#fff' : '#64748b', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center' }">
            {{ step === 5 && (isPermis || isStatAccidents) ? 3 : step }}
          </div>
          <span :style="{ fontSize: '0.78rem', fontWeight: '700', color: currentStep === step ? '#0f172a' : '#64748b', marginTop: '8px' }">{{ getStepLabel(step) }}</span>
        </div>
      </template>
    </div>

    <!-- STEP 1: INFOS -->
    <div v-if="currentStep === 1" class="wizard-card" style="background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;">
      <h3 style="font-size: 1.1rem; font-weight: 800; color: #0f172a; margin-bottom: 1.25rem; border-bottom: 1px dashed #e2e8f0; padding-bottom: 10px;">Étape 1 : Informations Générales d'Audit</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem;">
        <div>
          <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">Date d'Audit / Fiche</label>
          <input type="date" class="light-input" v-model="dateAudit" required />
        </div>
        <div>
          <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">Secteur / Zone de travail</label>
          <input type="text" class="light-input" placeholder="ex: Ligne CMS / Production A" v-model="secteur" required />
        </div>
        <div>
          <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">Intervenants / Responsables</label>
          <input type="text" class="light-input" placeholder="ex: M. Responsable HSE / Equipe" v-model="intervenants" required />
        </div>
        <div v-if="isStatAccidents">
          <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">Année de suivi</label>
          <input type="number" class="light-input" v-model.number="selectedAnnee" min="2020" max="2035" required />
        </div>
      </div>
    </div>

    <!-- STEP 2: STATISTIQUES ACCIDENTS & SANTÉ MENSUELLE -->
    <div v-if="currentStep === 2 && isStatAccidents" class="wizard-card" style="background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 10px;">
        <div>
          <h3 style="font-size: 1.15rem; font-weight: 800; color: #d97706; display: flex; align-items: center; gap: 8px;">
            <Activity :size="20" color="#d97706" /> Tableau Mensuel de Suivi des Accidents & Santé (Exercice {{ selectedAnnee }})
          </h3>
          <p style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
            Tous les champs sont numériques. La 1ère ligne (Total Accidents) est la somme automatique des accidents avec arrêt et sans arrêt.
          </p>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span style="font-size: 0.78rem; font-weight: 700; color: #475569;">Cible IF (Target):</span>
          <input type="number" step="0.1" v-model.number="targetIF" style="width: 70px; padding: 4px 8px; font-weight: 800; font-size: 0.85rem; border: 1px solid #cbd5e1; border-radius: 6px; text-align: center;" />
        </div>
      </div>

      <!-- TABLEAU EXCEL GRID -->
      <div style="overflow-x: auto; border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 1.5rem;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: center; min-width: 1100px;">
          <thead>
            <tr style="background: #003d4d; color: #fff;">
              <th style="padding: 10px 14px; text-align: left; font-weight: 800; min-width: 260px; border: 1px solid #002833;">Données</th>
              <th v-for="(lbl, idx) in MONTHS_LABELS" :key="idx" style="padding: 8px 4px; font-weight: 700; font-size: 0.75rem; border: 1px solid #002833; width: 75px;">
                {{ lbl }}
              </th>
              <th style="padding: 10px 12px; font-weight: 800; background: #002833; color: #a8e063; min-width: 95px; border: 1px solid #001c24;">Total Annuel</th>
            </tr>
          </thead>
          <tbody>

            <!-- LIGNE 1 : NOMBRE D'ACCIDENTS (SOMME AVEC ARRET + SANS ARRET) -->
            <tr style="background: #f0fdf4; border-bottom: 2px solid #bbf7d0;">
              <td style="padding: 10px 14px; text-align: left; font-weight: 800; color: #166534; border: 1px solid #e2e8f0;">
                ★ Nombre d'accident de travail <span style="font-size: 0.7rem; font-weight: 600; color: #15803d; display: block;">(Somme : Avec Arrêt + Sans Arrêt)</span>
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'acc-tot-' + m" style="padding: 6px; border: 1px solid #e2e8f0; font-size: 0.95rem; font-weight: 800; color: #15803d; background: #dcfce7;">
                {{ getAccidentTotal(m) }}
              </td>
              <td style="padding: 6px; border: 1px solid #e2e8f0; font-size: 1.05rem; font-weight: 800; color: #166534; background: #bbf7d0;">
                {{ getTotalAnnuel('total_accidents') }}
              </td>
            </tr>

            <!-- LIGNE 2 : ACCIDENTS AVEC ARRET -->
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 700; color: #334155; border: 1px solid #e2e8f0;">
                Nombre d'accidents du travail avec arrêt
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'acc-avec-' + m" style="padding: 4px; border: 1px solid #e2e8f0;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_accidents_avec_arret" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.85rem;" />
              </td>
              <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #0f172a; background: #f8fafc;">
                {{ getTotalAnnuel('nb_accidents_avec_arret') }}
              </td>
            </tr>

            <!-- LIGNE 3 : ACCIDENTS SANS ARRET -->
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 700; color: #334155; border: 1px solid #e2e8f0;">
                Nombre d'accident de travail sans arrêt
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'acc-sans-' + m" style="padding: 4px; border: 1px solid #e2e8f0;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_accidents_sans_arret" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.85rem;" />
              </td>
              <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #0f172a; background: #f8fafc;">
                {{ getTotalAnnuel('nb_accidents_sans_arret') }}
              </td>
            </tr>

            <!-- LIGNE 4 : HEURES TRAVAILLEES (JAUNE) -->
            <tr style="background: #fef9c3; border-bottom: 1px solid #fde047;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #854d0e; border: 1px solid #fde047;">
                Nombre d'heures travaillées
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'heures-' + m" style="padding: 4px; border: 1px solid #fde047;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_heures_travaillees" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #fde047; background: #fff; border-radius: 4px; font-size: 0.82rem; color: #854d0e;" />
              </td>
              <td style="padding: 6px; border: 1px solid #fde047; font-weight: 800; color: #854d0e; background: #fef08a;">
                {{ getTotalAnnuel('nb_heures_travaillees').toLocaleString() }}
              </td>
            </tr>

            <!-- LIGNE 5 : JOURS PERDUS -->
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 700; color: #334155; border: 1px solid #e2e8f0;">
                nombre total de jours perdus (Accident avec Arrêt)
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'jours-' + m" style="padding: 4px; border: 1px solid #e2e8f0;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_jours_perdus" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.85rem;" />
              </td>
              <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #0f172a; background: #f8fafc;">
                {{ getTotalAnnuel('nb_jours_perdus') }}
              </td>
            </tr>

            <!-- LIGNE 6 : NOMBRE DES TRAVAILLEURS (JAUNE) -->
            <tr style="background: #fef9c3; border-bottom: 1px solid #fde047;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #854d0e; border: 1px solid #fde047;">
                Nombre des travailleurs
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'salaries-' + m" style="padding: 4px; border: 1px solid #fde047;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_travailleurs" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #fde047; background: #fff; border-radius: 4px; font-size: 0.82rem; color: #854d0e;" />
              </td>
              <td style="padding: 6px; border: 1px solid #fde047; font-weight: 800; color: #854d0e; background: #fef08a;">
                {{ getDernierEffectif() }} (eff.)
              </td>
            </tr>

            <!-- LIGNE 7 : NOMBRE DES VISITES MEDICALES (JAUNE) -->
            <tr style="background: #fef9c3; border-bottom: 1px solid #fde047;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #854d0e; border: 1px solid #fde047;">
                Nombre des visites médicales
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'visites-' + m" style="padding: 4px; border: 1px solid #fde047;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_visites_medicales" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #fde047; background: #fff; border-radius: 4px; font-size: 0.82rem; color: #854d0e;" />
              </td>
              <td style="padding: 6px; border: 1px solid #fde047; font-weight: 800; color: #854d0e; background: #fef08a;">
                {{ getTotalAnnuel('nb_visites_medicales') }}
              </td>
            </tr>

            <!-- LIGNE 8 : NOMBRE DES MALADIES PROFESSIONNELLES (JAUNE) -->
            <tr style="background: #fef9c3; border-bottom: 2px solid #e2e8f0;">
              <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #854d0e; border: 1px solid #fde047;">
                Nombre des maladies Professionnelle
              </td>
              <td v-for="m in MONTHS_KEYS" :key="'maladies-' + m" style="padding: 4px; border: 1px solid #fde047;">
                <input type="number" min="0" v-model.number="accidentData[m].nb_maladies_pro" style="width: 100%; padding: 6px 2px; text-align: center; font-weight: 700; border: 1px solid #fde047; background: #fff; border-radius: 4px; font-size: 0.82rem; color: #854d0e;" />
              </td>
              <td style="padding: 6px; border: 1px solid #fde047; font-weight: 800; color: #854d0e; background: #fef08a;">
                {{ getTotalAnnuel('nb_maladies_pro') }}
              </td>
            </tr>

          </tbody>
        </table>
      </div>

      <!-- TABLEAU 2 : INDICATEURS CALCULÉS TF, IF, TG, IG -->
      <div style="margin-top: 1.75rem;">
        <h4 style="font-size: 1rem; font-weight: 800; color: #0284c7; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
          <TrendingUp :size="18" color="#0284c7" /> Indicateurs Clés de Sécurité Calculés (TF, IF, TG, IG)
        </h4>
        <div style="overflow-x: auto; border: 1px solid #cbd5e1; border-radius: 8px;">
          <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: center; min-width: 1100px;">
            <thead>
              <tr style="background: #0284c7; color: #fff;">
                <th style="padding: 8px 14px; text-align: left; font-weight: 800; min-width: 260px; border: 1px solid #0369a1;">Indicateur</th>
                <th v-for="(lbl, idx) in MONTHS_LABELS" :key="'kpi-lbl-' + idx" style="padding: 8px 4px; font-weight: 700; font-size: 0.75rem; border: 1px solid #0369a1; width: 75px;">
                  {{ lbl }}
                </th>
                <th style="padding: 8px 12px; font-weight: 800; background: #0369a1; color: #fff; min-width: 95px; border: 1px solid #075985;">Cumul Annuel</th>
              </tr>
            </thead>
            <tbody>
              <!-- TF -->
              <tr style="background: #f0fdf4; border-bottom: 1px solid #cbd5e1;">
                <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #166534; border: 1px solid #e2e8f0;">
                  TF : Taux de Fréquence <span style="font-size: 0.7rem; font-weight: 500; color: #64748b;">(Acc. arrêt / Heures) × 1M</span>
                </td>
                <td v-for="m in MONTHS_KEYS" :key="'tf-' + m" style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 700; color: #166534;">
                  {{ getTF(m) }}
                </td>
                <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #166534; background: #dcfce7;">
                  {{ getTotalAnnuel('nb_heures_travaillees') > 0 ? Math.round((getTotalAnnuel('nb_accidents_avec_arret') / getTotalAnnuel('nb_heures_travaillees')) * 1000000) : 0 }}
                </td>
              </tr>

              <!-- IF -->
              <tr style="border-bottom: 1px solid #cbd5e1;">
                <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #1e40af; border: 1px solid #e2e8f0;">
                  IF : Indice de Fréquence <span style="font-size: 0.7rem; font-weight: 500; color: #64748b;">(Acc. arrêt / Salariés) × 1 000</span>
                </td>
                <td v-for="m in MONTHS_KEYS" :key="'if-' + m" :style="{
                  padding: '6px',
                  border: '1px solid #e2e8f0',
                  fontWeight: '800',
                  color: '#fff',
                  background: Number(getIF(m)) > targetIF ? '#ef4444' : (Number(getIF(m)) > 0 ? '#10b981' : '#f8fafc')
                }">
                  <span :style="{ color: (Number(getIF(m)) === 0) ? '#64748b' : '#fff' }">{{ getIF(m) }}</span>
                </td>
                <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #1e40af; background: #dbeafe;">
                  {{ getDernierEffectif() > 0 ? ((getTotalAnnuel('nb_accidents_avec_arret') / getDernierEffectif()) * 1000).toFixed(2) : '0.00' }}
                </td>
              </tr>

              <!-- TARGET IF -->
              <tr style="background: #fef2f2; border-bottom: 1px solid #cbd5e1;">
                <td style="padding: 6px 14px; text-align: left; font-weight: 700; color: #991b1b; border: 1px solid #e2e8f0;">
                  Target IF (Seuil cible)
                </td>
                <td v-for="m in MONTHS_KEYS" :key="'target-if-' + m" style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 700; color: #991b1b;">
                  {{ targetIF }}
                </td>
                <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #991b1b; background: #fee2e2;">
                  {{ targetIF }}
                </td>
              </tr>

              <!-- TG -->
              <tr style="background: #fffbeb; border-bottom: 1px solid #cbd5e1;">
                <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #b45309; border: 1px solid #e2e8f0;">
                  TG : Taux de Gravité <span style="font-size: 0.7rem; font-weight: 500; color: #64748b;">(Jours perdus × 1 000) / Heures</span>
                </td>
                <td v-for="m in MONTHS_KEYS" :key="'tg-' + m" style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 700; color: #b45309;">
                  {{ getTG(m) }}
                </td>
                <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #b45309; background: #fef3c7;">
                  {{ getTotalAnnuel('nb_heures_travaillees') > 0 ? ((getTotalAnnuel('nb_jours_perdus') * 1000) / getTotalAnnuel('nb_heures_travaillees')).toFixed(4) : '0.0000' }}
                </td>
              </tr>

              <!-- SOMME TAUX INCAPACITE PERMANENTE (POUR IG) -->
              <tr style="border-bottom: 1px solid #cbd5e1;">
                <td style="padding: 6px 14px; text-align: left; font-weight: 700; color: #475569; border: 1px solid #e2e8f0;">
                  Somme taux incapacité permanente (%)
                </td>
                <td v-for="m in MONTHS_KEYS" :key="'incap-' + m" style="padding: 4px; border: 1px solid #e2e8f0;">
                  <input type="number" min="0" step="0.1" v-model.number="accidentData[m].incapacite_permanente" style="width: 100%; padding: 4px 2px; text-align: center; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.8rem;" />
                </td>
                <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 700; color: #475569; background: #f8fafc;">
                  {{ getTotalAnnuel('incapacite_permanente') }} %
                </td>
              </tr>

              <!-- IG -->
              <tr style="background: #faf5ff;">
                <td style="padding: 8px 14px; text-align: left; font-weight: 800; color: #7e22ce; border: 1px solid #e2e8f0;">
                  IG : Indice de Gravité <span style="font-size: 0.7rem; font-weight: 500; color: #64748b;">(Incap. perm. × 1 000) / Heures</span>
                </td>
                <td v-for="m in MONTHS_KEYS" :key="'ig-' + m" style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 700; color: #7e22ce;">
                  {{ getIG(m) }}
                </td>
                <td style="padding: 6px; border: 1px solid #e2e8f0; font-weight: 800; color: #7e22ce; background: #f3e8ff;">
                  {{ getTotalAnnuel('nb_heures_travaillees') > 0 ? ((getTotalAnnuel('incapacite_permanente') * 1000) / getTotalAnnuel('nb_heures_travaillees')).toFixed(4) : '0.0000' }}
                </td>
              </tr>

            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- STEP 2: PERMIS DE TRAVAIL NUMERIC FORM -->
    <div v-if="currentStep === 2 && isPermis" class="wizard-card" style="background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;">
      <h3 style="font-size: 1.1rem; font-weight: 800; color: #3b82f6; margin-bottom: 8px;"><Shield :size="20" style="display: inline; margin-right: 8px;"/> Formulaire Permis de Travail (FGSI-PERMIS)</h3>
      <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1.25rem;">Saisissez le nombre de permis délivrés pour les travaux planifiés :</p>
      
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
        <div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border: 1px solid #cbd5e1; border-top: 4px solid #3b82f6;">
          <label style="font-size: 0.88rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 6px; margin-bottom: 6px;"><FileText :size="16" color="#3b82f6"/> Plan de Prévention</label>
          <span style="font-size: 0.75rem; color: #64748b; display: block; margin-bottom: 8px;">Nombre de plans établis</span>
          <input type="number" class="light-input" min="0" v-model="planPrevention" style="font-size: 1.3rem; font-weight: 800; color: #1d4ed8; text-align: center;" />
        </div>

        <div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border: 1px solid #cbd5e1; border-top: 4px solid #ea580c;">
          <label style="font-size: 0.88rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 6px; margin-bottom: 6px;"><HardHat :size="16" color="#ea580c"/> Permis Travail en Hauteur</label>
          <span style="font-size: 0.75rem; color: #64748b; display: block; margin-bottom: 8px;">Nombre de permis hauteur</span>
          <input type="number" class="light-input" min="0" v-model="permisHauteur" style="font-size: 1.3rem; font-weight: 800; color: #c2410c; text-align: center;" />
        </div>

        <div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border: 1px solid #cbd5e1; border-top: 4px solid #dc2626;">
          <label style="font-size: 0.88rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 6px; margin-bottom: 6px;"><Flame :size="16" color="#dc2626"/> Permis de Feu</label>
          <span style="font-size: 0.75rem; color: #64748b; display: block; margin-bottom: 8px;">Nombre de permis feu délivrés</span>
          <input type="number" class="light-input" min="0" v-model="permisFeu" style="font-size: 1.3rem; font-weight: 800; color: #b91c1c; text-align: center;" />
        </div>
      </div>

      <div>
        <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">Remarques & Précautions Spécifiques</label>
        <textarea class="light-input" rows="3" placeholder="Description des travaux, précautions..." v-model="permisRemarques"></textarea>
      </div>
    </div>

    <!-- CHECKLIST ITEMS FOR AUDIT / TOURNÉE -->
    <div v-if="!isPermis && !isStatAccidents && (currentStep === 2 || currentStep === 3 || currentStep === 4)">
      <template v-for="q in questionsData" :key="q.id">
        <div v-if="isTargetStepForQuestion(q, currentStep)" style="background: #fff; border-radius: 10px; padding: 1.25rem; margin-bottom: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
          <div style="font-size: 0.93rem; font-weight: 700; color: #1e293b;">{{ q.id }}. {{ q.text }}</div>
          <div style="display: flex; gap: 8px; margin-top: 10px;">
            <button type="button" @click="updateAnswer(q.id, 'val', 1)" :style="{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: '700', border: '1px solid', borderColor: answers[q.id]?.val === 1 ? '#10b981' : '#cbd5e1', background: answers[q.id]?.val === 1 ? '#10b981' : '#f8fafc', color: answers[q.id]?.val === 1 ? '#fff' : '#475569', cursor: 'pointer' }">✓ Conforme (1)</button>
            <button type="button" @click="updateAnswer(q.id, 'val', 0)" :style="{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: '700', border: '1px solid', borderColor: answers[q.id]?.val === 0 ? '#ef4444' : '#cbd5e1', background: answers[q.id]?.val === 0 ? '#ef4444' : '#f8fafc', color: answers[q.id]?.val === 0 ? '#fff' : '#475569', cursor: 'pointer' }">✗ Non Conforme (0)</button>
            <button type="button" @click="updateAnswer(q.id, 'val', 'NA')" :style="{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: '700', border: '1px solid', borderColor: answers[q.id]?.val === 'NA' ? '#64748b' : '#cbd5e1', background: answers[q.id]?.val === 'NA' ? '#64748b' : '#f8fafc', color: answers[q.id]?.val === 'NA' ? '#fff' : '#475569', cursor: 'pointer' }">N/A</button>
          </div>

          <!-- FULL NON-CONFORME ACTION SUBCARD -->
          <div v-if="answers[q.id]?.val === 0" style="margin-top: 12px; padding: 1.25rem; background: #f8fafc; border-left: 4px solid #ef4444; border-radius: 8px; border: 1px solid #fee2e2;">
            <div style="font-size: 0.82rem; font-weight: 800; color: #ef4444; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
              <AlertTriangle :size="16" color="#ef4444" /> Action Corrective & Constat Requis
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
              
              <!-- CONSTAT -->
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">Constat détecté</label>
                <input type="text" class="light-input" placeholder="Description du constat..." :value="answers[q.id]?.constat || ''" @input="e => updateAnswer(q.id, 'constat', e.target.value)" />
              </div>

              <!-- PHOTO DROPZONE / FILE PICKER -->
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">Photo (Facultatif — Parcourir)</label>
                <div v-if="!answers[q.id]?.photo" style="border: 2px dashed #00c996; background: rgba(0,201,150,0.05); padding: 10px; border-radius: 8px; text-align: center; cursor: pointer;">
                  <label style="cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.78rem; color: #00c996; font-weight: 700;">
                    <Camera :size="16" /> Glisser une photo ou Parcourir
                    <input type="file" accept="image/*" style="display: none;" @change="e => handlePhotoUpload(q.id, e.target.files[0])" />
                  </label>
                </div>
                <div v-else style="display: flex; align-items: center; gap: 10px; background: #fff; padding: 6px 12px; border-radius: 8px; border: 1px solid #cbd5e1;">
                  <img :src="answers[q.id]?.photo" alt="Constat" style="width: 38px; height: 38px; object-fit: cover; border-radius: 6px; border: 1px solid #00c996;" />
                  <span style="font-size: 0.78rem; font-weight: 600; color: #0f172a; flex: 1;">Photo enregistrée</span>
                  <button type="button" @click="updateAnswer(q.id, 'photo', '')" style="background: transparent; border: none; color: #ef4444; cursor: pointer;"><X :size="18"/></button>
                </div>
              </div>

              <!-- ACTION PROPOSÉE -->
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">Action à mener</label>
                <input type="text" class="light-input" placeholder="Action corrective proposée..." :value="answers[q.id]?.action || ''" @input="e => updateAnswer(q.id, 'action', e.target.value)" />
              </div>

              <!-- RESPONSABLE DÉSIGNÉ -->
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">Responsable désigné</label>
                <input type="text" class="light-input" placeholder="ex: Responsable Maintenance" :value="answers[q.id]?.resp || ''" @input="e => updateAnswer(q.id, 'resp', e.target.value)" />
              </div>

              <!-- DÉLAI & ÉTAT ACTION -->
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div>
                  <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">Délai (Date)</label>
                  <input type="date" class="light-input" :value="answers[q.id]?.delai || ''" @input="e => updateAnswer(q.id, 'delai', e.target.value)" />
                </div>
                <div>
                  <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">État Action</label>
                  <select class="light-input" :value="answers[q.id]?.etat || 'Non engagée'" @change="e => updateAnswer(q.id, 'etat', e.target.value)">
                    <option value="Non engagée">Non engagée</option>
                    <option value="En cours">En cours</option>
                    <option value="Soldée">Soldée</option>
                    <option value="En retard">En retard</option>
                  </select>
                </div>
              </div>

              <!-- COMMENTAIRES -->
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">Commentaires / Observations</label>
                <input type="text" class="light-input" placeholder="Remarques..." :value="answers[q.id]?.comm || ''" @input="e => updateAnswer(q.id, 'comm', e.target.value)" />
              </div>

            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- STEP 5: SYNTHÈSE & SUBMISSION -->
    <div v-if="currentStep === 5">
      <div style="background: linear-gradient(135deg, #003d4d 0%, #001c24 100%); color: #fff; border-radius: 12px; padding: 1.75rem; display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
        <div>
          <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #a8e063;">Synthèse de la Fiche</div>
          <div style="font-size: 1.4rem; font-weight: 800; margin-top: 4px;">
            {{ isStatAccidents ? `Bilan Annuel des Accidents SST ${selectedAnnee}` : (isPermis ? 'Permis de Travail Enregistré' : 'Taux de Conformité HSE') }}
          </div>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; font-family: var(--font-mono); color: #00c996;">
          {{ isStatAccidents ? `TOTAL: ${getTotalAnnuel('total_accidents')}` : (isPermis ? 'FGSI-PERMIS' : `${scoreObj.score} %`) }}
        </div>
      </div>

      <!-- SYNTHESE STATISTIQUES ACCIDENTS -->
      <div v-if="isStatAccidents" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div style="padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Total Accidents</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #059669; margin-top: 4px;">{{ getTotalAnnuel('total_accidents') }}</div>
          <div style="font-size: 0.75rem; color: #64748b;">{{ getTotalAnnuel('nb_accidents_avec_arret') }} avec arrêt · {{ getTotalAnnuel('nb_accidents_sans_arret') }} sans arrêt</div>
        </div>

        <div style="padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 8px;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Heures Travaillées</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #1d4ed8; margin-top: 4px;">{{ getTotalAnnuel('nb_heures_travaillees').toLocaleString() }} h</div>
          <div style="font-size: 0.75rem; color: #64748b;">Cumul annuel</div>
        </div>

        <div style="padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #ef4444; border-radius: 8px;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Jours Perdus</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #b91c1c; margin-top: 4px;">{{ getTotalAnnuel('nb_jours_perdus') }} j</div>
          <div style="font-size: 0.75rem; color: #64748b;">Incapacité temporaire</div>
        </div>

        <div style="padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 8px;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Taux Fréquence (TF)</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #0284c7; margin-top: 4px;">
            {{ getTotalAnnuel('nb_heures_travaillees') > 0 ? Math.round((getTotalAnnuel('nb_accidents_avec_arret') / getTotalAnnuel('nb_heures_travaillees')) * 1000000) : 0 }}
          </div>
          <div style="font-size: 0.75rem; color: #64748b;">Moyen annuel</div>
        </div>

        <div style="padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; border-radius: 8px;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Indice Fréquence (IF)</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #d97706; margin-top: 4px;">
            {{ getDernierEffectif() > 0 ? ((getTotalAnnuel('nb_accidents_avec_arret') / getDernierEffectif()) * 1000).toFixed(2) : '0.00' }}
          </div>
          <div style="font-size: 0.75rem; color: #64748b;">Cible: {{ targetIF }}</div>
        </div>

        <div style="padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; border-radius: 8px;">
          <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Santé au Travail</div>
          <div style="font-size: 1.4rem; font-weight: 800; color: #7c3aed; margin-top: 4px;">
            {{ getTotalAnnuel('nb_visites_medicales') }} V. / {{ getTotalAnnuel('nb_maladies_pro') }} MP
          </div>
          <div style="font-size: 0.75rem; color: #64748b;">Visites / Maladies pro</div>
        </div>
      </div>

      <div v-else-if="isPermis" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div style="padding: 15px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 8px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #64748b;">Plan de Prévention</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #1d4ed8; margin-top: 4px;">{{ planPrevention }}</div>
        </div>
        <div style="padding: 15px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #ea580c; border-radius: 8px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #64748b;">Permis Hauteur</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #c2410c; margin-top: 4px;">{{ permisHauteur }}</div>
        </div>
        <div style="padding: 15px; background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #dc2626; border-radius: 8px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #64748b;">Permis de Feu</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: #b91c1c; margin-top: 4px;">{{ permisFeu }}</div>
        </div>
      </div>
      <div v-else-if="nonConformingActions.length > 0" class="wizard-card" style="background: #fff; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #e2e8f0;">
        <h3 style="font-size: 1.05rem; font-weight: 800; color: #ef4444; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
          <AlertTriangle :size="18" color="#ef4444" /> Tableau Récapitulatif des Actions Correctives Générées ({{ nonConformingActions.length }})
        </h3>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem;">
            <thead>
              <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0; color: #475569; text-align: left;">
                <th style="padding: 10px;">Constat</th>
                <th style="padding: 10px;">Action Proposée</th>
                <th style="padding: 10px;">Responsable</th>
                <th style="padding: 10px;">Délai</th>
                <th style="padding: 10px;">État</th>
                <th style="padding: 10px;">Photo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in nonConformingActions" :key="q.id" style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px; color: #1e293b;">{{ answers[q.id]?.constat || 'Non renseigné' }}</td>
                <td style="padding: 10px; color: #1e293b;">{{ answers[q.id]?.action || 'Non renseignée' }}</td>
                <td style="padding: 10px; color: #64748b;">{{ answers[q.id]?.resp || 'Non désigné' }}</td>
                <td style="padding: 10px; color: #64748b;">{{ answers[q.id]?.delai || 'Non défini' }}</td>
                <td style="padding: 10px;">
                  <span :style="{ padding: '3px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: '800', background: answers[q.id]?.etat === 'Soldée' ? '#dcfce7' : (answers[q.id]?.etat === 'En cours' ? '#dbeafe' : '#fee2e2'), color: answers[q.id]?.etat === 'Soldée' ? '#166534' : (answers[q.id]?.etat === 'En cours' ? '#1e40af' : '#991b1b') }">
                    {{ answers[q.id]?.etat || 'Non engagée' }}
                  </span>
                </td>
                <td style="padding: 10px;">
                  <img v-if="answers[q.id]?.photo" :src="answers[q.id].photo" alt="Photo" style="width: 32px; height: 32px; border-radius: 4px; object-fit: cover;" />
                  <span v-else>—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>


      <div style="margin-bottom: 1.5rem;">
        <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">Commentaires généraux des auditeurs / intervenants</label>
        <textarea class="light-input" rows="4" placeholder="Remarques finales..." v-model="commentairesGeneraux"></textarea>
      </div>
    </div>

    <!-- FOOTER ACTIONS -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2rem; padding-top: 1.25rem; border-top: 2px solid #e2e8f0;">
      <button class="btn btn-secondary" @click="prevStep" :style="{ visibility: currentStep === 1 ? 'hidden' : 'visible', background: '#e2e8f0', color: '#334155' }">
        <ChevronLeft :size="16" /> Étape Précédente
      </button>
      <button class="btn btn-primary" @click="currentStep === 5 ? handleSubmit() : nextStep()" style="max-width: 260px;">
        <template v-if="currentStep === 5">
          {{ editingAudit ? 'Mettre à jour la Fiche' : 'Soumettre la Fiche HSE' }}
        </template>
        <template v-else>
          Étape Suivante <ChevronRight :size="16" />
        </template>
      </button>
    </div>

  </div>
</template>
