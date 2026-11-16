// Linha de chamada (SVG em pixels do palco) e caixa de texto (DOM).
// A caixa é o slide: um título e uma lista de tópicos (campo `pontos` de beats.json). Sem selos de
// procedência e sem linha de fonte na tela (ficam nos dados e nos relatórios de auditoria).
import { STAGE_W, STAGE_H, boxPlacement } from './layout.js';

const NS = 'http://www.w3.org/2000/svg';

/** Texto com **negrito** vira nós de DOM (sem innerHTML: o conteúdo nunca é lido como HTML). */
function preenche(el, texto) {
  el.textContent = '';
  String(texto).split('**').forEach((trecho, i) => {
    if (!trecho) return;
    if (i % 2) { const b = document.createElement('strong'); b.textContent = trecho; el.appendChild(b); }
    else el.appendChild(document.createTextNode(trecho));
  });
}

export function criaChamada(palco) {
  const svg = document.createElementNS(NS, 'svg');
  svg.id = 'chamada';
  svg.setAttribute('width', STAGE_W); svg.setAttribute('height', STAGE_H);
  svg.setAttribute('viewBox', `0 0 ${STAGE_W} ${STAGE_H}`);
  const linha = document.createElementNS(NS, 'path');
  const ponto = document.createElementNS(NS, 'circle');
  const anel = document.createElementNS(NS, 'circle');
  // halo (traço largo sob a linha) e mira (cruz em volta do ponto): só os temas os mostram
  const halo = document.createElementNS(NS, 'path');
  const mira = document.createElementNS(NS, 'path');
  linha.setAttribute('class', 'linha'); ponto.setAttribute('class', 'ponto'); anel.setAttribute('class', 'anel');
  halo.setAttribute('class', 'halo'); mira.setAttribute('class', 'mira');
  svg.append(halo, linha, anel, mira, ponto);
  palco.appendChild(svg);

  const caixa = document.createElement('div');
  caixa.id = 'caixa';
  caixa.innerHTML = `<p class="topico"></p><h2></h2><ul class="pontos"></ul><p class="caption"></p>`;
  palco.appendChild(caixa);
  const q = (s) => caixa.querySelector(s);
  let atual = null;       // beat cujo conteúdo está na caixa
  let ret = [0, 0, 0, 0]; // retângulo da caixa em px do palco
  let yTitulo = 46;       // altura (px do palco, relativa ao topo da caixa) do meio da primeira linha do título

  /** Lista de tópicos: "- texto" é subtópico do tópico anterior; **negrito** destaca. */
  function montaPontos(pontos) {
    const ul = q('.pontos');
    ul.textContent = '';
    let sub = null;
    for (const p of pontos) {
      const filho = /^-\s+/.test(p);
      if (filho && ul.lastElementChild) {
        if (!sub) { sub = document.createElement('ul'); ul.lastElementChild.appendChild(sub); }
        const li = document.createElement('li');
        preenche(li, p.replace(/^-\s+/, ''));
        sub.appendChild(li);
      } else {
        sub = null;
        const li = document.createElement('li');
        preenche(li, p);
        ul.appendChild(li);
      }
    }
  }

  /** Coloca o conteúdo do beat e mede a caixa (só quando o beat muda). */
  function define(beat, texto) {
    if (atual === beat) return;
    atual = beat;
    const { side, vert } = boxPlacement(beat.callout);
    caixa.className = `${side} ${vert}`;
    const pontos = Array.isArray(texto.pontos) ? texto.pontos : [];
    q('.topico').textContent = texto.topico ?? '';
    q('.topico').style.display = texto.topico ? '' : 'none';
    q('h2').textContent = texto.headline;
    montaPontos(pontos);
    q('.pontos').style.display = pontos.length ? '' : 'none';
    // sem tópicos (beat de extra, ainda no formato antigo): a legenda aparece como parágrafo
    q('.caption').textContent = pontos.length ? '' : texto.caption ?? '';
    q('.caption').style.display = pontos.length || !texto.caption ? 'none' : '';
    const r = caixa.getBoundingClientRect();
    const pr = palco.getBoundingClientRect();
    const k = pr.width / STAGE_W;
    ret = [(r.left - pr.left) / k, (r.top - pr.top) / k, r.width / k, r.height / k];
    const h = q('h2').getBoundingClientRect();
    const alturaLinha = parseFloat(getComputedStyle(q('h2')).lineHeight) || 48;
    yTitulo = (h.top - r.top) / k + alturaLinha / 2;
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
    const ey = ret[1] + yTitulo;                                  // altura do título
    const dir = side === 'left' ? 1 : -1;
    let cx = ex + dir * 56;                                       // onde a diagonal vira horizontal
    if ((ax - cx) * dir < 0) cx = ax;                             // âncora entre o cotovelo e a caixa
    const pts = [[ax, ay], [cx, ey], [ex, ey]];
    const L = Math.hypot(cx - ax, ey - ay) + Math.abs(ex - cx);
    linha.setAttribute('d', `M${pts.map((p) => p.join(',')).join(' L')}`);
    linha.style.strokeDasharray = L;
    linha.style.strokeDashoffset = L * (1 - pLinha);
    halo.setAttribute('d', linha.getAttribute('d'));
    halo.style.strokeDasharray = L;
    halo.style.strokeDashoffset = L * (1 - pLinha);
    const r = Math.min(1, pLinha * 6);
    const m1 = 11 * r, m2 = 24 * r;
    mira.setAttribute('d', `M${ax - m2},${ay} L${ax - m1},${ay} M${ax + m1},${ay} L${ax + m2},${ay} M${ax},${ay - m2} L${ax},${ay - m1} M${ax},${ay + m1} L${ax},${ay + m2}`);
    ponto.setAttribute('cx', ax); ponto.setAttribute('cy', ay); ponto.setAttribute('r', 7 * r);
    anel.setAttribute('cx', ax); anel.setAttribute('cy', ay); anel.setAttribute('r', 15 * r);
  }

  function overflow() {
    return caixa.scrollHeight > caixa.clientHeight + 1 || [...caixa.querySelectorAll('li, .caption')].some((e) => e.scrollWidth > e.clientWidth + 1);
  }
  return { caixa, define, atualiza, ret: () => ret, overflow };
}
