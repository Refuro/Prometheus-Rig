// Screenshot a production web build (dev tools on): waits for GAME_READY, then for each shot in
// shots.json calls window.godotShot(name), waits for SHOT_READY <name>, and captures <name>.png.
// Usage: node tools/shots.cjs <url> <outdir> <shots.json>
// Needs the playwright package on NODE_PATH and its Chromium (studio/setup/install-shots-wsl.sh).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [url, outdir, listFile] = process.argv.slice(2);
  const list = JSON.parse(fs.readFileSync(listFile, 'utf8')).shots || [];
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({
    args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const logs = [];
  page.on('console', (m) => logs.push(m.text()));
  page.on('pageerror', (e) => logs.push('PAGEERROR ' + e.message));
  await page.goto(url);
  for (let i = 0; i < 60 && !logs.some((l) => l.includes('GAME_READY')); i++) await page.waitForTimeout(500);
  const ready = logs.some((l) => l.includes('GAME_READY'));
  const missing = [];
  if (ready) {
    for (const shot of list) {
      const mark = 'SHOT_READY ' + shot.name;
      await page.evaluate((n) => window.godotShot && window.godotShot(n), shot.name);
      let got = false;
      for (let i = 0; i < 40; i++) {
        if (logs.some((l) => l.includes(mark))) { got = true; break; }
        if (logs.some((l) => l.includes('SHOT_MISSING ' + shot.name))) break;
        await page.waitForTimeout(250);
      }
      if (!got) { missing.push(shot.name); continue; }
      await page.waitForTimeout(shot.wait_ms || 800);
      await page.screenshot({ path: path.join(outdir, shot.name + '.png') });
    }
  }
  fs.writeFileSync(path.join(outdir, 'console.log'), logs.join('\n'));
  await browser.close();
  const errors = logs.filter((l) => /SCRIPT ERROR|PAGEERROR|Parse Error/.test(l));
  console.log(`shots: ${list.length - missing.length}/${list.length} captured, ready=${ready}, errors=${errors.length}` +
    (missing.length ? `, not registered or never ready: ${missing.join(', ')}` : ''));
  process.exit(ready && errors.length === 0 && missing.length === 0 ? 0 : 1);
})().catch((e) => { console.error('shots failed: ' + e.message); process.exit(2); });
