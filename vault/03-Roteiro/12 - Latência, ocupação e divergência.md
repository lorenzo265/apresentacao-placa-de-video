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
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - PTX ISA]]"]
---
# 12 - Latência, ocupação e divergência

## Objetivo
Mostrar como a GPU esconde latência com muitos warps, o que limita a ocupação do SM e o custo da divergência de ramos.

## Itens do enunciado cobertos
- pipeline

## Já confirmado na fonte primária
- Os recursos que limitam a ocupação por SM: 65.536 registradores de 32 bits (conta derivada de [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9) e 128 KB de L1/memória compartilhada.
- Conta teórica: um kernel com 10 registradores por thread usa 320 registradores por warp (32 threads). Com 65.536 registradores por SM, sobrariam até 204 warps se só os registradores limitassem. Os limites reais de warps por SM e a granularidade de alocação ainda faltam (guia CUDA).

## A levantar
- Quantos warps e threads cabem em um SM na Blackwell workstation? (tabela de capacidades do guia CUDA, a verificar)
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
