#!/usr/bin/env node
// Quadros do lookdev (tema Keynote realista) para comparar com as fotos da placa real.
// Uso: node harness/tools/lookdev.cjs [--beats a0.2,a1.1] [--qualidades media,alta] [--luzes neutra,fria,quente]
//                                     [--cut seminario] [--sufixo x] [--no-build] [--sem-folha] [--tempo]
//                                     [--acumula N] [--saida harness/dist/outra-pasta]
// --acumula N: amostras da acumulação de quadros (?acumula=N; menos amostras, captura mais rápida no SwiftShader).
// --saida: pasta de saída no lugar de harness/dist/lookdev.
// --tempo: mede também o tempo médio de desenho por quadro (ms; seeks síncronos, SwiftShader) e grava tempos.json.
// Grava harness/dist/lookdev/<qualidade>[-<luz>]/<beat>.png (1920 x 1080, modo de captura, no fim da
// chamada do beat), a folha harness/dist/lookdev/folha.png (beats por linha, qualidades e luzes por coluna)
// e harness/dist/lookdev/referencia.png (cada beat ao lado das referências da mesma face, tabela REFS).
// As referências são de terceiros e não são versionadas (spec/references/cache/); só entram na folha local.
const fs = require('fs');
const path = require('path');
const { garanteBuild, serve, abre, HARNESS, DIST } = require('./smoke.cjs');

const arg = (k, def) => { const a = process.argv.slice(2); return a.includes(k) ? a[a.indexOf(k) + 1] : def; };
const OUT = path.resolve(arg('--saida', path.join(HARNESS, 'dist', 'lookdev')));
const ACUMULA = arg('--acumula', null);
const BEATS_PADRAO = 'a0.2,a1.1,a1.3,a1.4,a2.4,a2.7,a3.1';
// Referência de cada beat: a mesma face da placa e um ângulo parecido (face A = ventiladores, face B =
// grades e X com "RTX PRO 6000"; ver ARCHITECTURE.md, seção 7.6). Comparar vistas de faces diferentes
// dá falso alarme de espelhamento. Render oficial para o tom, foto real para o material. Mudou a câmera
// de um beat no storyboard (lado da câmera em z), confira o par aqui.
const CACHE = path.join(HARNESS, 'spec', 'references', 'cache');
const REFS = {
  'a0.2': [['face B, foto real de frente (storagereview/sr-2)', 'storagereview/sr-2.jpg'], ['face B, render oficial (pny/back)', 'pny/back.png']],
  'a1.1': [['face A, vista da ponta oposta ao bracket (pny/3qtr-right)', 'pny/3qtr-right.png'], ['face A, foto real (storagereview/sr-5)', 'storagereview/sr-5.jpg']],
  'a1.3': [['face B, render oficial (pny/back)', 'pny/back.png'], ['face B, foto real (storagereview/sr-2)', 'storagereview/sr-2.jpg']],
  'a1.4': [['face A e borda superior, render oficial (pny/3qtr-top-right)', 'pny/3qtr-top-right.png'], ['borda superior, foto real (storagereview/sr-3)', 'storagereview/sr-3.jpg']],
  'a1.5': [['bracket e saídas, foto real (storagereview/sr-1)', 'storagereview/sr-1.jpg']],
  'a2.8': [['frente do PCB, package e memória (sabareesh/wb-bare-pcb)', 'sabareesh/wb-bare-pcb.jpg'], ['cooler da placa irmã, derived (rtx5090/wccftech-cooler-1)', 'rtx5090/wccftech-cooler-1.jpg']],
  'a3.1': [['verso do PCB, memória e cabo flat (gn/gn-29)', 'gn/gn-29.jpg'], ['frente do PCB, package e memória (sabareesh/wb-bare-pcb)', 'sabareesh/wb-bare-pcb.jpg']],
};

async function main() {
  const beats = arg('--beats', BEATS_PADRAO).split(',');
  const qualidades = arg('--qualidades', 'media').split(',');
  const luzes = arg('--luzes', 'neutra').split(',');
  const corte = arg('--cut', 'seminario');
  const sufixo = arg('--sufixo', '');
  if (!process.argv.includes('--no-build')) garanteBuild();
  const { chromium } = require('playwright');
  const { srv, url } = await serve(DIST);
  const colunas = [];
  const tempos = {};
  try {
    for (const q of qualidades) {
      for (const luz of luzes) {
        const col = `${q}${luz === 'neutra' ? '' : `-${luz}`}${sufixo ? `-${sufixo}` : ''}`;
        colunas.push(col);
        const dir = path.join(OUT, col);
        fs.mkdirSync(dir, { recursive: true });
        const t0 = Date.now();
        const s = await abre(chromium, url, `cut=${corte}&tema=keynote&qualidade=${q}${luz === 'neutra' ? '' : `&luz=${luz}`}${ACUMULA != null ? `&acumula=${ACUMULA}` : ''}`);
        try {
          const lista = await s.page.evaluate(() => window.__tour.beats);
          for (const id of beats) {
            const e = lista.find((b) => b.id === id);
            if (!e) { console.log(`  ${col}: beat ${id} não está no corte ${corte}`); continue; }
            await s.page.evaluate((t) => window.__tour.seek(t), e.settle + 0.35);
            await s.page.screenshot({ path: path.join(dir, `${id}.png`), timeout: 180000 });
            if (process.argv.includes('--tempo')) {
              tempos[col] ??= {};
              tempos[col][id] = await s.page.evaluate((b) => {
                const ts = Array.from({ length: 8 }, (_, i) => b.start + (b.settle + 1 - b.start) * (i / 7));
                // readPixels de 1 pixel espera o quadro terminar: mede o desenho, não só o envio dos comandos
                const gl = document.querySelector('#cena3d canvas').getContext('webgl2');
                const px = new Uint8Array(4);
                const fim = () => gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
                window.__tour.seek(ts[0]); fim();
                const t0 = performance.now();
                for (const t of ts) { window.__tour.seek(t); fim(); }
                return (performance.now() - t0) / ts.length;
              }, e);
            }
          }
          const mats = await s.page.evaluate(() => window.__cena.materiais?.() ?? []);
          fs.writeFileSync(path.join(OUT, 'materiais.json'), JSON.stringify(mats, null, 1));
          if (s.erros.length) console.log(`  ${col}: erros no console: ${s.erros.join(' | ')}`);
        } finally { await s.browser.close(); }
        console.log(`lookdev: ${col} ok (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
      }
    }
  } finally { srv.close(); }
  if (Object.keys(tempos).length) {
    console.log('tempo médio de desenho por quadro (ms, SwiftShader na CPU; vale a comparação entre colunas):');
    console.log(['', ...beats].map((x) => x.padEnd(14)).join(''));
    for (const [c, t] of Object.entries(tempos)) console.log([c, ...beats.map((b) => (t[b] ?? NaN).toFixed(0))].map((x) => String(x).padEnd(14)).join(''));
    fs.writeFileSync(path.join(OUT, 'tempos.json'), JSON.stringify(tempos, null, 1));
  }
  if (process.argv.includes('--sem-folha')) return;

  const browser = await chromium.launch();
  const img = (p) => (fs.existsSync(p) ? `data:image/${p.endsWith('.jpg') ? 'jpeg' : 'png'};base64,${fs.readFileSync(p).toString('base64')}` : '');
  const css = `body{margin:0;background:#111;color:#e8e8e8;font:500 22px Inter,system-ui,sans-serif}
    h1{margin:0;padding:22px 28px 14px;font-size:30px;font-weight:700} .g{display:grid;gap:10px;padding:0 28px 28px;align-items:center}
    figure{margin:0} img{display:block;width:100%;object-fit:contain;background:#000} figcaption{padding:6px 2px 0;color:#aaa;font-size:18px}
    .cab{color:#ddd;font-weight:700;font-size:22px;padding:4px 2px} .lado{color:#bbb;font-size:18px;writing-mode:vertical-rl;transform:rotate(180deg);text-align:center}`;
  // folha: beats por linha, colunas = qualidade e luz
  const todas = fs.readdirSync(OUT).filter((d) => fs.statSync(path.join(OUT, d)).isDirectory()).filter((d) => colunas.includes(d));
  let page = await browser.newPage({ viewport: { width: 60 + todas.length * 640, height: 800 } });
  await page.setContent(`<style>${css}</style><h1>Lookdev: Keynote realista</h1>
    <div class="g" style="grid-template-columns:28px repeat(${todas.length},1fr)"><div></div>${todas.map((t) => `<div class="cab">${t}</div>`).join('')}
    ${beats.map((id) => `<div class="lado">${id}</div>${todas.map((t) => `<figure><img src="${img(path.join(OUT, t, `${id}.png`))}"></figure>`).join('')}`).join('')}</div>`);
  await page.screenshot({ path: path.join(OUT, 'folha.png'), fullPage: true });
  await page.close();
  // referência: cada beat ao lado das referências da mesma face (tabela REFS)
  const col = colunas[0];
  const linhas = beats.filter((b) => REFS[b]);
  const semRef = beats.filter((b) => !REFS[b]);
  if (semRef.length) console.log(`lookdev: sem referência pareada na tabela REFS: ${semRef.join(', ')}`);
  page = await browser.newPage({ viewport: { width: 1900, height: 800 } });
  await page.setContent(`<style>${css}</style><h1>Referência contra o nosso quadro, mesma face (julgar material, luz e sombra)</h1>
    <div class="g" style="grid-template-columns:28px repeat(3,1fr)">
    ${linhas.map((b) => {
    const figs = [[`nosso ${b} (${col})`, path.join(OUT, col, `${b}.png`)], ...REFS[b].map(([r, p]) => [r, path.join(CACHE, p)])].slice(0, 3);
    while (figs.length < 3) figs.push(['', '']);
    return `<div class="lado">${b}</div>${figs.map(([r, p]) => (p ? `<figure><img style="height:420px" src="${img(p)}"><figcaption>${r}</figcaption></figure>` : '<div></div>')).join('')}`;
  }).join('')}</div>`);
  await page.screenshot({ path: path.join(OUT, 'referencia.png'), fullPage: true });
  await browser.close();
  console.log(`lookdev: ${path.relative(process.cwd(), OUT)}`);
}
main().catch((e) => { console.error(e); process.exit(1); });
