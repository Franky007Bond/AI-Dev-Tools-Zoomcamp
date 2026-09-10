# Waitly

Waitly is a single-restaurant, in-house web app that replaces the paper waitlist. It manages a live queue combining walk-ins and reservations, tracks tables on a visual floor plan, sends two-way SMS updates to guests, and forecasts wait times.

> **Status:** Frontend mock is running; backend is not started. Spec: [`_docs/specs.md`](_docs/specs.md). HTTP contract: [`openapi.yaml`](openapi.yaml).

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

```powershell
cd frontend
npm install
npm run dev      # http://localhost:5173/  (guest join: /join)
npm test
```

Agent notes (layout, git root, mock vs OpenAPI): [`AGENTS.md`](AGENTS.md).

## Contributing
_Contribution guidelines TBD._

## License
_TBD._
