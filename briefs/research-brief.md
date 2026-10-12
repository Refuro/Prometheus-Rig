## 1. Mission
Find niches where a solo builder working with AI agents can fill a real gap
profitably. This run produces a ranked longlist and three shortlisted niches,
with evidence, so I can choose one niche to validate with real buyers.

Calibrate for speed. A full team of AI agents will prototype and build, so
software that a traditional team would need months for can take us days to
weeks. Do not rule out a niche because the product seems large to build.
Do not assume speed elsewhere: finding buyers, earning trust, payments,
support, and waiting for real-world results move at human pace. Judge niches
mainly on those.

## 2. What makes a niche good
The economics must work: number of reachable buyers x price x margin has to
reach the target below. A high-price product needs few customers; a low-price
product needs volume. Judge every niche on that math, not on size alone.

**Target:** $5,000/month profit within 12 months of launch

Score each niche 1-5 on these, in priority order:
1. **Proof of spending:** buyers already pay for something to solve this: a
   competitor, a workaround tool, a freelancer, or paid staff time.
2. **Gap:** existing options leave a clear opening: too expensive, built for a
   different customer, missing a key feature, poor reviews, or abandoned.
3. **Pain:** buyers describe the problem in their own words, often and with
   frustration.
4. **Reachability:** we can name where these buyers gather (forums,
   subreddits, Discords, associations, marketplaces) and reach them without a
   sales team.
5. **Buildability:** an agent team could ship a working MVP within about 2
   weeks. Score down only for things agents can't speed up: needing
   approval from a platform or partner, hard-to-get data, or integrations that
   require a business relationship.
6. **Economics:** the buyers x price x margin math plausibly reaches the target.

A niche with no competitors at all is a warning sign, not a win: it usually
means no one pays for this. Treat it as a gap only if there is other proof of
spending (workarounds, freelancers, staff time).

## 3. Hard no's
A niche is out if it:
- Is heavily regulated, or needs a license or permit costing more than $100.
- Requires my personal likeness (face, voice, personal brand) to sell.
- Needs more than $1,000 upfront before the first sale.
- Involves physical products, inventory, or hardware.
- Is a two-sided marketplace that needs both sides at once to work.
- Sells only to large enterprises with long sales cycles.
- Holds other people's money, or sensitive health or financial data.

## 4. Personal fit (tiebreakers only)
Anything goes. Interests break ties only, and never outrank the evidence.
(The owner's personal interests listed here in run 1 are kept out of the public repo;
run 2 dropped them entirely so they couldn't bias the search.)

## 5. Sources and evidence rules
- Every factual claim links to its source. No link, no claim.
- Quote buyers' complaints in their own words, with links.
- Take competitor prices from their own pricing pages, with the date checked.
- Label every estimate as an estimate and show the math.
- Mark each conclusion as **found** (directly in a source) or **inferred** (our
  reasoning).
- Prefer sources from the last 2 years.
- Never invent numbers, quotes, companies, or links.
- Good sources: app store reviews, G2/Capterra/Trustpilot reviews, Hacker
  News, niche forums, industry associations, competitor sites and changelogs,
  job postings (show what companies pay people to do by hand), Google Trends.
- Reddit: read threads that appear in web search results only. Do not scrape
  Reddit or work around its access limits.

## 6. How the team works
Four seats. Heavy reading runs on Codex (larger plan); judgment runs on Claude.
- **Lead + synthesizer (Claude):** owns the funnel, assigns work, enforces
  these rules, scores niches against section 2, and writes the notes and
  summary.
- **Analyst A, pain (Codex):** buyer complaints and unmet needs: reviews,
  forums, Hacker News, Reddit via search, job postings.
- **Analyst B, market (Codex):** competitors, pricing pages, changelogs,
  abandoned products, trends.
- **Skeptic (Claude):** argues every shortlisted niche should die: who already
  does this, why hasn't it worked, would anyone pay, how would we reach buyers.
  Runs on a different model than the analysts so they don't share blind spots.
  A niche reaches the shortlist only if it survives the skeptic.

Analysts may use sub-agents inside their own seat to research in parallel,
but report one merged result each.

Funnel:
1. **Longlist:** 25 niches, each with one line on the gap and one evidence link.
2. **Screen:** cut to 8 using the hard no's and a quick score.
3. **Checkpoint:** stop and report to me (section 9).
4. **Deep dive:** after my approval, research the top candidates, then put each
   through the skeptic.
5. **Shortlist:** 3 niches.

## 7. Deliverables
All in `~/openrig/research/run-1/`:
- `longlist.md`: a table of all 25 niches with score, verdict (kept or cut),
  the reason, and one link.
- `shortlist/<niche>.md`: one page per finalist covering the buyer, the
  problem in buyers' words (with links), at least 2 competitors with prices,
  the gap, the scores, the economics math, the skeptic's strongest objection
  and the answer to it, and the cheapest test that would validate it.
- `summary.md`: a ranked recommendation in under 300 words, plus open
  questions for me.
- `sources.md`: every link used, with the date it was accessed.
- `retro.md` (written by the lead at the end): start and end time of each
  phase, every handoff that waited or was sent back and why, which seat was
  the bottleneck, where rules were unclear, and what to change for run 2.

## 8. Limits and stop rules
- Never: spend money, create accounts, sign up for anything, post publicly,
  or contact people.
- Stop at the checkpoint in section 9 and wait for my approval.
- Effort cap: the longlist and screen happen in one working session. If the
  work can't finish within the cap, stop and report what's missing instead of
  pushing on.
- If usage limit warnings appear, stop, save progress, and report.
- If agents disagree and can't resolve it in two exchanges, write both
  positions down and let me decide.

## 9. My checkpoints
1. **After the screen (8 niches):** I review and pick which ones get a deep
   dive.
2. **After the shortlist:** I review the 3 finalists and pick one to validate
   with real buyers. That is a separate brief.
