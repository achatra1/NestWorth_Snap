"""Resend integration for transactional email (password reset)."""
import logging

import resend

from backend.config import settings

logger = logging.getLogger(__name__)


async def send_password_reset_email(to_email: str, reset_url: str) -> None:
    """
    Send a password reset email via Resend.

    Raises:
        Exception: If the Resend API call fails.
    """
    resend.api_key = settings.RESEND_API_KEY

    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": [to_email],
        "subject": "Reset your NestWorth password",
        "html": f"""
            <p>We received a request to reset your NestWorth password.</p>
            <p><a href="{reset_url}">Click here to reset your password</a></p>
            <p>This link expires in 1 hour. If you didn't request this, you can ignore this email.</p>
        """,
    })
