# Falas refeitas do seminário

Escritas em 2026-11-16, só para o que é obrigatório: os oito itens do enunciado, o mínimo de base para entendê-los e a declaração do que não achamos. Seguem a ordem dos 18 slides do corte curto.

## Como usar

- Cada bloco diz **quem fala**, **em qual slide** e quanto tempo leva. A **fala** é para ser dita em voz alta, em frases curtas. Não é para ser lida palavra por palavra: leia o tópico que está na tela e depois explique com a fala.
- As palavras em **negrito** são onde a voz deve parar ou subir. São os termos e os números.
- Todo bloco segue o mesmo caminho: **o que é**, **como é nesta GPU**, **o que não achamos**. Quem ouve aprende o ritmo.
- Os fatos são os já auditados do projeto. Onde a frase é conclusão ou leitura do grupo, ela diz isso.

---

## Bloco 1. Abertura (Vitor, slide 1)

**Fala**

Olá, nós somos o grupo Warp 32. Vamos apresentar a arquitetura de uma GPU real: a NVIDIA RTX PRO 6000 Blackwell.

O enunciado pede que a gente explique oito itens de uma arquitetura: os **registradores**, o **conjunto de instruções**, se ela é **CISC ou RISC**, o **pipeline**, o **cache**, o **gerenciamento de memória**, a **MMU** e as **interrupções**.

Vamos explicar cada um com os números desta GPU. Começamos pelo básico e sempre dizemos o que cada palavra significa antes de usá-la.

E uma combinação: quando uma informação **não está nas fontes que lemos**, nós vamos dizer isso claramente. É o que o enunciado pede.

---

## Bloco 2. O básico: CPU, GPU, placa e chip (Vitor, slides 2 a 5)

**Fala**

Primeiro, o básico. Todo computador tem um **processador**: o circuito que executa as instruções de um programa. O processador principal é a **CPU**. Ela segue poucas tarefas de cada vez e é boa em decidir caminhos depressa.

A **GPU** nasceu para outra coisa: desenhar imagens. A tela é feita de pontinhos, os **pixels**, e cada pixel pede quase a mesma conta, só com números diferentes. Por isso a GPU faz **a mesma conta sobre muitos dados ao mesmo tempo**. Esta tem **24.064 núcleos CUDA**, que são pequenas unidades de conta. CUDA é o nome que a NVIDIA dá à programação das suas GPUs.

A GPU vem numa **placa de vídeo**, que se encaixa na **placa-mãe**, a placa principal do computador. Esta placa leva a sua própria memória, de **96 gigabytes**, uma entrada de energia e saídas de imagem. É a edição Workstation, para computadores profissionais, e usa até **600 watts**.

Se abrimos a placa, no centro fica a placa de circuito e, nela, o **chip GB202**. Esse chip é a GPU. Tem **92,2 bilhões de transistores**, que são chaves elétricas minúsculas, em **750 milímetros quadrados** de silício. É dentro dele que vamos olhar a partir de agora.

---

## Bloco 3. Memória própria da placa (Arthur, slide 6)

**Fala**

Todo processador precisa de uma **memória de trabalho**, a RAM, onde ficam os dados enquanto ele calcula. A GPU tem a sua, **separada da memória do computador**: **96 gigabytes de GDDR7**, um tipo de memória feito para placas de vídeo.

No verso da placa há **16 chips** de memória, e o teardown, que é a desmontagem da placa feita pela Gamers Nexus, fala em **32 posições** no total. Os chips se ligam ao GB202 por um **barramento de 512 bits**: são 512 linhas de dados em paralelo, formadas por **16 controladores** de 32 bits. A memória tem **ECC**, um código que corrige um bit trocado por erro, e ele fica sempre ligado.

Por que a memória fica na placa? Por velocidade. A memória da placa entrega **1.792 gigabytes por segundo**. A ligação com o resto do computador, o PCIe, leva cerca de **63 por sentido**. A memória da placa é cerca de **28 vezes mais rápida**. Na nossa leitura, por isso compensa copiar os dados para a placa uma vez e fazer as contas lá dentro.

---

## Bloco 4. Dentro do chip: SM, warp e pipeline (João, slide 7)

Este bloco tem mais conteúdo que o slide. Se sobrar tempo, os slides de apoio estão no índice (tecla M): chip em GPCs e SMs, dentro de um SM, warp e SIMT.

**Fala, parte 1: a estrutura**

O chip é feito de **caixas dentro de caixas**. A maior é o **GPC**, e são 12. Cada GPC agrupa TPCs, e cada TPC tem 2 SMs. São 94 TPCs, então **188 SMs**. O texto do whitepaper fala em 192 para o chip completo, mas a tabela desta placa dá 188 e fecha com os 24.064 núcleos. Nós adotamos 188.

O **SM** é a peça que importa: recebe as tarefas, busca as instruções e as executa. Lembra um núcleo de CPU: tem **escalonador**, que escolhe o que executar, **registradores**, que guardam os números em uso, e **cache L1**, uma memória rápida. Cada SM tem **128 núcleos CUDA**, em **4 partições**.

**Fala, parte 2: como o trabalho chega**

Quem programa a GPU escreve o código para uma só **thread**, uma execução do programa com os seus dados, e manda rodar milhares de vezes. O SM junta as threads em grupos de **32, os warps**. As 32 threads de um warp executam a **mesma instrução**, cada uma com os seus dados: a NVIDIA chama isso de **SIMT**. Cada thread tem o seu contador de programa e os seus registradores. Se elas seguem caminhos diferentes num if, o warp percorre um caminho, depois o outro, e desliga as threads que não estão nele. Cada SM mantém até **48 warps**.

**Fala, parte 3: o pipeline (item do enunciado)**

Agora o **pipeline**: executar a instrução em etapas, como numa linha de montagem. Num processador de livro-texto: buscar, **decodificar**, que é ler o que ela pede, executar e guardar o resultado. Várias instruções ficam em andamento ao mesmo tempo.

Nesta GPU, cada partição do SM tem o seu **escalonador de warp**. A cada **ciclo**, uma batida do relógio, ele escolhe um warp pronto e despacha a instrução às threads ativas, até 32. O clock de boost é de 2.617 megahertz: cerca de **2,6 bilhões de ciclos por segundo**.

Trocar de warp **não tem custo**. Na nossa leitura, quando um warp espera um dado da memória, o escalonador executa outro. Uma conta de inteiro ou FP32 leva **4 ciclos**, mas esse valor foi medido numa RTX 5080, da mesma família, e não nesta placa.

O que **não achamos**: quantos estágios o pipeline da Blackwell tem.

---

## Bloco 5. Registradores (Lorenzo, slide 8)

**Fala**

**Registrador** é a memória interna do processador, a mais rápida. Ele guarda uma **palavra**, que aqui tem **32 bits**.

Na teoria de circuitos digitais, um registrador é um conjunto de **flip-flops**, que são memórias de 1 bit. Ele só guarda um valor novo quando o sinal **load** chega junto com o **clock**, a batida do relógio. E registrador tem **nome e não endereço**: no código desta GPU aparecem R0, R1, R2 e assim por diante.

Cada SM tem **65.536 registradores** de 32 bits. São **256 kilobytes**, em 4 bancos de 16.384, um por partição. Na placa toda, 188 vezes 256 KB dão **48.128 KB**.

Aqui há uma diferença importante para a CPU. Numa CPU, quando o sistema troca uma tarefa por outra, ele **copia os registradores para a memória**. Na GPU, cada warp mantém os seus registradores enquanto existir. Por isso trocar de warp **não custa nada**.

O que **não achamos**: como o banco de registradores é construído por dentro, com bancos e portas. Há medidas de outras gerações, mas não da Blackwell.

---

## Bloco 6. Conjunto de instruções (Lorenzo, slide 9)

**Fala**

**Conjunto de instruções** é a lista de ordens que o processador entende, com o formato delas. Na NVIDIA ele tem **duas camadas**.

A primeira é o **PTX**. É uma máquina virtual: um processador descrito em documento, com instruções estáveis entre gerações de GPU. O programa, escrito em CUDA C, vira PTX. A segunda é o **SASS**, que é o código de máquina de cada geração. O PTX é traduzido para SASS pelo **ptxas**, ou pelo **driver**, o programa que controla a placa. Nesta placa o alvo é o **sm_120**.

Por que duas camadas? Porque o SASS pode mudar de uma geração para outra. Só com o PTX o programa fica compatível com GPUs futuras.

Nós compilamos um exemplo de verdade: o **SAXPY**, que calcula y igual a a vezes x mais y, para cada posição de duas listas de números. Em PTX são **20 instruções**. Em SASS são **19 úteis**.

E cada instrução SASS tem **16 bytes**, ou **128 bits**, sempre. Com tamanho fixo, o circuito sabe onde cada instrução começa sem precisar decodificar a anterior. Na Blackwell, só achamos documentada a largura. Os campos dentro dos 128 bits **não achamos**.

---

## Bloco 7. Registradores no código (Lorenzo, slide 10)

**Fala**

Voltando aos registradores, agora no código de verdade. No SASS aparecem **quatro tipos**: **R**, de uso geral, **UR**, uniformes, **P**, os predicados, que têm 1 bit e guardam verdadeiro ou falso, e **SR**, os especiais, como o que guarda o índice da thread.

Quem decide quantos registradores cada thread usa é o **compilador**, o programa que traduz o código para a máquina. O máximo é **255 por thread**. Só que os 65.536 registradores do SM são **repartidos entre todos os warps**. Com 255 por thread, o SM comporta só **8 warps**, numa conta simples nossa, e o máximo é 48. O nosso SAXPY usa só **10 registradores** por thread. Com ele, cabem os **48 warps**.

Isso importa porque, quanto mais warps no SM, mais opções o escalonador tem para trocar quando um espera. Por isso, na nossa leitura, o compilador tenta gastar poucos registradores.

---

## Bloco 8. CISC ou RISC (Lorenzo, slide 11)

**Fala**

São duas filosofias de conjunto de instruções. No **CISC**, as instruções são complexas e de tamanho variável, e uma só pode ler a memória, calcular e gravar. No **RISC**, as instruções são simples, de tamanho fixo, só as de **carga e armazenamento** tocam a memória, e há muitos registradores.

Uma coisa antes de tudo: a NVIDIA **não classifica** o SASS como CISC nem como RISC. Então a conclusão é **do grupo**, a partir dos critérios clássicos.

A favor de RISC temos três coisas. Primeiro, as instruções têm **16 bytes fixos**. Segundo, a memória é tocada por instruções de carga e armazenamento, com poucas exceções, como a LDGSTS, que copia da memória global para a compartilhada. No nosso SAXPY, a LDG lê, a STG grava, e a conta, a FFMA, usa só registradores. Terceiro, há muitos registradores: até **255 por thread**.

Contra, há instruções que fazem muito trabalho de uma vez. A **HMMA** multiplica um bloco de matriz numa só instrução: 16 por 8 por 16, que dão **2.048 multiplicações** com soma. É uma instrução de **acelerador**, ou seja, de um processador feito para um tipo de trabalho.

A nossa conclusão: **RISC no formato e na regra de acesso à memória, com instruções de acelerador**. Sobre microcódigo, não há nenhuma informação pública.

---

## Bloco 9. Cache (Arthur, slide 12)

**Fala**

Já vimos a memória da placa, de 96 gigabytes. Ela é grande, mas é o degrau mais lento. Por isso existe uma **escada de memória**. Do mais rápido ao mais lento: os registradores, o cache L1 e a memória compartilhada, o cache L2 e a GDDR7.

**Cache** é uma memória pequena, perto de quem calcula, que guarda uma cópia dos dados usados há pouco, porque os programas costumam voltar aos mesmos dados. Cada SM tem **128 KB de L1**, e o chip inteiro divide **128 MB de L2**.

A **latência**, que é o tempo até o dado chegar, cresce a cada degrau. Pesquisadores mediram numa RTX 5080, da mesma família: **30 a 40 ciclos** no L1, cerca de **358** no L2 e cerca de **877** na memória global. Lembrando: não é medida desta placa.

Um detalhe: os 128 KB do SM são divididos entre o cache L1 e a **memória compartilhada**. O cache é automático, mas a memória compartilhada é o próprio programa que escolhe o que guardar. A divisão é decidida com o programa já rodando. Segundo o guia CUDA, a compartilhada pode ter 0, 8, 16, 32, 64 ou 100 KB.

O que **não achamos**: a política do cache, ou seja, que dado sai quando ele enche, e a associatividade.

---

## Bloco 10. MMU (Thiago, slides 13 e 14)

**Fala**

Agora, como a GPU acha um dado. Cada dado na memória tem um **endereço**, o número da sua posição. O programa usa um **endereço virtual**, e a **MMU**, a unidade de gerenciamento de memória, traduz para o **endereço físico**, a posição real. Numa CPU, isso separa um programa do outro e deixa o sistema guardar os dados onde houver espaço.

A tradução usa **tabelas de páginas**: a memória é dividida em **páginas**, blocos de tamanho padronizado, e a tabela diz onde cada uma está. A tabela é em **níveis**, como um endereço postal: estado, cidade, rua e número.

Nesta GPU, segundo o **código aberto do driver**, o endereço virtual tem **57 bits** e a tabela tem **6 níveis**. As páginas têm 4 KB, 64 KB, 2 MB ou 512 MB, e os 96 GB cabem em 192 páginas de 512 MB. Uma correção: o nosso **artigo escrito** cita 49 bits e 5 níveis, que era o formato da **Pascal**, de 2016. O driver atual usa o da **Hopper**.

O que **não achamos**: o tamanho e a política da **TLB**, o cache das traduções recentes, e se cada programa tem o seu espaço de endereços. O código do driver mostra o que o software programa, e não o circuito.

---

## Bloco 11. Falha de página (Thiago, slide 15)

**Fala**

E se a MMU não encontra a página na tabela? É uma **falha de página**. Na CPU, o sistema operacional resolve e a instrução se repete.

Nesta GPU, quem resolve também é software na CPU: o **driver**. A GPU anota a falha num **buffer**, uma área de memória, e avisa a CPU. O driver lê um **lote** de falhas, junta as repetidas, atende e manda a GPU **repetir os acessos**.

Segundo o whitepaper da geração Pascal, isso permite trazer para a GPU, sob demanda, uma página que ainda não está na memória dela. Falha de página, então, nem sempre é erro. Erro é o acesso a um endereço ilegal.

---

## Bloco 12. Interrupções (Thiago, slide 16)

**Fala**

Uma **interrupção** é um aviso que faz o processador parar o que está fazendo, rodar uma rotina de atendimento, o **tratador**, e voltar de onde parou. Achamos **três mecanismos** nesta GPU.

Primeiro: a **GPU avisa a CPU**. Isso é feito por mensagens de interrupção, chamadas MSI-X ou MSI, ou, se não der, pela linha legada. O tratador do driver tem duas metades: a de cima faz o mínimo na hora, e a de baixo faz o trabalho pesado depois, para não segurar a CPU.

Segundo: a instrução **trap**. Quando o programa a executa, ele aborta e gera uma interrupção para a CPU.

Terceiro: a **falha de página**, que acabamos de ver. Ela segura o **canal**, que é a fila de trabalho da GPU: o canal não pode ser trocado e os outros esperam até o driver atender.

O que **não achamos**: como funciona a preempção, que é trocar uma tarefa por outra no meio, nesta placa, e se existe tratador de interrupção dentro do SM. A nossa leitura é que os avisos vão ao driver, na CPU, e não são tratados dentro do SM.

---

## Bloco 13. Fechamento (Vitor, slides 17 e 18)

**Fala**

Para fechar. O que **achamos** foram tamanhos, limites e formatos: 65.536 registradores por SM, instruções de 16 bytes, endereços de 57 bits, 128 megabytes de L2.

O que quase nunca achamos foi o **funcionamento por dentro**: estágios do pipeline, tamanho da TLB, política dos caches, microcódigo. Vemos três razões: os documentos oficiais descrevem o que quem programa precisa saber, o código do driver mostra o que o software programa e não o circuito, e os pesquisadores mediram outras placas. É o que o enunciado pede.

Resumindo os oito itens. **Registradores**: 65.536 por SM, até 255 por thread. **Instruções**: PTX e SASS, de 16 bytes. **CISC ou RISC**: RISC com instruções de acelerador, conclusão do grupo. **Pipeline**: 4 escalonadores por SM, sem número de estágios. **Cache**: 128 KB de L1 e 128 MB de L2. **Gerenciamento de memória**: 96 GB de GDDR7. **MMU**: 57 bits e 6 níveis. **Interrupções**: da GPU para a CPU.

Obrigado. Abrimos para as perguntas.

---

# Como apresentar melhor do que o jeito que já fazemos

## O que atrapalha hoje

1. **Cada item parece um assunto solto.** Quem ouve recebe oito definições e não vê o que liga uma à outra.
2. **A tela e a fala repetem a mesma coisa.** Quem ouve lê a tela, e a fala vira só um eco.
3. **Os "não achamos" aparecem sem preparo** e soam como buraco. Eles são resposta certa, mas precisam de um lugar fixo.
4. **Falta ensaio de tempo e de passagem** entre uma pessoa e outra.

## 1. Um exemplo único do começo ao fim: o SAXPY

O SAXPY é a conta y = a·x + y que compilamos. Em vez de oito assuntos soltos, o grupo acompanha **uma conta** pelos oito itens. Cada pessoa fecha o seu bloco com uma frase que volta ao exemplo. São frases curtas, para dizer no fim do bloco:

- **Registradores:** "No nosso SAXPY, cada thread usa 10 registradores."
- **Instruções:** "No nosso SAXPY, 20 instruções PTX viraram 19 instruções SASS."
- **CISC ou RISC:** "No nosso SAXPY, a LDG lê da memória, a STG grava, e a conta FFMA usa só registradores."
- **Pipeline:** "Com 10 registradores por thread, o SAXPY deixa o SM manter os 48 warps, e o escalonador sempre tem outro warp pronto."
- **Cache e memória:** "As duas LDG do SAXPY vão buscar x e y na memória, e o caminho passa pela escada de cache." Esta é leitura nossa: o caminho exato dentro da GPU não achamos documentado.
- **MMU:** "Cada endereço que o SAXPY lê é um endereço virtual, que a MMU traduz." Também é leitura nossa.
- **Interrupções:** "Se o SAXPY acessasse um endereço ilegal, o erro apareceria como Xid 31 no registro do driver."

Isso faz quem ouve perceber que são **partes da mesma máquina**.

## 2. O mesmo caminho em todo bloco

Todo mundo usa a mesma ordem de quatro passos. Quem ouve aprende o ritmo na segunda vez e acompanha melhor:

1. **A pergunta, em uma frase:** "O que é pipeline?"
2. **A resposta simples**, sem número.
3. **O número desta GPU**, dizendo o que ele significa.
4. **O que não achamos**, dito em voz firme, no fim do bloco. Sempre no fim, sempre com a mesma frase: "Isso não achamos nas fontes que lemos."

## 3. A tela mostra o quê, a fala explica o porquê

- Leia o **título** e o **tópico em negrito**, e deixe o resto da tela como apoio.
- Depois explique com a fala, olhando para a plateia.
- Quando aparecer um número, **diga o que ele significa** e pare um segundo. Número sem significado ninguém guarda.
- A linha verde que aponta no slide é um dedo: acompanhe com a mão ou com o olhar.

## 4. Passagens entre as pessoas

Cada pessoa termina chamando a próxima, com uma frase que diz o que vem. Exemplos:

- Vitor para Arthur: "Já sabemos o que é o chip. Agora o Arthur explica de onde vêm os dados que ele usa."
- Arthur para João: "Os dados chegam ao chip. O João mostra o que o chip faz com eles."
- João para Lorenzo: "Cada thread precisa guardar números e ler ordens. O Lorenzo explica como."
- Lorenzo para Arthur: "Os números e as ordens estão prontos. O Arthur volta para mostrar a memória rápida por perto, o cache."
- Arthur para Thiago: "O dado está no cache ou na memória. O Thiago explica como a GPU acha o endereço dele."
- Thiago para Vitor: "Falamos do que achamos. O Vitor fecha com o que ficou de fora."

## 4.1 Mudança de ordem para o Lorenzo e o Arthur

Lorenzo fala nos slides 8 a 11 e Arthur volta no 12. Se preferirem não ter um intervalo de quatro slides entre as falas do Arthur, **o Arthur pode fazer o cache (slide 12) logo depois da memória (slide 6)** e Lorenzo vem depois. Para isso, é só trocar a ordem dos beats no `storyboard.json`. Digam se querem que eu faça.

## 5. Tempo

As falas deste arquivo somam cerca de **17 minutos e meio** em ritmo normal (140 palavras por minuto). Com as passagens entre as pessoas, perto de **19**. Se os 22 minutos incluem as perguntas, sobram uns 3 minutos para elas. Por isso:

- **Não acrescentem** conteúdo além do que está aqui.
- **Combinem marcos.** Quem fala no ritmo chega ao slide 9 (instruções) aos **7 minutos**, ao cache (slide 12) aos **11**, à MMU aos **13** e às interrupções aos **15**.
- **Se estiverem atrasados**, cortem nesta ordem: o parágrafo da memória compartilhada no bloco do cache, o bloco 7 inteiro (registradores no código, slide 10) e a parte 2 da fala do João, que pode virar só uma frase sobre threads e warps. Juntos, são cerca de 2 minutos.
- **Se o professor disser que os 22 minutos não incluem as perguntas**, sobra folga e dá para voltar pelo índice (tecla M) aos slides de GPC, SM, warp e SIMT.

## 6. Perguntas

- Cada pessoa **responde as perguntas do seu bloco**. A folha `perguntas-e-respostas.md` tem as respostas.
- O Vitor **organiza**: repete a pergunta e chama quem responde.
- Se ninguém souber, a frase é sempre a mesma: **"Isso não achamos nas fontes que lemos. O que achamos de mais próximo foi..."** E dizer o mais próximo.
- **Nunca inventem** um número ou um motivo. É melhor dizer que não achamos.

## 7. Ensaio

1. **Uma vez, em voz alta, em ordem, com cronômetro.** Quem erra palavra, simplifica.
2. Treinar **só as passagens** entre as pessoas: são onde o grupo trava.
3. **Cada um lê a sua folha de perguntas** em voz alta, e outro faz de professor.
4. Abrir o `tour.html` **uma vez antes**, na máquina em que vão apresentar, e passar os 18 slides.

## 8. Duas coisas que só o professor responde

- Os 22 minutos incluem as perguntas?
- O grupo pode ter 5 integrantes? (O resumo do enunciado diz "até 4", e a proposta entregue tem 5.)
