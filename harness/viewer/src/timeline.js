// Timeline mestre (GSAP), pausada. Todo estado animado é função do tempo dela.
// Por beat: entrada (câmera/enquadramento + destaque), chamada (linha e caixa), hold, saída.
import gsap from 'gsap';
import { resolve, uniao } from './world.js';
import { STAGE_W, STAGE_H, safeRect, BOX_IN, LINE_OUT_DEFAULT } from './layout.js';

import CAMINHOS from './caminhos.json';

const VIA_IN = CAMINHOS.estilo.revela_s;      // s para o caminho na placa se desenhar inteiro, depois da entrada

const EASE_PADRAO = 'power2.inOut';
const boa = (e) => (typeof e === 'string' && gsap.parseEase(e) ? e : EASE_PADRAO);

/** Seleciona os beats ready do corte, na ordem do array. */
export function beatsDoCorte(storyboard, corte) {
  const def = storyboard.cuts[corte];
  if (!def) throw new Error(`corte desconhecido: ${corte}`);
  const prontos = storyboard.beats.filter((b) => b.status === 'ready');
  if (def.beats) {
    const set = new Set(def.beats);
    return prontos.filter((b) => set.has(b.id));
  }
  return prontos.filter((b) => b.priority <= def.max_priority);
}

/** Enquadramento de um beat de diagrama: {cx, cy, lw}. A caixa de texto reserva uma coluna da tela. */
export function enquadra(world, beat) {
  const v = beat.view;
  const alvo = uniao(resolve(world, v.focus, v.diagram));
  if (!alvo) { console.warn(`[${beat.id}] foco ${v.focus} não resolve em ${v.diagram}`); return null; }
  const p = v.padding ?? 0.08;
  const fw = alvo[2] * (1 + 2 * p), fh = alvo[3] * (1 + 2 * p);
  const [sx, sy, sw, sh] = safeRect(beat.callout);
  const k = Math.min(sw / fw, sh / fh);                // px por unidade do mundo
  const vw = STAGE_W / k;
  // o centro do foco vai para o centro da área livre
  const fcx = alvo[0] + alvo[2] / 2, fcy = alvo[1] + alvo[3] / 2;
  const cx = fcx - ((sx + sw / 2) - STAGE_W / 2) / k;
  const cy = fcy - ((sy + sh / 2) - STAGE_H / 2) / k;
  return { cx, cy, lw: Math.log(vw) };
}

/**
 * mergulho(beat, camAnterior, nivel, vbAlvo): para um beat de diagrama que entra vindo do 3D, a pose de câmera
 * 3D do mergulho (a câmera avança até a peça enquanto o diagrama entra) ou null. Configuração do
 * viewer (src/mergulho.json), não do storyboard.
 */
export function constroiTimeline({ storyboard, corte, world, mergulho = null }) {
  const beats = beatsDoCorte(storyboard, corte);
  const S = {
    cam: { px: 0, py: 0, pz: 0, tx: 0, ty: 0, tz: 0, fov: 30 },
    vb: { cx: 0, cy: 0, lw: Math.log(1600) },
    mix: 0, hl: 1, line: 0, box: 0, flow: 0, expl: 0,
    via: 0, viaA: 0,     // caminho na placa (overlay.path): avanço do traçado e opacidade
    afasta: 0,           // mergulho: fração do afastamento das peças que tapam a peça-alvo
  };
  const tl = gsap.timeline({ paused: true, defaults: { immediateRender: false } });
  const entradas = [];

  const camDe = (c) => ({ px: c.pos[0], py: c.pos[1], pz: c.pos[2], tx: c.target[0], ty: c.target[1], tz: c.target[2], fov: c.fov });
  let cam = null;      // último estado de câmera 3D
  let vb = null;       // último enquadramento de diagrama
  let mix = null;      // 0 = 3D, 1 = diagrama
  let nivel = 0;       // nível de explosão no fim do beat anterior (0 = montada)
  let cursor = 0;
  const nivelDe = (e) => (e === 'assembled' ? 0 : Number(String(e).slice(1)));

  beats.forEach((b, i) => {
    const start = cursor;
    const diag = b.level >= 2;
    let mergulhoDe = null;
    tl.set(S, { afasta: 0 }, start);
    let dur, ease;
    if (diag) {
      dur = b.view.duration; ease = boa(b.view.ease);
      const alvo = enquadra(world, b) ?? vb ?? S.vb;
      const de = vb && mix === 1 ? vb : { ...alvo, lw: alvo.lw + 0.12 };
      if (i === 0) { Object.assign(S.vb, alvo); }
      const mixDe = mix ?? 1;
      if (i === 0) S.mix = 1;
      tl.fromTo(S.vb, { ...de }, { ...alvo, duration: dur, ease }, start);
      // mergulho: vindo do 3D, a câmera avança até a peça enquanto o diagrama entra alinhado a ela
      const m = mixDe !== 1 && cam && mergulho ? mergulho(b, cam, nivel, alvo) : null;
      if (mixDe !== 1) {
        // no mergulho a fusão começa depois (a peça real fica à vista enquanto a câmera desce)
        const [m0, m1] = m?.cfg?.mistura ?? [0, 1];
        tl.fromTo(S, { mix: mixDe }, { mix: 1, duration: dur * (m1 - m0), ease: 'power1.inOut' }, start + dur * m0);
      }
      {
        if (m) {
          tl.fromTo(S.cam, { ...cam }, { ...m.cam, duration: dur, ease: boa(m.ease) }, start);
          if (m.afasta) tl.fromTo(S, { afasta: 0 }, { afasta: 1, duration: dur * (m.cfg?.afasta_ate ?? 0.6), ease: 'power2.inOut' }, start);
          mergulhoDe = { ...m, de: cam };
          cam = m.cam;
        }
      }
      vb = alvo; mix = 1;
    } else {
      dur = b.camera.duration; ease = boa(b.camera.ease);
      const alvo = camDe(b.camera);
      const de = cam ?? alvo;
      if (i === 0) Object.assign(S.cam, alvo);
      tl.fromTo(S.cam, { ...de }, { ...alvo, duration: dur, ease }, start);
      const mixDe = mix ?? 0;
      if (mixDe !== 0) tl.fromTo(S, { mix: mixDe }, { mix: 0, duration: dur, ease: 'power1.inOut' }, start);
      cam = alvo; mix = 0;
    }
    // explosão: do nível anterior ao pedido, na entrada do beat (beat sem explode_state mantém o anterior)
    const alvoNivel = b.explode_state != null ? nivelDe(b.explode_state) : nivel;
    if (i === 0) S.expl = alvoNivel;
    tl.fromTo(S, { expl: nivel }, { expl: alvoNivel, duration: dur, ease: diag ? 'none' : ease }, start);
    nivel = alvoNivel;
    // destaque: 0 -> 1 durante a entrada
    tl.fromTo(S, { hl: 0 }, { hl: 1, duration: dur, ease: 'none' }, start);
    tl.set(S, { line: 0, box: 0, flow: 0 }, start);

    const c = b.callout;
    const lineIn = Math.max(0.001, c?.line_in ?? 0);
    const lineOut = Math.max(0.001, c?.line_out ?? LINE_OUT_DEFAULT);
    const chamada = c ? Math.max(lineIn, BOX_IN) : BOX_IN;
    const tEntrada = start + dur;
    const settle = tEntrada + chamada;
    if (c) tl.fromTo(S, { line: 0 }, { line: 1, duration: lineIn, ease: 'power2.out' }, tEntrada);
    tl.fromTo(S, { box: 0 }, { box: 1, duration: BOX_IN, ease: 'power1.out' }, tEntrada);
    if (b.flows?.length) tl.fromTo(S, { flow: 0 }, { flow: 1, duration: BOX_IN, ease: 'none' }, tEntrada);
    // caminho na placa (overlay.path em beat 3D): o traço avança da origem ao fim depois da entrada
    const via = b.level <= 1 && b.overlay?.path;
    if (via) {
      tl.set(S, { via: 0, viaA: 0 }, start);
      tl.fromTo(S, { viaA: 0 }, { viaA: 1, duration: BOX_IN, ease: 'power1.out' }, tEntrada);
      tl.fromTo(S, { via: 0 }, { via: 1, duration: VIA_IN, ease: 'power1.inOut' }, tEntrada);
    } else tl.set(S, { via: 0, viaA: 0 }, start);
    const tSaida = settle + b.hold;
    const saida = c ? lineOut : LINE_OUT_DEFAULT;
    if (c) tl.fromTo(S, { line: 1 }, { line: 0, duration: saida, ease: 'power2.in' }, tSaida);
    tl.fromTo(S, { box: 1 }, { box: 0, duration: saida, ease: 'power1.in' }, tSaida);
    if (b.flows?.length) tl.fromTo(S, { flow: 1 }, { flow: 0, duration: saida, ease: 'none' }, tSaida);
    if (via) tl.fromTo(S, { viaA: 1 }, { viaA: 0, duration: saida, ease: 'power1.in' }, tSaida);
    const end = tSaida + saida;
    entradas.push({ id: b.id, start, entrada: tEntrada, settle, end, level: b.level, beat: b, mergulho: mergulhoDe });
    cursor = end;
  });
  tl.set({}, {}, cursor);        // fixa a duração
  return { tl, S, beats: entradas, duration: cursor };
}
