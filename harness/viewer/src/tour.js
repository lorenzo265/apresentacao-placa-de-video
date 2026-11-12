// Junta tudo: timeline mestre, cena 3D, camada de diagramas, chamada, cabeçalho, controles.
// Expõe window.__tour (ver README). Na captura, o que aparece é função só do tempo da linha do tempo;
// ao vivo, o apresentador anda de momento em momento e pode girar e aproximar sem perder o lugar.
import gsap from 'gsap';
import { constroiTimeline, beatsDoCorte, orbita } from './timeline.js';
import { resolve, uniao, fatoresDestaque } from './world.js';
import { criaCamadaDiagramas } from './diagrams.js';
import { criaChamada } from './callout.js';
import { criaCabecalho } from './header.js';
import { criaControles } from './controls.js';
import { STAGE_W, STAGE_H, HEADER_H, boxPlacement, safeRect } from './layout.js';
import { criaCotas } from './cotas.js';
import { criaCaminhos } from './caminhos3d.js';
import MERGULHO from './mergulho.json';

const COR_CAMINHO = { energy: '#ffb020', data: '#35d0e6', heat: '#ff6a3d' };

export function criaTour({ dados, palco, cena, capture, corte, tema = null }) {
  const { textos, world, medidas } = dados;

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
  // Trilha: uma linha do tempo com os seus beats. A principal é a do corte (os momentos das setas); a
  // dos extras tem todos os beats prontos e só é montada quando o índice abre um beat fora do corte.
  const TODOS = '__todos';
  function montaTrilha(nome) {
    const sb = nome === TODOS
      ? enquadraAuto({ ...dados.storyboard, cuts: { ...dados.storyboard.cuts, [TODOS]: { max_priority: 99 } } }, TODOS, cena)
      : enquadraAuto(dados.storyboard, nome, cena);
    const r = constroiTimeline({ storyboard: sb, corte: nome, world, mergulho: cena.blockout ? null : mergulho });
    return { nome, ...r, dims: new Map(), dims3d: null };
  }
  const principal = montaTrilha(corte);
  if (!principal.beats.length) throw new Error(`corte "${corte}" não tem beats ready`);
  let T = principal;           // trilha ativa
  let trilhaTodos = null;
  const storyboard = dados.storyboard;

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
  const dimsDe = (i) => {
    if (i < 0) return null;
    if (!T.dims.has(i)) T.dims.set(i, fatoresDestaque(world, T.beats[i].beat));
    return T.dims.get(i);
  };
  const ativo = (t) => { let k = 0; for (let i = 0; i < T.beats.length; i++) if (T.beats[i].start <= t + 1e-9) k = i; return k; };

  // Destaque em 3D: fatores por malha de cada beat. Beat de diagrama herda o do último beat 3D.
  function preparaDims3d(tr) {
    const dims3d = [];
    let ult = null;
    tr.beats.forEach((e, i) => {
      const b = e.beat;
      if (b.level <= 1) {
        const partes = [b.part, ...(b.highlight ?? []).filter((h) => !h.startsWith('tag:'))].filter(Boolean);
        const tags = (b.highlight ?? []).filter((h) => h.startsWith('tag:')).map((h) => h.slice(4));
        if (tr === principal) for (const p of partes) if (!cena.temPeca(p) && cena.temAncora('card')) console.warn(`[${b.id}] peça ${p} não existe no GLB; sem esmaecer`);
        ult = cena.fatoresDe(partes, tags);
      }
      dims3d[i] = ult;
      if (tr === principal && b.overlay && !caminhos.tem(b.overlay.path)) console.warn(`[3D] caminho ${b.overlay.path} sem mapeamento em caminhos.json (beat ${b.id}); nada desenhado`);
    });
    tr.dims3d = dims3d;
  }
  preparaDims3d(principal);

  let qVb = T.S.vb;      // enquadramento quantizado do quadro atual
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
    const a = cena.ancoraTela(c.anchor);
    // âncora numa peça em vitrine: o ponto vai para a borda da peça voltada para a caixa, para não
    // tapar a marcação dela
    if (a && b.vitrine && cena.ancoraDaPeca?.(c.anchor, b.vitrine.peca)) {
      const cx = cena.caixaNo(b.vitrine.peca);
      if (cx) {
        const xs = [];
        for (let i = 0; i < 8; i++) {
          const p = cena.projeta([i & 1 ? cx.max.x : cx.min.x, i & 2 ? cx.max.y : cx.min.y, i & 4 ? cx.max.z : cx.min.z]);
          if (p) xs.push(p[0]);
        }
        if (xs.length) {
          const dir = boxPlacement(c).side === 'left' ? -1 : 1;
          const borda = dir > 0 ? Math.max(...xs) : Math.min(...xs);
          return [borda - dir * 10, a[1]];
        }
      }
    }
    return a;
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
    if (!posesVit.has(b)) posesVit.set(b, cena.poseVitrine(b.vitrine, b.camera, b.callout?.box) ?? {});
    return posesVit.get(b);
  }

  // ---- estado da navegação (modo Apresentação) ----
  // idx: momento atual (ou o destino, durante a transição) na trilha principal.
  // fase: 'andando' (transição até o settle do momento), 'leitura' (a linha do tempo segue pelo hold: volta
  // do plano de herói, pulsos dos fluxos) e 'parado' (fim do hold; só o relógio de ambiente corre).
  let idx = 0;
  let fase = 'parado';
  let extraDe = null;      // num extra aberto pelo índice: o momento para onde as setas voltam
  let livre = false;       // usuário com a câmera 3D na mão (camera-controls)
  let vbLivre = null;      // usuário com o diagrama na mão: enquadramento {cx, cy, lw}
  let volta = null;        // volta suave da câmera ou do diagrama ao enquadramento do momento: {cam, vb, k}
  let tocando = false;
  let paraEm = null;
  let turbo = null;        // instante até onde a linha do tempo corre depressa (fim do hold com volta de câmera)
  let ambiente = 0;        // s de relógio com o momento parado; soma ao tempo dos fluxos, nunca na captura
  let suspenso = false;    // modo Explorar no comando: o tour não desenha
  let disclaimerDe = (b) => (b.view ? world.diagrams.get(b.view.diagram)?.disclaimer ?? null : null);
  const VOLTA_S = 0.6;
  const suave = (k) => k * k * (3 - 2 * k);
  const fimHold = (e) => e.settle + e.beat.hold;

  /** Desenha um quadro completo (3D, SVG e DOM) a partir do estado atual da timeline. */
  function desenha() {
    const { tl, S, beats, dims3d } = T;
    // Quantiza o estado: o mesmo instante dá o mesmo quadro, mesmo que a timeline chegue por
    // caminhos diferentes (erro de ponto flutuante na ordem de 1e-12 viraria um pixel diferente).
    const t = Math.round(tl.time() * 1e6) / 1e6;
    const q = (v) => Math.round(v * 1e6) / 1e6;
    let vb = { cx: q(S.vb.cx), cy: q(S.vb.cy), lw: q(S.vb.lw) };
    const expl = q(S.expl);
    const mix = q(S.mix), hl = q(S.hl), line = q(S.line), box = q(S.box), flow = q(S.flow);
    let cam = Object.fromEntries(Object.entries(S.cam).map(([k2, v]) => [k2, q(v)]));
    // volta do enquadramento livre ao do momento (só ao vivo; o seek zera)
    if (volta) {
      const w = suave(Math.min(1, volta.k));
      if (volta.cam) cam = orbita(volta.cam, cam, w, {});
      if (volta.vb) vb = { cx: volta.vb.cx + (vb.cx - volta.vb.cx) * w, cy: volta.vb.cy + (vb.cy - volta.vb.cy) * w, lw: volta.vb.lw + (vb.lw - volta.vb.lw) * w };
    }
    qVb = vbLivre ?? vb;
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
    const tFluxo = t + ambiente;      // parado no fim do hold, os pulsos continuam a correr
    caminhos.atualiza({ caminho: !ocultar3d && b.level <= 1 ? b.overlay?.path ?? null : null, via: q(S.via), alfa: q(S.viaA) * (1 - mix), t: tFluxo });
    camadaDiag.atualiza({
      vb: qVb, dims: dimsDe(i), dimsAnt: dimsDe(i - 1), hl,
      flowsAtivos: b.flows ?? [], flowAlpha: flow, t: tFluxo, visivel: mix,
      alvo: b.level >= 2 ? b.callout?.anchor ?? null : null,
      // vindo do 3D não havia diagrama na tela: os vizinhos já entram apagados (não há de onde apagar)
      vista: b.view?.diagram ?? null, vistaAnt: i > 0 ? beats[i - 1].beat.view?.diagram ?? (beats[i - 1].beat.level <= 1 ? b.view?.diagram ?? null : null) : null,
    });
    cotas?.atualiza({ visivel: ocultar3d ? 0 : (1 - mix) * Math.max(0, 1 - expl / 0.25) });
    chamada.atualiza(b, ancoraDe(b), line, box, COR_CAMINHO[b.overlay?.path] ?? corLinha);
    cabecalho.atualiza({
      beat: b, disclaimer: disclaimerDe(b), mix, blockoutVisivel: !!cena.blockout,
      // contador de momentos: na trilha principal, a posição; num extra, a palavra
      rotulo: T === principal ? `${i + 1} / ${beats.length}` : 'Extra',
      progresso: T === principal ? (i + 1) / beats.length : (extraDe + 1) / principal.beats.length,
    });
    controles?.atualiza();
  }

  // ---- câmera e diagrama na mão do apresentador ----
  let alvoTmp = null;
  function poseLivre() {
    const p = cena.camera.position;
    alvoTmp = cena.controls.getTarget(alvoTmp ?? p.clone());
    return { px: p.x, py: p.y, pz: p.z, tx: alvoTmp.x, ty: alvoTmp.y, tz: alvoTmp.z, fov: cena.camera.fov };
  }
  /** Devolve a câmera (ou o diagrama) ao enquadramento do momento. suave: com transição de VOLTA_S. */
  function recentra(suaveVolta = true) {
    const tinha = livre || !!vbLivre;
    volta = suaveVolta && tinha && !capture ? { cam: livre ? poseLivre() : null, vb: vbLivre, k: 0 } : null;
    livre = false; vbLivre = null;
    return tinha;
  }
  const diagNaTela = () => !suspenso && !capture && T.S.mix > 0.5 && fase !== 'andando';
  const noPalco = (ev) => { const r = palco.getBoundingClientRect(); return [(ev.clientX - r.left) * STAGE_W / r.width, (ev.clientY - r.top) * STAGE_H / r.height]; };
  if (!capture) {
    // diagramas: roda do mouse aproxima em torno do cursor, arrastar desloca
    palco.addEventListener('wheel', (ev) => {
      if (!diagNaTela() || ev.target.closest?.('.ui')) return;
      ev.preventDefault();
      const de = vbLivre ?? { ...qVb };
      const [sx, sy] = noPalco(ev);
      const vw = Math.exp(de.lw), vh = vw * STAGE_H / STAGE_W;
      const wx = de.cx - vw / 2 + sx * vw / STAGE_W, wy = de.cy - vh / 2 + sy * vh / STAGE_H;
      const lw = Math.min(Math.log(40000), Math.max(Math.log(20), de.lw + Math.sign(ev.deltaY) * Math.min(0.5, Math.abs(ev.deltaY) * 0.0016)));
      const vw2 = Math.exp(lw), vh2 = vw2 * STAGE_H / STAGE_W;
      vbLivre = { cx: wx + vw2 / 2 - sx * vw2 / STAGE_W, cy: wy + vh2 / 2 - sy * vh2 / STAGE_H, lw };
      volta = null;
    }, { passive: false });
    let arrasto = null;
    palco.addEventListener('pointerdown', (ev) => {
      if (!diagNaTela() || ev.button !== 0 || ev.target.closest?.('.ui')) return;
      arrasto = { x: ev.clientX, y: ev.clientY, de: vbLivre ?? { ...qVb }, andou: false };
    });
    addEventListener('pointermove', (ev) => {
      if (!arrasto) return;
      const r = palco.getBoundingClientRect();
      const dx = (ev.clientX - arrasto.x) * STAGE_W / r.width, dy = (ev.clientY - arrasto.y) * STAGE_W / r.width;
      if (!arrasto.andou && Math.hypot(dx, dy) < 4) return;
      arrasto.andou = true;
      const k = Math.exp(arrasto.de.lw) / STAGE_W;
      vbLivre = { cx: arrasto.de.cx - dx * k, cy: arrasto.de.cy - dy * k, lw: arrasto.de.lw };
      volta = null;
    });
    addEventListener('pointerup', () => { arrasto = null; });
  }

  // ---- navegação ----
  /** Posiciona a linha do tempo num instante e desenha (API dos testes e da captura: quadro determinístico). */
  function seek(t) {
    tocando = false; paraEm = null; turbo = null; volta = null; livre = false; vbLivre = null; ambiente = 0;
    cena.controls.enabled = false;
    T.tl.time(Math.min(T.duration, Math.max(0, t)), false);
    if (T === principal) idx = ativo(T.tl.time());
    fase = 'parado';
    desenha();
  }
  /** Chega a um momento da trilha ativa já montado (settle) e segue pela leitura. */
  function chega(i) {
    const e = T.beats[i];
    seek(e.settle);
    if (T === principal) idx = i;
    if (!capture) { fase = 'leitura'; tocando = true; paraEm = fimHold(e) - 1e-3; }
  }
  function voltaDoExtra() {
    if (extraDe == null) return false;
    T = principal; const i = extraDe; extraDe = null;
    chega(i);
    return true;
  }
  const extras = () => storyboard.beats.filter((b) => b.status === 'ready' && !principal.beats.some((x) => x.id === b.id)).map((b) => b.id);

  const tour = {
    ready: null,
    duration: principal.duration, fps: storyboard.fps, cut: corte,
    beats: principal.beats.map(({ id, start, entrada, settle, end, level, mergulho: m }) => ({ id, start, entrada, settle, end, level, mergulho: !!m })),
    /** Beats prontos fora do corte: abertos pelo índice, fora do caminho das setas. */
    extras: extras(),
    storyboard,
    textoDe,
    /** Estado quantizado da cena 3D no instante atual (para os testes). */
    estado: () => ({ expl: Math.round(T.S.expl * 1e6) / 1e6, mix: Math.round(T.S.mix * 1e6) / 1e6, via: Math.round(T.S.via * 1e6) / 1e6, acum: cena.acumulacao?.() ?? null, cam: { ...T.S.cam }, vb: { ...qVb } }),
    /** Onde a apresentação está: momento (índice na trilha principal), total, fase, extra aberto, enquadramento livre. */
    momento: () => ({ idx: extraDe ?? idx, total: principal.beats.length, fase, extra: extraDe != null ? T.beats[ativo(T.tl.time())].id : null, livre: livre || !!vbLivre, suspenso }),
    seek,
    time: () => T.tl.time(),
    beatAtual: () => T.beats[ativo(T.tl.time())],
    playing: () => tocando && fase === 'andando',
    play() { recentra(false); cena.controls.enabled = false; paraEm = null; tocando = true; fase = 'andando'; },
    pause() { tocando = false; paraEm = null; fase = 'parado'; },
    /** Seta para a direita: próximo momento, e para. No meio da transição, pula para o fim dela. */
    next() {
      if (suspenso) return;
      if (voltaDoExtra()) return;
      if (fase === 'andando') { chega(idx); return; }
      if (idx >= T.beats.length - 1) return;
      const e = T.beats[idx];
      recentra(true);
      ambiente = 0;
      // o resto do hold não é esperado: salta para o início da saída (com volta de câmera no hold, corre depressa até lá)
      if (e.beat.camera?.hold_orbit && T.tl.time() < fimHold(e)) turbo = fimHold(e);
      else T.tl.time(Math.max(T.tl.time(), fimHold(e)), false);
      idx += 1;
      paraEm = T.beats[idx].settle; tocando = true; fase = 'andando';
    },
    /** Seta para a esquerda: momento anterior, já montado. */
    prev() {
      if (suspenso) return;
      if (voltaDoExtra()) return;
      if (idx === 0 && fase !== 'andando') { chega(0); return; }
      chega(Math.max(0, idx - 1));
    },
    /** Vai a um beat pelo id e para nele (API dos testes: sem leitura, quadro fixo). */
    goto(id) {
      const i = principal.beats.findIndex((x) => x.id === id);
      if (i < 0) throw new Error(`beat ${id} não está no corte ${corte}`);
      T = principal; extraDe = null;
      seek(principal.beats[i].settle);
    },
    /** Vai a um momento ou a um extra (índice da tela). O extra guarda o momento para onde as setas voltam. */
    irPara(id) {
      if (suspenso) return;
      const i = principal.beats.findIndex((x) => x.id === id);
      if (i >= 0) { T = principal; extraDe = null; chega(i); return; }
      if (!trilhaTodos) { trilhaTodos = montaTrilha(TODOS); preparaDims3d(trilhaTodos); }
      const j = trilhaTodos.beats.findIndex((x) => x.id === id);
      if (j < 0) throw new Error(`beat ${id} não está pronto`);
      if (extraDe == null) extraDe = idx;
      T = trilhaTodos;
      chega(j);
    },
    recentra: () => recentra(true),
    /** Modo Explorar assume a cena: o tour para de desenhar. retoma() volta ao momento em que estava. */
    suspende() { suspenso = true; tocando = false; paraEm = null; turbo = null; recentra(false); cena.controls.enabled = false; },
    retoma() { suspenso = false; chega(T === principal ? idx : ativo(T.tl.time())); },
    probe(id) {
      const i = T.beats.findIndex((x) => x.id === id);
      if (i < 0 || i !== ativo(T.tl.time())) return { erro: `beat ${id} não é o beat ativo` };
      const b = T.beats[i].beat;
      const a = ancoraDe(b);
      return {
        anchor: a, focus: focoDe(b), box: chamada.ret(),
        captionOverflow: chamada.overflow(), headline: textoDe(id).headline,
      };
    },
  };

  const controles = capture ? null : criaControles(palco, tour);
  tour.controles = controles;

  // Câmera 3D na mão: o primeiro gesto solta a câmera do storyboard; o momento não muda
  cena.controls.enabled = false;
  cena.controls.addEventListener('controlstart', () => { if (!suspenso) { livre = true; volta = null; } });

  if (!capture) {
    // Laço ao vivo: a timeline anda por seu próprio tempo; o resto só redesenha.
    gsap.ticker.add((_, ms) => {
      if (suspenso) return;
      const dt = Math.min(0.1, ms / 1000);
      if (tocando) {
        const fim = paraEm ?? T.duration;
        let passo = dt;
        if (turbo != null) { if (T.tl.time() >= turbo) turbo = null; else passo = Math.max(dt, (turbo - T.tl.time()) * Math.min(1, dt / 0.25)); }
        const t = Math.min(fim, T.tl.time() + passo);
        T.tl.time(t, false);
        if (t >= fim) {
          if (fase === 'andando') { fase = 'leitura'; paraEm = fimHold(T.beats[ativo(t)]) - 1e-3; if (paraEm <= t) { tocando = false; paraEm = null; fase = 'parado'; } }
          else { tocando = false; paraEm = null; fase = 'parado'; }
        }
      } else ambiente += dt;
      if (volta) { volta.k += dt / VOLTA_S; if (volta.k >= 1) volta = null; }
      // girar e aproximar a qualquer hora em momento 3D, menos durante a transição
      cena.controls.enabled = T.S.mix < 0.5 && fase !== 'andando';
      if (livre) {
        cena.controls.update(dt);
        // planos de recorte acompanham a distância, como em ajustaCamera
        const d = cena.controls.distance, cam = cena.camera;
        const near = Math.min(Math.max(1, d * 0.08), 60), far = Math.max(2000, d * 12);
        if (cam.near !== near || cam.far !== far) { cam.near = near; cam.far = far; cam.updateProjectionMatrix(); }
      }
      desenha();
    });
  }

  tour.ready = (async () => {
    await Promise.all(['400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter', '400 20px "JetBrains Mono"', '500 20px "JetBrains Mono"']
      .map((f) => document.fonts.load(f)));
    await document.fonts.ready;
    // As larguras de texto dependem das fontes: refaz o encaixe dos rótulos se preciso (já medido após o load).
    principal.tl.time(0, false);
    desenha();
    window.__tourReady = true;
  })();
  return tour;
}

/**
 * Enquadramento automático (camera.enquadra e keys[].enquadra no storyboard): a pose escrita no beat dá só
 * a direção de vista e o fov; distância e alvo saem da caixa da placa no nível de explosão daquele
 * instante, para ela encher a área livre (fora da caixa de texto e do cabeçalho). Devolve uma cópia.
 */
function enquadraAuto(sb, corte, cena) {
  if (cena.blockout || !cena.enquadraNivel) return sb;
  const copia = JSON.parse(JSON.stringify(sb));
  let beats;
  try { beats = beatsDoCorte(copia, corte); } catch { return sb; }
  const nivelDe = (e) => (e === 'assembled' ? 0 : Number(String(e).slice(1)));
  // sem linha de chamada, a caixa (só título) fica no canto inferior esquerdo: a placa fica acima dela
  const livre = (b) => (b.callout ? safeRect(b.callout) : [48, HEADER_H + 24, STAGE_W - 96, STAGE_H - HEADER_H - 24 - 210]);
  const aplica = (alvo, cfg, nivel, fov, rect) => {
    const r = cena.enquadraNivel({ nivel, pos: alvo.pos, target: alvo.target, fov, rect, folga: cfg?.folga ?? 0.04, pecas: cfg?.pecas ?? null });
    if (r) { alvo.pos = r.pos; alvo.target = r.target; }
  };
  let nivel = 0;
  for (const b of beats) {
    if (b.level >= 2) continue;
    const n1 = b.explode_state != null ? nivelDe(b.explode_state) : nivel;
    const c = b.camera;
    if (c) {
      const ate = c.explode_ate ?? 1;
      for (const k of c.keys ?? []) if (k.enquadra) aplica(k, k.enquadra, nivel + (n1 - nivel) * Math.min(1, k.at / ate), k.fov ?? c.fov, livre(b));
      if (c.enquadra) aplica(c, c.enquadra, n1, c.fov, livre(b));
    }
    nivel = n1;
  }
  cena.aplicaEstado?.(0, null, null, 1);
  return copia;
}
