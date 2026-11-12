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
| `power.inductors` | indutores em fileiras nas duas bordas longas do PCB (corrigido pela proposta da F2; antes: borda do conector e canto em degrau) | confirmed (foto) | a propor | B | gn-33, gn-38, gn-40 | quantidade: entre 10 e 20 visíveis, sem total seguro. Pista de baixa autoridade: um blog fala em 24 de um mesmo tipo |
| `power.vrm.gpu`, `power.vrm.mem` | fases de energia | inferred | a propor | B | nenhuma fonte desta placa. Para a 5090 FE as fontes divergem (30, 27 ou 34) | **tudo** |
| `pcb.smd` | componentes pequenos (capacitores, resistores) | confirmed ("PCB muito denso") | illustrative | C | Gamers Nexus | não serão contados |

Regra: nenhuma peça "a propor" entra em `assembly.json` sem passar pela `gpu-assembly-proposal` e pelo gate humano. Peça com **Existe** `derived` ou `inferred` aparece no vídeo com o selo correspondente, mesmo que a forma fique convincente.

## 3. Ordem de desmontagem e estágios de explosão

A ordem vem do teardown desta placa (Gamers Nexus). Os estágios E1 a E7 são `confirmed` quanto à ordem. A direção e a distância de cada explosão são escolha de direção de arte.

| Estágio | O que sai | Peças | Procedência da ordem |
|---|---|---|---|
| E1 | bracket (o teardown diz "back plate") | `io.bracket` | confirmed (ordem); a identificação da peça vem das fotos |
| E2 | um parafuso, depois o aro da face B | `frame.rim` | confirmed |
| E3 | tampas centrais (o X). Os 4 parafusos claros em volta do centro são do E5, não daqui (corrigido pela proposta da F2); a fixação das tampas não foi vista | `frame.center_covers` | confirmed |
| E4 | grampo do slot e adaptador PCIe | `pcie.clamp`, `pcie.adapter` | confirmed |
| E5 | placa que cobre o PCB | `pcb.plate` | confirmed |
| E6 | cabos flat e parafusos da mola de pressão | `flex.*`, `cooler.leaf_spring` | confirmed |
| E7 | PCB principal, com a pasta térmica à vista | `pcb.main`, `gpu.package`, `mem.*`, `power.*` | confirmed |
| (não sai) | carcaça, ventiladores e aletas ficam montados no teardown | `frame.shroud`, `frame.face_b`, `cooler.*` | confirmed (foto gn-29) |
| E8 | cooler aberto: ventiladores, aletas, câmara de vapor | `cooler.*` | **inferred**: no teardown, os ventiladores não são retirados, e do interior as fotos só mostram a base de contato e as aletas por fora |

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

- Envelope do GLB igual à **convenção do projeto** (137,16 × 304,8 mm, conversão exata das polegadas do datasheet), com erro de até 0,5 mm. Pela decisão D2 da proposta (aprovada em 2026-11-10), os 137,16 mm incluem os contatos PCIe: 11,16 mm de contatos mais 126 mm de carcaça. A fonte oficial tem resolução de 0,1", ou seja, a placa real pode diferir da convenção em mais de 1 mm. A NVIDIA dá 304 × 137 mm para a 5090 FE.
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

## 9. Depois do gate da F2 (2026-11-10)

A proposta (`design/proposal.md`) foi aprovada, e `design/assembly.json` foi escrito a partir dela: 44 peças (18 de fidelidade A, 13 B, 13 C), válido no schema. Onde este plano e a proposta divergem, vale a proposta. `measurements.csv` passou de 33 para 129 linhas; as 96 novas estão como não auditadas.

O que o `assembly-planner` deixou em aberto:
- **O schema não tem campo de interfaces.** Elas viraram linhas `iface_*` do CSV. Também falta dizer se `explode` é relativo à peça-mãe (adotado: relativo), e `count` não aceita zero.
- **Peças fora do assembly por não terem item na proposta:** `mem.pads` e `pcie.clamp` (estão em `known_deviations`).
- **Posições que são escolha de bloqueio, sem fonte (`inferred`):** altura dos ventiladores e do bracket, profundidade das portas e do adaptador PCIe.
- **Dados que faltam:** contorno e espessura de `pcb.back_frame`; posição de `power.vrm.mem`, `power.controller` e `power.aux`; extensão de `cooler.fins.3`; pontas dos cabos flat; orientação de `io.board`.
- **Possíveis interferências para o `integrator`:** a aba do adaptador com o chip `mem.back.15` e com a `pcb.plate`; o furo da placa em (204, 124) com o chanfro do PCB e o conector de energia.
- **Desmontagem:** E1 a E7 é viável. O `flex.dp` aparece como translação, mas na foto continua preso à carcaça. O E8 separa peças soldadas e continua `inferred`.
- **Face B:** fica como filha de `frame.shroud`, sem explodir, porque a proposta trata as grades como parte das carcaças.

## 10. Revisão com as medidas do visual-qa (2026-11-10)

Base: `harness/qa/visual-qa-referencias-modelagem.md` (PCB nu sobre régua do Chiphell, PCB com componentes do blog sabareesh, desenho do PCB no manual da Alphacool, renders quase ortogonais da PNY). Revisão feita pelo `assembly-planner` em `design/measurements.csv` e `design/assembly.json`. Nenhum `id` de peça ou de âncora mudou. A proposta aprovada (`proposal.md`, `proposal.json`) não foi editada: ela continua sendo o registro do que foi aprovado, e as linhas do CSV citam o valor antigo.

### 10.1 O que D8 passa a ser

D8 aprovou 108 x 112 mm com tolerância de 10 mm só para bloquear volumes, com a condição de medir antes de travar. A medição foi feita: **119,6 x 121,5 mm, tolerância de 1,5 mm**, por duas fontes independentes (foto retificada e desenho da Alphacool, que dá 117,6 x 120,9). Os 108 x 112 deixam de valer. D8 fica cumprida, não revogada: era a decisão de medir, e a medida entrou. O que continua aberto dentro de D8: o tamanho do chanfro e do recorte em V do conector, e a identidade da foto do Chiphell (sem SKU; nada nela contradiz a Workstation Edition).

### 10.2 Referencial

O relatório usa x' no comprimento e y' na altura, com origem no canto entre a borda do lado do bracket e a borda dos contatos. É o mesmo referencial (u, v) da proposta (seção 2: "u a partir da borda do lado do bracket, v a partir da borda dos contatos"), então **u = x' e v = y'**, sem troca de eixo nem espelhamento. Na placa: x = `pcb_main_card_x_min` + u e y = `pcb_main_card_y_min` + v. O eixo trocado que o relatório aponta é do package (a proposta pôs os 63 mm em y; a medida põe o lado longo em x), não do referencial. Ângulos no plano xy contam a partir de +x, no sentido anti-horário visto de +z.

### 10.3 O que mudou

| Tema | Antes | Agora | Procedência |
|---|---|---|---|
| PCB | 108 x 112, centrado em x 152 | 119,6 x 121,5; x de 99,3 a 218,9; y de 14,4 a 135,9 | derived |
| Chip no PCB | (54; 56), centro do PCB | (52,7; 61,0); na placa (152; 75,4) | derived |
| Package | 56 x 63, lado longo em y | 67 x 57,5, lado longo em x | derived |
| Furos da mola | 78 x 84, iguais ao contorno da mola | 63,7 x 77,8, centrados no chip | derived |
| Furos da `pcb.plate` | 104 x 108, centrados no chip | 106 x 102 (furos de canto), centrados no PCB | posição derived, função inferred |
| Memória | grade regular com passo de 15 | grade medida, passo de 13,3 e 13,0; lado de 14 mm atravessado na fileira | derived |
| Conector de energia | 195, 40 ± 20 graus, no topo do PCB | 192, giro de 45 ± 4 graus (−45 no CSV), centro em y 124,4 | x e ângulo derived; y inferred |
| Carcaça | 126 | 124 ± 2; parede de 1 mm para o PCB caber | derived; parede inferred |
| Ventiladores | 61 e 244, aro de 115 | 58,5 e 242,8, aro de 116,8 | derived |
| Pilhas das pontas | 98 e 98 | 99,3 (bracket) e 85,9 (ponta oposta) | derived |
| Indutores | duas fileiras | três fileiras: contatos, ponta longe do bracket (nova) e borda superior | derived (contagem); posição inferred |
| Explosão | `cooler.base` 40; `fins.1` e `.2` 120 | `cooler.base` 20; `fins.1` e `.2` 140 | illustrative |

**Ponto 9 (assimetria das pilhas), conta refeita.** Com o chip em x 152 e u 52,7, o PCB começa em 152 − 52,7 = 99,3 e termina em 218,9; sobram 99,3 mm do lado do bracket e 85,9 mm do outro. Centrar o PCB (92,6 a 212,2) poria o chip em 145,3, a 6,2 mm do cruzamento do X (151,5 ± 2,5) e a 7,2 mm do cruzamento da face B (152,5), onde o furo da `pcb.plate` mostra o verso do chip. O ponto médio dos ventiladores (150,65) também aponta para cerca de 151. Decisão: o chip fica sob o X, em 152 (dentro da tolerância das duas faces), e as pilhas ficam assimétricas. Por fora a placa continua quase simétrica (ventiladores a 58,5 e 62 mm das pontas); a assimetria é interna.

**Peças novas: nenhuma.** O canal da borda superior com as duas fendas, o logotipo da borda superior e o X da face A entram como feições de `frame.shroud`; o X da face B, como feição de `frame.face_b` e `frame.center_covers`; o texto "RTX PRO 6000", como feição de `frame.center_covers`. Motivos: (1) são forma ou superfície de peças que já existem e não se separam delas em nenhum estágio; (2) texto e logotipo são detalhe de superfície, que a seção 5.2 da arquitetura põe no passo do Blender; (3) o schema não tem campo de feições e o `blockout.py` para com erro se o assembly tiver peça sem construtor. Cada feição ganhou linhas no CSV e, quando há número, uma âncora: `anchor.frame.shroud.power_opening` e `anchor.frame.center_covers.text`. Âncora nova também em `anchor.power.inductors.far_end`.

**Âncoras corrigidas.** `anchor.pcb.plate.1` saiu do furo da chapa para a chapa (152; 100,4). `anchor.cooler.leaf_spring.1` saiu da janela para o anel (152; 101,4). `anchor.pcb.back_frame.1` foi para o anel do primeiro furo (120,15; 36,5), onde há corpo da peça.

**Explosão de E7 e E8.** Com o PCB a +40 (E7) e a base a +40 (E8), a face de contato encostava no die. A base passou para +20: sobram 20 mm até o die e 16 mm até o componente mais baixo do PCB. O PCB continua a +40, abaixo da mola (+80), então a ordem e as câmeras de E7 não mudam. As pilhas das pontas passaram de 120 para 140 mm: a 120 a pilha do bracket atravessava o bracket, que saiu 40 mm no E1. A ordem dos estágios não mudou.

### 10.4 O que o blockout precisa para acompanhar

O `blockout.py` não foi editado (fora do escopo desta revisão). Ele lê as chaves do CSV pelos nomes, e nenhuma chave que ele usa foi renomeada ou removida. Mas ele tem posições fixas no código que as medidas novas contradizem:

1. **Conector de energia no topo do PCB.** O script centra o conector em `pcb_main_card_y_min + pcb_main_height` (135,9). Girado 45 graus, o corpo sobe 10,55 mm e passa do envelope (cerca de 146,5 contra 137,16). **A conferência do envelope em y vai falhar até o script usar `power_connector_center_y`.**
2. **Giro dos chips de memória.** O script põe o lado de 14 mm ao longo das fileiras laterais e atravessado nas das bordas; a medida pede o contrário. Com o passo de 13,3 e 13,0, os chips vizinhos se sobrepõem no blockout.
3. **Centro dos padrões.** `pcb.plate`, `fasteners.e5_plate` e a moldura de `cooler.base` são centrados no die no script; o assembly os centra no PCB (`iface_pcb_center_x`, `iface_pcb_center_y`). As âncoras `anchor.fasteners.e5_plate.*` vão aparecer a cerca de 4,6 mm dos corpos do blockout.
4. **Pilhas assimétricas.** O script usa `fin_stack_end_length_x` nas duas pontas (agora 85,9); as linhas `fin_stack_end_1_length_x` e `fin_stack_end_2_length_x` têm os comprimentos reais.
5. **Fileira de indutores da ponta longe do bracket.** O script tem 13 + 11 posições fixas; a fileira nova (`iface_far_end_inductor_band_x`, `_y`) não tem corpo, e a âncora dela vai aparecer longe da peça.
6. **Contorno do PCB.** Continua caixa, sem chanfro, recorte e rebaixo (`pcb_main_chamfer_angle_deg`, `pcb_main_contact_edge_recess_*`).

A cópia `viewer/public/data/measurements.json` também precisa ser regenerada.

### 10.5 Em aberto

Decisão humana:
- **Indutores:** a contagem visível (cerca de 10 + 10 a 11 + 7, mais os escondidos na ponta do bracket) passa dos 24 representativos de D4. Subir ou manter é decisão de D4.
- **Pilhas assimétricas** (99,3 e 85,9): consequência direta das medidas, mas muda a leitura "duas pontas iguais" da proposta. Confirmar ou pedir referência.

Nova referência ou nova medição:
- Orientação do die dentro do package: a proposta leu o die mais comprido na altura (gn-42), a mesma leitura que errou o package. Em gn-41 a moldura mede 2,4 vezes a largura do die, cerca de 58 mm, que agora bate com o lado curto do package (57,5): isso sugere o die também com o lado longo em x. Reconferir no sabareesh e em gn-42.
- Package contra memória: com o package de 57,5 em y centrado em v 61,0, a fileira da borda de energia fica cerca de 1 mm sobre ele (dentro das tolerâncias somadas). O desenho da Alphacool pode desempatar.
- Tamanho do chanfro e do recorte em V do conector, e a distância do conector à borda (`power_connector_center_y` é escolha de bloqueio).
- Canal da borda superior, as duas fendas e o logotipo: vistos, sem cota.
- Contorno da `pcb.plate` (104 x 108, escala antiga), janela e anel da mola, posição do conector auxiliar: medidos com a escala do PCB antigo.
- Furos cobreados de canto: centro do padrão não informado (adotado o centro do PCB), um dos quatro não confirmado, e não está provado que prendam a `pcb.plate`.
- Altura dos ventiladores e da fileira de DisplayPort na carcaça: continuam centradas por escolha de bloqueio.
- Catálogo: a imagem 89589 da Puget não é desta placa (tem grade no bracket). O assembly não a cita; `spec/references/index.md` precisa da correção (fora desta revisão).

Continuam sem fonte, com o aviso de tela: interior do cooler, fases de energia, alturas de componente, posição de `power.vrm.mem`, `power.controller` e `power.aux`.


## 11. Referencial corrigido (2026-11-10)

### 11.1 O problema

O referencial antigo (x a partir do bracket, y para cima a partir dos contatos, face A dos ventiladores em z = 0 e face B em z = 40, sistema destro) era o **espelho** da placa real. Olhando a placa pela face dos ventiladores com os contatos embaixo (`spec/references/cache/pny/front.png`), o bracket fica à esquerda; no referencial antigo, visto de z negativo, ele ficava à direita. Formas simétricas não sofriam, mas tudo o que tem lateralidade saía trocado: o canto do conector de energia em relação à face vista, o sentido das pás, o texto "RTX PRO 6000" e o logotipo que entram no passo do Blender. Achado pelo modelador da carcaça e confirmado pela sessão principal no quadro do beat a1.1.

### 11.2 O referencial adotado

Mantidos x a partir do plano do bracket e y a partir da ponta dos contatos; **a face A dos ventiladores passa para z = 40 e a face B (grades e X) para z = 0**. É um espelho em z: z_novo = 40 - z_antigo. Motivos para esta escolha e não outra:

1. Num sistema destro com x para a direita e y para cima, z sai da tela na direção do observador. Para o observador ver `pny/front.png` (bracket à esquerda, contatos embaixo), a face dos ventiladores tem de ficar em z alto. Não há outro jeito de manter x e y sem espelhar.
2. Espelhar x (medir da ponta oposta) ou y (medir do topo) mudaria quase todas as 175 linhas do CSV, a proposta aprovada e as medidas do visual-qa, que são todas distâncias ao bracket e aos contatos. O espelho em z mexe só nas coordenadas de espessura: 4 linhas do CSV.
3. Todas as medidas no plano xy (posições, ângulos, a fileira do conector a -45 graus, a caixa do texto) foram tiradas como distâncias ao bracket e aos contatos e continuam valendo. O texto da face B, lido em `pny/back.png` com os contatos para cima, agora lê certo visto de -z.

Conferência: visto de +z, a placa aparece como `pny/front.png`; visto de -z com os contatos para cima, como `pny/back.png`. Ângulos no plano xy contam de +x, anti-horário visto de +z (do lado dos ventiladores). Contrato em `ARCHITECTURE.md`, seção 7.6.

### 11.3 O que mudou

| Onde | O quê | Quantidade |
|---|---|---|
| `design/measurements.csv` | coordenadas de z espelhadas: `iface_pcb_back_z` 33,9 para 6,1; `iface_pcb_front_z` 32,3 para 7,7; `iface_die_contact_z` 29,3 para 10,7; `iface_adapter_board_z_min` 37,5 para 0,93 (o mínimo agora é a face do lado da face B: 40 - 37,5 - 1,57). As linhas `layer_*` são espessuras e não mudaram | 4 linhas |
| `design/measurements.csv` | remedição da seção 11.5 e as contas que dependem dela | 18 linhas alteradas, 1 nova (`shroud_center_section_height`) |
| `design/measurements.csv` | interfaces da carcaça promovidas de `frame.py` para o CSV, porque as peças vizinhas dependem delas: `shroud_face_a_plate_thickness`, `shroud_channel_depth`, `shroud_end_plate_recess`, `shroud_end_plate_thickness` (todas `inferred`) | 4 linhas novas; total de 175 |
| `design/assembly.json` | z de todas as âncoras espelhado; y de 68 âncoras deslocado pela altura remedida (+0,35 nas que seguem o centro da carcaça, +0,36 nas que seguem o PCB); x das âncoras dos ventiladores (61,2 e 243,3); sinal de z invertido em `explode.dir` (E2 a E7 e a base do E8 explodem para -z, os ventiladores do E8 para +z); 14 trechos de `rationale` e `viewer_disclaimer` e 3 de `known_deviations` com z, altura e centro dos ventiladores. Ids de peça e de âncora iguais; distâncias de explosão iguais | 77 âncoras, 40 direções |
| `design/assembly.json` e schema | campo opcional `kind` nas âncoras: `opening` para âncora de abertura ou de vão (seção 11.6) | 2 âncoras |
| `parts/blockout.py` | construtores reescritos no referencial novo (camadas da face B a partir de z = 0, ventilador e chapa da face A a partir de z = 40); caixas que respeitam a carcaça detalhada (`frame.keepouts()`); grava `build/blockout.glb` em vez de `build/card.glb` | |
| `parts/frame.py` | construtores reescritos no referencial novo; lê as 4 interfaces promovidas do CSV; `keepouts()` para as vizinhas; âncora `opening` aceita na caixa da peça | |
| `parts/frame_compare.py` | vistas e camadas no referencial novo, perspectivas sem espelhar a imagem, calibração sem a aba do bracket | |
| `parts/integrate.py`, `parts/frame_remeasure.py` | novos (seções 11.5 e 11.7) | |
| `story/storyboard.json` | `camera.pos` e `camera.target` com z = 40 - z nos 31 beats com câmera (o pedido falava em 32; o arquivo tem 31: atos 0 a 3, a7.5 e a7.6); `callout.box` com topo e base trocados (só a1.2 tinha um dos dois). `hold`, textos, ordem, `part`, `highlight` e beats de diagrama intactos | 31 câmeras, 1 caixa |

### 11.4 Como conferir

1. `python3 -I harness/parts/integrate.py` e abrir `harness/dist/integracao/01-face-a-ventiladores.png` ao lado de `pny/front.png` (bracket à esquerda, contatos embaixo, conector de energia na borda superior, à direita do centro) e `02-face-b.png` ao lado de `pny/back.png` (contatos em cima, bracket à esquerda, tampa com o texto na metade de baixo).
2. `harness/dist/parts/frame/02-face-a-sobreposta.png` e `04-face-b-sobreposta.png`: contornos da carcaça sobre os renders, sem espelhar.
3. Quadros do tour: `node harness/tools/frame3d.cjs --pos ... --target ... --no-build` com o `card.glb` novo em `viewer/dist/data/` (os 31 quadros conferidos estão em `harness/dist/frames3d/ref-<beat>.png`). Com `camera.up = (0, 0, 1)` fixo no viewer, cada quadro é o anterior invertido na vertical: as câmeras que olhavam a face B de cima agora olham de baixo.

Ajuste além da transformação: só **a1.2** (vista frontal da face A). Invertido na vertical, o quadro mostrava a placa de cabeça para baixo (contatos em cima, bracket à direita), o contrário da referência que o beat apresenta. A câmera foi espelhada em y em torno do alvo (de y 184,6 para -39,8) e em x em torno do meio da placa (alvo e posição de x 55,1 para 249,7), para manter a composição (placa à esquerda, caixa à direita); a caixa volta a `right-bottom`. Nos outros 30, a âncora fica dentro do quadro, a caixa não a cobre e a peça destacada aparece.

### 11.5 Remedição da carcaça (item 7 da F4)

Script: `parts/frame_remeasure.py` (saída em `dist/parts/frame/remedicao.json`). A calibração anterior incluía a aba do bracket (cerca de 3 px a mais), o que encolhia as medidas em cerca de 0,5 %.

| Grandeza | Antes | Medido (dois ou mais métodos) | Adotado |
|---|---|---|---|
| Altura da carcaça (módulos dos ventiladores) | 124 ± 2 (visual-qa); cerca de 122,4 (modelador) | bordas com subpixel: 123,47 (frente) e 123,26 (verso); soma do alfa: 123,24 e 123,20 | **123,3 ± 1,0** |
| Altura da seção central | não medida | 122,05 e 122,15; 121,81 e 122,10 | **122,0 ± 1,0** (linha nova; a carcaça ainda não modela o degrau) |
| Centro do ventilador 1 | 58,5 ± 2,5 (visual-qa); 61,19 (modelador) | crista do aro 61,13; borda externa do aro 61,14; borda do cubo 61,28 | **61,2 ± 1,0** |
| Centro do ventilador 2 | 242,8 ± 2,5 | 243,31; 243,35; 243,29 | **243,3 ± 1,0** |
| Entalhe da borda dos contatos | 138 a 158 | recuo visível de 146,0 a 158,5 (frente) e 145,0 a 157,5 (verso); antes de x 145 o lóbulo do adaptador esconde a borda | **145,5 a 158,0** |

O 124 vinha da razão altura por comprimento; o 122,4 do modelador misturava a seção central, que é cerca de 1,3 mm mais baixa, com a calibração que incluía o bracket. Com 58,5 o rotor encostava na placa de extremidade (folga negativa de 0,6 mm); com 61,2 sobram 2,1 mm, e a borda externa do aro medida fica a 3,4 mm da ponta do bracket, quase igual ao lado oposto (3,6 mm). A foto `storagereview/sr-4.jpg` foi tentada (retificação pelas quatro bordas e pelos anéis), mas as pontas somem no fundo escuro e no bracket, e os anéis retificados saem com 8 a 10 % de excentricidade: a foto não entrou nos números. Tudo `derived`, não auditado.

Contas refeitas com a altura nova: `iface_shroud_y_min` 13,86; `iface_shroud_center_y` e `iface_fan_center_y` 75,51 (o centro dos ventiladores, medido, fica 0,15 a 0,27 mm acima do centro dos módulos); `pcie_fingers_below_shroud` 12,4; `shroud_wall` 0,8 (limite (123,3 - 121,5) / 2 = 0,9); `pcb_main_card_y_min` 14,76; `iface_pcb_center_y` 75,51; `iface_die_center_y` 75,76; faixas dos indutores 23,36, 126,86 e 73,16; `fan_centers_distance` 182,1. `power_connector_center_y` ficou em 124,4 (escolha de bloqueio), para não mover o encaixe da carcaça.

### 11.6 Âncoras de abertura

`anchor.frame.shroud.power_opening` (centro da abertura do conector no fundo do canal, a 4,1 mm do corpo) e `anchor.frame.center_covers.1` (cruzamento do X, no vão entre as duas tampas, a 5,0 mm) ficam onde estão: marcam exatamente o que o texto aponta, e a linha de chamada não precisa de superfície. Ganharam `"kind": "opening"` no assembly; a conferência aceita âncora de abertura dentro da caixa envolvente da peça e continua exigindo 2 mm das outras.

### 11.7 Integração (F4)

`parts/integrate.py` gera `build/card.glb` (seção 7.2.1 da arquitetura). Resultado em 2026-11-10: envelope sem o bracket 304,80 x 137,16 x 40,00 (erro 0,00); 44 ids, 77 âncoras e nenhum nome repetido; malhas da carcaça fechadas e orientadas (31 810 triângulos); arquivo de 1,1 MB, determinístico; relatório em `build/integration-report.md`.

Resolvidas no blockout (as caixas agora respeitam a carcaça): pilhas das pontas contra as paredes e os cantos (contorno recortado; a do bracket começa depois de `io.board`); `cooler.fins.3` contra a chapa da face A, o fundo do canal e a parede do entalhe; `io.aux_header` (1,7 mm para dentro da borda do PCB) e `power.connector` (profundidade de 9,9 em vez de 11) contra o fundo do canal; moldura da `cooler.base` recortada em volta do entalhe, do canal e dos dois conectores; `io.board` abaixo do duto do ventilador 1; parafusos da placa de extremidade fora da parede curva e da chapa da face A; tubos de calor acima da face de contato. Resolvidas por medida: `pcb.main` contra a parede do entalhe (entalhe remedido) e o rotor do ventilador 1 contra a placa de extremidade (centro remedido).

Pendências, cada uma com dono (nenhuma corrigida em silêncio):
- **Adaptador PCIe na espessura** (assembly-planner, modeler-complex): o adaptador (z de 0,93 a 2,5) fica dentro da camada da face B, das tampas e do aro; a face B só tem recorte para a faixa, e `pny/back` mostra a grade inteira. O J3 atravessa a `pcb.plate`; a aba cobre um furo de canto da placa; as cabeças dos parafusos do E4 ficam entre o adaptador e a face B.
- **Parafusos do E5 sob as tampas** (modeler-complex): as tampas de 2,5 mm maciças não têm alívio para as 4 cabeças que `gn-20` mostra ao tirá-las.
- **Orçamento do verso** (assembly-planner): mola (1,2) e memória (1,1) não cabem nos 2,1 mm de `layer_back_mem_pad`.
- **Seção central mais baixa** (modeler-complex, pcb-layout-modeler, visual-qa): a carcaça tem 122,0 mm entre os módulos, onde fica o PCB de 121,5 ± 1,5; com parede de 0,8 não cabe. Ou o PCB é menor (a Alphacool dá 120,9), ou a parede é mais fina ali.
- **Orientação do conector de energia** (pcb-layout-modeler, modeler-complex): o CSV põe a fileira de pinos no plano do PCB a -45 graus; a abertura da carcaça põe o lado longo em z, como em `pny/3qtr-top-right`. Um dos dois está errado.
- **Cruzamento do X** (visual-qa): `frame_compare.py` mede 152,0 na face A e 150,4 na face B, o inverso das linhas `x_rib_cross_face_a/_b` (150,4 e 152,5).
- **Parafuso do aro** (assembly-planner, modeler-complex): sem posição vista, fica dentro do aro sem furo.
- **Package contra memória** (visual-qa): 1 mm, já listado na seção 10.5.

Viewer (fora desta tarefa, porque outro agente edita `viewer/src/`): o chão de sombra (z = -2) e as luzes ficam do lado de z positivo, que agora é o da face A. Nos beats que olham a face B, a câmera fica abaixo do chão e a luz principal vem de trás da peça. Ver o relatório da F4.

## 12. Arbitragem e contratos de 2026-11-11

Base: `harness/qa/visual-qa-arbitragem.md` e os pedidos dos modeladores de I/O (`parts/io_parts.py`), do PCB (`parts/pcb_layout.py`, `pcb.py`) e do interior do cooler (`parts/cooler.py`). Editados só `design/measurements.csv` e `design/assembly.json`; nenhum id de peça ou de âncora mudou, nenhuma linha do CSV foi apagada, e cada linha alterada cita o valor antigo. O referencial é o da seção 11 (face B em z = 0).

### 12.1 Viés de escala do `pcb-a`

O que está sobre o PCB na foto `chiphell/pcb-a.jpg` sai 1,3% maior (`chiphell_pcb_a_scale_factor` = 1,013 ± 0,004, aparente sobre real; quatro indícios na arbitragem). Toda linha tirada dessa foto, ou que usou como régua uma medida dela, foi dividida pelo fator, com a nota "corrigido pelo fator de escala do pcb-a (visual-qa, 2026-11-11)" e tolerância = tol / 1,013 + valor x 0,004 / 1,013, arredondada para cima. Entraram: contorno do PCB, centro do chip, furos da mola (e o contorno da mola), furos de canto (e os da `pcb.plate`), rebaixo da borda dos contatos, campo de esferas (`pcb-b`, régua nos furos do `pcb-a`), package em x (`sabareesh`, régua no PCB do `pcb-a`), J3 do adaptador, x do conector de energia. As medidas do adaptador que a arbitragem já deu corrigidas (comprimento, alturas, zona dos dedos) não foram divididas de novo. Ângulos não mudam.

Conferência contra fontes independentes:

| Grandeza | Antes | Corrigido | Alphacool | Diferença |
|---|---|---|---|---|
| PCB em x | 119,6 | 118,07 | 117,6 | +0,47 (dentro de 2,0) |
| PCB em y | 121,5 | 119,94 | 120,9 | -0,96 (dentro de 2,0) |
| Furos da mola em x | 63,7 | 62,9 | 63,6 | -0,7 (dentro de 1,3) |
| Furos da mola em y | 77,8 | 76,3 (77,3 remedido / 1,013) | 76,4 | -0,1 |
| Centro do chip | (52,7; 61,0) | (52,02; 60,22) | (51,3; 60,5) | (+0,7; -0,3) |

As cinco grandezas se aproximam da Alphacool, menos o PCB em y, que passa de +0,6 para -1,0 (ainda dentro das tolerâncias somadas). O PCB corrigido cabe na seção central da carcaça (122,0) com a parede de 0,8.

### 12.2 Contas propagadas

PCB de x 99,98 a 218,05 e de y 15,54 a 135,48 (centrado na carcaça). Centro do die continua em (152; 75,76): a correção de `pcb_main_card_y_min` e de `gpu_center_v` se cancela. Centro do PCB (159,02; 75,51). Grade da memória: as distâncias ao chip da arbitragem (42,55; 36,0; 35,1; 19,4; passo de 13,95) somadas ao centro do chip corrigido, o que dá u 9,47 e 94,57, v 32,32 a 88,12, borda de energia em v 96,22 de u 31,1, borda dos contatos em v 25,12 e u 32,62 e 71,42; as 32 âncoras de memória seguem a grade (a conferência do blockout compara com 0,01 mm). Pegada de 12 x 14 com o lado de 12 ao longo da fileira; na borda dos contatos o chip gira, e o vão entre as fileiras de cima e de baixo fica em 58,1: o package de 57,5 cabe com 0,25 a 0,35 mm de cada lado (`gb202_package_y` mantido, justificativa refeita, tolerância 1,0). Faixas dos indutores: 25,10 (contatos), 127,12 (borda de energia), (209,80; 75,76) (ponta). Pilhas das pontas: 99,98 e 86,75.

### 12.3 Contratos pedidos pelos modeladores

| Tema | Contrato |
|---|---|
| Saídas de vídeo | passo 20,9; fileira em z 13,5; topo do bracket 28,6 abaixo do topo da carcaça; com o centro da fileira a 72,25 da ponta das línguas (sr-1), `dp_row_center_y` = 60,79 e âncoras em y 29,44, 50,34, 71,24 e 92,14. O assembly é a referência: o modo `--ancoras` do `io_parts.py` coincide com o modo pela foto quando o script ler `bracket_top_below_shroud_top` e `dp_row_center_z` no lugar de 27,0 e 15,3. A porta 1 desce até y 21,39 e só cabe porque o canto da carcaça do lado do bracket junto aos contatos é quase reto (`shroud_corner_radius_bracket_bottom` = 3, promovido do `frame.py`). `io.bracket` deixou de ser descrito como centrado. |
| Conector de energia | de pé: lado longo (18,85) em z, de 7,7 a 26,55; fileiras lado a lado no plano, ao longo do chanfro; face de encaixe para (+x, +y). `power_connector_rotation_deg` (-45) passa a ser o eixo através das fileiras. Corpo de 11,5 (derived) por 9,7 (inferred). Abertura da carcaça centrada no corpo: z de 6,2 a 28,05 (antes 9,07 a 30,93); no encaixe o canal desce até a abertura. Âncora da abertura em (204,25; 137,16; 17,13); âncora do conector no centro da face de encaixe (197,33; 130,24; 17,13). |
| Âncora de energia | `anchor.power.vrm.gpu.1` em (153,39; 31,05; 8,6): segundo estágio da borda dos contatos, conferido com a grade nova (o modelador propôs 153,4; 29,31; 8,6). |
| Peças sem dono | receptáculo do J3 (verso, 24,7 x 6,9, centrado em (128,1; 26,9), de z 5,07 a 6,1) e conector de 4 vias (frente, u 34,8, v 116,7) ficam dentro de `pcb.smd`, com linhas próprias no CSV. Motivos: não têm item na proposta aprovada (peça nova passa pelo gate humano) e o `blockout.py` para com erro diante de peça sem construtor. Proposta para o próximo gate: `pcb.j3_receptacle` (filha de `pcb.main`, E7, derived) e `io.fan_header` (filha de `pcb.main`, E7, existência derived, função inferred). |
| Furos do adaptador | 4 com anel, 1 no lóbulo e 2 na faixa, em coordenadas de placa a partir do J3 e da borda dos dedos, divididos pelo fator (`iface_adapter_*_hole_*`). Os valores do modelador estavam com a altura comprimida por 0,9439 (para bater com o 34,5 antigo) e com o J3 em 125. |
| J3 | interface `iface_j3_center_x` = 128,1 (pelo receptáculo medido no PCB) e `iface_j3_center_y` = 26,9 (pelo adaptador, que fica em y = 0); `pcie_adapter_connector_x` e `_center_y` seguem. A proporção de gn-05 (contatos de 48 a 131) prefere cerca de 125: em aberto. |

### 12.4 Pendências de interferência resolvidas no contrato

| Pendência | Resolução |
|---|---|
| Adaptador dentro das camadas da face B, tampas e aro | o adaptador sobe para o plano da `pcb.plate` (z 2,5 a 4,07). A `pcb.plate` ganha recorte no contorno da aba e do J3 (folga 0,5); a tampa inferior, um rebaixo sobre a aba com fundo em z 1,3, onde cabem a presilha e as cabeças do E4 (vistas ao tirar as tampas, gn-22); a face B e o aro, o recorte da faixa de `iface_adapter_x_min` a `_max` até z 4,07; a parede inferior da carcaça, uma fenda para a faixa. A diagonal da aba passa a 1,5 mm do furo de canto da `pcb.plate`, o que sustenta a leitura. |
| J3 atravessando a `pcb.plate` | resolvida pelo recorte acima; o J3 tem 2,03 mm de altura combinada (plugue 1,0, receptáculo 1,03; divisão inferred). |
| Cabeças do E5 sob as tampas | rebaixos na face B e nas tampas, de 5,0 + 2 x 0,3 de diâmetro, com fundo em z 0,7. |
| Mola e memória do verso em 2,1 mm; mola contra `pcb.back_frame` (0,60) | a mola assenta na `pcb.back_frame` (0,8): z 4,1 a 5,3; as cabeças do E6 ficam sob ela (3,2 a 4,1) em furos de alívio da `pcb.plate`. No plano, o anel não passa sobre os chips: no máximo 70,1 x 57,0 (`leaf_spring_ring_max_*`). |
| Parafuso do aro sem furo | o aro ganha furo onde o parafuso ficar, com a cabeça no recuo da placa de extremidade. Falta referência para a posição: gn-16 em resolução maior, o quadro do vídeo da GN no passo 2, ou a ponta do bracket fotografada sem o bracket. |
| Seção central de 122,0 contra o PCB | resolvida pela correção de escala (sobra 1,03 por lado). |
| Package contra memória | resolvida pela grade da arbitragem. |
| Furo da mola sob o `power.connector` | continuava com o conector em pé (a base das lâminas chega a 12,25 mm atrás do centro; o furo ficava a 13,1). O centro do conector andou 2,5 mm ao longo da direção de encaixe, para (193,26; 126,17): o furo fica 0,35 mm livre de uma coluna de raio 3, o encaixe na carcaça não muda e o corpo fica abaixo do fundo do canal. |
| Indutor isolado sobre o furo da `pcb.plate` | continua (cerca de 1,3 mm) com a escala corrigida. Registrada a omissão da coluna roscada da `cooler.base` nesse furo (211,34; 125,86), que é o candidato a furo não confirmado pelo visual-qa. |

### 12.5 Interior do cooler

- **Passo das aletas:** `fin_pitch` passa de 1,6 (prática de mercado) para 1,52 ± 0,07 (`derived`, período das listras em `pny/back` e `pny/front`), e a contagem segue a geometria: 59, 57 e 42 (`count` com procedência `inferred`, porque ler as listras como aletas e não como lâminas da grade é inferência). Escolhido medir em vez de só ajustar a contagem: havia uma referência, e o passo de mercado não tinha nenhuma.
- **Tubos:** comprimentos desenvolvidos de 135,5 e 144,9 em linhas novas; `heatpipe_length_per_side` fica em 110 como trecho reto do blockout, porque 144,9 tiraria o tubo reto da placa e a conferência do envelope falharia.
- **Linhas novas:** `contact_plate_t` 1,0, `base_frame_t` 4,0, `iface_heatpipe_axis_z` 18,7, `heatpipe_pitch_stack` 18 (derived, 5090 FE), `heatpipe_pitch_chamber` 12,5; `vapor_chamber_thickness` (4) passa a ser câmara mais face de contato (3 + 1).
- **Pilha central:** `fin_stack_center_length_x` (64) marcada como pendente de medida.

### 12.6 O que cada script precisa refazer

- `io_parts.py`: ler `bracket_top_below_shroud_top`, `dp_row_center_z`, `dp_row_from_bracket_tip` e `dp_port_pitch` do CSV; posicionar o adaptador por `iface_j3_center_x` com as alturas da arbitragem (sem o 0,9439); adaptador em z 2,5 e plugue até `iface_j3_mating_z`; conector de energia no centro novo.
- `pcb_layout.py` e `pcb.py`: contorno, furos e grade novos; girar os 2 chips da borda dos contatos; corrigir pelo fator as posições que tirou das fotos (indutores, estágios, cantos do contorno, conector de 4 vias); modelar o receptáculo do J3 e o conector de 4 vias em `pcb.smd` pelas linhas novas; `pcb.back_frame` com 0,8.
- `frame.py`: recorte da face B e do aro por `iface_adapter_x_min` e `_max` até `iface_adapter_board_z_max`; fenda na parede inferior; rebaixos sob as cabeças do E5 e sobre a aba; abertura do conector pela âncora nova (o canal tem de descer até z 6,2 no encaixe); furo do aro.
- `cooler.py` (em andamento, não editado): mola em `iface_spring_z_*`; contorno da `cooler.base` novo; colunas conforme 12.4.
- `blockout.py`: continua gerando com o CSV novo (só lê chaves que existem); para acompanhar, usar `iface_adapter_x_min`, os rebaixos e a mola nova, girar os chips da borda dos contatos e pôr o conector de pé.
- `viewer/public/data/measurements.json` precisa ser regenerado.

### 12.7 Em aberto

- J3 em 128,1 (receptáculo medido) contra cerca de 125 (proporção de gn-05): medir os contatos no `pny/front`. Se der 125, o chip vai para perto de 149 (dentro da tolerância do X) e o PCB anda junto.
- Qual furo de canto não foi confirmado; a posição do indutor isolado.
- Passo das aletas: listras são aletas ou lâminas da grade.
- Posição do parafuso do aro; a presilha (`pcie.clamp`) e as peças novas propostas em 12.3 dependem do gate humano.
- Nada desta seção foi auditado.
