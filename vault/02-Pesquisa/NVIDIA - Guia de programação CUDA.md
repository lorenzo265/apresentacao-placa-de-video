---
tipo: fonte
status: rascunho
secao: Execução SIMT
autor: NVIDIA
link: https://docs.nvidia.com/cuda/cuda-programming-guide/
acessado: 2026-11-09
procedencia: confirmed
---
# NVIDIA - Guia de programação CUDA

## Dados da fonte
- **Título:** CUDA Programming Guide, versão 13.5 (o endereço antigo `cuda-c-programming-guide` foi substituído por este). Páginas abertas: 1.2 Programming Model, 2.7 NVCC, 4.1 Unified Memory, 5.1 Compute Capabilities.
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura por resumo automático.

## Pontos que servem à apresentação
- Define o **SIMT**, o warp de 32 threads e a divergência: as threads que não seguem o desvio ficam "mascaradas". Serve a [[05 - Modelo de execução SIMT]] e [[12 - Latência, ocupação e divergência]].
- A tabela de compute capabilities repete os 64K registradores e 255 por thread e dá a cache unificada de 128 KB nas CC 12.x. As colunas de threads e blocos por SM não puderam ser separadas pelo resumo.
- Sobre PTX, o guia explica as opções do `nvcc` ("PTX-only, GPU forward compatible"). **Não achei** nele a descrição do driver compilando o PTX ao carregar, nem o endereço virtual de 49 bits.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 8.

> [!note]
> Resumo com palavras próprias. Rodada não auditada.
