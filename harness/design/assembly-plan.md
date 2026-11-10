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

