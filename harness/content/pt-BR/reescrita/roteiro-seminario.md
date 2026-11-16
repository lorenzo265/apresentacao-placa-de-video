# Roteiro do seminário: falas finais
Os 22 momentos do corte do seminário, na ordem das setas do tour. Cerca de 2.850 palavras, perto de 20 minutos em voz alta. A explicação completa de cada momento, as palavras novas e as perguntas com resposta estão nos roteiros de estudo (partes 1 a 3, no fim deste arquivo).

## 1. O que é uma GPU, e o roteiro (a0.1)

**Na tela:** Uma GPU faz a mesma conta sobre muitos dados ao mesmo tempo. Esta tem 24.064 núcleos CUDA.

**Fala:** Uma GPU, unidade de processamento gráfico, é um processador feito para fazer a mesma conta sobre muitos dados ao mesmo tempo. Ela nasceu para desenhar imagens: cada pontinho da tela, o pixel, pede quase a mesma conta, com números diferentes. A CPU, o processador principal do computador, segue poucas tarefas de cada vez, enquanto a GPU aposta na quantidade: esta placa tem 24.064 núcleos CUDA, que são pequenas unidades de conta. A placa é a NVIDIA RTX PRO 6000 Blackwell, edição Workstation, e vamos de fora dela até dentro do chip. No caminho, respondemos aos itens do enunciado: registradores, instruções, CISC ou RISC, pipeline, cache, gerenciamento de memória, MMU e interrupções. Cada afirmação tem um selo, confirmado, derivado, provável ou ilustrativo, e quando algo não está nas fontes que lemos, nós dizemos.

*Fonte: NVIDIA, datasheet da RTX PRO 6000 Blackwell Workstation Edition, p. 1 e 3, e whitepaper RTX PRO Blackwell v1.1, p. 9. Itens: enunciado da disciplina*

## 2. Por fora: ar, energia e dados (a1.1)

**Na tela:** 600 W de potência total viram calor, e dois ventiladores empurram o ar através da placa. A energia entra pelo topo, os dados pela borda de baixo.

**Fala:** Por fora, a placa ocupa dois slots, as vagas de encaixe de placas no gabinete. A potência total é de 600 W, o dobro dos 300 W da geração anterior, a RTX 6000 Ada, e praticamente toda essa energia vira calor. Para tirar o calor, dois ventiladores numa face fazem o ar atravessar a placa de um lado ao outro. A energia entra por um conector de 16 pinos na borda de cima. Os dados entram pela borda de baixo, que encaixa no PCIe 5.0 de 16 pistas, o barramento que liga a placa ao resto do computador. A imagem sai por quatro saídas DisplayPort, na chapa do fundo, o bracket. Para ver o que há dentro, vamos desmontar a placa.

*Fonte: NVIDIA, datasheet, p. 1 e 3, guia rápido, p. 8 e 10, e whitepaper RTX PRO Blackwell v1.1, Tab. 4. Gamers Nexus, teardown da RTX PRO 6000 Blackwell (2025)*

## 3. Desmontando na ordem de um teardown real (a2.1)

**Na tela:** Sete passos, na ordem do teardown desta placa feito pela Gamers Nexus. No fim, o chip GB202 coberto de pasta térmica.

**Fala:** Teardown é a desmontagem de um aparelho peça por peça, com fotos, e seguimos a ordem do teardown que a Gamers Nexus fez desta mesma placa. Primeiro saem o bracket, um aro externo e as tampas do centro. Depois sai o adaptador PCIe: os contatos que encaixam no computador ficam numa peça separada. Em seguida saem uma placa que cobre o circuito, os cabos flat e os parafusos de uma mola de lâmina. Por fim sai a PCB, a placa de circuito, que fica no centro, entre duas pilhas de aletas, as lâminas finas que passam o calor para o ar. Na PCB está o chip GB202, coberto de pasta térmica, que ajuda o calor a passar do chip para o cooler. Com a placa aberta, seguimos o caminho dos dados, que começa na memória.

*Fonte: Gamers Nexus, teardown da RTX PRO 6000 Blackwell (2025). Identificação das peças pelas fotos: leitura nossa*

## 4. A memória própria da placa: 96 GB (a3.1)

**Na tela:** 96 GB de GDDR7 só para a GPU, ligados ao chip por 512 bits. No verso, 16 chips, de 32 posições no total.

**Fala:** Todo processador precisa de uma memória de trabalho, onde ficam os dados enquanto ele calcula. Aqui começa o gerenciamento de memória, item do enunciado. Esta GPU tem memória própria, separada da memória do computador, com 96 GB de GDDR7, um tipo de memória feito para placas de vídeo. No verso da placa, que está na tela, a Gamers Nexus contou 16 chips de memória, e fala em 32 posições no total. Os chips se ligam ao processador por um barramento de 512 bits, ou seja, 512 bits transferidos em paralelo. A memória tem ECC, um código de correção de erros: bits extras guardados com os dados permitem achar e corrigir um bit trocado, e nesta placa ele fica sempre ligado. A memória fica na placa por um motivo: velocidade.

*Fonte: NVIDIA, datasheet, p. 3, e whitepaper RTX PRO Blackwell v1.1, p. 8, p. 13 e Tab. 4. Gamers Nexus, teardown da RTX PRO 6000 Blackwell (2025)*

## 5. Por que os dados moram na placa (a3.6)

**Na tela:** Memória da placa: 1.792 GB/s. Ligação com o computador, PCIe 5.0 x16: cerca de 63 GB/s por sentido, 28 vezes menos.

**Fala:** Banda é a quantidade de dados que passa por segundo, como a vazão de um cano em litros por segundo. A memória da placa tem 512 bits de largura e cada pino transmite 28 gigabits por segundo: 512 vezes 28, dividido por 8 bits por byte, dá 1.792 GB/s. Já a ligação com o computador, o PCIe 5.0 de 16 pistas, leva cerca de 63 GB/s em cada sentido, pela nossa conta. A memória da placa é, então, cerca de 28 vezes mais rápida que esse caminho, também conta nossa. A consequência, na nossa leitura, é a regra de projeto: copiar os dados para a placa uma vez e fazer as contas aqui dentro. Quem faz essas contas é o chip GB202, onde entramos agora.

*Fonte: NVIDIA, whitepaper RTX PRO Blackwell v1.1, Tab. 4, e datasheet, p. 3. PCI-SIG, comunicado sobre o PCIe 5.0 (2019). 63 GB/s e razão: contas nossas*

## 6. Caixas dentro de caixas: GPC, TPC e SM (a4.2)

**Na tela:** 12 GPCs, 94 TPCs, 2 SMs por TPC: 188 SMs. Cada SM tem 128 núcleos CUDA, 24.064 no total.

**Fala:** Daqui em diante a tela mostra desenho, não foto: as contagens são oficiais, e as posições dos blocos, ilustrativas. A organização do chip é de caixas dentro de caixas, e a maior é o GPC, que aparece 12 vezes. Dentro dos GPCs ficam os TPCs, e cada TPC tem 2 SMs, então os 94 TPCs desta placa dão 188 SMs. O SM, Streaming Multiprocessor, é a unidade que recebe os grupos de tarefas, busca as instruções e as executa. Cada SM tem 128 núcleos CUDA, e 188 vezes 128 dá os 24.064 da ficha técnica. Repetir o mesmo SM muitas vezes é o que dá força à GPU, porque cada SM trabalha num pedaço diferente dos dados. Agora vamos abrir um desses SMs.

*Fonte: NVIDIA, whitepaper RTX PRO Blackwell v1.1, Fig. 3 (p. 8), redesenhada, p. 9, p. 11 e Tab. 4, e datasheet, p. 3. Guia de programação CUDA 13.5, 3.2.2.2. Posições ilustrativas*

## 7. Dentro de um dos 188 SMs (t2.1)

**Na tela:** Cada SM tem escalonadores, registradores, cache L1 de 128 KB e 128 núcleos CUDA, em 4 partições. A placa tem 188 SMs.

**Fala:** Agora entramos em um dos 188 SMs. Um núcleo de processador comum repete uma rotina: lê a instrução, busca os números, faz a conta e guarda o resultado. O SM tem as peças dessa rotina, acesas na tela: o escalonador, que escolhe a próxima instrução, o banco de registradores, que guarda os números em uso, e o cache L1, uma memória rápida de 128 KB. A diferença está na quantidade: o SM tem 128 núcleos CUDA, em 4 partições, e cada partição tem o seu escalonador, o seu banco de registradores e 1 Tensor Core, uma unidade de contas de matrizes. Para entender como esses núcleos recebem trabalho, começamos pelo grupo de tarefas que o escalonador despacha, o warp.

*Fonte: NVIDIA, whitepaper RTX PRO Blackwell v1.1, p. 8, p. 9, Fig. 5 (p. 10) e p. 11*

## 8. Um warp: 32 threads que andam juntas (a5.1)

**Na tela:** O programa é escrito para uma thread e lançado em blocos. O SM divide cada bloco em warps de 32 threads com números seguidos.

**Fala:** Quem programa a GPU escreve o código para uma única thread, uma pequena tarefa com os seus dados, por exemplo: multiplique o elemento i de um vetor por 2. Depois manda rodar esse código milhares de vezes, e cada cópia recebe um número diferente e cuida de um elemento. As threads são lançadas em blocos, e o SM divide cada bloco em warps de 32 threads com números seguidos, de 0 a 31, de 32 a 63, e assim por diante. Os 32 quadrados da tela são um warp. A vantagem de agrupar, na nossa leitura, é dividir o custo de controle: a instrução é buscada uma vez e serve para 32 threads. Vamos ver como isso funciona.

*Fonte: NVIDIA, PTX ISA, 2.2.1 e 4.5.1. Guia de programação CUDA 13.5, 3.2.2.2*

## 9. SIMT: uma instrução, 32 threads (a5.2)

**Na tela:** As 32 threads do warp executam a mesma instrução, cada uma com os seus dados. Cada SM mantém até 48 warps.

**Fala:** Imagine um professor que dita uma conta para 32 alunos, e cada um faz a conta com os seus números. A NVIDIA chama isso de SIMT, uma instrução, muitas threads: as 32 threads do warp executam a mesma instrução, cada uma com os seus dados. Segundo o guia da NVIDIA, cada thread guarda o próprio estado, inclusive o contador de programa, que marca em que instrução ela está. Aqui a sala de aula deixa de valer: threads do mesmo warp podem seguir caminhos diferentes, e aí o warp percorre um caminho e depois o outro, desligando as threads de fora. Cada SM mantém até 48 warps ao mesmo tempo. Na nossa leitura, quando um warp espera um dado da memória, o escalonador passa para outro warp pronto, e o SM não fica parado.

*Fonte: NVIDIA, guia de programação CUDA 13.5, 3.2.2.1 e 3.2.2.2. Blackwell Tuning Guide 13.5, 1.4.1.1*

## 10. Pipeline: uma linha de montagem de instruções (a5.5)

**Na tela:** Cada uma das 4 partições escolhe um warp e despacha 32 threads por ciclo. Quantos estágios o pipeline tem: não achamos nas fontes lidas.

**Fala:** Pipeline é o jeito de executar instruções como numa linha de montagem: buscar a instrução, decodificar, que é entender o que ela pede, executar a conta e guardar o resultado. Enquanto uma instrução está na conta, a seguinte já está sendo decodificada. Mas se uma instrução precisa do resultado da anterior, ela espera, e a linha fica com um buraco. Nesta GPU, cada uma das 4 partições do SM tem o seu escalonador de warp. A cada ciclo, que é uma batida do relógio do chip, ele escolhe um warp pronto e despacha a mesma instrução para as 32 threads dele. Na nossa leitura, o escalonador tapa os buracos da linha com instruções de outros warps, porque trocar de warp não tem custo. Quantos estágios o pipeline tem, não achamos nas fontes lidas.

*Fonte: NVIDIA, whitepaper RTX PRO Blackwell v1.1, Fig. 5 (p. 10). Guia de programação CUDA 13.5, 3.2.2.2*

## 11. Registradores: 65.536 em cada SM (a5.6)

**Na tela:** Quatro bancos de 16.384 registradores de 32 bits: 256 KB por SM. Cada warp tem os seus registradores, então trocar de warp não tem custo.

**Fala:** Um registrador é a memória mais rápida de um processador: uma pequena caixa dentro do próprio circuito, que guarda um número enquanto ele é usado numa conta. Nesta GPU, cada registrador tem 32 bits, e cada uma das 4 partições do SM tem um banco de 16.384 registradores. São 65.536 por SM, ou 256 KB. Numa CPU, quando o sistema operacional troca uma thread por outra, ele copia os registradores da que sai para a memória. Na GPU, segundo o guia da NVIDIA, o banco é repartido entre os warps do SM, e cada warp fica com os seus registradores enquanto existir, por isso trocar de warp não tem custo. Na nossa leitura, é esse o motivo de o banco ser tão grande: ele guarda o estado de dezenas de warps.

*Fonte: NVIDIA, whitepaper RTX PRO Blackwell v1.1, p. 9 e Fig. 5 (p. 10). Blackwell Tuning Guide 13.5, 1.4.1.1. Guia de programação CUDA 13.5, 3.2.2.2*

## 12. Mais registradores por thread, menos warps (a5.8)

**Na tela:** O compilador escolhe quantos registradores cada thread usa, até 255. Com 255 cabem só 8 warps no SM, com os 10 do SAXPY cabem os 48.

**Fala:** Numa CPU, o número de registradores é fixo. Na GPU, quem decide quantos registradores cada thread usa é o compilador, o programa que traduz o código para a placa, e o limite oficial é de 255 por thread. Só que os 65.536 registradores do SM são repartidos entre todos os warps. Um warp de 32 threads com 255 registradores cada gasta 8.160, e 65.536 dividido por 8.160 dá só 8 warps no SM, conta nossa, sem as regras de arredondamento, que não achamos nas fontes lidas. Já o SAXPY, um programa curto que compilamos para esta placa, usa 10 registradores por thread, e aí vale outro limite oficial: no máximo 48 warps por SM. Com poucos warps, o escalonador tem menos opções de troca, e por isso, na nossa leitura, o compilador tenta gastar poucos registradores.

*Fonte: NVIDIA, Blackwell Tuning Guide 13.5, 1.4.1.1. Experimento do grupo (SAXPY, ptxas -v). Contas nossas*

## 13. Do código em C ao código da máquina (a5.9)

**Na tela:** O PTX é estável entre gerações e o SASS é o código desta placa. No SAXPY, 20 instruções PTX viram 19 instruções SASS úteis.

**Fala:** Conjunto de instruções é a lista de ordens que um processador entende, como somar, comparar ou ler da memória. Na NVIDIA, ele existe em duas camadas, lado a lado na tela. A primeira é o PTX, que a documentação chama de máquina virtual: um processador descrito no papel, com instruções estáveis entre gerações de GPU. A segunda é o SASS, o código de máquina de uma geração, nesta placa a sm_120, traduzido do PTX pela ferramenta ptxas ou pelo driver, o programa que controla a GPU. As duas camadas existem porque o SASS serve a uma geração, e o guia da NVIDIA avisa que um programa sem PTX não tem garantia de rodar em GPUs futuras. No SAXPY, as 20 instruções PTX viraram 19 instruções SASS úteis.

*Fonte: experimento do grupo, harness/examples/saxpy-cu/ (nvcc 13.5, PTX 9.5, sm_120). NVIDIA, PTX ISA 9.5, 1.1 e 1.2. Guia de programação CUDA 13.5, 2.7. Guia CUDA C++ 12.9.1, 6.1.1.2*

## 14. Toda instrução tem o mesmo tamanho: 128 bits (a5.10)

**Na tela:** Cada instrução SASS ocupa 16 bytes, ou 128 bits. Com tamanho fixo, o circuito sabe onde cada instrução começa sem decodificar a anterior.

**Fala:** Uma instrução é uma sequência de bits, e pode ter tamanho variável ou fixo. Com tamanho variável, o circuito precisa ler parte da instrução para saber onde a próxima começa. Com tamanho fixo, já sabe. Nesta placa, segundo a documentação da NVIDIA, todas as instruções SASS têm 16 bytes, ou 128 bits, e na nossa listagem os endereços andam sempre de 16 em 16. Um estudo de 2018 sobre a geração Volta abriu os 128 bits daquela geração: pelo menos 23 são bits de controle, avisos do compilador para o escalonador. Ou seja, o compilador resolve antes parte da organização do pipeline e grava a solução na instrução. Na Blackwell, só achamos documentada a largura de 128 bits. Tamanho fixo é uma marca dos processadores RISC, e isso leva à pergunta do enunciado.

*Fonte: NVIDIA, CUDA Binary Utilities, ap. 7.1. Experimento do grupo (saxpy-cu, endereço 0x0100). Campos: Jia et al. (Volta), cap. 2. Huerta et al. (Ampere), seção 4*

## 15. RISC ou CISC: RISC com extensões de acelerador (a5.12)

**Na tela:** Análise do grupo: tamanho fixo e memória acessada, como regra, por carga e armazenamento apontam RISC. A HMMA, de matriz, é extensão de acelerador.

**Fala:** No CISC, conjunto de instruções complexo, uma só instrução pode ler a memória, fazer a conta e gravar o resultado, e os tamanhos variam. No RISC, conjunto reduzido, cada instrução é simples, todas têm o mesmo tamanho, só carga e armazenamento, que leem e gravam, tocam a memória, e há muitos registradores. Nesta GPU, três critérios apontam para RISC: 16 bytes fixos por instrução, memória acessada, como regra, por carga e armazenamento, e até 255 registradores por thread. Mas a HMMA, que compilamos, multiplica um bloco de matriz numa só instrução. A NVIDIA não classifica o SASS nas fontes que lemos, então a conclusão é do grupo: RISC no formato e no acesso à memória, com instruções de acelerador. Nossa leitura: o formato fixo é simples de decodificar, e as instruções grandes fazem o trabalho de muitas simples.

*Fonte: análise do grupo sobre NVIDIA, CUDA Binary Utilities 13.5 (Blackwell and Rubin Instruction Set) e PTX ISA, 6.2. Blackwell Tuning Guide 13.5, 1.4.1.1. Experimento do grupo, harness/examples/mma/ (sm_120)*

## 16. A escada de memória: perto é rápido (a5.13)

**Na tela:** Do L1 à GDDR7, cada degrau é maior e mais lento. A GDDR7 demora cerca de 877 ciclos, o L1 de 30 a 40 (medidas na RTX 5080).

**Fala:** Toda carga espera o dado chegar, e essa espera é a latência. Pense numa mesa de estudo: o que está na mesa você pega na hora, e a biblioteca demora muito. O cache é a mesa do processador: uma memória pequena e perto de quem calcula, que guarda sozinha uma cópia dos dados usados há pouco, porque os programas costumam voltar aos mesmos dados. Nesta GPU, cada SM tem 128 KB de cache L1, o de primeiro nível, e o chip inteiro divide 128 MB de L2. Medido numa RTX 5080, da mesma família, o L1 responde em 30 a 40 ciclos, o L2 em cerca de 358 e a GDDR7 em cerca de 877. Como o cache decide o que guardar e o que jogar fora, não achamos nas fontes lidas.

*Fonte: NVIDIA, whitepaper RTX PRO Blackwell v1.1, p. 9 e Tab. 4. Latências: Jarmusch et al., seção VI (RTX 5080, GB203)*

## 17. Memória compartilhada: o programa escolhe o que guardar (a5.14)

**Na tela:** L1 e memória compartilhada são os mesmos 128 KB por SM. O programa escolhe 0, 8, 16, 32, 64 ou 100 KB de compartilhada.

**Fala:** O cache é automático, mas a memória compartilhada é o contrário: um espaço dentro do SM em que o próprio programa escolhe o que guardar. É como o quadro de uma sala de aula: o grupo copia ali, uma vez, o que todos vão usar. Na GPU, o grupo é um bloco de threads. Nesta placa, o L1 e a memória compartilhada são os mesmos 128 KB por SM, e o programa escolhe quanto vira compartilhada: 0, 8, 16, 32, 64 ou 100 KB, e o resto fica como L1. Na nossa leitura, assim o mesmo circuito serve tanto ao programa que planeja a própria memória quanto ao que deixa o cache decidir. Falta ver como a GPU encontra o endereço de cada dado.

*Fonte: NVIDIA, guia de programação CUDA 13.5, 3.2.2.2 e 3.2.6. Blackwell Tuning Guide 13.5, 1.4.2.3. Whitepaper RTX PRO Blackwell v1.1, p. 9*

## 18. MMU: a tradutora de endereços (a6.1)

**Na tela:** A MMU traduz endereços virtuais de 57 bits numa tabela de 6 níveis. Páginas de 4 KB a 512 MB, segundo o driver oficial.

**Fala:** Os programas usam endereços virtuais, e a MMU, unidade de gerenciamento de memória, os traduz para o endereço real. Numa CPU, isso separa um programa do outro e deixa o sistema guardar os dados onde houver espaço. A tradução é feita por páginas, blocos de tamanho fixo, numa tabela em níveis, como um endereço postal: estado, cidade, rua e número. Segundo o código aberto do driver da NVIDIA, a família desta placa usa endereços de 57 bits e 6 níveis. No artigo escrito citamos 49 bits, mas esse era o formato da Pascal, de 2016. As páginas vão de 4 KB a 512 MB, e página grande encurta a busca: os 96 GB cabem em 192 páginas de 512 MB, conta nossa. A TLB, cache das traduções recentes, não achamos nas fontes lidas.

*Fonte: driver aberto da NVIDIA (open-gpu-kernel-modules): ctrl2080mc.h, uvm_hal.c, uvm_hopper_mmu.c, uvm_ampere_mmu.c. NVIDIA, Pascal MMU Format Changes. Contagem de páginas: conta nossa*

## 19. Falha de página: o driver na CPU resolve (a6.2)

**Na tela:** A GPU anota a falha num buffer. O driver, na CPU, resolve um lote de falhas e manda a GPU repetir o acesso.

**Fala:** Uma falha de página acontece quando a MMU procura um endereço e a página não está na tabela. Numa CPU, o processador para o programa, o sistema operacional resolve e a instrução é repetida. Nesta GPU, quem resolve também é software na CPU: o driver. Segundo o código aberto dele, a GPU anota a falha numa área de memória, o buffer de falhas, e avisa a CPU. O driver lê um lote de falhas, junta as repetidas e manda a GPU repetir os acessos. Para que serve: segundo o whitepaper da Pascal, de 2016, a falha permite trazer para a GPU, sob demanda, uma página que não está na memória dela. Esse aviso chega à CPU por uma interrupção, o próximo assunto.

*Fonte: driver aberto da NVIDIA, uvm_gpu_replayable_faults.c e uvm_gpu_isr.c. NVIDIA, whitepaper Tesla P100, p. 27*

## 20. Interrupções: três jeitos de parar e avisar (a6.4)

**Na tela:** A GPU avisa a CPU por mensagem, o programa aborta com trap, ou a tarefa para no meio. Tratador dentro do SM: não achamos.

**Fala:** Uma interrupção é um aviso que faz o processador parar, rodar uma rotina de atendimento, o tratador, e voltar de onde parou, como a campainha, que evita ir à porta toda hora. Nesta GPU, achamos três mecanismos. No primeiro, a GPU avisa a CPU por MSI-X ou MSI, mensagens de interrupção, e o tratador do driver faz o mínimo na hora e deixa o trabalho pesado para depois, para não segurar a CPU. No segundo, o programa executa a instrução trap, que aborta e gera uma interrupção para a CPU. No terceiro, a tarefa para no meio, por falha de página ou por preempção, a troca de um programa por outro. Tratador dentro do SM não achamos em nenhuma fonte, e nossa leitura, provável, é que os avisos vão ao driver, na CPU.

*Fonte: driver aberto da NVIDIA, nv.c, nv-msi.c e uvm_gpu_non_replayable_faults.c. PTX ISA 9.5, 9.7.21.4. SM sem tratador: análise do grupo*

## 21. O que sabemos e o que falta (a7.4)

**Na tela:** Tamanhos e formatos estão nas fontes. O funcionamento interno, como os estágios do pipeline e a política dos caches, não.

**Fala:** Esta tabela junta o que achamos para cada item e onde as fontes lidas param. Tamanhos, limites e formatos estão documentados: 65.536 registradores por SM, instruções de 16 bytes, endereços de 57 bits e 128 MB de L2. O funcionamento por dentro quase nunca está: quantos estágios tem o pipeline, o tamanho da TLB e a política dos caches, isto é, que dado sai quando o cache enche. Vemos três razões: os documentos oficiais descrevem o que quem programa precisa saber, o código do driver mostra o que o software programa, e não o circuito, e os pesquisadores mediram outras placas. Por isso cada afirmação tem um selo: confirmado, derivado, provável ou ilustrativo. É o que o enunciado pede: quando um item não é público, o trabalho diz isso e explica por quê.

*Fonte: síntese do grupo a partir das fontes de cada seção (whitepaper, guias CUDA, Binary Utilities, driver aberto, artigos de medição)*

## 22. Os oito itens do enunciado nesta GPU (a7.5)

**Na tela:** Os oito itens do enunciado, resumidos. Obrigado. Perguntas?

**Fala:** Registradores: 65.536 por SM, até 255 por thread, e trocar de warp não custa nada. Instruções: o SASS tem instruções de tamanho fixo, 16 bytes cada. CISC ou RISC: na análise do grupo, RISC com extensões de acelerador, como a HMMA, que multiplica um bloco de matriz de uma vez. Pipeline: 4 escalonadores de warp por SM, cada um despachando 32 threads por ciclo, e o número de estágios não achamos nas fontes. Cache: 128 KB de L1 por SM, divididos com a memória compartilhada, e 128 MB de L2. MMU e gerenciamento de memória: endereços virtuais de 57 bits em 6 níveis, páginas de 4 KB a 512 MB, e falhas resolvidas em lote pelo driver, na CPU. Interrupções: as que achamos vão da GPU à CPU, e no SM não achamos tratador. Obrigado, e abrimos para perguntas.

*Fonte: síntese do grupo a partir das fontes citadas em cada momento. RISC ou CISC: análise do grupo*

---

Fora do corte do seminário (explicação completa nos roteiros de estudo): a2.13, t1.1, a4.4, a5.16, a5.7, a6.3.

---

# Roteiro de estudo, parte 1: abertura, placa, memória e planta do chip

Momentos: a0.1, a1.1, a2.1, a2.13, a3.1, a3.6, t1.1, a4.2, a4.4. Textos de tela em `parte-1.json`. Fatos do spec entre crases (`id`). "Conta nossa" quer dizer que a NVIDIA não dá o número pronto e nós fizemos a conta a partir de números com fonte.

Quem fala: Vitor (a0.1 a a2.13), Arthur (a3.1 e a3.6), João (t1.1 a a4.4), segundo o `storyboard.json`.

---

## a0.1. O que é uma GPU, e o roteiro

**Na tela:** a placa montada, vista de longe, sem destaque de peça. Selos: derivado e confirmado.

**Fala:** Uma GPU, sigla em inglês para unidade de processamento gráfico, é um processador feito para fazer a mesma conta sobre muitos dados ao mesmo tempo. Ela nasceu para desenhar imagens: a imagem da tela é feita de muitos pontinhos, os pixels, e cada pixel pede quase a mesma conta, só que com números diferentes. A CPU, o processador principal do computador, é feita para seguir poucas tarefas de cada vez e decidir caminhos depressa, enquanto a GPU aposta na quantidade: esta placa tem 24.064 núcleos CUDA, que são pequenas unidades de conta. Por isso a GPU hoje serve para duas coisas: mandar imagem para os monitores, pelas quatro saídas de vídeo desta placa, e fazer contas em massa para outros programas, como os de inteligência artificial. A placa que vamos abrir é a NVIDIA RTX PRO 6000 Blackwell, edição Workstation, feita para computadores de trabalho profissional. Dentro do chip, vamos responder aos itens do enunciado: pipeline, registradores, conjunto de instruções, se é CISC ou RISC, cache, gerenciamento de memória, MMU e interrupções. Cada afirmação aparece com um selo, confirmado, derivado, provável ou ilustrativo, e quando algo não está nas fontes que lemos, nós dizemos. O caminho começa pela placa por fora, passa por dentro dela e pela memória, e termina dentro do chip.

**Palavras novas**
- **GPU:** processador especializado em fazer a mesma conta sobre muitos dados ao mesmo tempo.
- **CPU:** o processador principal do computador, que roda o sistema e os programas comuns.
- **Pixel:** cada ponto da imagem da tela.
- **Núcleo CUDA:** pequena unidade de conta dentro do chip. CUDA é o nome da plataforma da NVIDIA para programar a GPU.
- **Selo de procedência:** confirmado (fonte oficial ou teardown desta placa), derivado (placa irmã, outra geração ou conta nossa), provável (proposta do grupo), ilustrativo (desenho).

**Perguntas possíveis**
1. *Um núcleo CUDA é igual a um núcleo de CPU?* Não. O núcleo CUDA só faz a conta: a cada ciclo, uma operação de ponto flutuante de 32 bits ou de inteiro de 32 bits. Na nossa leitura, quem se parece com um núcleo de CPU é o SM, que tem escalonador, registradores e cache próprios. Fonte: whitepaper RTX PRO Blackwell v1.1, p. 9, p. 11 e Fig. 5 (`sm.cuda_cores`, `sm.blocks`).
2. *De onde vem o 24.064?* Da ficha técnica (datasheet, p. 3) e da Tab. 4 do whitepaper. Confere com 188 SMs vezes 128 núcleos (`chip.cuda_cores`).
3. *O que significa "Workstation"?* É a edição para estações de trabalho, os computadores profissionais. O datasheet (p. 1) diz que a placa usa 600 W "para as cargas de trabalho profissionais mais exigentes". Existe também uma versão Max-Q, de 300 W (whitepaper, Tab. 4, `card.tgp_w`).

---

## a1.1. Por fora: ar, energia e dados

**Na tela:** close num ventilador, com destaque no outro ventilador, na carcaça, no bracket e no adaptador PCIe. A caixa de texto aponta para o ventilador 1. Selos: confirmado e derivado.

**Fala:** Por fora, a placa ocupa dois slots, que são as vagas de encaixe de placas no gabinete do computador. A potência total dela é de 600 W, o dobro dos 300 W da geração anterior desta linha, a RTX 6000 Ada, e praticamente toda essa energia termina virando calor. Para tirar esse calor, há dois ventiladores numa face, e o ar atravessa a placa de um lado ao outro em vez de bater na placa de circuito, que se chama PCB. A NVIDIA chama esse projeto de double flow through, fluxo duplo atravessado, com dois caminhos de ar, e a Gamers Nexus, que desmontou esta placa, diz que as aberturas do topo lançam ar para cima e para longe. A energia entra por um conector de 16 pinos na borda de cima. Os dados entram pela borda de baixo, que encaixa no PCIe 5.0 de 16 pistas, o barramento que liga a placa ao resto do computador, com 16 ligações de dados trabalhando juntas. A imagem sai pelas quatro saídas DisplayPort, na chapa do fundo, chamada bracket. Para ver o que há dentro, vamos desmontar a placa na mesma ordem de quem a abriu.

**Palavras novas**
- **Slot:** vaga de encaixe para placas no gabinete. Esta placa ocupa duas.
- **Potência total (TGP):** o máximo de energia por segundo que a placa usa, em watts.
- **PCB:** placa de circuito impresso, onde ficam soldados o chip e os outros componentes.
- **PCIe:** o barramento que liga a placa à placa-mãe. "5.0" é a geração, "x16" quer dizer 16 pistas.
- **Barramento:** caminho de comunicação entre partes do computador.
- **Bracket:** a chapa no fundo da placa, presa ao gabinete, onde ficam as saídas de vídeo.
- **DisplayPort:** padrão de conector para mandar imagem ao monitor.

**Perguntas possíveis**
1. *Os 600 W passam todos pelo conector?* Não sabemos. O datasheet chama os 600 W de "total board power" e não diz quanto vem do slot. O conector tem 16 pinos, pela norma 12 de potência e 4 de sinal. A placa vem com um adaptador de 4 cabos de 8 pinos, e 4 vezes 150 W dá 600 W, conta nossa. Fonte: datasheet, p. 3, guia rápido, p. 5 e 10, guia da Intel 613768 (`card.power_connector_pins`, `card.power_adapter`, `card.power_adapter_nominal_w`, lacuna `power.slot_connector_split`).
2. *Por onde o ar entra?* Não achamos nas fontes lidas. A Gamers Nexus diz que o ar atravessa a placa e que as aberturas do topo lançam ar para cima e para longe, mas não diz por qual face ele entra nem que todo o ar sai pelo topo (lacuna `airflow.direction`).
3. *O conector é 12VHPWR ou 12V-2x6?* Em aberto. O datasheet diz "PCIe CEM5 16-pin", a Gamers Nexus diz 12VHPWR, e as duas versões são quase iguais por fora (`card.power_connector`, `card.power_connector_gn`, lacuna `power.connector_variant`).

---

## a2.1. Desmontando na ordem de um teardown real

**Na tela:** a câmera viaja em volta da placa enquanto as peças saem na ordem dos estágios E1 a E7 e termina perto do chip coberto de pasta térmica, com a memória da frente no quadro. A caixa de texto aponta para a pasta. Selos: confirmado e derivado.

**Fala:** Teardown é a desmontagem de um aparelho peça por peça, com fotos, e aqui seguimos a ordem do teardown que a Gamers Nexus fez desta mesma placa, em sete passos. Primeiro saem o bracket, um aro externo preso por um único parafuso e as tampas do centro. Depois sai o adaptador PCIe: os contatos que encaixam no computador ficam numa peça separada, ligada à placa principal por um adaptador de pinagem própria. Em seguida saem uma placa que cobre o circuito, os cabos flat, que são cabos finos e chatos, e os parafusos de uma mola de lâmina. Por fim sai a PCB, que fica no centro, entre as duas pilhas de aletas, as lâminas finas que passam o calor para o ar. No meio da PCB está o chip GB202, coberto de pasta térmica, que preenche as pequenas falhas entre o chip e o cooler para o calor passar melhor. A Gamers Nexus esperava metal líquido, que a RTX 5090 Founders Edition usa, e achou pasta, o que mostra que uma placa parecida é pista, não prova. Agora vemos a placa inteira aberta.

**Palavras novas**
- **Teardown:** desmontagem documentada de um aparelho, peça por peça.
- **Adaptador PCIe:** peça separada que leva os contatos do slot PCIe até a placa principal.
- **Cabo flat:** cabo fino e chato que liga duas placas de circuito.
- **Aletas:** lâminas finas que aumentam a área de contato com o ar e passam o calor para ele.
- **Pasta térmica:** pasta que preenche as falhas microscópicas entre o chip e o cooler, onde ficaria ar, que conduz mal o calor.
- **Cooler:** o conjunto que tira o calor do chip (aletas, ventiladores e o que houver entre eles).

**Perguntas possíveis**
1. *Por que pasta e não metal líquido?* A fonte não explica. Ela só registra que esperava metal líquido, como na RTX 5090 Founders Edition, e achou pasta (`card.thermal_interface`, `ref5090.thermal_interface`). Não vamos supor um motivo.
2. *O que está escrito no chip?* A Gamers Nexus lê "GB 202-870-A1" depois de limpar a pasta. Na foto, a marcação só é legível em parte, então confiamos no texto da fonte (`chip.marking`).
3. *Para que serve a placa que cobre o PCB, e a mola?* Não achamos nas fontes lidas. A Gamers Nexus só diz que tirou a placa com alavanca e os parafusos da mola (`teardown.e5`, `teardown.e6`, lacuna `pcb.plate_function`). O "bracket" do primeiro passo é identificação nossa pelas fotos, porque o texto da fonte diz "back plate" (`teardown.e1`).

---

## a2.13. A placa aberta: energia, dados e calor

**Na tela:** a vista explodida completa (estágio E8), girando devagar. A carcaça com a grade sobe e mostra o interior do cooler. Selos: confirmado, provável e ilustrativo. Não há os caminhos coloridos nesta tela (ver relatório).

**Fala:** Com a placa toda aberta, dá para resumir o que ela faz em três caminhos. A energia entra pelo conector de 16 pinos e passa por fileiras de indutores, que vemos nas fotos da PCB, antes de chegar ao chip, mas como esse circuito de energia é organizado não achamos nas fontes lidas. Os dados entram pelo PCIe, vão ao chip e à memória, e a imagem sai pelas quatro saídas de vídeo. O calor sai do chip, passa pela pasta térmica para o cooler e é levado pelo ar dos ventiladores. O interior do cooler que aparece aqui é proposta nossa, provável, porque nenhum teardown que lemos abre o cooler desta placa. Dos três caminhos, o dos dados é o que interessa à arquitetura, e ele começa na memória.

**Palavras novas**
- **Indutor:** componente que guarda energia num campo magnético. Em fileira perto do chip, faz parte do circuito que prepara a energia para ele.
- **Vista explodida:** desenho com as peças afastadas umas das outras, na ordem em que se montam.

**Perguntas possíveis**
1. *Quantas fases de energia a placa tem?* Não achamos nas fontes lidas (lacuna `power.vrm.phases`). Os números da RTX 5090 Founders Edition divergem entre si e são de outra placa. Nossa proposta, provável, é de 24 fases para o chip e 4 para a memória, sem fonte. Fase é cada circuito em paralelo que entrega uma parte da corrente ao chip.
2. *A placa tem câmara de vapor?* Provavelmente. A NVIDIA diz que a RTX 5090 Founders Edition tem câmara de vapor 3D, e um revisor (Jon Peddie) descreve câmaras de vapor nesta placa, mas nenhum teardown lido mostra o interior do cooler (`ref5090.vapor_chamber`, `card.vapor_chamber_jpr`, lacuna `cooler.interior`). Câmara de vapor é uma chapa oca e selada com um pouco de líquido, que espalha o calor.
3. *Como o vídeo chega às saídas?* Há um cabo flat, mas a outra ponta não aparece nas fotos. Supomos, provável, que leve o vídeo até as saídas, porque a RTX 5090 Founders Edition tem a PCB em três peças (`ref5090.pcb_pieces`, lacuna `pcb.flat_cables_link`).

---

## a3.1. A memória própria da placa: 96 GB

**Na tela:** a PCB em vitrine, mostrando o verso com os chips de memória. A caixa de texto aponta para um chip do verso. Selos: confirmado e derivado.

**Fala:** Todo processador precisa de uma memória de trabalho, onde ficam os dados e os programas enquanto ele calcula, como a mesa onde se espalham os papéis de uma tarefa. Aqui começa o gerenciamento de memória, item do enunciado: esta GPU tem a sua própria memória, separada da memória do computador, com 96 GB do tipo GDDR7, uma memória feita para placas de vídeo. São 96 GB, o dobro dos 48 GB da geração anterior desta linha, a RTX 6000 Ada. No verso da placa, que está na tela, a Gamers Nexus contou 16 chips de memória, e ela fala em 32 posições no total. Se as 32 posições tiverem chip, cada um guarda 3 GB, porque 32 vezes 3 dá 96, mas essa conta é da própria fonte, e 24 chips de 4 GB também fechariam. Os chips se ligam ao processador por um barramento de 512 bits, ou seja, 512 bits de dados transferidos em paralelo, divididos entre 16 controladores de memória de 32 bits, que são os circuitos do chip que conversam com a memória. A memória tem ECC, um código de correção de erros: bits extras guardados junto com os dados permitem achar e corrigir um bit trocado, e nesta placa o ECC fica sempre ligado. Ter memória na própria placa tem um motivo, a velocidade, que comparamos a seguir.

**Palavras novas**
- **Memória de trabalho (RAM):** onde ficam dados e programas enquanto o processador trabalha. Perde o conteúdo quando a energia acaba.
- **GDDR7:** a sétima geração de memória do tipo GDDR, feita para placas de vídeo.
- **Gerenciamento de memória:** como o sistema decide onde cada dado fica, como chega até quem calcula e como os endereços são traduzidos.
- **Barramento de 512 bits:** 512 bits de dados transferidos em paralelo entre o chip e a memória.
- **Controlador de memória:** circuito dentro do chip que manda os pedidos de leitura e escrita para os chips de memória.
- **ECC:** código de correção de erros. Bits extras que permitem achar e corrigir erros.

**Perguntas possíveis**
1. *Então são 32 chips de 3 GB?* Não está provado. A fonte fala em 32 posições, não em 32 chips, e contou 16 no verso. 32 de 3 GB é dedução da própria Gamers Nexus, e 24 chips de 4 GB também dão 96 GB (`mem.positions`, `mem.chip_gb`, lacuna `mem.chip_density_and_population`).
2. *Como dois chips dividem um controlador?* Não achamos nas fontes lidas. Com 32 posições e 16 controladores, a média é de 2 por controlador, conta nossa. Nossa hipótese, provável, é que cada chip use 16 dos 32 bits (`mem.positions_per_controller`, lacuna `card.mem_pairing_mechanism`).
3. *O ECC corrige quantos bits?* O whitepaper (p. 13) fala em correção de erro simples, isto é, de um bit, sempre ligada e sem opção de desligar (`mem.ecc`). Detecção de erros maiores não está no trecho que lemos.

---

## a3.6. Por que os dados moram na placa

**Na tela:** a PCB em vitrine, agora pela frente, com o chip no meio e os chips de memória em volta. A caixa de texto aponta para um chip de memória da frente. Selos: confirmado e derivado.

**Fala:** Banda é a quantidade de dados que passa por segundo, como a vazão de um cano: quanto mais largo o cano e mais rápida a água, mais litros por segundo. A memória da placa tem 512 bits de largura e cada pino de dados transmite 28 gigabits por segundo, e 512 vezes 28, dividido por 8 bits por byte, dá 1.792 GB/s. A GDDR7 consegue isso em parte com uma técnica chamada PAM3: cada sinal usa três níveis de tensão em vez de dois, e assim carrega 1,5 bit por ciclo. Nesta face, em volta do chip, ficam mais chips de memória, e que sejam 16 é dedução nossa, que só vale se todas as posições tiverem chip: 32 posições menos os 16 do verso. Já a ligação com o resto do computador, o PCIe 5.0 de 16 pistas, leva cerca de 63 GB/s em cada sentido, pela nossa conta a partir dos 32 GT/s, 32 bilhões de transferências por segundo, de cada pista. A memória da placa é, então, cerca de 28 vezes mais rápida que o caminho até o computador, também conta nossa. A consequência, na nossa leitura, é a regra de projeto: copiar os dados para a placa uma vez e fazer as contas aqui dentro, sem ir e voltar a cada passo. Quem faz essas contas é o chip GB202, onde entramos agora.

**Palavras novas**
- **Banda:** quantidade de dados transferida por segundo, em GB/s.
- **Gbps:** gigabits por segundo, bilhões de bits por segundo num único pino.
- **Pino:** cada contato elétrico por onde passa um sinal.
- **PAM3:** sinalização com três níveis de tensão por sinal, em vez de dois.
- **GT/s:** bilhões de transferências por segundo, a taxa de cada pista PCIe.

**Perguntas possíveis**
1. *A comparação de 28 vezes é justa?* Com ressalva. Os 1.792 GB/s são a banda da memória, e os 63 GB/s do PCIe são por sentido, conta nossa (`card.mem_vs_pcie_ratio`, `pcie.x16_gbs_per_direction`). Mesmo somando os dois sentidos, a memória continua bem mais rápida.
2. *De onde vem 63 GB/s?* 32 GT/s por pista, vezes 128/130 da codificação, dividido por 8, vezes 16 pistas, dá 63,0 GB/s. A codificação 128b/130b só achamos na Wikipedia, de baixa autoridade. Sem ela seriam 64 GB/s (`pcie.gen5_lane_gts`, lacuna `mem.gddr7_standard`).
3. *Os chips da frente existem mesmo?* As fotos mostram pads em volta do chip, mas a fonte só conta os 16 do verso. Os 16 da frente no modelo são dedução nossa (32 menos 16), por isso o selo é derivado. Se forem 24 chips de 4 GB, a frente teria 8.

---

## t1.1. Dentro do chip: daqui em diante, diagrama

**Na tela:** o diagrama de blocos do GB202 inteiro: os 12 GPCs, o L2 no centro, os controladores nas laterais e, à esquerda, os contadores e o aviso "Por que 188 e não 192?". A caixa de texto aponta para o die. Selos: confirmado, ilustrativo e derivado.

**Fala:** Agora entramos no chip GB202, e daqui em diante a tela mostra desenho, não foto. Um chip é uma pastilha de silício, chamada die, coberta de transistores, que são chaves elétricas minúsculas que ligam e desligam e, juntas, formam os circuitos de conta e de memória. Este die tem 750 mm², a área de um quadrado de cerca de 2,7 cm de lado, e 92,2 bilhões de transistores, cerca de 123 milhões em cada milímetro quadrado, contas nossas. Ele é fabricado pela TSMC no processo 4N, e o 4 é o nome do processo, não a medida de alguma peça do circuito. O desenho refaz o diagrama de blocos oficial da NVIDIA: as contagens são oficiais, mas a posição física de cada bloco no die não achamos nas fontes lidas, então as posições são ilustrativas. Para a matéria, o que importa é como os blocos se organizam e se ligam, e é isso que o diagrama mostra. Começamos pelos blocos que fazem as contas.

**Palavras novas**
- **Die:** a pastilha de silício que contém o circuito do chip.
- **Transistor:** chave elétrica minúscula. Combinações de transistores formam portas lógicas, somadores e memórias.
- **Processo de fabricação:** o conjunto de técnicas da fábrica (aqui, TSMC 4N) usado para gravar o circuito no silício.
- **Diagrama de blocos:** desenho que mostra as partes de um sistema e como se ligam, sem a posição física real.

**Perguntas possíveis**
1. *4N quer dizer 4 nanômetros?* Não como medida. O whitepaper chama de "4nm 4N NVIDIA Custom Process", mas esse número é rótulo comercial do processo, não o tamanho de algum elemento do circuito (`chip.process`, Tab. 4, p. 48).
2. *Este desenho é uma foto do chip?* Não. É o redesenho da Fig. 3 do whitepaper, um diagrama de blocos. A planta física do die não achamos nas fontes lidas (`chip.block_diagram`).
3. *Como se chega a 123 milhões por mm²?* 92,2 bilhões divididos por 750 mm² dá cerca de 122,9 milhões, conta nossa.

---

## a4.2. Caixas dentro de caixas: GPC, TPC e SM

**Na tela:** os contadores (12 GPCs, 94 TPCs, 188 SMs, 24.064 núcleos), a legenda "1 GPC = 8 TPCs, 1 TPC = 2 SMs, 1 SM = 128 núcleos CUDA" e o GPC 0 em destaque. A caixa de texto aponta para um TPC. Selos: confirmado e ilustrativo.

**Fala:** A organização do chip é de caixas dentro de caixas, e a caixa maior é o GPC, Graphics Processing Cluster, que aparece 12 vezes. Dentro dos GPCs ficam os TPCs, e cada TPC tem 2 SMs, então os 94 TPCs desta placa dão 188 SMs. O SM, Streaming Multiprocessor, é a unidade que recebe os grupos de tarefas, busca as instruções e as executa. Cada SM tem 128 núcleos CUDA, e 188 vezes 128 dá os 24.064 núcleos da ficha técnica. Um núcleo CUDA não é um núcleo como o de uma CPU: é uma unidade de conta que, a cada ciclo, faz uma operação de ponto flutuante de 32 bits, o jeito de guardar números com vírgula, ou uma operação de inteiro de 32 bits. Repetir o mesmo SM muitas vezes é o que dá força à GPU, porque cada SM trabalha num pedaço diferente dos dados ao mesmo tempo. O chip completo tem 192 SMs, mas a tabela desta placa e a contagem de núcleos dão 188, e o motivo da diferença não achamos nas fontes lidas. Esses 188 SMs dividem uma memória rápida, o L2, que no diagrama fica no centro e vem a seguir.

**Palavras novas**
- **GPC (Graphics Processing Cluster):** o maior agrupamento do chip. Tem TPCs e unidades de gráfico.
- **TPC (Texture Processing Cluster):** um par de SMs com uma unidade de geometria.
- **SM (Streaming Multiprocessor):** a unidade que recebe trabalho, busca e executa instruções.
- **Ponto flutuante (FP32):** o jeito de o computador guardar números com vírgula, aqui em 32 bits.
- **Inteiro (INT32):** número sem vírgula, em 32 bits.
- **Ciclo:** uma batida do relógio do chip. Cada operação simples leva pelo menos um ciclo.

**Perguntas possíveis**
1. *Por que 188 e não 192?* O texto da p. 8 do whitepaper diz que a placa usa o GB202 completo, de 192 SMs, mas a Tab. 4 dá 188, e 188 vezes 128 confere com os 24.064 núcleos do datasheet. Adotamos 188. O whitepaper não explica a diferença. A explicação comum, partes do chip desligadas na fábrica, é inferência e não está na fonte (`chip.sm_count`, `chip.sm_count_full`, lacuna `chip.sm_count_reason`).
2. *Como os 94 TPCs se dividem pelos 12 GPCs?* O chip completo tem 8 TPCs por GPC, 96 no total. Com 94, a divisão não é inteira, e quais GPCs têm menos não achamos nas fontes lidas. As posições apagadas no desenho são ilustrativas (`chip.tpc_per_gpc`, lacuna `chip.tpc_gpc_distribution`).
3. *O que mais tem num GPC?* Segundo o whitepaper (p. 9), além dos 8 TPCs, um Raster Engine e duas partições de ROP com 8 ROPs cada, que são unidades de gráfico. Cada TPC tem uma PolyMorph Engine e 2 SMs.

---

## a4.4. L2 no centro, controladores nas laterais

**Na tela:** o diagrama inteiro, com o L2 e os 16 controladores (MC) em destaque e linhas animadas do L2 para cada controlador. A caixa de texto aponta para o L2. Selos: confirmado, derivado e ilustrativo.

**Fala:** Cache é uma memória pequena e rápida, perto de quem calcula, que guarda cópias dos dados usados há pouco. É como deixar na mesa os livros que você está usando em vez de ir à biblioteca toda vez, com uma diferença: a cache guarda cópias, e o original continua na memória da placa. No centro do diagrama fica o L2, uma cache de 128 MB que todos os GPCs dividem. Ele é o segundo nível, porque cada SM ainda tem a sua cache L1, de 128 KB, que veremos ao abrir o SM. Nas laterais do diagrama ficam os 16 controladores de memória, cada um com 32 bits de largura, e 16 vezes 32 dá os 512 bits do barramento até os chips GDDR7. As linhas na tela mostram esse caminho: quando um dado não está no L2, ele é buscado na memória da placa por um dos controladores. Um L2 grande significa, em geral, menos viagens até essa memória, que é mais lenta, e a geração anterior, a RTX 6000 Ada, tinha 96 MB de L2. Agora vamos abrir um dos 188 SMs, onde as instruções são de fato executadas.

**Palavras novas**
- **Cache:** memória pequena e rápida que guarda cópias dos dados usados há pouco.
- **L1 e L2:** níveis de cache. L1 fica dentro de cada SM e é a mais perto. L2 é maior e dividida pelo chip inteiro.
- **Acerto e falta (hit e miss):** acerto é quando o dado está na cache, falta é quando precisa buscar no nível de baixo.

**Perguntas possíveis**
1. *Qual a política do L2: associatividade, substituição, escrita?* Não achamos nas fontes lidas. O whitepaper dá só o tamanho (lacuna `cache.policy`).
2. *Quanto a memória é mais lenta que o L2?* Medido numa placa da mesma geração, a RTX 5080: cerca de 358 ciclos para um acerto no L2 e cerca de 877 para a memória. Na nossa placa não foi medido, por isso o selo é derivado. Fonte: Jarmusch et al., seção VI (`lat.l2_cycles`, `lat.global_cycles`).
3. *O L1 é só cache?* Não. Os 128 KB do SM são divididos entre cache L1 e memória compartilhada, que o programa usa diretamente, e o programa escolhe a divisão quando roda. Isso aparece no momento a5.14 (`sm.l1_shared_kb`, `mem.l1_carveout`).

---

## Nota sobre o corte do seminário (2026-11-16)

As falas do seminário foram encurtadas para caber em 22 minutos (`harness/content/pt-BR/reescrita/final.json`). Desta parte, saíram do corte os momentos **a2.13** (placa aberta), **t1.1** (entrada no chip) e **a4.4** (planta do L2). A ressalva de que o diagrama é desenho, com contagens oficiais e posições ilustrativas, passou para a fala de a4.2. O L2 de 128 MB aparece em a5.13. As falas completas, de todos os momentos, continuam aqui e servem para estudo e para responder perguntas.

---

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

**Fala:** Saímos da planta do chip e entramos em um dos 188 SMs, sigla de Streaming Multiprocessor, que é o bloco do chip que executa os programas. Um núcleo de processador comum repete sempre a mesma rotina: lê uma instrução, busca os números, faz a conta e guarda o resultado. O SM tem as peças dessa rotina, acesas na tela: o escalonador, que escolhe a próxima instrução, o banco de registradores, que guarda os números em uso, e o cache L1, uma memória pequena e rápida de 128 KB, perto das contas. A diferença está na quantidade: o SM tem 128 núcleos CUDA, e cada núcleo faz contas simples e trabalha, em cada ciclo, que é uma batida do relógio do chip, ou com número inteiro ou com número com vírgula, nunca com os dois ao mesmo tempo. Esses 128 núcleos estão divididos em 4 partições iguais, e cada partição tem o seu escalonador, o seu banco de registradores, 32 núcleos, conta nossa de 128 dividido por 4, e 1 Tensor Core, uma unidade que faz contas de matrizes. Embaixo, comum às quatro partições, fica o RT Core, a unidade de traçado de raios, usada em imagens 3D. Nossa leitura do porquê: a GPU aplica a mesma conta a muitos dados, e repetir muitas unidades simples é o jeito de fazer muitas contas ao mesmo tempo. Para entender como essas unidades recebem trabalho, começamos pelo escalonador e pelo pipeline.

**Palavras novas**
- **SM (Streaming Multiprocessor):** o bloco do chip que executa os programas. A placa tem 188.
- **Escalonador:** a parte que escolhe qual instrução vai ser executada a seguir.
- **Registrador:** memória minúscula e muito rápida dentro do circuito, que guarda um número em uso.
- **Cache L1:** memória pequena e rápida dentro do SM, que guarda cópias de dados usados há pouco.
- **Núcleo CUDA:** unidade que faz contas simples. Em cada ciclo opera como inteiro ou como número com vírgula (INT32 ou FP32), nunca os dois.
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

**Fala:** Imagine um professor que dita uma conta para 32 alunos, e cada aluno faz a conta com os números do seu próprio caderno. A NVIDIA chama esse modelo de SIMT, sigla em inglês para uma instrução, muitas threads: o escalonador manda uma instrução, e as 32 threads do warp a executam, cada uma com os seus dados. Existe um modelo parecido, o SIMD, uma instrução, muitos dados, em que uma instrução opera sobre uma fileira de números de uma vez. Segundo o guia de programação da NVIDIA, no SIMT cada thread guarda o seu próprio estado: os seus registradores e o seu contador de programa, que marca em que instrução ela está. Na nossa leitura, essa é a diferença que importa em relação ao SIMD. Aqui a comparação com a sala de aula deixa de valer, porque cada thread pode, se os seus dados pedirem, seguir por outro trecho do programa. Cada SM mantém até 48 warps ao mesmo tempo, ou 1.536 threads, conta nossa, e o estado de todos eles fica guardado dentro do chip. A vantagem, na nossa leitura de como o guia descreve o escalonador, é que quando um warp para esperando um dado da memória, o escalonador passa para outro warp que já tem o que precisa, e o SM não fica parado. Quando as threads de um mesmo warp seguem caminhos diferentes, acontece a divergência, que as quatro threads laranja vão mostrar agora.

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

**Fala:** O exemplo é o SAXPY, um programa curto que, para cada posição de dois vetores, faz y receber a vezes x mais y, e nós o compilamos para o alvo desta placa, o sm_120, com as ferramentas oficiais da NVIDIA. A coluna da direita é o SASS, o código de máquina que a placa executa, e nele cada registrador aparece com uma letra que diz o tipo. R são os registradores comuns, um conjunto para cada thread: R2 recebe o valor de x daquela thread e R7, o valor de y. UR é o que a documentação chama de registrador uniforme, e, segundo um estudo da geração Ampere, ele guarda um valor igual para o warp inteiro, como aqui o UR6, que, pela nossa leitura, guarda o número a, e a instrução FFMA calcula UR6 vezes R2 mais R7 numa só operação. SR são registradores especiais que o próprio hardware preenche: na instrução S2R, cada thread lê o seu número dentro do bloco, SR_TID.X, e a instrução IMAD usa esse número para calcular qual elemento do vetor é dela. P é um registrador de predicado, que guarda o resultado de uma comparação: a linha em destaque, ISETP, compara esse índice com o tamanho do vetor e grava a resposta em P0, e a linha seguinte encerra as threads que passaram do fim. O compilador informou 10 registradores por thread e zero bytes de spill, que é quando faltam registradores e valores precisam ir para a memória, que é bem mais lenta. Esse número 10 importa, porque decide quantos warps cabem no SM ao mesmo tempo.

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

**Fala:** Numa CPU, a quantidade de registradores é fixa e faz parte da definição do processador, então todo programa vê o mesmo número. Na GPU, quem decide quantos registradores cada thread usa é o compilador, e o limite oficial é de 255 por thread. Só que os quatro bancos do SM somam 65.536 registradores, e esse total é repartido entre todos os warps que estão no SM. Faça a conta: um warp de 32 threads com 255 registradores cada gasta 8.160 registradores, e 65.536 dividido por 8.160 dá só 8 warps no SM, conta nossa, que ignora regras de arredondamento da alocação que não achamos nas fontes lidas. Já o SAXPY, com 10 registradores por thread, gasta 320 por warp, e daria para mais de 200 warps, mas aí vale outro limite oficial: no máximo 48 warps por SM. Com só 8 warps, o escalonador tem menos opções para trocar quando um warp para esperando a memória, e por isso, na nossa leitura, o compilador tenta gastar poucos registradores. É uma troca: mais registradores por thread evitam o spill, e menos registradores deixam caber mais warps. Esses registradores aparecem dentro das instruções, e o próximo passo é o conjunto de instruções em si.

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

**Fala:** Toda instrução, no fim, é uma sequência de bits, zeros e uns, e um processador pode usar instruções de tamanho variável ou de tamanho fixo. Com tamanho variável, o circuito precisa ler parte da instrução para saber onde ela termina e a próxima começa, e com tamanho fixo ele já sabe de antemão. Nesta placa, todas as instruções SASS têm 16 bytes, ou 128 bits: a documentação da NVIDIA diz isso, e na nossa listagem os endereços andam sempre de 16 em 16. Na tela está a instrução FFMA do SAXPY, escrita como as duas palavras de 64 bits que a ferramenta mostra. Um estudo de 2018 sobre a geração Volta abriu os 128 bits das instruções daquela geração: pelo menos 91 são a instrução em si, pelo menos 23 são bits de controle, que são avisos do compilador para o escalonador, e 14 parecem sem uso. Ou seja, o compilador resolve antes parte da organização do pipeline e grava a solução dentro da instrução, e um estudo de 2025 sobre a geração Ampere descreve esses avisos, como um contador que diz quanto tempo o warp deve esperar. Na Blackwell, só achamos documentada a largura de 128 bits, e por isso a figura marca os bits de controle desta placa como não documentados. Tamanho fixo é uma das marcas dos processadores RISC, e isso leva à pergunta do enunciado: esta GPU é RISC ou CISC.

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

**Fala:** CISC e RISC são duas filosofias de projeto de conjunto de instruções. CISC quer dizer Complex Instruction Set Computer, computador com conjunto de instruções complexo: uma só instrução pode ler a memória, fazer a conta e gravar o resultado, e as instruções têm tamanhos diferentes. RISC quer dizer Reduced Instruction Set Computer, computador com conjunto de instruções reduzido: cada instrução faz uma coisa simples, todas têm o mesmo tamanho, só as instruções de carga e de armazenamento tocam a memória, e as contas acontecem entre muitos registradores. Usamos esses critérios na tabela, e três deles apontam para RISC: as instruções têm 16 bytes fixos, a memória global e a compartilhada são acessadas, como regra, por instruções de carga e armazenamento, como LDG e STG, e cada thread pode usar até 255 registradores. Dois pontos afastam do RISC clássico: a HMMA, que compilamos, faz o warp inteiro multiplicar um bloco de matriz nos Tensor Cores, 2.048 multiplicações com soma numa só instrução, pela nossa conta de 16 vezes 8 vezes 16, e a LDGSTS e a UTMALDG, pela descrição oficial, copiam da memória global para a compartilhada, de memória para memória. A quantidade, 258 instruções na lista oficial pela nossa contagem, não decide, porque o reduzido de RISC fala da simplicidade de cada instrução, e sobre microcódigo não achamos nada nas fontes lidas. Nas fontes que lemos, a NVIDIA não classifica o SASS, então esta é a conclusão do grupo: é RISC no formato e na regra de acesso à memória, com instruções próprias de acelerador, e nossa leitura do porquê é que um formato fixo é simples de decodificar a cada ciclo, enquanto as instruções grandes fazem numa ordem só um trabalho que pediria muitas instruções simples. Essas instruções de carga buscam dados na memória, e quanto tempo isso leva depende de onde o dado está, que é o assunto da hierarquia de memória e dos caches.

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

---

## Nota sobre o corte do seminário (2026-11-16)

As falas do seminário foram encurtadas para caber em 22 minutos (`harness/content/pt-BR/reescrita/final.json`). Desta parte, saíram do corte os momentos **a5.16** (divergência) e **a5.7** (registradores na listagem SASS). A ideia essencial da divergência entrou numa frase de a5.2, e o SAXPY, com os seus 10 registradores por thread, é apresentado em a5.8. A ordem também mudou: a5.1 e a5.2 (warp e SIMT) vêm antes de a5.5 (pipeline). As falas completas, de todos os momentos, continuam aqui e servem para estudo e para responder perguntas.

---

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
