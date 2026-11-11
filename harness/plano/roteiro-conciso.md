# Roteiro conciso do seminário

Sessão de roteiro conciso, aberta em 2026-11-11 a pedido do autor: "remontar a forma de apresentar, menos palavras e fillers, de forma concisa mas que passe a informação". Seminário de 22 minutos (alvo 20), ao vivo, navegando o `tour.html` com as setas.

Divisão de donos: esta sessão cuida do texto (`harness/content/pt-BR/beats.json`) e dos campos de texto e duração (`hold`, `priority`) do `storyboard.json`. A sessão de câmera e desmontagem com GSAP cuida de `camera`, `view`, `explode_state` e da desmontagem.

**Estado (2026-11-11): aprovado pelo autor e aplicado no commit b4cad83. O corte do seminário tem 27 beats e o plano de herói da sessão de câmera. Auditoria do `fact-checker` em andamento.** As seções 1 a 5 guardam a proposta original. O que vale está nas seções 5.1, 6 e 6.1.

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

## 5.1 Respostas do autor (2026-11-11)

- Ressalvas saem da fala e vão para o bloco de Q&A deste arquivo: **sim**.
- Fechar a lista de beats com a sessão de câmera: **sim**.
- Enfoque: **manter a placa**, e a explicação foca **só no que o enunciado pede de forma explícita** (registradores, instruções, CISC ou RISC, MMU, interrupções, gerenciamento de memória, pipeline, cache). Leitura confirmada: a placa é o fio visual, o texto explica só os oito itens. "Quero ser direto na apresentação."
- Formato da fala: **tópicos curtos**, separados por •, no campo `fala` (painel N).

## 6. Combinado com a sessão de câmera

Sessão irmã: `session_018iRo36DfXdjSBu15DhrohB`. Orquestradora: `session_018iRo36V6iZYhDLKo7AWJja`.

- 2026-11-11: proposta da seção 4 enviada à sessão de câmera, com pedido do plano dela (ordem, beats de desmontagem, duração mínima de câmera). Nada combinado ainda, aguardando o autor.
- 2026-11-11, resposta da câmera (o plano dela também espera o autor): desmontagem num único beat com vários estágios (cerca de 2,2 s por estágio, campo `explode_seq` dela). Câmera mínima de 2,0 s para troca pequena e 3,0 s para troca grande, parada durante o texto. Possíveis beats novos: E8 (carcaça da face B solta, `inferred`) e plano de herói explodido de cerca de 7 s antes do chip. Minha resposta: E1 a E6 num único beat com fala curta, plano de herói mudo, hold = câmera + leitura + fala.

## 6.1 Corte do seminário aplicado

Ficam (priority 1), na ordem do storyboard: a0.1 (absorve a0.2), a1.1 (absorve a1.3), a2.1 (absorve a2.7, desmontagem E1 a E7 numa fala), **a2.13** (plano de herói mudo, criado pela sessão de câmera, texto já em `beats.json`), a3.1 (absorve a3.2), a3.6, t1.1 (absorve a4.1), a4.2, a4.4, t2.1 (absorve a5.4), a5.5, a5.1 (absorve a5.3), a5.2, a5.16, a5.6, a5.7, a5.8 (absorve a5.15), a5.9, a5.10, a5.12 (absorve a5.11), a5.13, a5.14, a6.1, a6.2, a6.3, a6.4, a7.4 e a7.5.

Saem (priority 2, continuam no corte completo com o texto antigo): a0.2, a0.3, a0.4, a1.3, a1.4, a2.2, a2.4, a2.7, a2.8, a2.9, a2.10, a2.11, a3.2, a3.3, a4.1, a4.3, a4.5, a5.3, a5.4, a5.11, a5.15, a6.5 e a7.1.

Números: 390 palavras na tela (antes 1.341), 799 de tópicos na fala (antes 2.779). `hold` = 0,8 s por palavra de tópico + 4 s, com o mínimo de leitura do validador e, nos beats com fluxos animados, 60% do `hold` antigo. Tocando sozinho dá **cerca de 13:40**. Ao vivo, com cada um falando os tópicos por extenso, a estimativa é de 15 a 17 minutos.

Reserva, se o ensaio ficar curto (todas cobrem itens do enunciado): a5.15 (ocupação), a3.5 (ECC), a6.5 (AMP e escalonamento de contextos), a4.3 (conflito 192 contra 188).

Pedidos à sessão de câmera: `explode_seq` E1 a E7 em a2.1, herói a2.13 entre a2.1 e a3.1, enquadramento dos beats fundidos.

## 7. Respostas para perguntas (Q&A)

Ressalvas que saíram da fala. Use se alguém perguntar.

| Beat | Pergunta provável | Resposta curta |
|---|---|---|
| a1.1 | Por onde o ar entra? | Não achamos nas fontes lidas. A Gamers Nexus só diz que atravessa a placa e sai pelas aberturas do topo |
| a2.1 | Quantos parafusos? Para que serve a placa que cobre o PCB? E a mola? | A fonte não diz. A contagem de sete passos é nossa, e a identificação das peças vem das fotos |
| a2.1 | Não era metal líquido? | Na RTX 5090 Founders Edition é. A Gamers Nexus esperava metal líquido e achou pasta. Placa irmã é pista, não prova |
| a3.1 | São 32 chips? | 32 posições. Se todas estiverem ocupadas, 32 x 3 GB = 96 GB, que é a dedução da própria fonte. 24 x 4 GB também fecha |
| a3.1 | Como dois chips dividem um controlador? | Não achamos fonte. Proposta nossa, provável: cada chip usa 16 dos 32 bits |
| a3.6 | De onde vem o 63 GB/s? | 32 GT/s por pista (PCI-SIG), 16 pistas e codificação 128b/130b, só achada em fonte secundária. Conta nossa |
| t1.1 | O 4 de TSMC 4N é 4 nm? | Não. É o rótulo do processo, não a medida de nenhum elemento |
| a4.2 | O chip não tinha 192 SMs? | O GB202 completo tem 96 TPCs e 192 SMs. O texto da p. 8 do whitepaper diz que esta placa usa o chip completo, mas a Tab. 4 dá 188, que fecha com os 24.064 núcleos. Adotamos 188 |
| a4.2 | Como os 94 TPCs se distribuem nos 12 GPCs? | Não achamos nas fontes lidas |
| a4.4 | Quanto o L2 cresceu? | 128 MB contra 96 MB da RTX 6000 Ada, um terço a mais (conta nossa) |
| a5.5 | Por que "partição"? | O whitepaper não dá nome às quatro divisões. Partição é o nome que adotamos |
| a5.5 | E FP64? | 2 núcleos FP64 por SM, a 1/64 da taxa de FP32. Latência medida na RTX 5080: cerca de 64 ciclos |
| a5.1 | Quem decide qual SM recebe qual bloco? | O trecho do guia CUDA que lemos não diz. Lacuna declarada |
| a5.2 | O escalonador esconde a latência? | A NVIDIA diz que ele escolhe a cada ciclo um warp pronto. Que isso esconda a espera pela memória é leitura nossa |
| a5.16 | O hardware real faz exatamente isso? | É mais flexível: desde a compute capability 7.0 as threads divergem e reconvergem em grupos menores que o warp |
| a5.6 | Quanto dá na placa toda? | 188 x 256 KB = 48.128 KB. A organização interna do banco (bancos e portas) não achamos para a Blackwell |
| a5.7 | O que é o UR? | Caminho uniforme. Achamos só o nome das instruções, não o funcionamento |
| a5.8 | E a ocupação total? | 48 warps x 32 = 1.536 threads por SM, 288.768 na placa (contas nossas). A granularidade de alocação de registradores não levantamos |
| a5.9 | O que são LDC R1 e LDCU.64 UR4? | Cargas sem par no PTX, não documentadas. Hipótese nossa, sem confirmação: a LDCU.64 carrega o descritor usado em desc[UR4] |
| a5.10 | Como são usados os 128 bits? | Na Volta (Jia et al.): ao menos 91 de instrução, ao menos 23 de controle, 14 aparentemente sem uso. Na Blackwell, não documentado |
| a5.12 | Rodaram numa GPU? | Não. O SASS foi gerado com ptxas e nvdisasm, sem executar. A versão FP8, QMMA, faz 4.096 |
| a5.12 | E microcódigo? | Nada público |
| a5.13 | As latências são desta placa? | Não. Foram medidas na RTX 5080, por terceiros. Do L2 à memória, a latência sobe 2,4 vezes (conta nossa) |
| a5.14 | Se são 128 KB, por que no máximo 100? | O guia CUDA lista até 100 KB de memória compartilhada na compute capability 12.0, e o Tuning Guide fala em 128 KB por SM. A diferença não está explicada |
| a6.1 | Como se dividem os 57 bits? | Índices de 1, 9, 9, 9 e 8 bits, mais 9 no último nível para página de 4 KB, e 12 de deslocamento. Páginas de 2 MB e 512 MB terminam antes |
| a6.2 | E um acesso ilegal? | Aparece no log como Xid 31, GPU memory page fault. Enquanto o driver não atende, o canal não pode ser trocado (fault and stall) |
| a6.3 | Vale para todo programa CUDA? | Lemos só os canais do próprio driver (UVM). Supor o mesmo esquema para um programa comum é leitura nossa |
| a6.4 | O que é Xid 13? | Erro de execução do programa na GPU, que o driver registra no log |
| a7.4 | Por que a NVIDIA não publica? | Não sabemos o motivo. Dizemos só que não achamos nas fontes lidas |
| fora do corte | Quanto a placa mudou em relação à Ada? | 142 para 188 SMs (1,32x), L2 1,33x, memória e potência 2,00x (contas nossas, Tab. 4 do whitepaper) |
| fora do corte | E o MIG? | Divide a placa em 1 instância de 96 GB, 2 de 48 GB ou 4 de 24 GB |
