# Diagramas dos níveis 2 a 4

Os níveis de chip, SM e conceito não são geometria 3D. São **cenas declarativas** em `diagrams/<id>.json`, desenhadas pelo viewer em uma camada SVG. Este arquivo é o contrato entre quem gera os diagramas (`diagram-designer`) e quem os desenha (`viewer-engineer`). O schema é `schemas/diagram.schema.json` e a validação é `tools/validate.py`.

## Regras

1. **Diagrama não é editado à mão.** Cada `diagrams/<id>.json` sai de um script `diagrams/build_<id>.py`, que lê `spec/card.spec.json`. O campo `generated_by` guarda o nome do script. Se o spec mudar, roda-se o script de novo.
2. **Toda contagem vem do spec.** Nó com número traz `count.claim`, o id do fato. O validador recusa diagrama que desenha um número diferente do spec.
3. **Forma e posição são ilustrativas.** Todo nó tem `shape_provenance` (`illustrative` ou `inferred`). O diagrama inteiro tem `disclaimer`, que o viewer mostra.
4. **As contas ficam declaradas.** `checks` lista as contas que o desenho precisa fechar (`chip.tpc_active * 2` = 188). O validador recalcula.
5. **Nada de mecanismo sem fonte.** Se o beat está bloqueado, o diagrama mostra a lacuna: o que se sabe, o que não é público.

## Geometria

- Cada diagrama tem o seu próprio sistema de coordenadas: `size` é `[largura, altura]`, a origem fica no canto superior esquerdo e o y cresce para baixo. Use 1600 × 900 como padrão.
- Os ids de nó e de fluxo são **únicos no projeto inteiro**, não só dentro do diagrama: cada diagrama usa um prefixo próprio (`chip.`, `sm.`, `warp.`, `isa.`, `risc.`, `memh.`, `mmu.`, `irq.`).
- Todo nó tem `rect: [x, y, largura, altura]` **absoluto dentro do diagrama** (não relativo ao pai). `parent` é a hierarquia lógica, usada para destaque, e não muda a geometria.
- A ordem do array `nodes` é a ordem de desenho: o que vem depois fica por cima. Liste o contêiner antes do conteúdo.
- `embed`: o nó contém outro diagrama. O viewer desenha o diagrama filho ajustado ao `rect` do nó, mantendo a proporção e centralizando. É assim que o zoom contínuo funciona: o diagrama do SM mora dentro de uma das células de SM da planta do chip. Um diagrama pode ser embutido em um só lugar.
- Diagramas que não estão dentro de outro (MMU, interrupções) são colocados lado a lado pelo campo `world` do storyboard.

## Texto

- `label` é o texto principal e `sublabel` o secundário. Os dois são opcionais: células pequenas e repetidas ficam sem texto.
- Sem `label_size`, o viewer ajusta o texto ao retângulo. Com `label_size`, usa essa altura, em unidades do diagrama.
- `mono: true` para código, endereços e nomes de instrução. `align` é `center` (padrão) ou `left`.
- O viewer esconde rótulos que ficariam menores que 9 px na tela e os mostra quando o zoom chega. Não é preciso tratar isso no diagrama.
- Português do Brasil, com acentos. Nomes de instrução e trechos de código ficam como na fonte.

## Estilo

`kind` escolhe a classe visual (`k-<kind>` no CSS do viewer). Use os da tabela. Se precisar de um novo, acrescente aqui e avise o `viewer-engineer`.

| kind | Uso |
|---|---|
| `die`, `frame` | contorno de um diagrama ou de uma região |
| `gpc`, `tpc`, `sm` | hierarquia do chip |
| `block`, `sched`, `regfile`, `core`, `tensor`, `rt`, `tex`, `ldst`, `sfu` | unidades dentro do SM |
| `cache`, `memory`, `memctl` | níveis de memória e controladores |
| `field` | campo de bits (palavra de instrução, endereço virtual) |
| `table`, `cell`, `header` | tabelas (tabela de páginas, critérios) |
| `codeline` | uma linha de código (use `mono` e `align: left`) |
| `actor`, `lane` | CPU, driver, GPU nos diagramas de sistema; `lane` é a faixa horizontal de um ator |
| `step` | passo numerado de um fluxo (tratador de interrupção, percurso da tabela de páginas) |
| `thread`, `thread-alt` | uma thread de um warp; `thread-alt` é a thread que seguiu outro caminho (laranja, como no logotipo do grupo) |
| `counter` | número em destaque |
| `note`, `gap` | observação; `gap` é lacuna declarada ("não é público") |

Um `kind` que o viewer não conhece recebe o estilo neutro de `frame`, sem erro.

`state: "disabled"` desenha o nó apagado e hachurado (posição não habilitada). `tags` são livres e servem para o storyboard selecionar grupos (`tag:sm`).

## Fluxos

`flows` liga dois nós. `points` é a polilinha em coordenadas do diagrama; sem ele o viewer liga os centros. `path` usa as cores dos três caminhos do tour (`data` em ciano, `energy` em âmbar, `heat` em vermelho) ou `control`. Um fluxo só é animado no beat que o lista.

## O que o storyboard faz com um diagrama

Um beat de nível 2 a 4 tem `view` (em vez de `camera`):

- `view.diagram` e `view.focus`: o viewer enquadra o retângulo que envolve os nós de `focus`, com `padding` de folga.
- `highlight`: nós em destaque; o resto do diagrama fica esmaecido.
- `flows`: fluxos animados.
- `callout.anchor`: o nó de onde sai a linha de chamada.

Seletores aceitam o id de um nó ou `tag:<nome>`.
