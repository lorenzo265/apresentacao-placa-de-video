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
