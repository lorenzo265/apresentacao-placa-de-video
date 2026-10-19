---
tipo: fonte
status: rascunho
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
- **Alcance da leitura:** cerca de 112.000 caracteres, lidos por resumo automático os primeiros 100.000.

## Pontos que servem à apresentação
- É a referência oficial das ferramentas `cuobjdump` e `nvdisasm`, que mostram o SASS, e traz uma **referência de instruções por arquitetura**. A seção 4.4, "Blackwell and Rubin Instruction Set", cobre as capacidades de computação 10.0, 10.3, 10.7, 11.0 e 12.0. A placa deste trabalho é a 12.0 ([[NVIDIA - Compute capability das GPUs CUDA]]).
- A lista traz só nomes de opcodes e descrições curtas, não a codificação em bits. Famílias que aparecem: ponto flutuante (FADD, FFMA, FMUL, HMMA, DMMA, QMMA, OMMA), inteiros (IMAD, IADD3, LOP3, SHF, IMMA), memória (LDG, LDS, LDSM, STG, STS, atômicas), controle (BRA, CALL, RET, EXIT, BSSY, BSYNC, WARPSYNC), predicados (PLOP3, PSETP) e operações de tensor e cópia assíncrona (UTMALDG, UTMASTG, UTCHMMA). Serve a [[08 - Instruções PTX e SASS, RISC ou CISC]].
- O documento **não define a largura da instrução**. O exemplo de `cuobjdump` mostra duas palavras de 64 bits (em hexadecimal) por instrução, o que é compatível com uma instrução de 128 bits, mas o texto não diz isso.
- O documento **não explica o que é o SASS** nem sua relação formal com o PTX. Ele só mostra os dois lado a lado para o mesmo kernel.

> [!note] Limite
> O resumo veio de leitura automática. **Auditoria pelo `fact-checker` pendente** em 2026-10-19 (lista de opcodes e exemplo de palavras de 64 bits): não citar nos slides ou no texto final antes dela.
