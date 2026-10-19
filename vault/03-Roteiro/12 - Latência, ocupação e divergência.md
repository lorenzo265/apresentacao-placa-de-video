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
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 12 - Latência, ocupação e divergência

## Objetivo
Mostrar como a GPU esconde latência com muitos warps, o que limita a ocupação do SM e o custo da divergência de ramos.

## Itens do enunciado cobertos
- pipeline

## Já confirmado na fonte primária
- Os recursos que limitam a ocupação por SM: 65.536 registradores de 32 bits (conta derivada de [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9) e 128 KB de L1/memória compartilhada.

## A levantar
- Quantos warps e threads cabem em um SM na Blackwell workstation? (tabela de capacidades do guia CUDA, a verificar)
- Exemplo numérico de ocupação com um kernel que usa N registradores por thread.
- O que é divergência de warp e como o hardware a trata?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `derived`. Confirmar com a fonte antes de virar texto final.

Anterior: [[11 - Escalonamento, CPU e interrupções]] | Próxima: [[13 - O que a Blackwell mudou]]
