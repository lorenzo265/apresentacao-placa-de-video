---
tipo: fonte
status: rascunho
secao: Pipeline
autor: Huerta, Abaie Shoushtary, Cruz, González (UPC)
link: https://arxiv.org/abs/2503.20481
acessado: 2026-11-09
procedencia: derived
---
# Huerta et al. - Analyzing Modern NVIDIA GPU Cores

## Dados da fonte
- **Título:** Analyzing Modern NVIDIA GPU cores (arXiv 2503.20481v1, março de 2025).
- **Autor / publicador:** Rodrigo Huerta, Mojtaba Abaie Shoushtary, José-Lorenzo Cruz, Antonio González (Universitat Politècnica de Catalunya).
- **Link:** no frontmatter (PDF em arxiv.org/pdf/2503.20481).
- **Data de acesso:** 2026-11-09. Leitura direta das páginas 1 a 12 do PDF.

## Pontos que servem à apresentação
- Confirma que as GPUs modernas deixam o **compilador** controlar dependências: cada instrução SASS leva bits de controle (contador de espera, yield, seis contadores de dependência, bit de reúso). Serve a [[06 - O SM por dentro]] e [[08 - Instruções PTX e SASS, RISC ou CISC]].
- Descreve o SM com **quatro subnúcleos**, um escalonador que emite uma instrução por ciclo e política "greedy then youngest guiado pelo compilador" (inferida por teste). Serve a [[11 - Escalonamento, CPU e interrupções]].
- Descreve registradores regulares, uniformes (64 por warp), de predicado, especiais e os de controle. Dá estágios do front-end, mas **não a profundidade do pipeline**. Serve a [[07 - Registradores]].
- **Medido em Ampere e Turing, não em Blackwell**; o artigo só afirma que vale para outras arquiteturas. Usar com procedência `derived`.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 7.

> [!note]
> Resumo com palavras próprias. Rodada não auditada.
