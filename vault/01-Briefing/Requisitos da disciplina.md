---
tipo: briefing
status: pronto
prazo: 2026-10-26
---
# Requisitos da disciplina

Trabalho em grupo (até 4 integrantes, segundo este resumo; a [[Proposta formal]] entregue e o artigo têm 5, a conferir) da disciplina de Organização e Arquitetura de Computadores. Resumo do enunciado recebido, com palavras próprias.

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

Total em jogo: 4,0 pontos. O seminário tem 22 minutos (informado pelo autor em 2026-11-10; antes, de 15 a 20).

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
| Registradores | [[07 - Registradores]] | whitepaper (256 KB e Fig. 5: quatro bancos de 16.384), Tuning Guide (255 por thread), experimento | baixo |
| Conjunto de instruções | [[08 - Instruções PTX e SASS, RISC ou CISC]] | PTX e Binary Utilities (auditados) e experimento `sm_120` | médio: opcodes documentados, campos de controle só pela Volta |
| CISC ou RISC | [[08 - Instruções PTX e SASS, RISC ou CISC]] | lista oficial de 258 mnemônicos; whitepaper (o AMP é RISC-V) | baixo: análise do grupo, aprovada em 2026-11-10 e apresentada como tal |
| MMU | [[10 - Memória virtual e MMU]] | código aberto do driver (57 bits, 6 níveis), documento da Pascal | médio: TLB e espaço de endereços por programa são lacunas declaradas |
| Interrupções | [[11 - Escalonamento, CPU e interrupções]] | driver aberto (MSI, duas metades), PTX (`trap`), catálogo de Xid, whitepaper (AMP) | médio: envio de comandos lido só para os canais do próprio driver (UVM); o caminho de um programa CUDA comum é leitura nossa |
| Gerenciamento de memória | [[03 - Memória e barramentos]], [[09 - Hierarquia de memória e caches]], [[10 - Memória virtual e MMU]], [[11 - Escalonamento, CPU e interrupções]] | whitepaper (hierarquia e GDDR7); driver aberto (tabela de páginas, falha de página atendida em lote); Tuning Guide (divisão do L1 escolhida em tempo de execução) | médio: memória unificada no guia CUDA ainda não lida |
| Pipeline | [[05 - Modelo de execução SIMT]], [[06 - O SM por dentro]], [[12 - Latência, ocupação e divergência]] | whitepaper (Fig. 5: quatro partições com escalonador); guia CUDA (SIMT, escalonador de warp, divergência); Tuning Guide (48 warps) | médio: **o número de estágios do pipeline é lacuna declarada** |
| Cache | [[09 - Hierarquia de memória e caches]] | whitepaper (tamanhos); latências medidas na RTX 5080 (`derived`) | médio: **política e associatividade são lacuna declarada** |

## Fontes
As fontes marcadas como lidas foram abertas. As demais foram encontradas por busca e ainda não foram abertas.

| Fonte | Status | Cobre |
|---|---|---|
| [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]] | lida | chip, SM, memória, AMP, comparação com a Ada |
| [[NVIDIA - Página da RTX PRO 6000 Blackwell]] | lida | ficha do produto |
| [[NVIDIA - Guia de programação CUDA]] | lido em parte; o capítulo 3.2.2 por busca literal na página baixada | SIMT, divergência, escalonador de warp, troca de warp sem custo |
| [[NVIDIA - Blackwell Tuning Guide]] | lido (trecho de ocupação por leitura direta) | 64K registradores, 255 por thread, 48 warps por SM |
| [[NVIDIA - PTX ISA]] | lida em parte (cerca de 300.000 dos 470.000 caracteres), auditada | ISA virtual, registradores, predicação |
| [[NVIDIA - CUDA Binary Utilities]] | lida (inclusive o apêndice final), auditada | SASS: opcodes da compute capability 12.0 |
| [[NVIDIA - Compute capability das GPUs CUDA]] | lida | compute capability 12.0 da placa |
| [[NVIDIA - open-gpu-kernel-modules, UVM e MMU]] e [[NVIDIA - open-gpu-kernel-modules, interrupções e falhas]] | lidos em parte (pontos centrais por leitura direta) | MMU de 6 níveis, falhas de página, MSI e MSI-X |
| [[NVIDIA - Pascal MMU Format Changes]], [[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)]], [[NVIDIA - Catálogo de Xid]], [[NVIDIA - README do GSP (driver 595.80)]], [[NVIDIA - PTX ISA, versão 9.5 e instrução trap]], [[Huerta et al. - Analyzing Modern NVIDIA GPU Cores]] | lidos (fontes citadas pelo artigo entregue) | MMU da Pascal, preempção, erros, GSP, `trap`, bits de controle |
| Documentação de hardware externo do projeto NVK do Mesa (`docs.mesa3d.org/drivers/nvk/external_hardware_docs.html`) | a ler | índice de documentação de hardware |
| [[Jia et al. - Dissecting the NVIDIA Volta GPU]] | lido em parte, auditado | codificação de 128 bits, registradores, escalonador (derivado) |
| [[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]] | lido em parte, auditado | latências e pipeline na GB203 (derivado) |
| [[Ampere - Demystifying the Nvidia Ampere Architecture]] | lido por resumo, não auditado | mapeamento PTX para SASS |
| Artigos da Hopper (arXiv 2501.12084) e do B200 (arXiv 2512.02189) | a ler | caches e pipeline |
| [[NVIDIA - Datasheet da RTX PRO 6000 Workstation Edition]] | lida | conector de energia, formato, cooler, saídas |
| [[NVIDIA - Guia de início rápido RTX PRO Blackwell]] | lida | adaptador de energia incluído, posição do conector, dois slots, desenho do bracket |
| [[Gamers Nexus - Teardown da RTX PRO 6000 Blackwell]] | lida por resumo | ordem de desmontagem, memória, interface térmica |
| [[Jon Peddie Research - The Nvidia RTX Pro 6000 Blackwell Edition]], [[Puget Systems - Review da RTX PRO 6000 Blackwell Workstation]], [[sabareesh - 4x RTX PRO 6000 Blackwell com water block]] | lidas por resumo | peso, posição do conector, carcaça (terceiros) |
| [[NVIDIA - Anúncio da GeForce RTX 50 e Founders Edition da RTX 5090]], [[wccftech e Notebookcheck - RTX 5090 Founders Edition (PCB e cooler)]], [[Northridge Fix - Teardown da RTX 5090 Founders Edition (via imprensa)]] | lidas por resumo | placa irmã: três placas de circuito, câmara de vapor (derivado) |
| Fases de energia e interior do cooler desta placa | **sem fonte** | viram proposta de engenharia |

## Achados da primeira rodada de pesquisa
- O whitepaper cobre bem a estrutura do chip e os tamanhos de recurso, mas **não cobre** MMU, interrupções, conjunto de instruções, profundidade do pipeline e política dos caches. Esses são os itens de maior risco de lacuna.
- O whitepaper tem duas inconsistências internas (192 contra 188 SMs, e dois valores para a banda da Ada). Detalhes em [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]].
- O único processador da GPU que o whitepaper identifica pela ISA é o AMP, que é **RISC-V**.
- **A largura da instrução em `sm_120` é de 16 bytes (128 bits)**: o apêndice do formato JSON do Binary Utilities diz "The instruction size is 16 bytes" e o experimento com as ferramentas oficiais confirma (ver `harness/examples/saxpy/`).
- O SASS aceita operando direto do banco de constantes em instruções aritméticas (Binary Utilities 3.1.1), uma exceção ao modelo load-store puro. Isso entra na análise RISC ou CISC da seção 08.
- A primeira auditoria independente (`harness/qa/fact-check-isa.md`) achou 2 erros que bloqueavam e 13 ajustes. Todos foram corrigidos. Isso entra em [[08 - Instruções PTX e SASS, RISC ou CISC]] e [[11 - Escalonamento, CPU e interrupções]].

Ver também: [[Briefing]], [[Plano de pesquisa]] e [[Decisões do projeto]].
