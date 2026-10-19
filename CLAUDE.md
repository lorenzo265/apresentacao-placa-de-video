# Apresentação da RTX PRO 6000 Blackwell

Apresentação cinematográfica e interativa de uma placa de vídeo NVIDIA RTX PRO 6000 Blackwell: modelo 3D desmontável, câmera que se aproxima de cada peça e uma linha de chamada até uma caixa de texto com a explicação. Idioma do conteúdo: PT-BR.

## Estrutura

- `harness/`: camada técnica (spec, modelagem, storyboard, viewer). Comece por `harness/ARCHITECTURE.md`, que é a fonte de verdade.
- `vault/`: vault Obsidian com a camada editorial (briefing, pesquisa, roteiro, ensaios). Tem o próprio `vault/CLAUDE.md`, que vale para tudo dentro de `vault/`.
- `.claude/agents/`: subagentes do harness, com o modelo de cada um no frontmatter.
- `.claude/skills/`: skills do projeto (`gpu-assembly-proposal`).

## Regras do projeto

1. **Procedência em tudo.** Toda peça e afirmação é `confirmed`, `derived`, `inferred` ou `illustrative`. Nunca apresente `inferred` como fato. Detalhes em `harness/ARCHITECTURE.md`.
2. **Sem fonte, sem fato.** Não invente números nem citações. Lacuna vira pendência.
3. **Quem cria não aprova.** `visual-qa` e `fact-checker` são sempre agentes separados de quem produziu.
4. **Gates humanos** nas fases F0, F2 e F6 (ver arquitetura).
5. **Orquestrador:** sessão principal em Fable 5.1 (`/model`). Justificativa em `harness/ARCHITECTURE.md`, seção 6.1.
6. **Vault:** use a skill `obsidian-vault-organizer` para qualquer organização dentro de `vault/`. Não mexa em `vault/.obsidian/`.
7. **Git:** um commit por mudança lógica, mensagem curta em PT-BR. Não reescreva histórico.

## Modelos por skill e por agente

Uma skill carrega suas instruções no contexto de quem a invoca, então **o modelo efetivo é o do agente que a usa**. Por isso cada skill abaixo tem um tipo de modelo e um agente responsável. O modelo de cada agente está no frontmatter de `.claude/agents/` e a lista completa em `harness/ARCHITECTURE.md`, seção 6.

### Tipos de modelo
| Tipo | Modelo | Use para | Nunca use para |
|---|---|---|---|
| A. Raciocínio de alto risco | `fable` (Fable 5.1) | orquestração, inferência de partes não públicas, auditoria de fatos, classificações com argumento (RISC ou CISC), MMU e interrupções com pouca fonte | tarefa mecânica |
| B. Geração difícil e julgamento visual | `opus` (Opus 5.5) | geometria complexa, planejamento com muitas restrições, direção de câmera, crítica visual, reestruturar o roteiro | tarefa mecânica |
| C. Trabalho volumoso e bem definido | `sonnet` (Sonnet 5.5) | pesquisa e extração, texto didático, código web padrão, peças simples, rotina do vault | decidir conteúdo técnico sem auditoria |
| D. Mecânico e determinístico | `haiku` (Haiku 5.5) | rodar scripts, validar schemas e malhas, instanciar tabelas, capturas | decidir qualquer conteúdo técnico |

### Skills
| Skill | Estado | Tipo | Invocada por | Por quê |
|---|---|---|---|---|
| `gpu-assembly-proposal` | pronta | **A** | `architecture-inferencer` | Propõe o que não é público. Um erro aqui contamina modelagem e texto |
| `chip-architecture-explainer` | a escrever | **C** + auditoria A | `technical-writer`, `storyboard-director` | Texto em volume sobre registradores, ISA, cache, MMU. O `fact-checker` (A) audita |
| `source-registration` | a escrever | **C** | `spec-researcher` | Rotina de registrar fonte: nota no vault, excertos em `harness/spec/sources/`, contas conferidas |
| `sass-example-lab` | a escrever | **C**, **A** para a interpretação | `spec-researcher` | Escrever PTX, compilar com `ptxas`, desmontar com `nvdisasm`. Interpretar o SASS e classificar é com A |
| `build123d-gpu-parts` | a escrever | **B** peças complexas, **C** simples, **D** repetitivas | `modeler-complex`, `modeler-standard`, `instancer` | Segue o agente |
| `cinematic-storyboard` | a escrever | **B** | `storyboard-director` | Ritmo, câmera e enquadramento exigem julgamento visual |
| `explainer-writing-ptbr` | a escrever | **C** | `technical-writer` | Escrita didática em volume, sempre seguida de auditoria |
| `viewer-scaffold` | a escrever | **C** | `viewer-engineer` | Código web padrão com teste automatizado |
| `model-qa` | a escrever | **D** mecânico, **B** visual | `ops-runner`, `visual-qa` | Checagens de malha e schema são mecânicas. Comparar com referência é visual |
| `obsidian-vault-organizer` | externa | **C** rotina, **B** reestruturação | sessão principal | Triar Inbox, links e propriedades é rotina. Mudar a estrutura do roteiro é decisão |
| `docx`, `pdf` (exportar a proposta e o texto) | externas | **C** | sessão principal | Formatação e exportação, sem decisão de conteúdo |
| `deep-research` (lacunas como MMU e interrupções) | externa | **C** coletores, **A** síntese | sessão principal | Coleta é volume, síntese e conclusão carregam o risco |
| `skill-creator`, `code-review`, `simplify` | externas | **B** | sessão principal | Escrever e revisar código e skills é geração difícil |

### Regras
1. **Skill de julgamento nunca roda em D.** Isso inclui qualquer skill que classifique, proponha ou conclua algo técnico.
2. **Gate de fatos é sempre A.** O `fact-checker` roda em Fable, em contexto separado de quem produziu o texto.
3. **Escalada:** se um agente falhar duas vezes na mesma tarefa, ela sobe um tipo (D para C, C para B, B para A). Não se desce de tipo para economizar em skill de julgamento.
4. **Rebaixar só com evidência.** No primeiro uso de uma skill, use o tipo mais alto da tabela. Só rebaixe depois de três execuções em que o `fact-checker` não achou erro.
5. **Dúvida de classificação:** pergunte ao humano, não decida em silêncio.
6. **A confirmar:** se o frontmatter de skill aceitar o campo `model`, repita o tipo ali. Até lá, vale a regra pelo agente que invoca.
7. **Esta sessão de construção** rodou em Sonnet 5.5 (tipo C) e delegou a auditoria ao `fact-checker` (A). Para as fases de inferência (MMU, interrupções, conector, interior do cooler) e de redação final, abra a sessão em Fable (ou Opus) com `/model`.

## Estado atual

- Placa: RTX PRO 6000 Blackwell, Workstation Edition.
- Contexto: trabalho de Arquitetura da disciplina de Organização e Arquitetura de Computadores, grupo de até 4. Entregas: proposta em 2026-10-26 (0,5), texto em 2026-11-09 (1,5), seminário em 2026-11-16 (2,0). Ver `vault/01-Briefing/Requisitos da disciplina.md`.
- O enunciado cobra arquitetura (registradores, instruções, CISC/RISC, MMU, interrupções, gerenciamento de memória, pipeline, cache). Roteiro v2 (14 seções, da placa ao interior do chip) confirmado em 2026-10-19. O v1, focado em hardware físico, está arquivado em `vault/_arquivo/roteiro-v1/`.
- Fase atual: F1 em andamento. Fontes lidas: whitepaper da arquitetura e página do produto (ver `harness/spec/sources/`). Também lidos: PTX ISA, CUDA Binary Utilities, compute capability e dois artigos de microbenchmark; exemplos SAXPY e `mma` compilados para `sm_120` em `harness/examples/`. As fontes de instruções foram auditadas pelo `fact-checker` (`harness/qa/fact-check-isa.md`); a análise RISC ou CISC da seção 08 aguarda revisão humana. Pendentes: guia CUDA, código aberto do driver (MMU e interrupções) e o conector de energia.
