---
tipo: secao
status: rascunho
secao: Hierarquia de memória e caches
ordem: 9
nivel: chip
part_id: chip.memhier
procedencia_esperada: derived
itens_enunciado: [cache, gerenciamento de memória]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]"]
---
# 09 - Hierarquia de memória e caches

## Objetivo
Percorrer a hierarquia de memória da GPU, dos registradores à GDDR7, com tamanhos, larguras e o papel de cada nível.

## Itens do enunciado cobertos
- cache
- gerenciamento de memória

## Já confirmado na fonte primária
- Registradores: 256 KB por SM. L1/memória compartilhada: 128 KB por SM, configurável, 24.064 KB no total ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 9 e Tab. 4).
- L2: 131.072 KB (128 MB). Na RTX A6000 eram 6.144 KB e na RTX 6000 Ada, 98.304 KB ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4).
- Memória principal: 96 GB de GDDR7 a 1.792 GB/s ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4).
- Derivado (RTX 5080, chip GB203, não GB202): L1 entre 30 e 40 ciclos, acerto no L2 por volta de 358 ciclos e memória global por volta de 876,7 ciclos ([[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture|Jarmusch et al.]], seção VI). Os tamanhos de registradores e L1 por SM (256 KB e 128 KB) coincidem com os do whitepaper da GB202.

## A levantar
- Qual a latência e a largura de banda de cada nível? (microbenchmarks de gerações anteriores)
- Como funcionam a política de escrita, a associatividade e a coerência do L1 e do L2?
- O que é coalescência de acessos e por que ela importa?
- Como a L1 é dividida entre cache e memória compartilhada?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `derived`. Confirmar com a fonte antes de virar texto final.

Anterior: [[08 - Instruções PTX e SASS, RISC ou CISC]] | Próxima: [[10 - Memória virtual e MMU]]
