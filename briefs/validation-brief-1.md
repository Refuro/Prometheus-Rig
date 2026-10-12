# Validation run 1 — brief

**Status:** approved by the user to start Phase 0. Offer confirmed by run 2 checkpoint 2: A07. The postal address (a PO box) is still pending; it is required before any real email is sent (Phase 2), not before.
**Output folder:** `research/validation-1/`
**Offer:** A07, Word multilevel numbering and template repair (done-for-you service), starting price about $150 per sanitized template. B05 was cut at run 2 checkpoint 2.

## 1. Mission
Find out whether a small agent team can take a researched offer to real paying interest with almost no human work: name it, build its web presence, find prospects, email them, answer replies, deliver free samples and report results.

This tests two things, and the final report must judge them separately:
1. **The offer:** do real buyers want it enough to reply, send a sample, or pay?
2. **The pipeline:** can agents run outreach and delivery well enough to trust them unattended?

A clean "no" on either is a valid result. Do not inflate numbers or reframe a failed test as a success.

## 2. Hard rules (never break these; stop and ask if unsure)
**Law and honesty**
- US recipients only. Business contacts only: published work addresses of businesses or organizations (a contact page, a staff page, a role address like office@). No consumers, no private individuals, no purchased or scraped-in-bulk lists, no guessed personal addresses.
- Every cold email follows CAN-SPAM: the brand name and the user's real postal address in the footer (from `config`; never invent one), honest From line and subject, and a working one-line unsubscribe. Honor opt-outs immediately and add them to `do-not-contact.csv`, which is checked before every send.
- Send as the brand. No invented human personas, fake names or fake titles. If anyone asks whether they're talking to a person or an AI, answer truthfully: "Messages are written with AI assistance and overseen by the owner."
- No fake testimonials, client counts, reviews, guarantees the team can't deliver, or claims of credentials the brand doesn't have.
- Email and the brand's own website only. No automated posting or messaging on LinkedIn, Reddit, Facebook, Upwork, Fiverr or any other platform. Reading public pages follows briefs/RESEARCH-WEB-ACCESS-RULE.md (v2); that rule covers reading only, never sending or posting.

**Money and accounts**
- $0 agent spending. Agents never create accounts, sign up for services, enter payment details, or start free trials. The user creates every account and hands over scoped access.
- Payments only through a Stripe payment link the user creates. Agents never see card data or Stripe secret keys.

**Credentials and files**
- Credentials live only in `~/.config/validation-1/` (mode 600). Never print them, write them to logs, commit them, or paste them into messages.
- Customer files go only in `research/validation-1/delivery/<case-id>/`. They are never shared, never used for anything else, and deleted 30 days after delivery. Ask prospects to send a non-confidential or sanitized document.

**Escalate to the user instead of acting** on: a legal threat or complaint, a request for a call or meeting, a request for anything outside the offer, a refund request, any reply the team is unsure how to answer, and any outreach step a rule here doesn't clearly allow.

## 3. Team (lean; seats idle unless triggered)
| Seat | Runtime | Job |
|---|---|---|
| Lead | Claude | Offer design, launch plan, phase gates, weekly report, final verdict draft. Owns `validation.json`. |
| Ops | Codex | DNS and email authentication, landing page deploy, sending and inbox scripts, warm-up, auto-stops, delivery tooling. |
| Prospector | Codex | Builds prospect lists from public business sources, with a source URL and date for every contact. |
| Writer | Claude | Landing page copy, cold emails, follow-ups, reply drafts and sample-delivery notes. |
| Skeptic | Claude, fresh session at each gate only | Reviews the plan, the first batch and the verdict. Checks rule compliance, claims and the numbers. |

**Daily rhythm:** a scheduled kickoff (a WSL cron running `rig send` to the lead at 9:00 PT) starts each working day. The lead runs that day's work (warm-up, sends, reply handling, delivery) and parks the seats idle. There is no polling and no always-on chatter.

## 4. Phases and gates

### Phase 0: plan (target 1 day) → USER GATE
**Step 1: evidence review (lead + skeptic, before any planning).** Re-read run 2's A07 material: `research/run-2/pain-deepdive-A07.md`, `lead-verdicts.md`, `skeptic-objections.md`, `lead-rebuttals.md` and the A07 sources. Re-open the key pages under web access rule v2: the Upwork $125 job, the Freelancer awards, the $250–750 budgets. Write `plan/evidence-review.md`:
- which claims hold up, which don't, and what changed since the run;
- what the evidence says about who buys, what they ask for, the price they pay, and the competition (10–36 bidders per post);
- anything that should change the offer, the price or the target segments.
If the review undercuts the offer (e.g. the key jobs can't be confirmed, or prices are far below $150), stop and report before planning further.

Deliverables in `research/validation-1/plan/`:
- **offer.md:** what exactly is fixed, what's excluded, turnaround and price. Default: a paid fix at about $150 per sanitized template, with a free sample (e.g. one section fixed) only as a fallback if prospects hesitate. Anchor on the evidence review (Upwork $125 with 2 hires, Freelancer CAD 90 award, $250–750 budgets). Give a price range with reasoning. Plan for outbound to firms that never post jobs, rather than competing with the 10–36 bidders on job boards.
- **names.md:** 5–8 brand name options, each with domain availability (checked via public lookup) and a USPTO trademark search result (opened page, dated). Recommend one.
- **audience.md:** 2–3 target segments (e.g. small law firms, consultancies, admin-heavy offices), why, where their public business contacts come from, and an estimated reachable count.
- **sequence.md:** a first email plus up to 2 follow-ups, spaced 3–5 business days apart, with personalization rules (what the writer may reference and what it may not).
- **landing.md:** page copy and structure: offer, how it works, sample request form or address, price, FAQ, footer with postal address and contact.
- **metrics.md:** the kill / change / keep thresholds (section 6), with any proposed changes argued.
- **Skeptic review:** `plan/skeptic.md`.
- **User gate:** the user approves the name, offer, price, segments and copy, then does the setup in section 8.

### Phase 1: build and warm up (2–3 weeks, mostly waiting)
- Ops configures DNS on the user's domain: SPF, DKIM, DMARC (start `p=none` with reports), MX as the mail host requires. Verify with a test send and a header check, and record the results in `ops/dns-check.md`.
- Ops deploys the landing page to Vercel on the brand domain, plus `/privacy` and a contact address.
- **Warm-up, with no warm-up services:** week 1 sends real, varied messages to the user's own other addresses and replies to them, 3–5 per day; weeks 2–3 add a few real low-risk sends. Keep a log in `ops/warmup.csv`.
- Prospector builds batch 1: 30 contacts in `prospects/batch-01.csv` (business, segment, contact address, source URL, date found, personalization note).
- Writer drafts batch 1 emails in `outbox/batch-01/` (one file per email). **Nothing is sent.**

### Phase 2: calibration → USER GATE
- The user reviews every batch-1 email. The lead logs each edit or rejection in `calibration.md`, with the reason, and the writer's rules are updated from them.
- After the user approves, ops sends batch 1 at no more than 10 per day.
- Every reply draft is held for user approval during this phase.
- Every free-sample fix is reviewed by the user before it goes back, for the first 5 deliveries.
- **Skeptic review of batch 1:** compliance, tone, personalization accuracy, and claims.
- **Gate:** the user decides whether to move to phase 3, repeat calibration, or stop.

### Phase 3: autonomous run
- Agents send, follow up, answer routine replies, and deliver samples without per-message approval. The user reviews a random sample daily from `daily/<date>.md` during the first week, then weekly.
- **Volume:** ramp from 10 to at most 30 cold emails per day. Cap total first-touch contacts at 300 for this run.
- **Auto-stops** (ops enforces them in the send script; on a stop, sending halts, `ops/STOP.md` explains why, and the dashboard alert fires):
  - bounce rate above 3% over the last 50 sends;
  - any spam complaint or blocklist hit;
  - any angry, legal or threatening reply;
  - unsubscribe rate above 2% over the last 100 sends;
  - an authentication failure (SPF, DKIM or DMARC) on a sent message;
  - any rule-compliance doubt the lead can't resolve.

  Only the user restarts after a stop.

### Phase 4: verdict
- The lead drafts `verdict.md`, the skeptic reviews it in a fresh session, and the lead writes a rebuttal. The user decides.
- The verdict covers:
  - offer result against the thresholds;
  - pipeline result (what the agents did well and badly, how many messages the user had to fix, and how often they stopped);
  - cost in usage and dollars;
  - the recommendation: keep, change or kill.
- `retro.md` lists what to change in the next validation run.

## 5. Delivering samples (the factory test)
- Fixes are done by script where possible (python-docx and direct OOXML edits for Word; openpyxl and Power Query guidance for Excel). Every fix gets a before/after check and a short change note.
- Never claim a fix that wasn't verified by opening the output file and checking numbering levels, styles and links.
- If a document can't be fixed safely, say so honestly and offer nothing further.
- Turnaround promise: whatever offer.md states. The default is 2 business days for samples.

## 6. Thresholds (provisional; the lead may argue changes in Phase 0)
Measured after at least 200 delivered first-touch emails:
- **Keep:** at least 3 sample requests AND at least 1 paid order or a written commitment to pay at the stated price.
- **Change:** at least 2% positive replies but no payment. Revise the price, the segment or the offer, then run one more batch.
- **Kill:** fewer than 1% positive replies, or sample requests that never convert after delivery.

Report every number with its denominator (e.g. "4 replies / 212 delivered").

## 7. Tracker for the dashboard
The lead maintains `research/validation-1/validation.json`:
```json
{
  "run": "validation-1",
  "phase": "plan|build|warmup|calibration|autonomous|verdict|stopped",
  "phase_note": "one line",
  "offer": "A07",
  "brand": "",
  "counts": {"prospects": 0, "drafted": 0, "sent": 0, "delivered": 0, "bounced": 0,
             "replies": 0, "positive": 0, "unsubscribed": 0, "samples_requested": 0,
             "samples_delivered": 0, "paid": 0, "complaints": 0},
  "stopped": false,
  "stop_reason": "",
  "waiting_on_user": ""
}
```

## 8. User setup checklist (after the Phase 0 gate)
1. Register the brand domain (Vercel) and create one mailbox on it (Zoho Mail Lite or Google Workspace, with SMTP/IMAP enabled).
2. Create a Vercel token with an expiry, limited to the team or project that hosts the landing page.
3. Put credentials in `~/.config/validation-1/` (mode 600): mailbox address and app password, SMTP/IMAP hosts and Vercel token. Add the PO box address for footers when you have it; Phase 2 can't start without it.
4. Optional, before any paid offer goes out: create a Stripe payment link, and register the trade name with Washington's Business Licensing Service before taking payments under the brand name.
5. Set up the 9:00 PT daily kickoff cron (the operator can do this).

## 9. Operations (same as run 2)
- Set permissions before dispatch, and do a dry run of the full path (DNS check, deploy, a send to the user's own address, reply parsing, an auto-stop trigger) before any real send.
- Fresh sessions at each phase; keep context lean; use file prefixes per seat.
- Pause and report on any usage warning. The operator stays idle unless asked.
- Approval prompts are logged; nothing that touches the outside world is pre-approved beyond the send and deploy scripts named in the dry run.
