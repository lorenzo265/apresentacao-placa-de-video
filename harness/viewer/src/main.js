import '@fontsource/inter/latin-400.css';
import '@fontsource/inter/latin-500.css';
import '@fontsource/inter/latin-600.css';
import '@fontsource/inter/latin-700.css';
import '@fontsource/jetbrains-mono/latin-400.css';
import '@fontsource/jetbrains-mono/latin-500.css';
import './kinds.css';
import './style.css';
import { buildWorld } from './world.js';
import { criaCena } from './scene3d.js';
import { criaTour } from './tour.js';
import { STAGE_W, STAGE_H } from './layout.js';

const params = new URLSearchParams(location.search);
const capture = params.get('capture') === '1';
// No arquivo único (npm run build:single) os dados vêm embutidos na página.
const embutido = window.__TOUR_DATA__ ?? null;
const getJson = async (u) => {
  if (embutido && u in embutido) return embutido[u];
  const r = await fetch(u);
  if (!r.ok) throw new Error(`${u}: ${r.status}`);
  return r.json();
};

async function inicia() {
  const palco = document.getElementById('palco');
  if (capture) document.body.classList.add('capture');

  // Palco lógico de 1920x1080; no modo ao vivo é escalado para caber na janela.
  let escala = 1;
  const ajusta = () => {
    escala = capture ? 1 : Math.min(innerWidth / STAGE_W, innerHeight / STAGE_H);
    palco.style.transform = capture ? 'none' : `translate(-50%, -50%) scale(${escala})`;
  };
  ajusta();
  addEventListener('resize', ajusta);

  const manifest = await getJson('data/manifest.json');
  const [storyboard, textos, medidas] = await Promise.all([
    getJson('data/storyboard.json'), getJson('data/beats.json'), getJson('data/measurements.json'),
  ]);
  const diagramas = await Promise.all(manifest.diagrams.map((d) => getJson(`data/diagrams/${d.file}`)));
  const world = buildWorld(storyboard, diagramas);
  world.avisos.forEach((a) => console.warn(`[diagramas] ${a}`));

  const cena = await criaCena(document.getElementById('cena3d'), {
    medidas, temGlb: manifest.glb, pixelRatio: capture ? 1 : Math.min(2, devicePixelRatio * escala),
  });
  cena.avisos.forEach((a) => console.warn(`[3D] ${a}`));

  const corte = params.get('cut') ?? (storyboard.cuts.completo ? 'completo' : Object.keys(storyboard.cuts)[0]);
  const tour = criaTour({ dados: { storyboard, textos, world }, palco, cena, capture, corte });
  window.__tour = tour;
  await tour.ready;
  const beat = params.get('beat');
  if (beat) tour.goto(beat);
}

inicia().catch((e) => {
  console.error(e);
  window.__tourErro = String(e.stack ?? e);
  document.body.insertAdjacentHTML('beforeend', `<pre id="erro">${String(e.message ?? e)}</pre>`);
});
