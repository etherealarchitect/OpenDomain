import base64
import hashlib
import hmac
import io
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import pyotp
import qrcode
from backend.app.core.config import settings
from backend.app.core.security import hash_password, verify_password
from backend.app.models.auth import (
    AuthAuditEvent,
    AuthChallenge,
    AuthChallengePurpose,
    AuthSession,
    AuthToken,
    AuthTokenPurpose,
    BackupCode,
)
from backend.app.models.user import User
from backend.app.services.mail_service import MailService
from cryptography.fernet import Fernet
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(self, db: AsyncSession, mailer: MailService | None = None):
        self.db = db
        self.mailer = mailer or MailService()
        self._fernet = Fernet(settings.effective_auth_encryption_key.encode())

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _digest(value: str) -> str:
        return hmac.new(
            settings.effective_token_pepper.encode(), value.encode(), hashlib.sha256
        ).hexdigest()

    def _encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def _decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode()).decode()

    async def _audit(
        self, event_type: str, user_id: uuid.UUID | None, ip_address: str | None
    ) -> None:
        self.db.add(AuthAuditEvent(user_id=user_id, event_type=event_type, ip_address=ip_address))

    async def _create_token(self, user: User, purpose: AuthTokenPurpose) -> str:
        await self.db.execute(
            update(AuthToken)
            .where(
                AuthToken.user_id == user.id,
                AuthToken.purpose == purpose,
                AuthToken.used_at.is_(None),
            )
            .values(used_at=self._now())
        )
        raw_token = secrets.token_urlsafe(48)
        self.db.add(
            AuthToken(
                user_id=user.id,
                purpose=purpose,
                token_hash=self._digest(raw_token),
                expires_at=self._now() + timedelta(minutes=settings.auth_token_expire_minutes),
            )
        )
        await self.db.flush()
        return raw_token

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        company: str | None,
        phone: str | None,
        ip_address: str | None,
    ) -> None:
        existing = await self.db.scalar(select(User).where(User.email == email).with_for_update())
        if existing:
            # Do not disclose account existence. For unverified accounts, issue a fresh link.
            if not existing.is_verified:
                token = await self._create_token(existing, AuthTokenPurpose.EMAIL_VERIFICATION)
                await self.mailer.send_verification(existing.email, existing.full_name, token)
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            company=company,
            phone=phone,
            is_active=True,
            is_verified=False,
        )
        try:
            async with self.db.begin_nested():
                self.db.add(user)
                await self.db.flush()
        except IntegrityError:
            # A concurrent request may have created the same normalized email.
            # Preserve the enumeration-safe response rather than surfacing a 500.
            existing = await self.db.scalar(select(User).where(User.email == email))
            if existing and not existing.is_verified:
                token = await self._create_token(existing, AuthTokenPurpose.EMAIL_VERIFICATION)
                await self.mailer.send_verification(existing.email, existing.full_name, token)
            return
        token = await self._create_token(user, AuthTokenPurpose.EMAIL_VERIFICATION)
        await self._audit("account_registered", user.id, ip_address)
        await self.mailer.send_verification(user.email, user.full_name, token)

    async def consume_verification(self, raw_token: str, ip_address: str | None) -> User:
        token = await self.db.scalar(
            select(AuthToken)
            .where(
                AuthToken.token_hash == self._digest(raw_token),
                AuthToken.purpose == AuthTokenPurpose.EMAIL_VERIFICATION,
                AuthToken.used_at.is_(None),
                AuthToken.expires_at > self._now(),
            )
            .with_for_update()
        )
        if not token:
            raise AuthError("This verification link is invalid or has expired")
        token.used_at = self._now()
        user = await self.db.get(User, token.user_id, with_for_update=True)
        if not user:
            raise AuthError("This verification link is invalid or has expired")
        user.is_verified = True
        await self._audit("email_verified", user.id, ip_address)
        return user

    async def resend_verification(self, email: str, ip_address: str | None) -> None:
        user = await self.db.scalar(select(User).where(User.email == email))
        if user and user.is_active and not user.is_verified:
            token = await self._create_token(user, AuthTokenPurpose.EMAIL_VERIFICATION)
            await self.mailer.send_verification(user.email, user.full_name, token)
            await self._audit("verification_resent", user.id, ip_address)

    async def create_login_challenge(
        self, email: str, password: str, ip_address: str | None
    ) -> AuthChallenge:
        user = await self.db.scalar(select(User).where(User.email == email))
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            await self._audit("login_failed", user.id if user else None, ip_address)
            raise AuthError("Invalid email or password")
        if not user.is_verified:
            raise AuthError("Verify your email address before signing in")
        return await self.create_login_challenge_for_verified_user(user, ip_address)

    async def create_login_challenge_for_verified_user(
        self, user: User, ip_address: str | None
    ) -> AuthChallenge:
        if not user.is_active or not user.is_verified:
            raise AuthError("Verify your email address before signing in")
        purpose = (
            AuthChallengePurpose.MFA_LOGIN
            if user.two_factor_enabled
            else AuthChallengePurpose.MFA_ENROLLMENT
        )
        challenge = AuthChallenge(
            user_id=user.id,
            purpose=purpose,
            expires_at=self._now() + timedelta(minutes=settings.auth_challenge_expire_minutes),
        )
        self.db.add(challenge)
        await self.db.flush()
        await self._audit("login_password_verified", user.id, ip_address)
        return challenge

    async def begin_mfa_enrollment(
        self, challenge_id: uuid.UUID, ip_address: str | None
    ) -> tuple[AuthChallenge, str, str]:
        challenge = await self._challenge(challenge_id, AuthChallengePurpose.MFA_ENROLLMENT)
        if not challenge.secret_encrypted:
            secret = pyotp.random_base32()
            challenge.secret_encrypted = self._encrypt(secret)
        else:
            secret = self._decrypt(challenge.secret_encrypted)
        user = await self.db.get(User, challenge.user_id)
        if not user:
            raise AuthError("Enrollment session expired")
        uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=settings.app_name)
        await self._audit("mfa_enrollment_started", user.id, ip_address)
        return challenge, secret, uri

    @staticmethod
    def qr_data_uri(provisioning_uri: str) -> str:
        image = qrcode.make(provisioning_uri)
        output = io.BytesIO()
        image.save(output, format="PNG")
        return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()

    async def verify_mfa(
        self, challenge_id: uuid.UUID, code: str, ip_address: str | None
    ) -> tuple[User, list[str] | None]:
        challenge = await self.db.scalar(
            select(AuthChallenge).where(AuthChallenge.id == challenge_id).with_for_update()
        )
        if (
            not challenge
            or challenge.completed_at
            or challenge.expires_at <= self._now()
            or challenge.attempts >= 5
        ):
            raise AuthError("This security challenge is invalid or has expired")
        challenge.attempts += 1
        user = await self.db.get(User, challenge.user_id, with_for_update=True)
        if not user:
            raise AuthError("This security challenge is invalid or has expired")

        if challenge.purpose == AuthChallengePurpose.MFA_ENROLLMENT:
            if not challenge.secret_encrypted:
                raise AuthError("Authenticator setup has not started")
            secret = self._decrypt(challenge.secret_encrypted)
            if not pyotp.TOTP(secret).verify(code, valid_window=1):
                await self._audit("mfa_enrollment_failed", user.id, ip_address)
                raise AuthError("That authenticator code is not valid")
            user.two_factor_secret = self._encrypt(secret)
            user.two_factor_enabled = True
            user.last_totp_counter = self._matched_totp_counter(pyotp.TOTP(secret), code)
            codes = await self._replace_backup_codes(user.id)
            challenge.completed_at = self._now()
            await self._audit("mfa_enabled", user.id, ip_address)
            return user, codes

        if challenge.purpose != AuthChallengePurpose.MFA_LOGIN or not user.two_factor_secret:
            raise AuthError("This security challenge is invalid or has expired")
        verified = await self._verify_totp_or_backup(user, code)
        if not verified:
            await self._audit("mfa_login_failed", user.id, ip_address)
            raise AuthError("That authentication code is not valid")
        challenge.completed_at = self._now()
        await self._audit("login_completed", user.id, ip_address)
        return user, None

    async def _challenge(
        self, challenge_id: uuid.UUID, purpose: AuthChallengePurpose
    ) -> AuthChallenge:
        challenge = await self.db.scalar(
            select(AuthChallenge).where(
                AuthChallenge.id == challenge_id,
                AuthChallenge.purpose == purpose,
                AuthChallenge.completed_at.is_(None),
                AuthChallenge.expires_at > self._now(),
            )
        )
        if not challenge:
            raise AuthError("This security challenge is invalid or has expired")
        return challenge

    def _matched_totp_counter(self, totp: pyotp.TOTP, code: str) -> int | None:
        normalized = code.replace(" ", "")
        current_counter = int(self._now().timestamp() // totp.interval)
        return next(
            (
                counter
                for counter in range(current_counter - 1, current_counter + 2)
                if hmac.compare_digest(totp.at(counter * totp.interval), normalized)
            ),
            None,
        )

    async def _verify_totp_or_backup(self, user: User, code: str) -> bool:
        normalized = code.replace(" ", "").upper()
        totp = pyotp.TOTP(self._decrypt(user.two_factor_secret))
        if (
            len(normalized) == 6
            and normalized.isdigit()
            and totp.verify(normalized, valid_window=1)
        ):
            matched_counter = self._matched_totp_counter(totp, normalized)
            if matched_counter is None or user.last_totp_counter == matched_counter:
                return False
            user.last_totp_counter = matched_counter
            return True
        digest = self._digest(normalized)
        backup = await self.db.scalar(
            select(BackupCode)
            .where(
                BackupCode.user_id == user.id,
                BackupCode.code_hash == digest,
                BackupCode.used_at.is_(None),
            )
            .with_for_update()
        )
        if not backup:
            return False
        backup.used_at = self._now()
        return True

    async def _replace_backup_codes(self, user_id: uuid.UUID) -> list[str]:
        await self.db.execute(delete(BackupCode).where(BackupCode.user_id == user_id))
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.db.add_all(
            [BackupCode(user_id=user_id, code_hash=self._digest(code)) for code in codes]
        )
        return codes

    async def create_session(
        self, user: User, ip_address: str | None, user_agent: str | None
    ) -> str:
        raw_token = secrets.token_urlsafe(48)
        self.db.add(
            AuthSession(
                user_id=user.id,
                token_hash=self._digest(raw_token),
                expires_at=self._now() + timedelta(days=settings.session_expire_days),
                ip_address=ip_address,
                user_agent=(user_agent or "")[:512] or None,
            )
        )
        await self.db.flush()
        return raw_token

    async def get_session_user(self, raw_token: str) -> User | None:
        session = await self.db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == self._digest(raw_token),
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > self._now(),
            )
        )
        if not session:
            return None
        user = await self.db.get(User, session.user_id)
        if not user or not user.is_active or not user.is_verified or not user.two_factor_enabled:
            return None
        session.last_seen_at = self._now()
        return user

    async def revoke_session(self, raw_token: str) -> None:
        await self.db.execute(
            update(AuthSession)
            .where(
                AuthSession.token_hash == self._digest(raw_token), AuthSession.revoked_at.is_(None)
            )
            .values(revoked_at=self._now())
        )

    async def revoke_user_sessions(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=self._now())
        )

    async def request_password_reset(self, email: str, ip_address: str | None) -> None:
        user = await self.db.scalar(select(User).where(User.email == email))
        if user and user.is_active:
            token = await self._create_token(user, AuthTokenPurpose.PASSWORD_RESET)
            await self.mailer.send_password_reset(user.email, user.full_name, token)
            await self._audit("password_reset_requested", user.id, ip_address)

    async def reset_password(
        self, raw_token: str, new_password: str, ip_address: str | None
    ) -> None:
        token = await self.db.scalar(
            select(AuthToken)
            .where(
                AuthToken.token_hash == self._digest(raw_token),
                AuthToken.purpose == AuthTokenPurpose.PASSWORD_RESET,
                AuthToken.used_at.is_(None),
                AuthToken.expires_at > self._now(),
            )
            .with_for_update()
        )
        if not token:
            raise AuthError("This password reset link is invalid or has expired")
        user = await self.db.get(User, token.user_id, with_for_update=True)
        if not user:
            raise AuthError("This password reset link is invalid or has expired")
        token.used_at = self._now()
        user.hashed_password = hash_password(new_password)
        await self.revoke_user_sessions(user.id)
        await self._audit("password_reset_completed", user.id, ip_address)
