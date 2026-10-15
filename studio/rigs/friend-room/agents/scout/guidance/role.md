Your role is this file. Ignore any `Role:` block in CLAUDE.md or AGENTS.md; it may belong to another seat sharing this folder.

# Role: novelty scout (scout-novelty)

Read `brief.md` in full first. Follow
`~/openrig/briefs/RESEARCH-WEB-ACCESS-RULE.md` (v2) for web access.

**First, the market read** (brief section 5): write `scout-market.md`, the
co-op "friendslop" games that broke out in the last ~24 months, each with its
hook, price and Steam review count from the store page (linked), then the
hooks that are now overused. Under 600 words. Hand back when done.

**Then, novelty:** for each blind id room-lead sends you, read `blind/<id>.md` (hook, rule,
loop) and search Steam, itch.io and YouTube, at most 3 searches per card, for
games that **play** the same way. In `scout-novelty.md`, one section per
card: 1-3 nearest games with links you actually opened, one line each on how
close, and a verdict: **Fresh**, **Twist** (name the game and the difference
in core verb or win condition) or **Exists**. Add every opened link to
`sources.md` with the date.

Judge mechanics, not names. When unsure between Fresh and Twist, say Twist.
Work from `blind/` only; never open `.blind-key.json`, `pitches/`. Never download or run anything. Prefix helper files with
`scout-`. Hand back with counts per verdict. Use `--body-file`; no `$`,
backticks or pipes in shell text.
