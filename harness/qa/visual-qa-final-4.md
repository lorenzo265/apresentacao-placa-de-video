# Visual-QA final (quarta passada) da placa e do tour (2026-11-12)

- Autor: agente `visual-qa`, contexto separado de quem modelou. Só reportou; não editou nada.
- **Processo: esta passada rodou em Sonnet 5.5 (tipo C), por decisão do autor (limite de uso do Opus), e não no Opus que a regra do projeto pede para crítica visual.** Julgamentos finos de tom e beleza têm margem maior de erro.
- Objeto: `harness/dist/tour.html` (21,2 MB, aberto por file://), tema Keynote, `acumula=2` nos beats e `acumula=6` nas vistas livres, 1920 x 1080, deviceScaleFactor 1, Chromium sem opções (SwiftShader). Scripts em `harness/dist/qa/final-4/scripts/` (`beats.cjs`, `vistas.cjs`, `seq.cjs`, `probe.cjs`).
- Capturas: `harness/dist/qa/final-4/`. `b-<beat>.png` = os 28 beats do corte do seminário no `settle`; `v*` = vistas livres (`__frame3d`); `s-a2.1-*` e `s-a3.1-*` = quadros intermediários; `folha-a2.1.png`, `folha-a3.1.png`, `folha-diagramas-1/2.png`; `z-*` = recortes ampliados (sem clarear).
- Referências: `pny/front`, `pny/back` (já usadas na passada 3, não reabertas), nenhuma para interior do cooler, hero explodido e vitrine do chip (sem referência). Diagramas fora do escopo de forma.

## Veredito: aprovado com ressalvas, melhor que a passada 3

Nada bloqueia. Dos cinco achados de beleza, três estão resolvidos (close do chip, grades de frente, chips claros demais), um está parcial (explodida) e um parcial (geometria sob o cabeçalho). Restam: vista explodida ainda modesta e rasa, PCB que lê como metal cinza claro, marcação dos chips do a3.1 de cabeça para baixo, vitrine do chip ainda uma laje lisa.

## Lateralidade

**Não está espelhada.** Face A ortogonal (`v01-face-a-orto.png`): balcão do bracket à esquerda, ventiladores no mesmo sentido. Face B (`v02-face-b-orto.png`, vista por trás): contatos embaixo à direita do centro, bracket à direita, "RTX PRO 6000" no triângulo superior lendo girado, como em `pny/back`. a2.13 e `v11` mantêm bracket à esquerda e contatos na borda inferior, coerente com a face A. Só olhei a face B em duas vistas; não repeti a órbita completa.

## Os cinco achados da passada 3

| # | Estado | Números e evidência |
|---|---|---|
| 1 explodida pequena e escura (a2.13, a2.1) | **parcial** | a2.13: largura do conjunto de 1215 para 1350 px (+11%), altura de 805 para 753 px; luminância média do objeto de 98 para 109; pixels acima de 220 de 0,55% para 1,5%. Mais larga e mais clara, porém a diagonal quase rasante achata as camadas e os dois ventiladores quase de perfil encostam em y = 113, logo sob o cabeçalho (`b-a2.13.png`). O aro e os dois triângulos escuros da face B ainda são os elementos mais apagados e a chapa branca central ficou a peça mais brilhante. A vista `v11-explodida-E8-3qtr.png` (3/4 mais alto) é bem mais bonita que o enquadramento do beat. Em movimento (`folha-a2.1.png`, quadros 20 a 60%), o conjunto ocupa só cerca de um quarto da largura e fica colado ao topo, com muito vazio |
| 2 close do chip escuro (a2.1) | **resolvido** | luminância do quadro de 32 para 63; pixels abaixo de 20 de 50% para 7%; no recorte da placa, de 54% para 2%. PCB, chips de memória e pasta se leem (`b-a2.1.png`, `z-a2.1-chips-esq.png`). A linha de chamada termina no die, certo. Novo problema: ver achado 1 abaixo |
| 3 grades pretas de frente (face B) | **resolvido** | nervuras finas grafite agora leem de frente (`v02-face-b-orto.png`); aro grafite, não mais prateado. As duas marcas pequenas junto à grade esquerda continuam (nota) |
| 4 geometria sob o cabeçalho (a2.1, a3.1, a3.6) | **parcial** | faixa de fundo ajuda: "Placa > Chip > SM > Conceito" legível nos três. Mas no a2.1 ainda há geometria escura atravessando o topo (y 0 a 60, esquerda) e uma coluna preta que sobe até y = 150; no a3.1 as barras da carcaça cruzam a faixa em x 200 a 290; no a3.6 um grande bloco preto ocupa a metade superior (`b-a2.1.png`, `b-a3.1.png`, `b-a3.6.png`). Não atrapalha a leitura do texto |
| 5 chip da vitrine liso e chips claros demais (a3.1, a3.6) | **parcial** | chips do PCB agora epóxi cinza escuro com "GDDR7" e códigos (`z-a3.6-chips.png`); o selo "Ilustrativo: peça fora da posição" legível. A vitrine continua uma laje cinza uniforme (cerca de 60/255), sem substrato, esferas ou relevo, e a textura do texto está borrada (`z-a3.1-vitrine.png`). Os chips ainda são cinza médio, não escuros como em `gn-29`/`gn-30` |

## Achados novos e regressões

| # | Sev. | Beat | Descrição | Captura |
|---|---|---|---|---|
| 1 | ajusta | a2.1, a3.1, a3.6 | O ganho de luz lavou o PCB: a mascara de solda lê como alumínio cinza claro, com trilhas brancas, em vez de preto ou verde escuro (referências de PCB real são escuras). Chips e capacitores ficam como os elementos mais escuros, o inverso do real. Não é perda de detalhe, é tom | `z-a2.1-chips-esq.png`, `b-a3.1.png` |
| 2 | ajusta | a2.13 | Enquadramento quase rasante: o conjunto perde a leitura de empilhamento, ventiladores quase de perfil no topo, e a chapa branca central e os blocos de aletas competem. Falta altura de câmera | `b-a2.13.png`, `v11-explodida-E8-3qtr.png` |
| 3 | ajusta | a3.1 | Marcação "GDDR7" dos chips do PCB aparece com a linha de código acima do nome, ou seja girada cerca de 180 graus na tela, enquanto a vitrine no mesmo quadro está certa. Em a2.1 e a3.6 está na orientação certa | `z-a3.1-chips-pcb.png`, `z-a3.1-vitrine.png` |
| 4 | ajusta | a3.1 | A âncora (ponto verde) cai sobre o texto "XXXXXX" da vitrine, tapando parte da marcação | `z-a3.1-vitrine.png` |
| 5 | nota | a2.1 | O fim do close mostra uma placa grande cortada na borda inferior direita e outra esquerda, dois planos de metal sem leitura; composição menos limpa que a anterior, embora mais clara | `b-a2.1.png` |
| 6 | nota | a3.1 (em movimento) | Quadros a 0 e 25%: ventiladores colados ao topo, quase sob o cabeçalho; chapas claras quase brancas aparecem a 50% e brigam com a vitrine | `folha-a3.1.png` |
| 7 | nota | diagramas | Leve queda de luminância média de 1 a 2,5 pontos nos beats de diagrama (fundo e faixa), sem perda de legibilidade. Os problemas antigos seguem: rodapé ilustrativo corta "Chip completo" no a4.2 e a5.9, SM esmaecido e texto pequeno no t2.1 | `folha-diagramas-1.png`, `folha-diagramas-2.png` |
| 8 | nota | a0.1, a1.1, a7.5 | Praticamente idênticos à passada 3 (diferença média de pixels 1,3 a 1,4). a1.1: linha longa de cerca de 740 px até uma placa pequena, atravessa o vazio; continua só nota | `b-a1.1.png` |

## A marcação "GDDR7"

- **Chips do verso (face B aberta, `v10-b-aberta-E8.png`):** legível, texto na horizontal nos chips da coluna direita; parte dos chips (cima à esquerda) com texto vertical, aceitável para chips girados. Não verifiquei contra foto o sentido real.
- **PCB no a2.1:** legível e na orientação certa, cinza sobre epóxi preto, mas pequeno (cerca de 25 px de altura de letra).
- **PCB no a3.6:** orientação certa, contraste baixo (cinza sobre cinza), só legível ampliado.
- **PCB no a3.1:** orientação invertida (achado 3).
- **Vitrine no a3.1:** legível e grande, mas as linhas de código são borradas e a âncora cobre uma delas.
- Como a marcação é ilustrativa ("XXXX"), o selo ilustrativo do beat cobre.

## Sem regressão

Percorri os 28 beats (nenhum travou, a3.1 a 29 s por software). Caixa, selos, linha e texto legíveis em todos; nenhum selo sumiu; sem espelhamento; cores sem estouro, nenhum branco puro em tampas ou aro (a única mancha clara é a chapa metálica do a2.13 e a3.1). Diagramas a4.2, t2.1, a5.5, a5.9, t1.1, a5.16, a6.4, a7.4 vistos individualmente em folha; os demais só no cálculo de diferença (1,3 a 2,5 de média, ou seja, essencialmente iguais).

## O que não verifiquei

Fluidez, ritmo e sentido do giro da câmera ao vivo e em GPU (só `seek`); a viragem A para B em movimento; qualidade alta sem acumulação reduzida; texto linha a linha dos diagramas a5.2, a5.6 a a5.8, a5.10, a5.12 a a5.14, a6.1 a a6.3; beats fora do corte (a2.4, a2.9); a órbita A-B completa e o a2.9; comparação ponto a ponto com fotos de referência nesta passada (usei o que já estava registrado na passada 3 para lateralidade); as vistas `v10` e `v11` são minhas, em ortográfica com explosão E8, onde as camadas se sobrepõem por construção.
