// Espaço único dos diagramas: posiciona os diagramas de topo (storyboard.world),
// embute os filhos (node.embed) e entrega todos os nós em coordenadas do mundo.
// Não calcula layout nem inventa rótulo: só aplica as transformações do contrato.

/** Ajusta um diagrama de tamanho [cw, ch] dentro de rect [x,y,w,h], proporção preservada e centrado. */
function encaixa(size, rect) {
  const s = Math.min(rect[2] / size[0], rect[3] / size[1]);
  return { s, ox: rect[0] + (rect[2] - size[0] * s) / 2, oy: rect[1] + (rect[3] - size[1] * s) / 2 };
}

export function buildWorld(storyboard, diagramList) {
  const diagrams = new Map(diagramList.map((d) => [d.id, d]));
  const recs = [];                 // todos os nós, na ordem de desenho
  const byId = new Map();          // id do nó -> registro
  const flows = new Map();         // id do fluxo -> {flow, diagram, T}
  const transform = new Map();     // id do diagrama -> {ox, oy, s}
  const placed = new Set();
  const avisos = [];

  function coloca(id, T, host) {
    if (placed.has(id)) { avisos.push(`diagrama ${id} colocado mais de uma vez; ignorado`); return; }
    const d = diagrams.get(id);
    if (!d) { avisos.push(`diagrama ${id} não existe`); return; }
    placed.add(id);
    transform.set(id, T);
    for (const f of d.flows ?? []) flows.set(f.id, { flow: f, diagram: id, T });
    for (const n of d.nodes) {
      const [x, y, w, h] = n.rect;
      const rect = [T.ox + x * T.s, T.oy + y * T.s, w * T.s, h * T.s];
      const rec = {
        id: n.id, node: n, diagram: id, rect, s: T.s, host, idx: recs.length,
        children: [], isContainer: false,
        cx: rect[0] + rect[2] / 2, cy: rect[1] + rect[3] / 2,
      };
      if (byId.has(n.id)) avisos.push(`id de nó repetido: ${n.id}`);
      byId.set(n.id, rec);
      recs.push(rec);
      if (n.embed) {
        rec.isContainer = true;
        const c = diagrams.get(n.embed);
        if (c) coloca(n.embed, (({ s, ox, oy }) => ({ s: s, ox, oy }))(encaixa(c.size, rect)), rec);
        else avisos.push(`embed ${n.embed} não existe (nó ${n.id})`);
      }
    }
  }

  // diagramas de topo
  for (const w of storyboard.world ?? []) {
    const d = diagrams.get(w.diagram);
    if (d) coloca(d.id, encaixa(d.size, w.rect), null);
    else avisos.push(`world: diagrama ${w.diagram} não existe`);
  }
  // Os que não estão em world nem embutidos: lado a lado, à direita do que já existe.
  const embutidos = new Set([...diagrams.values()].flatMap((d) => d.nodes.filter((n) => n.embed).map((n) => n.embed)));
  let xNext = Math.max(0, ...(storyboard.world ?? []).map((w) => w.rect[0] + w.rect[2])) + 200;
  for (const d of diagrams.values()) {
    if (placed.has(d.id) || embutidos.has(d.id)) continue;
    avisos.push(`diagrama ${d.id} fora do world; colocado à direita`);
    coloca(d.id, { s: 1, ox: xNext, oy: 0 }, null);
    xNext += d.size[0] + 200;
  }

  // hierarquia lógica (parent) e contêineres
  for (const r of recs) {
    const p = r.node.parent ? byId.get(r.node.parent) : null;
    if (p) { p.children.push(r); p.isContainer = true; }
  }
  return { recs, byId, flows, transform, diagrams, avisos };
}

/** Resolve seletores (id ou tag:<nome>) dentro de um diagrama; id também vale em qualquer diagrama. */
export function resolve(world, selectors, diagramId) {
  const out = new Set();
  for (const sel of selectors ?? []) {
    if (sel.startsWith('tag:')) {
      const tag = sel.slice(4);
      for (const r of world.recs) if (r.diagram === diagramId && (r.node.tags ?? []).includes(tag)) out.add(r);
    } else {
      const r = world.byId.get(sel);
      if (r) out.add(r);
    }
  }
  return [...out];
}

/** Retângulo que envolve os registros, em coordenadas do mundo. */
export function uniao(recs) {
  if (!recs.length) return null;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const r of recs) {
    x0 = Math.min(x0, r.rect[0]); y0 = Math.min(y0, r.rect[1]);
    x1 = Math.max(x1, r.rect[0] + r.rect[2]); y1 = Math.max(y1, r.rect[1] + r.rect[3]);
  }
  return [x0, y0, x1 - x0, y1 - y0];
}

/**
 * Fatores de opacidade por nó para um destaque. Selecionados e descendentes (parent e embed) = 1;
 * o resto do MESMO diagrama = 0,25; conteúdo embutido herda o fator do nó hospedeiro.
 */
export function fatoresDestaque(world, beat) {
  const sels = beat.highlight;
  if (!sels?.length || !beat.view) return null;
  const vd = beat.view.diagram;
  const sel = new Set(resolve(world, sels, vd));
  const cheio = new Set();
  const marca = (r) => {
    if (cheio.has(r)) return;
    cheio.add(r);
    r.children.forEach(marca);
    if (r.node.embed) for (const x of world.recs) if (x.host === r) marca(x);
  };
  sel.forEach(marca);
  const f = new Float32Array(world.recs.length).fill(1);
  for (const r of world.recs) {
    if (r.diagram === vd) f[r.idx] = cheio.has(r) ? 1 : 0.25;
    else if (r.host) f[r.idx] = cheio.has(r) ? 1 : f[r.host.idx];
  }
  return f;
}
