// Copia os dados reais (ou os exemplos, quando faltam) para public/data/.
// O viewer não tem conteúdo embutido: tudo o que aparece vem destes arquivos.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const viewer = path.resolve(aqui, '..');
const harness = path.resolve(viewer, '..');
const out = path.join(viewer, 'public', 'data');
const ex = path.join(harness, 'schemas', 'examples');

fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(path.join(out, 'diagrams'), { recursive: true });

const manifest = { generated_by: 'scripts/sync-data.mjs', source: {}, diagrams: [], glb: false };

function copiaOuExemplo(chave, real, exemplo, destino) {
  if (fs.existsSync(real)) {
    fs.copyFileSync(real, path.join(out, destino));
    manifest.source[chave] = 'real';
  } else {
    fs.copyFileSync(exemplo, path.join(out, destino));
    manifest.source[chave] = 'examples';
  }
}

copiaOuExemplo('storyboard', path.join(harness, 'story', 'storyboard.json'),
  path.join(ex, 'storyboard.example.json'), 'storyboard.json');
copiaOuExemplo('beats', path.join(harness, 'content', 'pt-BR', 'beats.json'),
  path.join(ex, 'beats.example.json'), 'beats.json');

// Diagramas: todos os diagrams/*.json reais; se não houver nenhum, os dois exemplos juntos.
const dDir = path.join(harness, 'diagrams');
const reais = fs.existsSync(dDir) ? fs.readdirSync(dDir).filter((f) => f.endsWith('.json') && !f.startsWith('_') && !f.startsWith('.')).sort().filter((f) => {
  try { const d = JSON.parse(fs.readFileSync(path.join(dDir, f), 'utf8')); return d && d.id && Array.isArray(d.nodes); } catch { return false; }
}) : [];
// Conjunto coerente: se o storyboard é o de exemplo, os diagramas reais não casam com ele
// (ids diferentes); então vão os de exemplo. Para forçar os reais: SYNC_REAL_DIAGRAMS=1.
const usaReais = reais.length && (manifest.source.storyboard === 'real' || process.env.SYNC_REAL_DIAGRAMS === '1');
if (reais.length && !usaReais) console.log('sync-data: storyboard é de exemplo; usando os diagramas de exemplo (SYNC_REAL_DIAGRAMS=1 força os reais)');
if (usaReais) {
  for (const f of reais) {
    fs.copyFileSync(path.join(dDir, f), path.join(out, 'diagrams', f));
    manifest.diagrams.push({ file: f, source: 'real' });
  }
} else {
  for (const f of ['diagram.example.json', 'diagram.child.example.json']) {
    fs.copyFileSync(path.join(ex, f), path.join(out, 'diagrams', f));
    manifest.diagrams.push({ file: f, source: 'examples' });
  }
}
manifest.source.diagrams = usaReais ? 'real' : 'examples';

// GLB
const glb = path.join(harness, 'build', 'card.glb');
if (fs.existsSync(glb)) {
  fs.copyFileSync(glb, path.join(out, 'card.glb'));
  manifest.glb = true;
}
manifest.source.glb = manifest.glb ? 'real' : 'absent';

// Medidas: CSV -> JSON { feature: {...} }
function linhasCsv(texto) {
  const linhas = [];
  let campo = '', linha = [], aspas = false;
  for (let i = 0; i < texto.length; i++) {
    const c = texto[i];
    if (aspas) {
      if (c === '"' && texto[i + 1] === '"') { campo += '"'; i++; }
      else if (c === '"') aspas = false;
      else campo += c;
    } else if (c === '"') aspas = true;
    else if (c === ',') { linha.push(campo); campo = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && texto[i + 1] === '\n') i++;
      linha.push(campo); campo = '';
      if (linha.some((x) => x !== '')) linhas.push(linha);
      linha = [];
    } else campo += c;
  }
  if (campo || linha.length) { linha.push(campo); linhas.push(linha); }
  return linhas;
}
const csv = path.join(harness, 'design', 'measurements.csv');
const medidas = {};
if (fs.existsSync(csv)) {
  const [cab, ...resto] = linhasCsv(fs.readFileSync(csv, 'utf8'));
  for (const l of resto) {
    const o = Object.fromEntries(cab.map((k, i) => [k, l[i] ?? '']));
    const num = (s) => (s === '' || Number.isNaN(Number(s)) ? null : Number(s));
    medidas[o.feature] = { ...o, value_mm: num(o.value_mm), tolerance_mm: num(o.tolerance_mm) };
  }
  manifest.source.measurements = 'real';
} else manifest.source.measurements = 'absent';
fs.writeFileSync(path.join(out, 'measurements.json'), JSON.stringify(medidas, null, 1));

// Decodificador Draco local (sem CDN)
const dracoSrc = path.join(viewer, 'node_modules', 'three', 'examples', 'jsm', 'libs', 'draco', 'gltf');
const dracoOut = path.join(viewer, 'public', 'draco');
fs.mkdirSync(dracoOut, { recursive: true });
for (const f of ['draco_decoder.js', 'draco_decoder.wasm', 'draco_wasm_wrapper.js']) {
  if (fs.existsSync(path.join(dracoSrc, f))) fs.copyFileSync(path.join(dracoSrc, f), path.join(dracoOut, f));
}

fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 1));
console.log('sync-data:', JSON.stringify(manifest.source), `diagramas=${manifest.diagrams.length}`, `glb=${manifest.glb}`);
