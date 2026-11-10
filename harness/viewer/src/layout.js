// Constantes de layout em pixels lógicos do palco (1920 x 1080).
// O palco tem sempre este tamanho; no modo ao vivo ele é escalado para caber na janela.
export const STAGE_W = 1920;
export const STAGE_H = 1080;
export const HEADER_H = 88;     // cabeçalho com trilha de nível e progresso
export const DISC_H = 52;       // faixa fixa do aviso "diagrama ilustrativo"
export const MARGIN = 48;       // margem da caixa de texto
export const BOX_W = 620;       // largura da caixa de texto
export const GAP = 36;          // folga entre a caixa e o diagrama

// Tempos fixos da chamada (segundos)
export const BOX_IN = 0.4;
export const LINE_OUT_DEFAULT = 0.5;

// Nível de detalhe dos rótulos: altura do texto na tela, em px
export const LOD_MIN = 9;       // abaixo disto o rótulo some
export const LOD_FULL = 13;     // a partir daqui o rótulo está totalmente visível
export const LOD_BIG_START = 260; // rótulos gigantes (zoom muito acima) esmaecem
export const LOD_BIG_END = 420;

/** Lado da tela em que a caixa fica, a partir de callout.box (ou terço inferior esquerdo). */
export function boxPlacement(callout) {
  const [side, vert] = (callout?.box ?? 'left-bottom').split('-');
  return { side, vert };
}

/** Retângulo da tela livre para o diagrama: tudo menos a coluna da caixa, o cabeçalho e a faixa. */
export function safeRect(callout) {
  const { side } = boxPlacement(callout);
  const col = MARGIN + BOX_W + GAP;
  const y0 = HEADER_H + 24;
  const y1 = STAGE_H - DISC_H - 24;
  if (side === 'left') return [col, y0, STAGE_W - col - MARGIN, y1 - y0];
  return [MARGIN, y0, STAGE_W - col - MARGIN, y1 - y0];
}
