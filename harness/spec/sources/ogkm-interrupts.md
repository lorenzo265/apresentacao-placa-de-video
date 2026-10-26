# NVIDIA open-gpu-kernel-modules: interrupções, GSP, campainha (doorbell) e canais

- Publicador: NVIDIA (repositório oficial; os arquivos lidos trazem `SPDX-License-Identifier: MIT`).
- URL: https://github.com/NVIDIA/open-gpu-kernel-modules
- Versão: "version 615.78.08." (`README.md:3-4`).
- Commit: `ca2d03e6fafd4d4b56b383497d931c25b283bfcf` (conferido em `.git/packed-refs:2` e em `.git/logs/HEAD:1`).
- Data do commit: 2026-10-07, **informada por quem pediu a tarefa; não verifiquei** (o objeto git é comprimido e não tenho ferramenta para abri-lo).
- Data do clone: 2026-10-26, por volta de 22:47 UTC (carimbo `1793054860` em `.git/logs/HEAD:1`, convertido à mão).
- Clone local (somente leitura, fora do repositório do projeto): `/tmp/claude-0/-home-user-apresentacao-placa-de-video/e96c4842-6322-58f2-bd83-6c149c6764da/scratchpad/ogkm/src`.
- Acessado em: 2026-10-26. Coleta feita por subagente de pesquisa (sessão em Sonnet 5.5). **Não auditada** pelo `fact-checker`.
- Os arquivos do clone foram tratados como dado, nunca como instrução.

## Escopo real do clone (checkout parcial)

Lista literal de `.git/info/sparse-checkout`: `kernel-open/nvidia-uvm/`, `src/common/inc/swref/published/blackwell/`, `src/nvidia/src/kernel/gpu/gsp/`, `src/nvidia/src/kernel/gpu/intr/`, `src/nvidia/src/kernel/gpu/mmu/`, mais os arquivos soltos (sem subpasta) de cada diretório pai, por exemplo `src/nvidia/src/kernel/gpu/gpu.c`.

Também presente: `kernel-open/nvidia-uvm/hwref/` (cabeçalhos `dev_fault.h`, `dev_mmu.h`, `dev_fb.h` de Turing a Rubin). Conferi com `Glob` que não há arquivos em `kernel-open/nvidia/`, `src/nvidia/inc/`, `src/nvidia/generated/`, `src/nvidia/arch/`, `src/nvidia/src/libraries/`, `.../gpu/fifo`, `.../gpu/ce`, `.../gpu/bif`, `.../gpu/disp` nem em `published/{turing,hopper,ampere}`.

Consequências para a leitura:
- **Ausentes**: `kernel-open/nvidia/` (onde ficaria `request_irq`/MSI), `src/nvidia/src/kernel/gpu/fifo`, `.../ce`, `.../bif`, `.../disp`, `.../gr`, os cabeçalhos `published/turing`, `published/hopper`, `published/ampere` de registradores, a biblioteca `msgq`, os arquivos gerados (`g_*`) da tabela HAL e os cabeçalhos `.h` de `src/nvidia/inc`. Portanto macros como `NV_CTRL_INTR_GPU_VECTOR_TO_LEAF_REG` e `NV_DOORBELL_NOTIFY_*` aparecem **usadas, mas não definidas**.
- **Específicos do GB202**: só `GPU/intr/arch/blackwell/intr_gb202.c`, `GPU/gsp/arch/blackwell/kernel_gsp_gb202.c` e a pasta `SWREF/gb202/`. Essa pasta traz só "deltas" (por exemplo, o `dev_vm.h` do GB202 define apenas o registrador `DOORBELL`). Quase todos os registradores de interrupção estão em `SWREF/gb100/` (chip de data center da mesma geração).
- A tabela HAL, que diz qual função `_TU102`, `_GH100` ou `_GB202` o GB202 realmente chama, é gerada e **não está no clone**. Por isso muitas linhas abaixo valem para o arquivo citado e só chegam ao GB202 por extrapolação (marcada em "Procedência").

## Legenda

Abreviações de caminho (expansão literal):
- `GPU/` = `src/nvidia/src/kernel/gpu/`
- `SWREF/` = `src/common/inc/swref/published/blackwell/`
- `UVM/` = `kernel-open/nvidia-uvm/`

Procedência (coluna da direita):
- `confirmed`: o texto, o comentário ou o cabeçalho citado afirma isso, em arquivo do GB202 ou em código comum a várias gerações (não específico de chip). Aplicabilidade ao GB202 depende da HAL, que não está no clone.
- `derived (XXX)`: extrapolado de outra geração ou de outro chip da mesma geração; `XXX` diz qual (`GB100` = Blackwell de data center; `GH100` = Hopper; `GA100`/`GA102` = Ampere; `TU102` = Turing). Também uso `derived` para contas minhas, dizendo a conta.
- `lacuna`: o clone não cobre; está em "Lacunas" no fim.
- `conflict: true`: duas partes do clone divergem; as duas estão registradas.

"…" dentro de um trecho marca espaços ou comentário de coluna omitidos, sem alterar o texto. Um trecho que cruza duas linhas de comentário é unido em uma só linha (as linhas vão no "Arquivo:linha").

---

## 1. Como a GPU interrompe a CPU

### 1A. Caminho até a CPU (MSI, MSI-X, INTx, tratador)

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 1.1 O tratador de interrupção do Linux é o "top half" do RM (função `nvidia_isr`), que chama o UVM antes do resto | "This is called from RM's top-half ISR (see: the nvidia_isr() function)" | `UVM/uvm_gpu_isr.c:194` | confirmed |
| 1.2 O UVM entrega ao RM o ponteiro do seu top half | ".isrTopHalf = uvm_isr_top_half_entry," | `UVM/uvm_global.c:49` | confirmed |
| 1.3 Código que registra o IRQ no kernel (`request_irq`, MSI, MSI-X, INTx) | **não encontrado.** Busca por `request_irq`, `pci_alloc_irq`, `MSI`, `INTx` não acha código; só o comentário de 1.1 cita `nvidia_isr` | n/a | lacuna |
| 1.4 Tabela MSI-X no mapa de registradores: 12 entradas, 16 bytes cada, a partir de 0x10000 | "NV_VIRTUAL_FUNCTION_PRIV_MSIX_TABLE_ADDR_LO(i) … (0x00010000+(i)*16)" e "…ADDR_LO__SIZE_1 … 12" | `SWREF/gb100/dev_vm.h:569-570` | derived (GB100) |
| 1.5 Campos de cada entrada: ADDR_LO, ADDR_HI, DATA, VECTOR_CONTROL (bit 0 = máscara). Vetor "pendente" (PBA) em 0x20000, 32 bits | "NV_VIRTUAL_FUNCTION_PRIV_MSIX_PBA … 0x00020000" | `SWREF/gb100/dev_vm.h:569-585` e `:605` | derived (GB100) |
| 1.6 Há uma segunda tabela MSI-X "JUMBO", também de 12 entradas | "NV_VIRTUAL_FUNCTION_PRIV_JUMBO_MSIX_TABLE_ADDR_LO__SIZE_1 … 12" | `SWREF/gb100/dev_vm.h:587-588` | derived (GB100) |
| 1.7 Capability MSI-X no espaço de configuração PCI da PF0, com bit de habilitação | "NV_PF0_MSIX_CAPABILITY_HEADR_AND_CONTROL … 0x0000007c" e "…_MSIX_ENABLE … 31:31" | `SWREF/gb100/dev_pcfg_pf0.h:129` e `:160` | derived (GB100) |
| 1.8 O registrador padrão de "linha/pino de interrupção" do PCI está listado. Isso só mostra que consta no mapa, não que o INTx seja usado. O cabeçalho é parcial e não define capability MSI (sem X) | "NV_PF0_INTERRUPT_AND_LATENCY … 0x0000003c" | `SWREF/gb100/dev_pcfg_pf0.h:27` | derived (GB100) |
| 1.9 No GB20x o display de baixa latência ganha bit próprio na árvore | "GB20X+, we we report a separate low latency DISP bit that is only pending if the" | `GPU/intr/arch/blackwell/intr_gb202.c:87` | confirmed |
| 1.10 Existe a noção de "linha de interrupção separada" para display de baixa latência; nesse caso essas interrupções são atendidas no top half | "If we have a separate interrupt line, the low latency interrupts will" | `GPU/gsp/kernel_gsp.c:3447` | confirmed |
| 1.11 Quantos vetores MSI-X o driver habilita, afinidade de CPU | **não encontrado** | n/a | lacuna |

### 1B. Árvore de interrupções (registradores leaf e top)

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 1.12 LEAF = status por vetor: 16 registradores de 32 bits em 0x1000 | "NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_LEAF(i) … (0x1000+(i)*4)" e "…LEAF__SIZE_1 … 16" | `SWREF/gb100/dev_vm.h:102-103` | derived (GB100) |
| 1.13 LEAF_EN_SET (habilita) em 0x1200 e LEAF_EN_CLEAR (desabilita) em 0x1400, 16 registradores cada | "…LEAF_EN_SET(i) … (0x1200+(i)*4)" e "…LEAF_EN_CLEAR(i) … (0x1400+(i)*4)" | `SWREF/gb100/dev_vm.h:106-111` | derived (GB100) |
| 1.14 TOP = status por subárvore; TOP_EN_SET e TOP_EN_CLEAR em 0x1608 e 0x1610. Cada um tem **1** registrador de 32 bits | "…TOP(i) … (0x1600+(i)*4)", "…TOP_EN_SET(i) … (0x1608+(i)*4)", "…TOP_EN_CLEAR(i) … (0x1610+(i)*4)", "__SIZE_1 … 1" | `SWREF/gb100/dev_vm.h:77-78`, `:84-85`, `:93-94` | derived (GB100) |
| 1.15 Disparo por software de um vetor | "NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_LEAF_TRIGGER … 0x00001640" e "…_VECTOR … 11:0" | `SWREF/gb100/dev_vm.h:129-130` | derived (GB100) |
| 1.16 Valor do bit: 1 = pendente (TOP), 1 = habilitar (EN_SET), 1 = desabilitar (EN_CLEAR) | "…TOP_SUBTREE_INTR_PENDING … 1", "…EN_SET_SUBTREE_ENABLE … 1", "…EN_CLEAR_SUBTREE_DISABLE … 1" | `SWREF/gb100/dev_vm.h:82`, `:90`, `:99` | derived (GB100) |
| 1.17 O número do vetor tem 12 bits | "NV_CTRL_INTR_CTRL_ACCESS_DEFINES_VECTOR_WIDTH … 0x0000000c" | `SWREF/gb100/dev_ctrl.h:27` | derived (GB100) |
| 1.18 Cada subárvore (subtree) usa dois registradores leaf | "Each complete subtree maps to two leaf registers." | `GPU/intr/intr.c:1052` | confirmed |
| 1.19 Vetor vira (registrador leaf, bit) por duas macros; as definições das macros **não estão no clone** | "NvU32 reg = NV_CTRL_INTR_GPU_VECTOR_TO_LEAF_REG(intrVector);" e "NvU32 leafBit = NV_CTRL_INTR_GPU_VECTOR_TO_LEAF_BIT(intrVector);" | `GPU/intr/arch/turing/intr_tu102.c:329-330` | derived (TU102) |
| 1.20 O "registrador estático" principal é o leaf 4 | "For Turing+, it's leaf 4" | `GPU/intr/arch/blackwell/intr_gb202.c:35` (igual em `intr_tu102.c:1234`) | confirmed |
| 1.21 Vetores com número fixo no cabeçalho: PFB 141, THERMAL 146, HDACODEC 147, PTIMER 148, PMGR 149, PMU 152, LTC_ALL 153, PDISP 154, GSP_INTR_0 155, PBUS 156, XVE 157, PRIV_RING 158, PTIMER_ALARM 159. Para NVLink aparece só o nome simbólico (`NV_INTERRUPT_NVLW_INTR_0_VECTOR` e `_1_`), sem valor | "NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_GSP_INTR_0_VECTOR … 155" | `SWREF/gb100/dev_vm.h:114-128` | derived (GB100) |
| 1.22 Árvore de motores "stall" (Hopper): leaves 6 e 7; notificações (non-stall): leaves 0 e 1 | "engine stall tree: leaf 6 and 7 on Hopper." e "engine notification tree: leaf 0 and 1 on Hopper." | `GPU/intr/arch/hopper/intr_gh100.c:159` e `:188` | derived (GH100) |
| 1.23 Árvore de motores (Ampere): stall no leaf 6; notificação no leaf 0 | "engine stall tree: leaf 6 on Ampere." e "engine notification tree: leaf 0 on Ampere." | `GPU/intr/arch/ampere/intr_ga100.c:92` e `:120` | derived (GA100) |
| 1.24 Categorias de subárvore: ESCHED_DRIVEN_ENGINE, ESCHED_DRIVEN_ENGINE_NOTIFICATION, RUNLIST, RUNLIST_NOTIFICATION, UVM_OWNED, UVM_SHARED | "&pIntr->subtreeMap[NV2080_INTR_CATEGORY_RUNLIST_NOTIFICATION];" | `GPU/intr/arch/hopper/intr_gh100.c:47`, `:51`, `:55`, `:67`, `:71`, `:78` | derived (GH100) |
| 1.25 "Árvore alternativa" = a árvore **non-stall**, tratada sem o lock do RM | "The alternate tree is an aberration of nature meant to service **non stall interrupts**" e "without using locking." | `GPU/intr/arch/turing/intr_tu102.c:68-69` | derived (TU102) |
| 1.26 No non-stall só o registrador TOP 0 é lido | "Only INTR_TOP_0 is ever read" | `GPU/intr/arch/turing/intr_nonstall_tu102.c:232` | derived (TU102) |
| 1.27 Para saber o que está pendente, o código lê os leaves e **não** confere se o bit está habilitado | "Check if interrupt is pending. We skip checking if it is enabled in" | `GPU/intr/arch/turing/intr_tu102.c:978` | derived (TU102) |
| 1.28 Limpar uma interrupção = escrever o bit no próprio registrador leaf | "intrWriteRegLeaf_HAL(pGpu, pIntr, reg, NVBIT(bit), pThreadState);" | `GPU/intr/arch/turing/intr_tu102.c:660` | derived (TU102) |
| 1.29 Habilitar e desabilitar um vetor = escrever o bit em LEAF_EN_SET / LEAF_EN_CLEAR | "intrWriteRegLeafEnSet_HAL(pGpu, pIntr, reg, NVBIT(leafBit), NULL);" | `GPU/intr/arch/turing/intr_tu102.c:341` (e `…EnClear…` em `:371`) | derived (TU102) |
| 1.30 No descarregamento, todos os enables do topo são limpos | "Disable all interrupts since we're unloading" | `GPU/intr/arch/turing/intr_tu102.c:158` | derived (TU102) |
| 1.31 O código supõe até dois registradores TOP e ignora índices acima do `SIZE_1` (no cabeçalho GB100 `SIZE_1` = 1) | "SW assumptions that there are two top-levels." e "if (regIndex >= NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_TOP_EN_SET__SIZE_1)" | `GPU/intr/arch/turing/intr_cpu_tu102.c:162` e `:164` | derived (TU102) |
| 1.32 Cada função de acesso a esses registradores tem equivalente na GSP, com registradores `NV_GSP_INTR_*` | "Every function in this file needs to have a GSP equivalent" e "accessing NV_GSP_INTR_* registers." | `GPU/intr/arch/turing/intr_cpu_tu102.c:32-33` (igual em `intr_cpu_ga102.c:32-33`) | derived (TU102, GA102) |
| 1.33 A tabela "vetor ↔ motor" do kernel RM é pedida ao RM físico (que roda na GSP) por um controle interno | "NV2080_CTRL_CMD_INTERNAL_INTR_GET_KERNEL_TABLE," | `GPU/intr/intr.c:1104` | confirmed |
| 1.34 O kernel RM valida o mapa de subárvores recebido da GSP | "Validate a GSP-provided interrupt category-to-subtree mapping." | `GPU/intr/intr.c:1019` | confirmed |
| 1.35 A tabela vetor↔motor para o GB202 (valores) | **não encontrado.** A tabela é montada em tempo de execução (item 1.33) e a versão estática está em arquivo gerado fora do clone | n/a | lacuna |
| 1.36 Também existe o caminho antigo (Pascal), com registradores `NV_PMC_INTR_EN_SET/CLEAR`. O código Turing diz que o mascaramento antigo é emulado em software | "The PMC_INTR_MASK HW registers were deprecated in Pascal, but the Pascal-Volta interrupt" | `GPU/intr/arch/turing/intr_tu102.c:1363` | derived (TU102) |

### 1C. Top half e bottom half

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 1.37 `intrServiceStall_IMPL` é o serviço das interrupções "stall"; enfileira o motor pendente em uma fila de DPC e a processa | "intrQueueInterruptBasedDpc(pGpu, pIntr, nextEngine);" | `GPU/intr/intr.c:171` (função em `:116`; fila em `:1374`) | confirmed |
| 1.38 Fora do Windows o RM desliga a fila de DPC por interrupção e atende em laço | "if (!RMCFG_FEATURE_PLATFORM_WINDOWS)" e "pIntr->setProperty(pIntr, PDB_PROP_INTR_DISABLE_PER_INTR_DPC_QUEUEING, NV_TRUE);" | `GPU/intr/intr.c:771` e `:773` | confirmed |
| 1.39 Para cada motor pendente: primeiro limpa a interrupção, depois chama o serviço do motor | "bShouldService = intrservClearInterrupt(pGpu, pIntrService, &clearParams);" e "ret = intrservServiceInterrupt(pGpu, pIntrService, &serviceParams);" | `GPU/intr/intr.c:1186` e `:1199` | confirmed |
| 1.40 O padrão de limpeza é o do 1.28 (`intrClearLeafVector`) | "intrClearLeafVector_HAL(pGpu, pIntr," | `GPU/intr/intr_service.c:59` | confirmed |
| 1.41 Detecção de interrupção "presa" (mesmo valor repetido além do limite) | "Stuck interrupt detected for mcEngine %u" | `GPU/intr/intr.c:1563` | confirmed |
| 1.42 O bottom half non-stall atende a falha não-replayable e o buffer de eventos FECS que ficaram sem DPC | "intrServiceNonStallBottomHalf_IMPL" | `GPU/intr/intr.c:917` (corpo `:928-932`) | confirmed |
| 1.43 Falha não-replayable: o top half copia os pacotes do buffer de hardware para o de software; o DPC só lê do buffer de software | "top half of the interrupt handler, as such, we only copy fault packets" | `GPU/intr/arch/turing/intr_tu102.c:799` | derived (TU102) |
| 1.44 Interrupções do tipo "pulso" (Turing em diante) para falhas e contadores de acesso; as anteriores eram por nível | "Turing switches to pulse-based interrupts for replayable/non-replayable" | `UVM/uvm_gpu_isr.c:35` | confirmed |
| 1.45 O RM re-arma todas as interrupções de topo ao sair do top half, por isso o UVM as desabilita nas bordas do tratamento | "RM re-triggers all top-level interrupts when exiting its top half" | `UVM/uvm_gpu_isr.c:42-43` | confirmed |
| 1.46 O top half do UVM agenda o bottom half em uma fila de kthread própria | "nv_kthread_q_schedule_q_item(&parent_gpu->isr.bottom_half_q," | `UVM/uvm_gpu_isr.c:115` (também `:145` e `:188`) | confirmed |
| 1.47 Para evitar tempestade, o top half do UVM desabilita a interrupção antes de agendar o bottom half | "Interrupts need to be disabled here to avoid an interrupt storm" | `UVM/uvm_gpu_isr.c:110` | confirmed |
| 1.48 Retornos possíveis do top half do UVM ao RM: `NV_OK`, `NV_WARN_MORE_PROCESSING_REQUIRED`, `NV_ERR_NO_INTR_PENDING` | "NV_WARN_MORE_PROCESSING_REQUIRED:" | `UVM/uvm_gpu_isr.c:201` | confirmed |
| 1.49 Se o UVM não consegue pegar o lock, a GPU gera nova interrupção enquanto houver falha pendente | "(GET != PUT in the fault buffer)." | `UVM/uvm_gpu_isr.c:209` | confirmed |
| 1.50 Ao final do bottom half: reabilita, limpa o bit e reescreve GET para reavaliar a condição | "Rearm pulse interrupts. This guarantees that the state of the pending" | `UVM/uvm_gpu_isr.c:792` | confirmed |

---

## 2. Eventos que geram interrupção

| Evento | Dado e trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 2.1 Fim de trabalho (notificação "non-stall" por runlist) | "On Turing onwards, all non-stall interrupts, including the ones from" (continua: "PBDMA, have moved to reporting on the runlist that is served by the PBDMA") | `GPU/intr/intr.c:1244` | confirmed |
| 2.2 Idem: o RM dispara a notificação do motor "host" | "engineNonStallIntrNotify(pGpu, RM_ENGINE_TYPE_HOST);" | `GPU/intr/intr.c:1255` | confirmed |
| 2.3 A interrupção non-stall do FIFO serve a eventos de runlist | "The fifo non-stall interrupt is used for runlist events, which also" | `GPU/intr/arch/turing/intr_tu102.c:811` | derived (TU102) |
| 2.4 O UVM acompanha a conclusão de cada push por **semáforo de rastreio por canal** (o comentário não cita interrupção para isso) | "channel has a uvm_gpu_tracking_semaphore_t and a set of uvm_gpfifo_entry_t" | `UVM/uvm_channel.h:38-39` | confirmed |
| 2.5 Falha de página replayable (motor `REPLAYABLE_FAULT`). Com o UVM dono dela, uma chegada ao RM é erro | "Unexpected replayable interrupt routed to RM. Verify UVM took ownership." | `GPU/mmu/kern_gmmu.c:2453` | confirmed |
| 2.6 Falha não-replayable (motor `NON_REPLAYABLE_FAULT`) é atendida por `kgmmuServiceNonReplayableFault_HAL` | "status = kgmmuServiceNonReplayableFault_HAL(pGpu, pKernelGmmu);" | `GPU/mmu/kern_gmmu.c:2397` | confirmed |
| 2.7 Estouro do buffer de falhas tem interrupção de erro própria (replayable e non-replayable) | "status = kgmmuReportFaultBufferOverflow_HAL(pGpu, pKernelGmmu);" | `GPU/mmu/kern_gmmu.c:2410` e `:2431` | confirmed |
| 2.8 Falha de PRI (acesso a registrador): motor `INFO_FAULT`; com GSP, o kernel RM "repassa" a interrupção à GSP por campainha | "In case of PF Kernel RM, bounce the interrupt to GSP for handling." | `GPU/mmu/kern_gmmu.c:2461` | confirmed |
| 2.9 Há **dois** buffers de falha em hardware: índice 0 = não-replayable, índice 1 = replayable | "NV_VIRTUAL_FUNCTION_PRIV_MMU_NON_REPLAY_FAULT_BUFFER … 0" e "…MMU_REPLAY_FAULT_BUFFER … 1" | `SWREF/gb100/dev_vm.h:146-147` | derived (GB100) |
| 2.10 Cada buffer é um anel com GET e PUT de 20 bits, e há bit para habilitar interrupção de estouro | "…FAULT_BUFFER_GET_PTR … 19:0" e "…FAULT_BUFFER_SIZE_OVERFLOW_INTR … 29:29" | `SWREF/gb100/dev_vm.h:164`, `:176`, `:188` | derived (GB100) |
| 2.11 Tipos de falha de MMU no GB202 (16 códigos, 0x0 a 0xf): PDE, PDE_SIZE, PTE, VA_LIMIT_VIOLATION, UNBOUND_INST_BLOCK, PRIV_VIOLATION, RO_VIOLATION, WO_VIOLATION, PITCH_MASK_VIOLATION, WORK_CREATION, UNSUPPORTED_APERTURE, CC_VIOLATION, UNSUPPORTED_KIND, REGION_VIOLATION, POISONED, ATOMIC_VIOLATION | "NV_PFAULT_FAULT_TYPE_ATOMIC_VIOLATION … 0x0000000f" | `SWREF/gb202/dev_fault.h:275-290` | confirmed |
| 2.12 Falha de MMU em um canal leva a reset do canal, notificador de erro e escopo de TSG | "ROBUST_CHANNEL_FIFO_ERROR_MMU_ERR_FLT," e "RC_NOTIFIER_SCOPE_TSG);" | `GPU/mmu/kern_gmmu.c:3100` e `:3102` | confirmed |
| 2.13 Contadores de acesso (notificações de acesso à memória) | "pIntr->accessCntrIntrVector      = intrGetVectorFromEngineId(pGpu, pIntr, MC_ENGINE_IDX_ACCESS_CNTR, NV_FALSE);" | `GPU/intr/arch/turing/intr_tu102.c:191` | derived (TU102) |
| 2.14 Display: vetor PDISP 154; no GB20x existe também `DISP_LOW` | "NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_PDISP_VECTOR … 154" | `SWREF/gb100/dev_vm.h:123` | derived (GB100) |
| 2.15 Display: o vblank adiado também vira bit pendente (`DISP` ou `DISP_LOW`) | "Deferred vblank is pending which we need to handle" | `GPU/intr/arch/turing/intr_tu102.c:1025` | derived (TU102) |
| 2.16 Temporizador: vetores PTIMER 148 e PTIMER_ALARM 159; o `TMR` reporta nas duas árvores (PMC e dev_ctrl) | "it reports into both PMC and dev_ctrl. We need the PTIMER alarm in" | `GPU/intr/arch/turing/intr_tu102.c:105-106` | derived (TU102) |
| 2.17 Erros de barramento e anel de registradores: PRIV_RING 158, PBUS 156, XVE 157 | "NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_PRIV_RING_VECTOR … 158" | `SWREF/gb100/dev_vm.h:127` | derived (GB100) |
| 2.18 Interrupção do endpoint PCIe (XAL): erros de PRI, timeout de requisição e resposta, timeout de ACK da memória (FB), timeout TRS | "NV_XAL_EP_INTR_0_FB_ACK_TIMEOUT … 5:5" | `SWREF/gb100/dev_nv_xal_ep_zb.h:27-37` | derived (GB100) |
| 2.19 Térmico 146, PMU 152, cache L2 (LTC_ALL) 153, controlador de memória (PFB) 141 | "NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_THERMAL_VECTOR … 146" | `SWREF/gb100/dev_vm.h:116`, `:121`, `:122`, `:114` | derived (GB100) |
| 2.20 Firmware: a GSP tem vetor próprio (155) e motor `MC_ENGINE_IDX_GSP` | "NvU32 engineIdx = MC_ENGINE_IDX_GSP;" | `GPU/gsp/kernel_gsp.c:7236` | confirmed |
| 2.21 Log de troca de contexto do GR (FECS) pode gerar interrupção | "bitVectorSet(pEngines, MC_ENGINE_IDX_GRn_FECS_LOG(i));" | `GPU/intr/arch/turing/intr_tu102.c:1046` | derived (TU102) |
| 2.22 Copy engine: **sem interrupção própria no clone** (não há `MC_ENGINE_IDX_CE` nos diretórios lidos). O CE aparece como origem de **falha de MMU**: IDs de motor CE0 a CE19 = 65 a 84 | "NV_PFAULT_MMU_ENG_ID_CE19 … 84" | `SWREF/gb202/dev_fault.h:74-93` | confirmed (IDs); interrupção de CE = lacuna |
| 2.23 Ao limpar o estado do canal depois de uma falha, o UVM distingue falha vinda do host (PBDMA) e do CE | "else if (fault->fault_source.mmu_engine_type == UVM_MMU_ENGINE_TYPE_CE) {" | `UVM/uvm_ampere_host.c:117-122` | derived (GA100) |
| 2.24 Mailbox de mensagens (MNOC): 4 caixas de envio e 4 de recebimento, cada uma com bits `INTR_ENABLE` e `INTR_STATUS` (escreve 1 para limpar). O arquivo não diz para que lado serve | "NV_MNOC_ZB_PRI_MESSAGE_INFO_0_SENDMBOX_INTR_STATUS … 31:31" | `SWREF/gb100/dev_mnoc_pri_zb.h:27-45`, `:51-74` | derived (GB100) |
| 2.25 Erro ECC na própria GSP tem registrador de interrupção (corrigido e não corrigido) | "NV_PGSP_ECC_INTR_STATUS … 0x00110888" | `SWREF/gb100/dev_gsp.h:114` | derived (GB100) |
| 2.26 Interrupção "doorbell de CPU" por software, usada para avisar um convidado de vGPU de que há evento | "CPU_DOORBELL interrupt is used to notify a vGPU guest that there is an event pending." | `GPU/intr/swintr.c:70` | confirmed |
| 2.27 Essa interrupção por software é disparada escrevendo o vetor em `LEAF_TRIGGER` | "GPU_VREG_WR32(pGpu, NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_LEAF_TRIGGER," | `GPU/intr/arch/turing/intr_swintr_tu102.c:47` | derived (TU102) |
| 2.28 Tipos de interrupção visíveis a uma função virtual (VF): falhas (replayable, non-replayable, erro, info), contador de acesso, TMR, CPU_DOORBELL, GR0 a GR7 FECS_LOG | "case NV2080_INTR_TYPE_CPU_DOORBELL:" | `GPU/intr/intr_vgpu.c:82` | confirmed |

---

## 3. Firmware GSP (GPU System Processor)

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 3.1 Nome oficial no código | "reporting timeout events detected on the GSP (GPU System Processor)." | `GPU/gsp/kernel_gsp.c:2780` | confirmed |
| 3.2 O firmware da GSP é entregue à parte; os módulos abertos precisam do firmware da mesma versão | "must be used with GSP" (continua: "firmware and user-space NVIDIA GPU driver components") | `README.md:18-19` | confirmed |
| 3.3 O código-fonte do firmware que roda na GSP **não** está no clone; só o lado da CPU (e referências a imagens, como `BINDATA_LABEL_UCODE_IMAGE_PROD`) | "BINDATA_LABEL_UCODE_IMAGE_PROD" | `GPU/gsp/arch/blackwell/kernel_gsp_gb100.c:153` | confirmed |
| 3.4 Processador: RISC-V. Mensagem de erro quando o núcleo não está ligado | "RISC-V core is not enabled." | `GPU/gsp/arch/turing/kernel_gsp_tu102.c:313` | derived (TU102) |
| 3.5 Hopper em diante, a GSP sempre inicia em modo RISC-V | "Hopper+ GSP always boots in RISC-V mode." | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:951` | derived (GH100) |
| 3.6 Para Blackwell, os erros fatais se identificam como "GSP-RISCV instance 0" | "GSP-RISCV instance 0 unknown fatal error" | `GPU/gsp/arch/blackwell/kernel_gsp_gb100.c:260` | derived (GB100) |
| 3.7 Registrador de falha do núcleo: bits para GLOBAL_MEM, ROM, ITCM, DTCM, ICACHE, DCACHE, RVCORE (núcleo), REG, SE_LOGIC, SE_KSLT, TKE, FBIF, MPURAM | "NV_PGSP_RISCV_FAULT_CONTAINMENT_SRCSTAT_RVCORE … 6:6" | `SWREF/gb100/dev_gsp.h:73-112` | derived (GB100) |
| 3.8 Registradores do núcleo RISC-V no GB202: CPUCTL 0x388, RPC 0x3ec, IRQDELEG 0x534, IRQDEST 0x52c, IRQMASK 0x528, PRIV_ERR_STAT/INFO/ADDR/ADDR_HI, HUB_ERR_STAT | "NV_PRISCV_RISCV_IRQDEST … 0x0000052c" | `SWREF/gb202/dev_riscv_pri.h:27-36` | confirmed |
| 3.9 Ordem de bits, versão do conjunto RISC-V (RV32 ou RV64, extensões), tamanho de memória da GSP | **não encontrado** | n/a | lacuna |
| 3.10 Boot: o RM zera a GSP, escreve o endereço dos argumentos do GSP-FMC nos mailboxes e aponta o BootROM da GSP para o FMC | "Bootstrap the GSP-FMC by pointing the GSP's BootROM at it" | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:820` | derived (GH100) |
| 3.11 Boot: o núcleo é liberado escrevendo `STARTCPU` | "DRF_DEF(_PRISCV_RISCV, _CPUCTL, _STARTCPU, _TRUE));" | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:855` | derived (GH100) |
| 3.12 Boot: em geral via FSP ou SEC2 ("Starting to boot GSP via FSP/SEC2"); espera a liberação da máscara de alvo e do "lockdown" | "Starting to boot GSP via FSP." | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:969` | derived (GH100) |
| 3.13 Boot: antes de carregar o GSP-RM é preciso rodar o FWSEC (ucode do VBIOS) para montar o FRTS dentro da WPR2 | "FRTS is triggered by running a VBIOS-provided ucode called FWSEC." | `GPU/gsp/kernel_gsp.c:5553` | confirmed |
| 3.14 Depois do boot, liga a fila de status e envia o RPC `GSP_INIT` (informações do sistema entram, informações estáticas saem) | "Send GSP_INIT: system info in, static info out." | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:1088` | derived (GH100) |
| 3.15 O que a GSP faz: "RM offload" (o RM roda na GSP) | "NV_OK if GSP fw RM offload successfully initialized." | `GPU/gsp/kernel_gsp.c:5517` | confirmed |
| 3.16 Parte do tratamento de erro de canal (derrubada de canal, "RC") roda na GSP; notificações ao cliente e interação com o SO ficam na CPU | "RC error handling ("Channel Teardown sequence") is executed in GSP-RM." e "Client notifications, OS interaction etc happen in CPU-RM (Kernel RM)." | `GPU/gsp/kernel_gsp.c:713-714` | confirmed |
| 3.17 A GSP atende falhas não-replayable de MMU e interrupções de FIFO | "GSP RM services both MMU non-replayable fault and FIFO interrupts" | `GPU/intr/intr.c:1813` | confirmed |
| 3.18 Com GSP, a falha não-replayable é atendida no bottom half | "On GSP we service non replayable faults in the bottom half, so we" | `GPU/intr/arch/ampere/intr_ga100.c:59` | derived (GA100) |
| 3.19 O mesmo código do RM (Intr) é compilado também para a plataforma GSP | "if (pKernelDisplay != NULL && !RMCFG_FEATURE_PLATFORM_GSP)" | `GPU/intr/arch/blackwell/intr_gb202.c:159` | confirmed |
| 3.20 A GSP executa o LibOS: cada "tarefa" LibOS tem região de memória de log, e o GSP-RM recebe os argumentos dele como mais uma região | "// Add memory areas for logging each LIBOS task." e "// insert GSP-RM ELF args address; id must match libos-config.py entry" | `GPU/gsp/kernel_gsp.c:7051` e `:7064` | confirmed |
| 3.21 **Fila de comandos CPU → GSP**: memória de **sistema** compartilhada, 256 KB de comando e 256 KB de status | "const NvLength defaultCommandQueueSize = 0x40000; // 256 KB" e "const NvLength defaultStatusQueueSize  = 0x40000; // 256 KB" | `GPU/gsp/message_queue_cpu.c:71-72` | confirmed |
| 3.22 Os blocos da fila vivem em `ADDR_SYSMEM` (memória do sistema, com cache) | "RM_PAGE_SIZE, NV_MEMORY_NONCONTIGUOUS, ADDR_SYSMEM, NV_MEMORY_CACHED," | `GPU/gsp/message_queue_cpu.c:258` | confirmed |
| 3.23 Elemento de fila: mínimo de 1 página, máximo de 16 páginas (valor de `RM_PAGE_SIZE` **não está no clone**) | "queueElementSizeMin = RM_PAGE_SIZE;" e "queueElementSizeMax = RM_PAGE_SIZE * 16;" | `GPU/gsp/message_queue_cpu.c:85-86` | confirmed |
| 3.24 Layout: cabeçalho com tabela de páginas, fila de comando (cabeçalho e entradas), fila de status (cabeçalho e entradas) | "Shared memory layout." | `GPU/gsp/message_queue_cpu.c:300-307` | confirmed |
| 3.25 Ponteiros de cabeça e cauda das filas vêm de registradores (função `gpuGetGspMsgQueueRegisters`, que **não está no clone**) | "gpuGetGspMsgQueueRegisters(pGpu, RPC_TASK_RM_QUEUE_IDX, &cmdHead, &cmdTail, NULL, NULL)" | `GPU/gsp/message_queue_cpu.c:173` (status em `:372`) | confirmed |
| 3.26 Mensagens usam cabeçalhos MCTP e NVDM (tipo de mensagem, "start/end of message") | "SOM = 1 (start of message)" | `GPU/gsp/message_queue_cpu.c:504` | confirmed |
| 3.27 Modo de computação confidencial: elementos criptografados | "pRmQueueInfo->bEncryptionEnabled = gpuIsCCFeatureEnabled(pGpu);" | `GPU/gsp/message_queue_cpu.c:80` | confirmed |
| 3.28 A CPU escreve os elementos, faz um "store fence" e só depois publica a cauda | "a store fence is needed here." e "nRet = msgqTxSubmitBuffers(pMQI->hQueue, nElements);" | `GPU/gsp/message_queue_cpu.c:603` e `:607` | confirmed |
| 3.29 RPC síncrono = a CPU **faz polling** (laço com `osSpinLoop`) até a resposta chegar; não é por interrupção | "osSpinLoop();" | `GPU/gsp/kernel_gsp.c:3459` (laço em `:3366-3461`) | confirmed |
| 3.30 Eventos assíncronos GSP → CPU são tratados no bottom half (DPC) | "This function is called from interrupt bottom-half handler (DPC) and" | `GPU/gsp/kernel_gsp.c:7078` | confirmed |
| 3.31 **Interrupção GSP → CPU**: no serviço da GSP, o bit SWGEN0 do IRQSTAT (gerado por software na GSP) dispara a leitura das mensagens; é "edge triggered" e é limpo ANTES do serviço | "Clear edge triggered interrupt BEFORE (and never after)" e "kgspRpcRecvEvents(pGpu, pKernelGsp);" | `GPU/gsp/arch/turing/kernel_gsp_tu102.c:1036` e `:1042` | derived (TU102) |
| 3.32 Outro bit do IRQSTAT, HALT, é usado pelo firmware no protocolo CrashCat para pedir atenção ao host | "signal the host that some handling is required. Clear the interrupt" | `GPU/gsp/arch/turing/kernel_gsp_tu102.c:1019` | derived (TU102) |
| 3.33 Quem chama esse serviço é o serviço de interrupção do motor `MC_ENGINE_IDX_GSP` | "return kgspService_HAL(pGpu, pKernelGsp);" | `GPU/gsp/kernel_gsp.c:7262` | confirmed |
| 3.34 Posição numérica dos bits HALT e SWGEN0 no IRQSTAT | **não encontrado** (só aparecem por nome; o cabeçalho GB100 de falcon define apenas `EXTIRQ7`) | `SWREF/gb100/dev_falcon_v4.h:27` | lacuna |
| 3.35 **Interrupção CPU → GSP**: "notify op". A CPU grava opcode e argumentos em superfície compartilhada, faz store fence e escreve no registrador PRIV_DOORBELL | "5. Trigger notification interrupt to GSP." e "GPU_VREG_WR32(pGpu, NV_VIRTUAL_FUNCTION_PRIV_DOORBELL, NV_DOORBELL_NOTIFY_LEAF_SERVICE_LOCKLESS_OP_HANDLE);" | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:1222` e `:1224` | derived (GH100) |
| 3.36 Depois a CPU espera a GSP incrementar o número de sequência | "6. Poll on the sequence number to ensure the op completed." | `GPU/gsp/arch/hopper/kernel_gsp_gh100.c:1226` | derived (GH100) |
| 3.37 O mesmo registrador serve para a CPU "empurrar" uma interrupção à GSP com um `handle` (exige SR-IOV) | "@brief Trigger the PRIV doorbell" e "GPU_VREG_WR32(pGpu, NV_VIRTUAL_FUNCTION_PRIV_DOORBELL, handle);" | `GPU/intr/arch/turing/intr_sriov_tu102.c:36` e `:53` | derived (TU102) |
| 3.38 Layout do registrador PRIV_DOORBELL (0x2200): HANDLE 31:0 (inteiro), VECTOR 11:0, CPU_NOTIFICATION 31:31 | "NV_VIRTUAL_FUNCTION_PRIV_DOORBELL … 0x2200" | `SWREF/gb100/dev_vm.h:134-140` | derived (GB100) |
| 3.39 Há uma região de registradores reservada à GSP dentro da função virtual | "NV_VIRTUAL_FUNCTION_REGION5_GSP … 0x0004FFFF:0x00040000" | `SWREF/gb100/dev_vm.h:32` | derived (GB100) |
| 3.40 Como a GSP percebe um **novo comando** na fila (polling dela ou interrupção) | **não encontrado** (a biblioteca `msgq` e o lado do firmware não estão no clone) | n/a | lacuna |
| 3.41 Tipos de evento que a GSP envia à CPU (amostra): POST_EVENT, RC_TRIGGERED, OS_ERROR_LOG, SEMAPHORE_SCHEDULE_CALLBACK, TIMED_SEMAPHORE_RELEASE, UCODE_LIBOS_PRINT, GSP_LOCKDOWN_NOTICE, FECS_ERROR, PMU_HALTED, RECOVERY_ACTION, FORCED_DRIVER_SHUTDOWN, EXTDEV_INTR_SERVICE, NVLINK_* | "case NV_VGPU_MSG_EVENT_RC_TRIGGERED:" | `GPU/gsp/kernel_gsp.c:1597-1737` (RC em `:1601`) | confirmed |
| 3.42 Quando a GSP entra em "lockdown", a CPU não pode ler registradores dela, incluindo status e controle de interrupção | "including interrupt status and control. We shouldn't receive any more" | `GPU/gsp/kernel_gsp.c:1514` | confirmed |
| 3.43 Saúde: a GSP escreve "heartbeat" em registradores de mailbox; a CPU confere a cada 1 s | "osSchedule1HzCallback(pGpu, _kgspHealthPeriodicHealthCheck, pKernelGsp, NV_OS_1HZ_REPEAT);" | `GPU/gsp/kernel_gsp.c:2520` | confirmed |
| 3.44 Prazos do heartbeat: GSP-RM = 2× o timeout padrão; LibOS = timeout padrão + 30% (o comentário vizinho diz 1,25×; ver 7.11) | "pKernelGsp->gspRmHeartbeatTimeoutMs = defaultTimeoutMs * 2;" e "defaultTimeoutMs + ((defaultTimeoutMs / 10) * 3);" | `GPU/gsp/kernel_gsp.c:2451` e `:2457` | confirmed |
| 3.45 Mailboxes da GSP: MAILBOX0 em 0x110040, MAILBOX1 em 0x110044; quatro mailboxes de software em 0x110804 | "NV_PGSP_MAILBOX(i) … (0x110804+(i)*4)" e "…MAILBOX__SIZE_1 … 4" | `SWREF/gb100/dev_gsp.h:27-41` | derived (GB100) |
| 3.46 Reset da GSP: bit RESET do registrador `FALCON_ENGINE` (0x1103c0) | "GPU_FLD_WR_DRF_DEF(pGpu, _PGSP, _FALCON_ENGINE, _RESET, _TRUE);" | `GPU/gsp/arch/turing/kernel_gsp_tu102.c:830` (reg. em `SWREF/gb100/dev_gsp.h:33`) | derived (TU102, GB100) |
| 3.47 Erro fatal de hardware na GSP tem bit próprio no IRQSTAT (24) e é tratado pelo código de Blackwell | "NV_PGSP_FALCON_IRQSTAT_FATAL_ERROR … 24:24" | `SWREF/gb100/dev_gsp.h:69` | derived (GB100) |
| 3.48 O arquivo específico do GB202 cita o par PCI 2BB1/204B numa lista de placas que permitem 48 VMs de vGPU (função `_is48VmEnabled`). Nesse arquivo o comentário chama o par de "RTX Pro 6000 X"; o README chama 2BB1 com subsistema 204B de "RTX PRO 6000 Blackwell Workstation Edition" | "PCI_TABLE_ENTRY(0x2BB1, 0x204B)" e "// NVIDIA RTX Pro 6000 X" | `GPU/gsp/arch/blackwell/kernel_gsp_gb202.c:40` e `README.md:961-964` | confirmed; conflict: true (nome divergente, mesma ID) |

---

## 4. Como a CPU envia trabalho para a GPU

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 4.1 Canais, entradas de GPFIFO e pushbuffer: cada push reserva uma entrada de GPFIFO no canal | "Beginning a push on a channel implies reserving a GPFIFO entry in that" | `UVM/uvm_channel.h:43` | confirmed |
| 4.2 Entrada de GPFIFO no Blackwell (classes A e B): 8 bytes; campos GET, GET_HI, LEVEL, LENGTH, SYNC, OPCODE (campos listados em `clca6f.h:53-72`) | "#define NVCA6F_GP_ENTRY__SIZE" (valor 8) e "#define NVC96F_GP_ENTRY__SIZE" (valor 8) | `UVM/clca6f.h:52` e `UVM/clc96f.h:91` | confirmed |
| 4.3 Estrutura de controle do canal Blackwell: o único campo declarado é `GPPut`, no deslocamento 0x8c | "NvU32 GPPut;                   /* GP FIFO put offset               008c-008f*/" | `UVM/clc96f.h:31` (também `UVM/clca6f.h:29`) | confirmed |
| 4.4 No Turing (e também no Hopper, `clc86f.h:42`) o mesmo bloco declara ainda `GPGet` em 0x88 (somente leitura); nas duas classes Blackwell ele não é declarado | "NvU32 GPGet;                   /* GP FIFO get offset, read only    0088-008b*/" | `UVM/clc46f.h:61` | derived (TU102, GH100) |
| 4.5 A entrada de GPFIFO guarda o endereço virtual do pushbuffer (em palavras de 4 bytes) e o tamanho | "HWVALUE(C46F, GP_ENTRY0, GET, NvU64_LO32(pushbuffer_va) >> 2);" | `UVM/uvm_turing_host.c:201` | derived (TU102) |
| 4.6 Para avisar a GPU: grava `GPPut`, barreira de escrita e escreve o **token de submissão** no endereço da **campainha** do canal | "UVM_GPU_WRITE_ONCE(*channel->channel_info.workSubmissionOffset, channel->channel_info.workSubmissionToken);" | `UVM/uvm_turing_host.c:235` (grava `gpPut` em `:231`, `wmb()` em `:233`) | derived (TU102) |
| 4.7 Definição dos dois campos no canal de usuário | "Address of the channel's doorbell." e "The value that is used when ringing the channel's doorbell." | `UVM/uvm_user_channel.h:118` e `:121` | confirmed |
| 4.8 Em canais do UVM em modo confidencial, "tocar a campainha" é o último passo, depois de tornar os dados criptografados observáveis | "// Make sure all encrypted data is observable before ringing the doorbell." | `UVM/uvm_channel.c:1158` | confirmed |
| 4.9 Otimização do UVM (canais WLC): com PUT = GET + 2 em repouso, "basta tocar a campainha" para iniciar trabalho | "This is what enables the driver to submit work just by ringing a doorbell." | `UVM/uvm_channel.c:3933` | confirmed |
| 4.10 Registrador da campainha **de usuário** no GB202, em 0x30090: VECTOR 11:0, RUNLIST_ID 22:16, RUNLIST_DOORBELL 30:30 (1 = habilitado) | "NV_VIRTUAL_FUNCTION_DOORBELL … 0x30090" e "…DOORBELL_RUNLIST_DOORBELL … 30:30" | `SWREF/gb202/dev_vm.h:27-32` | confirmed |
| 4.11 Mesmo registrador no GB100: campos e polaridade **diferentes** (ver 7.2) | "NV_VIRTUAL_FUNCTION_DOORBELL … 0x30090" | `SWREF/gb100/dev_vm.h:620-632` | derived (GB100); conflict: true |
| 4.12 A região "USER" da função virtual (0x30000 a 0x3FFFF) contém a campainha; também guarda o identificador da classe de modo usuário (valor 50785) | "NV_VIRTUAL_FUNCTION_USER … 0x0003FFFF:0x00030000" e "…USERMODE_CLASS_ID_VALUE 50785" | `SWREF/gb100/dev_vm.h:30` e `:613` | derived (GB100); 50785 = 0xC661 por conversão minha |
| 4.13 Contexto de canal em memória (RAMFC): GP_BASE, GP_BASE_HI, GP_GET, PB_HEADER, INTR_NOTIFY_CTRL e outros; o `GP_PUT` fica no bloco USERD | "NV_RAMUSERD_GP_PUT … (35*32+31):(35*32+0)" | `SWREF/gb100/dev_ram.h:26-46` | derived (GB100) |
| 4.14 Comentário do UVM cita o USERD e o GPPUT em conjunto | "cannot guarantee that USERD/GPPUT physical address is accessible by" | `UVM/uvm_channel.c:3382` | confirmed |
| 4.15 Estado de cada canal no hardware (CHRAM): 2048 entradas de 32 bits; bits ENABLE, NEXT, BUSY, PBDMA_FAULTED, ENG_FAULTED, ON_PBDMA, ON_ENG, PENDING, CTX_RELOAD, PBDMA_BUSY, ENG_BUSY, ACQUIRE_FAIL | "NV_CHRAM_CHANNEL__SIZE_1      2048" | `SWREF/gb202/dev_runlist.h:26-66` | confirmed |
| 4.16 Comandos escritos em CHRAM: habilitar (0x2), desabilitar (0x3), recarregar contexto (0x200), limpar falha de PBDMA (0x11) e de motor (0x21) | "NV_CHRAM_CHANNEL_UPDATE_RESET_PBDMA_FAULTED      0x00000011" | `SWREF/gb202/dev_runlist.h:67-73` | confirmed |
| 4.17 Após tratar falha, o UVM limpa o bit no CHRAM e toca a campainha de novo | "UVM_GPU_WRITE_ONCE(*user_channel->work_submission_offset, user_channel->work_submission_token);" | `UVM/uvm_ampere_host.c:138` (limpeza em `:134`) | derived (GA100) |
| 4.18 O hardware que consome as entradas de GPFIFO é chamado de ESCHED; entradas de controle são processadas depois que as anteriores foram **buscadas** (não necessariamente concluídas) | "Control GPFIFO entries are guaranteed to be processed by ESCHED after" | `UVM/uvm_channel.h:708` | confirmed |
| 4.19 Como o token é montado (quais bits identificam canal e runlist) | **não encontrado**: o código só repassa `workSubmissionToken` recebido do RM | n/a | lacuna |

---

## 5. Escalonamento de canais e contextos (runlists, TSG) e relação com o AMP

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 5.1 **O código não menciona AMP** (nem "AI Management Processor"). A busca por `AI Management`, `AMP`, `Management Processor` acha só um nome de fornecedor sem relação ("Amptron") | `{ "AMP",    _VENDOR_NAME_ENTRY("Amptron")` | `src/common/inc/nvPNPVendorIds.h:90` | confirmed (ausência); não relacionado |
| 5.2 O comentário "scheduler" que existe em `kernel_gsp.c` é só sobre bandeiras de recurso, não descreve escalonador | "// Display, mem policy, TDR, FSP, scheduler: corresponds to KERNEL_DISPLAY" | `GPU/gsp/kernel_gsp.c:5167` | confirmed |
| 5.3 Preempção por hardware: `NV_RUNLIST_PREEMPT` com tipo RUNLIST ou TSG e bits de pendência | "NV_RUNLIST_PREEMPT_TYPE_TSG                        0x00000001" | `SWREF/gb202/dev_runlist.h:74-86` | confirmed |
| 5.4 A campainha do GB202 carrega o ID do runlist (7 bits) | "NV_VIRTUAL_FUNCTION_DOORBELL_RUNLIST_ID … 22:16" | `SWREF/gb202/dev_vm.h:29` | confirmed |
| 5.5 Entrada de runlist: seletor de fila `RUNQUEUE1` e deslocamento de base 8 | "NV_RAMRL_ENTRY_CHAN_RUNQUEUE_SELECTOR_RUNQUEUE1" (valor 0x1) e "NV_RAMRL_ENTRY_BASE_SHIFT                8" | `SWREF/gb202/dev_ram.h:29` e `:31` | confirmed |
| 5.6 O "ESCHED" (escalonador de engine do host) também dá nome às categorias de interrupção | "NV2080_INTR_CATEGORY_ESCHED_DRIVEN_ENGINE" | `GPU/intr/arch/hopper/intr_gh100.c:47` | derived (GH100) |
| 5.7 Nome histórico: o UVM tem pendência para renomear "HOST" para "ESCHED" | "TODO: Bug 3210931: Rename HOST references and files to ESCHED." | `UVM/uvm_blackwell_host.c:29` | confirmed |
| 5.8 Quando um canal falha, a derrubada acontece com escopo de TSG (grupo de canais) | "RC_NOTIFIER_SCOPE_TSG);" | `GPU/mmu/kern_gmmu.c:3102` | confirmed |
| 5.9 A derrubada de canal ("Channel Teardown sequence") roda na GSP (ver 3.16) | ver 3.16 | `GPU/gsp/kernel_gsp.c:713` | confirmed |
| 5.10 Conforme a origem da falha (host ou CE), o UVM escolhe limpar o bit PBDMA_FAULTED ou ENG_FAULTED do CHRAM | "clear_type_value = NV_CHRAM_CHANNEL_UPDATE_RESET_PBDMA_FAULTED;" | `UVM/uvm_ampere_host.c:118` (e `:122` para `ENG_FAULTED`) | derived (GA100) |
| 5.11 Algoritmo de escalonamento (fatia de tempo, prioridade), quem monta o runlist, relação entre AMP, GSP e ESCHED | **não encontrado** | n/a | lacuna |

---

## 6. Reset e falha da GPU (Xid), resumo curto

| Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|
| 6.1 Placa que sumiu do barramento: leitura volta com todos os bits em 1; o RM lê `PMC_BOOT_0` e prepara um "Secondary Bus reset" | "reading PMC_BOOT_0 register to check if the GPU was surprise removed/ off the bus" | `GPU/intr/intr.c:130` (também `:131`) | confirmed |
| 6.2 Falha fatal da GSP (CrashCat): marca saúde ruim, registra "xid 120", derruba canais e marca o dispositivo para reset | "Technically both event are associated with the xid 120 report" e "gpuMarkDeviceForReset(pGpu);" | `GPU/gsp/arch/turing/kernel_gsp_tu102.c:945` e `:963` | derived (TU102) |
| 6.3 Erro fatal de hardware na GSP (Blackwell): registra o erro, derruba todos os canais e marca para reset | "NV_ASSERT_OK(gpuMarkDeviceForReset(pGpu));" | `GPU/gsp/arch/blackwell/kernel_gsp_gb100.c:306` | derived (GB100) |
| 6.4 Xid 175: timeout da GSP por erro no subsistema de memória | "Log Xid 175 - GSP timeout due to memory subsystem error" | `GPU/gsp/kernel_gsp.c:2997` | confirmed |
| 6.5 Xid 154: mudança na ação de recuperação da GPU | "Log XID 154 to indicate new recovery action." | `GPU/gpu.c:7383` | confirmed |
| 6.6 Xid 140: erro de ECC não recuperável que escapou | "gpuCheckEccCounts_HAL should be able to detect and log Xid 140 (UNRECOVERABLE_ECC_ERROR_ESCAPE)" | `GPU/gsp/kernel_gsp.c:3107` | confirmed |
| 6.7 Reset por função (FLR) no config PCI: bit de capacidade e bit de iniciar | "NV_PF0_DEVICE_CAPABILITIES_FUNCTION_LEVEL_RESET_CAPABILITY … 28:28" | `SWREF/gb100/dev_pcfg_pf0.h:171` (iniciar em `:156`) | derived (GB100) |
| 6.8 Registrador de falhas de segurança do GB202 com bits para GSP (DCLS, watchdog L5), FSP, SEC2, PMU, clocks | "NV_SYSCTRL_SEC_FAULT_BIT_POSITION_GSP_L5_WDT … 19:19" | `SWREF/gb202/dev_pmc_zb.h:27-53` | confirmed |
| 6.9 Tabela completa de números Xid | **não encontrado** (as constantes `ROBUST_CHANNEL_*` e `GSP_ERROR` não são definidas no clone) | n/a | lacuna |

---

## 7. Contas conferidas e inconsistências

7.1 **Subárvores x registradores TOP (internamente inconsistente).** `SWREF/gb100/dev_vm.h:81` define `TOP_SUBTREE__SIZE_1 = 64`, mas `:78`, `:85` e `:94` dão `SIZE_1 = 1` para TOP, TOP_EN_SET e TOP_EN_CLEAR, e `:79` fixa o campo em `31:0`. Um registrador de 32 bits não cobre 64 subárvores. Outras contas: 16 leaves (`:103`) ÷ 2 leaves por subárvore (`intr.c:1052`) = **8 subárvores**; o código Hopper afirma por `ct_assert` que a maior subárvore non-stall é menor que 32 (`intr_gh100.c:124`). A leitura coerente é "8 subárvores caben em 1 registrador TOP", mas o `64` do cabeçalho segue sem explicação. Também o espaçamento de 8 bytes entre TOP (0x1600), TOP_EN_SET (0x1608) e TOP_EN_CLEAR (0x1610) caberia 2 registradores de cada, e o código tolera até 2 (`intr_cpu_tu102.c:162`). conflict: true (dentro do mesmo arquivo).

7.2 **Campainha de usuário: GB100 contra GB202.** GB202 (`SWREF/gb202/dev_vm.h:29-32`): RUNLIST_ID `22:16`; RUNLIST_DOORBELL `30:30` com ENABLE = `0x1`. GB100 (`SWREF/gb100/dev_vm.h:624-632`): RUNLIST_ID `22:16`; RUNLIST_DOORBELL `22:22` (**sobrepõe** o bit 22 do RUNLIST_ID) com ENABLE = `0x0`; GSP_DOORBELL `31:31`. O GB202 não tem `GSP_DOORBELL`. Para a RTX PRO 6000 vale o arquivo do GB202. conflict: true.

7.3 **Vetores x leaf 4.** Os vetores numerados de 141 a 159 (`dev_vm.h:114-128`) ficam em 128 a 159. Com leaves de 32 bits, `vetor ÷ 32` dá 4 para todos. Isso bate com "leaf 4" (`intr_gb202.c:35`). Conta minha, porque a macro `..._VECTOR_TO_LEAF_REG` não está no clone. Procedência: derived.

7.4 **Tabela MSI-X.** 12 entradas × 16 bytes = 192 bytes (0x10000 a 0x100BF), dentro da região PRIV (0x00000 a 0x2FFFF, `dev_vm.h:27`); a PBA em 0x20000 é de 32 bits e comporta os 12 vetores. A tabela JUMBO (0x410000) e sua PBA (0x420000) ficam dentro da região JUMBO (0x400000 a 0x42FFFF, `:29`). Fecha.

7.5 **Regiões da função virtual.** REGION0 (0x0000 a 0x7FFF) + REGION1 (0x8000 a 0x9FFF) + REGION2 (0xA000 a 0x2FFFF) = 0x30000 = tamanho da região PRIV (`dev_vm.h:33-35` e `:27`). Fecha. A região RL (0x8000 a 0x9FFF = 8 KiB, `:28`) tem o mesmo tamanho de 2048 entradas CHRAM × 4 bytes (`SWREF/gb202/dev_runlist.h:27`); só observo a coincidência, o cabeçalho não relaciona as duas.

7.6 **Largura do vetor.** 12 bits (`dev_ctrl.h:27`) permitiriam 4096 vetores; os 16 leaves de 32 bits só cobrem 512. Não é contradição (largura do campo contra quantidade implementada), mas o clone não diz quantos vetores são usados.

7.7 **Offsets repetidos.** `NV_CHRAM_CHANNEL(5)` (0x014) e `NV_RUNLIST_PREEMPT` (0x014) caem no mesmo deslocamento em `SWREF/gb202/dev_runlist.h` (`:26` e `:74`); portanto são blocos com bases diferentes que o cabeçalho não declara.

7.8 **Registrador de falhas de segurança.** `NV_SYSCTRL_SEC_FAULT` é declarado com faixa `0x3:0x0` (4 bytes = 32 bits), mas o campo `INTERRUPT` está em `32:32` (`SWREF/gb202/dev_pmc_zb.h:27` e `:53`). Um bit 32 não cabe em 32 bits. O arquivo não explica.

7.9 **Faixa de IDs de CE.** `CE0 = 65` e `CE19 = 84` (`dev_fault.h:74` e `:93`): 84 − 65 + 1 = 20 IDs. Fecha. Isso conta IDs do espaço de falhas, não o número de CEs presentes na placa.

7.10 **IDs PCI.** Os pares do código (`kernel_gsp_gb202.c:39-41`) batem com o README (`README.md:961-964` e `:977-978`): 2BB1 com subsistema 204B, 2BB5 com 204E e 220B. Os **nomes** divergem: o comentário do código diz "RTX Pro 6000 X" (2BB1) e "RTX Pro 6000 Blackwell DC" (2BB5/204E); o README diz "Workstation Edition" e "Server Edition". conflict: true (só de nome).

7.11 **Prazo do heartbeat da LibOS.** O comentário diz "set libos heartbeat timeout to 1.25 times the default timeout." (`GPU/gsp/kernel_gsp.c:2456`), e a linha seguinte calcula `defaultTimeoutMs + ((defaultTimeoutMs / 10) * 3)` (`:2457`), que é cerca de 1,3× (30% a mais). Comentário e código divergem; o arquivo não diz qual é o valor pretendido. conflict: true (comentário contra código).

---

## 8. Leituras minhas (interpretação, não auditada)

Estas frases são minhas, não do código. Quem for usar no texto final deve passar pelo `fact-checker`.

- **I1.** Os registradores `NV_VIRTUAL_FUNCTION_PRIV_CPU_INTR_*` (offsets 0x1000 a 0x1640) parecem estar no BAR0 do dispositivo, pois ficam na região PRIV (0x00000 a 0x2FFFF). O cabeçalho não diz "BAR0".
- **I2.** O vetor 155 (`GSP_INTR_0`) provavelmente é o vetor do motor `MC_ENGINE_IDX_GSP`. O clone não mostra a tabela que liga os dois.
- **I3.** O `workSubmissionOffset` (item 4.6) provavelmente é um mapeamento do registrador `NV_VIRTUAL_FUNCTION_DOORBELL` (0x30090). O código só chama o ponteiro de "doorbell do canal".
- **I4.** O `workSubmissionToken` provavelmente codifica `VECTOR` (11:0) e `RUNLIST_ID` (22:16), por serem os campos do registrador. O clone não mostra a montagem.
- **I5.** O fluxo "CPU grava no buffer, a GPU sinaliza por pulso, o top half copia, o bottom half atende" das falhas não-replayable é a leitura conjunta de `intr_tu102.c:798-801`, `:1128-1137` e `kern_gmmu.c:2379-2406`.
- **I6.** A GSP parece fazer o papel de "firmware que executa o RM" (offload); não há texto que a chame de escalonador. O AMP do whitepaper (p. 25) pode ser outro processador ou o mesmo; **o código não decide**.
- **I7.** O GB202 reaproveita a maior parte do código de Hopper/Turing para interrupções e GSP. Os indícios são: o arquivo do GB202 só define a árvore de display (`intr_gb202.c`) e itens de vGPU/fuse (`kernel_gsp_gb202.c`); `kernel_gsp_gb100.c:98` chama `kgspResetHw_GH100`; o UVM faz o GB20x herdar do GB100 (`uvm_hal.c:284-285`) e o MMU do GB20x herdar do Hopper (`uvm_hal.c:287-289`: "Note that GB20x MMU behaves as Hopper MMU, so it inherits from"). Falta a tabela HAL para confirmar.

---

## O que a fonte NÃO cobre

Sim, o código cobre; não, o clone não traz ou o código não diz:

| Pedido | Cobertura |
|---|---|
| Como o Linux registra o IRQ (MSI, MSI-X ou INTx), quantos vetores | **Não cobre.** Só o comentário `UVM/uvm_gpu_isr.c:194` e o mapa de registradores MSI-X (12 entradas, GB100) |
| Registradores de status, habilitação e limpeza | **Cobre** (leaf e top, GB100/TU102), com extrapolação para o GB202 |
| Árvore leaf/top, stall e non-stall | **Cobre** (comentários de TU102, GH100, GA100; registradores do GB100) |
| Top half e bottom half | **Cobre** o lado do RM e do UVM; o registro do tratador no kernel não |
| Quais eventos interrompem | **Cobre** falhas de MMU, runlist/notificação, display, timer, erros, GSP; **não cobre** copy engine |
| O que é a GSP, processador, função | **Cobre** em termos gerais; **não cobre** o código do firmware, a ISA RISC-V exata nem o escalonamento interno |
| Filas de mensagens e RPC | **Cobre** (CPU lado) |
| Como a GSP percebe comando novo | **Não cobre** |
| Canais, GPFIFO, doorbell, USERD, token | **Cobre** a mecânica; **não cobre** a montagem do token |
| Runlist e TSG | **Cobre** só nomes de registradores e preempção; **não cobre** o algoritmo |
| AMP | **O código não menciona** |
| Xid e reset | **Cobre** de forma pontual (120, 140, 154, 175) |

## Lacunas (para o `architecture-inferencer` e para nova coleta)

Marcadas como lacuna; nada foi preenchido por suposição.

1. **Registro de IRQ e MSI/MSI-X/INTx.** Falta `kernel-open/nvidia/` (por exemplo, os arquivos que chamam `request_irq` e `nvidia_isr`). Nome literal citado no código: `nvidia_isr()`. Os caminhos exatos do repositório completo não foram verificados por mim.
2. **Número de vetores MSI-X alocados e afinidade.** Depende da lacuna 1. Dado parcial: tabela MSI-X de 12 entradas no mapa GB100 (itens 1.4 a 1.7).
3. **Valores da tabela vetor↔motor do GB202.** A tabela é montada pela GSP em tempo de execução (item 1.33) e a estática vem de arquivo gerado (`g_*`) fora do clone.
4. **Macros e constantes citadas e não definidas no clone:** `NV_CTRL_INTR_GPU_VECTOR_TO_LEAF_REG`, `..._LEAF_BIT`, `NV_CTRL_INTR_SUBTREE_TO_LEAF_IDX_*`, `NV_CPU_INTR_STALL_SUBTREE_*`, `NV_DOORBELL_NOTIFY_LEAF_SERVICE_*`, `RM_PAGE_SIZE`. Estariam em cabeçalhos de `published/turing`, `published/hopper` e `src/nvidia/inc` (nomes de `#include` vistos no código: `published/turing/tu102/dev_vm.h`, `published/turing/tu102/dev_vm_addendum.h`, `published/turing/tu102/dev_ctrl.h`, `kernel/gpu/intr/intr.h`, `kernel/gpu/intr/engine_idx.h`, `gpu/gsp/message_queue.h`; caminhos no repositório completo não verificados).
5. **Tabela HAL do GB202** (quais funções `_TU102`, `_GH100`, `_GB100`, `_GB202` o GB202 usa). Gerada em tempo de compilação; não está no clone.
6. **Lado do firmware da GSP:** como a GSP percebe um comando novo na fila, o código RISC-V, a ISA exata (RV32/RV64 e extensões), o tamanho de TCM/cache e como ela escalona internamente.
7. **Biblioteca `msgq`** (`msgq/msgq_priv.h` aparece no `#include` de `message_queue_cpu.c:53`) e função `gpuGetGspMsgQueueRegisters` (usada em `:173`): definem as posições dos ponteiros de cabeça e cauda.
8. **Posição dos bits `HALT` e `SWGEN0`** do `IRQSTAT` da GSP (cabeçalho de falcon de Turing/Hopper não está no clone).
9. **Copy engine:** interrupção de CE, contagem real de CEs do GB202. Falta `src/nvidia/src/kernel/gpu/ce`.
10. **FIFO e runlists:** montagem do token de submissão, formato do runlist, política de escalonamento e TSG. Falta `src/nvidia/src/kernel/gpu/fifo`.
11. **AMP:** o código lido não o menciona. Relação AMP, GSP e ESCHED fica **em aberto** (o whitepaper p. 25 é a única fonte do AMP).
12. **Classe de canal usada pelo GB202** (BLACKWELL_CHANNEL_GPFIFO_A `0xC96F` ou `_B` `0xCA6F`). O clone traz as duas (`UVM/clc96f.h:27`, `UVM/clca6f.h:33`) e a tabela do UVM lista ambas (`UVM/uvm_hal.c:215` e `:228`); não diz qual o GB202 usa.
13. **Tabela de Xid** e fluxo completo de reset (FLR e reset de barramento secundário): só pontos soltos (itens 6.1 a 6.8).
14. **Data do commit** (2026-10-07): informada pelo solicitante; não conferida.
15. **Auditoria:** nenhum item acima foi revisado pelo `fact-checker`. Os trechos foram conferidos contra o código duas vezes (leitura direta e busca por texto com número de linha) para os números que importam: tamanhos de fila (3.21), tamanhos de registradores (1.12 a 1.14), MSI-X (1.4) e layout da campainha (4.10, 4.11, 7.2).
