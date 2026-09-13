# Waitly backend

FastAPI service for the Waitly host stand and guest join flow. Implements the HTTP contract in [`../openapi.yaml`](../openapi.yaml) and keeps state in an in-memory store (`src/backend/store.py`).

```powershell
uv sync
uv run waitly-api      # http://localhost:8001/v1
uv run pytest -v
```

Or with Make: `make install`, `make run`, `make test`.

Set `PORT` to change the listen port (default `8001`). Start the frontend separately; Vite proxies `/v1` to this API during local dev.
