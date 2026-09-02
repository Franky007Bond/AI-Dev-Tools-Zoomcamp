# Homework Quest — Task Backlog

Homework Quest is a Django web app for an always-on kitchen tablet. Household members log chores, earn effort-based XP, get peer PIN approval (or auto-approve after 24 hours), and compete on a weekly leaderboard for a randomly drawn real-world perk.

**Package manager:** Use **uv** for every Python environment and dependency change (`uv add`, `uv remove`, `uv lock`, `uv run …`). Do not introduce pip, Poetry, or a hand-managed venv for new work. If Django or test tools are missing from the uv environment, add them with uv before coding.

The Django project lives in this folder (`manage.py`, package `homework_quest`). Each task below is meant to be finishable in one session and assignable to someone who has not read the other tasks.

---

## 1. Passing smoke test for the empty project
Goal: Add a test that proves the empty Django project boots, and run it successfully with uv.
Description: Adopt **uv** as the package manager for this repo (pyproject.toml / lockfile, Django and test extras installed via `uv add`). Add one automated test that loads Django settings and asserts the project is configured (for example the default `/` response from the development URLconf or a trivial `assert True` that still runs under Django’s test runner). Success is `uv run python manage.py test` (or `uv run pytest`) exiting 0 on the empty project.

## 2. Test harness: pytest, Django DB, and uv scripts
Goal: Make unit and integration tests easy to run the same way for every later task.
Description: With **uv**, add pytest and pytest-django (or document `manage.py test`) and a single documented command such as `uv run pytest`. Configure an isolated test settings/database so tests do not need a running server or a developer’s sqlite file. Include a short note in the test config or README snippet so a new assignee knows the only supported runner is uv.

## 3. User Profile model with explicit admin flag
Goal: Persist household members with hashed 4-digit PINs, cycle XP, and a settings-access flag.
Description: Add a Profile with `name`, `avatar_url`, `pin_hash`, `current_cycle_xp`, `total_wins`, and `is_admin` (boolean, default False) so Task 27's settings gate has a real field to check instead of an undocumented convention decided later. Store PINs hashed only — never persist the raw 4-digit PIN.Add a Profile with name, avatar_url, pin_hash, current_cycle_xp, total_wins, and is_admin (boolean, default False) so Task 27's settings gate has a real field to check instead of an undocumented convention decided later. Store PINs hashed only — never persist the raw 4-digit PIN.

## 4. Unit tests for PIN hashing and profile XP fields
Goal: Prove PINs are hashed and cycle XP starts at zero without using the browser.
Description: Write unit tests that create a Profile, set a 4-digit PIN, and assert the stored value is not the plaintext PIN and that `check_pin` (or equivalent) accepts the correct PIN and rejects a wrong one. Also assert new profiles have `current_cycle_xp == 0` and `total_wins == 0`. Run with uv (`uv run pytest` or `uv run python manage.py test`).

## 5. Chore Template model and effort-based XP helper
Goal: Represent recurring chores and compute one fixed XP value from estimated minutes, not a range.
Description: Add a Chore Template with `title`, `category`, `estimated_minutes`, `base_xp`, and `recurrence_rule`. Implement one pure function/model method that maps minutes to XP using an explicit, documented curve anchored at the spec points — fix a single value for 5 minutes (e.g. 10, the low end of "10–20"), fix 45 minutes at 100, and define the interpolation/rounding between them — so "10–20 XP" resolves to one deterministic number instead of an open range. Keep the formula in one place so the UI slider and server can never drift apart.

## 6. Unit tests for XP scaling
Goal: Lock the minutes-to-XP formula with fast tests, including edge cases.
Description: Unit-test the XP helper for short jobs (~5 min), long jobs (45+ min), and boundaries (0, 60+). Tests should not hit HTTP or the database unless the helper is a model method that requires an instance. A new assignee only needs the XP function signature and these examples from the product spec.

## 7. Chore Instance model, status machine, and approval-source tracking
Goal: Track a chore from open to approved while recording how it was approved.
Description: Add Chore Instance with optional `template` (optional), `title`, `xp_value`, `status` (`Open`, `Pending`, `Approved`), `assignee`, `approver` (nullable), `submitted_at`, and `auto_approve_at` and an explicit `approved_via` field (`peer` / `auto`) rather than leaving the dashboard to infer it from `approver` being null.
Ad-hoc bounties start as `Open` with no assignee; a separate claim action (Task 35) is what moves them to `Pending`.

## 8. Unit tests for chore status and auto-approve timestamp
Goal: Verify status values and that pending chores get a 24-hour auto-approve deadline.
Description: Write unit tests that create an instance as Pending and assert `auto_approve_at` is 24 hours after `submitted_at`. Cover invalid transitions if you encode them (for example Approved chores cannot be approved again). No views required.

## 9. Perk Library and Weekly Cycle models
Goal: Store household perks and one weekly competition record with a selected stake.
Description: Perk has `title`, `description`, and `is_active`. Weekly Cycle has `start_time`, `end_time`, `selected_perk`, `standings_json` (or an equivalent snapshot), and `winner_ids` (multiple winners on a tie). The product resets on a fixed weekly schedule (e.g. Sunday 00:00) and draws the next stake from active perks.

## 10. Unit tests for shared-victory winner selection
Goal: Given XP totals, pick one winner or all tied leaders, without HTTP.
Description: Implement a small function that, given a mapping of profile id → cycle XP, returns the winner id list: the unique top scorer, or every profile sharing that top XP (shared victory). Unit-test a clear winner, a two-way tie at the top, a three-way tie, and an empty household. This is the rule used at weekly reset.

## 11. Peer approval service (no self-approval)
Goal: Let a different member approve a pending chore with a PIN and grant XP immediately.
Description: Implement a service function: given a pending Chore Instance, an approver Profile, and a PIN, verify the PIN, reject if approver is the assignee, set status to Approved, set `approver`, and add `xp_value` to the assignee’s `current_cycle_xp`. Do not implement the keypad UI here. Use uv to run any management commands or tests you add.

## 12. Unit tests for approval rules
Goal: Cover happy-path approval, bad PIN, and self-approval rejection.
Description: Unit-test that a valid peer PIN approves the chore and increases assignee XP by `xp_value`. Assert the assignee cannot approve their own pending chore even with a correct PIN, and that a wrong PIN leaves status and XP unchanged. Use Django’s test database via uv; no browser.

## 13. Auto-approve job
Goal: After 24 hours, pending chores grant XP without a peer PIN.
Description: Add a callable (management command or service used by a scheduler) that finds Pending instances with `auto_approve_at` in the past, marks them Approved without an approver (or with a sentinel), and adds XP to the assignee. Homework Quest uses this so the board cannot stall if nobody reviews. Document how to run it with `uv run python manage.py <command>`.

## 14. Unit tests for the auto-approve job
Goal: Prove due chores auto-grant XP and future chores are left pending.
Description: Create one pending chore whose `auto_approve_at` is in the past and one still in the future. Run the job and assert only the due chore is approved and XP is granted once (idempotent if the job runs twice). Freeze time if needed. Run tests with uv.

## 15. Integration test: log chore then peer-approve
Goal: Exercise the full pending → verified XP path through Django’s test client.
Description: Using the test client (not a real browser), create two profiles and POST (or call the public API/views you introduce) to log a chore as member A, then approve it as member B with B’s PIN. Assert the chore is Approved, A’s `current_cycle_xp` increased, and the response is not a 500. If views do not exist yet, this task includes the minimal log and approve endpoints required for the test. Dependencies and the test run must use uv.

## 16. Integration test: 24-hour auto-approve path
Goal: Show a logged chore that nobody reviews still pays out after the timeout.
Description: Integration-test logging a chore, advancing time 24 hours, running the auto-approve job, then fetching the chore or dashboard payload and asserting Auto-Approved (or Approved with no peer) and XP granted. Combine the test client and the job; do not require Selenium. Run with uv.

## 17. Weekly reset, XP zeroing, and perk draw
Goal: Close the current cycle, record winners, reset XP, and pick the next perk.
Description: Implement cycle close: snapshot standings, apply shared-victory winners and increment `total_wins`, set `current_cycle_xp` to 0 for everyone, create the next Weekly Cycle, and randomly choose one `is_active` perk as the new stake. Fixed schedule is weekly (Sunday 00:00 is the spec default). Expose a `uv run` management command so it can be cron’d later.

## 18. Integration test: week rollover and new stake
Goal: Prove a full week close through the database and command, including a tie.
Description: Seed two profiles with equal leading XP, at least two active perks, and an open cycle. Run the reset command, then assert both are winners, XP is 0, `total_wins` incremented for both, a new cycle exists, and `selected_perk` is one of the active perks. Use Django’s test client or the command runner; run via uv.

## 19. Dashboard idle view (leaderboard, stake, feed, actions)
Goal: Render the kitchen idle screen: standings, this week’s perk, countdown, activity, and three action buttons.
Description: Default `/` (or `/dashboard/`) shows left: rankings with avatars, cycle XP, progress vs the leader; the active stake banner; time until weekly reset. Right: chronological activity with status badges `Pending Approval`, `Auto-Approved`, `Verified`. Bottom: high-contrast `[ + Log Chore ]`, `[ Review Pending ]`, `[ Chore Pool ]`. Optimize for ~10–12" tablet landscape. Use existing models; stub empty states if data is missing.

## 20. Integration test: dashboard shows standings and feed
Goal: Hit the dashboard URL and assert leaderboard, stake text, and a feed row appear.
Description: Seed profiles with XP, an active Weekly Cycle with a named perk, and at least one pending and one approved Chore Instance. GET the dashboard with Django’s test client and assert member names, XP, the perk title, and status-related text/badges in the HTML (or JSON if the page is hydrated that way). Run with uv; no live browser required.

## 21. Chore pool: routines, ad-hoc bounty board, and PIN-verified logging
Goal: List routine and ad-hoc chores, and only ever create a Pending instance after the acting member is identified by PIN.
Description: `[ Chore Pool ]` / `[ + Log Chore ]` opens the hybrid pool: routine cards (title, minutes, XP) and an ad-hoc bounty tab. Posting a new ad-hoc bounty via the creator modal (title, category, effort slider using the shared XP helper) creates an unassigned `Open` Chore Instance — it does not log a completion. Logging completion of any chore, routine or ad-hoc, must go through the PIN-identified logging service (Task 34) before the instance becomes `Pending`.

## 22. Integration test: create ad-hoc chore from the pool
Goal: POST a new bounty and see it in the pool or feed with the computed XP.
Description: Using the test client, submit the ad-hoc form/API with a known minute value and assert a Chore Instance exists with the expected title and XP from the shared formula. Follow a redirect or GET the pool and assert the new card is listed. uv for deps and test execution.

## 23. Pending review queue and timeout progress
Goal: Show chores waiting for a peer, with XP, submitter, and 24-hour progress.
Description: `[ Review Pending ]` lists pending instances with avatar, title, XP, `submitted_at`, a 24-hour timeout progress bar, and an `[ Approve ]` control. Flag items nearing auto-approve. Tapping Approve should be wired to open the PIN overlay (or a placeholder hook if overlay is a later task). Read-only if you must stub PIN.

## 24. Integration test: pending queue lists only pending chores
Goal: GET the review page and assert pending items appear and approved ones do not.
Description: Seed one Pending and one Approved instance. Request the review URL via the test client and assert the pending title is present and the approved title is absent (or clearly not in the queue). Run with uv.

## 25. PIN security overlay
Goal: Global keypad: pick avatar, enter 4-digit PIN, then run the intercepted action.
Description: Implement a large 0–9 keypad overlay used for any XP-changing or approval action. Flow: select profile → enter PIN → validate → execute the pending action. Reuse the approval service so self-approval is impossible. Keep it usable on a tablet (large hit areas). Do not log raw PINs.

## 26. Integration test: overlay approve vs self-approve
Goal: Drive log + approve through HTTP the way the overlay will: second member succeeds, assignee fails.
Description: With the test client, log a chore as A, attempt approve as A (must fail), then approve as B with B’s PIN (must succeed and grant XP). If the overlay is JS-only, test the same POST endpoints the keypad uses. uv to run the suite.

## 27. Settings: members, perks, and routine templates
Goal: PIN-gated admin to CRUD profiles, perk library, and recurring chore templates.
Description: Build a settings area for adding/editing members (name, avatar, PIN), perks (title, description, active flag), and routine templates (title, category, minutes, XP/recurrence). Gate entry with a valid household PIN (any member or a designated admin—pick one and document it). This is household setup, not Django admin unless you explicitly skin contrib.admin for these models.

## 28. Integration test: settings CRUD for a perk
Goal: Create or toggle a perk through the settings HTTP API/forms and read it back.
Description: Authenticate the way settings expects (PIN session or equivalent), POST a new perk or disable an existing one, then GET settings or the cycle-draw data and assert `is_active` / title persisted. Keep this an integration test of views + DB, run with uv.

## 29. Weekly ceremony screen (winners + perk wheel) with a required Start-New-Cycle control
Goal: CCelebration UI for reset that always includes the spec-required manual trigger.
Description: On cycle close (fired automatically by the scheduled reset from Task 37) show final standings, crown winner(s) on shared victory, then a slot-machine/wheel reveal of the next perk. `[Start New Cycle]` is a permanent screen control, not a demo-only stub — wire it as a first-class button that re-invokes the same reset service used by the scheduler.

## 30. Arcade feedback: Web Audio SFX and confetti
Goal: Play retro SFX and a short visual burst on successful approve and on weekly win.
Description: On verified approval and on the ceremony screen, trigger confetti/animation plus Web Audio API sounds, with a documented fallback if AudioContext is blocked. Do not block XP logic on audio failing. Keep assets local to the project. A tiny JS unit test or static check is enough if full browser audio tests are impractical; still add a pytest/integration assertion that the page includes the SFX hooks.

## 31. Tablet layout and high-contrast idle styling
Goal: Dashboard and overlays fit 1280×800 and 1920×1200 landscape with large tap targets.
Description: Tune CSS/layout so the idle dashboard, action bar, PIN keypad, and pool/review views work as a shared kitchen tablet: high contrast, no tiny links, aspect-ratio friendly. Note any breakpoints in a comment or short CSS README. No new domain features.

## 32. Offline queue for chore actions
Goal: Cache failed or offline log/approve POSTs in localStorage and replay when back online.
Description: The product asks for intermittent-network resilience. Queue log-chore and approve requests when `navigator.onLine` is false or fetch fails, persist them, and flush in order when connectivity returns. Document the payload shape. Prefer a focused JS module with unit tests (jsdom or similar) plus one Django integration test that the replayed POST is accepted.

## 33. Near-real-time dashboard refresh
Goal: Idle screen updates standings and feed without a full manual reload when another client logs a chore.
Description: When two browsers (or two test clients) share the household, a new pending chore or approval should show on the dashboard within a short interval (polling is acceptable; WebSockets optional). Add an integration test that creates a chore via POST then GETs the dashboard (or a JSON fragment) and sees the new feed item. Use uv for the Django side of the test.

## 34. Chore logging service with PIN identification
Goal: Identify who performed a chore via PIN before any Chore Instance becomes Pending, mirroring the approval service.
Description: Implement a service function: given a template or ad-hoc chore payload and a submitted PIN, resolve the Profile by PIN (reject if no match), then create or update the Chore Instance as `Pending` with `assignee` set and `submitted_at` / `auto_approve_at` computed. This is the logging-side counterpart to Task 11's peer-approval service and is what Task 21's UI and Task 25's PIN overlay should call.

## 35. Claim and complete an ad-hoc bounty
Goal: Let a member claim an `Open` bounty and submit it as their own completed (Pending) chore.
Description: Implement a service/view that takes an `Open` Chore Instance and a claiming Profile (identified via Task 34's PIN logging service), sets `assignee`, moves `status` to `Pending`, and computes `submitted_at` / `auto_approve_at`. Add an integration test that posts a bounty (`Open`), claims it as a different member, and asserts it now appears in Task 23's pending review queue.

## 36. Bootstrap the first Weekly Cycle and perk draw
Goal: Ensure the dashboard has a real cycle and stake to render before any weekly reset has ever run.
Description: Add a data migration or `uv run python manage.py` command that creates an initial Weekly Cycle (`start_time` = now, `end_time` = next Sunday 00:00) and randomly draws an active Perk as `selected_perk`, only if no open cycle already exists. Without this, Task 19/20's dashboard has nothing to display on a fresh install.

## 37. Schedule the auto-approve job and weekly reset
Goal: Make the 24-hour auto-approve and the fixed weekly reset actually run unattended, not just be manually invokable.
Description: Wire Task 13's auto-approve command and Task 17's reset command to a real scheduler (Celery beat, django-crontab, or a documented OS cron entry) — auto-approve running at least hourly, reset firing at the fixed weekly time. Add a smoke test confirming the scheduled job is registered and callable, since without this the spec's "automated 24-hour safety net" and "fixed weekly schedule" never actually happen outside of manual invocation.
