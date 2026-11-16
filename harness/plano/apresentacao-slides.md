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
- `callout.js`: a caixa mostra kicker (`topico`), título e **lista de tópicos** (`pontos`), com `**negrito**` e subtópico (`- `). Fonte dos tópicos 28 px, título 44 px, caixa de 740 px e até 920 px de altura. A linha de chamada sai da altura do título.
- Saíram da tela: selos de procedência, linha de fonte, faixa "diagrama ilustrativo" (o diagrama ganhou a altura que ela ocupava), selo "peça fora da posição" da vitrine, selos e fontes do modo Explorar. O que é hipótese do grupo está dito no texto ("conclusão do grupo", "leitura do grupo", "não achamos nas fontes lidas").
- `controls.js`: as notas (N) mostram a fala em parágrafos.
- `layout.js`: `BOX_W` 740 e `DISC_H` 0 (o enquadramento dos diagramas e o automático da placa já usam esses valores).

**Dados**
- `content/pt-BR/beats.json`: `pontos` e `topico` nos 30 momentos e em 22 extras. `caption` só ficou nos extras que não foram convertidos. `fala` é apoio curto (60 a 100 palavras). `source_line` e `claims` seguem nos dados, só não aparecem na tela.
- `schemas/beats.schema.json` e `tools/validate.py`: até 8 tópicos, 110 palavras na tela, 32 por tópico, regra de leitura (0,4 s por palavra + 2 s) sobre os tópicos.
- `story/storyboard.json`: novo corte (priority 1, cinco beats clonados de cenas existentes: a0.5, a0.6, a1.7, a5.17 e a6.0), a2.1 passa a destacar o **chip** (`gpu.package`, âncora `anchor.gpu.package.1`) em vez da pasta térmica, `hold` ajustado.
- `content/pt-BR/pecas.json`: a camada 7 do Explorar usa o texto de a2.1.
- `content/pt-BR/roteiro-slides.md`: os 25 slides e as falas em texto corrido, para ler e imprimir (gerado do `beats.json`).
- `tools/smoke.cjs` e `tools/smoke-single.cjs`: conferem tópicos na tela, estouro da caixa e ausência de selo, fonte e faixa.

## 3. Nova ordem (30 momentos, cerca de 22 minutos)

Segundo pedido do autor no mesmo dia: o público não sabe nada de placa de vídeo nem de arquitetura. A ordem parte do mais simples (o que é uma CPU, uma GPU e uma placa de vídeo) e define cada termo antes de usá-lo. Cada slide de conceito segue a mesma lógica: o que é, em qualquer processador, e depois o número desta GPU.

| # | Beat | Slide | Cena | Fala de |
|---|---|---|---|---|
| 1 | a0.1 | Abertura: grupo e roteiro | placa montada | Vitor |
| 2 | a0.5 | **CPU e GPU**: processador, núcleo, pixel (novo) | placa montada | Vitor |
| 3 | a0.6 | **O que é uma placa de vídeo**: placa-mãe, GPU, memória, energia, imagem (novo) | placa por outro ângulo | Vitor |
| 4 | a1.1 | A placa por fora: slot, tamanho, watts, ventiladores | ventiladores | Vitor |
| 5 | a1.4 | **Energia**: fonte, conector de 16 pinos na borda de cima, adaptador 4 x 8 pinos | conector | Vitor |
| 6 | a1.5 | **Dados**: barramento, PCIe 5.0 x16, contatos na borda de baixo | bracket e adaptador PCIe | Vitor |
| 7 | a1.7 | **Imagem**: 4 DisplayPort 2.1b no bracket, bits e bytes (novo) | bracket | Vitor |
| 8 | a2.1 | Por dentro da placa: teardown, PCB, aletas, cooler | desmontagem | Vitor |
| 9 | a2.12 | **O chip GB202**: transistor, 92,2 bi, 750 mm², clock, TFLOPS | chip em vitrine | Vitor |
| 10 | a3.1 | Memória própria: RAM, 96 GB GDDR7, barramento de 512 bits, ECC | memória | Arthur |
| 11 | a3.6 | Por que os dados ficam na placa: banda, 1.792 GB/s contra 63 GB/s | memória | Arthur |
| 12 | a4.2 | GPCs, TPCs, SMs, L2 e controladores | planta do chip | João |
| 13 | t2.1 | Dentro de um SM | SM | João |
| 14 | a5.1 | Warp: thread, bloco, 32 threads | warp | João |
| 15 | a5.2 | SIMT, divergência, 48 warps por SM | warp | João |
| 16 | a5.5 | Pipeline | SM | João |
| 17 | a5.6 | Registradores: 65.536 por SM | SM | Lorenzo |
| 18 | a5.9 | Conjunto de instruções: ISA, CUDA C, PTX e SASS | código SASS | Lorenzo |
| 19 | a5.10 | Instrução de 128 bits | palavra de 128 bits | Lorenzo |
| 20 | a5.8 | Registradores no código: R, UR, P, SR, até 255 por thread | código SASS | Lorenzo |
| 21 | a5.12 | RISC ou CISC | tabela de critérios | Lorenzo |
| 22 | a5.17 | **Gerenciamento de memória: o mapa** (novo) | escada de memória | Arthur |
| 23 | a5.13 | Cache: a escada de memória | escada | Arthur |
| 24 | a5.14 | L1 e memória compartilhada | escada | Arthur |
| 25 | a6.0 | **Memória virtual: o que a MMU faz** (novo) | tabela de páginas | Thiago |
| 26 | a6.1 | MMU: 57 bits, 6 níveis | tabela de páginas | Thiago |
| 27 | a6.2 | Falha de página | interrupções | Thiago |
| 28 | a6.4 | Interrupções | interrupções | Thiago |
| 29 | a7.4 | O que achamos e o que falta | tabela de lacunas | Vitor |
| 30 | a7.5 | Resumo dos oito itens, perguntas | placa montada | Vitor |

O que mudou de lugar ou de peso:
- **Cinco slides novos** (2, 3, 7, 22 e 25), com cenas reaproveitadas: placa montada, outro ângulo da placa, escada de memória e tabela de páginas.
- **Energia, dados e imagem** têm um slide cada, com o lugar exato. A desmontagem (a2.1) não conta mais os sete passos do teardown nem fala de pasta térmica: diz o que há dentro e termina no chip, que ganha o slide seguinte.
- **O chip vem antes da memória** e antes do mergulho nos diagramas.
- **Instruções antes dos registradores no código:** a5.8 (R, UR, P, SR) passou para depois de PTX e SASS, porque usa a listagem SASS. O diagrama das instruções fica na tela por três slides seguidos.
- **Mapa do gerenciamento de memória** (22) antes de cache e MMU, para o item do enunciado aparecer inteiro antes dos detalhes.

Se o tempo apertar (30 slides, cerca de 22 minutos lendo), os que mais cabem pular, pelas setas ou pelo índice: a5.8, a5.14 e a3.6. Fora do corte (índice, tecla M): a2.13, t1.1, a4.4, a5.16 (divergência), a5.7 (listagem SASS), a6.3 (fila de comandos) e os caminhos de energia, dados e calor.

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
- Visual: aqui só havia o GLB de blockout (sem o detalhe do Blender). O enquadramento das cenas reaproveitadas é o de antes. **Conferir na máquina do autor** os slides 3, 5, 6, 7 e 9, que usam cenas 3D que o corte de hoje cedo não tinha.

## 6. Pendente

- Ensaiar com cronômetro: 30 slides, cerca de 22 minutos lendo os tópicos. É o limite da apresentação: se passar, pular a5.8, a5.14 e a3.6
- Terceira passada visual das cenas a1.4, a1.5 e a2.12 com a placa detalhada.
- Extras ainda no formato antigo (parágrafo): a0.2 a a0.4, a1.2, a4.1, a4.4, a4.5, a5.3, a5.4, a7.6, t1.1.
