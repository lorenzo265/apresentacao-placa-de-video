---
tipo: secao
status: rascunho
secao: Registradores
ordem: 7
nivel: chip
part_id: chip.regfile
procedencia_esperada: derived
itens_enunciado: [registradores]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 07 - Registradores

## Objetivo
Explicar o banco de registradores da GPU: tamanho, organização, quanto cada thread pode usar e como isso limita a ocupação do SM.

## Itens do enunciado cobertos
- registradores

## Já confirmado na fonte primária
- 256 KB de banco de registradores por SM ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9) e 48.128 KB no total da RTX PRO 6000 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4). A conta fecha: 188 × 256 KB = 48.128 KB.
- Conta derivada: 256 KB ÷ 4 B = 65.536 registradores de 32 bits por SM.

## A levantar
- Quantos registradores uma thread pode usar no máximo? (guia CUDA, a verificar)
- Quais são os registradores arquiteturais e especiais (predicados, ids de thread)? (PTX e ferramentas binárias, a verificar)
- Como o compilador aloca registradores e o que acontece quando faltam (spill)?
- Como o banco de registradores se compara ao de uma CPU?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `derived`. Confirmar com a fonte antes de virar texto final.

Anterior: [[06 - O SM por dentro]] | Próxima: [[08 - Instruções PTX e SASS, RISC ou CISC]]
