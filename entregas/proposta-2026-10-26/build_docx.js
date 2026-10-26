// Gera a versão direta da proposta em .docx: Arial 12, fundo branco, só tópicos, negrito e linhas.
// Uso: NODE_PATH=/opt/node22/lib/node_modules node build_docx.js
// Os nomes e o nome do grupo vêm de grupo.json. O logo vem de logo.svg (convertido em logo.png).
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Footer, AlignmentType, LevelFormat,
  BorderStyle, HeadingLevel, PageNumber,
} = require('docx');

const AQUI = __dirname;
const g = JSON.parse(fs.readFileSync(path.join(AQUI, 'grupo.json'), 'utf8'));
const nomes = g.integrantes.map((n) => n.trim());
if (nomes.some((n) => !n)) console.warn('ATENÇÃO: há nome vazio em grupo.json');
const [I1, I2, I3, I4, I5] = nomes;

async function logoPng() {
  const svg = fs.readFileSync(path.join(AQUI, 'logo.svg'), 'utf8').replace(/<\?xml.*?\?>/, '');
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 4 });
  await page.setContent(`<body style="margin:0;background:#fff"><div id="l" style="width:340px">${svg}</div></body>`);
  const buf = await page.locator('#l').screenshot();
  await browser.close();
  fs.writeFileSync(path.join(AQUI, 'logo.png'), buf);
  return buf;
}

const FONT = 'Arial';
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: 24, ...o });
const b = (text) => run(text, { bold: true });

// Tópico com rótulo em negrito e texto normal.
const topico = (rotulo, texto, nivel = 0) =>
  new Paragraph({
    numbering: { reference: 'topicos', level: nivel },
    spacing: { after: 80 },
    children: rotulo ? [b(rotulo + ' '), run(texto)] : [run(texto)],
  });

const titulo = (texto) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    keepNext: true,
    children: [new TextRun({ text: texto, font: FONT, size: 26, bold: true })],
  });

async function main() {
  const png = await logoPng();

  const corpo = [
    new Paragraph({
      spacing: { after: 120 },
      children: [new ImageRun({ type: 'png', data: png, transformation: { width: 220, height: 54 },
        altText: { title: 'Logo Warp 32', description: 'Grade de 32 quadrados (8 x 4), 4 deles em laranja', name: 'logo' } })],
    }),
    new Paragraph({
      spacing: { after: 40 },
      children: [new TextRun({ text: 'Proposta de trabalho', font: FONT, size: 32, bold: true })],
    }),
    new Paragraph({
      spacing: { after: 160 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: '000000', space: 6 } },
      children: [run(`${g.disciplina} · Linha ${g.linha} · Entrega: ${g.entrega}`)],
    }),

    titulo('Dados do grupo'),
    topico('Nome do grupo:', g.nome_grupo),
    new Paragraph({ numbering: { reference: 'topicos', level: 0 }, spacing: { after: 40 }, children: [b('Integrantes:')] }),
    ...nomes.map((n) => new Paragraph({
      numbering: { reference: 'nomes', level: 0 }, spacing: { after: 40 }, children: [run(n)],
    })),
    topico('Identidade visual:',
      'o logo é um warp, o grupo de 32 threads que a GPU executa em conjunto: 32 quadrados em grade 8 × 4, ' +
      'com 4 em laranja, as threads que seguem outro caminho do programa (divergência). Logo original, sem marca da NVIDIA.'),

    titulo('Proposta'),
    topico('O que será feito:',
      'estudo da arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell (chip GB202). O tema "GPU Nvidia" consta na lista de sugestões do professor.'),
    topico('Natureza:', 'estudo de um processador, na linha de Arquitetura: pesquisa em documentação oficial, sem projeto de hardware.'),
    topico('O que será levantado:',
      'registradores, conjunto de instruções (PTX e SASS), se é CISC ou RISC, MMU, interrupções, gerenciamento de memória, ' +
      'pipeline e cache. Quando um item não existir na GPU ou não for público, o trabalho diz isso e explica o motivo.'),
    topico('Entregas:',
      'documentação escrita (09/11) e seminário (16/11), com um tour 3D interativo da placa e do chip como apoio.'),
    topico('O que será usado ou adquirido:',
      'nada será adquirido, porque não há projeto de hardware. Serão usados documentação pública da NVIDIA, o código aberto ' +
      'do driver, artigos acadêmicos e ferramentas gratuitas do CUDA para compilar e desmontar exemplos curtos.'),

    titulo('Definição das tarefas'),
    new Paragraph({
      spacing: { after: 100 },
      children: [run('Todo o grupo é responsável pelo trabalho inteiro e revisa o texto dos colegas. Cada integrante responde por uma parte:')],
    }),
    topico(I1 + ':', 'registradores, conjunto de instruções e RISC ou CISC.'),
    topico(I2 + ':', 'hierarquia de memória, caches e gerenciamento de memória.'),
    topico(I3 + ':', 'MMU, interrupções e escalonamento.'),
    topico(I4 + ':', 'pipeline, execução SIMT, latência e ocupação.'),
    topico(I5 + ':', 'tour 3D, integração e condução do seminário.'),

    titulo('Cronograma'),
    topico('19/10 a 26/10:', 'formação do grupo, escolha do tema, leitura inicial e proposta (todos). Entrega da proposta em 26/10.'),
    topico('27/10 a 01/11:', 'aprofundar a leitura das fontes (cada um na sua parte).'),
    topico('02/11 a 08/11:', `redação do texto e primeira versão do tour (cada um na sua parte; ${I5} no tour).`),
    topico('09/11:', 'revisão cruzada e entrega da documentação escrita (todos).'),
    topico('10/11 a 14/11:', `tour final, slides de reserva e divisão das falas (${I5}, com todos).`),
    topico('15/11:', 'ensaio geral com cronômetro (todos).'),
    topico('16/11:', 'seminário (todos).'),

    titulo('Objetivo'),
    topico('', 'Aprofundar o conhecimento em arquitetura de computadores com um processador atual e muito diferente de uma CPU.'),
    topico('', 'Apresentar à turma um estudo de caso em que cada afirmação indica a fonte e o grau de certeza.'),
    topico('', 'Entregar as três etapas com qualidade, buscando os 4,0 pontos em jogo.'),
  ];

  const doc = new Document({
    creator: g.nome_grupo,
    title: `Proposta de trabalho - ${g.nome_grupo}`,
    styles: {
      default: { document: { run: { font: FONT, size: 24 } } },
      paragraphStyles: [{
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: '000000' },
        paragraph: {
          spacing: { before: 280, after: 100 }, outlineLevel: 0,
          border: { top: { style: BorderStyle.SINGLE, size: 6, color: '000000', space: 6 } },
        },
      }],
    },
    numbering: {
      config: [
        { reference: 'topicos', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 540, hanging: 270 } }, run: { font: FONT } } }] },
        { reference: 'nomes', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } }, run: { font: FONT } } }] },
      ],
    },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1247, right: 1247 } } },
      footers: { default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: `${g.nome_grupo} · Página `, font: FONT, size: 18 }),
          new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 }),
          new TextRun({ text: ' de ', font: FONT, size: 18 }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 18 })],
      })] }) },
      children: corpo,
    }],
  });

  const saida = path.join(AQUI, `Proposta - ${g.nome_grupo}.docx`);
  fs.writeFileSync(saida, await Packer.toBuffer(doc));
  console.log('DOCX:', saida);
}

main().catch((e) => { console.error(e); process.exit(1); });
