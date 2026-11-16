# Roteiro de estudo, parte 3: memória, MMU, interrupções e fechamento

Momentos a5.13, a5.14, a6.1, a6.2, a6.3, a6.4, a7.4 e a7.5 do corte do seminário. Apresentadores: Arthur (a5.13 e a5.14), Thiago (a6.1 a a6.4), Vitor (a7.4 e a7.5).

Itens do enunciado cobertos aqui: cache, gerenciamento de memória, MMU e interrupções. O a7.5 resume os oito itens.

Como ler os selos: **confirmado** vem de fonte oficial ou do teardown desta placa. **Derivado** vem de outra placa, de outra geração ou de conta nossa. **Provável** é leitura do grupo. **Ilustrativo** é só desenho. Ao responder pergunta, diga o selo junto com o número.

Momento anterior (a5.12, Lorenzo): conclusão RISC com extensões, com carga e armazenamento como regra. A parte 3 começa daí.

---

## a5.13. A escada de memória: perto é rápido

**Na tela.** Diagrama `chip.memhier`: quatro degraus de cima para baixo (Registradores, 256 KB por SM. L1 / memória compartilhada, 128 KB por SM. L2, 128 MB no chip. GDDR7, 96 GB na placa). À direita, a latência de cada degrau (registradores: sem medida levantada. L1: 30 a 40 ciclos. L2: cerca de 358. GDDR7: cerca de 876,7, todas medidas na RTX 5080) e o total na placa (48.128 KB de registradores, 24.064 KB de L1). Embaixo, a nota das latências e a caixa de lacuna da política dos caches. A linha de chamada aponta a latência da GDDR7.

**Fala.** Toda instrução de carga, que vimos na análise de RISC, precisa esperar o dado chegar, e essa espera se chama latência. Pense numa mesa de estudo: o que está na mesa você pega na hora, a estante demora um pouco, e a biblioteca demora muito. O cache é a mesa do processador: um degrau pequeno e perto de quem calcula, que guarda sozinho uma cópia dos dados usados há pouco, porque os programas costumam voltar aos mesmos dados. Nesta GPU, cada SM tem 256 KB de registradores e 128 KB de cache de primeiro nível, o L1, o chip inteiro divide 128 MB de cache de segundo nível, o L2, e a placa tem 96 GB de GDDR7. Medido numa RTX 5080, da mesma família, o L1 responde em 30 a 40 ciclos do relógio, o L2 em cerca de 358 e a GDDR7 em cerca de 877, de 22 a 29 vezes a espera do L1, conta nossa. Como o cache decide o que guardar e o que jogar fora, não achamos nas fontes lidas. Diferente da mesa, quem escolhe o que fica perto é o hardware, menos num pedaço do L1 que o próprio programa controla, e esse é o próximo assunto.

**Palavras novas.**
- Latência: o tempo entre pedir um dado e recebê-lo.
- Cache: memória pequena e rápida que guarda, sem o programa pedir, cópias dos dados usados há pouco.
- L1 e L2: caches de primeiro nível (dentro de cada SM) e de segundo nível (um só, dividido pelo chip todo).
- Ciclo: uma batida do relógio que marca o passo do chip.
- GDDR7: o tipo de memória principal da placa, os chips em volta do processador.

**Perguntas prováveis.**
1. *Por que as latências são de outra placa?* Não achamos medida do GB202. A RTX 5080 (chip GB203) é da mesma família e tem os mesmos 256 KB de registradores e 128 KB de L1 por SM. Por isso o selo é derivado. Fonte: Jarmusch et al., arXiv 2507.10789, Tab. II e seção VI.
2. *Quanto é um ciclo em tempo?* Nesta placa o relógio de boost é 2.617 MHz, então um ciclo dura cerca de 0,38 nanossegundo (conta nossa). Não convertemos as latências medidas para nanossegundos porque a RTX 5080 tem outro relógio. Fonte: whitepaper RTX PRO Blackwell v1.1, Tab. 4 (`chip.boost_clock_mhz`).
3. *O cache é associativo? Qual a política de escrita? Qual o tamanho da linha?* Não achamos nas fontes lidas. O whitepaper só dá tamanhos. Lacuna `cache.policy` do spec.

---

## a5.14. Memória compartilhada: o programa escolhe o que guardar

**Na tela.** Mesmo diagrama, com zoom no degrau do L1. Ao lado dele, a divisão desenhada em "cache L1" e "compartilhada", a nota "divisão escolhida em tempo de execução" e a lista "compartilhada: 0, 8, 16, 32, 64 ou 100 KB". A linha de chamada aponta a parte compartilhada.

**Fala.** O cache é automático, mas a memória compartilhada é o contrário: um espaço dentro do SM em que o próprio programa escolhe o que guardar. É como o quadro de uma sala de aula: o grupo copia ali, uma vez, o que todos vão usar, em vez de cada aluno ir à biblioteca buscar a mesma coisa. Na GPU, o grupo é um bloco de threads, os warps que o SM recebe juntos, e o guia CUDA diz que a memória compartilhada do SM é dividida entre esses blocos. Nesta GPU, o L1 e a memória compartilhada são os mesmos 128 KB por SM, e o programa escolhe, ao rodar, quanto vira compartilhada: 0, 8, 16, 32, 64 ou 100 KB, e o resto fica como cache L1. Quem pede metade dos 100 KB recebe 64 KB, e não 50, porque só existem esses tamanhos. Na nossa leitura, assim o mesmo circuito serve tanto ao programa que planeja a própria memória quanto ao que prefere deixar o cache decidir. Já sabemos onde o dado mora, e falta ver como a GPU encontra o endereço dele.

**Palavras novas.**
- Memória compartilhada: memória dentro do SM que o programa usa de propósito, dividida entre os blocos de threads.
- Bloco de threads: grupo de warps que o programa manda junto para o mesmo SM.
- Carveout: a fatia do L1 separada para memória compartilhada.
- Compute capability 12.0: a versão de arquitetura desta placa, que define limites como esses tamanhos.

**Perguntas prováveis.**
1. *São 128 KB ou 100 KB de memória compartilhada?* 128 KB é o total do L1 com a compartilhada (whitepaper, p. 9). O guia CUDA 13.5, 3.2.6, diz que a compartilhada vai no máximo a 100 KB na compute capability 12.0. O Tuning Guide 13.5, 1.4.1.1, fala em 128 KB de capacidade por SM. Nenhuma fonte lida explica a diferença (lacuna `cuda.smem_per_sm_cc120`).
2. *Como o programa escolhe a divisão?* Com `cudaFuncSetAttribute` e o atributo `cudaFuncAttributePreferredSharedMemoryCarveout`. Fonte: Blackwell Tuning Guide 13.5, 1.4.2.3.
3. *Quanto um bloco sozinho pode usar?* Até 99 KB por bloco na compute capability 12.0. Fonte: Blackwell Tuning Guide 13.5, 1.4.1.1.

---

## a6.1. MMU: a tradutora de endereços

**Na tela.** Diagrama `sys.mmu`: o endereço virtual de 57 bits cortado em campos ([56], [55:47], [46:38], [37:29], [28:21], [20:12] e [11:0], o deslocamento de 12 bits), os 6 níveis da tabela (PDE4, PDE3, PDE2, PDE1, PDE0 e PTE) descendo até a página de 4 KB, as saídas antecipadas para 2 MB e 512 MB, a tabela de tamanhos de página (4 KB, 64 KB, 2 MB, 512 MB, sempre somando 57 bits), a Pascal (49 bits, 5 níveis) para comparar e duas caixas de lacuna (TLB e espaço de endereços por programa). A linha de chamada aponta o deslocamento de 12 bits.

**Fala.** Todo dado tem um endereço, como o número de uma casa, e os programas usam endereços virtuais, que a MMU, a unidade de gerenciamento de memória, traduz para o endereço real na hora do acesso. Numa CPU, isso separa um programa do outro e deixa o sistema guardar os dados onde houver espaço. A tradução é feita por páginas, blocos de tamanho fixo, numa tabela em níveis, como um endereço postal que desce de estado para cidade, rua e número. Segundo o código aberto do driver da NVIDIA, a família desta placa usa endereços de 57 bits e 6 níveis: cada nível lê um pedaço do endereço, e os últimos 12 bits dão a posição dentro de uma página de 4 KB. No artigo citamos 49 bits, mas esse era o formato da Pascal, de 2016. As páginas vão de 4 KB a 512 MB, e página grande encurta a busca: os 96 GB da placa cabem em 192 páginas de 512 MB, contra mais de 25 milhões de páginas de 4 KB, conta nossa. Uma MMU costuma guardar as traduções recentes num cache chamado TLB, e a TLB desta GPU não achamos nas fontes lidas. Quando a página procurada não está na tabela, acontece uma falha de página, o próximo momento.

**Palavras novas.**
- Endereço virtual: o número que o programa usa para achar um dado, antes de ser traduzido.
- Endereço físico: o lugar real do dado na memória.
- MMU: a peça que traduz endereço virtual em físico.
- Página: bloco de memória de tamanho fixo, a unidade da tradução.
- Tabela de páginas: a tabela, em níveis, que diz onde cada página está.
- Deslocamento: a parte final do endereço, que diz a posição dentro da página.
- TLB: cache de traduções recentes, para não percorrer a tabela a cada acesso.

**Perguntas prováveis.**
1. *Por que o artigo diz 49 bits?* Os 49 bits e 5 níveis são da Pascal, de 2016 (documento Pascal MMU Format Changes). O driver atual lista o GB202 na família GB20x (`ctrl2080mc.h`) e diz que essa família usa a MMU da Hopper (`uvm_hal.c`), com 57 bits e 6 níveis (`uvm_hopper_mmu.c`). É atualização, não erro de fonte.
2. *Isso descreve o circuito?* Não diretamente. O código do driver mostra o que o software programa na GPU. Documento de hardware de MMU só achamos o da Pascal (lacuna `mmu.hardware_doc`).
3. *Cada programa tem o próprio espaço de endereços?* Numa CPU, sim. Nesta GPU não achamos fonte que descreva o espaço por programa. O driver dá um limite de 2^57 por canal, mas nada por programa (lacuna `mmu.address_space_per_program`).
4. *Como as contas fecham?* Índices de 1, 9, 9, 9 e 8 bits somam 36. Para 4 KB, mais 9 bits no último nível e 12 de deslocamento: 36 + 9 + 12 = 57. Para 512 MB: 28 bits de índice e 29 de deslocamento. 96 GB divididos por 512 MB dão 192, e por 4 KB dão 25.165.824 (contas nossas).

---

## a6.2. Falha de página: o driver na CPU resolve

**Na tela.** Diagrama `sys.irq`, faixa do mecanismo 3, "falha de página e preempção": 1. falha de página no acesso, 2. a falha vai para o buffer, 3. o canal não pode ser trocado (os outros esperam, fault and stall), 4. o driver resolve um lote e manda a GPU repetir, 5. a GPU repete o acesso. Também a caixa Xid 31, "GPU memory page fault". As setas do mecanismo 3 se acendem. A linha de chamada aponta o passo 3.

**Fala.** Uma falha de página acontece quando a MMU procura um endereço e a página não está na tabela. Numa CPU, o processador para o programa, o sistema operacional resolve e a instrução é repetida. Nesta GPU, quem resolve também é software na CPU: o driver da NVIDIA. Segundo o código aberto do driver, a GPU anota a falha num buffer e a CPU é avisada, e o driver lê um lote de falhas, junta as repetidas para gastar menos tempo e manda a GPU repetir os acessos. Enquanto isso, o canal da falha, que é uma fila de trabalho da GPU, não pode ser trocado, e os outros canais ficam parados, o que o código chama de fault and stall, falhar e esperar. Para que serve: no whitepaper da Pascal, de 2016, a NVIDIA explica que a falha permite trazer para a GPU, sob demanda, uma página que não está na memória dela, a chamada memória unificada. Se o endereço é ilegal, não há o que trazer, e o driver registra o erro Xid 31, falha de página da memória da GPU. A ordem de repetir vai da CPU para a GPU, e é esse caminho que vem agora.

**Palavras novas.**
- Falha de página: acesso a um endereço cuja página não está na tabela.
- Driver: o programa que roda na CPU e controla a GPU.
- Buffer de falhas: a lista onde a GPU anota as falhas para o driver ler.
- Canal: uma fila de trabalho da GPU (detalhe no próximo momento).
- Repetição (replay): a GPU refaz o acesso depois que o driver resolveu a falha.
- Memória unificada: um só espaço de endereços para CPU e GPU, com páginas trazidas quando precisam.
- Xid: código de erro que o driver escreve no registro do sistema.

**Perguntas prováveis.**
1. *Toda falha pode ser repetida?* Não. As falhas do motor gráfico (Graphics Engine, no código) são repetíveis. Que os programas dos SMs rodem nesse motor é leitura nossa, provável. As dos motores de cópia e de submissão não são: nelas o hardware troca de canal ("fault and switch"). As de outros motores são fatais. Fonte: driver aberto, `uvm_gpu_non_replayable_faults.c`, comentário do topo.
2. *Falha de página é sempre erro?* Não. Com memória unificada, é o jeito normal de trazer uma página para a GPU. Erro é o acesso a endereço ilegal, que vira Xid 31. Fontes: whitepaper Tesla P100, p. 27, e catálogo de Xid.
3. *Como a CPU fica sabendo?* Por interrupção. A metade de cima do tratador da UVM (`uvm_isr_top_half`) agenda o atendimento das falhas numa thread do sistema. Fonte: driver aberto, `uvm_gpu_isr.c`.

---

## a6.3. Como a CPU entrega trabalho à GPU

**Na tela.** Diagrama `sys.cmd`: faixa da CPU (driver) e faixa da GPU. Passos: 1. grava os comandos no pushbuffer, 2. aponta uma entrada da GPFIFO para os comandos (`set_gpfifo_entry`), 3. avança o ponteiro PUT (`write_gpu_put`), 4. a GPU lê a fila do canal. No meio, o anel da GPFIFO com os ponteiros GET e PUT, a nota "uma entrada é reservada ao começar o push", a lista de canais e o aviso "descrito para os canais do próprio driver, para um programa CUDA comum é leitura nossa". A linha de chamada aponta o passo 3.

**Fala.** Quem entrega trabalho à GPU é a CPU, e as duas andam em ritmos diferentes. A solução clássica é uma fila de produtor e consumidor, como a roda de pedidos de uma lanchonete: o atendente pendura os pedidos, a cozinha tira na ordem, e cada um trabalha no seu ritmo. Na GPU essa fila é um anel chamado GPFIFO, que ao chegar ao fim volta ao começo, com dois ponteiros: o PUT marca até onde a CPU enfileirou, e o GET, a última entrada que a GPU concluiu. Segundo o código aberto do driver, o driver reserva uma entrada do anel, grava os comandos numa área de memória chamada pushbuffer, aponta a entrada para esses comandos e, por último, avança o PUT. A GPU tem várias filas assim, independentes, chamadas canais. A lanchonete deixa de valer em dois pontos: a entrada do anel só aponta onde o pedido está, e cada canal tem um número fixo de entradas, então um pedido novo só pode começar quando há uma entrada livre no anel. Uma ressalva: isso foi lido nos canais do próprio driver, e que um programa CUDA comum use o mesmo caminho é leitura nossa, provável, sem trecho de fonte. Esse é o caminho da CPU para a GPU, e o caminho de volta, quando a GPU precisa chamar a CPU, é a interrupção.

**Palavras novas.**
- Produtor e consumidor: esquema em que um lado põe trabalho numa fila e o outro tira, cada um no seu ritmo.
- Buffer em anel: fila que, ao chegar ao fim, volta ao começo.
- GPFIFO: a fila em anel de cada canal da GPU.
- PUT e GET: os ponteiros de até onde a CPU escreveu e até onde a GPU concluiu.
- Pushbuffer: a área de memória onde o driver grava os comandos.
- Canal: uma fila de execução independente da GPU.

**Perguntas prováveis.**
1. *Por que a entrada aponta para os comandos em vez de guardá-los?* As fontes lidas não dão o motivo. O que elas dizem é que a entrada da GPFIFO referencia os comandos no pushbuffer e que um pushbuffer atende pushes de vários canais. Fonte: driver aberto, `uvm_pushbuffer.h`.
2. *Um programa CUDA comum usa esse mesmo caminho?* É leitura nossa, provável. Os trechos lidos descrevem só os canais do próprio driver (UVM). Lacuna `cmd.user_path`.
3. *Quem atualiza o GET?* O driver, depois de conferir quais entradas a GPU já concluiu ("Latest GPFIFO entry completed by the GPU"). Fonte: driver aberto, `uvm_channel.h`.

---

## a6.4. Interrupções: três jeitos de parar e avisar

**Na tela.** Diagrama `sys.irq` inteiro, com três faixas (GPU, PCIe, CPU) e três mecanismos. Mecanismo 1, a GPU interrompe a CPU: evento na GPU, MSI-X, MSI ou linha legada, metade de cima (`nvidia_isr` chama `rm_isr`), metade de baixo (`nvidia_isr_kthread_bh` chama `rm_isr_bh`) numa thread do kernel. Mecanismo 2, o programa aborta: instrução `trap` e a frase do manual "Abort execution and generate an interrupt to the host CPU", mais a caixa Xid 13. Mecanismo 3: falha de página e preempção ("Pascal, Blackwell sem fonte"). A nota da análise do grupo, "Não achamos rotina de interrupção executada pelo próprio SM", recebe a linha de chamada.

**Fala.** Uma interrupção é um aviso que faz o processador parar o que está fazendo, rodar uma rotina de atendimento, o tratador, e voltar de onde parou, como a campainha que poupa você de ir à porta a cada minuto. Nas fontes, achamos três mecanismos nesta GPU. No primeiro, a GPU interrompe a CPU por MSI-X ou MSI, que são avisos enviados como mensagem, ou por uma linha de interrupção antiga, conforme o driver consegue ligar, e o tratador do driver tem duas metades: a de cima roda na hora e faz o mínimo, e a de baixo roda depois, numa thread do sistema, com o trabalho pesado, para não segurar a CPU. No segundo, o programa executa a instrução trap, que, segundo o manual do PTX, aborta a execução e gera uma interrupção para a CPU. No terceiro, a tarefa para no meio, pela falha de página que acabamos de ver ou pela preempção, que tira um programa para dar a vez a outro e que, na Pascal, acontecia instrução a instrução, enquanto para a Blackwell não achamos fonte. O que não achamos em nenhuma fonte é um tratador de interrupção rodando dentro do próprio SM. Nossa leitura, provável, é que o SM não atende interrupções como uma CPU, e os avisos vão para o driver, na CPU. Essa é uma das lacunas do trabalho, e o próximo momento junta todas elas.

**Palavras novas.**
- Interrupção: aviso que faz o processador parar, atender um evento e voltar.
- Tratador: a rotina que atende a interrupção.
- MSI e MSI-X: interrupções enviadas como mensagem, em vez de um fio dedicado.
- Metade de cima e metade de baixo: a parte curta do tratador, que roda na hora, e a parte longa, que roda depois.
- trap: instrução do PTX que aborta o programa e interrompe a CPU.
- Preempção: tirar um programa no meio para dar a vez a outro, guardando o estado dele.

**Perguntas prováveis.**
1. *O que é o Xid 13 que aparece na tela?* "Graphics Engine Exception", o código que o driver registra para falhas gerais de programa, como passar do fim de um vetor. Nenhuma fonte liga o `trap` a um Xid específico. Fonte: catálogo de Xid da NVIDIA.
2. *Qual modo de interrupção esta placa usa na prática?* Não achamos nas fontes lidas. O driver tenta MSI-X ou MSI e, se falhar, recua para "PCIe virtual-wire interrupts". Fonte: driver aberto, `nv.c` e `nv-msi.c`.
3. *Existe trap no código de máquina?* Sim, a lista da Blackwell tem `BPT`, "BreakPoint/Trap". Fonte: CUDA Binary Utilities 13.5 (`isa.op.bpt`).
4. *E a preempção antes da Pascal?* Na Kepler era por bloco de threads. Desde a Pascal é instrução a instrução, com o contexto salvo na memória da GPU. Fonte: whitepaper Tesla P100, p. 30 (selo derivado).

---

## a7.4. O que sabemos e o que falta

**Na tela.** Diagrama `close.gaps`: tabela com três colunas (item do enunciado, o que sabemos, onde as fontes lidas param) e oito linhas (Registradores, Instruções, RISC ou CISC, MMU, Interrupções, Gerenciamento de memória, Pipeline, Cache). A câmera parte do cabeçalho e desce até a lacuna do cache ("substituição, escrita, associatividade, linha").

**Fala.** Esta tabela junta, para cada item do enunciado, o que achamos e onde as fontes que lemos param. Tamanhos, limites e formatos estão documentados: 65.536 registradores por SM, instruções de 16 bytes, endereços de 57 bits e 128 MB de L2. O funcionamento por dentro quase nunca está: quantos estágios tem o pipeline, que é a linha de montagem das instruções, qual o tamanho da TLB, e qual a política dos caches, isto é, que dado sai quando o cache enche e quando uma escrita chega à memória. Vemos três razões: os documentos oficiais descrevem o que quem programa precisa saber, o código do driver mostra o que o software programa e não o circuito, e os pesquisadores mediram outras placas, como a RTX 5080 e GPUs Volta, Turing e Ampere. Por isso cada afirmação desta apresentação tem um selo: confirmado, quando vem de fonte oficial ou do teardown desta placa, derivado, quando vem de outra placa, de outra geração ou de conta nossa, provável, quando é leitura do grupo, e ilustrativo, quando é só desenho. É o que o enunciado pede: quando um item não existe ou não é público, o trabalho diz isso e explica por quê. Para fechar, uma frase para cada item.

**Palavras novas.**
- Lacuna declarada: algo que procuramos e não achamos nas fontes, dito com clareza.
- Política de cache: as regras de que dado sai quando o cache enche e de quando uma escrita chega à memória.
- Associatividade: em quantos lugares do cache um mesmo dado pode ficar.
- Selo de procedência: a marca que diz de onde vem cada afirmação.

**Perguntas prováveis.**
1. *Por que a NVIDIA não documenta isso?* Não sabemos o motivo e não especulamos. Dizemos só o que as fontes lidas cobrem e onde param.
2. *O que faltou ler?* Os artigos de medição da Hopper (arXiv 2501.12084) e do B200 (arXiv 2512.02189), a memória unificada no guia CUDA atual e um documento de hardware de MMU da Hopper ou da Blackwell, que não achamos. Fonte: `vault/01-Briefing/Requisitos da disciplina.md`.
3. *Por que confiar em medidas de outra placa?* Não confiamos como se fossem desta: levam o selo derivado e dizem em que placa foram medidas. A RTX 5080 é da mesma família e tem os mesmos tamanhos de registradores e L1 por SM.

---

## a7.5. Os oito itens do enunciado nesta GPU

**Na tela.** A placa remontada, em vista inteira, sem diagrama. Só o cabeçalho e a legenda.

**Fala.** Registradores: cada SM tem 65.536 registradores de 32 bits, até 255 por thread, e trocar de warp não custa nada porque o estado de cada warp fica guardado no chip. Instruções: o SASS, o código de máquina desta GPU, tem instruções de tamanho fixo, 16 bytes cada, e a lista oficial tem 258 nomes, pela nossa contagem. CISC ou RISC: na análise do grupo, um RISC com extensões, porque o formato é fixo e a memória é acessada, como regra, por carga e armazenamento, mas há instruções como a HMMA, que multiplica um bloco de matriz de uma vez. Pipeline: cada SM tem 4 escalonadores de warp, cada um despachando 32 threads por ciclo, e o número de estágios não achamos nas fontes. Cache: 128 KB de L1 por SM, divididos com a memória compartilhada no tamanho que o programa escolher entre seis opções, e 128 MB de L2 para o chip todo, com a política dos caches fora das fontes. MMU e gerenciamento de memória: endereços virtuais de 57 bits em 6 níveis, páginas de 4 KB a 512 MB, e falhas de página resolvidas em lote pelo driver, na CPU. Interrupções: as que achamos vão da GPU para a CPU, por MSI-X ou MSI, pelo trap de um programa ou por uma falha de página, e dentro do SM não achamos tratador. Esse é o retrato da RTX PRO 6000 Blackwell que as fontes permitem, cada parte com o seu selo, e agora abrimos para perguntas.

**Palavras novas.** Nenhuma. Todas já foram explicadas antes.

**Perguntas prováveis.**
1. *Afinal, é RISC ou CISC?* RISC com extensões, na análise do grupo (selo provável), aprovada pelo autor em 2026-11-10. A favor de RISC: tamanho fixo de 16 bytes, carga e armazenamento como regra, muitos registradores. Contra: HMMA, TEX e LDGSTS fazem muito trabalho numa instrução. A NVIDIA não classifica. Fontes: CUDA Binary Utilities 13.5, PTX ISA 6.2, experimento `harness/examples/mma/`.
2. *A GPU tem MMU própria?* Sim. O catálogo de Xid diz que o Xid 31 é registrado quando a MMU da GPU reporta uma falha, e o driver programa a tabela de páginas dela. Fontes: catálogo de Xid e driver aberto.
3. *Qual item ficou mais fraco?* Pipeline e cache: temos a estrutura e os tamanhos, mas o número de estágios e a política dos caches não estão nas fontes lidas (lacunas `pipeline.depth` e `cache.policy`).

---

## Nota sobre o corte do seminário (2026-11-16)

As falas do seminário foram encurtadas para caber em 22 minutos (`harness/content/pt-BR/reescrita/final.json`). Desta parte, saiu do corte o momento **a6.3** (como a CPU entrega trabalho à GPU, a fila GPFIFO). A fala de a6.2 agora termina ligando a falha de página à interrupção. Se perguntarem como a CPU manda trabalho para a GPU, a resposta completa está em a6.3, acima. As falas completas, de todos os momentos, continuam aqui e servem para estudo e para responder perguntas.
