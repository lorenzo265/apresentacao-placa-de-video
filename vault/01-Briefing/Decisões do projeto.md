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
| 2026-10-19 | Modelo por skill definido em quatro tipos (A fable, B opus, C sonnet, D haiku), no `CLAUDE.md` da raiz | Skill roda no modelo de quem a invoca; skills de julgamento nunca em D, gate de fatos sempre em A |
| 2026-11-09 | Seminário de **15 a 20 minutos**; corte do seminário com alvo de 17 minutos | Informado pelo grupo |
| 2026-11-09 | Agente `diagram-designer` em tipo B (opus) confirmado | Os diagramas do chip cobrem os itens do enunciado e não tinham responsável |
| 2026-11-09 | Artigo entregue como documentação escrita. O seminário usa o mesmo exemplo SAXPY do artigo (`harness/examples/saxpy-cu/`) | O que aparece na tela precisa bater com o texto entregue |
| 2026-11-09 | Todo o trabalho técnico passa a ser feito neste repositório | Decisão do autor |
| 2026-11-09 | A divisão da fala no seminário segue a definição de tarefas da [[Proposta formal]] entregue em 26/10 | É a divisão que o professor já recebeu |
| 2026-11-09 | Proposta entregue arquivada (PDF e transcrição); o rascunho de 19/10 foi para `_arquivo/` | O repositório só tinha o rascunho, que não foi a versão entregue |
| 2026-11-10 | Conclusão RISC ou CISC aprovada: "RISC no formato, com instruções próprias de acelerador", apresentada como análise do grupo | Aprovação do autor depois da auditoria de 2026-11-09 |
| 2026-11-10 | Início da implementação do viewer e dos diagramas do chip | Decisão do autor |
| 2026-11-10 | Os diagramas dos níveis 2 a 4 são desenhados em uma camada SVG com um espaço de coordenadas único, e não no canvas 3D | Texto nítido em qualquer zoom, captura determinística e muito menos código; o zoom continua contínuo do chip ao detalhe |

## Em aberto
- Três ajustes na divisão da fala (`harness/story/video-plan.md`, seção 6).
