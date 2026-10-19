---
tipo: briefing
status: pronto
---
# Decisões do projeto

Registro curto de decisões já tomadas. Detalhes técnicos em `harness/ARCHITECTURE.md`.

| Data | Decisão | Motivo |
|---|---|---|
| 2026-10-19 | Placa: **RTX PRO 6000 Blackwell** | Escolha do autor. A RTX 6000 Ada ficou como comparação |
| 2026-10-19 | Orquestrador: **Fable 5.1** na sessão principal, Opus 5.5 como alternativa | Coordena 15 agentes e 9 fases. Um briefing ruim se multiplica pelos subagentes, e o consumo de tokens do orquestrador é pequeno perto do dos workers |
| 2026-10-19 | Geometria em **build123d** (sem Blender) e viewer em **Three.js** | O ambiente tem Node, Python e Chromium, mas não Blender |
| 2026-10-19 | Selos de procedência (`confirmed`, `derived`, `inferred`, `illustrative`) em toda peça e texto | Peças sem documentação pública serão propostas de engenharia, e o espectador precisa saber a diferença |
| 2026-10-19 | Harness em `harness/` e vault em `vault/`, no mesmo repositório | Um só lugar para o programa e o conteúdo editorial |
| 2026-10-19 | Variante: **Workstation Edition** | Escolha do autor |
| 2026-10-19 | Público: estudante de computação e o professor, com rigor de engenharia | Escolha do autor |
| 2026-10-19 | Conteúdo sem limite definido pelo grupo | Escolha do autor |
| 2026-10-19 | Tema do trabalho: **GPU Nvidia**, linha de Arquitetura | Enunciado da disciplina, ver [[Requisitos da disciplina]] |
| 2026-10-19 | **Roteiro v2** confirmado: foco na arquitetura da GPU (14 seções, da placa ao chip). Roteiro v1 arquivado | O v1 não cobria nenhum item exigido pelo professor |
| 2026-10-19 | Proposta formal de 2026-10-26 rascunhada em [[Proposta formal]] | Entrega de 0,5 ponto |

## Em aberto
- Duração do seminário ([[Briefing]]).
- Divisão de trabalho entre os integrantes.
