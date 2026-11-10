---
tipo: fonte
status: rascunho
secao: MMU
autor: NVIDIA
link: https://github.com/NVIDIA/open-gpu-kernel-modules/tree/main/kernel-open/nvidia-uvm
acessado: 2026-11-09
procedencia: confirmed
---
# NVIDIA - open-gpu-kernel-modules, UVM e MMU

## Dados da fonte
- **Título:** código aberto do driver NVIDIA, diretório `kernel-open/nvidia-uvm/` (arquivos `uvm_blackwell_mmu.c`, `uvm_hopper_mmu.c`, `uvm_hal.c`, `uvm_blackwell.c`), ramo `main`.
- **Autor / publicador:** NVIDIA (licença MIT).
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Código lido por resumo automático de `raw.githubusercontent.com`; `uvm_blackwell_mmu.c` veio literal.

## Pontos que servem à apresentação
- Existe `uvm_blackwell_mmu.c`, mas a família **GB20x** (onde está a GB202) usa a MMU da **Hopper**: o código comenta "GB20x MMU behaves as Hopper MMU". Serve a [[10 - Memória virtual e MMU]].
- A tabela de páginas da Hopper tem **6 níveis** (PDE4, PDE3, PDE2, PDE1, PDE0 e PTE) e **57 bits** de endereço virtual. Páginas de 4 KB, 64 KB, 2 MB e 512 MB; a GB100 acrescenta 256 GB.
- O comentário do código dá a divisão dos bits do VA por nível (56:56, 55:47, 46:38, 37:29, 28:21, 20:16 ou 20:12), que alimenta o diagrama.
- Limites: a ligação do PCI ID da GB202 à entrada GB20x do código é **inferência pelo nome**; a lista de tamanhos de página da Hopper não foi lida literalmente.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seção 9.1.

> [!note]
> Resumo com palavras próprias. Rodada não auditada. Compare com o formato da Pascal em [[NVIDIA - Pascal MMU Format Changes]].
