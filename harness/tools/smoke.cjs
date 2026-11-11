#!/usr/bin/env node
// Smoke test do viewer: percorre todos os beats do corte e falha se algo estiver fora do lugar.
// Uso: node harness/tools/smoke.cjs [--cut completo] [--tema keynote|estudio|blueprint] [--acumula N] [--no-build]
// --acumula N: quadros acumulados com a cena parada no tema realista (padrão 2 aqui, para o teste caber no
// tempo com render por software; o viewer usa 32 na média e 64 na alta). Com 2, o caminho da acumulação
// (deslocamento de subpixel, luz de área, mistura) é exercitado em todo beat parado e no teste de determinismo.
// Também exporta ferramentas (servidor estático, build) usadas por capture.cjs.
const fs = require('fs');
const path = require('path');
const http = require('http');
const { execSync } = require('child_process');

const HARNESS = path.resolve(__dirname, '..');
const VIEWER = path.join(HARNESS, 'viewer');
const DIST = path.join(VIEWER, 'dist');
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff', '.wasm': 'application/wasm', '.glb': 'model/gltf-binary', '.png': 'image/png' };

function maisNovo(dir, ref) {
  let novo = false;
  const anda = (d) => {
    for (const f of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, f.name);
      if (f.isDirectory()) anda(p);
      else if (fs.statSync(p).mtimeMs > ref) novo = true;
    }
  };
  anda(dir);
  return novo;
}

/** Faz o build se o dist não existir ou estiver mais velho que o código e os dados. */
function garanteBuild() {
  const idx = path.join(DIST, 'index.html');
  const ref = fs.existsSync(idx) ? fs.statSync(idx).mtimeMs : 0;
  const fontes = [path.join(VIEWER, 'src'), path.join(HARNESS, 'story'), path.join(HARNESS, 'content'), path.join(HARNESS, 'diagrams'), path.join(HARNESS, 'build')]
    .filter((d) => fs.existsSync(d));
  const mudou = !ref || fontes.some((d) => maisNovo(d, ref)) || fs.statSync(path.join(VIEWER, 'index.html')).mtimeMs > ref;
  if (mudou) {
    console.log('smoke: fazendo o build do viewer...');
    execSync('npm run build', { cwd: VIEWER, stdio: 'inherit' });
  }
}

function serve(raiz) {
  return new Promise((ok) => {
    const srv = http.createServer((req, res) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      if (p.endsWith('/')) p += 'index.html';
      const f = path.join(raiz, path.normalize(p));
      if (!f.startsWith(raiz) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); res.end('não encontrado'); return; }
      res.writeHead(200, { 'content-type': TIPOS[path.extname(f)] ?? 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => ok({ srv, url: `http://127.0.0.1:${srv.address().port}/` }));
  });
}

async function abre(chromium, url, query) {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const erros = [];
  page.on('console', (m) => { if (m.type() === 'error') erros.push(`console: ${m.text()}`); });
  page.on('pageerror', (e) => erros.push(`pageerror: ${e.message}`));
  page.on('requestfailed', (r) => erros.push(`requisição falhou: ${r.url()}`));
  const avisos = [];
  page.on('console', (m) => { if (m.type() === 'warning') avisos.push(m.text()); });
  await page.goto(`${url}?capture=1&${query}`);
  await page.waitForFunction('window.__tourReady === true || window.__tourErro', null, { timeout: 60000 });
  const erro = await page.evaluate('window.__tourErro');
  if (erro) throw new Error(`o viewer não iniciou: ${erro}`);
  return { browser, page, erros, avisos };
}

const palavras = (s) => (s.trim() ? s.trim().split(/\s+/).length : 0);
const dentro = (p, W, H) => p[0] >= 0 && p[0] <= W && p[1] >= 0 && p[1] <= H;
const inter = (a, b) => a[0] < b[0] + b[2] && b[0] < a[0] + a[2] && a[1] < b[1] + b[3] && b[1] < a[1] + a[3];

/** Cópia do dist com o storyboard de exemplo de beats 3D (e os diagramas de exemplo) no lugar dos reais. */
function montaFixture3d() {
  const site = path.join(HARNESS, 'dist', 'fixture3d-site');
  fs.rmSync(site, { recursive: true, force: true });
  fs.cpSync(DIST, site, { recursive: true });
  const ex = path.join(HARNESS, 'schemas', 'examples');
  const d = path.join(site, 'data');
  fs.copyFileSync(path.join(ex, 'fixture3d.storyboard.example.json'), path.join(d, 'storyboard.json'));
  fs.copyFileSync(path.join(ex, 'fixture3d.beats.example.json'), path.join(d, 'beats.json'));
  fs.rmSync(path.join(d, 'diagrams'), { recursive: true, force: true });
  fs.mkdirSync(path.join(d, 'diagrams'));
  const diagrams = ['diagram.example.json', 'diagram.child.example.json'];
  for (const f of diagrams) fs.copyFileSync(path.join(ex, f), path.join(d, 'diagrams', f));
  const man = JSON.parse(fs.readFileSync(path.join(d, 'manifest.json'), 'utf8'));
  man.diagrams = diagrams.map((file) => ({ file, source: 'examples' }));
  fs.writeFileSync(path.join(d, 'manifest.json'), JSON.stringify(man));
  return site;
}

async function main() {
  const args = process.argv.slice(2);
  const fixture = args.includes('--fixture3d');
  const corte = fixture ? 'fixture3d' : args.includes('--cut') ? args[args.indexOf('--cut') + 1] : 'completo';
  const tema = args.includes('--tema') ? args[args.indexOf('--tema') + 1] : null;
  const acumula = args.includes('--acumula') ? Number(args[args.indexOf('--acumula') + 1]) : 2;
  const FRAMES = path.join(HARNESS, 'dist', tema ? `frames-${tema}` : 'frames');
  if (!args.includes('--no-build')) garanteBuild();
  const { chromium } = require('playwright');
  const raiz = fixture ? montaFixture3d() : DIST;
  const { srv, url } = await serve(raiz);
  const falhas = [];
  const falha = (id, msg) => { falhas.push(`${id}: ${msg}`); console.log(`  FALHA ${id}: ${msg}`); };
  const dados = path.join(raiz, 'data');
  const textos = JSON.parse(fs.readFileSync(path.join(dados, 'beats.json'), 'utf8')).beats;
  const storyboard = JSON.parse(fs.readFileSync(path.join(dados, 'storyboard.json'), 'utf8'));
  const porId = Object.fromEntries(storyboard.beats.map((b) => [b.id, b]));
  fs.mkdirSync(FRAMES, { recursive: true });

  let sessao;
  try {
    sessao = await abre(chromium, url, `cut=${corte}${tema ? `&tema=${tema}` : ''}&acumula=${acumula}`);
    const { page, erros, avisos } = sessao;
    const info = await page.evaluate(() => ({ beats: window.__tour.beats, duration: window.__tour.duration, fps: window.__tour.fps, cut: window.__tour.cut }));
    console.log(`smoke: corte ${info.cut}${tema ? `, tema ${tema}` : ''}, ${info.beats.length} beats, ${info.duration.toFixed(1)} s, ${info.fps} fps, acumulação ${acumula}`);
    if (tema) {
      const aplicado = await page.evaluate(() => document.documentElement.dataset.tema ?? null);
      if (aplicado !== tema) falha('tema', `o tema pedido (${tema}) não foi aplicado (${aplicado})`);
    }

    for (const e of info.beats) {
      const b = porId[e.id];
      const tx = textos[e.id];
      await page.evaluate((t) => window.__tour.seek(t), e.settle);
      const pr = await page.evaluate((id) => window.__tour.probe(id), e.id);
      const est = await page.evaluate(() => {
        const c = document.querySelector('#caixa .caption');
        return { fonte: parseFloat(getComputedStyle(c).fontSize) };
      });
      await page.screenshot({ path: path.join(FRAMES, `${e.id}.png`) });
      let ok = true;
      const f = (m) => { ok = false; falha(e.id, m); };
      if (pr.erro) { f(pr.erro); continue; }
      if (!tx) f('sem texto em beats.json');
      else {
        if (pr.headline !== tx.headline) f(`headline "${pr.headline}" difere de beats.json "${tx.headline}"`);
        if (palavras(tx.headline) > 8) f(`headline com ${palavras(tx.headline)} palavras (máx. 8)`);
        if (palavras(tx.caption) > 35) f(`caption com ${palavras(tx.caption)} palavras (máx. 35)`);
        const minimo = 0.4 * palavras(tx.caption) + 2;
        if (b.hold < minimo) f(`hold ${b.hold} s menor que a regra de leitura (${minimo.toFixed(1)} s)`);
      }
      if (pr.captionOverflow) f('o texto estoura a caixa');
      if (est.fonte < 28) f(`corpo do caption com ${est.fonte}px (mín. 28)`);
      const [bx, by, bw, bh] = pr.box;
      if (bx < 0 || by < 0 || bx + bw > 1920 || by + bh > 1080) f(`caixa fora da tela [${pr.box.map(Math.round)}]`);
      if (fixture && b.level <= 1) {
        const st = await page.evaluate(() => window.__tour.estado());
        const pedido = b.explode_state === 'assembled' ? 0 : Number(b.explode_state.slice(1));
        if (st.expl !== pedido) f(`explosão no fim do beat é ${st.expl}, o pedido era ${b.explode_state} (${pedido})`);
        if (st.mix !== 0) f(`mistura 3D/diagrama deveria ser 0, é ${st.mix}`);
        if (!pr.anchor) f(`âncora 3D ${b.callout?.anchor} não resolvida`);
      }
      if (b.callout) {
        if (!pr.anchor) {
          if (b.level >= 2) f(`âncora ${b.callout.anchor} não resolvida no diagrama`);
          else console.log(`  aviso ${e.id}: âncora 3D ${b.callout.anchor} não existe na cena; sem linha`);
        } else {
          if (!dentro(pr.anchor, 1920, 1080)) f(`âncora fora da tela [${pr.anchor.map(Math.round)}]`);
          if (inter([pr.anchor[0] - 1, pr.anchor[1] - 1, 2, 2], pr.box)) f('a caixa cobre a âncora');
        }
      }
      if (b.level >= 2) {
        if (!pr.focus) f('sem retângulo de foco');
        else {
          const [x, y, w, h] = pr.focus;
          if (x < -0.5 || y < -0.5 || x + w > 1920.5 || y + h > 1080.5) f(`foco não cabe na tela [${pr.focus.map(Math.round)}]`);
          if (inter(pr.focus, pr.box)) f('a caixa cobre o foco');
        }
      }
      if (ok) console.log(`  ok ${e.id}`);
    }

    // Determinismo: mesmo instante, com um seek para outro ponto no meio, dá a mesma imagem.
    if (fixture) {
      const glb = await page.evaluate(() => window.__cena?.glb);
      if (!glb) falha('fixture3d', 'o GLB não carregou (cena em blockout)');
    }
    const alvos = new Set(fixture ? info.beats.slice(1)
      : [info.beats[0], info.beats.find((x) => porId[x.id].flows?.length), info.beats[info.beats.length - 1]].filter(Boolean));
    for (const e of alvos) {
      const tA = e.start + (e.settle - e.start) * 0.45 + 0.013;
      const tB = e.settle + 0.5;
      const tC = e.end + 0.0;
      for (const t of [tA, tB]) {
        await page.evaluate((x) => window.__tour.seek(x), t);
        const a = await page.screenshot();
        await page.evaluate((x) => window.__tour.seek(x), tC);
        await page.screenshot();
        await page.evaluate((x) => window.__tour.seek(x), t);
        const b2 = await page.screenshot();
        if (!a.equals(b2)) falha(e.id, `captura não determinística em t=${t.toFixed(3)}`);
        else console.log(`  ok determinismo ${e.id} t=${t.toFixed(2)}`);
      }
    }
    erros.forEach((m) => falha('console', m));
    [...new Set(avisos)].forEach((m) => console.log(`  aviso do viewer: ${m}`));
  } finally {
    if (sessao) await sessao.browser.close();
    srv.close();
  }
  if (falhas.length) {
    console.log(`\nsmoke: ${falhas.length} falha(s)`);
    process.exit(1);
  }
  console.log('\nsmoke: tudo certo');
}

module.exports = { garanteBuild, serve, abre, HARNESS, VIEWER, DIST };
if (require.main === module) main().catch((e) => { console.error(e); process.exit(2); });
