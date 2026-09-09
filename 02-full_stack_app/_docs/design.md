## Color Palette

| Role | Token Name | Hex Value | Usage |
| --- | --- | --- | --- |
| **Primary Brand** | `color-primary-600` | `#0284C7` | Primary actions, active tabs, brand headers |
| **Primary Hover** | `color-primary-700` | `#0369A1` | Hover states for primary buttons |
| **Background** | `color-bg-base` | `#F8FAFC` | Main application background (Slate 50) |
| **Surface** | `color-bg-surface` | `#FFFFFF` | Cards, panels, modal containers |
| **Border** | `color-border` | `#E2E8F0` | Dividers, table borders, input outlines (Slate 200) |
| **Text Primary** | `color-text-main` | `#0F172A` | Primary headings and important text (Slate 900) |
| **Text Muted** | `color-text-muted` | `#64748B` | Secondary labels, descriptions, table hints (Slate 500) |
| **Success / Free** | `color-success` | `#10B981` | Free table status, confirmed SMS replies |
| **Warning / Reserved** | `color-warning` | `#F59E0B` | Reserved table status, pending SMS grace period |
| **Danger / Occupied** | `color-danger` | `#EF4444` | Occupied table status, no-show auto-removal |

---

## Typography

* **Font Family:** `Inter, system-ui, -apple-system, sans-serif` optimized for high legibility on desktop/laptop host stand displays.
* **Scale:**
* **H1 (Page Title):** 24px / Bold (`line-height: 32px`)
* **H2 (Section Header):** 18px / SemiBold (`line-height: 28px`)
* **H3 (Card Header):** 16px / Medium (`line-height: 24px`)
* **Body:** 14px / Regular (`line-height: 20px`)
* **Small / Caption:** 12px / Regular (`line-height: 16px`)

---

## Spacing & Layout Architecture

* **Grid Base:** 4px spacing scale (`space-1` = 4px, `space-2` = 8px, `space-3` = 12px, `space-4` = 16px, `space-6` = 24px, `space-8` = 32px).

---

## Component Specifications

### Buttons

* **Primary Button:** Height 40px, padding `0 16px`, background `color-primary-600`, text white, border-radius 6px. Font weight: Medium (14px).
* **Secondary Button:** Height 40px, padding `0 16px`, background `color-bg-surface`, border `1px solid color-border`, text `color-text-main`, border-radius 6px.
* **Danger Button:** Height 40px, padding `0 16px`, background `color-danger`, text white, border-radius 6px (used for removing parties or forced no-show triggers).

### Inputs & Form Controls

* **Text Input:** Height 40px, padding `8px 12px`, background white, border `1px solid color-border`, border-radius 6px, font-size 14px. Focus state: `border-color: color-primary-600` with a 2px ring.
* **Fields Required for Manual Party Entry:** Name, Phone Number, Party Size, and Notes.

### Badges & Status Indicators

* **Table Status Badges:**
* *Free:* Green background (`#ECFDF5`), Green text (`#047857`).
* *Occupied:* Red background (`#FEF2F2`), Red text (`#B91C1C`).
* *Reserved:* Amber background (`#FFFBEB`), Amber text (`#B45309`).


* **Queue Item Badges:** Displays calculated rule-based estimated wait time based on position, party size, and turnover.

---