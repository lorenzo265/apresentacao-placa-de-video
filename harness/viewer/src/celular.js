// Layout do celular (só com window.__CELULAR__, decidido no index.html: tela de toque pequena ou ?celular=1).
// No computador este módulo não roda e nada muda.
//
// O palco lógico continua 1920 x 1080 (3D, diagramas, linha de chamada); o que é texto sai dele para
// painéis nativos, em tamanho de leitura: cabeçalho compacto em cima, caixa de texto num painel
// recolhível (embaixo em retrato, à direita em paisagem) e botões grandes no lugar das teclas.
// Em retrato o palco ocupa a largura toda e o enquadramento usa o palco inteiro (layout.js, safeRect).
import { STAGE_W, STAGE_H, rectLivre3d } from './layout.js';

const ICONE_CENTRO = '<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="3.2"/><path d="M12,2.5 L12,6.5 M12,17.5 L12,21.5 M2.5,12 L6.5,12 M17.5,12 L21.5,12"/></svg>';

export function criaLayoutCelular(palco) {
  const raiz = document.documentElement;
  raiz.classList.add('celular');
  const movel = document.createElement('div');
  movel.id = 'movel';
  movel.innerHTML = `
    <div id="m-area"></div>
    <section id="m-painel" class="ui" aria-label="Texto do momento">
      <button class="m-alca" data-a="alca" aria-label="Recolher ou abrir o texto"><i></i></button>
      <div class="m-rolagem"></div>
    </section>
    <button id="m-centro" class="ui" aria-label="Voltar ao enquadramento" hidden>${ICONE_CENTRO}</button>`;
  document.body.appendChild(movel);
  const area = movel.querySelector('#m-area');
  const painel = movel.querySelector('#m-painel');
  const rolagem = painel.querySelector('.m-rolagem');

  let recolhido = false;
  let alturaLivre = null;          // altura do painel em retrato arrastada pela alça (px); null = a padrão
  let escala = 1;
  let palcoRet = { l: 0, t: 0, w: 0, h: 0 };
  const retrato = () => innerHeight >= innerWidth;

  /** Altura do painel em retrato quando nada foi arrastado: o que sobra abaixo do palco na largura toda. */
  function alturaPadrao() {
    const cs = getComputedStyle(movel);
    const altura = movel.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    const largura = movel.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    const fixo = [...movel.children].filter((e) => e.dataset.linha === 'fixa' && e.offsetParent).reduce((s, e) => s + e.offsetHeight, 0);
    return Math.max(150, Math.round(altura - fixo - largura * STAGE_H / STAGE_W));
  }
  const alturaRecolhida = () => (document.body.classList.contains('modo-explorar') ? 132 : 64);

  /** Põe o palco (1920 x 1080, escalado) dentro da área livre. Devolve a escala. */
  function ajusta() {
    const r = retrato();
    raiz.classList.toggle('retrato', r);
    raiz.classList.toggle('paisagem', !r);
    raiz.classList.toggle('recolhido', recolhido);
    if (r) {
      const h = recolhido ? alturaRecolhida() : alturaLivre ?? alturaPadrao();
      movel.style.setProperty('--painel-h', `${Math.round(h)}px`);
    }
    const a = area.getBoundingClientRect();
    escala = Math.max(0.05, Math.min(a.width / STAGE_W, a.height / STAGE_H));
    const w = STAGE_W * escala, h = STAGE_H * escala;
    // em retrato o palco encosta no cabeçalho (sobra embaixo, junto do texto); em paisagem, centrado
    const top = r && !recolhido ? a.top : a.top + (a.height - h) / 2;
    palcoRet = { l: a.left + (a.width - w) / 2, t: top, w, h };
    palco.style.left = `${palcoRet.l + w / 2}px`;
    palco.style.top = `${palcoRet.t + h / 2}px`;
    palco.style.transform = `translate(-50%, -50%) scale(${escala})`;
    for (const [k, v] of Object.entries(palcoRet)) movel.style.setProperty(`--palco-${k}`, `${v}px`);
    return escala;
  }
  new ResizeObserver(() => ajusta()).observe(movel);
  addEventListener('orientationchange', () => setTimeout(ajusta, 120));

  // ---- alça do painel: tocar recolhe ou abre; em retrato, arrastar muda a altura ----
  function alternaRecolhido(v = !recolhido) {
    recolhido = v;
    if (!recolhido && alturaLivre != null && alturaLivre < alturaRecolhida() + 40) alturaLivre = null;
    ajusta();
  }
  function ligaAlca(alca) {
    let arr = null;
    alca.addEventListener('pointerdown', (ev) => {
      arr = { y: ev.clientY, h: parseFloat(movel.style.getPropertyValue('--painel-h')) || alturaPadrao(), andou: false };
      alca.setPointerCapture(ev.pointerId);
    });
    alca.addEventListener('pointermove', (ev) => {
      if (!arr || !retrato()) return;
      const dy = ev.clientY - arr.y;
      if (!arr.andou && Math.abs(dy) < 8) return;
      arr.andou = true;
      recolhido = false;
      alturaLivre = Math.max(alturaRecolhida(), Math.min(innerHeight * 0.78, arr.h - dy));
      ajusta();
    });
    const fim = () => {
      if (!arr) return;
      const a = arr; arr = null;
      if (!a.andou) { alternaRecolhido(); return; }
      if (alturaLivre <= alturaRecolhida() + 30) { alturaLivre = null; alternaRecolhido(true); }
    };
    alca.addEventListener('pointerup', fim);
    alca.addEventListener('pointercancel', fim);
  }
  ligaAlca(painel.querySelector('.m-alca'));

  /** Destino da linha de chamada (callout.js): a borda do palco voltada para o painel do texto. */
  function destinoLinha() {
    if (retrato()) return { tipo: 'baixo' };
    if (recolhido) return { tipo: 'direita', y: null };
    const h2 = rolagem.querySelector('#caixa h2');
    if (!h2 || !escala) return { tipo: 'direita', y: null };
    const r = h2.getBoundingClientRect();
    const y = (r.top + Math.min(r.height / 2, 14) - palcoRet.t) / escala;
    return { tipo: 'direita', y: Math.max(40, Math.min(STAGE_H - 40, y)) };
  }

  /** Liga o resto depois que o tour e o Explorar existem: muda os elementos de lugar e liga os gestos. */
  function liga({ tour, explorar, cena }) {
    const $ = (s) => document.getElementById(s);
    // cabeçalho em cima; caixa, aviso e selo no painel; barra embaixo
    const cab = $('cabecalho');
    cab.dataset.linha = 'fixa';
    movel.prepend(cab);
    rolagem.append($('caixa'));
    movel.append($('aviso-diagrama'), $('selo-vitrine'));
    const barra = $('barra');
    barra.dataset.linha = 'fixa';
    movel.append(barra, $('indice'), $('notas'));
    // rótulos curtos e sem tecla
    const bt = (a) => barra.querySelector(`[data-a=${a}]`);
    bt('indice').textContent = 'Índice';
    bt('notas').textContent = 'Notas';
    bt('explorar').textContent = 'Explorar';
    // "voltar ao enquadramento" vira um botão redondo no canto do palco
    const centroOrig = bt('centro'), centro = $('m-centro');
    new MutationObserver(() => { centro.hidden = centroOrig.hidden; }).observe(centroOrig, { attributes: true, attributeFilter: ['hidden'] });
    centro.addEventListener('click', () => { tour.recentra(); centro.blur(); });
    const idx = $('indice');
    const ajuda = idx.querySelector('header p');
    if (ajuda) ajuda.textContent = 'Toque num momento. Os extras, tracejados, ficam fora do caminho das setas.';
    idx.querySelector('[data-a=fecha]').textContent = 'Fechar';
    // tocar nas notas fecha
    $('notas').addEventListener('click', () => { $('notas').hidden = true; });

    // ---- Explorar: topo em cima, camadas e explicação numa folha (embaixo ou à direita) ----
    if (explorar) {
      const ex = $('explorar');
      movel.append(ex);
      const folha = document.createElement('div');
      folha.className = 'ex-folha ui';
      folha.innerHTML = '<button class="m-alca" aria-label="Recolher ou abrir a explicação"><i></i></button>';
      const dica = ex.querySelector('.ex-dica');
      dica.textContent = 'um dedo gira, dois dedos aproximam, toque numa peça para selecionar';
      folha.append(ex.querySelector('.ex-camadas'), ex.querySelector('.ex-painel'), dica);
      ex.append(folha);
      ex.querySelector('.ex-topo').dataset.linha = 'fixa';
      const sair = ex.querySelector('[data-a=sair]');
      sair.textContent = 'Voltar à apresentação';
      ligaAlca(folha.querySelector('.m-alca'));
      // trocar de modo muda o que ocupa o topo e a folha: refaz o encaixe
      new MutationObserver(() => { recolhido = false; ajusta(); }).observe(ex, { attributes: true, attributeFilter: ['hidden'] });
      // a seleção de uma peça abre a explicação no começo
      const exPainel = ex.querySelector('.ex-painel');
      new MutationObserver(() => { exPainel.scrollTop = 0; }).observe(exPainel, { childList: true });
    }

    // ---- deslizar para passar o momento: no painel do texto ou a partir das bordas do palco ----
    const emExplorar = () => !!explorar?.ativo();
    const passa = (dx) => { if (dx < 0) tour.next(); else tour.prev(); };
    let desl = null;
    painel.addEventListener('pointerdown', (ev) => {
      if (ev.pointerType === 'mouse' || ev.target.closest('.m-alca')) return;
      desl = { id: ev.pointerId, x: ev.clientX, y: ev.clientY, t: performance.now() };
    });
    // bordas do palco: o toque que começa nelas não chega ao giro da câmera (fase de captura)
    const BORDA = 26;
    palco.addEventListener('pointerdown', (ev) => {
      if (ev.pointerType !== 'touch' || emExplorar()) return;
      if (ev.clientX - palcoRet.l > BORDA && palcoRet.l + palcoRet.w - ev.clientX > BORDA) return;
      ev.stopPropagation();
      desl = { id: ev.pointerId, x: ev.clientX, y: ev.clientY, t: performance.now(), borda: true };
    }, true);
    const fimDesl = (ev) => {
      if (!desl || ev.pointerId !== desl.id) return;
      const dx = ev.clientX - desl.x, dy = ev.clientY - desl.y, dt = performance.now() - desl.t;
      desl = null;
      if (ev.type !== 'pointerup' || emExplorar()) return;
      if (Math.abs(dx) > 50 && Math.abs(dx) > 1.6 * Math.abs(dy) && dt < 900) passa(dx);
    };
    addEventListener('pointerup', fimDesl);
    addEventListener('pointercancel', fimDesl);      // o painel rolou na vertical: não é deslize

    // ---- recorte da câmera 3D: as câmeras do storyboard foram compostas com a coluna da caixa de texto
    // ao lado; no celular a caixa está fora do palco, então a imagem 3D mostra só a área livre do
    // computador (um retângulo 16:9 em volta dela), ampliada para o palco inteiro. Com setViewOffset as
    // âncoras, os caminhos e a linha de chamada projetam no mesmo recorte. Muda suave entre momentos;
    // diagramas e Explorar ficam sem recorte. ----
    if (cena?.camera && cena.ajustaCamera) {
      const cam = cena.camera;
      let rc = null, tAnt = 0;
      const alvo = () => {
        const b = tour.beatAtual()?.beat;
        if (!b || b.level >= 2) return { x: 0, y: 0, w: STAGE_W };
        const [fx, fy, fw, fh] = rectLivre3d(b.callout);
        const w = Math.min(STAGE_W, fw + 48), h = w * STAGE_H / STAGE_W;
        return { x: Math.max(0, Math.min(STAGE_W - w, fx + fw / 2 - w / 2)), y: Math.max(0, Math.min(STAGE_H - h, fy + fh / 2 - h / 2)), w };
      };
      const aplica = () => {
        if (rc.w > STAGE_W - 0.5) { if (cam.view?.enabled) cam.clearViewOffset(); return; }
        cam.setViewOffset(STAGE_W, STAGE_H, rc.x, rc.y, rc.w, rc.w * STAGE_H / STAGE_W);
      };
      const ajusta0 = cena.ajustaCamera;
      cena.ajustaCamera = (c) => {
        ajusta0(c);
        const a = alvo(), t = performance.now(), dt = (t - tAnt) / 1000;
        tAnt = t;
        if (!rc || dt > 0.5) rc = { ...a };
        else { const k = 1 - Math.exp(-dt / 0.3); for (const n of ['x', 'y', 'w']) rc[n] += (a[n] - rc[n]) * k; }
        aplica();
      };
      // Explorar enquadra a placa no palco inteiro: sem recorte
      const ex = $('explorar');
      if (ex) new MutationObserver(() => { if (!ex.hidden && cam.view?.enabled) { cam.clearViewOffset(); rc = null; } }).observe(ex, { attributes: true, attributeFilter: ['hidden'] });
    }

    // ---- desempenho: no celular a cena começa na qualidade baixa (main.js); se ainda assim ficar
    // abaixo de 24 quadros por segundo, a resolução do canvas cai (duas vezes no máximo) ----
    if (cena?.renderer && cena.qualidade?.() === 'baixa') {
      const desenha0 = cena.desenha;
      const med = { ult: 0, n: 0, soma: 0, cortes: 0 };
      cena.desenha = (o) => {
        const fez = desenha0(o);
        if (fez && med.cortes < 2) {
          const t = performance.now(), d = t - med.ult;
          med.ult = t;
          if (d > 0 && d < 250) { med.n++; med.soma += d; }
          if (med.n >= 45) {
            const qps = 1000 * med.n / med.soma;
            med.n = 0; med.soma = 0;
            if (qps < 24) {
              const pr = cena.renderer.getPixelRatio(), novo = Math.max(0.5, pr * 0.75);
              if (novo < pr - 0.01) { cena.renderer.setPixelRatio(novo); med.cortes++; console.info(`[celular] ${qps.toFixed(0)} qps: resolução ${novo.toFixed(2)}`); }
              else med.cortes = 2;
            } else med.cortes = 2;
          }
        }
        return fez;
      };
    }
    ajusta();
  }

  return { ajusta, liga, destinoLinha, escala: () => escala, recolhe: alternaRecolhido, recolhido: () => recolhido };
}
