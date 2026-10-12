# Research brief: niche discovery, run 2

> **Template note (2026-10-12):** this is the current research template. Every run also follows
> `briefs/SHARED-RULES.md`. Before reusing it, do section 0.

## 0. Answerability check (before dispatch)
For every question the funnel must answer (screen gates, deep-dive bar, verdicts), the lead writes one
line in `ops/answerability.md`: **can public evidence answer this?** Say yes, partly or no, and give the
kind of source that would. Anything marked "no" (for example settled payments, buyer counts, conversion)
moves out of the research bar into a **market test** recommendation for the checkpoint report. The lead
shows this file at the dry run. Don't start the longlist while a gate depends on a "no" question.

## 1. Mission
Find niches where a solo builder working with AI agents can fill a real gap
profitably. This run produces a ranked longlist, a screened top 8, and up to
three shortlisted niches with evidence, so I can choose one to validate with
real buyers. Zero finalists is an acceptable result; never pad the shortlist.

Calibrate for speed. An agent team builds software in days to weeks, so do not
rule out a niche because the product seems large. Finding buyers, earning
trust, payments and support still move at human pace: judge niches hardest
on those.

Run 1 found nothing (see research/run-1/summary.md). Its two lessons drive
this brief: weak niches looked strong on one or two threads, and both deep
dives died on general-purpose tools that industry-specific searches missed.
Those checks now happen at the screen, not the deep dive.

## 2. No personal interests
Ignore my interests entirely. Do not organize search by industry, and do not
favor any industry, hobby or community. The only question is where the
evidence is strongest. Run 1's brief listed interests as tiebreakers and the
team built whole search lanes around them; that is the bias this run removes.

To keep the search broad:
- Search by method (section 6), not by industry.
- At most 3 longlist niches from any one industry or community.
- Any business model a solo builder plus agents can run counts: software,
  automation services, data or reports, templates or digital products.
- Out of scope for this run (a separate team covers them): content and
  creator income (YouTube, TikTok, newsletters), affiliate sites, and other
  "make money online with AI" models.

## 3. What makes a niche good
The economics must work: reachable buyers x price x margin reaches the target.
**Target:** $5,000/month profit within 12 months of launch.

Score each criterion 1-5, then multiply by its weight. Maximum 55 at the
screen. Economics is a pass/fail check at the screen (an obviously
impossible path to the target fails) and is scored 1-5, weight 2, only in
the deep dive, once there is real data: its numbers are too guess-heavy to
move rankings earlier.

| Criterion | Weight | What a 5 looks like |
|---|---|---|
| Proof of spending | 3 | Buyers already pay for a tool, a workaround, a freelancer or staff time to solve it |
| Gap | 3 | The best existing option, including general-purpose tools, clearly fails a named need |
| Pain | 2 | Many buyers describe it in their own words, with frustration |
| Reachability | 2 | We can name where buyers gather and reach them without a sales team |
| Economics | deep dive only | The buyers x price x margin math plausibly reaches the target |
| Buildability | 1 | An agent team could ship a working MVP within about 2 weeks |

Ties: higher Proof of spending wins, then higher Gap.

A niche with no competitors at all is a warning sign: it usually means nobody
pays. Count it as a gap only with other proof of spending.

Judge the buyer's problem separately from any one product idea. Rejecting
"a $149 add-on" is not the same as rejecting the problem; say which one the
evidence rules out.

Economics: keep the parts separate and label each one's strength: total
buyers, buyers we could actually reach, price (from comparable products) and
the conversion assumption. Don't collapse guesses into one confident number.

## 4. Hard no's
A niche is out if it:
- Is heavily regulated, or needs a license or permit costing more than $100.
- Requires my personal likeness (face, voice, personal brand) to sell.
- Needs more than $1,000 upfront before the first sale.
- Involves physical products, inventory or hardware.
- Is a two-sided marketplace that needs both sides at once.
- Sells only to large enterprises with long sales cycles.
- Holds other people's money, or sensitive health or financial data.
- Depends on one platform's approval to exist (an app-store or marketplace
  review we cannot route around).
- Repeats a run 1 niche (research/run-1/niches.json), unless there is new
  evidence run 1 did not have. Say what is new.

## 5. Evidence rules
- Every factual claim links to a page the citing agent actually opened. No
  search-snippet claims. This applies to the skeptic too.
- Quote buyers' complaints in their own words, with links.
- **Independent post:** a distinct author in a distinct thread. Count all
  posts, and separately count recent ones (within the last 24 months).
- Take competitor prices from their own pricing pages, with the date checked.
- Label every estimate and show the math. Secondary sources for buyer counts
  are acceptable if labeled; give a range, not a single number.
- Mark each conclusion **found** (stated in a source) or **inferred**.
- Never invent numbers, quotes, companies or links.
- Reddit: only threads that appear in web search results. Do not scrape it.
- Web access follows briefs/RESEARCH-WEB-ACCESS-RULE.md (v2): built-in tools first, then
  official access, Exa, and a logged-out browser at human pace for verdict-deciding pages.
  Never log in, solve CAPTCHAs, rotate proxies or bulk-scrape. Log every fallback page.
- Do not add requirements this brief doesn't state (for example a country,
  company size or recency cutoff). If you think one is needed, flag it at the
  checkpoint instead of applying it.

## 6. How the team works
- **Lead + synthesizer (Claude):** owns the funnel, merges and scores, writes
  the notes, keeps niches.json current. Keep messages short; Claude usage is
  the scarce budget.
- **Analyst A (Codex), complaints first:** start from buyers' own words:
  reviews of existing tools (G2, Capterra, app stores), forums, Hacker News,
  Reddit via search, support communities. Find needs people say are unmet.
- **Analyst B (Codex), spending first:** start from where money already
  goes: job postings for manual work, freelancer gigs (Upwork, Fiverr),
  paid templates and add-ons, tools with price complaints, abandoned or
  acquired products. Find spending with no good product behind it.
- **Skeptic (Claude):** tries to kill every screened niche. For each one:
  name the closest general-purpose substitute (spreadsheets, Airtable, Notion,
  Zapier, Jotform, Calendly, OptimoRoute and similar) and its price, the
  strongest incumbent, and why buyers haven't switched. Cite opened pages only.
  Every objection also states **what evidence would overturn it**. Finding a
  competitor is not proof the buyer's exact workflow is served: check the
  competitor's documented limits before calling the gap closed.
- **Rebuttal round:** before any niche is closed after the screen, the lead
  answers the skeptic's objection in writing (one short paragraph), and the
  analysts look for the overturning evidence the skeptic named.

Every verdict uses exactly one of:
- **Contradicted:** evidence shows buyers' needs are already met, or they
  won't pay.
- **Insufficient evidence:** we couldn't find enough either way. Not a
  rejection; say what's missing.
- **Worth a small test:** promising, and the cheapest validation test is named.
- **Shortlist:** meets the deep-dive bar.

Funnel:
1. **Longlist:** exactly 25 niches (13 from A, 12 from B), duplicates merged,
   at most 3 per industry. One line on the gap and at least one link each.
2. **Screen to 8.** To pass, a niche needs all of:
   - an Economics sanity pass;
   - at least 5 independent buyer posts, at least 3 of them recent;
   - the closest general-purpose substitute named, with its price;
   - no hard no.
3. **Skeptic pass on the 8:** one line each, the strongest objection.
4. **Checkpoint 1:** report to me and wait.
5. **Deep dive** the niches I choose. To reach the shortlist a niche needs at
   least 10 independent buyer posts (at least 5 recent), a buyer-count range,
   and to survive the skeptic.
6. **Checkpoint 2:** report every deep-dived niche with its verdict
   category and the shortlist (0 to 3), then wait.

## 7. Deliverables
All in ~/openrig/research/run-2/:
- `niches.json`: kept current per briefs/NICHES-SCHEMA.md, including the
  `funnel` field with the peak count each stage reached.
- `longlist.md`: all 25 with weighted score, verdict and reason, and one link.
- `shortlist/<id>.md`: per finalist: buyer, the problem in buyers' words
  with links, post counts (all and recent), competitors and the closest
  general-purpose substitute with prices, the gap, scores, the economics
  math, the skeptic's strongest objection and the answer, and the cheapest
  test that would validate it.
- `summary.md`: ranked recommendation in under 300 words, plus questions.
- `sources.md`: every link used, with the date it was accessed.
- `retro.md`: phase times, every wait or send-back and why, the bottleneck,
  unclear rules, and what to change for run 3.

## 8. Operations
- Before dispatch, the operator sets the team's permissions so these run
  without prompts: `rig queue` commands for every seat, and the lead's own
  validation and update scripts inside ~/openrig. Lifecycle commands (rig up,
  rig down, seat stop) still ask.
- Launch run 2 as a new team with fresh agent sessions. Don't reuse run 1's
  seats: their conversations are hundreds of thousands of tokens long and
  burn usage on every turn. Keep agents' context lean: write findings to
  files and read back only what's needed.
- Each seat prefixes its helper files with its name (pain-, market-,
  skeptic-, lead-) so no two seats write the same file.
- The lead parks its goal row on the rows it dispatches, so stuck-sweeps
  don't flag it.
- Before dispatch, run one small dry run of the whole working path (claim,
  web read, save a file, run the lead's validator, hand back) and confirm no
  step stops for approval. Fix any that do, then dispatch.
- The operator does not monitor the run; it acts only when messaged.

## 9. Limits and stop rules
- Never: spend money, create accounts, sign up for anything, post publicly,
  or contact people.
- Stop and wait at both checkpoints.
- Longlist and screen happen in one working session. If the work can't
  finish within it, stop and report what's missing.
- If usage limit warnings appear, stop, save progress and report.
- If agents disagree and can't resolve it in two exchanges, write both
  positions down and let me decide.
