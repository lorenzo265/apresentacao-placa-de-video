---
tipo: fonte
status: rascunho
secao: Interrupções
autor: NVIDIA
link: https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html
acessado: 2026-11-09
procedencia: confirmed
---
# NVIDIA - Catálogo de Xid

## Dados da fonte
- **Título:** Analyzing Xid Errors with the Xid Catalog (atualizado em 2026-11-04 segundo a página).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura por resumo automático.

## Pontos que servem à apresentação
- **Xid 31** se chama "GPU memory page fault" e é registrado quando a **MMU** reporta uma falha, por exemplo acesso a endereço ilegal. Liga a MMU ao driver em [[10 - Memória virtual e MMU]] e [[11 - Escalonamento, CPU e interrupções]].
- **Xid 13** se chama "Graphics Engine Exception" e é registrado para falhas gerais de aplicação do usuário. O catálogo, pelo resumo, cita acesso fora dos limites como causa típica; confirmar na página na auditoria.
- O catálogo é geral para as GPUs NVIDIA, **não cita a Blackwell** em particular. O que o driver faz com cada Xid (reiniciar o aplicativo) está na coluna de resolução.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 4.

> [!note]
> Resumo com palavras próprias. Rodada não auditada.
