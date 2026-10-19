---
tipo: briefing
status: revisar
prazo: 2026-10-26
---
# Proposta de trabalho: arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell

> [!todo] Antes de entregar (apagar este bloco)
> - Preencher nomes, matrículas e turma.
> - Conferir com o professor o **formato esperado** da proposta (tamanho, template, arquivo). Este rascunho é um texto corrido que pode ser exportado para Word ou PDF.
> - Decidir a divisão de tarefas da seção 8 (está como sugestão).
> - Confirmar a **duração do seminário** e ajustar a seção 6.

**Disciplina:** Organização e Arquitetura de Computadores
**Linha do trabalho:** Arquitetura
**Entrega:** 26/10/2026
**Integrantes:** [nome 1], [nome 2], [nome 3], [nome 4]

## 1. Tema e justificativa
O grupo estudará a arquitetura da **GPU NVIDIA da família Blackwell, chip GB202**, na placa **RTX PRO 6000 Blackwell Workstation Edition**. O tema consta na lista de sugestões do professor ("GPU Nvidia", com a "Tecnologia CUDA" como parte do estudo).

A escolha se justifica por três motivos. A GPU é um exemplo de arquitetura que difere de uma CPU em quase todos os itens da disciplina (registradores, conjunto de instruções, pipeline, caches, memória virtual), o que permite um estudo comparativo rico. A Blackwell é a geração mais recente da linha profissional, e a NVIDIA publica um documento de arquitetura detalhado para ela. E a placa tem 96 GB de memória GDDR7 e consumo máximo de 600 W, o que torna visíveis as decisões de organização de memória e de energia.

## 2. Objetivos
**Geral.** Explicar, com rigor de engenharia e de modo acessível a um estudante de computação, como a GPU GB202 é organizada e como funciona, cobrindo os itens que a disciplina exige.

**Específicos.**
1. Descrever a organização do chip, do nível da placa até o SM (Streaming Multiprocessor).
2. Levantar o conjunto de registradores e o conjunto de instruções (PTX e SASS) e classificar a arquitetura como RISC ou CISC com critérios explícitos.
3. Explicar a hierarquia de memória e os caches, o gerenciamento de memória e a MMU.
4. Explicar o mecanismo de interrupções e a comunicação com a CPU, incluindo o escalonamento de contextos.
5. Explicar o pipeline, a execução SIMT e os fatores que limitam a ocupação.
6. Comparar, item a item, a GPU com uma CPU.

## 3. Escopo: itens do enunciado e tratamento
| Item exigido | Como será tratado | Fonte principal prevista |
|---|---|---|
| Conjunto de registradores | Banco de registradores por SM, registradores por thread, registradores especiais | Documento de arquitetura da NVIDIA, guia CUDA, especificação do PTX |
| Conjunto de instruções | PTX (ISA virtual) e SASS (código de máquina), com exemplo de kernel compilado | Especificação do PTX, ferramentas binárias do CUDA |
| CISC ou RISC | Classificação do SASS por critérios explícitos; o escalonador AMP da GPU usa um processador RISC-V | Ferramentas binárias do CUDA, documento de arquitetura |
| MMU | Tradução de endereços, tabelas de página, TLB, falhas de página | Código aberto dos módulos de kernel da NVIDIA, guia CUDA |
| Interrupções | Comunicação GPU-CPU, interrupções, firmware e escalonamento de contextos | Código aberto dos módulos de kernel, documento de arquitetura |
| Gerenciamento de memória | GDDR7, hierarquia, memória unificada | Documento de arquitetura, guia CUDA |
| Pipeline | Execução SIMT, warps, unidades do SM, latência e ocupação | Documento de arquitetura, guia CUDA, artigos de microbenchmark |
| Cache | L1/memória compartilhada e L2: tamanhos, políticas e latências | Documento de arquitetura, artigos de microbenchmark |

Fica **fora do escopo**: simulação física (térmica ou elétrica), comparação de desempenho com outras placas e programação de aplicações CUDA além de exemplos curtos para ilustrar as instruções.

## 4. Metodologia e fontes
O estudo é uma pesquisa documental em fontes primárias, com registro de cada fonte (autor, link, data de acesso) e conferência de cada número.

**Já consultadas (19/10/2026).** O documento *NVIDIA RTX PRO Blackwell GPU Architecture*, versão 1.1, e a página oficial do produto. Deles saíram os números de base, como 12 GPCs, 94 TPCs e 188 SMs na RTX PRO 6000, 128 núcleos CUDA por SM, 256 KB de registradores e 128 KB de L1/memória compartilhada por SM, 128 MB de L2, memória GDDR7 de 96 GB com barramento de 512 bits e 1.792 GB/s. As contas desses números foram conferidas entre si.

**A consultar.** O guia de programação CUDA, a especificação do PTX, as ferramentas binárias do CUDA (referência de instruções SASS), o código aberto dos módulos de kernel da NVIDIA e artigos acadêmicos de microbenchmarking de GPUs NVIDIA de gerações anteriores.

**Lacunas já identificadas.** O documento de arquitetura da NVIDIA não trata de MMU, interrupções, conjunto de instruções nem política dos caches, e tem duas inconsistências internas (192 contra 188 SMs, e dois valores para a banda de memória da geração anterior). Por isso, esses itens dependem das outras fontes listadas.

## 5. Tratamento de informação não pública
Parte da arquitetura de uma GPU comercial não é documentada. O grupo adotará quatro níveis de confiança, mostrados em todo o material:

| Nível | Significado |
|---|---|
| Confirmado | Documento oficial do fabricante, sobre esta GPU |
| Derivado | Documentado para outra geração ou medido em microbenchmarks, e extrapolado |
| Provável | Proposta de engenharia, sem evidência direta |
| Ilustrativo | Apenas didático, sem pretensão de fidelidade (por exemplo, a posição dos blocos no die) |

Quando um item exigido pelo professor não existir na GPU ou não for público, o trabalho dirá isso de forma explícita e explicará o motivo, em vez de preencher a lacuna com suposição.

## 6. Produto da apresentação
1. **Documentação escrita** (09/11), organizada pelos itens da seção 3.
2. **Tour 3D interativo** em página web: a câmera desce da placa até o interior do chip e, a cada parte, uma linha leva a uma caixa de texto com a explicação, com o nível de confiança indicado. O tour é a ferramenta do seminário, não um substituto do conteúdo.
3. **Seminário** (16/11), conduzido pelos integrantes, usando o tour como apoio visual. A duração será ajustada ao tempo informado pelo professor.

O roteiro do tour tem 14 seções: três sobre a placa (visão geral; energia, dados e calor; memória e barramentos), nove sobre o chip (planta do chip, execução SIMT, SM, registradores, instruções, caches, MMU, escalonamento e interrupções, latência e ocupação) e duas de fechamento (o que a Blackwell mudou; GPU contra CPU).

## 7. Cronograma
| Período | Atividade | Entrega |
|---|---|---|
| 19/10 a 26/10 | Formação do grupo, escolha do tema, escopo e proposta | **26/10: proposta (0,5)** |
| 27/10 a 01/11 | Leitura das fontes de arquitetura (CUDA, PTX, SASS, driver aberto, artigos) e registro das fontes | |
| 02/11 a 08/11 | Redação do documento, conferência dos números e primeira versão do tour | |
| 09/11 | Fechamento do texto | **09/11: documentação escrita (1,5)** |
| 10/11 a 14/11 | Tour completo, textos finais e ensaio | |
| 15/11 | Ensaio geral com cronômetro | |
| 16/11 | Seminário | **16/11: apresentação (2,0)** |

## 8. Divisão de tarefas (sugestão)
| Integrante | Foco principal |
|---|---|
| [nome 1] | Registradores, conjunto de instruções, RISC ou CISC |
| [nome 2] | Memória, caches, MMU |
| [nome 3] | Pipeline, SIMT, interrupções e escalonamento |
| [nome 4] | Tour 3D, integração e apresentação |

Todos revisam o texto uns dos outros e dominam o conjunto, porque qualquer integrante pode ser questionado no seminário.

## 9. Resultados esperados e critérios de sucesso
- Todos os itens exigidos pelo professor tratados, ou com a ausência justificada.
- Cada número do texto com fonte e conferido.
- Linguagem que um estudante de computação acompanhe, com termo novo definido na primeira vez.
- Tour 3D funcionando no seminário, com plano de reserva (slides ou capturas) se algo falhar.

## 10. Riscos
| Risco | Mitigação |
|---|---|
| Itens sem fonte pública (MMU, interrupções, SASS) | Declarar a lacuna, usar o driver aberto e microbenchmarks, rotular o nível de confiança |
| Inconsistências nos documentos do fabricante | Conferir contas entre tabelas e citar a tabela de origem |
| Pouco tempo para o tour 3D | Priorizar o texto, que vale nota, e fazer o tour em versão enxuta |
| Falha técnica no seminário | Capturas e slides de reserva |

## 11. Referências
**Consultadas**
- NVIDIA. *NVIDIA RTX PRO Blackwell GPU Architecture*, v1.1. Disponível em: https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf. Acesso em: 19 out. 2026.
- NVIDIA. *NVIDIA RTX PRO 6000 Blackwell Workstation Edition*. Disponível em: https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/. Acesso em: 19 out. 2026.

**A consultar**
- NVIDIA. *CUDA C++ Programming Guide*.
- NVIDIA. *Parallel Thread Execution ISA*.
- NVIDIA. *CUDA Binary Utilities*.
- NVIDIA. *open-gpu-kernel-modules*. Disponível em: https://github.com/NVIDIA/open-gpu-kernel-modules.
- Artigos acadêmicos de microbenchmarking de GPUs NVIDIA (a localizar).

Ver também: [[Requisitos da disciplina]], [[Briefing]] e [[Plano de pesquisa]].
