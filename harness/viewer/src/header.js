// Cabeçalho: trilha de nível, contador de momentos, barra de progresso; faixa fixa com o aviso dos diagramas.
const NIVEIS = [['Placa', [0, 1]], ['Chip', [2]], ['SM', [3]], ['Conceito', [4]]];

export function criaCabecalho(palco) {
  const h = document.createElement('header');
  h.id = 'cabecalho';
  h.innerHTML = `
    <nav class="trilha">${NIVEIS.map(([n]) => `<span>${n}</span>`).join('<i>›</i>')}</nav>
    <div class="secao"></div>
    <div class="progresso"><div class="barra"></div></div>`;
  const aviso = document.createElement('div');
  aviso.id = 'aviso-diagrama';
  const blockout = document.createElement('div');
  blockout.id = 'aviso-blockout';
  blockout.textContent = 'blockout: forma provisória';
  palco.append(h, aviso, blockout);
  const itens = [...h.querySelectorAll('.trilha span')];
  const barra = h.querySelector('.barra'), secao = h.querySelector('.secao');
  let nivelAnt = -1, textoAnt = null;

  return {
    atualiza({ beat, progresso, rotulo, disclaimer, mix, blockoutVisivel }) {
      if (beat.level !== nivelAnt) {
        nivelAnt = beat.level;
        NIVEIS.forEach(([, ls], i) => itens[i].classList.toggle('ativo', ls.includes(beat.level)));
      }
      if (secao.textContent !== rotulo) secao.textContent = rotulo;      // contador de momentos ("7 / 28") ou "Extra"
      barra.style.width = `${(progresso * 100).toFixed(2)}%`;
      if (disclaimer !== textoAnt) { textoAnt = disclaimer; aviso.textContent = disclaimer ?? ""; }
      aviso.style.opacity = mix;
      aviso.style.visibility = mix > 0.001 ? 'visible' : 'hidden';
      blockout.style.visibility = blockoutVisivel && mix < 0.5 ? 'visible' : 'hidden';
    },
  };
}
