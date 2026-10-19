---
tipo: fonte
status: pronto
secao: Chip e SM
autor: NVIDIA
link: https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf
acessado: 2026-10-19
procedencia: confirmed
---
# NVIDIA - Whitepaper RTX PRO Blackwell v1.1

## Dados da fonte
- **Título:** NVIDIA RTX PRO Blackwell GPU Architecture, versão 1.1 (49 páginas).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-19.

## Pontos que servem à apresentação
- Dá a **planta oficial do chip GB202**: GPCs, TPCs, SMs, controladores de memória e L2. Serve de base para [[04 - Planta do chip]] e [[06 - O SM por dentro]].
- Dá o **tamanho dos recursos por SM** (registradores e L1/compartilhada), que alimentam as contas de [[07 - Registradores]] e [[09 - Hierarquia de memória e caches]].
- Descreve a **memória GDDR7 e o ECC** da placa, base de [[03 - Memória e barramentos]].
- Revela que o escalonador de contextos da GPU roda num **processador RISC-V dedicado** (AMP), útil em [[08 - Instruções PTX e SASS, RISC ou CISC]] e [[11 - Escalonamento, CPU e interrupções]].
- Traz as **especificações completas** da RTX PRO 6000 contra a RTX 6000 Ada e a RTX A6000, base de [[13 - O que a Blackwell mudou]].

## Números conferidos
Tabela completa, com página de cada número, em `harness/spec/sources/nvidia-rtx-pro-blackwell-architecture-v1.1.md`.

> [!warning] Inconsistências do documento
> O texto diz que a RTX PRO 6000 usa o GB202 **completo** (192 SMs), mas as tabelas dão **188 SMs**. Usamos as tabelas. Além disso, a banda de memória da RTX 6000 Ada aparece com dois valores (1.008 e 960 GB/s) em tabelas diferentes.

> [!note] O que este documento não cobre
> MMU e memória virtual, interrupções, conjunto de instruções, profundidade do pipeline, política dos caches. Para isso, ver [[Plano de pesquisa]].
