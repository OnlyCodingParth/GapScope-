from fastapi import APIRouter, Cookie, Response

from app.core.config import get_settings
from app.schemas.auth import GoogleCredential
from app.services.auth import COOKIE_NAME, create_session_from_claims, delete_session, get_session_user, verify_google_credential

router = APIRouter(prefix="/auth")


@router.post("/google")
def google_sign_in(payload: GoogleCredential, response: Response) -> dict[str, object]:
    session_id, user = create_session_from_claims(verify_google_credential(payload.credential))
    settings = get_settings()
    response.set_cookie(COOKIE_NAME, session_id, httponly=True, secure=settings.cookie_secure, samesite="lax", max_age=settings.session_ttl_seconds, path="/")
    return {"user": user}


@router.get("/me")
def current_user(gapscope_session: str | None = Cookie(default=None)) -> dict[str, object]:
    return {"user": get_session_user(gapscope_session)}


@router.post("/logout", status_code=204)
def logout(response: Response, gapscope_session: str | None = Cookie(default=None)) -> Response:
    delete_session(gapscope_session)
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = 204
    return response
