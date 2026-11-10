---
tipo: briefing
status: rascunho
---
# Plano de pesquisa

O que precisa ser levantado antes da modelagem (fase F1 do harness). Cada item vira uma nota de fonte em `02-Pesquisa/` (modelo em `Templates/Template - Fonte`), e o trecho bruto vai para `harness/spec/sources/`.

Os itens abaixo são **alvos**. O que cada fonte de fato diz está na nota da fonte, e o trecho bruto em `harness/spec/sources/`. A rodada do hardware físico é de 2026-11-09 (`physical-card-sources.md`); a auditoria está em `harness/qa/fact-check-fisico.md`.

| # | Alvo | Para quê | Procedência que gera | Status |
|---|---|---|---|---|
| 1 | Ficha técnica oficial da NVIDIA para a placa | Chip, memória, barramento, potência, conector, saídas, dimensões | `confirmed` | lido: [[NVIDIA - Página da RTX PRO 6000 Blackwell]] e [[NVIDIA - Datasheet da RTX PRO 6000 Workstation Edition]] (conector de energia incluído). Faltam peso oficial e dimensões em mm |
| 2 | Documentação do chip da família Blackwell usado na placa | Arquitetura, blocos do chip, recursos de workstation | `confirmed` | lido: [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]] |
| 3 | Reviews e fotos da própria placa | Aparência externa, cooler, bracket, saídas | `confirmed` | parcial: [[Jon Peddie Research - The Nvidia RTX Pro 6000 Blackwell Edition]], [[Puget Systems - Review da RTX PRO 6000 Blackwell Workstation]], [[sabareesh - 4x RTX PRO 6000 Blackwell com water block]]. Fotos das vistas padrão ainda não catalogadas |
| 4 | Teardown da própria placa, se existir | Layout interno real | `confirmed` | lido por resumo: [[Gamers Nexus - Teardown da RTX PRO 6000 Blackwell]]. Não abre o cooler nem conta as fases de energia. As 35 imagens não foram catalogadas |
| 5 | Teardown da placa de consumo irmã que usa o mesmo chip | Posição da memória, VRM, estrutura do cooler | `derived` | parcial: [[NVIDIA - Anúncio da GeForce RTX 50 e Founders Edition da RTX 5090]], [[wccftech e Notebookcheck - RTX 5090 Founders Edition (PCB e cooler)]], [[Northridge Fix - Teardown da RTX 5090 Founders Edition (via imprensa)]]. O teardown do TechPowerUp bloqueou o acesso automático |
| 6 | Teardown da geração anterior da linha profissional | Prática de projeto da linha (memória em clamshell, VRM, cooler) | `derived` | pendente (não buscado) |
| 7 | Referências gerais de engenharia (VRM, GDDR, câmara de vapor, PCIe) | Embasar a seção "Como funciona" de cada peça | `confirmed` (conceito) | pendente |
| 8 | Normas dos conectores e encapsulamentos (slot PCIe, conector de 16 pinos, DisplayPort, GDDR7) | Medidas padronizadas para a modelagem | `confirmed` (norma) | pendente |

## Lacunas esperadas (viram `inferred` ou `illustrative`)
- Número exato de fases do VRM e componentes. Confirmado como lacuna em 2026-11-09: nenhuma fonte desta placa conta as fases.
- Camadas e roteamento do PCB, e as dimensões do PCB principal.
- Estrutura interna do cooler (câmara de vapor, aletas). Confirmado como lacuna: o teardown não abre o cooler.
- Fabricante dos chips de memória, diâmetro dos ventiladores, tipos de parafuso.
- Interior do chip.

A fila completa, por ordem de impacto no vídeo, está em `harness/design/assembly-plan.md`, seção 8.

Essas lacunas alimentam a skill `gpu-assembly-proposal`, depois que o spec for validado.

As fontes de arquitetura (guia CUDA, PTX, SASS, código aberto dos módulos de kernel, artigos de microbenchmark), com status e o que cada uma cobre, estão em [[Requisitos da disciplina]].

Ver também: [[Briefing]] e [[Decisões do projeto]].
