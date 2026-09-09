# Waitly — Restaurant Waitlist Manager
## Requirements & Scope (v1)

## 1. Overview
A single-restaurant, in-house web application that replaces the paper waitlist. It manages a live queue that combines walk-ins and reservations, tracks table availability via a floor plan, sends two-way SMS updates to guests, and forecasts wait times.

## 2. Users
- **Host** — the only staff role in v1. Full access to the queue, floor plan, and settings.
- **Guest** — interacts only via SMS (joins remotely by QR/web form, replies to confirm/cancel). No account or login required.

## 3. Core Functional Requirements

### 3.1 Queue Management
- Single unified queue combining walk-ins and reservations.
- Host can add a party manually (name, phone, party size, notes).
- Guests can join remotely via a QR code / web link before arriving (same fields as above).
- Host can reorder, edit, remove, or seat any party.
- Reservations appear in the queue at their scheduled time and hold a table block on the floor plan.

### 3.2 Floor Plan & Table Management
- Visual floor plan showing all tables, seating capacity, and status (free / occupied / reserved).
- Host taps a table to toggle status or assign a waiting party to it.
- Reservations automatically block their assigned table for the reserved window.

### 3.3 Wait Time Forecasting
- Rule-based estimate per party, calculated from:
  - Position in queue
  - Party size (vs. available table sizes)
  - Current table availability / expected turnover
- Estimate recalculates as the queue and floor plan change.

### 3.4 SMS Notifications (Two-Way)
- Automatic text when a party joins the queue (confirmation + estimated wait).
- "Your table is ready" text when a table becomes available.
- Guest can reply to **confirm** (on their way) or **cancel** (remove from queue).
- **No-show handling:** grace period (default 5–10 min, configurable) after the "ready" text; if no confirmation, party is auto-removed and host is notified.

### 3.5 Analytics Dashboard
- Simple daily/weekly summary view:
  - Average wait time
  - Total parties seated
  - No-show rate
  - Busiest hours/days
- No CSV export or detailed reporting in v1.

## 4. Explicitly Out of Scope (v1)
- Multi-location / multi-tenant support
- Guest-facing live status/tracking web page (SMS only)
- Multiple staff roles or permission tiers
- POS integration
- Native mobile app (desktop/laptop browser only)
- Data-driven/ML wait-time forecasting
- Detailed reports or data export

## 5. Platform
- Web application, optimized for desktop/laptop browser use at the host stand.

## 6. Open Items for Future Discussion
- Special requests/notes per party (seating preference, high chair, occasion)
- Large party handling (combining tables)
- Party size limits
- Branding/customization of SMS messages
- Configurable grace period and reminder cadence

---
*Generated from a scoping session on 2026-09-09. This document reflects v1 decisions and can evolve as requirements are refined.*
