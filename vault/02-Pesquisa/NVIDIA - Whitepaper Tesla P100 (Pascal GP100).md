---
tipo: fonte
status: rascunho
secao: MMU
autor: NVIDIA
link: https://images.nvidia.com/content/pdf/tesla/whitepaper/pascal-architecture-whitepaper.pdf
acessado: 2026-11-09
procedencia: derived
---
# NVIDIA - Whitepaper Tesla P100 (Pascal GP100)

## Dados da fonte
- **Título:** NVIDIA Tesla P100: the most advanced datacenter accelerator ever built featuring Pascal GP100 (WP-08019-001_v01.1, 2016).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura direta das páginas 2 a 4, 27, 28 e 30.

## Pontos que servem à apresentação
- Origem da memória virtual "de CPU" nas GPUs NVIDIA: **49 bits de endereço virtual**, cobrindo os 48 bits das CPUs, e **falhas de página** (p. 27). Serve a [[10 - Memória virtual e MMU]].
- Memória unificada: a página pode ser **migrada sob demanda** ou **mapeada por PCIe ou NVLink** sem copiar. O artigo do grupo diz só "copia".
- **Preempção no nível de instrução** com o contexto salvo na DRAM da GPU (p. 30), contra a preempção por bloco da Kepler. Serve a [[11 - Escalonamento, CPU e interrupções]].
- É documento de **outra geração** (Pascal, 2016): não vale como afirmação sobre a Blackwell.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 3.

> [!note]
> Resumo com palavras próprias. Rodada não auditada.
