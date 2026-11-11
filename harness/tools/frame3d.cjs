#!/usr/bin/env node
// Um quadro da cena 3D (sem o tour), para o diretor de storyboard enquadrar a câmera.
// Uso: node harness/tools/frame3d.cjs --pos x,y,z --target x,y,z [--fov 30] [--explode assembled|E1..E8]
//        [--part <id>] [--anchor <anchor.id> [--box right-center]] [--out nome] [--no-build]
// Saída: harness/dist/frames3d/<nome>.png (1920 x 1080) e, no console, a posição da âncora na tela.
const fs = require('fs');
const path = require('path');
const { garanteBuild, serve, HARNESS, DIST } = require('./smoke.cjs');

const args = process.argv.slice(2);
const arg = (k, def = null) => (args.includes(`--${k}`) ? args[args.indexOf(`--${k}`) + 1] : def);
const vec = (k) => {
  const v = (arg(k) ?? '').split(',').map(Number);
  if (v.length !== 3 || v.some(Number.isNaN)) { console.error(`uso: --${k} x,y,z (mm, referencial CAD)`); process.exit(2); }
  return v;
};

(async () => {
  const pos = vec('pos'), target = vec('target');
  const fov = Number(arg('fov', 30));
  const explode = arg('explode', 'assembled');
  if (!/^(assembled|E[1-8])$/.test(explode)) { console.error('--explode: assembled ou E1 a E8'); process.exit(2); }
  const part = arg('part'), anchor = arg('anchor'), box = arg('box', 'right-center');
  if (!args.includes('--no-build')) garanteBuild();
  const nome = arg('out') ?? `${explode}${part ? '_' + part : ''}_${Date.now() % 100000}`;
  const { chromium } = require('playwright');
  const { srv, url } = await serve(DIST);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    const erros = [];
    page.on('pageerror', (e) => erros.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') erros.push(m.text()); });
    await page.goto(`${url}?capture=1&frame3d=1`);
    await page.waitForFunction('window.__tourReady === true || window.__tourErro', null, { timeout: 60000 });
    const e0 = await page.evaluate('window.__tourErro');
    if (e0) throw new Error(e0);
    const r = await page.evaluate((o) => window.__frame3d(o), { pos, target, fov, explode, part, anchor, box });
    if (!r.glb) console.log('aviso: GLB não carregou; é o marcador de blockout');
    if (part && !r.peca) console.log(`aviso: peça ${part} não existe no GLB`);
    const dir = path.join(HARNESS, 'dist', 'frames3d');
    fs.mkdirSync(dir, { recursive: true });
    const png = path.join(dir, `${nome}.png`);
    await page.screenshot({ path: png });
    console.log(`quadro: ${png}`);
    if (r.erroAncora) console.log(`ERRO: ${r.erroAncora}`);
    else if (anchor) {
      console.log(`âncora ${anchor}: tela [${r.ancora.map((x) => x.toFixed(1)).join(', ')}] ${r.dentro ? 'DENTRO' : 'FORA'} do quadro; caixa [${r.caixa.map(Math.round)}] ${r.cobre ? 'COBRE a âncora' : 'não cobre a âncora'}`);
    }
    if (erros.length) console.log(`erros no console: ${erros.join(' | ')}`);
    if (r.erroAncora || (anchor && (!r.dentro || r.cobre))) process.exitCode = 1;
  } finally { await browser.close(); srv.close(); }
})().catch((e) => { console.error(e); process.exit(2); });
