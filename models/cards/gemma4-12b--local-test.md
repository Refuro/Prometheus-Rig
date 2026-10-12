# gemma4:12b · local test (Ollama, num_ctx 16384)

**Brief:** `model-test/tasks.json` (3 synthetic tasks, 2026-10-11). Never ran in a seat.
**Seen once:** 3 prompts, 1 run each. **Confidence:** very low.

| Task | gemma4:12b | qwen3-coder:30b |
|---|---|---|
| JSON extract | pass, 64.0 s | pass, 29.1 s, but `example` merged several reviews |
| Skeptic (free text) | concrete; one test says "Run $100 of highly targeted Meta ads" (no spending rule in the prompt) | concrete, shorter; no pass grade recorded |
| Tool-call JSON | pass, 1.6 s | pass, 0.9 s |

[O056, O057]

## Read
Both produce valid JSON on easy prompts; speed also depends on hardware. qwen's merged example wasn't forbidden by the schema (`example: string`). Neither has been seen with tools, a queue or a long session.

## Next step
Before any seat use, run one real low-stakes role (for example the checker or receipt writer) behind a Claude or Codex reviewer, with an explicit no-spend rule.
