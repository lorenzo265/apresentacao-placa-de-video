---
tipo: briefing
status: revisar
prazo: 2026-10-26
---
# Requisitos da disciplina

Trabalho em grupo (até 4 integrantes) da disciplina de Organização e Arquitetura de Computadores. Resumo do enunciado recebido, com palavras próprias.

## Escolha do grupo
- Linha: **Arquitetura** (estudo e apresentação em seminário de um processador ou microcontrolador).
- Tema: **GPU Nvidia**, que consta na lista de sugestões do professor. "Tecnologia CUDA" também consta e se encaixa como parte do estudo.
- A outra linha, **Organização**, é de projeto de hardware com Arduino ou ESP32 (Vespa) do laboratório. Não é a nossa.

## O que o professor exige
Não basta listar características. O estudo precisa levantar, nos casos em que a arquitetura tiver o item:
- conjunto de registradores;
- conjunto de instruções;
- se é CISC ou RISC;
- como funciona a MMU;
- mecanismo de interrupções;
- gerenciamento de memória;
- pipeline;
- mecanismo de cache;
- e o que mais for relevante.

Nem todo item existe em toda arquitetura. Quando um item não existir, ou não for público, o trabalho diz isso de forma explícita e explica por quê.

## Datas e notas
| Data | Entrega | Pontos |
|---|---|---|
| 2026-10-19 | Criação do grupo e escolha do assunto | - |
| 2026-10-26 | Proposta formal do que o grupo fará | 0,5 |
| 2026-11-09 | Documentação escrita | 1,5 |
| 2026-11-16 | Apresentação em seminário | 2,0 |

Total em jogo: 4,0 pontos. A duração do seminário ainda não foi informada. Perguntar ao professor.

## Cobertura do roteiro v1 contra o enunciado
| Item exigido | Coberto hoje? | Onde |
|---|---|---|
| Registradores | não | |
| Conjunto de instruções | não | |
| CISC ou RISC | não | |
| MMU | não | |
| Interrupções | não | |
| Gerenciamento de memória | parcial | [[07 - Memória]], só o lado físico |
| Pipeline | não | |
| Cache | não | |

O roteiro v1 trata de hardware físico da placa (cooler, entrega de energia, PCB, pads). Isso não é o que o enunciado avalia. A placa deve virar a moldura do trabalho, e o centro precisa ser a arquitetura da GPU.

## Proposta de roteiro v2 (aguardando confirmação)
Ideia: o tour desce em níveis, da placa até o interior do chip, como uma sequência de zooms.

| Parte | Seção | Item do enunciado |
|---|---|---|
| A. A placa como sistema | 1. Abertura e visão geral | contexto |
| | 2. Energia, dados e calor na placa | organização física, resumida |
| | 3. Memória e barramentos (GDDR, PCIe) | organização, gerenciamento de memória |
| B. O chip | 4. Planta do chip: GPCs, SMs, L2, controladores de memória | visão geral |
| | 5. Modelo de execução: SIMT, warps, blocos (CUDA) | pipeline, modelo de programação |
| | 6. O SM por dentro: escalonadores e unidades de execução | pipeline |
| | 7. Registradores | registradores |
| | 8. Instruções: PTX e SASS, e a pergunta RISC ou CISC | conjunto de instruções, CISC/RISC |
| | 9. Hierarquia de memória e caches | cache, gerenciamento de memória |
| | 10. Memória virtual da GPU (MMU) | MMU, gerenciamento de memória |
| | 11. Comunicação com a CPU e interrupções | interrupções |
| | 12. Latência, ocupação e divergência | pipeline |
| C. Fechamento | 13. O que a Blackwell mudou | contexto da geração |
| | 14. GPU contra CPU: o que muda em cada item | síntese |

## Fontes primárias prováveis
Nenhuma foi coletada. A existência e o conteúdo de cada uma precisam ser verificados.
- Whitepaper da arquitetura Blackwell (NVIDIA).
- Guia de programação CUDA e especificação do PTX (NVIDIA).
- Documentação das ferramentas binárias do CUDA, com a lista de instruções SASS por arquitetura.
- Código aberto dos módulos de kernel da NVIDIA, que pode documentar MMU e interrupções no nível de registradores.
- Artigos acadêmicos de microbenchmarking de GPUs NVIDIA de gerações anteriores.
- Ficha oficial da RTX PRO 6000 Blackwell Workstation Edition.

Ver também: [[Briefing]], [[Plano de pesquisa]] e [[Decisões do projeto]].
