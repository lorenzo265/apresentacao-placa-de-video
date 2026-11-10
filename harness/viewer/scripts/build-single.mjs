// Gera um único arquivo .html com tudo embutido (código, estilos, fontes e dados).
// Abre com dois cliques, sem servidor e sem internet. Uso: npm run build:single
// Saída: harness/dist/tour.html
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const viewer = path.resolve(aqui, '..');
const dist = path.join(viewer, 'dist');
const saida = path.resolve(viewer, '..', 'dist', 'tour.html');

const le = (p) => fs.readFileSync(path.join(dist, p), 'utf8');
const leJson = (p) => JSON.parse(le(p));
let html = le('index.html');

// Dados: as mesmas chaves que o viewer pediria por fetch.
const manifest = leJson('data/manifest.json');
if (manifest.glb) throw new Error('build-single ainda não embute o GLB: falta decidir o formato (base64 + Draco)');
const dados = { 'data/manifest.json': manifest };
for (const f of ['storyboard.json', 'beats.json', 'measurements.json']) dados[`data/${f}`] = leJson(`data/${f}`);
for (const d of manifest.diagrams) dados[`data/diagrams/${d.file}`] = leJson(`data/diagrams/${d.file}`);
// "<" escapado: o JSON não pode fechar a tag <script> por acidente.
const dadosTxt = JSON.stringify(dados).replace(/</g, '\\u003c');

// Estilos: troca cada url(./fonte) por data URI. Só woff2 (todo navegador atual lê).
const mCss = html.match(/<link rel="stylesheet"[^>]*href="\.\/(assets\/[^"]+\.css)"[^>]*>/);
if (!mCss) throw new Error('não achei a folha de estilos no index.html do build');
let css = le(mCss[1]);
css = css.replace(/,?url\(\.\/[^)]+\.woff\)format\("woff"\)/g, '');
css = css.replace(/url\(\.\/([^)]+\.woff2)\)/g, (_, f) => {
  const b64 = fs.readFileSync(path.join(dist, 'assets', f)).toString('base64');
  return `url(data:font/woff2;base64,${b64})`;
});
const resto = css.match(/url\(\.\/[^)]+\)/g);
if (resto) throw new Error(`estilo ainda aponta para arquivo externo: ${resto.join(', ')}`);

// Código: um módulo só, embutido.
const mJs = html.match(/<script type="module"[^>]*src="\.\/(assets\/[^"]+\.js)"[^>]*><\/script>/);
if (!mJs) throw new Error('não achei o script no index.html do build');
const js = le(mJs[1]);
if (/<\/script/i.test(js)) throw new Error('o código contém "</script" e quebraria a página embutida');
if (/\bimport\(/.test(js)) console.warn('build-single: o código tem import() dinâmico; confira se ele não é usado sem GLB');

// Substituições com função: o conteúdo tem "$" e não pode ser lido como padrão.
html = html.replace(mCss[0], () => `<style>${css}</style>`);
html = html.replace(mJs[0], () => '');
html = html.replace('</body>', () =>
  `<script>window.__TOUR_DATA__=${dadosTxt};</script>\n<script type="module">${js}</script>\n</body>`);
html = html.replace(/<link rel="modulepreload"[^>]*>\s*/g, '');

const externo = html.match(/(?:src|href)="\.\/[^"]+"/g);
if (externo) throw new Error(`a página ainda aponta para arquivo externo: ${externo.join(', ')}`);

fs.mkdirSync(path.dirname(saida), { recursive: true });
fs.writeFileSync(saida, html);
console.log(`build-single: ${path.relative(process.cwd(), saida)} (${(html.length / 1048576).toFixed(2)} MB, ${manifest.diagrams.length} diagramas)`);
