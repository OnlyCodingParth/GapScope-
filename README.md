# GapScope

GapScope is an education tool being built to help students understand the reason behind a mistake, starting with quadratic equations.

## Architecture

The React frontend talks only to `/api`. During local development Vite forwards that path to the FastAPI backend, so browser code never needs a backend host name. The backend provides a health endpoint and a local Quadratic Equations content database for the next quiz and diagnosis phases.

## Prerequisites

Node 20+ and Python 3.11+.

## Run locally

Frontend:

```sh
cd frontend
npm install
npm run dev
```

Backend on Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Backend on macOS/Linux:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

`GET http://127.0.0.1:8000/api/health` returns `{"status":"ok","service":"gapscope-backend"}`.

## Demo data

The backend creates and seeds `backend/data/gapscope.db` when it starts. From `backend`, run `python -m app.seed` to seed again safely; stable IDs prevent duplicates. Read-only content endpoints are `/api/questions`, `/api/misconceptions`, `/api/misconception-mappings`, and `/api/prerequisites`.

## Environment

Copy the `.env.example` file in each app only when changing local defaults. Frontend `VITE_API_BASE_URL` defaults to `/api`; set `VITE_GOOGLE_CLIENT_ID` to enable Google Identity Services. Backend `APP_ENV` defaults to `local`, `FRONTEND_ORIGIN` defaults to `http://localhost:5173`, and Google login requires matching `GOOGLE_CLIENT_ID`. Set a high-entropy `SESSION_SECRET` and `COOKIE_SECURE=true` for HTTPS production.

## Quiz attempts

The student preview can load and submit the seeded Quadratic Equations quiz. The backend owns grading, derives the student from the authenticated session, and returns its result at `GET /api/attempts/{attempt_id}`. `GET /api/quiz/questions` intentionally omits correct answers; submit one answer for each question using `POST /api/attempts`.

## Current scope

The project includes its foundation, Google-authenticated student sessions, seeded question bank, deterministic answer grading, and misconception mapping. It intentionally does not include learning-gap diagnosis, reports, recommendations, AI features, or teacher analytics.
