# Proposta de engenharia da F2: partes não públicas da RTX PRO 6000 Blackwell Workstation Edition (v0.1)

- Data: 2026-11-10. Autor: `architecture-inferencer`, com a skill `gpu-assembly-proposal`.
- Estado: **aguardando gate humano**. Nada daqui entra em `assembly.json` nem em `measurements.csv` sem aprovação.
- Versão estruturada: `harness/design/proposal.json` (mesmos ids e números).
- Base: `spec/card.spec.json` e seus `gaps`, `design/assembly-plan.md` v0.3 (fila da seção 8), `spec/references/index.md` e as fotos em cache.

**Como ler.** "Vi" quer dizer que está na foto citada. "Deduzi" quer dizer raciocínio meu. Leitura de foto vale no máximo `derived` até o `visual-qa` conferir. As fotos foram abertas reduzidas a 2000 × 1125 (os originais têm 3840 × 2160) e sem ferramenta de recorte: texto pequeno e contagem fina têm leitura incerta.

**Nenhum nível de procedência foi promovido** sem foto ou fonte nova citada.

---

## 1. Decisões que dependem do humano

| # | Decisão | Recomendação |
|---|---|---|
| D1 | Memória: adotar 32 chips de 3 GB, 16 por face, em pares por controlador? | Sim, como `derived`. Os pads da frente desenham as mesmas 16 posições do verso. O mecanismo do par (16 bits por chip) fica `inferred`, com selo "provável" |
| D2 | Altura: tratar os 137,16 mm como medida da ponta dos contatos PCIe ao topo, e modelar a carcaça com 126 mm? | Sim. Segue a norma CEM e reduz o conflito de 15 mm para 4 mm. Muda o critério de aceite da seção 6.2 do plano: o envelope passa a incluir os contatos |
| D3 | A foto de terceiro dentro de gn-05 pode entrar em `measurements.csv`? | Sim, como `derived` com a ressalva de origem. gn-03, que é desta placa, aponta para a mesma altura de carcaça |
| D4 | Fases de energia: contagem representativa ou exata? | Representativa (nível C): 24 de núcleo e 4 de memória, com aviso na tela. O texto não cita o número como fato |
| D5 | Estágio E8: mostrar câmara de vapor com 10 heat pipes, derivados da 5090 FE? | Sim, com selo "derivado da placa irmã" e o lembrete da pasta térmica. A face de contato e as três regiões de aletas, vistas em foto, não levam esse selo |
| D6 | Modelar a placa das saídas de vídeo como terceira placa? | Sim, `derived`. O cabo flat largo vai para a ponta das portas. A forma é ilustrativa |
| D7 | O conector de pinos dourados da borda superior entra no modelo? | Entra como geometria, com o rótulo neutro "conector auxiliar". A função (sincronismo) só aparece se o grupo confirmar no guia do usuário |
| D8 | Dimensões do PCB: aceitar 108 × 112 mm com ±10 mm? | Usar para o bloqueio de volumes e pedir ao `visual-qa` uma medição em recortes de resolução cheia de gn-29 e gn-25 antes de travar |

## 2. Dúvidas abertas e contas que não fecham

| # | Tema | O que acontece | Estado |
|---|---|---|---|
| Q1 | Altura oficial | Com os contatos, a foto dá 133 mm (±4 %), contra 137,16 mm. Sobram 4 mm sem explicação | não fecha por 3 % |
| Q2 | Largura do PCB | Com o chip de memória como régua, dá 100 a 104 mm ou 115 a 120 mm, conforme o lado do chip que fica ao longo da borda | faixa larga |
| Q3 | Borda de energia do PCB | Com 112 mm de altura e package de 63 mm, sobram cerca de 10,5 mm para estágios e indutores | apertado |
| Q4 | Parafusos | Somam 19 sem as tampas centrais; o tapete mostra de 15 a 20; a GN fala em parafusos "around the center" que não aparecem | não fecha se E3 tiver parafusos |
| Q5 | Ar nas aletas centrais | O PCB fecha a passagem para a face B. Não sei por onde nem em que sentido o ar passa | sem evidência |
| Q6 | Ventilador sobre o PCB | Cerca de 20 mm de cada disco de ventilador ficam sobre o PCB (15 % da área) | plausível, não verificado |
| Q7 | Contagem de fases | 24 vem de fileiras parciais e de um blog; a 5090 FE tem 27, 30 ou 34 conforme a fonte | conta de potência fecha; contagem não é verificável |
| Q8 | Folga do conector | 50 A contra 55 A da norma (10 %); 8,3 A por pino contra 9,5 A (14 %) | fecha com folga pequena |
| Q9 | Térmica | Estimativa de 78 a 85 °C contra 82 °C medidos, com coeficiente de troca suposto | ordem de grandeza |
| Q10 | Textos lidos em foto | "MP29816-A", "85N", "4R7", "330" lidos em imagem reduzida | a reconferir |
| Q11 | Orientação do package | 56 mm ao longo do comprimento e 63 mm ao longo da altura é leitura minha | confiança 0,5 |
| Q12 | Sentido das pás | Não determinei o sentido de curvatura nem o de giro | a reconferir |

---

## 3. Tabela-resumo

| Item | Peça | Proposta (valor central e faixa) | Procedência | Conf. | Evidência |
|---|---|---|---|---|---|
| 1 | `cooler.vapor_chamber` | Câmara de vapor 3D sobre o chip; face de contato de 60 × 68 mm (54 a 70 × 60 a 76); 4 mm de espessura (3 a 6) | derived | 0,60 | vi a face de contato (gn-32, gn-34, gn-39); câmara vem da 5090 FE e da Jon Peddie |
| 1 | `cooler.heatpipes` | 10 tubos, 5 por lado (8 a 12), 8 mm | derived | 0,45 | só análogo (PCGH: "insgesamt zehn Heatpipes") |
| 1 | `cooler.fins.1`, `.2` | Placas empilhadas ao longo do comprimento; 98 × 118 × 22 mm; 60 aletas cada (48 a 75), representativo | derived | 0,50 | orientação vista (gn-02, gn-31); contagem não |
| 1 | `cooler.fins.3` | Pilha central em 3 degraus, 64 mm (55 a 75), sobre a câmara | derived | 0,50 | gn-26, gn-30, gn-34 |
| 1 | `cooler.heat_path` | die, pasta, câmara, tubos, três pilhas, ar da face A para a B | inferred | 0,50 | 82 °C a 1700 RPM (GN) |
| 2 | `pcb.main` | 108 × 112 mm (98 a 118 × 102 a 118); centrado em 152 mm do bracket; chanfro no canto do conector | derived | 0,45 | gn-29, gn-31, gn-40, gn-41 |
| 2 | `mem.topology` | 32 chips de 24 Gbit, 16 por face, 2 por controlador, 16 bits cada | derived (o mecanismo é inferred) | 0,75 | gn-29 e pads da frente |
| 2 | `mem.back.1..16` | 5 + 5 + 4 + 2 em volta do package; coordenadas com ±4 mm | derived | 0,60 | gn-29, gn-30 |
| 3 | `boards.topology` | 3 placas: principal, adaptador PCIe, saídas de vídeo | derived | 0,65 | duas vistas; a terceira deduzida |
| 3 | `pcie.adapter` | Em L, 100 × 35 mm, faixa de 16,5 mm, conector de 23 mm | derived | 0,65 | gn-25 |
| 3 | `io.board` | Placa estreita com 4 DisplayPort, passo de 19,5 mm | derived (forma illustrative) | 0,55 | gn-16 mostra só a placa de extremidade |
| 3 | `flex.dp` | Cabo flat de 22 mm de largura até a placa das saídas | derived | 0,55 | gn-29, gn-31, gn-32 |
| 3 | `flex.fan.1`, `.2` | Um cabo fino por ventilador | inferred | 0,35 | gn-30 (um conector pequeno) |
| 3 | `io.aux_header` | Conector de duas fileiras na borda superior, sob a tampa lisa do painel | derived (função inferred) | 0,50 | gn-13, gn-21, gn-30 |
| 4 | `power.vrm.gpu` | 24 fases (20 a 30) em duas fileiras nas bordas longas; controlador MPS | inferred | 0,35 | fileiras parciais em gn-33, gn-36, gn-38, gn-40, gn-42 |
| 4 | `power.vrm.mem` | 4 fases (3 a 8) | inferred | 0,30 | nenhuma |
| 4 | `power.split` | Cerca de 590 W pelo conector de 16 pinos, 10 W pelo slot (0 a 75) | inferred | 0,45 | conector de passo fino em gn-25 |
| 5 | `gpu.package` | Package de 56 × 63 mm; die de 24,2 × 31,0 mm; moldura de 11 mm, bege | derived | 0,55 | gn-33, gn-41, gn-42; vazamento sobre o GB202 |
| 6 | `fasteners.*` | E1: 4; E2: 1; E3: 0 (0 a 4); E4: 6; E5: 4; E6: 4; E7: 0. Total 19 (19 a 23). Torx T6 nos internos | derived | 0,50 | gn-11, gn-16, gn-20, gn-22, gn-24, gn-29 |
| 7 | `cooler.fan.*` | 7 pás em foice, cubo de 40 mm, rotor de 111 mm, 13 mm de profundidade | derived (ângulos illustrative) | 0,50 | gn-02, gn-05, gn-26 |
| 8 | `mem.front.1..16` | 16 posições atrás das 16 do verso, com chips de 3 GB | derived | 0,70 | pads em gn-33, gn-36, gn-37, gn-40, gn-42 |
| 9 | `card.thickness` | 40 mm (39 a 42) | derived | 0,65 | texto de terceiro em gn-05; 5090 FE |
| 9 | `card.height_reference` | 137,16 mm inclui os contatos; carcaça de 126 mm (122 a 129) | derived | 0,55 | gn-05, gn-03; norma CEM |

---

## 4. Detalhe por item

### Item 1. Interior do cooler

**O que vi.**
- A face de contato: placa plana de tom acobreado escuro, com a marca da pasta do tamanho do die e um código datamatrix (gn-32, gn-34, gn-35, gn-39).
- Em volta dela, uma moldura preta com colunas roscadas e pads: faixas sobre barras cinza nas laterais e um pad com nervuras junto à borda superior (gn-34, gn-39).
- Duas carcaças quase quadradas nas pontas. Atrás das pás há aletas finas verticais (gn-02). As aletas são placas empilhadas ao longo do comprimento da placa.
- Uma pilha central em três degraus entre os ventiladores, que continua sob a borda superior do PCB (gn-26, gn-30, gn-34). Um pad branco liga essa pilha aos componentes da borda.
- A face B de cada ponta é uma grade de nervuras que faz parte da carcaça. As nervuras continuam na lateral arredondada (gn-16, gn-29).

**O que não vi.** O interior da câmara, qualquer heat pipe, a ligação entre as pilhas, os ventiladores fora do lugar.

**Proposta.**
- `cooler.vapor_chamber` (`derived`, 0,60). Câmara de vapor 3D com corpo plano sobre o chip. Face de contato de 60 × 68 mm, medida em gn-34 com a marca da pasta como régua. Espessura de 4 mm (3 a 6), sem evidência.
- `cooler.heatpipes` (`derived`, 0,45). Dez tubos, cinco para cada ponta, de 8 mm, ao longo do comprimento. Como as aletas são empilhadas nessa direção, os tubos atravessam todas: a geometria da foto é compatível com o análogo.
- `cooler.fins.1` e `.2` (`derived`, 0,50). Cada pilha com cerca de 98 × 118 × 22 mm. Sessenta aletas com passo de 1,6 mm é prática de mercado: não contei em foto. Nível C para a contagem.
- `cooler.fins.3` (`derived`, 0,50). Pilha separada, sobre a câmara, do lado da face A. Também recebe calor dos indutores da borda.
- `cooler.heat_path` (`inferred`, 0,50). Die, pasta, face de contato, vapor na câmara e nos tubos, aletas, ar. O ar entra pela face A e sai pela face B nas pontas.

**Análogo.** RTX 5090 Founders Edition: "3D Vapor Chamber with integrated heat pipes" (NVIDIA), "insgesamt zehn Heatpipes" (PCGH, 2026-11-10), "five double-length heatpipes" (TechPowerUp, só resumo de busca). Para esta placa, a Jon Peddie fala em "bilateral 3D vapor chambers", sem abrir a placa.

**Alternativas.** Bloco maciço com tubos soldados; duas câmaras separadas; pilha única de ponta a ponta com rebaixo no centro.

**Verificações.**
- Térmica: vazão necessária de 44 CFM para 600 W com 25 K de aquecimento do ar. Área de aletas de 0,55 m². Com coeficiente de troca suposto de 50 W/m²K, a estimativa do núcleo fica entre 78 e 85 °C. A GN mediu 82 °C a 1700 RPM nesta placa e 72 °C a cerca de 1570 RPM na 5090 FE (569 W, metal líquido). Fecha em ordem de grandeza (Q9).
- Geometria: cabe nos 40 mm (ver item 9).
- Montagem: a mola em X puxa o PCB contra a face de contato com 4 parafusos.

**Aviso para a tela.** "Estrutura provável, derivada da RTX 5090 Founders Edition: nenhuma foto desta placa mostra o cooler por dentro. Só a face de contato e as aletas por fora foram vistas."

### Item 2. PCB principal e a pergunta de memória

**O que vi.**
- PCB quase quadrado entre as duas carcaças; as bordas laterais avançam um pouco sobre elas (gn-29, gn-31).
- Chanfro e entalhe no canto do conector de energia, na borda superior, do lado oposto ao bracket (gn-29, gn-30).
- Um rebaixo raso na borda dos contatos PCIe, com um controlador e uma fileira de indutores (gn-38, gn-40, gn-41).
- Quatro furos grandes nos cantos do package (gn-33, gn-40).
- No verso: 16 chips, 5 + 5 nas laterais, 4 na borda de energia, 2 na borda dos contatos. Nenhuma posição vazia (gn-29).
- Na frente: pads com a mesma disposição (ver item 8).

**Proposta para `pcb.main`** (`derived`, 0,45).
- 108 × 112 mm, faixa de 98 a 118 por 102 a 118. Espessura de 1,6 mm (`inferred`).
- Centro a 152 mm da ponta do bracket (os ventiladores são simétricos e o X cruza nesse ponto). Em x, de 98 a 206 mm.
- GB202 no centro do PCB, com ±5 mm.
- Conector de 16 pinos no canto da borda superior, a cerca de 195 mm do bracket (185 a 205), girado no plano cerca de 40° (20 a 60, confiança 0,3).
- Conector auxiliar na mesma borda, no canto do lado do bracket.

**De onde vêm os números.** Duas réguas em gn-29: o chip GDDR7 (12 × 14 mm) e o conector de placa a placa, que mede 23 mm no adaptador (gn-25). A foto é oblíqua. As duas leituras possíveis dão 100 ou 117 mm de largura (Q2). O valor central fica entre elas.

**Proposta para a memória, `mem.topology`** (`derived`, 0,75; o mecanismo do par é `inferred`, 0,5).
- 32 chips de 24 Gbit (3 GB), 16 por face.
- Cada chip da frente fica atrás de um do verso. O par divide um controlador de 32 bits, 16 bits por chip.

**Por que não 24 chips de 4 GB.** A capacidade fecharia, mas 8 controladores teriam dois chips e 8 teriam um, e os pads da frente cobrem 16 posições, não 8.

**Verificações.**
- Memória: 32 × 3 GB = 96 GB. 32 × 16 bits = 512 bits. 32 ÷ 16 = 2 por controlador. Fecha.
- Geometria: 98 + 108 + 98 = 304 mm. A altura cabe em 126 mm de carcaça. A borda de energia fica apertada (Q3).
- Montagem: o PCB sai por último, preso só pela mola e pelos conectores.

**Coordenadas propostas** (referencial do PCB, u a partir da borda do lado do bracket, v a partir da borda dos contatos, ±4 mm):

| Grupo | Chips | Centros (u, v) em mm |
|---|---|---|
| lateral do lado do bracket | 5 | (18, 26), (18, 41), (18, 56), (18, 71), (18, 86) |
| lateral oposta | 5 | (90, 26), (90, 41), (90, 56), (90, 71), (90, 86) |
| borda de energia | 4 | (31,5; 95,5), (46,5; 95,5), (61,5; 95,5), (76,5; 95,5) |
| borda dos contatos | 2 | (38; 16,5), (70; 16,5) |

São um arranjo regular compatível com a foto, não uma medição.

**Aviso para a tela.** "Ocupação provável: 32 chips de 3 GB, dois por controlador. A marcação dos chips não foi lida."

### Item 3. Quantas placas e o que os cabos ligam

**O que vi.**
- Duas placas: a principal e o adaptador PCIe, que encaixa por um conector de placa a placa com a serigrafia "J3" (gn-24, gn-25).
- Um cabo flat marrom, largo, que sai do canto do PCB do lado do bracket e entra na carcaça dessa ponta (gn-29, gn-31, gn-32, gn-34).
- Um conector pequeno de cabo plano no verso, junto ao mesmo canto (gn-30).
- Um conector preto de pinos dourados em duas fileiras na borda superior, no canto do lado do bracket (gn-21, gn-26, gn-30). No painel montado há um retângulo liso acima dessa posição (gn-13).

**Proposta.**
- `boards.topology` (`derived`, 0,65): três placas.
- `pcie.adapter` (`derived`, 0,65): em L, 100 mm de comprimento, 35 mm de altura total, faixa de 16,5 mm. Quatro furos em volta do conector e dois na faixa.
- `io.board` (`derived`, 0,55; forma `illustrative`): placa estreita atrás da placa de extremidade, com as 4 portas em fileira.
- `flex.dp` (`derived`, 0,55): o cabo largo leva os sinais de vídeo até `io.board`.
- `flex.fan.1` e `.2` (`inferred`, 0,35): um cabo fino por ventilador.
- `io.aux_header` (existência `derived`, 0,8; função `inferred`, 0,3): conector auxiliar sob a tampa lisa. Função provável: ligação com a placa RTX PRO Sync.

**Análogo.** 5090 FE: "unique 3-piece PCB" (NVIDIA); placa de E/S "connected via a flex cable to the main PCB" (GN, 2026-11-10).

**Alternativas.** Quatro placas, com uma só para os ventiladores; ventiladores no mesmo cabo das saídas.

**Verificações.** Montagem: os cabos soltam em E6, antes do PCB. Geometria: o conector do adaptador cai a cerca de 27 mm da borda do PCB, onde gn-29 mostra um conector fino.

**Achado.** A "matriz de contatos no centro do X" do catálogo são os capacitores do verso do chip, vistos pelo furo quadrado da placa que cobre o PCB (gn-20, gn-27, gn-29).

**Aviso para a tela.** "Três placas: duas vistas em foto e uma, a das saídas de vídeo, deduzida."

### Item 4. Fases de energia e conta de potência

**O que vi.**
- Cerca de 10 indutores em fileira numa borda, com uma fileira de estágios de potência atrás (gn-33).
- De 6 a 8 indutores na borda do conector de energia, entre o conector auxiliar e o de 16 pinos (gn-36, gn-42).
- Mais indutores numa lateral (gn-38).
- Um CI quadrado junto à borda dos contatos, com marcação que li como "MPS ... MP29816-A" (gn-40). Leitura incerta.
- Indutores menores marcados "4R7" e "330", de conversores auxiliares.
- No verso, duas filas de componentes retangulares na borda de energia (gn-29, gn-30).

No total, vi de 18 a 20 indutores do tipo principal, sem ver nenhuma borda inteira.

**Proposta.**
- `power.vrm.gpu` (`inferred`, 0,35): 24 fases (20 a 30) para os trilhos de núcleo. Cerca de 12 na borda dos contatos, 8 na borda de energia e 4 numa lateral ou no verso. Estágios integrados de 50 A (suposto). Um ou dois controladores.
- `power.vrm.mem` (`inferred`, 0,30): 4 fases (3 a 8) de 30 A.
- `power.split` (`inferred`, 0,45): cerca de 590 W pelo conector de 16 pinos e 10 W pelo slot.

**Conta de potência.**

| Passo | Valor |
|---|---|
| Potência total (datasheet) | 600 W |
| Ventiladores e miúdos (suposto) | 25 W |
| Memória: 32 chips × 2,2 W (suposto), mais perdas | 78 W na entrada |
| Núcleo, na entrada do conversor | 497 W |
| Núcleo, na saída (rendimento de 91 %, suposto) | 452 W |
| Corrente a 0,9 V | cerca de 500 A (430 a 535) |
| Capacidade: 24 × 50 A | 1200 A, folga de 2,4 vezes |
| Memória: 70 W a 1,2 V | 59 A contra 120 A (4 × 30 A) |
| Conector: 600 W ÷ 12 V | 50 A contra 55 A da norma |

**Análogo.** 5090 FE: 30 fases (wccftech), 34 com 4 no verso (PCGH; Tom's por resumo), 19 + 8 (TechPowerUp, só resumo). Blog sabareesh sobre esta placa: um indutor "identical to the 23 still on the board".

**Alternativas.** 20 fases só na frente; 30 fases; 16 + 8 em dois trilhos (combina com os limites do controlador, mas é coincidência numérica).

**Verificações.** Energia: fecha com folga nos conversores e com folga pequena no conector (Q8). Geometria: apertada (Q3). Térmica: pads sobre os estágios e pad dos indutores para a pilha central.

**Aviso para a tela.** "Estrutura provável: a NVIDIA não publica o número de fases. A quantidade no modelo é representativa."

### Item 5. Package do GB202

**O que vi.**
- Die escuro e espelhado, mais comprido na direção da altura do cartão (gn-42).
- Substrato verde à vista em volta do die, com componentes pequenos.
- Moldura larga, bege ou bronze, quase quadrada (gn-33, gn-42).
- Marcação: "NVIDIA", "S TW 2508", "e1", "GB202-870-A1", parcialmente legível (gn-42).

**Proposta** (`derived`, 0,55).
- Die: 24,2 × 31,0 mm. Vem de 750 mm² (oficial) e da proporção de 1 para 1,28 em duas fotos.
- Package: 56 × 63 mm (54 a 60 por 60 a 66), com os 63 mm ao longo da altura.
- Janela de substrato: 34 × 40 mm. Moldura de 11 mm de largura.
- Topo do die a 2,9 mm do PCB (`inferred`).

**Análogo.** Vazamento de 2024 sobre o GB202: die de 24 × 31 mm e package de 63 × 56 mm (só resumo de busca). Em gn-41, a moldura mede 2,4 vezes a largura do die, ou seja, 57 mm: bate com o lado de 56 mm.

**Alternativas.** Package de 64 × 59 mm (outra medida em foto); package girado.

**Verificações.** Geometria: 24,2 × 31,0 = 750 mm². Montagem: 4 furos da mola nos cantos.

**Aviso para a tela.** "Dimensões do encapsulamento estimadas por proporção em foto e por um vazamento sobre o mesmo chip."

### Item 6. Parafusos por estágio

| Estágio | Peça | Qtd. | Cabeça | Procedência | Evidência |
|---|---|---|---|---|---|
| E1 | bracket | 4 | cruz | derived (foto) | gn-11, gn-15 |
| não sai | placa de extremidade | 13 a 15 | estrela | derived (foto) | gn-16: 4 com arruela clara e 9 a 10 pequenos |
| E2 | aro | 1 | não vista | confirmed (texto); posição inferred | GN; candidato em gn-16, ao lado de um canto |
| E3 | tampas centrais | 0 (0 a 4) | não vista | inferred | a GN fala em "some screws around the center" |
| E4 | fixação e adaptador PCIe | 6 | Torx (suposto) | derived (foto) | gn-22, gn-24, gn-25 |
| E5 | placa que cobre o PCB | 4 | Torx (suposto) | derived (foto) | gn-20, gn-22, gn-24 |
| E6 | mola em X | 4 | Torx (suposto) | derived (foto) | gn-29 |
| E7 | PCB | 0 | — | derived (sequência da GN) | sai depois dos cabos e da mola |

**Correção ao plano.** Os 4 parafusos claros da placa central prendem a placa que cobre o PCB (E5). Em gn-20 a tampa central sobe com eles ainda no lugar.

**Total de E1 a E7:** 19 (19 a 23). O tapete mostra de 15 a 20 (Q4).

**Tipo de cabeça interno:** Torx T6 (T5 a T8), confiança 0,4. Vem de um resumo sobre a 5090 FE e de uma tampa de chave com símbolo de estrela em gn-28.

**Aviso para a tela.** "Quantidades contadas em fotos por etapa. O tipo de cabeça não foi confirmado."

### Item 7. Ventiladores: forma da pá

**O que vi.** Sete pás largas, curvadas em foice, que quase se tocam vistas de frente. Cubo com tampa de acabamento concêntrico. Os dois iguais (gn-02, gn-05, gn-26).

**Proposta** (`derived`, 0,50; ângulos `illustrative`).
- 7 pás; cubo de 40 mm; rotor de 111 mm dentro do aro de 115 mm.
- Varredura de 45° entre a raiz e a ponta (30 a 60). Pás cobrindo 85 % do anel visto de frente.
- Passo de 35° na raiz e 20° na ponta; profundidade axial de 13 mm. Sem vista lateral, são ilustrativos.
- Anel unindo as pontas das pás: provável, confiança 0,5.
- Ar da face A para a face B. 1700 RPM em carga (GN).

**Não determinado.** O sentido de curvatura e de giro (Q12).

**Aviso para a tela.** "Forma da pá aproximada a partir de fotos de frente. Ângulo e espessura são ilustrativos."

### Item 8. As 16 posições de memória da frente

**O que vi** (nunca os chips, só os pads):
- Uma faixa com 5 lóbulos numa lateral (gn-33) e uma faixa longa com lóbulos na outra (gn-37).
- Dois pads com nervuras, cada um do tamanho de dois chips, entre o package e os indutores da borda de energia (gn-36, gn-42).
- Dois pads arredondados, do tamanho de um chip, na borda dos contatos, com um indutor "4R7" no meio (gn-33, gn-40).

A contagem por lado (5, 5, 4, 2) repete a do verso.

**Proposta** (`derived`, 0,70). As 16 posições ficam atrás das 16 do verso, nas mesmas coordenadas do item 2, e contêm chips de 24 Gbit. O calor sai por pads para a moldura da base do cooler.

**Alternativa.** Oito posições ocupadas e oito vazias sob pads contínuos (hipótese dos 24 chips de 4 GB). Um pad sobre posição vazia não teria função.

**Aviso para a tela.** "As 16 posições da frente só foram vistas cobertas por pads térmicos. Chips e posições são dedução."

### Item 9. Espessura e a cota de 5,4"

**Espessura** (`derived`, 0,65): 40 mm (39 a 42).
- A página de terceiro capturada em gn-05 diz "304 mm x 137 mm x 40 mm" para esta placa.
- A 5090 FE tem 42 mm segundo a Puget e 40 mm segundo a Tom's Hardware (resumo de busca).
- O passo de dois slots é 40,64 mm.

Orçamento de camadas (não é medida):

| No centro, a partir da face B | mm | Nas pontas, a partir da face A | mm |
|---|---|---|---|
| tampas centrais | 2,5 | ventilador e aro | 15 |
| placa que cobre o PCB | 1,5 | pilha de aletas | 22 |
| pad e memória do verso | 2,1 | grade da face B | 3 |
| PCB | 1,6 | | |
| package e pasta | 3,0 | | |
| câmara de vapor | 4,0 | | |
| aletas centrais e tampa da face A | 25,3 | | |
| **soma** | **40,0** | **soma** | **40** |

**Altura** (`derived`, 0,55).
- A norma CEM mede a altura "from the bottom of the edge finger to the top of the card".
- Em gn-05, a carcaça tem 122 mm, e os contatos descem 11 mm abaixo dela: 133 mm no total.
- Em gn-03, que é desta placa, a razão comprimento por altura dá carcaça de 118 a 122 mm.
- **Proposta:** os 137,16 mm incluem os contatos e não incluem o bracket. A carcaça tem 126 mm (122 a 129).
- Sobram 4 mm entre os 133 medidos e os 137,16 oficiais, dentro dos ±4 % da foto (Q1).

**Alternativas.** A cota incluir o bracket (não fecha: o bracket padrão tem 120 mm); a carcaça ter mesmo 137 mm (contradito por gn-03); o número ser herdado da ficha da 5090 FE.

**Aviso para a tela.** "A altura oficial de 137 mm parece incluir os contatos dourados. A carcaça, medida em foto, tem cerca de 126 mm."

---

## 5. Linhas sugeridas para `design/measurements.csv`

Não editei o CSV. Estado sugerido para todas: "proposta F2, aguardando gate humano".

```csv
feature,value_mm,tolerance_mm,method,source,provenance,status
card_thickness,40,2,texto de terceiro legível em gn-05; 5090 FE com 42 mm (Puget),proposal.json: card.thickness,derived,proposta F2
shroud_height_proposed,126,4,137.16 menos 11 mm de contatos; hipótese de que a cota oficial inclui os contatos,proposal.json: card.height_reference,derived,proposta F2
pcie_fingers_below_shroud,11,2,proporção em foto (gn-05),references/index.md: Proporções medidas em foto,derived,proposta F2
pcb_main_width,108,10,proporção em foto oblíqua (gn-29); chip GDDR7 e conector J3 como réguas,proposal.json: pcb.main,derived,proposta F2
pcb_main_height,112,8,proporção em foto oblíqua (gn-29) e orçamento de componentes,proposal.json: pcb.main,derived,proposta F2
pcb_main_center_from_bracket_end,152,6,simetria dos ventiladores e cruzamento do X (gn-05),proposal.json: pcb.main,derived,proposta F2
pcb_main_thickness,1.6,0.4,referência da norma; sem medida,proposal.json: pcb.main,inferred,proposta F2
power_connector_center_from_bracket_end,195,10,canto do PCB (gn-29) e faixa de 55 a 70 % do comprimento,proposal.json: pcb.main,derived,proposta F2
gb202_package_x,56,3,vazamento sobre o GB202 conferido por proporção em gn-41,proposal.json: gpu.package,derived,proposta F2
gb202_package_y,63,3,vazamento sobre o GB202; sem conferência em foto,proposal.json: gpu.package,derived,proposta F2
gb202_die_x,24.2,1.3,750 mm2 com proporção de 1 para 1.28 (gn-05; gn-42),proposal.json: gpu.package,derived,proposta F2
gb202_die_y,31.0,1.5,750 mm2 com proporção de 1 para 1.28 (gn-05; gn-42),proposal.json: gpu.package,derived,proposta F2
gb202_stiffener_ring_width,11,2,(56 - 34) / 2; janela por proporção em foto,proposal.json: gpu.package,derived,proposta F2
gb202_die_top_above_pcb,2.9,0.6,prática de mercado,proposal.json: gpu.package,inferred,proposta F2
pcie_adapter_length,100,8,proporção em foto (gn-25); zona de contatos de 84.3 mm como régua,proposal.json: pcie.adapter,derived,proposta F2
pcie_adapter_strip_height,16.5,2,proporção em foto (gn-25),proposal.json: pcie.adapter,derived,proposta F2
pcie_adapter_total_height,35,3,proporção em foto (gn-25),proposal.json: pcie.adapter,derived,proposta F2
pcie_adapter_connector_length,23,2,proporção em foto (gn-25),proposal.json: pcie.adapter,derived,proposta F2
vapor_chamber_contact_plate_x,60,8,proporção em foto (gn-34); marca da pasta como régua,proposal.json: cooler.vapor_chamber,derived,proposta F2
vapor_chamber_contact_plate_y,68,8,proporção em foto (gn-34),proposal.json: cooler.vapor_chamber,derived,proposta F2
vapor_chamber_thickness,4,1.5,prática de mercado,proposal.json: cooler.vapor_chamber,inferred,proposta F2
heatpipe_diameter,8,2,prática de mercado,proposal.json: cooler.heatpipes,inferred,proposta F2
fin_stack_end_length_x,98,8,(304.8 - largura do PCB) / 2,proposal.json: cooler.fins.1_2,derived,proposta F2
fin_stack_end_depth_z,22,4,orçamento de espessura,proposal.json: cooler.fins.1_2,inferred,proposta F2
fin_pitch,1.6,0.4,prática de mercado; não contado em foto,proposal.json: cooler.fins.1_2,inferred,proposta F2
fin_stack_center_length_x,64,10,proporção em foto (gn-34),proposal.json: cooler.fins.3,derived,proposta F2
fan_rotor_diameter,111,4,aro de 115 mm menos folga,proposal.json: cooler.fan.blade,inferred,proposta F2
fan_axial_depth,13,3,orçamento de espessura,proposal.json: cooler.fan.blade,inferred,proposta F2
dp_port_pitch,19.5,2,proporção em foto (gn-16); receptáculo de 16.1 mm como régua,proposal.json: io.board,derived,proposta F2
flex_dp_width,22,4,proporção em foto (gn-29),proposal.json: flex.dp,derived,proposta F2
vrm_inductor_side,6.5,1.5,proporção em foto (gn-40) e prática de mercado,proposal.json: power.vrm.gpu,inferred,proposta F2
```

As coordenadas dos 32 chips de memória estão em `proposal.json` (`mem.back.1..16`), no referencial do PCB.

---

## 6. O que mudaria na árvore de peças (seção 2 do plano)

| id | Mudança | Detalhe |
|---|---|---|
| `cooler.heatpipes` | acrescentar | 10 tubos, `derived` da 5090 FE, fidelidade B, estágio E8 |
| `cooler.base` | redefinir | face de contato da câmara mais moldura preta com pads e colunas |
| `cooler.fins.3` | manter separada | pilha central em três degraus |
| `io.aux_header` | acrescentar | conector de pinos dourados sob a tampa lisa do painel |
| `flex.*` | desdobrar | `flex.dp`, `flex.fan.1`, `flex.fan.2` |
| `pcb.plate` | completar | dissipador da memória do verso; 4 parafusos claros; furo quadrado |
| `pcb.back_frame` | acrescentar | chapa preta de apoio da mola, que fica no PCB (gn-30) |
| `cooler.leaf_spring` | completar | mola metálica em X, com janela e 4 braços |
| `frame.center_covers` | completar | 2 tampas triangulares na face B (gn-27) |
| `frame.face_b` | ajustar | as grades fazem parte das carcaças das pontas |
| `fasteners.*` | corrigir | os 4 parafusos claros são de E5; E4 tem 6 |
| `mem.front.1..16` | completar | posições espelhadas às do verso |
| `power.inductors` | completar | duas fileiras, uma em cada borda longa |
| `power.controller` | acrescentar | controlador MPS junto à borda dos contatos; leitura a reconferir |
| `power.aux` | acrescentar | conversores auxiliares ("4R7", "330"), fidelidade C |
| `card` | ajustar | espessura de 40 mm; a altura de 137,16 mm inclui os contatos (D2) |
| E8 | manter `inferred` | nenhuma evidência nova do interior do cooler |

---

## 7. Fontes desta rodada e o que não consegui ver

**Abertas em 2026-11-10** (resumo automático, salvo indicação):
- PCGH, 5090 FE: https://www.pcgameshardware.de/Geforce-RTX-5090-Grafikkarte-281029/Specials/Founders-Edition-mit-High-Density-PCB-und-Double-Pass-Through-1463646/
- Gamers Nexus, review da 5090 FE: https://gamersnexus.net/gpus/nvidia-geforce-rtx-5090-founders-edition-review-benchmarks-gaming-thermals-power
- Gamers Nexus, esta placa (releitura): RPM e temperatura.
- Notebookcheck, 5090 FE (releitura): "two-thirds blow-through".
- **Fonte oficial nova, ainda não registrada em `spec/sources/`:** guia rápido da linha RTX PRO Blackwell, https://images.nvidia.com/aem-dam/Solutions/design-visualization/quadro-product-literature/rtx-pro-blackwell-online-qsg-210x148mm-20250718-r14.pdf. Li as páginas 1 a 8 como imagem. A placa vem com um "Auxiliary Power Cable (4x PCIe 8-pin (PSU) to 1x PCIe Gen5 16-pin (GPU) power adapter)" e um "Enhanced Straight Extender", e é "dual-slot". As páginas seguintes não foram lidas e podem trazer um diagrama da placa.

**Só resumo de busca (não valem como fato):** vazamento do package do GB202 (techspot, guru3d, Tom's); MPS MP29816-C; TechPowerUp e Tom's sobre a 5090 FE (câmara, tubos, fases, 40 mm).

**Bloqueadas ou truncadas:** TweakTown, HotHardware, Guru3D e TechPowerUp (403); Tom's Hardware (corpo truncado); MPS (página não carregou).

**O que não consegui ver:**
- O interior do cooler, os ventiladores fora do lugar, qualquer heat pipe.
- A placa das saídas de vídeo e a outra ponta dos cabos.
- A frente do PCB sem pads e as bordas inteiras com os indutores.
- A extremidade oposta ao bracket e uma vista ortogonal de qualquer face.
- Os parafusos de E2 e E3.
- Recortes em resolução cheia: não tive ferramenta de recorte. Textos e contagens finas precisam de releitura pelo `visual-qa`.
- A figura 3 da Jon Peddie, creditada à NVIDIA.
