---
tipo: secao
status: rascunho
secao: Planta do chip
ordem: 4
nivel: chip
part_id: chip.floorplan
procedencia_esperada: confirmed
itens_enunciado: [visão geral]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 04 - Planta do chip

## Objetivo
Mostrar como o GB202 está organizado: GPCs, TPCs, SMs, L2 e controladores de memória.

## Itens do enunciado cobertos
- visão geral

## Já confirmado na fonte primária
- Chip completo: 12 GPCs, 96 TPCs, 192 SMs e 24.576 núcleos CUDA ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 8).
- Na RTX PRO 6000: **94 TPCs, 188 SMs e 24.064 núcleos CUDA** ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4). Contas: 94 × 2 = 188 e 188 × 128 = 24.064.
- GPC: 1 Raster Engine, 2 partições de ROP com 8 ROPs cada e 8 TPCs. TPC: 1 PolyMorph Engine e 2 SMs ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9).
- L2 de 128 MB (131.072 KB) ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9).
- 92,2 bilhões de transistores, 750 mm², processo TSMC 4N customizado ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4).

## A levantar
- Como os blocos se ligam entre si (rede interna, crossbar) e aos controladores de memória?
- Onde ficam os motores de vídeo, o AMP e a interface PCIe no chip?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> O desenho do chip no viewer é um diagrama proporcional às contagens oficiais. A posição física real de cada bloco no die não é pública em detalhe, então o desenho é ilustrativo.

Anterior: [[03 - Memória e barramentos]] | Próxima: [[05 - Modelo de execução SIMT]]
