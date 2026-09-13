# Waitly frontend

Host-stand and guest-join UI for Waitly. API calls go through `src/api/client.js`, which uses the HTTP backend by default (`src/api/httpBackend.js`).

```powershell
npm install
npm run dev      # http://localhost:5173/  (guest join: /join)
npm test
```

Start the backend first (`cd ../backend ; uv run waitly-api`). Vite proxies `/v1` to `http://localhost:8001`.

Set `VITE_USE_MOCK=true` to run against the in-memory mock instead of HTTP.
