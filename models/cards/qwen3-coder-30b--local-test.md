# qwen3-coder:30b · local test (Ollama, num_ctx 16384)

**Brief:** `model-test/tasks.json` (3 synthetic tasks, 2026-10-11). Never ran in a seat.
**Seen once:** 3 prompts, 1 run each. **Confidence:** very low.

## What happened
- **JSON extract:** pass in 29.1 s, but the `example` field merged several reviews (the schema didn't forbid it). [O057]
- **Skeptic (free text):** concrete and short; no pass grade was recorded.
- **Tool-call JSON:** pass, 0.9 s.

Speed depends on hardware. The comparison with gemma4:12b is in `cards/gemma4-12b--local-test.md`.

## Next step
Same as gemma4:12b: one real low-stakes role behind a reviewer, with a no-spend rule, before any seat use.
