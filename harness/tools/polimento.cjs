#!/usr/bin/env node
// Capturas do polimento do tour (acumulação de quadros, caminhos na placa, mergulho para o chip).
// Uso: node harness/tools/polimento.cjs [--quadros a0.2@settle,t1.1@0.5] [--cut seminario] [--qualidade media]
//        [--extra "acumula=0"] [--sufixo antes] [--out harness/dist/polimento] [--no-build]
// Cada item é <beat>@<instante>: "settle" (fim da chamada), "s+N" (N segundos depois do settle), "fim" (fim
// do beat) ou uma fração da entrada (0 = início do beat, 1 = fim da entrada). Grava <out>/<beat>-<instante>[-<sufixo>].png e imprime o
// tempo de cada seek (o desenho é síncrono, então o tempo inclui a acumulação de quadros).
const fs = require('fs');
const path = require('path');
const { garanteBuild, serve, abre, HARNESS, DIST } = require('./smoke.cjs');

const args = process.argv.slice(2);
const arg = (k, def) => (args.includes(k) ? args[args.indexOf(k) + 1] : def);
const PADRAO = 'a0.2@settle,a1.3@settle,a2.9@settle,a2.10@settle,a2.11@settle,t1.1@0.2,t1.1@0.5,t1.1@0.8';

(async () => {
  const itens = arg('--quadros', PADRAO).split(',').map((s) => { const [id, q] = s.split('@'); return { id, q: q ?? 'settle' }; });
  const corte = arg('--cut', 'seminario');
  const out = path.resolve(arg('--out', path.join(HARNESS, 'dist', 'polimento')));
  const sufixo = arg('--sufixo', '');
  const extra = arg('--extra', '');
  const qualidade = arg('--qualidade', '');
  fs.mkdirSync(out, { recursive: true });
  if (!args.includes('--no-build')) garanteBuild();
  const { chromium } = require('playwright');
  const { srv, url } = await serve(DIST);
  const s = await abre(chromium, url, `cut=${corte}&tema=keynote${qualidade ? `&qualidade=${qualidade}` : ''}${extra ? `&${extra}` : ''}`);
  try {
    const beats = await s.page.evaluate(() => window.__tour.beats);
    for (const { id, q } of itens) {
      const e = beats.find((b) => b.id === id);
      if (!e) { console.log(`  ${id}: não está no corte ${corte}`); continue; }
      // settle, fim, s+N (N segundos depois do settle) ou fração da entrada
      const t = q === 'settle' ? e.settle : q === 'fim' ? e.end : q.startsWith('s+') ? e.settle + Number(q.slice(2))
        : e.start + ((e.entrada ?? e.settle - 0.8) - e.start) * Number(q);
      const ms = await s.page.evaluate((x) => { const t0 = performance.now(); window.__tour.seek(x); return performance.now() - t0; }, t);
      const nome = `${id}-${q}${sufixo ? `-${sufixo}` : ''}.png`;
      await s.page.screenshot({ path: path.join(out, nome), timeout: 600000 });
      console.log(`  ${nome}: t=${t.toFixed(2)} s, seek ${ms.toFixed(0)} ms`);
    }
    if (s.erros.length) console.log(`erros no console: ${s.erros.join(' | ')}`);
  } finally { await s.browser.close(); srv.close(); }
})().catch((e) => { console.error(e); process.exit(1); });
