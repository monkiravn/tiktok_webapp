# Migration to FastAPI + React

This document describes the new split architecture and how to run the services.

## Overview

- Backend: FastAPI + SQLAlchemy + SQLite (via `uv` and `uvicorn`)
- Frontend: React (Vite) + TailwindCSS
- Legacy Flask app remains under `src/` until the migration is complete.

## Backend (FastAPI)

Paths:
- App: `backend/app/main.py`
- Config: `backend/app/config.py`
- DB/Seed: `backend/app/db.py`
- Models: `backend/app/models.py`
- Routers: `backend/app/routers/api.py`
- Services: `backend/app/services/*`

Run (dev):
```bash
uv sync
copy backend\.env.example backend\.env  # Windows
# or: cp backend/.env.example backend/.env
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Notes:
- Requires ffmpeg in PATH for video processing.
- SQLite DB `app.db` at repo root; admin seed `admin/password123`.
- Upload directory: `uploads/`.

API base path: `/api/v1`
- Health: `GET /health`
- Upload: `POST /upload` (multipart `file`)
- Download: `GET /download/{filename}`
- TikTok live: `/tiktok_live/status`, `/start`, `/stop`, `/users` (GET/POST/DELETE), `/get_live_status`

Auth and Users:
- `POST /auth/register` (status=pending)
- `POST /auth/login` -> returns `{ access_token, token_type }` (Bearer)
- `GET /auth/me` -> current user info (requires Authorization)
- `GET /users/` (admin) -> all users
- `GET /users/pending` (admin)
- `PUT /users/{user_id}/approve` (admin)
- `DELETE /users/{user_id}` (admin, cannot delete self)

## Frontend (React + Tailwind)

Paths:
- `frontend/`

Run (dev):
```bash
cd frontend
copy .env.example .env  # Windows
# or: cp .env.example .env
npm install
npm run dev  # http://localhost:5173
```

The frontend uses `VITE_API_BASE_URL` to reach the backend (default `http://localhost:8000/api/v1`).

## Next Steps

1. Port authentication to FastAPI using JWT (login/refresh) and protect routes.
2. Port remaining repositories/models from `src/` to `backend/app` (remove Flask-isms).
3. Migrate admin/user pages to React; call new FastAPI endpoints.
4. Remove Flask code once fully ported and tested.
