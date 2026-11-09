# Revisão do artigo entregue em 2026-11-09

- Documento: "Estudo da arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell (chip GB202)", 13 páginas, grupo Warp 32. Entregue como documentação escrita (1,5 ponto).
- Revisor: sessão principal (Fable), em 2026-11-09. Quem escreveu o artigo foi outro integrante, fora deste repositório.
- Método: cada afirmação foi comparada com as fontes registradas em `harness/spec/sources/`. As fontes novas que o artigo cita foram abertas nesta data (`mmu-interrupts-sources.md`). O que está marcado **leitura direta** foi conferido pelo revisor no documento ou no código-fonte baixado; o resto veio por resumo automático e ainda pede auditoria do `fact-checker`.
- O experimento da seção 4.4 foi refeito do zero: `harness/examples/saxpy-cu/`.

## 1. Veredito

O artigo cumpre o enunciado: trata os nove itens, tem um experimento real e reproduzível e admite o que não é público. Para uma entrega de graduação é um bom texto.

Ele fica abaixo do que o projeto se propôs em quatro pontos:

1. **Dois erros de conteúdo em itens que o professor cobra** (MMU e RISC ou CISC).
2. **Seis afirmações mais fortes do que a fonte sustenta**, quase sempre um dado de outra geração ou uma dedução do grupo escrita como fato da Blackwell.
3. **Não usa os quatro níveis de confiança** que a proposta prometeu "em todo o material".
4. **Cache e pipeline ficaram rasos**: só tamanhos, sem latência, política ou a divisão real do L1.

Nada disso exige retratação. O seminário pode apresentar as correções como avanço sobre o artigo ("depois da entrega, fomos ao código aberto do driver e à lista oficial de instruções"), o que conta a favor do grupo.

## 2. O que confere

| Afirmação do artigo | Fonte | Como foi conferido |
|---|---|---|
| Listagem SASS da Figura 4, 10 registradores, 0 de spill, 16 bytes por instrução | `nvcc` e `cuobjdump` 13.5.37 | **refeito**: saída idêntica, instrução por instrução |
| PTX versão 9.5 | PTX gerado pelo `nvcc`; página do PTX ISA | leitura direta |
| 65.536 registradores de 32 bits por SM; até 255 por thread; até 48 warps por SM na compute capability 12.0 | Blackwell Tuning Guide 13.5, 1.4.1.1: "64K 32-bit registers per SM", "maximum number of registers per thread is 255", "48 for compute capability 12.0" | leitura direta |
| `trap` para a execução e gera interrupção para a CPU | PTX ISA 9.5, 9.7.21.4: "Abort execution and generate an interrupt to the host CPU" | leitura direta |
| Xid 31 em acesso a endereço inválido | catálogo de Xid: "GPU memory page fault ... logged when a fault is reported by the MMU" | leitura direta |
| Xid 13 em acesso fora do vetor | catálogo de Xid: "Graphics Engine Exception ... Typically this is an out-of-bounds error where the user has walked past the end of an array" | leitura direta |
| 126 TFLOPS; MIG com até 4 instâncias de 24 GB; processo "4 nm" | whitepaper, Tab. 4, p. 44 e 45, p. 48 ("TSMC 4nm 4N NVIDIA Custom Process") | resumo de leitura de página |
| Tabela 1, linha da RTX 6000 Ada | whitepaper, Tab. 4 | idem |
| Pascal: 49 bits, falhas de página, memória unificada, preempção no nível de instrução | whitepaper do Tesla P100, p. 27 e 30 | idem |
| Pascal: páginas de 4 KB, 64 KB e 2 MB | "Pascal MMU Format Changes", p. 2 | idem. Vale **para a Pascal** (ver E1) |
| Bits de controle gravados pelo compilador em cada instrução | Huerta et al., seção 4 | idem. Medido em Ampere e Turing, não na Blackwell |
| AMP é um processador RISC-V que escalona contextos | whitepaper, p. 25 | já auditado |
| 512 × 28 ÷ 8 = 1.792 GB/s; 188 SMs; 24.064 núcleos; L2 de 128 MB | whitepaper | já auditado |

## 3. Erros e afirmações acima da fonte

| # | Gravidade | Onde | O que o artigo diz | O que a fonte diz | Como corrigir no seminário |
|---|---|---|---|---|---|
| E1 | **erro** | 4.8 MMU | "Desde a arquitetura Pascal, a GPU usa endereços virtuais de 49 bits"; páginas de 4 KB, 64 KB e 2 MB | Isso é a Pascal (2016). No código aberto do driver, a família GB20x usa a MMU da Hopper: `uvm_hal.c` diz "GB20x MMU behaves as Hopper MMU", e `uvm_hopper_mmu.c` define **57 bits** de endereço virtual (`num_va_bits_hopper` retorna 57) e **6 níveis** (PDE4, PDE3, PDE2, PDE1, PDE0, PTE), com páginas de 4 KB, 64 KB, 2 MB e 512 MB. **Leitura direta do código** | Mostrar a tabela de 6 níveis e dizer: "o artigo usou o documento da Pascal; o driver atual mostra que a Blackwell foi além" |
| E2 | **erro** | 4.5 RISC ou CISC, Tabela 4 | "só as instruções de carga e armazenamento acessam a memória" | A lista oficial de instruções da Blackwell (Binary Utilities 13.5) tem `LDGSTS` "Asynchronous Global to Shared Memcopy", `UBLKCP` "Bulk Data Copy", `UMEMSETS` "Initialize Shared Memory", `ATOMG` "Atomic Operation on Global Memory". A seção 3.1.1 mostra aritmética com operando direto de constante. **Leitura direta** | Conclusão refinada: RISC no formato, com instruções de acelerador. Ver `vault/03-Roteiro/08` |
| E3 | sem fonte | 4.1 | A placa tem 188 de 192 SMs porque "as partes com problema são desligadas" | O whitepaper não dá motivo. A p. 8 diz até que a placa usa o GB202 completo, e as tabelas dão 188 | "A NVIDIA não explica a diferença, e o documento se contradiz" |
| E4 | fonte não sustenta | 4.9 | "pequenos processadores RISC-V dentro dela, como o GSP (NVIDIA, 2026d)" | O README citado não menciona RISC-V. Diz que o GSP serve para "offload GPU initialization and management tasks". **Leitura direta.** RISC-V só está documentado para o AMP | Dizer RISC-V só do AMP |
| E5 | não confere com o exemplo | 4.2 | "encontramos ... um registrador que sempre vale zero (RZ)" | `RZ` não aparece na listagem da Figura 4 nem na reprodução | Tirar `RZ` da lista ou mostrar outro código em que ele apareça |
| E6 | simplificação | 4.6 | Na Blackwell os 128 núcleos fazem inteiro ou ponto flutuante | O whitepaper (p. 11) diz que são unificados, mas "only operate as either FP32 or INT32 ... in any given clock cycle" e que nem toda operação inteira dobra de vazão | Acrescentar "um tipo por ciclo" |
| E7 | derivado como fato | 4.10 | "quatro escalonadores escolhem, a cada ciclo, qual warp vai executar" | Vem de medições em outras GPUs: Volta (Jia), Ampere e Turing (Huerta), RTX 5080 (Jarmusch). O whitepaper desta placa não escreve "quatro" | Selo "derivado" |
| E8 | derivado como fato | 4.6 | Divergência: "executa primeiro um caminho e depois o outro"; pesquisadores "fazem testes na placa" | O guia CUDA diz que as threads fora do desvio "will be masked off". Huerta et al. não mediram nenhuma Blackwell | Usar a frase do guia; dizer em que GPUs foi medido |
| E9 | acima da fonte | 4.3 | "o driver compila o PTX na hora"; o PTX "é igual para todas as gerações" | O PTX ISA diz "translated at install time"; o guia CUDA fala em código "PTX-only, GPU forward compatible". O PTX é versionado (9.5) | "O PTX é estável e versionado; a tradução para SASS acontece depois" |
| E10 | termo | Tabela 2 | "Frequência máxima: 2.617 MHz" | A Tab. 4 chama de "GPU Boost Clock" | Usar o nome da fonte |
| E11 | conflito não declarado | Tabela 1 | RTX 6000 Ada com 960 GB/s | O whitepaper dá 1.008 GB/s na Tab. 1 e 960 GB/s na Tab. 4 | Citar a tabela usada |
| E12 | contradição interna | 4.2 e 4.9 | 4.2: na GPU os registradores não são salvos na troca. 4.9: a preempção salva o estado na memória | As duas coisas valem, em níveis diferentes: entre warps do mesmo programa nada é salvo; entre programas, o contexto vai para a memória da GPU (P100, p. 30) | Separar os dois níveis na fala |
| E13 | incompleto | 4.8 | Na memória unificada "o driver copia as páginas" | O P100 descreve migração sob demanda **ou** mapeamento pelo barramento | Detalhe; só se perguntarem |
| E14 | fonte fraca | 1, 3 | "a GPU mais potente da NVIDIA para computadores de mesa"; dados de concorrentes | Fontes secundárias (VRLA Tech, Guru3D). Não conferidas por nós | Não repetir superlativos no seminário |

## 4. O que falta em relação à proposta e ao enunciado

| Item | Situação no artigo | O que o seminário acrescenta |
|---|---|---|
| Níveis de confiança (proposta, seção 5) | ausentes | selo em todo beat |
| Mecanismo de cache | só tamanhos | latências medidas na RTX 5080 (`derived`): L1 de 30 a 40 ciclos, L2 perto de 358, memória global perto de 877; L1 e memória compartilhada no mesmo bloco de 128 KB |
| Pipeline | "não divulgado" | 4 partições, 4 ciclos em INT32 e FP32, estágios citados por Huerta et al. (`derived`) |
| MMU | 49 bits (Pascal) | 57 bits, 6 níveis, 4 tamanhos de página, pelo driver aberto |
| Interrupções | "manda uma interrupção pelo PCIe" | o caminho no driver: MSI ou MSI-X, metade de cima (`nvidia_isr`), metade de baixo em thread do kernel; falha de página gravada em buffer, tratada em lote e reexecutada |
| Instruções de Tensor Core | ausentes | `HMMA` e `QMMA` compilados em `harness/examples/mma/` |
| Comparação GPU contra CPU item a item (objetivo 6 da proposta) | só na conclusão | tabela-síntese no fechamento |
| Tamanho do conjunto de instruções | ausente | cerca de 257 mnemônicos em 13 categorias (a reconferir) |

## 5. Observações de forma

- O artigo tem cinco autores. O resumo do enunciado guardado em `vault/01-Briefing/Requisitos da disciplina.md` fala em grupo de até quatro. Conferir com o professor ou corrigir a nota.
- A seção 4.11 atribui o tour 3D a um integrante. O repositório não registra autoria por pessoa.
- A proposta de 26/10 que está no repositório é o rascunho com campos "[nome 1]". A versão entregue não está aqui.
- Referências ausentes para conteúdo usado: CUDA Binary Utilities (lista de instruções SASS) e Jia et al. (bits de controle na Volta).

## 6. O que não foi verificado

- Dados de concorrentes da Tabela 1 e da seção 3 (AMD, Intel, Apple) e as datas das gerações.
- Lindholm et al. (2008) e Hennessy e Patterson (2019), citados para SIMT: não abertos.
- A lista exata de tamanhos de página da HAL Hopper (`page_sizes`). Os quatro tamanhos acima saem da função de profundidade da tabela.
- Que o GB202 é tratado pelo driver como "GB20x": é pelo nome da família, não por uma linha do código que cite o GB202.
- As seções do whitepaper, do P100, de Huerta et al. e do guia CUDA foram lidas por outro agente, parte por resumo automático. Auditoria formal pendente.
