# Phase 1: project foundation

## Implemented

The project has a React TypeScript frontend with accessible foundation routes, an API client that only uses `/api`, and a FastAPI health endpoint. The frontend shows live backend status and handles unavailable, failed, and invalid responses without presenting made-up product data.

## Dependencies installed and tested

Frontend: React 19.3.0, React DOM 19.3.0, React Router DOM 7.18.4, Vite 8.3.3, TypeScript 6.0.3, Tailwind CSS 4.3.3, `@tailwindcss/vite` 4.3.3, IBM Plex Sans 5.3.0, Source Serif 4 5.3.0, plus the Vite template's React plugin and oxlint.

Backend: FastAPI 0.142.2, Uvicorn 0.54.0, pydantic-settings 2.15.0, pytest 8.4.2, and httpx 0.28.1.

## Commands

Run the frontend with `cd frontend`, `npm install`, and `npm run dev`. Run `npm run build` and `npm run lint` for checks. In the backend virtual environment, run `python -m pytest` and `uvicorn app.main:app --reload --port 8000`.

## Environment

`frontend/.env.example` documents `VITE_API_BASE_URL=/api`. `backend/.env.example` documents local `APP_ENV` and `FRONTEND_ORIGIN`; it lists future secret names only as comments. Neither application needs a `.env` file to start.

## Tests performed

Backend health test passed. The frontend production build passed; lint completed with one non-failing React advisory about the initial health-check state update. The live health endpoint, allowed/disallowed CORS behavior, Vite `/api` proxy, all five routes, and responsive widths 320, 375, 768, 1024, and 1440 were checked. Backend stop/restart was checked through the unavailable state and retry control. Temporary malformed-response and application non-2xx endpoint checks were not added because this phase intentionally exposes only the health endpoint.

## Known limitations and next phase

This is a foundation release. It has no database, authentication, diagnosis engine, learner data, reports, or practice. Phase 2 can add the SQLite and JSON content foundation described in the master plan.
