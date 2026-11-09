---
tipo: secao
status: rascunho
secao: Escalonamento, CPU e interrupções
ordem: 11
nivel: chip
part_id: chip.host-if
procedencia_esperada: derived
itens_enunciado: [interrupções, escalonamento]
prazo:
fontes: ["[[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]", "[[NVIDIA - open-gpu-kernel-modules, interrupções e falhas]]", "[[NVIDIA - PTX ISA, versão 9.5 e instrução trap]]", "[[NVIDIA - Catálogo de Xid]]", "[[NVIDIA - README do GSP (driver 595.80)]]", "[[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)]]"]
---
# 11 - Escalonamento, CPU e interrupções

## Objetivo
Explicar como a CPU entrega trabalho à GPU, quem escalona os contextos, e como a GPU avisa a CPU (interrupções).

## Itens do enunciado cobertos
- interrupções
- escalonamento

## Já confirmado na fonte primária
- O AMP é um escalonador de contextos programável, implementado em um processador **RISC-V** dedicado na frente do pipeline da GPU. Ele tira da CPU o escalonamento de contextos ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 25).
- Interface com o computador: PCIe Gen 5 ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], Tab. 4).
- MIG: o GB202 pode ser dividido em até 4 instâncias de GPU isoladas ([[NVIDIA - Whitepaper RTX PRO Blackwell v1.1|whitepaper]], p. 44).

## Já levantado (rodada de 2026-11-09, auditoria formal pendente)
Trechos brutos em `harness/spec/sources/mmu-interrupts-sources.md`. "Leitura direta" quer dizer conferido no código-fonte ou na página baixada.

- **Os SMs não têm interrupção no sentido de uma CPU.** O que existe são três mecanismos: a GPU interrompe a CPU; um programa da GPU aborta e avisa a CPU; e o programa da GPU é preemptado.
- **A GPU interrompe a CPU por MSI ou MSI-X.** O driver registra o tratador com `request_threaded_irq(..., nvidia_isr, nvidia_isr_kthread_bh, ...)` e habilita MSI (`pci_enable_msi`) ou MSI-X ([[NVIDIA - open-gpu-kernel-modules, interrupções e falhas|driver aberto]], `nv.c` e `nv-msi.c`, leitura direta).
- **Tratamento em duas metades, como em qualquer driver.** A metade de cima (`nvidia_isr`, que chama `rm_isr`) roda no contexto da interrupção e faz o mínimo. A metade de baixo (`nvidia_isr_kthread_bh`, que chama `rm_isr_bh`) roda em uma thread do kernel (mesma fonte, leitura direta).
- **Falha de página.** A metade de cima da UVM (`uvm_isr_top_half`) agenda o tratamento em uma fila de thread do kernel. As falhas do motor gráfico e de computação são "replayable": o driver lê um lote do buffer de falhas, resolve e manda a GPU repetir. As demais são "non-replayable" e fazem o hardware trocar de canal ("fault and switch") (mesma fonte).
- **Exceção de programa.** A instrução `trap` do PTX: "Abort execution and generate an interrupt to the host CPU" ([[NVIDIA - PTX ISA, versão 9.5 e instrução trap|PTX ISA 9.5]], 9.7.21.4, leitura direta). A lista de instruções da Blackwell tem `BPT`, "BreakPoint/Trap" (Binary Utilities 13.5).
- **Como o erro aparece.** Xid 13, "Graphics Engine Exception": em geral, acesso além do fim de um vetor. Xid 31, "GPU memory page fault": falha reportada pela MMU ([[NVIDIA - Catálogo de Xid|catálogo de Xid]], leitura direta).
- **Preempção.** Desde a Pascal, uma tarefa de computação pode ser interrompida no nível de instrução, e o contexto vai para a memória da GPU ([[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)|whitepaper do P100]], p. 30). `derived`: não achamos texto que repita isso para a Blackwell.
- **GSP.** Processador da GPU para o qual o driver transfere inicialização e gerenciamento ([[NVIDIA - README do GSP (driver 595.80)|README do GSP]], leitura direta). O README não diz que ele é RISC-V. RISC-V só está documentado para o AMP.

## A levantar
- Como a CPU envia comandos (canais, GPFIFO, pushbuffer): o driver cita `set_gpfifo_entry` e `write_gpu_put`, falta ler.
- Como o AMP, o GSP e o driver dividem o escalonamento de contextos.
- Como o MIG isola recursos entre instâncias?
- Auditoria do `fact-checker` sobre esta rodada.

## Fontes
- [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]]
- [[NVIDIA - open-gpu-kernel-modules, interrupções e falhas]]
- [[NVIDIA - PTX ISA, versão 9.5 e instrução trap]]
- [[NVIDIA - Catálogo de Xid]]
- [[NVIDIA - README do GSP (driver 595.80)]]
- [[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> Detalhes de interrupções e de firmware dependem do código aberto do driver. O que não estiver lá fica registrado como lacuna declarada.

Anterior: [[10 - Memória virtual e MMU]] | Próxima: [[12 - Latência, ocupação e divergência]]
