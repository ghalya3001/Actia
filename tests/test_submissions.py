"""
Tests d'intégration complets pour les soumissions de formulaires HSE,
la normalisation relationnelle, le recalcul des KPIs et les endpoints du Dashboard.
"""

import pytest
from app.models.submission import (
    FormSubmission,
    AuditHSESubmission,
    AuditHSEItem,
    TourneeHSESubmission,
    TourneeHSEItem,
    PermisTravailSubmission,
)
from app.models.dashboard import KPISnapshot, DashboardWidget, KPIDefinition


def get_auth_token(client, db_session=None):
    from app.models.user import User, UserStatus
    reg = {
        "email": "test_submissions@platformactia.com",
        "full_name": "Test Submissions Manager",
        "password": "SecurePassword123"
    }
    client.post("/api/v1/auth/register", json=reg)
    if db_session:
        user = db_session.query(User).filter(User.email == reg["email"]).first()
        if user:
            user.status = UserStatus.APPROVED.value
            db_session.commit()
    resp = client.post("/api/v1/auth/login", data={"username": reg["email"], "password": reg["password"]})
    return resp.json()["access_token"]


def test_create_and_read_audit_hse_relational(client, db_session):
    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # Payload identique à ce que AuditWizard.vue envoie
    payload = {
        "reference": "FGSI-001-Ind:F",
        "form_type": "audit_hse",
        "secteur": "Ligne CMS A",
        "intervenants": "Ghalya M., Jean D.",
        "date_audit": "2026-09-08",
        "commentaires_generaux": "Audit d'inspection trimestriel",
        "taux_conformite": 94.5,
        "total_conforme": 48,
        "total_non_conforme": 2,
        "total_na": 1,
        "count_soldee": 1,
        "count_non_engagee": 0,
        "count_en_cours": 0,
        "count_en_retard": 1,
        "items_data": {
            "1": {"val": 1},
            "2": {
                "val": 0,
                "constat": "EPI non portés",
                "action": "Fournir lunettes",
                "resp": "Chef Ligne",
                "delai": "2026-09-15",
                "etat": "En retard",
                "comm": "Rappel sécurité"
            },
            "3": {"val": "NA"}
        }
    }

    # 1. POST
    post_res = client.post("/api/v1/audits/", json=payload, headers=headers)
    assert post_res.status_code == 201, post_res.text
    audit_data = post_res.json()
    audit_id = audit_data["id"]

    assert audit_data["reference"] == "FGSI-001-Ind:F"
    assert audit_data["form_type"] == "audit_hse"
    assert audit_data["secteur"] == "Ligne CMS A"
    assert audit_data["taux_conformite"] == 94.5

    # 2. Vérification directe dans la base relationnelle
    sub = db_session.query(FormSubmission).filter(FormSubmission.id == audit_id).first()
    assert sub is not None
    assert isinstance(sub, AuditHSESubmission)
    assert sub.total_conforme == 48
    assert sub.count_en_retard == 1

    # Vérification des items dans audit_hse_items
    items = db_session.query(AuditHSEItem).filter(AuditHSEItem.audit_id == audit_id).all()
    assert len(items) == 3
    item2 = next((it for it in items if it.question_id == 2), None)
    assert item2 is not None
    assert item2.conformite == 0
    assert item2.etat == "en_retard"
    assert item2.action_corrective == "Fournir lunettes"

    # 3. GET /audits/{id} pour tester la reconstitution du dictionnaire items_data
    get_res = client.get(f"/api/v1/audits/{audit_id}", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert "items_data" in get_data
    assert "2" in get_data["items_data"]
    assert get_data["items_data"]["2"]["val"] == 0
    assert get_data["items_data"]["2"]["etat"] == "En retard"
    assert get_data["items_data"]["2"]["action"] == "Fournir lunettes"


def test_tournee_and_permis_submissions(client, db_session):
    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Tournée HSE
    tournee_payload = {
        "reference": "FGSI-010-Ind:A",
        "form_type": "tournee_hse",
        "secteur": "Magasin PDR",
        "intervenants": "Marc S.",
        "date_audit": "2026-09-08",
        "commentaires_generaux": "Tournée sécurité",
        "taux_conformite": 100.0,
        "total_conforme": 42,
        "total_non_conforme": 0,
        "total_na": 0,
        "count_soldee": 0,
        "count_non_engagee": 0,
        "count_en_cours": 0,
        "count_en_retard": 0,
        "items_data": {
            "101": {"val": 1},
            "102": {"val": 1}
        }
    }
    t_res = client.post("/api/v1/audits/", json=tournee_payload, headers=headers)
    assert t_res.status_code == 201
    t_id = t_res.json()["id"]

    t_sub = db_session.query(TourneeHSESubmission).filter(TourneeHSESubmission.id == t_id).first()
    assert t_sub is not None
    assert t_sub.total_conforme == 42

    # 2. Permis de Travail
    permis_payload = {
        "reference": "FGSI-PERMIS",
        "form_type": "permis_travail",
        "secteur": "Toiture Bâtiment A",
        "intervenants": "Société Extérieure ABC",
        "date_audit": "2026-09-08",
        "commentaires_generaux": "Travaux de réfection toiture",
        "taux_conformite": 100.0,
        "total_conforme": 0,
        "total_non_conforme": 0,
        "total_na": 0,
        "count_soldee": 0,
        "count_non_engagee": 0,
        "count_en_cours": 0,
        "count_en_retard": 0,
        "items_data": {
            "plan_prevention": 2,
            "permis_hauteur": 1,
            "permis_feu": 1,
            "remarques": "Échafaudage vérifié conforme"
        }
    }
    p_res = client.post("/api/v1/audits/", json=permis_payload, headers=headers)
    assert p_res.status_code == 201
    p_id = p_res.json()["id"]

    p_sub = db_session.query(PermisTravailSubmission).filter(PermisTravailSubmission.id == p_id).first()
    assert p_sub is not None
    assert p_sub.nb_plan_prevention == 2
    assert p_sub.nb_permis_feu == 1


def test_stats_and_dashboard_endpoints(client, db_session):
    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Stats endpoint
    stats_res = client.get("/api/v1/audits/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_audits" in stats
    assert "avg_conformite" in stats

    # 2. Dashboard definitions
    defs_res = client.get("/api/v1/dashboard/definitions", headers=headers)
    assert defs_res.status_code == 200
    defs = defs_res.json()
    assert len(defs) >= 5

    # 3. Dashboard widgets
    widgets_res = client.get("/api/v1/dashboard/widgets", headers=headers)
    assert widgets_res.status_code == 200
    widgets = widgets_res.json()
    assert len(widgets) > 0


def test_update_and_delete_audit(client, db_session):
    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/v1/audits/",
        json={
            "reference": "FGSI-001-Ind:F",
            "form_type": "audit_hse",
            "secteur": "Zone Test",
            "intervenants": "Intervenant Test",
            "date_audit": "2026-09-08",
            "taux_conformite": 50.0,
            "items_data": {
                "1": {"val": 0, "etat": "En cours", "action": "Action 1"}
            }
        },
        headers=headers
    )
    audit_id = create_res.json()["id"]

    # Test PUT
    put_res = client.put(
        f"/api/v1/audits/{audit_id}",
        json={
            "taux_conformite": 100.0,
            "items_data": {
                "1": {"val": 1, "etat": "Soldée"}
            }
        },
        headers=headers
    )
    assert put_res.status_code == 200
    assert put_res.json()["taux_conformite"] == 100.0

    # Test DELETE
    del_res = client.delete(f"/api/v1/audits/{audit_id}", headers=headers)
    assert del_res.status_code == 200

    # Vérifier que l'audit n'existe plus
    get_res = client.get(f"/api/v1/audits/{audit_id}", headers=headers)
    assert get_res.status_code == 404


def test_statistiques_accidents_submission(client, db_session):
    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "reference": "FGSI-STAT-ACCIDENTS",
        "form_type": "statistiques_accidents",
        "secteur": "Production Générale",
        "intervenants": "Responsable HSE Actia",
        "date_audit": "2026-09-10",
        "commentaires_generaux": "Suivi mensuel des indicateurs SST",
        "taux_conformite": 100.0,
        "items_data": {
            "annee": 2026,
            "target_if": 2.5,
            "months": {
                "1": {
                    "nb_accidents_avec_arret": 2,
                    "nb_accidents_sans_arret": 3,
                    "nb_heures_travaillees": 78507,
                    "nb_jours_perdus": 20,
                    "nb_travailleurs": 510,
                    "nb_visites_medicales": 15,
                    "nb_maladies_pro": 1,
                    "incapacite_permanente": 20.0
                },
                "2": {
                    "nb_accidents_avec_arret": 1,
                    "nb_accidents_sans_arret": 1,
                    "nb_heures_travaillees": 68822,
                    "nb_jours_perdus": 18,
                    "nb_travailleurs": 504,
                    "nb_visites_medicales": 10,
                    "nb_maladies_pro": 0,
                    "incapacite_permanente": 18.0
                }
            }
        }
    }

    # 1. POST
    post_res = client.post("/api/v1/audits/", json=payload, headers=headers)
    assert post_res.status_code == 201, post_res.text
    res_data = post_res.json()
    sub_id = res_data["id"]

    # 2. Vérification règle utilisateur : Ligne 1 = Ligne 2 + Ligne 3 (2 + 3 = 5)
    assert "items_data" in res_data
    months = res_data["items_data"]["months"]
    assert months["1"]["nb_accidents_total"] == 5
    assert months["1"]["nb_accidents_avec_arret"] == 2
    assert months["1"]["nb_accidents_sans_arret"] == 3
    assert months["1"]["nb_heures_travaillees"] == 78507
    assert months["1"]["nb_jours_perdus"] == 20
    assert months["1"]["nb_travailleurs"] == 510

    # Vérification indicateurs TF, IF, TG, IG
    # TF = (2 / 78507) * 1 000 000 ≈ 25.48
    # IF = (2 / 510) * 1000 ≈ 3.92
    assert months["1"]["tf_valeur"] > 25.0
    assert months["1"]["if_valeur"] > 3.9

    # Mois 2 : (1 + 1 = 2)
    assert months["2"]["nb_accidents_total"] == 2

    # Vérification totaux consolidés
    totals = res_data["items_data"]["totals"]
    assert totals["total_accidents_avec_arret"] == 3
    assert totals["total_accidents_sans_arret"] == 4
    assert totals["total_accidents"] == 7

    # 3. GET /audits/{id}
    get_res = client.get(f"/api/v1/audits/{sub_id}", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["form_type"] == "statistiques_accidents"
    assert get_data["items_data"]["months"]["1"]["nb_accidents_total"] == 5


def test_custom_fields_relational(client, db_session):
    """
    Vérifie la persistance relationnelle des champs personnalisés :
    - Enregistrement dans custom_field_definitions et custom_field_values
    - Endpoints /api/v1/custom-fields/definitions et /values/{id}
    - Reconstitution transparente dans /api/v1/audits/{id}
    """
    from app.models.submission import CustomFieldDefinition, CustomFieldValue

    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Création d'un permis avec des champs personnalisés
    payload = {
        "reference": "FGSI-PERMIS-TEST-CF",
        "form_type": "permis_travail",
        "secteur": "Atelier Maintenance",
        "intervenants": "Technicien A",
        "date_audit": "2026-09-23",
        "taux_conformite": 100.0,
        "items_data": {
            "plan_prevention": 3,
            "permis_hauteur": 1,
            "permis_feu": 2,
            "dynamic_fields": [
                {
                    "fieldId": "custom_extincteurs",
                    "label": "Extincteurs contrôlés",
                    "type": "numeric",
                    "value": 15,
                    "unit": "Appareils",
                    "isCustom": True
                },
                {
                    "fieldId": "custom_prestataire",
                    "label": "Société Intervenante",
                    "type": "text",
                    "value": "Securitas Industrie",
                    "unit": "",
                    "isCustom": True
                }
            ]
        }
    }

    res = client.post("/api/v1/audits/", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    sub_id = res.json()["id"]

    # 2. Vérification directe en BDD dans les tables normalisées
    cf_defs = db_session.query(CustomFieldDefinition).all()
    assert len(cf_defs) >= 2
    def_names = [d.name for d in cf_defs]
    assert "Extincteurs contrôlés" in def_names
    assert "Société Intervenante" in def_names

    cf_vals = db_session.query(CustomFieldValue).filter(CustomFieldValue.submission_id == sub_id).all()
    assert len(cf_vals) == 2
    num_val = next(v for v in cf_vals if v.field_def.name == "Extincteurs contrôlés")
    assert num_val.numeric_value == 15.0

    txt_val = next(v for v in cf_vals if v.field_def.name == "Société Intervenante")
    assert txt_val.text_value == "Securitas Industrie"

    # 3. Vérification des endpoints de l'API custom-fields
    def_res = client.get("/api/v1/custom-fields/definitions?form_type=permis_travail", headers=headers)
    assert def_res.status_code == 200
    def_list = def_res.json()
    assert any(d["name"] == "Extincteurs contrôlés" for d in def_list)

    val_res = client.get(f"/api/v1/custom-fields/values/{sub_id}", headers=headers)
    assert val_res.status_code == 200
    val_list = val_res.json()
    assert len(val_list) == 2

    # 4. Vérification de la lecture via /api/v1/audits/{id}
    audit_res = client.get(f"/api/v1/audits/{sub_id}", headers=headers)
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert "dynamic_fields" in audit_data["items_data"]
    dfs = audit_data["items_data"]["dynamic_fields"]
    assert len(dfs) == 2
    assert any(f["label"] == "Extincteurs contrôlés" and f["value"] == 15.0 for f in dfs)
    assert any(f["label"] == "Société Intervenante" and f["value"] == "Securitas Industrie" for f in dfs)


def test_centralized_multiuser_visibility(client, db_session):
    """
    Vérifie que les données sont centralisées :
    - Alice soumet une fiche
    - Bob soumet une fiche
    - Bob voit la fiche d'Alice dans l'historique avec le nom d'Alice
    - Alice voit la fiche de Bob dans l'historique avec le nom de Bob
    - Les stats sont identiques et consolidées pour toute l'usine
    """
    from app.models.user import User, UserStatus

    # 1. Enregistrement et approbation d'Alice
    client.post("/api/v1/auth/register", json={
        "email": "alice_central@actia.com",
        "full_name": "Alice Martin",
        "password": "Password123"
    })
    user_a = db_session.query(User).filter(User.email == "alice_central@actia.com").first()
    user_a.status = UserStatus.APPROVED.value
    db_session.commit()
    token_a = client.post("/api/v1/auth/login", data={"username": "alice_central@actia.com", "password": "Password123"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Enregistrement et approbation de Bob
    client.post("/api/v1/auth/register", json={
        "email": "bob_central@actia.com",
        "full_name": "Bob Dupont",
        "password": "Password123"
    })
    user_b = db_session.query(User).filter(User.email == "bob_central@actia.com").first()
    user_b.status = UserStatus.APPROVED.value
    db_session.commit()
    token_b = client.post("/api/v1/auth/login", data={"username": "bob_central@actia.com", "password": "Password123"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Alice soumet un audit
    res_a = client.post("/api/v1/audits/", json={
        "reference": "FGSI-001-ALICE",
        "form_type": "audit_hse",
        "secteur": "Secteur Alpha",
        "intervenants": "Alice M.",
        "date_audit": "2026-09-25",
        "taux_conformite": 80.0,
        "items_data": {"1": {"val": 1}}
    }, headers=headers_a)
    assert res_a.status_code == 201
    audit_a_id = res_a.json()["id"]

    # 4. Bob soumet une tournée
    res_b = client.post("/api/v1/audits/", json={
        "reference": "FGSI-010-BOB",
        "form_type": "tournee_hse",
        "secteur": "Secteur Beta",
        "intervenants": "Bob D.",
        "date_audit": "2026-09-25",
        "taux_conformite": 100.0,
        "items_data": {"101": {"val": 1}}
    }, headers=headers_b)
    assert res_b.status_code == 201
    tournee_b_id = res_b.json()["id"]

    # 5. Bob consulte l'historique : il doit voir TOUTES les fiches de l'usine (la sienne + celle d'Alice)
    list_bob = client.get("/api/v1/audits/", headers=headers_b).json()
    bob_seen_ids = [sub["id"] for sub in list_bob]
    assert audit_a_id in bob_seen_ids, "Bob ne voit pas la fiche d'Alice dans l'historique centralisé !"
    assert tournee_b_id in bob_seen_ids, "Bob ne voit pas sa propre fiche !"

    # Vérification que le nom de l'auteur est correctement restitué
    alice_item_in_bob_list = next(sub for sub in list_bob if sub["id"] == audit_a_id)
    assert alice_item_in_bob_list["author_name"] == "Alice Martin"

    bob_item_in_bob_list = next(sub for sub in list_bob if sub["id"] == tournee_b_id)
    assert bob_item_in_bob_list["author_name"] == "Bob Dupont"

    # 6. Alice et Bob consultent les statistiques : elles doivent être identiques et centralisées
    stats_a = client.get("/api/v1/audits/stats", headers=headers_a).json()
    stats_b = client.get("/api/v1/audits/stats", headers=headers_b).json()
    assert stats_a["total_audits"] == stats_b["total_audits"]
    assert stats_a["total_audits"] >= 2
    assert stats_a["avg_conformite"] == stats_b["avg_conformite"]



