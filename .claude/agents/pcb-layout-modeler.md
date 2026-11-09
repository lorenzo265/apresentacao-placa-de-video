---
name: pcb-layout-modeler
description: Modela o conjunto de placas de circuito (PCB principal, adaptador PCIe, cabos flat) e posiciona componentes a partir de uma tabela de layout (memória, VRM, capacitores, conector), com textura procedural de trilhas e silkscreen. Use na fase F3.
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep
---

- Gere `parts/pcb/layout.csv` (id, tipo, x, y, rotação, lado, provenance) a partir de `design/proposal.json`. Os componentes são instanciados a partir dessa tabela, não modelados um a um.
- Esta placa não tem um PCB único no comprimento da placa: há um PCB principal, um adaptador PCIe separado e cabos flat (ver `harness/design/assembly-plan.md`, seções 1 e 2). Modele cada placa como peça própria.
- Memória: 32 posições, 16 delas no verso (`confirmed`). A posição exata vem do proposal e é `derived` ou `inferred`.
- Respeite as regras de coerência do proposal: chips de memória em volta do die, fases de energia perto do conector, distâncias plausíveis.
- Componentes pequenos (`pcb.smd`) são representativos (nível C): a quantidade não é fato e o layout marca isso.
- Camadas do PCB, máscara de solda e silkscreen entram como textura procedural, não como geometria.
- Peças com procedência `inferred` ou `illustrative` ficam marcadas no layout para o viewer exibir o aviso.
- Entregue `part.py`, `part.glb`, `part.step` e `qa/`.
