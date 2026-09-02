# Project Scope Specification: Homework Quest

## 1. Executive Summary & Overview
The **Homework Quest** is an interactive, shared-screen web application designed for an always-on kitchen tablet display. It gamifies household chore management through competitive motivation, effort-based Experience Point (XP) rewards, and engaging arcade audio-visual feedback. 

Household members log chores, earn XP, and compete on a weekly leaderboard for pre-set real-world perks drawn at random at the beginning of each cycle. Fairness is maintained through peer approval authentication backed by an automated 24-hour timeout safety net.

---

## 2. Core Game Loop & Design Decisions

| Parameter | Decision / Mechanism | Description |
| :--- | :--- | :--- |
| **Primary Mechanic** | Gamified Guild (XP & Rewards) | Members earn XP for completing tasks and unlock real-world household privileges. |
| **Motivation Dynamic** | Competitive Leaderboard | Members compete for the top spot on a weekly leaderboard. |
| **Verification System** | Peer Approval (Seconding) | Tasks require confirmation by another housemate via a 4-digit PIN. |
| **Approval Timeout** | 24-Hour Auto-Approve | Unreviewed tasks auto-grant XP after 24 hours to prevent progress bottlenecks. |
| **XP Point Model** | Effort / Time-Based Scaling | XP scales dynamically with estimated time/difficulty (e.g., 5 min = 10–20 XP; 45+ min = 100+ XP). |
| **Chore Source** | Hybrid Pool | Combines automated recurring routines (daily/weekly) with an ad-hoc bonus chore board. |
| **Platform Target** | Kitchen Tablet / Web Dashboard | Optimized for an always-on, high-contrast, shared-screen tablet display. |
| **Authentication** | Quick 4-Digit PIN | Fast profile selection and PIN verification for completing or approving tasks. |
| **Idle Screen State** | Live Leaderboard & Feed | Default display shows real-time standings, weekly stake details, and recent activity. |
| **Feedback System** | Arcade SFX + Visual Animations | High-energy visual confetti/animations paired with retro sound effects through tablet speakers. |
| **Perk Selection** | Random Draw | At cycle start, the system randomly selects the week's stake from a custom household library. |
| **Tie-Breaker Rule** | Shared Victory | If members finish with identical top XP, all tied members win the week's reward stake. |
| **Reset Cycle** | Fixed Schedule | Resets automatically on a fixed weekly schedule (e.g., Sunday 00:00). |

---

## 3. Detailed Screen & View Specifications

### 3.1 Main Dashboard (Default Idle View)
The primary screen displayed when no active interaction is taking place on the kitchen tablet.

* **Leaderboard Pane (Left):**
  * **Current Cycle Standings:** Visual rankings of household members with custom avatars, current XP totals, and animated progress bars.
  * **Active Stake Banner:** Prominently highlights the week's Random Draw perk (e.g., *"This Week's Stake: Winner chooses Friday Night Movie"*).
  * **Time Remaining Counter:** Live countdown timer showing time remaining until the next fixed weekly reset.
* **Activity Stream Pane (Right):**
  * **Real-Time Feed:** Chronological list of recent task completions, pending peer approvals, and awarded XP points.
  * **Status Badges:** Visual indicator tags showing task states (`Pending Approval`, `Auto-Approved`, `Verified`).
* **Global Action Bar (Bottom):**
  * High-contrast touch buttons: **`[ + Log Chore ]`**, **`[ Review Pending ]`**, and **`[ Chore Pool ]`**.

### 3.2 Chore Board & Ingestion View
Accessed by tapping **`[ Chore Pool ]`** or **`[ + Log Chore ]`**. Manages both automated routines and ad-hoc task creation.

* **Routine Tasks Tab:**
  * Grid/list of recurring tasks scheduled for the current day/week.
  * Card elements display chore name, estimated duration, and calculated XP badge (e.g., *"Deep Clean Fridge — 45 min — 100 XP"*).
* **Ad-Hoc Bonus Marketplace Tab:**
  * Displays user-generated, one-off bounty tasks posted by household members.
* **Ad-Hoc Task Creator Modal:**
  * **Inputs:** Chore Title, Category, and Effort/Time Slider (5 min to 60+ min).
  * **Dynamic XP Calculator:** Automatically recalculates XP value as the effort slider is adjusted.
  * **Submit Button:** Adds the bounty to the active open pool.

### 3.3 Verification & Approval Flow View
Accessed by tapping **`[ Review Pending ]`** or selecting a pending task from the Activity Feed.

* **Pending Approvals Queue:**
  * List of tasks submitted by housemates awaiting peer confirmation.
  * Card details include member avatar, task name, XP value, submission timestamp, and a **24-Hour Timeout Progress Bar**.
* **Action Controls:**
  * **`[ Approve ]` Button:** Triggers the PIN Security Overlay. Upon valid peer PIN entry, releases XP immediately accompanied by retro arcade sound effects and confetti visuals.
  * **Auto-Approval Indicator:** Visually flags tasks nearing the 24-hour mark to inform members that XP will be auto-granted soon if unreviewed.

### 3.4 PIN Security Overlay (Global Modal)
A lightweight pop-up keypad intercepting any point-altering or approval action.

* **Interface:** Large, touch-friendly 0–9 numeric keypad with profile avatar selection.
* **Flow:** Select Avatar $\rightarrow$ Enter 4-Digit PIN $\rightarrow$ Instant validation/action execution.
* **Security Rules:** Self-approval is strictly prevented by system logic (a member cannot approve their own pending submissions).

### 3.5 Weekly Reset & Random Draw Screen
An automated celebration event screen displayed at the scheduled weekly reset time (e.g., Sunday 00:00).

* **Ceremony & Victory Phase:**
  * Plays celebratory arcade fanfare audio and full-screen visual animations.
  * Displays final standings and crowns the weekly winner (or highlights all tied members in the event of a Shared Victory).
* **Random Perk Selection Phase:**
  * Animated "Slot Machine / Wheel" effect cycling through available items in the **Perk Library**.
  * Formally locks in and displays the Pre-Set Stake for the upcoming weekly cycle.
* **`[ Start New Cycle ]` Trigger:** Resets current XP tallies to 0 and initializes the board for the new week.

### 3.6 System Settings & Perk Library View
A PIN-protected administrative management area for household setup.

* **Member Management:** Add/edit household profiles, avatars, and PIN codes.
* **Perk Library Manager:** Add, edit, or toggle availability for custom perks (e.g., *"Exemption from Trash Duty"*, *"Takeout Choice"*).
* **Routine Schedule Manager:** Customize recurring base tasks, recurrence schedules, and default effort ratings.

---

## 4. System Entity Model (Data Schema)

| Entity | Core Attributes | Relationships & Notes |
| :--- | :--- | :--- |
| **User Profile** | `id`, `name`, `avatar_url`, `pin_hash`, `current_cycle_xp`, `total_wins` | Has many `ChoreInstance` submissions & approvals. |
| **Chore Template** | `id`, `title`, `category`, `estimated_minutes`, `base_xp`, `recurrence_rule` | Defines automated recurring tasks. |
| **Chore Instance** | `id`, `template_id` (optional), `title`, `xp_value`, `status` (`Open`, `Pending`, `Approved`), `assignee_id`, `approver_id`, `submitted_at`, `auto_approve_at` | Tracks individual task completions and approvals. |
| **Perk Library** | `id`, `title`, `description`, `is_active` | Pool of rewards available for the random weekly draw. |
| **Weekly Cycle** | `id`, `start_time`, `end_time`, `selected_perk_id`, `standings_json`, `winner_ids` | Historical log of weekly competitions and outcomes. |

---

## 5. Technical Requirements & Non-Functionals

* **Responsive Layout:** Fixed aspect ratio optimization for standard 10"–12" tablet landscape orientation (e.g., 1920x1200 or 1280x800).
* **Persistence & Real-time State:** Instant state synchronization across multiple client renders (if accessed concurrently from phone or tablet).
* **Audio Playback:** Local Web Audio API implementation with fallback support for low-latency sound triggers.
* **Offline Resilience:** Local storage caching for offline queuing during intermittent network connectivity.
