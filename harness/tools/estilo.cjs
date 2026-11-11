#!/usr/bin/env node
// Capturas das direções de estilo (?tema=...) para o autor escolher olhando imagens.
// Uso: node harness/tools/estilo.cjs [--temas keynote,estudio,blueprint] [--beats a0.2,a2.9] [--cut seminario] [--no-build]
//      node harness/tools/estilo.cjs --perf [--beats a2.9,a5.9]   (só mede quadros por segundo ao vivo)
//      node harness/tools/estilo.cjs --perf --qualidades baixa,media,alta   (Keynote realista por nível de qualidade)
// Grava harness/dist/estilo/<tema>/<beat>.png (1920 x 1080), uma folha de contato por tema
// (harness/dist/estilo/folha-<tema>.png) e a comparação lado a lado (harness/dist/estilo/comparacao.png),
// com o visual atual (sem tema) na primeira coluna. Também mede o tempo de desenho por quadro.
const fs = require('fs');
const path = require('path');
const { garanteBuild, serve, abre, HARNESS, DIST } = require('./smoke.cjs');

const OUT = path.join(HARNESS, 'dist', 'estilo');
const NOMES = { atual: 'Atual (sem tema)', keynote: 'A. Keynote', estudio: 'B. Estúdio de produto', blueprint: 'C. Blueprint técnico' };
const ROTULO_BEAT = { 'a0.2': 'placa montada', 'a2.9': 'caminho da energia', 't1.1': 'placa para chip', 'a5.5': 'interior do SM', 'a5.9': 'CUDA, PTX, SASS', 'a6.1': 'tabela de páginas' };

const arg = (k, def) => { const a = process.argv.slice(2); return a.includes(k) ? a[a.indexOf(k) + 1] : def; };

/** Quadros por segundo ao vivo (laço do GSAP ligado), tocando a entrada de cada beat. */
async function perf(chromium, url, temas, beats, corte) {
  const linhas = [];
  // cada tema também com ?leve=1 (sem os efeitos caros)
  const qs = arg('--qualidades', null);
  const lista = qs ? ['atual', ...qs.split(',').map((q) => `keynote@${q}`)] : ['atual', ...temas.flatMap((t) => [t, `${t}+leve`])];
  for (const tema of lista) {
    const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    const [nomeQ, leve] = tema.split('+');
    const [nome, q] = nomeQ.split('@');
    await page.goto(`${url}?cut=${corte}${tema === 'atual' ? '' : `&tema=${nome}`}${leve ? '&leve=1' : ''}${q ? `&qualidade=${q}` : ''}`);
    await page.waitForFunction('window.__tourReady === true', null, { timeout: 60000 });
    const r = { tema };
    for (const id of beats) {
      r[id] = await page.evaluate(async (id) => {
        const b = window.__tour.beats.find((x) => x.id === id);
        const roda = (ms) => new Promise((ok) => { const t0 = performance.now(); const f = () => (performance.now() - t0 < ms ? requestAnimationFrame(f) : ok()); requestAnimationFrame(f); });
        window.__tour.seek(b.start); window.__tour.play();
        await roda(1500);                                  // aquecimento: shaders e camadas
        window.__tour.seek(b.start); window.__tour.play();
        let n = 0; const t0 = performance.now();
        await new Promise((ok) => { const f = () => { n++; if (performance.now() - t0 < 4000) requestAnimationFrame(f); else ok(); }; requestAnimationFrame(f); });
        window.__tour.pause();
        return n / ((performance.now() - t0) / 1000);
      }, id);
    }
    linhas.push(r);
    await browser.close();
  }
  console.log('quadros por segundo ao vivo (SwiftShader, CPU, 1920 x 1080; só vale a comparação entre colunas):');
  console.log(['tema', ...beats].map((x) => x.padEnd(16)).join(''));
  for (const r of linhas) console.log([r.tema, ...beats.map((b) => r[b].toFixed(1))].map((x) => String(x).padEnd(16)).join(''));
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, qs ? 'perf-qualidade.json' : 'perf.json'), JSON.stringify(linhas, null, 1));
}

async function main() {
  const temas = arg('--temas', 'keynote,estudio,blueprint').split(',');
  const beats = arg('--beats', 'a0.2,a2.9,t1.1,a5.5,a5.9,a6.1').split(',');
  const corte = arg('--cut', 'seminario');
  if (!process.argv.includes('--no-build')) garanteBuild();
  const { chromium } = require('playwright');
  const { srv, url } = await serve(DIST);
  if (process.argv.includes('--perf')) {
    try { await perf(chromium, url, temas, arg('--beats', 'a0.2,a2.9,a5.5,a5.9').split(','), corte); } finally { srv.close(); }
    return;
  }
  const tempos = {};
  try {
    for (const tema of ['atual', ...temas]) {
      const dir = path.join(OUT, tema);
      fs.mkdirSync(dir, { recursive: true });
      const s = await abre(chromium, url, `cut=${corte}${tema === 'atual' ? '' : `&tema=${tema}`}`);
      try {
        const lista = await s.page.evaluate(() => window.__tour.beats);
        tempos[tema] = {};
        for (const id of beats) {
          const e = lista.find((b) => b.id === id);
          if (!e) { console.log(`  ${tema}: beat ${id} não está no corte ${corte}`); continue; }
          await s.page.evaluate((t) => window.__tour.seek(t), e.settle + 0.35);
          await s.page.screenshot({ path: path.join(dir, `${id}.png`) });
          // tempo de desenho: 12 seeks em instantes diferentes da entrada e do hold (síncronos)
          tempos[tema][id] = await s.page.evaluate((b) => {
            const ts = Array.from({ length: 12 }, (_, i) => b.start + (b.settle + 1 - b.start) * (i / 11));
            window.__tour.seek(ts[0]);
            const t0 = performance.now();
            for (const t of ts) window.__tour.seek(t);
            return (performance.now() - t0) / ts.length;
          }, e);
        }
        if (s.erros.length) console.log(`  ${tema}: erros no console: ${s.erros.join(' | ')}`);
      } finally { await s.browser.close(); }
      console.log(`estilo: ${tema} ok`);
    }

    // folhas de contato (montadas numa página e fotografadas)
    const browser = await chromium.launch();
    const img = (tema, id) => {
      const p = path.join(OUT, tema, `${id}.png`);
      return fs.existsSync(p) ? `data:image/png;base64,${fs.readFileSync(p).toString('base64')}` : '';
    };
    const css = `body{margin:0;background:#111;color:#e8e8e8;font:500 22px Inter,system-ui,sans-serif}
      h1{margin:0;padding:22px 28px 14px;font-size:30px;font-weight:700} .g{display:grid;gap:10px;padding:0 28px 28px}
      figure{margin:0} img{display:block;width:100%} figcaption{padding:6px 2px 0;color:#aaa;font-size:18px}
      .cab{color:#ddd;font-weight:700;font-size:22px;padding:4px 2px} .lado{color:#bbb;font-size:18px;writing-mode:vertical-rl;transform:rotate(180deg);text-align:center}`;
    for (const tema of temas) {
      const page = await browser.newPage({ viewport: { width: 1980, height: 800 } });
      await page.setContent(`<style>${css}</style><h1>${NOMES[tema] ?? tema}</h1><div class="g" style="grid-template-columns:1fr 1fr">${
        beats.map((id) => `<figure><img src="${img(tema, id)}"><figcaption>${id} &middot; ${ROTULO_BEAT[id] ?? ''}</figcaption></figure>`).join('')}</div>`);
      await page.screenshot({ path: path.join(OUT, `folha-${tema}.png`), fullPage: true });
      await page.close();
    }
    const cols = ['atual', ...temas];
    const page = await browser.newPage({ viewport: { width: 60 + cols.length * 640, height: 800 } });
    await page.setContent(`<style>${css}</style><h1>Comparação: mesmo beat por linha</h1>
      <div class="g" style="grid-template-columns:28px repeat(${cols.length},1fr)"><div></div>${cols.map((t) => `<div class="cab">${NOMES[t] ?? t}</div>`).join('')}
      ${beats.map((id) => `<div class="lado">${id} &middot; ${ROTULO_BEAT[id] ?? ''}</div>${cols.map((t) => `<figure><img src="${img(t, id)}"></figure>`).join('')}`).join('')}</div>`);
    await page.screenshot({ path: path.join(OUT, 'comparacao.png'), fullPage: true });
    await browser.close();
  } finally { srv.close(); }

  console.log('\ntempo médio de desenho por quadro (ms, SwiftShader, sem GPU; vale como comparação relativa):');
  console.log(['tema', ...beats].map((x) => x.padEnd(10)).join(''));
  for (const [tema, t] of Object.entries(tempos)) console.log([tema, ...beats.map((b) => (t[b] ?? NaN).toFixed(1))].map((x) => String(x).padEnd(10)).join(''));
  fs.writeFileSync(path.join(OUT, 'tempos.json'), JSON.stringify(tempos, null, 1));
  console.log(`\nestilo: ${path.relative(process.cwd(), OUT)}`);
}
main().catch((e) => { console.error(e); process.exit(1); });
