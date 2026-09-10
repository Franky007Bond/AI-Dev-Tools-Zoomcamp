## Specifications
- Product spec: [`_docs/specs.md`](_docs/specs.md)
- Visual tokens (color + type): [`_docs/design.md`](_docs/design.md)
- Backend HTTP contract: [`openapi.yaml`](openapi.yaml)

## Repo layout
- This folder is a **course module** inside the parent git repo `AI-Dev-Tools-Zoomcamp`. Git commands run from the parent root. Do not create a nested `.git` here.
- Frontend lives in [`frontend/`](frontend/) (Vite + React). That spelling is intentional; do not rename folders or “fix” paths unless asked.
- There is **no backend package yet**. Host/guest UI talks to `frontend/src/api/client.js` → in-memory mock (`mockBackend.js` + `localStorage` key `waitly.mock.v1`). Wait estimates: `frontend/src/api/forecast.js`.
- When a backend is added, implement [`openapi.yaml`](openapi.yaml). Do not invent a different resource shape. Keep the mock until asked to switch the client to HTTP.

## UI constraints
- Apply `_docs/design.md` for **color and typography only**.
- Do **not** restyle or restructure the host-stand layout unless asked. Keep:
  - top tabs: Board / SMS / Analytics / Settings
  - Board as two columns: queue (left) + floor plan (right)
  - pill-style tab/action buttons
  - queue ticket Edit + Remove **right-aligned**
- Host stand is `/`. Guest join is `/join` (QR / public form). No guest live-status page in v1.

## Stack
- Frontend: Node.js in `frontend/`
- Backend (when started): Python with **uv** for dependency management
- v1 is a single restaurant, one host role, no auth, rule-based wait estimates (not ML)

## Commands
PowerShell: chain with `;`, not `&&`. Git commit messages: use a PowerShell here-string, not bash `<<EOF`.

```powershell
cd frontend
npm install
npm run dev      # http://localhost:5173/  guest: /join
npm test
```

Backend later:

```powershell
uv sync
uv add <PACKAGE-NAME>
uv run python <PYTHON-FILE>
```

## Documentation lookups
Use the **/find-docs** skill when implementing against any external library, framework, or API (SMS provider, web framework, floor-plan/canvas library, OpenAPI tooling). Do not rely on training data for API details.

## Git
Commit when asked. Branch work lives on parent-repo `master` unless a feature branch is requested.
