# Fact-check independente: instruções (PTX, SASS, RISC ou CISC)

- Data: 2026-10-19
- Auditor: agente `fact-checker` (Fable), em contexto separado de quem escreveu as notas.
- Escopo: notas de fontes de instruções em `vault/02-Pesquisa/`, seção 08 do roteiro, `harness/spec/sources/isa-sources.md` e os exemplos de `harness/examples/saxpy/`.
- Método: reabriu o PTX ISA (4 blocos), o Binary Utilities (2 blocos), a página de compute capability, o artigo da Blackwell/GB203 e o texto extraído do artigo da Volta; recontou o SASS do SAXPY à mão.
- Resultado: **não aprovado na primeira passada** (2 achados que bloqueiam). Correções aplicadas no mesmo dia.

## Resumo dos vereditos
- Confirmados sem ressalva: definição e propriedades do PTX (load-store, tradução, estabilidade, predicado de guarda, versão 9.4); seção 4.4 do Binary Utilities e todos os opcodes citados; versão 13.4; compute capability 12.0 da placa; números do artigo da Volta (91/23/14 bits, opcode de 10 a 13 bits, predicação de 4 bits, `warp id % 4`, bancos de 64 bits); números da GB203 (4 partições, 4 ciclos, L1, L2, global); endereços do SAXPY de 0x10 em 0x10, 32 instruções, 20 em PTX.
- Confirmados com local errado: warp "typically 32" (está na 2.2.1, e a 4.5.1 diz que `WARP_SZ` é 32 em todos os alvos); 128 bits da Volta (capítulo 2, não capítulo 1).

## Achados e resolução
| # | Severidade | Achado | Resolução |
|---|---|---|---|
| 1 | bloqueia | "O Binary Utilities não declara a largura da instrução" está errado: o apêndice do JSON diz "The instruction size is 16 bytes". Conferido também pelo grupo | Corrigido na nota da fonte, na seção 08, no `isa-sources.md` e no README. A largura de 128 bits passa a `confirmed` (documentação mais experimento) |
| 2 | bloqueia | Afirmar "só carga e armazenamento" omite que instruções aritméticas aceitam operando direto de constante (Binary Utilities 3.1.1: `IMAD R0, R0, c[0x0][0x0], R3`). Conferido também pelo grupo | Tabela RISC ou CISC reescrita: "RISC com exceção". Pendência de "operando de constante" removida |
| 3 | ajusta | "Só registradores como operandos" ignora imediatos (`IMAD.WIDE R2, R7, 0x4, R2`) | Texto passa a dizer "registradores ou imediatos" |
| 4 | ajusta | Referência da Volta: o texto de 128 bits está no capítulo 2 (p. 11), não no capítulo 1 | Corrigido nas notas e no `isa-sources.md`. Bancos de registradores citam também a seção 3.5 |
| 5 | ajusta | Tabela de correspondência do README do SAXPY estava errada para `ld.param` (px e py são `LDC.64`, pa e pn são `LDCU`; `LDCU.64 UR4` é o descritor; `LDC R7` é `%ntid.x`) | Tabela refeita. Duas instruções sem par no PTX marcadas como `inferred` |
| 6 | ajusta | "20 viram 19 porque cvta some e mul.wide+add viram IMAD.WIDE" não fecha a conta | Explicação refeita: −2 (cvta), −1 (3 em 2) e +2 sem par no PTX |
| 7 | ajusta | "Muitos registradores: 65.536" é conta derivada e é o banco físico, não o limite por thread | Linha reescrita e marcada como provisória. Limite por thread (255) fica pendente do guia CUDA |
| 8 | ajusta | Latência de 4 ciclos como critério RISC: é microarquitetura, e o FP64 tem 63,57 ciclos | Latência removida da tabela e mencionada em nota, com a exceção do FP64 |
| 9 | nota | "Afasta de um conjunto reduzido": em RISC, "reduzido" trata da simplicidade de cada instrução | Linha passou a "neutro", com a explicação |
| 10 | nota | Faltavam critérios: modos de endereçamento, controle de escalonamento exposto ao compilador (lembra VLIW), SASS não é ISA estável | Três critérios adicionados e a camada classificada foi explicitada |
| 11 | nota | "RISC por definição" soa tautológico | Reescrito: "RISC por projeto". O whitepaper só cita RISC-V no AMP (conferido pelo grupo) |
| 12 | ajusta | "OMMA para FP4 com escala por bloco" não é o que o artigo diz: FP4 sem escala caiu em QMMA, e OMMA apareceu com escala `ue8m0`, sem tipo de entrada especificado | Corrigido na nota do artigo e na seção 08 |
| 13 | nota | Local do warp "typically 32" e citação da 4.5.1 | Corrigido |
| 14 | nota | O PTX não usa o termo SASS; "não são endereçáveis" deve ser "não plenamente endereçáveis" | Corrigido na nota do PTX |
| 15 | nota | A tabela 4.4 descreve `LDCU` e `S2UR` como cargas para registrador uniforme | Citado como resposta parcial sobre o caminho uniforme (o nome, não o funcionamento) |

## O que o auditor não conseguiu verificar
- Whitepaper RTX PRO Blackwell p. 25 (só viu o excerto local). O grupo conferiu no texto completo que "RISC-V" aparece uma única vez, no AMP.
- Arquitetura do exemplo do `nvdisasm` na seção 3.1.1 (o documento não a declara).
- Função exata de `c[0x0][0x37c]` e `c[0x0][0x358]` (não documentada).
- Bloco 300.000 a 400.000 do PTX ISA (tabela de `.target`); não afeta nenhuma afirmação.
- Versões de `ptxas` 12.9.86 e `nvdisasm` 13.4.92 (não reexecutou).
- Limite de 255 registradores por thread (guia CUDA, pendente).

## Estado após as correções
Os pontos acima estão aplicados nos arquivos. A seção 08 continua com `status: revisar`: a classificação RISC ou CISC é análise do grupo (`inferred`) e precisa de revisão humana antes de ir ao texto final.
