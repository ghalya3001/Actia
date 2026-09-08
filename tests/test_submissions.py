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


def get_auth_token(client):
    reg = {
        "email": "test_submissions@platformactia.com",
        "full_name": "Test Submissions Manager",
        "password": "SecurePassword123"
    }
    client.post("/api/v1/auth/register", json=reg)
    resp = client.post("/api/v1/auth/login", data={"username": reg["email"], "password": reg["password"]})
    return resp.json()["access_token"]


def test_create_and_read_audit_hse_relational(client, db_session):
    token = get_auth_token(client)
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
    token = get_auth_token(client)
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
    token = get_auth_token(client)
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
    token = get_auth_token(client)
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
