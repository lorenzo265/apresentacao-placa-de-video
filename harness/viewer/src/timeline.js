// Timeline mestre (GSAP), pausada. Todo estado animado é função do tempo dela.
// Por beat: entrada (câmera/enquadramento + destaque), chamada (linha e caixa), hold, saída.
import gsap from 'gsap';
import { resolve, uniao } from './world.js';
import { STAGE_W, STAGE_H, safeRect, BOX_IN, LINE_OUT_DEFAULT } from './layout.js';

import CAMINHOS from './caminhos.json';

const VIA_IN = CAMINHOS.estilo.revela_s;      // s para o caminho na placa se desenhar inteiro, depois da entrada

const EASE_PADRAO = 'power2.inOut';

/**
 * Câmera em arco orbital: o alvo anda em linha reta e a posição gira em torno dele em coordenadas
 * esféricas (Z para cima): distância em escala log, azimute pelo menor ângulo, elevação linear.
 * Assim a câmera contorna a placa em vez de atravessá-la. Em giros grandes ela recua um pouco no
 * meio do caminho (arco), como num plano de Keynote. k em [0, 1], já com a curva de easing.
 */
const ARCO_RECUO = 0.18;     // recuo no meio do giro, por radiano de mudança de direção (limitado a 0,25)
function esfera(c) {
  const dx = c.px - c.tx, dy = c.py - c.ty, dz = c.pz - c.tz;
  const r = Math.max(1e-6, Math.hypot(dx, dy, dz));
  return { r, az: Math.atan2(dy, dx), el: Math.asin(Math.max(-1, Math.min(1, dz / r))) };
}
export function orbita(a, b, k, out = {}) {
  const ea = esfera(a), eb = esfera(b);
  let daz = eb.az - ea.az;
  daz -= 2 * Math.PI * Math.round(daz / (2 * Math.PI));
  // ângulo total entre as duas direções de vista, para o recuo do arco
  const va = [Math.cos(ea.el) * Math.cos(ea.az), Math.cos(ea.el) * Math.sin(ea.az), Math.sin(ea.el)];
  const vb = [Math.cos(eb.el) * Math.cos(eb.az), Math.cos(eb.el) * Math.sin(eb.az), Math.sin(eb.el)];
  const ang = Math.acos(Math.max(-1, Math.min(1, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2])));
  const recuo = 1 + Math.min(0.25, ARCO_RECUO * ang) * Math.sin(Math.PI * k);
  const r = Math.exp(Math.log(ea.r) + (Math.log(eb.r) - Math.log(ea.r)) * k) * recuo;
  const az = ea.az + daz * k, el = ea.el + (eb.el - ea.el) * k;
  const l = (x, y) => x + (y - x) * k;
  out.tx = l(a.tx, b.tx); out.ty = l(a.ty, b.ty); out.tz = l(a.tz, b.tz);
  out.px = out.tx + r * Math.cos(el) * Math.cos(az);
  out.py = out.ty + r * Math.cos(el) * Math.sin(az);
  out.pz = out.tz + r * Math.sin(el);
  out.fov = l(a.fov, b.fov);
  return out;
}
/**
 * Tween de câmera em arco na timeline: escreve em S.cam a cada render (seek incluído).
 * pontos (opcional): poses intermediárias [{at, ...cam}] com at em fração da duração; a curva de easing
 * vale para o percurso inteiro e cada trecho é um arco entre poses vizinhas.
 */
function tweenCam(tl, S, de, para, dur, ease, at, pontos = []) {
  const p = { k: 0 };
  const nos = [{ at: 0, ...de }, ...pontos, { at: 1, ...para }];
  tl.fromTo(p, { k: 0 }, {
    k: 1, duration: dur, ease,
    onUpdate: () => {
      let j = 1;
      while (j < nos.length - 1 && p.k > nos[j].at) j++;
      const a = nos[j - 1], b = nos[j];
      orbita(a, b, Math.min(1, Math.max(0, (p.k - a.at) / Math.max(1e-6, b.at - a.at))), S.cam);
    },
  }, at);
}
/** Gira a câmera em torno do alvo (graus de azimute), para a volta lenta do plano de herói. */
function giraAzimute(c, graus) {
  const a = THREE_RAD * graus, dx = c.px - c.tx, dy = c.py - c.ty;
  return { ...c, px: c.tx + dx * Math.cos(a) - dy * Math.sin(a), py: c.ty + dx * Math.sin(a) + dy * Math.cos(a) };
}
const THREE_RAD = Math.PI / 180;
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
    vit: 0, vitR: 0,     // vitrine: entrada da peça do beat e volta da peça do beat anterior
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
      const pontos = (b.camera.keys ?? []).map((k) => ({ at: k.at, ...camDe({ fov: b.camera.fov, ...k }) }));
      tweenCam(tl, S, de, alvo, dur, ease, start, pontos);
      const mixDe = mix ?? 0;
      if (mixDe !== 0) tl.fromTo(S, { mix: mixDe }, { mix: 0, duration: dur, ease: 'power1.inOut' }, start);
      cam = alvo; mix = 0;
    }
    // explosão: do nível anterior ao pedido, na entrada do beat (beat sem explode_state mantém o anterior)
    const alvoNivel = b.explode_state != null ? nivelDe(b.explode_state) : nivel;
    if (i === 0) S.expl = alvoNivel;
    // vários estágios num beat: cada estágio ocupa a mesma fatia de tempo (a coreografia de cada um já
    // tem a própria curva, em desmontagem.json)
    const varios = Math.abs(alvoNivel - nivel) > 1;
    // a desmontagem pode terminar antes da câmera (camera.explode_ate), para a aproximação final
    // acontecer com as peças já paradas
    const durEx = diag ? dur : dur * (b.camera?.explode_ate ?? 1);
    tl.fromTo(S, { expl: nivel }, { expl: alvoNivel, duration: durEx, ease: diag || varios ? 'none' : ease }, start);
    nivel = alvoNivel;
    // vitrine (illustrative): a peça do beat sai da placa para a pose de apresentação; a do beat
    // anterior volta ao lugar durante esta entrada
    const vAnt = i > 0 ? beats[i - 1].vitrine ?? null : null;
    const vCur = b.vitrine ?? null;
    const mesma = vAnt && vCur && vAnt.peca === vCur.peca;
    tl.set(S, { vit: mesma ? 1 : 0, vitR: 0 }, start);
    if (vCur && !mesma) tl.fromTo(S, { vit: 0 }, { vit: 1, duration: dur, ease: 'power2.inOut' }, start);
    if (vAnt && !mesma) tl.fromTo(S, { vitR: 1 }, { vitR: 0, duration: dur, ease: 'power2.inOut' }, start);
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
    // plano de herói: volta lenta em torno do alvo durante a leitura (a acumulação de quadros não roda)
    if (!diag && b.camera.hold_orbit) {
      const fim = giraAzimute(cam, b.camera.hold_orbit);
      const p = { k: 0 }, ini = { ...cam };
      tl.fromTo(p, { k: 0 }, { k: 1, duration: end - tEntrada, ease: 'sine.inOut', onUpdate: () => orbita(ini, fim, p.k, S.cam) }, tEntrada);
      cam = fim;
    }
    entradas.push({ id: b.id, start, entrada: tEntrada, settle, end, level: b.level, beat: b, mergulho: mergulhoDe });
    cursor = end;
  });
  tl.set({}, {}, cursor);        // fixa a duração
  return { tl, S, beats: entradas, duration: cursor };
}
