---
tipo: briefing
status: pronto
prazo: 2026-10-26
---
# Proposta formal

Versão **entregue em 2026-10-26** (0,5 ponto), em duas páginas. O arquivo original está ao lado: ![[Proposta entregue 2026-10-26.pdf]]

O texto abaixo é a transcrição do PDF, para busca e links. O rascunho longo de 19/10, que não foi o entregue, está em `_arquivo/Proposta formal - rascunho de 2026-10-19.md`.

## Dados do grupo
- **Nome do grupo:** Warp 32
- **Integrantes:** Lorenzo Ruggini, Arthur Lincke, Thiago Karwinski, João Zamora, Vitor Amora
- **Identidade visual:** o logo é um warp, o grupo de 32 threads que a GPU executa em conjunto: 32 quadrados em grade 8 × 4, com 4 em laranja, as threads que seguem outro caminho do programa.

## Proposta
- **O que será feito:** estudo da arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell (chip GB202).
- **Natureza:** estudo de um processador, na linha de Arquitetura: pesquisa em documentação oficial.
- **O que será levantado:** registradores, conjunto de instruções (PTX e SASS), se é CISC ou RISC, MMU, interrupções, gerenciamento de memória, pipeline e cache. Quando um item não existir na GPU ou não for público, o trabalho vai dizer isso e explicar o motivo.
- **Entregas:** documentação escrita (09/11) e seminário (16/11), com um tour 3D interativo da placa e do chip como apoio.
- **O que será usado ou adquirido:** nada será adquirido, porque não há projeto de hardware. Serão usados documentação pública da NVIDIA, o código aberto do driver, artigos acadêmicos e ferramentas gratuitas do CUDA para compilar e desmontar exemplos curtos.

## Definição das tarefas
Todo o grupo é responsável pelo trabalho inteiro e revisa o texto dos colegas. Cada integrante responde por uma parte:

| Integrante | Parte | Seções do roteiro |
|---|---|---|
| Lorenzo Ruggini | registradores, conjunto de instruções e RISC ou CISC | [[07 - Registradores]], [[08 - Instruções PTX e SASS, RISC ou CISC]] |
| Arthur Lincke | hierarquia de memória, caches e gerenciamento de memória | [[03 - Memória e barramentos]], [[09 - Hierarquia de memória e caches]] |
| Thiago Karwinski | MMU, interrupções e escalonamento | [[10 - Memória virtual e MMU]], [[11 - Escalonamento, CPU e interrupções]] |
| João Zamora | pipeline, execução SIMT, latência e ocupação | [[05 - Modelo de execução SIMT]], [[06 - O SM por dentro]], [[12 - Latência, ocupação e divergência]] |
| Vitor Amora | tour 3D, integração e condução do seminário | [[01 - Abertura e visão geral]], [[02 - Energia, dados e calor na placa]], [[13 - O que a Blackwell mudou]], [[14 - GPU contra CPU e encerramento]] |

A coluna "Seções do roteiro" não está no PDF: é a correspondência com o roteiro v2, feita em 2026-11-09. A [[04 - Planta do chip]] não tem dono na proposta.

## Cronograma
| Período | Atividade |
|---|---|
| 19/10 a 26/10 | formação do grupo, escolha do tema, leitura inicial e proposta (todos). Entrega da proposta em 26/10 |
| 27/10 a 01/11 | aprofundar a leitura das fontes (cada um na sua parte) |
| 02/11 a 08/11 | redação do texto e primeira versão do tour (cada um na sua parte; Vitor Amora no tour) |
| 09/11 | revisão cruzada e entrega da documentação escrita (todos) |
| 10/11 a 14/11 | tour final, slides de reserva e divisão das falas (Vitor Amora, com todos) |
| 15/11 | ensaio geral com cronômetro (todos) |
| 16/11 | seminário (todos) |

## Objetivo
- Aprofundar o conhecimento em arquitetura de computadores com um processador atual e muito avançado.
- Apresentar à turma um estudo de caso em que apresente uma proposta inovadora de aprendizado, por meio de visualização de cada etapa do funcionamento da placa de vídeo.

## O que a proposta compromete (conferido em 2026-11-09)
| Compromisso | Situação |
|---|---|
| Levantar os oito itens e declarar o que não é público | cumprido no artigo; aprofundado para o seminário (ver `harness/qa/revisao-artigo.md`) |
| Usar o código aberto do driver | o artigo não cita o código do driver. As seções 10 e 11 do roteiro agora usam |
| Compilar e desmontar exemplos com as ferramentas do CUDA | cumprido e reproduzido (`harness/examples/saxpy-cu/`) |
| Tour 3D interativo da placa e do chip no seminário | **não existe ainda**. Plano em `harness/story/video-plan.md` |
| "Visualização de cada etapa do funcionamento da placa" | é o que os três caminhos (energia, dados, calor) e os níveis do tour entregam |
| Slides de reserva e divisão das falas até 14/11 | divisão proposta em `harness/story/video-plan.md`, seção 6; slides por fazer |
| Ensaio geral em 15/11 | por fazer |

Ver também: [[Requisitos da disciplina]], [[Briefing]] e [[Plano de pesquisa]].
