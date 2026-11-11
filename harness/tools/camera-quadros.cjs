#!/usr/bin/env node
// Quadros da entrada de beats do tour, para conferir câmera e desmontagem (sessão de câmera).
// Uso: node harness/tools/camera-quadros.cjs --beats a2.1,a2.11 [--fracs 0,0.25,0.5,0.75,1] [--cut completo] [--no-build]
// Saída: harness/dist/camera/<beat>_<frac>.png (1920 x 1080). frac 1 = fim da entrada; 1.5 = meio da leitura.
const fs = require('fs');
const path = require('path');
const { garanteBuild, serve, DIST } = require('./smoke.cjs');
const args = process.argv.slice(2);
const arg = (k, d = null) => (args.includes(`--${k}`) ? args[args.indexOf(`--${k}`) + 1] : d);
(async () => {
  if (!args.includes('--no-build')) garanteBuild();
  const ids = (arg('beats') ?? '').split(',').filter(Boolean);
  const fracs = (arg('fracs') ?? '0,0.33,0.66,1').split(',').map(Number);
  const cut = arg('cut', 'completo');
  const out = path.join(DIST, 'camera'); fs.mkdirSync(out, { recursive: true });
  const { chromium } = require('playwright');
  const { srv, url } = await serve(DIST);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    page.on('pageerror', (e) => console.log('erro:', e.message));
    await page.goto(`${url}?capture=1&cut=${cut}&acumula=0${arg('q') ? '&qualidade=' + arg('q') : ''}`);
    await page.waitForFunction('window.__tour && window.__tour.duration > 0 || window.__tourErro', null, { timeout: 120000 });
    await page.evaluate('window.__tour.ready');
    const beats = await page.evaluate('window.__tour.beats');
    for (const id of ids) {
      const b = beats.find((x) => x.id === id);
      if (!b) { console.log(`beat ${id} fora do corte`); continue; }
      for (const f of fracs) {
        const t = f <= 1 ? b.start + (b.entrada - b.start) * f : b.entrada + (b.end - b.entrada) * (f - 1);
        await page.evaluate((tt) => window.__tour.seek(tt), t);
        await page.waitForTimeout(150);
        const nome = `${id}_${String(f).replace('.', '')}.png`;
        await page.screenshot({ path: path.join(out, nome) });
        console.log(nome, `t=${t.toFixed(2)}`);
      }
    }
  } finally { await browser.close(); srv.close(); }
})().catch((e) => { console.error(e); process.exit(2); });
