# Auditoria dos textos do modo Explorar

Agente: `fact-checker` (contexto separado de quem escreveu), em 2026-11-12. Objeto: `content/pt-BR/pecas.json`, primeira versão. Conferido contra `spec/card.spec.json`, `spec/sources/physical-card-sources.md`, `spec/references/index.md`, `design/assembly.json`, `content/pt-BR/beats.json`, `story/storyboard.json` e `plano/camera-gsap.md`. O auditor não reabriu as páginas das fontes nem viu as fotos.

**Veredito da primeira passada: reprovado, com 5 erros de correção curta.** Todas as correções propostas foram aplicadas com o texto do auditor. **Falta a segunda passada** sobre o arquivo corrigido e sobre a tela pronta.

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

## Pendente

1. Segunda passada do `fact-checker` sobre `pecas.json` corrigido.
2. `power.vrm.mem` não tem posição nem âncora no assembly: se não houver malha clicável, tirar da lista.
3. Clique numa pá (`cooler.fan.*.blade`) deve cair no ventilador pai: conferido no código (sobe pela hierarquia do GLB), falta conferir na tela.
