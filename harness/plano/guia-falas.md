# Guia das falas do seminário

Escrito em 2026-11-16, no dia do seminário, para reescrever as falas e os textos de tela. Substitui o estilo do roteiro conciso, que o autor julgou superficial e vago. Vale para `harness/content/pt-BR/beats.json` (campos `headline`, `caption`, `fala`) e para o roteiro de estudo do grupo.

## Para quem falamos

Uma pessoa de 10 anos, inteligente e curiosa, que nunca abriu um computador. Ela entende tudo se cada palavra nova for explicada antes de ser usada e se cada ideia vier com um exemplo concreto. Os próprios apresentadores também não são especialistas: a fala precisa ensinar a eles também.

## O que o professor cobra

O enunciado pede, para a arquitetura escolhida: conjunto de registradores, conjunto de instruções, se é CISC ou RISC, como funciona a MMU, mecanismo de interrupções, gerenciamento de memória, pipeline e cache. E avisa: "não basta apresentar as características". Então cada item precisa responder três perguntas:

1. **O que é isso, em qualquer processador?** (a ideia geral, com uma comparação do dia a dia)
2. **Como é nesta GPU?** (o mecanismo, com os números e a fonte)
3. **Por que é assim?** (o motivo de projeto: o que a GPU ganha com isso)

## Regras da fala

1. **Frases completas, faladas.** A `fala` é o que o apresentador diz em voz alta, em frases inteiras, não tópicos soltos. De 4 a 8 frases por momento. Uma ideia por frase.
2. **Explique antes de usar.** Toda palavra técnica (warp, SM, thread, cache, registrador, latência, barramento) é explicada na primeira vez que aparece, em uma frase simples. Depois pode ser usada sem explicar de novo.
3. **Concreto antes de abstrato.** Primeiro o exemplo ou a comparação, depois o termo técnico. Exemplo: "Imagine 32 alunos fazendo a mesma conta, cada um com os seus números. Na GPU, esse grupo de 32 se chama warp."
4. **Comparações com limite.** Toda comparação do dia a dia vem com o ponto em que ela deixa de valer, quando isso evita um erro de entendimento.
5. **Números com sentido.** Todo número vem com a unidade e com algo que o torne palpável ("96 GB, cerca de 12 vezes a memória de um notebook comum" só se a comparação tiver fonte ou for conta nossa declarada).
6. **Proibido:** frases de efeito, ditados, metáforas soltas sem explicação, frases que não dizem nada ("é aqui que a mágica acontece", "o coração da placa", "tudo se conecta", "por trás dos panos"), perguntas retóricas sem resposta, jargão sem explicação, listas de características sem o porquê.
7. **Ligue um momento ao seguinte.** A última frase de um momento prepara o próximo ("Mas de onde vêm os dados que essas threads usam? Da memória, que é o próximo assunto.").
8. **Honestidade sobre o que não sabemos.** Quando a NVIDIA não documenta algo, diga com clareza: "isso não achamos nas fontes que lemos" e, se houver, "o que achamos de mais próximo foi...". Hipótese nossa é dita como hipótese ("provavelmente", "nossa leitura é que"), nunca como fato.
9. **Tela e fala dividem o trabalho.** O `headline` diz o assunto em linguagem simples (até 8 palavras). A `caption` traz a frase-chave e o número principal (até 2 frases curtas). A `fala` explica. A tela não repete a fala inteira.
10. **Estilo do projeto:** PT-BR com acentos, sem travessões, sem ponto e vírgula. Sem "a NVIDIA não publica": use "não achamos nas fontes lidas".

## Exemplo antes e depois

**Antes (a5.2):** "• Parecido com SIMD, mas cada thread guarda o próprio estado • Até 48 warps por SM • Provável, leitura nossa: enquanto um warp espera a memória, outro executa, e a espera fica escondida"

**Depois (ilustração do tom, conferir os fatos no spec):** "Uma thread é uma pequena tarefa: uma sequência de instruções com os seus próprios dados. A GPU não manda instruções para uma thread de cada vez. Ela junta 32 threads num grupo chamado warp e manda a mesma instrução para as 32 de uma vez. É como um professor que dita a mesma conta para 32 alunos, e cada aluno faz a conta com os seus números. A NVIDIA chama esse jeito de trabalhar de SIMT, que quer dizer uma instrução para muitas threads. Cada bloco de execução do chip, o SM, pode manter até 48 warps prontos. A vantagem: quando um warp para esperando um dado da memória, o SM passa para outro warp que já tem o que precisa, e o tempo de espera não fica parado. Essa última parte é a nossa leitura de como a NVIDIA descreve o escalonador."

## Roteiro de estudo

Além dos textos de tela, o grupo precisa de um documento de estudo: para cada momento, o que aparece na tela, a fala completa, as palavras novas com definição, e duas ou três perguntas que a turma ou o professor podem fazer, com a resposta e a fonte.
