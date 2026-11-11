# Roteiro conciso do seminário

Sessão de roteiro conciso, aberta em 2026-11-11 a pedido do autor: "remontar a forma de apresentar, menos palavras e fillers, de forma concisa mas que passe a informação". Seminário de 22 minutos (alvo 20), ao vivo, navegando o `tour.html` com as setas.

Divisão de donos: esta sessão cuida do texto (`harness/content/pt-BR/beats.json`) e dos campos de texto e duração (`hold`, `priority`) do `storyboard.json`. A sessão de câmera e desmontagem com GSAP cuida de `camera`, `view`, `explode_state` e da desmontagem.

**Estado: proposta, aguardando o autor. Nenhum texto foi reescrito.**

## 1. Diagnóstico do corte atual

| Medida | Hoje (48 beats do corte do seminário) |
|---|---|
| Palavras na tela (`caption`) | 1.341, cerca de 28 por beat |
| Palavras faladas (`fala`, painel N) | 2.779, cerca de 58 por beat. A 140 palavras por minuto, cerca de 20 minutos só de fala |
| Beats da placa física (atos 0 a 3) | 18 de 48, para um item que o enunciado não cobra |

O que pesa:
1. **Ressalva falada em todo beat.** "conta nossa", "não achamos nas fontes lidas", "segundo a Gamers Nexus", "é leitura nossa das fotos". O selo de procedência já está na tela e diz isso.
2. **Tela e fala repetem a mesma coisa** com palavras diferentes (a0.2, a1.5, a3.7, a5.6).
3. **Desmontagem contada passo a passo** (sete beats, a2.1 a a2.7), com detalhes que a plateia não guarda (quantos parafusos, que a fonte chama de back plate).
4. **Conflitos de fonte no palco** (192 contra 188 SMs, os dois valores da banda da Ada, carveout de 100 contra 128 KB). São rigor bom, mas cabem em resposta a pergunta.
5. **Definições que a turma já tem** (o que é MMU, interrupção, contexto) ocupam a frase de abertura de vários beats.

## 2. Proposta de regras de estilo

1. **Tela (`caption`): uma frase, até 15 palavras.** O número principal e o que ele quer dizer.
2. **Fala (`fala`): até 35 palavras**, cerca de 15 segundos. Uma ideia por beat, com a ligação à matéria quando houver ("como na CPU", "diferente da CPU").
3. **O selo carrega a procedência.** A fala não repete "conta nossa" nem "segundo a fonte" para fatos `confirmed` e `derived`. Para `inferred` a palavra **"provável"** continua obrigatória na tela e na fala (regra do projeto). Lacuna do enunciado continua dita em voz alta, uma vez, curta: "não é público".
4. **Ressalvas vão para o Q&A.** Conflitos de fonte, contas de conferência e o "por que não sabemos" ficam num bloco de respostas para perguntas, no fim deste arquivo, organizado por beat. Nada some do projeto: o artigo e os relatórios do `fact-checker` continuam valendo.
5. **Sem definição do que a turma já sabe.** Define só o que é da GPU (warp, SIMT, PTX, SASS, carveout).
6. Estilo do projeto mantido: PT-BR com acentos, sem travessão, sem ponto e vírgula, "não achamos nas fontes lidas" em vez de "a NVIDIA não publica".

## 3. Exemplos antes e depois

**a1.4, conector de energia** (placa)

- Antes, tela (35 palavras): "O conector de energia fica na borda superior, com 16 pinos. Pela norma, 12 de potência e 4 de sinal. Os 600 W são a potência total da placa. Quanto passa pelo conector, não achamos."
- Antes, fala (48): "No topo, o conector de energia, de 16 pinos. Pela norma, 12 levam potência e 4 levam sinal. Os 600 W são a potência total da placa. Se tudo viesse em 12 V, seriam cerca de 50 A, conta nossa. A variante, 12VHPWR ou 12V-2x6, está em aberto."
- Depois, tela (10): "Um conector de 16 pinos no topo alimenta 600 W."
- Depois, fala (22): "Toda a energia entra por aqui: um conector de 16 pinos, 12 de potência e 4 de sinal. A placa consome até 600 W."
- Para o Q&A: 50 A em 12 V (conta nossa), variante 12VHPWR ou 12V-2x6 em aberto.

**a5.6, registradores** (enunciado)

- Antes, tela (20): "Cada partição tem um banco de 16.384 registradores de 32 bits. Os quatro somam 65.536, ou 256 KB por SM."
- Antes, fala (68): "Numa CPU, a troca de contexto salva os registradores na memória. [...] Na placa inteira são 48.128 KB, 188 vezes 256. Como o banco é organizado por dentro, em bancos e portas, não achamos fonte para a Blackwell."
- Depois, tela (12): "65.536 registradores de 32 bits por SM: 256 KB."
- Depois, fala (33): "Na CPU, trocar de tarefa é salvar registradores na memória. Aqui todos os warps residentes já têm os seus no banco do SM. Por isso trocar de warp não custa nada."
- Para o Q&A: 48.128 KB na placa, organização interna do banco não é pública.

**a6.2, falha de página** (enunciado)

- Antes, fala (84 palavras, com definição de canal, Xid 31 e TLB).
- Depois, tela (13): "Falha de página: a GPU para o canal e o driver, na CPU, resolve."
- Depois, fala (34): "Como na CPU, a falha de página para o acesso e o sistema resolve. A diferença: quem resolve é o driver, na CPU, em lote. Depois a GPU repete o acesso."
- Para o Q&A: fault and stall, Xid 31, TLB sem fonte.

## 4. Proposta de estrutura: o enunciado como espinha

Hoje são 48 beats e cerca de 20 minutos. Proposta: **cerca de 34 beats e 18 a 19 minutos**, com folga para a troca de apresentador. O tempo sai da placa física e das ressalvas, e vai para os itens do enunciado.

| Bloco | Hoje | Proposta | Tempo alvo | O que muda |
|---|---|---|---|---|
| Abertura | a0.1 a a0.4 (4) | 2 beats: título com a placa, ficha em quatro números | 0:45 | a0.4 (mapa e selos) sai: os selos se explicam no primeiro que aparece, e o fechamento os retoma |
| Placa por fora | a1.1, a1.3, a1.4 (3) | 2: ventiladores e fluxo de ar juntos, conector | 0:45 | |
| Desmontagem | a2.1, a2.2, a2.4, a2.7 (4) | 2: a desmontagem em sequência contínua (câmera mostra os passos, uma fala), e a pasta térmica sobre o chip | 1:00 | depende da sessão de câmera: a desmontagem vira um beat com vários estágios, ou beats mudos curtos |
| Três caminhos | a2.8 a a2.11 (4) | 3: energia, dados, calor (a2.8 some, a abertura dos caminhos entra na fala da energia) | 1:15 | |
| Memória e barramento | a3.1 a a3.3 (3) | 2: memória em volta do chip (16 no verso, 32 posições, 96 GB), barramento de 512 bits e banda | 0:50 | a3.3 (como dois chips dividem um controlador, provável) vai para o Q&A |
| Planta do chip | t1.1, a4.1 a a4.5 (6) | 3: o die e "daqui é diagrama", hierarquia GPC, TPC, SM (188), L2 no centro e controladores nas bordas | 1:30 | a4.3 (conflito 192 contra 188) e a4.5 (AMP, que volta em a6.5) vão para o Q&A |
| SM e pipeline | t2.1, a5.4, a5.5, a5.3, a5.1, a5.2, a5.15, a5.16 (8) | 6: o SM, quatro partições e escalonador (pipeline), warp de 32, SIMT, ocupação, divergência | 3:00 | a5.3 (bloco para warp) entra na fala do warp. a5.4 entra em t2.1 |
| Registradores | a5.6 a a5.8 (3) | 3 | 1:45 | |
| Instruções e RISC ou CISC | a5.9 a a5.12 (4) | 3: PTX para SASS, 128 bits fixos, HMMA e o veredito do grupo juntos | 2:00 | |
| Cache | a5.13 (1) | 1 | 0:40 | |
| MMU, interrupções, escalonamento | a6.1 a a6.5 (5) | 5 | 3:15 | hoje são 3:14 de `hold` com 360 palavras de fala. Fica o tempo, cai a fala pela metade, sobra respiração para o diagrama animar |
| Fechamento | a7.1, a7.4, a7.5 (3) | 2: o que sabemos e o que falta (com os selos), Ada contra Blackwell como gancho final ou cortado | 1:00 | a7.6 créditos fica fora do corte, como hoje |
| **Total** | **48** | **cerca de 34** | **cerca de 18:30** | |

## 5. Perguntas ao autor

1. Estilo de fala: o que está no painel N é **roteiro para ler** (frases completas) ou **tópicos** para o apresentador falar com as próprias palavras?
2. Profundidade da placa física: manter cerca de 4:30 (proposta) ou encolher ainda mais em favor do chip?
3. Ressalvas: tudo bem tirá-las da fala e guardá-las num bloco de Q&A neste arquivo (ou num campo novo, o que pede mudança de schema e do viewer, que não são meus)?
4. Juntar beats muda ids e a lista de beats: preciso combinar com a sessão de câmera antes. Prefere que eu já negocie a lista acima com ela?

## 6. Combinado com a sessão de câmera

(vazio até o autor aprovar a estrutura)

## 7. Respostas para perguntas (Q&A)

(preenchido na reescrita, por beat)
