from email.message import EmailMessage

import aiosmtplib

from src.conf.config import settings


async def send_verification_email(email_to: str, token: str):
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = email_to
    message["Subject"] = "Verify your email"
    verify_link = f"http://localhost:8000/api/auth/verify/{token}"
    message.set_content(f"Please click the link to verify your email: {verify_link}")

    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username,
        password=settings.mail_password,
        start_tls=True,
        validate_certs=False,
    )

async def send_reset_password_email(email_to: str, token: str):
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = email_to
    message["Subject"] = "Reset your password"
    reset_link = f"http://localhost:8000/api/auth/reset-password/{token}"
    message.set_content(f"Please click the link to reset your password: {reset_link}")

    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username,
        password=settings.mail_password,
        start_tls=True,
        validate_certs=False,
    )

async def send_reset_password_email(email_to: str, token: str):
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = email_to
    message["Subject"] = "Password Reset Request"
    reset_link = f"http://localhost:8000/api/auth/reset-password/{token}"
    message.set_content(f"""
    <html>
      <body>
        <p>To reset your password, please click the link below:</p>
        <p><a href="http://localhost:8000/api/auth/reset-password/{token}">Reset Password</a></p>
      </body>
    </html>
    """, subtype='html')
    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username,
        password=settings.mail_password,
        start_tls=True,
        validate_certs=False,
    )
