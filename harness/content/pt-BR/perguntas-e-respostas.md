# Perguntas que o professor pode fazer, e a resposta curta

Para os 18 slides do corte curto. As respostas vêm dos roteiros de estudo que já passaram pela auditoria de fatos, escritas mais curtas. Cada um leva a folha dos seus slides.

## Regra de ouro

O professor pediu que, quando um item não existe ou não é público, o trabalho **diga isso e explique por quê**. Então "não achamos" não é falha, é a resposta que ele quer. Use sempre este formato:

> "Isso não achamos nas fontes que lemos. O que achamos de mais próximo foi [X]."

Nunca invente um número ou um motivo. Se não souber, diga que não achamos.

## Duas perguntas que só o professor responde

1. Os 22 minutos incluem as perguntas?
2. O grupo pode ter 5 integrantes? (O resumo do enunciado diz "até 4", e a proposta entregue tem 5.)

---

## Slides 1 a 3: abertura, CPU e GPU, placa de vídeo (Vitor)

**Um núcleo CUDA é igual a um núcleo de CPU?**
Não. O núcleo CUDA só faz a conta (uma operação com números inteiros ou com vírgula de 32 bits por ciclo). Quem se parece com um núcleo de CPU é o SM, que tem escalonador, registradores e cache próprios.

**De onde vem o 24.064?**
Da ficha técnica da NVIDIA. Confere com a conta: 188 SMs × 128 núcleos = 24.064.

**O que quer dizer "Workstation"?**
É a edição para estações de trabalho, os computadores profissionais.

## Slide 4: por dentro da placa (Vitor)

**Por que pasta térmica e não metal líquido?**
A fonte não explica. Ela só diz que esperava metal líquido, como na RTX 5090 Founders Edition, e achou pasta. Não vamos supor o motivo.

**Para que serve a placa que cobre o circuito, e a mola?**
Não achamos. A fonte só diz que a placa saiu com uma alavanca e que os parafusos da mola saíram. O nome "bracket" do primeiro passo é identificação nossa pelas fotos.

## Slide 5: o chip GB202 (Vitor ou João)

**Por que 188 SMs e não 192?**
O chip completo tem 192, e o texto do whitepaper diz que esta placa usa o chip completo. Mas a tabela dele dá 188, e 188 × 128 fecha com os 24.064 núcleos da ficha técnica. Adotamos 188. O whitepaper não explica a diferença.

**O "4" de TSMC 4N é 4 nanômetros?**
Não. É o nome do processo de fabricação, não a medida de nenhuma peça do circuito.

**O que está escrito no chip?**
A Gamers Nexus lê "GB 202-870-A1". Na foto só dá para ler em parte, então confiamos no texto dela.

## Slide 6: memória de 96 GB (Arthur)

**São 32 chips de 3 GB?**
Não está provado. A fonte fala em 32 posições e contou 16 chips no verso. 32 × 3 GB dá 96 GB, mas 24 chips de 4 GB também dão, e as fontes não excluem isso.

**Como dois chips dividem um controlador?**
Não achamos. A nossa hipótese, provável: cada chip usa 16 dos 32 bits do controlador.

**O ECC corrige quantos bits?**
Corrige um bit trocado (correção simples), e fica sempre ligado.

## Slide 7: pipeline (João)

**Quantos estágios tem o pipeline da Blackwell?**
Não achamos. A NVIDIA não descreve os estágios. Um estudo de outra geração, a Ampere, descreve etapas como busca, decodificação e emissão, mas não dá a profundidade total.

**Os 4 ciclos foram medidos nesta placa?**
Não, numa RTX 5080, da mesma família. É valor derivado.

**Quanto dura um ciclo?**
O clock de boost é 2.617 MHz, então um ciclo dura cerca de 0,38 nanossegundo (1 ÷ 2,617 GHz, conta nossa).

**Como o escalonador escolhe o warp?**
O guia da NVIDIA só diz que ele escolhe, a cada ciclo, um warp com threads prontas. A regra exata não achamos.

## Slides 8 e 10: registradores (Lorenzo)

**Como 256 KB viram 65.536 registradores?**
Cada registrador tem 32 bits, ou 4 bytes. 256 KB ÷ 4 B = 65.536. Também são 4 bancos × 16.384.

**Trocar de programa inteiro também não tem custo?**
Não. "Sem custo" vale só para trocar entre warps que já estão no SM. Trocar o programa inteiro (preempção) salva o contexto na memória.

**Como o banco de registradores é construído por dentro?**
Na Blackwell não achamos. Há medidas de outras gerações (Volta e Ampere), mas não valem para esta.

**De onde vem o 255 por thread?**
Do guia de ajuste da Blackwell da NVIDIA: "o máximo de registradores por thread é 255".

**A conta de 8 warps é exata?**
É aproximada. A alocação real tem regras de arredondamento que não achamos.

## Slide 9: conjunto de instruções (Lorenzo)

**Quando a tradução de PTX para SASS acontece?**
Pode ser na compilação (o `ptxas`) ou na hora de rodar, pelo driver. No nosso experimento, quem traduziu foi o compilador `nvcc`, que chama o `ptxas`.

**O PTX é igual em todas as gerações?**
Não "igual": é estável e tem versão. O nosso é o 9.5.

**Por que o mesmo SASS não roda em qualquer GPU NVIDIA?**
Porque o SASS é o código de máquina de cada geração. Só com o PTX embutido o programa fica compatível com GPUs futuras.

## Slide 11: CISC ou RISC (Lorenzo)

**Então é RISC ou não?**
Pelo formato (16 bytes fixos) e pela regra de acesso à memória, sim, RISC. Não é RISC puro, porque tem instruções de acelerador (matriz, textura, cópia assíncrona). A NVIDIA não classifica, então é **análise do grupo**.

**O artigo dizia só "RISC". Mudou?**
Não, aprofundamos. O artigo olhou o exemplo SAXPY, de 20 instruções. Aqui olhamos a lista oficial, de 258, e por isso apontamos as exceções.

**Como são 2.048 multiplicações numa instrução?**
A HMMA multiplica um bloco 16 × 8 × 16, e 16 × 8 × 16 = 2.048 (conta nossa).

**Existe processador RISC na GPU?**
Sim, o AMP, que escalona contextos, é RISC-V. Ele fica fora do SM e não diz nada sobre o SASS.

**Cuidado:** as definições de CISC e RISC são as clássicas da disciplina. Não registramos um livro como fonte. Se pedirem a referência, diga que são os critérios clássicos.

## Slide 12: cache (Arthur)

**Por que as latências são de outra placa?**
Não achamos medida do GB202. A RTX 5080 é da mesma família e tem os mesmos 256 KB de registradores e 128 KB de L1 por SM. Por isso são valores derivados.

**O cache é associativo? Qual a política de escrita? Qual o tamanho da linha?**
Não achamos. O whitepaper só dá tamanhos.

## Slides 13 e 14: MMU (Thiago)

**Por que o artigo diz 49 bits e o seminário 57?**
Os 49 bits e 5 níveis são da Pascal, de 2016. O código atual do driver diz que a família do GB202 usa o formato da Hopper: 57 bits e 6 níveis. É atualização, não erro de fonte.

**Isso descreve o circuito?**
Não diretamente. O código do driver mostra o que o software programa. Documento de hardware de MMU só achamos o da Pascal.

**Cada programa tem o próprio espaço de endereços?**
Numa CPU, sim. Nesta GPU não achamos fonte que descreva isso.

**Como as contas fecham?**
Índices de 1, 9, 9, 9 e 8 bits somam 36. Para página de 4 KB: 36 + 9 + 12 de deslocamento = 57. 96 GB ÷ 512 MB = 192 páginas.

## Slide 15: falha de página (Thiago)

**Toda falha pode ser repetida?**
Não. As do motor gráfico são repetíveis. As dos motores de cópia e de submissão não são. As de outros motores são fatais.

**Falha de página é sempre erro?**
Não. Com memória unificada, é o jeito normal de trazer uma página para a GPU. Erro é o acesso a endereço ilegal, que aparece como Xid 31.

**Como a CPU fica sabendo?**
Por interrupção: a metade de cima do tratador agenda o atendimento numa thread do sistema.

## Slide 16: interrupções (Thiago)

**O que é o Xid 13 que aparece na tela?**
"Graphics Engine Exception": o código do driver para falhas gerais de programa, como passar do fim de um vetor. Nenhuma fonte liga o `trap` a um Xid específico.

**Qual modo de interrupção esta placa usa na prática?**
Não achamos. O driver tenta MSI-X ou MSI e, se falhar, usa a linha legada.

**Existe trap no código de máquina?**
Sim. A lista da Blackwell tem a instrução `BPT` (breakpoint e trap).

## Slides 17 e 18: lacunas e resumo (Vitor)

**Por que a NVIDIA não documenta isso?**
Não sabemos o motivo e não especulamos. Dizemos só o que as fontes lidas cobrem e onde param.

**O que vocês não leram?**
Os artigos de medição da Hopper e do B200, a memória unificada no guia CUDA atual e um documento de hardware de MMU da Hopper ou da Blackwell, que não achamos.

**Por que confiar em medida de outra placa?**
Não confiamos como se fosse desta: dizemos em que placa foi medida. A RTX 5080 é da mesma família.

**A GPU tem MMU própria?**
Sim. O código do driver programa a tabela de páginas dela, e o código de erro Xid 31 aparece quando a MMU da GPU reporta falha.

**Qual item ficou mais fraco?**
Pipeline e cache: temos a estrutura e os tamanhos, mas o número de estágios e a política dos caches não estão nas fontes lidas.
