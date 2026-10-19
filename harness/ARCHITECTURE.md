# Harness: apresentação cinematográfica de uma GPU NVIDIA RTX 6000 (workstation)

Versão 0.1. Documento vivo, é a fonte de verdade da arquitetura do harness.

## 1. Produto final

Uma página web (Three.js) que:

1. Apresenta a placa montada, com rotação lenta.
2. Desmonta a placa em ordem lógica (a ordem real de um teardown).
3. A cada peça: câmera cinematográfica aproxima, uma **linha de chamada** nasce de um ponto âncora da peça e vai até uma **caixa de texto** com a explicação, a explicação some e a próxima peça entra.
4. Cada explicação traz um selo de **procedência** (confirmado, derivado, provável ou ilustrativo), para o espectador saber o que é fato e o que é proposta de engenharia.
5. Pode ser exportada em vídeo (Playwright + ffmpeg) e permite navegação livre depois do tour.

## 2. Placa escolhida: RTX PRO 6000 Blackwell

Decidido em 2026-10-19: **RTX PRO 6000 Blackwell** (`card_id: rtx-pro-6000-blackwell-ws`). O harness continua parametrizado por `card_id`, então outra placa afetaria só `spec/` e o conteúdo. A tabela abaixo mantém a RTX 6000 Ada como contexto de comparação.

| | RTX 6000 Ada Generation | RTX PRO 6000 Blackwell (Workstation Edition) |
|---|---|---|
| GPU | AD102 | GB202 |
| Memória | 48 GB GDDR6 ECC | 96 GB GDDR7 ECC |
| Potência | ~300 W | ~600 W |
| Cooler | blower dual-slot | dual-slot, active, fluxo diferente |
| Conector | 16 pinos | 16 pinos (12V-2x6) |

Esses números são de memória e **devem ser verificados** pelo `spec-researcher` antes de entrarem no `spec.json`.
Variante a confirmar na pesquisa: Workstation Edition (~600 W) ou Max-Q (~300 W). O padrão do harness é a Workstation Edition.

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
| F1 | `card_id` | `spec/card.spec.json` + `spec/sources/` | `fact-checker` |
| F2 | spec | `design/assembly.json` + `design/proposal.md` | humano (revisa o que é "provável") |
| F3 | assembly | `parts/<id>/part.py`, `.glb`, `.step` por peça | `ops-runner` (lint) + `visual-qa` |
| F4 | partes | `build/card.glb` | interferência, bounding box vs. spec |
| F5 | GLB | materiais PBR, texturas procedurais | `visual-qa` |
| F6 | GLB + assembly | `story/storyboard.json` + `content/pt-BR/*.md` | `fact-checker` + humano |
| F7 | tudo | `viewer/` | Playwright smoke test |
| F8 | viewer | capturas, `dist/tour.mp4` | `visual-qa` |

## 6. Roster de agentes e modelos

O modelo de cada agente segue o **custo do erro** e a **complexidade do raciocínio** da função.
O orquestrador é a sessão principal. Os demais são subagentes em `.claude/agents/`.

| Agente | Modelo | Função | Por que esse modelo |
|---|---|---|---|
| **maestro** (sessão principal) | fable | Plano, despacho, estado, decisão de gates | Coordenação longa, muitas dependências |
| `spec-researcher` | sonnet | Pesquisa web e extrai fatos com fonte para o spec | Volume de leitura e extração estruturada |
| `architecture-inferencer` | fable | Propõe a arquitetura provável do que é privado | Raciocínio de engenharia por analogia; erro aqui contamina tudo |
| `assembly-planner` | opus | Árvore de montagem, ordem de explosão, interfaces | Planejamento estrutural com muitas restrições |
| `modeler-complex` | opus | Cooler (câmara de vapor, heatpipes, aletas), shroud, backplate | Geometria difícil e paramétrica |
| `pcb-layout-modeler` | opus | PCB, tabela de posicionamento de componentes, silkscreen | Layout denso e coerente com a engenharia |
| `modeler-standard` | sonnet | Bracket, ventilador, conectores, die, módulos de memória | Peças bem definidas |
| `instancer` | haiku | Parafusos, MLCCs, aletas: instanciamento a partir de tabelas | Mecânico e repetitivo |
| `lookdev` | sonnet | Materiais PBR e texturas procedurais | Ajuste iterativo guiado por render |
| `integrator` | opus | Monta o GLB, resolve interferências e convenções | Reconcilia o trabalho de vários agentes |
| `storyboard-director` | opus | Câmera, ritmo, âncoras, ordem dramática | Julgamento estético visual |
| `technical-writer` | sonnet | Textos extensos em PT-BR por peça | Escrita didática em volume, validada pelo fact-checker |
| `viewer-engineer` | sonnet | App Three.js, timeline, linhas de chamada | Código web padrão |
| `visual-qa` | opus | Crítico visual isolado (renders x referências) | Visão e julgamento fino |
| `fact-checker` | fable | Audita toda afirmação contra spec e procedência | Barreira final de correção técnica |
| `ops-runner` | haiku | Roda scripts, valida schema, nomes, malhas, capturas | Trabalho determinístico |

Regra de escalada: se um agente de modelo menor falhar duas vezes na mesma peça, a tarefa sobe um nível.

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
  "units": "mm", "up": "+Z", "origin": "pcb.bottom_left_front",
  "parts": [
    {"id": "cooler.heatsink", "parent": "cooler", "provenance": "derived",
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

## 8. Estrutura de diretórios

```
apresentacao-placa-de-video/          # raiz do repositório = raiz do projeto Claude Code
  CLAUDE.md
  .claude/agents/*.md                 # um arquivo por agente (modelo no frontmatter)
  .claude/skills/<skill>/SKILL.md
  vault/                              # vault Obsidian: briefing, pesquisa, roteiro, ensaios
  harness/
    ARCHITECTURE.md
    spec/            # fatos + fontes
    design/          # assembly.json, proposal.md
    parts/<id>/      # part.py, part.glb, part.step, qa/
    build/           # card.glb
    story/           # storyboard.json
    content/pt-BR/   # textos por peça
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
| `cinematic-storyboard` | a escrever | storyboard-director |
| `explainer-writing-ptbr` | a escrever | technical-writer |
| `viewer-scaffold` | a escrever | viewer-engineer |
| `model-qa` | a escrever | ops-runner, visual-qa, integrator |

## 10. Riscos e limites

- O layout interno do die, os esquemáticos e a lista exata de componentes são proprietários. Tudo isso será `inferred` ou `illustrative`, e o viewer diz isso.
- Marcas e logos da NVIDIA: aceitável em uso educacional, e exige revisão antes de qualquer uso comercial.
- Render sem GPU (SwiftShader) é lento. Vídeo em alta resolução pode exigir captura quadro a quadro.
- Modelos de baixo nível de erro (haiku) só executam tabelas e scripts. Nunca decidem conteúdo técnico.

## 11. Próximos passos

1. ~~Humano escolhe a placa~~ Feito: RTX PRO 6000 Blackwell. Pendente: variante (Workstation ou Max-Q) e os dados do briefing no vault (público, tempo de fala, prazo).
2. `spec-researcher` monta o spec e as fontes, e o `fact-checker` valida.
3. `architecture-inferencer` roda a skill `gpu-assembly-proposal` e o humano revisa a proposta.
4. Piloto: PCB + cooler + shroud com explosão e uma única chamada funcionando no viewer, de ponta a ponta.
