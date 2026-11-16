# Roteiro dos slides do seminário

Gerado de `content/pt-BR/beats.json` e `story/storyboard.json` em 2026-11-16. É o que aparece na tela (tópicos) e o apoio falado de cada momento, na ordem das setas. Não editar aqui: edite o `beats.json` e gere de novo.

## 1. RTX PRO 6000 Blackwell: da placa ao chip (a0.1, Vitor)

*Abertura*

- **Grupo Warp 32**: Lorenzo Ruggini, Arthur Lincke, Thiago Karwinski, João Zamora e Vitor Amora
- GPU: processador que executa a mesma operação sobre muitos dados ao mesmo tempo. Esta placa tem **24.064 núcleos CUDA**
- **Roteiro**
  - A placa e o chip GB202
  - Dentro do chip: SM, warp e pipeline
  - Registradores, instruções e RISC ou CISC
  - Cache, memória, MMU e interrupções

**Fala:** Nosso tema é a GPU NVIDIA RTX PRO 6000 Blackwell. Uma GPU é um processador feito para fazer a mesma operação em muitos dados de uma vez, e esta tem 24.064 núcleos CUDA. Vamos da placa até o interior do chip e, no caminho, cobrir os itens do enunciado: registradores, instruções, CISC ou RISC, pipeline, cache, memória, MMU e interrupções.

## 2. A placa por fora (a1.1, Vitor)

*A placa*

- **NVIDIA RTX PRO 6000 Blackwell**, edição Workstation
- Tamanho: **12 pol (305 mm)** de comprimento por **5,4 pol (137 mm)** de altura, em **2 slots**
- Potência total: **600 W**. A geração anterior, a RTX 6000 Ada, tem 300 W
- Memória de **96 GB GDDR7** com ECC. Interface **PCIe 5.0 x16**
- **2 ventiladores** empurram o ar através da placa, e as aberturas anguladas do topo lançam ar para cima

**Fala:** Por fora, a placa ocupa dois slots e mede cerca de 305 por 137 milímetros. Consome até 600 watts, tem 96 gigabytes de memória GDDR7 e se liga ao computador por PCIe 5.0 de 16 pistas. Dois ventiladores empurram o ar através da placa, e as aberturas anguladas do topo lançam ar para cima. Como em qualquer chip, quase toda a energia elétrica consumida vira calor, e é isso que a refrigeração precisa tirar.

## 3. Energia: conector de 16 pinos, borda de cima (a1.4, Vitor)

*A placa*

- A energia entra por **1 conector de 16 pinos**, na **borda de cima** da placa
- Pela norma do conector, **12 pinos levam potência** (6 de +12 V e 6 de retorno) e **4 levam sinal**
- A placa vem com um **adaptador**: **4 conectores de 8 pinos** da fonte ligam no conector de 16 pinos
- Pela norma, cada conector de 8 pinos fornece até **150 W**. Conta nossa: 4 × 150 W = **600 W**, o mesmo valor da potência total da placa
- Em 12 V, 600 W são cerca de **50 A** (600 ÷ 12)

**Fala:** A energia entra por um único conector de 16 pinos, na borda de cima. Pela norma do conector, doze pinos levam potência e quatro levam sinal. A placa vem com um adaptador que liga quatro conectores de 8 pinos da fonte nesse conector. Pela norma, cada conector de 8 pinos fornece até 150 watts, e a nossa conta dá 600 watts para os quatro, o mesmo valor da potência total da placa.

## 4. Dados pelo PCIe, imagem pelo DisplayPort (a1.5, Vitor)

*A placa*

- **Dados**: entram e saem pelo **PCIe 5.0 x16**, nos contatos da **borda de baixo**, que encaixam na placa-mãe
- Esses contatos ficam num **adaptador PCIe separado** da placa de circuito
- **Imagem**: sai por **4 saídas DisplayPort 2.1b**, no **bracket**, a chapa da traseira do gabinete
- O padrão DisplayPort 2.1b chega a **80 Gbps**

**Fala:** Os dados entram e saem pelo PCIe 5.0 de 16 pistas, nos contatos da borda de baixo, que encaixam na placa-mãe. Esses contatos ficam num adaptador separado da placa de circuito. A imagem sai por quatro saídas DisplayPort 2.1b, no bracket, que é a chapa da traseira do gabinete. O padrão chega a 80 gigabits por segundo.

## 5. Por dentro da placa (a2.1, Vitor)

*A placa*

- Para abrir a placa saem, entre outras peças, o bracket, a moldura, as tampas e o adaptador PCIe. Identificação das peças: leitura nossa das fotos
- No centro fica a **placa de circuito (PCB)**, entre duas **pilhas de aletas** que passam o calor para o ar
- Na PCB está o chip **GB202**
- Em volta do chip ficam os **chips de memória** GDDR7

**Fala:** Agora abrimos a placa, na ordem do teardown da Gamers Nexus: saem, entre outras peças, o bracket, a moldura externa, as tampas do centro e o adaptador PCIe. No centro fica a placa de circuito, entre duas pilhas de aletas que passam o calor para o ar. Na PCB está o chip GB202, e em volta dele ficam os chips de memória.

## 6. O chip GB202 (a2.12, Vitor)

*O chip*

- **92,2 bilhões** de transistores em **750 mm²** de silício: cerca de 123 milhões por mm²
- Processo de fabricação **TSMC 4N**
- **188 SMs** e **24.064 núcleos CUDA**, com **128 MB** de cache L2
- Clock de boost de **2.617 MHz** e pico de **126 TFLOPS** em FP32 (126 trilhões de operações por segundo)
- Marcação no chip, lida pela Gamers Nexus: GB 202-870-A1

**Fala:** Este é o chip da placa, o GB202. São 92,2 bilhões de transistores em 750 milímetros quadrados, fabricados no processo TSMC 4N. Ele tem 188 SMs, que somam 24.064 núcleos CUDA, e 128 megabytes de cache L2. Com o clock de boost de 2.617 megahertz, chega a um pico de 126 teraflops em precisão simples, sem contar os Tensor Cores. A memória se liga a ele por um barramento de 512 bits.

## 7. Memória própria: 96 GB de GDDR7 (a3.1, Arthur)

*Gerenciamento de memória*

- A GPU tem **memória própria**, separada da memória do computador: **96 GB de GDDR7**
- No verso da placa há **16 chips**. O teardown fala em **32 posições** de memória no total
- Os chips se ligam ao GB202 por um barramento de **512 bits**, de **16 controladores** de 32 bits
- **ECC**: bits extras guardados com os dados corrigem um bit trocado. Fica sempre ligado

**Fala:** Esta GPU tem memória própria, separada da memória do computador: 96 gigabytes de GDDR7, um tipo de memória feito para placas de vídeo. No verso da placa há 16 chips, e o teardown fala em 32 posições no total. Eles se ligam ao chip por um barramento de 512 bits, formado por 16 controladores de 32 bits. A memória tem ECC, que corrige um bit trocado, e ele fica sempre ligado.

## 8. Por que os dados ficam na placa (a3.6, Arthur)

*Gerenciamento de memória*

- **Memória da placa**: 28 Gbps por pino × 512 bits ÷ 8 = **1.792 GB/s**
- **PCIe 5.0 x16**: 32 GT/s × 16 pistas ÷ 8 = 64 GB/s, cerca de **63 GB/s** com a codificação, em cada sentido
- A memória da placa é cerca de **28 vezes mais rápida** que o PCIe
- Conclusão do grupo: copiar os dados para a placa uma vez e calcular lá dentro

**Fala:** Banda é quanto dado passa por segundo. A memória da placa chega a 1.792 gigabytes por segundo, e o PCIe leva cerca de 63 por sentido, então a memória é cerca de 28 vezes mais rápida. Por isso, na nossa leitura, compensa copiar os dados para a placa uma vez e fazer as contas lá dentro. Quem faz as contas é o chip, e agora vamos entrar nele.

## 9. Dentro do chip: GPCs, TPCs e SMs (a4.2, João)

*O chip*

- Diagrama esquemático: as contagens são oficiais, a posição dos blocos é ilustrativa
- **12 GPCs**. Cada GPC agrupa TPCs, e cada **TPC** tem **2 SMs**: 94 TPCs × 2 = **188 SMs**
- **SM** (Streaming Multiprocessor): recebe as tarefas, busca e executa as instruções
- Cada SM tem **128 núcleos CUDA**: 188 × 128 = **24.064**
- **L2** de **128 MB** no centro do chip e **16 controladores de memória** nas laterais

**Fala:** Daqui em diante a tela mostra desenho, não foto: as contagens são oficiais, mas a posição dos blocos é ilustrativa. O chip tem 12 GPCs. Cada GPC agrupa TPCs, e cada TPC tem 2 SMs, que são quem executa as instruções. São 94 TPCs, então 188 SMs, e como cada SM tem 128 núcleos CUDA, são 24.064 no total. A Tabela 4 do whitepaper dá 188 SMs, e o texto fala em 192 para o chip completo: adotamos 188, que fecha com os 24.064. No centro fica o cache L2 de 128 megabytes, e nas laterais ficam os 16 controladores de memória.

## 10. Dentro de um SM (t2.1, João)

*O SM*

- Lembra um núcleo de CPU: tem **escalonador**, **registradores** e **cache L1**
- A diferença é a quantidade: **128 núcleos CUDA**, em **4 partições**
- Cada partição tem o seu **escalonador de warp**, o seu **banco de registradores** e **1 Tensor Core** (unidade de contas com matrizes)
- No SM também há **1 RT Core** e **4 unidades de textura**
- **Registradores**: 256 KB. **L1 e memória compartilhada**: 128 KB

**Fala:** Dentro de um SM há as peças que um núcleo de CPU também tem: escalonador, registradores e cache L1. A diferença é a quantidade. O SM tem 128 núcleos CUDA, divididos em 4 partições, e cada partição tem o seu escalonador, o seu banco de registradores e um Tensor Core. Também há um RT Core e 4 unidades de textura. A unidade de trabalho que o escalonador despacha é o warp.

## 11. Warp: 32 threads juntas (a5.1, João)

*Execução em warps*

- **Thread**: uma execução do programa com os seus dados, por exemplo multiplicar o elemento i de um vetor por 2
- O programa é escrito para **uma thread** e lançado milhares de vezes, em **blocos** de threads
- O SM divide cada bloco em **warps de 32 threads**, com números seguidos: 0 a 31, 32 a 63 e assim por diante
- Os 32 quadrados do desenho são um warp
- Leitura do grupo: a instrução é buscada **uma vez** e serve para as 32 threads

**Fala:** Quem programa a GPU escreve o código para uma thread, uma pequena tarefa com os seus dados, e manda rodar esse código milhares de vezes. As threads são lançadas em blocos, e o SM divide cada bloco em warps de 32 threads com números seguidos. Os 32 quadrados da tela são um warp. Na nossa leitura, a vantagem é dividir o custo de controle: a instrução é buscada uma vez e serve para as 32 threads.

## 12. SIMT: uma instrução, 32 threads (a5.2, João)

*Execução em warps*

- **SIMT**: as 32 threads do warp executam a **mesma instrução**, cada uma com os seus dados
- Cada thread tem o seu **contador de programa** e os seus **registradores**
- Se as threads divergem num if, o warp executa **cada caminho** e desliga as threads que não estão nele
- Cada SM mantém até **48 warps** ao mesmo tempo (1.536 threads)
- Leitura do grupo: quando um warp espera a memória, o SM executa outro

**Fala:** SIMT quer dizer uma instrução, várias threads: as 32 threads do warp executam a mesma instrução, cada uma com os seus dados. Mesmo assim, cada thread guarda o seu próprio contador de programa e os seus registradores. Por isso, num if, o warp percorre um caminho, depois o outro, desligando as threads que não estão nele. Cada SM mantém até 48 warps ao mesmo tempo e, na nossa leitura, quando um espera a memória, o SM passa para outro.

## 13. Pipeline: um escalonador por partição (a5.5, João)

*Pipeline*

- **Pipeline**: a instrução passa por etapas, como numa linha de montagem. Num processador de livro-texto: buscar, decodificar, executar, guardar
- Cada uma das **4 partições** do SM tem o seu **escalonador de warp**
- A cada **ciclo**, o escalonador escolhe um warp pronto e despacha a instrução para as threads ativas dele (até **32**)
- Trocar de warp **não tem custo**. Leitura do grupo: se um warp espera, outro entra no lugar
- Medido em uma RTX 5080: **4 ciclos** para uma operação de inteiro ou FP32
- Número de estágios do pipeline: **não achamos** nas fontes lidas

**Fala:** Pipeline é a execução em etapas, como uma linha de montagem: buscar a instrução, decodificar, executar e guardar o resultado. Nesta GPU, cada uma das 4 partições do SM tem um escalonador de warp. A cada ciclo, ele escolhe um warp pronto e despacha a instrução para as 32 threads. Trocar de warp não tem custo, então, na nossa leitura, o escalonador tapa os buracos da linha com instruções de outros warps. Pesquisadores mediram 4 ciclos para inteiro ou FP32 numa RTX 5080. Quantos estágios o pipeline tem, não achamos nas fontes.

## 14. Registradores: 65.536 por SM (a5.6, Lorenzo)

*Registradores*

- **Registrador**: a memória mais rápida do processador, dentro do circuito. Guarda o número da conta em andamento
- Cada registrador tem **32 bits**
- Cada SM tem **65.536 registradores** = **256 KB**, em **4 bancos** de 16.384 (um por partição)
- Na placa toda: 188 × 256 KB = **48.128 KB**
- Cada warp mantém os seus registradores enquanto existir: **trocar de warp não custa nada**. Na CPU, trocar de tarefa copia os registradores para a memória

**Fala:** Registrador é a memória mais rápida de um processador: fica dentro do circuito e guarda o número que está sendo usado numa conta. Aqui cada registrador tem 32 bits, e cada SM tem 65.536 deles, que dão 256 KB, em 4 bancos de 16.384, um por partição. Numa CPU, trocar de tarefa copia os registradores para a memória. Na GPU, cada warp fica com os seus registradores enquanto existir, então trocar de warp não custa nada.

## 15. Até 255 registradores por thread (a5.8, Lorenzo)

*Registradores*

- No código SASS: **R** (uso geral), **UR** (uniformes), **P** (predicados) e **SR** (especiais, como SR_TID.X, o índice da thread)
- O **compilador** decide quantos registradores cada thread usa, até **255**. Na CPU, a ISA fixa o conjunto
- Os **65.536** registradores do SM são repartidos entre todos os warps
- Com **255** por thread: 32 × 255 = 8.160 por warp, e só **8 warps** cabem no SM (conta nossa, o limite é 48)
- O SAXPY que compilamos usa **10** por thread, e aí cabem os **48 warps**

**Fala:** No código da GPU aparecem registradores R, de uso geral, UR, uniformes, P, predicados, e SR, especiais, como o que guarda o índice da thread. Numa CPU, o número de registradores é fixo. Na GPU, o compilador decide quantos cada thread usa, até 255. Só que os 65.536 registradores do SM são repartidos entre todos os warps: com 255 por thread, cabem só 8 warps, pela nossa conta simples. Com os 10 registradores do SAXPY, cabem os 48 warps. Com poucos warps, o escalonador tem menos opções de troca.

## 16. Do CUDA C ao PTX e ao SASS (a5.9, Lorenzo)

*Conjunto de instruções*

- O programa em **CUDA C** vira **PTX**, uma máquina virtual com instruções estáveis entre gerações de GPU
- O **ptxas** (ou o driver) traduz o PTX para **SASS**, o código de máquina desta placa, o **sm_120**
- O SASS muda a cada geração: programa sem PTX não tem garantia de rodar em GPUs futuras
- Exemplo, o SAXPY (y = a·x + y): **20 instruções PTX** viram **19 instruções SASS** úteis
- A lista oficial da família Blackwell tem **258 mnemônicos**, contados por nós

**Fala:** Conjunto de instruções é a lista de ordens que o processador entende. Na NVIDIA ele tem duas camadas. O PTX é uma máquina virtual, com instruções estáveis entre gerações. O SASS é o código de máquina de cada geração, nesta placa o sm_120, gerado a partir do PTX pelo ptxas ou pelo driver. No SAXPY, que compilamos, 20 instruções PTX viraram 19 instruções SASS úteis.

## 17. Toda instrução tem 128 bits (a5.10, Lorenzo)

*Conjunto de instruções*

- Cada instrução SASS ocupa **16 bytes = 128 bits**, sempre
- Tamanho fixo: o circuito sabe onde cada instrução começa **sem decodificar a anterior**
- Na nossa listagem, os endereços andam de **16 em 16**: 0000, 0010, 0020
- Na **Volta**, um estudo de 2018 achou ao menos **23 bits de controle**: avisos do compilador ao escalonador
- Na Blackwell, só achamos documentada a **largura**, não os campos

**Fala:** Cada instrução SASS tem 16 bytes, ou 128 bits. Com tamanho fixo, o circuito sabe onde cada instrução começa sem decodificar a anterior, e na nossa listagem os endereços andam sempre de 16 em 16. Um estudo de 2018 abriu os 128 bits da geração Volta e contou pelo menos 23 bits de controle, e estudos da Ampere e da Turing os descrevem como avisos do compilador ao escalonador: o compilador resolve parte da organização do pipeline e grava a solução na instrução. Na Blackwell só achamos documentada a largura.

## 18. RISC ou CISC: RISC com extensões (a5.12, Lorenzo)

*CISC ou RISC*

- **CISC**: instruções complexas e de tamanho variável. Uma instrução pode ler a memória, calcular e gravar
- **RISC**: instruções simples, de tamanho fixo. Só carga e armazenamento tocam a memória, e há muitos registradores
- **A favor de RISC**: 16 bytes fixos, memória por carga e armazenamento (salvo exceções como a LDGSTS) e até 255 registradores por thread
- **Contra**: a HMMA multiplica um bloco de matriz numa só instrução
- A NVIDIA não classifica o SASS. **Conclusão do grupo: RISC no formato, com instruções de acelerador**

**Fala:** No CISC, uma instrução pode ser complexa e de tamanho variável, e pode ler a memória, calcular e gravar. No RISC, as instruções são simples, de tamanho fixo, só carga e armazenamento tocam a memória e há muitos registradores. Nesta GPU, três critérios apontam para RISC: 16 bytes fixos, memória por carga e armazenamento, salvo exceções como a LDGSTS, e até 255 registradores por thread. Contra, a HMMA multiplica um bloco de matriz numa só instrução. A NVIDIA não classifica o SASS, então a conclusão é do grupo: RISC no formato, com instruções de acelerador.

## 19. Cache: a escada de memória (a5.13, Arthur)

*Cache*

- **Cache**: memória pequena, perto de quem calcula, com cópia dos dados usados há pouco
- **L1**: **128 KB** por SM. **L2**: **128 MB** para o chip todo. Depois, a **GDDR7**
- Latência medida em uma **RTX 5080**, da mesma família: L1 **30 a 40 ciclos**, L2 cerca de **358**, GDDR7 cerca de **877**
- Quanto mais longe do SM, maior e mais lento
- Política de substituição, associatividade e escrita: **não achamos** nas fontes lidas

**Fala:** Cache é uma memória pequena e próxima de quem calcula, que guarda sozinha uma cópia dos dados usados há pouco, porque os programas costumam voltar aos mesmos dados. Cada SM tem 128 KB de L1, e o chip inteiro divide 128 MB de L2. Pesquisadores mediram numa RTX 5080, da mesma família, L1 em 30 a 40 ciclos, L2 em cerca de 358 e GDDR7 em cerca de 877. Como o cache decide o que guardar e o que descartar, não achamos nas fontes lidas.

## 20. Memória compartilhada: o programa escolhe (a5.14, Arthur)

*Cache*

- O **L1** e a **memória compartilhada** são os mesmos **128 KB** por SM
- O cache L1 é **automático**. Na memória compartilhada, o **programa** escolhe o que guardar: um bloco de threads copia ali, uma vez, o que todos vão usar
- A divisão é escolhida em **tempo de execução**. Segundo o guia CUDA, a compartilhada pode ter **0, 8, 16, 32, 64 ou 100 KB**

**Fala:** O cache é automático, mas a memória compartilhada é o contrário: um espaço dentro do SM em que o próprio programa escolhe o que guardar. Na GPU, quem a usa em conjunto é um bloco de threads. Nesta placa, o L1 e a memória compartilhada são os mesmos 128 KB por SM, e o programa escolhe quanto vira compartilhada: 0, 8, 16, 32, 64 ou 100 KB. O Tuning Guide fala em 128 KB por SM para essa mesma geração, e a diferença para os 100 KB do guia CUDA não está explicada. Falta ver como a GPU encontra o endereço de cada dado.

## 21. MMU: endereço virtual de 57 bits (a6.1, Thiago)

*MMU*

- A **MMU** traduz o **endereço virtual** do programa em endereço físico, usando **tabelas de páginas**
- Nesta família de GPUs: endereços de **57 bits** e tabela de **6 níveis**
- **Páginas** de 4 KB, 64 KB, 2 MB e 512 MB. Página grande encurta a busca: 96 GB = 192 páginas de 512 MB
- O artigo cita 49 bits e 5 níveis: era o formato da **Pascal** (2016)
- **TLB** (cache das traduções): tamanho e política **não achamos**

**Fala:** Os programas usam endereços virtuais, e a MMU traduz cada um para o endereço real, usando tabelas de páginas. Segundo o código aberto do driver da NVIDIA, esta família usa endereços de 57 bits e 6 níveis, no formato da Hopper. As páginas vão de 4 KB a 512 MB, e uma página grande encurta a busca: os 96 GB cabem em 192 páginas de 512 MB. O artigo cita 49 bits e 5 níveis, que era o formato da Pascal, de 2016. O tamanho e a política da TLB, o cache das traduções, não achamos.

## 22. Falha de página: o driver, na CPU, resolve (a6.2, Thiago)

*MMU e interrupções*

- **Falha de página**: a MMU não encontra o endereço na tabela de páginas
- A GPU anota a falha num **buffer** e avisa a CPU
- O **driver**, que é software na CPU, lê um **lote** de falhas, junta as repetidas e atende
- Depois manda a GPU **repetir** os acessos
- Na CPU é parecido: o sistema operacional resolve e a instrução se repete

**Fala:** Uma falha de página acontece quando a MMU não encontra a página na tabela. Na CPU, o sistema operacional resolve e a instrução se repete. Aqui quem resolve também é software na CPU: o driver. Segundo o código aberto dele, a GPU anota a falha num buffer e avisa a CPU. O driver lê um lote de falhas, junta as repetidas e manda a GPU repetir os acessos. Pelo whitepaper da Pascal, isso permite trazer para a GPU, sob demanda, uma página que não estava na memória dela.

## 23. Interrupções: três mecanismos (a6.4, Thiago)

*Interrupções*

- **1. A GPU avisa a CPU** por MSI-X, MSI ou linha legada
  - O tratador do driver tem duas metades: a primeira faz o mínimo na hora, a segunda faz o trabalho pesado depois
- **2. A instrução trap** aborta o programa e gera uma interrupção para a CPU
- **3. A falha de página** segura o canal: ele não pode ser trocado e os outros esperam até o driver atender
- Preempção (trocar um programa por outro): citada no driver, mas como funciona nesta placa **não achamos**
- Tratador dentro do SM: **não achamos**. Leitura do grupo: os avisos vão ao driver, na CPU

**Fala:** Interrupção é um aviso que faz o processador parar, rodar uma rotina de atendimento e voltar de onde parou. Nesta GPU, achamos três mecanismos. Primeiro, a GPU avisa a CPU por MSI-X ou MSI, e o tratador do driver faz o mínimo na hora e deixa o trabalho pesado para depois. Segundo, a instrução trap aborta o programa e gera uma interrupção para a CPU. Terceiro, uma falha de página segura o canal até o driver atender. Como a preempção funciona nesta placa e se há tratador dentro do SM, não achamos nas fontes, e nossa leitura é que os avisos vão ao driver, na CPU.

## 24. O que achamos e o que falta (a7.4, Vitor)

*Fechamento*

- **Documentado**: tamanhos, limites e formatos. 65.536 registradores por SM, instruções de 16 bytes, endereços de 57 bits, L2 de 128 MB
- **Quase nunca documentado**: o funcionamento por dentro
- **Não achamos**: estágios do pipeline, tamanho da TLB, política dos caches e microcódigo
- Os documentos oficiais descrevem o que quem programa precisa saber, o driver mostra o que o software programa e os pesquisadores mediram outras placas
- O enunciado pede: item não público, dizer isso e explicar por quê

**Fala:** A tabela junta o que achamos para cada item e onde as fontes lidas param. Tamanhos, limites e formatos estão documentados. O funcionamento por dentro quase nunca está: estágios do pipeline, tamanho da TLB, política dos caches e microcódigo não achamos. Vemos três razões: os documentos oficiais descrevem o que quem programa precisa saber, o código do driver mostra o que o software programa, e não o circuito, e os pesquisadores mediram outras placas. É o que o enunciado pede: quando um item não é público, dizer isso e explicar por quê.

## 25. Resumo dos oito itens do enunciado (a7.5, Vitor)

*Resumo*

- **Registradores**: 65.536 por SM, até 255 por thread
- **Instruções**: PTX e SASS. Cada instrução SASS tem 16 bytes
- **CISC ou RISC**: conclusão do grupo, RISC com extensões de acelerador
- **Pipeline**: 4 escalonadores por SM, 32 threads por ciclo cada
- **Cache**: L1 de 128 KB por SM e L2 de 128 MB
- **MMU**: 57 bits, 6 níveis, páginas de 4 KB a 512 MB
- **Memória**: 96 GB de GDDR7
- **Interrupções**: da GPU para a CPU, e trap

**Fala:** Resumindo os oito itens: registradores, 65.536 por SM e até 255 por thread. Instruções, PTX e SASS, e cada instrução SASS tem 16 bytes. CISC ou RISC, conclusão do grupo: RISC com extensões de acelerador. Pipeline, 4 escalonadores por SM despachando 32 threads por ciclo cada. Cache, 128 KB de L1 por SM e 128 MB de L2. MMU, 57 bits em 6 níveis. Memória, 96 GB de GDDR7 e falhas de página resolvidas pelo driver. Interrupções, da GPU para a CPU. Obrigado, e abrimos para perguntas.

Fala total: cerca de 2029 palavras.
