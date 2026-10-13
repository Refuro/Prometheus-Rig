// Small, safe Markdown renderer for agent-written files (PL-002 reader; shared by decide.html and job.html, PL-034).
// It escapes everything first, so no raw HTML from agents ever reaches the page. Links to other files in the job
// come out as <a class="fref" data-f="path">; the page decides what to do with them.
const mdEsc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function mdInline(t){
  return t
    .replace(/`([^`]+)`/g, (_, c) => /^[\w~./-]+\.(md|json|csv|txt|ya?ml)$/i.test(c) ? `<a class="fref" data-f="${c}">${c}</a>` : `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/(^|[^*\w])\*([^*\n]+)\*(?=[^*\w]|$)/g, "$1<i>$2</i>")
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, txt, href) => /^https?:/i.test(href)
      ? `<a href="${href}" target="_blank" rel="noopener noreferrer">${txt}</a>` : `<a class="fref" data-f="${href}">${txt}</a>`)
    .replace(/(^|\s)(https?:\/\/[^\s<]+[^\s<.,;:)])/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
}
function md(src){
  const lines = mdEsc(String(src || "")).replace(/\r/g, "").split("\n"), out = [];
  let i = 0;
  const isTable = k => /^\s*\|.*\|\s*$/.test(lines[k] || "") && /^\s*\|[\s:|-]+\|\s*$/.test(lines[k + 1] || "");
  while (i < lines.length){
    const ln = lines[i];
    if (/^\s*```/.test(ln)){ const buf = []; i++; while (i < lines.length && !/^\s*```/.test(lines[i])) buf.push(lines[i++]); i++; out.push(`<pre>${buf.join("\n")}</pre>`); continue; }
    const h = /^(#{1,6})\s+(.*)$/.exec(ln);
    if (h){ const n = Math.min(6, h[1].length + 1); out.push(`<h${n}>${mdInline(h[2])}</h${n}>`); i++; continue; }
    if (/^\s*([-*_])\s*\1\s*\1[\s\1]*$/.test(ln)){ out.push("<hr>"); i++; continue; }
    if (isTable(i)){
      const row = s => s.trim().replace(/^\||\|$/g, "").split("|").map(c => mdInline(c.trim()));
      const head = row(lines[i]); i += 2; const body = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) body.push(row(lines[i++]));
      out.push(`<div class="tbl"><table><thead><tr>${head.map(c => `<th>${c}</th>`).join("")}</tr></thead><tbody>${body.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }
    if (/^\s*&gt;\s?/.test(ln)){ const buf = []; while (i < lines.length && /^\s*&gt;\s?/.test(lines[i])) buf.push(lines[i++].replace(/^\s*&gt;\s?/, "")); out.push(`<blockquote>${md_unesc(buf.join("\n"))}</blockquote>`); continue; }
    const li = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(ln);
    if (li){
      const ordered = /\d/.test(li[2]), items = [];
      while (i < lines.length){
        const m = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(lines[i]);
        if (m){ items.push({ind: m[1].length, t: m[3]}); i++; }
        else if (lines[i].trim() && /^\s{2,}/.test(lines[i]) && items.length){ items[items.length - 1].t += " " + lines[i].trim(); i++; }
        else break;
      }
      const base = items[0].ind;
      out.push(`<${ordered ? "ol" : "ul"}>${items.map(it => `<li${it.ind > base ? ' class="sub"' : ""}>${mdInline(it.t)}</li>`).join("")}</${ordered ? "ol" : "ul"}>`);
      continue;
    }
    if (!ln.trim()){ i++; continue; }
    const buf = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,6}\s|\s*```|\s*([-*+]|\d+[.)])\s|\s*&gt;)/.test(lines[i]) && !isTable(i)) buf.push(lines[i++].trim());
    out.push(`<p>${mdInline(buf.join(" "))}</p>`);
  }
  return out.join("\n");
}
// Blockquotes are re-parsed from already-escaped text: unescape once so it isn't escaped twice.
function md_unesc(s){ return md(s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&")); }
