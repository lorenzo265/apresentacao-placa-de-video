# NVIDIA open-gpu-kernel-modules, MMU da GPU (GMMU), UVM e falhas de página

- Publicador: NVIDIA
- URL: https://github.com/NVIDIA/open-gpu-kernel-modules
- Versão: 615.78.08 (`README.md:4`: "version 615.78.08.")
- Commit lido: `ca2d03e6fafd4d4b56b383497d931c25b283bfcf` (conferido em `.git/refs/heads/main:1` e `.git/logs/HEAD:1`)
- Data do commit: 2026-10-07, **informada por quem pediu a coleta; não conferida** (clone raso, não li o objeto do commit)
- Data do clone: 2026-10-26 (carimbo 1793054860 no reflog, que dá 2026-10-26 22:47 UTC)
- Data da leitura: 2026-10-26
- Forma de leitura: Glob, Grep e Read direto nos arquivos do clone. Sem resumo automático.
- Clone: raso (`.git/shallow`) e parcial (`.git/info/sparse-checkout`). Só existem estes diretórios: `src/nvidia/src/kernel/gpu/{mmu,intr,gsp}`, `src/common/inc/swref/published/blackwell`, `kernel-open/nvidia-uvm`, mais os arquivos soltos de `src/nvidia/src/kernel/gpu/` e `src/common/inc/`.
- Procedência: `confirmed` quando o código ou o comentário afirma. `derived` quando é conta ou ligação minha entre duas passagens do código (a coluna diz quais). Leitura minha sem prova direta fica na seção "Interpretações (não auditadas)".
- Esta fonte é código de driver. Não é especificação de hardware, nem documento da NVIDIA sobre a GB202. O que vale para a GB202 é o que o código liga à família GB20x.

Abreviações de caminho (relativas à raiz do repositório; no clone a raiz é `<scratchpad>/ogkm/src/`):
- `RM/` = `src/nvidia/src/kernel/gpu/mmu/`
- `SW/` = `src/common/inc/swref/published/`
- `UVM/` = `kernel-open/nvidia-uvm/`

## Aviso de escopo (leia antes das tabelas)

O repositório mistura duas famílias Blackwell, e o código as separa:
- **GB10x** (`ARCHITECTURE_GB100`): tem a página de 256 GB e usa `uvm_hal_mmu_mode_blackwell`.
- **GB20x** (`ARCHITECTURE_GB200`, valor 0x1B0, a família da GB202): `UVM/uvm_hal.c:287-288` diz que a MMU "se comporta como a da Hopper". Nesse caso o conjunto de páginas é o da Hopper (4 KB, 64 KB, 2 MB, 512 MB), **sem** 256 GB.

Por isso as tabelas abaixo marcam o escopo (GB10x, GB20x ou Hopper) de cada dado.

## 1. A GPU tem MMU própria (GMMU)? Onde está definida?

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| G-01 | O driver modela uma MMU da GPU chamada GMMU, como objeto do RM que roda na CPU | `Kernel GMMU module header` / `Defines and structures used on CPU RM for the GMMU object.` | `RM/kern_gmmu.c:26-27` | confirmed |
| G-02 | Há código por geração de GPU, com formato (`fmt`) separado do restante | pastas `RM/arch/{maxwell,pascal,volta,turing,ampere,hopper,blackwell,rubin}/`; Blackwell: `kern_gmmu_gb100.c` e `kern_gmmu_fmt_gb10x.c` | listagem de diretório | confirmed |
| G-03 | O bloco de hardware aparece nos registradores como HUBMMU, e como MMU dentro da região `VIRTUAL_FUNCTION_PRIV` | `NV_HUBMMU_PRI_MMU_FAULT_STATUS  0x0000A560` ; `NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE  0x000030B0` | `SW/blackwell/gb100/dev_hubmmu_base.h:28`; `SW/blackwell/gb100/dev_vm.h:338` | confirmed |
| G-04 | As tabelas de página ficam, por padrão, na memória de vídeo (vidmem) | `// Default placement for PDEs is in vidmem.` ; `pKernelGmmu->PDEAperture = ADDR_FBMEM;` (PTE: linhas 136-137) | `RM/kern_gmmu.c:130-131` | confirmed |
| G-05 | O RM admite tabela de PTE em memória do sistema como alternativa | `constructFlags \|= VASPACE_FLAGS_RETRY_PTE_ALLOC_IN_SYS;` | `RM/kern_gmmu.c:251` | confirmed |
| G-06 | Dois escritores de tabela: o RM (monta a árvore por callbacks de percurso) e o UVM (monta a árvore dos espaços de usuário e a registra no RM) | `struct MMU_WALK_CALLBACKS g_gmmuWalkCallbacks` ; `nvUvmInterfaceSetPageDirectory(gpu_va_space->duped_gpu_va_space,` | `RM/gmmu_walk.c:38-41`; `UVM/uvm_va_space.c:1486` | confirmed |
| G-07 | Para a família GB20x o UVM trata a MMU como a da Hopper, não como a do GB10x | `Note that GB20x MMU behaves as Hopper MMU, so it inherits from` / `Hopper's MMU, not from GB10x.` | `UVM/uvm_hal.c:287-288` (entrada da arquitetura `GB200`, linhas 283-291) | confirmed |
| G-08 | A GB202 cai na arquitetura `BLACKWELL_GB2XX` no RM, e esse valor (0x01B0) é o mesmo da constante `ARCHITECTURE_GB200` do UVM | `case HAL_IMPL_GB202:` ... `*gpuArch = GPU_ARCHITECTURE_BLACKWELL_GB2XX;` ; `GPU_ARCHITECTURE_BLACKWELL_GB2XX GPU_ARCHITECTURE(_CLASSIC, 0x01B0)` ; `NV2080_CTRL_MC_ARCH_INFO_ARCHITECTURE_GB200 (0x000001B0)` | `src/nvidia/src/kernel/gpu/gpu.c:4823-4826`; `SW/nv_arch.h:53`; `UVM/ctrl2080mc.h:38` | derived (igualdade numérica; o código que passa o valor do RM ao UVM não está no clone) |
| G-09 | O cabeçalho da classe de canal `BLACKWELL_CHANNEL_GPFIFO_B` (0xCA6F) tem guarda de inclusão com nome "gb202"; essa classe herda as operações de host da classe A (inclusive as de TLB) | `#ifndef __gb202_clca6f_h__` ; `#define  BLACKWELL_CHANNEL_GPFIFO_B (0x0000CA6F)` ; `.parent_id = BLACKWELL_CHANNEL_GPFIFO_A,` | `UVM/clca6f.h:24,33`; `UVM/uvm_hal.c:227-229` | derived (o vínculo vem do nome da guarda) |
| G-10 | Regra de herança das tabelas HAL do UVM: operação nula copia a do pai | `// Go through all the ops and assign from parent's corresponding op` / `// if NULL` | `UVM/uvm_hal.c:536-537` | confirmed |
| G-11 | O cabeçalho de MMU da GB202 não define formato de PTE nem de PDE: só "kinds" e uma constante de aperture. Os campos VER3 que o código Blackwell usa estão no cabeçalho da Hopper, incluído pelo código de formato (`#include "published/hopper/gh100/dev_mmu.h"`) | `#define NV_MMU_PTE_APERTURE_VIDEO_MEMORY  0x00000000` (único aperture; o arquivo inteiro tem 26 `#define`, contando a guarda) | `SW/blackwell/gb202/dev_mmu.h:26-50`; `RM/arch/hopper/kern_gmmu_fmt_gh10x.c:28` | confirmed (conteúdo dos arquivos); a leitura "então a GB202 usa o formato da Hopper" é interpretação (I1) |

## 2. Formato das tabelas de página

Cabeçalho do formato VER3 (Hopper) usado também pela Blackwell: `UVM/hwref/hopper/gh100/dev_mmu.h` (abreviado `HOP-MMU` abaixo).

### 2.1 Níveis, tamanho de VA e tamanho das entradas

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| F-01 | Hopper e GB10x só aceitam o formato versão 3 | `return (version == GMMU_FMT_VERSION_3);` ; `NV_ASSERT_OR_RETURN_VOID(version == GMMU_FMT_VERSION_3);` | `RM/arch/hopper/kern_gmmu_gh100.c:43-46`; `RM/arch/hopper/kern_gmmu_fmt_gh10x.c:59` | confirmed |
| F-02 | VA de 57 bits no formato v3 | ` *  NUM_VA_BITS = 57` ; `case GMMU_FMT_VERSION_3:` / `pKernelGmmu->maxVASize = 1ULL << 57;` ; `static NvU32 num_va_bits_hopper(void)` / `return 57;` | `RM/arch/blackwell/kern_gmmu_fmt_gb10x.c:30`; `RM/arch/maxwell/kern_gmmu_gm107.c:326-327`; `UVM/uvm_hopper_mmu.c:113-116` | confirmed |
| F-03 | Seis níveis (PD4 a PD0, mais a tabela de folhas); o nível PD0 é "dual" (duas tabelas: 64 KB e 4 KB) | diagrama abaixo; `pLevels[4].numSubLevels   = 2;` ; `NV_ASSERT_OR_RETURN_VOID(numLevels >= 7);` | `RM/arch/blackwell/kern_gmmu_fmt_gb10x.c:30-49`; `RM/arch/hopper/kern_gmmu_fmt_gh10x.c:60,100` | confirmed |
| F-04 | Bits de índice por nível: 1, 9, 9, 9, 8 e depois 9 (páginas de 4 KB) ou 5 (páginas de 64 KB) | `static const NvU32 bit_widths[] = {1, 9, 9, 9, 8};` ; `case UVM_PAGE_SIZE_4K:` / `return 9;` ; `case UVM_PAGE_SIZE_64K:` / `return 5;` | `UVM/uvm_hopper_mmu.c:92,102-105` | confirmed |
| F-05 | Faixas de VA por nível no UVM (mesma tabela para Hopper e GB10x) | `PDE4 56:56`, `PDE3 55:47`, `PDE2 46:38`, `PDE1 37:29`, `PDE0 28:21`, `PTE_64K / PTE_4K 20:16 / 20:12` | `UVM/uvm_hopper_mmu.c:24-32`; `UVM/uvm_blackwell_mmu.c:24-31` | confirmed |
| F-06 | Tamanho das entradas: PDE 8 bytes, PDE dual 16 bytes, PTE 8 bytes | `#define NV_MMU_VER3_PDE__SIZE  8` ; `#define NV_MMU_VER3_DUAL_PDE__SIZE  16` ; `#define NV_MMU_VER3_PTE__SIZE  8` | `HOP-MMU:440,488,547`; confirmado por `UVM/uvm_hopper_mmu.c:85-88` (`entries_per_index_hopper(depth) * 8`) | confirmed |
| F-07 | Tamanho da tabela alocada: 256 bytes para a tabela de páginas de 64 KB; 4096 bytes nos demais níveis. O nível 0 só precisa de 16 bytes, mas o mínimo efetivo é 32 e a alocação é alinhada a 4 KB | `if (depth == 5 && page_size == UVM_PAGE_SIZE_64K)` / `return 256;` ; `// depth 0 requires only a 16-byte allocation to house the 2 entries at the` / `// 0-depth level. Due to HW constraints, the effective minimum allocation` / `// size is 32 bytes. It must be 4k aligned.` | `UVM/uvm_hopper_mmu.c:121-126` | confirmed |
| F-08 | Ampere (geração anterior): formato v2, VA de 49 bits, topo PD3 [48:47] | ` *  PD3 [48:47]` ; `case GMMU_FMT_VERSION_2:` / `pKernelGmmu->maxVASize = 1ULL << 49;` | `RM/arch/ampere/kern_gmmu_fmt_ga10x.c:30`; `RM/arch/maxwell/kern_gmmu_gm107.c:323-324` | confirmed |

Diagrama literal do GB10x (`RM/arch/blackwell/kern_gmmu_fmt_gb10x.c:29-50`). O comentário do Hopper (`kern_gmmu_fmt_gh10x.c:31-52`) é igual, menos a página de 256 GB:

```
 *  NUM_VA_BITS = 57
 *  PD4[56]
 *  PD3 [55:47]
 *  PD2 [46:38] / PT_256GB [46:38] (256GB Page)
 *  PD1 [37:29] / PT_512M [37:29] (512MB page)
 *  PD0 [28:21] / PT_LARGE [28:21] (2MB page)
 *  PT_SMALL       PT_BIG (64KB page)
 *  [20:12]               [20:16]
```

### 2.2 Tamanhos de página

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| F-10 | GB10x: páginas de 256 GB, 512 MB, 2 MB, 64 KB e 4 KB | `return UVM_PAGE_SIZE_256G \| UVM_PAGE_SIZE_512M \| UVM_PAGE_SIZE_2M \| UVM_PAGE_SIZE_64K \| UVM_PAGE_SIZE_4K;` ; `// Page directory 1 can now hold a PTE pointing to a 256GB Page` / `pLevels[2].bPageTable = NV_TRUE;` | `UVM/uvm_blackwell_mmu.c:58-61`; `RM/arch/blackwell/kern_gmmu_fmt_gb10x.c:59-60` | confirmed |
| F-11 | Hopper e, pela herança, GB20x/GB202: 512 MB, 2 MB, 64 KB e 4 KB. O Hopper não define `page_sizes`; ele copia a tabela do Ampere, que lista esses quatro | `return UVM_PAGE_SIZE_512M \| UVM_PAGE_SIZE_2M \| UVM_PAGE_SIZE_64K \| UVM_PAGE_SIZE_4K;` ; `hopper_mmu_mode_hal = *ampere_mmu_mode_hal;` | `UVM/uvm_ampere_mmu.c:50-53`; `UVM/uvm_hopper_mmu.c:524` (sem atribuição de `page_sizes` nas linhas 524-537) | derived (a ligação GB20x -> Hopper está em G-07; o resultado é a soma de três trechos) ; **conflict: true** com F-10 se alguém ler "Blackwell" sem separar GB10x de GB20x (ver C-01) |
| F-12 | Página "grande" (big) de 64 KB como padrão; Pascal em diante só admite 64 KB | `// Retrieve Big Page Size. If it is not yet set, set it to 64K.` ; ` * On Pascal+, the big page size is 64KB. The function checks and captures` | `RM/kern_gmmu.c:744`; `RM/arch/pascal/kern_gmmu_gp100.c:297` | confirmed |
| F-13 | Os limites de bit dos níveis dão 4 KB (bit 12), 64 KB (bit 16), 2 MB (bit 21), 512 MB (bit 29), 256 GB (bit 38) | (conta; ver A-02) | `RM/arch/blackwell/kern_gmmu_fmt_gb10x.c:38-49` | derived |
| F-14 | Uma entrada do nível mais alto (PDE4) cobre 64 PB; mesma frase em Hopper e Blackwell | `// A single top level PDE on Blackwell covers 64 PB and that's the minimum` / `// size that can be used.` ; `parent_gpu->rm_va_size = 64 * UVM_SIZE_1PB;` | `UVM/uvm_blackwell.c:44-47`; `UVM/uvm_hopper.c:55-58` | confirmed |

### 2.3 Entrada de página (PTE) no formato v3

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| F-20 | Bit de validade: bit 0 | `#define NV_MMU_VER3_PTE_VALID  0:0` | `HOP-MMU:490` | confirmed |
| F-21 | Aperture (onde a página está): bits 2:1. 0 = memória de vídeo local, 1 = peer, 2 = memória do sistema coerente, 3 = memória do sistema não coerente | `NV_MMU_VER3_PTE_APERTURE  2:1` ; `..._VIDEO_MEMORY 0x00000000` ; `..._PEER_MEMORY 0x00000001` ; `..._SYSTEM_COHERENT_MEMORY 0x00000002` ; `..._SYSTEM_NON_COHERENT_MEMORY 0x00000003` | `HOP-MMU:493-497` | confirmed |
| F-22 | Flags de permissão e cache num campo único PCF ("permission control flags"), bits 7:3 | `#define NV_MMU_VER3_PTE_PCF  7:3` ; comentário no UVM: `// PCF (permission control flags) 7:3` | `HOP-MMU:498`; `UVM/uvm_hopper_mmu.c:199` | confirmed |
| F-23 | "Kind" (tipo de superfície): bits 11:8. O UVM usa `GENERIC_MEMORY` (0x6) | `#define NV_MMU_VER3_PTE_KIND  11:8` ; `#define NV_MMU_PTE_KIND_GENERIC_MEMORY  0x6` | `HOP-MMU:535`; `SW/blackwell/gb202/dev_mmu.h:28`; `UVM/uvm_hopper_mmu.c:203` | confirmed |
| F-24 | Endereço físico: bits 51:12, deslocamento 12 (páginas alinhadas a 4 KB) | `#define NV_MMU_VER3_PTE_ADDRESS  51:12` ; `#define NV_MMU_VER3_PTE_ADDRESS_SHIFT  0x0000000c` | `HOP-MMU:536,546` | confirmed |
| F-25 | Identificador de peer: bits 63:61 (valores 0 a 7) | `#define NV_MMU_VER3_PTE_PEER_ID  63:(64-3)` | `HOP-MMU:537-545` | confirmed |
| F-26 | Endereço de vidmem na prática: o UVM define o campo como 39:12 e diz que o campo "não é mantido pelo hardware". Peer e sistema usam 51:12 | `// Field defines which are unmaintained by HW` ; `#define NV_MMU_VER3_PTE_ADDRESS_VID  39:12` | `UVM/uvm_hopper_mmu.c:43-46` | confirmed (ver C-03 sobre 38 contra 40 bits) |
| F-27 | O PTE v3 não tem campo de linha de compressão (comptag) | `// range NV_MMU_VER3_PTE_ADDRESS because v3 doesn't have comptagline in the PTE.` | `RM/arch/hopper/kern_gmmu_fmt_gh10x.c:180` | confirmed |
| F-28 | O PTE v2 (Turing e Ampere) tinha bits separados para volátil, criptografado, privilégio, somente leitura e atômico desabilitado, nos bits 3 a 7; o v3 troca esses bits pelo PCF de 5 bits (mesmo intervalo 7:3) | `NV_MMU_VER2_PTE_VOL  3:3` ; `..._ENCRYPTED 4:4` ; `..._PRIVILEGE 5:5` ; `..._READ_ONLY 6:6` ; `..._ATOMIC_DISABLE 7:7` | `HOP-MMU:383-397` | confirmed (campos); a leitura "o PCF substitui esses bits" é derived |

Combinações do PCF para PTE válida. O cabeçalho define 32 constantes (`HOP-MMU:503-534`), com os nomes `REGULAR`/`PRIVILEGE`, `RW`/`RO`, `ATOMIC`/`NO_ATOMIC`, `CACHED`/`UNCACHED`, `ACE`/`ACD`. Amostra literal:

```
NV_MMU_VER3_PTE_PCF_REGULAR_RW_ATOMIC_CACHED_ACE        0x00000000
NV_MMU_VER3_PTE_PCF_REGULAR_RW_ATOMIC_UNCACHED_ACE      0x00000001
NV_MMU_VER3_PTE_PCF_PRIVILEGE_RW_ATOMIC_CACHED_ACE      0x00000002
NV_MMU_VER3_PTE_PCF_REGULAR_RO_ATOMIC_CACHED_ACE        0x00000004
NV_MMU_VER3_PTE_PCF_REGULAR_RW_NO_ATOMIC_CACHED_ACE     0x00000008
NV_MMU_VER3_PTE_PCF_REGULAR_RW_ATOMIC_CACHED_ACD        0x00000010
NV_MMU_VER3_PTE_PCF_PRIVILEGE_RO_NO_ATOMIC_UNCACHED_ACD 0x0000001F
```

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| F-30 | Privilégio, somente leitura, atômicos e cacheável são escolhas do PCF: `REGULAR`/`PRIVILEGE`, `RW`/`RO`, `ATOMIC`/`NO_ATOMIC`, `CACHED`/`UNCACHED` | lista das 32 constantes (amostra acima) | `HOP-MMU:503-534` | confirmed |
| F-31 | Padrão de bits do PCF: bit 0 = cached(0)/uncached(1), bit 1 = regular(0)/privilege(1), bit 2 = RW(0)/RO(1), bit 3 = atomic(0)/no_atomic(1), bit 4 = ACE(0)/ACD(1). Conferi nas 32 constantes | (leitura da lista) | `HOP-MMU:503-534` | derived (o código não declara o mapeamento por bit) |
| F-32 | `ACE` é usado quando os contadores de acesso estão ligados e `ACD` quando estão desligados | `bool ac = !(flags & UVM_MMU_PTE_FLAGS_ACCESS_COUNTERS_DISABLED);` ; `if (ac) {` ... `..._NO_ATOMIC_CACHED_ACE` | `UVM/uvm_hopper_mmu.c:134,140-147,155-162` | confirmed (uso); a expansão da sigla não aparece no cabeçalho |
| F-33 | No UVM, leitura só e leitura-escrita saem como `NO_ATOMIC`; só `READ_WRITE_ATOMIC` sai como `ATOMIC`. Todos como `REGULAR` | `case UVM_PROT_READ_WRITE_ATOMIC:` / `return cached ? NV_MMU_VER3_PTE_PCF_REGULAR_RW_ATOMIC_CACHED_ACE :` | `UVM/uvm_hopper_mmu.c:140-153` | confirmed |
| F-34 | `CACHED` quer dizer que o L2 da GPU pode guardar o dado de forma não coerente; em vidmem isso é seguro | `// data from the page pointed by the PTE may be cached incoherently by the` / `// GPU L2. ... For vidmem` / `// aperture, however, it is safe to use _CACHED` | `UVM/uvm_mmu.h:159-163` | confirmed |
| F-35 | PTE inválida (valid = 0) usa o PCF para dizer o motivo: 0 = invalid, 1 = sparse, 2 = mapping nowhere, 3 = no valid 4 KB page | `NV_MMU_VER3_PTE_PCF_INVALID 0x00000000` ; `..._SPARSE 0x00000001` ; `..._MAPPING_NOWHERE 0x00000002` ; `..._NO_VALID_4KB_PAGE 0x00000003` | `HOP-MMU:499-502` | confirmed |
| F-36 | Acesso a mapeamento esparso (sparse) não gera falha: a MMU manda leituras e escritas para páginas de depuração | `// Sparse PTEs will indicate to MMU to route all reads and writes to the` / `// debug pages. Therefore, accesses to sparse mappings do not generate` / `// faults.` | `UVM/uvm_mmu.h:179-181` | confirmed |
| F-37 | PTE "unmapped" de página grande manda a MMU parar o percurso e não guardar PTEs de 4 KB; PTE grande totalmente zero (inválida) manda ler e guardar PTEs de 4 KB | `// GPU MMU that there might be 4k PTEs present instead, and that those 4k` / `// entries should be read and cached. Unmapped big PTEs indicate that there` / `// are no 4k PTEs below the unmapped big entry, so MMU should stop its walk` | `UVM/uvm_mmu.h:190-193` | confirmed |
| F-38 | A tradução do RM entre PCF "de software" e "de hardware" cobre 25 combinações de PTE válida; o cabeçalho tem 32 | `#define PTE_PCF_VALID_LIST(fn) \` (25 itens) | `RM/arch/hopper/kern_gmmu_gh100.c:111-136` | confirmed (lista); a contagem 25 + 7 = 32 é derived (ver A-06 e C-05) |

### 2.4 Entrada de diretório (PDE) no formato v3

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| F-40 | PDE simples (8 bytes): bit 0 válido/`IS_PTE`, aperture em 2:1 (0 = inválido, 1 = vídeo, 2 = sistema coerente, 3 = sistema não coerente), PCF em 5:3, endereço em 51:12 com deslocamento 12 | `NV_MMU_VER3_PDE_APERTURE  2:1` ; `NV_MMU_VER3_PDE_PCF  5:3` ; `NV_MMU_VER3_PDE_ADDRESS  51:12` ; `NV_MMU_VER3_PDE_ADDRESS_SHIFT  0x0000000c` | `HOP-MMU:414-440` | confirmed |
| F-41 | PDE dual (16 bytes) = metade "big" + metade "small". Big: aperture 2:1, PCF 5:3, endereço 51:8 (deslocamento 8). Small: aperture 66:65, PCF 69:67, endereço 115:76 (deslocamento 12) | `NV_MMU_VER3_DUAL_PDE_ADDRESS_BIG  51:8` ; `NV_MMU_VER3_DUAL_PDE_APERTURE_SMALL  66:65` ; `NV_MMU_VER3_DUAL_PDE_ADDRESS_SMALL  115:76` ; `NV_MMU_VER3_DUAL_PDE_ADDRESS_BIG_SHIFT 8` | `HOP-MMU:442-488` | confirmed |
| F-42 | O PCF do PDE codifica "ATS permitido ou não" e "cacheado ou não" (PDE válido) ou "inválido/esparso" (PDE inválido) | `NV_MMU_VER3_PDE_PCF_VALID_CACHED_ATS_ALLOWED  0x00000000` ; `..._VALID_UNCACHED_ATS_NOT_ALLOWED 0x00000003` ; `..._SPARSE_ATS_ALLOWED 0x00000001` | `HOP-MMU:425-437` | confirmed |
| F-43 | Num nível com `bPageTable`, o próprio diretório pode conter um PTE (página de 512 MB no PD1; 2 MB no PD0). No GB10x o PD2 também (256 GB) | `// Page directory 1 can hold a PTE pointing to a 512MB Page` / `pLevels[3].bPageTable     = NV_TRUE;` | `RM/arch/hopper/kern_gmmu_fmt_gh10x.c:92-93` | confirmed |
| F-44 | Em máquinas com ATS, a Hopper faz busca em paralelo na tabela ATS (CPU) e na tabela da GPU. O UVM marca `ATS_NOT_ALLOWED` nas faixas que ele gerencia, em granularidade de 512 MB (PDE1). "Todas as GPUs com ATS" usam o mesmo mecanismo | `// Hopper GPUs on ATS-enabled systems, perform a parallel lookup on both` / `// ATS and GMMU page tables.` ; `// and have the same PDE1 coverage (512MB).` | `UVM/uvm_hopper_mmu.c:342-343`; `UVM/uvm_mmu.h:104-107` | confirmed |

### 2.5 Aperture: como RM e UVM escolhem

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| F-50 | RM: memória de vídeo -> aperture vídeo; memória do sistema -> coerente se a página é cacheada pela CPU, senão não coerente | `return GMMU_APERTURE_VIDEO;` ; `return GMMU_APERTURE_SYS_COH;` ; `return GMMU_APERTURE_SYS_NONCOH;` | `RM/kern_gmmu.c:620,624,626` | confirmed |
| F-51 | UVM: `SYS` -> coerente; `SYS_NON_COHERENT` -> não coerente; `VID` -> vídeo; peer e EGM -> peer | `aperture_bits = NV_MMU_VER3_PTE_APERTURE_SYSTEM_COHERENT_MEMORY;` ... `NV_MMU_VER3_PTE_APERTURE_PEER_MEMORY;` | `UVM/uvm_hopper_mmu.c:186-195` | confirmed |

## 3. TLB: invalidação e caches do percurso de tabelas

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| T-01 | Caminho do RM: escreve o registrador `NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE` (deslocamento 0x30B0) e espera o bit `TRIGGER` cair | `GPU_VREG_WR32(pGpu, NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE, pParams->regVal);` ; `// Wait for the invalidate command to complete.` ; `if (FLD_TEST_DRF(_VIRTUAL_FUNCTION_PRIV, _MMU_INVALIDATE, _TRIGGER, _FALSE, regVal))` / `break;` | `RM/arch/blackwell/kern_gmmu_gb100.c:61-64`; `RM/arch/turing/kern_gmmu_tu102.c:69-72`; `SW/blackwell/gb100/dev_vm.h:338` | confirmed (a função `_GB100` é do Blackwell; que o RM a use na GB202 não está provado no clone, ver lacuna 1) |
| T-02 | Campos do registrador de invalidação: `ALL_VA` 0:0, `ALL_PDB` 1:1, `HUBTLB_ONLY` 2:2, `REPLAY` 5:3, `SYS_MEMBAR` 6:6, `ACK` 8:7, `INVAL_SCOPE` 16:15, `CACHE_LEVEL` 26:24, `TRIGGER` 31:31 | `NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE_ALL_VA  0:0` ... `..._TRIGGER  31:31` | `SW/blackwell/gb100/dev_vm.h:339-402` | confirmed |
| T-03 | Escopo por espaço de endereços: se `ALL_PDB` não está ligado, o RM grava o PDB (endereço e aperture) nos registradores `MMU_INVALIDATE_PDB` (0x30A0) e `MMU_INVALIDATE_UPPER_PDB` (0x30A4) | `if (!FLD_TEST_DRF(_VIRTUAL_FUNCTION_PRIV, _MMU_INVALIDATE, _ALL_PDB, _TRUE, pParams->regVal))` / `kgmmuSetPdbToInvalidate_HAL(pGpu, pKernelGmmu, pParams);` | `RM/arch/blackwell/kern_gmmu_gb100.c:55-58`; `RM/arch/turing/kern_gmmu_tu102.c:134-154`; `SW/blackwell/gb100/dev_vm.h:327-337` | confirmed |
| T-04 | O RM não invalida por faixa: liga `ALL_VA` e escolhe um PDB ou todos | `// Not using range-based invalidate.` | `RM/arch/maxwell/kern_gmmu_gm107.c:193` | confirmed |
| T-05 | Escopo de TLB: todos, só os de "link" (NVLink) ou só os que não são de link | `NV_GMMU_INVAL_SCOPE_ALL_TLBS` / `_LINK_TLBS` / `_NON_LINK_TLBS` ; registrador `INVAL_SCOPE_*` 0, 1, 2 | `RM/arch/ampere/kern_gmmu_ga100.c:59-75`; `SW/blackwell/gb100/dev_vm.h:364-367` | confirmed |
| T-06 | Invalidação de BAR só precisa do TLB do "hub", não do de GR | `// For host VAS (e.g. BAR) we do not have to invalidate GR.` ; `..._HUBTLB_ONLY, _TRUE` | `RM/arch/maxwell/kern_gmmu_gm107.c:225-229` | confirmed |
| T-07 | Nível do cache: o registrador permite invalidar só PTE (`PTE_ONLY`) ou PTE e diretórios até `UP_TO_PDE0` ... `UP_TO_PDE5` | `NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE_CACHE_LEVEL_PTE_ONLY 0x00000001` ; `..._UP_TO_PDE0 0x00000002` ; `..._UP_TO_PDE5 0x00000007` | `SW/blackwell/gb100/dev_vm.h:380-388` | confirmed |
| T-08 | Existe cache de diretórios e cache de PDB: o hardware ignora invalidação cujo PDB não está "no cache de PDB" | `// GPU's PDB. This is harmless - hardware will drop an invalidate targeting` / `// a PDB that is not in the PDB cache.` | `UVM/uvm_mmu.h:286-287` | confirmed |
| T-09 | Existe um cache do percurso de tabelas ("page table walk cache"), com linha de 32 bytes | `// The GMMU page table walk cache operates at its own CL granularity` / `// (32B).` | `UVM/uvm_gpu.h:1325-1326` | confirmed |
| T-10 | A GPU faz leitura antecipada (prefetch) de PDB e de tradução física: Pascal já podia ler entradas de PDB não inicializadas; Blackwell tem prefetcher de tradução física (Hopper não) | `// Because GMMU can prefetch uninitialized PDB entries and cause XVE to hang,` ; `// Blackwell has a physical translation prefetcher, meaning SW must assume` ; `// Hopper doesn't prefetch translations for physical requests` | `RM/arch/pascal/kern_gmmu_gp100.c:49`; `UVM/uvm_blackwell.c:84-85`; `UVM/uvm_hopper.c:97` | confirmed |
| T-11 | Caminho do UVM: métodos de host no canal (`MEM_OP_A` a `MEM_OP_D`, operação `MMU_TLB_INVALIDATE` = 0x09, `..._TARGETED` = 0x0A) | `#define NVC96F_MEM_OP_D_OPERATION_MMU_TLB_INVALIDATE  0x00000009` ; `..._TARGETED  0x0000000a` | `UVM/clc96f.h:67-71` | confirmed |
| T-12 | Esses métodos invalidam por PDB (um ou todos), por nível ("este nível e todos abaixo"), com ou sem os TLBs de GPC, com `SYSMEMBAR` e com confirmação global | `// Invalidate affects this level and all below` ; `// Invalidate tlb caches at all levels of the page table` ; `TLB_INVALIDATE_GPC_ENABLE 0x00000000` / `_DISABLE 0x00000001` | `UVM/clc96f.h:47-61` | confirmed |
| T-13 | Invalidação por VA: o tamanho é potência de 2 que contém a faixa; o hardware alinha o endereço para baixo ao tamanho; o campo guarda log2 do tamanho em unidades de 4 KB | `// The invalidation size must be a power-of-two number of pages containing` / `// the passed interval` ; `// The hardware aligns the target address down to the invalidation size.` ; `log2_invalidation_size -= 12;` | `UVM/uvm_blackwell_host.c:111-112,122,130-131`; `UVM/clc96f.h:37` | confirmed |
| T-14 | Não existe invalidação só de tradução física: a única forma é invalidar todos os PDBs e todas as VAs | `// There is no specific mechanism to invalidate only physical translations,` / `// nor per-address physical translations.` | `UVM/uvm_blackwell_host.c:181-182` | confirmed |
| T-15 | Há TLBs menores dentro de cada GPC ("uTLB"): por GPC há 2 uTLB "LTP" por TPC mais 1 uTLB "RGG". No Blackwell, até 10 TPCs por GPC (no Hopper, até 9) | `// There are up to 10 TPCs per GPC in Blackwell, and there are 2 LTP uTLBs per TPC. Besides, there is one active RGG uTLB per GPC.` (quebrado em 3 linhas) ; `NvU32 utlbs = parent_gpu->rm_info.maxTpcPerGpcCount * 2 + 1;` | `UVM/uvm_blackwell_fault_buffer.h:31-33,87`; `UVM/uvm_hopper_fault_buffer.h:31` | confirmed |
| T-16 | A invalidação em lote do UVM cai para "invalidar tudo" depois de 8 faixas; o valor é provisório | `// TODO: Bug 1767241: Run benchmarks to figure out a good number` / `parent_gpu->tlb_batch.max_ranges = 8;` | `UVM/uvm_blackwell.c:33-34` | confirmed |
| T-17 | No Blackwell, invalidação de TLB não deve usar barreira de memória (membar) avulsa | `// TLB invalidate on Blackwell+ GPUs should not use a standalone membar.` | `UVM/uvm_hal.c:741` | confirmed |
| T-18 | Para fechar uma janela de leitura antecipada, o UVM faz invalidação "fantasma" com VA falsa, sem apagar linhas | `// We don't need to invalidate lines, but we need the invalidate to not be` / `// ignored in order to flush out pending prefetch fills from SYS clients.` | `UVM/uvm_blackwell_host.c:280-281` | confirmed |

## 4. Falhas de página (page faults)

### 4.1 Hardware: buffers, registradores e formato da entrada

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| P-01 | Dois buffers de falha por GPU: índice 0 = non-replayable, índice 1 = replayable | `#define NV_VIRTUAL_FUNCTION_PRIV_MMU_NON_REPLAY_FAULT_BUFFER  0` ; `#define NV_VIRTUAL_FUNCTION_PRIV_MMU_REPLAY_FAULT_BUFFER  1` | `SW/blackwell/gb100/dev_vm.h:146-147` | confirmed |
| P-02 | Registradores por buffer, espaçados de 32 bytes: `LO`/`HI` (endereço do buffer, modo virtual ou físico, aperture), `GET` (ponteiro de 20 bits, bit de corrupção, bit de overflow), `PUT`, `SIZE` (tamanho de 20 bits, enable no bit 31) | `NV_VIRTUAL_FUNCTION_PRIV_MMU_FAULT_BUFFER_LO(i)  (0x00003000+(i)*32)` ; `..._GET_PTR  19:0` ; `..._SIZE_ENABLE  31:31` | `SW/blackwell/gb100/dev_vm.h:148-196` | confirmed |
| P-03 | Cada entrada do buffer tem 32 bytes (8 palavras) | `#define NVC369_BUF_SIZE  32` | `UVM/clc369.h:35` | confirmed |
| P-04 | Campos da entrada: instância (`INST`, campo de 52 bits que guarda o endereço sem os 12 bits baixos; a aperture é o campo `INST_APERTURE`, bits 9:8), endereço da falha (`ADDR`, mesma forma), `TIMESTAMP`, `ENGINE_ID`, `FAULT_TYPE`, `REPLAYABLE_FAULT`, `CLIENT`, `ACCESS_TYPE`, `MMU_CLIENT_TYPE`, `GPC_ID`, `PROTECTED_MODE`, `REPLAYABLE_FAULT_EN`, `VALID` (bit 31 da palavra 7) | `NVC369_BUF_ENTRY_INST  MW((31+1*32):(0*32+12))` ; `..._ADDR  MW((31+3*32):(2*32+12))` ; `..._VALID  MW((31+7*32):(7*32+31))` | `UVM/clc369.h:36-67` | confirmed |
| P-05 | O tamanho padrão do buffer vem do hardware (`SET_DEFAULT`) e é lido em unidades de entrada vezes 32 bytes | `GPU_VREG_FLD_IDX_WR_DRF_DEF(pGpu, _VIRTUAL_FUNCTION_PRIV, _MMU_FAULT_BUFFER_SIZE, index, _SET_DEFAULT, _YES);` ; `faultBufferSize = GPU_VREG_IDX_RD_DRF(...) * NVC369_BUF_SIZE;` | `RM/arch/blackwell/kern_gmmu_gb100.c:325-326` | confirmed (o valor numérico padrão não aparece) |
| P-06 | Tipos de falha (16 valores): PDE, PDE_SIZE, PTE, VA_LIMIT_VIOLATION, UNBOUND_INST_BLOCK, PRIV_VIOLATION, RO_VIOLATION, WO_VIOLATION, PITCH_MASK_VIOLATION, WORK_CREATION, UNSUPPORTED_APERTURE, CC_VIOLATION, UNSUPPORTED_KIND, REGION_VIOLATION, POISONED, ATOMIC_VIOLATION | `#define NV_PFAULT_FAULT_TYPE_PDE  0x00000000` ... `#define NV_PFAULT_FAULT_TYPE_ATOMIC_VIOLATION  0x0000000f` | `SW/blackwell/gb202/dev_fault.h:275-290` | confirmed |
| P-07 | No Blackwell, o tipo de falha `COMPRESSION_FAILURE` foi descontinuado | `// NV_PFAULT_FAULT_TYPE_COMPRESSION_FAILURE fault type is deprecated on` / `// Blackwell.` | `UVM/uvm_blackwell_fault_buffer.c:32-33` | confirmed |
| P-08 | Tipos de acesso: leitura, escrita, atômico (forte e fraco), prefetch, nas versões virtual e física | `NV_PFAULT_ACCESS_TYPE_VIRT_ATOMIC_STRONG 0x00000002` ; `..._VIRT_ATOMIC_WEAK 0x00000004` ; `..._PHYS_READ 0x00000008` | `SW/blackwell/gb202/dev_fault.h:334-347` | confirmed |
| P-09 | Quem pode falhar: clientes de GPC (SM e outros) ou de HUB (CE, Host etc.). IDs de engine: Graphics 384, BAR1 256, BAR2 320, CE0 a CE19 de 65 a 84, Host0 em 85, PHYSICAL 56 | `NV_PFAULT_MMU_ENG_ID_GRAPHICS  384` ; `..._BAR1  256` ; `..._BAR2  320` ; `..._CE0  65` ; `..._PHYSICAL  56` ; `NV_PFAULT_MMU_CLIENT_TYPE_GPC 0x00000000` / `_HUB 0x00000001` | `SW/blackwell/gb202/dev_fault.h:28,33-34,74,101,348-349` | confirmed |
| P-10 | A falha de buffer cheio (overflow) é erro fatal | `* @brief Report MMU Fault buffer overflow errors. MMU Fault` / `*        buffer overflow is a fatal error.` | `RM/arch/volta/kern_gmmu_gv100.c:393-394` | confirmed |
| P-11 | Onde o buffer mora: por padrão em memória do sistema, cacheada; em computação confidencial (CC) tem de ficar em vidmem | `faultBufferAddrSpace = bAllocInVidmem ? ADDR_FBMEM : ADDR_SYSMEM;` ; `// Whenever Hopper CC is enabled, HW requires both replayable and non-replayable` | `RM/kern_gmmu.c:1029-1030,1042-1043` | confirmed |

### 4.2 Quem trata: replayable (UVM) e non-replayable (RM + UVM)

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| P-20 | Falha replayable = vem do motor Graphics (SM). Non-replayable = vem de outros motores | `// driver. The Graphics Engine faults are called replayable faults, while the` / `// rest are called non-replayable.` | `UVM/uvm_gpu_non_replayable_faults.c:44-45` | confirmed |
| P-21 | O UVM só atende non-replayable do Copy Engine e do PBDMA (Host/ESCHED); de outros motores são fatais | `// services non-replayable faults from the Copy and PBDMA (Host/ESCHED) Engines.` / `// Non-replayable faults originated in other engines are considered fatal, and` | `UVM/uvm_gpu_non_replayable_faults.c:49-50` | confirmed |
| P-22 | Non-replayable de CE/PBDMA: o hardware tira o canal de execução e todos os canais do mesmo TSG ("fault and switch"). Replayable bloqueia a preempção até o software atender ("fault and stall") | `// preempting the channel associated with the fault, a mechanism called "fault` / `// and switch".` ; `// software (UVM) services the fault. This is sometimes known as "fault and` / `// stall".` | `UVM/uvm_gpu_non_replayable_faults.c:63-64,75-77` | confirmed |
| P-23 | Posse dos buffers: replayable = o UVM é dono do buffer de hardware (lê PUT, atualiza GET). Non-replayable = o RM é dono, copia as falhas de CE/PBDMA para um "shadow buffer" que o UVM lê | `// replayable faults, UVM has sole SW ownership of the hardware buffer` ; `// faults, UVM reads the fault entries out of a regular CPU buffer, shared with` / `// RM, called "shadow buffer".` | `UVM/uvm_gpu_non_replayable_faults.c:96,100-101` | confirmed |
| P-24 | O UVM assume a interrupção de falha replayable (e o RM a devolve se o UVM sair) | `status = uvm_rm_locked_call(nvUvmInterfaceOwnPageFaultIntr(parent_gpu->rm_device, NV_TRUE));` ; `// Disable the interrupt when RM loses the ownership and enable it back when` | `UVM/uvm_gpu_replayable_faults.c:188`; `RM/arch/volta/kern_gmmu_gv100.c:89-91` | confirmed |
| P-25 | Se a interrupção replayable chega ao RM, é erro | `NV_PRINTF(LEVEL_ERROR, "Unexpected replayable interrupt routed to RM. Verify UVM took ownership.\n");` | `RM/kern_gmmu.c:2453` | confirmed |
| P-26 | Non-replayable: a cópia do buffer de hardware para o shadow acontece na "metade de cima" (top half) da interrupção; o serviço depois só lê a cópia | `// This interrupt was already cleared in the top half and "serviced" in the top half since copy from HW fault buffer always happens in the top half.` (em 4 linhas) | `src/nvidia/src/kernel/gpu/intr/arch/turing/intr_tu102.c:1128-1130`; `RM/kern_gmmu.c:2383-2386` | confirmed |
| P-27 | O RM só atende falha que o cliente (UVM) não atende: o UVM trata CE/PBDMA com o bit `REPLAYABLE_FAULT_EN` quando o buffer do cliente está ligado | `*bRmServiceable = (!bClientBufEnabled \|\| !bUvmHandledNonFatal \|\| !(bEngineCE \|\| bPbdmaFault));` | `RM/arch/volta/kern_gmmu_gv100.c:727` | confirmed |
| P-28 | Laço do UVM para replayable: busca entradas em lote, ordena e converte instância em espaço de VA, atende o lote e emite replay | `status = fetch_fault_buffer_entries(parent_gpu, batch_context, FAULT_FETCH_MODE_BATCH_READY);` ; `status = preprocess_fault_batch(parent_gpu, batch_context);` ; `status = service_fault_batch(parent_gpu, FAULT_SERVICE_MODE_REGULAR, batch_context);` | `UVM/uvm_gpu_replayable_faults.c:2925,2934,2943` | confirmed |
| P-29 | Parâmetros padrão: lote de 256 entradas; política de replay `BATCH_FLUSH`; no máximo 20 lotes por execução | `#define UVM_PERF_FAULT_BATCH_COUNT_DEFAULT 256` ; `#define UVM_PERF_FAULT_REPLAY_POLICY_DEFAULT UVM_PERF_FAULT_REPLAY_POLICY_BATCH_FLUSH` ; `#define UVM_PERF_FAULT_MAX_BATCHES_PER_SERVICE_DEFAULT 20` | `UVM/uvm_gpu_replayable_faults.c:73,80,103` | confirmed |
| P-30 | Atender uma página: confere permissão lógica, consulta heurística de "thrashing" (pode atrasar a CPU), escolhe a memória de destino (residência) e manda movimentar e mapear | `new_residency = uvm_va_block_select_residency(va_block,` ; `status = uvm_va_block_service_locked(gpu, va_block, va_block_retry, block_context);` | `UVM/uvm_gpu_replayable_faults.c:1513,1580` | confirmed |
| P-31 | O ponteiro de instância da entrada é traduzido para o espaço de VA e a GPU (as entradas são ordenadas por instância para fazer poucas traduções) | `// Translate all instance pointers to a VA space and GPU instance. Since the` / `// buffer is ordered by instance_ptr, we minimize the number of translations.` | `UVM/uvm_gpu_replayable_faults.c:1000-1001` | confirmed |
| P-32 | Replay: o UVM empurra no canal um método "replay" para o hardware reexecutar os acessos que falharam. Tipos: `NONE`, `START`, `START_ACK_ALL`, `CANCEL_TARGETED`, `CANCEL_GLOBAL`, `CANCEL_VA_GLOBAL` | `gpu->parent->host_hal->replay_faults(&push, type);` ; `NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE_REPLAY_START  0x00000001` | `UVM/uvm_gpu_replayable_faults.c:507`; `SW/blackwell/gb100/dev_vm.h:348-354` | confirmed |
| P-33 | Falha fatal (permissão ou endereço inválido) não interrompe o atendimento; é marcada e depois "cancelada" por canal ou por faixa de VA | `// Fatal faults are flagged as fatal for later cancellation. Servicing is not` / `// interrupted on fatal faults due to insufficient permissions or invalid` / `// addresses.` | `UVM/uvm_gpu_replayable_faults.c:1340-1342` | confirmed |
| P-34 | Erro global (falta de memória, ECC): cancela todas as falhas para disparar RC (recuperação de canal robusta) | `// Unconditionally cancel all faults to trigger RC. This will not` | `UVM/uvm_gpu_replayable_faults.c:2953` | confirmed |
| P-35 | O cancelamento é um método de host no canal; se falhar, a aplicação pode travar ou o sistema cair | `// Push a fault cancel method on the given client. Any failure during this` / `// operation may lead to application hang (requiring manual Ctrl+C from the` / `// user) or system crash (requiring reboot).` | `UVM/uvm_gpu_replayable_faults.c:336-339` | confirmed |
| P-36 | Caminho do RM numa falha atendida por ele (visto só no ramo de função virtual SR-IOV): acha o canal pelo bloco de instância, grava notificação de erro `MMU_ERR_FLT` no TSG e reinicia o canal com motivo `MMU_FLT` | `kfifoConvertInstToKernelChannel_HAL(pGpu, pKernelFifo,` / `&pParsedFaultEntry->mmuFaultInstBlock, &pKernelChannel);` ; `ROBUST_CHANNEL_FIFO_ERROR_MMU_ERR_FLT,` ; `resetChannelParams.resetReason = NV906F_CTRL_CMD_RESET_CHANNEL_REASON_MMU_FLT;` | `RM/kern_gmmu.c:3017-3018,3095,3100` | confirmed (o ramo do PF sem SR-IOV não está no clone) |
| P-37 | Prefetch: por padrão uma falha de prefetch é tratada como leitura; há registrador para filtrar (enviar todas ou nenhuma) | `// Prefetch faults, if not ignored, are handled like read faults and` ; `NV_VIRTUAL_FUNCTION_PRIV_MMU_PAGE_FAULT_CTRL_PRF_FILTER_SEND_ALL 0x00000000` / `_SEND_NONE 0x00000003` | `UVM/uvm_hal_types.h:613`; `SW/blackwell/gb100/dev_vm.h:197-200` | confirmed |
| P-38 | Endereço da falha: a GPU entrega 57 bits e o RM estende o sinal (forma canônica) para o UVM, se a VA da GPU for pelo menos tão larga quanto a da CPU (`if (gpuVaAddrShift >= cpuAddrShift)`, linha 911) | `*pMmuFaultAddress = (NvU64)(((NvS64)*pMmuFaultAddress << (64 - 57)) >>` / `(64 - 57));` | `RM/arch/hopper/kern_gmmu_gh100.c:919-920` | confirmed (função de Hopper; ver G-07/G-08) |

## 5. Relação com a CPU

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| U-01 | O módulo `nvidia-uvm` implementa a memória unificada: ele move as páginas para o processador que acessa, depois mapeia | `// Moves the physical pages of the given region onto the destination processor.` ; `// Performs any operations necessary to establish a coherent mapping` / `// (migrations, cache invalidates, etc.) in response to the given service block` | `UVM/uvm_va_block.h:722`; `UVM/uvm_va_block.h:1268-1270` | confirmed |
| U-02 | Migração também por contadores de acesso: a GPU conta acessos remotos por região (granularidade de 64 KB, 2 MB, 16 MB ou 16 GB) e notifica quando passa de um limite (padrão 256, faixa 1 a 65535) | `MODULE_PARM_DESC(uvm_perf_access_counter_migration_enable, "Whether access counters will trigger migrations."` ; `NV_VIRTUAL_FUNCTION_PRIV_ACCESS_COUNTER_CONFIG_MIMC_GRANULARITY_2M 0x00000001` ; `#define UVM_PERF_ACCESS_COUNTER_THRESHOLD_DEFAULT   256` | `UVM/uvm_gpu_access_counters.c:81-82,45`; `SW/blackwell/gb100/dev_vm.h:409-412` | confirmed |
| U-03 | A VA de uma GPU Hopper/Blackwell no UVM tem 57 bits (128 PB) e o desenho de uso fica assim: RM nos primeiros 64 PB, depois identidade de pares, depois mapa linear da vidmem (até 1 TB) | `// Hopper-Rubin:` / `+----------------+ 128PB` ; `\|  rm_mem(64PB)  \| (rm_va_size)` ; `\|  (up to 1TB)   \|` | `UVM/uvm_mmu.h:42-64` | confirmed |
| U-04 | ATS (Address Translation Services) é opcional e depende da plataforma: o parâmetro do módulo "não tem efeito a menos que a plataforma suporte ATS" | `"Any other value is ignored. Has no effect unless the "` / `"platform supports ATS."` | `UVM/uvm_ats.c:33-34` | confirmed |
| U-05 | O UVM liga a GPU ao espaço de endereços da CPU via `iommu_sva_bind_device()` (SVA) e grava PASID e bit de ATS no bloco de instância. O comentário de compatibilidade cita `arm_smmu_sva_bind()` em aarch64 | `iommu_handle = UVM_IOMMU_SVA_BIND_DEVICE(&pci_dev->dev, mm);` ; `// For ATS support on aarch64, arm_smmu_sva_bind() is needed for` | `UVM/uvm_ats_sva.c:352`; `UVM/uvm_ats_sva.h:32-33` | confirmed |
| U-06 | Blackwell, ATS sem PASID ("non-PASID ATS", também dito "serial ATS"): a GPU traduz IOVA para endereço físico do sistema | `// Whether this GPU uses non-PASID ATS (aka serial ATS) to translate` / `// IOVAs to SPAs.` | `UVM/uvm_gpu.h:1315-1316` | confirmed |
| U-07 | Efeito do prefetcher físico do Blackwell com IOMMU: pode ler uma tradução inválida antiga depois de `dma_map_page()`; o UVM trata com invalidação ("flush" ou "full") | `// transitioning an IOMMU GPA mapping from invalid to valid (dma_map_page() and` / `// friends).` ; `UVM_DMA_MAP_INVALIDATION_FLUSH,` / `UVM_DMA_MAP_INVALIDATION_FULL,` | `UVM/uvm_hal_types.h:620-621,629,632`; `UVM/uvm_blackwell.c:84-120` | confirmed |
| U-08 | HMM (Heterogeneous Memory Management, do kernel Linux) é suportado e ligado por padrão, a menos que configuração do build ou ATS o impeça | `// Support for HMM ( https://docs.kernel.org/mm/hmm.html ):` ; `"Default: false (HMM is enabled if possible). "` | `UVM/uvm_hmm.c:27,31` | confirmed |
| U-09 | Endereços da memória do sistema que a GPU usa vêm da API de DMA do sistema operacional, menos um deslocamento (`dma_addressable_start`) | `cpu_addr = dma_alloc_coherent(&parent_gpu->pci_dev->dev, size, &dma_addr, gfp_flags);` ; `// referencing sysmem from the GPU, dma_addressable_start should be` / `// subtracted from the DMA address we get from the OS.` | `UVM/uvm_gpu.c:3988,3973-3974` | confirmed |
| U-10 | Cada espaço de VA de GPU no UVM tem sua própria árvore de tabelas; o UVM troca o PDB que o RM tinha criado pelo seu | `// Replace the existing PDB, if present, with the new one allocated by UVM.` | `UVM/uvm_va_space.c:1473` | confirmed |
| U-11 | Os acessos da CPU à memória da GPU pelo BAR2 passam por uma MMU da GPU com tabelas e bloco de instância próprios; o registrador `BAR2_BLOCK_LOW_ADDR` guarda o modo (físico ou virtual), o destino e o ponteiro | `NV_VIRTUAL_FUNCTION_PRIV_FUNC_BAR2_BLOCK_LOW_ADDR_MODE_VIRTUAL 0x00000001` ; `status = kbusInitInstBlk_HAL(pGpu, pKernelBus,` | `SW/blackwell/gb100/dev_vm.h:68-70`; `RM/bar2_walk.c:81` | confirmed |
| U-12 | Coerência de cache para memória do sistema não coerente: há operações de L2 `L2_FLUSH_DIRTY` e `L2_SYSMEM_NCOH_INVALIDATE` no método de host | `#define NVC96F_MEM_OP_D_OPERATION_L2_FLUSH_DIRTY  0x00000010` ; `..._L2_SYSMEM_NCOH_INVALIDATE  0x00000011` | `UVM/clc96f.h:72-73` | confirmed |

## 6. Bloco de instância (instance block, PDB) e espaço de endereços por contexto

| id | Dado | Trecho literal curto | Arquivo:linha | Procedência |
|---|---|---|---|---|
| I-01 | Cada canal tem um bloco de instância (memória apontada por um "ponteiro de instância") e o RM grava nele o limite de VA, a base do diretório de páginas (PDB, parte baixa e alta), os dados de ATS e um valor mágico | `status = kgmmuInstBlkVaLimitGet_HAL(pKernelGmmu, pVAS, subctxId, pInstBlkParams, &vaLimitOffset, &vaLimitData);` ; `MEM_WR32(pInstBlk + dirBaseHiOffset, dirBaseHiData);` ; `MEM_WR32(pInstBlk + dirBaseLoOffset, dirBaseLoData);` | `RM/kern_gmmu.c:2105,2155-2156` (e 2189-2190) | confirmed |
| I-02 | Campos que entram na parte baixa do PDB: alvo (aperture), reexecução de falha para textura e para GCC, versão do formato de tabela, tamanho de página grande, bit volátil e endereço | `SF_NUM(_RAMIN_PAGE_DIR_BASE, _TARGET, aperture) \|` ; `SF_DEF(_RAMIN_PAGE_DIR_BASE, _FAULT_REPLAY_TEX, _ENABLED) \|` ; `SF_DEF(_RAMIN, _USE_NEW_PT_FORMAT, _TRUE) :` ; `SF_NUM(_RAMIN_PAGE_DIR_BASE, _LO, addrLo);` | `RM/arch/pascal/kern_gmmu_gp100.c:158-171` | confirmed (código de Pascal; o vínculo a GB202 é derived, ver lacunas). Observação: esse código só liga o bit de formato novo quando a versão do formato é a 2 (`GMMU_FMT_VERSION_2 == pFmt->version`, linha 164), e o caminho de subcontexto da Volta força `_USE_VER2_PT_FORMAT` (`kern_gmmu_gv100.c:377`). **O clone não tem ramo do bloco de instância para o formato v3** |
| I-03 | Limite de VA no bloco: `vaLimit` com os 12 bits baixos em 1 | `*pData   = (vaLimit & vaMask) \| 0xfff;` | `RM/arch/pascal/kern_gmmu_gp100.c:102` | confirmed |
| I-04 | A partir da Volta há um PDB por subcontexto (VEID); o bloco guarda uma entrada `NV_RAMIN_SC_PAGE_DIR_BASE_*(subctxId)` para cada | `*pOffsetLo = SF_OFFSET(NV_RAMIN_SC_PAGE_DIR_BASE_LO(subctxId));` ; `*pDataLo = NV_RAMIN_SC_PAGE_DIR_BASE_TARGET_INVALID;` (subcontexto sem espaço) | `RM/arch/volta/kern_gmmu_gv100.c:385,357` | confirmed |
| I-05 | No bloco de instância base entram o bit `ENABLE_ATS` e o `PASID` | `*pOffset = SF_OFFSET(NV_RAMIN_ENABLE_ATS);` ; `SF_NUM(_RAMIN, _PASID, pasid);` | `RM/arch/volta/kern_gmmu_gv100.c:204-206` | confirmed |
| I-06 | O bloco de instância só liga o ATS se o espaço de VA tem ATS ligado e o PASID já foi dado pelo SO | `// Enable ATS in instance block only when both ATS is enabled in the` / `// vaspace and a valid PASID is provisioned through` | `RM/kern_gmmu.c:2114-2115` | confirmed |
| I-07 | A entrada de falha traz o ponteiro de instância (`INST`) e sua aperture, e o UVM mapeia 1 para 1 entre ponteiro de instância e canal e daí para o espaço de VA | `NVC369_BUF_ENTRY_INST_APERTURE  MW((9+0*32):(0*32+8))` ; `// Physical instance pointer. There is a 1:1 mapping between instance` / `// pointer and channel.` | `UVM/clc369.h:36,42`; `UVM/uvm_user_channel.h:159-160` | confirmed |
| I-08 | Subcontextos de um mesmo TSG têm espaços de VA distintos, e uma falha de SM pode trazer qualquer ponteiro de instância do TSG | `// This structure contains the GPU VA spaces of all the subcontexts in a TSG. It` ; `// since SM fault/access counter notification packets may report any` / `// instance_ptr in the TSG.` | `UVM/uvm_user_channel.h:33-37` | confirmed |
| I-09 | O PDB é do mesmo tamanho do diretório raiz inteiro, não só da parte usada, porque a GMMU pode ler entradas não inicializadas | `// Because GMMU can prefetch uninitialized PDB entries and cause XVE to hang,` / `// we need to allocate all entries of the PDB regardless of vaLimit.` | `RM/arch/pascal/kern_gmmu_gp100.c:49-50` | confirmed (Pascal) |
| I-10 | Endereço de PDB na invalidação: alinhado a 4 KB, aperture só vídeo ou sistema | `NV_VIRTUAL_FUNCTION_PRIV_MMU_INVALIDATE_PDB_ADDR_ALIGNMENT  0x0000000c` ; `..._PDB_APERTURE_VID_MEM 0x00000000` / `..._SYS_MEM 0x00000001` | `SW/blackwell/gb100/dev_vm.h:328-334` | confirmed |

## 7. Diferenças entre gerações que o código mostra

"GB20x" = família da GB202. Linhas de origem entre parênteses.

| id | Aspecto | Ampere | Hopper | Blackwell GB10x | Blackwell GB20x (GB202) | Procedência |
|---|---|---|---|---|---|---|
| D-01 | Formato de tabela | v2 (`gm107.c:323`) | v3 (`gh100.c:43-46`) | v3 (`gb10x.c:57` chama o do Hopper) | UVM: MMU do Hopper (`uvm_hal.c:287-289`) | confirmed (UVM) |
| D-02 | Bits de VA | 49 | 57 | 57 | 57 (herdado, `uvm_blackwell.c:64` pela herança da tabela HAL) | confirmed; GB20x derived |
| D-03 | Níveis | 5 (`ga10x.c:30-45`) | 6 (`gh10x.c:31-52`) | 6 | 6 | confirmed |
| D-04 | Páginas | 4 KB, 64 KB, 2 MB, 512 MB (`uvm_ampere_mmu.c:52`) | igual ao Ampere | **+256 GB** (`uvm_blackwell_mmu.c:60`) | igual ao Hopper, sem 256 GB (`uvm_hal.c:289`) | confirmed; GB20x derived; conflict: true (C-01) |
| D-05 | Campos de PTE | v2: VOL, ENCRYPTED, PRIVILEGE, READ_ONLY, ATOMIC_DISABLE, COMPTAGLINE | v3: PCF 7:3, sem comptag | v3 | v3 | confirmed |
| D-06 | VA de canais e de host | 2^40 (`uvm_ampere.c:64,66`) | 2^57 (`uvm_hopper.c:77,79`) | 2^57 (`uvm_blackwell.c:64,66`) | 2^57 (herdado) | confirmed; GB20x derived |
| D-07 | PDE de nível mais alto cobre | 128 TB (`uvm_ampere.c:43-46`) | 64 PB (`uvm_hopper.c:55-58`) | 64 PB (`uvm_blackwell.c:44-47`) | 64 PB (herdado) | confirmed; GB20x derived |
| D-08 | Prefetch de tradução física | n/d | não faz (`uvm_hopper.c:97`) | faz (`uvm_blackwell.c:84`) | herdado do GB10x | confirmed; GB20x derived |
| D-09 | Inicialização do nível 0 | n/d | `gmmu_pt_depth0_init_required = false` (`uvm_hopper.c:95`) | `= non_pasid_ats_enabled` (`uvm_blackwell.c:80`) | herdado | confirmed; GB20x derived |
| D-10 | uTLBs por GPC | n/d | até 9 TPCs (`uvm_hopper_fault_buffer.h:31`) | até 10 TPCs (`uvm_blackwell_fault_buffer.h:31`) | herdado | confirmed; GB20x derived |
| D-11 | Falha de compressão | tipo existe (`kern_gmmu_gp100.c:220-221`) | existe | descontinuado (`uvm_blackwell_fault_buffer.c:32-33`) | herdado | confirmed; GB20x derived |
| D-12 | Operações de TLB do host | `uvm_hal_hopper_host_tlb_invalidate_*` (`uvm_hal.c:206-208`) | idem | acrescenta `tlb_invalidate_phys`, `tlb_flush_prefetch`, `l2_invalidate` (`uvm_hal.c:218-224`) | classe de canal B, herda as de A (`uvm_hal.c:227-229`) | confirmed; GB20x derived |

## 8. Contas conferidas

| id | Conta | Resultado |
|---|---|---|
| A-01 | Bits de VA: 1 + 9 + 9 + 9 + 8 (níveis PD4 a PD0) = 36; mais 9 (PT_SMALL 20:12) = 45; mais 12 (deslocamento de 4 KB) = 57. Com página grande: 36 + 5 (20:16) + 16 = 57 | fecha com `NUM_VA_BITS = 57` |
| A-02 | Tamanhos de página pelo bit mais baixo de cada nível: 2^12 = 4 KB, 2^16 = 64 KB, 2^21 = 2 MB, 2^29 = 512 MB, 2^38 = 256 GB; cobertura por entrada: PD3 2^47 = 128 TB, PD4 2^56 = 64 PB | fecha com os nomes do comentário e com `UVM_SIZE_1PB` (`uvm_common.h:206`) |
| A-03 | Tamanho das tabelas: PD4 2 x 8 = 16 B; PD3, PD2, PD1 512 x 8 = 4096 B; PD0 256 x 16 = 4096 B; PT_SMALL 512 x 8 = 4096 B; PT_BIG 32 x 8 = 256 B | fecha com `allocation_size_hopper` (4096 e 256) e com o comentário do nível 0 (16 B, mínimo 32 B) |
| A-04 | Deslocamentos do PDE dual: o "big" é 8 (tabela de 256 B alinhada a 256 B) e o "small" é 12 (tabela de 4 KB alinhada a 4 KB) | fecha com A-03 |
| A-05 | Entrada de falha: 8 palavras de 32 bits = 32 B; o bit `VALID` é o 31 da palavra 7 | fecha com `NVC369_BUF_SIZE = 32` |
| A-06 | PCF: 2^5 = 32 nomes no cabeçalho (`HOP-MMU:503-534`). A lista de tradução do RM tem 25 (9 privilegiadas + 16 regulares). Faltam 7, todas privilegiadas: `RW_NO_ATOMIC_CACHED_ACD`, `RW_NO_ATOMIC_UNCACHED_ACD`, `RO_ATOMIC_CACHED_ACE`, `RO_ATOMIC_CACHED_ACD`, `RO_ATOMIC_UNCACHED_ACD`, `RO_NO_ATOMIC_CACHED_ACD`, `RO_NO_ATOMIC_UNCACHED_ACD` | 25 + 7 = 32. O UVM usa `PRIVILEGE_RO_NO_ATOMIC_UNCACHED_ACD` (uma das 7) no PTE "poisoned" (`uvm_hopper_mmu.c:271`) |
| A-07 | uTLBs por GPC no código: `maxTpcPerGpcCount * 2 + 1`; o teto no Blackwell é 10 x 2 + 1 = 21, igual a `UVM_BLACKWELL_GPC_UTLB_COUNT` (RGG = 0 e LTP0 a LTP19 = 1 a 20) | fecha |
| A-08 | uTLBs da GB202 (**derived**, com entradas de fora do código): a fonte `nvidia-rtx-pro-blackwell-architecture-v1.1.md` diz 8 TPCs por GPC e 12 GPCs; se `maxTpcPerGpcCount` = 8 então 8 x 2 + 1 = 17 por GPC e 12 x 17 = 204 no chip completo (fórmula de `uvm_blackwell.c:38`). Os valores `maxTpcPerGpcCount` e `maxGpcCount` vêm do RM em tempo de execução e não aparecem no clone | não confirmado em código |
| A-09 | Largura do PDB nos dois caminhos de invalidação: registrador do RM = 28 bits (`PDB_ADDR` 31:4) + 20 bits (`UPPER_PDB_ADDR` 19:0) = 48 bits de página de 4 KB, ou 60 bits de endereço; método de host = 20 bits (`PDB_ADDR_LO` 31:12) + 27 bits (`PDB_ADDR_HI` 26:0) = 47 bits, ou 59 bits de endereço | os dois cobrem muito mais que qualquer memória física; os números diferem entre as duas interfaces |
| A-10 | Vidmem de 96 GB da placa (da fonte do whitepaper do projeto) cabe em 37 bits (2^37 = 128 GB), portanto cabe no campo de endereço de vidmem do PTE (39:12) | cruzamento entre duas fontes, derived |
| A-11 | Cobertura de VA do UVM: o diagrama `Hopper-Rubin` do UVM começa em 128 PB no topo; 2^57 B = 128 PB | fecha |

## 9. Inconsistências e conflitos dentro da fonte

| id | O que | Onde | Situação |
|---|---|---|---|
| C-01 | **conflict: true (escopo).** O arquivo `uvm_blackwell_mmu.c` lista a página de 256 GB, mas a tabela de arquiteturas liga a família GB20x (a da GB202) à MMU do Hopper, sem 256 GB. Cada afirmação vale para uma subfamília diferente | `UVM/uvm_blackwell_mmu.c:58-61` contra `UVM/uvm_hal.c:283-291` | Não resolvido no clone. Para a GB202, vale `uvm_hal.c`. Se alguém quiser afirmar "256 GB na GB202", falta fonte |
| C-02 | O comentário do GB10x diz "Page directory 1 can now hold a PTE pointing to a 256GB Page", mas o código altera `pLevels[2]`, que o diagrama do mesmo arquivo chama de PD2 [46:38]. Os nomes PD de comentários e de `pageLevelIdTag` também estão deslocados em relação ao diagrama (`pLevels[0]` = "Page directory 4" tem a etiqueta `..._PD0`) | `RM/arch/blackwell/kern_gmmu_fmt_gb10x.c:38,59-60`; `RM/arch/hopper/kern_gmmu_fmt_gh10x.c:62-68` | Parece comentário herdado da Ampere (onde o nível 2 do vetor era o PD1). Interpretação, não afirmada pelo código |
| C-03 | Largura do endereço de vidmem: o campo definido no UVM é 39:12 (40 bits), mas o comentário do "PTE envenenado" diz que o endereço precisa caber em 38 bits ("max address width of vidmem") | `UVM/uvm_hopper_mmu.c:46` contra `UVM/uvm_hopper_mmu.c:266-267` | Dois números na mesma fonte. Não resolvido |
| C-04 | No registrador de invalidação do RM, o campo `CANCEL_GPC_ID` (19:15) sobrepõe `INVAL_SCOPE` (16:15) | `SW/blackwell/gb100/dev_vm.h:363-364` | O cabeçalho não explica. Pode valer para modos diferentes de uso, mas isso é interpretação |
| C-05 | O cabeçalho define 32 PCFs de PTE válida; a tradução do RM aceita 25 | `HOP-MMU:503-534` contra `RM/arch/hopper/kern_gmmu_gh100.c:111-136` | Ver A-06. O UVM usa uma das 7 que faltam |
| C-06 | Codificação de aperture do PDB difere entre as duas interfaces de invalidação: o registrador do RM tem 1 bit (`VID_MEM` 0, `SYS_MEM` 1) e o método de host tem 2 bits (`VID_MEM` 0, `SYS_MEM_COHERENT` 2) | `SW/blackwell/gb100/dev_vm.h:328-331` contra `UVM/clc96f.h:62-64` | Não é erro: são interfaces diferentes. Registrado para evitar mistura |

## 10. Interpretações (não auditadas)

Leituras minhas. Nenhuma está escrita como fato no código.

- **I1. A GB202 usa o formato de tabela da Hopper.** Razões: G-07 (comentário do UVM), G-11 (o cabeçalho de MMU da GB202 só tem "kinds" e uma aperture) e F-11 (conjunto de páginas). A parte do RM não é verificável no clone (ver lacunas).
- **I2. Percurso de uma tradução.** Um acesso vem de um cliente (por exemplo o SM), passa por um uTLB do GPC e, se falha, vai ao TLB do hub e ao percorredor de tabelas, que lê o PDB do bloco de instância do contexto e desce 6 níveis até o PTE. O código mostra as partes (uTLB, hub, PDB, níveis) mas **não descreve o algoritmo do percorredor**. A ordem acima é a composição das partes.
- **I3. Padrão de bits do PCF (F-31).** Leitura da lista de constantes. O cabeçalho não declara o mapeamento por bit.
- **I4. Resumo do ciclo de uma falha replayable.** SM falha, a entrada de 32 B vai ao buffer, o UVM atende em lote (migra e mapeia), invalida TLB quando precisa e emite replay; se a falha é fatal, cancela e o RM reinicia o canal. Todas as etapas estão em P-20 a P-36, mas o encadeamento completo em uma frase é minha composição.
- **I5. "Sysmem via IOMMU".** O código usa endereços da API de DMA do SO (U-09); que isso seja um endereço de IOMMU (IOVA) quando há IOMMU ligado é o comportamento normal do Linux, não algo que o código afirme. O código cita "IOMMU GPA mapping" em `uvm_hal_types.h:620`.
- **I6. Sem ATS em PC comum.** Não há fato no clone sobre a GB202 numa estação x86 usar ATS. U-04 e U-05 mostram que o uso depende de plataforma e de configuração do kernel. Não afirmo nem nego.

## 11. O que a fonte NÃO cobre

- Capacidade, associatividade, política de substituição e latência de qualquer TLB, uTLB, cache de PDE ou cache do percurso (só aparecem os controles de invalidação e o tamanho de linha de 32 B).
- O algoritmo e o pipeline do percorredor de tabelas em hardware.
- Largura real do endereço físico da GB202 e o tamanho máximo de vidmem aceito (o código só traz campos e um comentário de 38 bits).
- Quantos GPCs e TPCs a GB202 tem em tempo de execução (valores vêm do RM em `rm_info`).
- Latência e custo de uma falha, ou taxa de falhas.
- Comportamento do IOMMU da CPU (Intel VT-d, AMD-Vi) e da tabela de páginas do SO; o código só usa a API de DMA.
- Se a GB202 numa estação x86 liga ATS, SVA ou HMM em um sistema típico.
- Layout de bits do bloco de instância para Hopper e Blackwell (ver lacunas).
- Políticas de escalonamento de contextos e o que acontece com o AMP (RISC-V) numa falha; a pasta `gsp` do clone não foi lida a fundo para este tema.
- Interrupções em geral. Só li o que toca falhas de página (P-24 a P-26).
- Registradores de depuração de MMU, canais e memória protegida (WPR), computação confidencial (CC) além dos pontos citados.

## 12. Lacunas (para o `architecture-inferencer` e para a próxima coleta)

Itens que precisam de arquivos que **não estão no clone**. Os nomes abaixo vêm de `#include` do próprio código lido; o caminho exato no repositório **não foi verificado**.

1. **HAL por chip da GB202 no RM.** Qual função `_GH100`, `_GB100`, `_GB10X` ou `_GH10X` o RM liga à GB202. Está em código gerado pelo NVOC (`g_kern_gmmu_nvoc.*` e afins), que o clone não tem. Sem isso, F-01 a F-06, T-01 e P-38 valem por herança (UVM) e não por prova do RM.
2. **Estruturas do formato.** `mmu/gmmu_fmt.h` e `mmu/mmu_fmt.h` (incluídos em `kern_gmmu_fmt_*.c` e `gmmu_walk.c`) e `gpu/mmu/kern_gmmu.h` (inclui `NUM_FAULT_BUFFERS`, propriedades de PDB e de página de 512 MB: `bPageSize512mbSupported`, `bHugePageSupported`, que o clone só mostra sendo zeradas em modo "cache only", `RM/kern_gmmu.c:81-82`).
3. **Layout do bloco de instância.** As macros `NV_RAMIN_*` vêm de `published/<arq>/<chip>/dev_ram.h` (por exemplo `published/volta/gv100/dev_ram.h`, incluído em `kern_gmmu_gv100.c:40`). Para Hopper e Blackwell, o clone só traz deltas (`SW/blackwell/gb202/dev_ram.h` tem 8 `#define`). Também faltam `kbusInitInstBlk` e a criação do canal (módulos `gpu/bus` e `gpu/fifo`). Não sei como o bloco de instância sinaliza o formato v3.
4. **Reinício de canal e erro robusto (RC) no caminho do PF sem SR-IOV.** Só vi o ramo do VF (`RM/kern_gmmu.c:3003-3159`). O RC depende de `kernel_rc.h` e `kernel_fifo.h`, fora do clone.
5. **Dimensionamento do buffer.** `replayableFaultBufferSize` vem de `kgmmuGetStaticInfo` (`RM/kern_gmmu.c:1246`), preenchido pelo firmware (GSP) via controle `NV2080_CTRL_CMD_INTERNAL_GMMU_GET_STATIC_INFO`. O número não aparece no clone.
6. **Página de 256 GB e de 512 MB na GB202 no lado do RM.** Só há o UVM (G-07). Falta ver se o RM habilita 512 MB (`bPageSize512mbSupported`) e o que faz com 256 GB.
7. **Campos `rm_info.gpuArch` e `gpuImplementation` da GB202.** A igualdade 0x1B0 (G-08) é numérica. Falta o código que preenche `rm_info` a partir do RM (fora do clone).
8. **Contagem de GPCs e TPCs** que alimenta `utlb_count` (A-08) vem de `rm_info.maxGpcCount` e `maxTpcPerGpcCount`; sem fonte no clone.
9. **Detalhes de ATS na GB202:** `non_pasid_ats_enabled` e `ats_supported` são preenchidos a partir de informações do RM (`gpu_platform_info`), fora do clone.
10. **Cabeçalhos de hardware `dev_mmu.h` do Blackwell completo:** `SW/blackwell/gb100/` não tem `dev_mmu.h` (só `gb202/` e `gb20b/`, ambos minúsculos). Os campos v3 vêm do Hopper. Se for preciso citar "campo X da Blackwell", falta o arquivo.
11. **Fonte oficial de hardware** (manual da NVIDIA) para tamanho de TLB, latência e algoritmo do percorredor. O código aberto não cobre. O guia de programação CUDA pode cobrir o comportamento visível ao programador (memória unificada), mas não os números internos.
