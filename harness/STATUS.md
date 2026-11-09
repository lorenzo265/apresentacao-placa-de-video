# Acompanhamento do projeto

Data: **2026-11-09**. Feito a partir da leitura completa do repositório (harness, agentes, skill, vault, fontes, auditorias) e de testes no ambiente.

## 1. Resumo

1. **O projeto está na F1 (pesquisa).** Não existe modelo 3D, viewer, storyboard, texto final nem vídeo. O que existe é pesquisa de boa qualidade sobre o chip e as instruções, um roteiro em tópicos e a arquitetura do harness.
2. **A documentação escrita vence hoje (2026-11-09, 1,5 ponto) e não está no repositório.** As 14 seções do roteiro são notas de pesquisa (13 `rascunho`, 1 `revisar`), não texto de entrega. `harness/content/` não existe.
3. **O repositório ficou sem commits de 2026-10-19 até hoje.** O cronograma da proposta previa leitura de fontes de 27/10 a 01/11 e redação de 02/11 a 08/11. Nada disso está aqui. Se foi feito fora do repositório, precisa entrar.
4. **Os dois itens de risco alto do enunciado continuam sem nenhuma fonte lida:** MMU (seção 10) e interrupções (seção 11).
5. **O seminário é em 7 dias (2026-11-16, 2,0 pontos).** O pipeline completo descrito na arquitetura (9 fases, 16 agentes) em uma semana é risco alto. A seção 7 propõe uma ordem de corte.
6. **Hoje a parte física saiu do zero:** datasheet oficial e teardown da própria placa registrados, e a estrutura real mostrou que o plano de montagem da v0.1 estava errado em pontos importantes.

## 2. Prazos

| Data | Entrega | Pontos | Situação no repositório |
|---|---|---|---|
| 2026-10-26 | proposta formal | 0,5 | rascunho com `status: revisar`, ainda com "[nome 1]" e o bloco "antes de entregar". **Não há registro de que foi entregue** |
| 2026-11-09 | documentação escrita | 1,5 | **não existe** |
| 2026-11-16 | seminário | 2,0 | sem slides, sem ensaio, sem viewer. Duração ainda não informada pelo professor |

## 3. Estado por fase

| Fase | O que deveria existir | O que existe | Estado |
|---|---|---|---|
| F0 Escopo | placa escolhida | RTX PRO 6000 Blackwell Workstation Edition | feito |
| F1 Pesquisa | `spec/card.spec.json`, fontes, auditoria | 4 arquivos de fontes, 16 notas no vault, 2 exemplos `sm_120`, auditoria das instruções. **Falta:** `card.spec.json`, guia CUDA, driver aberto, normas, catálogo de fotos | parcial |
| F2 Arquitetura | `proposal.json`, `proposal.md`, `assembly.json` | só o plano (`design/assembly-plan.md`), de hoje | não iniciada |
| F3 Modelagem | `parts/<id>/` | nada | não iniciada |
| F4 Integração | `build/card.glb` | nada | não iniciada |
| F5 Lookdev | `materials.json` | nada | não iniciada |
| F6 Roteiro e textos | `storyboard.json`, `content/pt-BR/` | só o plano (`story/video-plan.md`), de hoje, e as notas do vault | não iniciada |
| F7 Viewer | `viewer/` | nada | não iniciada |
| F8 QA e vídeo | capturas, `dist/tour.mp4` | nada | não iniciada |

Apoio: 16 agentes definidos (um novo hoje). **1 skill escrita de 10 previstas.** Nenhum schema JSON, nenhum `requirements.txt` nem `package.json`.

## 4. Estado por item do enunciado

É por esta tabela que o professor dá nota.

| Item exigido | Seção | Fontes lidas | Texto pronto | O que falta |
|---|---|---|---|---|
| Registradores | 07 | whitepaper, PTX, Volta, experimento | não | limite por thread (guia CUDA) |
| Conjunto de instruções | 08 | PTX, Binary Utilities, experimentos; auditado | não (nota em `revisar`) | contagem de opcodes; revisão humana |
| CISC ou RISC | 08 | idem | não | **revisão humana da análise**, pendente desde 19/10 |
| MMU | 10 | **nenhuma** | não | driver aberto, guia CUDA. Ou lacuna declarada |
| Interrupções | 11 | só o AMP no whitepaper | não | driver aberto. Ou lacuna declarada |
| Gerenciamento de memória | 03, 09, 10 | whitepaper, GB203 | não | memória unificada (guia CUDA) |
| Pipeline | 05, 06, 12 | whitepaper, GB203, Volta | não | SIMT, divergência, limites de ocupação (guia CUDA) |
| Cache | 09 | whitepaper (tamanhos), GB203 (latências) | não | política, associatividade (artigos da Hopper e do B200, não lidos) |

Nenhuma nota de seção está com `status: pronto`. As seções 10 e 14 têm `fontes: []`.

## 5. O que falta no planejamento

Achados da revisão da v0.1. Os que têm "resolvido" foram tratados hoje nos planos v0.2. Os demais continuam abertos.

| # | Lacuna | Situação |
|---|---|---|
| 1 | O plano de montagem descrevia uma placa genérica (um ventilador, heatpipes, um PCB no comprimento da placa). A placa real tem cooler de fluxo duplo, dois ventiladores, adaptador PCIe separado e cabos flat | resolvido em `design/assembly-plan.md` |
| 2 | Não havia nenhuma fonte física: sem teardown, sem datasheet, sem conector | resolvido em parte: `spec/sources/physical-card-sources.md`. A auditoria (`qa/fact-check-fisico.md`) não aprovou na primeira passada; as 26 correções estão aplicadas e falta a segunda passada |
| 3 | Os níveis 2 a 4 do tour (chip, SM, conceitos), que cobrem todos os itens do enunciado, não tinham dono no roster | resolvido no plano: agente `diagram-designer` e contrato `diagrams/<id>.json`. Tipo de modelo aguarda confirmação |
| 4 | O vídeo era "opcional", sem resolução, fps, método de captura, cortes nem QA | resolvido em `story/video-plan.md` |
| 5 | O texto de 5 seções por peça não cabe em um quadro de vídeo | resolvido no plano: `headline`, `caption`, `body` e `fala` |
| 6 | "Uma peça por beat" não comporta o roteiro v2, em que a maior parte dos beats é conceito, não peça | resolvido no plano: atos e 63 beats |
| 17 | Regra de procedência não cobre "observação direta desta placa por terceiro" (peso, posição do conector) | **aberto** (grupo): por ora esses dados são `derived` |
| 18 | Memória: as fontes dão 32 posições, não 32 chips. O arranjo em pares por controlador é proposta | aberto: fila da F2 |
| 7 | Sem critério de fidelidade nem método de medida | resolvido no plano: níveis A, B e C, `measurements.csv`, pacote de referências |
| 8 | Contratos errados para a pilha escolhida (GLB em metros e Y para cima; teste de malha fechada falha) | achado em teste, corrigido nos contratos e nos agentes |
| 9 | **Duração do seminário** desconhecida desde 19/10 | **aberto** (professor) |
| 10 | **Divisão de trabalho** e quem fala cada ato | **aberto** (grupo) |
| 11 | Schemas JSON dos contratos | aberto |
| 12 | 9 skills "a escrever". Para uma semana, escrever só as que destravam a trilha crítica | aberto: ver seção 7 |
| 13 | Normas (slot PCIe, conector de 16 pinos, DisplayPort, GDDR7) não registradas, então nenhuma medida padronizada pode entrar | aberto |
| 14 | 35 fotos do teardown sem catálogo; faltam fotos de produto das vistas padrão | aberto |
| 15 | Plano de reserva do seminário só citado na proposta | resolvido no plano (`story/video-plan.md`, seção 9); falta executar |
| 16 | `vault/04-Slides` e `vault/05-Ensaio` vazios | aberto |

## 6. O que falta na implementação

Por trilha (definidas em `ARCHITECTURE.md`, seção 5.1), em ordem de dependência.

**A. Texto (vale 1,5 hoje e sustenta o seminário)**
1. Ler e registrar o guia de programação CUDA e o código aberto do driver. Auditar.
2. Decidir, por item, entre fonte encontrada e lacuna declarada (MMU, interrupções).
3. Revisão humana da análise RISC ou CISC.
4. `spec/card.spec.json` consolidado.
5. Redigir as 14 seções, auditar, exportar em Word ou PDF.

**B. Diagramas do chip (níveis 2 a 4)**
1. Contrato e schema de `diagrams/<id>.json`.
2. Planta do chip, SM, escada de memória, palavra de 128 bits, PTX para SASS: todos têm fonte auditada.
3. Tradução de endereço, submissão de trabalho, interrupção: **bloqueados** por fonte.

**C. Placa física (níveis 0 e 1)**
1. Catalogar fotos e registrar normas.
2. `gpu-assembly-proposal` sobre as 7 lacunas de `design/assembly-plan.md`, seção 8. Gate humano.
3. `assembly.json` e `measurements.csv`.
4. Blockout, depois as peças de nível A: moldura, placa traseira, ventiladores, aletas, PCB principal com memória, conector, bracket, adaptador PCIe.
5. Integração, materiais, QA visual contra foto.

**D. Viewer e vídeo**
1. `requirements.txt` e `package.json` com versões fixas.
2. Esqueleto do viewer com timeline única, `seek` e modo de captura.
3. Script de captura por beat com cache, e montagem com `ffmpeg`.
4. Linha de chamada, caixa de texto, selo, cabeçalho de nível, três caminhos.
5. `storyboard.json` (63 beats; 42 de prioridade 1) e `beats.json`.
6. Checagens automáticas e QA visual.
7. Corte do seminário, MP4 e PDF de reserva.

Dos 63 beats planejados, **10 estão bloqueados por falta de fonte, 5 deles de prioridade 1** (SIMT e os quatro de MMU e interrupções).

## 7. Proposta de plano até o seminário

Proposta, não decisão. A ordem de prioridade é A, depois B, depois D, depois C: primeiro o que vale nota.

| Dia | Trilha A (texto) | Trilhas B e D (diagramas, viewer) | Trilha C (placa) | Gate humano |
|---|---|---|---|---|
| seg 09/11 | fontes de MMU e interrupções; redação; auditoria; **entrega** | | | revisar RISC ou CISC; entregar |
| ter 10/11 | `card.spec.json` | esqueleto do viewer e captura; schemas | catálogo de fotos, normas; proposta de engenharia | aprovar a proposta (F2) |
| qua 11/11 | `beats.json` dos atos 4 e 5 | planta do chip e SM; storyboard em blockout | `assembly.json`, medidas, blockout | aprovar o animatic (F6) |
| qui 12/11 | `beats.json` dos demais atos; auditoria | diagramas dos atos 5 e 6; linha de chamada e caixa | peças de nível A | |
| sex 13/11 | | viewer completo; primeira captura (cerca de 5 h) | integração, materiais, QA visual | |
| sáb 14/11 | slides de apoio | correções; segunda captura; PDF de reserva | correções | assistir o corte inteiro |
| dom 15/11 | ensaio geral com cronômetro | congelar | congelar | |
| seg 16/11 | **seminário** | | | |

Linhas de corte, decididas de antemão:
- Se a proposta de engenharia não for aprovada na terça, a placa física fica com exterior fiel (nível A só para moldura, ventiladores, conector e bracket) e interior em blockout rotulado.
- Se os diagramas atrasarem na quinta, os níveis 3 e 4 viram diagramas estáticos com a mesma caixa de texto e o mesmo selo.
- Se a captura falhar na sexta, o seminário usa o viewer ao vivo e o PDF de quadros.
- Skills a escrever nesta semana: só `viewer-scaffold`, `chip-diagram-kit` e `build123d-gpu-parts`. As outras ficam para depois do seminário.

## 8. Decisões que só o grupo pode tomar

1. **A documentação de hoje:** foi entregue por outro caminho? Se não, o que será entregue e quando.
2. **A proposta de 26/10:** foi entregue?
3. **Duração do seminário** (perguntar ao professor). Define o corte do vídeo.
4. **Viewer ao vivo ou vídeo corrido** no seminário. Recomendação: viewer ao vivo, com MP4 de reserva.
5. **MMU e interrupções:** investir mais um dia em fonte ou assumir lacuna declarada.
6. **Análise RISC ou CISC:** revisar e aprovar.
7. **Divisão de trabalho** e quem apresenta cada ato.
8. **Tipo de modelo do `diagram-designer`:** proposto B (opus).
9. **Logos da NVIDIA** no modelo: proposto não usar.
10. **Narração gravada e trilha:** proposto nenhuma no corte do seminário.
11. **Regra de procedência:** `confirmed` inclui observação direta desta placa por terceiro identificado (peso, posição do conector)? Hoje esses dados estão como `derived`.
12. **Beats de MMU e interrupções:** se a fonte não vier, viram beats de lacuna declarada. Hoje estão só bloqueados, e a cobertura do enunciado não fecha.

## 9. Feito em 2026-11-09

- Pesquisa do hardware físico: datasheet oficial, teardown da própria placa e análises de terceiros, em `spec/sources/physical-card-sources.md`, com 8 notas novas no vault.
- Auditoria independente dessa rodada: `qa/fact-check-fisico.md`. Resultado: não aprovado na primeira passada (3 achados que bloqueavam, 16 ajustes). Correções aplicadas; segunda passada pendente.
- `design/assembly-plan.md`: plano de montagem sobre a placa real.
- `story/video-plan.md`: plano da apresentação em vídeo, com 63 beats.
- `ARCHITECTURE.md` v0.2, 8 agentes ajustados e 1 agente novo.
- Teste da pilha: `build123d` e `trimesh` instalam e exportam; custo de captura medido (cerca de 1 s por quadro em 1080p).
