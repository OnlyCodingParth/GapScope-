# GapScope backend

The FastAPI service exposes `GET /api/health`, keeps `/docs` available, and initializes a local SQLite database at `data/gapscope.db` on startup. Read-only content APIs are `GET /api/questions`, `/api/misconceptions`, `/api/misconception-mappings`, and `/api/prerequisites`.

Create a virtual environment, install `requirements-dev.txt`, then run `uvicorn app.main:app --reload --port 8000`. Run `python -m app.seed` to explicitly seed safely, or `python -m pytest` for tests.
