---
tipo: secao
status: rascunho
secao: Latência, ocupação e divergência
ordem: 12
nivel: chip
part_id: chip.latency
procedencia_esperada: derived
itens_enunciado: [pipeline]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - Blackwell Tuning Guide]]", "[[NVIDIA - Guia de programação CUDA]]", "[[NVIDIA - PTX ISA]]"]
---
# 12 - Latência, ocupação e divergência

## Objetivo
Mostrar como a GPU esconde latência com muitos warps, o que limita a ocupação do SM e o custo da divergência de ramos.

## Itens do enunciado cobertos
- pipeline

## Já confirmado na fonte primária
- Os recursos que limitam a ocupação por SM: 65.536 registradores de 32 bits (conta derivada de [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9) e 128 KB de L1/memória compartilhada.
- Conta teórica: um kernel com 10 registradores por thread usa 320 registradores por warp (32 threads). Com 65.536 registradores por SM, sobrariam até 204 warps se só os registradores limitassem. Os limites reais de warps por SM e a granularidade de alocação ainda faltam (guia CUDA).

- **Limite oficial de ocupação:** no máximo 48 warps e 32 blocos por SM na compute capability 12.0, e 128 KB de memória compartilhada por SM ([[NVIDIA - Blackwell Tuning Guide|Blackwell Tuning Guide]] 13.5, 1.4.1.1, leitura direta em 2026-11-09). Conta nossa: 48 × 32 = 1.536 threads por SM e 288.768 na placa. O teto de 204 warps da conta teórica acima não vale: o limite real é 48.
- **Divergência:** as threads que não seguem o desvio "will be masked off" ([[NVIDIA - Guia de programação CUDA|guia CUDA]], lido por resumo).

## A levantar
- Exemplo numérico de ocupação com um kernel que usa N registradores por thread.
- O que é divergência de warp e como o hardware a trata?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - PTX ISA]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `derived`. Confirmar com a fonte antes de virar texto final.

Anterior: [[11 - Escalonamento, CPU e interrupções]] | Próxima: [[13 - O que a Blackwell mudou]]
