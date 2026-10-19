---
tipo: fonte
status: pronto
secao: Instruções
autor: NVIDIA
link: https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html
acessado: 2026-10-19
procedencia: confirmed
---
# NVIDIA - CUDA Binary Utilities

## Dados da fonte
- **Título:** CUDA Binary Utilities, versão 13.4 (documentação do CUDA).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-19.
- **Alcance da leitura:** cerca de 112.000 caracteres, lidos por resumo automático, inclusive o apêndice final do formato JSON.

## Pontos que servem à apresentação
- É a referência oficial das ferramentas `cuobjdump` e `nvdisasm`, que mostram o SASS, e traz uma **referência de instruções por arquitetura**. A seção 4.4, "Blackwell and Rubin Instruction Set", cobre as capacidades de computação 10.0, 10.3, 10.7, 11.0 e 12.0. A placa deste trabalho é a 12.0 ([[NVIDIA - Compute capability das GPUs CUDA]]).
- A lista traz só nomes de opcodes e descrições curtas, não a codificação em bits. Famílias que aparecem: ponto flutuante (FADD, FFMA, FMUL, HMMA, DMMA, QMMA, OMMA), inteiros (IMAD, IADD3, LOP3, SHF, IMMA), memória (LDG, LDS, LDSM, STG, STS, atômicas), controle (BRA, CALL, RET, EXIT, BSSY, BSYNC, WARPSYNC), predicados (PLOP3, PSETP) e operações de tensor e cópia assíncrona (UTMALDG, UTMASTG, UTCHMMA). Serve a [[08 - Instruções PTX e SASS, RISC ou CISC]].
- **Largura da instrução: 16 bytes (128 bits).** O corpo das seções 2 a 4 não a declara, mas o apêndice do formato JSON do `nvdisasm` diz: "The instruction size is 16 bytes" (a amostra está marcada "SM90 (16 bytes instruction)"). Os exemplos de `cuobjdump` mostram duas palavras de 64 bits por instrução, o que é coerente.
- Os exemplos de desmontagem da seção 3.1.1 mostram instruções aritméticas com **operando direto do banco de constantes**, como `IMAD R0, R0, c[0x0][0x0], R3` e `ISETP.GE.AND P0, PT, R0, c[0x0][0x170], PT`. A arquitetura desse exemplo não é declarada.
- A tabela 4.4 descreve `LDCU` como carga de constante para um registrador uniforme e `S2UR` como cópia de registrador especial para um registrador uniforme. Isso dá o nome do caminho uniforme (`UR`), não o seu funcionamento.
- O documento **não explica o que é o SASS** nem sua relação formal com o PTX. Ele só mostra os dois lado a lado para o mesmo kernel.

> [!note] Limite
> O resumo veio de leitura automática. Auditado pelo `fact-checker` em 2026-10-19 (ver `harness/qa/fact-check-isa.md`). Os dois erros que bloqueavam (largura da instrução e operando de constante) foram corrigidos acima.
