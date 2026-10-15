# Architecture: [game title]

> Tech lead. Two pages at most. Devs and the reviewer read it before every task.

## Hard requirements from the design
[each one with the design doc it comes from and whether the owner accepted its price, e.g. "rewind works on a
long crossing (feel.md): snapshot rewind; exact replay not required"]

## Engineering cost of constraints (owner rule, 2026-10-15)
| Constraint | Rough effort | Forecloses | Cheap alternative | Owner decision |
|---|---|---|---|---|
| | | | [or "can't estimate"] | |

## Modules
| Module | Folder | Does | Owner seat for now |
|---|---|---|---|
| | | | |

## Rules every task follows
- Simulation: [tick, what rules may read, what is display only]
- Data: values via `Data.value(file, key)`; text via `Text.t(id)`
- Steam: only through `Platform`
- Tests: where they go; state hashing only for constraints the owner chose with their price

## Decisions
[one line each, dated, with why]
