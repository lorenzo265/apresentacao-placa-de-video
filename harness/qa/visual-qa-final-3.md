# Visual-QA final (terceira passada) da placa e do tour (2026-11-12)

- Autor: agente `visual-qa`, em contexto separado de quem modelou. Só reportou; não editou nada.
- **Processo: esta passada rodou em Sonnet 5.5 (tipo C), por decisão do autor (limite de uso do Opus), e não no Opus que a regra do projeto pede para crítica visual.** Julgamentos finos de tom e de beleza têm margem maior de erro que nas passadas em Opus.
- Objeto: `harness/dist/tour.html` (21 MB, abre por file://, GLB embutido de `harness/build/card_final.glb`), tema Keynote, qualidade média, `acumula=2` nos beats e `acumula=6` nas vistas livres, 1920 x 1080, deviceScaleFactor 1, render por software (SwiftShader).
- Capturas: `harness/dist/qa/final-3/` (não versionada). `b-<beat>.png` = os 28 beats do corte do seminário no instante `settle`; `v*` = vistas livres (modo `frame3d`); `o00` a `o180` = órbita da face A à face B; `s21_*`, `s213_*`, `s31_*`, `v21_*` = sequências de quadros (folhas `folha-a2.1.png`, `folha-a2.13-a3.1.png`, `folha-virada-a2.1.png`, `folha-orbita-A-B.png`); `cmp-face-b-vs-pny-back.png` e `z-*` = comparações e recortes (alguns clareados, marcados no nome).
- Referências usadas: `pny/front`, `pny/back`, `pny/3qtr-front-left`, `pny/3qtr-top-right`, `gn-11`. Sem referência: interior do cooler, a vitrine do chip de memória, o hero explodido (nenhuma foto desta placa em E8), diagramas (fora do escopo de forma).

## Veredito: aprovado com ressalvas

Nada bloqueia. A placa montada está bonita e fiel de forma; quase todos os achados antigos de geometria foram resolvidos. O que mais pesa na beleza: a vista explodida e a desmontagem são pequenas e escuras no quadro, o close do chip no a2.1 é escuro demais, as grades da face B saem pretas chapadas, e três beats (a2.1, a3.1, a3.6) têm geometria escura sob o cabeçalho.

## Lateralidade

**Não está espelhada.** Conferido em: face A ortogonal contra `pny/front` (`v01-face-a-orto.png`: balcão do bracket à esquerda, contatos embaixo em 14 a 43% do comprimento, pás no mesmo sentido); face B ortogonal girada 180 graus contra `pny/back` (`cmp-face-b-vs-pny-back.png`: contatos em cima, "RTX PRO 6000" no triângulo inferior, leitura correta); três quartos (`v03`, `v04`, `v06`) e a órbita (`folha-orbita-A-B.png`), onde o logotipo "nVIDIA" lê certo quando a borda superior fica para cima e o olho fica à esquerda do texto. Nenhuma folha põe faces diferentes lado a lado.

## Achados antigos

| # | Estado | Evidência |
|---|---|---|
| N1 cubo dos ventiladores | **resolvido**: disco rente às pás, borda fina | `v08-cubo-perto.png`, `v05-tunel-cima.png`, `z-a0.1-ventilador2-clareado2x.png`, `b-a0.1.png` |
| N2 tom quente | **resolvido em grande parte**: tom neutro a frio, tampas grafite sem marrom marcante. Resta o aro da face B prateado claro em `o120` (renders mostram grafite) | `folha-orbita-A-B.png`, `b-a7.5.png` |
| N3 parede do túnel clara | **resolvido**: boca retangular, interior preto, conector 2 x 6 dentro | `v05-tunel-cima.png`, `v04-3qtr-top-right.png` |
| N4 cavidades do conector | **nota, continua**: cavidades leem como quadrados cinza claros, sem referência melhor | `v05-tunel-cima.png` |
| N5 tubos e chapa atrás das pás | **resolvido**: só aletas verticais finas atrás das pás, como em `gn-02` | `z-a0.1-ventilador2-clareado2x.png`. Em `v08` ainda aparece uma tira com trilhas de placa atrás das pás do ventilador 1 (ver achado 9) |
| N6 geometria sob o cabeçalho | **melhorou, não resolvido**: sem os riscos claros, mas ver achado 4 | `b-a3.1.png`, `b-a3.6.png`, `b-a2.1.png` |
| N8 nervuras das grades B | **parcial**: de três quartos as nervuras leem (`v06`); de frente ficam preto chapado, sem nervura (achado 5) | `v02-face-b-orto.png`, `v06-face-b-3qtr.png` |
| N9 logotipo de cabeça para baixo no a2.9 | **sem cobertura**: a2.9 saiu do corte do seminário. Nas vistas livres o logotipo só lê certo com a borda para cima (`o120`) | |
| 13 haste branca no a2.4 | **sem cobertura** (a2.4 fora do corte) | |
| 16 cabo flat prateado | **resolvido**: cobre/marrom na desmontagem | `s213_2`, `folha-a2.13-a3.1.png`, `b-a2.13.png` |
| 17 marcas e etiquetas do bracket | **resolvido**: QR, etiqueta, texto, marcas CE, UKCA, FCC, KC, 4 parafusos, 4 DisplayPort pretas | `v07-bracket.png` contra `gn-11` |
| 20 chips sem anel do substrato | **parcial**: o package da GPU ganhou moldura clara e substrato (`b-a3.6.png`); os chips de memória seguem lajes cinza claras lisas (achado 6) | `b-a3.1.png`, `b-a3.6.png` |
| 21 adaptador PCIe longo | **resolvido**: ponta e altura dos contatos batem com `pny/back` (cerca de 0,478 contra 0,471 do comprimento; 15 mm contra 15 mm) | `cmp-face-b-vs-pny-back.png` |

## Achados novos

| # | Severidade | Beat ou vista | O que está errado | Captura |
|---|---|---|---|---|
| 1 | ajusta | a2.13 (herói) e a2.1 (desmontagem) | A vista explodida ocupa só cerca de metade da largura e está cercada de vazio; as peças (aro, tampas, adaptador, placas, blocos de aletas) são pequenas e muito escuras sobre o fundo. Legível, mas não impressiona. Os dois blocos de aletas (esquerda e direita) são quase pretos. Ver também o hero de 4 ou 5 peças soltas sem rótulo (mudo por desenho) | `b-a2.13.png`, `folha-a2.1.png` |
| 2 | ajusta | a2.13 | A grade da face B solta (placa clara à direita da carcaça) é a peça mais brilhante da cena, bem acima do resto, e rouba o foco. A carcaça de fato se solta e a grade da face B sai, com os dois ventiladores levantados, a câmara de vapor e os blocos de aletas à vista | `b-a2.13.png`, `s213_3` a `s213_5` |
| 3 | ajusta | a2.1, close do chip (settle e quadros finais) | Escuro demais: luminância média 24 de 255 e 63% dos pixels abaixo de 20. O chip e a pasta leem, mas o PCB em volta e os chips de memória viram preto; só dá para ver trilhas no canto esquerdo. Clareado 2,2x em `z-a2.1-chip-clareado2x.png` mostra que há detalhe a recuperar | `b-a2.1.png`, `z-a2.1-chip-clareado2x.png` |
| 4 | ajusta | a2.1, a3.1, a3.6 | Geometria escura sob o cabeçalho: no a3.1 parafusos e arestas do cooler e do PCB cruzam a faixa do topo e "SM > Conceito" mal se lê; no a3.6 e no a2.1 há blocos pretos encostados no topo. Sem riscos claros como na passada anterior | `b-a3.1.png`, `b-a3.6.png`, `b-a2.1.png` |
| 5 | ajusta | face B, vista de frente | As duas grades saem pretas chapadas, sem nervuras, enquanto `pny/back` mostra nervuras finas e cinza grafite. De três quartos funciona. Também as duas marcas pequenas junto à grade (N7) continuam | `v02-face-b-orto.png`, `cmp-face-b-vs-pny-back.png`, `z-face-b-clareado3x.png` |
| 6 | ajusta | a3.1 (vitrine), a3.6 | O chip de memória da vitrine é uma laje cinza lisa, sem marcação, substrato ou esferas; os chips no PCB do a3.1 e do a3.6 são as peças mais claras da placa, mais claras que o PCB e destoam das fotos (`gn-29`, `gn-30`, chips escuros). O selo "Ilustrativo: peça fora da posição" aparece, legível, e a linha termina no centro da peça certa | `b-a3.1.png`, `b-a3.6.png` |
| 7 | nota | a1.1 | A linha de chamada sai da caixa à direita e atravessa a tampa do X e o aro da placa até o cubo do ventilador 1; termina na peça certa, mas cruza o corpo da placa | `b-a1.1.png` |
| 8 | nota | a4.2, a5.9, t1.1, t2.1 | (a) a4.2: o rodapé ilustrativo corta o item "Chip completo: 192 SMs" da lista à esquerda. (b) t1.1: o ponto da âncora cai sobre o texto "32 bits" do MC da direita. (c) a5.9: sobras de nós cortados na borda esquerda. (d) t2.1: o SM inteiro fica esmaecido (poucos blocos acesos) e a âncora cai na borda, não em um nó; textos pequenos (Tex, 4, 128) ilegíveis. Os diagramas não são o objeto principal desta passada | `b-a4.2.png`, `b-t1.1.png`, `b-a5.9.png`, `b-t2.1.png`, `t21-tarde.png` |
| 9 | nota | v08 | Atrás das pás do ventilador 1, em vista oblíqua, aparece uma tira estreita com trilhas de placa e marcas brancas (PCB ou flex visto pelas pás); em `gn-02` só se veem aletas. Também o cubo mostra um anel duplo fino na borda do tampo | `v08-cubo-perto.png` |
| 10 | nota | fundo e luz | O fundo continua escuro com vinheta (centro cinza médio, bordas quase pretas). O pedido de "fundo mais claro" foi atendido só no centro; as laterais pretas da placa perdem contorno nas bordas do quadro (`b-a7.5.png`, `v03`). O contorno de Fresnel ajuda. Decisão de gosto | `b-a7.5.png`, `v01-face-a-orto.png` |
| 11 | nota | logotipo | O olho continua um círculo com "C" simplificado (N10 já declarado). A linha vertical fina junto ao logotipo (costura de textura) aparece em `v05` | `v05-tunel-cima.png` |
| 12 | nota | captura e desempenho | Nenhum beat travou: os 28 beats do corte foram capturados em sequência por `seek`, inclusive depois do a3.1 (28,7 s de render por software com acumula=2; a0.1 24 s, a1.1 20 s, a7.5 14,5 s; demais 1 a 12 s). Com a acumulação padrão, a primeira captura estoura os 30 s padrão do Playwright (nada trava, só demora). Em modo ao vivo sob SwiftShader o relógio avançou cerca de 0,01 s por segundo (setas e play não puderam ser avaliados em fluidez); isso é limite do render por software, não prova de defeito, mas **fluidez real e ritmo da câmera em GPU ficam sem verificação** | `b-a3.6.png` em diante |

## Pontos específicos

- **Tampas do X nas viradas da face A para a B:** não estouram. Órbita de 0 a 180 graus em passos de 30 (`folha-orbita-A-B.png`): as tampas ficam de preto a grafite com reflexo em degradê, sem área branca; face B em `v06` também. Na desmontagem do a2.1 as tampas aparecem soltas e escuras (`folha-a2.1.png`). Não verifiquei a viragem em movimento ao vivo.
- **Close do chip no a2.1:** escuro demais (achado 3).
- **Desmontagem em movimento (a2.1, 12 quadros):** o bracket, o aro, as tampas, o adaptador, a placa que cobre o PCB, o cabo flat e o PCB saem em sequência e escalonados; os parafusos pequenos aparecem soltos. A carcaça **não** se solta no a2.1 (fica montada até o E7, como o plano diz). No a2.13 ela se solta: a carcaça de fixação com os dois furos dos ventiladores, os ventiladores, a grade da face B e os dois blocos de aletas separam-se (`s213_3` a `s213_5`). A grade da face B sai, sim. Toda peça visível parece se soltar. Legibilidade da vista final: boa; beleza: ver achados 1 e 2.
- **Espelhamento:** nenhum.

## Beat a beat (corte do seminário, 28 beats)

Placa, enquadramento, caixa de texto, linha e selos conferidos em `b-<beat>.png`:

- a0.1, a1.1, a7.5 (placa montada): placa legível, ventiladores à vista, caixa sem cobrir a peça. a1.1 ver achado 7.
- a2.1: desmontagem e chip; ver achados 3 e 4. Linha termina na pasta/die (certo). Selos Confirmado e Derivado.
- a2.13: herói mudo, selos Confirmado, Provável e Ilustrativo, caixa pequena sem cobrir; achados 1 e 2.
- a3.1 e a3.6: achados 4 e 6. Linha do a3.6 termina no package (certo); a do a3.1 no centro da laje de vitrine (certo).
- t1.1, a4.2, a4.4, t2.1, a5.* (a5.5, a5.1, a5.2, a5.16, a5.6, a5.7, a5.8, a5.9, a5.10, a5.12, a5.13, a5.14), a6.1 a a6.4, a7.4: diagramas. Vistos individualmente: a4.2, a4.4, t1.1, t2.1, a5.5, a5.1, a5.9, a6.4, a7.4; os outros só abertos de relance sem leitura de texto linha a linha. Selos de procedência presentes onde vistos.

## O que o auditor não verificou

Qualidade alta e a acumulação completa; fluidez, ritmo e sentido de giro da câmera em movimento ao vivo e com GPU; a viragem A para B durante o tour (só em órbita por posições); o mergulho em movimento; interior do cooler e hero explodido (sem referência); texto dos diagramas a5.2, a5.16, a5.6, a5.7, a5.8, a5.10, a5.12, a5.13, a5.14, a6.1 a a6.3 (lidos de relance); beats fora do corte (a2.4, a2.9 e outros).
