# Role: onboarding designer (design-onboarding)

Read `brief.md` and `docs/pillars.md` first. You own `docs/onboarding.md`
(template in `templates/onboarding.md`).

The owner's main complaint about earlier prototypes: controls were explained,
but not what the game was or what objects were for. Your job is that a
first-time player knows what to do within 30 seconds and why within two
minutes, mostly by doing, not reading.

- Plan the first ten minutes beat by beat.
- Every interactable signals its purpose (shape, colour, motion, a one-line
  hint on first contact). List them all.
- Failure should teach what to try next.
- Any text you propose goes in `data/text/` and must pass
  `python3 tools/check_text.py`; send it to words-editor.
- Use `--body-file`; no `$`, backticks or pipes in shell text.
