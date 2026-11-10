# Fact-check da F6: quarta passada (estreita)

- Data: 2026-11-10
- Auditor: agente `fact-checker` (Fable), em contexto separado.
- Escopo: só o que a terceira passada reprovou ou mandou ajustar: beat a6.3 e diagrama `sys.cmd`; beat a7.4 e diagrama `close.gaps`; os ajustes em a5.3, a5.5, a6.2, a7.1, a7.2, `close.delta` e `chip.sm`; o fato `cmd.submit` e o bloco de fontes reescrito.
- **Vereditos:** a6.3, `sys.cmd`, a7.4 e `close.gaps`: **aprovados com ressalvas**. Nenhum bloqueio novo. Os quatro bloqueios da terceira passada estão fechados.

## Conferido por busca literal no código do driver
- A sequência desenhada e descrita confere com `uvm_channel.c` (linhas 984 a 1014: `set_gpfifo_entry` antes de `write_gpu_put`), `uvm_channel.h` (reserva da entrada ao começar o push; `gpu_get`) e `uvm_pushbuffer.h`.
- "A GPU lê a fila" é sustentável: "queued to be read by the GPU (by referencing them in a GPFIFO entry)".
- "Pushbuffer: um por GPU" e "atende pushes de vários canais" conferem.
- A fala do a6.3 só diz "não lemos" e "é leitura nossa" sobre o caminho de um programa CUDA comum.
- Em `close.gaps`, nenhuma célula chama de "não público" algo que só não foi levantado.

## Ressalvas e resolução
| # | Peso | Onde | Problema | Resolução |
|---|---|---|---|---|
| E1 | ajusta | a7.1, fala | Depois da correção anterior, o pronome "ela" apontava para a Max-Q | frase reescrita: "A potência da Workstation Edition cresceu mais do que o número de SMs: 2,00 contra 1,32" |
| E2 | ajusta | `close.gaps`, linha de instruções | "Nada público" onde a lacuna só sustenta "sem fonte da Blackwell" | "bits de controle do sm_120: sem fonte da Blackwell / medidos só em Volta, Turing e Ampere" |
| E3 | ajusta | a6.2 (e a6.1, a5.6, a5.13, a5.14) | "A NVIDIA não publica" onde só podemos dizer "não achamos nas fontes lidas" | os cinco textos trocados |
| E4 | baixa | `sys.cmd`, GET; a6.3, fala | O rótulo dizia "última entrada concluída" e a seta caía numa entrada pendente; a seta do GET estava `confirmed` sem trecho | "GET: até onde a GPU já concluiu / atualizado pelo driver"; seta `illustrative`; fala ajustada |
| E5 | baixa | storyboard a6.3 | Selo `derived` sem nada derivado | `inferred`, `confirmed`, `illustrative` |
| E6 | baixa | `sys.cmd`, notas | Faltava `uvm_channel.h`; "a entrada" em vez de "uma entrada" | corrigido; `cmd.s4` cita `cmd.submit` |
| E7 | baixa | spec, `card.tgp_w` | A âncora apontava para o datasheet e a nota citava a Tab. 4 | âncora corrigida para o whitepaper |
| E8 | nota | arquivo de fontes | Uma linha em branco partia a tabela | removida |

## Lacuna fechada nesta passada
O auditor achou, na cópia já baixada do guia CUDA 13.5 (seção 3.2.6), os tamanhos de memória compartilhada da compute capability 12.0: "devices of compute capability 12.0 support shared memory sizes of 0, 8, 16, 32, 64, and 100", com máximo de 100 KB. A sessão principal confirmou por busca literal. Virou o fato `mem.shared_sizes_cc120` e entrou no beat a5.14 e no diagrama da escada de memória. Fica registrado o conflito com o Tuning Guide, que fala em 128 KB por SM.

## O que o auditor não conseguiu verificar
- A Fig. 5 do whitepaper. Por isso a fala do a5.5 passou a dizer "o whitepaper não dá nome a essas quatro divisões", que é o que a busca no texto sustenta.
- O render real no viewer (a sessão principal rodou o teste e olhou os quadros).
- As negativas universais ("nada público" sobre microcódigo): não houve busca externa. A legenda do a7.4 as apresenta como "não achamos publicado".

## Estado do gate de fatos da F6
| Material | Estado |
|---|---|
| 25 beats e 8 diagramas dos atos 4 a 6 | aprovado com ressalvas; ressalvas fechadas |
| a5.3, a5.14, a7.1, a7.2, `close.delta` | aprovados com ajustes; ajustes aplicados |
| a6.3, `sys.cmd`, a7.4, `close.gaps` | aprovados com ressalvas; ressalvas aplicadas |

Os 31 beats prontos e os 11 diagramas passaram pelo gate de fatos. O que resta é o **gate humano** do animatic.
