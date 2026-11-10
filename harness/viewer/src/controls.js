// Controles (escondidos em captura) e painel de notas. Teclado: setas, espaço, N.
const ICON_PLAY = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M7,4 L20,12 L7,20 Z"/></svg>';
const ICON_PAUSA = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M7,4 H10 V20 H7 Z M14,4 H17 V20 H14 Z"/></svg>';

export function criaControles(palco, tour, { cortes, corteAtual, draftBlocked }) {
  const barra = document.createElement('div');
  barra.id = 'controles';
  barra.innerHTML = `
    <button data-a="prev" title="Beat anterior (←)"><svg viewBox="0 0 24 24" width="26" height="26"><path d="M6,5 V19 M19,5 L9,12 L19,19 Z"/></svg></button>
    <button data-a="play" title="Tocar ou pausar (espaço)"><svg viewBox="0 0 24 24" width="26" height="26"><path d="M7,4 L20,12 L7,20 Z"/></svg></button>
    <button data-a="next" title="Próximo beat (→)"><svg viewBox="0 0 24 24" width="26" height="26"><path d="M18,5 V19 M5,5 L15,12 L5,19 Z"/></svg></button>
    <select data-a="beat" title="Ir para o beat"></select>
    <select data-a="corte" title="Corte">${cortes.map((c) => `<option ${c === corteAtual ? 'selected' : ''}>${c}</option>`).join('')}</select>
    <button data-a="notas" title="Notas do apresentador (N)">Notas</button>`;
  palco.appendChild(barra);
  const sel = barra.querySelector('[data-a=beat]');
  sel.innerHTML = tour.beats.map((b) => `<option value="${b.id}">${b.id}  ${tour.textoDe(b.id).headline}</option>`).join('');

  const painel = document.createElement('aside');
  painel.id = 'notas';
  painel.hidden = true;
  palco.appendChild(painel);

  function atualizaPainel() {
    const b = tour.beatAtual();
    const t = tour.textoDe(b.id);
    const lista = draftBlocked.map((x) => `<li><b>${x.id}</b> <em>${x.status}</em></li>`).join('') || '<li>nenhum</li>';
    painel.innerHTML = `
      <h3>Notas do apresentador</h3>
      <p class="quem">Beat <b>${b.id}</b> &middot; fala de <b>${b.beat.speaker ?? 'sem responsável'}</b></p>
      <p class="fala">${t.fala ? t.fala.replace(/</g, '&lt;') : '(sem fala registrada)'}</p>
      <h4>Beats fora do corte (rascunho ou bloqueados)</h4><ul>${lista}</ul>`;
  }
  const alterna = () => { painel.hidden = !painel.hidden; if (!painel.hidden) atualizaPainel(); };

  barra.addEventListener('click', (e) => {
    const a = e.target.dataset?.a;
    if (a === 'prev') tour.prev();
    else if (a === 'next') tour.next();
    else if (a === 'play') tour.playing() ? tour.pause() : tour.play();
    else if (a === 'notas') alterna();
  });
  sel.addEventListener('change', () => tour.goto(sel.value));
  barra.querySelector('[data-a=corte]').addEventListener('change', (e) => {
    const u = new URL(location.href); u.searchParams.set('cut', e.target.value); location.href = u;
  });
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'SELECT') return;
    if (e.key === 'ArrowRight') tour.next();
    else if (e.key === 'ArrowLeft') tour.prev();
    else if (e.key === ' ') { e.preventDefault(); tour.playing() ? tour.pause() : tour.play(); }
    else if (e.key === 'n' || e.key === 'N') alterna();
  });

  return {
    atualiza() {
      barra.querySelector('[data-a=play]').innerHTML = tour.playing() ? ICON_PAUSA : ICON_PLAY;
      const id = tour.beatAtual().id;
      if (sel.value !== id) sel.value = id;
      if (!painel.hidden && painel.dataset.id !== id) { painel.dataset.id = id; atualizaPainel(); }
    },
    esconde() { barra.hidden = true; painel.remove(); },
  };
}
