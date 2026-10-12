# Rig Console roadmap

## Done
- Niche board: funnel (peaks, targets), ranked niche cards with IDs and evidence badges, checkpoint picker
- Live graph: team cards, plain-English actions + timers, activity strips, merged handoff lines (animated only
  while the receiver is busy; parked handoffs drawn faint), pan/zoom/fit, drag, hover cards, screen viewer,
  message an agent, copy attach command, context meters
- Live activity feed, handoff sparks, pickup/finish rings, file pops (graph page)
- Replay: play any team's recorded history at 30–600x, scrub, skip quiet stretches (graph page)
- Phone view (m.html), installable app; decision gates for any job (decide.html); playable builds (play.html)
- Event store: SQLite at ~/.local/share/rig-console/console.db (store.py), backfilled from the activity log and queue
- Alerts with dismiss, desktop notifications, ntfy push; health strip; run report (timeline, usage, evidence,
  approvals, decisions, cross-run table); auto-start service; Tailscale access with token

## Next
1. Web footprint chips on agent cards (from each run's access-log.csv: built-in / Exa / browser).
2. Validation view: sent → replies → samples → paid, red banner on auto-stop.
2b. Approve / deny buttons for agent permission prompts (show exact command, confirm, log).
3. TV mode (full screen, larger text, optional soft sound on handoffs).
4. Mini funnel on each team box.

## Architecture: when to grow up
Now (done or due):
- SQLite for history (events). One file, no server, lives in Ubuntu's filesystem, not OneDrive.
- Numbered schema migrations in store.py (PRAGMA user_version). Never edit an old step.
- Put the project under git and commit after each working change.

Triggers for the next steps, not dates:
- serve.py passes ~1,000 lines, or two people/agents edit it → split into api/, collectors/, store/.
- Pages share more than a couple of components, or a page passes ~1,000 lines → move the frontend to
  Vite + TypeScript with shared components (still served as static files).
- A bug ships twice in the same area → add tests for that area (pytest for parsers and the collector first).
- More than one machine writes data, or real customers' data arrives (validation run) → Postgres, or keep
  customer data out of the console entirely and only store counts.
- The console must work while your PC is off → host the collector and DB on a small server.
