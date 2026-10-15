# Critic check (experiment E2)

A one-off measurement for the Model Architect (`models/EXPERIMENTS.md`, E2; owner-approved
2026-10-14 with a budget of two critic sessions). A Claude critic and a Codex critic re-judge depth-1's
24 blind cards. Both use the same anchored role (`agents/critic/guidance/role.md`) and the same rubric,
fixed before scoring (`rubric.md`). The Studio Architect dispatches, records and runs
`tools/compare.py`. No gate, no lead seat, no other seats.

## When
After Bridge work, never alongside it. The earliest slot is while bridge-prod waits at an owner gate
(the m2a depth gate), at a time the operator picks. Each seat has a 45-minute limit (`brief.md`).

## Before launch: the answer key (MA-035 K1)
The key gives R1-R6 for each of the 24 cards, each with its quoted line (format in `tools/compare.py`).
The Model Architect drafts it from depth-1's blind cards, then the Studio Architect and `review-codex`
check it. It's frozen (sha256 recorded in `run-record.md`) before launch. The Studio Architect keeps it
outside the job folder; no file in this kit names where, because the seats can
read this folder. No launch until the key is frozen.

## Seats (exactly two)
| Seat | Runtime | Model | Record |
|---|---|---|---|
| `critics-claude@e2-critics` | claude-code | the operator's default Claude model | the exact model id in the launch record |
| `critics-codex@e2-critics` | codex | `gpt-6.1-sol` | the exact model id in the launch record |

## Launch (Ubuntu, operator)

    cp -r ~/openrig/studio/rigs/critic-check ~/openrig/jobs/e2-critics
    mkdir -p ~/openrig/jobs/e2-critics/blind ~/openrig/jobs/e2-critics/out/claude ~/openrig/jobs/e2-critics/out/codex
    cp ~/openrig/jobs/depth-1/blind/x-*.md ~/openrig/jobs/e2-critics/blind/
    cd ~/openrig/jobs/e2-critics
    rig spec validate rig.yaml
    rig up ./rig.yaml --cwd .

Copy only `blind/x-*.md`, never `.blind-key.json` or depth-1's critic notes. Pre-approve for both
seats: `rig queue` commands, reads in the job folder, and writes in that seat's own `out/<seat>/`
folder. Then tell `arch-studio@architects` the seats are up, with the launch record. The Studio
Architect sends both start messages at the same moment, and records start and end times, stops and
prompts in `run-record.md`.

## After
`python3 tools/compare.py . --key <the key file>` writes `results.md`.
Before trusting it, the Studio Architect checks both seats' transcripts for any read of the key,
`depth-1` or the other critic's folder, and notes in `run-record.md` whether either critic hit the
45-minute limit. With no lead seat, the Studio Architect acts as lead
for run closure (shared rules section 6): it writes `model-notes.jsonl` and `model-metrics.csv` (one row
per critic) in the job folder, then sends `results.md` to the Model Architect and names both files.
Then the operator brings the rig down and keeps the folder.
