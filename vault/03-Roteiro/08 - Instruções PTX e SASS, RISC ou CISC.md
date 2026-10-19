---
tipo: secao
status: rascunho
secao: Instruções PTX e SASS, RISC ou CISC
ordem: 8
nivel: chip
part_id: chip.isa
procedencia_esperada: derived
itens_enunciado: [conjunto de instruções, CISC/RISC]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - PTX ISA]]", "[[NVIDIA - CUDA Binary Utilities]]", "[[NVIDIA - Compute capability das GPUs CUDA]]", "[[Jia et al. - Dissecting the NVIDIA Volta GPU]]", "[[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]"]
---
# 08 - Instruções PTX e SASS, RISC ou CISC

## Objetivo
Apresentar o conjunto de instruções da GPU em suas duas camadas (PTX e SASS), mostrar um exemplo de kernel compilado e discutir, com critérios explícitos, se é RISC ou CISC.

## Itens do enunciado cobertos
- conjunto de instruções
- CISC/RISC

## Já confirmado na fonte primária
- A placa tem **compute capability 12.0**, alvo `sm_120` ([[NVIDIA - Compute capability das GPUs CUDA|cuda-gpus]]).
- **PTX** é uma máquina virtual e ISA de baixo nível, estável entre gerações, traduzida para o conjunto de instruções do hardware ([[NVIDIA - PTX ISA|PTX ISA]], introdução).
- O PTX se descreve como **máquina load-store**: os operandos das instruções aritméticas ficam em registradores, e `ld` e `st` movem dados entre memória e registradores (seção 6.2). Toda instrução pode ter um predicado de guarda `@p` (seção 9.3).
- **SASS**: a referência de instruções do CUDA Binary Utilities 13.4 cobre a compute capability 12.0 (seção 4.4). Famílias de opcodes: ponto flutuante (FADD, FFMA, FMUL), inteiros (IMAD, IADD3, LOP3), memória (LDG, LDS, STG, STS), controle (BRA, CALL, RET, EXIT, BSSY, BSYNC), predicados (PLOP3, PSETP) e matrizes e cópias assíncronas (HMMA, QMMA, OMMA, UTMALDG, UTCHMMA) ([[NVIDIA - CUDA Binary Utilities|Binary Utilities]]).
- O documento do Binary Utilities **não declara** a largura da instrução nem define formalmente o SASS.
- O único processador da GPU que o whitepaper identifica pela ISA é o AMP, **RISC-V** ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 25).

## Observado com as ferramentas oficiais (experimento do grupo)
Compilamos um kernel SAXPY em PTX para `sm_120` com o `ptxas` 12.9 e desmontamos com o `nvdisasm` 13.4, sem GPU. Arquivos e comandos em `harness/examples/saxpy/`.
- **Largura fixa:** as 32 instruções do resultado ficam em endereços que avançam sempre de 0x10 em 0x10, ou seja, **16 bytes (128 bits) por instrução**, exibidos como duas palavras de 64 bits.
- **Memória só por instruções próprias:** acesso à global por `LDG` e `STG`, constantes por `LDC` e `LDCU`. As instruções aritméticas (`IMAD`, `FFMA`, `ISETP`) têm só registradores como operandos neste kernel.
- **Parâmetros do kernel no banco de constantes 0** (`c[0x0][...]`).
- **Predicação:** `ISETP` escreve `P0` e `@P0 EXIT` encerra as threads fora do vetor.
- **Menos instruções que no PTX:** 20 em PTX viram 19 úteis em SASS, porque `cvta` some e `mul.wide` mais `add.s64` viram uma `IMAD.WIDE`.
- **Registradores:** 10 por thread, 0 de spill.

> [!note] Alcance
> É um kernel pequeno. Ele ilustra o formato, mas não prova regras para toda a ISA.

## Derivado de geração anterior ou GPU irmã
- Na **Volta**, cada instrução é uma palavra de 128 bits que inclui a informação de controle de escalonamento: ao menos 91 bits de instrução, ao menos 23 de controle e 14 aparentemente sem uso. O opcode tem de 10 a 13 bits e a predicação usa 4 bits ([[Jia et al. - Dissecting the NVIDIA Volta GPU|Jia et al.]], seções 1, 2.3). O experimento acima mostra que o tamanho de 128 bits se mantém em `sm_120`.
- Na Volta, os operandos podem ser registradores, **endereços de memória (constante, compartilhada ou global)** ou imediatos (seção 2.3). Não vimos operando de constante em instrução aritmética no nosso kernel.
- Na RTX 5080 (GB203, mesma família), o `mma.sync` do PTX vira `QMMA` (FP8, FP6) e `OMMA` (FP4 com escala), e instruções INT32 e FP32 têm latência de 4 ciclos ([[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture|Jarmusch et al.]], seções V-B e IV).

## RISC ou CISC? (análise do grupo)
A NVIDIA não classifica o SASS como RISC ou CISC. Usamos critérios clássicos e as evidências acima.

| Critério clássico | O que as fontes mostram | Sugere |
|---|---|---|
| Instruções de largura fixa | 16 bytes em todas as instruções do nosso kernel `sm_120`; 128 bits na Volta | RISC |
| Memória só por carga e armazenamento | PTX é load-store; no SASS, `LDG`/`STG` separados e aritmética só com registradores no nosso kernel | RISC (a confirmar em outros kernels) |
| Muitos registradores | 65.536 registradores de 32 bits por SM | RISC |
| Latência regular e curta nas operações simples | 4 ciclos para INT32 e FP32 na GB203 | RISC |
| Execução condicional por predicado em toda instrução | 4 bits de predicação (Volta) | neutro |
| Instruções que fazem muito trabalho | `HMMA`, `QMMA`, `OMMA` (matrizes), `UTMALDG` (cópia assíncrona) | afasta de um conjunto "reduzido" |
| Microcódigo | nenhuma informação pública | não determinado |

**Conclusão provisória (`inferred`):** pelo formato, o SASS se comporta como RISC (largura fixa, carga/armazenamento, muitos registradores), mas com instruções especializadas pesadas, próprias de uma arquitetura de domínio específico (matrizes e cópias). A distinção clássica entre RISC e CISC é menos nítida nesse tipo de arquitetura. Já o AMP, o processador de gerenciamento da GPU, é RISC-V, ou seja, RISC por definição.

## A levantar
- Compilar um kernel com `mma` para mostrar `HMMA`, `QMMA` ou `OMMA` em `sm_120`.
- Verificar se alguma instrução aritmética aceita operando de constante em `sm_120` (no SAXPY as constantes entram por `LDC`/`LDCU`).
- Os campos de controle da segunda palavra de 64 bits não são documentados para `sm_120`. Só existe descrição para a Volta.
- Confirmar na documentação o que é o caminho uniforme (registradores `UR`).
- Ler os artigos de Ampere (arXiv 2208.11174) e Hopper (arXiv 2501.12084) para o mapeamento de PTX para SASS.

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - PTX ISA]]
- [[NVIDIA - CUDA Binary Utilities]]
- [[NVIDIA - Compute capability das GPUs CUDA]]
- [[Jia et al. - Dissecting the NVIDIA Volta GPU]]
- [[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]
- Exemplo compilado: `harness/examples/saxpy/`

## No viewer
- Nível: chip (nível 4, conceitos). Animação sugerida: uma instrução PTX virando SASS, com a palavra de 128 bits aparecendo.

## Procedência
> [!warning]
> O SASS não tem documentação oficial completa. A largura de 128 bits em `sm_120` foi **observada** nas ferramentas oficiais, e o resto do formato vem da Volta (derivado). A classificação RISC ou CISC é análise do grupo (`inferred`).

Anterior: [[07 - Registradores]] | Próxima: [[09 - Hierarquia de memória e caches]]
