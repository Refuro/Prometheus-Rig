// Capture screenshots of a web build: the splash, then each stage via debug keys 1-9.
// Usage: node tools/shots.cjs <url> <outdir> <stages>
// Needs the playwright package on NODE_PATH and its Chromium (see studio/setup/install-shots-wsl.sh).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [url, outdir, stagesArg] = process.argv.slice(2);
  const stages = Math.max(1, Math.min(9, parseInt(stagesArg || '1', 10)));
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({
    args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const logs = [];
  page.on('console', (m) => logs.push(m.text()));
  page.on('pageerror', (e) => logs.push('PAGEERROR ' + e.message));
  await page.goto(url);
  for (let i = 0; i < 40 && !logs.some((l) => l.includes('PROTO_READY')); i++) await page.waitForTimeout(500);
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(outdir, '00-splash.png') });
  await page.mouse.click(640, 360); // closes the splash and focuses the canvas
  await page.waitForTimeout(1800);
  await page.screenshot({ path: path.join(outdir, 'stage-1.png') });
  for (let s = 2; s <= stages; s++) {
    await page.keyboard.press(String(s));
    await page.waitForTimeout(1800);
    await page.screenshot({ path: path.join(outdir, `stage-${s}.png`) });
  }
  fs.writeFileSync(path.join(outdir, 'console.log'), logs.join('\n'));
  await browser.close();
  const ready = logs.some((l) => l.includes('PROTO_READY'));
  const errors = logs.filter((l) => /SCRIPT ERROR|PAGEERROR|Parse Error/.test(l));
  console.log(`shots: ${stages + 1} images, ready=${ready}, errors=${errors.length}`);
  process.exit(ready && errors.length === 0 ? 0 : 1);
})().catch((e) => { console.error('shots failed: ' + e.message); process.exit(2); });
