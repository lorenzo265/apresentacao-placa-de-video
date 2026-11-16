# Briefing: enxugar as falas e fechar o corte do seminário

Seminário hoje, 22 minutos. As falas reescritas (`harness/content/pt-BR/reescrita/parte-1.json`, `parte-2.json`, `parte-3.json`, já auditadas pelo `fact-checker` e corrigidas) somam cerca de 6.000 palavras, uns 40 minutos falados. Decisão do autor: **enxugar e cortar**.

## Regras
1. Leia `harness/plano/guia-falas.md` (o tom que o autor quer: claro, concreto, explica antes de usar, nada de frases vagas). Enxugar não pode voltar ao estilo de tópicos soltos de que o autor reclamou.
2. **Orçamento:** no máximo 2.900 palavras de `fala` no total do corte do seminário (cerca de 20 minutos a 140 palavras por minuto). Cada fala fica entre 70 e 140 palavras, em frases completas.
3. **Estrutura de cada fala mantida:** o que é (com a comparação do dia a dia, se ajudar), como é nesta GPU (o número principal com unidade), por que é assim. Corte detalhes secundários, segundos números, ressalvas longas (deixe a ressalva essencial em uma frase curta) e repetições entre momentos.
4. **Sem fato novo.** Só pode encurtar ou reorganizar o que já está nas partes auditadas. Não troque números nem procedência. "Provável", "nossa leitura" e "não achamos nas fontes lidas" ficam quando a frase continua.
5. **Cortes de momentos:** tire do corte do seminário os momentos menos centrais para o enunciado, até caber no orçamento. Candidatos: a5.7 (listagem SASS), a5.16 (divergência), t1.1 (entrada no chip), a2.13 (placa aberta), a4.4 (planta do L2). Os itens do enunciado (registradores, instruções, CISC ou RISC, MMU, interrupções, gerenciamento de memória, pipeline, cache) precisam continuar cobertos. Quando um momento sai, a ideia essencial dele pode entrar numa frase do momento vizinho.
6. **Ordem:** ponha a5.1 e a5.2 (warp e SIMT) antes de a5.5 (pipeline), porque o pipeline usa a palavra warp.
7. `headline` até 8 palavras, `caption` até 2 frases curtas. Sem travessões nem ponto e vírgula.

## Saídas
- `harness/content/pt-BR/reescrita/final.json`: `{"<id>": {"headline", "caption", "fala", "source_line", "claims"}}` só dos momentos que ficam no corte, na ordem nova, e uma chave `"_corte"` com a lista ordenada dos ids e `"_fora"` com os que saíram.
- Os roteiros de estudo `parte-*-estudo.md` NÃO são encurtados: eles guardam a explicação completa. Acrescente ao fim de cada um uma nota curta dizendo quais momentos saíram do corte e que a fala completa está ali.
- Na resposta: a lista ordenada do corte, as palavras por momento e o total, e o que foi cortado de cada fala em uma linha.
