---
tipo: secao
status: rascunho
secao: Escalonamento, CPU e interrupções
ordem: 11
nivel: chip
part_id: chip.host-if
procedencia_esperada: derived
itens_enunciado: [interrupções, escalonamento]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - open-gpu-kernel-modules (interrupções e GSP)]]"]
---
# 11 - Escalonamento, CPU e interrupções

> [!todo] Fonte coletada em 2026-10-26, síntese pendente
> O levantamento no código aberto do driver está em [[NVIDIA - open-gpu-kernel-modules (interrupções e GSP)]] (bruto em `harness/spec/sources/ogkm-interrupts.md`). Falta auditoria do `fact-checker` e a redação (tipo A: Fable ou Opus). Lacunas declaradas: o código não menciona o AMP, e MSI ou MSI-X não foram encontrados no trecho lido; o mapa de interrupções vem do GB100 (`derived`).

## Objetivo
Explicar como a CPU entrega trabalho à GPU, quem escalona os contextos, e como a GPU avisa a CPU (interrupções).

## Itens do enunciado cobertos
- interrupções
- escalonamento

## Já confirmado na fonte primária
- O AMP é um escalonador de contextos programável, implementado em um processador **RISC-V** dedicado na frente do pipeline da GPU. Ele tira da CPU o escalonamento de contextos ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 25).
- Interface com o computador: PCIe Gen 5 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4).
- MIG: o GB202 pode ser dividido em até 4 instâncias de GPU isoladas ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 44).

## A levantar
- Como a CPU envia comandos (filas de comandos, campainha/doorbell)? (código aberto do driver)
- Como a GPU sinaliza conclusão e erros por interrupção (MSI/MSI-X) e como o driver trata isso?
- Qual o papel do firmware (GSP) e do AMP no escalonamento?
- Como o MIG isola recursos entre instâncias?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> Detalhes de interrupções e de firmware dependem do código aberto do driver. O que não estiver lá fica registrado como lacuna declarada.

Anterior: [[10 - Memória virtual e MMU]] | Próxima: [[12 - Latência, ocupação e divergência]]
