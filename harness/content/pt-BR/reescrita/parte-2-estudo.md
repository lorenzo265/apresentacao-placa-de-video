# Roteiro de estudo, parte 2: o SM, o pipeline, os registradores e as instruções

Momentos, na ordem do corte do seminário: t2.1, a5.5, a5.1, a5.2, a5.16, a5.6, a5.7, a5.8, a5.9, a5.10, a5.12. Antes vem a a4.4 (L2 e controladores de memória) e depois vem a a5.13 (a escada de memória e os caches).

Itens do enunciado cobertos aqui: **pipeline** (a5.5, com apoio de a5.1, a5.2 e a5.16), **conjunto de registradores** (a5.6, a5.7, a5.8), **conjunto de instruções** (a5.9, a5.10) e **CISC ou RISC** (a5.12).

Como ler as fontes citadas:
- **whitepaper**: NVIDIA, *RTX PRO Blackwell GPU Architecture* v1.1. Fala do chip desta placa.
- **guia CUDA**: NVIDIA, *CUDA Programming Guide* 13.5. Fala de todas as GPUs NVIDIA atuais.
- **Tuning Guide**: NVIDIA, *Blackwell Tuning Guide* 13.5. Dá os limites da compute capability 12.0, que é a desta placa.
- **Binary Utilities**: NVIDIA, *CUDA Binary Utilities* 13.5. Lista oficial das instruções SASS da Blackwell.
- **PTX ISA**: NVIDIA, manual do PTX.
- **Jarmusch et al.**: artigo que mediu a RTX 5080, placa irmã da mesma família. O que vem dele é `derived`, não medido nesta placa.
- **Jia et al.**: artigo de 2018 sobre a geração Volta. `derived`.
- **Huerta et al.**: artigo de 2025 sobre a geração Ampere. `derived`.
- **experimento do grupo**: os programas compilados em `harness/examples/` com as ferramentas oficiais, sem rodar numa GPU.

---

## t2.1 · Dentro de um dos 188 SMs

**Na tela:** o diagrama do SM inteiro (redesenho da Fig. 5 do whitepaper). Acesos: os quatro escalonadores ("L0 i-Cache + Warp Scheduler"), os quatro bancos de registradores e a faixa do L1 de 128 KB. No topo, os contadores 4 partições, 128 núcleos CUDA, 65.536 registradores e 256 KB.

**Fala:** Saímos da planta do chip e entramos em um dos 188 SMs, sigla de Streaming Multiprocessor, que é o bloco do chip que executa os programas. Um núcleo de processador comum repete sempre a mesma rotina: lê uma instrução, busca os números, faz a conta e guarda o resultado. O SM tem as peças dessa rotina, acesas na tela: o escalonador, que escolhe a próxima instrução, o banco de registradores, que guarda os números em uso, e o cache L1, uma memória pequena e rápida de 128 KB, perto das contas. A diferença está na quantidade: o SM tem 128 núcleos CUDA, e cada núcleo faz, a cada ciclo, que é uma batida do relógio do chip, uma conta simples de número inteiro ou de número com vírgula. Esses 128 núcleos estão divididos em 4 partições iguais, e cada partição tem o seu escalonador, o seu banco de registradores, os seus 32 núcleos e 1 Tensor Core, uma unidade que faz contas de matrizes. Embaixo, comum às quatro partições, fica o RT Core, a unidade de traçado de raios, usada em imagens 3D. Nossa leitura do porquê: a GPU aplica a mesma conta a muitos dados, e repetir muitas unidades simples é o jeito de fazer muitas contas ao mesmo tempo. Para entender como essas unidades recebem trabalho, começamos pelo escalonador e pelo pipeline.

**Palavras novas**
- **SM (Streaming Multiprocessor):** o bloco do chip que executa os programas. A placa tem 188.
- **Escalonador:** a parte que escolhe qual instrução vai ser executada a seguir.
- **Registrador:** memória minúscula e muito rápida dentro do circuito, que guarda um número em uso.
- **Cache L1:** memória pequena e rápida dentro do SM, que guarda cópias de dados usados há pouco.
- **Núcleo CUDA:** unidade que faz uma conta simples por ciclo, de inteiro ou de número com vírgula (FP32 ou INT32).
- **Ciclo:** uma batida do relógio do chip. Tudo no chip anda no ritmo dessas batidas.
- **Tensor Core:** unidade especializada em multiplicar blocos de matrizes.
- **RT Core:** unidade especializada em traçado de raios, usada para gerar imagens 3D.

**Perguntas prováveis**
1. *Por que 188 SMs se o chip tem 192?* A tabela do whitepaper dá 188 para esta placa, e 188 × 128 = 24.064 núcleos, igual ao datasheet. O texto da p. 8 diz que a placa usa o chip completo, de 192. O whitepaper não explica a diferença. Fonte: whitepaper, p. 8 e Tab. 4.
2. *O núcleo CUDA faz conta de inteiro e de ponto flutuante ao mesmo tempo?* Não. Ele opera como FP32 ou como INT32, um tipo em cada ciclo. Fonte: whitepaper, p. 11.
3. *O SM é igual a um núcleo de CPU?* Tem as mesmas peças básicas (escalonador, registradores, cache), mas com muito mais unidades de conta e executando grupos de 32 threads de uma vez. A comparação é nossa, para dar uma ideia. Fonte: whitepaper, Fig. 5.

---

## a5.5 · Pipeline: uma linha de montagem de instruções

**Na tela:** o mesmo SM, agora com as quatro partições em foco e os quatro escalonadores acesos. Contador "4 partições". A caixa de texto aponta o escalonador da partição 1 ("Dispatch (32 thread/clk)").

**Fala:** Pipeline é o jeito de executar instruções como numa linha de montagem, com postos: buscar a instrução, decodificar, que é entender o que ela pede, executar a conta e guardar o resultado. Enquanto uma instrução está na conta, a seguinte já está sendo decodificada, então vários postos trabalham ao mesmo tempo, mas se uma instrução precisa do resultado da anterior, ela espera, e a linha fica com um buraco. Na GPU, cada uma das 4 partições do SM tem o seu escalonador de warp, e warp é um grupo de 32 threads, que são pequenas tarefas, cada uma com os seus próprios dados. A cada ciclo, o escalonador escolhe um warp que está pronto e despacha a mesma instrução para as 32 threads dele, e com as quatro partições o SM despacha até 128 threads por ciclo, conta nossa. Numa placa irmã, a RTX 5080, pesquisadores mediram 4 ciclos até uma conta simples de inteiro ou de número com vírgula ficar pronta. O guia da NVIDIA diz que trocar de warp não tem custo, e nossa leitura é que o escalonador usa isso para tapar os buracos da linha com instruções de outros warps. Quantos estágios o pipeline tem e como o escalonador escolhe entre os warps prontos, não achamos nas fontes lidas: um estudo da geração Ampere descreve as etapas, mas não diz quantas são. Para entender de onde vêm tantos warps prontos, vamos olhar o warp de perto.

**Palavras novas**
- **Pipeline:** execução em etapas sobrepostas, como uma linha de montagem: várias instruções em andamento, cada uma num posto.
- **Decodificar:** ler a instrução e descobrir o que ela pede e com quais operandos.
- **Thread:** uma pequena tarefa, uma sequência de instruções com os seus próprios dados.
- **Warp:** grupo de 32 threads que recebe a mesma instrução ao mesmo tempo.
- **Despachar (ou emitir):** mandar a instrução para as unidades que vão executá-la.
- **Latência:** tempo entre começar uma operação e o resultado ficar pronto. Aqui, medida em ciclos.

**Perguntas prováveis**
1. *Quantos estágios tem o pipeline da Blackwell?* Não achamos nas fontes lidas. A NVIDIA não descreve os estágios no whitepaper. Huerta et al. descrevem, para a geração Ampere, as etapas de busca, decodificação, emissão e duas etapas intermediárias (Control e Allocate) antes da leitura de operandos, mas não dão a profundidade total. Fonte: lacuna `pipeline.depth` do spec. Huerta et al., seções 5.1 e 5.3.
2. *Os 4 ciclos foram medidos nesta placa?* Não. Foram medidos na RTX 5080 (chip GB203, mesma família). Por isso o selo é `derived`. Fonte: Jarmusch et al., Tab. III. No mesmo artigo, uma conta FP64 levou cerca de 63,6 ciclos.
3. *Quanto tempo dura um ciclo?* O clock de boost desta placa é 2.617 MHz, ou seja, cerca de 2,6 bilhões de ciclos por segundo. Um ciclo dura perto de 0,38 nanossegundo (conta nossa: 1 ÷ 2,617 GHz). Fonte: whitepaper, Tab. 4.
4. *Como o escalonador escolhe o warp?* O guia CUDA só diz que, a cada ciclo de emissão, ele escolhe um warp com threads prontas. A regra exata não achamos nas fontes da NVIDIA. Huerta et al. propõem uma regra para a Ampere, medida, não oficial. Fonte: guia CUDA 13.5, 3.2.2.2.

---

## a5.1 · Um warp: 32 threads que andam juntas

**Na tela:** o diagrama do warp: 32 quadrados numerados de 0 a 31. Os de 28 a 31 são laranja. Embaixo, os contadores "32 threads por warp", "até 48 warps por SM" e "1.536 threads por SM". A caixa aponta a thread 7.

**Fala:** Quem programa a GPU escreve o código pensando numa única thread, por exemplo: pegue o elemento número i de um vetor e multiplique por 2. Depois manda rodar esse mesmo código milhares de vezes, e cada cópia, que é uma thread, recebe um número diferente, então cada uma cuida de um elemento. As threads são lançadas em blocos, e o SM que recebe um bloco o divide em warps de 32 threads com números seguidos: o primeiro warp leva as threads de 0 a 31, o segundo, de 32 a 63, e assim por diante. Os 32 quadrados da tela são as threads de um warp, e a documentação da NVIDIA fixa o warp em 32 threads em todas as arquiteturas que ela cobre. Numa CPU, quem decide qual thread roda em cada momento é o sistema operacional, que é um programa, e na GPU essa escolha é feita pelo próprio circuito, o escalonador de warp, a cada ciclo. A vantagem de agrupar, na nossa leitura, é dividir o custo de controle: a instrução é buscada e decodificada uma vez e serve para 32 threads. As quatro threads laranja no canto vão mostrar, daqui a pouco, o que acontece quando o warp precisa tomar uma decisão. Antes disso, vamos ver como uma só instrução serve para 32 threads que têm dados diferentes.

**Palavras novas**
- **Bloco de threads:** conjunto de threads que o programa lança junto e que vai inteiro para um SM.
- **Sistema operacional:** o programa que gerencia o computador (Windows, Linux) e decide o que roda na CPU.

**Perguntas prováveis**
1. *Por que 32?* O manual do PTX diz que o tamanho do warp (WARP_SZ) é 32 em todas as arquiteturas que ele cobre. O motivo da escolha do número não achamos nas fontes lidas. Fonte: PTX ISA, 2.2.1 e 4.5.1.
2. *Quem decide qual SM recebe qual bloco?* O trecho lido do guia CUDA diz só que o SM recebe blocos e os divide em warps. Quem distribui os blocos entre os 188 SMs, e com que regra, não achamos. Fonte: guia CUDA 13.5, 3.2.2.2. Lacuna `sched.block_to_sm`.
3. *Como o bloco é dividido?* Sempre do mesmo jeito: cada warp tem threads de números seguidos e crescentes, e o primeiro warp contém a thread 0. Fonte: guia CUDA 13.5, 3.2.2.2.

---

## a5.2 · SIMT: uma instrução, 32 threads

**Na tela:** o mesmo warp, com as threads acesas e o contador "até 48 warps por SM" em destaque. A caixa aponta a thread 15.

**Fala:** Imagine um professor que dita uma conta para 32 alunos, e cada aluno faz a conta com os números do seu próprio caderno. A NVIDIA chama esse modelo de SIMT, sigla em inglês para uma instrução, muitas threads: o escalonador manda uma instrução, e as 32 threads do warp a executam, cada uma com os seus dados. Existe um modelo parecido, o SIMD, uma instrução, muitos dados, em que uma instrução opera sobre uma fileira de números de uma vez. A diferença, segundo o guia de programação da NVIDIA, é que no SIMT cada thread guarda o seu próprio estado: os seus registradores e o seu contador de programa, que marca em que instrução ela está. Aqui a comparação com a sala de aula deixa de valer, porque cada thread pode, se os seus dados pedirem, seguir por outro trecho do programa. Cada SM mantém até 48 warps ao mesmo tempo, ou 1.536 threads, conta nossa, e o estado de todos eles fica guardado dentro do chip. A vantagem, na nossa leitura de como o guia descreve o escalonador, é que quando um warp para esperando um dado da memória, o escalonador passa para outro warp que já tem o que precisa, e o SM não fica parado. Quando as threads de um mesmo warp seguem caminhos diferentes, acontece a divergência, que as quatro threads laranja vão mostrar agora.

**Palavras novas**
- **SIMT (Single Instruction, Multiple Threads):** uma instrução executada por muitas threads, cada uma com o seu estado.
- **SIMD (Single Instruction, Multiple Data):** uma instrução que opera sobre um vetor de dados de uma vez.
- **Contador de programa:** registrador que guarda o endereço da próxima instrução de uma thread.

**Perguntas prováveis**
1. *As 1.536 threads executam todas ao mesmo tempo?* Não. Elas estão residentes no SM, com o estado guardado. A cada ciclo, cada uma das 4 partições despacha uma instrução para 32 threads. Fonte: Tuning Guide 13.5, 1.4.1.1 (48 warps). Whitepaper, Fig. 5 (32 threads por ciclo por partição). Conta nossa: 48 × 32.
2. *Esconder a espera da memória é dado oficial?* O guia diz que o contexto de cada warp fica no chip e que trocar de warp não tem custo, e que a cada ciclo o escalonador escolhe um warp pronto. Que isso serve para esconder a espera é a nossa leitura. Fonte: guia CUDA 13.5, 3.2.2.2.
3. *Quantas threads a placa inteira mantém?* 1.536 × 188 = 288.768, conta nossa. Fonte: Tuning Guide 13.5 e whitepaper, Tab. 4.

---

## a5.16 · Divergência: o warp percorre os dois caminhos

**Na tela:** o mesmo warp, mais de perto. As threads 0 a 27 em uma cor e as 28 a 31 em laranja. A caixa aponta a thread 31, com a nota "Seguiu o outro caminho do desvio".

**Fala:** Todo programa tem decisões do tipo se isso for verdade, faça aquilo, senão, faça outra coisa, e em programação isso se chama desvio, ou if. Numa CPU, cada thread decide sozinha, mas num warp as 32 threads executam a mesma instrução e cada uma decide com os seus próprios dados, então elas podem discordar. Na tela, as threads de 0 a 27 seguiram um caminho, e as quatro laranja, de 28 a 31, seguiram o outro. Segundo o guia de programação da NVIDIA, o warp executa cada caminho tomado, um depois do outro, e desliga as threads que não estão naquele caminho. O custo é o tempo: enquanto as quatro laranja trabalham, as outras 28 esperam paradas, e o warp gasta o tempo dos dois caminhos. Desde a compute capability 7.0, que é o número que a NVIDIA usa para cada geração de GPU, e esta placa é 12.0, cada thread tem o seu próprio contador de programa, e a GPU pode reagrupar as threads ativas e juntá-las de novo em grupos menores que o warp. A lição para quem programa, na nossa leitura, é fazer as threads de um mesmo warp seguirem o mesmo caminho sempre que der. As quatro threads laranja também são o logo do nosso grupo, o Warp 32, e cada uma delas guarda os seus valores em registradores, que são o próximo assunto.

**Palavras novas**
- **Desvio (if):** ponto do programa em que o caminho depende de uma condição.
- **Divergência:** quando threads do mesmo warp seguem caminhos diferentes num desvio.
- **Compute capability:** número da NVIDIA que identifica a geração e os recursos de uma GPU. Esta placa é 12.0.

**Perguntas prováveis**
1. *Antes da 7.0 era diferente?* Sim. O warp tinha um único contador de programa para as 32 threads, com uma máscara dizendo quais estavam ativas. Fonte: guia CUDA 13.5, 3.2.2.1.1.
2. *Com o contador por thread, a divergência deixou de custar?* O guia diz que o warp executa cada caminho tomado, desabilitando as threads de fora. O contador por thread permite reagrupar e reconvergir em grupos menores que o warp, mas não achamos nas fontes que o custo dos dois caminhos desapareça. Fonte: guia CUDA 13.5, 3.2.2.1 e 3.2.2.1.1.
3. *Como a GPU sabe quais threads estão desligadas?* Antes da 7.0, por uma máscara de threads ativas (guia CUDA, 3.2.2.1.1). Como isso é feito no circuito da Blackwell, não achamos nas fontes lidas.

---

## a5.6 · Registradores: 65.536 em cada SM

**Na tela:** o SM com os quatro bancos de registradores acesos. A caixa aponta o banco da partição 1 ("16.384 × 32 bits"). No topo, 65.536 e 256 KB.

**Fala:** Um registrador é a memória mais rápida de um processador: uma pequena caixa dentro do próprio circuito, que guarda um número enquanto ele está sendo usado numa conta. As contas pegam os números nos registradores e devolvem o resultado num registrador, porque buscar na memória principal leva muito mais tempo, como vamos ver na parte de memória. Nesta GPU, cada registrador tem 32 bits, e cada uma das 4 partições do SM tem um banco com 16.384 registradores, como mostra a figura oficial. Somando os quatro bancos, são 65.536 registradores por SM, ou 256 KB, o dobro dos 128 KB do cache L1 do mesmo SM. Numa CPU, quando o sistema operacional troca uma thread por outra, ele copia os registradores da que sai para a memória e traz os da que entra. Na GPU, segundo o guia da NVIDIA, o banco é repartido entre os warps que estão no SM, cada warp fica com os seus registradores enquanto existir, e por isso trocar de warp não tem custo. Nossa leitura é que esse é o motivo de o banco ser tão grande: ele guarda ao mesmo tempo o estado de dezenas de warps. Para ver esses registradores num programa de verdade, compilamos um exemplo pequeno e olhamos o código que a placa executa.

**Palavras novas**
- **Banco de registradores:** o conjunto físico de registradores de uma partição.
- **Bit:** um zero ou um. Um registrador de 32 bits guarda um número de 32 zeros e uns.
- **Troca de contexto:** salvar o estado de uma tarefa e carregar o de outra, para revezar o processador.

**Perguntas prováveis**
1. *Como os 256 KB viram 65.536?* Cada registrador tem 32 bits, ou 4 bytes. 256 KB ÷ 4 B = 65.536. O Tuning Guide confirma: "64K 32-bit registers per SM". E 4 × 16.384 = 65.536, pela Fig. 5. Fonte: whitepaper, p. 9 e Fig. 5. Tuning Guide 13.5, 1.4.1.1.
2. *Quanto dá na placa toda?* 188 × 256 KB = 48.128 KB, valor que a Tab. 4 do whitepaper também traz.
3. *A troca de programa inteiro também não tem custo?* Não. "Sem custo" vale para trocar entre warps que já estão no SM. Trocar o programa inteiro (preempção) salva o contexto na memória, segundo o documento da geração Pascal. São dois níveis diferentes. Fonte: guia CUDA 13.5, 3.2.2.2. Revisão do artigo, item F9.
4. *Como o banco é organizado por dentro (portas, sub-bancos)?* Na Blackwell não achamos nas fontes lidas. Há medidas da Volta (dois bancos de 64 bits por partição, Jia et al.) e da Ampere (Huerta et al.), que são de outras gerações. Lacuna `regfile.organization`.

---

## a5.7 · Registradores num programa de verdade

**Na tela:** o diagrama com três colunas: CUDA C, PTX e SASS do SAXPY. As linhas do SASS acesas. A caixa aponta a linha `0060 ISETP.GE.AND P0, PT, R7, UR5, PT`.

**Fala:** O exemplo é o SAXPY, um programa curto que, para cada posição de dois vetores, faz y receber a vezes x mais y, e nós o compilamos para o alvo desta placa, o sm_120, com as ferramentas oficiais da NVIDIA. A coluna da direita é o SASS, o código de máquina que a placa executa, e nele cada registrador aparece com uma letra que diz o tipo. R são os registradores comuns, um conjunto para cada thread: R2 recebe o valor de x daquela thread e R7, o valor de y. UR é o que a documentação chama de registrador uniforme, e, segundo um estudo da geração Ampere, ele guarda um valor igual para o warp inteiro, como aqui o UR6, que guarda o número a, e a instrução FFMA calcula UR6 vezes R2 mais R7 numa só operação. SR são registradores especiais que o próprio hardware preenche: na instrução S2R, cada thread lê o seu número, SR_TID.X, e é assim que ela sabe qual elemento do vetor é dela. P é um registrador de predicado, que guarda o resultado de uma comparação: a linha em destaque, ISETP, compara o número da thread com o tamanho do vetor e grava a resposta em P0, e a linha seguinte encerra as threads que passaram do fim. O compilador informou 10 registradores por thread e zero bytes de spill, que é quando faltam registradores e valores precisam ir para a memória, que é bem mais lenta. Esse número 10 importa, porque decide quantos warps cabem no SM ao mesmo tempo.

**Palavras novas**
- **SAXPY:** conta clássica de teste: y recebe a vezes x mais y, para cada posição de dois vetores.
- **SASS:** o código de máquina que a GPU executa. A NVIDIA chama de "CUDA assembly".
- **sm_120:** o nome do alvo de compilação desta placa (compute capability 12.0).
- **Registrador uniforme (UR):** registrador com um valor só para o warp inteiro.
- **Registrador especial (SR):** registrador que o hardware preenche, como o número da thread.
- **Predicado (P):** registrador de um bit que guarda verdadeiro ou falso, e pode ligar ou desligar uma instrução.
- **Spill:** quando faltam registradores e o compilador guarda valores na memória.

**Mapa da listagem (para responder com segurança)**
- `S2R R0, SR_TID.X`: número da thread dentro do bloco.
- `S2UR UR4, SR_CTAID.X`: número do bloco, num registrador uniforme.
- `LDC R7, c[0x0][0x360]`: tamanho do bloco (blockDim.x).
- `IMAD R7, R7, UR4, R0`: i = tamanho do bloco × número do bloco + número da thread.
- `LDCU UR5 ...` guarda n, `ISETP.GE.AND P0 ...` testa i ≥ n, `@P0 EXIT` encerra quem passou do fim.
- `LDCU UR6 ...` guarda a. `LDG.E R2` lê x[i], `LDG.E R7` lê y[i]. `FFMA R7, R2, UR6, R7` faz a × x + y. `STG.E` grava y[i].
- A correspondência entre deslocamento no banco de constantes e parâmetro é leitura nossa (`derived`), pela ordem e tamanho dos parâmetros. Fonte: `harness/examples/saxpy-cu/README.md`.

**Perguntas prováveis**
1. *Vocês rodaram isso na placa?* Não. Compilamos para o alvo sm_120 com `nvcc` e desmontamos com `cuobjdump` (versão 13.5), sem GPU. O código é o que a placa executaria. Fonte: `harness/examples/saxpy-cu/README.md`.
2. *E o registrador RZ, que vale sempre zero?* Ele não aparece nesta listagem, então não citamos. Fonte: revisão do artigo, item F4.
3. *O que fazem as duas instruções sem par no código C (`LDC R1, c[0x0][0x37c]` e `LDCU.64 UR4, c[0x0][0x358]`)?* A função delas não está documentada. Nossa hipótese é que a segunda carrega o descritor de memória usado em `desc[UR4]`, mas isso é inferência. Lacuna `isa.ldc_ldcu_saxpy`.

---

## a5.8 · Mais registradores por thread, menos warps

**Na tela:** o mesmo diagrama, com foco nos contadores: "20 instruções PTX", "10 registradores por thread", "até 255 registradores por thread (limite)" e "65.536 registradores por SM".

**Fala:** Numa CPU, a quantidade de registradores é fixa e faz parte da definição do processador, então todo programa vê o mesmo número. Na GPU, quem decide quantos registradores cada thread usa é o compilador, e o limite oficial é de 255 por thread. Só que o banco do SM é um só, com 65.536 registradores, e ele é repartido entre todos os warps que estão no SM. Faça a conta: um warp de 32 threads com 255 registradores cada gasta 8.160 registradores, e 65.536 dividido por 8.160 dá só 8 warps no SM, conta nossa, que ignora regras de arredondamento da alocação que não achamos nas fontes lidas. Já o SAXPY, com 10 registradores por thread, gasta 320 por warp, e daria para mais de 200 warps, mas aí vale outro limite oficial: no máximo 48 warps por SM. Com só 8 warps, o escalonador tem menos opções para trocar quando um warp para esperando a memória, e por isso, na nossa leitura, o compilador tenta gastar poucos registradores. É uma troca: mais registradores por thread evitam o spill, e menos registradores deixam caber mais warps. Esses registradores aparecem dentro das instruções, e o próximo passo é o conjunto de instruções em si.

**Palavras novas**
- **Ocupação:** quantos warps estão residentes num SM em relação ao máximo de 48.
- **Compilador:** programa que traduz o código escrito por pessoas para o código da máquina.

**Contas, passo a passo**
- 255 × 32 = 8.160 registradores por warp. 65.536 ÷ 8.160 = 8,03, ou seja, 8 warps.
- 10 × 32 = 320 por warp. 65.536 ÷ 320 = 204,8. O limite oficial de 48 warps vence.
- 8 warps é 1/6 do máximo de 48.

**Perguntas prováveis**
1. *De onde vem o 255?* Do Blackwell Tuning Guide: "The maximum number of registers per thread is 255." Huerta et al. falam em 1 a 256 por warp na Ampere, mas vale o número oficial. Fonte: Tuning Guide 13.5, 1.4.1.1.
2. *A conta de 8 warps é exata?* É aproximada. A alocação real de registradores tem regras de arredondamento que não achamos nas fontes lidas.
3. *O programador controla isso?* O compilador decide, e o número aparece na saída do `ptxas -v` ("Used 10 registers"). Como o programador pode limitar esse número não está nas fontes que lemos, então não afirmamos detalhes.

---

## a5.9 · Do código em C ao código da máquina

**Na tela:** as colunas PTX e SASS lado a lado, com setas ligando cada linha PTX à instrução SASS correspondente. A caixa aponta `0120 EXIT`.

**Fala:** Conjunto de instruções é a lista de ordens que um processador entende, como somar, comparar, ler da memória ou pular para outro ponto do programa. Na NVIDIA, ele existe em duas camadas, e a tela mostra as duas lado a lado, depois do código em C. A primeira é o PTX, que a documentação chama de máquina virtual: um processador descrito no papel, com um conjunto de instruções estável entre gerações de GPU. A segunda é o SASS, o código de máquina de uma geração específica, que nesta placa se chama sm_120, e quem traduz o PTX para o SASS é a ferramenta ptxas ou o próprio driver da placa. As duas camadas existem porque o SASS é feito para uma geração, e o guia da NVIDIA avisa que um programa entregue sem PTX não tem garantia de rodar em GPUs futuras. No SAXPY, as 20 instruções PTX viraram 19 instruções SASS úteis: duas conversões de endereço sumiram, uma multiplicação e duas somas de endereço viraram duas IMAD.WIDE, e apareceram duas instruções sem par no PTX, cuja função não achamos documentada. As setas ligam cada linha PTX à instrução SASS que ela virou, e a última instrução útil é o EXIT, que encerra a thread. Agora vamos abrir uma dessas instruções SASS e ver o que ela tem por dentro.

**Palavras novas**
- **Conjunto de instruções (ISA):** a lista de instruções que um processador entende e o formato delas.
- **PTX:** a ISA virtual da NVIDIA, estável entre gerações.
- **Máquina virtual:** processador definido só em documento, que é traduzido para um processador real.
- **ptxas:** ferramenta da NVIDIA que traduz PTX para SASS.
- **Driver:** o programa que controla a placa a partir do sistema operacional.

**A conta 20 → 19**
- 20 instruções PTX.
- As duas `cvta.to.global` somem: −2.
- `mul.wide` mais duas `add.s64` (3 instruções) viram duas `IMAD.WIDE`: −1.
- Aparecem `LDC R1, c[0x0][0x37c]` e `LDCU.64 UR4, c[0x0][0x358]`, sem par no PTX: +2.
- 20 − 2 − 1 + 2 = 19. A listagem tem 32 instruções no total: depois do `EXIT` vêm uma `BRA` e 12 `NOP`. Fonte: `harness/examples/saxpy-cu/README.md` e nota da seção 08 do roteiro.

**Perguntas prováveis**
1. *Quando a tradução PTX para SASS acontece?* O manual do PTX diz que os programas PTX são traduzidos "at install time" para o conjunto de instruções do hardware. O guia CUDA C++ 12.9.1 diz que o PTX carregado em tempo de execução é compilado pelo driver (compilação just-in-time). No nosso experimento, quem traduziu foi o `nvcc`, que chama o `ptxas`. Fontes: PTX ISA 9.5, 1.1. Guia CUDA C++ 12.9.1, 6.1.1.2. Guia CUDA 13.5, 2.7.2.
2. *O PTX é igual em todas as gerações?* É estável e versionado. O nosso é a versão 9.5. Dizer "igual" seria impreciso. Fonte: PTX ISA, 1.2. Revisão do artigo, item F8.
3. *Por que o mesmo programa SASS não roda em qualquer GPU NVIDIA?* O guia CUDA diz que só com o PTX embutido o programa é compatível com GPUs futuras. Sem PTX, não há essa compatibilidade. Fonte: guia CUDA 13.5, 2.7.3.1.

---

## a5.10 · Toda instrução tem o mesmo tamanho: 128 bits

**Na tela:** a instrução `FFMA R7, R2, UR6, R7` com as duas palavras de 64 bits em hexadecimal (`0x0000000602077c23` e `0x004fca0008000007`), a faixa "16 bytes = 128 bits por instrução", os campos da Volta (≥ 91 bits de instrução, ≥ 23 de controle, 14 sem uso, opcode de 10 a 13 bits, predicado de 4 bits) e o aviso "Bits de controle, no sm_120: não documentados".

**Fala:** Toda instrução, no fim, é uma sequência de bits, zeros e uns, e um processador pode usar instruções de tamanho variável ou de tamanho fixo. Com tamanho variável, o circuito precisa ler parte da instrução para saber onde ela termina e a próxima começa, e com tamanho fixo ele já sabe de antemão. Nesta placa, todas as instruções SASS têm 16 bytes, ou 128 bits: a documentação da NVIDIA diz isso, e na nossa listagem os endereços andam sempre de 16 em 16. Na tela está a instrução FFMA do SAXPY, escrita como as duas palavras de 64 bits que a ferramenta mostra. Um estudo de 2018 sobre a geração Volta abriu esses 128 bits: pelo menos 91 são a instrução em si, pelo menos 23 são bits de controle, com avisos do compilador para o escalonador, como quanto tempo esperar, e 14 parecem sem uso. Ou seja, o compilador resolve antes parte da organização do pipeline e grava a solução dentro da instrução, o que um estudo de 2025 sobre a geração Ampere também descreve. Na Blackwell, só achamos documentada a largura de 128 bits, e por isso a figura marca os bits de controle desta placa como não documentados. Tamanho fixo é uma das marcas dos processadores RISC, e isso leva à pergunta do enunciado: esta GPU é RISC ou CISC.

**Palavras novas**
- **Byte:** 8 bits. 16 bytes = 128 bits.
- **Opcode:** a parte da instrução que diz qual operação fazer.
- **Bits de controle:** bits que o compilador grava na instrução para orientar o escalonador (esperas, dependências, reúso de registrador).
- **Hexadecimal:** jeito de escrever números em base 16. Cada dígito vale 4 bits.

**Perguntas prováveis**
1. *Onde a NVIDIA diz 16 bytes?* No apêndice do formato JSON do CUDA Binary Utilities: "The instruction size is 16 bytes." O corpo do documento não declara. Confirmamos no experimento: endereços de 0x10 em 0x10. Fonte: Binary Utilities, ap. 7.1. `harness/examples/saxpy-cu/`.
2. *Os campos da Volta valem na Blackwell?* Não sabemos. A largura de 128 bits se manteve, mas a posição dos campos em sm_120 não está documentada, e a NVIDIA não dá acesso aos bits de controle pelas ferramentas (Huerta et al., seção 6). Lacuna `isa.control_bits_blackwell`.
3. *Antes da Volta era diferente?* Sim. Segundo Jia et al., cada instrução tinha 64 bits e uma palavra de 64 bits de controle servia para várias instruções. Fonte: Jia et al., cap. 2.

---

## a5.12 · RISC ou CISC: RISC com extensões de acelerador

**Na tela:** a tabela "RISC ou CISC? Critérios para o SASS (sm_120)", com três colunas (critério, o que as fontes mostram, aponta para). Acesas: a linha da largura da instrução (RISC), a do acesso à memória (RISC, com exceções) e a do trabalho por instrução (afasta do RISC clássico). Em destaque, a conclusão: "RISC no formato, com instruções próprias de acelerador. Análise do grupo, a NVIDIA não classifica o SASS".

**Fala:** CISC e RISC são duas filosofias de projeto de conjunto de instruções. CISC quer dizer Complex Instruction Set Computer, computador com conjunto de instruções complexo: uma só instrução pode ler a memória, fazer a conta e gravar o resultado, e as instruções têm tamanhos diferentes. RISC quer dizer Reduced Instruction Set Computer, computador com conjunto de instruções reduzido: cada instrução faz uma coisa simples, todas têm o mesmo tamanho, só as instruções de carga e de armazenamento tocam a memória, e as contas acontecem entre muitos registradores. Usamos esses critérios na tabela, e três deles apontam para RISC: as instruções têm 16 bytes fixos, a memória global e a compartilhada são acessadas, como regra, por instruções de carga e armazenamento, como LDG e STG, e cada thread pode usar até 255 registradores. Dois pontos afastam do RISC clássico: a HMMA, que compilamos, faz o warp inteiro multiplicar um bloco de matriz nos Tensor Cores, 2.048 multiplicações com soma numa só instrução, e a LDGSTS e a UTMALDG, pela descrição oficial, copiam da memória global para a compartilhada, de memória para memória. A quantidade, 258 instruções na lista oficial, não decide, porque o reduzido de RISC fala da simplicidade de cada instrução, e sobre microcódigo não achamos nada nas fontes lidas. Nas fontes que lemos, a NVIDIA não classifica o SASS, então esta é a conclusão do grupo: é RISC no formato e na regra de acesso à memória, com instruções próprias de acelerador, e nossa leitura do porquê é que um formato fixo é simples de decodificar a cada ciclo, enquanto as instruções grandes fazem numa ordem só um trabalho que pediria muitas instruções simples. Essas instruções de carga buscam dados na memória, e quanto tempo isso leva depende de onde o dado está, que é o assunto da hierarquia de memória e dos caches.

**Palavras novas**
- **CISC (Complex Instruction Set Computer):** instruções poderosas e de tamanhos variados, que podem misturar acesso à memória e conta.
- **RISC (Reduced Instruction Set Computer):** instruções simples, de tamanho fixo, com memória acessada só por carga e armazenamento.
- **Carga e armazenamento (load-store):** regra em que só instruções próprias (carga e armazenamento) leem e gravam a memória, e as contas usam registradores.
- **Memória global:** a memória grande da placa (os 96 GB de GDDR7).
- **Memória compartilhada:** memória pequena dentro do SM, que o programa endereça diretamente.
- **Microcódigo:** pequenos programas internos que alguns processadores usam para executar instruções complexas.
- **Acelerador:** processador feito para um tipo de trabalho, como gráficos ou matrizes.

**Os critérios da tabela, um por um**
| Critério | O que as fontes mostram | Aponta para |
|---|---|---|
| Largura da instrução | 16 bytes em todas (Binary Utilities, ap. 7.1, e experimento) | RISC |
| Acesso à memória | carga e armazenamento como regra (PTX ISA 6.2: "load-store machine". SASS: LDG, STG, LDS, STS). Exceções: LDGSTS ("Asynchronous Global to Shared Memcopy") e UTMALDG ("Tensor Load from Global to Shared Memory"). Instruções aritméticas aceitam operando do banco de constantes num exemplo do Binary Utilities (3.1.1) sem arquitetura declarada | RISC, com exceções |
| Modos de endereçamento | vimos descritor, banco de constantes e imediato. A lista completa não levantamos | não determinado |
| Registradores | 65.536 por SM, até 255 por thread | RISC |
| Trabalho por instrução | HMMA (bloco de matriz por warp), TEX (busca de textura) | afasta do RISC clássico |
| Tamanho do conjunto | 258 mnemônicos em 13 categorias (contagem nossa, conferida duas vezes) | neutro |
| Escalonamento no binário | ≥ 23 bits de controle (Volta) | lembra VLIW |
| Microcódigo | nada nas fontes lidas | não determinado |

Fonte da tabela: seção 08 do roteiro (`vault/03-Roteiro/08 - Instruções PTX e SASS, RISC ou CISC.md`), conclusão aprovada pelo grupo em 2026-11-10.

**Perguntas prováveis**
1. *Então é RISC ou não?* Pelo formato e pela regra de acesso à memória, sim: RISC. Mas não é RISC puro, porque tem instruções próprias de acelerador (matriz, textura, cópia assíncrona entre memórias). E não é CISC: as instruções têm tamanho fixo e as contas usam registradores como regra. A NVIDIA não classifica o SASS nas fontes que lemos, então é análise do grupo. Fonte: seção 08 do roteiro.
2. *O artigo de vocês dizia só "RISC". Mudou?* A conclusão continua de pé como regra geral. O artigo partiu do exemplo SAXPY, de 20 instruções. No seminário olhamos a lista oficial inteira, de 258 instruções, e por isso apontamos as exceções. É um aprofundamento, não uma correção. Fonte: revisão do artigo, item F6.
3. *Como são 2.048 multiplicações?* O `mma.sync` do PTX com forma m16n8k16 virou uma instrução `HMMA.16816.F32`. O bloco é 16 × 8 × 16, e 16 × 8 × 16 = 2.048 multiplicações com soma (conta nossa). A versão FP8, `QMMA.16832`, faz 16 × 8 × 32 = 4.096. Fonte: `harness/examples/mma/README.md`.
4. *Existe algum processador declaradamente RISC na GPU?* Sim. O AMP, o processador que escalona contextos na GPU, é RISC-V, segundo o whitepaper (p. 25). Ele fica fora do SM, e não diz nada sobre o SASS.
5. *O que é VLIW, que aparece na tabela?* Very Long Instruction Word: projeto em que o compilador decide a ordem e o paralelismo e grava isso na instrução. O SASS lembra isso porque, pelo menos na Volta, o compilador grava bits de controle de escalonamento em cada instrução. É observação nossa, fora da dicotomia RISC ou CISC. Fonte: Jia et al., cap. 2. Huerta et al., seção 4.

**Cuidado na resposta**
- As definições de CISC e RISC são de livro-texto. O grupo não registrou um livro como fonte (Hennessy e Patterson e Stallings não foram abertos). Se o professor pedir a referência, diga que são os critérios clássicos da disciplina.
- Não diga que "toda ISA RISC atual tem cópia de memória para memória" ou coisa parecida: a seção 08 marca isso como argumento sem fonte registrada.
