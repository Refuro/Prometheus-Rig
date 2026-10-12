# Research web access rule (v2, 2026-10-11)

Applies to every research and validation seat. Replaces v1 ("never route around blocks; built-in tools only"). Where a brief says otherwise, this file wins.

## Goal
Get the evidence a verdict needs from public pages, using the lightest tool that works, without putting the user's accounts at risk or defeating a site's protections.

## Tiers: try them in order and stop at the first that works
1. **Built-in web search and page reading.** This is the default for everything.
2. **Official access.** A platform's own API, RSS feed or public data export, if one exists and credentials have been provided. Never create keys or accounts yourself.
3. **Exa (search and page contents).** Use it when tier 1 returns a block (403, captcha, login wall, empty render) or can't find the page. Exa returns indexed public text. Treat it as a copy of the page, and note in the log that the text may be older than the live page.
4. **Browser tool, logged out, human pace.** Use this only when tiers 1–3 failed AND the page decides a verdict (an earnings figure, order or sales count, policy text, price). Open the page as a normal visitor and read what's shown. Wait at least 10 seconds between page loads on the same site.

## Never
- **Logged-in access.** Never sign in, reuse cookies, or open pages while authenticated to any account, especially the user's. Platforms punish the account, not the page.
- **Defeating protections.** No CAPTCHA solving, proxy or IP rotation, fake user agents or browser fingerprints, stealth plugins, or paid unblocking or scraping services. If a page shows a CAPTCHA or a "verify you're human" check in the browser, stop and log it as blocked.
- **Bulk collection.** At most 40 pages per site per run through tiers 3–4 combined. No crawling categories, search result pages beyond the first 2, or whole shops. Sample what the verdict needs.
- **Private data.** Collect business and earnings facts only, not personal details about individuals beyond what a public business page shows.
- **Anything beyond reading.** No posting, messaging, sign-ups, purchases, form submissions or reviews.

## Logging (required)
Every page reached through tiers 2–4 gets one line in `<run>/access-log.csv`:
`date_utc,seat,tier,url,why_needed,result(ok|blocked|captcha|stale),niche_id`

Evidence from tiers 3–4 is labeled in source files as `via-exa` or `via-browser`. Each checkpoint report includes:
- a count of pages by tier;
- the verdicts that rest mainly on tier 3–4 evidence;
- every still-blocked page that would have decided a verdict. The user can open these by hand and add them to `<run>/user-verified.md`. Facts there count as opened evidence.

## When unsure
If a step isn't clearly allowed here, don't do it. Log it and ask in the checkpoint report.
