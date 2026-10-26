---
tipo: briefing
status: pronto
prazo: 2026-10-26
---
# Requisitos da disciplina

Trabalho em grupo (o enunciado diz até 4 integrantes; o nosso grupo, **Warp 32**, tem 5: confirmar com o professor) da disciplina de Organização e Arquitetura de Computadores. Resumo do enunciado recebido, com palavras próprias.

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
| Conjunto de instruções | [[08 - Instruções PTX e SASS, RISC ou CISC]] | PTX e Binary Utilities (auditados) e experimento `sm_120` | médio: opcodes documentados, campos de controle só pela Volta |
| CISC ou RISC | [[08 - Instruções PTX e SASS, RISC ou CISC]] | whitepaper: o AMP é RISC-V | médio: a classificação do SASS depende da lista de instruções |
| MMU | [[10 - Memória virtual e MMU]] | código aberto do driver (formato das tabelas, TLB, falhas) e guia CUDA, **sem auditoria** | médio: faltam tamanho e latência do TLB, e parte do código da GB202 não está no trecho lido |
| Interrupções | [[11 - Escalonamento, CPU e interrupções]] | whitepaper (AMP) e código aberto do driver (árvore de interrupções, GSP), **sem auditoria** | **alto**: MSI ou MSI-X não achados, o código não cita o AMP, mapa vem do GB100 |
| Gerenciamento de memória | [[03 - Memória e barramentos]], [[09 - Hierarquia de memória e caches]], [[10 - Memória virtual e MMU]] | whitepaper: hierarquia e GDDR7 | médio |
| Pipeline | [[05 - Modelo de execução SIMT]], [[06 - O SM por dentro]], [[12 - Latência, ocupação e divergência]] | whitepaper: parcial | médio |
| Cache | [[09 - Hierarquia de memória e caches]] | whitepaper: tamanhos | médio: política e latências vêm de medições |

## Fontes
As fontes marcadas como lidas foram abertas. As demais foram encontradas por busca e ainda não foram abertas.

| Fonte | Status | Cobre |
|---|---|---|
| [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]] | lida | chip, SM, memória, AMP, comparação com a Ada |
| [[NVIDIA - Página da RTX PRO 6000 Blackwell]] | lida | ficha do produto |
| [[NVIDIA - CUDA C++ Programming Guide]] | lido em 2026-10-26 (PDF oficial v13.4, edição Legacy; rascunho, em auditoria) | modelo de execução, ocupação, limites por thread da cc 12.0 |
| [[NVIDIA - PTX ISA]] | lida em parte (cerca de 300.000 dos 470.000 caracteres), auditada | ISA virtual, registradores, predicação |
| [[NVIDIA - CUDA Binary Utilities]] | lida (inclusive o apêndice final), auditada | SASS: opcodes da compute capability 12.0 |
| [[NVIDIA - Compute capability das GPUs CUDA]] | lida | compute capability 12.0 da placa |
| [[NVIDIA - open-gpu-kernel-modules (MMU)]] e [[NVIDIA - open-gpu-kernel-modules (interrupções e GSP)]] | lidos em 2026-10-26 (versão 615.78.08, checkout parcial; rascunho, em auditoria) | MMU, interrupções, comunicação com a CPU |
| Documentação de hardware externo do projeto NVK do Mesa (`docs.mesa3d.org/drivers/nvk/external_hardware_docs.html`) | a ler | índice de documentação de hardware |
| [[Jia et al. - Dissecting the NVIDIA Volta GPU]] | lido em parte, auditado | codificação de 128 bits, registradores, escalonador (derivado) |
| [[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]] | lido em parte, auditado | latências e pipeline na GB203 (derivado) |
| [[Ampere - Demystifying the Nvidia Ampere Architecture]] | lido por resumo, não auditado | mapeamento PTX para SASS |
| Artigos da Hopper (arXiv 2501.12084) e do B200 (arXiv 2512.02189) | a ler | caches e pipeline |
| [[Teardown e conector de energia (RTX PRO 6000 e 5090)]] | lido em 2026-10-26 (rascunho, em auditoria) | conector de 16 pinos, memória, cooler; VRM e camadas do PCB seguem sem fonte |

## Achados da primeira rodada de pesquisa
- O whitepaper cobre bem a estrutura do chip e os tamanhos de recurso, mas **não cobre** MMU, interrupções, conjunto de instruções, profundidade do pipeline e política dos caches. Esses são os itens de maior risco de lacuna.
- O whitepaper tem duas inconsistências internas (192 contra 188 SMs, e dois valores para a banda da Ada). Detalhes em [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]].
- O único processador da GPU que o whitepaper identifica pela ISA é o AMP, que é **RISC-V**.
- **A largura da instrução em `sm_120` é de 16 bytes (128 bits)**: o apêndice do formato JSON do Binary Utilities diz "The instruction size is 16 bytes" e o experimento com as ferramentas oficiais confirma (ver `harness/examples/saxpy/`).
- O SASS aceita operando direto do banco de constantes em instruções aritméticas (Binary Utilities 3.1.1), uma exceção ao modelo load-store puro. Isso entra na análise RISC ou CISC da seção 08.
- A primeira auditoria independente (`harness/qa/fact-check-isa.md`) achou 2 erros que bloqueavam e 13 ajustes. Todos foram corrigidos. Isso entra em [[08 - Instruções PTX e SASS, RISC ou CISC]] e [[11 - Escalonamento, CPU e interrupções]].

## Achados da rodada de 2026-10-26
- **Guia CUDA:** 255 registradores por thread e 65.536 por SM na cc 12.0 (fecha a pendência do PTX). Conflitos registrados com o whitepaper: L1 mais memória compartilhada (100 KB contra 128 KB por SM) e unidades INT32 separadas contra unificadas.
- **Driver aberto, MMU:** o código liga a família GB20x à MMU da Hopper. Para a GB202 o conjunto de páginas é 4 KB, 64 KB, 2 MB e 512 MB (a página de 256 GB é só da GB10x). É `derived`, porque parte do código que decide isso não está no clone.
- **Driver aberto, interrupções:** o GSP é RISC-V e roda o RM. O código não menciona o AMP do whitepaper. MSI ou MSI-X não foram encontrados no trecho lido.
- **Conector:** a NVIDIA chama de "PCIe CEM5 16-pin", com adaptador de 4 cabos de 8 pinos na caixa; outras fontes o chamam de 12V-2x6 ou 12VHPWR (`conflict`).
- Tudo isso passou por auditoria do `fact-checker` em 2026-10-26: ver `harness/qa/fact-check-proposta.md`, `fact-check-driver.md` e `fact-check-cuda-power.md` (quando existirem).

Ver também: [[Briefing]], [[Plano de pesquisa]] e [[Decisões do projeto]].
