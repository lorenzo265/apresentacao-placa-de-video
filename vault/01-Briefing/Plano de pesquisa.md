---
tipo: briefing
status: rascunho
---
# Plano de pesquisa

O que precisa ser levantado antes da modelagem (fase F1 do harness). Cada item vira uma nota de fonte em `02-Pesquisa/` (modelo em `Templates/Template - Fonte`), e o trecho bruto vai para `harness/spec/sources/`.

Nenhuma fonte foi coletada ainda. Os itens abaixo são **alvos**, não fatos.

| # | Alvo | Para quê | Procedência que gera | Status |
|---|---|---|---|---|
| 1 | Ficha técnica oficial da NVIDIA para a placa | Chip, memória, barramento, potência, conector, saídas, dimensões | `confirmed` | lido: [[NVIDIA - Página da RTX PRO 6000 Blackwell]] e, em 2026-10-26, datasheet e guia de início rápido (conector de 16 pinos), em [[Teardown e conector de energia (RTX PRO 6000 e 5090)]] |
| 2 | Documentação do chip da família Blackwell usado na placa | Arquitetura, blocos do chip, recursos de workstation | `confirmed` | lido: [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]] |
| 3 | Reviews e fotos da própria placa | Aparência externa, cooler, bracket, saídas | `confirmed` | parcial: ver [[Teardown e conector de energia (RTX PRO 6000 e 5090)]] (resumos automáticos, em auditoria) |
| 4 | Teardown da própria placa, se existir | Layout interno real | `confirmed` | parcial: um teardown encontrado (GamersNexus), a conferir com uma segunda fonte |
| 5 | Teardown da placa de consumo irmã que usa o mesmo chip | Posição da memória, VRM, estrutura do cooler | `derived` | parcial: dados da página da NVIDIA da RTX 5090 FE; VRM e PCB sem fonte aberta |
| 6 | Teardown da geração anterior da linha profissional | Prática de projeto da linha (memória em clamshell, VRM, cooler) | `derived` | pendente |
| 7 | Referências gerais de engenharia (VRM, GDDR, câmara de vapor, PCIe) | Embasar a seção "Como funciona" de cada peça | `confirmed` (conceito) | pendente |

## Lacunas esperadas (viram `inferred` ou `illustrative`)
- Número exato de fases do VRM e componentes.
- Camadas e roteamento do PCB.
- Estrutura interna do cooler (heatpipes, câmara de vapor, aletas).
- Interior do chip.

Essas lacunas alimentam a skill `gpu-assembly-proposal`, depois que o spec for validado.

As fontes de arquitetura (guia CUDA, PTX, SASS, código aberto dos módulos de kernel, artigos de microbenchmark), com status e o que cada uma cobre, estão em [[Requisitos da disciplina]].

Ver também: [[Briefing]] e [[Decisões do projeto]].
