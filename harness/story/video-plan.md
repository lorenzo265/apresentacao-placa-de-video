# Plano da apresentação em vídeo (v0.2)

Estado: **proposta para o gate humano da F6**. Nada aqui foi implementado. Complementa `harness/ARCHITECTURE.md` (seções 1, 5 e 7.3) e depende de `harness/design/assembly-plan.md` para os atos da placa física.

## 1. O que muda em relação à v0.1

| Tema | v0.1 (ARCHITECTURE.md) | v0.2 (este plano) |
|---|---|---|
| Vídeo | "pode ser exportada em vídeo" (opcional) | entregável de primeira classe, com cortes, especificação técnica e QA próprios |
| Unidade do roteiro | uma peça por beat, um texto por peça | **atos e beats**: uma seção do roteiro tem vários beats, cada beat tem uma ideia só |
| Texto na tela | texto longo (5 seções fixas) na caixa | três densidades: `headline`, `caption` (vídeo) e `body` (texto longo, só no viewer) |
| Duração | indefinida | um storyboard, vários **cortes** por prioridade de beat |
| Captura | Playwright + ffmpeg, sem método | relógio virtual, quadro a quadro, renderizado por beat com cache |
| Níveis 2 a 4 (chip) | "diagrama" sem dono | diagramas declarativos gerados a partir do spec, com agente e contrato próprios |
| Fonte na tela | só o selo de procedência | selo **e** linha de fonte em todo beat que mostra número |
| Fala | não prevista | notas de fala por beat, legendas `.vtt` geradas delas |

## 2. Entregáveis de vídeo

| Corte | Para quê | Beats | Duração |
|---|---|---|---|
| `seminario` | apoio visual da fala ao vivo, em 16/11 | só prioridade 1 (48 beats) | **alvo de 20 min, teto de 22 min** (duração informada pelo autor em 2026-11-10) |
| `completo` | tour inteiro no viewer e vídeo de arquivo | todos (62 beats) | sem limite |
| `teaser` | abertura do seminário, sem fala | lista fixa de 6 a 8 beats | 30 a 45 s |

Regra: existe **um** `storyboard.json`. Cada beat tem `priority` (1 essencial, 2 reserva, 3 só no completo). O corte é um filtro, não um segundo roteiro.

### 2.1 Orçamento de tempo do corte do seminário

Duração informada pelo autor em 2026-11-10: **22 minutos** (antes, de 15 a 20). O alvo passa a 20 minutos, para sobrar margem de fala e de troca de apresentador. O tempo a mais foi para o chip, que é o que o enunciado cobra: os sete beats de reserva dos atos 4 a 6 (a4.3, a4.5, a5.3, a5.15, a5.8, a5.11 e a6.3) subiram para a prioridade 1. A placa física ficou com o mesmo orçamento. São 48 beats de prioridade 1.

| Ato | Seções | Beats (prio 1) | Tempo | Acumulado | Base |
|---|---|---|---|---|---|
| 0. Abertura | 01 | 4 | 0:40 | 0:40 | orçamento |
| 1. A placa por fora | 01 | 3 | 1:00 | 1:40 | orçamento |
| 2. Desmontagem e os três caminhos | 02 | 8 | 2:20 | 4:00 | orçamento |
| 3. Memória e barramentos | 03 | 3 | 1:10 | 5:10 | orçamento |
| T1 e 4. O chip e SIMT | 04, 05 | 9 | 3:20 | 8:30 | medido no viewer |
| T2 e 5. Dentro do SM | 06 a 09, 12 | 13 | 6:20 | 14:50 | medido no viewer |
| 6. A GPU no sistema | 10, 11 | 5 | 3:33 | 18:23 | medido no viewer |
| 7. Fechamento | 13, 14 | 3 | 1:39 | 20:02 | 1:09 medido (a7.1 e a7.4) mais 0:30 de orçamento para a remontagem (a7.5) |

Leitura do orçamento: 5 minutos para a placa física (o gancho visual) e 15 minutos para os itens que o enunciado cobra. O tempo medido é o que o viewer leva tocando sozinho (transição, entrada da chamada, `hold` e saída): 14:23 nos 29 beats prontos do corte. Ao vivo quem dita o ritmo é a fala, que costuma passar disso. A margem até os 22 minutos é de cerca de 2 minutos. Se o ensaio passar de 21 minutos, o corte sai primeiro dos atos 1 e 2, depois dos sete beats promovidos, nunca do resto dos atos 5 e 6.

Os beats de prioridade 2 que restaram (todos da placa física) ficam prontos como reserva: entram no viewer ao vivo se alguém perguntar, sem contar no tempo.

Formato do seminário (decidido em 2026-11-10): **viewer ao vivo, em um arquivo `.html` único, avançando beat a beat pelo teclado**. O vídeo fica suspenso por enquanto: ficou pesado, e o HTML abre em qualquer computador sem internet. A captura em MP4 continua disponível como plano de reserva, se o grupo voltar a querer.

## 3. Estrutura em atos

As 14 seções do roteiro v2 não mudam (a tabela de cobertura do enunciado continua válida). O que muda é que cada seção passa a ter vários beats. O número da seção aparece na tela, para o professor ligar o vídeo ao texto escrito.

| Ato | Nível | Seções | Conteúdo | Selo dominante |
|---|---|---|---|---|
| 0. Abertura | 0 | 01 | placa montada, título, ficha, mapa do tour | confirmado |
| 1. A placa por fora | 0 | 01 | volta externa: frente, topo, conector, bracket, traseira | confirmado (ficha); forma a derivar de fotos ainda não catalogadas |
| 2. Desmontagem e os três caminhos | 1 | 02 | teardown na ordem real; energia, dados e calor destacados por cor | derivado e provável |
| 3. Memória e barramentos | 1 | 03 | chips GDDR7, 16 controladores de 32 bits, PCIe, saídas | confirmado (números), derivado (posição) |
| T1. Mergulho no chip | 1 para 2 | 04 | zoom contínuo: package, die, planta | muda para ilustrativo |
| 4. O chip | 2 | 04, 05 | GPC, TPC, SM, L2, controladores, SIMT | confirmado (contagens), ilustrativo (forma) |
| T2. Mergulho no SM | 2 para 3 | 06 | zoom em um SM | ilustrativo |
| 5. Dentro do SM | 3 e 4 | 06 a 09, 12 | unidades, registradores, instruções, RISC ou CISC, caches, ocupação | confirmado, derivado, análise do grupo |
| 6. A GPU no sistema | 4 | 10, 11 | MMU, envio de comandos, interrupções, AMP, MIG | confirmado (driver aberto), derivado (Pascal) e leitura do grupo onde indicado |
| 7. Fechamento | 0 | 13, 14 | Ada contra Blackwell, lacunas, remontagem, fontes | confirmado e derivado |

### 3.1 Os três caminhos como fio condutor

A mensagem central do briefing (energia, dados e calor) vira um recurso visual fixo, usado do ato 2 ao ato 7:

| Caminho | Cor | Na placa (nível 1) | No chip (níveis 2 a 4) |
|---|---|---|---|
| Energia | âmbar | conector, indutores, fases, die | não se aplica |
| Dados | ciano | contatos PCIe, GPU, memória, saídas de vídeo | controladores de memória, L2, SM, instrução |
| Calor | vermelho-alaranjado | die, interface térmica, câmara de vapor, aletas, ar | não se aplica |

O caminho de dados é o único que atravessa a transição T1. Ele é o que liga visualmente a placa física (onde a nota não está) ao chip (onde a nota está). Cor nunca é o único código: cada caminho tem também ícone e rótulo.

## 4. Lista de beats

Legenda de prioridade: 1 essencial, 2 seminário, 3 só no corte completo. "Fonte" indica onde o número já está registrado. Beats marcados **bloqueado** não podem ser escritos enquanto a fonte não existir (regra "sem fonte, sem fato").

### Atos 0 a 3: placa física

Fontes abreviadas: "datasheet" é o PDF oficial da placa, "GN" é o teardown desta placa pela Gamers Nexus, "JPR" é a análise da Jon Peddie Research, "5090 FE" é a placa irmã. Tudo em `harness/spec/sources/physical-card-sources.md`. Os estágios E1 a E8 estão em `harness/design/assembly-plan.md`, seção 3.

| Beat | Seção | O que se vê | Texto na tela (ideia) | Procedência | Fonte | Prio |
|---|---|---|---|---|---|---|
| a0.1 | 01 | tela escura; a contraluz revela a silhueta; entra o logotipo do grupo (32 quadrados em grade 8 × 4, 4 em laranja) | título do trabalho, disciplina, grupo Warp 32 | não se aplica | | 1 |
| a0.2 | 01 | giro lento da placa montada | RTX PRO 6000 Blackwell Workstation Edition | confirmed | datasheet | 1 |
| a0.3 | 01 | ficha entra linha a linha | 96 GB GDDR7 com ECC, 600 W, 24.064 núcleos CUDA, PCIe 5.0 x16 | confirmed | datasheet, p. 3 | 1 |
| a0.4 | 01 | mapa do tour | cinco níveis, três caminhos, quatro selos | não se aplica | | 1 |
| a1.1 | 01 | face A: dois ventiladores de 7 pás e o X central | dois ventiladores na mesma face | confirmed (dois, na frente, texto da GN); derived (7 pás contadas em foto, faixa de 7 a 8; axiais) | GN, foto gn-02; datasheet | 1 |
| a1.2 | 01 | réguas no comprimento e na altura | 5,4" × 12,0" (137,2 × 304,8 mm), dois slots | confirmed (polegadas), derived (mm) | datasheet, p. 3 | 2 |
| a1.3 | 01 | a placa gira para a face B (duas grades e o X com "RTX PRO 6000"); o ar entra pela face A e sai pela face B nas duas pontas | "double-flow-through": o ar atravessa a placa em vez de bater no PCB | confirmed (atravessa a placa; grades na face B); derived (sentido da face A para a B) | datasheet, p. 1 e 3; GN ("pushes air straight through the card rather than into a PCB"), fotos gn-03 e gn-08 | 1 |
| a1.4 | 01 | topo, conector de energia: 12 pinos de potência e 4 de sinal | um conector de 16 pinos (PCIe CEM5); a placa inteira consome até 600 W, cerca de 50 A se tudo viesse em 12 V (conta nossa) | confirmed (tipo; 600 W de potência total da placa); derived (posição no topo, JPR) | datasheet, p. 3; JPR | 1 |
| a1.5 | 01 | bracket de chapa lisa com 4 portas em fileira | 4 DisplayPort 2.1b | confirmed | datasheet, p. 3; foto gn-16 | 2 |
| a1.6 | 01 | placa ao lado do contorno da 5090 FE | carcaça quase idêntica, segundo a Puget; outro propósito: 96 GB com ECC | derived | Puget Systems | 3 |
| a2.1 | 02 | E1: sai o bracket | a desmontagem segue a ordem de um teardown real | confirmed (ordem); derived (a peça é o bracket: o texto diz "back plate", a identificação vem das fotos) | GN, fotos gn-14 a gn-16 | 1 |
| a2.2 | 02 | E2: um parafuso, sai o aro da face B | | confirmed (ordem); derived (forma do aro, por foto) | GN, foto gn-17 | 1 |
| a2.3 | 02 | E3: parafusos e tampas centrais | | confirmed | GN | 2 |
| a2.4 | 02 | E4: grampo e adaptador PCIe | o conector PCIe é uma peça separada | confirmed | GN | 1 |
| a2.5 | 02 | E5: placa que cobre o PCB | | confirmed (existe); função é lacuna | GN | 2 |
| a2.6 | 02 | E6: cabos flat e mola de pressão | | confirmed | GN | 2 |
| a2.7 | 02 | E7: sai o PCB quase quadrado do centro da placa, entre as duas pilhas de aletas; close na pasta sobre o die | pasta térmica, não metal líquido como na 5090 FE: derivar da placa irmã pode errar | confirmed | GN; 5090 FE (NVIDIA) | 1 |
| a2.8 | 02 | vista explodida inteira, pausa | os três caminhos | não se aplica | | 1 |
| a2.9 | 02 | caminho da energia em âmbar: conector, indutores, die | 600 W de potência total da placa; não achamos fonte com o número de fases | confirmed (conector, 600 W totais), **inferred** (fases, a propor na F2) | datasheet; lacuna | 1 |
| a2.10 | 02 | caminho dos dados em ciano: contatos PCIe, adaptador, cabo flat, GPU, memória, saídas | o trajeto pelos cabos é o da placa irmã | confirmed (as peças existem), derived (o que os cabos ligam e as três placas, 5090 FE) | GN; NVIDIA (5090 FE) | 1 |
| a2.11 | 02 | E8 e caminho do calor em vermelho: die, pasta, câmara de vapor, aletas, ar | não achamos fonte que mostre o interior do cooler desta placa | confirmed (pasta, aletas), derived (câmara de vapor), inferred (E8: ordem e interior) | GN; 5090 FE | 1 |
| a2.12 | 02 | close no package | GB202-870-A1 | confirmed (texto da GN: "GB 202-870-A1"); na foto a marcação é legível só em parte | GN, foto gn-42 | 2 |
| a3.1 | 03 | verso do PCB: 16 chips em U em volta do chip (5, 5, 4 e 2) | 16 chips GDDR7 no verso | confirmed (16 no verso, texto da GN); derived (disposição 5, 5, 4 e 2, de foto oblíqua) | GN, foto gn-29 | 1 |
| a3.2 | 03 | contador sobre as 32 posições | 32 posições; se todas ocupadas, 32 × 3 GB = 96 GB | confirmed (32 posições, 96 GB), derived (32 chips de 3 GB, dedução da GN) | GN; datasheet | 1 |
| a3.3 | 03 | linhas ciano dos chips até os 16 controladores | 16 controladores × 32 bits = 512 bits; em média dois chips por controlador, e como eles dividem o controlador é proposta | confirmed (512, 16), derived (razão 2:1, se as 32 posições estiverem ocupadas), **inferred** (arranjo em pares, selo "provável") | whitepaper, p. 8 (só 16 × 32); GN (32 posições) | 1 |
| a3.4 | 03 | sinal de três níveis | 28 Gbps × 512 ÷ 8 = 1.792 GB/s; PAM3 | confirmed | whitepaper, Tab. 4 e p. 12 | 2 |
| a3.5 | 03 | um bit trocado sendo corrigido | ECC de correção simples, sempre ligado | confirmed | whitepaper, p. 13 | 2 |
| a3.6 | 03 | barra do PCIe ao lado da barra da memória | por que os dados moram na placa: a memória local é cerca de 28 vezes mais larga que o PCIe 5.0 x16 (1.792 contra no máximo 63 GB/s por direção) | confirmed (32 GT/s por pista, PCI-SIG); derived (63 GB/s é conta, e a codificação 128b/130b só tem fonte secundária) | `standards-sources.md`, não auditado | 2 |
| a3.7 | 03 | saídas de vídeo | DisplayPort 2.1b, até 80 Gbps | confirmed | whitepaper, p. 30 | 3 |

### Transição T1 e ato 4: o chip (seções 04 e 05)

| Beat | Seção | O que se vê | Texto na tela (ideia) | Procedência | Fonte | Prio |
|---|---|---|---|---|---|---|
| t1.1 | 04 | zoom contínuo do package até a superfície do die; o die vira diagrama | "A partir daqui é diagrama: as contagens são oficiais, as posições são ilustrativas" | illustrative | regra do harness | 1 |
| a4.1 | 04 | die com régua e contador | 750 mm², 92,2 bilhões de transistores, TSMC 4N | confirmed | whitepaper, Tab. 4 | 1 |
| a4.2 | 04 | 12 GPCs acendem; um GPC abre em TPCs; um TPC abre em 2 SMs | 12 GPCs, 94 TPCs, 188 SMs; conta animada 94 × 2 = 188 e 188 × 128 = 24.064 | confirmed (contagem) | whitepaper, Tab. 4 e p. 9 | 1 |
| a4.3 | 04 | nota lateral sobre o chip completo | o GB202 completo tem 96 TPCs e 192 SMs; nesta placa a tabela dá 94 e 188; o próprio documento se contradiz na p. 8 | confirmed (com conflito declarado) | whitepaper, p. 8 contra Tab. 4 | 1 |
| a4.4 | 04 | L2 no centro, 16 controladores na borda, linhas ciano até os chips de memória | L2 de 128 MB; 16 controladores × 32 bits = 512 bits | confirmed (tamanhos), illustrative (posição) | whitepaper, p. 8 e 9 | 1 |
| a4.5 | 04 | blocos fora dos GPCs: AMP, vídeo, PCIe | o AMP é um processador RISC-V que escalona contextos | confirmed (existência), illustrative (posição) | whitepaper, p. 25 | 1 |
| a5.1 | 05 | grade de threads vira blocos, blocos viram warps de 32 | grid, bloco, warp; `WARP_SZ` = 32 | confirmed | PTX ISA, 4.5.1 | 1 |
| a5.2 | 05 | um warp recebe uma instrução, 32 threads executam juntas | SIMT: uma instrução, 32 threads, cada uma com seu contador de instrução e seus registradores; até 48 warps por SM | confirmed | Blackwell Tuning Guide 13.5, 1.4.1.1; guia CUDA 13.5, 3.2.2.1 | 1 |
| a5.3 | 05 | o SM e a miniatura do warp dentro do escalonador | o SM recebe blocos de threads e os divide em warps; quem escolhe o SM de cada bloco, o trecho lido não diz | confirmed; lacuna declarada | guia CUDA 13.5, 3.2.2.2 | 1 |

### Transição T2 e ato 5: dentro do SM (seções 06 a 09 e 12)

| Beat | Seção | O que se vê | Texto na tela (ideia) | Procedência | Fonte | Prio |
|---|---|---|---|---|---|---|
| t2.1 | 06 | zoom de um SM entre os 188 | "Um dos 188" | illustrative | regra do harness | 1 |
| a5.4 | 06 | o SM redesenhado a partir da Fig. 5 do whitepaper: quatro blocos e as unidades comuns | 128 núcleos CUDA, 4 Tensor Cores, 1 RT Core, 4 unidades de textura, 2 núcleos FP64 | confirmed | whitepaper, p. 8 e 9 e Fig. 5, p. 10 | 1 |
| a5.5 | 06 | cada partição acende: escalonador de warp, banco de registradores, núcleos, Tensor Core | 4 partições, cada uma com escalonador de warp e despacho de 32 threads por ciclo; 4 ciclos em INT32 e FP32 (FP64 leva cerca de 64) | confirmed (4 blocos, escalonador, 32 threads por ciclo); derived (latências, GB203) | whitepaper, Fig. 5, p. 10; Jarmusch et al., Tab. III | 1 |
| a5.6 | 07 | quatro bancos de registradores, um por bloco | 4 × 16.384 = 65.536 registradores de 32 bits, 256 KB por SM | confirmed | whitepaper, p. 9 e Fig. 5; Tuning Guide 13.5 | 1 |
| a5.7 | 07 | listagem SASS real com `R`, `UR`, `P` e `SR` coloridos | famílias de registradores; SAXPY usa 10 por thread, 0 de spill | confirmed (medido e reproduzido) | `harness/examples/saxpy-cu/` | 1 |
| a5.8 | 07 | uma thread pedindo registradores até o teto | até 255 registradores por thread; 64K por SM | confirmed | Blackwell Tuning Guide 13.5, 1.4.1.1 | 1 |
| a5.9 | 08 | código CUDA, PTX e SASS lado a lado, linhas ligando instruções (a mesma listagem da Figura 4 do artigo) | 20 instruções PTX viram 19 úteis em SASS | confirmed (medido e reproduzido) | `harness/examples/saxpy-cu/` | 1 |
| a5.10 | 08 | uma instrução vira uma palavra de 128 bits; campos aparecem | 16 bytes fixos; opcode, operandos, predicado e controle | confirmed (largura), derived da Volta (campos) | Binary Utilities, ap. 7.1; Jia et al., cap. 2 | 1 |
| a5.11 | 08 | `HMMA.16816.F32` dispara uma grade de multiplicações | uma instrução, 2.048 multiplicações-acumulações | confirmed (a instrução gerada), derived (2.048 é conta nossa) | `harness/examples/mma/` | 1 |
| a5.12 | 08 | tabela de critérios preenchendo linha a linha; ao lado, `LDGSTS`, `TEX` e `HMMA` com a descrição oficial; selo "análise do grupo" na tela | RISC no formato, com instruções próprias de acelerador | inferred (análise do grupo sobre fatos `confirmed`) | seção 08, aprovada em 2026-11-10; Binary Utilities 13.5 | 1 |
| a5.13 | 09 | escada de memória com tamanho e latência por degrau | registradores, L1 de 128 KB, L2 de 128 MB, GDDR7 de 96 GB | confirmed (tamanhos), derived (latências da GB203) | whitepaper, Tab. 4; Jarmusch et al., VI | 1 |
| a5.14 | 09 | o degrau do L1 dividido entre cache e memória compartilhada | a divisão (carveout) é escolhida em tempo de execução; os tamanhos nesta placa não foram levantados | confirmed; lacuna declarada | Blackwell Tuning Guide 13.5, 1.4.2.3 | 3 |
| a5.15 | 12 | SM enchendo de warps até o teto de 48 | 48 warps × 32 threads = 1.536 threads por SM; 288.768 na placa | confirmed (48), derived (contas) | Blackwell Tuning Guide 13.5, 1.4.1.1 | 1 |
| a5.16 | 12 | um warp de 32 threads; 4 ficam laranja e seguem outro caminho; a imagem vira o logotipo do grupo | divergência: o warp executa cada caminho, com as threads do outro caminho desabilitadas | confirmed. Ressalva do guia: o hardware pode diferir | guia CUDA 13.5, 3.2.2.1 | 1 |

### Ato 6: a GPU no sistema (seções 10 e 11)

| Beat | Seção | O que se vê | Texto na tela (ideia) | Procedência | Fonte | Prio |
|---|---|---|---|---|---|---|
| a6.1 | 10 | um endereço de 57 bits fatiado em seis índices mais o deslocamento, descendo PDE4, PDE3, PDE2, PDE1, PDE0 e PTE até a GDDR7; páginas de 2 MB e 512 MB param antes | 57 bits, 6 níveis, páginas de 4 KB a 512 MB | confirmed, com o escopo "segundo o driver oficial" | driver aberto: `ctrl2080mc.h`, `uvm_hal.c`, `uvm_hopper_mmu.c`, `uvm_ampere_mmu.c` | 1 |
| a6.2 | 10 | a tradução falha; a falha vai para um buffer e o canal fica parado; a CPU resolve um lote e a GPU repete o acesso. Ao lado, a Pascal (49 bits, 5 níveis) para comparar | falha de página: grava, para o canal, interrompe a CPU, resolve em lote, repete | confirmed (driver); derived (Pascal); TLB é lacuna declarada | driver aberto; documento da Pascal; Xid 31 | 1 |
| a6.3 | 11 | faixas CPU e GPU, pushbuffer, anel da GPFIFO com GET e PUT | o driver grava comandos, aponta uma entrada da GPFIFO e avança o PUT; vale para os canais do próprio driver | confirmed (canais do driver); inferred (programa CUDA comum) | driver aberto, `uvm_channel.c` e `uvm_pushbuffer.h` | 1 |
| a6.4 | 11 | sinal de interrupção da GPU para a CPU; metade de cima, metade de baixo; ao lado, `trap` e os códigos Xid 13 e 31 | três mecanismos documentados: a GPU interrompe a CPU, o programa aborta com `trap`, ou é preemptado. Não achamos rotina de interrupção executada pelo próprio SM | confirmed (os três mecanismos: driver, PTX, Xid); derived (preempção, Pascal); **inferred** (a leitura de que o SM não trata interrupções, selo "provável") | driver aberto, `nv.c` e `nv-msi.c`; PTX ISA 9.5, 9.7.21.4; catálogo de Xid | 1 |
| a6.5 | 11 | AMP na frente do pipeline; chip dividido em 4 | AMP RISC-V escalona contextos; MIG com até 4 instâncias | confirmed | whitepaper, p. 25 e 44 | 1 |

O ato 6 concentra os dois itens de **risco alto** do enunciado (MMU e interrupções). Em 2026-11-09 as fontes foram levantadas (`harness/spec/sources/mmu-interrupts-sources.md`) e os pontos centrais conferidos por leitura direta do código do driver. A auditoria (`harness/qa/fact-check-segunda-leva.md`) não aprovou na primeira passada; as correções estão aplicadas e falta a segunda. O beat a6.3 continua bloqueado e saiu do corte do seminário. Se a fonte não aparecer, cada beat bloqueado vira um beat de **lacuna declarada**: mostra o que se sabe, o que não é público e por quê. Isso atende o enunciado, mas precisa ser decidido, não acontecer por falta de tempo.

### Ato 7: fechamento (seções 13 e 14)

| Beat | Seção | O que se vê | Texto na tela (ideia) | Procedência | Fonte | Prio |
|---|---|---|---|---|---|---|
| a7.1 | 13 | barras RTX 6000 Ada contra RTX PRO 6000 Blackwell Workstation Edition | 142 para 188 SMs; L2 de 98.304 para 131.072 KB; 48 para 96 GB; TGP de 300 para 600 W | confirmed (valores); derived (razões) | whitepaper, Tab. 4 | 1 |
| a7.2 | 13 | nota sobre a banda da Ada | 1.008 GB/s na Tab. 1 e 960 GB/s na Tab. 4: a razão cita a tabela usada | confirmed (com conflito declarado) | whitepaper, Tab. 1 e 4 | 3 |
| ~~a7.3~~ | 14 | **retirado em 2026-11-10**: tabela-síntese GPU contra CPU | o enunciado não pede comparação com CPU, e a tabela exigiria fonte e auditoria para o lado da CPU. A síntese item a item do enunciado já está no a7.4 | não se aplica | não se aplica | fora |
| a7.4 | 14 | lista de lacunas declaradas | o que não é público e por quê | não se aplica | todas as seções | 1 |
| a7.5 | 14 | placa remonta em ordem inversa; legenda dos quatro selos | "o que é fato, o que é derivado, o que é proposta" | não se aplica | | 1 |
| a7.6 | 14 | créditos e lista de fontes rolando | fontes com data de acesso | não se aplica | `spec/sources/` | 2 |

## 5. Linguagem visual

1. **Cenário.** Estúdio escuro, fundo em gradiente quase preto, chão que só recebe sombra. A placa é o único objeto com cor.
2. **Luz.** Três pontos (principal, preenchimento, contraluz) mais mapa de ambiente para os metais. A mesma luz do início ao fim, para a remontagem do ato 7 casar com a abertura.
3. **Câmera.** Lente longa (fov de 25 a 35 graus) nas peças, para não distorcer proporção. Movimento sempre com aceleração e freio. Uma ideia por movimento.
4. **Explosão.** Na ordem real do teardown, um estágio por vez. Parafusos saem antes da peça que prendem.
5. **Linha de chamada.** Ponto na âncora, linha com um cotovelo, caixa. A linha se desenha em 0,8 s e acompanha a peça.
6. **Caixa de texto.** `headline` (até 8 palavras), `caption` (até 35 palavras), selo de procedência, linha de fonte. Nunca cobre a peça em foco.
7. **Selo de procedência.** Quatro estados com cor, ícone e palavra: confirmado, derivado, provável, ilustrativo. Nos níveis 2 a 4 aparece também uma faixa fixa "diagrama ilustrativo".
8. **Cabeçalho.** Trilha de nível (Placa, Chip, SM, Conceito), número e nome da seção do texto escrito, barra de progresso.
9. **Tipografia.** Uma família sem serifa para texto e uma monoespaçada para código, as duas de licença aberta e embarcadas no viewer (sem CDN). Corpo mínimo de 28 px em 1080p, para leitura em projetor.
10. **Marcas.** Sem logos da NVIDIA na geometria nem nas texturas, até decisão humana em contrário (ver ARCHITECTURE, seção 10).

## 6. Texto e fala

Cada beat tem quatro campos de texto, todos auditados pelo `fact-checker`:

| Campo | Onde aparece | Limite |
|---|---|---|
| `headline` | vídeo e viewer | 8 palavras |
| `caption` | vídeo e viewer | 35 palavras |
| `body` | só no viewer, painel expansível | sem limite (as 5 seções fixas de `content/pt-BR/<part>.md`) |
| `fala` | notas do apresentador e legendas `.vtt` | o que cabe no `hold` do beat |

Regra de tempo de leitura: `hold` ≥ 0,4 s por palavra do `caption` + 2 s. O teste automatizado falha se um beat violar a regra. É uma regra do projeto, a calibrar no primeiro ensaio com cronômetro.

Quem fala o quê: a coluna `speaker` do storyboard recebe o nome do integrante. A divisão segue a **definição de tarefas da proposta entregue em 26/10** (`vault/01-Briefing/Proposta formal.md`), em que cada integrante "responde por uma parte". Em ordem de apresentação:

| Ordem | Quem | Parte na proposta | Beats do corte | Tempo |
|---|---|---|---|---|
| 1 | Vitor | tour 3D, integração e condução | atos 0, 1 e 2: abertura, a placa por fora, desmontagem e os três caminhos | 4:00 |
| 2 | Arthur | hierarquia de memória, caches e gerenciamento | ato 3: memória e barramentos | 1:10 |
| 3 | João | pipeline, SIMT, latência e ocupação | T1 e ato 4 (planta do chip, SIMT); T2, a5.4 e a5.5 (o SM e as partições); a5.3 e a5.15 (do bloco ao warp, ocupação); a5.16 (divergência, com o logotipo) | 5:42 |
| 4 | Lorenzo | registradores, instruções, RISC ou CISC | a5.6 a a5.12 | 3:29 |
| 5 | Arthur | (continuação) | a5.13: escada de memória e latências | 0:30 |
| 6 | Thiago | MMU, interrupções e escalonamento | ato 6, com o envio de comandos (a6.3) | 3:33 |
| 7 | Vitor | condução | ato 7: Ada contra Blackwell, lacunas, remontagem | 1:39 |

Totais: João 5:42, Vitor 5:39, Thiago 3:33, Lorenzo 3:29, Arthur 1:40. Soma: 20:03 (a diferença de um segundo para a tabela da seção 2.1 é arredondamento).

A divisão fica como está: em 2026-11-10 o autor disse que os três ajustes que estavam em aberto (dono da planta do chip, posição do beat de divergência e o tempo menor do Arthur) não precisam de decisão. A planta do chip segue com o João, e a divergência (a5.16) segue logo depois do SM.

Cada apresentador revisa as notas de fala e as fontes do seu bloco antes do ensaio de 15/11, porque é quem responde às perguntas daquela parte. O projeto não registra autoria de trabalho que a pessoa não fez.

## 7. Especificação técnica do vídeo

| Item | Valor | Motivo |
|---|---|---|
| Proporção e resolução | 16:9, 1920 × 1080 | resolução nativa de projetor de sala |
| Taxa de quadros | 30 fps no corte do seminário | a captura custa cerca de 1 s por quadro (seção 7.1); 60 fps dobra o tempo. Reavaliar depois do piloto |
| Mestre | sequência PNG por beat | permite refazer um beat sem refazer o vídeo |
| Distribuição | MP4 H.264, `yuv420p`, `+faststart`; cópia WebM | toca em qualquer computador de sala |
| Legendas | `.vtt` geradas do campo `fala` | acessibilidade e ensaio |
| Áudio | nenhum no corte do seminário (fala ao vivo) | trilha e narração gravada são decisão humana; só material de licença livre |

### 7.1 Captura determinística

O risco declarado na ARCHITECTURE (render lento sem GPU) vira requisito de projeto:

1. O viewer tem **uma** linha do tempo mestre (GSAP), pausada, e expõe `window.__tour.seek(t)` e `window.__tour.ready`. Nenhuma animação depende do relógio real.
2. Modo `?capture=1&cut=seminario&beat=<id>`: esconde os controles, fixa o tamanho da janela e a densidade de pixels em 1.
3. Um script de captura (Playwright) faz, para cada quadro: `seek(i / fps)`, espera o quadro renderizar, salva o PNG.
4. Cada beat é um segmento. O segmento tem uma chave (hash do beat, do GLB, dos materiais e do texto). Se a chave não mudou, o segmento não é refeito.
5. O `ffmpeg` monta cada segmento e concatena o corte.
6. **Custo medido (2026-11-09, neste ambiente, cena sintética).** Three.js 0.170 em Chromium headless com SwiftShader, 600 mil triângulos, materiais PBR, mapa de ambiente e sombra, 1920 × 1080: cerca de 10 ms para desenhar o quadro e cerca de **1,0 s para salvar o PNG** com `page.screenshot`. Em 1280 × 720 o total cai só para 0,9 s. O gargalo é a captura, não o render. Consequências:
   - 10 minutos a 30 fps são 18.000 quadros, cerca de 5 horas em série. A 60 fps, o dobro.
   - Renderizar beats em paralelo (vários processos) e o cache por beat deixam de ser luxo.
   - Vale medir no piloto uma captura que leia o canvas direto, sem `page.screenshot`.
   - A medição precisa ser refeita com o GLB real e com os diagramas.
7. **Custo medido com o viewer real (2026-11-10).** Nos beats de diagrama, a captura levou em média **188 ms por quadro** em 1920 × 1080 (1.884 quadros, cinco beats do corte do seminário). O corte dos atos de chip, com 9:52, daria cerca de 17.800 quadros a 30 fps: perto de 56 minutos em série. O 3D em blockout mediu 249 ms por quadro; com o modelo real esse número sobe. O teste de determinismo ainda falha em dois pontos e precisa fechar antes da captura final.

### 7.2 Diagramas dos níveis 2 a 4

Os atos 4 a 6 valem a nota. Definido em 2026-11-10 (contrato completo em `harness/diagrams/README.md`):

- Contrato `diagrams/<id>.json`: cena declarativa (nós, grupos, contagens, fluxos, rótulos), gerada **a partir do spec**, nunca desenhada à mão. A planta do chip nasce dos números 12, 94 e 188; se o spec mudar, o diagrama muda.
- O viewer desenha os diagramas em uma **camada SVG**, por cima do canvas 3D, com um espaço de coordenadas único. O diagrama do SM mora dentro de uma célula de SM da planta do chip (`embed`), então o zoom é contínuo do chip até o detalhe. Motivos: texto nítido em qualquer zoom, captura determinística e muito menos código do que texto em 3D.
- A passagem da placa 3D para o diagrama (beat t1.1) é uma fusão: a câmera 3D aproxima do chip enquanto a camada SVG aparece.
- Um beat de nível 2 a 4 tem `view` (diagrama e nós a enquadrar), `highlight` e `flows`, em vez de `camera`. O campo `world` do storyboard posiciona os diagramas que não estão dentro de outro.
- Agente `diagram-designer` (tipo B, opus) e skill `chip-diagram-kit`. Ver `harness/ARCHITECTURE.md`, seção 6.
- Todo diagrama carrega `provenance` por elemento: contagem `confirmed`, posição `illustrative`.

## 8. QA do vídeo

| Checagem | Quem | Falha se |
|---|---|---|
| Âncora visível | `ops-runner` (Playwright) | a âncora sai da tela ou fica atrás de outra peça em qualquer quadro do `hold` |
| Caixa não cobre a peça | `ops-runner` | a caixa cruza o retângulo projetado da peça em foco |
| Texto cabe | `ops-runner` | o `caption` estoura a caixa ou passa de 35 palavras |
| Tempo de leitura | `ops-runner` | `hold` menor que a regra da seção 6 |
| Câmera não atravessa peça | `ops-runner` | o caminho da câmera cruza geometria |
| Contraste e corpo mínimo | `ops-runner` | contraste abaixo de 4,5:1 ou corpo menor que 28 px |
| Fidelidade à placa real | `visual-qa` | quadro de vista padrão diverge da foto de referência (ver `assembly-plan.md`, seção 6) |
| Fatos e selos | `fact-checker` | número sem fonte, selo errado, `inferred` escrito como fato |
| Cobertura do enunciado | `fact-checker` | item exigido sem beat de prioridade 1 |
| Ensaio com cronômetro | humano | o corte do seminário passa do tempo do professor |

## 9. Plano de reserva para o seminário

1. Viewer rodando de arquivo local, sem internet (bibliotecas embarcadas).
2. MP4 do corte do seminário no mesmo computador e em um pendrive.
3. PDF com um quadro por beat de prioridade 1 (gerado pela mesma captura), para o caso de não haver como tocar vídeo.
4. Teste na sala ou em projetor equivalente antes do dia.

## 10. Pendências deste plano

- Confirmar se os 22 minutos incluem perguntas.
- Viewer ao vivo ou vídeo corrido (grupo).
- Narração gravada e trilha: sim ou não (grupo).
- Uso de logos da NVIDIA (grupo).
- Nenhum beat está bloqueado por falta de fonte desde 2026-11-10. Faltam imagem e texto para os atos 0 a 3 e para a7.5 e a7.6. O a7.3 foi retirado.
- Segunda passada do `fact-checker` sobre a seção 4 (a primeira não aprovou; correções em `harness/qa/fact-check-fisico.md`).
- Registrar no excerto local do whitepaper a coluna da RTX 6000 Ada (beat a7.1).
