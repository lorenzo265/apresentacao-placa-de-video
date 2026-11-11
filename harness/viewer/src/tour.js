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
import { criaCotas } from './cotas.js';
import { criaCaminhos } from './caminhos3d.js';
import MERGULHO from './mergulho.json';

const COR_CAMINHO = { energy: '#ffb020', data: '#35d0e6', heat: '#ff6a3d' };

export function criaTour({ dados, palco, cena, capture, corte, tema = null }) {
  const { storyboard, textos, world, medidas } = dados;

  // Retângulo de mundo (diagramas) na tela para um enquadramento {cx, cy, lw}, e o inverso: o
  // enquadramento que põe um retângulo de mundo num retângulo da tela (escala uniforme pela largura).
  const retNaTela = ([x, y, w, h], vb) => {
    const vw = Math.exp(vb.lw), vh = vw * STAGE_H / STAGE_W, kk = STAGE_W / vw;
    return [(x - (vb.cx - vw / 2)) * kk, (y - (vb.cy - vh / 2)) * kk, w * kk, h * kk];
  };
  const vbPara = ([x, y, w], [qx, qy, qw]) => {
    const kk = qw / w, vw = STAGE_W / kk, vh = vw * STAGE_H / STAGE_W;
    return { cx: x - qx / kk + vw / 2, cy: y - qy / kk + vh / 2, lw: Math.log(vw) };
  };
  /** Retângulo (px) com a proporção asp, centrado em r e ajustado por dentro dele. */
  const ajustaDentro = (r, asp) => {
    let w = r[2], h = w / asp;
    if (h > r[3]) { h = r[3]; w = h * asp; }
    return [r[0] + (r[2] - w) / 2, r[1] + (r[3] - h) / 2, w, h];
  };
  // Mergulho (src/mergulho.json): pose final da câmera 3D para o nó do diagrama terminar onde o
  // enquadramento do beat o põe, com a peça projetada por baixo dele.
  function mergulho(b, camAnt, nivel, vbAlvo) {
    const cfg = MERGULHO.diagramas[b.view?.diagram];
    const no = cfg && world.byId.get(cfg.no);
    if (!cfg || !no || !cena.temPeca(cfg.peca)) return null;
    cena.caixaEm(cfg.peca, nivel);
    const f = cena.faceDe(cfg.peca);
    if (!f) return null;
    const [c0, c1, c2] = f.cantos;
    const asp = Math.hypot(c1.x - c0.x, c1.y - c0.y) / Math.max(1e-6, Math.hypot(c2.x - c1.x, c2.y - c1.y));
    const F = retNaTela(no.rect, vbAlvo);
    // a peça projetada é o retângulo em que o nó (proporção dele) cabe por dentro
    const W = no.rect[2] / no.rect[3] >= asp ? F[2] : F[3] * asp;
    const H = W / asp;
    const cam = cena.poseMergulho({ peca: cfg.peca, rect: [F[0] + F[2] / 2 - W / 2, F[1] + F[3] / 2 - H / 2, W, H], fov: cfg.fov ?? camAnt.fov, inclinacao: cfg.inclinacao_graus ?? 8, de: camAnt });
    if (!cam) return null;
    // o que fica sobre a peça (cooler, carcaça) sai do caminho da câmera
    const afasta = cfg.afasta ? cena.preparaAfastamento({ peca: cfg.peca, de: camAnt, recuo: cfg.afasta.recuo_mm, sobe: cfg.afasta.sobe_mm }) : null;
    return { cam, ease: cfg.ease, cfg, no, afasta };
  }
  const { tl, S, beats, duration } = constroiTimeline({ storyboard, corte, world, mergulho: cena.blockout ? null : mergulho });
  if (!beats.length) throw new Error(`corte "${corte}" não tem beats ready`);

  const camadaDiag = criaCamadaDiagramas(palco, world, tema?.diagramas ?? null);
  const cotas = tema?.cena?.cotas ? criaCotas(palco, cena, medidas) : null;
  const chamada = criaChamada(palco);
  const corLinha = tema?.linha ?? '#f1f4f8';
  const cabecalho = criaCabecalho(palco);
  // selo da vitrine: só enquanto alguma peça está fora da posição (a procedência do beat não muda)
  const seloVit = document.createElement('div');
  seloVit.id = 'selo-vitrine';
  seloVit.innerHTML = '<span class="selo s-illustrative"><svg viewBox="0 0 16 16" width="22" height="22"><path d="M8,2 L14,8 L8,14 L2,8 Z"/></svg>Ilustrativo: peça fora da posição</span>';
  palco.appendChild(seloVit);
  const caminhos = criaCaminhos(palco, cena);
  if (!cena.blockout) caminhos.avisos.forEach((a) => console.warn(`[3D] ${a}`));

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

  // Destaque em 3D: fatores por malha de cada beat. Beat de diagrama herda o do último beat 3D.
  const dims3d = [];
  {
    let ult = null;
    beats.forEach((e, i) => {
      const b = e.beat;
      if (b.level <= 1) {
        const partes = [b.part, ...(b.highlight ?? []).filter((h) => !h.startsWith('tag:'))].filter(Boolean);
        const tags = (b.highlight ?? []).filter((h) => h.startsWith('tag:')).map((h) => h.slice(4));
        for (const p of partes) if (!cena.temPeca(p) && cena.temAncora('card')) console.warn(`[${b.id}] peça ${p} não existe no GLB; sem esmaecer`);
        ult = cena.fatoresDe(partes, tags);
      }
      dims3d[i] = ult;
      if (b.overlay && !caminhos.tem(b.overlay.path)) console.warn(`[3D] caminho ${b.overlay.path} sem mapeamento em caminhos.json (beat ${b.id}); nada desenhado`);
    });
  }

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

  // vitrine: sem pos explícita, a pose é calculada uma vez por beat a partir da câmera dele
  const posesVit = new Map();
  function vitrineDe(b) {
    if (b.vitrine.pos) return {};
    if (!posesVit.has(b.id)) posesVit.set(b.id, cena.poseVitrine(b.vitrine, b.camera, b.callout?.box) ?? {});
    return posesVit.get(b.id);
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
    const expl = q(S.expl);
    const mix = q(S.mix), hl = q(S.hl), line = q(S.line), box = q(S.box), flow = q(S.flow);
    const cam = Object.fromEntries(Object.entries(S.cam).map(([k2, v]) => [k2, q(v)]));
    qVb = vb;
    const i = ativo(t), e = beats[i], b = e.beat;
    chamada.define(b, textoDe(b.id));
    const ocultar3d = mix >= 0.999;
    // mergulho: na entrada do beat a câmera 3D anda mesmo com o canvas quase oculto (o diagrama segue a peça)
    const mergulhando = !!e.mergulho && t < e.entrada && !cena.blockout;
    cena.renderer.domElement.style.visibility = ocultar3d ? 'hidden' : 'visible';
    cena.renderer.domElement.style.opacity = 1 - mix;
    if (ocultar3d && !mergulhando) seloVit.style.visibility = 'hidden';
    if (!ocultar3d || mergulhando) {
      const af = e.mergulho?.afasta ? { g: e.mergulho.afasta.g, f: q(S.afasta) } : null;
      const vAnt = i > 0 ? beats[i - 1].beat.vitrine : null;
      const vit = [];
      if (b.vitrine) vit.push({ ...b.vitrine, ...vitrineDe(b), k: q(S.vit) });
      if (vAnt && vAnt.peca !== b.vitrine?.peca) vit.push({ ...vAnt, ...vitrineDe(beats[i - 1].beat), k: q(S.vitR) });
      cena.aplicaEstado(expl, i > 0 ? dims3d[i - 1] : null, dims3d[i], hl, af, vit);
      const kv = Math.max(0, ...vit.map((v) => v.k));
      seloVit.style.opacity = Math.min(1, kv * 2) * (1 - mix);
      seloVit.style.visibility = kv > 0.001 && mix < 0.999 ? 'visible' : 'hidden';
      if (!livre) cena.ajustaCamera(cam);
      // na captura, a cena só acumula quadros fora da entrada do beat (o estado 3D só muda nela)
      if (!ocultar3d) cena.desenha({ parado: !capture || t > e.entrada + 1e-6 });
    }
    if (mergulhando) {
      // o nó do diagrama fica colado à peça projetada (proporção do nó, por dentro dela) e, no fim da
      // entrada, passa suavemente para o enquadramento do beat
      const { cfg, no } = e.mergulho;
      const f = cena.faceDe(cfg.peca);
      const pts = f?.cantos.map((p) => cena.projeta([p.x, p.y, p.z]));
      if (pts && pts.every(Boolean)) {
        const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
        const P = [Math.min(...xs), Math.min(...ys), Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)];
        const vm = vbPara(no.rect, ajustaDentro(P, no.rect[2] / no.rect[3]));
        const tau = (t - e.start) / Math.max(1e-6, e.entrada - e.start);
        const a0 = cfg.cola_ate ?? 0.8;
        const u = Math.min(1, Math.max(0, (tau - a0) / Math.max(1e-6, 1 - a0)));
        const w = u * u * (3 - 2 * u);
        qVb = { cx: q(vm.cx + (vb.cx - vm.cx) * w), cy: q(vm.cy + (vb.cy - vm.cy) * w), lw: q(vm.lw + (vb.lw - vm.lw) * w) };
      }
    }
    caminhos.atualiza({ caminho: !ocultar3d && b.level <= 1 ? b.overlay?.path ?? null : null, via: q(S.via), alfa: q(S.viaA) * (1 - mix), t });
    camadaDiag.atualiza({
      vb: qVb, dims: dimsDe(i), dimsAnt: dimsDe(i - 1), hl,
      flowsAtivos: b.flows ?? [], flowAlpha: flow, t, visivel: mix,
      alvo: b.level >= 2 ? b.callout?.anchor ?? null : null,
      // vindo do 3D não havia diagrama na tela: os vizinhos já entram apagados (não há de onde apagar)
      vista: b.view?.diagram ?? null, vistaAnt: i > 0 ? beats[i - 1].beat.view?.diagram ?? (beats[i - 1].beat.level <= 1 ? b.view?.diagram ?? null : null) : null,
    });
    cotas?.atualiza({ visivel: ocultar3d ? 0 : (1 - mix) * Math.max(0, 1 - expl / 0.25) });
    chamada.atualiza(b, ancoraDe(b), line, box, COR_CAMINHO[b.overlay?.path] ?? corLinha);
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
    beats: beats.map(({ id, start, entrada, settle, end, level, mergulho: m }) => ({ id, start, entrada, settle, end, level, mergulho: !!m })),
    textoDe,
    /** Estado quantizado da cena 3D no instante atual (para os testes). */
    estado: () => ({ expl: Math.round(S.expl * 1e6) / 1e6, mix: Math.round(S.mix * 1e6) / 1e6, via: Math.round(S.via * 1e6) / 1e6, acum: cena.acumulacao?.() ?? null, cam: { ...S.cam }, vb: { ...qVb } }),
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
