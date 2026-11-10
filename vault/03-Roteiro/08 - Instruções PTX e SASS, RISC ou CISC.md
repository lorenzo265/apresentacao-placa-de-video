---
tipo: secao
status: pronto
secao: Instruções PTX e SASS, RISC ou CISC
ordem: 8
nivel: chip
part_id: chip.isa
procedencia_esperada: derived
itens_enunciado: [conjunto de instruções, CISC/RISC]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - PTX ISA]]", "[[NVIDIA - CUDA Binary Utilities]]", "[[NVIDIA - Compute capability das GPUs CUDA]]", "[[Jia et al. - Dissecting the NVIDIA Volta GPU]]", "[[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]", "[[Ampere - Demystifying the Nvidia Ampere Architecture]]"]
---
# 08 - Instruções PTX e SASS, RISC ou CISC

## Objetivo
Apresentar o conjunto de instruções da GPU em suas duas camadas (PTX e SASS), mostrar exemplos de kernel compilado e discutir, com critérios explícitos, se é RISC ou CISC.

## Itens do enunciado cobertos
- conjunto de instruções
- CISC/RISC

## Já confirmado na fonte primária
- A placa tem **compute capability 12.0**, alvo `sm_120` ([[NVIDIA - Compute capability das GPUs CUDA|cuda-gpus]]).
- **PTX** é uma máquina virtual e ISA de baixo nível, estável entre gerações, traduzida na instalação para o conjunto de instruções do hardware ([[NVIDIA - PTX ISA|PTX ISA]], seções 1.1 e 1.2). O documento do PTX não usa o termo SASS; o Binary Utilities chama o código do hardware de "CUDA assembly".
- O PTX se descreve como **máquina load-store**: os operandos das instruções aritméticas ficam em registradores, e `ld` e `st` movem dados entre memória e registradores (seção 6.2). Toda instrução pode ter um predicado de guarda `@p` (seção 9.3).
- **SASS:** a referência de instruções do CUDA Binary Utilities 13.4 cobre a compute capability 12.0 (seção 4.4). Famílias de opcodes: ponto flutuante (FADD, FFMA, FMUL), inteiros (IMAD, IADD3, LOP3), memória (LDG, LDS, STG, STS), controle (BRA, CALL, RET, EXIT, BSSY, BSYNC), predicados (PLOP3, PSETP) e matrizes e cópias assíncronas (HMMA, QMMA, OMMA, UTMALDG, UTCHMMA) ([[NVIDIA - CUDA Binary Utilities|Binary Utilities]]).
- **Largura da instrução: 16 bytes (128 bits).** O apêndice do formato JSON do `nvdisasm` diz "The instruction size is 16 bytes". O corpo das seções 2 a 4 não a declara.
- **Operando de constante direto em instrução aritmética:** os exemplos da seção 3.1.1 do Binary Utilities mostram `IMAD R0, R0, c[0x0][0x0], R3` e `ISETP.GE.AND P0, PT, R0, c[0x0][0x170], PT`. A arquitetura desse exemplo não é declarada.
- O whitepaper cita **RISC-V** só para o AMP, o escalonador de contextos da GPU ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 25).

## Observado com as ferramentas oficiais (experimento do grupo)
Compilamos kernels em PTX para `sm_120` com o `ptxas` 12.9 e desmontamos com o `nvdisasm` 13.4, sem GPU. Arquivos e comandos em `harness/examples/saxpy/` e `harness/examples/mma/`.
- **Largura fixa:** as 32 instruções do SAXPY ficam em endereços que avançam sempre de 0x10 em 0x10, ou seja, 16 bytes por instrução, exibidos como duas palavras de 64 bits. Isto concorda com o apêndice do Binary Utilities.
- **Memória:** o acesso à global usa `LDG` e `STG`; as constantes entram por `LDC` e `LDCU`. Neste kernel nenhuma instrução aritmética tem endereço de memória como operando, mas elas aceitam **imediatos** (`IMAD.WIDE R2, R7, 0x4, R2`).
- **Parâmetros do kernel no banco de constantes 0** (`c[0x0][...]`), por exemplo o ponteiro `x` em `c[0x0][0x380]`.
- **Predicação:** `ISETP` escreve `P0` e `@P0 EXIT` encerra as threads fora do vetor.
- **Uma instrução de matriz por warp:** `mma.sync` em PTX virou `HMMA.16816.F32` (FP16) e `QMMA.16832.F32.E4M3.E4M3` (FP8), 2.048 e 4.096 multiplicações-acumulações por instrução.
- **Registradores:** 10 por thread, 0 de spill, nos dois exemplos.
- **Contagem:** 20 instruções PTX viram 19 úteis em SASS: o `cvta` some (−2), `mul.wide` mais dois `add.s64` viram duas `IMAD.WIDE` (−1) e aparecem duas instruções sem par no PTX (+2): `LDC R1, c[0x0][0x37c]` e `LDCU.64 UR4, c[0x0][0x358]`. A função delas não é documentada. Nossa hipótese (`inferred`) é que a segunda carrega o descritor de memória usado em `desc[UR4]`.

> [!note] Alcance
> São kernels pequenos. Ilustram o formato, mas não provam regras para toda a ISA.

## Derivado de geração anterior ou GPU irmã
- Na **Volta**, cada instrução é uma palavra de 128 bits que inclui a informação de controle de escalonamento: ao menos 91 bits de instrução, ao menos 23 de controle e 14 aparentemente sem uso. O opcode tem de 10 a 13 bits e a predicação usa 4 bits ([[Jia et al. - Dissecting the NVIDIA Volta GPU|Jia et al.]], capítulo 2, p. 11, e seção 2.3). O tamanho de 128 bits se mantém em `sm_120`, mas o uso dos bits de controle em `sm_120` não está documentado.
- Os operandos na Volta podem ser registradores, **endereços de memória (constante, compartilhada ou global)** ou imediatos (seção 2.3).
- Na RTX 5080 (GB203, mesma família), o `mma.sync` do PTX vira `QMMA` para FP8 e FP6, e também para FP4 sem escala. `OMMA` só foi observado no teste com escala por bloco ([[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture|Jarmusch et al.]], seção V-B).
- Na A100 (Ampere), o `mad.rn.f32` e o `fma.rn.f32` do PTX viram `FFMA`, e o `wmma` vira `HMMA.16816` ([[Ampere - Demystifying the Nvidia Ampere Architecture|artigo da Ampere]]): o mnemônico `HMMA.16816` atravessa gerações.

## RISC ou CISC? (análise do grupo)
A NVIDIA não classifica o SASS como RISC ou CISC. A classificação abaixo vale para o **SASS de `sm_120`**, a camada de hardware. O PTX é outra camada: é a camada estável, enquanto o SASS muda a cada geração.

| Critério clássico | O que as fontes mostram | Sugere |
|---|---|---|
| Instruções de largura fixa | 16 bytes em todas as instruções (documentação oficial e experimento em `sm_120`) | RISC |
| Acesso à memória só por carga e armazenamento | PTX é load-store. No SASS, global e compartilhada passam por `LDG`/`STG`/`LDS`/`STS`, mas há ressalvas. (1) Instruções aritméticas aceitam operando direto do banco de constantes no exemplo da seção 3.1.1 do Binary Utilities, cuja arquitetura não é declarada; Huerta et al. confirmam isso na Ampere. No nosso código de `sm_120` isso não aparece. Fica `derived`. (2) A lista oficial da Blackwell tem instruções que copiam **de memória para memória**: `LDGSTS` ("Asynchronous Global to Shared Memcopy") e `UTMALDG` ("Tensor Load from Global to Shared Memory"). A NVIDIA classifica a `LDGSTS` como instrução de carga e armazenamento. (3) Não contam como evidência: `UBLKCP` ("Bulk Data Copy"), `UMEMSETS` ("Initialize Shared Memory"), `ATOMG` e `REDG`: a descrição oficial tem poucas palavras e não basta para afirmar como acessam a memória | regra RISC, com a `LDGSTS` e a `UTMALDG` como exceções |
| Modos de endereçamento | `desc[UR4][R2.64]` (descritor mais par de registradores), `c[banco][deslocamento]` e imediatos. Não levantamos a lista completa | não determinado |
| Registradores | Banco físico de 256 KB por SM, 65.536 registradores de 32 bits (derivado), compartilhado entre os warps. O limite visível por thread é 255 (Blackwell Tuning Guide 13.5, 1.4.1.1) | RISC |
| Instruções que fazem muito trabalho | `HMMA` e `QMMA` fazem 2.048 e 4.096 multiplicações-acumulações por instrução (conta nossa). A lista oficial tem ainda `TEX` ("Texture Fetch"), `MUFU` ("FP32 Multi Function Operation"), `DECOMPRESS` ("Decompress a vector") e `SPARSIFY` ("Generate metadata and compress a vector"). Porém "reduzido" em RISC fala da simplicidade de cada instrução (formato fixo, poucos modos), e há ISAs RISC com extensões vetoriais e matriciais | afasta do RISC clássico; típico de acelerador |
| Tamanho do conjunto | 258 mnemônicos em 13 categorias na seção "Blackwell and Rubin Instruction Set" (duas contagens independentes sobre a página, com o mesmo resultado) | neutro: o número de instruções não define RISC |
| Escalonamento exposto ao compilador | Na Volta, ao menos 23 bits por instrução são de controle (esperas, barreiras, reuso). O compilador decide parte do escalonamento | afasta do RISC clássico e lembra VLIW (observação nossa) |
| Microcódigo | nenhuma informação pública | não determinado |

**Conclusão (`inferred`, análise do grupo; aprovada pelo humano em 2026-11-10):** o SASS é **RISC no formato e na regra geral, com extensões de acelerador**. Não é RISC puro nem CISC.

- A favor de RISC: instrução de largura fixa (128 bits), acesso à memória global e compartilhada por carga e armazenamento como regra, muitos registradores, poucos modos de endereçamento visíveis.
- Contra o RISC clássico: cópia assíncrona de memória para memória (`LDGSTS`, `UTMALDG`); instruções que fazem muito trabalho de uma vez (`HMMA` e `QMMA` multiplicam um bloco de matriz por warp; `TEX` busca e filtra textura).
- Fora da dicotomia: o compilador grava na instrução o controle de escalonamento, o que lembra VLIW.

Frase para o seminário: "Pelo formato é RISC: instrução de tamanho fixo, memória acessada por carga e armazenamento como regra, até 255 registradores por thread. Mas o conjunto tem instruções próprias de acelerador: busca de textura, multiplicação de um bloco de matriz por warp e cópia assíncrona da memória global para a compartilhada. A NVIDIA não classifica o SASS; esta é a análise do grupo."

O artigo entregue em 2026-11-09 concluiu "RISC" com base no exemplo SAXPY. A conclusão continua de pé como regra geral; o seminário a aprofunda com a lista completa de instruções.

> [!note] Argumentos ainda sem fonte registrada
> ISAs RISC atuais também têm operações atômicas de leitura, operação e escrita, e algumas têm instruções de cópia de memória. Se isso for dito no seminário, a fonte (especificação da ISA citada) precisa ser registrada antes. Sem a fonte, a frase não entra.

Já o AMP, o processador de gerenciamento da GPU, é RISC-V, ou seja, uma ISA RISC por projeto.

> [!note] Fora da tabela
> A latência não entra como critério porque é propriedade da microarquitetura, não da ISA. Para referência: instruções INT32 e FP32 levam 4 ciclos na GB203, mas FP64 leva cerca de 63,6 ciclos ([[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture|Jarmusch et al.]], Tab. III).

## A levantar
- Levantar os modos de endereçamento (a contagem de 258 mnemônicos foi fechada em 2026-11-09).
- Ancorar a semântica de `ATOMG` e `REDG` nas instruções `atom` e `red` do PTX.
- Para que serve o ciclo `BRA` após o último `EXIT` e quais campos de controle `sm_120` usa. A Volta tem descrição, `sm_120` não.
- Limite de registradores por thread (guia CUDA).
- Documentação do caminho uniforme (registradores `UR`). A tabela 4.4 descreve `LDCU` como carga de constante para um registrador uniforme e `S2UR` como cópia de registrador especial para um registrador uniforme, mas isso dá o nome, não o funcionamento.
- Ler o artigo da Hopper (arXiv 2501.12084).

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - PTX ISA]]
- [[NVIDIA - CUDA Binary Utilities]]
- [[NVIDIA - Compute capability das GPUs CUDA]]
- [[Jia et al. - Dissecting the NVIDIA Volta GPU]]
- [[Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture]]
- [[Ampere - Demystifying the Nvidia Ampere Architecture]]
- Exemplos compilados: `harness/examples/saxpy-cu/` (o do artigo, reproduzido), `harness/examples/saxpy/` e `harness/examples/mma/`
- Auditoria: `harness/qa/fact-check-isa.md`

## No viewer
- Nível: chip (nível 4, conceitos). Animação sugerida: uma instrução PTX virando SASS, com a palavra de 128 bits aparecendo.

## Procedência
> [!warning]
> Largura de 128 bits e lista de opcodes: `confirmed` (documentação oficial mais experimento). Campos de controle e modos de endereçamento: `derived` da Volta. A classificação RISC ou CISC é análise do grupo (`inferred`) e deve ser apresentada como tal.

Anterior: [[07 - Registradores]] | Próxima: [[09 - Hierarquia de memória e caches]]
