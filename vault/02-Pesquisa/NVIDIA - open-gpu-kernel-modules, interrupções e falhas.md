---
tipo: fonte
status: rascunho
secao: Interrupções
autor: NVIDIA
link: https://github.com/NVIDIA/open-gpu-kernel-modules/tree/main/kernel-open
acessado: 2026-11-09
procedencia: confirmed
---
# NVIDIA - open-gpu-kernel-modules, interrupções e falhas

## Dados da fonte
- **Título:** código aberto do driver NVIDIA: `kernel-open/nvidia-uvm/uvm_gpu_isr.c`, `uvm_gpu_replayable_faults.c`, `uvm_gpu_non_replayable_faults.c`, `uvm_blackwell_fault_buffer.c` e `kernel-open/nvidia/nv.c`, ramo `main`.
- **Autor / publicador:** NVIDIA (licença MIT).
- **Link:** no frontmatter.
- **Data de acesso:** 2026-11-09. Leitura por resumo automático; `nv.c` só até o caractere 100.000 de 176.317.

## Pontos que servem à apresentação
- A interrupção da GPU passa por um **handler de IRQ** do módulo `nvidia` (`nvidia_isr`, com MSI ou MSI-X). A **metade de cima** é curta; a **metade de baixo** roda em thread do kernel (`nvidia_isr_kthread_bh`). Serve a [[11 - Escalonamento, CPU e interrupções]].
- A UVM é consultada na metade de cima (`uvm_isr_top_half`) e agenda sua metade de baixo numa fila de threads. Desde a Turing as interrupções de falha são **por pulso** e ficam desligadas entre o aviso e o tratamento para evitar "tempestade".
- Falha de página: a GPU grava entradas num **buffer de falhas**; a CPU lê o ponteiro PUT por BAR0 (PCIe), junta duplicatas, serve em lote e manda a GPU **reproduzir** (replay) os acessos. Falhas de CE e PBDMA ("não reproduzíveis") passam por um buffer sombra gerido pelo RM.
- Limite: o código não diz com todas as letras que a interrupção "vai pelo PCIe"; os literais `pci_enable_msix` e `pci_enable_msi` não foram vistos.

## Trecho bruto salvo em
`harness/spec/sources/mmu-interrupts-sources.md`, seções 9.2 e 9.3.

> [!note]
> Resumo com palavras próprias. Rodada não auditada. Falha fatal chega ao usuário como Xid ([[NVIDIA - Catálogo de Xid]]).
