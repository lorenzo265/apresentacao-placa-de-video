# Fontes de conjunto de instruções (rodada de 2026-10-19)

Excertos curtos e números, com a localização na fonte. Os PDFs não são versionados.
Leitura feita por resumo automático (WebFetch) e por texto extraído de PDF (`pdftotext`). Tudo o que está marcado [auditado] foi reaberto e conferido de forma independente pelo `fact-checker` em 2026-10-19 (relatório em `harness/qa/fact-check-isa.md`).

## 1. NVIDIA, PTX ISA 9.4
URL: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html (acessado em 2026-10-19; `confirmed`)

| Dado | Trecho ou valor | Seção |
|---|---|---|
| Definição | "a low-level parallel thread execution virtual machine and instruction set architecture (ISA)" | 1. Introduction [auditado] |
| Tradução | "PTX programs are translated at install time to the target hardware instruction set" | 1.1 (variante em 2.1) [auditado] |
| Estabilidade | "Provide a stable ISA that spans multiple GPU generations" | 1.2 Goals of PTX [auditado] |
| Load-store | "PTX describes a load-store machine, so operands for ALU instructions must all be in variables declared in the .reg register state space" | 6.2 Source Operands [auditado] |
| ld/st | "Instructions ld and st move data from/to addressable state spaces to/from registers" | 6.2 [auditado] |
| Predicado de guarda | "All instructions have an optional guard predicate which controls conditional execution of the instruction" | 9.3 (também 4.3.2) [auditado] |
| Registradores | "aside from predicate registers which are 1-bit, scalar registers have a width of 8-, 16-, 32-, 64-, or 128-bits"; "not fully addressable, i.e., it is not possible to refer to the address of a register" | 5.1.1 [auditado] |
| Warp | "Typically, a warp has 32 threads" (2.2.1); "all target architectures have a WARP_SZ value of 32" (4.5.1) | 2.2.1 e 4.5.1 [auditado] |
| Versão | "Parallel Thread Execution ISA Version 9.4" | título e 1.3 [auditado] |

Não confirmado nos trechos lidos: `sm_120` como alvo (`.target`) dentro deste documento (aparecem `sm_100` e `sm_100a`); número máximo de registradores por thread (o PTX remete ao guia de programação CUDA). Não foi lido o bloco 300.000 a 400.000.
O documento do PTX nunca usa o termo "SASS".

## 2. NVIDIA, CUDA Binary Utilities 13.4
URL: https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html (acessado em 2026-10-19; `confirmed`)

| Dado | Valor | Seção |
|---|---|---|
| Cobertura | "The Blackwell and Rubin architectures (Compute Capability 10.0, 10.3, 10.7, 11.0, and 12.0) have the following instruction set format:" | 4.4 [auditado] |
| Opcodes de ponto flutuante | FADD, FFMA, FMUL, FMNMX3, HMMA, DMMA, OMMA, QMMA | 4.4 [auditado] |
| Opcodes de inteiros | IMAD, IADD3, LOP3, SHF, POPC, IDP4A, IMMA | 4.4 [auditado] |
| Opcodes de memória | LDG, LDS, LDSM, LDGSTS, STG, STS, STAS, ATOMG, REDG | 4.4 [auditado] |
| Opcodes de controle | BRA, CALL, RET, EXIT, BSSY, BSYNC, WARPSYNC | 4.4 [auditado] |
| Opcodes de predicado | PLOP3, PSETP, P2R, R2P | 4.4 [auditado] |
| Tensor e cópia assíncrona | UTMALDG, UTMASTG, UBLKCP, LDTM, STTM, UTCCP, UTCHMMA, UTCQMMA | 4.4 [auditado] |
| Uniforme | `LDCU`: carga de constante para registrador uniforme; `S2UR`: registrador especial para registrador uniforme | 4.4 [auditado] |
| **Largura da instrução** | "The instruction size is 16 bytes." (amostra marcada "SM90 (16 bytes instruction)"). O corpo das seções 2 a 4 não declara a largura | apêndice 7.1, formato JSON [auditado e conferido pelo grupo] |
| Exemplo de desmontagem | duas palavras de 64 bits por instrução, ex.: `LDC R1, c[0x0][0x37c] ; /* 0x0000df00ff017b82 */` (compilado para `sm_100`) | 2.1.1 [auditado] |
| **Operando de constante em aritmética** | `IMAD R0, R0, c[0x0][0x0], R3 ;` e `ISETP.GE.AND P0, PT, R0, c[0x0][0x170], PT ;` (arquitetura do exemplo não declarada) | 3.1.1 [auditado e conferido pelo grupo] |
| Definição de SASS | **não declarada**; só aparece "CUDA assembly" e a opção `-sass` | opções |

## 3. NVIDIA, CUDA GPUs (compute capability)
URL: https://developer.nvidia.com/cuda-gpus (acessado em 2026-10-19; `confirmed`)
- RTX PRO 6000 Blackwell Workstation Edition: **12.0**. Max-Q Workstation Edition e Server Edition: 12.0. GeForce RTX 5090: 12.0. RTX 6000 Ada: 8.9. [auditado]

## 4. Jia et al., Volta (arXiv 1804.06826)
URL: https://arxiv.org/abs/1804.06826 (`derived`: Volta, 2018)
Texto extraído do PDF com `pdftotext`. Localização conforme o próprio artigo.

| Dado | Trecho ou valor | Seção |
|---|---|---|
| Largura | "Volta uses one 128-bit word to encode each instruction together with its corresponding control information" | capítulo 2, abertura (p. 11) [auditado] |
| Antes da Volta | uma palavra de 64 bits por instrução e outra de 64 bits de controle para várias instruções | capítulo 2 [auditado] |
| Bits | ao menos 91 de instrução, ao menos 23 de controle, 14 aparentemente não usados | capítulo 2 [auditado] |
| Opcode | 10 a 13 bits, nos bits menos significativos da primeira metade de 64 bits | 2.3 [auditado] |
| Operandos | registradores (gerais, especiais, predicado), endereços de memória (constante, compartilhada, global) ou imediato | 2.3 [auditado] |
| Predicação | 4 bits: negação e índice de 3 bits | 2.3 [auditado] |
| Partições | quatro blocos de processamento; `scheduler id = warp id % 4` | 2.2 [auditado] |
| Banco de registradores | dois bancos de 64 bits (banco = índice mod 2); conflito quando os 3 fontes da FFMA caem no mesmo banco; cache de reuso | capítulo 1 (p. 6 a 7), 2.1 e 3.5 (p. 30) [auditado] |

## 5. Jarmusch et al., Blackwell GB203 (arXiv 2507.10789)
URL: https://arxiv.org/abs/2507.10789 (`derived`: RTX 5080, GB203, não GB202)

| Dado | Valor | Onde |
|---|---|---|
| Partições do SM | 4 (unidades INT32 e FP32 unificadas) | seções IV e IV-B [auditado] |
| Latência INT32 e FP32 | 4 ciclos (verdadeira); **FP64: 63,57** | Tab. III [auditado] |
| L1 | 30 a 40 ciclos | seção VI-B [auditado] |
| L2 (acerto) | cerca de 358 ciclos | seção VI-C [auditado] |
| Memória global | cerca de 876,7 ciclos | seção VI-D [auditado] |
| Registradores e L1 por SM | 256 KB e 128 KB | Tab. II [auditado] |
| Mapeamento de matriz | `mma.sync`: HMMA (Hopper); QMMA para FP8 e FP6 e, como alternativa do software atual, também para FP4 sem escala; OMMA apenas no teste com escala por bloco `ue8m0`, cujas entradas o artigo não especifica | seção V-B [auditado] |
| Observação | a legenda da Tab. V diz que e8m0 "was not tested", o que contradiz o texto da seção V-B | Tab. V |

## 6. Ampere (arXiv 2208.11174), leitura por resumo automático, não auditada
- SASS "closed-source and compatible only within each architecture family"; `mad`/`fma` de f32 viram `FFMA`; `wmma` (m16n16k16, f16) vira 2 × `HMMA.16816.F16`. A100.

## Lacunas desta rodada
- Limite de registradores por thread (guia CUDA).
- Lista completa e contagem dos opcodes de `sm_120`.
- Funções de `LDC R1, c[0x0][0x37c]` e `LDCU.64 UR4, c[0x0][0x358]` no SAXPY (não documentadas).
- Hopper (arXiv 2501.12084) e B200 (arXiv 2512.02189) não foram lidos.
