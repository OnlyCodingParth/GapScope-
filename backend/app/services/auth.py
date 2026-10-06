import secrets
import hashlib
import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import get_settings
from app.core.database import connect

COOKIE_NAME = "gapscope_session"
logger = logging.getLogger(__name__)


def session_key(session_id: str) -> str:
    secret = get_settings().session_secret or "gapscope-local-development-session-secret"
    return hashlib.sha256(f"{secret}:{session_id}".encode()).hexdigest()


def verify_google_credential(credential: str) -> dict[str, object]:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured.")
    try:
        claims = id_token.verify_oauth2_token(credential, requests.Request(), settings.google_client_id)
    except Exception as error:
        logger.warning("Google ID credential verification failed: %s", error)
        raise HTTPException(status_code=401, detail="Google sign-in could not be verified.") from error
    if claims.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        logger.warning("Google ID credential verification failed: unexpected issuer")
        raise HTTPException(status_code=401, detail="Google sign-in could not be verified.")
    if not claims.get("sub") or not claims.get("email"):
        raise HTTPException(status_code=401, detail="Google sign-in could not be verified.")
    return claims


def safe_user(row: object) -> dict[str, str | None]:
    return {"id": row["id"], "email": row["email"], "name": row["name"], "picture": row["picture"]}


def create_session_from_claims(claims: dict[str, object]) -> tuple[str, dict[str, str | None]]:
    now = datetime.now(UTC).isoformat()
    user_id = str(uuid4())
    with connect() as connection:
        existing = connection.execute("SELECT * FROM users WHERE google_sub = ?", (claims["sub"],)).fetchone()
        if existing is None:
            connection.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, claims["sub"], claims["email"], claims.get("name") or claims["email"], claims.get("picture"), now, now))
            user = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        else:
            connection.execute("UPDATE users SET email = ?, name = ?, picture = ?, updated_at = ? WHERE id = ?", (claims["email"], claims.get("name") or claims["email"], claims.get("picture"), now, existing["id"]))
            user = connection.execute("SELECT * FROM users WHERE id = ?", (existing["id"],)).fetchone()
        session_id = secrets.token_urlsafe(32)
        expires_at = (datetime.now(UTC) + timedelta(seconds=get_settings().session_ttl_seconds)).isoformat()
        connection.execute("INSERT INTO sessions VALUES (?, ?, ?)", (session_key(session_id), user["id"], expires_at))
        return session_id, safe_user(user)


def get_session_user(session_id: str | None) -> dict[str, str | None]:
    if not session_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    with connect() as connection:
        stored_id = session_key(session_id)
        row = connection.execute("SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.id = ? AND s.expires_at > ?", (stored_id, datetime.now(UTC).isoformat())).fetchone()
        if row is None:
            connection.execute("DELETE FROM sessions WHERE id = ?", (stored_id,))
            raise HTTPException(status_code=401, detail="Authentication required.")
        return safe_user(row)


def delete_session(session_id: str | None) -> None:
    if session_id:
        with connect() as connection:
            connection.execute("DELETE FROM sessions WHERE id = ?", (session_key(session_id),))


def require_user_id(session_id: str | None) -> str:
    return str(get_session_user(session_id)["id"])
