---
tipo: secao
status: rascunho
secao: O SM por dentro
ordem: 6
nivel: chip
part_id: chip.sm
procedencia_esperada: derived
itens_enunciado: [pipeline, unidades de execução]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 06 - O SM por dentro

## Objetivo
Abrir um SM e mostrar suas unidades: núcleos CUDA, Tensor Cores, RT Core, unidades de textura, FP64, registradores e memória local.

## Itens do enunciado cobertos
- pipeline
- unidades de execução

## Já confirmado na fonte primária
- Por SM: 128 núcleos CUDA FP32, 4 Tensor Cores de 5ª geração, 1 RT Core de 4ª geração, 4 unidades de textura ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9).
- Por SM: 256 KB de banco de registradores e 128 KB de L1/memória compartilhada ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9).
- FP64: 2 núcleos por SM, a 1/64 da taxa da FP32 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], nota da Fig. 3).
- Tensor Cores: FP16, BF16, TF32, INT8, FP8, e novos FP4 e FP6 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 15).

## A levantar
- Quantos escalonadores de warp o SM tem e como as unidades se dividem entre eles? (Figura 5 do whitepaper, p. 10, ainda não detalhada)
- Qual a profundidade do pipeline e a latência das instruções? (microbenchmarks de gerações anteriores)
- Como o SM emite instruções para as unidades?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> Profundidade e latências do pipeline vêm de medições em gerações anteriores, não de documento oficial da Blackwell. Ficam como derivadas.

Anterior: [[05 - Modelo de execução SIMT]] | Próxima: [[07 - Registradores]]
