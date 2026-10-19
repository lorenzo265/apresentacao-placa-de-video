# Fontes de conjunto de instruções (rodada de 2026-10-19)

Excertos curtos e números, com a localização na fonte. Os PDFs não são versionados.
Leitura feita por resumo automático (WebFetch) e por texto extraído de PDF (`pdftotext`). Os trechos marcados com [auditar] foram repassados ao `fact-checker`.

## 1. NVIDIA, PTX ISA 9.4
URL: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html (acessado em 2026-10-19; `confirmed`)

| Dado | Trecho ou valor | Seção |
|---|---|---|
| Definição | "a low-level parallel thread execution virtual machine and instruction set architecture (ISA)" | Introdução [auditar] |
| Tradução | "PTX programs are translated at install time to the target hardware instruction set" | Introdução [auditar] |
| Estabilidade | "Provide a stable ISA that spans multiple GPU generations" | Introdução [auditar] |
| Load-store | "PTX describes a load-store machine, so operands for ALU instructions must all be in variables declared in the .reg register state space" | 6.2 Source Operands [auditar] |
| ld/st | "Instructions ld and st move data from/to addressable state spaces to/from registers" | 6.2 [auditar] |
| Predicado de guarda | "All instructions have an optional guard predicate which controls conditional execution of the instruction" | 9.3 [auditar] |
| Registradores | escalares de 8, 16, 32, 64 ou 128 bits; predicados de 1 bit; não endereçáveis | State spaces [auditar] |
| Warp | "Typically, a warp has 32 threads"; tamanho dependente de máquina | Modelo de máquina [auditar] |

Não confirmado nos trechos lidos: `sm_100` e `sm_120` como alvos (`.target`), número máximo de registradores por thread (o PTX remete ao guia de programação CUDA).

## 2. NVIDIA, CUDA Binary Utilities 13.4
URL: https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html (acessado em 2026-10-19; `confirmed`)

| Dado | Valor | Seção |
|---|---|---|
| Cobertura | seção "Blackwell and Rubin Instruction Set" para compute capability 10.0, 10.3, 10.7, 11.0 e 12.0 | 4.4 [auditar] |
| Opcodes de ponto flutuante | FADD, FFMA, FMUL, FMNMX3, HMMA, DMMA, OMMA, QMMA | 4.4 [auditar] |
| Opcodes de inteiros | IMAD, IADD3, LOP3, SHF, POPC, IDP4A, IMMA | 4.4 [auditar] |
| Opcodes de memória | LDG, LDS, LDSM, LDGSTS, STG, STS, STAS, ATOMG, REDG | 4.4 [auditar] |
| Opcodes de controle | BRA, CALL, RET, EXIT, BSSY, BSYNC, WARPSYNC | 4.4 [auditar] |
| Opcodes de predicado | PLOP3, PSETP, P2R, R2P | 4.4 [auditar] |
| Tensor e cópia assíncrona | UTMALDG, UTMASTG, UBLKCP, LDTM, STTM, UTCCP, UTCHMMA, UTCQMMA | 4.4 [auditar] |
| Largura da instrução | **não declarada**; o exemplo de cuobjdump mostra 2 palavras de 64 bits em hex por instrução (ex.: `/* 0x0000df00ff017b82 */` e `/* 0x000fe20000000800 */`) | exemplos [auditar] |
| Definição de SASS | **não declarada**; só aparece "CUDA assembly" e a opção `-sass` | opções |

## 3. NVIDIA, CUDA GPUs (compute capability)
URL: https://developer.nvidia.com/cuda-gpus (acessado em 2026-10-19; `confirmed`)
- RTX PRO 6000 Blackwell Workstation Edition: **12.0**. GeForce RTX 5090: 12.0. RTX 6000 Ada: 8.9. [auditar]

## 4. Jia et al., Volta (arXiv 1804.06826)
URL: https://arxiv.org/abs/1804.06826 (`derived`: Volta, 2018)
Texto extraído do PDF com `pdftotext`. Localização por seção do próprio artigo.

| Dado | Trecho ou valor | Seção |
|---|---|---|
| Largura | "Volta uses one 128-bit word to encode each instruction together with its corresponding control information" | 1, Instructions [auditar] |
| Antes da Volta | uma palavra de 64 bits por instrução e outra de 64 bits de controle para várias instruções | 1 [auditar] |
| Bits | ao menos 91 de instrução, ao menos 23 de controle, 14 aparentemente não usados | 1 [auditar] |
| Opcode | 10 a 13 bits, nos bits menos significativos da primeira metade de 64 bits | 2.3 [auditar] |
| Operandos | registradores (gerais, especiais, predicado), endereços de memória (constante, compartilhada, global) ou imediato | 2.3 [auditar] |
| Predicação | 4 bits: negação e índice de 3 bits | 2.3 [auditar] |
| Partições | quatro blocos de processamento; `scheduler id = warp id % 4` | 2.2 [auditar] |
| Banco de registradores | dois bancos de 64 bits; conflito de banco quando os 3 fontes da FFMA caem no mesmo banco | 1 [auditar] |

## 5. Jarmusch et al., Blackwell GB203 (arXiv 2507.10789)
URL: https://arxiv.org/abs/2507.10789 (`derived`: RTX 5080, GB203, não GB202)

| Dado | Valor | Onde |
|---|---|---|
| Partições do SM | 4 | seção IV [auditar] |
| Latência INT32 e FP32 | 4 ciclos (verdadeira) | Tab. III [auditar] |
| L1 | 30 a 40 ciclos | seção VI-B [auditar] |
| L2 (acerto) | cerca de 358 ciclos | seção VI-C [auditar] |
| Memória global | cerca de 876,7 ciclos | seção VI-D [auditar] |
| Registradores e L1 por SM | 256 KB e 128 KB | Tab. II [auditar] |
| Mapeamento de matriz | `mma.sync`: HMMA (Hopper); QMMA (FP8, FP6) e OMMA (FP4 com escala) na Blackwell | seção V-B [auditar] |

## Lacunas desta rodada
- Largura da instrução no `sm_120` não confirmada por fonte oficial. Depende de um `nvdisasm` real (tentativa em andamento).
- Modos de endereçamento do SASS e operandos de constante: só a menção do artigo da Volta.
- Ampere (arXiv 2208.11174), Hopper (arXiv 2501.12084) e B200 (arXiv 2512.02189) não foram lidos.
