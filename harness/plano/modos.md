# Dois modos de visualização (sessão de modos)

Dono: sessão de modos (branch `claude/apresentacao-modos`), aberta em 2026-11-12 pela orquestradora a pedido do autor. Sessões irmãs: câmera e desmontagem (`claude/apresentacao-camera-gsap`: `scene3d.js`, `desmontagem.json`, storyboard) e orquestradora (lookdev: `materials.json`, `lookdev.js`, `temas.js`, `temas.css`). Não mexo nesses arquivos sem combinar.

## 1. Pedido do autor (2026-11-12)

"Não gosto da forma que está apresentado hoje, esse sistema de completo, seminário e os botões que não funcionam não dá certo. Vamos dividir em dois modos limpos: uma sucessão de momentos que permite controle da tela mas age como um slide, passo nas setas direita e esquerda; e outra que conseguimos controlar a placa por completo, selecionamos os painéis que queremos remover e removemos com uma explicação de cada um. Mas repensamos todo o sistema de visualização da página."

## 2. Diagnóstico da interface atual

- Barra com sete controles (anterior, tocar, próximo, lista de beats, seletor de corte, notas). O seletor de corte recarrega a página.
- O tour é uma linha do tempo que toca sozinha; a seta toca até o próximo beat. Só dá para girar a placa com o tour pausado, e só em beat 3D.
- O painel de notas (tecla N) lista os beats fora do corte e cobre meia tela.
- Dois cortes (seminário com 28 beats, completo com 58 prontos) para a mesma apresentação.

## 3. Proposta (aprovada, ver seção 5)

Página de rascunho com esboços das telas, enviada ao autor em 2026-11-12.

### 3.1 Modo Apresentação

- Seta direita: próximo momento, e para. Seta esquerda: momento anterior, já montado. Seta no meio da animação: pula para o fim dela. Espaço e clicker valem como seta direita.
- Girar e aproximar a qualquer hora (3D e diagramas), sem perder o lugar. Tecla R, ou a próxima seta, devolve o enquadramento do momento.
- Sai: tocar sozinho, seletor de corte, lista de beats na barra. Fica: trilha de nível, contador "7 / 28", caixa de texto, linha de atalhos que some.
- Tecla N: notas com quem fala, tópicos da fala e título do próximo momento. Tecla M: índice dos momentos por ato.
- Momentos: os 28 beats do corte do seminário, na mesma ordem, com a mesma câmera, desmontagem e texto. Os 30 beats que só estavam no corte completo viram extras: fora do caminho das setas, abertos pelo índice (recomendação).

### 3.2 Modo Explorar

- Placa inteira sob controle (girar, aproximar). Clique na peça ou na lista de camadas seleciona e abre a explicação com selo de procedência. Remover toca a desmontagem que já existe (`desmontagem.json`); recolocar toca ao contrário.
- Camadas: os oito estágios E1 a E8. Recomendação: ordem real com atalho (remover a camada k tira antes as camadas da frente, em sequência rápida). E8 segue `inferred`, com selo e aviso.
- Peças soldadas ao PCB (chip, memória, conector, reguladores): selecionar, ler e ver de perto, sem remover.
- Sair devolve a apresentação ao momento em que ela estava.

### 3.3 Textos por peça

- Camadas 2 a 7: beats a2.2 a a2.7 (escritos e auditados, hoje `draft` e sem uso na tela).
- Ventiladores, conector, memória, PCIe: beats a1.x e a3.x.
- Peças sem beat: texto novo curto, só com fatos de `spec/card.spec.json` e de `design/assembly.json`, com selo. Passa pelo `fact-checker` antes de entrar. Sem fonte, a peça mostra "não achamos nas fontes lidas".

### 3.4 Perguntas abertas ao autor

1. Momentos: 28 numerados e extras no índice (recomendado), todos os 58 em sequência, ou só os 28.
2. Ordem de remoção no Explorar: ordem real com atalho (recomendado) ou livre com selo de ilustrativo.
3. Entrada: abrir direto na Apresentação (recomendado) ou tela inicial com os dois modos.
4. Tela do Explorar: lista de camadas e painel (recomendado) ou tela limpa com cartão flutuante.

## 4. Combinado com as outras sessões

- 2026-11-12: proposta enviada em resumo à orquestradora. Nada combinado ainda com a sessão de câmera; o modo Explorar vai precisar de uma função de estado por camada em `scene3d.js` (hoje a explosão é um nível contínuo único), a combinar com ela antes de mexer.

## 5. Decisões do autor (2026-11-12)

O autor escolheu as quatro recomendações:

1. Momentos: os 28 do corte do seminário nas setas, os outros 30 como extras no índice.
2. Remoção no Explorar: ordem real com atalho.
3. Entrada: abre direto na Apresentação; botão e tecla E levam ao Explorar; Esc volta ao momento.
4. Tela do Explorar: lista de camadas à esquerda e painel à direita.

## 6. Feito (2026-11-12)

- Apresentação: `viewer/src/tour.js` (trilha principal e trilha de extras, fases andando, leitura e parado, câmera e diagrama livres com volta suave), `controls.js` (barra, índice, notas, teclado), `header.js` (contador "7 / 28" no lugar da seção).
- Explorar: `viewer/src/explorar.js`, `content/pt-BR/pecas.json`, `viewer/src/modos.css`. Sem mudança em `scene3d.js`, `desmontagem.json`, storyboard nem nos arquivos de lookdev: remover uma camada é levar o nível de explosão que a cena já tem.
- O que era o "botão que não funciona": a seta tocava a linha do tempo a partir do instante atual, então esperava o resto do `hold` do beat (até 28 s) antes de qualquer coisa se mexer. Agora a seta salta para o início da saída.
- Teste: `tools/smoke-single.cjs` adaptado (momentos pela seta, pulo da animação, notas, índice, extra, Explorar). Passa no corte do seminário, por `file://` e sem rede.
- Textos: duas passadas do `fact-checker` (`qa/fact-check-modo-explorar.md`), ambas reprovadas e corrigidas com o texto do auditor.

## 7. Pendente

- Terceira passada do `fact-checker` nos textos fixos corrigidos do Explorar, e segunda passada dos beats a2.2 a a2.6 (hoje `draft`, usados como explicação das camadas 2 a 6).
- `visual-qa` da orquestradora nas telas dos dois modos (quem cria não aprova).
- Ensaio numa máquina com GPU: aqui só houve render por software, abaixo de 1 quadro por segundo, então a fluidez das transições e do giro livre não foi vista.
- "Ver de perto" mantém a direção em que o usuário olha; com a placa toda desmontada, outra peça pode ficar na frente.
- Abrir um extra da desmontagem pelo índice mostra a placa no estado daquele beat, sem animação de passagem.
- `smoke.cjs`, `capture.cjs` e as outras ferramentas de captura não foram rodadas depois da mudança (usam `seek`, cujo caminho não mudou; o cabeçalho agora mostra o contador no lugar de "Seção NN", o que muda os quadros capturados).
- Decisão do autor: a peça `io.bracket` usa o texto a1.5 ("com 4 portas DisplayPort") e a camada 1 diz "As portas não saem com ele". O auditor não exige mudança.
