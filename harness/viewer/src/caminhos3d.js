// Caminhos na placa 3D (overlay.path dos beats a2.9, a2.10 e a2.11): uma linha de luz que percorre as
// peças do caminho, na linguagem dos fluxos dos diagramas no Keynote (núcleo claro, cauda e halo na cor
// do caminho). O mapeamento de peças está em caminhos.json; os pontos saem das caixas das peças no GLB a
// cada quadro (acompanham a explosão) e são projetados para a tela. Camada SVG sobre o canvas 3D, fora
// da acumulação de quadros. Tudo é função do tempo da timeline: o mesmo instante dá o mesmo desenho.
// Sem traço tracejado nem filtro: os pulsos são trechos de polilinha calculados aqui (determinismo).
import DADOS from './caminhos.json';
import { STAGE_W, STAGE_H } from './layout.js';

const NS = 'http://www.w3.org/2000/svg';
const el = (tag, attrs, pai) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs ?? {})) e.setAttribute(k, v);
  if (pai) pai.appendChild(e);
  return e;
};
const CLASSE = { energy: 'v-energy', data: 'v-data', heat: 'v-heat' };
const r1 = (x) => Math.round(x * 10) / 10;

/** Trecho [a, b] (comprimento de arco, px) de uma polilinha com comprimentos acumulados; '' se vazio. */
function subPolilinha(pts, cum, a, b) {
  const L = cum[cum.length - 1];
  a = Math.max(0, a); b = Math.min(L, b);
  if (b - a < 0.5) return '';
  const em = (s) => {
    let i = 1;
    while (i < cum.length - 1 && cum[i] < s) i++;
    const seg = cum[i] - cum[i - 1] || 1;
    const t = (s - cum[i - 1]) / seg;
    return [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t, i];
  };
  const [ax, ay, ia] = em(a), [bx, by, ib] = em(b);
  let d = `M${r1(ax)},${r1(ay)}`;
  for (let i = ia; i < ib; i++) d += ` L${r1(pts[i][0])},${r1(pts[i][1])}`;
  return `${d} L${r1(bx)},${r1(by)}`;
}

export function criaCaminhos(palco, cena) {
  const est = DADOS.estilo;
  const svg = el('svg', { id: 'caminhos', width: STAGE_W, height: STAGE_H, viewBox: `0 0 ${STAGE_W} ${STAGE_H}` });
  const chamada = palco.querySelector('#chamada');
  if (chamada) palco.insertBefore(svg, chamada); else palco.appendChild(svg);
  svg.style.visibility = 'hidden';
  const avisos = [];

  // Monta a árvore de cada caminho: trechos na ordem do arquivo; o pai vem antes do filho.
  const caminhos = new Map();
  for (const [nome, c] of Object.entries(DADOS.caminhos)) {
    const g = el('g', { class: `via ${CLASSE[nome] ?? ''}` }, svg);
    const trechos = [];
    const porId = new Map();
    for (const t of c.trechos) {
      let pai = null, idx = 0;
      if (t.de) {
        const [pid, pi] = t.de.split(':');
        pai = porId.get(pid) ?? null;
        idx = Number(pi ?? 0);
        if (!pai) avisos.push(`caminho ${nome}: trecho ${t.id} nasce em ${t.de}, que não existe`);
      }
      const gt = el('g', { class: 'trecho' }, g);
      const tr = {
        def: t, pai, idx, fim: t.fim ?? 'no',
        base: el('path', { class: 'v-base' }, gt),
        brilho: el('path', { class: 'v-brilho' }, gt),
        pulsos: el('g', {}, gt),
        marcas: el('g', {}, gt),
        pts: [], cum: [], o: 0,
      };
      porId.set(t.id, tr);
      trechos.push(tr);
    }
    const gFim = el('g', { class: 'v-fins' }, g);
    caminhos.set(nome, { g, trechos, gFim });
  }
  // Peças e nós que faltam no GLB: aviso uma vez, e o ponto é pulado.
  for (const [nome, c] of caminhos) {
    for (const tr of c.trechos) {
      for (const p of tr.def.pontos) {
        const ok = p.no ? cena.temAncora(p.no) : cena.temPeca(p.peca);
        if (!ok) avisos.push(`caminho ${nome}: ${p.no ?? p.peca} não existe no GLB; ponto pulado`);
      }
    }
  }

  /** Ponto 3D (mm) de uma definição de ponto, no estado atual da explosão. */
  function ponto3d(p) {
    const c = p.no ? cena.caixaNo(p.no) : cena.caixaPeca(p.peca);
    if (!c) return null;
    const [fx, fy, fz] = p.em ?? [0.5, 0.5, 0.5];
    return [c.min.x + (c.max.x - c.min.x) * fx, c.min.y + (c.max.y - c.min.y) * fy, c.min.z + (c.max.z - c.min.z) * fz];
  }

  // Elementos reaproveitados de um quadro para o outro (pulsos e marcas), criados sob demanda.
  function pool(pai, tag, cls) {
    const itens = [];
    let n = 0;
    return {
      inicio() { n = 0; },
      pega(attrs) {
        let e = itens[n];
        if (!e) { e = el(tag, { class: cls }, pai); itens.push(e); }
        for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
        e.style.display = '';
        n++;
        return e;
      },
      fim() { for (let i = n; i < itens.length; i++) itens[i].style.display = 'none'; },
    };
  }
  for (const c of caminhos.values()) {
    for (const tr of c.trechos) {
      tr.pCauda = est.cauda_px.map(() => pool(tr.pulsos, 'path', 'v-cauda'));
      tr.pHalo = pool(tr.pulsos, 'path', 'v-halo');
      tr.pNucleo = pool(tr.pulsos, 'path', 'v-nucleo');
      tr.pMarca = pool(tr.marcas, 'circle', 'v-marca');
      tr.pAnel = pool(tr.marcas, 'circle', 'v-anel');
    }
    c.pFim = pool(c.gFim, 'circle', 'v-dissipa');
    c.pFrente = pool(c.gFim, 'circle', 'v-frente');
  }

  let ativo = null;
  /**
   * caminho: 'energy' | 'data' | 'heat' | null; via: avanço do traçado (0 a 1); alfa: opacidade;
   * t: tempo da timeline (s), que move os pulsos.
   */
  function atualiza({ caminho, via, alfa, t }) {
    const c = caminho ? caminhos.get(caminho) : null;
    if (!c || alfa <= 0.001) {
      if (ativo) { svg.style.visibility = 'hidden'; ativo = null; }
      return;
    }
    if (ativo !== c) {
      for (const x of caminhos.values()) x.g.style.display = x === c ? '' : 'none';
      svg.style.visibility = 'visible';
      ativo = c;
    }
    svg.style.opacity = alfa;

    // 1. pontos na tela e comprimentos (px); o deslocamento de cada trecho é o arco até onde nasce
    let total = 0;
    for (const tr of c.trechos) {
      // índice do ponto de nascimento na polilinha do pai (que começa pelo ponto de junção, se tiver pai)
      const pi = tr.pai ? Math.min(tr.idx + (tr.pai.pai ? 1 : 0), tr.pai.pts.length - 1) : 0;
      const ini = tr.pai ? tr.pai.pts[pi] ?? null : null;
      tr.o = tr.pai ? tr.pai.o + (tr.pai.cum[pi] ?? 0) : 0;
      const pts = [], marca = [];
      if (ini) { pts.push(ini); marca.push(false); }
      for (const p of tr.def.pontos) {
        const q = ponto3d(p);
        const s = q && cena.projeta(q);
        if (!s) continue;
        pts.push(s); marca.push(p.marca !== false);
      }
      const cum = [0];
      for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
      tr.pts = pts; tr.cum = cum; tr.marca = marca;
      total = Math.max(total, tr.o + (cum[cum.length - 1] ?? 0));
    }

    // 2. desenho: base revelada, pulsos que correm e nós; a frente do traçado brilha enquanto avança
    const D = via * total;                         // até onde o traçado chegou (arco global, px)
    const P = est.periodo_px, vel = est.vel_px_s;
    const fase = (t * vel) % P;
    c.pFim.inicio(); c.pFrente.inicio();
    for (const tr of c.trechos) {
      for (const p of tr.pCauda) p.inicio();
      tr.pHalo.inicio(); tr.pNucleo.inicio(); tr.pMarca.inicio(); tr.pAnel.inicio();
      const L = tr.cum[tr.cum.length - 1] ?? 0;
      const vis = Math.min(L, Math.max(0, D - tr.o));
      const d = tr.pts.length >= 2 ? subPolilinha(tr.pts, tr.cum, 0, vis) : '';
      tr.base.setAttribute('d', d);
      tr.brilho.setAttribute('d', d);
      if (vis > 0.5) {
        // pulsos: cabeças em s = fase + k P no arco global; cada uma com caudas em camadas e núcleo claro
        const k0 = Math.floor((tr.o - fase) / P);
        for (let k = k0; ; k++) {
          const sg = fase + k * P;                 // cabeça no arco global
          const s = sg - tr.o;                     // no arco do trecho
          if (s - est.cauda_px[0] > vis) break;
          if (s < 0) continue;
          const sh = Math.min(s, vis);
          est.cauda_px.forEach((l, j) => {
            const dd = subPolilinha(tr.pts, tr.cum, s - l, sh);
            if (dd) tr.pCauda[j].pega({ d: dd, opacity: est.cauda_op[j] });
          });
          if (s <= vis) {
            const dh = subPolilinha(tr.pts, tr.cum, s - est.halo_px, s);
            if (dh) tr.pHalo.pega({ d: dh });
            const dn = subPolilinha(tr.pts, tr.cum, s - est.nucleo_px, s);
            if (dn) tr.pNucleo.pega({ d: dn });
          }
        }
      }
      // nós luminosos nos pontos já alcançados
      tr.pts.forEach((p, i) => {
        if (!tr.marca[i] || tr.cum[i] > vis + 0.5) return;
        const cresce = Math.min(1, (vis - tr.cum[i]) / 40 + 0.35);
        tr.pAnel.pega({ cx: r1(p[0]), cy: r1(p[1]), r: r1(11 * cresce) });
        tr.pMarca.pega({ cx: r1(p[0]), cy: r1(p[1]), r: r1(4.5 * cresce) });
      });
      // frente do traçado
      if (vis > 0.5 && vis < L - 0.5) {
        const dd = subPolilinha(tr.pts, tr.cum, vis - 1, vis);
        const m = /L([-\d.]+),([-\d.]+)$/.exec(dd);
        if (m) c.pFrente.pega({ cx: m[1], cy: m[2], r: 7 });
      }
      // fim que dissipa: dois anéis que se abrem e somem, defasados (sem direção)
      if (tr.fim === 'dissipa' && L > 0 && vis >= L - 0.5) {
        const [x, y] = tr.pts[tr.pts.length - 1];
        for (let j = 0; j < 3; j++) {
          const u = ((t * 0.55 + j / 3) % 1 + 1) % 1;
          c.pFim.pega({ cx: r1(x), cy: r1(y), r: r1(8 + 46 * u), opacity: Math.round((1 - u) * (1 - u) * 100) / 100 });
        }
      }
      for (const p of tr.pCauda) p.fim();
      tr.pHalo.fim(); tr.pNucleo.fim(); tr.pMarca.fim(); tr.pAnel.fim();
    }
    c.pFim.fim(); c.pFrente.fim();
  }

  return { atualiza, avisos, tem: (n) => caminhos.has(n) };
}
