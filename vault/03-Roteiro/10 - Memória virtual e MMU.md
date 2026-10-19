---
tipo: secao
status: rascunho
secao: Memória virtual e MMU
ordem: 10
nivel: chip
part_id: chip.mmu
procedencia_esperada: derived
itens_enunciado: [MMU, gerenciamento de memória]
prazo:
fontes: []
---
# 10 - Memória virtual e MMU

## Objetivo
Explicar como a GPU traduz endereços: se há MMU própria, como são as tabelas de página, o TLB, o tratamento de falhas de página e a relação com a memória da CPU.

## Itens do enunciado cobertos
- MMU
- gerenciamento de memória

## Já confirmado na fonte primária
- Nada nas fontes lidas até agora. Ver [[Plano de pesquisa]].

## A levantar
- A GPU tem MMU própria e como é a tradução de endereços? (código aberto do driver e guia CUDA sobre memória unificada)
- Quais tamanhos de página, quantos níveis de tabela e como é o TLB?
- O que acontece numa falha de página da GPU?
- Como isso se liga ao IOMMU da CPU e ao espaço de endereços visível pelo PCIe?

## Fontes
- Nenhuma ainda. Ver [[Plano de pesquisa]].

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> O funcionamento interno da MMU da GPU pode não ser totalmente público. Onde faltar fonte, o trabalho dirá isso de forma explícita e explicará o motivo.

Anterior: [[09 - Hierarquia de memória e caches]] | Próxima: [[11 - Escalonamento, CPU e interrupções]]
