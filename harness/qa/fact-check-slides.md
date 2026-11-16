# Auditoria de fatos: slides do seminário (2026-11-16)

Auditor: agente `fact-checker`, em contexto separado de quem escreveu o texto. Escopo: `pontos` e `fala` dos 25 momentos do corte do seminário em `content/pt-BR/beats.json`, contra `spec/card.spec.json`, `spec/sources/`, `examples/` e `diagrams/`.

**Veredito: aprovado com ressalvas.** Nenhum número errado; todas as contas conferem (12 pol = 304,8 mm, 4 x 150 = 600, 600 / 12 = 50, 92,2 bi / 750 = 122,9 milhões por mm², 24.064 x 2 x 2,617 GHz = 125,95 TFLOPS, 94 x 2 = 188, 188 x 128 = 24.064, 28 x 512 / 8 = 1.792, 48 x 32 = 1.536, 188 x 256 = 48.128, 32 x 255 = 8.160 e 65.536 / 8.160 = 8,03, 96 GB / 512 MB = 192). Como os selos saíram da tela, o risco é de redação: hipótese do grupo que parece fato.

## Erros (todos corrigidos)

| # | Beat | Problema | Correção |
|---|---|---|---|
| E1 | a7.5 | "PTX e SASS, 16 bytes cada": os 16 bytes são só do SASS | "Cada instrução SASS tem 16 bytes" |
| E2 | a5.5 | "se um warp espera, outro entra no lugar" estava como fato | "Leitura do grupo: ..." |
| E3 | a7.5 | RISC com extensões sem marca de conclusão do grupo | "conclusão do grupo" |
| E4 | a5.1 | "blocos com milhares de threads" lia-se como milhares por bloco | "lançado milhares de vezes, em blocos de threads" |

## Ressalvas aplicadas

R1 (a1.5): "chapa metálica" virou "chapa", e a posição dos contatos PCIe ganhou o fato derivado `card.pcie_edge_position`. R2 e R3 (a1.1): "lançam ar para cima" sem "o", e a frase do calor vira princípio geral. R4 e R5 (a1.4): "Pela norma do conector" e "conta nossa" na soma 4 x 150 W. R6 (a2.1): sem "de metal" nas aletas, com "identificação das peças: leitura nossa das fotos". R7 (a2.12): marcação "lida pela Gamers Nexus". R8 e R9 (a3.6): 64 GB/s brutos e 63 com a codificação, e "na nossa leitura" na fala. R10 (a4.2): 188 contra 192 dito na fala. R11 (t2.1): "Lembra um núcleo de CPU". R12 (a5.5): "threads ativas (até 32)" e etapas "num processador de livro-texto". R13 (a5.8): "conta nossa". R14 (a5.9): lista "da família Blackwell". R15 (a5.10): Volta e Ampere na fala. R16 (a5.12): exceções como a LDGSTS. R17 (a5.14): "segundo o guia CUDA" e o Tuning Guide (128 KB) na fala. R18 e R19 (a6.4): a falha de página segura o canal, preempção e tratador no SM na fala. R20 a R23: `claims` e `source_line` completados.

## Em aberto

- **R24, tamanho do grupo:** o slide de abertura lista 5 integrantes (nomes da proposta entregue). O `CLAUDE.md` e o vault registram "até 4". Conferir com o autor.
- **R17, diagrama:** `diagrams/chip.memhier.json` tem duas notas antigas ("os tamanhos possíveis na compute capability 12.0 não foram levantados") que contradizem o rótulo com os tamanhos no mesmo diagrama. Corrigir na etapa de design.
- **a2.1:** "em volta do chip ficam os chips de memória" vem de `mem.back_layout` (leitura de foto, `derived`).
- O auditor não conferiu as fontes originais na web, só o spec e os excertos salvos.
