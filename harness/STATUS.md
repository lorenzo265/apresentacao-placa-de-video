# Acompanhamento do projeto

Data: **2026-11-10**.

## 1. Resumo

1. **A documentação escrita foi entregue** (artigo de 13 páginas, grupo Warp 32). A revisão está em `qa/revisao-artigo.md` (segunda versão): o artigo cumpre a proposta e quase tudo tem fonte oficial. Sobram um dado desatualizado (49 bits na MMU), uma generalização na análise RISC ou CISC e cinco afirmações sem fonte ou com a fonte errada. **A primeira versão da revisão acusava o artigo de quatro erros que não eram erros**; a auditoria pegou e foi corrigido.
2. **A pesquisa (F1) está quase fechada.** Todos os itens do enunciado têm fonte, inclusive MMU e interrupções, que estavam em branco. Falta consolidar `spec/card.spec.json`. As duas auditorias do dia reprovaram a primeira passada e tiveram as correções aplicadas; falta a segunda passada de cada uma.
3. **A placa física agora tem base real:** teardown, datasheet, normas dos conectores e 75 fotos catalogadas. O plano de montagem está na v0.3 e mudou bastante em relação à manhã.
4. **O seminário tem 22 minutos** (informado em 2026-11-10; antes, de 15 a 20). O corte do seminário tem 48 beats, alvo de 20 minutos e 20:02 no orçamento atual (14:23 medidos no viewer para os atos 4 a 7, mais o orçamento da placa física e da remontagem).
5. **Nada das fases F2 a F8 existe ainda**, além de planos, schemas e do validador. O seminário é em 7 dias.

## 2. Prazos

| Data | Entrega | Pontos | Situação |
|---|---|---|---|
| 2026-10-26 | proposta formal | 0,5 | entregue. PDF e transcrição arquivados em 2026-11-09 (`vault/01-Briefing/Proposta formal.md`). Ela compromete o tour 3D como apoio do seminário e já define a parte de cada integrante |
| 2026-11-09 | documentação escrita | 1,5 | entregue (artigo). Revisão em `qa/revisao-artigo.md`. O PDF não está versionado |
| 2026-11-16 | seminário, 22 minutos | 2,0 | plano de vídeo pronto; sem viewer, sem slides, sem ensaio |

## 3. Estado por fase

| Fase | Existe | Falta | Estado |
|---|---|---|---|
| F0 Escopo | placa, público, duração | | feito |
| F1 Pesquisa | 6 arquivos de fontes, 43 notas no vault, 3 exemplos `sm_120`, catálogo de 88 imagens, 3 auditorias e 1 revisão | `spec/card.spec.json`; segunda passada das auditorias; guia CUDA lido por inteiro | quase fechada |
| F2 Arquitetura | `design/assembly-plan.md` v0.3, `design/proposal.md` (aprovada em 2026-11-10), `design/assembly.json` (44 peças), `design/measurements.csv` (129 medidas) | auditoria das 96 medidas novas | feita em 2026-11-10 |
| F3 Modelagem | | tudo | não iniciada |
| F4 Integração | | tudo | não iniciada |
| F5 Lookdev | | tudo | não iniciada |
| F6 Roteiro e textos | `story/video-plan.md` (63 beats), notas do roteiro com as seções 08, 10 e 11 atualizadas | `storyboard.json`, `beats.json`, textos longos | não iniciada |
| F7 Viewer | | tudo | não iniciada |
| F8 QA e vídeo | custo de captura medido | tudo | não iniciada |

Apoio: 16 agentes, 1 skill escrita de 10, 5 schemas com validador testado (`tools/validate.py`), `requirements.txt`.

## 4. Estado por item do enunciado

| Item | Seção | Fonte | O que o seminário mostra | Pendência |
|---|---|---|---|---|
| Registradores | 07 | Tuning Guide, whitepaper (Fig. 5), experimento | 4 bancos de 16.384 por SM (65.536), até 255 por thread, famílias `R`, `UR`, `P`, `SR` no código real | |
| Conjunto de instruções | 08 | PTX 9.5, Binary Utilities 13.5, experimento reproduzido | CUDA, PTX e SASS lado a lado; palavra de 128 bits; 258 mnemônicos em 13 categorias | |
| CISC ou RISC | 08 | lista oficial de instruções | "RISC no formato, com instruções próprias de acelerador" (análise do grupo) | aprovada em 2026-11-10 |
| MMU | 10 | código oficial do driver (leitura direta), documento da Pascal | 57 bits, 6 níveis, páginas de 4 KB a 512 MB; comparação com a Pascal | TLB é lacuna declarada; espaço de endereços por programa sem trecho de fonte |
| Interrupções | 11 | driver, PTX, catálogo de Xid | três mecanismos documentados: interrupção para a CPU, `trap`, preempção. Que o SM não trata interrupções é leitura do grupo (`inferred`) | como a CPU envia comandos (falta ler) |
| Gerenciamento de memória | 03, 09, 10 | whitepaper, driver, normas | GDDR7, hierarquia, falha de página em lote | memória unificada no guia CUDA |
| Pipeline | 05, 06, 12 | whitepaper (Fig. 5), Tuning Guide, guia CUDA, artigos | 4 blocos com escalonador de warp (`confirmed`), 48 warps por SM, divergência com o logotipo do grupo | profundidade do pipeline é lacuna declarada |
| Cache | 09 | whitepaper, artigo da RTX 5080 | tamanhos (`confirmed`) e latências (`derived`) | política e associatividade: lacuna |

## 5. Pendências de planejamento

| # | Item | Situação |
|---|---|---|
| 1 | Plano de montagem genérico | resolvido: `design/assembly-plan.md` v0.3, baseado em teardown e fotos |
| 2 | Fontes físicas | resolvido, com auditoria aplicada (`qa/fact-check-fisico.md`) |
| 3 | Dono dos diagramas do chip | resolvido: `diagram-designer`, tipo B, confirmado |
| 4 a 8 | Vídeo, texto por beat, atos, fidelidade, contratos | resolvidos nos planos |
| 9 | Duração do seminário | resolvido: 22 minutos (2026-11-10) |
| 10 | Quem apresenta cada bloco | resolvido: segue a definição de tarefas da proposta entregue (`story/video-plan.md`, seção 6). Três ajustes pequenos aguardam o grupo |
| 11 | Schemas dos contratos | resolvido: `schemas/` e `tools/validate.py`. Em 2026-11-10 o contrato dos diagramas ganhou geometria e a decisão da camada SVG (`diagrams/README.md`) |
| 12 | Skills a escrever | aberto: nesta semana só `viewer-scaffold`, `chip-diagram-kit` e `build123d-gpu-parts` |
| 13 | Normas | resolvido em parte: `spec/sources/standards-sources.md`. A norma PCIe aberta é a revisão 3.0; a bracket de dois slots e o receptáculo DisplayPort não têm desenho de fonte forte |
| 14 | Catálogo de fotos | resolvido: `spec/references/index.md`. Faltam vistas ortogonais oficiais, a frente do PCB e o interior do cooler |
| 15 | Plano de reserva do seminário | planejado, falta executar |
| 16 | Slides e ensaio | aberto |
| 17 | Regra de procedência para observação de terceiro | aberto: por ora `derived` |
| 18 | Memória: 32 posições ou 32 chips | a norma permite 32 chips de 3 GB; a frente do PCB nunca foi fotografada sem pads. Fila da F2 |
| 19 | Altura da placa | aberto: 137,2 mm oficiais contra 122 mm de carcaça medidos em foto de terceiro |
| 20 | Auditoria da segunda leva (MMU, normas, revisão do artigo, RISC ou CISC) | feita: `qa/fact-check-segunda-leva.md`, 29 achados, correções aplicadas. Falta a segunda passada |
| 21 | Auditoria visual das fotos e das medidas tiradas delas | aberto (`visual-qa`) |

## 6. O que falta implementar

**A. Texto.** Consolidar `spec/card.spec.json`; escrever `beats.json` (42 beats do corte, depois os 21 restantes); auditar; textos longos por seção.

**B. Diagramas do chip.** Planta do chip, SM, escada de memória, palavra de 128 bits, PTX para SASS, tabela de páginas de 6 níveis, caminho da interrupção. Todos têm fonte. Bloqueado: como a CPU envia comandos.

**C. Placa física.** Proposta de engenharia para 9 lacunas (`assembly-plan.md`, seção 8); gate humano; `assembly.json`; blockout; peças de nível A (carcaça, face B, ventiladores, aletas, PCB com memória, conector, bracket, adaptador PCIe); integração; materiais; QA contra foto.

**D. Viewer e vídeo.** `package.json`; esqueleto com timeline única, `seek` e modo de captura; captura por beat com cache; linha de chamada, caixa, selo, cabeçalho, três caminhos; `storyboard.json`; checagens automáticas; corte do seminário, MP4 e PDF de reserva.

Beats bloqueados: 3 de 63 (a5.3, a5.14 e a6.3), nenhum de prioridade 1.

## 7. Plano até o seminário (proposta)

Prioridade: A, depois B, depois D, depois C.

| Dia | Texto e diagramas | Viewer e vídeo | Placa física | Decisão sua |
|---|---|---|---|---|
| ter 10/11 | `card.spec.json`; `beats.json` dos atos 4 a 6 | esqueleto do viewer e captura; `package.json` | proposta de engenharia (F2) | aprovar a proposta; aprovar RISC ou CISC |
| qua 11/11 | diagramas: planta do chip, SM, tabela de páginas | linha de chamada, caixa, selo; storyboard em blockout | `assembly.json`, blockout | aprovar o animatic |
| qui 12/11 | diagramas: instrução, memória, interrupção; `beats.json` dos atos 0 a 3 e 7 | três caminhos; transições entre níveis | peças de nível A | |
| sex 13/11 | auditoria final dos textos | viewer completo; primeira captura (cerca de 5 h) | integração, materiais, QA visual | |
| sáb 14/11 | slides de apoio; notas de fala por apresentador | correções; segunda captura; PDF de reserva | correções | assistir o corte inteiro |
| dom 15/11 | ensaio geral com cronômetro | congelar | congelar | |
| seg 16/11 | **seminário** | | | |

Linhas de corte: se a proposta de engenharia não for aprovada na terça, o interior da placa fica em blockout rotulado e só o exterior recebe detalhe. Se os diagramas atrasarem na quinta, os níveis 3 e 4 viram diagramas estáticos. Se a captura falhar na sexta, o seminário usa o viewer ao vivo e o PDF de quadros.

## 8. Decisões que são suas

1. Conclusão RISC ou CISC: **aprovada em 2026-11-10**.
2. **Divisão da fala:** já segue a proposta entregue. Faltam três ajustes pequenos (`story/video-plan.md`, seção 6): dono da planta do chip, posição do beat da divergência e o tempo do Arthur.
3. **Como tratar o artigo no seminário:** recomendo citar só a MMU como atualização ("o formato mudou na Hopper") e apresentar RISC ou CISC como aprofundamento. O resto se resolve na fala.
4. **Tamanho do grupo:** a proposta entregue e o artigo têm cinco integrantes; a nota do enunciado no vault diz até quatro. Corrigir a nota?
5. **Versionar o PDF do artigo?** A proposta entregue já foi versionada a seu pedido. O artigo traz os mesmos nomes completos; depende de o repositório ser público.
6. Viewer ao vivo ou vídeo corrido (recomendado: ao vivo, com MP4 de reserva).
7. Logos da NVIDIA no modelo: **resolvido em 2026-11-10**, o modelo segue o design da placa original.
8. Regra de procedência para observação direta por terceiro.
9. Os 22 minutos incluem perguntas?

## 8.1 Animatic dos atos de chip (2026-11-10)

Existe e roda. É a **primeira versão de ponta a ponta**: conteúdo e estrutura primeiro, acabamento visual depois.

| Peça | Arquivo | Estado |
|---|---|---|
| Fatos consolidados | `spec/card.spec.json` (177 fatos: 141 do chip e da ficha, 36 da placa física para os atos 0 a 3) | validado; os citados na tela foram auditados. Os 36 novos tiveram a primeira passada (`qa/fact-check-fisico-atos-0-3.md`: não aprovado, correções aplicadas); segunda passada feita e corrigida; falta a terceira passada e a confirmação humana da regra de classe do teardown |
| Montagem da placa | `design/assembly.json` (44 peças), `design/measurements.csv` (129 medidas, 96 não auditadas) | válido no schema |
| Blockout da placa | `parts/blockout.py` gera `build/card.glb` (277 nós, 270 kB, determinístico; não versionado) e `build/blockout-report.json` | refeito em 2026-11-10 com as medidas do `visual-qa` (PCB de 119,6 x 121,5 mm com chanfro e rebaixo, memória na grade medida, conector a 45 graus, carcaça de 124 mm). Envelope exato; 44 de 44 peças com nó; nenhuma âncora a mais de 2 mm da peça; 4 interpenetrações no mesmo estágio (3 esperadas: tubos nas aletas); 38 peças ainda com algum valor de bloqueio. O tour roda os atos 0 a 3 sobre ele. No a1.4 a carcaça aparece esmaecida, do tempo em que não havia abertura para o conector: rever o destaque |
| Viewer | `viewer/`, `tools/smoke.cjs`, `tools/capture.cjs` | roda; placa ainda em blockout |
| Diagramas | `diagrams/` (11 cenas, geradas por script, 21 testes) | os 11 passaram pelo gate de fatos |
| Textos | `content/pt-BR/beats.json` (31 beats) | os 31 passaram pelo gate de fatos |
| Storyboard | `story/storyboard.json` (62 beats, todos prontos desde 2026-11-10; corte do seminário com 48 beats e 20:12 no viewer, completo com 62 e 24:23) | validado; os atos 0 a 3 rodam sobre o blockout e aguardam o gate humano do animatic da placa. O ato 0 mede 64 s contra 40 s de orçamento. A ordem de a3.6 e a3.7 foi trocada para o último beat 3D terminar perto do chip |
| Auditoria | `qa/fact-check-f6*.md` (quatro passadas) | **aprovado com ressalvas, todas aplicadas**. Gate humano do animatic: **aprovado em 2026-11-10** |
| Proposta da placa física | `design/proposal.md`, `design/proposal.json` | **aprovada no gate humano da F2 em 2026-11-10** (oito decisões, conforme recomendado) |
| Entrega | um `.html` único, navegado ao vivo; sem vídeo por enquanto. Gerado por `npm run build:single` (`harness/dist/tour.html`, 1,3 MB), testado por `tools/smoke-single.cjs` nos dois cortes | decisão de 2026-11-10; o seminário tem 22 minutos |

Tempo do corte do seminário: ato 4 com 1:56, ato 5 com 4:57, ato 6 com 2:59, ato 7 com 1:09 (só dois dos quatro beats essenciais existem). Atos 4 a 7: 11:03, para um orçamento de 11:50. O corte completo desses atos dá 15:17.

Nas telas, as quatro divisões do SM se chamam "partições", para não confundir com "bloco de threads".

Decisão do diretor do storyboard: o SM aparece **antes** do warp (a ordem na tela fica seção 04, 06, 05, 12, 07...), porque o warp está desenhado dentro do escalonador do SM e assim o zoom só desce. O roteiro escrito não muda.

### Fila da etapa de design (não fazer agora)
Combinado com o autor em 2026-11-10: design e visualização vêm depois de a estrutura estar aprovada.

1. Viewer: trajetória do zoom entre níveis (hoje o alvo sai da tela no meio do mergulho).
2. Viewer: esmaecer o diagrama hospedeiro quando o foco está em um diagrama embutido.
3. Viewer: o teste de determinismo falha em um ponto (diferença invisível de alguns pixels em nó esmaecido). Precisa fechar antes da captura final.
4. Diagramas: SM em paisagem; números das threads e rótulos pequenos maiores; estado "ainda sem divergência" para as 4 threads laranja.
5. Viewer: mostrar na tela a procedência por nó (hoje só o selo do beat e o aviso do diagrama aparecem).
6. Teaser: seis beats dão quase 3 minutos; a meta é de 30 a 45 s. Falta `hold` por corte ou um teaser de 3 beats.
7. Falas: a do ato 4 passa do tempo de tela (cerca de 168 s de fala para 116 s); as do ato 6 sobram.
8. Placa 3D real, explosão e os três caminhos coloridos (dependem da F2 e da F3).
9. Atos 0 a 3 (dependem da placa 3D). A tabela GPU contra CPU (a7.3) foi retirada em 2026-11-10: o enunciado não pede comparação com CPU.
10. Viewer: o texto do aviso do diagrama quebra em duas linhas e sai da faixa em alguns beats.
11. Créditos do tour (a7.6): a linha de fonte promete a lista completa de fontes com data de acesso; a lista ainda não existe na tela.
12. Cabeçalho: a trilha tem quatro nomes (Placa, Chip, SM, Conceito) e o a0.4 fala em cinco níveis.
13. Viewer 3D: esmaecimento com aspecto de vidro; a âncora não testa oclusão; `overlay.path` aceito mas sem desenho (falta o mapeamento de peças por caminho).
14. Classe do destino do cabo flat (`flex.dp`): o beat a2.10 diz "proposta nossa, provável" e `proposal.json`/`assembly.json` dizem `derived`, por um texto sobre a 5090 FE que não está em `spec/sources/`. Registrar a fonte ou descer a proposta para `inferred`.
15. O beat t1.1 (já aprovado) diz "a NVIDIA não publica"; a redação que as auditorias seguintes adotaram é "não achamos nas fontes lidas".

## 9. Feito em 2026-11-09

Manhã:
- Fontes do hardware físico e auditoria (`qa/fact-check-fisico.md`); planos v0.2 de montagem e de vídeo; `ARCHITECTURE.md` v0.2; agente `diagram-designer`; teste da pilha e custo de captura.

Tarde:
- Revisão do artigo entregue (`qa/revisao-artigo.md`) e reprodução exata do experimento dele (`examples/saxpy-cu/`).
- Fontes de MMU e interrupções (`spec/sources/mmu-interrupts-sources.md`), com os pontos centrais conferidos por leitura direta do código do driver.
- Análise RISC ou CISC revisada com a lista oficial de instruções da Blackwell.
- Normas dos conectores e da memória (`spec/sources/standards-sources.md`) e tabela `design/measurements.csv`.
- Catálogo das 75 fotos do teardown e dos renders oficiais (`spec/references/index.md`); plano de montagem v0.3.
- Schemas dos cinco contratos e validador (`schemas/`, `tools/validate.py`).
- Orçamento de tempo para 15 a 20 minutos e proposta de divisão da fala.

Noite:
- Proposta entregue em 26/10 arquivada e transcrita; divisão da fala alinhada a ela.
- Auditoria da segunda leva (`qa/fact-check-segunda-leva.md`): reprovou a primeira passada. Revisão do artigo reescrita; seções `06`, `07`, `08`, `10` e `11`, os beats e os planos corrigidos.
