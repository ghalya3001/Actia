"""
===============================================================================
MODULE DE SÉCURITÉ ET CRYPTOGRAPHIE (SECURITY.PY)
===============================================================================
Rôle :
  Fournit les fonctions utilitaires pour la protection des données sensibles :
  - Hachage et vérification des mots de passe avec l'algorithme robuste bcrypt.
  - Création et signature des jetons d'accès JWT (Access Tokens avec identifiant JTI).
  - Génération de jetons de rafraîchissement (Refresh Tokens opaques).
  - Génération de codes temporaires à usage unique (OTP à 6 chiffres).

Équipe de maintenance :
  - Bcrypt applique un "sel" (salt) aléatoire automatique pour chaque hachage,
    ce qui empêche toute attaque par table arc-en-ciel (rainbow tables).
  - La limite des 72 octets est inhérente à l'algorithme bcrypt standard.
===============================================================================
"""

import uuid
import jwt
import bcrypt
import random
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, Tuple
from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hache un mot de passe en clair à l'aide de bcrypt avec un sel sécurisé.

    Args:
        password (str): Le mot de passe saisi par l'utilisateur en clair.

    Returns:
        str: L'empreinte sécurisée (hash bcrypt) encodée en chaîne de caractères UTF-8.
    """
    # Conversion de la chaîne str en tableau d'octets bytes
    pwd_bytes = password.encode('utf-8')

    # Bcrypt limite la taille du mot de passe à 72 octets : tronquage de précaution
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]

    # Génération d'un sel cryptographique unique aléatoire
    salt = bcrypt.gensalt()

    # Calcul de l'empreinte hachée avec le sel
    hashed = bcrypt.hashpw(pwd_bytes, salt)

    # Décodage en chaîne de caractères pour stockage facile dans PostgreSQL
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond à l'empreinte hachée en base.

    Args:
        plain_password (str): Le mot de passe en clair soumis lors de la connexion.
        hashed_password (str): L'empreinte hachée stockée dans la table 'users'.

    Returns:
        bool: True si les mots de passe correspondent parfaitement, False sinon.
    """
    # Conversion du mot de passe clair en octets
    pwd_bytes = plain_password.encode('utf-8')
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]

    # Conversion de l'empreinte en octets
    hash_bytes = hashed_password.encode('utf-8')

    # Comparaison sécurisée en temps constant contre les attaques temporelles (timing attacks)
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> Tuple[str, str, datetime]:
    """
    Génère un jeton d'accès JWT signé numériquement avec une charge utile standard.

    Args:
        subject (Union[str, Any]): L'identifiant du sujet (généralement l'adresse e-mail).
        expires_delta (Optional[timedelta]): Durée de validité personnalisée. Si None,
                                             utilise ACCESS_TOKEN_EXPIRE_MINUTES de la config.

    Returns:
        Tuple[str, str, datetime]:
            - encoded_jwt (str) : Le jeton JWT encodé sous forme 'header.payload.signature'
            - jti (str)         : Identifiant unique du jeton (UUID v4) pour traçabilité/révocation
            - expire (datetime) : Date et heure exacte d'expiration au format UTC
    """
    # JTI (JWT ID) : identifiant aléatoire unique permettant de blacklister/révoquer un jeton précis
    jti = str(uuid.uuid4())

    # Calcul de l'horodatage d'expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Données intégrées dans le payload du token JWT
    to_encode = {
        "exp": expire,                     # Date d'expiration (expiration timestamp)
        "sub": str(subject),               # Sujet du jeton (ex: email du manager)
        "jti": jti,                        # Identifiant unique de ce jeton spécifique
        "iat": datetime.now(timezone.utc)  # Date d'émission (issued at)
    }

    # Signature cryptographique avec la clé secrète et l'algorithme choisi (HS256)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti, expire


def generate_refresh_token() -> Tuple[str, datetime]:
    """
    Génère un jeton de rafraîchissement opaque (Refresh Token) à longue durée de vie.
    Ce token permet de renouveler l'Access Token sans ressaisir les identifiants.

    Returns:
        Tuple[str, datetime]:
            - raw_token (str)     : Jeton sous la forme 'ref_<uuid64hex>'
            - expires_at (datetime): Date limite de validité (ex: +7 jours)
    """
    # Chaîne aléatoire cryptographiquement forte de 64 caractères hexadécimaux
    raw_token = f"ref_{uuid.uuid4().hex}{uuid.uuid4().hex}"

    # Date d'expiration calculée selon REFRESH_TOKEN_EXPIRE_DAYS
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return raw_token, expires_at


def generate_otp_code() -> str:
    """
    Génère un code numérique à 6 chiffres aléatoire (One-Time Password) pour la vérification.
    Exemple de sortie : '482910'.

    Returns:
        str: Code OTP à 6 chiffres sous forme de chaîne de caractères.
    """
    return f"{random.randint(100000, 999999)}"


def generate_reset_token() -> str:
    """
    Génère un jeton UUID v4 générique pour les opérations de réinitialisation.

    Returns:
        str: Chaîne représentant un UUID v4 aléatoire.
    """
    return str(uuid.uuid4())
