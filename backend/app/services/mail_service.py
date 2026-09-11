import logging
from dataclasses import dataclass
from html import escape

import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    text: str


class MailService:
    """Resend transport with a deliberately non-delivering development fallback."""

    async def send(self, message: EmailMessage) -> None:
        if not settings.resend_api_key:
            if settings.is_production:
                raise RuntimeError("Transactional mail is not configured")
            logger.info(
                "Email suppressed in development: subject=%s recipient=%s",
                message.subject,
                message.to,
            )
            return

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": settings.mail_from,
                    "to": [message.to],
                    "subject": message.subject,
                    "html": message.html,
                    "text": message.text,
                },
            )
            response.raise_for_status()

    async def send_verification(self, email: str, name: str, token: str) -> None:
        # A fragment is never sent in HTTP requests, server access logs, or
        # Referer headers. The client reads it and POSTs it once to the API.
        url = f"{settings.app_url.rstrip('/')}/verify-email#token={token}"
        safe_name = escape(name)
        expires = settings.auth_token_expire_minutes
        text = (
            f"Hi {name},\n\nVerify your email address to activate your "
            f"OpenDomain account: {url}\n\nThis link expires in {expires} minutes."
        )
        html = f"""
<div style="background:#0c0c0e;color:#e4e4e7;font-family:Inter,Arial,sans-serif;padding:40px">
  <div style="max-width:560px;margin:auto;background:#141416;border:1px solid #2a2a2e;border-radius:12px;padding:32px">
    <p style="color:#6d8aff;font-family:monospace;margin:0 0 24px">&lt;.&gt; opendomain</p>
    <h1 style="font-size:24px;margin:0 0 12px">Verify your email address</h1>
    <p style="color:#a1a1aa;line-height:1.6">Hi {safe_name}, confirm your email to continue securing your account with an authenticator app.</p>
    <a href="{escape(url, quote=True)}" style="display:inline-block;background:#6d8aff;color:#0c0c0e;padding:12px 18px;border-radius:8px;font-weight:600;text-decoration:none">Verify email address</a>
    <p style="color:#a1a1aa;font-size:13px;line-height:1.6;margin-top:24px">This link expires in {expires} minutes. If you did not create an OpenDomain account, you can safely ignore this email.</p>
  </div>
</div>
"""
        await self.send(
            EmailMessage(
                to=email,
                subject="Verify your OpenDomain email address",
                text=text,
                html=html,
            )
        )

    async def send_password_reset(self, email: str, name: str, token: str) -> None:
        url = f"{settings.app_url.rstrip('/')}/reset-password#token={token}"
        safe_name = escape(name)
        expires = settings.auth_token_expire_minutes
        text = (
            f"Hi {name},\n\nReset your OpenDomain password: {url}\n\n"
            f"This link expires in {expires} minutes."
        )
        html = (
            f"<p>Hi {safe_name},</p>"
            f'<p><a href="{escape(url, quote=True)}">Reset your OpenDomain password</a></p>'
            f"<p>This link expires in {expires} minutes.</p>"
        )
        await self.send(
            EmailMessage(
                to=email,
                subject="Reset your OpenDomain password",
                text=text,
                html=html,
            )
        )
