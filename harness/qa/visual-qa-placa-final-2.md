# Visual-QA: segunda passada da placa detalhada (2026-11-11)

- Autor: agente `visual-qa` (Opus), em contexto separado de quem modelou. Só reportou; não editou geometria, materiais nem storyboard.
- Objeto: `harness/dist/tour.html` de 19:26 (GLB embutido: `build/card_final.glb`, passe do Blender sobre `build/card.glb` sha256 bd75e85ba5aa, o mesmo do relatório de integração), tema Keynote, qualidade média, acumulação de 8 a 16 amostras, 1920 x 1080, deviceScaleFactor 1.
- Capturas: `harness/dist/qa/placa-final-2/` (não versionada). `v*` são vistas livres (modo `frame3d` do próprio `tour.html`), `b-*` são os beats do corte do seminário, `z*` são recortes ampliados (alguns clareados, marcados no nome), `cmp-*` são folhas lado a lado com a referência na mesma vista, `ref-*` são recortes das referências.
- Referência de cada vista: `pny/front` (face A quase ortogonal), `pny/back` (face B quase ortogonal, contatos em cima), `pny/3qtr-top-right`, `pny/3qtr-back-right`, `pny/3qtr-front-left`, `gn/gn-02`, `gn/gn-08`, `gn/gn-11` (bracket), `gn/gn-13` (borda superior), `gn/gn-29` (verso do PCB, E6). Vistas sem referência estão marcadas "sem referência".
- Cuidado com a equivalência das vistas: a câmera do viewer tem o eixo z como "para cima", então as vistas livres saem giradas no plano da imagem em relação às fotos. As folhas `cmp-*` giram o render (90 ou 180 graus, nunca espelham) até a mesma orientação da foto. Nenhuma folha põe lado a lado faces diferentes.

## Veredito: aprovado com ressalvas

O único bloqueio da primeira passada (achado 1, conector de energia invisível) está resolvido: o conector 2 x 6 com a faixa de sinal aparece pelo túnel na borda superior, no beat a1.4 e nas vistas equivalentes a `pny/3qtr-top-right` e `pny/3qtr-back-right`. Nenhum achado novo bloqueia. Ficam ajustes de forma (cubo dos ventiladores), de lookdev (tom quente, luva do túnel clara, tubos e chapa atrás das pás) e de storyboard (geometria sobre o cabeçalho em dois beats).

**Lateralidade: não está espelhada.** Conferido em quatro vistas equivalentes: face A contra `pny/front` (`cmp-v01-vs-pny-front.png`), face B contra `pny/back` (`cmp-v02-vs-pny-back.png`), três quartos contra `pny/3qtr-top-right` (`cmp-v03-vs-pny-3qtr-top-right.png`, render girado 90 graus) e contra `pny/3qtr-back-right` (`cmp-v04-vs-pny-3qtr-back-right.png`, girado 180 graus). Bracket, contatos, canal da borda superior, conector, logotipo e "RTX PRO 6000" ficam do lado certo. O logotipo foi lido de frente (`v30-logo-frontal-perto.png`): visto do lado dos ventiladores ele aparece de cabeça para baixo, e girado 180 graus (`z30-logo-girado-180-face-b-para-cima.png`) lê "nVIDIA" com o bloco do olho à esquerda, como em `ref-pny-logo-zoom.png`: as letras apontam para a face B e a leitura corre para a ponta oposta ao bracket, igual à referência. Não há espelhamento.

**Texto da face B:** legível e na orientação de `pny/back`: no triângulo junto à borda superior, ao longo da nervura, lendo de baixo para cima e para a direita com os contatos em cima; "RTX PRO" em negrito e "6000" em traço fino, como na referência (`v31-texto-face-b-frontal-perto.png` girado 180 graus, `v18-x-face-b-texto-perto.png`, `ref-pny-back-texto-zoom.png`, beats `b-a0.2.png` e `b-a1.3.png`).

**Medidas refeitas na vista ortogonal da face B (`v02-face-b-orto-pnyback.png`, 4,567 px/mm, perspectiva de cerca de 3%):**

| Medida | Modelo | Referência | Estado |
|---|---|---|---|
| Altura da carcaça / comprimento | 0,403 | 0,404 (renders) | igual |
| Contatos PCIe, a partir do bracket | 50,4 a 132,7 mm | 48,8 a 130,2 (renders), 48 a 131 (gn-05) | sem mudança, dentro de ±4 mm |
| Ponta do adaptador (com o gancho) | 151,3 mm | cerca de 144,7 (`pny/back`, 2,26 px/mm) | cerca de 6,6 mm mais longa, sem mudança |
| Contatos abaixo da carcaça | 14,0 mm | 11,1 (`pny/back`) a 12,8 | sem mudança |
| Aba do bracket além dos contatos | 14,7 mm | 15,5 (`pny/back`), 15,0 a 16,7 | corrigida (antes 11,5) |
| Cobertura do disco pelas pás (limiar de brilho) | cerca de 0,72 | cerca de 0,56 a 0,77 conforme o limiar | corrigida |

## O que foi verificado

Contorno e proporção nas vistas ortogonais das duas faces; quatro vistas de três quartos contra os renders da PNY; borda superior de frente (canal, duas fendas, retângulo liso, túnel, logotipo); borda inferior; as duas pontas; o bracket contra `gn-11`; o túnel do conector no eixo de 45 graus e em três outros ângulos; ventiladores de perto (7 pás nos dois, sentido igual ao de `pny/front`); tampas do X das duas faces de frente e oblíquas; grades da face B de frente e rasantes; estágios E6 e E7 contra `gn-29`; os 19 beats 3D do corte do seminário (a0.1 a a0.4, a1.1, a1.3, a1.4, a2.1, a2.2, a2.4, a2.7 a a2.11, a3.1 a a3.3, a7.5) e dois fora do corte (a2.5, a2.6), com selos, linha de chamada e caixa.

## Estado dos achados da primeira passada

| # | Antes | Estado agora | Evidência |
|---|---|---|---|
| 1 | bloqueia: conector invisível | **resolvido**. A face 2 x 6 e os 4 contatos de sinal aparecem pelo túnel; no a1.4 a linha de chamada termina sobre o conector. Ressalvas nos achados novos N3 e N4 | `v11-tunel-eixo-45.png`, `v12-tunel-cima-3qtr.png`, `v13-conector-como-pny-top-right.png`, `v14-conector-face-b-3qtr.png`, `b-a1.4.png`, `cmp-v04-vs-pny-3qtr-back-right.png` |
| 2 | grades transparentes | **resolvido**. Opacas, nervuras uniformes, nada do interior aparece | `v19-grade-face-b-obliqua.png`, `v04-3qtr-back-right.png`, `b-a1.3.png` |
| 3 | tubos brilhantes e chapa clara atrás das pás | **parcial**. Os tubos deixaram de brilhar, mas continuam legíveis como tubos cinza pelas pás do ventilador 2, e a chapa clara continua lá (é a pendência conhecida da pilha central). Ver N5 | `z-a0.1-ventilador2.png`, `z17-atras-ventilador2.png` (clareado 2x), `z06-ventilador2-cubo-interior.png` (clareado 1,8x) |
| 4 | triângulos foscos e cinza | **parcial**. Em vista oblíqua agem como laca (reflexo nítido em degradê). De frente ficam marrom-escuros e chapados, não pretos. Ver N2 | `v12-tunel-cima-3qtr.png`, `v17-x-face-a-3qtr.png`, `v01-face-a-orto.png`, `v31-texto-face-b-frontal-perto.png` |
| 5 | pás de corda estreita | **resolvido**. Cobertura de cerca de 0,72; as pás quase se tocam, como em `pny/front` | `cmp-v01-vs-pny-front.png`, `v15-ventilador1-perto.png` |
| 6 | cubos cromados | **parcial**. O tampo ficou acetinado, mas segue mais claro que a referência (cerca de 145 contra 96 de luminância em `v06` contra `pny/3qtr-front-left`), e a parede lateral do cubo aparece clara e alta. Ver N1 | `z06-ventilador2-cubo-interior.png`, `ref-pny-3qtr-front-left-ventilador2.png`, `v16-cubo-perto-obliquo.png` |
| 7 | linhas claras nas tampas do X da face A | **parcial**. Restam duas ou três linhas verticais finas perto do eixo central das duas tampas | `z17-costura-tampas-x.png` (clareado 2,2x), `z01-face-a-centro-x-clareado.png` |
| 8 | pontas dos tubos na ponta oposta | **resolvido**. Só os 2 furos pequenos, como em `pny/3qtr-top-right` | `v10-ponta-oposta-orto.png` |
| 9 | placa sempre de baixo, ato 0 sem ventiladores, cortes | **resolvido** no ato 0 e no a2.2: ventiladores à vista em a0.1 e a0.3, texto legível no a0.2, placa inteira no a0.2 e no a2.2. Sobra o logotipo de cabeça para baixo no a2.9 (N9) | `b-a0.1.png`, `b-a0.2.png`, `b-a0.3.png`, `b-a2.2.png` |
| 10 | laje de sombra no chão | **resolvido**. Nenhuma laje nos beats montados | `b-a0.1.png`, `b-a0.3.png`, `b-a7.5.png` |
| 11 | destaques na face escondida, caminhos | **resolvido**. Âmbar sobre conector, indutores e chip; ciano chega às portas e termina na memória da frente | `b-a2.9.png`, `b-a2.10.png`, `b-a2.11.png` |
| 12 | a2.10 sem "Ilustrativo" | **resolvido** | `b-a2.10.png` |
| 13 | haste branca e tracejados | **parcial**. No a2.4 ainda há um traço claro vertical, do pé do quadro até a caixa (o aro explodido visto de quina). Não aparece no a2.7 nem no a3.3 | `b-a2.4.png`, `z-a2.4-haste.png` |
| 14 | adaptador pequeno e de quina no a2.4 | **resolvido**. Maior e de frente para a câmera | `b-a2.4.png` |
| 15 | DisplayPort brancas | **resolvido**. Bocas pretas com contorno | `v09-ponta-bracket-orto.png`, `v21-bracket-3qtr-gn11.png` |
| 16 | cabo flat prateado | **parcial**. Âmbar no a2.6 e no a2.8; nas vistas rasantes do E6 o reflexo deixa o cabo bege-prateado (luminância 176 contra cerca de 55 em `gn-29`) | `b-a2.6.png`, `v32-e6-destaque-flex.png`, `v33-e7-verso-gn29.png` |
| 17 | aba do bracket curta; faltam marcas e etiquetas | **parcial**. A aba passou a 14,7 mm (corrigida). As marcas regulatórias (CE, UKCA, FCC, KC) e as três etiquetas de `gn-11` continuam ausentes: há só contornos em relevo | `v02-face-b-orto-pnyback.png`, `v21-bracket-3qtr-gn11.png`, `v09-ponta-bracket-orto.png` |
| 18 | dourado alaranjado | **resolvido**. Champanhe, como nos renders da PNY | `z30-logo-girado-180-face-b-para-cima.png`, `ref-pny-logo-zoom.png`, `v18-x-face-b-texto-perto.png` |
| 19 | bloco do logotipo | não procede (já marcado); nada mudou | |
| 20 | chips como placas claras, sem anel verde | **continua**. Memória da frente e package seguem cinza claro; o substrato verde não aparece no a2.7 nem no a3.3 | `b-a3.2.png`, `b-a3.3.png`, `b-a2.7.png` |
| 21 | adaptador longo, contatos baixos | **continua** (6,6 mm e 14,0 mm, tabela acima) | `v02-face-b-orto-pnyback.png` |
| 22 | README e folha de comparação | README **resolvido** (descreve o referencial novo). A tabela `REFS` do `lookdev.cjs` não foi reexecutada nesta passada | `harness/viewer/README.md` |
| 23 | linha do a1.1 cruza o ventilador 2 | **resolvido** | `b-a1.1.png` |
| 24 | a2.5 e a2.6 sem "Provável" | **resolvido** (os dois têm o selo). A âncora do a2.6 fica no vazio ao lado da mola | `b-a2.5.png`, `b-a2.6.png` |

## Achados novos

| # | Severidade | Peça | Vista e evidência | O que está errado |
|---|---|---|---|---|
| N1 | ajusta | `cooler.fan.1` e `.2` (nível A) | três quartos: `z06-ventilador2-cubo-interior.png` contra `ref-pny-3qtr-front-left-ventilador2.png`; `v16-cubo-perto-obliquo.png`; beats `b-a0.1.png`, `b-a0.3.png`, `b-a1.1.png`, `b-a7.5.png` | O cubo parece um cilindro alto que sobressai das pás, com cerca de 10 mm de parede lateral clara à vista. Nas referências (`pny/3qtr-front-left`, `gn-02`) o cubo é um disco quase rente às pás, de borda fina. Pelo GLB, o cubo vai de z 25,3 a 39,2 e as pás de 27,6 a 38,8: a raiz das pás fica baixa junto ao cubo e expõe a lateral. É a diferença de contorno mais visível nos planos de abertura. Na vista frontal o tampo também mostra dois aros desencontrados (`z01-cubo1.png`, `v16`) |
| N2 | ajusta | tom geral; `carcaca.tampa_x`, `ventilador.pa`, carcaça | `v06-3qtr-front-left.png` contra `pny/3qtr-front-left`; `cmp-v04-vs-pny-3qtr-back-right.png` | Toda a imagem puxa para o quente: R > G > B em pás e tampas (pá 63, 59, 56 contra a referência 33, 35, 38, que puxa para o frio). As tampas do X ficam marrom-escuras de frente. As laterais e a borda superior saem quase pretas, onde os renders mostram grafite médio, e o aro da face B e os braços do X saem prateados, onde os renders mostram grafite. As cores da tabela são neutras (`#383b3f`, `#0b0b0c`), então o desvio vem da luz ou dos tons, não do material |
| N3 | ajusta | `frame.shroud`, luva do túnel do conector | `v13-conector-como-pny-top-right.png`, `v14-conector-face-b-3qtr.png`, `v12-tunel-cima-3qtr.png`, `b-a1.4.png`, contra `pny/3qtr-top-right` e `pny/3qtr-back-right` | A parede interna do túnel acende como um triângulo cinza-claro abaixo do conector e vira o elemento mais claro da borda superior. Na referência a abertura é um retângulo preto limpo na ponta do painel, com a face 2 x 6 logo dentro. Escurecer o interior da luva, como a tabela já faz em outras aberturas |
| N4 | nota | `power.connector` | `v11-tunel-eixo-45.png`, `v13`, `b-a1.4.png` | De lado, as 12 cavidades leem como quadrados brancos. Na referência elas ficam cinza sobre o corpo preto. O ângulo de 45 graus do túnel não pode ser confirmado nem negado nas fotos desta placa: `gn-29` e `gn-13` são oblíquas. Na vista `pny/3qtr-top-right` o contorno da abertura do modelo não é o retângulo limpo da referência |
| N5 | ajusta (pendência conhecida, ver abaixo) | `cooler.heatpipes`, `cooler.fins.3`, chapa sob o ventilador 2 | `z-a0.1-ventilador2.png` (sem clarear), `z17-atras-ventilador2.png` | No plano de abertura (a0.1) dá para contar 4 ou 5 tubos cinza e uma chapa clara pelas pás do ventilador 2. Em `gn-02` só se veem aletas verticais finas atrás das pás |
| N6 | ajusta | storyboard a2.9 e a3.1 | `z-a2.9-cabecalho.png`, `b-a2.9.png`, `b-a3.1.png` | A geometria entra na faixa do cabeçalho: no a2.9, riscos claros (bordas da carcaça explodida) passam sob "Conceito" e "SEÇÃO 02"; no a3.1, a placa e as aletas preenchem o topo e "SM > Conceito" mal se lê. Também no a3.2 um risco claro atravessa a tela perto do topo |
| N7 | nota | `frame.face_b` | `v02-face-b-orto-pnyback.png` (quatro marcas pequenas perto dos cantos internos das grades), `v14-conector-face-b-3qtr.png` | Furos ou cabeças pequenas visíveis nas grades da face B; `pny/back` e `gn-08` não mostram nada ali |
| N8 | nota | grades da face B, de perto | `v31-texto-face-b-frontal-perto.png` | De frente e de perto, as nervuras saem onduladas e interrompidas. De longe some |
| N9 | nota | storyboard a2.9 | `b-a2.9.png` | O logotipo da borda superior ocupa o alto do quadro de cabeça para baixo (a câmera olha do lado dos ventiladores). A geometria está certa, mas a plateia lê "AIDIVn" |
| N10 | nota | logotipo | `v30-logo-frontal-perto.png` contra `ref-pny-logo-zoom.png` | O olho é um desenho simplificado (círculo com "C"), não a espiral da marca. Já declarado no README; registrado só para a decisão de deixar assim |

## Pendências conhecidas (só o estado)

- **Pilha de aletas central e tubos entre os ventiladores:** continua. Tubos e chapa visíveis pelo ventilador 2 no a0.1 (N5). Pelas grades em V do centro aparecem só aletas.
- **Face do conector talvez 3 mm mais funda:** continua, sem medida. No eixo do túnel (`v11`) a face fica visivelmente recuada dentro da moldura. Não medi a profundidade.
- **J3 em 128,1 contra cerca de 125:** não conferido visualmente (exigiria uma vista de E4 com régua); o contrato não mudou desde a primeira passada.
- **Adaptador PCIe contra o parafuso da mola, 0,78 mm:** continua registrada como pendência em `build/integration-report.md`, sobre o mesmo `card.glb` (sha256 bd75e85ba5aa) que o passe do Blender usou. Não aparece em nenhum beat.

## O que o auditor não verificou

A qualidade alta, a luz fria e a quente e a acumulação completa (32 ou 64 amostras); a imagem em movimento e o sentido de giro animado; o interior do cooler (sem referência desta placa); as vistas da ponta oposta e da borda dos contatos de frente (sem referência ortogonal: "sem referência"); a contagem de aletas; os 16 chips do verso e a disposição 5, 5, 4 e 2, que não mudaram de geometria e não foram recontados um a um nesta passada; os beats fora do corte do seminário além de a2.5 e a2.6; o mergulho t1.1; a medida exata da altura do cubo acima das pás na raiz (só os limites das caixas do GLB). As medidas em pixel valem para a perspectiva de uma câmera a 1350 mm (cerca de 3% entre as faces).
