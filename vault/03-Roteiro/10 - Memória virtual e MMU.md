---
tipo: secao
status: rascunho
secao: Memória virtual e MMU
ordem: 10
nivel: chip
part_id: chip.mmu
procedencia_esperada: derived
itens_enunciado: [MMU, gerenciamento de memória]
prazo:
fontes: ["[[NVIDIA - open-gpu-kernel-modules, UVM e MMU]]", "[[NVIDIA - Pascal MMU Format Changes]]", "[[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)]]", "[[NVIDIA - Catálogo de Xid]]", "[[NVIDIA - Guia de programação CUDA]]"]
---
# 10 - Memória virtual e MMU

## Objetivo
Explicar como a GPU traduz endereços: se há MMU própria, como são as tabelas de página, o TLB, o tratamento de falhas de página e a relação com a memória da CPU.

## Itens do enunciado cobertos
- MMU
- gerenciamento de memória

## Já levantado (rodada de 2026-11-09, auditoria formal pendente)
Trechos brutos em `harness/spec/sources/mmu-interrupts-sources.md`. Os itens marcados "leitura direta" foram conferidos no código-fonte baixado.

- **A GPU tem MMU própria.** Uma falha da MMU, como acesso a endereço ilegal, é registrada pelo driver como Xid 31, "GPU memory page fault" ([[NVIDIA - Catálogo de Xid|catálogo de Xid]], leitura direta). Que cada programa tem o seu próprio espaço de endereços é o esperado, mas ainda **não temos o trecho da fonte**: é pendência.
- **O GB202 usa o formato de MMU da Hopper: 6 níveis e 57 bits de endereço virtual.** O driver oficial lista o GB202 entre as implementações da família GB20x (`ctrl2080mc.h`: "valid ARCHITECTURE_GB20x implementation values") e diz "GB20x MMU behaves as Hopper MMU" (`uvm_hal.c`). Para a Hopper: PDE4 (bit 56), PDE3 (55:47), PDE2 (46:38), PDE1 (37:29), PDE0 (28:21) e PTE (20:12 para 4 KB, 20:16 para 64 KB); `num_va_bits` devolve 57 ([[NVIDIA - open-gpu-kernel-modules, UVM e MMU|driver aberto]], leitura direta).
- **A conta dos 57 bits, por tamanho de página.** Os índices têm 1, 9, 9, 9 e 8 bits (`bit_widths[] = {1, 9, 9, 9, 8}`), mais 9 no último nível para 4 KB ou 5 para 64 KB. Página de 4 KB: 45 de índice + 12 de deslocamento. De 64 KB: 41 + 16. De 2 MB: 36 + 21. De 512 MB: 28 + 29. Sempre 57.
- **Tamanhos de página: 4 KB, 64 KB, 2 MB e 512 MB.** A lista está em `page_sizes_ampere` ("UVM_PAGE_SIZE_512M | UVM_PAGE_SIZE_2M | UVM_PAGE_SIZE_64K | UVM_PAGE_SIZE_4K"), que a Hopper herda (leitura direta). A página de 2 MB termina no PDE0 e a de 512 MB no PDE1, sem descer até o último nível.
- **Evolução.** Na Pascal (2016) eram 49 bits, 5 níveis e páginas de 4 KB, 64 KB e 2 MB ([[NVIDIA - Pascal MMU Format Changes|documento da Pascal]]). A Ampere ainda tinha 49 bits. O formato de 57 bits entrou na Hopper, e a família GB20x usa esse formato. A Pascal também trouxe falhas de página e memória unificada ([[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)|whitepaper do P100]], p. 27 e 30). O artigo entregue em 2026-11-09 usa os 49 bits da Pascal; os três tamanhos de página que ele cita continuam valendo.
- **Falha de página na prática.** A GPU grava a falha em um buffer e o canal fica parado; a CPU é interrompida, o driver lê o buffer, resolve as falhas em lote e manda a GPU repetir os acessos ("replayable faults") ([[NVIDIA - open-gpu-kernel-modules, interrupções e falhas|driver aberto]]). Ver [[11 - Escalonamento, CPU e interrupções]].

> [!warning] Ressalvas
> Tudo aqui vale "segundo o driver oficial": código de driver mostra o que o software programa, não o circuito. Dentro da família GB20x há uma exceção, a implementação GB20B, que usa só 4 KB, 64 KB e 2 MB. Tamanho e organização das TLBs continuam sem fonte: é lacuna declarada.

## A levantar
- TLB: tamanho, níveis e política. Provável lacuna declarada (o driver só mostra as operações de invalidação).
- Memória unificada na versão atual do guia CUDA: como a página migra entre CPU e GPU.
- Como isso se liga ao IOMMU da CPU e ao espaço de endereços visível pelo PCIe?
- Auditoria do `fact-checker` sobre esta rodada.

## Fontes
- [[NVIDIA - open-gpu-kernel-modules, UVM e MMU]]
- [[NVIDIA - Pascal MMU Format Changes]]
- [[NVIDIA - Whitepaper Tesla P100 (Pascal GP100)]]
- [[NVIDIA - Catálogo de Xid]]
- [[NVIDIA - Guia de programação CUDA]]

## No viewer
- Nível: chip. Câmera e âncora: a definir pelo storyboard.

## Procedência
> [!warning]
> Estrutura da tabela de páginas: `confirmed`, com o escopo "segundo o driver oficial" (o GB202 está listado na família GB20x). Dados da Pascal: `derived`. Espaço de endereços por programa: pendência. TLB: lacuna declarada.

Anterior: [[09 - Hierarquia de memória e caches]] | Próxima: [[11 - Escalonamento, CPU e interrupções]]
