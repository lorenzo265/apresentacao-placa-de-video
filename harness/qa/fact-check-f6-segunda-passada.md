# Fact-check da F6: segunda passada

- Data: 2026-11-10
- Auditor: agente `fact-checker` (Fable), em contexto separado, diferente do da primeira passada.
- Escopo: os 25 beats de `content/pt-BR/beats.json`, os 8 diagramas dos atos 4 a 6, os 16 fatos acrescentados ao spec depois da primeira passada, as listas `provenance` do storyboard e a tabela de cobertura do enunciado.
- **Veredito: aprovado com ressalvas.** Os 3 bloqueios da primeira passada estão resolvidos e não há erro de fato nos textos dos 25 beats. As ressalvas são de metadado e de sincronização.
- Limite: o material mudou durante a auditoria (diagramas novos chegaram). O veredito **não cobre** `sys.cmd`, `close.delta`, `close.gaps` nem os beats a5.3, a5.14, a6.3, a7.1, a7.2 e a7.4, que precisam de passada própria.

## Os 24 achados da primeira passada
- **Resolvidos (20):** 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 19, 22, 23 e 24.
- **Resolvidos em parte (4):** 9 (rótulos de tela certos; notas internas e o script ainda dizem "desabilitadas"), 18 (duas linhas da tabela de cobertura), 20 (as setas existiam no diagrama, mas o beat não as listava), 21 (duas notas do spec).

## Conferências desta passada
- Os contadores novos de `chip.isa` (255 por thread, 65.536 por SM) conferem com o Tuning Guide.
- O par `mma.sync` e `HMMA.16816.F32` de `chip.risc` confere com os arquivos de `examples/mma/`.
- 14 dos 16 fatos novos conferidos por busca literal nas cópias baixadas, com valor e procedência certos.

## Ressalvas e resolução
| # | Peso | Onde | Problema | Resolução |
|---|---|---|---|---|
| N1 | antes do gate humano | storyboard, `provenance` de dez beats | A lista não refletia tudo o que o texto e o diagrama mostram (contas nossas sem `derived`, leituras do grupo sem `inferred`) | passado ao `storyboard-director` |
| N2 | antes do gate humano | a5.9, `flows` | As setas novas (`isa.map.12` a `16`) não estavam listadas no beat | passado ao `storyboard-director` |
| N3 | antes do gate humano | cópias de dados do viewer | Estavam defasadas em relação aos diagramas | o build sincroniza; refeito antes de gerar o animatic |
| N4 | antes de fechar a F6 | `sys.irq`, nó de envio de comandos | Apontava para um quadro ainda não auditado | texto neutro até a6.3 passar pelo gate |
| N5 | antes de fechar a F6 | spec, `cmd.user_path` | Afirmava sem trecho que o caminho de um programa CUDA "passa pela parte fechada do driver" | o fato sai do spec e vira lacuna; o texto fica como leitura nossa |
| N6 | antes de fechar a F6 | spec, duas lacunas | Diziam "não aberto" e "nenhum trecho" para coisas já lidas | reescritas |
| N7 | antes de fechar a F6 | a5.16 | A frase sobre a compute capability 7.0 não tinha fato | trecho registrado; fato `simt.independent_scheduling` criado e citado |
| N8 | nota | `chip.isa` | Falta a seta de `%ntid.x` para `LDC R7` | passado ao `diagram-designer` |
| N9 | nota | `chip.isa`, contadores | Não diziam o quê | passado ao `diagram-designer` |
| N10 | nota | fontes, GPFIFO | Faltava a frase dos ponteiros GET e PUT | acrescentada (`uvm_pushbuffer.h`, linhas 74 e 75) |
| N11 | nota | spec, âncoras de `source` | Formato desigual entre fatos antigos e novos | fica para depois |
| N12 | nota | a5.1, a5.8, a6.4 | Um fato não citado; dois destaques fora do foco | fato citado; foco passado ao `storyboard-director` |

## O que o auditor não conseguiu verificar
- As Figuras 3 e 5 do whitepaper: a cópia em texto só tem a legenda. O arranjo do diagrama de blocos e "uma SFU e quatro LD/ST por bloco" ficam pela palavra de quem viu a página (a primeira passada e a sessão principal).
- Jia et al.: que opcode e predicado ficam dentro dos 91 bits é leitura razoável, marcada `derived`, sem excerto.
- Itens herdados: Jarmusch, datasheet, Pascal, P100, a contagem de 258 mnemônicos.

## Estado
Os 25 beats e os 8 diagramas dos atos 4 a 6 estão **aprovados com ressalvas** no gate de fatos. Falta fechar as ressalvas acima, auditar os seis beats e três diagramas novos, e o **gate humano** do animatic.
