from fastapi.testclient import TestClient

from app.api import auth
from app.main import app
from tests.test_attempts import complete_submission, sign_in


def test_google_auth_me_and_logout(monkeypatch) -> None:
    monkeypatch.setattr(auth, "verify_google_credential", lambda _: {"sub": "auth-user", "email": "learner@example.test", "name": "Learner", "picture": None})
    with TestClient(app) as client:
        assert client.get("/api/auth/me").status_code == 401
        login = client.post("/api/auth/google", json={"credential": "valid"})
        assert login.status_code == 200
        assert login.json()["user"]["email"] == "learner@example.test"
        assert client.get("/api/auth/me").status_code == 200
        assert client.post("/api/auth/logout").status_code == 204
        assert client.get("/api/auth/me").status_code == 401


def test_invalid_google_credential_is_rejected(monkeypatch) -> None:
    def reject(_: str):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Google sign-in could not be verified.")
    monkeypatch.setattr(auth, "verify_google_credential", reject)
    with TestClient(app) as client:
        assert client.post("/api/auth/google", json={"credential": "invalid"}).status_code == 401


def test_attempts_require_owner_and_hide_other_users() -> None:
    with TestClient(app) as client:
        assert client.post("/api/attempts", json={"responses": []}).status_code == 401
        sign_in(client, "student-one")
        created = client.post("/api/attempts", json={"responses": complete_submission(client)}).json()
        client.post("/api/auth/logout")
        sign_in(client, "student-two")
        assert client.get(f"/api/attempts/{created['id']}").status_code == 404
