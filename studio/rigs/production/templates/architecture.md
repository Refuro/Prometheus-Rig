# Architecture: [game title]

> Tech lead. Two pages at most. Devs and the reviewer read it before every task.

## Hard requirements from the design
[each one with the design doc it comes from, e.g. "deterministic fixed-step sim (feel.md, quality-bar.md)"]

## Modules
| Module | Folder | Does | Owner seat for now |
|---|---|---|---|
| | | | |

## Rules every task follows
- Simulation: [tick, what rules may read, what is display only]
- Data: values via `Data.value(file, key)`; text via `Text.t(id)`
- Steam: only through `Platform`
- Tests: where they go, how determinism is hashed

## Decisions
[one line each, dated, with why]
