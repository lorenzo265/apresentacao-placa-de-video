---
tipo: briefing
status: pronto
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

## Roteiro v2 (confirmado em 2026-10-19)
O tour desce em níveis, da placa até o interior do chip. O roteiro v1 (hardware físico) foi arquivado em `_arquivo/roteiro-v1/` e serve de material para a seção 02.

| Parte | Seção |
|---|---|
| A. A placa como sistema | [[01 - Abertura e visão geral]], [[02 - Energia, dados e calor na placa]], [[03 - Memória e barramentos]] |
| B. O chip | [[04 - Planta do chip]], [[05 - Modelo de execução SIMT]], [[06 - O SM por dentro]], [[07 - Registradores]], [[08 - Instruções PTX e SASS, RISC ou CISC]], [[09 - Hierarquia de memória e caches]], [[10 - Memória virtual e MMU]], [[11 - Escalonamento, CPU e interrupções]], [[12 - Latência, ocupação e divergência]] |
| C. Fechamento | [[13 - O que a Blackwell mudou]], [[14 - GPU contra CPU e encerramento]] |

## Cobertura do roteiro v2 contra o enunciado
| Item exigido | Seções | Fonte primária já lida | Risco de lacuna |
|---|---|---|---|
| Registradores | [[07 - Registradores]] | whitepaper: tamanho do banco | médio: limites por thread vêm do guia CUDA |
| Conjunto de instruções | [[08 - Instruções PTX e SASS, RISC ou CISC]] | nenhuma | **alto**: o SASS não tem documentação oficial completa |
| CISC ou RISC | [[08 - Instruções PTX e SASS, RISC ou CISC]] | whitepaper: o AMP é RISC-V | médio: a classificação do SASS depende da lista de instruções |
| MMU | [[10 - Memória virtual e MMU]] | nenhuma | **alto** |
| Interrupções | [[11 - Escalonamento, CPU e interrupções]] | whitepaper: AMP e escalonamento | **alto**: o whitepaper não fala de interrupções |
| Gerenciamento de memória | [[03 - Memória e barramentos]], [[09 - Hierarquia de memória e caches]], [[10 - Memória virtual e MMU]] | whitepaper: hierarquia e GDDR7 | médio |
| Pipeline | [[05 - Modelo de execução SIMT]], [[06 - O SM por dentro]], [[12 - Latência, ocupação e divergência]] | whitepaper: parcial | médio |
| Cache | [[09 - Hierarquia de memória e caches]] | whitepaper: tamanhos | médio: política e latências vêm de medições |

## Fontes
Os links abaixo foram encontrados por busca e só as duas primeiras foram abertas e lidas.

| Fonte | Status | Cobre |
|---|---|---|
| [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]] | lida | chip, SM, memória, AMP, comparação com a Ada |
| [[NVIDIA - Página da RTX PRO 6000 Blackwell]] | lida | ficha do produto |
| Guia de programação CUDA (`docs.nvidia.com/cuda/cuda-c-programming-guide/`) | a ler | modelo de execução, ocupação, limites por thread |
| Especificação do PTX (`docs.nvidia.com/cuda/parallel-thread-execution/`) | a ler | ISA virtual |
| Ferramentas binárias do CUDA, referência de instruções (`docs.nvidia.com/cuda/cuda-binary-utilities/`) | a ler | SASS |
| Código aberto dos módulos de kernel (`github.com/NVIDIA/open-gpu-kernel-modules`) | a ler | MMU, interrupções, comunicação com a CPU |
| Documentação de hardware externo do projeto NVK do Mesa (`docs.mesa3d.org/drivers/nvk/external_hardware_docs.html`) | a ler | índice de documentação de hardware |
| Artigos de microbenchmarking de GPUs NVIDIA de gerações anteriores | a localizar | pipeline, latências, caches |
| Teardown ou review com fotos da própria placa | a localizar | conector de energia, VRM, cooler |

## Achados da primeira rodada de pesquisa
- O whitepaper cobre bem a estrutura do chip e os tamanhos de recurso, mas **não cobre** MMU, interrupções, conjunto de instruções, profundidade do pipeline e política dos caches. Esses são os itens de maior risco de lacuna.
- O whitepaper tem duas inconsistências internas (192 contra 188 SMs, e dois valores para a banda da Ada). Detalhes em [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]].
- O único processador da GPU que o whitepaper identifica pela ISA é o AMP, que é **RISC-V**. Isso entra em [[08 - Instruções PTX e SASS, RISC ou CISC]] e [[11 - Escalonamento, CPU e interrupções]].

Ver também: [[Briefing]], [[Plano de pesquisa]] e [[Decisões do projeto]].
