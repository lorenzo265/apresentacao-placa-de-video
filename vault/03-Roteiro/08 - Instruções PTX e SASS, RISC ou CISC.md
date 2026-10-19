---
tipo: secao
status: rascunho
secao: Instruções PTX e SASS, RISC ou CISC
ordem: 8
nivel: chip
part_id: chip.isa
procedencia_esperada: derived
itens_enunciado: [conjunto de instruções, CISC/RISC]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]"]
---
# 08 - Instruções PTX e SASS, RISC ou CISC

## Objetivo
Apresentar o conjunto de instruções da GPU em suas duas camadas (PTX e SASS), mostrar um exemplo de kernel compilado e discutir, com critérios explícitos, se é RISC ou CISC.

## Itens do enunciado cobertos
- conjunto de instruções
- CISC/RISC

## Já confirmado na fonte primária
- O único processador da GPU que o whitepaper identifica pela ISA é o AMP, **RISC-V** ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 25). Os SMs não têm ISA descrita no documento.

## A levantar
- O que é PTX (ISA virtual) e o que é SASS (código de máquina)? (documentação do PTX, ainda não lida)
- Qual a lista de instruções SASS e como são codificadas? (ferramentas binárias do CUDA, a verificar para a Blackwell)
- Quais critérios usaremos para dizer RISC ou CISC (carga/armazenamento, largura fixa, modos de endereçamento)?
- Um kernel pequeno compilado, mostrando PTX e SASS lado a lado (a gerar, com o compilador do CUDA, se disponível).

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> O SASS não tem documentação oficial completa. A classificação RISC ou CISC será feita com critérios explícitos e marcada como derivada.

Anterior: [[07 - Registradores]] | Próxima: [[09 - Hierarquia de memória e caches]]
