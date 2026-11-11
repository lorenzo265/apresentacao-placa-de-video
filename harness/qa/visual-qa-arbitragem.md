# Visual-QA: arbitragem de medidas em conflito (2026-11-11)

- Autor: agente `visual-qa` (Opus), em contexto separado dos modeladores. Só mediu; não editou o repositório.
- Escopo: três conflitos entre `design/measurements.csv` (medição de 2026-11-10, `visual-qa-referencias-modelagem.md`) e as remedições dos modeladores do PCB e das peças de I/O, mais um registro sobre a altura da carcaça.
- Scripts e capturas de trabalho: pasta `vq3/` do scratchpad da sessão (não versionada).

## Achado transversal: medidas tiradas de `chiphell/pcb-a.jpg` saem cerca de 1,3% grandes
A homografia pela grade da base é boa (resíduo RMS de 0,07 mm), mas o que está sobre o PCB sai maior que o real. Quatro indícios independentes:
- passo dos dedos PCIe (norma: 1,00 mm) medido em 1,0105 mm por FFT em 64 mm;
- zona dos dedos no CSV com 85,5 contra 84,3 da norma (+1,4%);
- passo das esferas GDDR7 medido em 0,762 por 0,741 mm contra 0,75 por 0,73 da Micron (`spec/sources/standards-sources.md`, seção 9), +1,3% a +1,6%; a contagem bate com a pegada (266 esferas);
- furos da mola: 77,3 medidos contra 76,4 da Alphacool.

Causa provável: o PCB fica 1,6 mm acima da base e a câmera estava a cerca de 15 cm. Fator adotado: 1,013 ± 0,004 (aparente sobre real). Nem a medição anterior nem os modeladores corrigiram isso. Afeta todas as linhas tiradas do `pcb-a`, inclusive o contorno do PCB, o centro do chip e os furos da mola, que precisam de remedição.

## 1. Grade da memória
| Origem | Passo | Borda de energia | Lado do bracket |
|---|---|---|---|
| CSV | 13,3 / 13,0 | v 95,7 | u 11,2 |
| Modelador do PCB | 14,1 a 14,2 | v 97,75 | u 9,1 |
| Alphacool | 13,5 (pad de 67,5 / 5) | | |
| **Arbitragem** | **13,95 ± 0,15** | **v 97,0** | **u 10,1** |

Método: as duas faces retificadas no referencial do chip (centro e giro pelos 4 furos da mola, resíduo de 0,02 mm); dois métodos independentes (centro do campo de esferas por picos de coluna com subpixel; período global por autocorrelação), que concordam em 14,10 a 14,15 na escala da base; corrigido pelo fator, 13,95.

Causas: o modelador do PCB mediu certo na escala da base, sem o fator. O CSV tinha erro de leitura: os rótulos do recorte usado tinham a origem deslocada (cerca de +1,6 mm em u e -2,7 mm em v); `mem_side_opposite_u` de 98,2 é cerca de 95,2. A Alphacool não dá passo: 4 x 13,95 + 12 = 67,8 bate com o pad.

Consequência: o conflito do package com a fileira de memória some (vão de 58,1 mm para o package de 57,5).

## 2. Passo das DisplayPort
CSV 19,5; modelador 20,88; **arbitragem 20,9 ± 0,4**. Em `storagereview/sr-1.jpg` o período das portas por autocorrelação é 133,27 px; duas escalas concordam (comprimento do bracket de 120,02 mm até a dobra; línguas de 20,32 mm da norma), dando 21,05. `jpr/F2.jpg` dá 20,6 (imagem pequena) e o desenho do guia rápido, 20,5 a 20,8. Limite físico: com 19,5 o contorno interno da abertura daria 15,8 mm, menor que o receptáculo de 16,1 (valor de fonte secundária). O 19,5 veio de usar como régua uma feição maior que o receptáculo.

Medidas vizinhas: topo do bracket a **28,6 ± 1,0** mm abaixo do topo da carcaça (o modelador deu 27,0, provavelmente medindo depois da dobra); centro da fileira de portas em **z 13,5 ± 0,7** a partir da face oposta aos ventiladores (o modelador deu 15,3).

## 3. Alturas do adaptador PCIe
| Origem | Faixa | Sem lóbulo | Com lóbulo | Comprimento |
|---|---|---|---|---|
| CSV | 17,5 | 34,5 | 38 | 102 |
| Modelador de I/O | 18,45 | 36,55 | 40,18 | 102,2 |
| **Arbitragem** | **17,4** | **36,2** | **38,8** | **101,4** |

Método: homografia anterior com perfis de borda; nas bordas viradas para a câmera a borda externa já é a posição real (aparece a parede do PCB); nas outras, fator 1,0105 tirado dos dedos do próprio adaptador; borda dos dedos é a borda da placa, não o fim do dourado. Zona dos dedos corrigida: 84,6.

## 4. Altura da carcaça (registro)
Em `pny/front.png`, pelas linhas sem o bracket: 123,3 mm, o que confirma o integrador; com a aba incluída: 122,7, o viés da medição de 122,4 do modelador. O 124 da medição anterior não tem esse viés (seu erro de +0,6% é outro, não reconstruído). O viés não passa para as medidas do `pcb-a`.

## Linhas propostas para `measurements.csv`
`mem_side_v_pitch` 13,95 (0,15); `mem_power_edge_u_pitch` 13,95 (0,15); `mem_side_bracket_u` 10,1 (1,0); `mem_side_opposite_u` 95,2 (1,0); `mem_side_v_first` 33,1 (1,0); `mem_power_edge_v` 97,0 (1,0); `mem_power_edge_u_first` 31,8 (1,0); `mem_contact_edge_v` 25,9 (1,0); `mem_contact_edge_u_1` 33,3 (1,0); `mem_contact_edge_u_2` 72,1 (1,0); criar `mem_rows_du_from_gpu` 42,55, `mem_power_edge_dv_from_gpu` 36,0, `mem_contact_edge_dv_from_gpu` 35,1 (0,2 cada); `mem_footprint_along_row` 12 e `mem_footprint_across_row` 14 (0,5; na borda dos contatos o chip gira); criar `chiphell_pcb_a_scale_factor` 1,013 (0,004, sem unidade); `dp_port_pitch` 20,9 (0,4); criar `bracket_top_below_shroud_top` 28,6 (1,0) e `dp_row_center_z` 13,5 (0,7); `pcie_adapter_strip_height` 17,4 (0,5); `pcie_adapter_total_height` 38,8 (0,6); `pcie_adapter_total_height_without_lobe` 36,2 (0,6); `pcie_adapter_length` 101,4 (0,6); `pcie_finger_zone_total` 84,6 (0,8). Furos da mola, pela mesma correção: cerca de 62,9 x 76,3. Todas `derived`.

Os valores absolutos de u e v herdam `gpu_center_u` 52,7 e `gpu_center_v` 61,0, que estão na escala da base e não foram remedidos. Uma checagem rápida sugere que o PCB pode ter menos que 119,6 mm no comprimento (Alphacool: 117,6); não verificado.

## O que não foi verificado
Homografia própria da foto da frente (`pcb-b`) pela grade; distorção da lente; posição exata da câmera; a norma VESA e o desenho do receptáculo Molex (fechariam o passo das DisplayPort sem depender do bracket).
