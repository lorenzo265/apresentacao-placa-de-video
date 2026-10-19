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

## Em aberto
- Variante: Workstation Edition ou Max-Q.
- Público, tempo de fala e prazo ([[Briefing]]).
