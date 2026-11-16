Reescrita urgente das falas do seminário (é hoje) do tour da RTX PRO 6000 Blackwell. Repositório /home/user/apresentacao-placa-de-video. Trabalhe em PT-BR.

## Por quê
O autor achou o texto atual "vergonhoso de ruim": superficial, confuso, cheio de frases vagas, como se o público já soubesse o que tem na placa. Ninguém na sala sabe, nem o próprio grupo. A apresentação precisa ensinar, com conteúdo embasado e bem estruturado, focada no que o professor pediu.

## Leia antes (nesta ordem)
1. `harness/plano/guia-falas.md`: as regras desta reescrita. Siga à risca, inclusive o exemplo de antes e depois.
2. `vault/01-Briefing/Requisitos da disciplina.md`: o que o professor cobra (registradores, instruções, CISC ou RISC, MMU, interrupções, gerenciamento de memória, pipeline, cache; "não basta apresentar as características").
3. `harness/content/pt-BR/beats.json`: texto atual (campos `headline`, `caption`, `fala`, `source_line`, `claims`).
4. `harness/story/storyboard.json`: o que cada momento mostra na tela (peça, diagrama, câmera, procedência). Os diagramas estão em `harness/diagrams/*.json`.
5. `harness/spec/card.spec.json`: os fatos com procedência (`confirmed`, `derived`, `inferred`, `illustrative`). Só use fatos daqui, das fontes em `harness/spec/sources/` e dos exemplos em `harness/examples/`. Sem fonte, sem fato. Nunca apresente `inferred` como fato. Para entender os conceitos com profundidade, use também o artigo do grupo e as notas do roteiro em `vault/` (seções 01 a 14).

## Sua parte
Os momentos: __MOMENTOS__.
Antes e depois da sua parte vêm outros momentos escritos por outros agentes em paralelo; a primeira frase da sua parte pode retomar o assunto anterior e a última deve preparar o seguinte (veja a lista completa do corte do seminário no `storyboard.json`, beats com `priority` 1 e `status` diferente de `draft`).

Para cada momento, escreva:
- `headline` (até 8 palavras, linguagem simples), `caption` (até 2 frases curtas, com a frase-chave e o número principal), `fala` (4 a 8 frases completas, faladas, que explicam: o que é em qualquer processador, como é nesta GPU com números e fonte, por que é assim), `source_line` (mantenha ou ajuste para as fontes usadas) e `claims` (ids do spec que sustentam o texto; acrescente os que usar).
- Para o roteiro de estudo: o que aparece na tela, as palavras novas com definição de uma linha, e 2 ou 3 perguntas que a turma ou o professor podem fazer, com a resposta curta e a fonte.

O texto precisa bater com o que a tela mostra no momento (peça destacada, diagrama). Se a tela não sustenta a fala, diga no relatório.

## Onde gravar (NÃO edite beats.json: outros agentes trabalham em paralelo)
- Textos: `harness/content/pt-BR/reescrita/__ARQ__.json`, no formato `{"<id>": {"headline": ..., "caption": ..., "fala": ..., "source_line": ..., "claims": [...]}}`.
- Roteiro de estudo: `harness/content/pt-BR/reescrita/__ARQ__-estudo.md`.
Não faça commit. Na resposta final, liste os momentos feitos, os fatos novos que usou (com id do spec) e qualquer ponto em que a tela não combina com a explicação.
