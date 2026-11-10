// Cotas da placa montada (só no tema blueprint): linhas de cota no chão, projetadas do 3D a cada
// quadro. Os números vêm de measurements.json e só entram medidas já auditadas; nada é inventado.
import { STAGE_W, STAGE_H } from './layout.js';

const NS = 'http://www.w3.org/2000/svg';
const el = (tag, attrs = {}, pai) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (pai) pai.appendChild(e);
  return e;
};
const fmt = (v) => `${String(v).replace('.', ',')} mm`;

export function criaCotas(palco, cena, medidas) {
  const svg = el('svg', { id: 'cotas', width: STAGE_W, height: STAGE_H, viewBox: `0 0 ${STAGE_W} ${STAGE_H}` }, palco);
  const auditada = (k) => {
    const m = medidas?.[k];
    return m && /^auditado/.test(m.status ?? '') && m.provenance !== 'inferred' ? m.value_mm : null;
  };
  const L = auditada('card_envelope_length'), H = auditada('card_envelope_height');
  const D = 22;                                       // afastamento da linha de cota, em mm
  const lista = [];
  if (L) lista.push({ a: [0, 0, 0], b: [L, 0, 0], o: [0, -1, 0], txt: fmt(L) });
  if (H) lista.push({ a: [L ?? 304.8, 0, 0], b: [L ?? 304.8, H, 0], o: [1, 0, 0], txt: fmt(H) });
  for (const c of lista) {
    c.g = el('g', { class: 'cota' }, svg);
    c.ext = el('path', { class: 'cota-ext' }, c.g);
    c.lin = el('path', { class: 'cota-lin' }, c.g);
    c.pt = el('path', { class: 'cota-ponta' }, c.g);
    c.t = el('text', { class: 'cota-txt', 'text-anchor': 'middle' }, c.g);
    c.t.textContent = c.txt;
  }
  const soma = (p, o, k) => [p[0] + o[0] * k, p[1] + o[1] * k, p[2] + o[2] * k];
  let visAnt = -1;

  return {
    atualiza({ visivel }) {
      const v = Math.round(visivel * 50) / 50;
      if (v !== visAnt) { visAnt = v; svg.style.opacity = v; svg.style.visibility = v > 0 ? 'visible' : 'hidden'; }
      if (v <= 0) return;
      for (const c of lista) {
        const P = [c.a, soma(c.a, c.o, D + 6), c.b, soma(c.b, c.o, D + 6), soma(c.a, c.o, D), soma(c.b, c.o, D)].map((p) => cena.projeta(p));
        if (P.some((p) => !p)) { c.g.style.display = 'none'; continue; }
        c.g.style.display = '';
        const [a0, a1, b0, b1, m0, m1] = P;
        const f = (p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`;
        // extensão começa um pouco afastada da peça, como no desenho técnico
        const ini = (p, q) => [p[0] + (q[0] - p[0]) * 0.18, p[1] + (q[1] - p[1]) * 0.18];
        c.ext.setAttribute('d', `M${f(ini(a0, a1))} L${f(a1)} M${f(ini(b0, b1))} L${f(b1)}`);
        c.lin.setAttribute('d', `M${f(m0)} L${f(m1)}`);
        // traços oblíquos de 45 graus nas pontas
        const ang = Math.atan2(m1[1] - m0[1], m1[0] - m0[0]);
        const k = 9, a45 = ang + Math.PI / 4;
        const tr = (p) => `M${(p[0] - Math.cos(a45) * k).toFixed(1)},${(p[1] - Math.sin(a45) * k).toFixed(1)} L${(p[0] + Math.cos(a45) * k).toFixed(1)},${(p[1] + Math.sin(a45) * k).toFixed(1)}`;
        c.pt.setAttribute('d', `${tr(m0)} ${tr(m1)}`);
        let deg = ang * 180 / Math.PI;
        if (deg > 90) deg -= 180; else if (deg < -90) deg += 180;
        const mx = (m0[0] + m1[0]) / 2, my = (m0[1] + m1[1]) / 2;
        // texto do lado de fora da cota (lado oposto à peça)
        const nx = -Math.sin(deg * Math.PI / 180), ny = Math.cos(deg * Math.PI / 180);
        const fora = (a1[0] - a0[0]) * nx + (a1[1] - a0[1]) * ny > 0 ? 1 : -1;
        c.t.setAttribute('transform', `translate(${(mx + nx * 16 * fora).toFixed(1)} ${(my + ny * 16 * fora).toFixed(1)}) rotate(${deg.toFixed(2)})`);
      }
    },
  };
}
