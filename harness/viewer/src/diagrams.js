// Camada SVG dos diagramas: um <svg> sobre o canvas 3D com viewBox animado.
// Desenhista sem opinião: posições, rótulos e contagens vêm dos JSON.
import { STAGE_W, STAGE_H, LOD_MIN, LOD_FULL, LOD_BIG_START, LOD_BIG_END } from './layout.js';

const NS = 'http://www.w3.org/2000/svg';
const el = (tag, attrs = {}, pai) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (pai) pai.appendChild(e);
  return e;
};
const suave = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

// Medição de texto por canvas 2D (determinística depois que as fontes carregam).
const ctx = document.createElement('canvas').getContext('2d');
const cacheLarg = new Map();
function larguraPorUnidade(texto, mono, peso) {
  const k = `${mono ? 'm' : 's'}${peso}|${texto}`;
  let v = cacheLarg.get(k);
  if (v === undefined) {
    ctx.font = `${peso} 100px ${mono ? '"JetBrains Mono"' : 'Inter'}, sans-serif`;
    v = ctx.measureText(texto).width / 100;
    cacheLarg.set(k, v);
  }
  return v;
}

/**
 * opcoes (só com ?tema; sem tema, o desenho é o de sempre):
 *   raio:       raio de canto como fração do menor lado do nó (padrão 0,04)
 *   rotuloMono: títulos de contêiner em JetBrains Mono (a medida de encaixe usa a mesma fonte).
 *               Rótulo e sub-rótulo seguem em Inter: na mono, mais larga, os sub-rótulos pequenos
 *               ficariam abaixo do limite de leitura e sumiriam
 *   sombra:     placas com sombra (dois retângulos deslocados sob cada nó)
 *   fluxo:      { vel, periodo, fase, camadas: [{cls, l}] }: cada camada é um traço de comprimento l
 *               com período fixo; todas terminam no mesmo ponto, o que dá cabeça e cauda à luz
 *   hospedeiro: opacidade dos nós fora do diagrama em foco e dos que ele embute (o hospedeiro do
 *               zoom), para a planta do chip não aparecer em escala gigante atrás do SM
 */
export function criaCamadaDiagramas(container, world, opcoes = null) {
  const raio = opcoes?.raio ?? 0.04;
  const todosMono = !!opcoes?.rotuloMono;
  const comSombra = !!opcoes?.sombra;
  const SEM_SOMBRA = new Set(['note', 'gap', 'lane']);
  const opHospedeiro = opcoes?.hospedeiro ?? null;
  // diagrama -> diagrama que o embute (para saber se um nó está dentro do diagrama em foco)
  const pai = new Map();
  for (const r of world.recs) if (r.isContainer && r.node.embed) pai.set(r.node.embed, r.diagram);
  const dentroDe = (d, v) => { for (let x = d; x; x = pai.get(x)) if (x === v) return true; return false; };
  const fatorVista = new Map();      // diagrama em foco -> Float32Array por nó
  const fatoresDaVista = (v) => {
    if (!opHospedeiro || !v) return null;
    if (!fatorVista.has(v)) fatorVista.set(v, Float32Array.from(world.recs, (r) => (dentroDe(r.diagram, v) ? 1 : opHospedeiro)));
    return fatorVista.get(v);
  };
  const svg = el('svg', { id: 'diagramas', width: STAGE_W, height: STAGE_H, viewBox: `0 0 ${STAGE_W} ${STAGE_H}`, preserveAspectRatio: 'none' }, container);
  const defs = el('defs', {}, svg);
  const padrao = el('pattern', { id: 'hachura', patternUnits: 'userSpaceOnUse', width: 8, height: 8 }, defs);
  el('path', { d: 'M-2,2 L2,-2 M0,8 L8,0 M6,10 L10,6', class: 'hachura-traco' }, padrao);
  const gNos = el('g', { id: 'nos' }, svg);
  const gFluxos = el('g', { id: 'fluxos' }, svg);

  // ---- nós ----
  const itens = world.recs.map((r) => monta(r, gNos));

  function monta(r, pai) {
    const n = r.node, [x, y, w, h] = r.rect;
    const g = el('g', { class: `n k-${n.kind}${n.state === 'disabled' ? ' disabled' : ''}`, 'data-id': n.id }, pai);
    const rx = Math.min(w, h) * raio;
    if (comSombra && n.state !== 'disabled' && !SEM_SOMBRA.has(n.kind)) {
      // sombra de placa: um núcleo curto e uma penumbra mais larga, sem filtro (barato e determinístico)
      const m0 = Math.min(w, h), dy = Math.min(m0 * 0.05, Math.max(w, h) * 0.02);
      el('rect', { x: x - dy * 0.35, y: y + dy * 0.9, width: w + dy * 0.7, height: h + dy * 0.5, rx: rx + dy * 0.4, class: 'sombra s2' }, g);
      el('rect', { x, y: y + dy * 0.45, width: w, height: h, rx, class: 'sombra s1' }, g);
    }
    const rect = el('rect', { x, y, width: w, height: h, rx }, g);
    if (opcoes) rect.classList.add('corpo');
    if (n.state === 'disabled') el('rect', { x, y, width: w, height: h, rx, class: 'hachurada' }, g);
    const it = { r, g, rect, textos: [], visivel: true, op: 1, hostFade: !!n.embed, alvo: false };
    const rotulos = [];
    const mono = !!n.mono;                       // rótulo principal
    const monoSec = mono || todosMono;           // título de contêiner
    const peso = n.kind === 'counter' || r.isContainer || n.kind === 'header' ? 600 : 500;
    const esq = n.align === 'left';
    const m = Math.min(w, h);
    const fit = (txt, hPref, maxW, mm = mono) => Math.min(hPref, maxW / Math.max(0.5, larguraPorUnidade(txt, mm, mm && todosMono ? 500 : peso)));
    const sz = n.label_size ? n.label_size * r.s : null;
    const teto = 0.1 * Math.max(w, h);       // rótulo ajustado nunca passa de 10% do maior lado
    if (n.label) {
      if (r.isContainer) {
        // contêiner: título no canto superior esquerdo
        const hh = sz ? (todosMono ? fit(n.label, sz, w * 0.8, monoSec) : sz) : fit(n.label, m * 0.045, w * 0.8, monoSec);
        rotulos.push({ txt: n.label, x: x + m * 0.03, y: y + m * 0.02 + hh / 2, h: hh, anchor: 'start', cls: 'titulo' });
      } else if (n.sublabel) {
        const h1 = sz ?? fit(n.label, Math.min(h * 0.34, teto), w * 0.92);
        const h2 = fit(n.sublabel, Math.min(h1 * 0.8, h * 0.26), w * 0.92);
        const total = h1 + h2 * 1.15;
        const y1 = y + (h - total) / 2 + h1 / 2;
        const ax = esq ? x + h * 0.25 : x + w / 2;
        rotulos.push({ txt: n.label, x: ax, y: y1, h: h1, anchor: esq ? 'start' : 'middle', cls: 'rotulo' });
        rotulos.push({ txt: n.sublabel, x: ax, y: y1 + h1 / 2 + h2 * 0.65, h: h2, anchor: esq ? 'start' : 'middle', cls: 'sub' });
      } else {
        const hh = sz ?? fit(n.label, Math.min(h * 0.5, teto), (esq ? w - h * 0.5 : w * 0.92));
        rotulos.push({ txt: n.label, x: esq ? x + h * 0.25 : x + w / 2, y: y + h / 2, h: hh, anchor: esq ? 'start' : 'middle', cls: 'rotulo' });
      }
    } else if (n.sublabel && !r.isContainer) {
      const hh = fit(n.sublabel, Math.min(h * 0.4, teto), w * 0.92);
      rotulos.push({ txt: n.sublabel, x: x + w / 2, y: y + h / 2, h: hh, anchor: 'middle', cls: 'sub' });
    }
    for (const t of rotulos) {
      const e = el('text', { x: t.x, y: t.y, 'font-size': t.h, 'text-anchor': t.anchor, class: `${t.cls}${n.mono ? ' mono' : ''}` }, g);
      e.textContent = t.txt;
      it.textos.push({ e, h: t.h, op: 1 });
    }
    return it;
  }

  // ---- fluxos ----
  const fx = opcoes?.fluxo ?? null;
  const camadasFluxo = fx?.camadas ?? [{ cls: 'f-anim', l: 0 }];
  const vel = fx?.vel ?? 70;
  const fluxos = new Map();
  let nFluxo = 0;
  for (const [id, { flow, T }] of world.flows) {
    const de = world.byId.get(flow.from), para = world.byId.get(flow.to);
    let pts;
    if (flow.points?.length >= 2) pts = flow.points.map(([px, py]) => [T.ox + px * T.s, T.oy + py * T.s]);
    else if (de && para) pts = [[de.cx, de.cy], [para.cx, para.cy]];
    else continue;
    const cam = flow.path ?? 'control';
    const g = el('g', { class: `fluxo f-${cam}`, visibility: 'hidden' }, gFluxos);
    const d = 'M' + pts.map((p) => p.join(',')).join(' L');
    el('path', { d, class: 'f-base' }, g);
    const camadas = camadasFluxo.map((c) => {
      const e = el('path', { d, class: c.cls }, g);
      if (fx) e.style.strokeDasharray = `${c.l} ${fx.periodo - c.l}`;
      return { e, l: c.l };
    });
    const fase = fx ? (nFluxo * (fx.fase ?? 0) * fx.periodo) % fx.periodo : 0;
    nFluxo++;
    const ponta = el('path', { d: 'M-9,-6 L7,0 L-9,6 Z', class: 'f-ponta' }, g);
    let rot = null;
    if (flow.label) { rot = el('text', { class: 'f-rotulo', 'text-anchor': 'middle' }, g); rot.textContent = flow.label; }
    const meio = pts[Math.floor((pts.length - 1) / 2)], meio2 = pts[Math.floor((pts.length - 1) / 2) + 1] ?? meio;
    const fim = pts[pts.length - 1], ant = pts[pts.length - 2];
    fluxos.set(id, {
      g, camadas, fase, ponta, rot, mx: (meio[0] + meio2[0]) / 2, my: (meio[1] + meio2[1]) / 2,
      fim, ang: Math.atan2(fim[1] - ant[1], fim[0] - ant[0]) * 180 / Math.PI, vis: false,
    });
  }

  /**
   * Atualiza o quadro. vb = {cx, cy, lw} (lw = log da largura em unidades do mundo).
   * dims: Float32Array|null (fator do destaque); dimsAnt: o do beat anterior; hl: 0..1 entre os dois.
   * flowsAtivos: ids; flowAlpha: 0..1; t: tempo da timeline em s.
   */
  let alvoAtual = null;
  const porId = new Map(itens.map((it) => [it.r.id, it]));
  function atualiza({ vb, dims, dimsAnt, hl, flowsAtivos, flowAlpha, t, visivel, alvo = null, vista = null, vistaAnt = null }) {
    const hv = fatoresDaVista(vista), hvAnt = fatoresDaVista(vistaAnt);
    if (alvo !== alvoAtual) {
      // nó-âncora do beat: os temas o realçam (sem tema não há regra para .alvo)
      porId.get(alvoAtual)?.g.classList.remove('alvo');
      porId.get(alvo)?.g.classList.add('alvo');
      alvoAtual = alvo;
    }
    svg.style.opacity = visivel;
    svg.style.visibility = visivel > 0.001 ? 'visible' : 'hidden';
    if (visivel <= 0.001) return;
    const vw = Math.exp(vb.lw), vh = vw * STAGE_H / STAGE_W;
    const x0 = vb.cx - vw / 2, y0 = vb.cy - vh / 2;
    const k = STAGE_W / vw;                       // pixels por unidade do mundo
    svg.setAttribute('viewBox', `${x0} ${y0} ${vw} ${vh}`);
    padrao.setAttribute('patternTransform', `scale(${1 / k})`);

    for (const it of itens) {
      const [x, y, w, h] = it.r.rect;
      const fora = x > x0 + vw || y > y0 + vh || x + w < x0 || y + h < y0 || Math.max(w, h) * k < 1.5;
      if (fora === it.visivel) { it.visivel = !fora; it.g.style.display = fora ? 'none' : ''; }
      if (fora) continue;
      const a = dimsAnt ? dimsAnt[it.r.idx] : 1, b = dims ? dims[it.r.idx] : 1;
      let op = a + (b - a) * hl;
      if (hv || hvAnt) { const ha = hvAnt ? hvAnt[it.r.idx] : 1, hb = hv ? hv[it.r.idx] : 1; op *= ha + (hb - ha) * hl; }
      op = Math.round(op * 100) / 100;
      if (op !== it.op) { it.op = op; it.g.style.opacity = op; }
      const fadeHost = (it.hostFade ? 1 - suave(200, 340, w * k) : 1);
      const fadeCont = it.r.isContainer ? 1 - suave(1100, 1500, Math.min(w, h) * k) : 1;
      for (const tx of it.textos) {
        const px = tx.h * k;
        const o = suave(LOD_MIN, LOD_FULL, px) * (1 - suave(LOD_BIG_START, LOD_BIG_END, px)) * fadeHost * fadeCont;
        const q = Math.round(o * 50) / 50;
        if (q !== tx.op) { tx.op = q; tx.e.style.opacity = q; tx.e.style.display = q <= 0 ? 'none' : ''; }
      }
    }

    for (const [id, f] of fluxos) {
      const on = flowAlpha > 0.001 && flowsAtivos.includes(id);
      if (on !== f.vis) { f.vis = on; f.g.setAttribute('visibility', on ? 'visible' : 'hidden'); }
      if (!on) continue;
      f.g.style.opacity = flowAlpha;
      for (const c of f.camadas) c.e.style.strokeDashoffset = -(t * vel) - f.fase + c.l;   // andamento vem do tempo da timeline
      f.ponta.setAttribute('transform', `translate(${f.fim[0]} ${f.fim[1]}) rotate(${f.ang}) scale(${1 / k})`);
      if (f.rot) {
        f.rot.setAttribute('x', f.mx); f.rot.setAttribute('y', f.my - 12 / k);
        f.rot.setAttribute('font-size', 24 / k);
      }
    }
  }

  return { svg, atualiza };
}
