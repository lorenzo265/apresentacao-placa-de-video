---
tipo: fonte
status: rascunho
secao: Instruções
autor: Jia, Maggioni, Staiger, Scarpazza
link: https://arxiv.org/abs/1804.06826
acessado: 2026-10-19
procedencia: derived
---
# Jia et al. - Dissecting the NVIDIA Volta GPU

## Dados da fonte
- **Título:** Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking (arXiv 1804.06826, 2018).
- **Autores:** Zhe Jia, Marco Maggioni, Benjamin Staiger, Daniele P. Scarpazza.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-19.
- **Alcance da leitura:** texto extraído do PDF e lidas as seções 2.1 a 2.3 e trechos do capítulo 1. Os capítulos de memória e caches ainda não foram lidos.

## Por que é `derived`
A Volta é de **quatro gerações antes** da Blackwell (Volta, Turing, Ampere, Ada, Blackwell). O que o artigo mostra vale para a Volta e só vira evidência para a Blackwell quando outra fonte confirma. O exemplo de `cuobjdump` da Blackwell (duas palavras de 64 bits por instrução) é compatível com o que o artigo descreve.

## Pontos que servem à apresentação
- Na Volta, **cada instrução ocupa uma palavra de 128 bits, que inclui a informação de controle** de escalonamento. Antes, usava-se 64 bits por instrução mais uma palavra de 64 bits de controle para várias instruções. Pelas medições dos autores, pelo menos 91 bits codificam a instrução, pelo menos 23 bits são de controle e 14 pareciam não usados (seção 1, "Instructions").
- O opcode tem de 10 a 13 bits e fica nos bits menos significativos da primeira metade da palavra. Os operandos podem ser registradores (gerais, especiais ou de predicado), **endereços de memória (constante, compartilhada ou global)** ou um valor imediato. A predicação usa 4 bits: um de negação e três para o índice do predicado (seção 2.3).
- O SM da Volta é dividido em **quatro blocos de processamento**, e o bloco de um warp é `id do warp mod 4` (seção 2.2).
- Os registradores da Volta se dividem em **dois bancos de 64 bits**, e uma instrução como a FFMA que lê os três operandos fonte do mesmo banco sofre um **conflito de banco** e é serializada. Há também um cache de reuso de registradores para mitigar isso (capítulo 1).

Serve a [[08 - Instruções PTX e SASS, RISC ou CISC]] e [[07 - Registradores]].
