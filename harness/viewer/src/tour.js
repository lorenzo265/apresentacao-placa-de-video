// Junta tudo: timeline mestre, cena 3D, camada de diagramas, chamada, cabeçalho, controles.
// Expõe window.__tour (ver README). O que aparece é função só de tl.time().
import gsap from 'gsap';
import { constroiTimeline } from './timeline.js';
import { resolve, uniao, fatoresDestaque } from './world.js';
import { criaCamadaDiagramas } from './diagrams.js';
import { criaChamada } from './callout.js';
import { criaCabecalho } from './header.js';
import { criaControles } from './controls.js';
import { STAGE_W, STAGE_H, boxPlacement } from './layout.js';

const COR_CAMINHO = { energy: '#ffb020', data: '#35d0e6', heat: '#ff6a3d' };

export function criaTour({ dados, palco, cena, capture, corte }) {
  const { storyboard, textos, world } = dados;
  const { tl, S, beats, duration } = constroiTimeline({ storyboard, corte, world });
  if (!beats.length) throw new Error(`corte "${corte}" não tem beats ready`);

  const camadaDiag = criaCamadaDiagramas(palco, world);
  const chamada = criaChamada(palco);
  const cabecalho = criaCabecalho(palco);

  const textoDe = (id) => {
    const t = textos.beats[id];
    if (!t) { console.warn(`[${id}] sem texto em beats.json`); return { headline: id, caption: '', fala: '', source_line: '' }; }
    return t;
  };
  const dims = new Map();
  const dimsDe = (i) => {
    if (i < 0) return null;
    if (!dims.has(i)) dims.set(i, fatoresDestaque(world, beats[i].beat));
    return dims.get(i);
  };
  const ativo = (t) => { let k = 0; for (let i = 0; i < beats.length; i++) if (beats[i].start <= t + 1e-9) k = i; return k; };

  let qVb = S.vb;      // enquadramento quantizado do quadro atual
  const k = () => STAGE_W / Math.exp(qVb.lw);
  const mundoParaTela = (wx, wy) => {
    const kk = k(), vw = Math.exp(qVb.lw), vh = vw * STAGE_H / STAGE_W;
    return [(wx - (qVb.cx - vw / 2)) * kk, (wy - (qVb.cy - vh / 2)) * kk];
  };
  const avisados = new Set();
  const avisaUma = (m) => { if (!avisados.has(m)) { avisados.add(m); console.warn(m); } };

  function ancoraDe(b) {
    const c = b.callout;
    if (!c) return null;
    if (b.level >= 2) {
      const r = world.byId.get(c.anchor);
      if (!r) { avisaUma(`[${b.id}] âncora ${c.anchor} não existe nos diagramas; sem linha`); return null; }
      // Centro do nó; se o nó for largo na tela, o ponto vai para a borda voltada para a caixa,
      // para a linha não atravessar o rótulo.
      const [sx, sy] = mundoParaTela(r.cx, r.cy);
      const larg = r.rect[2] * k();
      if (larg <= 140) return [sx, sy];
      return [sx + (boxPlacement(c).side === 'left' ? -1 : 1) * larg / 2, sy];
    }
    if (!cena.temAncora(c.anchor)) { avisaUma(`[${b.id}] âncora ${c.anchor} não existe na cena 3D; sem linha`); return null; }
    return cena.ancoraTela(c.anchor);
  }
  function focoDe(b) {
    if (b.level < 2 || !b.view) return null;
    const u = uniao(resolve(world, b.view.focus, b.view.diagram));
    if (!u) return null;
    const [x0, y0] = mundoParaTela(u[0], u[1]);
    return [x0, y0, u[2] * k(), u[3] * k()];
  }

  let livre = false;       // usuário orbitando com camera-controls
  let tocando = false;
  let paraEm = null;
  let disclaimerDe = (b) => (b.view ? world.diagrams.get(b.view.diagram)?.disclaimer ?? null : null);

  /** Desenha um quadro completo (3D, SVG e DOM) a partir do estado atual da timeline. */
  function desenha() {
    // Quantiza o estado: o mesmo instante dá o mesmo quadro, mesmo que a timeline chegue por
    // caminhos diferentes (erro de ponto flutuante na ordem de 1e-12 viraria um pixel diferente).
    const t = Math.round(tl.time() * 1e6) / 1e6;
    const q = (v) => Math.round(v * 1e6) / 1e6;
    const vb = { cx: q(S.vb.cx), cy: q(S.vb.cy), lw: q(S.vb.lw) };
    const mix = q(S.mix), hl = q(S.hl), line = q(S.line), box = q(S.box), flow = q(S.flow);
    const cam = Object.fromEntries(Object.entries(S.cam).map(([k2, v]) => [k2, q(v)]));
    qVb = vb;
    const i = ativo(t), e = beats[i], b = e.beat;
    chamada.define(b, textoDe(b.id));
    const ocultar3d = mix >= 0.999;
    cena.renderer.domElement.style.visibility = ocultar3d ? 'hidden' : 'visible';
    cena.renderer.domElement.style.opacity = 1 - mix;
    if (!ocultar3d) {
      if (!livre) cena.ajustaCamera(cam);
      cena.desenha();
    }
    camadaDiag.atualiza({
      vb, dims: dimsDe(i), dimsAnt: dimsDe(i - 1), hl,
      flowsAtivos: b.flows ?? [], flowAlpha: flow, t, visivel: mix,
    });
    chamada.atualiza(b, ancoraDe(b), line, box, COR_CAMINHO[b.overlay?.path] ?? '#f1f4f8');
    cabecalho.atualiza({
      beat: b, progresso: t / duration, disclaimer: disclaimerDe(b), mix,
      blockoutVisivel: !!cena.blockout,
    });
    controles?.atualiza();
  }

  function seek(t) {
    tocando = false; paraEm = null; livre = false; cena.controls.enabled = false;
    tl.time(Math.min(duration, Math.max(0, t)), false);
    desenha();
  }
  const settleDe = (i) => beats[i].settle;
  const tour = {
    ready: null,
    duration, fps: storyboard.fps, cut: corte,
    beats: beats.map(({ id, start, settle, end, level }) => ({ id, start, settle, end, level })),
    textoDe,
    seek,
    time: () => tl.time(),
    beatAtual: () => beats[ativo(tl.time())],
    playing: () => tocando,
    play() { livre = false; cena.controls.enabled = false; paraEm = null; tocando = true; },
    pause() { tocando = false; paraEm = null; cena.controls.enabled = !capture && S.mix < 0.5; },
    next() {
      const ref = tocando && paraEm != null ? paraEm : tl.time();
      const alvo = beats.findIndex((x) => x.settle > ref + 0.05);
      if (alvo < 0) return;
      livre = false; cena.controls.enabled = false;
      paraEm = beats[alvo].settle; tocando = true;
    },
    prev() {
      const i = Math.max(0, ativo(tl.time()) - 1);
      seek(settleDe(i)); this.pause();
    },
    goto(id) {
      const i = beats.findIndex((x) => x.id === id);
      if (i < 0) throw new Error(`beat ${id} não está no corte ${corte}`);
      seek(settleDe(i)); this.pause();
    },
    probe(id) {
      const i = beats.findIndex((x) => x.id === id);
      if (i < 0 || i !== ativo(tl.time())) return { erro: `beat ${id} não é o beat ativo` };
      const b = beats[i].beat;
      const a = ancoraDe(b);
      return {
        anchor: a, focus: focoDe(b), box: chamada.ret(),
        captionOverflow: chamada.overflow(), headline: textoDe(id).headline,
      };
    },
  };

  const draftBlocked = storyboard.beats.filter((b) => b.status !== 'ready' || !beats.some((x) => x.id === b.id));
  const controles = capture ? null : criaControles(palco, tour, { cortes: Object.keys(storyboard.cuts), corteAtual: corte, draftBlocked });

  // Orbitar livremente em beat 3D com o tour pausado
  cena.controls.enabled = false;
  cena.controls.addEventListener('controlstart', () => { livre = true; });

  if (!capture) {
    // Laço ao vivo: a timeline anda por seu próprio tempo; o resto só redesenha.
    gsap.ticker.add((_, ms) => {
      const dt = Math.min(0.1, ms / 1000);
      if (tocando) {
        const fim = paraEm ?? duration;
        const t = Math.min(fim, tl.time() + dt);
        tl.time(t, false);
        if (t >= fim) { tocando = false; paraEm = null; cena.controls.enabled = S.mix < 0.5; }
      }
      if (livre) cena.controls.update(dt);
      desenha();
    });
  }

  tour.ready = (async () => {
    await Promise.all(['400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter', '400 20px "JetBrains Mono"', '500 20px "JetBrains Mono"']
      .map((f) => document.fonts.load(f)));
    await document.fonts.ready;
    // As larguras de texto dependem das fontes: refaz o encaixe dos rótulos se preciso (já medido após o load).
    tl.time(0, false);
    desenha();
    window.__tourReady = true;
  })();
  return tour;
}
