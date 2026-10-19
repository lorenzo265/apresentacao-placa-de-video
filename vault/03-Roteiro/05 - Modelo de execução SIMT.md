---
tipo: secao
status: rascunho
secao: Modelo de execução SIMT
ordem: 5
nivel: chip
part_id: chip.exec-model
procedencia_esperada: confirmed
itens_enunciado: [pipeline, modelo de programação]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 05 - Modelo de execução SIMT

## Objetivo
Explicar como um programa CUDA vira trabalho para milhares de unidades: threads, warps, blocos e grids, e o modelo SIMT.

## Itens do enunciado cobertos
- pipeline
- modelo de programação

## Já confirmado na fonte primária
- O SM cumpre as funções de escalonar warps, gerenciar memória e alimentar as unidades CUDA, Tensor e RT ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9). O documento não detalha o mecanismo.

## A levantar
- Qual é o tamanho do warp e como as threads de um bloco são agrupadas?
- Como blocos são distribuídos pelos SMs?
- O que é SIMT e em que ele difere de SIMD? (guia de programação CUDA, ainda não lido)

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `confirmed`. Confirmar com a fonte antes de virar texto final.

Anterior: [[04 - Planta do chip]] | Próxima: [[06 - O SM por dentro]]
