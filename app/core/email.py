import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_otp_email(email_to: str, otp_code: str) -> bool:
    """
    Sends a 6-digit OTP verification code via Gmail SMTP if credentials are configured in .env.
    If SMTP credentials are not set, prints the simulated email in the server console.
    """
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD
    from_email = settings.EMAILS_FROM_EMAIL or smtp_user or "noreply@platformactia.com"

    # Console simulation log
    print(f"\n[EMAIL SIMULATION] Verification OTP code sent to {email_to}: {otp_code}\n")

    # If Gmail SMTP credentials are set in .env, send real email!
    if smtp_user and smtp_password:
        try:
            subject = "PlatformActia - Code de vérification à 6 chiffres"
            
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

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
            msg["To"] = email_to

            part = MIMEText(html_content, "html")
            msg.attach(part)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [email_to], msg.as_string())

            logger.info(f"Real Gmail SMTP Email sent to {email_to}")
            print(f"[REAL SMTP GMAIL] Email successfully sent to {email_to} via Gmail SMTP!")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMTP email: {e}")
            print(f"[SMTP ERROR] Could not send email via Gmail SMTP: {e}")
            return False
    else:
        logger.info("SMTP credentials not configured in .env - email printed in console simulation.")
        return True
