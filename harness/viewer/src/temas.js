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
      // Fundo de estúdio em cinza-azulado médio (pedido do autor em 2026-11-11: mais claro e com contraste):
      // centro por volta de 130, bordas por volta de 50. A placa preta destaca-se por baixo (sombra de
      // contato) e pelo recorte de luz nas bordas, não pelo fundo escuro.
      base: '#23272b',
      halos: [
        { x: 0.56, y: 0.44, r: 0.85, cor: [112, 119, 126], a: 1 },
        { x: 0.56, y: 0.48, r: 0.45, cor: [150, 158, 165], a: 0.7 },
      ],
      vinheta: 0.55,
    },
    linha: '#8fdc2a',
    // Na placa, realismo acima de efeito (decisão do autor em 2026-11-10): sem contorno verde nem
    // halo nas peças; materiais de src/materials.json e estúdio fotográfico (src/lookdev.js).
    cena: {
      realista: {
        exposicao: 1.0,
        balanco_K: 5800,
        ambiente: 0.36,                // intensidade do mapa de ambiente
        // Ambiente no referencial canônico (câmera em -y olhando +y, acima da placa), unidades do
        // estúdio virtual: HDR escurecido da Poly Haven mais caixas de luz que desenham os reflexos.
        hdr: { K: 5600, i: 0.5 },
        caixas: [
          // teto-fundo em quatro faixas de borda nítida (vãos a 8%): nas tampas do X, que são espelho
          // preto, o reflexo ganha bordas, como em storagereview/sr-2 e sr-5; nas superfícies foscas
          // a média fica perto da caixa lisa de antes (4,0 em 20 x 6)
          { nome: 'teto-fundo', K: 5600, i: 4.8, pos: [0, 10, 11], tam: [20, 12], degrade: [0.02, 1], listras: [4, 0.5], vao: 0.08 },
          // zênite: caixa larga e fraca quase sobre a placa; nas vistas de frente as tampas do X ganham
          // o reflexo largo e escuro das fotos em vez de um preto morto
          { nome: 'zenite-tampas', K: 5600, i: 0.7, pos: [0, 3, 16], tam: [14, 8], degrade: [0.35, 1] },
          { nome: 'faixa-esquerda', K: 5600, i: 3.2, pos: [-13, -3, 5], tam: [2.4, 16] },
          { nome: 'faixa-direita', K: 6200, i: 2.2, pos: [13, 5, 4], tam: [2.4, 14] },
          { nome: 'frente-baixa', K: 5200, i: 0.5, pos: [0, -14, 1], tam: [16, 3] },
          { nome: 'rebatedor', K: 5600, i: 8, pos: [0, -9, -8.5], tam: [30, 7], degrade: [1, 0.4] },
          { nome: 'recorte-fundo', K: 6500, i: 14, pos: [0, 15, 2], tam: [28, 1.4] },
        ],
        // Luzes diretas (mm a partir do centro da placa, no mesmo referencial canônico)
        luzes: [
          { papel: 'principal', K: 5400, i: 3.4, pos: [-420, -380, 640], sombra: true },
          { papel: 'preenchimento', K: 7200, i: 0.28, pos: [560, -320, 140] },
          { papel: 'recorte', K: 6500, i: 1.6, pos: [120, 700, 120] },
          // segundo recorte, do outro lado e por trás: desenha o contorno da carcaça preta em qualquer azimute
          // (o estúdio gira com a câmera) e na virada da face A para a B, quando a placa passa de quina
          { papel: 'recorte-2', K: 6800, i: 0.8, pos: [-520, 640, 160] },
        ],
        luzFria: 7500, luzQuente: 3000,   // ?luz=fria|quente: conferência do material nas duas luzes
        virada: 60,                    // mm em z em torno do meio da espessura em que o estúdio vira de lado
        chao: { folga: 1.5, sombra: 0.5, contato: { opacidade: 0.9, folga: 5, desfoque: 16, nucleo: 2.5 } },
        contorno: 0.18,                // recorte de luz permanente nas bordas (Fresnel), em qualquer ângulo
        apaga: 0.92,                   // destaque: quanto as outras peças escurecem e perdem a cor
        realce: { cor: 0xeef8e6, forca: 0.2 },   // recorte de luz na peça destacada (branco com um toque do acento)
        ao: { raio: 10, espessura: 4, intensidade: 0.9 },
        dof: { abertura: 7, maxCoc: 3, maxCocAlta: 5 },   // px do palco de 1920 x 1080
        // acumulação com a cena parada (lookdev.js): largura do filtro em tenda (px do alvo) e raio
        // angular da luz principal tratada como luz de área (sombra suave)
        acumula: { filtro_px: 1.0, luz_graus: 5 },
      },
      cotas: false,
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

/**
 * Tema pedido na URL, ou null. Nome desconhecido é ignorado com aviso.
 * ?leve=1 desliga os efeitos caros do tema: desfoque de fundo da caixa, brilho do nó-alvo,
 * halo das arestas 3D e halo dos fluxos (para notebook fraco ou projetor com placa integrada).
 */
export function temaDaUrl(params, padrao = null) {
  // padrao: tema do arquivo único (keynote); ?tema=nenhum volta ao visual sem tema
  const nome = params.get('tema') ?? padrao;
  if (!nome || nome === 'nenhum') return null;
  if (!TEMAS[nome]) { console.warn(`[tema] tema desconhecido: ${nome}; usando o padrão`); return null; }
  const t = { nome, ...TEMAS[nome], leve: params.get('leve') === '1' };
  if (t.leve) {
    t.cena = { ...t.cena, arestas: t.cena.arestas && { ...t.cena.arestas, halo: 0 } };     // (Keynote já não tem arestas)
    const fx = t.diagramas.fluxo;
    t.diagramas = { ...t.diagramas, fluxo: fx && { ...fx, camadas: fx.camadas.filter((c) => c.cls !== 'f-halo') } };
  }
  return t;
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
