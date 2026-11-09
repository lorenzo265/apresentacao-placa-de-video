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
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]", "[[Jia et al. - Dissecting the NVIDIA Volta GPU]]"]
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
- **Quatro blocos por SM** ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Fig. 5, p. 10, figura vista em 2026-11-09). Cada bloco tem "L0 i-Cache + Warp Scheduler + Dispatch (32 thread/clk)", "Register File (16,384 x 32-bit)", núcleos "FP32 / INT32", um Tensor Core de 5ª geração, quatro unidades LD/ST e uma SFU. Embaixo, comuns aos quatro: "128 KB L1 Data Cache / Shared Memory", quatro unidades de textura e o RT Core. Contas: 4 × 16.384 = 65.536 registradores; 4 × 32 = 128 threads despachadas por ciclo.
- Derivado (RTX 5080, chip GB203): latência de 4 ciclos para instruções INT32 e FP32 ([[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture|Jarmusch et al.]], seção IV e Tab. III). As quatro partições que esse artigo mede coincidem com a figura oficial.
- Derivado (Volta): o escalonador de um warp é `id do warp mod 4` ([[Jia et al. - Dissecting the NVIDIA Volta GPU|Jia et al.]], seção 2.2). Ainda sem confirmação para a Blackwell.

## A levantar
- Qual é a política de escolha do warp em cada escalonador? (a NVIDIA não divulga; Huerta et al. inferem uma para a Ampere)
- Qual a profundidade do pipeline e a latência das instruções? (microbenchmarks de gerações anteriores)
- Como o SM emite instruções para as unidades?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]
- [[Jia et al. - Dissecting the NVIDIA Volta GPU]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> Profundidade e latências do pipeline vêm de medições em gerações anteriores, não de documento oficial da Blackwell. Ficam como derivadas.

Anterior: [[05 - Modelo de execução SIMT]] | Próxima: [[07 - Registradores]]
