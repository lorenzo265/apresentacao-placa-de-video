# Roteiro dos slides do seminário

Gerado de `content/pt-BR/beats.json` e `story/storyboard.json` em 2026-11-16. É o que aparece na tela (tópicos) e o apoio falado de cada momento, na ordem das setas. Não editar aqui: edite o `beats.json` e gere de novo.

## 1. RTX PRO 6000 Blackwell: da placa ao chip (a0.1, Vitor)

*Abertura*

- **Grupo Warp 32**: Lorenzo Ruggini, Arthur Lincke, Thiago Karwinski, João Zamora e Vitor Amora
- Tema: a **placa de vídeo** NVIDIA RTX PRO 6000 Blackwell, vista de fora até o interior do chip
- Vamos explicar cada termo antes de usá-lo, do básico até o que o enunciado pede
- **Roteiro**
  - A placa de vídeo, por fora e por dentro
  - O chip que calcula e a memória ao redor
  - Como o chip executa tarefas: SM, warp e pipeline
  - Registradores, instruções, CISC ou RISC, cache, MMU e interrupções

**Fala:** Nosso tema é a placa de vídeo NVIDIA RTX PRO 6000 Blackwell. Vamos partir do mais simples, o que é uma placa de vídeo, e ir até o interior do chip, explicando cada termo antes de usá-lo. No caminho cobrimos os itens do enunciado: registradores, instruções, CISC ou RISC, pipeline, cache, gerenciamento de memória, MMU e interrupções.

## 2. CPU e GPU: duas formas de calcular (a0.5, Vitor)

*Contexto*

- **Processador**: o circuito que executa as instruções, as ordens de um programa
- **CPU** (unidade central de processamento): o processador principal do computador. Segue poucas tarefas de cada vez e é boa em programas cheios de decisões
- **GPU** (unidade de processamento gráfico): nasceu para desenhar imagens. A tela é feita de **pixels**, pontinhos que pedem quase a mesma conta, com números diferentes
- Por isso a GPU aposta na **quantidade**: faz a mesma conta sobre muitos dados ao mesmo tempo
- Esta GPU tem **24.064 núcleos CUDA**, pequenas unidades de conta que não equivalem a núcleos de CPU. CUDA é o nome da NVIDIA para programar as suas GPUs

**Fala:** Todo computador tem um processador, o circuito que executa as instruções dos programas. A CPU é o processador principal e segue poucas tarefas de cada vez, decidindo caminhos depressa. A GPU nasceu para desenhar imagens: a tela é feita de pixels, e cada pixel pede quase a mesma conta com números diferentes. Por isso a GPU aposta na quantidade e faz a mesma conta sobre muitos dados ao mesmo tempo. Esta tem 24.064 núcleos CUDA, que são pequenas unidades de conta.

## 3. O que é uma placa de vídeo (a0.6, Vitor)

*A placa*

- **Placa-mãe**: a placa principal do computador, onde se ligam o processador, a memória e as outras placas
- A **placa de vídeo** se encaixa na placa-mãe. Leva a sua própria GPU, a sua própria **memória**, uma entrada de **energia** e saídas de **imagem** para o monitor
- Esta é a edição **Workstation**, para estações de trabalho: computadores de mesa para trabalho profissional pesado
- Vamos ver a energia, os dados, a imagem, o que há por dentro, o chip e a memória

**Fala:** A placa-mãe é a placa principal do computador, onde se ligam o processador, a memória e as outras placas. A placa de vídeo se encaixa nela e leva a sua própria GPU, a sua própria memória, uma entrada de energia e saídas de imagem para o monitor. Esta é a edição Workstation, feita para estações de trabalho, que são os computadores profissionais.

## 4. A placa por fora (a1.1, Vitor)

*A placa*

- **Slot**: o encaixe de placas da placa-mãe e a vaga correspondente na traseira do **gabinete** (a caixa do computador). Esta placa ocupa a largura de **2 slots**
- Tamanho: **12 pol (305 mm)** de comprimento por **5,4 pol (137 mm)** de altura
- **Potência total**: o máximo de energia por segundo que a placa usa, em **watts (W)**. Aqui são **600 W**. A geração anterior, a RTX 6000 Ada, tem 300 W
- **2 ventiladores** empurram o ar através da placa, e as aberturas anguladas do topo lançam ar para cima
- Tem **96 GB** (gigabytes) de memória e se liga ao computador por **PCIe 5.0 x16**. Explicamos nos próximos slides

**Fala:** Por fora, a placa ocupa dois slots, que são as vagas de encaixe de placas no gabinete, e mede cerca de 305 por 137 milímetros. A potência total é de 600 watts, o máximo de energia por segundo que ela usa, e a geração anterior usa 300. Dois ventiladores empurram o ar através da placa, e as aberturas anguladas do topo lançam ar para cima. Como em qualquer chip, quase toda a energia elétrica consumida vira calor, e é isso que a refrigeração precisa tirar.

## 5. Energia: conector de 16 pinos, borda de cima (a1.4, Vitor)

*A placa*

- A placa recebe energia da **fonte** do computador, a peça que transforma a energia da tomada na que o computador usa
- Ela entra por **1 conector de 16 pinos**, na **borda de cima** da placa
- A placa vem com um **adaptador**: **4 conectores de 8 pinos** da fonte ligam nele
- Pela norma, cada conector de 8 pinos fornece até **150 W**. Conta nossa: 4 × 150 W = **600 W**, o mesmo valor da potência total
- Em 12 V (volts), 600 W são cerca de **50 A** (ampères, a corrente elétrica): 600 ÷ 12. Conta nossa

**Fala:** A placa recebe energia da fonte do computador, a peça que transforma a energia da tomada na que o computador usa. Ela entra por um único conector de 16 pinos, na borda de cima. Pela norma do conector, doze pinos levam potência e quatro levam sinal. A placa vem com um adaptador que liga quatro conectores de 8 pinos da fonte nesse conector. Pela norma, cada um de 8 pinos fornece até 150 watts, e a nossa conta dá 600 watts para os quatro, o mesmo valor da potência total da placa.

## 6. Dados pelo PCIe (a1.5, Vitor)

*A placa*

- **Barramento**: caminho de comunicação entre partes do computador. Por ele os **dados** entram e saem da placa
- O **PCIe 5.0 x16** liga a placa de vídeo à placa-mãe. "5.0" é a geração e "x16" são 16 pistas, cada uma um caminho de dados independente
- Os contatos ficam na **borda de baixo**, num **adaptador PCIe** separado da placa de circuito, e encaixam no slot da placa-mãe

**Fala:** Barramento é o caminho de comunicação entre partes do computador. Os dados entram e saem da placa pelo PCIe 5.0 de 16 pistas, que a liga à placa-mãe: 5.0 é a geração, e cada uma das 16 pistas é um caminho de dados independente. Os contatos ficam na borda de baixo, num adaptador separado da placa de circuito, e encaixam no slot da placa-mãe.

## 7. Imagem: 4 saídas DisplayPort (a1.7, Vitor)

*A placa*

- **Imagem**: sai por **4 saídas DisplayPort 2.1b**, o conector que leva a imagem ao monitor
- Chega a **80 Gbps**: bilhões de **bits** por segundo (um bit é um zero ou um, e 8 bits formam 1 byte)
- As saídas ficam no **bracket**, a chapa da própria placa que fica na traseira do gabinete e a prende a ele

**Fala:** A imagem sai por quatro saídas DisplayPort 2.1b, o conector que leva a imagem ao monitor. O padrão chega a 80 gigabits por segundo, ou seja, 80 bilhões de bits por segundo, e um bit é um zero ou um. As saídas ficam no bracket, a chapa da própria placa que fica na traseira do gabinete e a prende a ele.

## 8. Por dentro da placa (a2.1, Vitor)

*A placa*

- **Teardown**: desmontagem de um aparelho, peça por peça, com fotos. Saem, entre outras, o bracket, a moldura, as tampas e o adaptador PCIe. Identificação das peças: leitura nossa das fotos do teardown
- No centro fica a **PCB** (placa de circuito impresso), onde o chip e os outros componentes são soldados
- Na PCB está o chip **GB202** (o nome deste chip), que faz os cálculos
- Em volta do chip ficam os **chips de memória**, explicados adiante
- A PCB fica entre duas **pilhas de aletas**: lâminas finas que passam o calor do chip para o ar. O conjunto que tira o calor é o **cooler**

**Fala:** Teardown é a desmontagem de um aparelho peça por peça, com fotos, e seguimos o de uma equipe que desmontou esta placa: saem, entre outras peças, o bracket, a moldura externa, as tampas do centro e o adaptador PCIe. No centro fica a placa de circuito, a PCB, onde o chip e os outros componentes são soldados. Nela estão o chip GB202 e, em volta dele, os chips de memória. A PCB fica entre duas pilhas de aletas, lâminas finas que passam o calor para o ar, e o conjunto que tira o calor se chama cooler.

## 9. O chip GB202 (a2.12, Vitor)

*O chip*

- **Chip**: um circuito numa pastilha de silício, feito de **transistores**, chaves elétricas minúsculas. Este é o que faz os cálculos
- **92,2 bilhões** de transistores em **750 mm²** de silício (cerca de 123 milhões por mm²), gravados pelo processo de fabricação **TSMC 4N** (TSMC é a fábrica, 4N o nome da técnica)
- **188 SMs** e **24.064 núcleos CUDA**, com **128 MB** de cache L2: partes que explicamos adiante
- **Clock**, a batida do relógio do chip, de boost: **2.617 MHz**, cerca de 2,6 bilhões de ciclos por segundo
- Pico de **126 TFLOPS** em FP32: 126 trilhões de operações por segundo com números de ponto flutuante (com vírgula) de 32 bits

**Fala:** Este é o chip da placa, o GB202. Um chip é um circuito feito de transistores, chaves elétricas minúsculas, e este tem 92,2 bilhões deles em 750 milímetros quadrados de silício, gravados pelo processo de fabricação TSMC 4N. Ele tem 188 SMs, que somam 24.064 núcleos CUDA, e 128 megabytes de cache L2. O clock, a batida do relógio do chip, chega a 2.617 megahertz, e o pico é de 126 teraflops em precisão simples, sem contar os Tensor Cores. A marcação no chip, lida pela Gamers Nexus, é GB 202-870-A1.

## 10. Memória própria: 96 GB de GDDR7 (a3.1, Arthur)

*Gerenciamento de memória*

- **Memória de trabalho (RAM)**: onde ficam os dados enquanto o processador calcula. Perde o conteúdo quando a energia acaba
- A GPU tem memória **própria**, separada da memória do computador: **96 GB de GDDR7**, um tipo de memória feito para placas de vídeo
- No verso da placa há **16 chips**. O teardown fala em **32 posições** (lugares para um chip) no total
- **Barramento de 512 bits**: 512 linhas de dados em paralelo entre a memória e o GB202, por **16 controladores** de 32 bits
- **ECC** (código de correção de erros): bits extras corrigem um bit trocado por erro. Fica sempre ligado

**Fala:** Todo processador precisa de uma memória de trabalho, a RAM, onde ficam os dados enquanto ele calcula. Esta GPU tem memória própria, separada da memória do computador: 96 gigabytes de GDDR7, um tipo feito para placas de vídeo. No verso da placa há 16 chips, e o teardown fala em 32 posições no total. Eles se ligam ao chip por um barramento de 512 bits, formado por 16 controladores de 32 bits, que são os circuitos que pedem as leituras e escritas. A memória tem ECC, que corrige um bit trocado, e ele fica sempre ligado.

## 11. Por que os dados ficam na placa (a3.6, Arthur)

*Gerenciamento de memória*

- **Banda**: a quantidade de dados que passa por segundo, em **GB/s** (gigabytes por segundo)
- **Memória da placa**: cada pino (linha de dados) transmite 28 Gbps. 28 × 512 ÷ 8 bits por byte = **1.792 GB/s**
- **PCIe 5.0 x16**: 32 GT/s (bilhões de transferências por segundo) × 16 pistas ÷ 8 = 64 GB/s, cerca de **63 GB/s** com a codificação (bits extras de controle), em cada sentido
- A memória da placa é cerca de **28 vezes mais rápida** que a ligação com o computador
- Conclusão do grupo: compensa copiar os dados para a placa uma vez e calcular lá dentro

**Fala:** Banda é quanto dado passa por segundo. A memória da placa chega a 1.792 gigabytes por segundo, e o PCIe leva cerca de 63 por sentido, então a memória é cerca de 28 vezes mais rápida. Por isso, na nossa leitura, compensa copiar os dados para a placa uma vez e fazer as contas lá dentro. Quem faz as contas é o chip, e agora vamos entrar nele.

## 12. Dentro do chip: GPCs, TPCs e SMs (a4.2, João)

*O chip*

- Desenho esquemático: contagens oficiais, posições ilustrativas
- O chip é feito de **caixas dentro de caixas**. A maior é o **GPC**, um grupo de processamento: são **12**
- Cada GPC agrupa **TPCs**, e cada TPC tem **2 SMs**: 94 TPCs × 2 = **188 SMs**
- **SM** (Streaming Multiprocessor): a unidade que recebe as tarefas, busca as instruções e as executa
- Cada SM tem **128 núcleos CUDA**: 188 × 128 = **24.064**
- No centro fica o **cache L2** de **128 MB**, uma memória rápida que o chip todo divide. Nas laterais, os **16 controladores** de memória

**Fala:** Daqui em diante a tela mostra desenho, não foto: as contagens são oficiais, mas a posição dos blocos é ilustrativa. O chip é feito de caixas dentro de caixas, e a maior é o GPC, que aparece 12 vezes. Cada GPC agrupa TPCs, e cada TPC tem 2 SMs, que são quem recebe as tarefas e executa as instruções. São 94 TPCs, então 188 SMs, e como cada SM tem 128 núcleos CUDA, são 24.064 no total. A Tabela 4 do whitepaper dá 188 SMs, e o texto fala em 192 para o chip completo: adotamos 188, que fecha com os 24.064. No centro fica o cache L2 de 128 megabytes, e nas laterais ficam os 16 controladores de memória.

## 13. Dentro de um SM (t2.1, João)

*O SM*

- Lembra um núcleo de CPU: tem **registradores** (guardam os números em uso), **cache L1** (memória rápida dentro do SM) e **escalonador** (escolhe qual grupo de threads, o warp, executa a seguir)
- A diferença é a quantidade: **128 núcleos CUDA**, divididos em **4 partições**
- **Núcleo CUDA**: a unidade que faz contas simples, com números inteiros ou com vírgula
- Cada partição tem o seu **escalonador de warp**, o seu **banco de registradores** e **1 Tensor Core**, uma unidade de contas com matrizes
- O SM também tem **1 RT Core** (traçado de raios, para imagens 3D) e **4 unidades de textura**

**Fala:** Dentro de um SM há as peças que um núcleo de CPU também tem: escalonador, que escolhe a próxima instrução, registradores, que guardam os números em uso, e cache L1, uma memória rápida dentro do SM. A diferença é a quantidade: 128 núcleos CUDA, divididos em 4 partições, e cada partição tem o seu escalonador, o seu banco de registradores e um Tensor Core. Também há um RT Core, para traçado de raios, e 4 unidades de textura. A unidade de trabalho que o escalonador despacha é o warp.

## 14. Warp: 32 threads juntas (a5.1, João)

*Execução em warps*

- **Thread**: uma execução do programa com os seus dados, por exemplo multiplicar o elemento i de um vetor por 2
- O programa é escrito para **uma thread** e lançado milhares de vezes, em **blocos**: grupos de threads lançados juntos, que vão para o mesmo SM
- O SM divide cada bloco em **warps de 32 threads**, com números seguidos: 0 a 31, 32 a 63 e assim por diante
- Os 32 quadrados do desenho são um warp
- Leitura do grupo: a instrução é buscada **uma vez** e serve para as 32 threads

**Fala:** Quem programa a GPU escreve o código para uma thread, uma execução do programa com os seus dados, e manda rodar esse código milhares de vezes. As threads são lançadas em blocos, grupos que vão juntos para o mesmo SM, e o SM divide cada bloco em warps de 32 threads com números seguidos. Os 32 quadrados da tela são um warp. Na nossa leitura, a vantagem é dividir o custo de controle: a instrução é buscada uma vez e serve para as 32 threads.

## 15. SIMT: uma instrução, 32 threads (a5.2, João)

*Execução em warps*

- **SIMT** (uma instrução, várias threads): as 32 threads do warp executam a **mesma instrução**, cada uma com os seus dados
- Cada thread tem o seu **contador de programa**, que guarda qual é a próxima instrução dela (normalmente a mesma das outras 31), e os seus **registradores**
- **Divergência**: se as threads seguem caminhos diferentes num if, o warp executa **cada caminho** e desliga as threads que não estão nele
- Cada SM mantém até **48 warps** ao mesmo tempo (1.536 threads)
- Leitura do grupo: quando um warp espera a memória, o SM executa outro

**Fala:** SIMT quer dizer uma instrução, várias threads: as 32 threads do warp executam a mesma instrução, cada uma com os seus dados. Mesmo assim, cada thread guarda o seu próprio contador de programa, que marca qual é a próxima instrução dela, e os seus registradores. Por isso, num if, o warp percorre um caminho, depois o outro, desligando as threads que não estão nele. Cada SM mantém até 48 warps ao mesmo tempo e, na nossa leitura, quando um espera a memória, o SM passa para outro.

## 16. Pipeline: um escalonador por partição (a5.5, João)

*Pipeline*

- **Pipeline**: a instrução passa por etapas, como numa linha de montagem, e várias ficam em andamento ao mesmo tempo. Num processador de livro-texto: buscar, decodificar (descobrir o que ela pede), executar, guardar
- Cada uma das **4 partições** do SM tem o seu **escalonador de warp**
- A cada **ciclo**, uma batida do relógio do chip, o escalonador despacha (manda executar) a instrução de um warp pronto às threads ativas (até **32**)
- Trocar de warp **não tem custo**. Leitura do grupo: se um espera, outro entra
- Uma conta de inteiro ou FP32 leva **4 ciclos** (latência medida numa RTX 5080)
- Número de estágios: **não achamos** nas fontes lidas

**Fala:** Pipeline é a execução em etapas, como uma linha de montagem: por exemplo buscar a instrução, decodificar, executar e guardar o resultado. Nesta GPU, cada uma das 4 partições do SM tem um escalonador de warp. A cada ciclo, ele escolhe um warp pronto e despacha a instrução para as threads ativas, até 32. Trocar de warp não tem custo, então, na nossa leitura, o escalonador tapa os buracos da linha com instruções de outros warps. Pesquisadores mediram 4 ciclos para inteiro ou FP32 numa RTX 5080. Quantos estágios o pipeline tem, não achamos nas fontes.

## 17. Registradores: 65.536 por SM (a5.6, Lorenzo)

*Registradores*

- **Registrador**: a memória mais rápida do processador, dentro do circuito. Guarda o número da conta em andamento
- Cada registrador tem **32 bits**, 32 zeros e uns
- Cada SM tem **65.536 registradores** = **256 KB**, em **4 bancos** de 16.384 (um por partição)
- Na placa toda: 188 × 256 KB = **48.128 KB**
- Cada warp mantém os seus registradores enquanto existir: **trocar de warp não custa nada**. Na CPU, trocar de tarefa copia os registradores para a memória

**Fala:** Registrador é a memória mais rápida de um processador: fica dentro do circuito e guarda o número que está sendo usado numa conta. Aqui cada registrador tem 32 bits, e cada SM tem 65.536 deles, que dão 256 KB, em 4 bancos de 16.384, um por partição. Numa CPU, trocar de tarefa copia os registradores para a memória. Na GPU, cada warp fica com os seus registradores enquanto existir, então trocar de warp não custa nada.

## 18. Do CUDA C ao PTX e ao SASS (a5.9, Lorenzo)

*Conjunto de instruções*

- **Conjunto de instruções (ISA)**: a lista de ordens que um processador entende e o formato delas
- O programa em **CUDA C** (a linguagem em que é escrito) vira **PTX**, uma máquina virtual: um processador descrito em documento, com instruções estáveis entre gerações
- O **ptxas**, tradutor da NVIDIA (ou o **driver**, que controla a placa), traduz o PTX para **SASS**, o código de máquina. O alvo desta placa é o **sm_120**
- O SASS pode mudar entre gerações: programa sem PTX não tem garantia de rodar em GPUs futuras
- Exemplo, o **SAXPY** (y = a·x + y): **20 instruções PTX** viram **19 instruções SASS** úteis

**Fala:** Conjunto de instruções é a lista de ordens que o processador entende. Na NVIDIA ele tem duas camadas. O PTX é uma máquina virtual, um processador descrito em documento, com instruções estáveis entre gerações. O SASS é o código de máquina de cada geração, nesta placa o sm_120, gerado a partir do PTX pelo ptxas ou pelo driver, o programa que controla a placa. No SAXPY, que compilamos, 20 instruções PTX viraram 19 instruções SASS úteis. A lista oficial da família Blackwell tem 258 mnemônicos, que contamos.

## 19. Toda instrução tem 128 bits (a5.10, Lorenzo)

*Conjunto de instruções*

- Cada instrução SASS ocupa **16 bytes = 128 bits** (1 byte = 8 bits), sempre
- Tamanho fixo: o circuito sabe onde cada instrução começa **sem decodificar a anterior**. Decodificar é descobrir o que a instrução pede
- Na nossa listagem, os endereços andam de **16 em 16**: 0000, 0010, 0020 (em hexadecimal, 0010 vale 16)
- Na **Volta**, uma geração anterior, um estudo de 2018 contou ao menos **23 bits de controle**, avisos do **compilador** (o programa que traduz o código) ao escalonador
- Na Blackwell, só achamos documentada a **largura**, não os campos

**Fala:** Cada instrução SASS tem 16 bytes, ou 128 bits. Com tamanho fixo, o circuito sabe onde cada instrução começa sem decodificar a anterior, e decodificar é descobrir o que a instrução pede. Na nossa listagem os endereços andam sempre de 16 em 16. Um estudo de 2018 abriu os 128 bits da geração Volta e contou pelo menos 23 bits de controle, e estudos da Ampere e da Turing os descrevem como avisos do compilador ao escalonador: o compilador resolve parte da organização do pipeline e grava a solução na instrução. Na Blackwell só achamos documentada a largura.

## 20. Até 255 registradores por thread (a5.8, Lorenzo)

*Registradores*

- No SASS aparecem registradores **R** (uso geral), **UR** (uniformes), **P** (predicados, de 1 bit) e **SR** (especiais, como SR_TID.X, o índice da thread)
- O **compilador**, o programa que traduz o código para a máquina, decide quantos registradores cada thread usa, até **255**. Na CPU, o conjunto é fixo
- Os **65.536** registradores do SM são repartidos entre todos os warps
- Com **255** por thread: 32 × 255 = 8.160 por warp, e só **8 warps** cabem no SM (conta nossa, o limite é 48)
- O **SAXPY** que compilamos usa **10** por thread, e aí cabem os **48 warps**

**Fala:** No código da GPU aparecem registradores R, de uso geral, UR, uniformes, P, predicados, que guardam um bit, e SR, especiais, como o que guarda o índice da thread. Numa CPU, o número de registradores é fixo. Na GPU, o compilador decide quantos cada thread usa, até 255. Só que os 65.536 registradores do SM são repartidos entre todos os warps: com 255 por thread, cabem só 8 warps, pela nossa conta simples. Com os 10 registradores do SAXPY, cabem os 48 warps. Com poucos warps, o escalonador tem menos opções de troca.

## 21. RISC ou CISC: RISC com extensões (a5.12, Lorenzo)

*CISC ou RISC*

- **CISC** (conjunto complexo de instruções): instruções complexas e de tamanho variável. Uma instrução pode ler a memória, calcular e gravar
- **RISC** (conjunto reduzido): instruções simples, de tamanho fixo. Só as de carga e armazenamento tocam a memória, e há muitos registradores
- **A favor de RISC**: 16 bytes fixos, memória por carga e armazenamento (salvo exceções como a LDGSTS) e até 255 registradores por thread
- **Contra**: a **HMMA** multiplica um bloco de matriz numa só instrução, trabalho de acelerador
- A NVIDIA não classifica o SASS. **Conclusão do grupo: RISC no formato, com instruções de acelerador**

**Fala:** No CISC, uma instrução pode ser complexa e de tamanho variável, e pode ler a memória, calcular e gravar. No RISC, as instruções são simples, de tamanho fixo, só carga e armazenamento tocam a memória e há muitos registradores. Nesta GPU, três critérios apontam para RISC: 16 bytes fixos, memória por carga e armazenamento, salvo exceções como a LDGSTS, e até 255 registradores por thread. Contra, a HMMA multiplica um bloco de matriz numa só instrução, trabalho de um acelerador, que é um processador feito para um tipo de trabalho. A NVIDIA não classifica o SASS, então a conclusão é do grupo: RISC no formato, com instruções de acelerador.

## 22. Gerenciamento de memória: o mapa (a5.17, Arthur)

*Gerenciamento de memória*

- **Gerenciamento de memória**: como o sistema decide onde cada dado fica, como ele chega a quem calcula e como os endereços são traduzidos
- **1. Onde ficam**: nos **registradores**, no **L1** e na memória compartilhada, no **L2** e na **GDDR7**, do mais rápido e mais perto da conta ao maior e mais lento
- **2. Como chegam mais rápido**: o **cache** guarda cópias dos dados usados há pouco
- **3. Como se acha o endereço**: a **MMU** traduz endereços virtuais em endereços físicos
- **4. Quando falta**: a **falha de página** é resolvida pelo driver

**Fala:** Gerenciamento de memória é como o sistema decide onde cada dado fica, como ele chega a quem calcula e como os endereços são traduzidos. Vamos ver quatro partes. Primeiro, onde ficam os dados, da memória mais rápida e pequena à maior e mais lenta. Depois, como o cache faz os dados chegarem mais rápido. Em seguida, como a MMU acha o endereço. E por fim, o que acontece quando o dado não está onde o programa pediu.

## 23. Cache: a escada de memória (a5.13, Arthur)

*Cache*

- **Cache**: memória pequena, perto de quem calcula, que guarda cópia dos dados usados há pouco. Programas costumam voltar aos mesmos dados
- **L1**: **128 KB** em cada SM. **L2**: **128 MB** para o chip todo. Depois, a **GDDR7**
- **Latência**: o tempo até o dado chegar, aqui em ciclos. Medida em uma **RTX 5080**, da mesma família: L1 **30 a 40**, L2 cerca de **358**, memória global (GDDR7) cerca de **877**
- Quanto mais longe do SM, maior e mais lento
- Política de substituição (que dado sai quando o cache enche) e associatividade (onde cada dado pode ficar): **não achamos**

**Fala:** Cache é uma memória pequena e próxima de quem calcula, que guarda sozinha uma cópia dos dados usados há pouco, porque os programas costumam voltar aos mesmos dados. Cada SM tem 128 KB de L1, e o chip inteiro divide 128 MB de L2. Latência é o tempo até o dado chegar, e pesquisadores mediram numa RTX 5080, da mesma família, L1 em 30 a 40 ciclos, L2 em cerca de 358 e GDDR7 em cerca de 877. Como o cache decide o que guardar e o que descartar, não achamos nas fontes lidas.

## 24. Memória compartilhada: o programa escolhe (a5.14, Arthur)

*Cache*

- O **L1** e a **memória compartilhada** são os mesmos **128 KB** por SM
- O cache L1 é **automático**. Na memória compartilhada, o próprio **programa** escolhe o que guardar: um bloco de threads copia ali, uma vez, o que todos vão usar
- A divisão é escolhida em **tempo de execução**, com o programa já rodando. Segundo o guia CUDA, a compartilhada pode ter **0, 8, 16, 32, 64 ou 100 KB**

**Fala:** O cache é automático, mas a memória compartilhada é o contrário: um espaço dentro do SM em que o próprio programa escolhe o que guardar. Na GPU, quem a usa em conjunto é um bloco de threads. Nesta placa, o L1 e a memória compartilhada são os mesmos 128 KB por SM, e o programa escolhe quanto vira compartilhada: 0, 8, 16, 32, 64 ou 100 KB, segundo o guia CUDA. O Tuning Guide fala em 128 KB por SM para essa mesma geração, e a diferença para os 100 KB do guia CUDA não está explicada. Falta ver como a GPU encontra o endereço de cada dado.

## 25. Memória virtual: o que a MMU faz (a6.0, Thiago)

*MMU*

- **Endereço**: o número que diz em que posição da memória um dado está
- O programa usa **endereços virtuais**. A **MMU** (unidade de gerenciamento de memória) traduz cada um para o **endereço físico**, a posição real na memória
- Numa CPU, isso separa um programa do outro e deixa o sistema guardar os dados onde houver espaço
- A tradução usa **tabelas de páginas**: a memória é dividida em **páginas**, blocos de tamanho padronizado, e a tabela diz onde cada uma está
- A tabela é em **níveis**, como um endereço postal: estado, cidade, rua e número

**Fala:** Os programas usam endereços virtuais, e a MMU, unidade de gerenciamento de memória, traduz cada um para o endereço físico, a posição real do dado na memória. Numa CPU, isso separa um programa do outro e deixa o sistema guardar os dados onde houver espaço. A tradução é feita por páginas, blocos de tamanho fixo, numa tabela em níveis, como um endereço postal: estado, cidade, rua e número. No próximo slide vemos como isso é nesta GPU.

## 26. MMU: endereço virtual de 57 bits (a6.1, Thiago)

*MMU*

- Segundo o código aberto do driver da NVIDIA, nesta família de GPUs o endereço virtual tem **57 bits** e a tabela tem **6 níveis**
- **Páginas** de 4 KB, 64 KB, 2 MB e 512 MB. Página grande tem menos níveis para percorrer: 96 GB = 192 páginas de 512 MB
- O nosso texto escrito cita 49 bits e 5 níveis: era o formato da **Pascal**, uma geração de 2016
- **TLB** (cache das traduções recentes): tamanho e política **não achamos**

**Fala:** Segundo o código aberto do driver da NVIDIA, esta família usa endereços virtuais de 57 bits e tabelas de 6 níveis, no formato da Hopper. As páginas vão de 4 KB a 512 MB, e uma página grande encurta a busca: os 96 GB cabem em 192 páginas de 512 MB. O artigo cita 49 bits e 5 níveis, que era o formato da Pascal, de 2016. O tamanho e a política da TLB, o cache das traduções, não achamos.

## 27. Falha de página: o driver, na CPU, resolve (a6.2, Thiago)

*MMU e interrupções*

- **Falha de página**: a MMU não encontra o endereço na tabela de páginas
- A GPU anota a falha num **buffer**, uma área de memória, e avisa a CPU
- O **driver**, que é software na CPU, lê um **lote** (grupo) de falhas, junta as repetidas e atende
- Depois manda a GPU **repetir** os acessos
- Na CPU é parecido: o sistema operacional resolve e a instrução se repete
- Serve para trazer à GPU, sob demanda, uma página que ainda não está na memória dela

**Fala:** Uma falha de página acontece quando a MMU não encontra a página na tabela. Na CPU, o sistema operacional resolve e a instrução se repete. Aqui quem resolve também é software na CPU: o driver. Segundo o código aberto dele, a GPU anota a falha num buffer e avisa a CPU. O driver lê um lote de falhas, junta as repetidas e manda a GPU repetir os acessos. Pelo whitepaper da Pascal, isso permite trazer para a GPU, sob demanda, uma página que não estava na memória dela.

## 28. Interrupções: três mecanismos (a6.4, Thiago)

*Interrupções*

- **Interrupção**: aviso que faz o processador parar, rodar uma rotina de atendimento (o **tratador**) e voltar de onde parou
- **1. A GPU avisa a CPU** por MSI-X, MSI ou linha legada, formas de pedir atenção. O tratador do driver faz o mínimo na hora e o resto depois
- **2. A instrução trap** aborta o programa e gera uma interrupção para a CPU
- **3. A falha de página** segura o canal, a fila de trabalho da GPU, até o driver atender
- **Não achamos**: a preempção (trocar uma tarefa por outra) nesta placa e o tratador dentro do SM. Leitura do grupo: os avisos vão ao driver

**Fala:** Interrupção é um aviso que faz o processador parar, rodar uma rotina de atendimento e voltar de onde parou. Nesta GPU, achamos três mecanismos. Primeiro, a GPU avisa a CPU por MSI-X ou MSI, e o tratador do driver faz o mínimo na hora e deixa o trabalho pesado para depois. Segundo, a instrução trap aborta o programa e gera uma interrupção para a CPU. Terceiro, uma falha de página segura o canal até o driver atender. Como a preempção funciona nesta placa e se há tratador dentro do SM, não achamos nas fontes, e nossa leitura é que os avisos vão ao driver, na CPU.

## 29. O que achamos e o que falta (a7.4, Vitor)

*Fechamento*

- **Documentado**: tamanhos, limites e formatos. 65.536 registradores por SM, instruções de 16 bytes, endereços de 57 bits, L2 de 128 MB
- **Quase nunca documentado**: o funcionamento por dentro
- **Não achamos**: estágios do pipeline, tamanho da TLB, política dos caches e microcódigo, os programas internos que alguns processadores usam para instruções complexas
- Os documentos oficiais descrevem o que quem programa precisa saber, o driver mostra o que o software programa, e não como o circuito é por dentro, e os pesquisadores mediram outras placas
- O enunciado pede: item não público, dizer isso e explicar por quê

**Fala:** A tabela junta o que achamos para cada item e onde as fontes lidas param. Tamanhos, limites e formatos estão documentados. O funcionamento por dentro quase nunca está: estágios do pipeline, tamanho da TLB, política dos caches e microcódigo não achamos. Vemos três razões: os documentos oficiais descrevem o que quem programa precisa saber, o código do driver mostra o que o software programa, e não o circuito, e os pesquisadores mediram outras placas. É o que o enunciado pede: quando um item não é público, dizer isso e explicar por quê.

## 30. Resumo dos oito itens do enunciado (a7.5, Vitor)

*Resumo*

- **Registradores**: 65.536 por SM, até 255 por thread
- **Instruções**: PTX e SASS, com 16 bytes por instrução SASS
- **CISC ou RISC**: RISC com extensões (conclusão do grupo)
- **Pipeline**: 4 escalonadores por SM
- **Cache**: L1 de 128 KB e L2 de 128 MB
- **MMU**: 57 bits, 6 níveis, páginas de 4 KB a 512 MB
- **Memória**: 96 GB de GDDR7
- **Interrupções**: da GPU para a CPU, e trap

**Fala:** Resumindo os oito itens: registradores, 65.536 por SM e até 255 por thread. Instruções, PTX e SASS, e cada instrução SASS tem 16 bytes. CISC ou RISC, conclusão do grupo: RISC com extensões de acelerador. Pipeline, 4 escalonadores por SM despachando até 32 threads por ciclo cada. Cache, 128 KB de L1 por SM e 128 MB de L2. MMU, 57 bits em 6 níveis. Memória, 96 GB de GDDR7 e falhas de página resolvidas pelo driver. Interrupções, da GPU para a CPU. Obrigado, e abrimos para perguntas.

Fala total: cerca de 2604 palavras.
