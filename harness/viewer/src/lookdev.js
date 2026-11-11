// Lookdev do modo realista (tema Keynote): materiais físicos de src/materials.json, texturas
// procedurais (geradas aqui, com semente fixa), estúdio com ambiente HDR e três luzes, chão que só
// recebe sombra, destaque realista (escurece e dessatura o resto, recorte de luz na peça) e
// pós-processamento (MSAA, oclusão de ambiente GTAO, profundidade de campo, AgX).
// Tudo é função do estado (câmera, explosão, destaque): o mesmo instante dá o mesmo quadro.
import * as THREE from 'three';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { FullScreenQuad } from 'three/examples/jsm/postprocessing/Pass.js';
import { GTAOPass } from 'three/examples/jsm/postprocessing/GTAOPass.js';
import TABELA from './materials.json';
import HDR_B64 from './ambiente-hdr.js';

// ---------------------------------------------------------------------------------------------
// Níveis de qualidade. "media" é o padrão: tem de rodar fluida num notebook com GPU integrada.
// ---------------------------------------------------------------------------------------------
// acum: quadros acumulados com a cena parada (média com deslocamento de subpixel, luz principal e
// profundidade de campo variando a cada amostra); 0 desliga. ?acumula=N na URL troca o número.
export const QUALIDADES = {
  baixa: { pos: false, msaa: 0, sombra: 0, prMax: 1, tex: 256, fisico: false, ao: false, dof: 0, acum: 0 },
  media: { pos: true, msaa: 4, sombra: 2048, prMax: 1.25, tex: 512, fisico: true, ao: false, dof: 12, acum: 32 },
  alta: { pos: true, msaa: 4, sombra: 4096, prMax: 2, tex: 1024, fisico: true, ao: true, dof: 24, acum: 64 },
};

/** Número de quadros acumulados pedido na URL (?acumula=N, 0 desliga); null se não pediu. */
export function acumulaDaUrl(params) {
  const v = params.get('acumula');
  if (v == null) return null;
  const n = Math.round(Number(v));
  if (!Number.isFinite(n) || n < 0) { console.warn(`[lookdev] acumula inválido: ${v}; usando o padrão da qualidade`); return null; }
  return Math.min(256, n);
}

/** Sequência de Halton (base b), índice i >= 1: pontos bem espalhados em [0, 1), sempre os mesmos. */
function halton(i, b) {
  let f = 1, r = 0;
  for (let k = i; k > 0; k = Math.floor(k / b)) { f /= b; r += f * (k % b); }
  return r;
}
/** Filtro em tenda: uniforme em [0, 1) para [-1, 1], mais denso no centro (menos moiré que a caixa). */
const tenda = (u) => (u < 0.5 ? Math.sqrt(2 * u) - 1 : 1 - Math.sqrt(2 - 2 * u));

/**
 * Parâmetros da amostra k da acumulação (k = 0 é o quadro normal, sem deslocamento). Só depende de k:
 * a captura dá sempre a mesma média. jx, jy em px do alvo; luz em [-1, 1]^2 (disco); rot e fase da
 * espiral da profundidade de campo.
 */
export function amostraAcumulacao(k, cfg) {
  if (k === 0) return null;
  const r = cfg?.filtro_px ?? 1;
  // disco da luz por mapeamento concêntrico (bases 5 e 7, independentes das do pixel)
  const a = 2 * halton(k, 5) - 1, b = 2 * halton(k, 7) - 1;
  let lu = 0, lv = 0;
  if (a || b) {
    const [rr, th] = Math.abs(a) > Math.abs(b) ? [a, (Math.PI / 4) * (b / a)] : [b, Math.PI / 2 - (Math.PI / 4) * (a / b)];
    lu = rr * Math.cos(th); lv = rr * Math.sin(th);
  }
  return {
    jx: tenda(halton(k, 2)) * r, jy: tenda(halton(k, 3)) * r,
    luz: [lu, lv],
    rot: halton(k, 11) * 2 * Math.PI, fase: halton(k, 13),
  };
}

/** Qualidade pedida na URL (?qualidade=alta|media|baixa); null se não pediu (vale o padrão e a escolha automática). */
export function qualidadeDaUrl(params) {
  const q = params.get('qualidade');
  if (!q) return null;
  if (!QUALIDADES[q]) { console.warn(`[lookdev] qualidade desconhecida: ${q}; usando media`); return 'media'; }
  return q;
}

/** Temperatura de cor (K) para cor linear com luminância 1 (aproximação de Tanner Helland). */
export function kelvin(K) {
  const t = K / 100;
  const r = t <= 66 ? 255 : 329.698727446 * Math.pow(t - 60, -0.1332047592);
  const g = t <= 66 ? 99.4708025861 * Math.log(t) - 161.1195681661 : 288.1221695283 * Math.pow(t - 60, -0.0755148492);
  const b = t >= 66 ? 255 : t <= 19 ? 0 : 138.5177312231 * Math.log(t - 10) - 305.0447927307;
  const c = new THREE.Color().setRGB(...[r, g, b].map((x) => Math.min(255, Math.max(0, x)) / 255), THREE.SRGBColorSpace);
  const l = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
  return c.multiplyScalar(1 / l);
}

// ---------------------------------------------------------------------------------------------
// Texturas procedurais (DataTexture RGBA8, pixel a pixel, semente fixa)
// ---------------------------------------------------------------------------------------------
function prng(semente) {
  let s = semente >>> 0;
  return () => { s = (s + 0x6d2b79f5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const hexRgb = (h) => { const c = new THREE.Color(h); return [c.r, c.g, c.b]; };      // linear
const lin2srgb = (x) => (x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055);
const byte = (x) => Math.max(0, Math.min(255, Math.round(x * 255)));
const suave = (x) => x * x * (3 - 2 * x);
const clamp01 = (x) => Math.max(0, Math.min(1, x));

/** Ruído de valor periódico (período p células numa textura de N px), interpolação suave. */
function ruidoPeriodico(N, p, rnd) {
  const g = new Float32Array(p * p).map(() => rnd());
  const out = new Float32Array(N * N);
  for (let y = 0; y < N; y++) {
    const fy = (y / N) * p, y0 = Math.floor(fy), ty = suave(fy - y0);
    for (let x = 0; x < N; x++) {
      const fx = (x / N) * p, x0 = Math.floor(fx), tx = suave(fx - x0);
      const a = g[(y0 % p) * p + (x0 % p)], b = g[(y0 % p) * p + ((x0 + 1) % p)];
      const c = g[((y0 + 1) % p) * p + (x0 % p)], d = g[((y0 + 1) % p) * p + ((x0 + 1) % p)];
      out[y * N + x] = (a + (b - a) * tx) + ((c + (d - c) * tx) - (a + (b - a) * tx)) * ty;
    }
  }
  return out;
}
function fbm(N, periodos, pesos, rnd) {
  const out = new Float32Array(N * N);
  let soma = 0;
  periodos.forEach((p, i) => { const r = ruidoPeriodico(N, p, rnd); for (let k = 0; k < out.length; k++) out[k] += r[k] * pesos[i]; soma += pesos[i]; });
  for (let k = 0; k < out.length; k++) out[k] /= soma;
  return out;
}

/** Canais de uma textura em construção: cor (linear), rugosidade, metal, altura e anisotropia. */
function canais(W, H) {
  return { W, H, cor: new Float32Array(W * H * 3), rug: new Float32Array(W * H), metal: new Float32Array(W * H), alt: new Float32Array(W * H), aniso: null, temCor: false };
}
function dataTex(dados, W, H, srgb) {
  const t = new THREE.DataTexture(dados, W, H, THREE.RGBAFormat, THREE.UnsignedByteType);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.magFilter = THREE.LinearFilter;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true;
  t.anisotropy = 8;
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.channel = 2;              // atributo uv2: as UVs do GLB (uv, uv1) ficam livres para os mapas assados
  t.needsUpdate = true;
  return t;
}
/** Converte os canais em texturas do three: map (cor), orm (G rugosidade, B metal), normal e anisotropia. */
function finaliza(c, relevo, periodico = true) {
  const { W, H } = c;
  const n = W * H;
  const orm = new Uint8Array(n * 4), nor = new Uint8Array(n * 4);
  for (let i = 0; i < n; i++) {
    orm[i * 4] = 255; orm[i * 4 + 1] = byte(c.rug[i]); orm[i * 4 + 2] = byte(c.metal[i]); orm[i * 4 + 3] = 255;
  }
  // normal pela derivada da altura (altura em px de textura; relevo escala a inclinação)
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const at = (xx, yy) => {
        if (periodico) return c.alt[((yy + H) % H) * W + ((xx + W) % W)];
        return c.alt[Math.min(H - 1, Math.max(0, yy)) * W + Math.min(W - 1, Math.max(0, xx))];
      };
      const dx = (at(x + 1, y) - at(x - 1, y)) * relevo, dy = (at(x, y + 1) - at(x, y - 1)) * relevo;
      const l = Math.hypot(dx, dy, 1);
      const i = (y * W + x) * 4;
      nor[i] = byte(-dx / l * 0.5 + 0.5); nor[i + 1] = byte(-dy / l * 0.5 + 0.5); nor[i + 2] = byte(1 / l * 0.5 + 0.5); nor[i + 3] = 255;
    }
  }
  const r = { orm: dataTex(orm, W, H, false), normal: dataTex(nor, W, H, false), map: null, aniso: null };
  if (c.temCor) {
    const cor = new Uint8Array(n * 4);
    for (let i = 0; i < n; i++) { for (let k = 0; k < 3; k++) cor[i * 4 + k] = byte(lin2srgb(c.cor[i * 3 + k])); cor[i * 4 + 3] = 255; }
    r.map = dataTex(cor, W, H, true);
  }
  if (c.aniso) r.aniso = dataTex(c.aniso, W, H, false);
  return r;
}

/** Metal jateado, anodizado, epóxi, pasta: grão fino e manchas largas na rugosidade, relevo sutil. */
function texGrao(def, p, N, rnd) {
  const c = canais(N, N);
  const fino = fbm(N, [64, 128], [0.6, 0.4], rnd);
  const largo = fbm(N, [3, 6], [0.7, 0.3], rnd);
  for (let i = 0; i < N * N; i++) {
    c.rug[i] = clamp01(def.rug + (fino[i] - 0.5) * 2 * p.rug_var + (largo[i] - 0.5) * 2 * (p.manchas ?? 0));
    c.metal[i] = def.metal;
    c.alt[i] = fino[i];
  }
  // abaixo de 512 px o grão fica grosso demais para relevo (vira martelado): só a rugosidade varia
  return finaliza(c, N < 512 ? 0 : (p.relevo ?? 0.2) * 6);
}

/** Cubo do ventilador: metal torneado (anisotropia concêntrica) dentro do raio do cubo; plástico fora. */
function texUsinagem(def, p, N, rnd, ctx) {
  const c = canais(N, N);
  c.temCor = true;
  c.aniso = new Uint8Array(N * N * 4);
  const D = ctx.bbox ? Math.max(ctx.bbox.tam[0], ctx.bbox.tam[1]) : 113;   // diâmetro coberto pela textura (mm)
  const Rc = ctx.valor(p.raio_cubo_mm);
  const cb = p.cubo, corCubo = hexRgb(cb.cor), corPl = hexRgb(def.cor);
  const aneis = new Float32Array(4096).map(() => rnd());
  const grao = fbm(N, [64, 128], [0.5, 0.5], rnd);
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const i = y * N + x;
      const px = ((x + 0.5) / N - 0.5) * D, py = ((y + 0.5) / N - 0.5) * D;
      const r = Math.hypot(px, py);
      const dentro = r < Rc - 0.6;
      const borda = !dentro && r < Rc;                       // chanfro escuro na borda do cubo
      if (dentro) {
        const anel = aneis[Math.floor(r / cb.passo_mm) % 4096];
        c.rug[i] = clamp01(cb.rug + (anel - 0.5) * (cb.var_rug ?? 0.08));
        c.metal[i] = cb.metal;
        const k = 1 + (anel - 0.5) * (cb.var_cor ?? 0.06);
        for (let j = 0; j < 3; j++) c.cor[i * 3 + j] = corCubo[j] * k;
        c.alt[i] = anel * (cb.relevo ?? 0.15);
        const tx = r > 1e-6 ? -py / r : 1, ty = r > 1e-6 ? px / r : 0;   // direção circunferencial
        c.aniso[i * 4] = byte(tx * 0.5 + 0.5); c.aniso[i * 4 + 1] = byte(ty * 0.5 + 0.5); c.aniso[i * 4 + 2] = 255;
      } else {
        c.rug[i] = clamp01(borda ? 0.45 : def.rug + (grao[i] - 0.5) * 0.04);
        c.metal[i] = borda ? 0.6 : def.metal;
        for (let j = 0; j < 3; j++) c.cor[i * 3 + j] = borda ? corCubo[j] * 0.35 : corPl[j];
        c.alt[i] = borda ? -0.5 : 0;
        c.aniso[i * 4] = 255; c.aniso[i * 4 + 1] = 128; c.aniso[i * 4 + 2] = 0;
      }
      c.aniso[i * 4 + 3] = 255;
    }
  }
  return finaliza(c, 3, false);
}

/** Aletas sobre uma caixa: a textura cobre um passo; fresta escura e borda da aleta com leve chanfro. */
function texAletas(def, p, N, rnd, ctx) {
  const W = 64, H = 4;
  const c = canais(W, H);
  c.temCor = true;
  const passo = ctx.valor(p.passo_mm), esp = ctx.valor(p.espessura_mm);
  const fr = esp / passo;
  const corA = hexRgb(def.cor), corF = hexRgb(p.fresta);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = y * W + x;
      const u = (x + 0.5) / W;
      const d = Math.abs(u - 0.5) / (fr / 2);               // 0 no meio da aleta, 1 na borda
      const aleta = d < 1;
      const k = aleta ? 1 : 0;
      for (let j = 0; j < 3; j++) c.cor[i * 3 + j] = corF[j] + (corA[j] - corF[j]) * k;
      c.rug[i] = aleta ? def.rug : 0.9;
      c.metal[i] = def.metal;
      c.alt[i] = aleta ? Math.sqrt(1 - Math.min(1, d * d)) : 0;
    }
  }
  return finaliza(c, 2.5);
}

/** Desenho em canais com repetição (periódico): retângulo, disco e traço espesso. */
function pinta(c) {
  const { W, H } = c;
  const idx = (x, y) => (((y % H) + H) % H) * W + (((x % W) + W) % W);
  return {
    ret(x0, y0, w, h, f) { for (let y = Math.round(y0); y < Math.round(y0 + h); y++) for (let x = Math.round(x0); x < Math.round(x0 + w); x++) f(idx(x, y), x - x0, y - y0); },
    disco(cx, cy, r, f) { for (let y = Math.floor(cy - r); y <= Math.ceil(cy + r); y++) for (let x = Math.floor(cx - r); x <= Math.ceil(cx + r); x++) { const d = Math.hypot(x - cx, y - cy); if (d <= r) f(idx(x, y), d / r); } },
    traco(pts, w, f) {
      for (let k = 1; k < pts.length; k++) {
        const [ax, ay] = pts[k - 1], [bx, by] = pts[k];
        const n = Math.ceil(Math.hypot(bx - ax, by - ay));
        for (let s = 0; s <= n; s++) { const t = n ? s / n : 0; this.ret(ax + (bx - ax) * t - w / 2, ay + (by - ay) * t - w / 2, w, w, f); }
      }
    },
  };
}
const corEm = (c, i, rgb) => { for (let j = 0; j < 3; j++) c.cor[i * 3 + j] = rgb[j]; };

/** Placa de circuito: máscara preta, trilhas em relevo, vias, serigrafia. Desenho ilustrativo. */
function texPcb(def, p, N, rnd) {
  const c = canais(N, N);
  c.temCor = true;
  const mm = N / p.tile_mm;                                   // px por mm
  const base = hexRgb(def.cor), trilha = hexRgb(p.trilha), seri = hexRgb(p.serigrafia), via = hexRgb(p.via);
  const grao = fbm(N, [32, 128], [0.5, 0.5], rnd);
  for (let i = 0; i < N * N; i++) { corEm(c, i, base); c.rug[i] = def.rug + (grao[i] - 0.5) * 0.06; c.metal[i] = 0; c.alt[i] = grao[i] * 0.08; }
  const d = pinta(c);
  // trilhas: caminhos de Manhattan com dobras de 45 graus, em feixes paralelos
  for (let f = 0; f < 26; f++) {
    let x = rnd() * N, y = rnd() * N;
    const fios = 2 + Math.floor(rnd() * 6), passo = (0.25 + rnd() * 0.2) * mm, w = Math.max(1.5, (0.1 + rnd() * 0.12) * mm);
    let dir = Math.floor(rnd() * 4);
    const pts = [[x, y]];
    for (let s = 0; s < 4; s++) {
      const L = (2 + rnd() * 9) * mm;
      const ang = dir * Math.PI / 2;
      x += Math.cos(ang) * L; y += Math.sin(ang) * L; pts.push([x, y]);
      const vira = rnd() < 0.5 ? 1 : -1;
      const L2 = (0.6 + rnd()) * mm;
      x += Math.cos(ang + vira * Math.PI / 4) * L2; y += Math.sin(ang + vira * Math.PI / 4) * L2; pts.push([x, y]);
      dir = (dir + (rnd() < 0.5 ? 0 : vira) + 4) % 4;
    }
    for (let k = 0; k < fios; k++) {
      const o = k * passo;
      d.traco(pts.map(([a, b]) => [a + o, b + o]), w, (i) => { corEm(c, i, trilha); c.rug[i] = def.rug - 0.08; c.alt[i] = 0.6; });
    }
  }
  // vias cobertas (relevo) e algumas abertas (anel estanhado)
  for (let k = 0; k < 140; k++) {
    const x = rnd() * N, y = rnd() * N, aberta = rnd() < 0.25, r = 0.22 * mm;
    d.disco(x, y, r, (i, t) => {
      if (aberta) { corEm(c, i, t < 0.45 ? [0.01, 0.01, 0.01] : via); c.metal[i] = t < 0.45 ? 0 : 1; c.rug[i] = 0.35; }
      c.alt[i] = Math.max(c.alt[i], (1 - t) * 0.8);
    });
  }
  // serigrafia: contornos de componentes e blocos de rótulo (ilegíveis de propósito)
  const seriPx = Math.max(1, Math.round(0.12 * mm));
  for (let k = 0; k < 9; k++) {
    const w = (1.5 + rnd() * 6) * mm, h = (1 + rnd() * 4) * mm, x = rnd() * N, y = rnd() * N;
    const f = (i) => { corEm(c, i, seri); c.rug[i] = 0.75; c.alt[i] = 0.9; };
    d.ret(x, y, w, seriPx, f); d.ret(x, y + h, w, seriPx, f); d.ret(x, y, seriPx, h, f); d.ret(x + w, y, seriPx, h + seriPx, f);
    if (rnd() < 0.7) {
      let tx = x + w + 0.6 * mm;
      const n = 2 + Math.floor(rnd() * 3);
      for (let j = 0; j < n; j++) { const cw = 0.5 * mm; d.ret(tx, y, cw, 0.8 * mm, f); tx += cw + 0.25 * mm; }
    }
  }
  return finaliza(c, 1.2);
}

/** Capacitores pequenos: corpos cerâmicos e terminais estanhados sobre a máscara. Posições ilustrativas. */
function texSmd(def, p, N, rnd) {
  const c = canais(N, N);
  c.temCor = true;
  const mm = N / p.tile_mm;
  const base = hexRgb(def.cor), corpo = hexRgb(p.corpo), term = hexRgb(p.terminal);
  for (let i = 0; i < N * N; i++) { corEm(c, i, base); c.rug[i] = def.rug; c.metal[i] = 0; c.alt[i] = 0; }
  const d = pinta(c);
  const passoY = 0.9 * mm, passoX = 1.4 * mm;
  for (let y = 0.3 * mm; y < N; y += passoY) {
    for (let x = 0.2 * mm; x < N; x += passoX) {
      if (rnd() < 0.18) continue;
      const vert = rnd() < 0.3, L = (0.9 + rnd() * 0.3) * mm, Wd = 0.5 * mm;
      const w = vert ? Wd : L, h = vert ? L : Wd;
      const jx = (rnd() - 0.5) * 0.2 * mm, jy = (rnd() - 0.5) * 0.1 * mm;
      d.ret(x + jx, y + jy, w, h, (i, u, v) => {
        const t = vert ? v / h : u / w;
        const ponta = t < 0.22 || t > 0.78;
        corEm(c, i, ponta ? term : corpo);
        c.metal[i] = ponta ? 1 : 0; c.rug[i] = ponta ? 0.3 : 0.55;
        const e = vert ? Math.min(u, w - u) / w : Math.min(v, h - v) / h;
        c.alt[i] = Math.min(1, e * 6);
      });
    }
  }
  return finaliza(c, 2);
}

/** Adaptador PCIe: máscara preta e contatos dourados no passo da norma (textura no referencial da placa). */
function texContatos(def, p, N, rnd, ctx) {
  const bb = ctx.bbox;
  const c = canais(N, N);
  c.temCor = true;
  const base = hexRgb(def.cor), ouro = hexRgb(p.ouro);
  const x0 = ctx.valor(p.x0_mm), zona = ctx.valor(p.zona_mm), passo = ctx.valor(p.passo_mm);
  const grao = fbm(N, [32, 64], [0.5, 0.5], rnd);
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const i = y * N + x;
      const [X, Y] = bb.cad((x + 0.5) / N, (y + 0.5) / N);   // mm, referencial da placa (x do bracket, y dos contatos)
      const r = X - x0;
      const naChave = Math.abs(r - p.curto_mm) < p.chave_mm / 2;
      const fase = ((r % passo) + passo) % passo / passo;
      const contato = Y >= 0 && Y < p.faixa_mm && r >= 0 && r <= zona && !naChave && Math.abs(fase - 0.5) < p.largura_rel / 2;
      if (contato) { corEm(c, i, ouro); c.metal[i] = 1; c.rug[i] = 0.24 + grao[i] * 0.08; c.alt[i] = 0.4; }
      else { corEm(c, i, base); c.metal[i] = 0; c.rug[i] = def.rug + (grao[i] - 0.5) * 0.06; c.alt[i] = grao[i] * 0.05; }
    }
  }
  return finaliza(c, 2, false);
}

/** Package do chip: moldura de reforço metálica, borda do substrato e o die no centro. */
function texPackage(def, p, N, rnd) {
  const c = canais(N, N);
  c.temCor = true;
  const mol = p.moldura, die = p.die;
  const corM = hexRgb(mol.cor), corS = hexRgb(p.substrato), corD = hexRgb(die.cor), base = hexRgb(def.cor);
  const grao = fbm(N, [32, 128], [0.5, 0.5], rnd);
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const i = y * N + x;
      const u = Math.abs((x + 0.5) / N - 0.5) * 2, v = Math.abs((y + 0.5) / N - 0.5) * 2;   // 0 no centro, 1 na borda
      const naDie = u < p.die_rel[0] && v < p.die_rel[1];
      const naJanela = u < p.janela_rel[0] && v < p.janela_rel[1];
      const naBorda = u > 0.975 || v > 0.97;
      if (naDie) { corEm(c, i, corD); c.metal[i] = die.metal; c.rug[i] = die.rug + grao[i] * 0.05; c.alt[i] = 1; }
      else if (naJanela || naBorda) { corEm(c, i, naBorda ? base : corS); c.metal[i] = 0; c.rug[i] = 0.42; c.alt[i] = 0; }
      else { corEm(c, i, corM); c.metal[i] = mol.metal; c.rug[i] = mol.rug + (grao[i] - 0.5) * 0.08; c.alt[i] = 0.6 + grao[i] * 0.05; }
    }
  }
  return finaliza(c, 1.5, false);
}

/**
 * Abertura (receptáculo de conector): a UV 'cavidade' põe u = 0,25 nas faces da casca (sobre a caixa
 * envolvente: borda frontal e lados) e u = 0,75 nas faces de dentro (paredes, língua, fundo). A textura
 * tem duas metades: casca metálica e interior escuro.
 */
function texAbertura(def, p) {
  const W = 4, H = 1;
  const c = canais(W, H);
  c.temCor = true;
  const fora = hexRgb(def.cor), dentro = hexRgb(p.interior.cor);
  for (let x = 0; x < W; x++) {
    const casca = x < W / 2;
    corEm(c, x, casca ? fora : dentro);
    c.metal[x] = casca ? def.metal : p.interior.metal;
    c.rug[x] = casca ? def.rug : p.interior.rug;
    c.alt[x] = 0;
  }
  const r = finaliza(c, 0, false);
  // oclusão do interior (canal R): a luz do ambiente e, com micro_sombra, a luz direta rasante quase
  // não entram na cavidade (a peça não tem oclusão assada)
  const ao = new Uint8Array(W * H * 4);
  for (let x = 0; x < W; x++) { const v = byte(x < W / 2 ? 1 : (p.interior.ao ?? 1)); ao.set([v, v, v, 255], x * 4); }
  r.ao = dataTex(ao, W, H, false);
  return r;
}

/**
 * Faixas ao longo do maior eixo da malha (cabo flat): reforço nas duas pontas ('reforco_mm' de
 * comprimento, cor e acabamento próprios) e, no meio, a película com trilhas finas paralelas por baixo.
 */
function texFaixas(def, p, N, rnd, ctx) {
  const c = canais(N, N);
  c.temCor = true;
  const [L, Wd] = ctx.bbox.tam;
  const base = hexRgb(def.cor), ref = hexRgb(p.reforco.cor), trilha = hexRgb(p.trilha ?? def.cor);
  const grao = fbm(N, [32, 64], [0.5, 0.5], rnd);
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const i = y * N + x;
      const u = ((x + 0.5) / N) * L, v = ((y + 0.5) / N) * Wd;
      const naPonta = u < p.reforco_mm || u > L - p.reforco_mm;
      if (naPonta) {
        corEm(c, i, ref); c.metal[i] = 0; c.rug[i] = p.reforco.rug + (grao[i] - 0.5) * 0.06; c.alt[i] = 0.5;
      } else {
        const fase = ((v % p.passo_trilha_mm) + p.passo_trilha_mm) % p.passo_trilha_mm / p.passo_trilha_mm;
        const tr = Math.abs(fase - 0.5) < 0.22;
        corEm(c, i, tr ? trilha : base); c.metal[i] = 0; c.rug[i] = def.rug + (grao[i] - 0.5) * 0.04; c.alt[i] = tr ? 0.25 : 0;
      }
    }
  }
  return finaliza(c, 1, false);
}

const GERADORES = { grao: texGrao, usinagem: texUsinagem, aletas: texAletas, pcb: texPcb, smd: texSmd, contatos_pcie: texContatos, package: texPackage, abertura: texAbertura, faixas: texFaixas };

// ---------------------------------------------------------------------------------------------
// UV e normais para malhas que chegam sem (blockout)
// ---------------------------------------------------------------------------------------------
/** Caixa: projeção pelo eixo dominante da normal de cada triângulo, em mm / tile. */
function uvCaixa(geo, tileMm) {
  const pos = geo.attributes.position, n = pos.count;
  const uv = new Float32Array(n * 2);
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), nn = new THREE.Vector3();
  const k = 1000 / tileMm;
  for (let t = 0; t < n; t += 3) {
    a.fromBufferAttribute(pos, t); b.fromBufferAttribute(pos, t + 1); c.fromBufferAttribute(pos, t + 2);
    nn.subVectors(c, b).cross(b.clone().sub(a)).normalize();
    const ax = Math.abs(nn.x), ay = Math.abs(nn.y), az = Math.abs(nn.z);
    for (let j = 0; j < 3; j++) {
      const v = [a, b, c][j];
      let u, w;
      if (ay >= ax && ay >= az) { u = v.x; w = v.z; }        // glTF Y = espessura: faces grandes da placa
      else if (az >= ax) { u = v.x; w = v.y; }
      else { u = v.z; w = v.y; }
      uv[(t + j) * 2] = u * k; uv[(t + j) * 2 + 1] = w * k;
    }
  }
  geo.setAttribute('uv2', new THREE.BufferAttribute(uv, 2));
}
/**
 * Cavidade: classifica cada triângulo da malha (não indexada) como casca, se o plano dele é um plano de
 * apoio da malha (nenhum vértice fica além dele, na direção da normal: borda frontal, lados, face de
 * encaixe), ou interior (paredes e fundo das cavidades, língua). Vale para peça girada em relação aos
 * eixos (o conector de energia, a 45 graus). u = 0,25 na casca, 0,75 no interior (ver texAbertura).
 */
function uvCavidade(geo) {
  geo.computeBoundingBox();
  const bb = geo.boundingBox, pos = geo.attributes.position, n = pos.count;
  const tol = Math.max(bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z) * 0.004;
  const uv = new Float32Array(n * 2);
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), nn = new THREE.Vector3();
  const apoio = new Map();                  // normal quantizada -> maior projeção dos vértices
  const maxProj = (nx, ny, nz) => {
    const k = `${Math.round(nx * 500)},${Math.round(ny * 500)},${Math.round(nz * 500)}`;
    if (!apoio.has(k)) {
      let m = -Infinity;
      for (let i = 0; i < n; i++) m = Math.max(m, pos.getX(i) * nx + pos.getY(i) * ny + pos.getZ(i) * nz);
      apoio.set(k, m);
    }
    return apoio.get(k);
  };
  for (let k = 0; k + 2 < n; k += 3) {
    a.fromBufferAttribute(pos, k); b.fromBufferAttribute(pos, k + 1); c.fromBufferAttribute(pos, k + 2);
    nn.subVectors(c, b).cross(a.clone().sub(b));
    let casca = false;
    if (nn.lengthSq() > 0) {
      nn.normalize();
      const cx = (a.x + b.x + c.x) / 3, cy = (a.y + b.y + c.y) / 3, cz = (a.z + b.z + c.z) / 3;
      casca = cx * nn.x + cy * nn.y + cz * nn.z >= maxProj(nn.x, nn.y, nn.z) - tol;
    }
    for (let j = 0; j < 3; j++) { uv[(k + j) * 2] = casca ? 0.25 : 0.75; uv[(k + j) * 2 + 1] = 0.5; }
  }
  geo.setAttribute('uv2', new THREE.BufferAttribute(uv, 2));
}
/** Plana: projeta pelo menor eixo da caixa envolvente e ajusta a textura à caixa (0 a 1). */
function uvPlanar(geo) {
  geo.computeBoundingBox();
  const bb = geo.boundingBox, tam = bb.getSize(new THREE.Vector3());
  const eixos = ['x', 'y', 'z'].sort((p, q) => tam[q] - tam[p]);   // maior, médio, menor
  const [eu, ev] = eixos;
  const pos = geo.attributes.position, uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) {
    const p = { x: pos.getX(i), y: pos.getY(i), z: pos.getZ(i) };
    uv[i * 2] = (p[eu] - bb.min[eu]) / tam[eu];
    uv[i * 2 + 1] = (p[ev] - bb.min[ev]) / tam[ev];
  }
  geo.setAttribute('uv2', new THREE.BufferAttribute(uv, 2));
  // Ponto (u, v) da textura no referencial da placa em mm (glTF: x = x, -z = y da placa).
  const cad = (u, v) => {
    const p = { x: 0, y: 0, z: 0 };
    p[eu] = (bb.min[eu] + u * tam[eu]) * 1000; p[ev] = (bb.min[ev] + v * tam[ev]) * 1000;
    return [p.x, -p.z];
  };
  return { tam: [tam[eu] * 1000, tam[ev] * 1000], cad };
}

// ---------------------------------------------------------------------------------------------
// Materiais
// ---------------------------------------------------------------------------------------------
/** Caminho de nomes do nó até a raiz: [nome, instance_of, nome do pai, ...]. */
function nomesDe(o) {
  const r = [];
  for (let a = o; a; a = a.parent) { if (a.name) r.push(a.name); if (a.userData?.instance_of) r.push(a.userData.instance_of); }
  return r;
}
function grupoDe(o) { for (let a = o; a; a = a.parent) if (a.userData?.group) return a.userData.group; return null; }

/**
 * Região escura da tabela ('escuros': interior de abertura que a malha não separa) para a malha, no
 * espaço da própria geometria: a caixa vem em mm do CAD (placa montada), com o GLB em metros e Y para
 * cima sob a raiz; null se a peça não tem região.
 */
function escuroDe(o, raiz) {
  const nomes = nomesDe(o);
  const r = (TABELA.escuros ?? []).find((e) => nomes.includes(e.peca));
  if (!r) return null;
  raiz.updateMatrixWorld(true);
  const rel = new THREE.Matrix4().copy(raiz.matrixWorld).invert().multiply(o.matrixWorld).invert();   // raiz -> malha
  const cad = (x, y, z) => new THREE.Vector3(x / 1000, z / 1000, -y / 1000).applyMatrix4(rel);
  const [x0, y0, z0] = r.caixa_mm.de, [x1, y1, z1] = r.caixa_mm.ate;
  const caixa = new THREE.Box3();
  for (const x of [x0, x1]) for (const y of [y0, y1]) for (const z of [z0, z1]) caixa.expandByPoint(cad(x, y, z));
  return { min: caixa.min, max: caixa.max, trans: (r.transicao_mm ?? 1) / 1000, luz: r.luz ?? 0.1 };
}

/** Resolve o material da tabela para uma malha (ver a ordem em materials.json, "descricao"). */
export function resolveMaterial(o, nomeMatGlb) {
  // slot de material do passo do Blender (nome listado em materiais_glb) é mais específico que a peça
  if (nomeMatGlb && TABELA.materiais_glb[nomeMatGlb]) return { id: TABELA.materiais_glb[nomeMatGlb], por: `material ${nomeMatGlb}` };
  for (const n of nomesDe(o)) {
    if (TABELA.pecas[n]) return { id: TABELA.pecas[n], por: `peça ${n}` };
    for (const p of TABELA.padroes) if (new RegExp(p.regex).test(n)) return { id: p.material, por: `padrão ${p.regex}` };
  }
  const g = grupoDe(o);
  if (g && TABELA.grupos[g]) return { id: TABELA.grupos[g], por: `grupo ${g}` };
  return { id: TABELA.padrao, por: 'padrão' };
}

const MASCARA_DBG = typeof location !== 'undefined' && new URLSearchParams(location.search).has('ldmascara');
const MASCARA_POS = typeof location !== 'undefined' && new URLSearchParams(location.search).get('ldmascara') === 'pos';
const FRAG_PARS = 'uniform float uApaga;\nuniform float uRealce;\nuniform vec3 uRealceCor;\nuniform float uMicro;\nuniform float uEnvLd;\nuniform float uInteriorLd;\nuniform float uAbertoLd;\n#ifdef LD_ESCURO\nuniform vec3 uEscMin;\nuniform vec3 uEscMax;\nuniform float uEscTrans;\nuniform float uEscLuz;\nvarying vec3 vPosLd;\n#endif\n';
// Micro-sombra (a "micro shadowing" dos motores de tempo real, fórmula da HDRP): o mapa de sombra não
// resolve cavidades de décimos de milímetro (frestas das grades e das aletas, fundo dos anéis), então a
// oclusão assada também apaga a luz direta que chega rasante: sombra = sat(|N.L| + 2 ao² - 1). Superfície
// aberta (ao = 1) não muda; lâmina com ao 0,8 perde a luz rasante. Força 'micro_sombra' do material.
const FRAG_MICRO_PARS = `#ifdef USE_AOMAP
void RE_Direct_Micro( IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float aoLd = texture2D( aoMap, vAoMapUv ).r;
	float sombraLd = saturate( abs( dot( geometryNormal, directLight.direction ) ) + 2.0 * aoLd * aoLd - 1.0 );
	directLight.color *= mix( 1.0, sombraLd, uMicro );
	RE_Direct_Physical( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
}
#undef RE_Direct
#define RE_Direct RE_Direct_Micro
#endif`;
// 'env' do material: multiplica a luz que vem do ambiente (a three ignora envMapIntensity com
// scene.environment).
//
// 'interior' do material: peça de dentro da carcaça (cooler, placa de circuito, cabos). Montada, ela só
// recebe a luz que passa pelas grades e pela abertura do conector; mas só a luz principal faz sombra e o
// ambiente não sabe da carcaça, então o interior visto pelas grades e por trás das pás acenderia. Com a
// placa montada, toda a luz dessas peças cai para a fração 'interior' e volta a 1 conforme o desmonte
// abre a carcaça (uAbertoLd, de 0 a 1: o uniforme ABERTO, que o estúdio atualiza a cada quadro).
const FRAG_MICRO = `float interiorLd = mix( uInteriorLd, 1.0, uAbertoLd );
#ifdef LD_ESCURO
	// região escura da peça (interior de abertura, 'escuros' da tabela), no espaço da própria malha:
	// acompanha a peça na explosão; borda suave de uEscTrans
	vec3 dentroLd = smoothstep( uEscMin - uEscTrans, uEscMin + uEscTrans, vPosLd ) * ( 1.0 - smoothstep( uEscMax - uEscTrans, uEscMax + uEscTrans, vPosLd ) );
	interiorLd *= mix( 1.0, uEscLuz, dentroLd.x * dentroLd.y * dentroLd.z );
#endif
reflectedLight.indirectDiffuse *= uEnvLd * interiorLd;
reflectedLight.indirectSpecular *= uEnvLd * interiorLd;
reflectedLight.directDiffuse *= interiorLd;
reflectedLight.directSpecular *= interiorLd;
#ifdef USE_CLEARCOAT
	clearcoatSpecularIndirect *= uEnvLd * interiorLd;
	clearcoatSpecularDirect *= interiorLd;
#endif
#include <aomap_fragment>`;
/** Quanto a carcaça está aberta (0 montada, 1 aberta): uniforme comum a todos os materiais. */
const ABERTO = { value: 1 };
const FRAG_FIM = `#include <opaque_fragment>
	{
		// destaque realista: o resto escurece e perde a cor; a peça destacada ganha recorte de luz
		float lumLd = dot( gl_FragColor.rgb, vec3( 0.2126, 0.7152, 0.0722 ) );
		gl_FragColor.rgb = mix( gl_FragColor.rgb, vec3( min( lumLd, 1.5 ) ) * 0.12, uApaga );
		gl_FragColor.rgb = min( gl_FragColor.rgb, vec3( mix( 64.0, 0.2, uApaga ) ) );   // reflexo forte não fura o escurecido
		float frLd = 1.0 - saturate( dot( normal, geometryViewDir ) );
		float fr2Ld = frLd * frLd;
		float aoRealceLd = 1.0;
		#ifdef USE_AOMAP
			// recorte só no contorno: dentro das frestas (oclusão baixa) as paredes rasantes não acendem
			aoRealceLd = texture2D( aoMap, vAoMapUv ).r;
			aoRealceLd *= aoRealceLd * aoRealceLd;
		#endif
		gl_FragColor.rgb += uRealceCor * ( fr2Ld * fr2Ld * frLd ) * uRealce * aoRealceLd;
	}`;

/** Instala o trecho de shader do destaque (idempotente; refaz depois de material.clone()). */
export function preparaMaterial(m, corRealce) {
  m.userData.ld = { apaga: { value: 0 }, realce: { value: 0 }, cor: { value: corRealce.clone() }, micro: { value: m.userData.micro ?? 0 }, env: { value: m.userData.env ?? 1 }, interior: { value: m.userData.interior ?? 1 } };
  const esc = m.userData.escuro ?? null;      // { min, max (espaço da malha), trans, luz }
  m.onBeforeCompile = (sh) => {
    if (esc) {
      sh.defines = { ...(sh.defines ?? {}), LD_ESCURO: '' };
      Object.assign(sh.uniforms, { uEscMin: { value: esc.min }, uEscMax: { value: esc.max }, uEscTrans: { value: esc.trans }, uEscLuz: { value: esc.luz } });
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vPosLd;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvPosLd = position;');
    }
    sh.uniforms.uApaga = m.userData.ld.apaga;
    sh.uniforms.uRealce = m.userData.ld.realce;
    sh.uniforms.uRealceCor = m.userData.ld.cor;
    sh.uniforms.uMicro = m.userData.ld.micro;
    sh.uniforms.uEnvLd = m.userData.ld.env;
    sh.uniforms.uInteriorLd = m.userData.ld.interior;
    sh.uniforms.uAbertoLd = ABERTO;
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>\n${FRAG_PARS}`)
      .replace('#include <lights_physical_pars_fragment>', `#include <lights_physical_pars_fragment>\n${FRAG_MICRO_PARS}`)
      .replace('#include <aomap_fragment>', FRAG_MICRO)
      .replace('#include <opaque_fragment>', FRAG_FIM);
  };
  m.customProgramCacheKey = () => (esc ? 'lookdev-destaque-7-escuro' : 'lookdev-destaque-7');
  return m;
}

/**
 * Troca os materiais do GLB pelos da tabela. Malha sem normais ganha normais planas; malha que
 * precisa de textura e não tem UV ganha UV (caixa em mm ou plana na caixa envolvente).
 * Devolve o relatório (malha, material, por quê) para conferência.
 */
export function aplicaMateriais(raiz, { medidas, q, corRealce }) {
  const valor = (v) => {
    if (typeof v === 'number') return v;
    const m = medidas?.[v.medida]?.value_mm;
    return (m != null ? m : v.reserva) * (v.fator ?? 1);
  };
  const cacheTex = new Map();
  const relatorio = [];
  const malhas = [];
  raiz.traverse((o) => { if (o.isMesh) malhas.push(o); });
  for (const o of malhas) {
    const orig = Array.isArray(o.material) ? o.material[0] : o.material;
    const nomeGlb = orig?.name ?? '';
    const { id, por } = resolveMaterial(o, nomeGlb);
    const def = TABELA.materiais[id] ?? TABELA.materiais[TABELA.padrao];
    // Mapas do GLB (passo do Blender) mandam, canal a canal: cor, normal, rugosidade e metal do GLB
    // substituem os da textura procedural; o canal que o GLB não traz continua procedural (por exemplo,
    // a peça que só ganhou oclusão assada mantém o grão da tabela).
    const mapasGlb = !!(orig?.map || orig?.normalMap || orig?.roughnessMap || orig?.metalnessMap || orig?.aoMap);
    let geo = o.geometry;
    const tx = def.textura;
    if (!geo.attributes.normal || (tx && !geo.attributes.uv2) || (tx?.uv === 'cavidade' && geo.index)) {
      if (geo.index) geo = geo.toNonIndexed();
      if (!geo.attributes.normal) geo.computeVertexNormals();      // não indexada: normais planas
      o.geometry = geo;
    }
    let tex = null;
    if (tx) {
      let bbox = null;
      if (tx.uv === 'planar_bbox') bbox = uvPlanar(geo);
      else if (tx.uv === 'cavidade') uvCavidade(geo);
      else if (!geo.attributes.uv2 || geo.userData.ldTile !== (tx.tipo === 'aletas' ? valor(tx.passo_mm) : tx.tile_mm)) {
        const tile = tx.tipo === 'aletas' ? valor(tx.passo_mm) : tx.tile_mm;
        uvCaixa(geo, tile);
        geo.userData.ldTile = tile;
      }
      // texturas presas à caixa da malha são por malha; as de repetição, por material
      const chave = bbox ? `${id}|${bbox.tam.map((x) => x.toFixed(1)).join('x')}|${o.name}` : id;
      if (!cacheTex.has(chave)) {
        const sem = [...chave].reduce((h, ch) => Math.imul(h ^ ch.charCodeAt(0), 16777619), 2166136261);
        cacheTex.set(chave, GERADORES[tx.tipo](def, tx, q.tex, prng(sem), { valor, bbox }));
      }
      tex = cacheTex.get(chave);
    }
    const fis = q.fisico && !!(def.anisotropia || def.verniz || tex?.aniso);
    const M = fis ? THREE.MeshPhysicalMaterial : THREE.MeshStandardMaterial;
    const m = new M({ name: id, color: def.cor, metalness: def.metal, roughness: def.rug, envMapIntensity: def.env ?? 1 });
    if (tex) {
      m.roughnessMap = tex.orm; m.metalnessMap = tex.orm; m.roughness = 1; m.metalness = 1;
      m.normalMap = tex.normal; m.normalScale.set(1, 1);
      if (tex.map) { m.map = tex.map; m.color.set(0xffffff); }
    }
    if (fis && (def.anisotropia || tex?.aniso)) {
      m.anisotropy = def.anisotropia?.forca ?? tx?.cubo?.anisotropia ?? 0.5;
      if (tex?.aniso) m.anisotropyMap = tex.aniso;
    }
    if (fis && def.verniz) {
      m.clearcoat = def.verniz.forca; m.clearcoatRoughness = def.verniz.rug;
      // laca sob verniz: o reflexo é o do verniz; a camada de baixo (pigmento) quase não tem especular
      // próprio (sem isto o reflexo dobra e a peça clareia). Sem verniz (qualidade baixa) vale 'rug'.
      if (def.verniz.especular_base != null) m.specularIntensity = def.verniz.especular_base;
    }
    if (mapasGlb) {
      // cor, ORM, normal e oclusão assados no Blender; a tabela dá só o que o GLB não traz
      for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap']) if (orig[k]) m[k] = orig[k];
      if (orig.aoMap) m.aoMapIntensity = def.ao ?? 1;
      if (orig.map) m.color.set(0xffffff);
      if (orig.roughnessMap) m.roughness = orig.roughness;
      if (orig.metalnessMap) m.metalness = orig.metalness;
      if (orig.normalMap) m.normalScale.copy(orig.normalScale);
      if (orig.emissiveMap) m.emissive.copy(orig.emissive);
    }
    if (tex?.ao && !orig?.aoMap) { m.aoMap = tex.ao; m.aoMapIntensity = def.ao ?? 1; }
    if (orig?.aoMap || tex?.ao) m.userData.micro = def.micro_sombra ?? 0;
    if (def.env != null) m.userData.env = def.env;
    if (def.interior != null) m.userData.interior = def.interior;
    const esc = escuroDe(o, raiz);
    if (esc) m.userData.escuro = esc;
    if (def.sobre_coplanar) {
      // superfície fina sobre outra quase coplanar (fração de mm): ganha o teste de profundidade
      m.polygonOffset = true; m.polygonOffsetFactor = -1; m.polygonOffsetUnits = -4;
    }
    preparaMaterial(m, corRealce);
    o.material = m;
    if (MASCARA_DBG) {
      const idx = Object.keys(TABELA.materiais).indexOf(id) + 1;
      o.material = new THREE.ShaderMaterial({
        uniforms: { uId: { value: idx * 9 / 255 } },
        vertexShader: 'varying vec3 vN; varying vec3 vP; void main(){ vN = normalize(mat3(modelMatrix) * normal); vP = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
        fragmentShader: MASCARA_POS ? 'uniform float uId; varying vec3 vN; varying vec3 vP; void main(){ gl_FragColor = vec4(vP.x / 320.0, vP.y / 160.0, (vP.z + 10.0) / 60.0, 1.0); }' : 'uniform float uId; varying vec3 vN; void main(){ vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n; gl_FragColor = vec4(uId, abs(n.z), 1.0, 1.0); }',
        side: THREE.DoubleSide,
      });
    }
    o.castShadow = o.receiveShadow = true;
    const doGlb = mapasGlb ? ['map', 'normalMap', 'roughnessMap', 'aoMap'].filter((k) => orig[k]).map((k) => (k === 'map' ? 'cor' : k.replace('Map', ''))) : [];
    relatorio.push({ malha: o.name, material: id, por, mapas: mapasGlb ? `glb (${doGlb.join(', ')})${tx ? ` + ${tx.tipo}` : ''}` : tx ? tx.tipo : null });
  }
  return relatorio;
}

// ---------------------------------------------------------------------------------------------
// Estúdio: ambiente (HDR escurecido + caixas de luz), luzes diretas e chão
// ---------------------------------------------------------------------------------------------
function texturaHdr() {
  const bin = atob(HDR_B64);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  const loader = new RGBELoader();
  loader.setDataType(THREE.HalfFloatType);
  const d = loader.parse(buf.buffer);
  const t = new THREE.DataTexture(d.data, d.width, d.height, THREE.RGBAFormat, d.type);
  t.colorSpace = THREE.LinearSRGBColorSpace;
  t.magFilter = t.minFilter = THREE.LinearFilter;
  t.generateMipmaps = false;
  t.flipY = true;
  t.needsUpdate = true;
  return t;
}

/** Ambiente pré-filtrado (PMREM) no referencial canônico: câmera em -y olhando +y, acima (z+). */
function criaAmbiente(renderer, cfg, corDe) {
  const cena = new THREE.Scene();
  const hdr = texturaHdr();
  const esfera = new THREE.Mesh(new THREE.SphereGeometry(60, 64, 32),
    new THREE.MeshBasicMaterial({ map: hdr, side: THREE.BackSide, color: corDe(cfg.hdr.K).multiplyScalar(cfg.hdr.i), toneMapped: false }));
  esfera.rotation.x = Math.PI / 2;                           // equirretangular com Y para cima -> Z para cima
  cena.add(esfera);
  const SEM_DBG = new URLSearchParams(location.search).get('ldsem')?.split(',') ?? [];
  for (const c of cfg.caixas) {
    if (SEM_DBG.includes(c.nome)) continue;
    const mat = new THREE.MeshBasicMaterial({ color: corDe(c.K).multiplyScalar(c.i), side: THREE.DoubleSide, toneMapped: false });
    if (c.degrade || c.listras) {
      // softbox com degradê (de c.degrade[0] a c.degrade[1] ao longo da largura): o reflexo nas faces
      // planas vira um degradê, como nas fotos de produto, em vez de um cinza chapado. 'listras' [n,
      // fração acesa]: n faixas acesas ao longo da altura, de borda nítida, com vãos escuros entre elas;
      // nas superfícies espelhadas (tampas do X) o reflexo ganha bordas e não lê como tinta cinza; nas
      // foscas a média é que conta
      const n = 64, m = c.listras ? 128 : 1, d = new Uint8Array(n * m * 4);
      for (let j = 0; j < m; j++) {
        let k = 1;
        if (c.listras) {
          const [nl, fr] = c.listras, f = ((j + 0.5) / m) * nl % 1;
          k = Math.abs(f - 0.5) < fr / 2 ? 1 : (c.vao ?? 0);
        }
        for (let i = 0; i < n; i++) {
          const t = i / (n - 1);
          const g = c.degrade ? c.degrade[0] + (c.degrade[1] - c.degrade[0]) * suave(t) : 1;
          const v = byte(g * k);
          d.set([v, v, v, 255], (j * n + i) * 4);
        }
      }
      const t = new THREE.DataTexture(d, n, m);
      t.magFilter = t.minFilter = THREE.LinearFilter;
      t.needsUpdate = true;
      mat.map = t;
    }
    const p = new THREE.Mesh(new THREE.PlaneGeometry(c.tam[0], c.tam[1]), mat);
    p.position.set(...c.pos);
    p.lookAt(0, 0, 0);
    cena.add(p);
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  const rt = pmrem.fromScene(cena, 0, 0.1, 200);
  pmrem.dispose();
  hdr.dispose();
  return rt.texture;
}

/** Sombra de contato: núcleo escuro e justo mais penumbra larga, desenhados uma vez num canvas. */
function sombraContato(L, H, c) {
  const px = 2, m = c.folga + c.desfoque * 2;
  const W = Math.round((L + 2 * m) * px), Hh = Math.round((H + 2 * m) * px);
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = Hh;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, Hh);
  ctx.filter = `blur(${c.desfoque * px * 0.5}px)`;
  ctx.fillStyle = '#5a5a5a';                                  // penumbra larga
  ctx.fillRect(m * px - c.folga * px, m * px - c.folga * px, (L + 2 * c.folga) * px, (H + 2 * c.folga) * px);
  ctx.filter = `blur(${c.nucleo * px}px)`;
  ctx.globalCompositeOperation = 'lighten';
  ctx.fillStyle = '#fff';                                     // núcleo: a placa encostando no chão
  ctx.fillRect(m * px, m * px, L * px, H * px);
  ctx.filter = 'none';
  const tex = new THREE.CanvasTexture(cv);
  const mat = new THREE.MeshBasicMaterial({ color: 0x000000, alphaMap: tex, transparent: true, opacity: c.opacidade, depthWrite: false });
  const plano = new THREE.Mesh(new THREE.PlaneGeometry(W / px, Hh / px), mat);
  plano.renderOrder = -1;
  return plano;
}

/**
 * Estúdio que acompanha a câmera, como numa mesa giratória de foto de produto: as luzes e o ambiente
 * giram com o azimute da câmera (a luz principal fica sempre do mesmo lado do quadro) e viram para o
 * outro lado da placa, de forma contínua, quando a câmera passa para a outra face (z abaixo do meio
 * da espessura). O chão só aparece com a câmera do lado dos ventiladores e acima do plano da placa:
 * some na virada, do lado da face oposta, com a câmera rasante e durante a explosão.
 */
export function criaEstudio({ renderer, scene, cfg, q, medidas, luz }) {
  const m = (k, d) => medidas?.[k]?.value_mm ?? d;
  const L = m('card_envelope_length', 304.8), H = m('card_envelope_height', 137.16), T = 40;
  const centro = new THREE.Vector3(L / 2, H / 2, T / 2);
  const Kforcado = luz === 'fria' ? cfg.luzFria : luz === 'quente' ? cfg.luzQuente : null;
  // Balanço de branco da câmera, como numa foto de produto: a câmera é balanceada na luz principal do
  // estúdio (cfg.balanco_K, se o tema der; senão a temperatura da luz 'principal'). Sem isto, kelvin()
  // mede contra o branco do sRGB (D65, cerca de 6500 K) e as luzes de 5200 a 5800 K deixavam a placa
  // inteira quente (R > G > B nas pás e nas tampas, segunda passada do visual-qa, achado N2). O balanço
  // é fixo: com ?luz=fria|quente as luzes mudam e a câmera não, e a conferência mostra a diferença.
  const Kbalanco = cfg.balanco_K ?? cfg.luzes.find((l) => l.papel === 'principal')?.K ?? 6500;
  const branco = kelvin(Kbalanco);
  const corDe = (K) => {
    const c = kelvin(Kforcado ?? K);
    c.setRGB(c.r / branco.r, c.g / branco.g, c.b / branco.b);
    return c.multiplyScalar(1 / (0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b));   // mantém a luminância 1
  };

  scene.environment = criaAmbiente(renderer, cfg, corDe);
  scene.environmentIntensity = cfg.ambiente;

  const SEM_DBG = new URLSearchParams(location.search).get('ldsem')?.split(',') ?? [];
  const luzes = cfg.luzes.map((l) => {
    const d = new THREE.DirectionalLight(corDe(l.K), SEM_DBG.includes(l.papel) ? 0 : l.i);
    d.userData.off = new THREE.Vector3(...l.pos);
    if (l.sombra && q.sombra) {
      d.castShadow = true;
      d.shadow.mapSize.set(q.sombra, q.sombra);
      Object.assign(d.shadow.camera, { left: -270, right: 270, top: 270, bottom: -270, near: 50, far: 2200 });
      d.shadow.bias = -0.0003;
      d.shadow.normalBias = 0.35;
      d.shadow.radius = 4;
    }
    d.target.position.copy(centro);
    scene.add(d, d.target);
    return d;
  });

  // chão: só sombra (ShadowMaterial) e sombra de contato; preso ao lado oposto ao da câmera
  const chao = new THREE.Group();
  chao.position.copy(centro);
  const zChao = -T / 2 - cfg.chao.folga;
  const recebe = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.ShadowMaterial({ opacity: cfg.chao.sombra }));
  recebe.position.z = zChao;
  recebe.receiveShadow = true;
  const contato = sombraContato(L, H, cfg.chao.contato);
  contato.position.z = zChao + 0.3;
  chao.add(recebe, contato);
  scene.add(chao);

  const R = new THREE.Matrix4(), Ra = new THREE.Matrix4(), Rf = new THREE.Matrix4(), Rinv = new THREE.Matrix4();
  const e = new THREE.Euler(), d = new THREE.Vector3(), eu = new THREE.Vector3(), ev = new THREE.Vector3();
  const raioLuz = Math.tan(((cfg.acumula?.luz_graus ?? 0) * Math.PI) / 180);   // raio angular da luz de área
  return {
    centro,
    /** Atualiza o estúdio para a câmera e o nível de explosão do quadro (puro: só depende deles). */
    atualiza(camera, explosao, luzAmostra = null) {
      d.subVectors(camera.position, centro);
      let phi = Math.atan2(d.y, d.x);
      if (Math.hypot(d.x, d.y) < 1e-3) phi = -Math.PI / 2;
      const s = suave(clamp01((d.z + cfg.virada) / (2 * cfg.virada)));
      const theta = Math.PI * (1 - s);
      Ra.makeRotationZ(phi + Math.PI / 2);
      Rf.makeRotationY(theta);
      R.multiplyMatrices(Ra, Rf);
      for (const l of luzes) {
        l.position.copy(l.userData.off);
        // acumulação: a luz que faz sombra varia num disco perpendicular a ela (luz de área): sombra suave
        if (luzAmostra && l.castShadow && raioLuz > 0) {
          const off = l.userData.off, dist = off.length();
          eu.set(-off.y, off.x, 0);
          if (eu.lengthSq() < 1e-6) eu.set(1, 0, 0);
          eu.normalize();
          ev.crossVectors(off, eu).normalize();
          l.position.addScaledVector(eu, luzAmostra[0] * raioLuz * dist).addScaledVector(ev, luzAmostra[1] * raioLuz * dist);
        }
        l.position.applyMatrix4(R).add(centro);
      }
      // three usa makeRotationFromEuler(-e) na consulta do ambiente: escolhe e para que isso dê R^-1
      Rinv.copy(R).invert();
      e.setFromRotationMatrix(Rinv);
      scene.environmentRotation.set(-e.x, -e.y, -e.z, e.order);
      chao.rotation.x = theta;
      // O chão só aparece com a câmera do lado dos ventiladores (a placa deitada sobre a mesa, vista de
      // cima). Com a câmera do lado da face oposta, o chão viraria um teto atrás da placa e a sombra, uma
      // laje solta no fundo preto; e com a câmera rasante ao plano da placa, a sombra se descola da placa
      // e vira uma faixa. Nos dois casos o chão some, de forma contínua.
      const lado = suave(clamp01(d.z / cfg.virada));
      const elev = Math.asin(clamp01(Math.abs(d.z) / Math.max(d.length(), 1e-6))) * (180 / Math.PI);
      const fElev = suave(clamp01((elev - (cfg.chao.elev_min ?? 12)) / ((cfg.chao.elev_cheia ?? 28) - (cfg.chao.elev_min ?? 12))));
      const fChao = Math.pow(Math.abs(Math.cos(theta)), 8) * lado * fElev * (1 - suave(clamp01(explosao / 0.6)));
      // carcaça aberta: de TABELA.interior_aberto.de a .ate no nível de explosão (contínuo)
      const ab = TABELA.interior_aberto ?? { de: 1.5, ate: 3 };
      ABERTO.value = suave(clamp01((explosao - ab.de) / (ab.ate - ab.de)));
      recebe.material.opacity = cfg.chao.sombra * fChao;
      contato.material.opacity = cfg.chao.contato.opacidade * fChao;
      chao.visible = fChao > 0.002;
    },
  };
}

// ---------------------------------------------------------------------------------------------
// Pós-processamento: cena em HalfFloat com MSAA, GTAO (alta), profundidade de campo, AgX
// ---------------------------------------------------------------------------------------------
const FINAL_VS = `precision highp float;
uniform mat4 modelViewMatrix; uniform mat4 projectionMatrix;
attribute vec3 position; attribute vec2 uv; varying vec2 vUv;
void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 ); }`;
const FINAL_FS = `precision highp float;
uniform sampler2D tCor; uniform sampler2D tProf;
uniform vec2 uTexel; uniform float uFoco; uniform float uAbertura; uniform float uMaxCoc;
uniform float uNear; uniform float uFar; uniform float uRot; uniform float uFase;
#include <tonemapping_pars_fragment>
varying vec2 vUv;
float vista( vec2 uv ) {
	float d = texture2D( tProf, uv ).x;
	return ( uNear * uFar ) / ( ( uFar - uNear ) * d - uFar ) * -1.0;
}
float coc( float z ) { return min( uMaxCoc, uAbertura * abs( z - uFoco ) / max( z, 1.0 ) ); }
void main() {
	vec4 c = texture2D( tCor, vUv );
	#if TAPS > 0
		float zc = vista( vUv ), cc = coc( zc );
		vec4 soma = c; float peso = 1.0;
		for ( int i = 0; i < TAPS; i ++ ) {
			float fi = float( i );
			// espiral de ouro; na acumulação, cada amostra gira a espiral e desloca os raios (uRot, uFase)
			float r = sqrt( ( fi + uFase ) / float( TAPS ) ) * uMaxCoc;
			float a = fi * 2.39996323 + uRot;
			vec2 uv = vUv + vec2( cos( a ), sin( a ) ) * r * uTexel;
			float z = vista( uv );
			float ct = coc( z );
			// o que está atrás só desfoca por cima de um ponto que também está desfocado
			float cEf = z < zc ? ct : min( ct, cc );
			float w = clamp( cEf - r + 0.5, 0.0, 1.0 );
			soma += texture2D( tCor, uv ) * w; peso += w;
		}
		c = soma / peso;
	#endif
	float a = c.a;
	vec3 rgb = a > 1e-4 ? c.rgb / a : vec3( 0.0 );
	#if defined( AGX_TONE_MAPPING )
		rgb = AgXToneMapping( rgb );
	#elif defined( ACES_FILMIC_TONE_MAPPING )
		rgb = ACESFilmicToneMapping( rgb );
	#endif
	// sai em linear, já com tons (0 a 1) e alfa pré-multiplicado: é o que se acumula (média correta
	// das bordas, sem o reflexo forte dominar); a passagem de exibição aplica sRGB e o pontilhado
	gl_FragColor = vec4( rgb * a, a );
}`;
// Exibição: média acumulada (linear, pré-multiplicada) para a tela, em sRGB, com pontilhado fixo.
const EXIBE_FS = `precision highp float;
uniform sampler2D tAcum;
#include <colorspace_pars_fragment>
varying vec2 vUv;
void main() {
	vec4 c = texture2D( tAcum, vUv );
	float a = clamp( c.a, 0.0, 1.0 );
	vec3 rgb = a > 1e-4 ? c.rgb / c.a : vec3( 0.0 );
	rgb = sRGBTransferOETF( vec4( rgb, 1.0 ) ).rgb;
	// pontilhado ordenado de meio nível (fixo por pixel): sem faixas no degradê escuro, determinístico
	vec2 p = floor( mod( gl_FragCoord.xy, 4.0 ) );
	float bayer = mod( p.x * 2.0 + p.y * 3.0 + p.x * p.y, 4.0 ) / 4.0 - 0.375;
	rgb += bayer / 255.0;
	gl_FragColor = vec4( rgb * a, a );
}`;

/**
 * Pós-processamento com acumulação. render(foco, k, amostra): desenha a amostra k (0 = quadro normal)
 * e a mistura na média (alvo HalfFloat, peso 1/(k+1) pela cor constante do blend, sem cópia de ida e
 * volta); exibe() leva a média para a tela. A amostra desloca a projeção em subpixel (jx, jy), gira a
 * espiral da profundidade de campo e desloca os raios.
 */
export function criaPos({ renderer, scene, camera, q, W, H, cfg }) {
  const prof = new THREE.DepthTexture(W, H);
  prof.type = THREE.UnsignedIntType;
  const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: q.msaa, depthTexture: prof });
  // média das amostras (linear com tons, pré-multiplicada); só é lida pela exibição
  const acum = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: false });
  let gtao = null, rtAo = null;
  if (q.ao) {
    gtao = new GTAOPass(scene, camera, W, H);
    gtao.output = GTAOPass.OUTPUT.Default;
    gtao.blendIntensity = cfg.ao.intensidade;
    gtao.updateGtaoMaterial({ radius: cfg.ao.raio, distanceExponent: 1.5, thickness: cfg.ao.espessura, scale: 1, samples: 16 });
    gtao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 16 });
    rtAo = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
  }
  const defines = { TAPS: q.dof };
  if (renderer.toneMapping === THREE.AgXToneMapping) defines.AGX_TONE_MAPPING = '';
  else if (renderer.toneMapping === THREE.ACESFilmicToneMapping) defines.ACES_FILMIC_TONE_MAPPING = '';
  const mat = new THREE.RawShaderMaterial({
    defines,
    uniforms: {
      tCor: { value: null }, tProf: { value: prof }, uTexel: { value: new THREE.Vector2(1 / W, 1 / H) },
      uFoco: { value: 500 }, uAbertura: { value: 0 }, uMaxCoc: { value: 1 }, uNear: { value: 1 }, uFar: { value: 6000 },
      uRot: { value: 0 }, uFase: { value: 0.5 },
      toneMappingExposure: { value: 1 },
    },
    vertexShader: FINAL_VS, fragmentShader: FINAL_FS, depthTest: false, depthWrite: false,
  });
  // mistura na média: novo * w + média * (1 - w), com w = 1/(k+1) na cor constante do blend
  mat.transparent = false;
  mat.blending = THREE.CustomBlending;
  mat.blendEquation = mat.blendEquationAlpha = THREE.AddEquation;
  mat.blendSrc = mat.blendSrcAlpha = THREE.ConstantAlphaFactor;
  mat.blendDst = mat.blendDstAlpha = THREE.OneMinusConstantAlphaFactor;
  const quad = new FullScreenQuad(mat);
  const matExibe = new THREE.RawShaderMaterial({
    uniforms: { tAcum: { value: acum.texture } },
    vertexShader: FINAL_VS, fragmentShader: EXIBE_FS, depthTest: false, depthWrite: false, blending: THREE.NoBlending,
  });
  const quadExibe = new FullScreenQuad(matExibe);
  const escala = W / 1920;                                    // CoC em px do palco lógico
  const pm = camera.projectionMatrix.elements;
  return {
    render(foco, k = 0, am = null) {
      // deslocamento de subpixel: soma na terceira coluna da projeção (e desfaz depois do desenho)
      const s8 = pm[8], s9 = pm[9];
      if (am) {
        pm[8] += (2 * am.jx) / W; pm[9] += (2 * am.jy) / H;
        camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
      }
      renderer.setRenderTarget(rt);
      renderer.clear();
      renderer.render(scene, camera);
      let cor = rt.texture;
      if (gtao) { gtao.render(renderer, rtAo, rt); cor = rtAo.texture; }
      if (am) {
        pm[8] = s8; pm[9] = s9;
        camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
      }
      const u = mat.uniforms;
      u.tCor.value = cor;
      u.uFoco.value = foco;
      u.uAbertura.value = cfg.dof.abertura * escala;
      u.uMaxCoc.value = Math.max(0.5, (q.dof > 12 ? cfg.dof.maxCocAlta : cfg.dof.maxCoc) * escala);
      u.uNear.value = camera.near; u.uFar.value = camera.far;
      u.uRot.value = am ? am.rot : 0;
      u.uFase.value = am ? am.fase : 0.5;
      u.toneMappingExposure.value = renderer.toneMappingExposure;
      mat.blendAlpha = 1 / (k + 1);                           // k = 0: substitui a média
      renderer.setRenderTarget(acum);
      const ac = renderer.autoClear;
      renderer.autoClear = false;                             // a média não pode ser limpa
      quad.render(renderer);
      renderer.autoClear = ac;
    },
    exibe() {
      renderer.setRenderTarget(null);
      quadExibe.render(renderer);
    },
    dispose() { rt.dispose(); acum.dispose(); prof.dispose(); rtAo?.dispose(); gtao?.dispose(); mat.dispose(); matExibe.dispose(); quad.dispose(); quadExibe.dispose(); },
  };
}
