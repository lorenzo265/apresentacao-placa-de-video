# Fontes de MMU, interrupções e do artigo do grupo (rodada de 2026-11-09)

> **Rodada sem auditoria formal do `fact-checker`.** Os pontos centrais foram reconferidos por **leitura direta** pela sessão principal em 2026-11-09 (seção "Conferência direta", no fim). O resto continua como veio da coleta, parte por resumo automático: não use em texto final antes da auditoria.

Data de acesso de todas as fontes: 2026-11-09. Nenhuma ferramenta de shell estava disponível (sem `curl` nem `pdftotext`). Dois modos de leitura, marcados em cada seção:

- **Leitura direta (PDF):** o PDF foi baixado pelo WebFetch e as páginas foram lidas como imagem com a ferramenta Read. O texto abaixo foi transcrito da página. Páginas citadas conforme o rodapé do documento.
- **Resumo automático:** WebFetch devolveu a página já processada por um modelo pequeno. Os trechos entre aspas vêm desse resumo e **podem ter sido reescritos**. Onde o resumo deu numeração de linhas de código, os números são aproximados (o próprio resumo avisou "pode estar errado em uma ou duas linhas").
- **Código-fonte via WebFetch:** `raw.githubusercontent.com`, ramo `main`, lido também por resumo automático. O arquivo `uvm_blackwell_mmu.c` (linhas 1 a 113) foi devolvido literalmente com números de linha; os demais, em trechos.

Regra de procedência desta rodada: `confirmed` só para fonte oficial NVIDIA que trata da Blackwell ou de todas as GPUs atuais; `derived` para outra geração (Pascal, Ampere, Turing) ou outra versão do documento.

Fontes já registradas e fora do escopo: `isa-sources.md`, `nvidia-rtx-pro-blackwell-architecture-v1.1.md` (mas ver a seção 10 abaixo), `nvidia-rtx-pro-6000-product-page.md`, `physical-card-sources.md`.

## 1. NVIDIA, Blackwell Tuning Guide (resumo automático)
URL aberta: https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html (HTML). O PDF do artigo (`archive/13.4.1/pdf/...`) **não foi aberto**; a página HTML atual se identifica como "Blackwell Tuning Guide 13.5 documentation (v13.5)", histórico de revisão com só "Version 1.0". `confirmed` (CC 12.0 citada de forma explícita).

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Registradores por SM | "The register file size is 64K 32-bit registers per SM." | 1.4.1.1 Occupancy |
| Registradores por thread | "The maximum number of registers per thread is 255." | 1.4.1.1 |
| Warps por SM | "The maximum number of concurrent warps per SM is 64 for compute capability 10.0 and 48 for compute capability 12.0." | 1.4.1.1 |
| Blocos por SM | "The maximum number of thread blocks per SM is 32 for devices of compute capability 10.0 and 12.0." | 1.4.1.1 |
| Memória compartilhada por SM (CC 12.0) | "For devices of compute capability 12.0, shared memory capacity per SM is 128KB." | 1.4.1.1 |
| Memória compartilhada por bloco (CC 12.0) | "For devices of compute capability 12.0 the maximum shared memory per thread block is 99 KB." | 1.4.1.1 |
| Divisão L1/compartilhada | "the portion of the L1 cache dedicated to shared memory (known as the carveout) can be selected at runtime" | 1.4.2.3 Unified Shared Memory/L1/Texture Cache |
| Opções de carveout | "0, 8, 16, 32, 64, 100, 132, 164, 196 and 228 KB per SM" (o resumo ligou essa lista ao B200, CC 10.0; para 12.x ver seção 8) | 1.4.2.3 |
| Threads por SM | **não declarado** no Tuning Guide. Derivado: 48 warps x 32 = 1.536 (`derived`, conta nossa) | , |
| Tabela de limites | não há tabela de limites no conteúdo devolvido | , |

## 2. NVIDIA, Pascal MMU Format Changes (leitura direta, 5 páginas do PDF)
URL: https://nvidia.github.io/open-gpu-doc/pascal/gp100-mmu-format.pdf. Metadados do PDF: autor NVIDIA, março de 2016. `derived` (Pascal). Páginas conforme a ordem do PDF (1 a 5; o documento não numera).

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Endereço virtual | "Expanded Virtual Addressing - Upto 49 Bits of VA." | p. 1, Highlights |
| Endereço físico (sysmem) | "Up to 47 bits of sysmem PA." Tabela de PTE: "the hardware supports 47 bits of sysmem addresses" (formato de 58 bits) | p. 1 e p. 3 |
| Páginas grandes | "Support for 2MB big pages." "Dropped support for 128KB Big Pages." | p. 1 |
| Níveis | "5 Level Format to support the expanded virtual addressing." "All page levels/tables are now 4KB in size." | p. 1 |
| Tamanhos de página | tabela "Page Level Sizes and Coverage": **4KB, 64KB e 2MB** (e nenhum outro). Alinhamento igual ao tamanho | p. 2 |
| Tabela de páginas | 4KB: 512 entradas, 4KB, cobre 2MB. 64KB: 32 entradas, 256B (várias tabelas empacotadas em uma página de 4K), cobre 2MB. 2MB: usa PD0 | p. 2 |
| Nomes dos níveis | Page Directory0 (PD0), PD1, PD2, PD3 e a Page Table (PT). Entradas: PD0 256 (8 bits, cobre 512MB), PD1 512 (9 bits, 256GB), PD2 512 (9 bits, 128TB), PD3 4 (2 bits, 512TB) | p. 2 |
| Divisão do VA de 49 bits | PD3 [48:47], PD2 [46:38], PD1 [37:29], PD0 [28:21], página de 2MB [20:0]; PT 64K [20:16] com página [15:0]; PT 4K [20:12] com página [11:0] | p. 2, "49 Bit VA breakdown" |
| Abertura (aperture) | 0 = inválido, 1 = memória de vídeo local, 2 = memória de sistema coerente, 3 = memória de sistema não coerente (PDE). Na PTE o valor 1 é "peer video memory" | p. 3 e 4 |
| Bits da PTE | Valid, Privileged, Read-Only, Atomic-Disable, Encryption ("Do not use. Set to 0"), PA, Peer ID, Aperture, Volatile, Kind (8 bits), CompTag Line (18 bits). Total 62 bits | p. 4 |
| Falha por permissão | "Setting this bit causes writes to this page to fault." (Read-Only); "An atomic request to a page with Atomic Disable high will fault." | p. 4 e 5 |
| PDE0 | dois ponteiros (páginas grandes e pequenas); total "64 bits for the two level format and 99 bits for the five level format" | p. 3 e 4 |

Conta conferida: 2 + 9 + 9 + 8 + 21 = 49 bits. Coerente.

## 3. NVIDIA, whitepaper Tesla P100 / Pascal GP100, WP-08019-001_v01.1 (leitura direta)
URL: https://images.nvidia.com/content/pdf/tesla/whitepaper/pascal-architecture-whitepaper.pdf (3,1 MB; páginas lidas: 2 a 4, 27, 28 e 30, numeração do rodapé). `derived` (Pascal, 2016).

| Dado | Trecho | Onde |
|---|---|---|
| 49 bits | "GP100 extends GPU addressing capabilities to enable 49-bit virtual addressing. This is large enough to cover the 48-bit virtual address spaces of modern CPUs, as well as the GPU's own memory." | p. 27, Pascal GP100 Unified Memory |
| Falhas de página | "Memory page faulting support in GP100 is a crucial new feature that provides more seamless Unified Memory functionality." | p. 27 |
| Migração sob demanda | "If a kernel running on the GPU accesses a page that is not resident in its memory, it faults, allowing the page to be automatically migrated to the GPU memory on-demand. Alternatively, the page may be mapped into the GPU address space for access over the PCIe or NVLink interconnects (mapping on access can sometimes be faster than migration)." | p. 27 |
| Coerência | "With the new page fault mechanism, global data coherency is guaranteed with Unified Memory." | p. 27 |
| Alocador do sistema | memória do `malloc` acessível da GPU "with operating system support" | p. 28 |
| Preempção | "allows compute tasks running on the GPU to be interrupted at instruction-level granularity, and their context swapped to GPU DRAM." | p. 30, Compute Preemption |
| Kepler | "the Kepler GPU architecture only provided coarser-grained preemption at the level of a block of threads" | p. 30 |

## 4. NVIDIA, Analyzing Xid Errors with the Xid Catalog (resumo automático)
URL: https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html. A página mostra "Last updated on Nov 04, 2026". `confirmed` (catálogo geral de todas as GPUs NVIDIA de datacenter e workstation; não cita Blackwell especificamente).

| Dado | Trecho | Onde |
|---|---|---|
| Xid 13, descrição | "Graphics Engine Exception" | catálogo, linha Xid 13 |
| Xid 13, condição | "This event is logged for general user application faults." (o resumo acrescenta que costuma ser acesso fora dos limites e que falha de hardware ou de software de sistema é rara; essa parte é paráfrase do resumo) | coluna Trigger Conditions |
| Xid 13, ação | RESTART_APP; investigação WORKFLOW_XID_13 | coluna Resolution |
| Xid 31, descrição | "GPU memory page fault" | catálogo, linha Xid 31 |
| Xid 31, condição | "This event is logged when a fault is reported by the MMU, such as when an illegal address access is made." | Trigger Conditions |
| Xid 31, ação | RESTART_APP; WORKFLOW_XID_31 (falhas repetidas na mesma GPU: RUN_DCGMEUD, possível problema de hardware) | Resolution |

O catálogo não tem coluna "Causes"; as causas estão em "Trigger Conditions".

## 5. NVIDIA, README do GSP, driver FreeBSD 595.80 (resumo automático)
URL: https://download.nvidia.com/XFree86/FreeBSD-x86_64/595.80/README/gsp.html. `confirmed` (driver geral; "Turing and later" cobre a Blackwell).

| Dado | Trecho | Onde |
|---|---|---|
| O que é | "Some GPUs include a GPU System Processor (GSP) which can be used to offload GPU initialization and management tasks." | abertura |
| Função | tarefas que o driver faria na CPU; "Offloading tasks which were traditionally performed by the driver on the CPU can improve performance" | abertura |
| GPUs | "The GSP firmware will be used by default for all Turing and later GPUs." | uso padrão |
| Firmware | arquivos entregues com o driver, módulos `nvidia_gsp_*_fw.ko` (ex.: `nvidia_gsp_tu10x_fw.ko` para Turing) | texto |
| RISC-V | **a página não menciona RISC-V**; não diz qual é a ISA do GSP | , |
| Controle | `nvidia-smi -q` mostra "GSP Firmware Version"; desligar com `hw.nvidia.registry.EnableGpuFirmware=0` | texto |

## 6. NVIDIA, PTX ISA (resumo automático da versão atual e leitura direta de uma versão antiga)
- **Versão atual:** a página https://docs.nvidia.com/cuda/parallel-thread-execution/index.html abriu com o título "Parallel Thread Execution ISA Version 9.5" em 2026-11-09. O registro de 2026-10-19 dizia 9.4; **a versão mudou entre as duas leituras** (ou a leitura anterior pegou página em cache). O HTML devolvido tem 471.126 caracteres e o texto vem truncado em "9.7.9.6 lop3" (seção 9.7.9 da versão 9.5); a seção `trap` **não foi lida na 9.5**.
- **Texto do `trap` lido em PTX ISA 7.5** (PDF https://docs.nvidia.com/cuda/archive/11.5.1/pdf/ptx_isa_7.5.pdf, leitura direta, p. 380 do rodapé, seção 9.7.18.4). `derived` por ser outra versão do mesmo documento; a nota "Supported on all target architectures" é da 7.5.

| Dado | Trecho | Onde |
|---|---|---|
| trap | "Perform trap operation." Sintaxe `trap;` | 7.5, 9.7.18.4 |
| trap, descrição | "Abort execution and generate an interrupt to the host CPU." | 7.5, 9.7.18.4 |
| trap, notas | "Introduced in PTX ISA version 1.0." "Supported on all target architectures." Exemplos `trap;` e `@p trap;` | 7.5, p. 380 |
| Tradução (9.5) | "PTX programs are translated at install time to the target hardware instruction set." | 9.5, 1.1 |
| Tradutor (9.5) | "The PTX-to-GPU translator and driver enable NVIDIA GPUs to be used as programmable parallel computers." | 9.5, 1.1 |
| Tradução (9.5) | "such a function is compiled to the PTX instruction set and the resulting kernel is translated at install time to the target GPU instruction set." | 9.5, 2.1 |
| JIT | o resumo da 9.5 **não usa** "JIT" nem "just-in-time" nos trechos lidos | , |

## 7. Huerta et al., "Analyzing modern NVIDIA GPU cores", arXiv 2503.20481v1 (leitura direta, páginas 1 a 12 do PDF)
URL: https://arxiv.org/pdf/2503.20481 (814 KB). `derived`: as medidas são de GPUs Ampere (RTX 3080, 3080 Ti, 3090 e A6000, CUDA 11.4 e NVBit 1.5.5) com validação cruzada em uma Turing (RTX 2080 Ti) na Tab. 4. **Blackwell não foi medida.** A seção 7.6 afirma que os resultados "remain applicable to other NVIDIA architectures", baseada em anúncios públicos, sem medida.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Bits de controle | "the ISA of modern NVIDIA GPU architectures contains control bits and information that the compiler provides to maintain correctness" e "these GPU architectures rely on the compiler to handle register data dependencies" | seção 4 |
| Stall counter | contador por warp, do compilador; "If this counter is not zero, this warp is not candidate to issue instructions" | seção 4 |
| Yield | "Another control bit is called Yield" | seção 4 |
| Contadores de dependência | "Each warp has six special registers" `SB0`..`SB5`, cada um conta até 63; máscara de 6 bits por instrução, dois campos de 3 bits para os contadores incrementados | seção 4 |
| Bit de reúso | "the reuse bit" por operando fonte, controla o cache de registradores | seção 4 |
| Registrador regular | "65536 32-bit registers per SM", grupos de 32 (2.048 registradores de warp); "The number of registers used by a particular warp can vary from 1 to 256" (a NVIDIA diz 255 por thread, ver seção 1) | 5.3 |
| Registrador uniforme | "Each warp has 64 private, 32-bit registers that store values shared by all the threads of the warp." | 5.3 |
| Predicado | "Each warp has eight 32-bit registers, each bit being a different thread"; predicado uniforme: "eight 1-bit registers" por warp | 5.3 |
| Outros | "SB Registers" (6 por warp), "B Registers" (16, controle de reconvergência), "Special Registers ... thread or block IDs" | 5.3 |
| `RZ`, `PT` | **não aparecem** nas páginas lidas (1 a 12); na conta de scoreboard o artigo conta "255 for the regular registers, 63 for the uniform", sem citar `RZ` | , |
| Subnúcleos | "SMs have four different sub-cores and warps are evenly distributed among sub-cores in a round robin manner (i.e., warp ID %4)"; cada subnúcleo emite uma instrução por ciclo | 5.2, seção 4 |
| Política do escalonador | "uses a greedy policy that selects an instruction from the same warp if it meets the eligibility criteria"; trocar para "the youngest one"; nome dado: "Compiler Guided Greedy Then Youngest (CGGTY)". "only confirmed this behavior for warps within the same CTA" | 5.1.2 |
| Estágios | busca com escalonador próprio, decodificação, emissão, e para instruções de latência fixa dois estágios intermediários, Control e Allocate, antes da leitura de operandos; "do not make use of" unidade coletora de operandos. **Não dá a profundidade total do pipeline** | 5.1, 5.3 |
| Banco de registradores | dois bancos por subnúcleo, uma porta de leitura de 1.024 bits por banco | 5.3 |
| Tab. 4 | RTX 3080: 68 SMs, 48 warps por SM, 128 KB L1/compartilhada; A6000: 84 SMs; RTX 2080 Ti (Turing): 68 SMs, **32 warps por SM**, 96 KB | Tab. 4 |
| Hardware coletando bits | NVIDIA "does not provide access" aos bits de controle pelas ferramentas; usam CUAssembler e SASS | seção 6 |

## 8. NVIDIA, Guia de programação CUDA (versão 13.5, resumo automático)
O endereço antigo `cuda-c-programming-guide` não foi tentado; o guia atual está em `docs.nvidia.com/cuda/cuda-programming-guide/`. Páginas abertas: `01-introduction/programming-model.html`, `04-special-topics/unified-memory.html` (título "4.1. Unified Memory"), `05-appendices/compute-capabilities.html` (5.1) e `02-basics/nvcc.html` (2.7). `confirmed`.

| Dado | Trecho | Onde |
|---|---|---|
| SIMT | "A warp executes the kernel code in a Single-Instruction Multiple-Threads (SIMT) paradigm." "all threads in the warp are executing the same kernel code, but each thread may follow different branches through the code." | 1.2.2.2 Warps and SIMT |
| Warp | "threads are organized into groups of 32 threads called warps." | 1.2.2.2 |
| Divergência | "the threads which do not follow the branch will be masked off." "this is sometimes called warp divergence." A frase "executes each branch path" **não aparece** nessa página | 1.2.2.2 |
| Execução independente | a página só remete a "Independent Thread Execution" (seção 3.2.2.1.1, **não aberta**); avisa "Hardware execution may differ" | 1.2.2.2 |
| Limites numéricos | a página 1.2 não traz limites; remete ao apêndice 5.1 | 1.2.3.3 |
| Registradores | Tab. 34: "Number of 32-bit registers per SM: 64 K"; "per thread: 255" (valores únicos) | 5.1, Tab. 34 |
| Threads/warps/blocos por SM | Tab. 33: valores listados 1024, 2048, 1536, 2048, 1024, 1536 (threads) e 32, 64, 48, 64, 32, 48 (warps), mas "o texto extraído achata as colunas" e **a coluna da CC 12.0 não pôde ser confirmada** | 5.1, Tab. 33 |
| Memória compartilhada | Tab. 35, 12.x: cache de dados unificado 128 KB; capacidades de memória compartilhada "0, 8, 16, 32, 64, 100" KB. 10.0: 256 KB e "0, 8, 16, 32, 64, 100, 132, 164, 196, 228" | 5.1, Tab. 35 |
| Memória unificada, falhas | "these systems usually use page faults in case a processor accesses a memory address" | 4.1.1.2.1.2 |
| Memória unificada, requisito | "For devices with compute capability 6.x or higher but without pageable memory access" (modo só com memória gerenciada) | 4.1.2 |
| 49 bits | **não aparece** em nenhuma das páginas abertas | , |
| PTX e forward compatibility | "PTX-only, GPU forward compatible" (`-arch=compute_<XY>`); "PTX and Cubin, GPU forward compatible" (`-arch=sm_<XY>`); "no PTX, no GPU forward compatibility" (`-arch=native`) | 2.7.3.1 |
| ptxas | "Individual PTX code is then passed to the ptxas tool, which generates Cubin for the target hardware ISAs." | 2.7.2 |
| JIT | a página cita JIT apenas como compilação "driven by the CUDA runtime compiler nvrtc"; **não descreve a compilação do PTX pelo driver ao carregar** | 2.7 |

## 9. NVIDIA, open-gpu-kernel-modules, ramo `main` (código-fonte, leitura por resumo)
Repositório: https://github.com/NVIDIA/open-gpu-kernel-modules, diretório `kernel-open/nvidia-uvm/` e `kernel-open/nvidia/`. O README do repositório (resumo) diz que os módulos funcionam em "any Turing or later GPU", exigem o firmware GSP e **lista a "NVIDIA RTX PRO 6000 Blackwell Workstation Edition" na tabela de PCI IDs**. `confirmed` para o que o driver programa; não é documento de hardware.

Estabelecer que GB202 cai na entrada "GB20x" do driver é uma inferência pelo nome do chip: o código comenta "GB20x MMU behaves as Hopper MMU" e usa o enum `..._GB200`; **não abri a tabela que liga o PCI ID do GB202 a esse enum** (lacuna).

### 9.1 MMU: arquivos existentes e qual HAL a Blackwell usa
Arquivos `uvm_*_mmu.c` listados na página do diretório (listagem truncada pelo site): `uvm_ampere_mmu.c`, `uvm_blackwell_mmu.c`, `uvm_hopper_mmu.c`. Também `uvm_blackwell.c`, `uvm_blackwell_ce.c`, `uvm_blackwell_host.c`, `uvm_blackwell_fault_buffer.{c,h}`, `uvm_hopper_*`, `uvm_hal.c`.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| HAL da família GB20x | Em `arch_table[]`: GB200 (parent GB100) com o comentário "Note that GB20x MMU behaves as Hopper MMU, so it inherits from" e `.mmu_mode_hal = uvm_hal_mmu_mode_hopper` | `uvm_hal.c`, `arch_table[]` |
| HAL da família GB100 | parent GH100 (Hopper), `uvm_hal_mmu_mode_blackwell` | `uvm_hal.c` |
| Chips integrados | GB10B, GB10C, GB20B usam `uvm_hal_mmu_mode_blackwell_integrated` | `uvm_hal.c`, `chip_table[]` |
| Blackwell reaproveita Hopper | "hopper_mmu_mode_hal = uvm_hal_mmu_mode_hopper();" depois "mmu_mode_hal->page_table_depth = page_table_depth_blackwell;" | `uvm_blackwell_mmu.c`, l. 68 a 83 |
| Níveis (GB100) | "On Blackwell, the UVM page tree 'depth' maps to hardware as follows:" 0 PDE4 (VA 56:56); 1 PDE3 (55:47); 2 PDE2 ou PTE de 256G (46:38); 3 PDE1 ou PTE de 512M (37:29); 4 PDE0 (PDE duplo 64K/4K, ou PTE de 2M) (28:21); 5 PTE_64K / PTE_4K (20:16 / 20:12) | `uvm_blackwell_mmu.c`, l. 24 a 32 |
| Tamanhos (GB100) | `page_sizes_blackwell`: "UVM_PAGE_SIZE_256G \| UVM_PAGE_SIZE_512M \| UVM_PAGE_SIZE_2M \| UVM_PAGE_SIZE_64K \| UVM_PAGE_SIZE_4K"; integrada: 2M, 64K, 4K | `uvm_blackwell_mmu.c`, l. 58 a 66 |
| Níveis (Hopper, usado pela GB20x) | "For Hopper, the UVM page tree 'depth' maps to hardware as follows:" 0 PDE4 56:56; 1 PDE3 55:47; 2 PDE2 46:38; 3 PDE1 (ou PTE 512M) 37:29; 4 PDE0 (PDE duplo 64k/4k, ou PTE 2M) 28:21; 5 PTE_64K / PTE_4K 20:16 / 20:12 | `uvm_hopper_mmu.c`, l. 21 a 29 (aprox.) |
| Tamanhos (Hopper) | `page_table_depth_hopper` trata 2M (profundidade 4), 512M (3) e 4K/64K (5). A função `page_sizes` do Hopper **não foi extraída**, então a lista completa de tamanhos da GB20x não foi lida literalmente | `uvm_hopper_mmu.c`, l. 52 a 63 (aprox.) |
| Bits de VA (Hopper) | `static NvU32 num_va_bits_hopper(void)` retorna `57`; `va_base[] = { 56, 47, 38, 29, 21 }`; a atribuição é `hopper_mmu_mode_hal.num_va_bits = num_va_bits_hopper;` | `uvm_hopper_mmu.c` (l. 110 a 113 aprox.) |
| Espaço de VA do driver | `max_channel_va = 1ull << 57` e `max_host_va = 1ull << 57`; `rm_va_size = 64 * UVM_SIZE_1PB` | `uvm_blackwell.c`, `uvm_hal_blackwell_arch_init_properties` |

Conta conferida: 1 + 9 + 9 + 9 + 8 = 36 bits nos diretórios (de 56 a 21) e 21 bits de deslocamento = 57 bits. Coerente com `num_va_bits = 57`. Na Pascal o diretório mais alto ocupava [48:47]; na Hopper o PDE3 ocupa [55:47] e acrescenta o PDE4 em [56].

### 9.2 Falhas de página e interrupções (UVM)
| Dado | Trecho | Onde |
|---|---|---|
| Interrupções por pulso | "Turing switches to pulse-based interrupts for replayable/non-replayable" | `uvm_gpu_isr.c`, l. 34 |
| Nível contra pulso | "Level-based interrupts are rearmed automatically as long as the interrupt condition is set. Pulse-based interrupts, on the other hand, are re-triggered by clearing their interrupt line and forcing the interrupt condition to be re-evaluated." | l. 38 a 41 |
| Tempestade de interrupções | "interrupts need to be disabled at interrupt handling boundaries, in order to avoid interrupt storms." | l. 43 a 44 |
| Metade de cima | "This is called from RM's top-half ISR (see: the nvidia_isr() function), and UVM is given a chance to handle the interrupt, before most of the RM processing." Função `uvm_isr_top_half()` (l. 218), entrada `uvm_isr_top_half_entry()` (l. 281) | l. 194 a 196 |
| Metade de baixo | "Schedule a bottom half, but do *not* release the GPU ISR lock. The bottom half releases the GPU ISR lock as part of its cleanup." Fila `nv_kthread_q` (`parent_gpu->isr.bottom_half_q`) | l. 112, 384 |
| Referências | "We take a reference during the top half, and an additional reference for each scheduled bottom. References are dropped at the end of the bottom halves." | l. 250 a 252 |
| Trava entre as metades | "The service_lock semaphore is taken in the top half using a raw semaphore call (down_trylock()). ... The pair of the two raw calls result in an ownership 'transfer' between the top and bottom halves." | l. 596 a 600 |
| Reativação | sequência "delicate": 1) reabilitar interrupções de falha, 2) rearmar as por pulso, 3) soltar `service_lock`, 4) soltar `interrupts_lock` | l. 755 a 759 |
| Falhas reproduzíveis | "The Graphics Engine faults are called replayable faults, while the rest are called non-replayable." | `uvm_gpu_non_replayable_faults.c`, l. 43 a 44 |
| Origem das não reproduzíveis | "A non-replayable fault originates in an engine other than Graphics." "UVM services non-replayable faults from the Copy and PBDMA (Host/ESCHED) Engines." | l. 47 e 48 |
| Fault and switch | falhas de CE e PBDMA fazem o hardware realizar preempção do canal associado, "a mechanism called 'fault and switch'" | l. 61 a 62 |
| Divisão RM e UVM | "While replayable faults are always the responsibility of UVM, the servicing of non-replayable faults is split between RM and UVM." UVM lê de um "shadow buffer", um buffer comum de CPU compartilhado com o RM; o RM acessa o buffer de hardware, lê o PUT e atualiza o GET | l. 93 a 105 |
| Buffer de falhas (reproduzíveis) | "Reading fault buffer GET/PUT pointers from the CPU is expensive." "Slow path: read the put pointer from the GPU register via BAR0 over PCIe" | `uvm_gpu_replayable_faults.c`, funções `uvm_parent_gpu_replayable_faults_pending` e comentário do parâmetro `update_put_ratio` |
| Lote | "Fetch a batch of faults from the buffer." "When possible, we coalesce duplicate entries to minimize the fault handling overhead." | mesmo arquivo, `fetch_fault_buffer_entries` |
| Reprodução | função `push_replay_on_gpu`; cancelamento `cancel_faults_*`; "Because each cancel itself triggers a replay..." | mesmo arquivo |
| Falha fatal | "RM handles the fault, which will do the correct fault reporting in the kernel logs and will initiate channel teardown" | `uvm_gpu_non_replayable_faults.c`, l. 553 a 554 |
| Blackwell, fault buffer | "NV_PFAULT_FAULT_TYPE_COMPRESSION_FAILURE fault type is deprecated on Blackwell."; só CE e Host (HUB) e GR são atendidas | `uvm_blackwell_fault_buffer.c` |

Não li os 38.330 últimos caracteres de `uvm_gpu_replayable_faults.c` na primeira passada; a segunda passada (a partir de 100.000) trouxe só `uvm_parent_gpu_service_replayable_faults`, `service_fault_batch` e o cancelamento, sem comentário sobre metade de baixo.

### 9.3 Interrupção no módulo `nvidia` (`kernel-open/nvidia/nv.c`)
Lido só até o caractere 100.000 de 176.317.

| Dado | Trecho ou comportamento | Onde |
|---|---|---|
| ISR de cima | `nvidia_isr` chama `rm_isr(...)`; devolve `IRQ_WAKE_THREAD` quando uma metade de baixo precisa rodar | `nv.c`, `nvidia_isr` |
| MSI-X | comentário: "nvidia_isr_msix() is called for each of the MSI-X vectors and they can run in parallel on different CPUs (cores), but this is not currently." Serializa com spinlock | `nvidia_isr_msix` |
| Metade de baixo | `nvidia_isr_kthread_bh` e `nvidia_isr_msix_kthread_bh` chamam `nvidia_isr_common_bh`, que chama `rm_isr_bh(sp, nv)` | `nv.c` |
| Registro do IRQ | caminho legado/MSI: `request_threaded_irq(nv->interrupt_line, nvidia_isr, nvidia_isr_kthread_bh, ...)`; caminho MSI-X: `nv_request_msix_irq(nvl)` | `nv_start_device` |
| MSI/MSI-X | habilitados por `nv_init_msix(nv)` se houver capability MSI-X e `rm_is_msix_allowed`; `nv_init_msi(nv)` se houver MSI; condicionado ao registro `NV_REG_ENABLE_MSI`. As chamadas `pci_enable_msix` e `pci_enable_msi` **não foram vistas** | `nv_start_device` |

## 10. NVIDIA, whitepaper RTX PRO Blackwell v1.1 (pontos de A2; leitura direta, páginas 8, 11, 12, 25, 44, 45, 46 a 48)
Mesma URL de `nvidia-rtx-pro-blackwell-architecture-v1.1.md`. `confirmed`. Páginas conforme o rodapé.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Chip e SMs | "The full GB202 GPU includes 12 Graphics Processing Clusters (GPCs), 96 Texture Processing Clusters (TPCs), 192 Streaming Multiprocessors (SMs)... The RTX PRO 6000 GPUs use the full GB202 GPU." | p. 8 |
| SMs da placa | Tab. 4: GPCs 12, TPCs 94, SMs 188, 24.064 núcleos CUDA | p. 46 |
| Motivo dos 188 SMs | **o documento não explica** por que 188 e não 192; não fala em partes com defeito nem em rendimento de fabricação | pesquisado em p. 8, 45, 46 |
| Inteiro e ponto flutuante | "INT operation update added in v1.1": "the number of possible integer operations in Blackwell GB20x GPUs are doubled for many integer instructions compared to Ada, by fully unifying the INT32 cores with the FP32 cores... However, the unified cores can only operate as either FP32 or INT32 cores in any given clock cycle. While many common INT operations can run at up to 2x throughput, not all INT operations can attain 2x speedups." | p. 11 |
| SM, figura 6 | Ada: coluna "FP32 / INT32" e coluna "FP32" separadas; Blackwell: bloco único "FP32 / INT32". Cada partição: "L0 i-Cache + Warp Scheduler + Dispatch (32 thread/clk)" e "Register File (16, 384 x 32-bit)" | p. 11, Fig. 6 |
| Frequência | Tab. 4, linha **"GPU Boost Clock (MHz)"**: 2617 (Workstation), 2280 (Max-Q), 2505 (Ada), 1800 (A6000). O documento não usa "máxima" | p. 46 |
| FP32 | Tab. 4: "Peak FP32 TFLOPS (non-Tensor)" 126,0 (nota 1: "Peak rates are based on GPU Boost Clock") | p. 46 e 48 |
| Processo | Tab. 4: "TSMC 4nm 4N NVIDIA Custom Process" | p. 48 |
| MIG | "NVIDIA Multi-Instance GPU (MIG) allows the Blackwell GB202 GPU to be partitioned into as many as four separate instances"; Tab. 3: Workstation e Max-Q: 1x 96GB, 2x 48GB, **4x 24GB** ("Total Memory Available per Instance") | p. 44 e 45 |
| AMP | "The AI Management Processor is implemented using a dedicated RISC-V processor located at the front of the GPU pipeline" | p. 25 |
| PAM3 | "3 levels delivering 1.5 bits per cycle" | p. 12 |

### Coluna da RTX 6000 Ada na Tab. 4 (p. 46 a 48), transcrita inteira
GPU AD102; arquitetura Ada Lovelace; GPCs 12; TPCs 71; SMs 142; CUDA Cores/SM 128; CUDA Cores/GPU 18.176; Tensor Cores/SM 4 (4ª geração); Tensor Cores/GPU 568 (4ª); RT Cores 142 (3ª); GPU Boost Clock 2505 MHz; FP32 91,1 TFLOPS; FP16 91,1; BF16 91,1; INT32 44,5 TOPS; RT TFLOPS 210,6; FP4 N/A; FP8 com acumulação FP16 728,5/1457 (com esparsidade); FP8 com FP32 728,5/1457; FP16 com FP16 364/728; FP16 com FP32 364/728; BF16 com FP32 364/728; TF32 182,1/364,2; INT8 Tensor 728,5/1457,0; memória 48 GB GDDR6; interface 384 bits; taxa 20 Gbps; largura de banda **960 GB/s**; ROPs 192; preenchimento de pixels 481,0 Gpixels/s; unidades de textura 568; texels 1422,8 Gtexels/s; L1/compartilhada 18.176 KB; **L2 98.304 KB**; arquivo de registradores 36.352 KB; vídeo 3 NVENC (8ª ger.) e 3 NVDEC (5ª ger.); **TGP 300 W**; transistores 76,3 bilhões; die 608,5 mm2; processo TSMC 4nm 4N custom; PCIe Gen 4.

Para comparar, a coluna da Workstation Edition: 188 SMs; L2 131.072 KB; 96 GB GDDR7; 28 Gbps; 1792 GB/s; TGP 600 W; 92,2 bilhões de transistores; 750 mm2; PCIe Gen 5.

### Contas entre as tabelas do whitepaper (conferidas por nós)
- 94 TPCs x 2 = 188 SMs; 188 x 128 = 24.064; 188 x 4 = 752 Tensor Cores. OK.
- 188 x 256 KB = 48.128 KB (registradores); 188 x 128 KB = 24.064 KB (L1). OK. Fig. 6: 16.384 x 32 bits por partição x 4 partições = 65.536 registradores (assume 4 partições, que a figura mostra como um bloco só; `derived`).
- 24.064 x 2 x 2,617 GHz = 125,95 TFLOPS, e a tabela dá 126,0. OK. Max-Q: 24.064 x 2 x 2,28 = 109,7. OK.
- 512 bits x 28 Gbps / 8 = 1.792 GB/s. OK. Ada: 384 x 20 / 8 = 960. OK.
- Ada: 71 x 2 = 142 SMs; 142 x 128 = 18.176; 142 x 4 = 568; 142 x 128 KB = 18.176 KB; 142 x 256 KB = 36.352 KB. OK.
- 192 ROPs x 2,617 = 502,5 Gpixels/s e 752 x 2,617 = 1.968,0 Gtexels/s. OK.
- **Inconsistência na coluna da RTX A6000:** 384 bits x 19,5 Gbps / 8 = 936 GB/s, mas a tabela diz 768 GB/s. Não afeta a placa do grupo.
- **Inconsistência já registrada:** texto da p. 8 diz 192 SMs na RTX PRO 6000; tabelas dizem 188.
- Divergência do whitepaper: p. 11 (nota v1.1) repete duas vezes a ressalva de INT32, com redação ligeiramente diferente.

## Conferência das afirmações do artigo (A1 a A10)

| # | Afirmação do artigo | Veredito | Evidência e onde |
|---|---|---|---|
| A1a | 65.536 registradores de 32 bits por SM | **confere** | Tuning Guide 1.4.1.1: "64K 32-bit registers per SM"; Guia CUDA Tab. 34 "64 K"; whitepaper Tab. 4: 48.128 KB / 188 = 256 KB |
| A1b | no máximo 255 registradores por thread | **confere** | Tuning Guide 1.4.1.1: "The maximum number of registers per thread is 255." Guia CUDA Tab. 34: 255. Huerta diz "from 1 to 256" por warp (divergência, ver Conflitos) |
| A1c | no máximo 48 warps por SM na CC 12.0 | **confere** | Tuning Guide 1.4.1.1: "64 for compute capability 10.0 and 48 for compute capability 12.0" |
| A1d | divisão L1/compartilhada configurável | **confere em parte** | Tuning Guide 1.4.2.3: carveout "can be selected at runtime"; a lista de tamanhos do guia é do B200. Para 12.x o Guia CUDA Tab. 35 dá cache unificado de 128 KB e compartilhada "0, 8, 16, 32, 64, 100" KB |
| A1e | extras | registrado | threads por SM: não declarado (48 x 32 = 1.536, derivado); blocos por SM: 32 (CC 10.0 e 12.0); compartilhada por bloco: 99 KB (CC 12.0); por SM "128KB" no Tuning Guide contra máximo de 100 KB na Tab. 35 (ver Conflitos) |
| A2a | frequência máxima 2.617 MHz | **confere em parte** | Tab. 4 p. 46 chama de "GPU Boost Clock (MHz)" 2617; não diz "máxima" |
| A2b | 126 TFLOPS em FP32 | **confere** | Tab. 4: 126,0, "Peak FP32 TFLOPS (non-Tensor)", baseado no boost clock. 24.064 x 2 x 2,617 = 125,95 |
| A2c | antes só metade dos núcleos fazia inteiro, agora os 128 fazem inteiro ou ponto flutuante | **confere em parte** | p. 11: unificados, mas "can only operate as either FP32 or INT32 cores in any given clock cycle" e "not all INT operations can attain 2x". Tab. 4: INT32 126,0 contra 44,5 na Ada (91,1 FP32) |
| A2d | MIG em até quatro partes de 24 GB | **confere** | p. 44 "as many as four separate instances"; Tab. 3 p. 45: 4x = 24GB |
| A2e | processo "4N" ou "4 nm" | **confere em parte** | p. 48: "TSMC 4nm 4N NVIDIA Custom Process". "4 nm" é o rótulo do processo, não a medida de nenhum elemento (o whitepaper não define) |
| A2f | 188 e não 192 SMs porque partes com defeito são desligadas | **não achado** | o whitepaper não dá motivo; p. 8 diz até que a RTX PRO 6000 usa o GB202 "completo". A explicação do artigo é do grupo (`inferred`) |
| A2g | coluna da RTX 6000 Ada | **transcrita acima** | 142 SMs, L2 98.304 KB, 48 GB GDDR6, TGP 300 W, 960 GB/s. Bate com a Tab. 1 do artigo (960 GB/s, 300 W, 48 GB) |
| A3a | endereços virtuais de 49 bits | **confere** (Pascal) | whitepaper P100 p. 27: "49-bit virtual addressing" |
| A3b | falhas de página | **confere** | p. 27 "Memory page faulting support in GP100" |
| A3c | memória unificada, cópia sob demanda | **confere em parte** | p. 27: migração "on-demand" **ou** mapeamento por PCIe/NVLink sem copiar |
| A3d | preempção no nível de instrução | **confere** | p. 30: "interrupted at instruction-level granularity, and their context swapped to GPU DRAM" |
| A4 | páginas de 4 KB, 64 KB e 2 MB | **confere** (Pascal) | Pascal MMU p. 2: só esses três tamanhos; 128KB foi removido. Níveis: PD3, PD2, PD1, PD0 e PT (5 níveis). Na geração atual há também 512 MB (ver A10) |
| A5a | Xid 31 | **confere** | "GPU memory page fault": "logged when a fault is reported by the MMU, such as when an illegal address access is made" |
| A5b | Xid 13 | **confere em parte** | "Graphics Engine Exception": "logged for general user application faults". O "acesso fora do vetor" vem do resumo da página, não do trecho citado |
| A6a | `trap` para a execução e gera interrupção para a CPU | **confere** (PTX 7.5) | "Abort execution and generate an interrupt to the host CPU." A seção da 9.5 não foi lida; o PTX 9.5 é a versão atual (título "Version 9.5") |
| A6b | driver compila o PTX "na hora" para GPU mais nova | **confere em parte** | PTX 9.5 1.1: "translated at install time to the target hardware instruction set". Guia CUDA 2.7.3.1: "PTX-only, GPU forward compatible". Nenhum dos dois, como lidos, diz "JIT pelo driver ao carregar" |
| A7 | GSP é RISC-V, cuida da inicialização e gestão | **confere em parte** | README: "offload GPU initialization and management tasks", por padrão "for all Turing and later GPUs". **RISC-V não é mencionado** nessa fonte |
| A8a | bits de controle gravados pelo compilador | **confere** (Ampere e Turing) | Huerta seção 4: stall counter, yield, seis contadores de dependência, bit de reúso |
| A8b | registradores `RZ`, `UR`, `SR`, `P` | **confere em parte** | UR ("64 private, 32-bit registers ... shared by all the threads of the warp"), predicados (8 por warp), especiais ("thread or block IDs") descritos em 5.3. `RZ` e `PT` não aparecem nas páginas lidas |
| A8c | número de escalonadores e estágios | **confere em parte** | 4 subnúcleos, cada um emite 1 instrução por ciclo; estágios Fetch, Decode, Issue, Control, Allocate e execução; **não dá a profundidade total** |
| A8d | GPUs medidas | registrado | RTX 3080, 3080 Ti, 3090 e A6000 (Ampere); RTX 2080 Ti (Turing); **nenhuma Blackwell** |
| A9a | quatro escalonadores por SM, um warp por ciclo | **confere em parte** | Huerta (Ampere, Turing); Jia (Volta; registrado em `isa-sources.md`); Jarmusch (GB203; registrado); whitepaper Fig. 6 mostra um escalonador de warp por partição ("32 thread/clk") sem escrever "quatro" |
| A9b | regra do escalonador não divulgada | **confere** | Huerta infere por teste, em Ampere, a política CGGTY e só dentro do mesmo CTA; nenhuma fonte NVIDIA a descreve |
| A9c | divergência: um caminho e depois o outro | **confere em parte** | Guia CUDA 1.2.2.2: "the threads which do not follow the branch will be masked off". "Executa um caminho e depois o outro" não aparece na página; execução independente de threads (CC 7.0+) não foi aberta (3.2.2.1.1) |
| A10a | a GPU "manda uma interrupção pelo barramento PCIe" | **confere em parte** | o driver registra um handler com `request_threaded_irq` e usa MSI/MSI-X (`nv_init_msix`, `nv_init_msi`); metade de cima `nvidia_isr` -> `rm_isr`, metade de baixo `nvidia_isr_kthread_bh` -> `rm_isr_bh`; a UVM atende falhas em `uvm_isr_top_half` e fila de kthread. O texto do código não diz "pelo PCIe" para a interrupção (só para a leitura do PUT por BAR0) |
| A10b | MMU da UVM na geração atual | **resposta** | GB20x usa a HAL da Hopper: 6 níveis (PDE4, PDE3, PDE2, PDE1, PDE0, PTE), **57 bits** de VA, tamanhos 4K, 64K, 2M e 512M (GB100 acrescenta 256G). Diferente do artigo ("49 bits desde a Pascal"): o 49 vale para a Pascal |

## Conflitos
1. **Bits de VA.** Pascal: 49 bits e 5 níveis (Pascal MMU, p. 1 e 2). Driver para Hopper e GB20x: 57 bits e 6 níveis (`num_va_bits_hopper` retorna 57). `conflict: true` para o texto "desde a Pascal, 49 bits" se for usado como valor atual. Não é erro das fontes: são gerações diferentes.
2. **Tamanhos de página.** Pascal: 4K, 64K, 2M. Driver Blackwell GB100: 256G, 512M, 2M, 64K, 4K. GB20x herda a Hopper: 512M aparece em `page_table_depth_hopper`; a lista exata não foi lida. `conflict: true` até a leitura de `page_sizes` do Hopper.
3. **Registradores por thread.** NVIDIA: máximo 255 (Tuning Guide, Guia CUDA Tab. 34). Huerta 5.3: o número usado por um warp "can vary from 1 to 256". Valor oficial vale; Huerta provavelmente conta `RZ`. `conflict: true`.
4. **Memória compartilhada por SM na CC 12.0.** Tuning Guide 1.4.1.1: "shared memory capacity per SM is 128KB". Guia CUDA Tab. 35: cache unificado de 128 KB e compartilhada selecionável até 100 KB; Tab. 34 lista 100 KB por SM para colunas que o resumo não identificou. `conflict: true` (128 KB é o total unificado com L1; 100 KB é o máximo de compartilhada).
5. **Versão do PTX.** Registrada 9.4 em 2026-10-19; a página aberta em 2026-11-09 traz 9.5. Não é conflito entre fontes, é atualização; `isa-sources.md` continua dizendo 9.4.
6. **Whitepaper:** 192 SMs (p. 8) contra 188 (tabelas) e 1.008 contra 960 GB/s da Ada (já em `nvidia-rtx-pro-blackwell-architecture-v1.1.md`). Nesta rodada a Tab. 4 dá 960 GB/s, coerente com 384 x 20 / 8.
7. **Tab. 4 do whitepaper, coluna RTX A6000:** 768 GB/s contra 936 GB/s pela conta (384 bits x 19,5 Gbps / 8).
8. **Limites por SM.** Tab. 33 do Guia CUDA (resumo automático) lista 16, 24 e 32 blocos por SM sem identificar a coluna; o Tuning Guide diz 32 para CC 10.0 e 12.0. Não resolvido.

## Lacunas
- **Documento de hardware de MMU para Blackwell:** `open-gpu-doc` mostrou as pastas `pascal`, `volta`, `turing`, `ampere` (esta com `host/` e `index.html`), `manuals` (`ampere`, `turing`, `volta`) e as de BIOS e de classes. Nada de Hopper ou Blackwell nas listagens abertas (as listagens vieram truncadas pelo site). Só o documento da Pascal foi lido.
- **`page_sizes` da HAL Hopper** e o conjunto exato de tamanhos para a GB20x.
- **Mapeamento do PCI ID do GB202 para a entrada GB20x** do `uvm_hal.c`.
- **Como a interrupção sai da GPU:** os literais `pci_enable_msix` e `pci_enable_msi` não foram vistos; `nv.c` foi lido só até o caractere 100.000 de 176.317. O texto "pelo barramento PCIe" não tem trecho literal.
- **Preempção na Blackwell:** só há fonte para a Pascal (whitepaper P100). Nada aberto sobre a granularidade atual.
- **49 bits no Guia CUDA:** não aparece nas páginas abertas.
- **Descrição do driver compilando o PTX ao carregar (JIT)** em documento oficial: não achada. A seção `trap` do PTX 9.5 não foi lida.
- **GSP como RISC-V:** nenhuma fonte aberta nesta rodada diz isso. Também não há fonte para "o código é fechado" além de o README citar os módulos de firmware como arquivos distribuídos.
- **Independent Thread Execution** (Guia CUDA, 3.2.2.1.1) e a coluna da CC 12.0 das Tab. 33 e 34, que o resumo automático não separou.
- **Tuning Guide em PDF 13.4.1** (versão citada no artigo): não aberto; usei o HTML 13.5.
- **Número de estágios do pipeline** e **instruções por ciclo na Blackwell:** sem fonte oficial.
- **`RZ` e `PT`** em fonte de leitura direta: nenhum achado.
- **Leitura direta ausente:** as seções 1, 4, 5, 6 (parcial), 8 e 9 foram lidas por resumo automático. A auditoria deve reabrir as páginas.

## Conferência direta (sessão principal, 2026-11-09)

Arquivos baixados com `curl` de `raw.githubusercontent.com/NVIDIA/open-gpu-kernel-modules/main` (o `version.mk` desse ramo diz `NVIDIA_VERSION = 620.70.06`) e páginas HTML baixadas de `docs.nvidia.com` e `download.nvidia.com`. Texto literal, buscado com `grep`.

### Driver aberto
| Dado | Trecho literal | Arquivo |
|---|---|---|
| Qual MMU a família GB20x usa | "Note that GB20x MMU behaves as Hopper MMU, so it inherits from Hopper's MMU, not from GB10x." com `.mmu_mode_hal = uvm_hal_mmu_mode_hopper` na entrada `NV2080_CTRL_MC_ARCH_INFO_ARCHITECTURE_GB200` | `kernel-open/nvidia-uvm/uvm_hal.c` |
| Níveis e bits (Hopper) | "UVM depth / HW level / VA bits: 0 PDE4 56:56; 1 PDE3 55:47; 2 PDE2 46:38; 3 PDE1 (or 512M PTE) 37:29; 4 PDE0 (dual 64k/4k PDE, or 2M PTE) 28:21; 5 PTE_64K / PTE_4K 20:16 / 20:12" | `uvm_hopper_mmu.c`, comentário do topo |
| Bits de endereço virtual | `static NvU32 num_va_bits_hopper(void) { return 57; }` | `uvm_hopper_mmu.c` |
| Tamanhos de página (Hopper) | `page_table_depth_hopper` trata 2M (profundidade 4), 512M (profundidade 3) e 4K ou 64K (profundidade 5) | `uvm_hopper_mmu.c` |
| GB10x (data center) | mesma árvore, com "PDE2 (or 256G PTE)"; `page_sizes_blackwell` devolve 256G, 512M, 2M, 64K e 4K | `uvm_blackwell_mmu.c` |
| Exceção dentro da GB20x | a implementação `GB20B` usa `uvm_hal_mmu_mode_blackwell_integrated` (2M, 64K, 4K) | `uvm_hal.c`, `chip_table` |
| Registro da interrupção | `request_threaded_irq(nv->interrupt_line, nvidia_isr, nvidia_isr_kthread_bh, ...)`; caminho alternativo `nv_request_msix_irq(nvl)`; antes, `nv_init_msix(nv)` ou `nv_init_msi(nv)` | `kernel-open/nvidia/nv.c` |
| MSI e MSI-X | `pci_enable_msi(nvl->pci_dev)`; `nv_pci_enable_msix(nvl, num_intr)` | `kernel-open/nvidia/nv-msi.c` |
| Metade de cima e de baixo | `nvidia_isr` chama `rm_isr`; `nvidia_isr_kthread_bh` chama `rm_isr_bh` | `nv.c` |
| UVM | `uvm_isr_top_half` agenda `schedule_replayable_faults_handler`, `uvm_parent_gpu_schedule_non_replayable_faults_handler` e os contadores de acesso em uma fila de thread do kernel chamada "UVM GPU%u BH" | `kernel-open/nvidia-uvm/uvm_gpu_isr.c` |

Ressalvas: (1) nenhuma linha lida cita o GB202 pelo nome; ele entra em "GB20x" pelo nome da família (`derived`). (2) A lista `page_sizes` da HAL Hopper não foi localizada; os tamanhos acima saem da função de profundidade. (3) Código de driver descreve o que o software programa, não o circuito: o número de entradas de TLB, por exemplo, não aparece.

### Documentos
| Dado | Trecho literal | Onde |
|---|---|---|
| Ocupação | "The maximum number of concurrent warps per SM is 64 for compute capability 10.0 and 48 for compute capability 12.0. ... The register file size is 64K 32-bit registers per SM. The maximum number of registers per thread is 255. The maximum number of thread blocks per SM is 32 for devices of compute capability 10.0 and 12.0. ... For devices of compute capability 12.0, shared memory capacity per SM is 128KB." | Blackwell Tuning Guide 13.5, 1.4.1.1 |
| `trap` | "Abort execution and generate an interrupt to the host CPU." "Supported on all target architectures." | PTX ISA 9.5, 9.7.21.4 |
| Tradução | "PTX programs are translated at install time to the target hardware instruction set." | PTX ISA 9.5, 1.1 |
| Xid 31 | "GPU memory page fault ... This event is logged when a fault is reported by the MMU, such as when an illegal address access is made by an applicable unit on the chip." | catálogo de Xid |
| Xid 13 | "Graphics Engine Exception ... This event is logged for general user application faults. Typically this is an out-of-bounds error where the user has walked past the end of an array" | catálogo de Xid |
| GSP | "Some GPUs include a GPU System Processor (GSP) which can be used to offload GPU initialization and management tasks." A página **não contém a palavra RISC** | README do GSP, driver 595.80 |

Conta nossa (`derived`): 48 warps × 32 threads = 1.536 threads por SM; × 188 SMs = 288.768 threads residentes na placa.

## Conferência direta, segunda rodada (sessão principal, 2026-11-09, depois da auditoria)

A auditoria (`harness/qa/fact-check-segunda-leva.md`) apontou trechos que precisavam de busca literal. Todos conferidos com `grep` nos arquivos baixados ou vendo a página. **Onde este bloco contradiz a tabela A1 a A10 acima, vale este bloco.**

| Dado | Trecho literal | Onde |
|---|---|---|
| O GB202 pertence à família GB20x | "/* valid ARCHITECTURE_GB20x implementation values */" seguido de `NV2080_CTRL_MC_ARCH_INFO_IMPLEMENTATION_GB202 (0x00000002)`, junto de GB200, GB203, GB205, GB206, GB207 e GB20B | `src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080mc.h` |
| Tamanhos de página (lacuna fechada) | `static NvU64 page_sizes_ampere(void) { return UVM_PAGE_SIZE_512M \| UVM_PAGE_SIZE_2M \| UVM_PAGE_SIZE_64K \| UVM_PAGE_SIZE_4K; }`; a HAL da Hopper começa copiando a da Ampere (`hopper_mmu_mode_hal = *ampere_mmu_mode_hal;`) e não troca `page_sizes` | `uvm_ampere_mmu.c`, `uvm_hopper_mmu.c` |
| Bits de índice por nível | `static const NvU32 bit_widths[] = {1, 9, 9, 9, 8};` | `uvm_hopper_mmu.c`, `index_bits_hopper` |
| GSP é RISC-V (corrige A7) | "prepares RISCV core to run GSP-RM"; `NV_PRINTF(LEVEL_ERROR, "RISC-V core is not enabled.\n");` | `src/nvidia/src/kernel/gpu/gsp/arch/turing/kernel_gsp_tu102.c` (família Turing; para o GB202 é `derived`) |
| Falhas não reproduzíveis | "Non-replayable faults originated in other engines are considered fatal, and"; "replayable faults block preemption of the channel until" | `uvm_gpu_non_replayable_faults.c`, comentário do topo |
| Recuo de MSI | "falling back to PCIe virtual-wire interrupts." | `nv-msi.c` |
| Quatro escalonadores por SM (corrige A9) | Fig. 5, p. 10: quatro blocos, cada um com "L0 i-Cache + Warp Scheduler + Dispatch (32 thread/clk)" e "Register File (16,384 x 32-bit)", núcleos "FP32 / INT32", "5TH GENERATION TENSOR CORE", quatro "LD/ST" e "SFU"; embaixo "128 KB L1 Data Cache / Shared Memory", quatro "Tex" e "4TH GENERATION RT CORE" | whitepaper RTX PRO Blackwell v1.1, página renderizada e vista |
| Divergência (corrige A9) | "If threads of a warp diverge via a data-dependent conditional branch, the warp executes each branch path taken, disabling threads that are not on that path." | guia CUDA 13.5, 3.2.2.1 |
| JIT pelo driver (corrige A6) | "Any PTX code loaded by an application at runtime is compiled further to binary code by the device driver. This is called just-in-time compilation." | guia CUDA C++ 12.9.1, 6.1.1.2 |

Contas (`derived`): 4 × 16.384 = 65.536 registradores por SM; índices de 1 + 9 + 9 + 9 + 8 bits, mais 9 (4 KB) ou 5 (64 KB) no último nível; 4 KB: 45 + 12; 64 KB: 41 + 16; 2 MB: 36 + 21; 512 MB: 28 + 29; sempre 57.

## Conferência direta, terceira rodada (sessão principal, 2026-11-10, depois da auditoria da F6)

Trechos pedidos pela auditoria `harness/qa/fact-check-f6.md`, conferidos com busca literal nos arquivos baixados (`uvm_gpu_non_replayable_faults.c`, `uvm_gpu_replayable_faults.c`, a página do guia CUDA 13.5 "Advanced Kernel Programming" e o texto do whitepaper).

| Dado | Trecho literal | Onde |
|---|---|---|
| Falha reproduzível segura o canal | "replayable faults block preemption of the channel until software (UVM) services the fault. This is sometimes known as \"fault and stall\". Note that replayable faults prevent the execution of other channels, which are stalled until the fault is serviced." | `uvm_gpu_non_replayable_faults.c`, linhas 75 a 78 |
| Lote de falhas | "Fetch a batch of faults from the buffer. Stop at the first entry that is"; "When possible, we coalesce duplicate entries to minimize the fault handling" | `uvm_gpu_replayable_faults.c`, linhas 728 e 809 |
| Repetição | função `push_replay_on_gpu` | `uvm_gpu_replayable_faults.c`, linha 490 |
| Estado por thread | "Individual threads composing a warp start together at the same program address, but they have their own instruction address counter and register state and are therefore free to branch and execute independently." | guia CUDA 13.5, 3.2.2.1 |
| Divergência | "A warp executes one common instruction at a time ... If threads of a warp diverge via a data-dependent conditional branch, the warp executes each branch path taken, disabling threads that are not on that path." | guia CUDA 13.5, 3.2.2.1 |
| Antes e depois da compute capability 7.0 | "On GPUs with compute capability lower than 7.0, warps used a single program counter shared amongst all 32 threads in the warp together with an active mask specifying the active threads of the warp." | guia CUDA 13.5, 3.2.2.1.1 |
| Escalonamento independente de threads | "In GPUs of compute capability 7.0 and later, independent thread scheduling allows full concurrency between threads, regardless of warp. With independent thread scheduling, the GPU maintains execution state per thread, including a program counter and call stack ... A schedule optimizer determines how to group active threads from the same warp together into SIMT units. ... threads can now diverge and reconverge at sub-warp granularity." | guia CUDA 13.5, 3.2.2.1.1 |
| Troca de warp sem custo | "The execution context (program counters, registers, etc.) for each warp processed by an SM is maintained on-chip throughout the warp's lifetime. Therefore, switching between warps incurs no cost." | guia CUDA 13.5, 3.2.2.2 |
| Escalonador de warp | "At each instruction issue cycle, a warp scheduler selects a warp with threads ready to execute its next instruction (the active threads of the warp) and issues the instruction to those threads." | guia CUDA 13.5, 3.2.2.2 |
| Registradores e memória partilhados | "Each SM has a set of 32-bit registers that are partitioned among the warps, and a shared memory that is partitioned among the thread blocks." | guia CUDA 13.5, 3.2.2.2 |
| Diagrama de blocos oficial | "Figure 3. GB202 GPU block diagram (full chip)." O auditor viu a figura (p. 8): duas fileiras de 6 GPCs, L2 no centro, controladores de memória nas laterais | whitepaper RTX PRO Blackwell v1.1, p. 8 |
| FP64 | "The FP64 TFLOP rate is 1/64th the TFLOP rate of FP32 operations." | whitepaper, nota da Fig. 3 |
| PAM3 | "uses PAM3 (Pulse Amplitude Modulation: 3 levels) signaling technology" | whitepaper, p. 12 |

## Conferência direta, quarta rodada (sessão principal, 2026-11-10): beats que estavam bloqueados

Busca literal nas cópias baixadas do guia CUDA 13.5, do Blackwell Tuning Guide 13.5 e do driver (`kernel-open/nvidia-uvm/uvm_channel.h`, `uvm_channel.c`, `uvm_pushbuffer.h`).

| Dado | Trecho literal | Onde |
|---|---|---|
| Do bloco ao warp | "When an SM is given one or more thread blocks to execute, it partitions them into warps and each warp gets scheduled for execution by a warp scheduler. The way a block is partitioned into warps is always the same; each warp contains threads of consecutive, increasing thread IDs with the first warp containing thread 0." | guia CUDA 13.5, 3.2.2.2 |
| Divisão do L1 | "the portion of the L1 cache dedicated to shared memory (known as the carveout) can be selected at runtime as in previous architectures ... using cudaFuncSetAttribute() with the attribute cudaFuncAttributePreferredSharedMemoryCarveout." A lista de tamanhos que vem em seguida é do H100 e do B200, não da compute capability 12.0 | Blackwell Tuning Guide 13.5, 1.4.2.3 |
| Canais | "the GPU has multiple independent queues of execution (UVM channels)"; "Each channel has a uvm_gpu_tracking_semaphore_t and a set of uvm_gpfifo_entry_t (one per each HW GPFIFO entry) allowing to track completion of pushes on the channel." | `uvm_pushbuffer.h`; `uvm_channel.h` |
| GPFIFO | "The beginning of the first pending push is called the GPU get and the end of the last push is called the CPU put. This follows the HW GPFIFO naming that's a true ringbuffer (always completing in order and supporting transparent wrap-around)."; "a HW channel has a fixed limit of GPFIFO entries it supports that's chosen at channel creation" | `uvm_pushbuffer.h` |
| Envio do trabalho | a função `internal_channel_submit_work(uvm_push_t *push, NvU32 push_size, NvU32 new_gpu_put)` termina em `gpu->parent->host_hal->write_gpu_put(channel, new_gpu_put);` | `uvm_channel.c`, linhas 984 a 1014 |
| Reserva | "Beginning a push on a channel implies reserving a GPFIFO entry in that channel and hence there can only be as many on-going pushes per channel as there are free GPFIFO entries." | `uvm_channel.h` |

Ressalva: esses trechos descrevem os canais que o **próprio driver** usa (os canais da UVM). O caminho de um programa CUDA comum passa pela parte fechada do driver. Aplicar a ele o mesmo esquema é `derived`.

