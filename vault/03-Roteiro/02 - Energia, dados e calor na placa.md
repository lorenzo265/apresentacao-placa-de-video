---
tipo: secao
status: rascunho
secao: Energia, dados e calor na placa
ordem: 2
nivel: placa
part_id: board.overview
procedencia_esperada: inferred
itens_enunciado: [organização física]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - Página da RTX PRO 6000 Blackwell]]"]
---
# 02 - Energia, dados e calor na placa

## Objetivo
Mostrar a placa desmontada em alto nível (cooler, placa de circuito, entrega de energia, package do chip) e os três caminhos que a atravessam: energia, dados e calor.

## Itens do enunciado cobertos
- organização física

## Já confirmado na fonte primária
- Potência total da placa: 600 W na Workstation Edition e 300 W na Max-Q ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4; [[NVIDIA - Página da RTX PRO 6000 Blackwell|página oficial]]).
- Conector de energia: a [[NVIDIA - Página da RTX PRO 6000 Blackwell|página oficial]] **não informa**. Continua pendente.

## A levantar
- Qual é o conector de energia e que corrente ele leva (teardown ou review da própria placa)?
- Como é o cooler por dentro e quantas fases tem a entrega de energia? (reaproveitar as notas arquivadas do roteiro v1)
- Há teardown da própria placa? Se não, quais placas irmãs servem de análogo?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - Página da RTX PRO 6000 Blackwell]]

## No viewer
- Nível: placa. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> A estrutura interna (cooler e entrega de energia) só vira fato se houver teardown da própria placa. Sem isso, é proposta de engenharia baseada em placas semelhantes e aparece com o selo "provável".

Anterior: [[01 - Abertura e visão geral]] | Próxima: [[03 - Memória e barramentos]]
