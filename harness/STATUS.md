# Acompanhamento do projeto

Data: **2026-11-09**, segunda atualização do dia. Substitui a versão da manhã.

## 1. Resumo

1. **A documentação escrita foi entregue** (artigo de 13 páginas, grupo Warp 32). A revisão está em `qa/revisao-artigo.md`: o artigo cumpre o enunciado, tem dois erros de conteúdo (MMU e RISC ou CISC) e seis afirmações acima da fonte. O seminário corrige.
2. **A pesquisa (F1) está quase fechada.** Todos os itens do enunciado têm fonte, inclusive MMU e interrupções, que estavam em branco. Falta consolidar `spec/card.spec.json` e fechar a auditoria da segunda leva.
3. **A placa física agora tem base real:** teardown, datasheet, normas dos conectores e 75 fotos catalogadas. O plano de montagem está na v0.3 e mudou bastante em relação à manhã.
4. **O seminário tem de 15 a 20 minutos.** O corte do seminário tem 42 beats e alvo de 17 minutos.
5. **Nada das fases F2 a F8 existe ainda**, além de planos, schemas e do validador. O seminário é em 7 dias.

## 2. Prazos

| Data | Entrega | Pontos | Situação |
|---|---|---|---|
| 2026-10-26 | proposta formal | 0,5 | entregue. PDF e transcrição arquivados em 2026-11-09 (`vault/01-Briefing/Proposta formal.md`). Ela compromete o tour 3D como apoio do seminário e já define a parte de cada integrante |
| 2026-11-09 | documentação escrita | 1,5 | entregue (artigo). Revisão em `qa/revisao-artigo.md`. O PDF não está versionado |
| 2026-11-16 | seminário, 15 a 20 minutos | 2,0 | plano de vídeo pronto; sem viewer, sem slides, sem ensaio |

## 3. Estado por fase

| Fase | Existe | Falta | Estado |
|---|---|---|---|
| F0 Escopo | placa, público, duração | | feito |
| F1 Pesquisa | 6 arquivos de fontes, 43 notas no vault, 3 exemplos `sm_120`, catálogo de 88 imagens, 3 auditorias | `spec/card.spec.json`; segunda passada das auditorias; guia CUDA lido por inteiro | quase fechada |
| F2 Arquitetura | `design/assembly-plan.md` v0.3, `design/measurements.csv` (33 medidas) | `proposal.json` (9 itens na fila), gate humano, `assembly.json` | não iniciada |
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
| Registradores | 07 | Tuning Guide (leitura direta), whitepaper, experimento | 64K por SM, até 255 por thread, famílias `R`, `UR`, `P`, `SR` no código real | |
| Conjunto de instruções | 08 | PTX 9.5, Binary Utilities 13.5, experimento reproduzido | CUDA, PTX e SASS lado a lado; palavra de 128 bits; cerca de 257 mnemônicos | reconferir a contagem |
| CISC ou RISC | 08 | lista oficial de instruções | "RISC no formato, com instruções de acelerador" | **aprovação humana da conclusão** |
| MMU | 10 | código aberto do driver (leitura direta), documento da Pascal | 57 bits, 6 níveis, páginas de 4 KB a 512 MB; comparação com a Pascal | TLB é lacuna declarada; auditoria |
| Interrupções | 11 | driver, PTX, catálogo de Xid | três mecanismos: MSI ou MSI-X para a CPU, `trap`, preempção | como a CPU envia comandos (falta ler) |
| Gerenciamento de memória | 03, 09, 10 | whitepaper, driver, normas | GDDR7, hierarquia, falha de página em lote | memória unificada no guia CUDA |
| Pipeline | 05, 06, 12 | Tuning Guide, guia CUDA, artigos | 48 warps por SM, 4 partições (`derived`), divergência com o logotipo do grupo | profundidade do pipeline é lacuna declarada |
| Cache | 09 | whitepaper, artigo da RTX 5080 | tamanhos (`confirmed`) e latências (`derived`) | política e associatividade: lacuna |

## 5. Pendências de planejamento

| # | Item | Situação |
|---|---|---|
| 1 | Plano de montagem genérico | resolvido: `design/assembly-plan.md` v0.3, baseado em teardown e fotos |
| 2 | Fontes físicas | resolvido, com auditoria aplicada (`qa/fact-check-fisico.md`) |
| 3 | Dono dos diagramas do chip | resolvido: `diagram-designer`, tipo B, confirmado |
| 4 a 8 | Vídeo, texto por beat, atos, fidelidade, contratos | resolvidos nos planos |
| 9 | Duração do seminário | resolvido: 15 a 20 minutos |
| 10 | Quem apresenta cada bloco | resolvido: segue a definição de tarefas da proposta entregue (`story/video-plan.md`, seção 6). Três ajustes pequenos aguardam o grupo |
| 11 | Schemas dos contratos | resolvido: `schemas/` e `tools/validate.py` |
| 12 | Skills a escrever | aberto: nesta semana só `viewer-scaffold`, `chip-diagram-kit` e `build123d-gpu-parts` |
| 13 | Normas | resolvido em parte: `spec/sources/standards-sources.md`. A norma PCIe aberta é a revisão 3.0; a bracket de dois slots e o receptáculo DisplayPort não têm desenho de fonte forte |
| 14 | Catálogo de fotos | resolvido: `spec/references/index.md`. Faltam vistas ortogonais oficiais, a frente do PCB e o interior do cooler |
| 15 | Plano de reserva do seminário | planejado, falta executar |
| 16 | Slides e ensaio | aberto |
| 17 | Regra de procedência para observação de terceiro | aberto: por ora `derived` |
| 18 | Memória: 32 posições ou 32 chips | a norma permite 32 chips de 3 GB; a frente do PCB nunca foi fotografada sem pads. Fila da F2 |
| 19 | Altura da placa | aberto: 137,2 mm oficiais contra 122 mm de carcaça medidos em foto de terceiro |
| 20 | Auditoria da segunda leva (MMU, normas, revisão do artigo, RISC ou CISC) | em andamento |

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

1. **Aprovar a conclusão RISC ou CISC** revisada (`vault/03-Roteiro/08`).
2. **Divisão da fala:** já segue a proposta entregue. Faltam três ajustes pequenos (`story/video-plan.md`, seção 6): dono da planta do chip, posição do beat da divergência e o tempo do Arthur.
3. **Como tratar as correções ao artigo** no seminário: apresentar como avanço (recomendado) ou não mencionar.
4. **Tamanho do grupo:** a proposta entregue e o artigo têm cinco integrantes; a nota do enunciado no vault diz até quatro. Corrigir a nota?
5. **Versionar o PDF do artigo?** A proposta entregue já foi versionada a seu pedido. O artigo traz os mesmos nomes completos; depende de o repositório ser público.
6. Viewer ao vivo ou vídeo corrido (recomendado: ao vivo, com MP4 de reserva).
7. Logos da NVIDIA no modelo (recomendado: não).
8. Regra de procedência para observação direta por terceiro.
9. Os 15 a 20 minutos incluem perguntas?

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
