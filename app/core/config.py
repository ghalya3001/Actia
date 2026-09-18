"""
===============================================================================
FICHIER DE CONFIGURATION GLOBALE DU BACKEND (CONFIG.PY)
===============================================================================
Rôle :
  Centralise l'ensemble des variables d'environnement et paramètres applicatifs
  du backend PlatformActia à l'aide de la bibliothèque Pydantic Settings.

Fonctionnement :
  - Lit automatiquement le fichier local `.env` s'il existe.
  - Définit des valeurs par défaut sécurisées pour le développement.
  - Valide les types des configurations (ports, chaînes de connexion, durées).

Équipe de maintenance :
  Pour modifier l'environnement (ex: passage en production), modifiez directement
  les clés correspondantes dans le fichier `.env` à la racine du projet.
===============================================================================
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Classe de configuration principale héritant de BaseSettings (Pydantic).
    Chaque attribut correspond à une variable d'environnement configurable.
    """

    # --- 1. Paramètres Généraux de l'Application ---
    # Nom public du projet utilisé dans la documentation OpenAPI / Swagger
    PROJECT_NAME: str = "PlatformActia Backend"

    # Préfixe global pour la version 1 de l'API REST (ex: /api/v1/audits)
    API_V1_STR: str = "/api/v1"

    # Environnement d'exécution ('development', 'staging', 'production')
    ENV: str = "development"

    # Mode débogage : active les logs détaillés et rechargements à chaud
    DEBUG: bool = True

    # Port d'écoute du serveur HTTP Uvicorn
    PORT: int = 8000

    # Adresse IP de liaison (0.0.0.0 permet d'écouter sur toutes les interfaces réseau)
    HOST: str = "0.0.0.0"

    # --- 2. Paramètres de Sécurité et Authentification (JWT) ---
    # Clé secrète cryptographique utilisée pour signer et vérifier les tokens JWT
    # ATTENTION MAINTENANCE : En production, cette clé DOIT être générée aléatoirement et gardée secrète !
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

    # Algorithme de chiffrement asymétrique ou symétrique (HS256 = HMAC avec SHA-256)
    ALGORITHM: str = "HS256"

    # Durée de validité du jeton d'accès (Access Token) en minutes (ici 60 min = 1 heure)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Durée de validité du jeton de rafraîchissement (Refresh Token) en jours (ici 7 jours)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Durée de validité du code OTP à 6 chiffres pour réinitialisation de mot de passe (15 minutes)
    RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # --- 3. Configuration de la Base de Données Relationnelle (PostgreSQL) ---
    # URL de connexion SQLAlchemy avec le pilote moderne psycopg v3 :
    # Format : postgresql+psycopg://utilisateur:motdepasse@serveur:port/nom_base
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/platformactia_db"

    # --- 4. Configuration du Serveur SMTP (Envoi d'e-mails réels via Gmail) ---
    # Serveur SMTP pour l'envoi des codes OTP de réinitialisation de mot de passe
    SMTP_HOST: str = "smtp.gmail.com"

    # Port standard SMTP avec chiffrement TLS STARTTLS
    SMTP_PORT: int = 587

    # Adresse email de l'expéditeur de la plateforme
    SMTP_USER: Optional[str] = "mimounaghalyya@gmail.com"

    # Mot de passe d'application Google (App Password) sécurisé
    SMTP_PASSWORD: Optional[str] = "akidgkgvcbfmykdl"

    # Adresse d'affichage "De / From" pour les e-mails reçus par l'utilisateur
    EMAILS_FROM_EMAIL: Optional[str] = "mimounaghalyya@gmail.com"

    # Nom d'affichage de l'expéditeur dans la boîte de messagerie
    EMAILS_FROM_NAME: str = "PlatformActia Responsable Portal"

    # Configuration Pydantic v2 pour charger les variables depuis le fichier .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore les variables d'environnement non déclarées sans lever d'erreur
    )


# Instanciation unique (Singleton) importée partout dans le projet via: `from app.core.config import settings`
settings = Settings()
