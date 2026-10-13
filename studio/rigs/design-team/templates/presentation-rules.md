# Studio presentation rules

From the prototype sprint brief (v3). These were written for prototypes; in
production they become the onboarding and UI baseline.

These are principles, not a level system. A sandbox can meet them with
gradual unlocks instead of stages.

1. **One new idea at a time.** Each stage (or unlock) introduces at most one
   new rule or object, lets the player use it until it clicks, then adds the
   next. The first stage teaches only the core verb and is winnable in under
   a minute. Later stages combine ideas the player already knows. Aim for
   5-8 short stages.
2. **The goal is always visible.** The goal bar (`ui.goal`) says what to do
   right now in a few words, and the goal itself is marked in the world
   (`ui.mark`: highlight, arrow, glow). The player never has to remember
   instructions.
3. **Things look like what they are** (section 5). No letters or abbreviations
   standing in for objects. Colour means the same thing everywhere: the
   player-controlled thing is the warmest colour, danger is always red, the
   goal is always green.
4. **Text is the last resort.** Show first: animation, a ghost of the move,
   the object reacting. Words only when showing can't do it, short (budgets
   in `text-budgets.json`), and once (`ui.hint_once`). The splash is a title
   and one sentence, then play starts. No rule screens, no title-card walls.
5. **Clean screen.** Only what matters right now is on screen. HUD at the edges,
   small. Nothing flickers or moves unless it means something.
6. **Feedback for every action within a tenth of a second:** a motion, a
   colour change, a small particle or shake. Clearing a stage is celebrated;
   failing is quick, readable (the player sees what went wrong), and retry is
   instant (R).
7. **The 30-second test.** A new player can say the goal in one sentence after
   30 seconds, and why each thing on screen matters after two minutes.

