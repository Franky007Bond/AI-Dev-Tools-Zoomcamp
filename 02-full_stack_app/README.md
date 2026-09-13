# Waitly

Waitly is a single-restaurant, in-house web app that replaces the paper waitlist. It manages a live queue combining walk-ins and reservations, tracks tables on a visual floor plan, sends two-way SMS updates to guests, and forecasts wait times.

## Stack

**Frontend** — React SPA built with Vite. The host stand (`/`) and guest join page (`/join`) call a thin API layer in `frontend/src/api/client.js`, which uses `fetch` via `httpBackend.js` to talk to the backend. During local dev, Vite proxies browser requests from `/v1` to the backend so the UI can stay on one origin.

**Backend** — Python API built with FastAPI, managed by `uv`. It implements the HTTP contract in [`openapi.yaml`](openapi.yaml) and keeps state in an in-memory store (seeded demo data, no database yet). Uvicorn serves the API at `http://localhost:8001/v1` by default.

**How they communicate** — JSON over REST. Mutating host actions (add party, seat, reorder, etc.) return a fresh `Snapshot` so the UI can refresh in one round trip; guest join uses `POST /v1/join`. The frontend polls `GET /v1/snapshot` every few seconds to stay live. Tests can still use the in-memory mock in `mockBackend.js` instead of HTTP.

## Who it's for
- **Host** — the only staff role in v1. Runs the queue, floor plan, and settings from a desktop/laptop browser at the host stand.
- **Guest** — no account needed. Joins the queue via a QR code/web link and gets updates by SMS.

## Features (v1)

- **Unified queue** — walk-ins and reservations in one list; host can add, edit, reorder, remove, or seat any party.
- **Visual floor plan** — tables shown as free / occupied / reserved; host taps a table to update status or seat a party. Reservations auto-block their table for the reserved window.
- **Wait time forecasting** — rule-based estimate from queue position, party size, and table availability; recalculates live.
- **Two-way SMS** — automatic texts on joining and when a table's ready; guests reply to confirm or cancel. No-shows are auto-removed after a grace period (default 5–10 min).
- **Analytics dashboard** — simple daily/weekly view of average wait time, parties seated, no-show rate, and busiest hours.

## Not in v1
- Multi-location/multi-tenant support
- Guest-facing live status page (SMS only)
- Multiple staff roles/permissions
- POS integration
- Native mobile app
- ML-based forecasting
- Detailed reports/export

## Platform
Web app, built for desktop/laptop browser use.

## Roadmap / open questions
- Special requests per party (seating preference, high chair, occasion)
- Large party handling (combining tables)
- Party size limits
- SMS message branding/customization
- Configurable grace period and reminder cadence

## Getting started

Run the backend and frontend in separate terminals.

**Backend** (FastAPI, default port `8001`):

```powershell
cd backend
uv sync
uv run waitly-api      # http://localhost:8001/v1
```

Or with Make:

```powershell
cd backend
make install
make run
make test
```

**Frontend** (Vite + React):

```powershell
cd frontend
npm install
npm run dev            # http://localhost:5173/  (guest join: /join)
npm test
```

The dev server proxies `/v1` to `http://localhost:8001`, so the browser talks to the backend without CORS setup.

### URLs
- Host stand: http://localhost:5173/
- Guest join: http://localhost:5173/join
- API base: http://localhost:8001/v1

If port `5173` is already in use, Vite picks the next free port (for example `5174`).

### Optional env vars
- `PORT` — backend listen port (default `8001`)
- `VITE_API_BASE` — frontend API base URL (default `/v1`)
- `VITE_USE_MOCK=true` — use the in-memory mock instead of HTTP

## Project layout
- [`frontend/`](frontend/) — host stand + guest join UI
- [`backend/`](backend/) — FastAPI service with in-memory store
- [`openapi.yaml`](openapi.yaml) — HTTP contract
- [`_docs/specs.md`](_docs/specs.md) — product spec
- [`_docs/design.md`](_docs/design.md) — color and typography tokens

Agent notes: [`AGENTS.md`](AGENTS.md).
