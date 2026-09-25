"""
===============================================================================
NOTE HISTORIQUE — AUDIT.PY (FICHIER SUPPRIMÉ)
===============================================================================
L'ancien modèle `HSEAudit` qui résidait dans ce fichier a été supprimé.

Raison :
  La table `hse_audits` était un vestige du prototypage initial. Elle stockait
  les audits HSE au format JSON semi-structuré (`items_data`), sans normalisation.

  Depuis l'introduction du patron Joined Table Inheritance dans `submission.py`,
  toutes les soumissions HSE passent par :
    - `FormSubmission` (table mère polymorphique)
    - `AuditHSESubmission` / `TourneeHSESubmission` / etc. (tables filles)
    - `AuditHSEItem` / `TourneeHSEItem` / etc. (tables d'items normalisées)

  La table `hse_audits` ne contenait aucune donnée de production et a été retirée
  pour simplifier le schéma et éviter toute confusion avec le système d'héritage.

Date de suppression : 2026-09-23
===============================================================================
"""
