---
tipo: fonte
status: rascunho
secao: MMU
autor: NVIDIA
link: https://nvidia.github.io/open-gpu-doc/pascal/gp100-mmu-format.pdf
acessado: 2026-11-09
procedencia: derived
---
# NVIDIA - Pascal MMU Format Changes

## Dados da fonte
- **Título:** Pascal MMU Format Changes (documento do projeto `open-gpu-doc`, março de 2016 nos metadados).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura direta das 5 páginas do PDF.

## Pontos que servem à apresentação
- É o **único documento de formato de MMU** que a NVIDIA publica no `open-gpu-doc` entre os abertos. Cobre a Pascal (2016), **não a Blackwell**; usar como exemplo didático, com procedência `derived`. Serve a [[10 - Memória virtual e MMU]].
- Endereço virtual de **49 bits**, tabela de **5 níveis** (PD3, PD2, PD1, PD0 e a tabela de páginas), todos os níveis com 4 KB.
- Tamanhos de página: **4 KB, 64 KB e 2 MB**; o de 128 KB foi removido. A divisão dos bits do VA vem numa tabela do documento (PD3 [48:47] até a página).
- Cada entrada diz onde está a memória (vídeo local, sistema coerente ou não coerente) e traz bits de permissão (somente leitura, atômicos desligados, privilegiado). Uma violação gera **falha de página**.
- As páginas do `open-gpu-doc` para Volta, Turing e Ampere que abri só tinham pastas de host e de chip; nada de Hopper ou Blackwell.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 2.

> [!note]
> Resumo com palavras próprias. Rodada não auditada. A MMU atual (57 bits) está em [[NVIDIA - open-gpu-kernel-modules, UVM e MMU]].
