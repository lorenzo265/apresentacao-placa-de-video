---
tipo: briefing
status: revisar
prazo: 2026-10-26
---
# Proposta de trabalho: arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell

> [!todo] Antes de entregar
> - Nomes e nome do grupo estão em `entregas/proposta-2026-10-26/grupo.json`. Para regerar o PDF: `python3 build.py` naquela pasta. Enquanto houver nome vazio, o PDF sai marcado como rascunho.
> - Confirmar a divisão de tarefas da seção 6: é uma sugestão minha, na ordem em que os nomes foram digitados (Lorenzo, Arthur, Thiago, João, Vitor). Para trocar, reordene os nomes em `grupo.json`.
> - O enunciado diz grupos de **até 4**. O grupo tem 5 (confirmado na sessão de 2026-10-26). Conferir com o professor, se ainda não foi feito.
> - Confirmar a **duração do seminário** com o professor e ajustar a seção 5.
> - Este texto é a fonte do PDF. O cabeçalho (nome do grupo, integrantes, identidade visual) vem de `grupo.json`. Blocos `[!todo]` e a linha "Ver também" não vão para o PDF.

## 1. Tema, natureza e justificativa
O grupo estudará a arquitetura da **GPU NVIDIA da família Blackwell, chip GB202**, na placa **RTX PRO 6000 Blackwell Workstation Edition**. O tema consta na lista de sugestões do professor ("GPU Nvidia", com a "Tecnologia CUDA" como parte do estudo).

**Natureza.** É um **estudo de arquitetura de um processador**, na linha de Arquitetura do enunciado. Não há projeto de hardware. O estudo é uma pesquisa documental em fontes primárias, com dois produtos de apoio: a documentação escrita e um tour 3D interativo para o seminário. Alguns exemplos curtos de código (um kernel em PTX compilado e desmontado) ilustram o conjunto de instruções.

**Justificativa.** A GPU difere de uma CPU em quase todos os itens da disciplina (registradores, conjunto de instruções, pipeline, caches, memória virtual), o que permite um estudo comparativo rico. A Blackwell é a geração mais recente da linha profissional, e a NVIDIA publica um documento de arquitetura detalhado para ela. E a placa tem 96 GB de memória GDDR7 e consumo máximo de 600 W, o que torna visíveis as decisões de organização de memória e de energia.

## 2. Objetivos
**Geral.** Explicar, com rigor de engenharia e de modo acessível a um estudante de computação, como a GPU GB202 é organizada e como funciona, cobrindo os itens que a disciplina exige.

**Específicos.**
1. Descrever a organização do chip, do nível da placa até o SM (Streaming Multiprocessor).
2. Levantar o conjunto de registradores e o conjunto de instruções (PTX e SASS) e classificar a arquitetura como RISC ou CISC com critérios explícitos.
3. Explicar a hierarquia de memória e os caches, o gerenciamento de memória e a MMU.
4. Explicar o mecanismo de interrupções e a comunicação com a CPU, incluindo o escalonamento de contextos.
5. Explicar o pipeline, a execução SIMT e os fatores que limitam a ocupação.
6. Comparar, item a item, a GPU com uma CPU.

**O que o grupo pretende atingir.**
- Aprofundar o conhecimento em arquitetura de computadores com um processador atual e muito diferente de uma CPU.
- Apresentar à turma um estudo de caso em que cada afirmação diz de onde veio e quão segura é.
- Entregar as três etapas (proposta, documentação e seminário) com qualidade, buscando os 4,0 pontos em jogo.

## 3. Escopo: itens do enunciado e tratamento
- **Conjunto de registradores.** Banco de registradores por SM, registradores por thread e registradores especiais. Fonte: documento de arquitetura da NVIDIA, guia CUDA e especificação do PTX.
- **Conjunto de instruções.** PTX (ISA virtual) e SASS (código de máquina), com exemplo de kernel compilado. Fonte: especificação do PTX e ferramentas binárias do CUDA.
- **CISC ou RISC.** Classificação do SASS por critérios explícitos; o escalonador AMP da GPU usa um processador RISC-V. Fonte: ferramentas binárias do CUDA e documento de arquitetura.
- **MMU.** Tradução de endereços, tabelas de página, TLB e falhas de página. Fonte: código aberto dos módulos de kernel da NVIDIA e guia CUDA.
- **Interrupções.** Comunicação GPU-CPU, interrupções, firmware e escalonamento de contextos. Fonte: código aberto dos módulos de kernel e documento de arquitetura.
- **Gerenciamento de memória.** GDDR7, hierarquia de memória e memória unificada. Fonte: documento de arquitetura e guia CUDA.
- **Pipeline.** Execução SIMT, warps, unidades do SM, latência e ocupação. Fonte: documento de arquitetura, guia CUDA e artigos de microbenchmark.
- **Cache.** L1/memória compartilhada e L2: tamanhos, políticas e latências. Fonte: documento de arquitetura e artigos de microbenchmark.

Fica **fora do escopo**: simulação física (térmica ou elétrica), comparação de desempenho com outras placas e programação de aplicações CUDA além de exemplos curtos para ilustrar as instruções.

## 4. Metodologia, fontes e materiais
O estudo é uma pesquisa documental em fontes primárias, com registro de cada fonte (autor, link, data de acesso) e conferência de cada número contra a fonte, por uma segunda leitura separada da redação.

**Materiais.** Nenhum hardware será adquirido, porque não há projeto de hardware. Serão usados: a documentação pública da NVIDIA, o código aberto dos módulos de kernel e artigos acadêmicos; as ferramentas de linha de comando do CUDA (`ptxas` e `nvdisasm`) para compilar e desmontar exemplos curtos, sem executar em GPU; e software gratuito para o tour 3D.

**Já consultadas.**
- O documento *NVIDIA RTX PRO Blackwell GPU Architecture*, versão 1.1, e a página oficial do produto. Deles saíram os números de base, como 12 GPCs, 94 TPCs e 188 SMs na RTX PRO 6000, 128 núcleos CUDA por SM, 256 KB de registradores e 128 KB de L1/memória compartilhada por SM, 128 MB de L2, memória GDDR7 de 96 GB com barramento de 512 bits e 1.792 GB/s. As contas desses números foram conferidas entre si.
- A especificação do PTX (versão 9.4), as ferramentas binárias do CUDA (versão 13.4) e a tabela de compute capability (a placa é 12.0). Deles saíram a definição do PTX como máquina load-store, a lista de instruções SASS desta geração e a largura de 16 bytes por instrução.
- O guia de programação CUDA (versão 13.4), com os limites da compute capability 12.0, como 255 registradores por thread e 65.536 registradores por SM.
- O código aberto dos módulos de kernel da NVIDIA (versão 615.78.08), lido por busca direta no código. Dele saíram o formato das tabelas de página da GPU, o tratamento de falhas de página e a invalidação do TLB, a árvore de interrupções e o firmware GSP.
- O datasheet e o guia de início rápido da NVIDIA, que informam o conector de energia (16 pinos) e a potência de 600 W.
- Três artigos de microbenchmarking de GPUs NVIDIA (Volta, Ampere e Blackwell GB203), usados como evidência de família, nunca como dado da nossa placa.
- Dois exemplos curtos (SAXPY e multiplicação de matrizes com a instrução `mma`) compilados para o alvo da placa (`sm_120`) e desmontados com as ferramentas oficiais.

**A consultar.** Os artigos de microbenchmarking das gerações Hopper e Blackwell B200, uma segunda fonte de teardown da própria placa, e uma segunda leitura, por área, do guia CUDA e do código do driver.

**Lacunas e conflitos já identificados.**
- O documento de arquitetura da NVIDIA não trata de MMU, interrupções, conjunto de instruções nem política dos caches, e tem duas inconsistências internas (192 contra 188 SMs, e dois valores para a banda de memória da geração anterior).
- O código aberto do driver descreve a MMU e as interrupções, mas não dá tamanho, associatividade nem latência do TLB, e não menciona o AMP do documento de arquitetura. A relação entre o AMP e o GSP fica em aberto.
- O guia CUDA e o documento de arquitetura divergem em alguns pontos, como a soma de L1 e memória compartilhada por SM (100 KB contra 128 KB).
- Parte do código do driver que decide a MMU da GB202 não estava no trecho lido, então alguns detalhes dela vêm da família GB20x e ficam marcados como derivados.

Esses itens serão declarados como lacuna ou conflito, com o motivo, e não preenchidos com suposição.

## 5. Tratamento de informação não pública e produto da apresentação
Parte da arquitetura de uma GPU comercial não é documentada. O grupo adotará quatro níveis de confiança, mostrados em todo o material:

- **Confirmado.** Documento oficial do fabricante, sobre esta GPU.
- **Derivado.** Documentado para outra geração ou medido em microbenchmarks, e extrapolado.
- **Provável.** Proposta de engenharia, sem evidência direta.
- **Ilustrativo.** Apenas didático, sem pretensão de fidelidade (por exemplo, a posição dos blocos no die).

Quando um item exigido pelo professor não existir na GPU ou não for público, o trabalho dirá isso de forma explícita e explicará o motivo, em vez de preencher a lacuna com suposição.

**Produto da apresentação.**
1. **Documentação escrita** (09/11), organizada pelos itens da seção 3.
2. **Tour 3D interativo** em página web: a câmera desce da placa até o interior do chip e, a cada parte, uma linha leva a uma caixa de texto com a explicação, com o nível de confiança indicado. O tour é a ferramenta do seminário, não um substituto do conteúdo.
3. **Seminário** (16/11), conduzido pelos integrantes, usando o tour como apoio visual. A duração será ajustada ao tempo informado pelo professor.

O roteiro do tour tem 14 seções: três sobre a placa (visão geral; energia, dados e calor; memória e barramentos), nove sobre o chip (planta do chip, execução SIMT, SM, registradores, instruções, caches, MMU, escalonamento e interrupções, latência e ocupação) e duas de fechamento (o que a Blackwell mudou; GPU contra CPU).

## 6. Definição das tarefas
Todo o grupo é responsável pelo trabalho e por todas as partes dele. Para que todos participem, cada integrante responde por uma parte, da pesquisa à explicação no seminário.

- **{{I1}}.** Registradores, conjunto de instruções (PTX e SASS), RISC ou CISC. Seções do roteiro: 07 e 08.
- **{{I2}}.** Hierarquia de memória, caches e gerenciamento de memória. Seções: 03 e 09.
- **{{I3}}.** Memória virtual e MMU; interrupções, comunicação com a CPU e escalonamento. Seções: 10 e 11.
- **{{I4}}.** Pipeline: execução SIMT, SM, latência, ocupação e divergência. Seções: 05, 06 e 12.
- **{{I5}}.** Tour 3D, integração, abertura e fechamento, slides de reserva e condução do seminário. Seções: 01, 02, 04, 13 e 14.

Todos revisam o texto uns dos outros e dominam o conjunto, porque qualquer integrante pode ser questionado no seminário.

## 7. Cronograma
- **19/10 a 26/10.** Formação do grupo, escolha do tema, leitura inicial das fontes de arquitetura, escopo e proposta. Responsável: todos. **Entrega em 26/10: proposta (0,5).**
- **27/10 a 01/11.** Aprofundamento das fontes por área: segunda leitura do guia CUDA e do código aberto do driver (a primeira rodada já foi feita), artigos de microbenchmark e resolução dos conflitos entre fontes. Responsável: cada integrante, na sua área.
- **02/11 a 08/11.** Redação do documento por item, conferência dos números e primeira versão do tour. Responsável: cada integrante, na sua área; {{I5}} no tour.
- **09/11.** Revisão cruzada e fechamento do texto. Responsável: todos. **Entrega em 09/11: documentação escrita (1,5).**
- **10/11 a 14/11.** Tour completo, textos finais, slides de reserva e divisão das falas. Responsável: {{I5}}, com todos.
- **15/11.** Ensaio geral com cronômetro. Responsável: todos.
- **16/11.** Seminário. Responsável: todos. **Apresentação (2,0).**

<!-- grafico-cronograma -->

## 8. Resultados esperados e critérios de sucesso
- Todos os itens exigidos pelo professor tratados, ou com a ausência justificada.
- Cada número do texto com fonte e conferido.
- Linguagem que um estudante de computação acompanhe, com termo novo definido na primeira vez.
- Tour 3D funcionando no seminário, com plano de reserva (slides ou capturas) se algo falhar.

## 9. Riscos
- **Itens sem fonte pública (MMU, interrupções, SASS).** Declarar a lacuna, usar o driver aberto e microbenchmarks, e rotular o nível de confiança.
- **Inconsistências nos documentos do fabricante.** Conferir contas entre tabelas e citar a tabela de origem.
- **Pouco tempo para o tour 3D.** Priorizar o texto, que vale nota, e fazer o tour em versão enxuta.
- **Falha técnica no seminário.** Capturas e slides de reserva.

## 10. Referências
**Consultadas**
- NVIDIA. *NVIDIA RTX PRO Blackwell GPU Architecture*, v1.1. Disponível em: https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf. Acesso em: 19 out. 2026.
- NVIDIA. *NVIDIA RTX PRO 6000 Blackwell Workstation Edition*. Disponível em: https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/. Acesso em: 19 out. 2026.
- NVIDIA. *Parallel Thread Execution ISA*, versão 9.4. Disponível em: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html. Acesso em: 19 out. 2026.
- NVIDIA. *CUDA Binary Utilities*, versão 13.4. Disponível em: https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html. Acesso em: 19 out. 2026.
- NVIDIA. *CUDA GPUs: Compute Capability*. Disponível em: https://developer.nvidia.com/cuda-gpus. Acesso em: 19 out. 2026.
- NVIDIA. *CUDA C++ Programming Guide* (edição Legacy), versão 13.4. Disponível em: https://docs.nvidia.com/cuda/cuda-c-programming-guide/. Acesso em: 26 out. 2026.
- NVIDIA. *open-gpu-kernel-modules*, versão 615.78.08. Disponível em: https://github.com/NVIDIA/open-gpu-kernel-modules. Acesso em: 26 out. 2026.
- NVIDIA. *NVIDIA RTX PRO 6000 Blackwell Workstation Edition*: datasheet. Disponível em: https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf. Acesso em: 26 out. 2026.
- NVIDIA. *NVIDIA RTX PRO Blackwell Architecture: Quick Start Guide*. Disponível em: https://images.nvidia.com/aem-dam/Solutions/design-visualization/quadro-product-literature/rtx-pro-blackwell-online-qsg-210x148mm-20250718-r14.pdf. Acesso em: 26 out. 2026.
- JIA, Z.; MAGGIONI, M.; STAIGER, B.; SCARPAZZA, D. P. Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking. *arXiv*:1804.06826, 2018.
- ABDELKHALIK, H.; ARAFA, Y.; SANTHI, N.; BADAWY, A.-H. Demystifying the Nvidia Ampere Architecture through Microbenchmarking and Instruction-level Analysis. *arXiv*:2208.11174, 2022.
- JARMUSCH, A.; GRADDON, N.; CHANDRASEKARAN, S. Dissecting the NVIDIA Blackwell Architecture with Microbenchmarks. *arXiv*:2507.10789, 2025.

**A consultar**
- LUO, W. et al. Dissecting the NVIDIA Hopper Architecture through Microbenchmarking and Multiple Level Analysis. *arXiv*:2501.12084, 2025.
- JARMUSCH, A.; CHANDRASEKARAN, S. Microbenchmarking NVIDIA's Blackwell Architecture: An in-depth Architectural Analysis. *arXiv*:2512.02189, 2025.

Ver também: [[Requisitos da disciplina]], [[Briefing]] e [[Plano de pesquisa]].
