#!/usr/bin/env node
// Teste do arquivo único (harness/dist/tour.html): abre por file://, sem rede,
// percorre todos os momentos com a seta do teclado, como no seminário, e exercita o índice, um extra
// e o modo Explorar (harness/plano/modos.md).
// Uso: node harness/tools/smoke-single.cjs [--cut completo|seminario] [--tema keynote|estudio|blueprint|nenhum] [--no-build]
// Sem --tema, confere que o arquivo abre no padrão de apresentação (tema Keynote).
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
  const FRAMES = path.join(HARNESS, 'dist', tema ? `frames-single-${tema}` : 'frames-single');      // sem --tema: Keynote
  if (!args.includes('--no-build')) execSync('npm run build:single', { cwd: path.join(HARNESS, 'viewer'), stdio: 'inherit' });
  const textos = JSON.parse(fs.readFileSync(path.join(HARNESS, 'content', 'pt-BR', 'beats.json'), 'utf8')).beats;
  fs.mkdirSync(FRAMES, { recursive: true });

  const { chromium } = require('playwright');
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 768 }, deviceScaleFactor: 1 });
  await ctx.setOffline(true);
  const page = await ctx.newPage();
  // Ao vivo (sem ?capture) o tour redesenha a cada quadro; com render por software (SwiftShader) um
  // quadro do tema realista passa de 1 s até a troca automática para a baixa. Limite folgado.
  page.setDefaultTimeout(180000);
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

  const deFora = pedidos.filter((u) => u !== url);
  if (deFora.length) falhas.push(`a página pediu arquivos de fora: ${deFora.join(', ')}`);
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
  // O arquivo único abre no tema Keynote por padrão (build-single.mjs); --tema nenhum pede o visual sem tema.
  {
    const esperado = tema === 'nenhum' ? null : tema ?? 'keynote';
    const aplicado = await page.evaluate(() => document.documentElement.dataset.tema ?? null);
    if (aplicado !== esperado) falhas.push(`o tema esperado (${esperado ?? 'sem tema'}) não foi aplicado (${aplicado ?? 'sem tema'})`);
    const q = await page.evaluate(() => window.__cena.qualidade?.() ?? null);
    console.log(`smoke-single: tema ${aplicado ?? 'sem tema'}${q ? `, qualidade ${q}` : ''}`);
  }
  // ---- modo Apresentação: a seta inicia a transição, a segunda seta pula para o fim dela ----
  const titulo = () => page.evaluate(() => document.querySelector('#caixa h2')?.textContent ?? '');
  const momento = () => page.evaluate(() => ({ ...window.__tour.momento(), id: window.__tour.beatAtual().id }));
  for (let i = 0; i < info.beats.length; i++) {
    const id = info.beats[i];
    if (i > 0) {
      await page.keyboard.press('ArrowRight');
      const m1 = await momento();
      if (m1.fase !== 'andando' || m1.idx !== i) falhas.push(`${id}: a seta para a direita não iniciou a transição (fase ${m1.fase}, momento ${m1.idx + 1})`);
      await page.keyboard.press('ArrowRight');      // no meio da animação: pula para o fim
    }
    const m = await momento();
    if (m.id !== id || m.idx !== i) falhas.push(`${id}: o momento ativo é ${m.id} (${m.idx + 1})`);
    if (m.fase === 'andando') falhas.push(`${id}: a segunda seta não parou no momento`);
    const h = await titulo();
    if (!textos[id]) falhas.push(`${id}: sem texto`);
    else if (h !== textos[id].headline) falhas.push(`${id}: título na tela "${h}" difere de "${textos[id].headline}"`);
    if (i % 6 === 0 || i === info.beats.length - 1) await page.screenshot({ path: path.join(FRAMES, `${id}.png`) });
  }
  // seta para a esquerda: momento anterior, já montado
  await page.keyboard.press('ArrowLeft');
  { const m = await momento(); if (m.idx !== info.beats.length - 2 || m.fase === 'andando') falhas.push(`a seta para a esquerda não voltou um momento (momento ${m.idx + 1}, fase ${m.fase})`); }

  // notas (N): fala do momento, sem lista de beats
  await page.keyboard.press('n');
  const notas = await page.evaluate(() => !document.getElementById('notas').hidden && document.querySelector('#notas .fala').textContent.length > 20);
  if (!notas) falhas.push('o painel de notas (tecla N) não abriu com a fala');
  await page.screenshot({ path: path.join(FRAMES, 'notas.png') });
  await page.keyboard.press('n');

  // índice (M): número e Enter leva ao momento; um extra abre fora do caminho e a seta volta
  await page.keyboard.press('m');
  if (await page.evaluate(() => document.getElementById('indice').hidden)) falhas.push('o índice (tecla M) não abriu');
  await page.screenshot({ path: path.join(FRAMES, 'indice.png') });
  await page.keyboard.type('3'); await page.keyboard.press('Enter');
  { const m = await momento(); if (m.idx !== 2 || !(await page.evaluate(() => document.getElementById('indice').hidden))) falhas.push(`o índice não levou ao momento 3 (momento ${m.idx + 1})`); }
  const extras = await page.evaluate(() => window.__tour.extras);
  if (extras.length) {
    await page.keyboard.press('m');
    await page.click(`#indice button[data-id="${extras[0]}"]`);
    let m = await momento();
    if (m.extra !== extras[0]) falhas.push(`o extra ${extras[0]} não abriu pelo índice (${JSON.stringify(m)})`);
    if ((await titulo()) !== textos[extras[0]]?.headline) falhas.push(`${extras[0]}: título do extra difere do de beats.json`);
    await page.keyboard.press('ArrowRight');
    m = await momento();
    if (m.extra || m.idx !== 2) falhas.push(`a seta não voltou do extra ao momento 3 (${JSON.stringify(m)})`);
  }

  // ---- modo Explorar (só com GLB): entra, remove a camada 4 (as da frente saem antes), clica numa peça, volta ----
  if (temGlb) {
    const ex = () => page.evaluate(() => window.__explorar.estado());
    await page.keyboard.press('e');
    if (!(await ex()).ativo) falhas.push('a tecla E não abriu o modo Explorar');
    await page.click('#explorar .ex-camadas button[data-k="4"]');
    const sel = await page.evaluate(() => document.querySelector('#explorar .ex-painel h2')?.textContent);
    if (!sel) falhas.push('a camada 4 não abriu a explicação');
    if (!(await page.evaluate(() => document.querySelector('#explorar .ex-painel .selo')))) falhas.push('a explicação da camada 4 não tem selo de procedência');
    await page.click('#explorar .ex-painel button[data-a="remover"]');
    await page.waitForFunction(() => { const e = window.__explorar.estado(); return e.alvo === 4 && e.nivel === 4; }, null, { timeout: 170000 });
    const fora = await page.evaluate(() => [...document.querySelectorAll('#explorar .ex-camadas button.fora')].map((b) => b.dataset.k).join(','));
    if (fora !== '1,2,3,4') falhas.push(`remover a camada 4 deveria deixar 1 a 4 fora (ficou ${fora})`);
    // clique na placa: o centro do PCB projetado tem de selecionar uma peça, com selo e ressalva ou texto
    const xy = await page.evaluate(() => {
      const c = window.__cena.caixa('pcb.main'); if (!c) return null;
      const p = window.__explorar.projeta([(c.min[0] + c.max[0]) / 2, (c.min[1] + c.max[1]) / 2, c.min[2]]);
      const r = document.querySelector('#cena3d canvas').getBoundingClientRect();
      return p && [r.left + p[0] * r.width / 1920, r.top + p[1] * r.height / 1080];
    });
    if (!xy) falhas.push('não consegui projetar o PCB para o clique');
    else {
      await page.mouse.click(xy[0], xy[1]);
      const e = await ex();
      if (e.sel?.tipo !== 'peca') falhas.push(`o clique na placa não selecionou uma peça (${JSON.stringify(e.sel)})`);
      else console.log(`smoke-single: clique na placa selecionou ${e.sel.id}`);
      if (!(await page.evaluate(() => document.querySelector('#explorar .ex-painel .selo')))) falhas.push('a peça clicada não mostra selo de procedência');
    }
    await page.screenshot({ path: path.join(FRAMES, 'explorar.png') });
    await page.click('#explorar .ex-camadas button[data-k="4"]');
    await page.click('#explorar .ex-painel button[data-a="recolocar"]');
    if ((await ex()).alvo !== 3) falhas.push('recolocar a camada 4 não levou o estado para as camadas 1 a 3 fora');
    await page.keyboard.press('Escape');
    const m = await momento();
    if ((await ex()).ativo || m.idx !== 2 || m.suspenso) falhas.push(`Esc não devolveu a apresentação ao momento 3 (${JSON.stringify(m)})`);
    if ((await titulo()) !== textos[info.beats[2]].headline) falhas.push('depois do modo Explorar o título do momento não voltou');
  }

  await browser.close();
  if (falhas.length) { falhas.forEach((f) => console.log(`  FALHA ${f}`)); console.log(`smoke-single: ${falhas.length} falha(s)`); process.exit(1); }
  console.log('smoke-single: ok (file://, sem rede, todos os momentos pela seta, notas, índice, extra, modo Explorar)');
}
main().catch((e) => { console.error(e); process.exit(1); });
