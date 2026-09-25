"""
===============================================================================
SERVICE D'EXPÉDITION D'E-MAILS NOTIFICATIONS ET OTP (EMAIL.PY)
===============================================================================
Rôle :
  Gère l'envoi des courriels transactionnels de la plateforme, notamment :
  - L'envoi du code OTP à 6 chiffres pour la réinitialisation de mot de passe.
  - La mise en page HTML responsive avec charte graphique PlatformActia (vert/noir).
  - Un mode dégradé automatique (Simulation console) si les identifiants SMTP Gmail
    ne sont pas renseignés dans le fichier `.env`.

Équipe de maintenance :
  - Pour Gmail : utilisez un "Mot de passe d'application" (16 caractères) généré
    depuis le compte Google (rubrique Sécurité > Validation en deux étapes).
  - En environnement de test/CI, le mode simulation dans la console s'active sans erreur.
===============================================================================
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

# Initialisation du logger pour tracer les envois et erreurs d'e-mails
logger = logging.getLogger(__name__)


def send_otp_email(email_to: str, otp_code: str) -> bool:
    """
    Expédie un e-mail HTML contenant le code OTP de vérification à l'utilisateur destinataire.

    Args:
        email_to (str): Adresse de messagerie de l'utilisateur demandeur.
        otp_code (str): Code de vérification à 6 chiffres (ex: '729143').

    Returns:
        bool: True si l'e-mail a été envoyé avec succès ou simulé en console,
              False si une erreur de transmission SMTP survient.
    """
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD
    from_email = settings.EMAILS_FROM_EMAIL or smtp_user or "noreply@platformactia.com"

    # --- Mode 1 : Journalisation / Simulation en Console (Utile pour le dev local) ---
    print(f"\n[EMAIL SIMULATION] Verification OTP code sent to {email_to}: {otp_code}\n")

    # --- Mode 2 : Envoi Réel via le Serveur SMTP Gmail ---
    if smtp_user and smtp_password:
        try:
            subject = "PlatformActia - Code de vérification à 6 chiffres"
            
            # Gabarit HTML stylisé avec la charte graphique officielle PlatformActia
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #000c10; color: #f0fdf4; margin: 0; padding: 30px; }}
                .card {{ max-width: 500px; margin: 0 auto; background: #001e26; border: 1px solid #00c996; border-radius: 16px; padding: 30px; text-align: center; }}
                .logo {{ font-size: 24px; font-weight: 800; color: #00c996; margin-bottom: 20px; }}
                .code-box {{ display: inline-block; background: #003d4d; border: 1px solid #56ab2f; border-radius: 12px; padding: 15px 30px; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #a8e063; margin: 25px 0; }}
                .text {{ font-size: 14px; color: #94a3b8; line-height: 1.6; }}
                .footer {{ font-size: 12px; color: #64748b; margin-top: 25px; border-top: 1px solid rgba(0,201,150,0.2); padding-top: 15px; }}
              </style>
            </head>
            <body>
              <div class="card">
                <div class="logo">PlatformActia</div>
                <h2 style="color:#ffffff; margin-bottom:10px;">Réinitialisation de mot de passe</h2>
                <p class="text">Voici votre code de vérification à 6 chiffres pour réinitialiser votre mot de passe Manager :</p>
                
                <div class="code-box">{otp_code}</div>
                
                <p class="text">Ce code est valide pendant <strong>15 minutes</strong>. Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer ce message.</p>
                <div class="footer">PlatformActia Backend System</div>
              </div>
            </body>
            </html>
            """

            # Construction de l'objet MIME multipart pour la compatibilité des clients mail
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
            msg["To"] = email_to

            # Attachement de la partie HTML
            part = MIMEText(html_content, "html")
            msg.attach(part)

            # Connexion sécurisée au serveur SMTP avec chiffrement TLS et timeout de sécurité
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()  # Négociation du tunnel TLS chiffré
                server.login(smtp_user, smtp_password)  # Authentification auprès de Google
                server.sendmail(from_email, [email_to], msg.as_string())  # Expédition

            logger.info(f"Real Gmail SMTP Email sent to {email_to}")
            print(f"[REAL SMTP GMAIL] Email successfully sent to {email_to} via Gmail SMTP!")
            return True
        except Exception as e:
            # En cas d'erreur de connexion ou de mot de passe SMTP invalide
            logger.error(f"Failed to send SMTP email: {e}")
            print(f"[SMTP ERROR] Could not send email via Gmail SMTP: {e}")
            return False
    else:
        # Si aucun identifiant SMTP n'est renseigné dans .env
        logger.info("SMTP credentials not configured in .env - email printed in console simulation.")
        return True
