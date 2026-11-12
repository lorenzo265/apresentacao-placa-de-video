// Interface do modo Apresentação (escondida na captura): barra discreta, índice de momentos (M),
// notas do apresentador (N) e teclado. Setas e clicker andam de momento em momento.
const ATOS = ['Abertura', 'Placa por fora', 'Desmontagem', 'Memória da placa', 'Chip', 'SM, registradores e instruções', 'A GPU no sistema', 'Fechamento'];
const SETA_E = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M15,5 L8,12 L15,19"/></svg>';
const SETA_D = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M9,5 L16,12 L9,19"/></svg>';
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;');

export function criaControles(palco, tour) {
  const barra = document.createElement('div');
  barra.id = 'barra';
  barra.className = 'ui';
  barra.innerHTML = `
    <div class="grupo">
      <button data-a="prev" aria-label="Momento anterior" title="Momento anterior (seta para a esquerda)">${SETA_E}</button>
      <button data-a="next" aria-label="Próximo momento" title="Próximo momento (seta para a direita)">${SETA_D}</button>
      <button data-a="indice" title="Índice dos momentos">Índice <kbd>M</kbd></button>
      <button data-a="notas" title="Notas do apresentador">Notas <kbd>N</kbd></button>
      <button data-a="centro" title="Voltar ao enquadramento do momento" hidden>Voltar ao enquadramento <kbd>R</kbd></button>
      <span class="extra" hidden>Extra. As setas voltam à apresentação.</span>
    </div>
    <div class="grupo">
      <button data-a="explorar" class="primario" title="Controlar a placa e remover as camadas" hidden>Explorar a placa <kbd>E</kbd></button>
    </div>`;
  palco.appendChild(barra);
  const bCentro = barra.querySelector('[data-a=centro]'), bExtra = barra.querySelector('.extra'), bExplorar = barra.querySelector('[data-a=explorar]');

  // ---- notas ----
  const notas = document.createElement('aside');
  notas.id = 'notas';
  notas.className = 'ui';
  notas.hidden = true;
  palco.appendChild(notas);
  function atualizaNotas() {
    const m = tour.momento(), b = tour.beatAtual(), t = tour.textoDe(b.id);
    const topicos = (t.fala ?? '').split('•').map((x) => x.trim()).filter(Boolean);
    const prox = !m.extra && m.idx + 1 < m.total ? tour.textoDe(tour.beats[m.idx + 1].id).headline : null;
    notas.innerHTML = `
      <p class="quem">${m.extra ? 'Extra' : `Momento ${m.idx + 1} de ${m.total}`} <span>fala de <b>${esc(b.beat.speaker ?? 'sem responsável')}</b></span></p>
      ${topicos.length ? `<ul class="fala">${topicos.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : '<p class="fala">(sem fala registrada)</p>'}
      ${prox ? `<p class="prox">A seguir: <b>${esc(prox)}</b></p>` : ''}`;
    notas.dataset.id = b.id;
  }

  // ---- índice ----
  const indice = document.createElement('div');
  indice.id = 'indice';
  indice.className = 'ui';
  indice.hidden = true;
  palco.appendChild(indice);
  const numero = new Map(tour.beats.map((b, i) => [b.id, i + 1]));
  const extras = new Set(tour.extras);
  {
    const grupos = [];
    for (const b of tour.storyboard.beats) {
      if (!numero.has(b.id) && !extras.has(b.id)) continue;
      let g = grupos.find((x) => x.act === b.act);
      if (!g) grupos.push(g = { act: b.act, itens: [] });
      g.itens.push(b.id);
    }
    indice.innerHTML = `
      <header><h2>Índice</h2><p>Clique num momento, ou digite o número e Enter. Os extras ficam fora do caminho das setas.</p>
        <button data-a="fecha">Fechar <kbd>Esc</kbd></button></header>
      <div class="colunas">${grupos.map((g) => `
        <section><h3>${esc(ATOS[g.act] ?? `Ato ${g.act}`)}</h3>${g.itens.map((id) => `
          <button data-id="${id}" class="${numero.has(id) ? 'momento' : 'extra'}"><i>${numero.get(id) ?? 'extra'}</i><span>${esc(tour.textoDe(id).headline)}</span></button>`).join('')}
        </section>`).join('')}</div>
      <p class="digitado" hidden></p>`;
  }
  const digitado = indice.querySelector('.digitado');
  let digitos = '';
  const mostraDigitos = () => { digitado.hidden = !digitos; digitado.textContent = digitos ? `Ir para o momento ${digitos}` : ''; };
  function abreIndice(abre) {
    indice.hidden = !abre; digitos = ''; mostraDigitos();
    if (abre) {
      const m = tour.momento(), atual = m.extra ?? tour.beats[m.idx].id;
      indice.querySelectorAll('button[data-id]').forEach((b) => b.classList.toggle('atual', b.dataset.id === atual));
      indice.querySelector('button.atual')?.scrollIntoView({ block: 'nearest' });
    }
  }
  indice.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.id) tour.irPara(b.dataset.id);
    abreIndice(false);
  });

  let explorar = null;       // modo Explorar (main.js liga depois, quando há GLB)
  const emExplorar = () => !!explorar?.ativo();
  const alternaNotas = () => { notas.hidden = !notas.hidden; if (!notas.hidden) atualizaNotas(); };

  barra.addEventListener('click', (e) => {
    const a = e.target.closest('button')?.dataset.a;
    if (a === 'prev') tour.prev();
    else if (a === 'next') tour.next();
    else if (a === 'indice') abreIndice(indice.hidden);
    else if (a === 'notas') alternaNotas();
    else if (a === 'centro') tour.recentra();
    else if (a === 'explorar') explorar?.entra();
    e.target.closest('button')?.blur();     // o espaço não deve reacionar o botão
  });

  window.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || emExplorar()) return;
    const k = e.key;
    if (!indice.hidden) {
      if (k === 'Escape' || k === 'm' || k === 'M') abreIndice(false);
      else if (/^\d$/.test(k)) { digitos = (digitos + k).slice(-2); mostraDigitos(); }
      else if (k === 'Backspace') { digitos = digitos.slice(0, -1); mostraDigitos(); }
      else if (k === 'Enter' && digitos) {
        const b = tour.beats[Number(digitos) - 1];
        if (b) { tour.irPara(b.id); abreIndice(false); } else { digitos = ''; mostraDigitos(); }
      }
      return;
    }
    if (k === 'ArrowRight' || k === 'PageDown' || k === ' ' || k === 'Enter') { e.preventDefault(); tour.next(); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); tour.prev(); }
    else if (k === 'Home') tour.irPara(tour.beats[0].id);
    else if (k === 'End') tour.irPara(tour.beats[tour.beats.length - 1].id);
    else if (k === 'n' || k === 'N') alternaNotas();
    else if (k === 'm' || k === 'M') abreIndice(true);
    else if (k === 'r' || k === 'R') tour.recentra();
    else if (k === 'e' || k === 'E') explorar?.entra();
    else if (k === 'Escape' && !notas.hidden) alternaNotas();
  });

  // A barra some quando o mouse fica parado; qualquer movimento a traz de volta.
  let ocioso = null;
  const acorda = () => {
    document.body.classList.remove('ocioso');
    clearTimeout(ocioso);
    ocioso = setTimeout(() => document.body.classList.add('ocioso'), 3500);
  };
  addEventListener('pointermove', acorda);
  addEventListener('pointerdown', acorda);
  acorda();

  let idNotas = null, livreAnt = null, extraAnt = null;
  return {
    /** Liga o modo Explorar: mostra o botão e a tecla E. */
    ligaExplorar(x) { explorar = x; bExplorar.hidden = false; },
    atualiza() {
      const m = tour.momento();
      if (m.livre !== livreAnt) { livreAnt = m.livre; bCentro.hidden = !m.livre; }
      if (!!m.extra !== extraAnt) { extraAnt = !!m.extra; bExtra.hidden = !m.extra; }
      const id = tour.beatAtual().id;
      if (!notas.hidden && idNotas !== id) { idNotas = id; atualizaNotas(); }
      if (notas.hidden) idNotas = null;
    },
  };
}
