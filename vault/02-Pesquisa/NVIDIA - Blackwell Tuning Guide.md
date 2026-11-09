---
tipo: fonte
status: rascunho
secao: Registradores
autor: NVIDIA
link: https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html
acessado: 2026-11-09
procedencia: confirmed
---
# NVIDIA - Blackwell Tuning Guide

## Dados da fonte
- **Título:** Blackwell Tuning Guide (CUDA 13.5, versão HTML; o artigo do grupo cita o PDF 13.4.1, que não foi aberto).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura por resumo automático da página.

## Pontos que servem à apresentação
- Dá os **limites oficiais por SM** que o artigo usa: 64K registradores de 32 bits por SM, máximo de 255 por thread, 48 warps por SM na compute capability 12.0. Serve a [[07 - Registradores]] e [[12 - Latência, ocupação e divergência]].
- Diz que a fração da L1 dedicada à memória compartilhada ("carveout") é escolhida em tempo de execução. A lista de tamanhos do guia é do B200, não da placa do grupo. Serve a [[09 - Hierarquia de memória e caches]].
- Dá 99 KB de memória compartilhada por bloco e 32 blocos por SM na CC 12.0. **Threads por SM não estão escritos**; 1.536 é conta nossa (48 x 32).

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 1.

> [!note]
> Resumo com palavras próprias. Rodada não auditada. O guia diz 128 KB de "shared memory" por SM; o guia CUDA diz 128 KB de cache unificado e no máximo 100 KB de compartilhada. Ver Conflitos.
