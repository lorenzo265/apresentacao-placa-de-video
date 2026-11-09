---
tipo: fonte
status: rascunho
secao: Normas
autor: PCI-SIG
link: https://www.design-reuse.com/news/46222/32gt-s-pci-express-5-0-specification.html
acessado: 2026-11-09
procedencia: confirmed   # comunicado da entidade, republicado por terceiro
---
# PCI-SIG - Comunicado do PCIe 5.0 (via Design & Reuse)

## Dados da fonte
- **Título:** PCI-SIG Achieves 32GT/s with New PCI Express 5.0 Specification (29 de maio de 2019).
- **Autor / publicador:** PCI-SIG, republicado na Design & Reuse. O site pcisig.com foi bloqueado para a ferramenta.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09.

## Pontos que servem à apresentação
- PCIe 5.0 tem 32 GT/s brutos por pista e "até 128 GB/s" em x16.
- O comunicado não cita a codificação nem diz se os 128 GB/s somam as duas direções. Por conta (32 x 16 / 8 = 64 GB/s por direção, bruto), são as duas direções somadas.
- Com a codificação 128b/130b (fonte de baixa autoridade), o útil fica em cerca de 63 GB/s por direção, contra 1.792 GB/s da memória local.

## Trecho bruto salvo em
`harness/spec/sources/standards-sources.md` (seções 15 e 16, conta C4). Rodada não auditada.

> [!note]
> Resumo com palavras próprias. Não cole trechos longos de terceiros aqui.
