# Slides do seminário: texto na tela e nova ordem

Sessão de 2026-11-16, dia do seminário, a pedido do autor. Parte da branch `claude/happy-volta-oxiky8` (falas reescritas de hoje) e substitui o formato de "caption curta na tela, fala longa no painel".

## 1. Pedido do autor

- A reescrita só mexeu nas falas. O **slide** também tem de mudar: tudo o que vamos falar fica como texto na tela, como num PowerPoint, e a gente lê. Ninguém deve precisar decorar a fala.
- A fala tinha frases de efeito ("a energia entra pelo topo, os dados pela borda de baixo"). Dizer **por onde**: a energia entra pelo conector tal, os dados pelo PCIe, a imagem sai pelas DisplayPort.
- Pasta térmica não é o foco. Mostrar o chip e falar do chip.
- Remover **todas as tags e fontes** da tela, para sobrar espaço para informação.
- Repensar a ordem. Pode reaproveitar cenas.

## 2. O que mudou

**Viewer** (`harness/viewer/src/`)
- `callout.js`: a caixa mostra kicker (`topico`), título e **lista de tópicos** (`pontos`), com `**negrito**` e subtópico (`- `). Fonte dos tópicos 30 px, título 46 px, caixa de 700 px. A linha de chamada sai da altura do título.
- Saíram da tela: selos de procedência, linha de fonte, faixa "diagrama ilustrativo" (o diagrama ganhou a altura que ela ocupava), selo "peça fora da posição" da vitrine, selos e fontes do modo Explorar. O que é hipótese do grupo está dito no texto ("conclusão do grupo", "leitura do grupo", "não achamos nas fontes lidas").
- `controls.js`: as notas (N) mostram a fala em parágrafos.
- `layout.js`: `BOX_W` 700 e `DISC_H` 0 (o enquadramento dos diagramas e o automático da placa já usam esses valores).

**Dados**
- `content/pt-BR/beats.json`: `pontos` e `topico` nos 25 momentos e em 22 extras. `caption` só ficou nos extras que não foram convertidos. `fala` é apoio curto (60 a 100 palavras). `source_line` e `claims` seguem nos dados, só não aparecem na tela.
- `schemas/beats.schema.json` e `tools/validate.py`: até 8 tópicos, 110 palavras na tela, 32 por tópico, regra de leitura (0,4 s por palavra + 2 s) sobre os tópicos.
- `story/storyboard.json`: novo corte (priority 1), a2.1 passa a destacar o **chip** (`gpu.package`, âncora `anchor.gpu.package.1`) em vez da pasta térmica, `hold` ajustado.
- `content/pt-BR/pecas.json`: a camada 7 do Explorar usa o texto de a2.1.
- `content/pt-BR/roteiro-slides.md`: os 25 slides e as falas em texto corrido, para ler e imprimir (gerado do `beats.json`).
- `tools/smoke.cjs` e `tools/smoke-single.cjs`: conferem tópicos na tela, estouro da caixa e ausência de selo, fonte e faixa.

## 3. Nova ordem (25 momentos, cerca de 20 minutos)

| # | Beat | Slide | Cena | Fala de |
|---|---|---|---|---|
| 1 | a0.1 | Abertura: grupo, o que é uma GPU, roteiro | placa montada | Vitor |
| 2 | a1.1 | A placa por fora: tamanho, 600 W, 96 GB, PCIe, ventiladores | ventiladores | Vitor |
| 3 | a1.4 | **Energia**: conector de 16 pinos na borda de cima, adaptador 4 x 8 pinos | conector | Vitor |
| 4 | a1.5 | **Dados e imagem**: PCIe na borda de baixo, 4 DisplayPort no bracket | bracket | Vitor |
| 5 | a2.1 | Por dentro da placa (desmontagem), termina no chip | desmontagem | Vitor |
| 6 | a2.12 | **O chip GB202**: 92,2 bi de transistores, 750 mm², 188 SMs, 126 TFLOPS | chip em vitrine | Vitor |
| 7 | a3.1 | Memória própria: 96 GB GDDR7, 512 bits, ECC | memória | Arthur |
| 8 | a3.6 | Por que os dados ficam na placa: 1.792 GB/s contra 63 GB/s | memória | Arthur |
| 9 | a4.2 | GPCs, TPCs, SMs, L2 e controladores | planta do chip | João |
| 10 | t2.1 | Dentro de um SM | SM | João |
| 11 | a5.1 | Warp: 32 threads | warp | João |
| 12 | a5.2 | SIMT, divergência, 48 warps por SM | warp | João |
| 13 | a5.5 | Pipeline | SM | João |
| 14 | a5.6 | Registradores: 65.536 por SM | SM | Lorenzo |
| 15 | a5.8 | Até 255 por thread e a ocupação | código SASS | Lorenzo |
| 16 | a5.9 | CUDA C, PTX e SASS | código SASS | Lorenzo |
| 17 | a5.10 | Instrução de 128 bits | palavra de 128 bits | Lorenzo |
| 18 | a5.12 | RISC ou CISC | tabela de critérios | Lorenzo |
| 19 | a5.13 | Cache: a escada de memória | escada | Arthur |
| 20 | a5.14 | L1 e memória compartilhada | escada | Arthur |
| 21 | a6.1 | MMU | tabela de páginas | Thiago |
| 22 | a6.2 | Falha de página | interrupções | Thiago |
| 23 | a6.4 | Interrupções | interrupções | Thiago |
| 24 | a7.4 | O que achamos e o que falta | tabela de lacunas | Vitor |
| 25 | a7.5 | Resumo dos oito itens, perguntas | placa montada | Vitor |

O que mudou de lugar ou de peso em relação à ordem de hoje cedo:
- **Entram** a1.4 (energia), a1.5 (dados e imagem) e a2.12 (o chip). A placa por fora deixou de ser um slide genérico: energia, dados e imagem têm um slide cada, com o lugar exato.
- A desmontagem (a2.1) não conta mais os sete passos do teardown nem fala de pasta térmica. Diz o que há dentro (PCB, chip, memória, aletas) e termina no chip, que ganha o slide seguinte.
- O chip vem **antes** da memória e antes do mergulho nos diagramas: placa, chip, o que o cerca (memória), o que há dentro dele (GPC, TPC, SM).
- Warp e SIMT antes de pipeline (feito de manhã) e registradores logo depois, na mesma figura do SM.
- O fechamento ficou com o resumo dos oito itens, que é a tela que o professor quer ver.

Passam a extras (índice, tecla M): a2.13 (placa aberta), t1.1, a4.4, a5.16 (divergência), a5.7 (listagem SASS), a6.3 (fila de comandos). Os caminhos de energia, dados e calor (a2.9 a a2.11) seguem como extras.

## 4. Regras do texto

1. Tela: tópicos que dizem a informação, com número e unidade, de 3 a 8 por slide. Negrito no número ou termo que importa.
2. Dizer onde: "entra pelo conector de 16 pinos, na borda de cima", "sai pelas 4 DisplayPort do bracket".
3. Sem frase de efeito, sem pergunta retórica, sem metáfora solta.
4. Hipótese do grupo dita no tópico ("Conclusão do grupo", "Leitura do grupo"). Lacuna dita no tópico ("não achamos nas fontes lidas").
5. Só fatos de `spec/card.spec.json` e das auditorias anteriores. Conta mostrada no tópico (4 x 150 W = 600 W) em vez de etiqueta.
6. Sem travessão, sem ponto e vírgula.

## 5. Conferência

- `python3 harness/tools/validate.py`: ok.
- `node harness/tools/smoke-single.cjs --cut seminario`: ver resultado em `harness/STATUS.md` ou no commit.
- Auditoria de fatos do texto novo pelo `fact-checker` (agente separado): aprovado com ressalvas, quatro erros de redação e as ressalvas aplicadas. Relatório em `harness/qa/fact-check-slides.md`.
- Visual: aqui só havia o GLB de blockout (sem o detalhe do Blender). O enquadramento das cenas reaproveitadas é o de antes. **Conferir na máquina do autor** os slides 3, 4, 5 e 6, que usam cenas 3D que o corte de hoje cedo não tinha.

## 6. Pendente

- Ensaiar com cronômetro: 25 slides, cerca de 20 minutos lendo os tópicos.
- Terceira passada visual das cenas a1.4, a1.5 e a2.12 com a placa detalhada.
- Extras ainda no formato antigo (parágrafo): a0.2 a a0.4, a1.2, a4.1, a4.4, a4.5, a5.3, a5.4, a7.6, t1.1.
