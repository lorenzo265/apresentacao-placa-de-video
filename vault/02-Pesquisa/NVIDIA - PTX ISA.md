---
tipo: fonte
status: pronto
secao: Instruções
autor: NVIDIA
link: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html
acessado: 2026-10-19
procedencia: confirmed
---
# NVIDIA - PTX ISA

## Dados da fonte
- **Título:** Parallel Thread Execution ISA, versão 9.4 (documentação do CUDA).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-19.
- **Alcance da leitura:** o documento tem cerca de 470.000 caracteres. Foram lidos, por resumo automático, os trechos de 0 a 300.000 e de 400.000 a 500.000. Falta a parte final de instruções e as notas por arquitetura. Nada foi confirmado sobre `sm_120` dentro deste documento.

## Pontos que servem à apresentação
- O PTX é uma **máquina virtual e ISA de baixo nível**, pensada para ser estável entre gerações de GPU. Os programas PTX são traduzidos para o conjunto de instruções do hardware, que o Binary Utilities chama de "CUDA assembly" ou SASS (ver [[NVIDIA - CUDA Binary Utilities]]). O documento do PTX nunca usa o termo SASS.
- O PTX se descreve como **máquina load-store**: os operandos das instruções aritméticas precisam estar em registradores, e `ld` e `st` movem dados entre os espaços de memória e os registradores (seção 6.2). Isso é um argumento direto para [[08 - Instruções PTX e SASS, RISC ou CISC]].
- Os registradores são tipados, têm 8, 16, 32, 64 ou 128 bits (predicados têm 1 bit), **não são plenamente endereçáveis** (não se pode tomar o endereço de um registrador) e o número disponível depende da plataforma. Toda instrução pode ter um **predicado de guarda** (`@p`). Serve a [[07 - Registradores]].
- A execução é **SIMT**: threads de um CTA executam em grupos chamados warps, e o tamanho do warp é "tipicamente 32" (seção 2.2.1); a seção 4.5.1 afirma que todas as arquiteturas-alvo têm `WARP_SZ` igual a 32. Serve a [[05 - Modelo de execução SIMT]].
- Espaços de memória: registradores, especiais, constante, global, local, parâmetros e compartilhada. Serve a [[09 - Hierarquia de memória e caches]].

> [!note] Limite
> O resumo veio de leitura automática de trechos longos. Auditado pelo `fact-checker` em 2026-10-19 (ver `harness/qa/fact-check-isa.md`).
