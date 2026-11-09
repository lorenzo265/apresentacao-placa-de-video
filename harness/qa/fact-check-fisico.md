# Fact-check independente: hardware físico (rodada de 2026-11-09)

- Data: 2026-11-09
- Auditor: agente `fact-checker` (Fable), em contexto separado de quem produziu os arquivos.
- Escopo: `harness/spec/sources/physical-card-sources.md`, `harness/design/assembly-plan.md` (seções 1, 2, 3 e 5) e `harness/story/video-plan.md` (seção 4: beats a0.1 a a3.7 contra a web; demais tabelas só contra arquivos locais).
- Resultado: **não aprovado na primeira passada** (3 achados que bloqueiam e 16 ajustes). As citações das fontes conferem quase todas; os erros estavam na classe de procedência e no texto de alguns beats. Correções aplicadas no mesmo dia pelo orquestrador. **A segunda passada do auditor ainda não foi feita.**

## Método
- **Datasheet NVIDIA:** lido diretamente, as 3 páginas como imagem. É a única leitura direta desta auditoria.
- **Gamers Nexus:** reaberta por extração automática dirigida, em 4 passagens que concordaram entre si. Não é leitura humana: citações acima de cerca de 125 caracteres vieram cortadas, e o auditor não viu o vídeo nem as 35 imagens.
- **Jon Peddie, Puget e as duas páginas NVIDIA da RTX 5090:** reabertas pelo mesmo método, com 1 ou 2 passagens cada.
- **Extras:** página do produto e blog sabareesh, 1 passagem cada.
- **Não reabertos:** wccftech, Notebookcheck, Northridge Fix, ficha Puget da 5090, cópia PNY e todos os "só snippet".
- **Arquivos locais:** `fact-check-isa.md`, `isa-sources.md`, whitepaper, READMEs de `harness/examples/` e `vault/01-Briefing/Requisitos da disciplina.md`.

## Resumo dos vereditos
- **Variante:** é a Workstation Edition. Gamers Nexus: "The one we're looking at specifically is called the Blackwell Workstation Edition", "We paid $8,000 for an RTX PRO 6000 GPU with 96GB of VRAM", "2 large fans on the front". "Max-Q" não aparece no artigo, e a placa não é a 5090 ("This is a 5090 die, just a fuller version of it").
- **Gamers Nexus, literal:** conferem os dois ventiladores na frente, os sete passos na ordem, "16 memory modules on the back", "32 total memory locations", pasta em vez de metal líquido, "GB 202-870-A1" (com espaço; a fonte chama de "SKU"), "customized pinout adapter", "12VHPWR cable", aletas, depressão e "vented slats".
- **Datasheet, literal:** conferem "1x PCIe CEM5 16-pin", "Total board power: 600 W", "5.4" H x 12" L, dual slot, extended height", "Double-flow-through", "channels airflow through dual axial pathways", "4x DisplayPort 2.1b", "PCIe 5.0 x16", "24,064", "512-bit", "1792 GB/s" e o rodapé "5349469. JUN26".
- **Jon Peddie:** conferem "4 pounds, 3 ounces, around 60% heavier", "top middle of the card", "4-to-1 adapter", "central, topside interface" e "bilateral 3D vapor chambers sandwiched between dual heatsinks and fans". As conversões fecham (1.899 g e 1.191 g).
- **Puget e NVIDIA (5090):** conferem "housing nearly identical to the GeForce RTX 5090", "Liquid Metal thermal interface material (TIM), and a unique 3-piece PCB" e "A 3D Vapor Chamber with integrated heat pipes and active fins".
- **Beats sem erro de fato:** a0.2, a0.3, a1.2, a1.3, a1.5, a2.1 a a2.8, a3.1, a3.2 (com a ressalva do achado 4), a3.4, a3.5 e a3.7.

## Respostas às perguntas da auditoria
1. **`confirmed` a rebaixar:** "16 posições na frente" e "32 chips" (o que é `confirmed` é "32 posições"); a ligação dos cabos flat "entre as placas" (a existência é `confirmed`); "axiais" nos ventiladores; o arranjo "um chip em cada face" (`inferred`); toda coluna Forma "derived (fotos)", que hoje é intenção, porque nenhuma foto foi vista. Os estágios E1 a E7 ficam `confirmed`.
2. **"confirmed (terceiro)":** a classe não existe na regra do projeto. Separar pelo tipo de dado, não pelo autor: observação direta desta placa por revisor (peso, conector no topo, pads, indutores) tem a mesma natureza do teardown, que também é de terceiro; descrição sem abrir a placa ("bilateral 3D vapor chambers") é `derived`; juízo comparativo ("nearly identical") é `derived`; o que só repete o datasheet cita o datasheet. Recomendação: `derived` com a fonte nomeada na tela, até o humano decidir se `confirmed` inclui "observação direta desta placa por terceiro identificado".
3. **Contas de memória:** a aritmética está certa. "32 posições" é literal, e a fonte fala em "locations", não em chips montados. A própria Gamers Nexus conclui "which means that they are 3GB memory modules as that totals 96GB": os 3 GB são dedução da fonte, sem leitura de marcação do chip, e continuam `derived`. Alternativa que as fontes registradas não excluem: 24 chips de 4 GB (16 no verso e 8 na frente). "Dois chips por controlador" é uma média (32 ÷ 16), válida só se as 32 posições estiverem ocupadas. O mecanismo (cada chip com 16 bits, um par por face) não está em fonte nenhuma, e a placa irmã mostra um chip por controlador: `inferred`.
4. **Beats com problema:** a2.9 e a3.3 bloqueavam; a1.1, a1.4, a1.6, a2.10 e a2.11 pediam ajuste.
5. **Termos:** "CEM5" é a especificação (PCIe CEM 5.x), não o nome do conector. "Canal" estava no lugar de "controlador". "Clamshell" estava no sentido certo, mas afirmava algo `inferred`. "Double flow-through" e "PAM3" estão corretos.

## Achados e resolução
| # | Severidade | Achado | Resolução |
|---|---|---|---|
| 1 | bloqueia | Beats a2.9 ("600 W entram por aqui") e a1.4 atribuíam 600 W ao conector. O datasheet diz "Total board power: 600 W", e a conta "conector e slot" está declarada como não fechada | Texto dos dois beats passou a "600 W de potência total da placa". Nenhum watt é atribuído ao conector antes de a norma ser registrada |
| 2 | bloqueia | Beat a3.3 e a seção 5 do plano de montagem davam "dois chips por controlador, um em cada face" como `derived`, citando o whitepaper. O whitepaper só dá 16 × 32 bits; a 5090 FE mostra um chip por controlador | Razão 2:1 passou a `derived` condicional (vale se as 32 posições estiverem ocupadas). O arranjo em pares passou a `inferred`, com selo "provável", e foi para a fila da proposta de engenharia |
| 3 | bloqueia | Classe "confirmed (terceiro)" fora da regra, no arquivo de fontes; a1.4 deixava a posição do conector sem classe | Classe removida. Dados de revisores passaram a `derived` com a fonte nomeada. A decisão sobre ampliar `confirmed` foi para o humano (`STATUS.md`, seção 8) |
| 4 | ajusta | "16 posições na frente" e "32 chips" como `confirmed` | 32 posições e 16 módulos no verso `confirmed`; 16 na frente e 32 chips `derived` |
| 5 | ajusta | O arquivo de fontes omitia que a Gamers Nexus afirma os 3 GB; "clamshell" estava como `derived` | Frase da fonte citada; clamshell movido para proposta (`inferred`) |
| 6 | ajusta | "O nome 12V-2x6 vem de revisores": para esta placa a fonte aberta diz "12VHPWR" | Corrigido: a equivalência com o "CEM5 16-pin" do datasheet não está provada |
| 7 | ajusta | "Axiais" atribuído à Gamers Nexus, que só diz "2 large fans on the front" | Fonte passou a "GN; datasheet", com "axiais" como `derived` |
| 8 | ajusta | Beat a1.6 "mesma carcaça" | "Carcaça quase idêntica, segundo a Puget" |
| 9 | ajusta | Trajeto dos cabos flat e das saídas no caminho de dados como `confirmed` | Só a existência dos cabos é `confirmed`; o trajeto é `derived` da 5090 FE |
| 10 | ajusta | Negativas universais ("nunca foi mostrado em teardown", "não é público") com cinco sites bloqueados; a2.11 sem o `inferred` do estágio E8 | "Não achamos fonte que mostre"; `inferred` (E8) acrescentado |
| 11 | ajusta | Coluna Forma "derived (fotos)" e ato 1 "confirmado (fotos e ficha)": ninguém viu as fotos | "A derivar de fotos (não catalogadas)" |
| 12 | ajusta | "Canal" em vez de "controlador" | Corrigido nos dois planos |
| 13 | ajusta | O plano de montagem citava este relatório antes de ele existir | Resolvido com a gravação deste arquivo |
| 14 | ajusta | Tolerância de 0,5 mm no envelope: a fonte oficial tem resolução de 0,1" | 137,2 × 304,8 mm declarado como convenção do projeto; tolerância de 0,5 mm vale contra a convenção, não contra a placa |
| 15 | ajusta | "Metade dos indutores coberta por pad" como contagem: a frase da fonte é ambígua | Citação em inglês no arquivo de fontes; não é usada como contagem |
| 16 | ajusta | Capa do datasheet descrita como "dois recortes de ventilador": o auditor viu duas áreas de grade fina, sem pás | "Face não identificada" até catalogar as fotos |
| 17 | ajusta | Beat a5.11: 2.048 como "confirmed (medido)" | `derived` (conta M × N × K) |
| 18 | ajusta | Beat a5.5 "4 ciclos por instrução" | "4 ciclos em INT32 e FP32" |
| 19 | ajusta | Beat a7.1: a coluna da RTX 6000 Ada não está no excerto local do whitepaper | Beat marcado "a registrar" e pendência aberta |
| 20 | nota | Frases úteis da Gamers Nexus não registradas: "The PCB is in the center of the card", "The design is full flow-through, which pushes air straight through the card rather than into a PCB", "We also saw a massive GPU substrate" | Registradas no arquivo de fontes e usadas no plano de montagem |
| 21 | nota | A figura 3 da Jon Peddie é creditada "Source: Nvidia" e pode ser ilustração oficial do cooler | Registrado como pista para a F2 |
| 22 | nota | O blog sabareesh diz que o indutor perdido é "identical to the 23 still on the board" | Registrado como pista, não como contagem |
| 23 | nota | A fonte grafa "GB 202-870-A1" e chama de "SKU"; a marcação não foi lida em foto | Grafia corrigida, com a ressalva |
| 24 | nota | Beat a4.4 sem "illustrative" para a posição; a5.9 sem a palavra "úteis" | Corrigido |
| 25 | nota | "40,64 mm", "filtros" e "parece repetir a descrição da NVIDIA" sem fonte | Marcado como provisório ou removido |
| 26 | ajusta | Cobertura: o item pipeline não tinha beat de prioridade 1 com conteúdo; MMU e interrupções só têm beats bloqueados | a5.5 promovido a prioridade 1. A decisão sobre os beats de lacuna do ato 6 foi para o humano |

## O que o auditor não conseguiu verificar
- **Imagens e vídeo da Gamers Nexus.** Não foi confirmado qual é o "back" do PCB nem a face mostrada no render do datasheet.
- **Frases longas** da Gamers Nexus e da Jon Peddie vieram truncadas, entre elas a dos indutores e a do peso. A Jon Peddie não diz como pesou a placa nem se o adaptador vem na caixa.
- **Guia de instalação da página da RTX 5090.** O "3-slot card (61mm)" consta, mas o extrator devolveu potências que não batem entre si. Reler antes de usar.
- **"PAM3" no whitepaper, p. 12.** Não se sabe se a sigla é literal ou glosa do excerto local. A relação entre os 512 bits lógicos e as linhas físicas do GDDR7 depende da norma, que não está registrada.
- **Norma do conector de 16 pinos e potência do slot.** Não registradas: a equivalência entre "CEM5 16-pin", "12VHPWR" e "12V-2x6" não foi confirmada.
- **Fontes fora da prioridade** (wccftech, Notebookcheck, Northridge Fix): não reabertas, e não aprovadas por falta de erro aparente.

## Estado após as correções
Os 26 achados têm resolução aplicada nos arquivos. O arquivo de fontes passa a "auditada com ressalvas". Os dois planos continuam **sem aprovação** até uma segunda passada do `fact-checker` e o gate humano.
