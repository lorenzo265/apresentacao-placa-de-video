---
tipo: fonte
status: rascunho
secao: Normas
autor: Intel
link: https://cdrdv2-public.intel.com/613768/613768_2.11.pdf
acessado: 2026-11-09
procedencia: confirmed   # fabricante que cita a CEM 5.1
---
# Intel - ATX12VO Design Guide 2.11 (12V-2x6 e CEM 5.1)

## Dados da fonte
- **Título:** ATX12VO (12V Only) Desktop Power Supply Design Guide, Revision 2.11, maio de 2024 (doc. 613768).
- **Autor / publicador:** Intel.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09.

## Pontos que servem à apresentação
- A CEM 5.1 define três conectores auxiliares de 12 V: 2x3 (75 W), 2x4 (150 W) e 12V-2x6 (600 W). O 12VHPWR veio da CEM 5.0 e foi substituído pelo 12V-2x6 na 5.1; são quase idênticos, mas no 12V-2x6 os pinos de potência são mais longos e os de sinal mais curtos.
- 12 pinos de potência (6 de +12 V e 6 de retorno) e 4 de sinal. Os sinais SENSE0 e SENSE1 dizem à placa quanto ela pode puxar: 600, 450, 300 ou 150 W; aberto nos dois significa 0 W.
- A tabela de corrente da norma pede 55 A para 600 W, não 50 A.
- A potência do conector não inclui a do slot.
- Passo de 3,00 mm entre pinos de potência (cota de desenho, a reconferir).

## Trecho bruto salvo em
`harness/spec/sources/standards-sources.md` (seção 2). Rodada não auditada.

> [!note]
> Resumo com palavras próprias. Não cole trechos longos de terceiros aqui.
