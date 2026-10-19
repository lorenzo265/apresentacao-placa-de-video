---
tipo: secao
status: rascunho
secao: Memória e barramentos
ordem: 3
nivel: placa
part_id: board.memory
procedencia_esperada: confirmed
itens_enunciado: [gerenciamento de memória, organização]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - Página da RTX PRO 6000 Blackwell]]"]
---
# 03 - Memória e barramentos

## Objetivo
Explicar a memória GDDR7 e as interfaces externas da placa: barramento de memória, PCIe e saídas de vídeo.

## Itens do enunciado cobertos
- gerenciamento de memória
- organização

## Já confirmado na fonte primária
- Memória: 96 GB de GDDR7 com ECC ([[NVIDIA - Página da RTX PRO 6000 Blackwell|página oficial]]).
- Barramento: 512 bits, com dezesseis controladores de 32 bits ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 8).
- Taxa de 28 Gbps por pino, o que dá 1.792 GB/s ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4). A conta fecha: 28 × 512 ÷ 8 = 1.792.
- GDDR7 usa sinalização de 3 níveis, com 1,5 bit por ciclo ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 12).
- ECC com correção de erro simples (SEC), sempre ligado, sem opção de desligar ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 13).
- Interface PCIe Gen 5 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4). Saídas: 4 DisplayPort 2.1 ([[NVIDIA - Página da RTX PRO 6000 Blackwell|página oficial]]); o padrão 2.1b chega a 80 Gbps ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 30).

## A levantar
- Quantos chips de memória a placa tem e em que modo (os 96 GB sugerem um arranjo em duas faces)? Pendente de teardown.
- Qual a banda do PCIe Gen 5 na largura da placa, e por que ela é bem menor que a da memória local?
- Como o controlador de memória fala com cada chip (canais de 32 bits)?

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - Página da RTX PRO 6000 Blackwell]]

## No viewer
- Nível: placa. Câmera e âncora: a definir pelo storyboard.

## Procedência
Esperada: `confirmed`. Confirmar com a fonte antes de virar texto final.

Anterior: [[02 - Energia, dados e calor na placa]] | Próxima: [[04 - Planta do chip]]
