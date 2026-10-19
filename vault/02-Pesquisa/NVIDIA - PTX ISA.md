---
tipo: fonte
status: rascunho
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
- O PTX é uma **máquina virtual e ISA de baixo nível**, pensada para ser estável entre gerações de GPU. Os programas PTX são traduzidos para o conjunto de instruções do hardware, que é o SASS (ver [[NVIDIA - CUDA Binary Utilities]]).
- O PTX se descreve como **máquina load-store**: os operandos das instruções aritméticas precisam estar em registradores, e `ld` e `st` movem dados entre os espaços de memória e os registradores (seção 6.2). Isso é um argumento direto para [[08 - Instruções PTX e SASS, RISC ou CISC]].
- Os registradores são tipados, têm 8, 16, 32, 64 ou 128 bits (predicados têm 1 bit), **não são endereçáveis** e o número disponível depende da plataforma. Toda instrução pode ter um **predicado de guarda** (`@p`). Serve a [[07 - Registradores]].
- A execução é **SIMT**: threads de um CTA executam em grupos chamados warps, e o tamanho do warp é "tipicamente 32". Serve a [[05 - Modelo de execução SIMT]].
- Espaços de memória: registradores, especiais, constante, global, local, parâmetros e compartilhada. Serve a [[09 - Hierarquia de memória e caches]].

> [!note] Limite
> O resumo veio de leitura automática de trechos longos. **Auditoria pelo `fact-checker` pendente** em 2026-10-19: não citar nos slides ou no texto final antes dela.
