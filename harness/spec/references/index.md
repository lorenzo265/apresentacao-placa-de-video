# Pacote de referências visuais da RTX PRO 6000 Blackwell Workstation Edition

> Catalogado em 2026-11-09 a partir das imagens do teardown da Gamers Nexus (GN) e das imagens oficiais da NVIDIA (página do produto e datasheet). **Tudo aqui é observação visual**: descreve o que aparece na imagem, não o que se espera da placa. Contagens com resolução insuficiente aparecem como faixa. Nada aqui passou ainda pelo `visual-qa` nem pelo `fact-checker`.

## Como usar

- As imagens ficam em `harness/spec/references/cache/` (`gn/` e `nvidia/`). A pasta tem um `.gitignore` próprio (`*`) e **não é versionada**: são imagens de terceiros. Para recriar o cache, baixe de novo pelas URLs da Tabela 1 (a página da GN responde a `curl` com User-Agent de navegador).
- Ids: `gn-NN` segue a ordem das imagens no corpo do artigo da GN (todas as `<img>` com `inline-images`, inclusive anúncios e gráficos). Para as capturas de vídeo foi baixado o original em resolução cheia (`data-full-url`, 3840 × 2160). `nv-NN` são as imagens da NVIDIA; `nv-13` é o PDF do datasheet, com as páginas renderizadas em `nv-13-p-1.png` a `nv-13-p-3.png`.
- Convenção de faces, usada no texto todo:
  - **face A** = a face com os dois ventiladores.
  - **face B** = a face oposta, com grade fina e o texto "RTX PRO 6000" no X central.
  - **borda superior** = a borda oposta aos dedos PCIe (onde entra o cabo de energia).
  - **extremidade do bracket** = a ponta com as saídas DisplayPort; **extremidade oposta** = a outra ponta.
- Página da GN: https://gamersnexus.net/gpus/nvidia-rtx-pro-6000-blackwell-benchmarks-tear-down-thermals-gaming-llm-acoustic-tests. O artigo diz ser a adaptação escrita de um vídeo de 2025-06-24.

### Contagem

| Origem | Arquivos | Mostram a placa |
|---|---|---|
| GN, corpo do artigo | 75 (não 35, como dizia `physical-card-sources.md`) | 38 capturas de vídeo mostram uma placa deste modelo (gn-02, gn-03, gn-08 a gn-42, gn-46). Em gn-12 aparecem duas placas e não dá para dizer qual é qual. gn-05 traz uma foto de terceiro (TechPowerUp) |
| NVIDIA, página do produto | 12 imagens | 4 renders da placa (nv-01 a nv-04) e 2 renders de família, em que a placa aparece pequena (nv-05, nv-06). nv-07 a nv-12 são imagens de aplicação, sem a placa |
| NVIDIA, datasheet | 1 PDF (3 páginas) | a capa (nv-13, p. 1) é o mesmo render de nv-01 |

## Tabela 1. Catálogo por imagem

Qualidade "para medir": **boa** = quase ortogonal, nítida, com a peça inteira; **média** = dá para tirar proporção grosseira ou contagem; **ruim** = só serve para identificar.

| id | URL original | Arquivo no cache | Tipo | Vista | Estágio | O que aparece | Qualidade |
|---|---|---|---|---|---|---|---|
| gn-01 | [toolkit-tear-down.jpg](https://gamersnexus.net/u/inline-images/toolkit-tear-down.jpg) | `cache/gn/gn-01.jpg` | outro | — | — | anúncio do kit de ferramentas da GN | — |
| gn-02 | [captura 0-49](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%200-49%20screenshot_0.png) | `cache/gn/gn-02.png` | placa montada | três quartos da face A, com a borda superior | antes de E1 | dois ventiladores, X central com dois pedaços de fita azul e transparente, cabo adaptador ligado na borda superior (3 plugues de 8 vias visíveis na outra ponta), dedos PCIe, bracket | média (melhor foto de ventilador) |
| gn-03 | [captura 0-52](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%200-52%20screenshot.png) | `cache/gn/gn-03.png` | placa montada | face B quase de frente, placa em pé, ao lado de uma TITAN X | antes de E1 | duas áreas de grade fina com nervuras, X central brilhante, texto "RTX PRO 6000" em diagonal, formas escuras atrás da grade de cima, cabo adaptador | média (a perspectiva distorce, ver "Proporções") |
| gn-04 | [captura 3-40](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%203-40%20screenshot.png) | `cache/gn/gn-04.png` | outro | — | — | captura de busca: PNY RTX Pro 6000 **Server Edition** (outra variante, com aletas expostas) | não usar |
| gn-05 | [captura 4-0](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%204-0%20screenshot.png) | `cache/gn/gn-05.png` | outro | foto quase ortogonal da face A (TechPowerUp), miniaturas "I/O", "Bottom", "Back" e foto de um GB202 | — | página da TechPowerUp capturada no vídeo | boa para proporção, mas de terceiro e sem confirmação de que é esta placa |
| gn-06 | [captura 4-4](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%204-4%20screenshot.png) | `cache/gn/gn-06.png` | gráfico | — | — | diagrama de GPC do whitepaper (NVIDIA) | — |
| gn-07 | [captura 4-24](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%204-24%20screenshot.png) | `cache/gn/gn-07.png` | outro | — | — | tabela de especificações da TechPowerUp | — |
| gn-08 | [captura 6-35](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%206-35%20screenshot.png) | `cache/gn/gn-08.png` | placa montada | face B em perspectiva, de cabeça para baixo; borda superior no primeiro plano | antes de E1 | X central brilhante com "RTX PRO 6000", grades, plugue do cabo na borda superior, logotipo NVIDIA na lateral, dedos PCIe no alto | média |
| gn-09 | [captura 6-55](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%206-55%20screenshot.png) | `cache/gn/gn-09.png` | placa montada | face B, close vertical do X central | antes de E1 | X central, texto "RTX PRO 6000", nervuras finas, dedos PCIe na lateral | média |
| gn-10 | [captura 6-59](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%206-59%20screenshot.png) | `cache/gn/gn-10.png` | placa montada | face B, close junto aos dedos PCIe | antes de E1 | dedos PCIe com entalhe, grades com nervuras, X | ruim |
| gn-11 | [captura 7-37](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%207-37%20screenshot.png) | `cache/gn/gn-11.png` | placa montada | bracket, três quartos | antes de E1 | 4 DisplayPort em uma fileira, etiquetas, 4 parafusos, marcas CE/UKCA/FCC, face B ao fundo | boa para disposição, média para medir |
| gn-12 | [captura 8-9](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%208-9%20screenshot.png) | `cache/gn/gn-12.png` | outro (comparação) | face A de duas placas lado a lado | — | duas placas de dois ventiladores; a imagem sozinha não diz qual é a PRO 6000 | ruim |
| gn-13 | [captura 8-39](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%208-39%20screenshot.png) | `cache/gn/gn-13.png` | placa montada | borda superior | antes de E1 | painel preto brilhante com duas fendas longas de ventilação e um retângulo liso; plugue de energia encaixado na ponta do painel; logotipo NVIDIA (espelhado) na lateral | média |
| gn-14 | [captura 9-8](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%209-8%20screenshot.png) | `cache/gn/gn-14.png` | placa montada | borda superior e face B, placa na mão | antes de E1 | cabo adaptador com plugues de 8 vias e etiquetas brancas | ruim |
| gn-15 | [captura 9-37](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%209-37%20screenshot.png) | `cache/gn/gn-15.png` | desmontagem | bracket, placa em pé | E1 | chave de fenda num parafuso do bracket; face B com "RTX PRO 6000" | média |
| gn-16 | [captura 9-58](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%209-58%20screenshot.png) | `cache/gn/gn-16.png` | desmontagem | extremidade do bracket, já sem o bracket | E1 | placa de extremidade preta: 4 parafusos com arruela clara nos cantos, 9 parafusos pequenos visíveis em volta dos 4 DisplayPort, dois furos | boa |
| gn-17 | [captura 10-10](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2010-10%20screenshot.png) | `cache/gn/gn-17.png` | desmontagem | face B, três quartos | E2 | aro fino preto (a "moldura externa") sendo retirado; DisplayPort na ponta | média |
| gn-18 | [captura 10-50](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2010-50%20screenshot.png) | `cache/gn/gn-18.png` | desmontagem | face B, close junto aos dedos | E2 a E3 | sem o aro: peça de fixação do adaptador PCIe com parafusos, peça central, pequeno conector no centro do X | ruim |
| gn-19 | [captura 10-54](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2010-54%20screenshot.png) | `cache/gn/gn-19.png` | desmontagem | peça solta na mão | E3 (provável) | peça preta com um pad rosa; a imagem não diz qual peça é | ruim |
| gn-20 | [captura 11-12](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2011-12%20screenshot.png) | `cache/gn/gn-20.png` | desmontagem | face B, de cima | E3 | tampa triangular "RTX PRO 6000" sendo erguida; por baixo, placa central com 4 parafusos claros, etiqueta QR e uma matriz de contatos no centro do X; adaptador PCIe à esquerda | média |
| gn-21 | [captura 11-22](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2011-22%20screenshot.png) | `cache/gn/gn-21.png` | desmontagem | borda superior, sem o aro | E3 | conector com pinos dourados em duas fileiras, conector preto pequeno, fila de componentes na borda do PCB, pad branco, pilha de aletas sob a borda | média |
| gn-22 | [captura 11-34](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2011-34%20screenshot.png) | `cache/gn/gn-22.png` | desmontagem | face B, close | E4 | desparafusando a fixação do adaptador PCIe; etiqueta QR | média |
| gn-23 | [captura 11-44](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2011-44%20screenshot.png) | `cache/gn/gn-23.png` | desmontagem | face B, três quartos, placa inteira | E4 | vista geral: DisplayPort na ponta esquerda, logotipo NVIDIA na lateral direita, tampas centrais já fora | média |
| gn-24 | [captura 12-3](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2012-3%20screenshot.png) | `cache/gn/gn-24.png` | desmontagem | adaptador PCIe na mão e placa | E4 | adaptador retirado; 6 parafusos pretos sobre o tapete | média |
| gn-25 | [captura 12-5](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2012-5%20screenshot.png) | `cache/gn/gn-25.png` | desmontagem | adaptador PCIe, quase de frente | E4 | placa fina: dedos PCIe com entalhe, conector fino (serigrafia "J3"), 4 furos com anel de cobre, texto "UMT 1125 94V-0 / 13-03 W6 2V-2" (leitura incerta) | boa para forma, sem escala própria |
| gn-26 | [captura 12-18](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2012-18%20screenshot.png) | `cache/gn/gn-26.png` | desmontagem | face A, borda superior sem o aro | E4 a E5 | ventiladores de perto, aletas centrais, fila de componentes do PCB, bloco preto do conector de energia inclinado (à direita), conector dourado (à esquerda) | média |
| gn-27 | [captura 12-31](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2012-31%20screenshot.png) | `cache/gn/gn-27.png` | desmontagem | vista geral | E5 | placa que cobre o PCB (`pcb.plate`) na mão, com furo quadrado central e pads em volta; PCB exposto entre as duas carcaças; tampa "RTX PRO 6000" e aro sobre o tapete; "NVIDIA" na lateral da carcaça | média |
| gn-28 | [captura 13-32](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2013-32%20screenshot.jpg) | `cache/gn/gn-28.jpg` | PCB | verso do PCB, close oblíquo | E5 a E6 | chips de memória com resíduo de pad, conectores finos, cabo flat marrom, componentes do verso do GPU | média |
| gn-29 | [captura 13-38](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2013-38%20screenshot.jpg) | `cache/gn/gn-29.jpg` | PCB | verso do PCB, quase de cima | E6 | 16 chips de memória em volta do GPU, reforço em X com 4 parafusos sobre o verso do GPU, capacitores do verso do GPU, 2 conectores finos, conector de energia na borda, conector dourado na outra ponta da mesma borda | boa para contagem, média para medir |
| gn-30 | [captura 13-59](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2013-59%20screenshot.jpg) | `cache/gn/gn-30.jpg` | PCB | borda do PCB (verso), close | E6 | 4 chips de memória, fila de componentes retangulares, conector de energia (2 × 6 cavidades visíveis), aletas sob a borda com pad branco | boa (detalhe) |
| gn-31 | [captura 14-14](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2014-14%20screenshot_1.jpg) | `cache/gn/gn-31.jpg` | desmontagem | vista geral de cima | E6 | PCB inteiro entre as duas carcaças de aletas, cabo flat erguido, `pcb.plate` e peça em X sobre o tapete | média (oblíqua) |
| gn-32 | [captura 14-32](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2014-32%20screenshot.png) | `cache/gn/gn-32.png` | cooler | PCB erguido e base do cooler | E7 | PCB na mão (lado do GPU), base de contato com marca de pasta, pads, cabo flat preso ao cooler, peça em X sobre o tapete | média |
| gn-33 | [captura 14-37](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2014-37%20screenshot.png) | `cache/gn/gn-33.png` | PCB | frente do PCB, close | E7 | GB202 coberto de pasta cinza, moldura bege em volta do substrato verde, pads cobrindo as laterais, fila de indutores na borda | boa para detalhe, ruim para medir |
| gn-34 | [captura 15-7](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2015-7%20screenshot.png) | `cache/gn/gn-34.png` | cooler | base do cooler, close | E7 | placa de contato de tom acobreado com a marca da pasta, código datamatrix, pads com relevo, aletas sob a borda | média |
| gn-35 | [captura 15-19](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2015-19%20screenshot.png) | `cache/gn/gn-35.png` | cooler | base do cooler, macro | E7 | marca de pasta (bolhas, centro mais marcado), datamatrix, pads | média |
| gn-36 | [captura 15-52](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2015-52%20screenshot.png) | `cache/gn/gn-36.png` | PCB | frente, borda junto ao GPU | E7 | dois pads grandes com nervuras, fila de indutores, bloco preto com pinos marcado "85N" (leitura incerta) | média |
| gn-37 | [captura 16-41](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2016-41%20screenshot.png) | `cache/gn/gn-37.png` | PCB | frente, lateral | E7 | pad longo sobre uma lateral, com marcas de contato e um pad que passa da borda | média |
| gn-38 | [captura 16-47](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2016-47%20screenshot.png) | `cache/gn/gn-38.png` | PCB | frente, canto com a borda em degrau | E7 | indutores em fileiras diagonais, CI, componente "4R7", pads | média |
| gn-39 | [captura 17-8](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2017-8%20screenshot.png) | `cache/gn/gn-39.png` | cooler | base do cooler, macro | E7 | pads da base, etiqueta datamatrix, parafuso | ruim |
| gn-40 | [captura 18-13](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2018-13%20screenshot.png) | `cache/gn/gn-40.png` | PCB | frente, borda, close | E7 | fila de indutores marcados, CI quadrado, componente "85N", borda em degrau | boa (detalhe) |
| gn-41 | [captura 18-25](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2018-25%20screenshot.png) | `cache/gn/gn-41.png` | PCB | frente | E7, depois | limpeza da pasta do die; contorno do PCB com degrau | média |
| gn-42 | [captura 18-54](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2018-54%20screenshot.png) | `cache/gn/gn-42.png` | PCB | frente, close do package | E7, depois | die limpo com marcação legível em parte; substrato verde com componentes; indutores e conector de energia na borda | boa para texto |
| gn-43 | [gn-modmat-1000x489_1.jpg](https://gamersnexus.net/u/inline-images/gn-modmat-1000x489_1.jpg) | `cache/gn/gn-43.jpg` | outro | — | — | anúncio do tapete da GN | — |
| gn-44 | [captura 21-6](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2021-6%20screenshot.png) | `cache/gn/gn-44.png` | outro | PCB da **RTX 5090 Founders Edition** (outro vídeo da GN) | — | metal líquido sobre o die, pads; **não é esta placa** | não usar |
| gn-45 | [RTX 5090 Founders Edition vs. PRO 6000 _](https://gamersnexus.net/u/inline-images/RTX%205090%20Founders%20Edition%20vs.%20PRO%206000%20_%20GPU%20Thermals%20_%20Port%20Royal%204K%20_%20GamersNexus_all-4x_foolhardy_Remacri.png) | `cache/gn/gn-45.png` | gráfico | — | — | temperatura, 5090 FE contra PRO 6000 (Port Royal 4K) | — |
| gn-46 | [captura 22-28](https://gamersnexus.net/u/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%2022-28%20screenshot.png) | `cache/gn/gn-46.png` | placa montada | três quartos da face A, instalada na bancada | — | ventiladores girando (borrados), cabo saindo da borda superior, "NVIDIA" na lateral | média |
| gn-47 | [GN Hemi-Anechoic Chamber Testing _ NVIDI](https://gamersnexus.net/u/inline-images/GN%20Hemi-Anechoic%20Chamber%20Testing%20_%20NVIDIA%20GPUs%20At%20Load%20Speeds%20%28Frequency%20Spectrum%20%40%201M%29%20_%20GamersNexus-4x_foolhardy_Remacri.png) | `cache/gn/gn-47.png` | gráfico | — | — | espectro de ruído (câmara semianecoica), 5090 FE contra PRO 6000 | — |
| gn-48 | [GN GPU Benchmark _ Dragon's Dogma 2 (4K_](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Dragon%27s%20Dogma%202%20%284K_Max%29%20_%20GamersNexus-4x_foolhardy_Remacri_8.png) | `cache/gn/gn-48.png` | gráfico | — | — | Dragon's Dogma 2, 4K Max | — |
| gn-49 | [GN GPU Benchmark _ Dragon's Dogma 2 (144](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Dragon%27s%20Dogma%202%20%281440p_Max%29%20_%20GamersNexus-4x_foolhardy_Remacri_10.png) | `cache/gn/gn-49.png` | gráfico | — | — | Dragon's Dogma 2, 1440p Max | — |
| gn-50 | [GN GPU Benchmark _ Dragon's Dogma 2 (108](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Dragon%27s%20Dogma%202%20%281080p_Max%29%20_%20GamersNexus-4x_foolhardy_Remacri_10.png) | `cache/gn/gn-50.png` | gráfico | — | — | Dragon's Dogma 2, 1080p Max | — |
| gn-51 | [GN GPU Benchmark _ FFXIV Dawntrail (4K_M](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20FFXIV%20Dawntrail%20%284K_Maximum%29%20_%20GamersNexus-4x_foolhardy_Remacri_13.png) | `cache/gn/gn-51.png` | gráfico | — | — | FFXIV Dawntrail, 4K | — |
| gn-52 | [GN GPU Benchmark _ FFXIV Dawntrail (1440](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20FFXIV%20Dawntrail%20%281440p_Maximum%29%20_%20GamersNexus-4x_foolhardy_Remacri_10.png) | `cache/gn/gn-52.png` | gráfico | — | — | FFXIV Dawntrail, 1440p | — |
| gn-53 | [GN GPU Benchmark _ FFXIV Dawntrail (1080](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20FFXIV%20Dawntrail%20%281080p_Maximum%29%20_%20GamersNexus-4x_foolhardy_Remacri_6.png) | `cache/gn/gn-53.png` | gráfico | — | — | FFXIV Dawntrail, 1080p | — |
| gn-54 | [GN GPU Benchmark _ Starfield (4K_Ultra) ](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Starfield%20%284K_Ultra%29%20_%20GamersNexus-4x_foolhardy_Remacri_9.png) | `cache/gn/gn-54.png` | gráfico | — | — | Starfield, 4K Ultra | — |
| gn-55 | [GN GPU Benchmark _ Starfield (1440p_Ultr](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Starfield%20%281440p_Ultra%29%20_%20GamersNexus-4x_foolhardy_Remacri_10.png) | `cache/gn/gn-55.png` | gráfico | — | — | Starfield, 1440p Ultra | — |
| gn-56 | [GN GPU Benchmark _ Resident Evil 4 (4K_P](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Resident%20Evil%204%20%284K_Prioritize%20Graphics%29%20_%20GamersNexus-4x_foolhardy_Remacri_16.png) | `cache/gn/gn-56.png` | gráfico | — | — | Resident Evil 4, 4K | — |
| gn-57 | [GN GPU Benchmark _ Resident Evil 4 (1440](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Resident%20Evil%204%20%281440p_Prioritize%20Graphics%29%20_%20GamersNexus-4x_foolhardy_Remacri_16.png) | `cache/gn/gn-57.png` | gráfico | — | — | Resident Evil 4, 1440p | — |
| gn-58 | [GN GPU Benchmark _ Black Myth_ Wukong Be](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Black%20Myth_%20Wukong%20Benchmark%20%284K_High%29%20_%20GamersNexus-4x_foolhardy_Remacri_7.png) | `cache/gn/gn-58.png` | gráfico | — | — | Black Myth: Wukong, 4K High | — |
| gn-59 | [GN GPU Benchmark _ Black Myth_ Wukong Be](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Black%20Myth_%20Wukong%20Benchmark%20%281440p_High%29%20_%20GamersNexus-4x_foolhardy_Remacri_8.png) | `cache/gn/gn-59.png` | gráfico | — | — | Black Myth: Wukong, 1440p High | — |
| gn-60 | [GN GPU Benchmark _ Black Myth_ Wukong Be](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Black%20Myth_%20Wukong%20Benchmark%20%281080p_High%29%20_%20GamersNexus-4x_foolhardy_Remacri_9.png) | `cache/gn/gn-60.png` | gráfico | — | — | Black Myth: Wukong, 1080p High | — |
| gn-61 | [GN GPU Benchmark _ Dying Light 2 (4K_Hig](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Dying%20Light%202%20%284K_High-Custom%29%20_%20GamersNexus-4x_foolhardy_Remacri_7.png) | `cache/gn/gn-61.png` | gráfico | — | — | Dying Light 2, 4K | — |
| gn-62 | [GN GPU Benchmark _ Dying Light 2 (1440p_](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Dying%20Light%202%20%281440p_High-Custom%29%20_%20GamersNexus-4x_foolhardy_Remacri_11.png) | `cache/gn/gn-62.png` | gráfico | — | — | Dying Light 2, 1440p | — |
| gn-63 | [GN GPU Benchmark _ Cyberpunk 2077_ Phant](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Cyberpunk%202077_%20Phantom%20Liberty%20%284K_Ultra%29%20_%20GamersNexus-4x_foolhardy_Remacri_6.png) | `cache/gn/gn-63.png` | gráfico | — | — | Cyberpunk 2077, 4K Ultra | — |
| gn-64 | [GN GPU Benchmark _ Cyberpunk 2077_ Phant](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Cyberpunk%202077_%20Phantom%20Liberty%20%281440p_Ultra%29%20_%20GamersNexus-4x_foolhardy_Remacri_8.png) | `cache/gn/gn-64.png` | gráfico | — | — | Cyberpunk 2077, 1440p Ultra | — |
| gn-65 | [GN GPU Benchmark _ Cyberpunk 2077_ Phant](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Cyberpunk%202077_%20Phantom%20Liberty%20%281080p_Ultra%29%20_%20GamersNexus-4x_foolhardy_Remacri_6.png) | `cache/gn/gn-65.png` | gráfico | — | — | Cyberpunk 2077, 1080p Ultra | — |
| gn-66 | [GN GPU Benchmark _ Black Myth_ Wukong Be](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Black%20Myth_%20Wukong%20Benchmark%20%284K_High%20Raster_Medium%20RT_FSR%20Quality%29%20_%20GamersNexus-4x_foolhardy_Remacri_5.png) | `cache/gn/gn-66.png` | gráfico | — | — | Black Myth: Wukong, 4K com RT | — |
| gn-67 | [GN GPU Benchmark _ Black Myth_ Wukong Be](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Black%20Myth_%20Wukong%20Benchmark%20%281440p_High%20Raster_Medium%20RT_FSR%20Quality%29%20_%20GamersNexus-4x_foolhardy_Remacri_4.png) | `cache/gn/gn-67.png` | gráfico | — | — | Black Myth: Wukong, 1440p com RT | — |
| gn-68 | [GN GPU Benchmark _ Cyberpunk_ Phantom Li](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Cyberpunk_%20Phantom%20Liberty%20%284K_RT%20Medium%29%20_%20GamersNexus-4x_foolhardy_Remacri_5.png) | `cache/gn/gn-68.png` | gráfico | — | — | Cyberpunk, 4K RT Medium | — |
| gn-69 | [GN GPU Benchmark _ Cyberpunk_ Phantom Li](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Cyberpunk_%20Phantom%20Liberty%20%284K_RT%20Ultra%29%20_%20GamersNexus-4x_foolhardy_Remacri_3.png) | `cache/gn/gn-69.png` | gráfico | — | — | Cyberpunk, 4K RT Ultra | — |
| gn-70 | [GN GPU Benchmark _ Cyberpunk_ Phantom Li](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Cyberpunk_%20Phantom%20Liberty%20%281080p_RT%20Medium%29%20_%20GamersNexus-4x_foolhardy_Remacri_6.png) | `cache/gn/gn-70.png` | gráfico | — | — | Cyberpunk, 1080p RT Medium | — |
| gn-71 | [GN GPU Benchmark _ Dragon's Dogma 2 (4K_](https://gamersnexus.net/u/inline-images/GN%20GPU%20Benchmark%20_%20Dragon%27s%20Dogma%202%20%284K_Max%20RT%29%20_%20GamersNexus-4x_foolhardy_Remacri_7.png) | `cache/gn/gn-71.png` | gráfico | — | — | Dragon's Dogma 2, 4K Max RT | — |
| gn-72 | [LM Studio _ Text Generation (Small) _ EX](https://gamersnexus.net/u/inline-images/LM%20Studio%20_%20Text%20Generation%20%28Small%29%20_%20EXPERIMENTAL%20CHART%20_%20GamersNexus-4x_foolhardy_Remacri.png) | `cache/gn/gn-72.png` | gráfico | — | — | LM Studio, geração de texto (modelos pequenos) | — |
| gn-73 | [LM Studio _ Text Generation (Large) _ EX](https://gamersnexus.net/u/inline-images/LM%20Studio%20_%20Text%20Generation%20%28Large%29%20_%20EXPERIMENTAL%20CHART%20_%20GamersNexus-4x_foolhardy_Remacri.png) | `cache/gn/gn-73.png` | gráfico | — | — | LM Studio, geração de texto (modelos grandes) | — |
| gn-74 | [gn-patreon-1000x250 copy_0.png](https://gamersnexus.net/u/inline-images/gn-patreon-1000x250%20copy_0.png) | `cache/gn/gn-74.png` | outro | — | — | anúncio do Patreon da GN | — |
| gn-75 | [gpu-header.png](https://gamersnexus.net/u/inline-images/gpu-header.png) | `cache/gn/gn-75.png` | outro | — | — | cabeçalho do site com outras placas (EVGA etc.) | — |
| nv-01 | [nvidia-geforce-rtx-pro-6000-og-1200x63](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-geforce-rtx-pro-6000-og-1200x630.jpg) | `cache/nvidia/nv-01.jpg` | placa montada (render oficial) | três quartos da face B, com a borda superior | — | face B com "RTX PRO 6000" no X; borda superior com duas fendas e o encaixe do conector na ponta do painel; logotipo NVIDIA claro (tom champanhe) na lateral | média para forma, ruim para medir |
| nv-02 | [nvidia-geforce-rtx-pro-6000-bm-l580-d@](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-geforce-rtx-pro-6000-bm-l580-d@2x.jpg) | `cache/nvidia/nv-02.jpg` | placa montada (render oficial) | igual a nv-01, placa pequena num banner largo | — | mesmo render | ruim |
| nv-03 | [nvidia-geforce-rtx-pro-6000-bm-uf1080-](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-geforce-rtx-pro-6000-bm-uf1080-p@2x.jpg) | `cache/nvidia/nv-03.jpg` | placa montada (render oficial) | igual a nv-01, formato vertical | — | mesmo render | ruim |
| nv-04 | [nvidia-geforce-rtx-pro-6000-bm-l440-t@](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-geforce-rtx-pro-6000-bm-l440-t@2x.jpg) | `cache/nvidia/nv-04.jpg` | placa montada (render oficial) | igual a nv-01 | — | mesmo render, enquadramento médio | ruim |
| nv-05 | [rtx-pro-6000-family-bm-md460-offset-d@](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/rtx-pro-6000-family-bm-md460-offset-d@2x.jpg) | `cache/nvidia/nv-05.jpg` | outro | família RTX PRO (racks, servidor, estação) | — | a placa aparece muito pequena | não usar |
| nv-06 | [rtx-pro-6000-family-bm-af-bottom-p@2x.](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/rtx-pro-6000-family-bm-af-bottom-p@2x.jpg) | `cache/nvidia/nv-06.jpg` | outro | idem, recorte menor | — | a placa aparece pequena, em pé, ao lado de uma estação | não usar |
| nv-07 | [agentic-and-generative-ai-fg-i1of5-d.j](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/agentic-and-generative-ai-fg-i1of5-d.jpg) | `cache/nvidia/nv-07.jpg` | outro | — | — | imagem de aplicação (avatar de IA) | — |
| nv-08 | [nvidia-rtx-pro-6000-bw-fg-i2of6-d.jpg](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-rtx-pro-6000-bw-fg-i2of6-d.jpg) | `cache/nvidia/nv-08.jpg` | outro | — | — | mapa de dados | — |
| nv-09 | [nvidia-rtx-pro-6000-bw-fg-i3of6-d.jpg](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-rtx-pro-6000-bw-fg-i3of6-d.jpg) | `cache/nvidia/nv-09.jpg` | outro | — | — | captura de software (gêmeo digital) | — |
| nv-10 | [nvidia-rtx-pro-6000-bw-fg-i4of6-d.jpg](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-rtx-pro-6000-bw-fg-i4of6-d.jpg) | `cache/nvidia/nv-10.jpg` | outro | — | — | render de arquitetura | — |
| nv-11 | [nvidia-rtx-pro-6000-bw-fg-i5of6-d.jpg](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-rtx-pro-6000-bw-fg-i5of6-d.jpg) | `cache/nvidia/nv-11.jpg` | outro | — | — | software de edição de vídeo | — |
| nv-12 | [nvidia-rtx-pro-6000-bw-fg-i6of6-d.jpg](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/nvidia-rtx-pro-6000-bw-fg-i6of6-d.jpg) | `cache/nvidia/nv-12.jpg` | outro | — | — | render de arquitetura | — |
| nv-13 | [workstation-blackwell-rtx-pro-6000-wor](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf) | `cache/nvidia/nv-13.pdf` | outro (datasheet) | p. 1: render de nv-01, girado | — | capa = três quartos da face B com a borda superior. Páginas em `nv-13-p-1.png` a `nv-13-p-3.png` | ruim para medir |

## Tabela 2. Vistas necessárias (seção 6.1 do plano) × o que temos

| Vista necessária | Imagens que servem | Vista ortogonal? |
|---|---|---|
| três quartos da placa montada | face A: gn-02, gn-46. Face B: nv-01 a nv-04, nv-13 p. 1 (render), gn-08, gn-23 (sem bracket) | — |
| face dos ventiladores (face A) | gn-02, gn-46, gn-26 (parcial, sem o aro), gn-05 (foto da TechPowerUp, quase ortogonal), gn-12 (identidade incerta) | só gn-05, de terceiro. **Foto oficial ortogonal: falta** |
| face oposta (face B, a "traseira") | gn-03, gn-08, gn-09, gn-10, nv-01 | **falta** (gn-03 é quase frontal, mas distorcida) |
| topo com o conector (borda superior) | gn-13 (montada), gn-08 (parcial), nv-01 (render), gn-21 e gn-26 (sem o aro) | **falta** |
| bracket | gn-11, gn-15; sem o bracket: gn-16 | **falta** (gn-11 e gn-16 são oblíquas, mas boas para a disposição) |
| extremidade oposta ao bracket | — | **falta**: nenhuma imagem mostra essa ponta de frente |
| borda inferior (dedos PCIe) | gn-10 (parcial), gn-05 (de lado, terceiro) | **falta** |
| E1 (sai o bracket, ver "Contradições") | gn-14, gn-15, gn-16 | — |
| E2 (um parafuso, sai o aro) | gn-17, gn-18 | o parafuso não aparece |
| E3 (tampas centrais) | gn-19 (provável), gn-20, gn-21 | — |
| E4 (fixação e adaptador PCIe) | gn-22, gn-23, gn-24, gn-25 | gn-25 quase frontal (adaptador) |
| E5 (placa que cobre o PCB) | gn-26 (transição), gn-27, gn-28 | — |
| E6 (cabos flat e mola) | gn-29, gn-30, gn-31 | — |
| E7 (sai o PCB, pasta à vista) | gn-32 a gn-42 | — |
| PCB, frente (lado do GPU) | gn-32 (parcial), gn-33, gn-36, gn-37, gn-38, gn-40, gn-41, gn-42 | **falta** (nenhuma mostra a frente inteira sem pads) |
| PCB, verso | gn-28, gn-29, gn-30, gn-31 | **falta** (gn-29 é a mais próxima, oblíqua) |
| cooler aberto | só a base de contato: gn-32, gn-34, gn-35, gn-39 | **falta**: ventiladores, aletas por dentro, câmara de vapor |

## Observações por pergunta

Só o que se vê. "Não dá para ver" quer dizer que nenhuma das 75 + 13 imagens mostra aquilo.

**a. Ventiladores.**
- Os dois ficam na face A (gn-02, gn-46; gn-12 e gn-26 de perto).
- Contei **7 pás em cada ventilador** em recortes de gn-02 em resolução cheia, com contagem razoavelmente segura: as pás não se sobrepõem no ângulo da foto. Se for preciso margem, vale a faixa de 7 a 8. gn-05 (TechPowerUp) também mostra 7 pás em cada um.
- Os dois parecem iguais: mesmo diâmetro aparente, mesmo número de pás, mesmo sentido de curvatura das pás e cubo igual, de acabamento concêntrico (gn-02, gn-05).
- Em gn-46 os ventiladores estão girando e não dá para contar.
- Atrás das pás aparecem aletas verticais finas (gn-02).

**b. Face B (a oposta aos ventiladores).**
- Não é uma placa lisa. São duas grandes áreas de grade, com nervuras finas paralelas, uma em cada metade, separadas por um X central de superfície brilhante (gn-03, gn-08, gn-09, gn-10, nv-01).
- Através da grade de cima aparecem formas escuras e reflexos (gn-03). Isso sugere aberturas, mas não dá para ver o que há atrás.
- Texto: "RTX PRO 6000" em diagonal num dos triângulos do X (gn-08, gn-09, gn-03). Em gn-20 esse triângulo sai como peça separada (tampa central).
- O aro fino que contorna essa face é a "moldura" retirada em E2 (gn-17).

**c. Conector de energia.**
- Fica na borda superior, oposta aos dedos PCIe (gn-02, gn-08, gn-13, gn-46).
- Ao longo do comprimento, fica na seção central, deslocado para o lado oposto ao bracket: entre 55 % e 70 % do comprimento a partir do bracket em gn-02 e gn-46 (fotos em perspectiva, faixa larga).
- Na placa montada, o plugue encaixa na ponta de um painel preto brilhante, ao lado de duas fendas longas de ventilação (gn-13, nv-01).
- No PCB, o conector fica num canto da borda superior, onde o contorno faz um degrau (gn-29, gn-31).
- Pinos: em gn-30 veem-se **12 cavidades grandes (2 × 6)**. Contatos menores de sinal não aparecem nessa resolução.
- Ângulo: o encaixe aponta para fora da borda superior. Em gn-26 e gn-29 o corpo do conector parece girado em relação à borda, mas a perspectiva não deixa medir o ângulo. **Ângulo exato: não dá para ver.**
- Na outra ponta do cabo adaptador há plugues de 8 vias: 3 visíveis em gn-02, 3 ou 4 em gn-14.

**d. Bracket.**
- As 4 DisplayPort ficam em **uma fileira**, ao longo do comprimento do bracket, igualmente espaçadas (gn-11, gn-15, gn-16).
- O bracket **não tem grade nem aberturas de ventilação** visíveis: é chapa preta lisa com 4 parafusos, marcas regulatórias (CE, UKCA, FCC, UL e outras), uma etiqueta "PRO 6000 96GB", uma etiqueta de código de barras "002159" e uma etiqueta da NVIDIA (gn-11).
- A etiqueta da NVIDIA traz "900-5G144-2200-000", "Vbios: 98.02.52.00.02", "MODEL: PG144C", "NVIDIA CORP", "699-5G144-0520-800", "RTX PRO 6000", "SANTA CLARA", "MADE IN VIETNAM", "BLACKWELL" e um número de série (não transcrito).
- Sem o bracket aparece uma placa de extremidade preta, que segura as 4 portas, com um furo central e outro ao lado de um parafuso (gn-16).

**e. PCB principal.**
- Contorno: quase quadrado, com um degrau na borda superior junto ao conector de energia (gn-29, gn-40, gn-41).
- O PCB ocupa só a seção central, entre as duas carcaças de aletas dos ventiladores (gn-27, gn-29, gn-31).
- Proporção grosseira em gn-31 (oblíqua, **não é medida**): cerca de 0,28 a 0,33 do comprimento da placa e 0,75 a 0,85 da altura.
- GB202: perto do centro do PCB, talvez um pouco deslocado para o lado dos dedos PCIe (gn-29, estimativa visual).
- Verso, gn-29 com recortes em resolução cheia: **16 chips de memória**, contagem razoavelmente segura (faixa de 15 a 16). Ficam em U em volta do GPU:
  - 5 de cada lado (lados voltados para as duas carcaças de aletas);
  - 4 na borda superior (lado do conector de energia);
  - 2 na borda dos dedos PCIe, um de cada lado de dois conectores finos.
- Frente: **não dá para contar**. Pads contínuos cobrem as fileiras (gn-33, gn-36, gn-37, gn-42). Os pads desenham a mesma disposição em volta do GPU: dois pads com nervuras em cima, dois embaixo e faixas longas com 4 a 6 lóbulos em cada lateral.
- Posições vazias: no verso, nenhuma (gn-29). Na frente, não dá para ver.
- `pcb.plate` (gn-27) tem pads na mesma disposição do verso, com um furo quadrado no centro.

**f. Entrega de energia.**
- Indutores (blocos pretos altos com código impresso, como "85N", "H5B" ou "R…", leitura incerta) aparecem em fileira ao longo da borda superior, do lado do GPU oposto aos dedos PCIe, junto ao conector de energia (gn-33, gn-36, gn-42). Continuam em fileiras diagonais no canto em degrau (gn-38, gn-40).
- Contagem: **cerca de 10** na fileira de gn-33 e gn-42; **8 ou mais** em gn-40, com a fileira cortada pela borda da foto; cerca de 10 por fileira em gn-38.
- Essas fotos podem mostrar trechos sobrepostos da mesma borda. O total visível fica **entre 10 e 20, sem contagem total segura**: nenhuma imagem mostra a borda inteira.
- Há também um indutor menor, "4R7", junto ao GPU (gn-33, gn-38).
- Do lado do verso, a mesma borda tem duas filas de componentes retangulares (gn-29, gn-30). Não dá para identificar que componentes são.

**g. Placas de circuito e cabos flat.**
- Visíveis: **2 placas**. O PCB principal (gn-29, gn-33) e o adaptador PCIe (gn-24, gn-25), que se liga por um conector fino ("J3") ao PCB principal.
- As 4 DisplayPort ficam na extremidade, longe do PCB principal, que é central (gn-16, gn-23, gn-29). Mas **a placa que carrega as portas não aparece** em nenhuma imagem.
- Cabo flat: pelo menos um, marrom com reforço preto. Sai de um conector no PCB e entra no corpo do cooler, do lado de uma das carcaças (gn-28, gn-29, gn-31, gn-32).
- A outra ponta do cabo **não aparece**, então não dá para ver o que ele liga.
- Há ainda um conector de pinos dourados em duas fileiras na borda superior (gn-21, gn-26, gn-29, gn-30) e uma matriz de contatos no centro do X da face B (gn-20). A função de nenhum dos dois aparece.

**h. Interface térmica e package.**
- **Pasta cinza**, não metal líquido (gn-33, gn-35, gn-36, gn-41). A marca na base do cooler é mais densa no centro (gn-35).
- O die é uma superfície escura e espelhada, sobre um substrato verde com fileiras de componentes pequenos. Em volta há uma moldura quadrada bege ou bronze (gn-33, gn-42).
- Marcação lida em gn-42:
  - "NVIDIA";
  - linha 2, que parece "S TW 2508" (incerto);
  - "e1" num círculo;
  - linha 3 ilegível;
  - linha 4 "GB202-870-A1", com o 4.º e o 5.º caracteres incertos.

**i. Cooler.**
- Vê-se a **base de contato**: placa de tom acobreado com código datamatrix e pads com relevo (gn-32, gn-34, gn-35, gn-39).
- **Câmara de vapor: não dá para ver.** Nada mostra se a base é câmara de vapor. **Heatpipes: nenhum visível.**
- Pilhas de aletas visíveis:
  - 2 grandes, uma sob cada ventilador, dentro de carcaças arredondadas (gn-27, gn-29, gn-31);
  - uma fileira de aletas sob a borda superior do PCB, com pad branco por cima (gn-21, gn-26, gn-30, gn-34);
  - aletas na região central entre os ventiladores (gn-02, gn-26).
- Ou seja, **pelo menos 3 regiões de aletas**. Se as regiões centrais são ligadas às grandes, não dá para ver.
- A mola em X aparece sobre o verso do GPU com 4 parafusos (gn-29) e solta sobre o tapete (gn-31, gn-32).

**j. Parafusos por etapa (só o que aparece).**

| Etapa | O que se vê |
|---|---|
| E1, bracket | 4 parafusos pretos de cabeça em cruz (gn-11, gn-15) |
| Placa de extremidade, sob o bracket (não se vê se sai) | 4 parafusos com arruela clara nos cantos e 9 parafusos pequenos de cabeça em estrela (parece Torx) em volta das portas. Pode haver mais sob o dedo (gn-16) |
| E2 | o texto da GN fala em um parafuso; ele não aparece em foto |
| E3 | 4 parafusos claros na placa central (gn-20) |
| E4 | vários parafusos pretos em volta da fixação do adaptador (gn-18, gn-22). 6 parafusos sobre o tapete em gn-24, sem saber de quais etapas |
| E6 | 4 parafusos com arruela na mola em X (gn-29) |
| Total | o tapete acumula entre 15 e 20 parafusos em gn-31 e gn-32, contagem incerta |

**k. Cores e acabamentos.**
- Carcaça e aro: preto e cinza-grafite foscos (gn-02, gn-17).
- X central: preto brilhante na face B (gn-08, gn-09, gn-13). Na face A é cinza-escuro brilhante, com dois pedaços de fita azul e transparente que parecem película ou lacre, não acabamento (gn-02, gn-46).
- Grades e aletas: pretas.
- Pás: cinza-escuro fosco. Cubos: cinza com acabamento concêntrico, como metal torneado (gn-02).
- Bracket: preto, com marcas brancas.
- Painel da borda superior: preto brilhante (gn-13).
- "RTX PRO 6000": claro, prateado (gn-08, gn-09). Puxa para dourado em gn-15, talvez pela luz.
- Logotipo NVIDIA: na lateral, cinza claro nas fotos (gn-13, gn-27, gn-29) e champanhe ou dourado no render (nv-01).
- Cabo adaptador: preto trançado, com etiquetas brancas (gn-02, gn-14).

## Proporções medidas em foto

Das fotos da GN, nenhuma é quase ortogonal da placa inteira.

- **gn-03**, a mais frontal, dá razão comprimento/altura de cerca de 2,7 a 2,8, contra 2,22 no envelope oficial (304,8 / 137,2). A face está girada e a lente distorce, então **não serve para medir**.
- **nv-01** a **nv-04** são renders em três quartos e também não servem.

A única imagem quase ortogonal é a **foto da TechPowerUp capturada em gn-05**. Medi num recorte de resolução cheia: `cache/gn/gn-05.png`, região x 440 a 1940, y 600 a 1360. Ressalvas:

- **Procedência**: é imagem de um banco de dados de terceiro, mostrada no vídeo da GN. Não há como confirmar que a foto é desta placa, e não de outra igual por fora. No máximo `derived`, e precisa de decisão do grupo antes de entrar em `design/measurements.csv`.
- **Ortogonalidade**: os aros dos ventiladores medem 518 px na horizontal e 525 px na vertical, uma diferença de cerca de 1 %. A vista é quase frontal.
- **Escala**: assumi que os 304,8 mm (12,0") correspondem ao comprimento da carcaça, sem o bracket: 1382 px, de x ≈ 80 a x ≈ 1462 no recorte. Isso dá 0,2206 mm/px.
- **Conferência pela altura**: a carcaça mede 555 px (122 mm); com os dedos PCIe, 605 px (133 mm). Nenhuma das duas fecha com 137,2 mm, uma diferença de 3 % a 11 %. Não sei o que a cota de 5,4" inclui. Por isso declaro **±4 % de escala**, mais ±5 px de borda borrada (±1,1 mm) em cada medida.

| Medida | Valor | Tolerância | Origem e motivo |
|---|---|---|---|
| Diâmetro externo do aro do ventilador | 115 mm | ±6 mm | gn-05, média de 518 e 525 px nos dois ventiladores. ±4 % de escala mais a borda |
| Diâmetro do cubo | 40 mm | ±3 mm | gn-05, 180 px |
| Distância entre os centros dos cubos | 182 mm | ±8 mm | gn-05, 827 px |
| Centro do ventilador 1, a partir da ponta do bracket | 61 mm | ±4 mm | gn-05, 278 px desde a borda da carcaça |
| Centro do ventilador 2, a partir da ponta do bracket | 244 mm | ±10 mm | gn-05 |
| Cruzamento do X central | 152 mm | ±7 mm | gn-05. Fica no meio do comprimento |
| Altura da carcaça, sem os dedos | 122 mm | ±6 mm | gn-05, 555 px. **Conflita** com 137,2 mm, ver acima |
| Dedos PCIe: início e fim, a partir da ponta do bracket | 48 mm e 131 mm (comprimento ≈ 82 mm) | ±4 mm | gn-05, x ≈ 300 a 672 |
| Quanto os dedos descem abaixo da carcaça | 11 mm | ±2 mm | gn-05, cerca de 50 px |
| Largura do PCB central | **não medida** | — | nenhuma foto ortogonal do PCB. A estimativa grosseira de 0,28 a 0,33 do comprimento (gn-31, oblíqua) não é medida |

## O que não foi possível ver

- Vistas ortogonais oficiais de qualquer face. A NVIDIA só publica o render em três quartos da face B (nv-01 = capa do datasheet).
- A extremidade oposta ao bracket e a borda dos dedos PCIe de frente.
- A frente do PCB sem pads: quantos chips de memória há na frente, onde ficam e se há posições vazias.
- O total de indutores e qualquer coisa sobre as fases de energia.
- O ângulo exato do conector de energia e os contatos de sinal.
- A placa que carrega as DisplayPort, e se ela é separada.
- A outra ponta do cabo flat.
- O interior do cooler: no teardown, os ventiladores não são retirados, e não aparecem heatpipes, câmara de vapor nem as pilhas de aletas por dentro. Não há estágio E8 em foto.
- A espessura da placa (nenhuma vista de topo ortogonal).
- O parafuso de E2 e os tipos de cabeça de vários parafusos.
- Qual placa é a PRO 6000 em gn-12.
- O que fica atrás da grade da face B.

## Contradições e ajustes em relação a `harness/design/assembly-plan.md`

1. **E1 não mostra uma "placa traseira".** Nas fotos, a primeira peça a sair é o **bracket** (gn-14 a gn-16). O texto da GN diz "back plate" exatamente nesse ponto, o que sugere que a GN chamou o bracket de "back plate". Não há placa traseira lisa: a face B é grade com nervuras e um X de tampas (gn-03, gn-08, gn-20). `frame.backplate` e a coluna "Lacuna: aberturas" precisam ser revistos.
2. **E2: a "moldura externa" é um aro fino**, que contorna a face B (gn-17). Não é uma carcaça inteira.
3. **A capa do datasheet mostra a face B.** O arquivo de fontes deixava a face não identificada. As "duas áreas de grade fina" do render são a face oposta aos ventiladores, com o texto "RTX PRO 6000" e a borda superior com o conector.
4. **Refrigeração**: além das duas pilhas grandes (`cooler.fins.1`, `cooler.fins.2`), há aletas sob a borda superior do PCB e na região central (gn-21, gn-26, gn-30). Falta uma peça na árvore, ou as pilhas não são só duas.
5. **35 imagens**: o artigo tem 75 imagens no corpo, sendo 43 capturas de vídeo. Uma delas (gn-44) é da RTX 5090 FE, não desta placa.
6. Não é contradição, mas reforça e localiza: 16 chips no verso (gn-29), pasta cinza (gn-33), conector na borda superior, na seção central, deslocado para longe do bracket (gn-02, gn-46). O PCB principal é só a seção central, o que torna plausível uma placa separada para as saídas, mas ela continua não vista.
