#!/usr/bin/env node
// Determinismo do polimento do viewer (tema Keynote realista, modo de captura):
//  1. acumulação de quadros num beat parado: o mesmo instante dá o mesmo PNG, chegando de outro beat, do
//     fim da entrada (onde a cena ainda não acumula e a média continua dali) ou do próprio instante; e o
//     fim da entrada, revisitado depois da média completa, volta ao quadro de uma amostra;
//  2. mergulho t1.1 no meio da entrada (câmera 3D andando, diagrama colado ao package) e enquadramento
//     final igual ao do beat;
//  3. caminho na placa (a2.10) no meio do traçado.
// Uso: node harness/tools/determinismo-polimento.cjs [--acumula 8] [--cut seminario] [--no-build]
// Falha (código 1) se algum par de capturas diferir. Com render por software cada amostra leva segundos:
// o padrão de 8 amostras exercita a mesma sequência fixa que o viewer usa com 32 ou 64.
const { garanteBuild, serve, abre, DIST } = require('./smoke.cjs');

const args = process.argv.slice(2);
const arg = (k, def) => (args.includes(k) ? args[args.indexOf(k) + 1] : def);

(async () => {
  const N = Number(arg('--acumula', 8));
  const corte = arg('--cut', 'seminario');
  if (!args.includes('--no-build')) garanteBuild();
  const { chromium } = require('playwright');
  const { srv, url } = await serve(DIST);
  const falhas = [];
  const s = await abre(chromium, url, `cut=${corte}&tema=keynote&acumula=${N}`);
  const { page } = s;
  const seek = (t) => page.evaluate((x) => window.__tour.seek(x), t);
  const shot = () => page.screenshot({ timeout: 900000 });
  const estado = () => page.evaluate(() => window.__tour.estado());
  const igual = (a, b, nome) => {
    if (a.equals(b)) console.log(`  ok ${nome}`);
    else { falhas.push(nome); console.log(`  FALHA ${nome}`); }
  };
  try {
    const beats = await page.evaluate(() => window.__tour.beats);
    const B = (id) => beats.find((b) => b.id === id);

    // 1. acumulação num beat parado (a0.2, placa montada)
    const p = B('a0.2'), outro = B('a2.9');
    console.log(`acumulação (${N} amostras) em a0.2`);
    await seek(p.settle);
    const A = await shot();
    const e1 = await estado();
    if (e1.acum?.n !== N) { falhas.push(`acumulação: ${e1.acum?.n} amostras, esperado ${N}`); console.log(`  FALHA amostras ${JSON.stringify(e1.acum)}`); }
    else console.log(`  ok ${N} amostras na média`);
    await seek(outro.start + (outro.entrada - outro.start) * 0.5);
    await shot();
    await seek(p.settle);
    igual(A, await shot(), 'a0.2 parado, de volta de outro beat');
    await seek(p.settle + 1.5);                     // mesmo estado 3D: a média já pronta é reaproveitada
    const A2 = await shot();
    await seek(p.entrada);                          // fim da entrada: 1 amostra, mesma assinatura
    const E = await shot();
    const e2 = await estado();
    if (e2.acum?.n !== 1) { falhas.push(`fim da entrada com ${e2.acum?.n} amostras, esperado 1`); console.log(`  FALHA fim da entrada ${JSON.stringify(e2.acum)}`); }
    await seek(p.settle);                           // continua a média a partir da amostra 1
    igual(A, await shot(), 'a0.2 parado, continuando do fim da entrada');
    await seek(p.entrada);                          // e volta a uma amostra
    igual(E, await shot(), 'a0.2 fim da entrada, depois da média completa');
    await seek(outro.settle);
    await seek(p.settle + 1.5);
    igual(A2, await shot(), 'a0.2 parado, outro instante do mesmo hold');

    // 2. mergulho t1.1 no meio da entrada
    const m = B('t1.1');
    if (!m?.mergulho) { falhas.push('t1.1 sem mergulho'); console.log('  FALHA t1.1 sem mergulho'); }
    for (const f of [0.35, 0.6]) {
      const t = m.start + (m.entrada - m.start) * f + 0.013;
      console.log(`mergulho t1.1 em ${Math.round(f * 100)}% da entrada`);
      await seek(t);
      const M1 = await shot();
      const vb1 = (await estado()).vb;
      await seek(B('a4.1').settle);
      await shot();
      await seek(p.settle);
      await seek(t);
      const vb2 = (await estado()).vb;
      igual(M1, await shot(), `t1.1 a ${Math.round(f * 100)}%`);
      if (JSON.stringify(vb1) !== JSON.stringify(vb2)) { falhas.push('t1.1: enquadramento do diagrama diferente'); console.log('  FALHA enquadramento'); }
    }
    // no fim da entrada o enquadramento é o do beat (o mesmo de um seek no settle)
    await seek(m.entrada);
    const vbFim = (await estado()).vb;
    await seek(m.settle);
    const vbSettle = (await estado()).vb;
    const d = Math.max(...['cx', 'cy', 'lw'].map((k) => Math.abs(vbFim[k] - vbSettle[k])));
    if (d > 1e-5) { falhas.push(`t1.1: fim do mergulho fora do enquadramento do beat (${d})`); console.log(`  FALHA fim do mergulho ${JSON.stringify(vbFim)} x ${JSON.stringify(vbSettle)}`); }
    else console.log('  ok fim do mergulho no enquadramento do beat');

    // 3. caminho na placa no meio do traçado
    const c = B('a2.10');
    const tc = c.entrada + 1.1;
    console.log('caminho dos dados (a2.10) no meio do traçado');
    await seek(tc);
    const C1 = await shot();
    await seek(B('a2.9').settle);
    await shot();
    await seek(tc);
    igual(C1, await shot(), 'a2.10 caminho a meio');
    if (s.erros.length) { falhas.push(...s.erros); s.erros.forEach((x) => console.log(`  FALHA ${x}`)); }
  } finally {
    await s.browser.close();
    srv.close();
  }
  if (falhas.length) { console.log(`\ndeterminismo-polimento: ${falhas.length} falha(s)`); process.exit(1); }
  console.log('\ndeterminismo-polimento: tudo certo');
})().catch((e) => { console.error(e); process.exit(2); });
