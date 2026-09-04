# Homework Quest — Tablet CSS

Kitchen tablet layout targets **1280×800** and **1920×1200** landscape orientations.

## Breakpoints

| Query | Use |
|-------|-----|
| `(min-width: 1280px)` | Default two-column dashboard, full action bar |
| `(max-width: 900px)` | Single-column stack (fallback for narrow viewports) |
| `(min-height: 800px)` | Extra vertical padding on main panels |

## Tap targets

All interactive controls aim for **≥ 48px** minimum height (action buttons use 64px; PIN keys use 72px).

## High contrast

- Background `#0d1117`, panels `#161b22`, text `#f5f5f5`
- Links and accents `#58a6ff`; primary actions green `#238636`
- No text links below 16px; navigation uses button-styled anchors

## Files

- `dashboard.css` — idle dashboard, action bar, shared tokens
- `pin_overlay.css` — full-screen PIN keypad
- `chore_pool.css`, `review_pending.css`, `settings.css`, `ceremony.css` — feature screens
- `tablet.css` — shared landscape tuning imported by all pages
