# Homework Quest

Homework Quest is a Django web app designed for an always-on kitchen tablet. Household members log chores, earn effort-based XP, get peer PIN approval (or auto-approve after 24 hours), and compete each week for a randomly drawn real-world perk.

---

## Table of contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Quick start](#quick-start)
4. [Project structure](#project-structure)
5. [Screens and URLs](#screens-and-urls)
6. [API endpoints](#api-endpoints)
7. [Management commands](#management-commands)
8. [Scheduled jobs](#scheduled-jobs)
9. [Testing](#testing)
10. [Core concepts](#core-concepts)
11. [Frontend behaviour](#frontend-behaviour)
12. [Further reading](#further-reading)

---

## Features

- **Dashboard** — live leaderboard, weekly stake, activity feed, and quick actions
- **Chore pool** — routine templates and ad-hoc bounty board
- **PIN overlay** — pick a household member, enter a 4-digit PIN, then log or approve
- **Peer approval** — a different member must verify chores before XP is granted
- **24-hour auto-approve** — pending chores pay out automatically if nobody reviews them
- **Weekly cycle** — standings reset every week; top scorer(s) win; next perk is drawn at random
- **Weekly ceremony** — celebration screen with winner crowns and perk wheel
- **Settings** — admin-only CRUD for members, perks, and routine templates
- **Offline queue** — failed log/approve requests are cached and replayed when back online
- **Near-real-time dashboard** — polls `/api/dashboard/` every 5 seconds for fresh data

---

## Requirements

| Tool | Version |
|------|---------|
| Python | ≥ 3.13 |
| [uv](https://docs.astral.sh/uv/) | latest (required package manager) |
| Django | 6.1 (installed via uv) |

> **Important:** Use **uv** for all dependency and environment work (`uv add`, `uv sync`, `uv run …`). Do not use pip, Poetry, or a hand-managed virtualenv for this project.

---

## Quick start

### 1. Install dependencies

```bash
uv sync
```

### 2. Apply database migrations

```bash
uv run python manage.py migrate
```

### 3. Bootstrap the first weekly cycle (fresh install)

Creates an open weekly cycle and randomly draws an active perk, but only if no open cycle exists yet.

```bash
uv run python manage.py bootstrap_weekly_cycle
```

> Before bootstrapping, add at least one **active perk** (via Django admin or the Settings screen after creating an admin member).

### 4. Run the development server

```bash
uv run python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser (landscape tablet viewport recommended).

### 5. Initial household setup (recommended order)

1. Create members in **Settings** (mark at least one as **Admin**).
2. Add **perks** to the perk library (keep at least one active).
3. Add **routine templates** for recurring chores.
4. Run `bootstrap_weekly_cycle` if the dashboard shows “No stake selected yet”.

---

## Project structure

```
01-overview/
├── manage.py                 # Django entry point
├── pyproject.toml            # uv project config + pytest settings
├── deploy/
│   └── cron.example          # Example OS cron entries for scheduled jobs
├── tests/                    # All pytest test modules
│   ├── paths.py              # Shared file paths for static-asset tests
│   └── test_*.py
├── homework_quest/             # Django project + app
│   ├── models.py             # Profile, ChoreTemplate, ChoreInstance, Perk, WeeklyCycle
│   ├── services.py           # Approval, logging, auto-approve business logic
│   ├── cycle.py              # Weekly reset and winner selection
│   ├── dashboard.py          # Dashboard context + JSON payload
│   ├── views.py              # Page views and JSON API views
│   ├── settings_auth.py      # Admin PIN gate for Settings
│   ├── scheduler.py          # Registered unattended jobs
│   ├── test_settings.py      # Isolated DB settings for pytest (not a test file)
│   ├── management/commands/  # Management commands
│   ├── templates/            # Django HTML templates
│   └── static/homework_quest/  # CSS, JS (see static/homework_quest/CSS.md)
└── _docs/
    ├── tasks.md              # Full task backlog / product spec
    └── plan.md               # Product plan
```

---

## Screens and URLs

| URL | Screen | Description |
|-----|--------|-------------|
| `/` | Dashboard | Leaderboard, stake, activity feed, action bar |
| `/chore-pool/` | Chore pool | Routine cards + ad-hoc bounty board |
| `/review-pending/` | Review queue | Pending chores with 24h timeout progress |
| `/ceremony/` | Weekly ceremony | Final standings, winners, perk wheel, **Start New Cycle** |
| `/settings/` | Settings | Admin PIN gate; members, perks, templates CRUD |
| `/admin/` | Django admin | Built-in Django admin (optional) |

---

## API endpoints

All API routes are under `/api/`.

| Method | URL | Purpose |
|--------|-----|---------|
| `GET` | `/api/dashboard/` | JSON snapshot for dashboard polling |
| `POST` | `/api/chores/log/` | Log a chore (JSON: `profile_id`, `pin`, `title`, plus `estimated_minutes` or `template_id`; XP is computed server-side) |
| `POST` | `/api/chores/<id>/approve/` | Peer-approve (JSON: `approver_id`, `pin`) |
| `GET` | `/api/chores/<id>/` | Chore detail JSON |

### Example: log a chore

```bash
curl -X POST http://127.0.0.1:8000/api/chores/log/ \
  -H "Content-Type: application/json" \
  -d '{"profile_id": 1, "pin": "1234", "title": "Dishes", "estimated_minutes": 14}'
```

### Example: peer-approve

```bash
curl -X POST http://127.0.0.1:8000/api/chores/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"approver_id": 2, "pin": "5678"}'
```

---

## Management commands

Run every command with `uv run python manage.py <command>`.

| Command | Description |
|---------|-------------|
| `bootstrap_weekly_cycle` | Create the first open weekly cycle + perk draw (idempotent) |
| `auto_approve_chores` | Approve pending chores past their 24-hour deadline |
| `reset_weekly_cycle` | Close the current cycle, record winners, reset XP, draw next perk |
| `run_scheduled_jobs` | Run registered jobs whose cron schedule matches the current time |

---

## Scheduled jobs

Homework Quest expects two unattended jobs:

| Job | Schedule | Command |
|-----|----------|---------|
| Auto-approve safety net | Every hour (`0 * * * *`) | `auto_approve_chores` |
| Weekly reset | Sunday 00:00 (`0 0 * * 0`) | `reset_weekly_cycle` |

Example OS cron entries are in [`deploy/cron.example`](deploy/cron.example). Adjust the project path before installing:

```bash
crontab deploy/cron.example
```

Registered jobs are defined in `homework_quest/scheduler.py`.

---

## Testing

### Run the full suite

```bash
uv run pytest
```

### Run a single file or test

```bash
uv run pytest tests/test_integration_dashboard.py
uv run pytest tests/test_approval.py -k "self_approval"
```

### Test configuration

| Setting | Value |
|---------|-------|
| Test directory | `tests/` |
| Django settings | `homework_quest.test_settings` (in-memory SQLite) |
| Config file | `pyproject.toml` → `[tool.pytest.ini_options]` |

Tests never touch the developer's `db.sqlite3` file.

---

## Core concepts

### XP formula

Effort is converted to XP by `homework_quest.xp.xp_from_minutes()`:

- **5 minutes → 10 XP**
- **45 minutes → 100 XP**
- Linear interpolation between anchors; result clamped to ≥ 0

### Chore lifecycle

```
Open  →  Pending  →  Approved
         (submitted)   (peer or auto)
```

- **Open** — unclaimed ad-hoc bounty on the board
- **Pending** — logged/claimed; awaiting peer review; 24-hour auto-approve timer starts
- **Approved** — XP granted to assignee (`approved_via`: `peer` or `auto`)

Self-approval is blocked: the assignee cannot approve their own chore.

### Weekly cycle

- One **open cycle** exists at a time (no winners recorded yet).
- On reset: standings are snapshotted, winner(s) crowned (shared victory on ties), XP zeroed, next perk drawn.
- Reset can be triggered by the management command, the **Start New Cycle** button on `/ceremony/`, or the weekly cron job.

### Settings access

Settings requires a household member with **`is_admin=True`** and a valid 4-digit PIN. Successful unlock stores an admin session; use **Lock** to end it.

### PIN security

- PINs are stored hashed only (never plaintext in the database).
- The global PIN overlay identifies the acting member before any XP-changing action.
- Raw PINs are not logged.

---

## Frontend behaviour

### PIN overlay

Used on **Review Pending** and **Chore Pool** for log and approve actions:

1. Select household member (avatar)
2. Enter 4-digit PIN on the keypad
3. Action executes (or queues offline — see below)

### Offline queue

When the network is unavailable or a fetch fails, log/approve requests are saved to `localStorage` under key `homework_quest_offline_queue_v1` and replayed in order when connectivity returns.

Payload schema is documented in `homework_quest/offline_queue.py`.

### Dashboard polling

The dashboard loads `dashboard.js`, which polls `GET /api/dashboard/` every **5 seconds** and updates the leaderboard and feed without a full page reload.

### Arcade feedback

On successful peer approval and on the weekly ceremony screen, the app plays retro Web Audio SFX and a confetti burst. If `AudioContext` is blocked by the browser, feedback fails silently — XP logic is never affected.

### Tablet layout

UI is tuned for **1280×800** and **1920×1200** landscape kitchen tablets. Breakpoints and tap-target guidelines are in [`homework_quest/static/homework_quest/CSS.md`](homework_quest/static/homework_quest/CSS.md).

---

## Further reading

- [`_docs/plan.md`](_docs/plan.md) — product overview and data model
- [`_docs/tasks.md`](_docs/tasks.md) — full implementation task backlog
- [`homework_quest/static/homework_quest/CSS.md`](homework_quest/static/homework_quest/CSS.md) — tablet CSS breakpoints
- [`deploy/cron.example`](deploy/cron.example) — production scheduling template
