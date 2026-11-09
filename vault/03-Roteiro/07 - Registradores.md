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
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - Blackwell Tuning Guide]]", "[[NVIDIA - PTX ISA]]", "[[Jia et al. - Dissecting the NVIDIA Volta GPU]]"]
---
# 07 - Registradores

## Objetivo
Explicar o banco de registradores da GPU: tamanho, organização, quanto cada thread pode usar e como isso limita a ocupação do SM.

## Itens do enunciado cobertos
- registradores

## Já confirmado na fonte primária
- 256 KB de banco de registradores por SM ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9) e 48.128 KB no total da RTX PRO 6000 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4). A conta fecha: 188 × 256 KB = 48.128 KB.
- Conta derivada: 256 KB ÷ 4 B = 65.536 registradores de 32 bits por SM.
- No PTX os registradores são tipados, têm de 8 a 128 bits, não são endereçáveis, e o limite por thread depende da plataforma ([[NVIDIA - PTX ISA|PTX]], state spaces).
- Medido: o kernel SAXPY compilado para `sm_120` usa **10 registradores por thread** e 0 bytes de spill (`ptxas -v`). O SASS usa registradores `R` (por thread), `UR` (caminho uniforme) e `P` (predicados). Ver `harness/examples/saxpy/`.
- Derivado (Volta): registradores em dois bancos de 64 bits, e conflito de banco quando os três fontes de uma FFMA caem no mesmo banco ([[Jia et al. - Dissecting the NVIDIA Volta GPU|Jia et al.]], capítulo 1). A confirmar na Blackwell.

- **Limites oficiais:** "The register file size is 64K 32-bit registers per SM. The maximum number of registers per thread is 255." ([[NVIDIA - Blackwell Tuning Guide|Blackwell Tuning Guide]] 13.5, 1.4.1.1, leitura direta em 2026-11-09). Os 65.536 registradores deixam de ser só conta nossa. A Fig. 5 do whitepaper (p. 10) mostra a organização: quatro bancos de "16,384 x 32-bit", um por bloco do SM.
- O exemplo do artigo, reproduzido em `harness/examples/saxpy-cu/`, usa 10 registradores e as famílias `R`, `UR`, `P` e `SR`.

## A levantar
- Quais são os registradores arquiteturais e especiais (predicados, ids de thread)? (PTX e ferramentas binárias, a verificar)
- Como o compilador aloca registradores e o que acontece quando faltam (spill)?
- Como o banco de registradores se compara ao de uma CPU?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - PTX ISA]]
- [[Jia et al. - Dissecting the NVIDIA Volta GPU]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `derived`. Confirmar com a fonte antes de virar texto final.

Anterior: [[06 - O SM por dentro]] | Próxima: [[08 - Instruções PTX e SASS, RISC ou CISC]]
