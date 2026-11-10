# Fact-check da F6: terceira passada (material novo)

- Data: 2026-11-10
- Auditor: agente `fact-checker` (Fable), em contexto separado.
- Escopo: o que chegou depois das duas primeiras passadas: os beats a5.3, a5.14, a6.3, a7.1, a7.2 e a7.4; os diagramas `close.delta`, `close.gaps` e `sys.cmd`; os nós novos de `chip.memhier`, `chip.isa`, `chip.sm` e `sys.irq`; e as ressalvas N1 a N12 da segunda passada.
- **Veredito: não aprovado**, por quatro erros em `a6.3`/`sys.cmd` e `a7.4`/`close.gaps`. Passam, com ajustes: a5.3, a5.14, a7.1, a7.2, `close.delta` e os nós novos dos diagramas já auditados.
- Correções aplicadas no mesmo dia. **Falta nova passada sobre `a6.3`, `sys.cmd`, `a7.4` e `close.gaps`.**

## Conferido e certo
- `close.delta`: os cinco pares batem com o spec e com a Tab. 4 do whitepaper. As razões (× 1,32, × 1,33, × 2,00, × 2,00, × 1,87, e × 1,78 pela Tab. 1) estão certas e marcadas como conta nossa.
- a5.3 confere com o literal do guia CUDA 13.5, 3.2.2.2.
- a5.14 não cita número que não temos.
- `chip.isa`: a seta nova (`%ntid.x` para `LDC R7`) confere com o README do exemplo.
- Cobertura do enunciado: os oito itens têm beat com conteúdo.

## Achados e resolução
| # | Severidade | Onde | Achado | Resolução |
|---|---|---|---|---|
| 1 | bloqueia | a6.3, fala; arquivo de fontes | "Um programa CUDA passa pela parte fechada do driver" continuava afirmado sem trecho | fala reescrita ("não lemos; supor o mesmo esquema é leitura nossa"); fontes corrigidas para `inferred` |
| 2 | bloqueia | a6.3, fala | "A GPU consome avançando o GET" vai além do trecho: no código lido, `gpu_get` é a última entrada concluída pela GPU, atualizada pelo driver | fala reescrita; trecho registrado |
| 3 | bloqueia | `sys.cmd`, passos 1 e 2; a6.3, legenda; fato `cmd.submit` | **Ordem invertida.** O driver reserva a entrada de GPFIFO ao começar o push, grava os comandos, aponta a entrada para eles (`set_gpfifo_entry`) e só então avança o PUT. O erro veio do registro do fato pela sessão principal | fato, fontes, legenda e diagrama corrigidos |
| 4 | bloqueia | `close.gaps`; a7.4 | O quadro chamava de "não é público" coisas que nós é que não levantamos (tamanhos do carveout, modos de endereçamento) | título, cabeçalho e células separam "nada público" de "não levantamos"; lacunas `isa.microcode` e `isa.addressing_modes` criadas |
| 5 | ajusta | a7.4, fonte; aviso de `close.gaps` | Vocabulário interno do projeto ia para a tela | textos trocados |
| 6 | ajusta | `close.gaps`, linha de instruções; storyboard a7.4 | "258 mnemônicos" é contagem nossa, sem marca | "(contagem nossa)"; `derived` no beat |
| 7 | ajusta | `close.delta`, potência; fato `card.tgp_w`; a7.1 | A comparação é honesta (os dois valores são da linha "TGP (Total Graphics Power)" da Tab. 4), mas o texto citava só o "Total board power" do datasheet | nota, fato e fala corrigidos |
| 8 | ajusta | a7.2; `close.delta` | 384 bits e 20 Gbps não eram fatos do spec | fatos `ada.bus_bits` e `ada.pin_rate_gbps` criados (literais da Tab. 4) e citados |
| 9 | ajusta | `sys.cmd`, pushbuffer | Desenhado dentro de um canal; no driver ele é por GPU e serve vários canais | movido para fora do quadro do canal |
| 10 | ajusta | storyboard a6.3 | A ressalva "leitura nossa" ficava fora do quadro; faltava `inferred` | foco ampliado; `inferred` acrescentado |
| 11 | ajusta | a6.2 contra a6.3 | Duas definições de canal | a6.2 passa a usar a do driver |
| 12 | ajusta | a5.3 | "Lacuna declarada" sem entrada no spec | lacuna `sched.block_to_sm` criada; "o trecho que lemos não diz" |
| 13 | ajusta | a5.5, `chip.sm` | Nenhum texto dizia que "partições" é nome nosso | dito na fala e no aviso do diagrama |
| 14 | nota | plano do vídeo, tabela de cobertura | Status antigos ("bloqueado", "a registrar") | sincronizados |
| 15 | nota | `close.delta` | Faltava dizer "Workstation Edition" (na Max-Q o × 2,00 de potência não vale) | acrescentado |

## Ressalvas da segunda passada
N2, N3, N4, N6, N7, N8, N9, N10 e N12: fechadas. N1: fechada nos 25 beats antigos; nos novos, fechada com os achados 6 e 10 acima. N5: fechada no spec; a parte que restava na fala do a6.3 e no arquivo de fontes é o achado 1. N11 (formato das âncoras): adiada.

## O que o auditor não conseguiu verificar
- A Fig. 5 do whitepaper (a cópia em texto só tem a legenda).
- Se Jarmusch et al. usam a palavra "partitions". Por isso o texto do beat diz só "é o nome que adotamos".
- O enquadramento real do a6.3 no viewer.
- Se a tabela de limites do guia CUDA traz os tamanhos de carveout da compute capability 12.0.

## Estado do gate de fatos da F6
| Material | Estado |
|---|---|
| 25 beats e 8 diagramas dos atos 4 a 6 (primeira leva) | aprovado com ressalvas; ressalvas fechadas |
| a5.3, a5.14, a7.1, a7.2, `close.delta` | passam com ajustes; ajustes aplicados |
| a6.3, `sys.cmd`, a7.4, `close.gaps` | reprovados; corrigidos; **aguardam nova passada** |
