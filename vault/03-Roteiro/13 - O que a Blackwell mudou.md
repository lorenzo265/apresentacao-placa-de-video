---
tipo: secao
status: rascunho
secao: O que a Blackwell mudou
ordem: 13
nivel: fechamento
part_id: blackwell.delta
procedencia_esperada: confirmed
itens_enunciado: [contexto da geração]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 13 - O que a Blackwell mudou

## Objetivo
Resumir o que mudou da geração anterior (Ada) para a Blackwell, ligando cada mudança aos itens do enunciado.

## Itens do enunciado cobertos
- contexto da geração

## Já confirmado na fonte primária
- SMs: 142 (RTX 6000 Ada) para 188. L2: 98.304 KB para 131.072 KB. Memória: 48 GB GDDR6 para 96 GB GDDR7. TGP: 300 W para 600 W ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4).
- Tensor Cores de 5ª geração com FP4 e FP6; RT Cores de 4ª geração; PCIe Gen 5; DisplayPort 2.1b; AMP; MIG com até 4 instâncias ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]]).
- Banda de memória da Ada: o whitepaper dá 1.008 GB/s na Tab. 1 e 960 GB/s na Tab. 4. Qualquer razão entre bandas precisa citar a tabela usada.

## A levantar
- Quais dessas mudanças são arquiteturais (afetam ISA, registradores, caches) e quais são de implementação?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: fechamento. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> A comparação com a Ada depende de números do mesmo documento que têm inconsistências. Cada razão apresentada cita a tabela de origem.

Anterior: [[12 - Latência, ocupação e divergência]] | Próxima: [[14 - GPU contra CPU e encerramento]]
