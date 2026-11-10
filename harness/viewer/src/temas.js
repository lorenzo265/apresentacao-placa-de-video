// Temas visuais opcionais (?tema=keynote|estudio|blueprint). Sem ?tema, nada daqui é usado
// e o viewer desenha exatamente como antes. Cada tema reúne:
//   fundo:     imagem fixa do palco (desenhada uma vez num canvas 2D, com pontilhado contra faixas)
//   cena:      luzes, exposição, ambiente, sombra, materiais das peças, arestas e sombra de contato
//   diagramas: raio de canto, fonte dos rótulos, estilo dos fluxos, sombra das placas
//   chamada:   cor da linha quando o beat não pertence a um dos três caminhos
// As cores dos três caminhos (energia, dados, calor) e dos selos de procedência são semânticas:
// os temas ajustam o tom para o fundo, mas não trocam o significado.

export const TEMAS = {
  // A. Keynote: preto profundo, um verde de acento, traço fino com brilho, luz correndo nos fluxos.
  keynote: {
    fundo: {
      base: '#020303',
      halos: [
        { x: 0.56, y: 0.42, r: 0.62, cor: [18, 24, 22], a: 1 },
        { x: 0.56, y: 0.50, r: 0.30, cor: [24, 34, 26], a: 0.55 },
      ],
      vinheta: 0.78,
    },
    linha: '#8fdc2a',
    cena: {
      exposicao: 1.0,
      ambiente: 0.9, ambienteLuz: 0.06,
      luzes: [
        { cor: 0xffffff, i: 1.9, pos: [160, -360, 640], sombra: true },
        { cor: 0x9fc2ff, i: 0.35, pos: [-420, -160, 200] },
        { cor: 0xd8ffb0, i: 3.2, pos: [-200, 700, 160] },
        { cor: 0xffffff, i: 0.9, pos: [760, 260, 60] },
      ],
      sombra: 0.6,
      contato: { opacidade: 0.8, folga: 12, desfoque: 26 },
      materiais: {
        carcaca: { cor: 0x30353b, metal: 0.55, rug: 0.4 },
        cooler: { cor: 0x4c535a, metal: 0.7, rug: 0.36 },
        pcb: { cor: 0x123320, metal: 0.15, rug: 0.55 },
        memoria: { cor: 0x3a3428, metal: 0.4, rug: 0.45 },
        energia: { cor: 0x4a3626, metal: 0.4, rug: 0.4 },
        io: { cor: 0x9aa1aa, metal: 0.9, rug: 0.28 },
        fixadores: { cor: 0xa9b0b7, metal: 0.9, rug: 0.3 },
      },
      arestas: { cor: 0x9ee04a, nucleo: 1.2, opNucleo: 0.5, halo: 6, opHalo: 0.07, angulo: 30 },
    },
    diagramas: {
      raio: 0.09, rotuloMono: false, sombra: false, hospedeiro: 0.05,
      fluxo: { vel: 240, periodo: 300, camadas: [
        { cls: 'f-halo', l: 90 }, { cls: 'f-cauda', l: 90 }, { cls: 'f-anim', l: 22 },
      ] },
    },
  },

  // B. Estúdio de produto: grafite com luz de estúdio, placa como foto de produto, placas em relevo.
  estudio: {
    fundo: {
      base: '#18191c',
      faixa: { topo: [44, 46, 50], baixo: [16, 17, 19] },
      halos: [
        { x: 0.52, y: 0.40, r: 0.62, cor: [70, 73, 78], a: 0.55 },
        { x: 0.52, y: 0.30, r: 0.28, cor: [84, 87, 92], a: 0.35 },
      ],
      vinheta: 0.5,
    },
    linha: '#ffffff',
    cena: {
      exposicao: 1.05,
      ambiente: 0.75, ambienteLuz: 0.1,
      luzes: [
        { cor: 0xfff4e8, i: 3.0, pos: [60, -420, 720], sombra: true },
        { cor: 0xd6e4ff, i: 0.9, pos: [-560, -300, 220] },
        { cor: 0xffffff, i: 3.0, pos: [-160, 680, 240] },
        { cor: 0xffffff, i: 0.5, pos: [780, 160, 60] },
      ],
      sombra: 0.5, sombraSuave: true,
      contato: { opacidade: 0.85, folga: 6, desfoque: 18 },
      materiais: {
        carcaca: { cor: 0x6a7078, metal: 0.45, rug: 0.42 },
        cooler: { cor: 0xb3b9c0, metal: 0.7, rug: 0.3 },
        pcb: { cor: 0x1f5135, metal: 0.1, rug: 0.5 },
        memoria: { cor: 0x2e3034, metal: 0.2, rug: 0.4 },
        energia: { cor: 0x3a3c41, metal: 0.3, rug: 0.45 },
        io: { cor: 0xcfd4da, metal: 0.9, rug: 0.24 },
        fixadores: { cor: 0xd3d8de, metal: 0.9, rug: 0.25 },
      },
      arestas: null,
    },
    diagramas: {
      raio: 0.07, rotuloMono: false, sombra: true, hospedeiro: 0.05,
      fluxo: { vel: 90, periodo: 22, camadas: [{ cls: 'f-anim', l: 0 }] },
    },
  },

  // C. Blueprint técnico: azul muito escuro com grade, contorno e cotas, rótulos em monoespaçada.
  blueprint: {
    fundo: {
      base: '#061327',
      halos: [{ x: 0.5, y: 0.45, r: 0.75, cor: [12, 34, 66], a: 0.9 }],
      vinheta: 0.55,
      grade: { passo: 24, cor: 'rgba(150,190,255,0.055)', maior: 5, corMaior: 'rgba(150,190,255,0.12)' },
    },
    linha: '#cfe2ff',
    cena: {
      exposicao: 1.0,
      ambiente: 0.0, ambienteLuz: 0.8,
      luzes: [
        { cor: 0xffffff, i: 1.1, pos: [200, -300, 700] },
        { cor: 0xffffff, i: 0.45, pos: [-400, -300, 150] },
      ],
      sombra: 0, contato: null,
      materiais: {
        '*': { cor: 0x2a5a98, metal: 0, rug: 1 },
      },
      arestas: { cor: 0xcfe2ff, nucleo: 1.4, opNucleo: 0.95, halo: 0, angulo: 25 },
      cotas: true,
    },
    diagramas: {
      raio: 0, rotuloMono: true, sombra: false, hospedeiro: 0.05,
      fluxo: { vel: 40, periodo: 16, camadas: [{ cls: 'f-anim', l: 10 }] },
    },
  },
};

/** Tema pedido na URL (ou embutido), ou null. Nome desconhecido é ignorado com aviso. */
export function temaDaUrl(params) {
  const nome = params.get('tema');
  if (!nome) return null;
  if (!TEMAS[nome]) { console.warn(`[tema] tema desconhecido: ${nome}; usando o padrão`); return null; }
  return { nome, ...TEMAS[nome] };
}

/** Gerador pseudoaleatório fixo: o pontilhado do fundo é o mesmo em toda execução. */
function prng(semente) {
  let s = semente >>> 0;
  return () => { s = (s + 0x6d2b79f5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

/**
 * Desenha o fundo do tema num canvas 1920 x 1080. Calculado pixel a pixel (sem gradiente do
 * navegador), com pontilhado de 1 nível, para não ter faixas nem variar entre execuções.
 */
export function desenhaFundo(canvas, f) {
  const W = canvas.width, H = canvas.height;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(W, H);
  const d = img.data;
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const base = hex(f.base);
  const rnd = prng(20261110);
  const suave = (x) => x * x * (3 - 2 * x);
  for (let y = 0; y < H; y++) {
    const v = y / (H - 1);
    let fr = base[0], fg = base[1], fb = base[2];
    if (f.faixa) {
      const k = suave(v);
      fr = f.faixa.topo[0] + (f.faixa.baixo[0] - f.faixa.topo[0]) * k;
      fg = f.faixa.topo[1] + (f.faixa.baixo[1] - f.faixa.topo[1]) * k;
      fb = f.faixa.topo[2] + (f.faixa.baixo[2] - f.faixa.topo[2]) * k;
    }
    for (let x = 0; x < W; x++) {
      const u = x / (W - 1);
      let r = fr, g = fg, b = fb;
      for (const h of f.halos ?? []) {
        const dx = (u - h.x) * (W / H), dy = v - h.y;
        const q = Math.max(0, 1 - Math.sqrt(dx * dx + dy * dy) / h.r);
        const a = suave(q) * h.a;
        r += (h.cor[0] - r) * a; g += (h.cor[1] - g) * a; b += (h.cor[2] - b) * a;
      }
      if (f.vinheta) {
        const dx = (u - 0.5) * 1.15, dy = (v - 0.5) * 1.15;
        const k = 1 - f.vinheta * suave(Math.min(1, (dx * dx + dy * dy) * 1.9));
        r *= k; g *= k; b *= k;
      }
      const n = rnd() - 0.5;          // pontilhado: ± meio nível
      const i = (y * W + x) * 4;
      d[i] = Math.max(0, Math.min(255, Math.round(r + n)));
      d[i + 1] = Math.max(0, Math.min(255, Math.round(g + n)));
      d[i + 2] = Math.max(0, Math.min(255, Math.round(b + n)));
      d[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  if (f.grade) {
    const { passo, cor, maior, corMaior } = f.grade;
    const x0 = Math.round((W / 2) % passo), y0 = Math.round((H / 2) % passo);
    for (const [c, so] of [[cor, false], [corMaior, true]]) {
      ctx.fillStyle = c;
      for (let x = x0, i = 0; x < W; x += passo, i++) {
        const k = Math.round((x - W / 2) / passo);
        if ((k % maior === 0) === so) ctx.fillRect(x, 0, 1, H);
      }
      for (let y = y0; y < H; y += passo) {
        const k = Math.round((y - H / 2) / passo);
        if ((k % maior === 0) === so) ctx.fillRect(0, y, W, 1);
      }
    }
  }
}
