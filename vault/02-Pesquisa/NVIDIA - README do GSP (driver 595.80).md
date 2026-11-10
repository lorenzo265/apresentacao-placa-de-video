---
tipo: fonte
status: rascunho
secao: Interrupções
autor: NVIDIA
link: https://download.nvidia.com/XFree86/FreeBSD-x86_64/595.80/README/gsp.html
acessado: 2026-11-09
procedencia: confirmed
---
# NVIDIA - README do GSP (driver 595.80)

## Dados da fonte
- **Título:** capítulo "GSP firmware" do README do driver NVIDIA para FreeBSD x86_64, versão 595.80.
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura por resumo automático.

## Pontos que servem à apresentação
- O **GSP (GPU System Processor)** é um processador da própria GPU que assume tarefas de **inicialização e gerenciamento** que o driver faria na CPU. Serve a [[11 - Escalonamento, CPU e interrupções]].
- O firmware é usado por padrão em **todas as GPUs Turing e posteriores**, o que inclui a Blackwell. Vem como módulos do driver, um por arquitetura.
- **Esta página não diz que o GSP é RISC-V.** O RISC-V que o whitepaper confirma é o do AMP (ver [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]). O artigo do grupo atribui RISC-V ao GSP sem fonte aqui.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 5.

> [!note]
> Resumo com palavras próprias. Rodada não auditada.
