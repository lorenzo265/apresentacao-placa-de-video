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
import { criaChamada } from './callout.js';

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
  // Para os testes: diz se o GLB entrou e se uma peça existe pelo id do assembly.
  window.__cena = { glb: !cena.blockout, temAncora: cena.temAncora, avisos: cena.avisos };

  // Modo ferramenta (?frame3d=1): um quadro da cena 3D sem o tour, para frame3d.cjs.
  if (params.get('frame3d') === '1') {
    const chamada = criaChamada(palco);
    window.__frame3d = ({ pos, target, fov = 30, explode = 'assembled', part = null, anchor = null, box = 'right-center' }) => {
      const nivel = explode === 'assembled' ? 0 : Number(explode.slice(1));
      const f = part ? cena.fatoresDe([part], []) : null;
      cena.aplicaEstado(nivel, f, f, 1);
      cena.ajustaCamera({ px: pos[0], py: pos[1], pz: pos[2], tx: target[0], ty: target[1], tz: target[2], fov });
      cena.desenha();
      const res = { glb: !cena.blockout, peca: part ? cena.temPeca(part) : null, ancora: null, caixa: null, dentro: null, cobre: null };
      if (anchor) {
        if (!cena.temAncora(anchor)) { res.erroAncora = `âncora ${anchor} não existe`; return res; }
        const a = cena.ancoraTela(anchor);
        const b = { callout: { anchor, box, line_in: 0, line_out: 0 }, provenance: [] };
        chamada.define(b, { headline: 'Título de exemplo', caption: 'Legenda de exemplo para ver onde a caixa fica.', source_line: '' });
        chamada.atualiza(b, a, 1, 1, '#f1f4f8');
        const r = chamada.ret();
        res.ancora = a; res.caixa = r;
        res.dentro = a[0] >= 0 && a[0] <= STAGE_W && a[1] >= 0 && a[1] <= STAGE_H;
        res.cobre = a[0] >= r[0] && a[0] <= r[0] + r[2] && a[1] >= r[1] && a[1] <= r[1] + r[3];
      }
      return res;
    };
    window.__tourReady = true;
    return;
  }

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
