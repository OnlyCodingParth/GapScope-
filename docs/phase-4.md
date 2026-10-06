# Phase 4: Google authentication and student identity

GapScope now uses Google Identity Services for student login. The browser sends the Google ID credential only to `POST /api/auth/google`; the backend verifies its signature, issuer, audience, and expiry using `google-auth` before creating an opaque server-side session.

## Configuration

Set the same Google OAuth web client ID in `frontend/.env` as `VITE_GOOGLE_CLIENT_ID` and `backend/.env` as `GOOGLE_CLIENT_ID`. Set `SESSION_SECRET` to a high-entropy value for deployment. `COOKIE_SECURE=false` works for local HTTP; set it to `true` under HTTPS. `SESSION_TTL_SECONDS` defaults to 28800.

## Session and attempts

The browser receives only an HTTP-only, SameSite=Lax session cookie. Its random value is hashed with the session secret before storage in SQLite. `users` stores the stable Google `sub`, and `sessions` stores session ownership and expiry. Attempt creation derives the student ID from the session; it never accepts a client-provided student ID. Attempt retrieval returns 404 for another student's attempt.

## APIs

- `POST /api/auth/google`
- `GET /api/auth/me`
- `POST /api/auth/logout`

`/student`, `POST /api/attempts`, and `GET /api/attempts/{attempt_id}` require an authenticated session. The read-only question and taxonomy APIs remain public.

## Tests

Backend tests mock Google verification and cover login, invalid credentials, session lookup, logout, authenticated attempt ownership, and cross-student denial. A real Google login needs locally configured client IDs and was not attempted without them.
