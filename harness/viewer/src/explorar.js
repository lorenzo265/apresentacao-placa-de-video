// Modo Explorar: a placa inteira sob o controle de quem assiste. Clique numa peça ou numa camada para
// ler a explicação; remover e recolocar tocam a desmontagem que o tour já usa (desmontagem.json).
// Ordem real com atalho: o estado é sempre "camadas 1 a k fora", que é o nível de explosão do tour.
// Remover a camada k tira antes as que estão na frente; recolocar a k recoloca antes as que saíram depois.
// Textos: só os de beats.json (auditados) ou o texto próprio de pecas.json; procedência sempre à vista.
import * as THREE from 'three';
import gsap from 'gsap';
import { STAGE_W, STAGE_H } from './layout.js';

const SELOS = {
  confirmed: { palavra: 'Confirmado', icone: 'M3,8 L7,12 L13,4' },
  derived: { palavra: 'Derivado', icone: 'M3,4 L13,4 M3,8 L13,8 M3,12 L9,12' },
  inferred: { palavra: 'Provável', icone: 'M5,6 Q5,3 8,3 Q11,3 11,6 Q11,8 8,9 L8,10 M8,12.5 L8,13' },
  illustrative: { palavra: 'Ilustrativo', icone: 'M8,2 L14,8 L8,14 L2,8 Z' },
};
const selo = (p, rotulo = '') => (SELOS[p]
  ? `<span class="selo s-${p}"><svg viewBox="0 0 16 16" width="22" height="22"><path d="${SELOS[p].icone}"/></svg>${rotulo}${SELOS[p].palavra}</span>` : '');
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;');

// Vista de partida: a do plano de herói do storyboard (a2.13), em mm. O enquadramento sai da caixa da placa.
const VISTA = { pos: [330, -900, 260], target: [150, 60, -70], fov: 34 };
// Área da tela livre para a placa: entre a lista de camadas e o painel da explicação.
const LIVRE = [470, 110, 860, 850];
const T_ULTIMO = 1.7, T_ATALHO = 0.55;      // s por camada: a pedida e as que saem antes dela

export function criaExplorar({ palco, cena, dados, textos, storyboard, tour }) {
  const camadas = dados.camadas;                       // [{estagio, nome, beat | texto}]
  const pecas = dados.pecas;                           // id -> {nome, beat, estagio, existe, forma, ressalva, quantidade}
  const beatSb = new Map(storyboard.beats.map((b) => [b.id, b]));
  const numero = new Map(tour.beats.map((b, i) => [b.id, i + 1]));
  const prontos = new Set([...tour.beats.map((b) => b.id), ...tour.extras]);
  const camadaDe = (k) => camadas.find((c) => c.estagio === k);
  const nomesDaCamada = (k) => Object.keys(pecas).filter((id) => pecas[id].estagio === k);

  const raiz = document.createElement('div');
  raiz.id = 'explorar';
  raiz.hidden = true;
  raiz.innerHTML = `
    <svg id="ex-linha" width="${STAGE_W}" height="${STAGE_H}" viewBox="0 0 ${STAGE_W} ${STAGE_H}"><path class="linha"/><circle class="ponto" r="7"/></svg>
    <header class="ex-topo ui"><h1>Explorar a placa</h1><button data-a="sair">Voltar à apresentação <kbd>Esc</kbd></button></header>
    <nav class="ex-camadas ui">
      <h2>Camadas 1 a 7 na ordem do teardown. A 8 é ilustrativa</h2>
      <ol>${camadas.map((c) => `<li><button data-k="${c.estagio}"><i>${c.estagio}</i><span>${esc(c.nome)}</span><em></em></button></li>`).join('')}</ol>
      <div class="acoes"><button data-a="remontar">Remontar tudo</button><button data-a="desmontar">Desmontar tudo</button></div>
    </nav>
    <aside class="ex-painel ui"></aside>
    <div class="ex-selo"><span class="selo s-inferred"><svg viewBox="0 0 16 16" width="22" height="22"><path d="${SELOS.inferred.icone}"/></svg>Provável: do interior do cooler só a base de contato aparece em foto. Abertura da carcaça ilustrativa</span></div>
    <p class="ex-dica">arraste: gira &middot; roda do mouse: aproxima &middot; clique: seleciona &middot; Delete: remove &middot; Z: recoloca a última &middot; Esc: volta</p>`;
  palco.appendChild(raiz);
  const painel = raiz.querySelector('.ex-painel');
  const linha = raiz.querySelector('#ex-linha .linha'), ponto = raiz.querySelector('#ex-linha .ponto');
  const seloE8 = raiz.querySelector('.ex-selo');
  const botoes = new Map([...raiz.querySelectorAll('.ex-camadas button[data-k]')].map((b) => [Number(b.dataset.k), b]));

  const st = { nivel: 0, hl: 1 };      // nível de explosão (contínuo) e mistura do destaque
  let ativo = false;
  let alvo = 0;                        // nível pedido: camadas 1 a alvo estão fora (ou a caminho)
  let sel = null;                      // { tipo: 'camada', k } | { tipo: 'peca', id }
  let fAnt = null, fCur = null;        // fatores de destaque (anterior e atual)
  let ancora = null;                   // nó de âncora da seleção, para a linha até o painel
  const limites = { min: 0, max: Infinity };

  // ---- conteúdo do painel ----
  /** Explicação de uma camada ou peça: texto de um beat auditado (com a procedência do beat) ou texto próprio. */
  function explicacao(item) {
    if (item.texto) return { ...item.texto, beat: null };
    if (!item.beat || !textos.beats[item.beat]) return null;
    const t = textos.beats[item.beat];
    return { headline: t.headline, caption: t.caption, source_line: t.source_line, provenance: beatSb.get(item.beat)?.provenance ?? [], beat: item.beat };
  }
  const camadaSel = () => (sel?.tipo === 'camada' ? sel.k : sel ? pecas[sel.id]?.estagio ?? null : null);

  function desenhaPainel() {
    if (!sel) {
      painel.innerHTML = `
        <p class="olho">Como usar</p>
        <h2>Escolha uma peça ou uma camada</h2>
        <p class="texto">Clique na placa ou na lista. Remover uma camada tira antes as que estão na frente dela. As camadas 1 a 7 seguem a ordem do teardown da Gamers Nexus. A 8 não é do teardown.</p>`;
      return;
    }
    const k = camadaSel();
    const cam = k ? camadaDe(k) : null;
    const item = sel.tipo === 'camada' ? cam : pecas[sel.id];
    const ex = explicacao(item);
    const fora = k != null && alvo >= k;
    let olho, selos;
    if (sel.tipo === 'camada') {
      olho = k <= 7 ? `Passo ${k} de 7 do teardown` : 'Além do teardown';
      selos = (ex?.provenance ?? []).map((p) => selo(p)).join('');
    } else {
      olho = k ? `Na camada ${k}: ${esc(cam.nome)}` : 'Fica na placa: não é retirada nos 7 passos do teardown';
      selos = selo(item.existe, 'Peça: ') + selo(item.forma, 'Forma: ');
    }
    // ação: sempre sobre a camada (a peça soldada sai com a camada dela)
    let acao = '';
    if (k != null) {
      const faixa = (a, b) => (a === b ? `Antes ${fora ? 'volta' : 'sai'} a camada ${a}.` : `Antes ${fora ? 'voltam' : 'saem'} as camadas ${a} a ${b}.`);
      const nota = fora ? (alvo > k ? faixa(alvo, k + 1) : '') : (alvo < k - 1 ? faixa(alvo + 1, k - 1) : '');
      const oQue = sel.tipo === 'camada' ? '' : ` a camada ${k}`;
      acao = `<button class="primario" data-a="${fora ? 'recolocar' : 'remover'}">${fora ? 'Recolocar' : 'Remover'}${oQue}</button>${nota ? `<p class="nota">${nota}</p>` : ''}`;
    }
    const noSlide = ex?.beat && prontos.has(ex.beat)
      ? `<button data-a="slide" data-id="${ex.beat}">${numero.has(ex.beat) ? `Na apresentação: momento ${numero.get(ex.beat)}` : 'Na apresentação: extra'}</button>` : '';
    painel.innerHTML = `
      <div class="selos">${selos}</div>
      <p class="olho">${olho}</p>
      <h2>${esc(item.nome)}</h2>
      ${ex ? `<h3>${esc(ex.headline)}</h3><p class="texto">${esc(ex.caption)}</p>` : `<p class="texto vazio">Esta peça ainda não tem texto auditado.${item.ressalva ? ' Veja a ressalva abaixo.' : ''}</p>`}
      ${sel.tipo === 'peca' && ex?.provenance?.length ? `<p class="prov">Texto: ${ex.provenance.map((p) => SELOS[p]?.palavra.toLowerCase()).join(', ')}</p>` : ''}
      ${sel.tipo === 'peca' && item.ressalva ? `<p class="ressalva">${esc(item.ressalva)}</p>` : ''}
      ${ex?.source_line ? `<p class="fonte">${esc(ex.source_line)}</p>` : ''}
      <div class="acoes">${acao}<div class="sec"><button data-a="perto">Ver de perto</button>${noSlide}</div></div>`;
  }
  function desenhaLista() {
    const k = camadaSel();
    for (const [n, b] of botoes) {
      b.classList.toggle('fora', alvo >= n);
      b.classList.toggle('sel', n === k);
      b.querySelector('em').textContent = alvo >= n ? (n === 8 ? 'fora, provável' : 'fora') : n === 8 ? 'provável' : '';
    }
  }

  // ---- seleção ----
  function seleciona(novo) {
    sel = novo;
    fAnt = fCur;
    const nomes = !sel ? [] : sel.tipo === 'camada' ? nomesDaCamada(sel.k) : [sel.id];
    fCur = nomes.length ? cena.fatoresDe(nomes, []) : null;
    gsap.killTweensOf(st, 'hl');
    st.hl = 0;
    gsap.to(st, { hl: 1, duration: 0.3, ease: 'power1.out' });
    // âncora da linha: a do beat da explicação, senão a primeira da peça
    ancora = null;
    if (sel) {
      const item = sel.tipo === 'camada' ? camadaDe(sel.k) : pecas[sel.id];
      const cands = [beatSb.get(item.beat)?.callout?.anchor, ...(sel.tipo === 'peca' ? [`anchor.${sel.id}.1`, `anchor.${sel.id}`] : [])];
      ancora = cands.find((a) => a && cena.temAncora(a)) ?? null;
    }
    desenhaPainel(); desenhaLista();
  }

  // ---- câmera ----
  const vAlvo = new THREE.Vector3();
  /** Enquadra a placa (ou só algumas peças) no nível dado, mantendo a direção em que o usuário está olhando. */
  function enquadra(nivel, ids = null, suave = true) {
    const p = cena.camera.position;
    cena.controls.getTarget(vAlvo);
    const r = cena.enquadraNivel({ nivel, pos: p.toArray(), target: vAlvo.toArray(), fov: cena.camera.fov, rect: LIVRE, folga: ids ? 0.16 : 0.05, pecas: ids });
    if (r) cena.controls.setLookAt(...r.pos, ...r.target, suave);
  }

  // ---- desmontagem ----
  function vaiNivel(novo) {
    novo = Math.max(0, Math.min(8, novo));
    gsap.killTweensOf(st, 'nivel');
    const tl = gsap.timeline();
    let de = st.nivel;
    const passos = [];
    if (novo > de) for (let n = Math.floor(de) + 1; n <= novo; n++) passos.push(n);
    else for (let n = Math.ceil(de) - 1; n >= novo; n--) passos.push(n);
    passos.forEach((n, i) => {
      const ultimo = i === passos.length - 1;
      tl.to(st, { nivel: n, duration: (ultimo ? T_ULTIMO : T_ATALHO) * Math.max(0.3, Math.abs(n - de)), ease: ultimo ? 'power1.inOut' : 'none' });
      de = n;
    });
    alvo = novo;
    enquadra(novo);
    desenhaPainel(); desenhaLista();
  }
  const remove = (k) => { if (k != null && alvo < k) vaiNivel(k); };
  const recoloca = (k) => { if (k != null && alvo >= k) vaiNivel(k - 1); };

  // ---- clique na placa ----
  const raio = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  function pecaEm(ev) {
    const r = cena.renderer.domElement.getBoundingClientRect();
    ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    raio.setFromCamera(ndc, cena.camera);
    for (const h of raio.intersectObjects(cena.scene.children, true)) {
      for (let a = h.object; a; a = a.parent) {
        const id = pecas[a.name] ? a.name : pecas[a.userData?.instance_of] ? a.userData.instance_of : null;
        if (id) return id;
      }
    }
    return null;
  }
  let toque = null;
  const tela = cena.renderer.domElement;
  tela.addEventListener('pointerdown', (ev) => { if (ativo && ev.button === 0) toque = [ev.clientX, ev.clientY]; });
  tela.addEventListener('pointerup', (ev) => {
    if (!ativo || !toque) return;
    const andou = Math.hypot(ev.clientX - toque[0], ev.clientY - toque[1]);
    toque = null;
    if (andou > 5) return;
    const id = pecaEm(ev);
    seleciona(id ? { tipo: 'peca', id } : null);
  });

  // ---- botões ----
  raiz.addEventListener('click', (ev) => {
    const b = ev.target.closest('button');
    if (!b) return;
    b.blur();
    if (b.dataset.k) { seleciona({ tipo: 'camada', k: Number(b.dataset.k) }); return; }
    const a = b.dataset.a;
    if (a === 'sair') sai();
    else if (a === 'remontar') vaiNivel(0);
    else if (a === 'desmontar') vaiNivel(8);
    else if (a === 'remover') remove(camadaSel());
    else if (a === 'recolocar') recoloca(camadaSel());
    else if (a === 'perto' && sel) enquadra(st.nivel, sel.tipo === 'camada' ? nomesDaCamada(sel.k) : [sel.id]);
    else if (a === 'slide') { const id = b.dataset.id; sai(); tour.irPara(id); }
  });
  window.addEventListener('keydown', (ev) => {
    if (!ativo || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    const k = ev.key;
    if (k === 'Escape' || k === 'e' || k === 'E') sai();
    else if (k === 'Delete' || k === 'Backspace') remove(camadaSel());
    else if (k === 'z' || k === 'Z') { if (alvo > 0) { seleciona({ tipo: 'camada', k: alvo }); vaiNivel(alvo - 1); } }
    else if (k === 'ArrowDown' || k === 'ArrowUp') {
      ev.preventDefault();
      const c = camadaSel() ?? (k === 'ArrowDown' ? 0 : 9);
      seleciona({ tipo: 'camada', k: Math.max(1, Math.min(8, c + (k === 'ArrowDown' ? 1 : -1))) });
    } else if (k === 'Enter' && sel) { const c = camadaSel(); if (c != null) (alvo >= c ? recoloca : remove)(c); }
    else return;
    ev.stopPropagation();
  }, true);

  // ---- quadro ----
  gsap.ticker.add((_, ms) => {
    if (!ativo) return;
    const dt = Math.min(0.1, ms / 1000);
    const c = cena.controls, cam = cena.camera;
    c.update(dt);
    const near = Math.min(Math.max(1, c.distance * 0.08), 60), far = Math.max(2000, c.distance * 12);
    if (cam.near !== near || cam.far !== far) { cam.near = near; cam.far = far; cam.updateProjectionMatrix(); }
    cena.aplicaEstado(st.nivel, fAnt, fCur, st.hl);
    cena.desenha();
    seloE8.style.visibility = st.nivel > 7.02 ? 'visible' : 'hidden';
    // linha da âncora da peça até o painel
    const a = ancora ? cena.ancoraTela(ancora) : null;
    const r = painel.getBoundingClientRect(), pr = palco.getBoundingClientRect(), kx = STAGE_W / pr.width;
    const ex = (r.left - pr.left) * kx, ey = (r.top - pr.top) * kx + 64;
    if (a && a[0] > LIVRE[0] - 60 && a[0] < ex - 20 && a[1] > 90 && a[1] < STAGE_H - 60) {
      linha.setAttribute('d', `M${a[0].toFixed(1)},${a[1].toFixed(1)} L${(ex - 56).toFixed(1)},${ey.toFixed(1)} L${ex.toFixed(1)},${ey.toFixed(1)}`);
      ponto.setAttribute('cx', a[0]); ponto.setAttribute('cy', a[1]);
      linha.parentNode.style.visibility = 'visible';
    } else linha.parentNode.style.visibility = 'hidden';
  });

  function entra() {
    if (ativo) return;
    tour.suspende();
    ativo = true;
    document.body.classList.add('modo-explorar');
    raiz.hidden = false;
    tela.style.visibility = 'visible'; tela.style.opacity = 1;
    const c = cena.controls, cam = cena.camera;
    limites.min = c.minDistance; limites.max = c.maxDistance;
    c.minDistance = 25; c.maxDistance = 3000; c.enabled = true;
    cam.fov = VISTA.fov; cam.updateProjectionMatrix();
    c.setLookAt(...VISTA.pos, ...VISTA.target, false);
    enquadra(alvo, null, false);
    seleciona(sel);
  }
  function sai() {
    if (!ativo) return;
    ativo = false;
    gsap.killTweensOf(st);
    st.nivel = alvo; st.hl = 1;
    raiz.hidden = true;
    document.body.classList.remove('modo-explorar');
    const c = cena.controls;
    c.minDistance = limites.min; c.maxDistance = limites.max;
    tour.retoma();
  }

  desenhaPainel(); desenhaLista();
  return {
    entra, sai, ativo: () => ativo,
    /** Para os testes: estado do modo. */
    estado: () => ({ ativo, nivel: Math.round(st.nivel * 1e4) / 1e4, alvo, sel }),
    seleciona, remove, recoloca, vaiNivel,
    projeta: (p) => cena.projeta(p),
  };
}
