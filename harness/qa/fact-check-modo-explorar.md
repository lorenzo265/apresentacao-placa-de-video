# Auditoria dos textos do modo Explorar

Agente: `fact-checker` (contexto separado de quem escreveu), em 2026-11-12. Objeto: `content/pt-BR/pecas.json`, primeira versão. Conferido contra `spec/card.spec.json`, `spec/sources/physical-card-sources.md`, `spec/references/index.md`, `design/assembly.json`, `content/pt-BR/beats.json`, `story/storyboard.json` e `plano/camera-gsap.md`. O auditor não reabriu as páginas das fontes nem viu as fotos.

**Veredito da primeira passada: reprovado, com 5 erros de correção curta.** Todas as correções propostas foram aplicadas com o texto do auditor. A segunda passada está abaixo.

## Erros (aplicados)

| # | Achado | Correção aplicada |
|---|---|---|
| 1 | Camada 1 se chamava "Bracket com as saídas de vídeo" e usava o beat a1.5. As saídas (`io.board.dp`) não saem no E1, a1.5 não cita o teardown, e a fonte diz "back plate": o bracket é leitura de foto (`derived`) | Nome "Bracket" e texto próprio `derived`: "Primeiro passo: a Gamers Nexus diz que tirou a "back plate". Pelas fotos, a peça que sai é o bracket [...]. As portas não saem com ele." |
| 2 | Peça `inferred` ou `derived` com beat perdia o selo da peça e a ressalva do assembly (`power.vrm.gpu`, `flex.fan.*`, `power.inductors`, `mem.front`) | Regra de tela: o selo ao lado do nome é sempre o da peça (existência e forma), a procedência do beat aparece junto do texto, e a ressalva aparece sempre que existe |
| 3 | `power.vrm.gpu` chamado "Fases de energia do chip": as fontes não dão as fases | "Regulador de tensão do chip (provável)", sem beat |
| 4 | `flex.fan.1` e `flex.fan.2` com o mesmo nome do cabo visto (`flex.dp`) | `flex.dp`: "Cabo flat largo". Os outros dois: "Cabo flat fino (provável)" |
| 5 | `power.vrm.mem` chamado "Alimentação da memória" | "Regulador de tensão da memória (provável)" |

## Ressalvas (aplicadas onde havia correção)

- Camada 8, texto novo: cada frase tem fonte e a procedência `derived, inferred, illustrative` está certa. A linha de fonte passou a dizer "fotos lidas por nós". O `_doc` passou a dizer que o interior é `inferred` e a abertura é `illustrative`.
- `pcb.main` ficou sem beat (a2.7 fala da pasta, não do PCB), para a ressalva das medidas aparecer.
- `pcb.back_frame`: "Chapa de apoio da mola". `io.board`: "Placa das saídas de vídeo (deduzida)".
- Rótulo "Passo N de 7 do teardown": a ordem das sete frases é `confirmed`. A identificação das peças dos passos 1 e 2 e a contagem de sete são `derived`; as camadas 1 e 2 levam o selo `derived`.
- Mantidos, verdadeiros mas fracos fora do tour: `frame.shroud` com a1.6 (segunda frase fala da memória), `frame.face_b` com a1.3 (fala do ar), camada 4 com a2.4 (cita o grampo, que não está no modelo).
- Passos que não batem por inteiro com o modelo: parafusos do passo 3 e grampo do passo 4 não estão modelados; o E6 inclui `flex.fan.*`, que são `inferred`.

## Segunda passada (2026-11-12)

`fact-checker`, sobre `pecas.json` corrigido e os textos fixos de `viewer/src/explorar.js`. Os 5 erros da primeira passada foram dados como corrigidos e a regra de tela como implementada. **Veredito: reprovado por 1 erro num texto fixo da tela; o resto, ressalvas.** Tudo aplicado com o texto do auditor, menos o item 7.

| # | Achado | Aplicado |
|---|---|---|
| 1 (erro) | "Sem texto próprio: não achamos mais do que a ressalva abaixo nas fontes lidas" afirmava uma lacuna de fonte que não existe (falta texto auditado, não fonte) | "Esta peça ainda não tem texto auditado. Veja a ressalva abaixo." (a segunda frase só quando há ressalva) |
| 2 | "Base da placa: não sai no teardown" | "Fica na placa: não é retirada nos 7 passos do teardown" |
| 3 | Selo do E8 dizia "interior do cooler sem foto"; a base de contato aparece em foto | "Provável: do interior do cooler só a base de contato aparece em foto. Abertura da carcaça ilustrativa" |
| 4 | Título da lista e "Como usar" punham a camada 8 na ordem do teardown; "provável" sumia com a camada fora | Título "Camadas 1 a 7 na ordem do teardown. A 8 é ilustrativa", texto de uso refeito, marca "fora, provável" |
| 5 | Herança de estágio no `sync-data.mjs` sem aviso | O sync registra no log a peça que herdar estágio (hoje nenhuma herda) |
| 6 | `_doc` dizia "beat já auditado", mas a2.2 a a2.6 só têm a primeira passada dos atos 0 a 3 | `_doc` corrigido |
| 7 | Camada 1 ("As portas não saem com ele") e peça `io.bracket` com a1.5 ("com 4 portas") em cliques seguidos | Não mexido: o auditor não exige. Fica para o autor |
| 8 | Câmara de vapor e tubos de calor sem a marca que `io.board` ganhou | "Câmara de vapor (deduzida)", "Tubos de calor (deduzidos)" |

Depois destas correções ninguém reauditou: **falta a terceira passada**.

## Pendente

1. Terceira passada do `fact-checker` (textos fixos corrigidos) e segunda passada dos beats a2.2 a a2.6.
2. `power.vrm.mem` não tem posição nem âncora no assembly: se não houver malha clicável, tirar da lista.
3. Clique numa pá (`cooler.fan.*.blade`) deve cair no ventilador pai: conferido no código (sobe pela hierarquia do GLB), conferido na tela em 2026-11-12 (o clique na pá selecionou `cooler.fan.1`).

## Terceira passada (2026-11-12)

`fact-checker`, em contexto separado, sobre `pecas.json` e os textos fixos de `viewer/src/explorar.js` depois das correções da segunda passada. Conferido contra `spec/card.spec.json`, `design/assembly.json`, `design/proposal.md`, `spec/sources/physical-card-sources.md`, `spec/references/index.md`, `content/pt-BR/beats.json`, `story/storyboard.json` e `viewer/public/data/pecas.json`. O auditor não reabriu as páginas das fontes, não viu as fotos e não rodou o viewer. O contexto do auditor só tinha leitura; a orquestradora transcreveu este bloco.

**Veredito: reprovado, com 3 erros de correção curta.** Os 5 erros da primeira passada e os itens 1 a 4, 6 e 8 da segunda estão corrigidos. O item 5 da segunda (aviso no `sync-data.mjs`) não foi conferido. O item 7 continua aberto, não obrigatório.

| # | Achado | Correção obrigatória |
|---|---|---|
| 1 (erro) | Camada 8, caption: "Não achamos fonte que mostre o interior do cooler desta placa." contradiz o selo fixo da mesma tela, a ressalva da câmara de vapor e o catálogo (base de contato em gn-32, gn-34, gn-35, gn-39) | "Do interior do cooler, só a base de contato aparece nas fotos desta placa." |
| 2 (erro) | Camada 8, caption: "os ventiladores nunca saem nas fotos" também se lê como "nunca aparecem nas fotos", o que é falso (gn-02, gn-26, gn-46). A mesma frase está no `viewer_disclaimer` de `cooler.fan.1` e `cooler.fan.2` | "Abrir a carcaça assim é ilustrativo: no teardown, os ventiladores não são retirados." No assembly: "O estágio com o cooler aberto é didático: no teardown, os ventiladores não são retirados." e rodar o sync |
| 3 (erro) | `power.controller` ("Controlador de energia") e `power.aux` ("Conversores auxiliares"): o nome afirma a função como fato. A proposta diz "Leitura incerta" e "a reconferir" (Q10), e a seção 16 das fontes diz "sem valor de fato" | "Controlador de energia (provável)" e "Conversores auxiliares (prováveis)" |

### Ressalvas da terceira passada

- Camada 5 mostra o selo "Provável" (procedência de a2.5 no storyboard) sem conteúdo inferido na caption.
- `gpu.package` com a2.12: "Na foto, ela só é legível em parte" é leitura nossa (`derived`) e o beat só declara `confirmed`. A nota de `chip.marking` no spec ("não foi lida em foto pelo grupo") contradiz o assembly ("lida em parte em gn-35, gn-42").
- `mem.front`: os chips da frente são dedução. O selo e a ressalva cobrem; "(deduzida)" no nome ficaria coerente com `io.board`.
- `mem.back` com a3.1: a caption não fala do verso.
- Beats a2.2 a a2.6 estão `draft` no storyboard e sem segunda passada.
- O `_doc` de `pecas.json` tem ponto e vírgula. Não vai para a tela.
- `power.vrm.mem`: `caminhos.json` cita o nó `power.vrm.mem.4`, mas a malha clicável não foi conferida na tela.

### Correções aplicadas (orquestradora, 2026-11-12)

Os três erros foram corrigidos com a redação sugerida, em `content/pt-BR/pecas.json` e nos dois `viewer_disclaimer` de `design/assembly.json`, depois `npm run sync`. A mesma frase ambígua aparecia em mais dois textos internos do assembly (racional de `cooler.fan.1` e o motivo do aviso de `cooler.base`), também corrigidos. Falta a quarta passada, só sobre esses itens.
