# Visual-QA: medição das referências novas para a modelagem (2026-11-10)

- Data: 2026-11-10
- Autor: agente `visual-qa` (Opus), em contexto separado. Só mede e reporta; não editou o repositório.
- Escopo: as referências baixadas em 2026-11-10 para `harness/spec/references/cache/` (não versionada): PCB nu com régua (Chiphell), PCB com componentes (blog sabareesh), renders quase ortogonais (PNY), renders em perspectiva (Puget), fotografias (StorageReview, Jon Peddie), water blocks (Alphacool, Bykski, Optimus) e a placa irmã (RTX 5090 Founders Edition). Fontes descritas em `harness/spec/sources/physical-card-sources.md`, seção 18, e em `harness/spec/references/batedores/`.
- **Conclusão principal: a decisão D8 da proposta (PCB de 108 x 112 mm, tolerância de 10 mm, "medir antes de travar") não se sustenta.** O PCB mede cerca de 119,6 mm no comprimento da placa por 121,5 mm na altura, com tolerância de 1,5 mm. Duas fontes independentes concordam: a foto com régua e o desenho do PCB no manual da Alphacool. Também estão errados no modelo atual o padrão dos 4 furos em volta do chip, a orientação do package do chip e a posição das memórias.
- Todas as medidas são `derived` (foto ou render de terceiros), com tolerância explícita.
- Recortes, imagens retificadas e scripts do auditor: `harness/spec/references/cache/visualqa/` (não versionada). A principal é `a_board.png`: a foto do verso do PCB retificada no referencial do PCB, a 10 px/mm.

## Método
- **Homografia pela grade da base de corte** na foto `chiphell/pcb-a.jpg`: 266 interseções da grade de 10 mm; resíduo RMS de 0,066 mm, máximo de 0,43 mm. A escala local varia cerca de 7% entre os cantos, por isso a imagem foi retificada em vez de usar uma escala única.
- **Giro do PCB sobre a base:** 1,2 a 1,8 grau conforme a borda; segunda retificação alinhada ao PCB. Cisalhamento residual de cerca de 0,5 grau (até 1 mm em 120 mm).
- **Validação por norma:** os contatos da placa adaptadora PCIe somam 85,5 mm (segmento curto de cerca de 12 mm, chave de cerca de 1,5 mm, segmento longo de cerca de 72 mm). A CEM 3.0 dá 12,15 mais 72,15 mm. Erro de escala abaixo de 1%.
- **`chiphell/pcb-b.jpg`:** sem homografia própria; régua interna pelo padrão de furos medido na outra foto.
- **Renders da PNY:** quase ortogonais (os dois ventiladores diferem 1% em diâmetro; os contatos saem 2,4% menores que a norma). Incerteza de 2 a 3%.
- **Referencial do PCB:** origem no canto entre a borda do lado do bracket e a borda dos contatos. x' segue o comprimento da placa; y' segue a altura, a partir da borda dos contatos PCIe.

## Identidade do PCB do Chiphell
Sustenta que é a Workstation Edition: placa PCIe separada com conector de placa a placa, igual à adaptadora da captura gn-25; formato quase quadrado com o chip centrado no padrão de furos, que bate com o desenho da Alphacool para a "RTX 6000 Workstation Edition" (63,6 x 76,4 mm contra 63,7 x 77,8 mm medidos); 16 posições de memória por face no arranjo 5, 5, 4 e 2, como a contagem da Gamers Nexus no verso; conector de energia num canto chanfrado; e a foto do PCB com componentes do blog sabareesh (identificada pelo autor como esta placa) é o mesmo desenho.

Não excluído: a imagem não mostra SKU nem nome de modelo, e a placa está nua, ainda presa ao painel de fabricação (pode ser refugo ou protótipo). Nada na imagem contradiz a Workstation Edition. A moldura em volta é trilho de painel, não parte do produto.

## Medidas propostas
Formato das colunas de `measurements.csv`. Valores em mm, salvo onde indicado.

| feature | valor | tol. | método | fonte |
|---|---|---|---|---|
| pcb_main_length_x | 119,6 | 1,5 | homografia e alinhamento ao PCB | chiphell/pcb-a; Alphacool, manual p. 3 (117,6) |
| pcb_main_height_y | 121,5 | 1,5 | idem | chiphell/pcb-a; Alphacool (120,9); blocos de 119,4 e 121,82 |
| pcb_corner_chamfer_angle_deg | 45 graus | 4 | linha dos furos do conector e borda do chanfro | chiphell a e b |
| pcb_contact_edge_recess | 4 (de x' 43 a 63) | 1 | retificação | chiphell/pcb-a |
| gpu_center_from_pcb_bracket_edge | 52,7 | 1,0 | centro do padrão de furos e do BGA | chiphell; Alphacool (51,3) |
| gpu_center_from_pcb_contact_edge | 61,0 | 1,0 | idem | chiphell; Alphacool (60,5) |
| spring_holes_dx_length | 63,7 | 1,0 | centroides dos furos | chiphell/pcb-a; Alphacool (63,6) |
| spring_holes_dy_height | 77,8 | 1,0 | idem | chiphell/pcb-a; Alphacool (76,4) |
| corner_plated_holes_span | 106 x 102 | 1,5 | centroides de cobre (um furo não confirmado) | chiphell/pcb-a |
| gb202_bga_field_length | 64 | 1,5 | furos como régua | chiphell/pcb-b |
| gb202_bga_field_height | 57 | 1,5 | idem | chiphell/pcb-b |
| gb202_package_length | 67 | 3 | reforço mais substrato, PCB como régua | sabareesh/wb-bare-pcb |
| gb202_package_height | 59 | 3 | idem | sabareesh |
| mem_pitch | 13,3 | 0,5 | retificação; Alphacool dá 13,5 | chiphell/pcb-a; Alphacool |
| mem_bracket_end_row_x | 11,2 | 1,0 | 5 posições, y' de 31,8 a 85,0 | chiphell/pcb-a |
| mem_far_end_row_x | 98,2 | 1,0 | 5 posições, mesmos y' | chiphell/pcb-a |
| mem_power_edge_y | 95,7 | 1,0 | 4 posições, x' 35,9, 48,9, 61,9 e 74,9 | chiphell/pcb-a |
| mem_contact_edge_y | 24,2 | 1,0 | 2 posições, x' 34,4 e 72,9 | chiphell/pcb-a |
| mem_footprint | 13 x 15,5 | 1,0 | campo de esferas | chiphell/pcb-a |
| power_connector_rotation_deg | 45 graus | 4 | furos e corpo; face de encaixe para fora pelo chanfro | chiphell; sabareesh (41) |
| power_connector_center_x | 192 | 3 | conta: PCB a partir de x 99,3 mais a posição no PCB | chiphell; Alphacool, Fig. 1 (189) |
| pcie_adapter_length | 102 | 1,5 | retificação | chiphell/pcb-a |
| pcie_adapter_strip_height | 17,5 | 1,0 | idem | chiphell/pcb-a |
| pcie_adapter_total_height | 38 (34,5 sem o lóbulo) | 1,0 | idem | chiphell/pcb-a |
| pcie_adapter_connector_length | 24 | 1,0 | idem | chiphell/pcb-a |
| pcie_finger_zone_total | 85,5 | 0,8 | idem; valida a escala contra a norma | chiphell/pcb-a |
| shroud_height | 124 | 2 | razão no render vezes 304,8 | pny/front, pny/back |
| card_height_with_fingers | 135,7 | 2 | idem; sustenta a decisão D2 | pny/front |
| fan_ring_outer_diameter | 116,8 | 2 | render | pny/front |
| fan_centers_from_bracket | 58,5 e 242,8 | 2,5 | idem | pny/front |
| fan_blade_count | 7 | 0 | harmônico angular e contagem visual | pny; puget; storagereview/sr-4 (foto real) |
| x_cross_from_bracket | 151,5 | 2,5 | render (frente 150,4; verso 152,5) | pny |
| x_rib_angle_deg | 46,5 graus | 2 | render | pny |
| pcie_side_notch | de 138 a 158, profundidade 4 | 2 | render | pny/front |
| shroud_corner_radius | 18 | 4 | ajuste a uma só profundidade; leitura fraca | pny/front |
| rtx_pro_6000_text | centro a 122 do bracket, 24 abaixo do topo, 45 graus, 35 x 4,5 | 3 | render | pny/back |

Memória: 16 posições por face, 32 no total, no arranjo 5 (ponta do bracket), 5 (ponta oposta), 4 (borda superior, a do conector de energia) e 2 (borda dos contatos). Três confirmações: as duas fotos do Chiphell, a foto do blog sabareesh e a lista de pads da Alphacool (4 x 5 mais 2 x 4 mais 4 x 1 = 32).

Indutores marcados "85N" na face do chip (foto sabareesh), com incerteza de 2 por borda: cerca de 10 na borda dos contatos, 10 a 11 na ponta longe do bracket (em pares), cerca de 7 menores na borda superior; na ponta do bracket só 1 visível, o resto sob massa térmica. No verso não foi possível separar indutor de estágio de potência.

Exterior, pelos renders e fotos: 7 pás por ventilador (a sugestão de 9 estava errada; o blockout está certo); texto "RTX PRO 6000" só na face oposta aos ventiladores, dourado, a 45 graus; borda superior com um canal rebaixado, duas fendas longas, o encaixe do conector na ponta longe do bracket e o logotipo NVIDIA dourado; bracket de chapa lisa com 4 DisplayPort. A imagem 89589 da Puget **não é desta placa** (tem grade no bracket): não usar.

## Contradições com o modelo atual
| # | Severidade | Onde | Valor atual | O que a referência sugere |
|---|---|---|---|---|
| 1 | bloqueia | `pcb_main_width`, `pcb_main_height`, contorno da base do cooler | 108 x 112, só caixa | 119,6 x 121,5, com chanfro a 45 graus, recorte em V do conector e rebaixo na borda dos contatos |
| 2 | bloqueia | `iface_spring_holes_dx`, `dy`; contorno da mola | 78 x 84 | 63,7 x 77,8; a mola provavelmente está grande demais no comprimento |
| 3 | bloqueia | `gb202_package_x`, `y` | 56 x 63 | cerca de 64 a 67 no comprimento por 57 a 59 na altura: o eixo longo está trocado |
| 4 | ajusta | grade da memória | fileiras em u 18 e 90; primeira em v 26 com passo 15; borda dos contatos em v 16,5; borda do conector em u 31,5 com passo 15 | 11,2 e 98,2; 31,8 com passo 13,3; 24,2; 35,9 com passo 13 |
| 5 | ajusta | `gpu_center_u`, `gpu_center_v` | 54 e 56 | 52,7 e 61,0 |
| 6 | ajusta | `power.inductors` | 24 representativos, na borda dos contatos e na superior | falta a fileira de cerca de 10 da ponta longe do bracket; a borda superior tem cerca de 7 menores |
| 7 | ajusta | `power_connector_rotation_deg` e centro | 40 com tolerância de 20; centro em 195 | 45 com tolerância de 4, face de encaixe para fora pelo chanfro; centro em cerca de 192 |
| 8 | ajusta | `shroud_height_proposed` | 126 com tolerância de 4 | 124 com tolerância de 2 |
| 9 | ajusta | `pcb_main_card_x_min` | 98 | 99,3 se o chip ficar em x 152; as pontas de aletas deixam de ser simétricas (conta do auditor, a conferir) |
| 10 | nota | `iface_plate_holes` | 104 x 108 | os furos cobreados de canto dão cerca de 106 x 102; não está provado que fixem a placa que cobre o PCB |
| 11 | nota | catálogo | usa a Puget 89589 | não é desta placa |

## O que cada referência ainda não resolve
- **Chiphell:** identidade do produto (sem SKU na imagem), alturas de componente, e o que é indutor ou estágio de potência no verso.
- **Sabareesh:** a contagem na ponta do bracket (sob massa térmica); perspectiva não corrigida.
- **Alphacool:** ordem de desmontagem e parafusos do cooler original; placa de I/O. Escala do desenho tirada dos pads (2%).
- **Bykski e Optimus:** nenhuma medida de PCB (o desenho da Bykski não está em escala igual nos dois eixos; só as cotas valem).
- **PNY e Puget:** são renders; não dão a espessura nem o ângulo do conector na carcaça.
- **Placa irmã:** os tubos de calor continuam em "5 ou 10"; o interior do cooler desta placa continua sem fonte.
- **Não examinado nesta rodada:** as fotos do cooler aberto da 5090 (wccftech), os quadros do vídeo oficial da NVIDIA, a pasta `cache/nvidia/`, a maior parte das capturas `gn-*` e o quadro da oficina de reparo.

## As cinco correções que mais aumentam a fidelidade
1. Contorno real do PCB (119,6 x 121,5 mm, com chanfro, recorte do conector e rebaixo), com a base do cooler e a placa que cobre o PCB ajustadas junto.
2. Furos da mola em 63,7 x 77,8 mm e package com o eixo longo no comprimento da placa, centrado em (52,7; 61,0).
3. Memória 5, 5, 4 e 2 por face, passo de 13,3 a 13,5 mm, com as coordenadas da tabela, nas duas faces.
4. Conector de 16 pinos a 45 graus no canto, a cerca de 192 mm do bracket.
5. Carcaça de 124 mm de altura, X a 46,5 graus cruzando a cerca de 151,5 mm, texto "RTX PRO 6000" na face oposta aos ventiladores e fileira de indutores na ponta longe do bracket. Manter as 7 pás.

## Estado
Relatório recebido em 2026-11-10. As medidas ainda não entraram em `measurements.csv` nem em `assembly.json`: a revisão é do `assembly-planner`. A decisão D8 da proposta aprovada previa esta medição antes de travar o PCB.
