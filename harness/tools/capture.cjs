#!/usr/bin/env node
// Captura determinística do tour: seek(i / fps) + screenshot, um beat por pasta, e montagem com ffmpeg.
// Uso: node harness/tools/capture.cjs --cut completo [--fps 30] [--beats a4.2,a5.5] [--out harness/dist]
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const { garanteBuild, serve, abre, HARNESS, VIEWER, DIST } = require('./smoke.cjs');

const arg = (nome, padrao) => { const i = process.argv.indexOf(`--${nome}`); return i >= 0 ? process.argv[i + 1] : padrao; };
const sha = (...partes) => { const h = crypto.createHash('sha256'); partes.forEach((p) => h.update(p)); return h.digest('hex'); };
const lista = (d) => (fs.existsSync(d) ? fs.readdirSync(d, { recursive: true, withFileTypes: true }).filter((f) => f.isFile()).map((f) => path.join(f.parentPath ?? f.path, f.name)).sort() : []);

async function main() {
  const corte = arg('cut', 'completo');
  const out = path.resolve(arg('out', path.join(HARNESS, 'dist')));
  const filtro = arg('beats', '') ? arg('beats').split(',') : null;
  if (!process.argv.includes('--no-build')) garanteBuild();
  const { chromium } = require('playwright');
  const dados = path.join(VIEWER, 'public', 'data');
  const storyboard = JSON.parse(fs.readFileSync(path.join(dados, 'storyboard.json'), 'utf8'));
  const textos = JSON.parse(fs.readFileSync(path.join(dados, 'beats.json'), 'utf8')).beats;
  const fps = Number(arg('fps', storyboard.fps));

  // Parte do hash comum a todos os beats: diagramas, GLB, medidas e o bundle do viewer.
  const comum = sha(
    ...lista(path.join(dados, 'diagrams')).map((f) => fs.readFileSync(f)),
    fs.existsSync(path.join(dados, 'card.glb')) ? fs.readFileSync(path.join(dados, 'card.glb')) : '',
    fs.readFileSync(path.join(dados, 'measurements.json')),
    JSON.stringify(storyboard.world ?? []),
    ...lista(path.join(DIST, 'assets')).filter((f) => /\.(js|css)$/.test(f)).map((f) => fs.readFileSync(f)),
    String(fps),
  );

  const { srv, url } = await serve(DIST);
  const { browser, page, erros } = await abre(chromium, url, `cut=${corte}`);
  try {
    const info = await page.evaluate(() => ({ beats: window.__tour.beats, duration: window.__tour.duration }));
    const porId = Object.fromEntries(storyboard.beats.map((b) => [b.id, b]));
    const dirCorte = path.join(out, 'capture', corte);
    fs.mkdirSync(dirCorte, { recursive: true });
    const segmentos = [];
    let quadros = 0, ms = 0;

    for (let i = 0; i < info.beats.length; i++) {
      const e = info.beats[i];
      if (filtro && !filtro.includes(e.id)) continue;
      const dir = path.join(dirCorte, e.id);
      const mp4 = path.join(dirCorte, `${e.id}.mp4`);
      const ant = info.beats[i - 1];
      const hash = sha(comum, JSON.stringify([porId[e.id], textos[e.id], ant && porId[ant.id], e.start, e.settle, e.end]));
      const arqHash = path.join(dir, '.hash');
      segmentos.push(mp4);
      if (fs.existsSync(arqHash) && fs.readFileSync(arqHash, 'utf8') === hash && fs.existsSync(mp4)) {
        console.log(`beat ${e.id}: sem mudanças, reaproveitado`);
        continue;
      }
      fs.rmSync(dir, { recursive: true, force: true });
      fs.mkdirSync(dir, { recursive: true });
      const k0 = Math.ceil(e.start * fps - 1e-9), k1 = Math.ceil(e.end * fps - 1e-9); // [k0, k1)
      const ult = i === info.beats.length - 1 ? Math.ceil(info.duration * fps - 1e-9) : k1;
      let n = 0;
      const t0 = Date.now();
      for (let k = k0; k < ult; k++) {
        await page.evaluate((t) => window.__tour.seek(t), k / fps);
        await page.screenshot({ path: path.join(dir, `${String(++n).padStart(5, '0')}.png`) });
      }
      ms += Date.now() - t0; quadros += n;
      console.log(`beat ${e.id}: ${n} quadros (${((Date.now() - t0) / n).toFixed(0)} ms por quadro)`);
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(dir, '%05d.png'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', '-movflags', '+faststart', mp4]);
      fs.writeFileSync(arqHash, hash);
    }
    if (erros.length) console.log(`avisos de console/erros: ${[...new Set(erros)].join(' | ')}`);
    if (!segmentos.length) { console.log('nenhum beat selecionado'); return; }
    // concatena
    const lst = path.join(dirCorte, 'concat.txt');
    fs.writeFileSync(lst, segmentos.map((s) => `file '${s}'`).join('\n') + '\n');
    const final = path.join(out, `tour-${corte}.mp4`);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', final]);
    console.log(`\nMP4: ${final}`);
    if (quadros) console.log(`tempo médio: ${(ms / quadros).toFixed(0)} ms por quadro (${quadros} quadros capturados, ${fps} fps)`);
  } finally {
    await browser.close();
    srv.close();
  }
}
main().catch((e) => { console.error(e); process.exit(1); });
