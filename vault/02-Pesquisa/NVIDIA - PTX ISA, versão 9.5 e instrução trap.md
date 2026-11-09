---
tipo: fonte
status: rascunho
secao: Interrupções
autor: NVIDIA
link: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html
acessado: 2026-11-09
procedencia: derived
---
# NVIDIA - PTX ISA, versão 9.5 e instrução trap

## Dados da fonte
- **Título:** Parallel Thread Execution ISA. A página atual abriu como **versão 9.5**; a nota anterior ([[NVIDIA - PTX ISA]]) registra 9.4. O texto da instrução `trap` foi lido no **PDF da versão 7.5** (seção 9.7.18.4, p. 380), porque o HTML da 9.5 vem truncado antes dessa seção.
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter (versão atual) e `docs.nvidia.com/cuda/archive/11.5.1/pdf/ptx_isa_7.5.pdf`.
- **Data de acesso:** 2026-11-09.

## Pontos que servem à apresentação
- `trap` "Abort execution and generate an interrupt to the host CPU." Está marcada como suportada em todas as arquiteturas-alvo (na 7.5). É o exemplo de exceção que sobe para a CPU em [[11 - Escalonamento, CPU e interrupções]].
- O PTX 9.5 diz que os programas PTX são "translated at install time to the target hardware instruction set". O artigo do grupo diz que o driver compila "na hora"; o PTX, como lido, não usa a palavra JIT. Ver [[08 - Instruções PTX e SASS, RISC ou CISC]].
- Procedência `derived` porque o texto da instrução é de versão antiga. Reler na 9.5 (PDF) na auditoria.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 6.

> [!note]
> Resumo com palavras próprias. Rodada não auditada.
