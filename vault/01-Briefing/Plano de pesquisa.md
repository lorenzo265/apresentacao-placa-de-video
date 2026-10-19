---
tipo: briefing
status: rascunho
---
# Plano de pesquisa

O que precisa ser levantado antes da modelagem (fase F1 do harness). Cada item vira uma nota de fonte em `02-Pesquisa/` (modelo em `Templates/Template - Fonte`), e o trecho bruto vai para `harness/spec/sources/`.

Nenhuma fonte foi coletada ainda. Os itens abaixo são **alvos**, não fatos.

| # | Alvo | Para quê | Procedência que gera | Status |
|---|---|---|---|---|
| 1 | Ficha técnica oficial da NVIDIA para a placa (variante a definir) | Chip, memória, barramento, potência, conector, saídas, dimensões | `confirmed` | pendente |
| 2 | Documentação do chip da família Blackwell usado na placa | Arquitetura, blocos do chip, recursos de workstation | `confirmed` | pendente |
| 3 | Reviews e fotos da própria placa | Aparência externa, cooler, bracket, saídas | `confirmed` | pendente |
| 4 | Teardown da própria placa, se existir | Layout interno real | `confirmed` | pendente |
| 5 | Teardown da placa de consumo irmã que usa o mesmo chip | Posição da memória, VRM, estrutura do cooler | `derived` | pendente |
| 6 | Teardown da geração anterior da linha profissional | Prática de projeto da linha (memória em clamshell, VRM, cooler) | `derived` | pendente |
| 7 | Referências gerais de engenharia (VRM, GDDR, câmara de vapor, PCIe) | Embasar a seção "Como funciona" de cada peça | `confirmed` (conceito) | pendente |

## Lacunas esperadas (viram `inferred` ou `illustrative`)
- Número exato de fases do VRM e componentes.
- Camadas e roteamento do PCB.
- Estrutura interna do cooler (heatpipes, câmara de vapor, aletas).
- Interior do chip.

Essas lacunas alimentam a skill `gpu-assembly-proposal`, depois que o spec for validado.

Ver também: [[Briefing]] e [[Decisões do projeto]].
