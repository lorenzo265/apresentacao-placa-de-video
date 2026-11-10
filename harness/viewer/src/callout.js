// Linha de chamada (SVG em pixels do palco) e caixa de texto (DOM).
import { STAGE_W, STAGE_H, boxPlacement } from './layout.js';

const NS = 'http://www.w3.org/2000/svg';

const SELOS = {
  confirmed: { palavra: 'Confirmado', icone: 'M3,8 L7,12 L13,4' },                       // visto
  derived: { palavra: 'Derivado', icone: 'M3,4 L13,4 M3,8 L13,8 M3,12 L9,12' },         // conta
  inferred: { palavra: 'Provável', icone: 'M5,6 Q5,3 8,3 Q11,3 11,6 Q11,8 8,9 L8,10 M8,12.5 L8,13' }, // interrogação
  illustrative: { palavra: 'Ilustrativo', icone: 'M8,2 L14,8 L8,14 L2,8 Z' },            // losango
};

export function criaChamada(palco) {
  const svg = document.createElementNS(NS, 'svg');
  svg.id = 'chamada';
  svg.setAttribute('width', STAGE_W); svg.setAttribute('height', STAGE_H);
  svg.setAttribute('viewBox', `0 0 ${STAGE_W} ${STAGE_H}`);
  const linha = document.createElementNS(NS, 'path');
  const ponto = document.createElementNS(NS, 'circle');
  const anel = document.createElementNS(NS, 'circle');
  linha.setAttribute('class', 'linha'); ponto.setAttribute('class', 'ponto'); anel.setAttribute('class', 'anel');
  svg.append(linha, anel, ponto);
  palco.appendChild(svg);

  const caixa = document.createElement('div');
  caixa.id = 'caixa';
  caixa.innerHTML = `<div class="selos"></div><h2></h2><p class="caption"></p><p class="fonte"></p>`;
  palco.appendChild(caixa);
  const q = (s) => caixa.querySelector(s);
  let atual = null;       // beat cujo conteúdo está na caixa
  let ret = [0, 0, 0, 0]; // retângulo da caixa em px do palco

  function selo(p) {
    const s = SELOS[p];
    return `<span class="selo s-${p}"><svg viewBox="0 0 16 16" width="22" height="22"><path d="${s.icone}"/></svg>${s.palavra}</span>`;
  }

  /** Coloca o conteúdo do beat e mede a caixa (só quando o beat muda). */
  function define(beat, texto) {
    if (atual === beat) return;
    atual = beat;
    const { side, vert } = boxPlacement(beat.callout);
    caixa.className = `${side} ${vert}`;
    q('.selos').innerHTML = (beat.provenance ?? []).map(selo).join('');
    q('h2').textContent = texto.headline;
    q('.caption').textContent = texto.caption;
    q('.fonte').textContent = texto.source_line;
    q('.fonte').style.display = texto.source_line ? '' : 'none';
    const r = caixa.getBoundingClientRect();
    const pr = palco.getBoundingClientRect();
    const k = pr.width / STAGE_W;
    ret = [(r.left - pr.left) / k, (r.top - pr.top) / k, r.width / k, r.height / k];
  }

  /** Desenha a linha do anchor [x,y] (px do palco) até a caixa, com um cotovelo. */
  function atualiza(beat, ancora, pLinha, pCaixa, cor) {
    caixa.style.opacity = pCaixa;
    caixa.style.visibility = pCaixa > 0.001 ? 'visible' : 'hidden';
    if (!beat.callout || !ancora || pLinha <= 0.001) { svg.style.visibility = 'hidden'; return; }
    svg.style.visibility = 'visible';
    svg.style.setProperty('--cor-linha', cor);
    const [ax, ay] = ancora;
    const { side } = boxPlacement(beat.callout);
    const ex = side === 'left' ? ret[0] + ret[2] : ret[0];       // borda da caixa voltada para o centro
    const ey = ret[1] + 46;                                       // altura do título
    const dir = side === 'left' ? 1 : -1;
    let cx = ex + dir * 56;                                       // onde a diagonal vira horizontal
    if ((ax - cx) * dir < 0) cx = ax;                             // âncora entre o cotovelo e a caixa
    const pts = [[ax, ay], [cx, ey], [ex, ey]];
    const L = Math.hypot(cx - ax, ey - ay) + Math.abs(ex - cx);
    linha.setAttribute('d', `M${pts.map((p) => p.join(',')).join(' L')}`);
    linha.style.strokeDasharray = L;
    linha.style.strokeDashoffset = L * (1 - pLinha);
    const r = Math.min(1, pLinha * 6);
    ponto.setAttribute('cx', ax); ponto.setAttribute('cy', ay); ponto.setAttribute('r', 7 * r);
    anel.setAttribute('cx', ax); anel.setAttribute('cy', ay); anel.setAttribute('r', 15 * r);
  }

  function overflow() { return caixa.scrollHeight > caixa.clientHeight + 1 || q('.caption').scrollWidth > q('.caption').clientWidth + 1; }
  return { caixa, define, atualiza, ret: () => ret, overflow };
}
