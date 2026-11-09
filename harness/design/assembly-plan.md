# Plano de montagem da placa real (v0.2)

Estado: **plano para a F2**, ainda sem `assembly.json`. Substitui a visão genérica da v0.1 ("backplate, shroud, ventilador, cooler, PCB") pela estrutura que as fontes mostram para a RTX PRO 6000 Blackwell Workstation Edition.

Base de fatos: `harness/spec/sources/physical-card-sources.md` (rodada de 2026-11-09) e as fontes já auditadas. A auditoria desta rodada está em `harness/qa/fact-check-fisico.md`. Este documento **não é a proposta de engenharia**: o que é lacuna fica marcado "a propor" e vai para o `architecture-inferencer` com a skill `gpu-assembly-proposal`, com gate humano.

## 1. O que a v0.1 supunha e o que as fontes mostram

| Tema | Suposição da v0.1 | O que as fontes mostram | Efeito no projeto |
|---|---|---|---|
| Cooler | "dual-slot, active", com heatpipes e aletas, um ventilador | "Double-flow-through", dois ventiladores na mesma face, ar por "dual axial pathways" (datasheet; Gamers Nexus) | o cooler é a estrutura da placa, não uma peça apoiada sobre o PCB |
| PCB | uma placa de circuito no comprimento da placa | adaptador PCIe separado e cabos flat (Gamers Nexus). Arranjo em três placas é oficial só para a RTX 5090 FE | `pcb-layout-modeler` deixa de modelar "o PCB" e passa a modelar um conjunto de placas |
| Origem das coordenadas | canto do PCB | o PCB principal não define o contorno da placa | origem passa a ser um canto do **envelope** da placa |
| Ordem de desmontagem | backplate, shroud, ventilador, cooler, PCB | sete passos do teardown desta placa, em que o PCB sai por último (seção 3) | `assembly-planner` segue a ordem real |
| Interface térmica | não definida | pasta térmica no die desta placa; a RTX 5090 FE usa metal líquido | exemplo real de que "derivar da placa irmã" pode errar: entra no vídeo |
| Memória | "chips em volta do die" | 32 posições, 16 no verso (Gamers Nexus) | conta fecha com 96 GB e 512 bits (seção 5) |
| Conector | "16 pinos (12V-2x6)" de memória | "1x PCIe CEM5 16-pin" (datasheet). O nome 12V-2x6 vem de revisores | usar o nome do datasheet no texto |

## 2. Árvore de peças

Colunas: **Existe** é a procedência de a peça existir nesta placa. **Forma** é a procedência da geometria que vamos modelar. **Fid.** é o nível de fidelidade (seção 4). "5090 FE" quer dizer derivado da GeForce RTX 5090 Founders Edition, que usa o mesmo chip e, segundo a Puget Systems, uma carcaça "quase idêntica".

### 2.1 Estrutura e exterior

| id | Peça | Existe | Forma | Fid. | Fonte | Lacuna |
|---|---|---|---|---|---|---|
| `card` | conjunto montado | confirmed | derived | A | datasheet: 5,4" x 12", dois slots | espessura em mm |
| `frame.backplate` | placa traseira | confirmed | derived (fotos) | A | Gamers Nexus, passo 1 | material, textura, aberturas |
| `frame.shroud` | moldura externa | confirmed | derived (fotos) | A | Gamers Nexus, passo 2; capa do datasheet | material, acabamento |
| `frame.center_covers` | tampas centrais | confirmed | derived (fotos) | B | Gamers Nexus, passo 3 | quantidade, forma |
| `io.bracket` | bracket com 4 DisplayPort 2.1b | confirmed | derived (norma e fotos) | A | datasheet, p. 3 | disposição das portas, grade |
| `fasteners.*` | parafusos | confirmed | a propor | C | Gamers Nexus (sem tipos) | tipos e quantidades |

### 2.2 Refrigeração

| id | Peça | Existe | Forma | Fid. | Fonte | Lacuna |
|---|---|---|---|---|---|---|
| `cooler.fan.1`, `cooler.fan.2` | dois ventiladores axiais na mesma face | confirmed | derived (fotos) | A | Gamers Nexus; datasheet ("dual axial pathways") | diâmetro, número de pás |
| `cooler.fins.1`, `cooler.fins.2` | pilhas de aletas atravessadas pelo ar | confirmed | derived (fotos) | A | Gamers Nexus (aletas mais altas onde termina a placa do PCB, com depressão) | contagem, passo, material |
| `cooler.vapor_chamber` | câmara de vapor | derived | a propor | B | 5090 FE (página NVIDIA: "3D Vapor Chamber with integrated heat pipes"); Jon Peddie descreve, sem abrir a placa | nenhum teardown desta placa mostra o interior |
| `cooler.leaf_spring` | mola de pressão sobre a GPU | confirmed | a propor | B | Gamers Nexus, passo 6 | forma |
| `gpu.tim` | pasta térmica | confirmed | illustrative | C | Gamers Nexus | |
| `mem.pads` | pads térmicos sobre a memória e parte dos indutores | confirmed | a propor | C | Gamers Nexus | espessura, contorno |

### 2.3 Eletrônica

| id | Peça | Existe | Forma | Fid. | Fonte | Lacuna |
|---|---|---|---|---|---|---|
| `pcb.main` | PCB principal | confirmed | a propor | A | Gamers Nexus, passo 7 | dimensões, contorno, posição do chip |
| `pcb.plate` | placa que cobre o PCB | confirmed | a propor | B | Gamers Nexus, passo 5 | função e forma |
| `pcie.adapter` | adaptador PCIe com pinagem própria | confirmed | derived (norma e fotos) | A | Gamers Nexus, passo 4 | dimensões |
| `pcie.clamp` | grampo do suporte do slot | confirmed | a propor | C | Gamers Nexus, passo 4 | forma |
| `flex.*` | cabos flat entre as placas | confirmed | a propor | B | Gamers Nexus, passo 6 | quantidade e trajeto |
| `io.board` | placa das saídas de vídeo | derived | a propor | B | 5090 FE ("3-piece PCB", NVIDIA) | não confirmada nesta placa |
| `gpu.package` | GB202 (marcação "GB202-870-A1") | confirmed | a propor | A | Gamers Nexus; whitepaper (die de 750 mm²) | dimensões do package e do die visível |
| `mem.back.1..16` | 16 chips GDDR7 no verso | confirmed | derived (norma) | A | Gamers Nexus | fabricante, posição exata |
| `mem.front.1..16` | 16 posições na frente (32 no total) | confirmed (contagem) | derived (norma) | A | Gamers Nexus ("32 total memory locations") | posição exata |
| `power.connector` | um conector "PCIe CEM5 16-pin" | confirmed | derived (norma) | A | datasheet, p. 3. Posição "no topo, no meio": Jon Peddie | ângulo, posição exata |
| `power.inductors` | indutores | confirmed | a propor | B | Gamers Nexus (metade coberta por pad) | quantidade |
| `power.vrm.gpu`, `power.vrm.mem` | fases de energia | inferred | a propor | B | nenhuma fonte desta placa. Para a 5090 FE as fontes divergem (30, 27 ou 34) | **tudo** |
| `pcb.smd` | componentes pequenos (capacitores, resistores) | confirmed ("PCB muito denso") | illustrative | C | Gamers Nexus | não serão contados |

Regra: nenhuma peça "a propor" entra em `assembly.json` sem passar pela `gpu-assembly-proposal` e pelo gate humano. Peça com **Existe** `derived` ou `inferred` aparece no vídeo com o selo correspondente, mesmo que a forma fique convincente.

## 3. Ordem de desmontagem e estágios de explosão

A ordem vem do teardown desta placa (Gamers Nexus). Os estágios E1 a E7 são `confirmed` quanto à ordem. A direção e a distância de cada explosão são escolha de direção de arte.

| Estágio | O que sai | Peças | Procedência da ordem |
|---|---|---|---|
| E1 | placa traseira | `frame.backplate` | confirmed |
| E2 | um parafuso, depois a moldura externa | `frame.shroud` | confirmed |
| E3 | parafusos em volta do centro e tampas centrais | `frame.center_covers` | confirmed |
| E4 | grampo do slot e adaptador PCIe | `pcie.clamp`, `pcie.adapter` | confirmed |
| E5 | placa que cobre o PCB | `pcb.plate` | confirmed |
| E6 | cabos flat e parafusos da mola de pressão | `flex.*`, `cooler.leaf_spring` | confirmed |
| E7 | PCB principal, com a pasta térmica à vista | `pcb.main`, `gpu.package`, `mem.*`, `power.*` | confirmed |
| E8 | cooler aberto: ventiladores, aletas, câmara de vapor | `cooler.*` | **inferred**: nenhum teardown desta placa abre o cooler |

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
| Memória: 32 posições × 3 GB = 96 GB | fecha | 32 e 96 GB `confirmed`; 3 GB por chip é `derived` (divisão) |
| Barramento: 16 controladores × 32 bits = 512 bits; 32 chips ÷ 16 controladores = 2 chips por controlador | fecha, e indica dois chips por canal (um em cada face) | 512 bits e 16 controladores `confirmed`; o arranjo em duas faces é `derived` |
| Banda: 28 Gbps × 512 ÷ 8 = 1.792 GB/s | fecha | `confirmed` (whitepaper e datasheet) |
| Envelope: 5,4" × 12,0" = 137,2 × 304,8 mm | conversão | polegadas `confirmed`, milímetros `derived` |
| Espessura em mm de "dois slots" | **não fecha ainda** | as fontes da 5090 FE divergem (2 slots, 42 mm, 61 mm de folga). Registrar a norma de slot antes de modelar |
| Energia: 600 W pelo conector e pelo slot | **não fechada** | falta registrar a norma do conector de 16 pinos e a potência do slot. Sem isso, nenhuma corrente entra no texto |
| Térmica: área de aletas e vazão para 600 W | **não fechada** | depende da proposta do interior do cooler |

## 6. Como medir sem ter a placa na mão

1. **Envelope oficial** como escala: 137,2 × 304,8 mm.
2. **Normas** para o que é padronizado: bracket e contatos PCIe, conector de 16 pinos, conector DisplayPort, encapsulamento GDDR7. As normas ainda **não estão registradas** em `spec/sources/`. Nenhuma medida de norma entra antes disso.
3. **Proporção em foto**: em vista quase ortogonal, mede-se em pixels contra o envelope conhecido. O resultado é `derived`, com tolerância declarada, e a foto usada fica citada.
4. **Análogo** (5090 FE) só para o que não aparece em nenhuma foto desta placa. Resultado `derived`.
5. **Proposta de engenharia** para o resto. Resultado `inferred`.

Tudo vai para `design/measurements.csv`: `feature, value_mm, tolerance_mm, method, source, provenance`. Os modeladores leem dessa tabela. Número solto no script é erro de lint.

### 6.1 Pacote de referências visuais

`spec/references/index.md` lista, por vista, a URL da imagem e o que ela mostra. Imagens não são versionadas (direitos de terceiros); ficam em cache local ignorado pelo git.

| Vista necessária | Temos hoje |
|---|---|
| três quartos da placa montada | capa do datasheet (render oficial) |
| face dos ventiladores, traseira, topo com o conector, bracket, extremidade | **não catalogado** |
| cada um dos estágios E1 a E7 | 35 capturas do teardown da Gamers Nexus, **sem catálogo**: ninguém olhou ainda o que cada uma mostra |
| PCB frente e verso | provavelmente entre as 35 capturas, a conferir |
| cooler aberto | **não existe** fonte para esta placa |

Primeira tarefa da F2: catalogar as 35 capturas e achar fotos de produto das vistas que faltam. Sem isso o `visual-qa` não tem com o que comparar.

### 6.2 Critério de aceite da fidelidade

- Envelope do GLB igual ao oficial, com erro de até 0,5 mm.
- Toda contagem visível em peça de nível A igual à da fonte, ou marcada "representativa" na tela.
- Para cada vista padrão com foto de referência, o `visual-qa` recebe o render na mesma vista ao lado da foto e aprova contorno, proporção e posição relativa.
- Toda diferença conhecida entra na lista "desvios conhecidos" do `assembly.json`, com o motivo.

## 7. Ajustes de contrato achados em teste (2026-11-09)

Testado neste ambiente com `build123d` 0.13.0 e `trimesh` 5.2.0 em Python 3.13: uma caixa com o envelope da placa foi exportada para STEP e GLB sem erro.

| Achado | Contrato da v0.1 | Correção |
|---|---|---|
| O GLB sai em **metros** e com **Y para cima** (padrão glTF): a caixa de 304,8 × 137,2 × 40,64 mm saiu com 0,30 × 0,04 × 0,14 | "unidades em mm, Z para cima" para tudo | CAD, `assembly.json` e `storyboard.json` em mm e Z para cima. A conversão para o referencial do GLB acontece em um único lugar, no `integrator`, e o viewer lê âncoras e câmeras já convertidas |
| A caixa exportada **não passa** no teste de malha fechada do `trimesh` (24 vértices, faces soltas). Depois de unir vértices, passa (8 vértices) | `ops-runner` exige "malha fechada" | validar o sólido no CAD (`is_valid`, volume maior que zero) e, no GLB, unir vértices antes do teste |
| `build123d` e `trimesh` não estão instalados nem declarados | "stack" só descrita em texto | versionar `harness/requirements.txt` e `harness/viewer/package.json` com versões fixas |
| Origem `pcb.bottom_left_front` | o PCB define o contorno | origem `card.envelope_min`: canto do envelope do lado da bracket e do lado dos contatos PCIe |

Campos novos por peça em `assembly.json`: `stage` (E1 a E8), `fidelity` (A, B ou C), `exists_provenance` e `shape_provenance` (as duas colunas da seção 2), `count` com `count_provenance`, e `measurements` (ids de `measurements.csv`).

## 8. Fila para o `architecture-inferencer` (F2)

Por ordem de impacto no vídeo:

1. Interior do cooler: câmara de vapor, ligação com as duas pilhas de aletas, caminho do calor.
2. PCB principal: contorno, dimensões, posição do GB202, das 32 posições de memória e do conector.
3. Quantas placas são e como os cabos flat as ligam (três, como na 5090 FE?).
4. Fases de energia da GPU e da memória, com a conta de potência.
5. Package do GB202: dimensões e moldura.
6. Parafusos: tipos e quantidades por estágio.
7. Ventiladores: diâmetro e número de pás (primeiro tentar medir por foto).
