# Apresentação da RTX PRO 6000 Blackwell

Apresentação cinematográfica e interativa de uma placa de vídeo NVIDIA RTX PRO 6000 Blackwell: modelo 3D desmontável, câmera que se aproxima de cada peça e uma linha de chamada até uma caixa de texto com a explicação. Idioma do conteúdo: PT-BR.

## Estrutura

- `harness/`: camada técnica (spec, modelagem, storyboard, viewer). Comece por `harness/ARCHITECTURE.md`, que é a fonte de verdade. O estado do projeto está em `harness/STATUS.md`; a placa real em `harness/design/assembly-plan.md`; o vídeo em `harness/story/video-plan.md`.
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
| `chip-diagram-kit` | a escrever | **B** | `diagram-designer` | Transforma os números do spec em diagramas dos níveis 2 a 4. Erro de desenho vira erro de conteúdo |
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
- Fase atual (2026-11-09): F1 quase fechada, nada das fases F2 a F8 existe além de planos, schemas e validador. Acompanhamento completo, pendências e plano até o seminário em `harness/STATUS.md`.
- Grupo Warp 32. Documentação escrita entregue em 2026-11-09 (artigo); revisão em `harness/qa/revisao-artigo.md`. Seminário de 22 minutos (informado em 2026-11-10).
- Fontes de chip e instruções: whitepaper, página do produto, PTX ISA, CUDA Binary Utilities, compute capability e dois artigos de microbenchmark; exemplos SAXPY e `mma` compilados para `sm_120` em `harness/examples/`. Auditadas pelo `fact-checker` (`harness/qa/fact-check-isa.md`); a análise RISC ou CISC da seção 08 aguarda revisão humana.
- Fontes do hardware físico (2026-11-09): datasheet oficial e teardown da própria placa em `harness/spec/sources/physical-card-sources.md`, auditoria em `harness/qa/fact-check-fisico.md`. A placa tem cooler de fluxo duplo com dois ventiladores, adaptador PCIe separado e 32 posições de memória; o interior do cooler e as fases de energia continuam sem fonte.
- Fontes de MMU e interrupções (`harness/spec/sources/mmu-interrupts-sources.md`), normas (`standards-sources.md`) e catálogo de fotos (`harness/spec/references/index.md`), todos de 2026-11-09, com auditoria da segunda leva em andamento.
- Planos (2026-11-09), ainda sem gate humano: montagem v0.3 (`harness/design/assembly-plan.md`) e vídeo (`harness/story/video-plan.md`, 63 beats, 42 no corte do seminário). Contratos em `harness/schemas/`, validados por `harness/tools/validate.py`.
- Conclusão RISC ou CISC aprovada pelo humano em 2026-11-10 (seção 08 do roteiro). Os diagramas do chip são desenhados em camada SVG (contrato em `harness/diagrams/README.md`).
- Animatic dos atos 4 a 7 rodando desde 2026-11-10: `spec/card.spec.json` (177 fatos, 36 deles da placa física, ainda na primeira passada de auditoria: `harness/qa/fact-check-fisico-atos-0-3.md`), viewer (`harness/viewer/`), 11 diagramas gerados por script (`harness/diagrams/`), 31 beats com texto e storyboard. Gate de fatos da F6: aprovado com ressalvas (`harness/qa/fact-check-f6-segunda-passada.md`). Combinado com o autor: estrutura e conteúdo primeiro, design e visualização depois (fila em `harness/STATUS.md`, seção 8.1).
- Gates humanos de 2026-11-10: animatic dos atos 4 a 7 aprovado (F6) e proposta de engenharia da placa aprovada (F2, `harness/design/proposal.md`). Entrega do tour: um `.html` único navegado ao vivo, sem vídeo por enquanto. Orçamento refeito para 22 minutos (alvo de 20): os sete beats de reserva do chip entraram no corte do seminário, e a tabela GPU contra CPU (a7.3) foi retirada, porque o enunciado não pede comparação com CPU.
- Placa física (2026-11-10): `harness/design/assembly.json` com 44 peças, a partir da proposta aprovada. Fonte nova: guia de início rápido da NVIDIA (adaptador de 4x 8 pinos, conector na borda superior).
- Blockout da placa (2026-11-10): `harness/parts/blockout.py` gera `harness/build/card.glb` (não versionado) a partir do assembly e das medidas; o viewer e o `.html` único já o carregam.
- Cadeia de fidelidade da placa (decisão do autor em 2026-11-10, `harness/ARCHITECTURE.md`, seção 5.2): build123d para forma e medidas, Blender por script para detalhe de superfície, three.js para a imagem. O modelo segue o design da placa original, com textos e marcas. Sem compra de modelo pronto. A RTX 5090 Founders Edition serve de referência `derived`. Referências novas em `harness/spec/sources/physical-card-sources.md`, seção 18 (PCB nu com régua, desenho cotado de water block).
- Textos dos atos 0 a 3 escritos e corrigidos após a primeira passada do `fact-checker` (`harness/qa/fact-check-f6-atos-0-3.md`); falta a segunda passada. O viewer já toca beats 3D (explosão por estágio, destaque, âncora), testado com um storyboard de exemplo.
- Storyboard dos atos 0 a 3 pronto em 2026-11-10 (os 62 beats estão `ready`; seminário em 20:12, completo em 24:23), sobre o blockout, sem gate humano ainda. O `visual-qa` mediu as referências novas (`harness/qa/visual-qa-referencias-modelagem.md`): o PCB mede cerca de 119,6 x 121,5 mm, não 108 x 112, e o blockout precisa de revisão.
- Estilo visual escolhido pelo autor em 2026-11-10: **Keynote hiper-realista** (`harness/ARCHITECTURE.md`, seção 5.2). A beleza passou a ser a prioridade do autor.
- Pendentes: correção do referencial espelhado e integração da carcaça (`integrator`), realismo da placa (materiais, luz, Blender), modelagem das demais peças, gate humano do animatic da placa, modelagem das peças de fidelidade A, regra de classe do teardown (decisão humana), atos 0 a 3, etapa de design do viewer (fila em `harness/STATUS.md`, seção 8.1).
