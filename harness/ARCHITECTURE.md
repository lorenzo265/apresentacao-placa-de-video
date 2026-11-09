# Harness: apresentação cinematográfica da NVIDIA RTX PRO 6000 Blackwell

Versão 0.2 (2026-11-09). Documento vivo, é a fonte de verdade da arquitetura do harness.

Documentos que detalham esta versão: `design/assembly-plan.md` (a placa real e como modelá-la), `story/video-plan.md` (a apresentação em vídeo) e `STATUS.md` (o que está feito e o que falta).

## 1. Produto final

Uma página web (Three.js) que:

1. Apresenta a placa montada, com rotação lenta.
2. Desmonta a placa em ordem lógica (a ordem real de um teardown).
3. A cada peça: câmera cinematográfica aproxima, uma **linha de chamada** nasce de um ponto âncora da peça e vai até uma **caixa de texto** com a explicação, a explicação some e a próxima peça entra.
4. Cada explicação traz um selo de **procedência** (confirmado, derivado, provável ou ilustrativo), para o espectador saber o que é fato e o que é proposta de engenharia.
5. É exportada em vídeo por captura determinística, quadro a quadro, em mais de um corte (seminário, completo, teaser). O vídeo é entregável de primeira classe, com especificação e QA próprios em `story/video-plan.md`.
6. Permite navegação livre depois do tour e roda de arquivo local, sem internet.

### 1.1 Níveis do tour (roteiro v2)

O trabalho é de Arquitetura (ver `vault/01-Briefing/Requisitos da disciplina.md`), então o tour desce em níveis, da placa até o interior do chip. Cada nível corresponde a um grupo de seções do roteiro (`vault/03-Roteiro/`).

| Nível | O que se vê | Seções | Natureza da geometria |
|---|---|---|---|
| 0. Placa montada | a placa inteira | 01 | peça física modelada |
| 1. Placa desmontada | cooler, placa de circuito, package, memória | 02, 03 | peça física modelada (interior `derived` ou `inferred`) |
| 2. Chip | planta do GB202: GPCs, SMs, L2, controladores de memória | 04 | diagrama proporcional às contagens oficiais |
| 3. SM | unidades dentro de um SM | 05 a 09, 12 | diagrama |
| 4. Conceitos | fluxos animados: warp, caminho de uma instrução, tradução de endereço, interrupção | 08, 10, 11 | animação didática, sem geometria física |
| Fechamento | placa remontada e comparação | 13, 14 | reaproveita os níveis anteriores |

Regras:
- Contagens e tamanhos do chip vêm do spec (`confirmed`). A forma e a posição desenhadas nos níveis 2 e 3 são `illustrative`, e o viewer diz isso.
- Cada peça de `design/assembly.json` ganha o campo `level` (0 a 4). Os ids `chip.*` são os mesmos `part_id` das notas do vault.
- Os níveis 2 a 4 não são geometria de CAD. São diagramas declarativos (`diagrams/<id>.json`), gerados a partir do spec pelo `diagram-designer` e desenhados pelo viewer no mesmo canvas.
- Uma seção do roteiro tem vários beats. O storyboard organiza os beats em atos (`story/video-plan.md`, seção 3).
- A passagem entre níveis é um beat próprio, com zoom contínuo.

## 2. Placa escolhida: RTX PRO 6000 Blackwell

Decidido em 2026-10-19: **RTX PRO 6000 Blackwell** (`card_id: rtx-pro-6000-blackwell-ws`). O harness continua parametrizado por `card_id`, então outra placa afetaria só `spec/` e o conteúdo. A tabela abaixo mantém a RTX 6000 Ada como contexto de comparação.

| | RTX 6000 Ada Generation | RTX PRO 6000 Blackwell (Workstation Edition) | Fonte do valor da Blackwell |
|---|---|---|---|
| GPU | AD102 (de memória, não verificado) | GB202, 188 SMs, 24.064 núcleos CUDA | whitepaper, Tab. 4; datasheet |
| Memória | 48 GB GDDR6 | 96 GB GDDR7 com ECC, 512 bits, 1.792 GB/s | whitepaper, Tab. 4; datasheet |
| Potência | 300 W | 600 W | whitepaper, Tab. 4; datasheet |
| Cooler | não levantado | "double-flow-through", dois ventiladores na frente | datasheet; teardown da Gamers Nexus |
| Conector | não levantado | um "PCIe CEM5 16-pin" | datasheet |
| Formato | não levantado | 5,4" × 12,0", dois slots | datasheet |

Os valores da Blackwell estão registrados em `spec/sources/`. Os da Ada (48 GB, 300 W) vêm da nota da seção 13 do roteiro, que cita a Tab. 4 do whitepaper, mas a coluna da Ada ainda não está no excerto local. A parte física (cooler, conector, placas de circuito, memória) foi levantada em 2026-11-09 e está em `spec/sources/physical-card-sources.md`, com auditoria em `qa/fact-check-fisico.md`. A estrutura real da placa difere bastante do que a v0.1 supunha: ver `design/assembly-plan.md`, seção 1.
Variante: Workstation Edition (600 W). A Max-Q (300 W) e a Server Edition têm outro cooler e não entram.

## 3. Princípios

1. **Procedência obrigatória.** Toda peça e toda afirmação carrega `provenance`:
   - `confirmed`: fonte oficial (datasheet, página NVIDIA) ou teardown da própria placa.
   - `derived`: deduzido de placa irmã com o mesmo chip (ex.: teardown da RTX 5090 ou 4090) ou da geração anterior.
   - `inferred`: proposta de engenharia plausível. Sempre mostrada como "provável".
   - `illustrative`: apenas didático, sem pretensão de fidelidade (ex.: interior do die).
2. **Contratos em arquivo.** Agentes não passam malhas pelo contexto. Eles leem e escrevem JSON, scripts e GLB em disco.
3. **Código gera geometria.** Cada peça é um script determinístico e re-executável (build123d), com um commit por peça aprovada.
4. **Verificador independente.** Quem cria nunca é quem aprova (`visual-qa`, `fact-checker`).
5. **Gates humanos** nos pontos de maior risco: escolha da placa, árvore de arquitetura "provável" e storyboard.
6. **Consistência de engenharia.** A arquitetura proposta precisa fechar as contas: orçamento de potência, número de chips de memória x largura do barramento, área térmica x TBP.

## 4. Stack

| Camada | Escolha | Motivo |
|---|---|---|
| Geometria | **build123d** (Python, CAD paramétrico) | Medidas exatas, STEP + glTF, sem Blender |
| Malha / pós-processo | trimesh, gltf-transform (Node) | Simplificação, Draco/meshopt, validação |
| Viewer | **Three.js + GSAP + camera-controls** (versões fixadas no build) | Timeline, câmera cinematográfica |
| Linhas de chamada | SVG sobreposto, âncora 3D projetada por frame, `stroke-dashoffset` | Linha "desenha" e segue a peça |
| Texto | DOM overlay (PT-BR) | Acessível e fácil de editar |
| QA visual e vídeo | Playwright + Chromium headless + ffmpeg (já instalados) | Capturas e render da tour sem GPU |
| Blender | **opcional**, não instalado | Só entra se precisarmos de render offline de alta qualidade |

Verificado em 2026-11-09: `build123d` 0.13.0 e `trimesh` 5.2.0 instalam em Python 3.13 e exportam STEP e GLB; Node 22, Playwright 1.63 e ffmpeg 6.1 estão no ambiente. Nenhuma dessas dependências está declarada no repositório ainda (`requirements.txt` e `package.json` são pendência). Achados do teste em `design/assembly-plan.md`, seção 7, e custo de captura em `story/video-plan.md`, seção 7.1.

## 5. Pipeline em fases (com gates)

```
F0 Escopo ──► F1 Pesquisa ──► F2 Arquitetura ──► F3 Modelagem ──► F4 Integração
 (humano)    (gate: fatos)   (gate: humano)     (fan-out, QA     (interferência,
                                                 por peça)         GLB)
        ──► F5 Lookdev ──► F6 Roteiro + Textos ──► F7 Viewer ──► F8 QA final + vídeo
                          (paralelos; gate: fatos) (gate: humano)
```

| Fase | Entra | Sai | Gate |
|---|---|---|---|
| F0 | pedido | `card_id` escolhido | humano |
| F1 | `card_id` | `spec/card.spec.json` + `spec/sources/` (hardware e arquitetura: ISA, memória, MMU, interrupções) | `fact-checker` |
| F2 | spec | `design/assembly.json` + `design/proposal.md` | humano (revisa o que é "provável") |
| F3 | assembly | `parts/<id>/part.py`, `.glb`, `.step` por peça | `ops-runner` (lint) + `visual-qa` |
| F4 | partes | `build/card.glb` | interferência, bounding box vs. spec |
| F5 | GLB | materiais PBR, texturas procedurais | `visual-qa` |
| F6 | GLB + assembly | `story/storyboard.json` + `content/pt-BR/*.md` | `fact-checker` + humano |
| F7 | tudo | `viewer/` | Playwright smoke test |
| F8 | viewer | capturas, `dist/tour.mp4` | `visual-qa` |

### 5.1 Trilhas e animatic

A v0.1 punha as fases em fila. Na prática são quatro trilhas que andam em paralelo depois da F2:

| Trilha | Fases | Entrega | Vale nota? |
|---|---|---|---|
| A. Texto | F1, F6 | documentação escrita e textos dos beats | sim (1,5 da documentação e base do seminário) |
| B. Diagramas do chip | F3, F5 | níveis 2 a 4, gerados a partir do spec | sim (cobrem todos os itens do enunciado) |
| C. Placa física | F2 a F5 | níveis 0 e 1, modelo desmontável | não diretamente (é o gancho visual) |
| D. Viewer e vídeo | F7, F8 | viewer, captura, cortes | é o meio do seminário (2,0) |

Regras novas:
1. **Animatic antes do detalhe.** A F3 começa por um *blockout*: cada peça é uma caixa com as dimensões do `assembly.json`. O viewer já roda o storyboard inteiro com o blockout. Câmeras, tempos e textos são aprovados aí (gate humano da F6), antes de qualquer peça detalhada.
2. **A trilha D começa junto com a F2.** O esqueleto do viewer e a captura determinística não dependem do modelo final.
3. **Prioridade em caso de aperto:** A, depois B, depois D, depois C. A placa física só recebe detalhe onde a câmera passa (níveis de fidelidade em `design/assembly-plan.md`, seção 4).

## 6. Roster de agentes e modelos

O modelo de cada agente segue o **custo do erro** e a **complexidade do raciocínio** da função.
O orquestrador é a sessão principal. Os demais são subagentes em `.claude/agents/`.

| Agente | Modelo | Função | Por que esse modelo |
|---|---|---|---|
| **maestro** (sessão principal) | fable | Plano, despacho, estado, decisão de gates | Coordenação longa, muitas dependências |
| `spec-researcher` | sonnet | Pesquisa web e extrai fatos com fonte para o spec | Volume de leitura e extração estruturada |
| `architecture-inferencer` | fable | Propõe a arquitetura provável do que é privado | Raciocínio de engenharia por analogia; erro aqui contamina tudo |
| `assembly-planner` | opus | Árvore de montagem, ordem de explosão, interfaces | Planejamento estrutural com muitas restrições |
| `modeler-complex` | opus | Cooler de fluxo duplo (pilhas de aletas, câmara de vapor proposta), moldura, placa traseira | Geometria difícil e paramétrica |
| `pcb-layout-modeler` | opus | Conjunto de placas (PCB principal, adaptador PCIe, cabos flat), tabela de posicionamento de componentes | Layout denso e coerente com a engenharia |
| `modeler-standard` | sonnet | Bracket, ventilador, conectores, die, módulos de memória | Peças bem definidas |
| `instancer` | haiku | Parafusos, MLCCs, aletas: instanciamento a partir de tabelas | Mecânico e repetitivo |
| `lookdev` | sonnet | Materiais PBR e texturas procedurais | Ajuste iterativo guiado por render |
| `integrator` | opus | Monta o GLB, resolve interferências e convenções | Reconcilia o trabalho de vários agentes |
| `diagram-designer` | opus | Diagramas dos níveis 2 a 4 (planta do chip, SM, fluxos), gerados a partir do spec | Traduz números oficiais em desenho sem inventar forma; é onde está a nota. **Novo na v0.2** |
| `storyboard-director` | opus | Câmera, ritmo, âncoras, ordem dramática | Julgamento estético visual |
| `technical-writer` | sonnet | Textos extensos em PT-BR por peça | Escrita didática em volume, validada pelo fact-checker |
| `viewer-engineer` | sonnet | App Three.js, timeline, linhas de chamada | Código web padrão |
| `visual-qa` | opus | Crítico visual isolado (renders x referências) | Visão e julgamento fino |
| `fact-checker` | fable | Audita toda afirmação contra spec e procedência | Barreira final de correção técnica |
| `ops-runner` | haiku | Roda scripts, valida schema, nomes, malhas, capturas | Trabalho determinístico |

Regra de escalada: se um agente de modelo menor falhar duas vezes na mesma peça, a tarefa sobe um nível.

Na v0.2 os agentes `assembly-planner`, `modeler-complex`, `pcb-layout-modeler`, `storyboard-director`, `technical-writer`, `viewer-engineer`, `ops-runner` e `visual-qa` foram ajustados à placa real e aos contratos novos. O tipo de modelo do `diagram-designer` (B) é proposta do orquestrador e aguarda confirmação humana.

### 6.1 Orquestrador

Decisão: **Fable 5.1** (alias `fable`) como modelo da sessão principal.

- **Papel.** Sustenta contexto longo (9 fases, ~15 agentes), escreve briefings autocontidos para cada subagente, decide os gates e reconcilia relatórios divergentes de QA. Um briefing ambíguo ou um gate frouxo se multiplica por todos os subagentes que dependem dele.
- **Custo.** O orquestrador lê resumos e escreve briefings, não malhas nem código de peça. Seu consumo de tokens é pequeno perto do dos workers, então pagar o modelo mais forte aqui rende mais do que em qualquer outro ponto.
- **Alternativa.** Opus 5.5 se o orçamento apertar, mantendo `fable` no `architecture-inferencer` e no `fact-checker`, que são as barreiras de correção.
- **Evitar.** Sonnet ou Haiku como orquestrador. O risco de briefings vagos e de aprovar fases cedo demais é maior nesse papel.
- **Como aplicar.** O modelo da sessão principal é escolhido com `/model` (não fica nos arquivos de agente). Abra a sessão do harness em Fable.

Este é um julgamento de projeto, não uma medição. Reavalie depois do piloto, olhando quantas rodadas de retrabalho cada gate gerou.

## 7. Contratos de dados

### 7.1 `spec/card.spec.json` (fatos)
```json
{
  "card_id": "rtx-pro-6000-blackwell-ws",
  "facts": [
    {"id": "gpu.chip", "value": "GB202", "provenance": "confirmed",
     "source": "spec/sources/nvidia-datasheet.md#L12"}
  ]
}
```

### 7.2 `design/assembly.json` (árvore)
```json
{
  "units": "mm", "up": "+Z", "origin": "card.envelope_min",
  "parts": [
    {"id": "cooler.heatsink", "parent": "cooler", "level": 1, "provenance": "derived",
     "confidence": 0.7, "rationale": "design análogo ao da placa irmã (teardown)",
     "geometry": "parts/cooler.heatsink/part.py",
     "explode": {"dir": [0, 0, 1], "distance": 60, "order": 4},
     "anchors": [{"id": "anchor.cooler.heatsink.1", "pos": [120, 40, 30]}],
     "fasteners": ["screw.cooler.1", "screw.cooler.2"]}
  ]
}
```

### 7.3 `story/storyboard.json` (roteiro)
```json
{
  "beats": [{
    "part": "cooler.heatsink",
    "explode_state": "stage_4",
    "camera": {"pos": [180, -90, 70], "target": [120, 40, 30], "fov": 32,
               "duration": 2.4, "ease": "power3.inOut"},
    "callout": {"anchor": "anchor.cooler.heatsink.1", "box": "right-center",
                "line_in": 0.8, "hold": 14.0, "line_out": 0.5},
    "text": "content/pt-BR/cooler.heatsink.md"
  }]
}
```

### 7.4 `content/pt-BR/<part>.md` (textos)
Seções fixas: **O que é** | **O que faz** | **Como funciona** | **Nesta placa** | **Nível de confiança** (com o selo de procedência). Frontmatter com `part`, `provenance` e `claims` (lista de fatos do spec que o texto usa, o que o fact-checker confere).

Esse é o texto longo (`body`), que aparece só no viewer. O texto de cada beat fica em `content/pt-BR/beats.json`, com `headline` (até 8 palavras), `caption` (até 35 palavras), `fala` (notas do apresentador) e `source_line` (a fonte que aparece na tela).

### 7.5 Mudanças de contrato da v0.2

| Contrato | O que muda | Detalhe em |
|---|---|---|
| `design/assembly.json` | origem `card.envelope_min` (canto do envelope, não do PCB); campos `stage`, `fidelity`, `exists_provenance`, `shape_provenance`, `count`, `measurements` | `design/assembly-plan.md`, seção 7 |
| `design/measurements.csv` | novo: toda medida com método, fonte, tolerância e procedência | `design/assembly-plan.md`, seção 6 |
| `spec/references/index.md` | novo: fotos de referência por vista (só URLs) | `design/assembly-plan.md`, seção 6.1 |
| `story/storyboard.json` | campos `id`, `act`, `section`, `level`, `priority`, `overlay`, `speaker`; bloco `cuts`; `fps` | `story/video-plan.md`, seções 2 e 4 |
| `diagrams/<id>.json` | novo: cena declarativa dos níveis 2 a 4 | `story/video-plan.md`, seção 7.2 |
| Unidades | CAD, assembly e storyboard em mm e Z para cima. O GLB sai em metros e Y para cima (padrão glTF). A conversão é feita só no `integrator` | `design/assembly-plan.md`, seção 7 |
| `schemas/*.schema.json` | novo: o `ops-runner` valida contra schemas que ainda não existem | pendência |

## 8. Estrutura de diretórios

```
apresentacao-placa-de-video/          # raiz do repositório = raiz do projeto Claude Code
  CLAUDE.md
  .claude/agents/*.md                 # um arquivo por agente (modelo no frontmatter)
  .claude/skills/<skill>/SKILL.md
  vault/                              # vault Obsidian: briefing, pesquisa, roteiro, ensaios
  harness/
    ARCHITECTURE.md
    STATUS.md        # acompanhamento: feito, falta, decisões pendentes
    spec/            # card.spec.json, sources/ (fontes), references/ (fotos, só URLs)
    examples/        # kernels PTX compilados para sm_120
    qa/              # relatórios do fact-checker e do visual-qa
    design/          # assembly-plan.md, assembly.json, proposal.md, measurements.csv
    parts/<id>/      # part.py, part.glb, part.step, qa/
    build/           # card.glb
    diagrams/        # cenas declarativas dos níveis 2 a 4
    story/           # video-plan.md, storyboard.json
    content/pt-BR/   # textos por peça e beats.json
    schemas/         # JSON Schema dos contratos
    tools/           # captura de vídeo e validações
    viewer/          # app Three.js
    dist/            # build final e vídeo
```

Os caminhos citados neste documento (`spec/`, `design/`, `parts/`...) são relativos a `harness/`.

### 8.1 Vault e harness

O `vault/` é a camada **editorial** (o que a apresentação diz e em que ordem). O `harness/` é a camada **técnica** (como o modelo e o viewer são gerados). A ligação entre eles:

- Cada nota de `vault/03-Roteiro/` tem a propriedade `part_id`, igual ao `id` da peça em `design/assembly.json`.
- Cada nota de `vault/02-Pesquisa/` é uma fonte. O `spec-researcher` grava o trecho bruto em `harness/spec/sources/` e o resumo na nota do vault.
- Os textos finais do viewer (`harness/content/pt-BR/`) nascem das notas do roteiro, passam pelo `fact-checker` e voltam ao vault com `status: pronto`.
- O vault é mantido pela skill `obsidian-vault-organizer`, e não é editado diretamente pelos agentes do harness, exceto o `technical-writer` e o `spec-researcher` nas pastas acima.

## 9. Skills

| Skill | Estado | Usada por |
|---|---|---|
| `gpu-assembly-proposal` | **escrita (v0.1)** | architecture-inferencer, assembly-planner |
| `build123d-gpu-parts` | a escrever | modeladores, instancer |
| `chip-architecture-explainer` | a escrever | technical-writer, storyboard-director |
| `source-registration` | a escrever | spec-researcher |
| `sass-example-lab` | a escrever | spec-researcher |
| `chip-diagram-kit` | a escrever (nova na v0.2) | diagram-designer |
| `cinematic-storyboard` | a escrever | storyboard-director |
| `explainer-writing-ptbr` | a escrever | technical-writer |
| `viewer-scaffold` | a escrever | viewer-engineer |
| `model-qa` | a escrever | ops-runner, visual-qa, integrator |

O tipo de modelo de cada skill (A, B, C ou D) e as regras de escalada estão em `CLAUDE.md`, seção "Modelos por skill e por agente".

## 10. Riscos e limites

- O whitepaper da NVIDIA não cobre MMU, interrupções, conjunto de instruções, pipeline do SM nem política dos caches. Esses itens dependem de outras fontes (guia CUDA, PTX, SASS, driver aberto, microbenchmarks) e podem terminar como lacuna declarada.
- O whitepaper tem inconsistências internas (192 contra 188 SMs, dois valores para a banda da RTX 6000 Ada). Toda conta é conferida entre tabelas e a tabela de origem é citada.
- O layout interno do die, os esquemáticos e a lista exata de componentes são proprietários. Tudo isso será `inferred` ou `illustrative`, e o viewer diz isso.
- Marcas e logos da NVIDIA: aceitável em uso educacional, e exige revisão antes de qualquer uso comercial.
- Captura sem GPU: medido em 2026-11-09, cerca de 1 s por quadro em 1080p, dominado pela gravação do PNG e não pelo render. Dez minutos a 30 fps levam cerca de 5 horas em série. Ver `story/video-plan.md`, seção 7.1.
- **Prazo.** Em 2026-11-09 só a F1 tem entregas. O seminário é em 2026-11-16. O pipeline completo em uma semana é risco alto; a ordem de corte está na seção 5.1 e o plano dia a dia em `STATUS.md`.
- **Interior da placa.** O único teardown desta placa não abre o cooler nem conta as fases de energia. O caminho do calor e o da energia terão partes `derived` e `inferred`, e o vídeo diz isso.
- **Placa irmã engana.** A RTX 5090 FE usa metal líquido e esta placa usa pasta térmica. Todo `derived` da 5090 FE pode estar errado do mesmo jeito.
- Modelos de baixo nível de erro (haiku) só executam tabelas e scripts. Nunca decidem conteúdo técnico.

## 11. Próximos passos

O acompanhamento detalhado, com o plano dia a dia até o seminário e as decisões humanas pendentes, está em `STATUS.md`. Em resumo:

1. Feito: placa, público, roteiro v2, proposta rascunhada, fontes de chip e de instruções auditadas, exemplos `sm_120`, fontes do hardware físico (2026-11-09), planos v0.2 de montagem e de vídeo.
2. Urgente (trilha A): documentação escrita, com prazo em 2026-11-09. Depende de ler o guia CUDA e o código aberto do driver para MMU e interrupções, ou de declarar a lacuna.
3. F1, fechar: consolidar `spec/card.spec.json`; registrar as normas (slot, conector de 16 pinos, DisplayPort, GDDR7); catalogar as fotos de referência.
4. F2: `architecture-inferencer` roda a `gpu-assembly-proposal` sobre a fila de `design/assembly-plan.md`, seção 8. Gate humano. Depois, `assembly.json`.
5. Trilha D: esqueleto do viewer com captura determinística e animatic em blockout.
6. Trilha B: `diagram-designer` gera a planta do chip e o SM a partir do spec.
7. F3 a F5 da placa física, só até o nível de fidelidade que cada beat pede.
