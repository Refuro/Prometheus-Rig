// "Since you last looked" (owner, 2026-10-14): what changed since you last tapped Seen, in this browser.
// window.rcSince(el) fills a container: new decisions and to-dos (linked), handoffs done, approval waits and
// the busiest teams, from /api/since. The first visit only starts the clock. Shared by the Now bar (nav.js)
// and the phone page (m.html). Names come from the console's own data and are escaped.
(() => {
  const SEEN_KEY = "rc.seenAt";
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const ago = s => s < 5400 ? `${Math.max(1, Math.round(s / 60))} min` : s < 172800 ? `${Math.round(s / 3600)} h` : `${Math.round(s / 86400)} days`;
  window.rcSince = async (box) => {
    if (!box) return;
    let at = 0;
    try { at = Number(localStorage.getItem(SEEN_KEY)) || 0; } catch {}
    const now = Date.now() / 1000;
    if (!at) { try { localStorage.setItem(SEEN_KEY, String(now)); } catch {} box.hidden = true; return; }
    let d;
    try { d = await (await fetch(`/api/since?ts=${Math.floor(at)}`, {cache: "no-store"})).json(); } catch { return; }
    if (!d || d.error) return;
    const bits = [];
    if (d.decisions_new_n) bits.push(`<a href="${esc(d.decisions_new[0].url)}">${d.decisions_new_n} new decision${d.decisions_new_n > 1 ? "s" : ""}</a>`);
    if (d.cards_new_n) bits.push(`<a href="/needs.html">${d.cards_new_n} new to-do${d.cards_new_n > 1 ? "s" : ""}</a>`);
    const n = (k, word) => `${k} ${word}${k === 1 ? "" : "s"}`;
    if (d.handoffs_done) bits.push(`${n(d.handoffs_done, "handoff")} done`);
    if (d.approval_waits) bits.push(n(d.approval_waits, "approval wait"));
    if ((d.busiest || []).length) bits.push(`busiest: ${d.busiest.map(t => esc(t.rig)).join(", ")}`);
    bits.push(`<a href="/digest.html">Today's digest</a>`);
    box.innerHTML = `<span class="lbl">SINCE ${esc(ago(now - at).toUpperCase())} AGO</span><span class="rcbits">${bits.length ? bits.join(" · ") : "nothing new"}</span>
      <button type="button" class="rcseen">Seen</button>`;
    box.hidden = false;
    box.querySelector(".rcseen").onclick = () => { try { localStorage.setItem(SEEN_KEY, String(Date.now() / 1000)); } catch {} box.hidden = true; };
  };
  // Today's digest headline (R-026), one line linking to the digest page. The phone page shows it.
  window.rcToday = async (box) => {
    if (!box) return;
    try {
      const d = await (await fetch("/api/digest", {cache: "no-store"})).json();
      if (!d || d.error || !d.headline) return;
      box.innerHTML = `<a href="/digest.html"><span class="lbl">TODAY</span> ${esc(d.headline)} →</a>`;
      box.hidden = false;
    } catch {}
  };
})();
