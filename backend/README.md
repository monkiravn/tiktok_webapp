# FastAPI Backend

## Run

```bash
uv sync
copy .env.example .env  # Windows (or: cp .env.example .env)
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes
- SQLite DB at `app.db`, admin seed `admin/password123`.
- Uploads under `uploads/`.
- Requires `ffmpeg` installed and on PATH.
- Base API path: `/api/v1`.
