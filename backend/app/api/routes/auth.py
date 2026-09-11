from datetime import UTC, datetime

from backend.app.api.deps import SESSION_COOKIE, CurrentUser, DbSession
from backend.app.core.config import settings
from backend.app.core.rate_limit import RateLimitUnavailableError, rate_limiter
from backend.app.core.security import hash_password, verify_password
from backend.app.models.auth import AuthChallengePurpose
from backend.app.models.user import User
from backend.app.schemas.user import (
    GenericAuthResponse,
    LoginRequest,
    MfaChallengeRequest,
    MfaChallengeResponse,
    MfaEnrollmentResponse,
    MfaVerifyRequest,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    VerifyEmailRequest,
)
from backend.app.services.auth_service import AuthError, AuthService
from fastapi import APIRouter, HTTPException, Request, Response, status

router = APIRouter(prefix="/auth", tags=["auth"])
GENERIC_EMAIL_MESSAGE = "If an eligible account exists, an email has been sent."


def client_ip(request: Request) -> str:
    # The application must only trust proxy forwarding headers when the proxy
    # itself has been explicitly configured as trusted. Until then, use the
    # direct peer address to prevent client-controlled spoofing.
    return request.client.host if request.client else "unknown"


async def enforce_auth_rate_limit(
    scope: str, identifier: str, limit: int, window_seconds: int
) -> None:
    try:
        await rate_limiter.check(scope, identifier, limit, window_seconds)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except RateLimitUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


def set_session_cookie(response: Response, raw_session: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=raw_session,
        max_age=settings.session_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
    )


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "company": user.company,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "two_factor_enabled": user.two_factor_enabled,
        "onboarding_state": user.onboarding_state,
        "created_at": user.created_at,
    }


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_202_ACCEPTED)
async def register(data: UserCreate, request: Request, db: DbSession):
    await enforce_auth_rate_limit("register-ip", client_ip(request), 5, 60 * 60)
    await enforce_auth_rate_limit("register-email", data.email, 3, 60 * 60)
    service = AuthService(db)
    try:
        await service.register(
            data.email, data.password, data.full_name, data.company, data.phone, client_ip(request)
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RegisterResponse(
        message="Check your email to verify your address and continue setup.", email=data.email
    )


@router.post("/verify-email", response_model=MfaChallengeResponse)
async def verify_email(data: VerifyEmailRequest, request: Request, db: DbSession):
    await enforce_auth_rate_limit("verify-email-ip", client_ip(request), 10, 60 * 60)
    service = AuthService(db)
    try:
        user = await service.consume_verification(data.token, client_ip(request))
        challenge = await service.create_login_challenge_for_verified_user(user, client_ip(request))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return MfaChallengeResponse(
        challenge_id=challenge.id,
        next_step="mfa_enrollment",
        expires_in_seconds=settings.auth_challenge_expire_minutes * 60,
    )


@router.post(
    "/resend-verification", response_model=GenericAuthResponse, status_code=status.HTTP_202_ACCEPTED
)
async def resend_verification(data: PasswordResetRequest, request: Request, db: DbSession):
    await enforce_auth_rate_limit("resend-verification-ip", client_ip(request), 5, 60 * 60)
    await enforce_auth_rate_limit("resend-verification-email", data.email, 3, 60 * 60)
    await AuthService(db).resend_verification(data.email, client_ip(request))
    return GenericAuthResponse(message=GENERIC_EMAIL_MESSAGE)


@router.post("/login", response_model=MfaChallengeResponse)
async def login(data: LoginRequest, request: Request, db: DbSession):
    await enforce_auth_rate_limit("login-ip", client_ip(request), 20, 15 * 60)
    await enforce_auth_rate_limit("login-email", data.email, 8, 15 * 60)
    try:
        challenge = await AuthService(db).create_login_challenge(
            data.email, data.password, client_ip(request)
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return MfaChallengeResponse(
        challenge_id=challenge.id,
        next_step=(
            "mfa" if challenge.purpose == AuthChallengePurpose.MFA_LOGIN else "mfa_enrollment"
        ),
        expires_in_seconds=settings.auth_challenge_expire_minutes * 60,
    )


@router.post("/mfa/enrollment", response_model=MfaEnrollmentResponse)
async def begin_mfa_enrollment(data: MfaChallengeRequest, request: Request, db: DbSession):
    await enforce_auth_rate_limit("mfa-enrollment-ip", client_ip(request), 10, 15 * 60)
    service = AuthService(db)
    try:
        challenge, secret, uri = await service.begin_mfa_enrollment(
            data.challenge_id, client_ip(request)
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return MfaEnrollmentResponse(
        challenge_id=challenge.id,
        next_step="mfa_enrollment",
        expires_in_seconds=max(0, int((challenge.expires_at - datetime.now(UTC)).total_seconds())),
        qr_data_uri=service.qr_data_uri(uri),
        secret=secret,
    )


@router.post("/mfa/verify")
async def verify_mfa(data: MfaVerifyRequest, response: Response, request: Request, db: DbSession):
    await enforce_auth_rate_limit("mfa-verify-ip", client_ip(request), 25, 15 * 60)
    service = AuthService(db)
    try:
        user, backup_codes = await service.verify_mfa(
            data.challenge_id, data.code, client_ip(request)
        )
        session = await service.create_session(
            user, client_ip(request), request.headers.get("user-agent")
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    set_session_cookie(response, session)
    return {"user": serialize_user(user), "backup_codes": backup_codes}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, db: DbSession):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await AuthService(db).revoke_session(token)
    response.delete_cookie(SESSION_COOKIE, domain=settings.cookie_domain, path="/")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return serialize_user(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, current_user: CurrentUser, db: DbSession):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.flush()
    return serialize_user(current_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChange, current_user: CurrentUser, request: Request, db: DbSession
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    current_user.hashed_password = hash_password(data.new_password)
    await AuthService(db).revoke_user_sessions(current_user.id)


@router.post(
    "/forgot-password", response_model=GenericAuthResponse, status_code=status.HTTP_202_ACCEPTED
)
async def forgot_password(data: PasswordResetRequest, request: Request, db: DbSession):
    await enforce_auth_rate_limit("forgot-password-ip", client_ip(request), 5, 60 * 60)
    await enforce_auth_rate_limit("forgot-password-email", data.email, 3, 60 * 60)
    await AuthService(db).request_password_reset(data.email, client_ip(request))
    return GenericAuthResponse(message=GENERIC_EMAIL_MESSAGE)


@router.post("/reset-password", response_model=GenericAuthResponse)
async def reset_password(data: PasswordResetConfirm, request: Request, db: DbSession):
    await enforce_auth_rate_limit("reset-password-ip", client_ip(request), 10, 60 * 60)
    try:
        await AuthService(db).reset_password(data.token, data.new_password, client_ip(request))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return GenericAuthResponse(message="Your password has been reset. You can now sign in.")
