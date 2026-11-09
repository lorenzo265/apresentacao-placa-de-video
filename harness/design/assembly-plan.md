# Plano de montagem da placa real (v0.3)

Estado: **plano para a F2**, ainda sem `assembly.json`. Substitui a visão genérica da v0.1 ("backplate, shroud, ventilador, cooler, PCB") pela estrutura que as fontes mostram para a RTX PRO 6000 Blackwell Workstation Edition.

Base de fatos: `harness/spec/sources/physical-card-sources.md`, `harness/spec/sources/standards-sources.md`, o catálogo de fotos `harness/spec/references/index.md` (todos de 2026-11-09) e as fontes já auditadas. A v0.3 incorpora as fotos e as normas, que ainda não passaram pelo `fact-checker`. A auditoria desta rodada está em `harness/qa/fact-check-fisico.md`: não aprovou na primeira passada, e as 26 correções estão aplicadas aqui. Falta a segunda passada. Este documento **não é a proposta de engenharia**: o que é lacuna fica marcado "a propor" e vai para o `architecture-inferencer` com a skill `gpu-assembly-proposal`, com gate humano.

## 1. O que a v0.1 supunha e o que as fontes mostram

| Tema | Suposição da v0.1 | O que as fontes mostram | Efeito no projeto |
|---|---|---|---|
| Cooler | "dual-slot, active", com heatpipes e aletas, um ventilador | "Double-flow-through", "2 large fans on the front", ar por "dual axial pathways" que atravessa a placa "rather than into a PCB" (datasheet; Gamers Nexus) | o cooler é a estrutura da placa, não uma peça apoiada sobre o PCB |
| PCB | uma placa de circuito no comprimento da placa | "The PCB is in the center of the card", com adaptador PCIe separado e cabos flat (Gamers Nexus). Arranjo em três placas é oficial só para a RTX 5090 FE | `pcb-layout-modeler` deixa de modelar "o PCB" e passa a modelar um conjunto de placas |
| Origem das coordenadas | canto do PCB | o PCB principal não define o contorno da placa | origem passa a ser um canto do **envelope** da placa |
| Ordem de desmontagem | backplate, shroud, ventilador, cooler, PCB | sete passos do teardown desta placa, em que o PCB sai por último (seção 3) | `assembly-planner` segue a ordem real |
| Interface térmica | não definida | pasta térmica no die desta placa; a RTX 5090 FE usa metal líquido | exemplo real de que "derivar da placa irmã" pode errar: entra no vídeo |
| Memória | "chips em volta do die" | 32 posições, 16 módulos no verso (Gamers Nexus) | a conta fecha com 96 GB se as 32 estiverem ocupadas (seção 5) |
| Conector | "16 pinos (12V-2x6)" de memória | "1x PCIe CEM5 16-pin" (datasheet; CEM5 é a especificação, não o nome do conector). A Gamers Nexus chama de "12VHPWR". A equivalência entre os nomes não está provada | usar o texto do datasheet |

### 1.1 O que as fotos mostraram (2026-11-09)

O catálogo `spec/references/index.md` olhou as 75 imagens do teardown (38 mostram esta placa) e os renders oficiais. Quatro fotos decisivas foram reconferidas pela sessão principal (gn-02, gn-03, gn-16, gn-29). Convenção: **face A** é a dos ventiladores, **face B** é a oposta, **borda superior** é a oposta aos contatos PCIe.

| O plano v0.2 dizia | O que as fotos mostram | Imagens |
|---|---|---|
| E1: sai a "placa traseira" | A primeira peça a sair é o **bracket**. O texto do teardown diz "back plate" nesse ponto. Não existe placa traseira lisa | gn-14 a gn-16 |
| Face oposta aos ventiladores: placa traseira | A face B é feita de duas áreas de grade com um X central brilhante, com o texto "RTX PRO 6000". O ar atravessa a placa da face A para a face B nas duas pontas | gn-03, gn-08 |
| E2: sai a "moldura externa" | Sai um aro fino que contorna a face B | gn-17 |
| Duas pilhas de aletas | Pelo menos três regiões: uma sob cada ventilador e outra junto à borda superior do PCB | gn-21, gn-26, gn-29 |
| Ventiladores: contagem de pás desconhecida | 7 pás em cada um (faixa de 7 a 8), os dois iguais | gn-02 |
| Memória: 16 no verso, posição desconhecida | 16 chips em U em volta do chip: 5 de cada lado, 4 junto à borda do conector de energia e 2 do lado oposto. Nenhuma posição vazia no verso | gn-29 |
| Bracket: disposição desconhecida | 4 DisplayPort em uma fileira; bracket de chapa lisa, sem grade | gn-11, gn-16 |
| Conector: "no topo, no meio" | Borda superior, na seção central, entre 55% e 70% do comprimento a partir do bracket, inclinado. 12 cavidades de potência visíveis | gn-13, gn-29 |
| PCB: contorno desconhecido | Quase quadrado, com um degrau no canto do conector, ocupando só a seção central da placa | gn-29 |
| Capa do datasheet: face não identificada | É a face B | nv-01 |
| Marcação do chip: só no texto | "GB202-870-A1" lido na foto do package | gn-35, gn-42 |

Continuam sem foto: a frente do PCB sem os pads (as outras 16 posições de memória), a placa das saídas de vídeo, o interior do cooler e qualquer vista ortogonal oficial.

As procedências "confirmed (foto)" desta versão são leitura de foto por um agente, reconferida em quatro imagens pela sessão principal. Até a passada do `visual-qa`, valem como `derived` sempre que a identificação depender só da imagem (forma, disposição, contagem). O que também está no texto do teardown continua `confirmed`.

## 2. Árvore de peças

Colunas: **Existe** é a procedência de a peça existir nesta placa. **Forma** é a procedência que a geometria terá. "A derivar de fotos" é intenção: as fotos ainda não foram catalogadas nem vistas por ninguém (seção 6.1). **Fid.** é o nível de fidelidade (seção 4). "5090 FE" quer dizer derivado da GeForce RTX 5090 Founders Edition, que usa o mesmo chip e, segundo a Puget Systems, uma carcaça "quase idêntica".

### 2.1 Estrutura e exterior

| id | Peça | Existe | Forma | Fid. | Fonte | Lacuna |
|---|---|---|---|---|---|---|
| `card` | conjunto montado | confirmed | derived | A | datasheet: 5,4" x 12", dois slots | espessura em mm |
| `frame.face_b` | face B: duas grades e X central com o texto "RTX PRO 6000" | confirmed (foto) | a derivar de fotos | A | gn-03, gn-08, nv-01 | material; o que há atrás da grade |
| `frame.rim` | aro fino que contorna a face B | confirmed (foto) | a derivar de fotos | B | gn-17; teardown, passo 2 | o parafuso que o prende não aparece |
| `frame.shroud` | carcaça: laterais e face A com os dois recortes de ventilador, em preto e grafite fosco | confirmed (foto) | a derivar de fotos | A | gn-02, gn-29 | material; espessura da placa; a ponta oposta ao bracket não aparece em foto |
| `frame.center_covers` | tampas centrais (o X) | confirmed | a derivar de fotos | A | teardown, passo 3; gn-19 a gn-21 | quantidade exata |
| `io.bracket` | bracket de chapa lisa, sem grade, com 4 DisplayPort 2.1b em uma fileira | confirmed (datasheet e foto) | a derivar de norma e fotos | A | datasheet, p. 3; gn-11, gn-16 | bracket de dois slots sem desenho de norma |
| `fasteners.*` | parafusos | confirmed | a propor | C | fotos: 4 no bracket; sob ele, 4 com arruela clara e 9 pequenos; 4 na placa central; 4 na mola em X | tipos de cabeça; parafuso do aro |

### 2.2 Refrigeração

| id | Peça | Existe | Forma | Fid. | Fonte | Lacuna |
|---|---|---|---|---|---|---|
| `cooler.fan.1`, `cooler.fan.2` | dois ventiladores iguais na face A, 7 pás cada (faixa de 7 a 8, contagem em foto) | confirmed (dois, na face A, pás contadas em foto); derived (axiais) | a derivar de fotos | A | teardown ("2 large fans on the front"); gn-02; datasheet ("dual axial pathways") | diâmetro: 115 ± 6 mm medido em foto de terceiro (`derived`, ver `measurements.csv`) |
| `cooler.fins.1`, `cooler.fins.2` | pilhas de aletas pretas nas duas pontas, atravessadas pelo ar | confirmed (foto) | a derivar de fotos | A | gn-29; teardown (aletas mais altas onde termina a placa do PCB, com depressão) | contagem, passo, material |
| `cooler.fins.3` | aletas junto à borda superior do PCB, na seção central | confirmed (foto) | a propor | B | gn-21, gn-26 | extensão e ligação com as outras pilhas |
| `cooler.base` | base de contato de tom acobreado | confirmed (foto) | a propor | B | gn-32, gn-34 | dimensões |
| `cooler.vapor_chamber` | câmara de vapor | derived | a propor | B | 5090 FE (página NVIDIA: "3D Vapor Chamber with integrated heat pipes"); Jon Peddie descreve "bilateral 3D vapor chambers", sem abrir a placa | não achamos teardown que mostre o interior. Pista: a figura 3 da Jon Peddie é creditada à NVIDIA |
| `cooler.leaf_spring` | mola de pressão sobre a GPU | confirmed | a propor | B | Gamers Nexus, passo 6 | forma |
| `gpu.tim` | pasta térmica | confirmed | illustrative | C | Gamers Nexus | |
| `mem.pads` | pads térmicos sobre a memória e sobre indutores | confirmed | a propor | C | Gamers Nexus | espessura, contorno |

### 2.3 Eletrônica

| id | Peça | Existe | Forma | Fid. | Fonte | Lacuna |
|---|---|---|---|---|---|---|
| `pcb.main` | PCB principal, quase quadrado, com degrau no canto do conector, só na seção central | confirmed (foto) | a derivar de fotos | A | teardown, passo 7; gn-29 | dimensões: não há foto ortogonal. Estimativa grosseira de 0,28 a 0,33 do comprimento da placa, que não vale como medida |
| `pcb.plate` | placa que cobre o PCB | confirmed | a propor | B | Gamers Nexus, passo 5 | função e forma |
| `pcie.adapter` | adaptador PCIe com pinagem própria, ligado ao PCB por um conector fino | confirmed (texto e foto) | a derivar de norma e fotos | A | teardown, passo 4; gn-25 | dimensões |
| `pcie.clamp` | grampo do suporte do slot | confirmed | a propor | C | Gamers Nexus, passo 4 | forma |
| `flex.*` | cabos flat | confirmed (existem); derived (o que ligam, pela 5090 FE) | a propor | B | teardown, passo 6; gn-29 (um cabo sai do PCB e entra no cooler) | a outra ponta não aparece |
| `io.board` | placa das saídas de vídeo | derived | a propor | B | 5090 FE ("3-piece PCB", NVIDIA). Reforço: as saídas ficam na ponta da placa e o PCB só ocupa o centro | não aparece em nenhuma foto |
| `gpu.package` | GB202 ("GB 202-870-A1" na grafia da Gamers Nexus, que chama de SKU) | confirmed | a propor | A | Gamers Nexus ("massive GPU substrate"); whitepaper (die de 750 mm²) | dimensões do package e do die visível; marcação não lida em foto |
| `mem.back.1..16` | 16 chips GDDR7 no verso, em U em volta do chip: 5 + 5 nos lados, 4 junto ao conector de energia, 2 do lado oposto | confirmed (texto e foto) | a derivar de norma (12 × 14 mm, `derived`) e fotos | A | teardown; gn-29 | fabricante; coordenadas |
| `mem.front.1..16` | 16 posições na frente | derived (32 posições no total menos 16 no verso; a fonte não diz "na frente" nem que estão ocupadas) | a derivar de norma | A | Gamers Nexus ("32 total memory locations") | ocupação e posição exata |
| `power.connector` | um conector de 16 pinos ("1x PCIe CEM5 16-pin") na borda superior, seção central, inclinado | confirmed (tipo; posição em foto) | a derivar de norma | A | datasheet, p. 3; gn-13, gn-29; norma em `standards-sources.md` | ângulo; se é 12VHPWR ou 12V-2x6 |
| `power.inductors` | indutores em fileiras junto à borda do conector e no canto em degrau | confirmed (foto) | a propor | B | gn-33, gn-38, gn-40 | quantidade: entre 10 e 20 visíveis, sem total seguro. Pista de baixa autoridade: um blog fala em 24 de um mesmo tipo |
| `power.vrm.gpu`, `power.vrm.mem` | fases de energia | inferred | a propor | B | nenhuma fonte desta placa. Para a 5090 FE as fontes divergem (30, 27 ou 34) | **tudo** |
| `pcb.smd` | componentes pequenos (capacitores, resistores) | confirmed ("PCB muito denso") | illustrative | C | Gamers Nexus | não serão contados |

Regra: nenhuma peça "a propor" entra em `assembly.json` sem passar pela `gpu-assembly-proposal` e pelo gate humano. Peça com **Existe** `derived` ou `inferred` aparece no vídeo com o selo correspondente, mesmo que a forma fique convincente.

## 3. Ordem de desmontagem e estágios de explosão

A ordem vem do teardown desta placa (Gamers Nexus). Os estágios E1 a E7 são `confirmed` quanto à ordem. A direção e a distância de cada explosão são escolha de direção de arte.

| Estágio | O que sai | Peças | Procedência da ordem |
|---|---|---|---|
| E1 | bracket (o teardown diz "back plate") | `io.bracket` | confirmed (ordem); a identificação da peça vem das fotos |
| E2 | um parafuso, depois o aro da face B | `frame.rim` | confirmed |
| E3 | parafusos em volta do centro e tampas centrais (o X) | `frame.center_covers` | confirmed |
| E4 | grampo do slot e adaptador PCIe | `pcie.clamp`, `pcie.adapter` | confirmed |
| E5 | placa que cobre o PCB | `pcb.plate` | confirmed |
| E6 | cabos flat e parafusos da mola de pressão | `flex.*`, `cooler.leaf_spring` | confirmed |
| E7 | PCB principal, com a pasta térmica à vista | `pcb.main`, `gpu.package`, `mem.*`, `power.*` | confirmed |
| (não sai) | carcaça, ventiladores e aletas ficam montados no teardown | `frame.shroud`, `frame.face_b`, `cooler.*` | confirmed (foto gn-29) |
| E8 | cooler aberto: ventiladores, aletas, câmara de vapor | `cooler.*` | **inferred**: os ventiladores nunca saem nas fotos, e não há imagem do interior |

O estágio E8 é didático. O vídeo diz isso na tela.

## 4. Níveis de fidelidade

"Seguir a placa real" não significa o mesmo esforço em toda peça. Cada peça recebe um nível, e o `visual-qa` cobra de acordo.

| Nível | Uso | Exigência |
|---|---|---|
| A (herói) | peça com beat próprio e close | contagens visíveis iguais às da placa (ventiladores, pás, portas, chips, pinos); contorno conferido contra foto na vista padrão; medidas com fonte ou tolerância declarada |
| B (visível) | aparece em beat de outra peça | forma e posição plausíveis, proporção conferida; detalhe simplificado |
| C (representativa) | elemento repetido ou pequeno | instanciado a partir de tabela; quantidade pode ser representativa, e o texto nunca cita o número como fato |

## 5. Contas que precisam fechar

| Conta | Resultado | Estado |
|---|---|---|
| Memória: 32 posições × 3 GB = 96 GB | fecha, **se** as 32 posições estiverem ocupadas | 32 posições e 96 GB `confirmed`. "32 chips" e "3 GB por chip" são `derived` (a própria Gamers Nexus faz a dedução, sem ler a marcação). As fontes não excluem 24 chips de 4 GB |
| Barramento: 16 controladores × 32 bits = 512 bits; 32 chips ÷ 16 controladores = 2 chips por controlador | fecha como média, com a mesma condição. O comunicado da JEDEC sobre o GDDR7 cita "support for 2-Channel mode to double system capacity", e existe chip de 24 Gbit (3 GB). Ligar esse modo a "dois chips por controlador de 32 bits" é leitura nossa: o comunicado não diz, e a norma em si não foi aberta | 512 bits e 16 controladores `confirmed`. A razão 2:1 é `derived` condicional. **Como** dois chips dividem um controlador (16 bits cada, um por face) é `inferred`: nenhuma fonte descreve, e a 5090 FE usa um chip por controlador. Vai para a proposta de engenharia |
| Banda: 28 Gbps × 512 ÷ 8 = 1.792 GB/s | fecha | `confirmed` (whitepaper e datasheet) |
| Envelope: 5,4" × 12,0" = 137,2 × 304,8 mm | conversão | polegadas `confirmed`, milímetros `derived` |
| Espessura em mm de "dois slots" | fecha em parte | passo entre slots de 20,32 mm; placa de dois slots pode ter componentes até 34,80 mm de altura sobre o PCB (CEM 3.0; conferir na 5.x). A espessura real da carcaça continua sem fonte: a 5090 FE tem 42 mm segundo a Puget |
| Altura: 5,4" contra a norma | declarada | a altura padrão de uma placa é 111,15 mm; esta tem 137,16 mm, cerca de 26 mm a mais (supondo a mesma referência de medida da norma, e adotando 111,15 entre os três valores que a cópia da norma traz). O datasheet chama isso de "extended height"; o termo não aparece nas páginas lidas da norma |
| Energia: 600 W de potência total | fecha | conector de 16 pinos: até 600 W, 12 pinos de potência (6 de +12 V, 6 de retorno) e 4 de sinal; 600 ÷ 12 = 50 A nominais; o guia Intel ATX12VO 2.11, que reproduz a CEM 5.1, tabela 55 A para 600 W (não reaberto pela auditoria). Por pino, a folga depende da conta: 8,3 A (50 A em 6 pinos) contra 9,5 A do contato da Molex dá 14%; 9,17 A (55 A em 6 pinos) dá 3,6%. As duas contas supõem três coisas sem fonte: que o conector da placa tem a especificação do da Molex, que os 600 W passam todos pelo conector e que a corrente se divide igualmente. O slot fornece até 75 W (CEM 3.0). **Como a placa reparte a carga entre slot e conector é lacuna** |
| Térmica: área de aletas e vazão para 600 W | **não fechada** | depende da proposta do interior do cooler |

## 6. Como medir sem ter a placa na mão

1. **Envelope oficial** como escala: 137,2 × 304,8 mm.
2. **Normas** para o que é padronizado: bracket e contatos PCIe, conector de 16 pinos, conector DisplayPort, encapsulamento GDDR7. Registradas em 2026-11-09 em `spec/sources/standards-sources.md` (rodada **não auditada**) e já lançadas em `design/measurements.csv`. Limites: a única cópia aberta da norma PCIe CEM é a revisão 3.0, de 2013; o desenho do receptáculo DisplayPort só veio de fonte de baixa autoridade; a bracket de dois slots não tem desenho.
3. **Proporção em foto**: em vista quase ortogonal, mede-se em pixels contra o envelope conhecido. O resultado é `derived`, com tolerância declarada, e a foto usada fica citada.
4. **Análogo** (5090 FE) só para o que não aparece em nenhuma foto desta placa. Resultado `derived`.
5. **Proposta de engenharia** para o resto. Resultado `inferred`.

Tudo vai para `design/measurements.csv`: `feature, value_mm, tolerance_mm, method, source, provenance`. Os modeladores leem dessa tabela. Número solto no script é erro de lint.

### 6.1 Pacote de referências visuais

`spec/references/index.md` cataloga 75 imagens do teardown e 13 da NVIDIA: uma linha por imagem, as vistas que cada uma serve e o que se vê em cada pergunta do modelo. As imagens não são versionadas (direitos de terceiros); ficam em `spec/references/cache/`, ignorado pelo git.

| Vista necessária | Situação |
|---|---|
| três quartos, face A e face B | temos (gn-02, gn-46; render oficial nv-01) |
| face A, face B, topo, bracket | temos fotos oblíquas, boas para forma e disposição. **Falta vista ortogonal oficial** |
| extremidade oposta ao bracket; borda dos contatos PCIe | **falta** |
| estágios E1 a E7 | temos, de 2 a 11 imagens por estágio |
| PCB, verso | temos (gn-29, oblíqua) |
| PCB, frente sem pads | **falta** |
| cooler aberto | **falta**: só a base de contato aparece |

Medidas por proporção: nenhuma foto do teardown nem da NVIDIA é ortogonal. A única quase ortogonal é uma foto de banco de dados de terceiro que aparece dentro do vídeo. As medidas tiradas dela estão em `measurements.csv` como `derived`, com ±4% de escala, e a altura medida (122 mm de carcaça) **não fecha** com os 137,2 mm oficiais. Usar com essa ressalva.

### 6.2 Critério de aceite da fidelidade

- Envelope do GLB igual à **convenção do projeto** (137,2 × 304,8 mm, conversão exata das polegadas do datasheet), com erro de até 0,5 mm. A fonte oficial tem resolução de 0,1", ou seja, a placa real pode diferir da convenção em mais de 1 mm. A NVIDIA dá 304 × 137 mm para a 5090 FE.
- Toda contagem visível em peça de nível A igual à da fonte, ou marcada "representativa" na tela.
- Para cada vista padrão com foto de referência, o `visual-qa` recebe o render na mesma vista ao lado da foto e aprova contorno, proporção e posição relativa.
- Toda diferença conhecida entra na lista "desvios conhecidos" do `assembly.json`, com o motivo.

## 7. Ajustes de contrato achados em teste (2026-11-09)

Testado neste ambiente com `build123d` 0.13.0 e `trimesh` 5.2.0 em Python 3.13: uma caixa com o envelope da placa foi exportada para STEP e GLB sem erro.

| Achado | Contrato da v0.1 | Correção |
|---|---|---|
| O GLB sai em **metros** e com **Y para cima** (padrão glTF): uma caixa de teste de 304,8 × 137,2 × 40,64 mm saiu com 0,30 × 0,04 × 0,14. A espessura de 40,64 mm é valor de teste, sem fonte | "unidades em mm, Z para cima" para tudo | CAD, `assembly.json` e `storyboard.json` em mm e Z para cima. A conversão para o referencial do GLB acontece em um único lugar, no `integrator`, e o viewer lê âncoras e câmeras já convertidas |
| A caixa exportada **não passa** no teste de malha fechada do `trimesh` (24 vértices, faces soltas). Depois de unir vértices, passa (8 vértices) | `ops-runner` exige "malha fechada" | validar o sólido no CAD (`is_valid`, volume maior que zero) e, no GLB, unir vértices antes do teste |
| `build123d` e `trimesh` não estão instalados nem declarados | "stack" só descrita em texto | versionar `harness/requirements.txt` e `harness/viewer/package.json` com versões fixas |
| Origem `pcb.bottom_left_front` | o PCB define o contorno | origem `card.envelope_min`: canto do envelope do lado da bracket e do lado dos contatos PCIe |

Campos novos por peça em `assembly.json`: `stage` (E1 a E8), `fidelity` (A, B ou C), `exists_provenance` e `shape_provenance` (as duas colunas da seção 2), `count` com `count_provenance`, e `measurements` (ids de `measurements.csv`).

## 8. Fila para o `architecture-inferencer` (F2)

Por ordem de impacto no vídeo:

1. Interior do cooler: câmara de vapor, ligação com as duas pilhas de aletas, caminho do calor.
2. PCB principal: contorno, dimensões, posição do GB202, das 32 posições de memória e do conector. Inclui a pergunta de memória: 32 chips de 3 GB em pares por controlador, ou outra ocupação.
3. Quantas placas são e como os cabos flat as ligam (três, como na 5090 FE?).
4. Fases de energia da GPU e da memória, com a conta de potência.
5. Package do GB202: dimensões e moldura.
6. Parafusos: tipos e quantidades por estágio.
7. Ventiladores: resolvido em parte pelas fotos (7 pás, cerca de 115 mm). Falta a forma da pá.
8. O que as 16 posições de memória da frente contêm e onde ficam (não há foto da frente sem pads).
9. Espessura da carcaça e o que a cota oficial de 5,4" de altura inclui (a foto de terceiro dá 122 mm de carcaça e 133 mm com os contatos).
