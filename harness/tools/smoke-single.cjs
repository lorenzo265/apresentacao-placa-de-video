#!/usr/bin/env node
// Teste do arquivo único (harness/dist/tour.html): abre por file://, sem rede,
// e percorre todos os beats com a seta do teclado, como no seminário.
// Uso: node harness/tools/smoke-single.cjs [--cut completo|seminario] [--tema keynote|estudio|blueprint] [--no-build]
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { pathToFileURL } = require('url');

const HARNESS = path.resolve(__dirname, '..');
const ARQ = path.join(HARNESS, 'dist', 'tour.html');

async function main() {
  const args = process.argv.slice(2);
  const corte = args.includes('--cut') ? args[args.indexOf('--cut') + 1] : null;
  const tema = args.includes('--tema') ? args[args.indexOf('--tema') + 1] : null;
  const FRAMES = path.join(HARNESS, 'dist', tema ? `frames-single-${tema}` : 'frames-single');
  if (!args.includes('--no-build')) execSync('npm run build:single', { cwd: path.join(HARNESS, 'viewer'), stdio: 'inherit' });
  const textos = JSON.parse(fs.readFileSync(path.join(HARNESS, 'content', 'pt-BR', 'beats.json'), 'utf8')).beats;
  fs.mkdirSync(FRAMES, { recursive: true });

  const { chromium } = require('playwright');
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 768 }, deviceScaleFactor: 1 });
  await ctx.setOffline(true);
  const page = await ctx.newPage();
  const falhas = [];
  const pedidos = [];
  page.on('console', (m) => { if (m.type() === 'error') falhas.push(`console: ${m.text()}`); });
  page.on('pageerror', (e) => falhas.push(`pageerror: ${e.message}`));
  page.on('request', (r) => { const u = r.url(); if (!u.startsWith('data:') && !u.startsWith('blob:')) pedidos.push(u); });

  const q = [corte && `cut=${corte}`, tema && `tema=${tema}`].filter(Boolean).join('&');
  const url = pathToFileURL(ARQ).href + (q ? `?${q}` : '');
  await page.goto(url);
  await page.waitForFunction('window.__tourReady === true || window.__tourErro', null, { timeout: 60000 });
  const erro = await page.evaluate('window.__tourErro');
  if (erro) throw new Error(`o arquivo único não iniciou: ${erro}`);

  const info = await page.evaluate(() => ({ beats: window.__tour.beats.map((b) => b.id), cut: window.__tour.cut, duration: window.__tour.duration }));
  console.log(`smoke-single: corte ${info.cut}, ${info.beats.length} beats, ${(info.duration / 60).toFixed(1)} min, ${(fs.statSync(ARQ).size / 1048576).toFixed(2)} MB`);

  const extras = pedidos.filter((u) => u !== url);
  if (extras.length) falhas.push(`a página pediu arquivos de fora: ${extras.join(', ')}`);
  const fontes = await page.evaluate(async () => { await document.fonts.ready; return [document.fonts.check('600 28px Inter'), document.fonts.check('500 20px "JetBrains Mono"')]; });
  if (!fontes[0] || !fontes[1]) falhas.push(`fontes embutidas não carregaram (Inter ${fontes[0]}, JetBrains Mono ${fontes[1]})`);

  // Se o build embutiu o GLB, ele tem de carregar e as peças têm de responder pelo id do assembly.
  const temGlb = /window\.__TOUR_GLB__=/.test(fs.readFileSync(ARQ, 'utf8'));
  if (temGlb) {
    const c = await page.evaluate(() => ({ glb: window.__cena.glb, avisos: window.__cena.avisos, pecas: ['gpu.package', 'pcb.main', 'cooler.fan.1', 'io.bracket'].filter((n) => !window.__cena.temAncora(n)) }));
    if (!c.glb) falhas.push(`o GLB embutido não carregou: ${c.avisos.join('; ')}`);
    if (c.pecas.length) falhas.push(`peças do assembly não achadas no GLB: ${c.pecas.join(', ')}`);
    console.log(`smoke-single: GLB embutido ${c.glb ? 'carregado' : 'NÃO carregado'}`);
  }
  if (tema) {
    const aplicado = await page.evaluate(() => document.documentElement.dataset.tema ?? null);
    if (aplicado !== tema) falhas.push(`o tema pedido (${tema}) não foi aplicado (${aplicado})`);
  }
  const titulo = () => page.evaluate(() => document.querySelector('#caixa h2')?.textContent ?? '');
  for (let i = 0; i < info.beats.length; i++) {
    const id = info.beats[i];
    if (i > 0) {
      // A seta tem de pôr o tour a caminho deste beat; o resto do trajeto é pulado para o teste não depender do relógio.
      await page.keyboard.press('ArrowRight');
      const andando = await page.evaluate(() => window.__tour.playing());
      if (!andando) falhas.push(`${id}: a seta para a direita não iniciou a transição`);
    }
    await page.evaluate((x) => { const b = window.__tour.beats.find((k) => k.id === x); window.__tour.seek(b.settle); }, id);
    const atual = await page.evaluate(() => window.__tour.beatAtual().id);
    if (atual !== id) falhas.push(`${id}: o beat ativo é ${atual}`);
    const h = await titulo();
    if (!textos[id]) falhas.push(`${id}: sem texto`);
    else if (h !== textos[id].headline) falhas.push(`${id}: título na tela "${h}" difere de "${textos[id].headline}"`);
    if (i % 6 === 0 || i === info.beats.length - 1) await page.screenshot({ path: path.join(FRAMES, `${id}.png`) });
  }
  await page.keyboard.press('n');
  const notas = await page.evaluate(() => !document.getElementById('notas').hidden && document.querySelector('#notas .fala').textContent.length > 20);
  if (!notas) falhas.push('o painel de notas (tecla N) não abriu com a fala');
  await page.screenshot({ path: path.join(FRAMES, 'notas.png') });

  await browser.close();
  if (falhas.length) { falhas.forEach((f) => console.log(`  FALHA ${f}`)); console.log(`smoke-single: ${falhas.length} falha(s)`); process.exit(1); }
  console.log('smoke-single: ok (file://, sem rede, todos os beats pela seta, notas)');
}
main().catch((e) => { console.error(e); process.exit(1); });
