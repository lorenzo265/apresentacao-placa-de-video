# Visual-QA: auditoria da placa 3D antes do gate do animatic (2026-11-11)

- Autor: agente `visual-qa` (Opus), em contexto separado de quem modelou. Só reportou; não editou o repositório.
- Escopo: `build/card_final.glb` no viewer (tema Keynote), os beats 3D do corte do seminário, contra os renders oficiais (`pny/`), as fotos reais (`storagereview/`), o PCB (`chiphell/`, `sabareesh/`), o teardown (`gn/`) e a placa irmã (`rtx5090/`).
- Imagens e scripts de trabalho: pasta `vq-final/` do scratchpad da sessão (não versionada).

## Veredito: reprovado para o gate
Um único achado bloqueia: o conector de energia não aparece de verdade, nem no beat que fala dele (a1.4) nem pela abertura da carcaça. Corrigido isso, a placa sobe para "aprovado com ressalvas". Lado, orientação, proporção e contagens estão certos.

**Lateralidade: não está espelhada.** Nas quatro vistas equivalentes a `pny/front`, `pny/back`, `pny/3qtr-top-right` e `pny/3qtr-back-right`, bracket, contatos, conector, canal da borda superior, logotipo e texto "RTX PRO 6000" ficam do lado certo e com a orientação certa. O alarme de espelhamento veio de uma folha de comparação que punha lado a lado vistas não equivalentes (a face oposta vista de baixo contra a face dos ventiladores vista de cima). O README do viewer ainda descrevia o referencial antigo.

**Forma, contra os renders quase ortogonais (mm):** altura da carcaça sobre comprimento 0,4045 contra 0,404; ventiladores em x 61,0 e 242,9 contra cerca de 62 e 244; diâmetro das pás 112 contra 115 ± 6; 7 pás com o sentido certo; cruzamento do X a cerca de 1 mm nas duas faces; contatos PCIe de 51,8 a 132,7 contra 48,8 a 130,2; ponta do adaptador 5,6 mm mais longa; conector a cerca de 67% do comprimento (o teardown dá de 55% a 70%).

**Interior (estágio E7):** correto contra as fotos: 16 chips no verso em 5, 5, 4 e 2; 16 na frente; conector no canto chanfrado a 45 graus; indutores nas bordas certas; mola em X com 4 parafusos.

## Achados
| # | Severidade | Onde | O que está errado | Quem corrige |
|---|---|---|---|---|
| 1 | bloqueia | conector de energia, abertura da carcaça, beat a1.4 | Pela abertura não se vê a face de encaixe 2 x 6: aparecem a lateral do corpo, componentes e o PCB. Nas fotos a face preta 2 x 6 fica rente à abertura. O a1.4 enquadra a face oposta por baixo, e o conector vira um risco | modelador (I/O e carcaça), assembly (giro de 45 graus contra a abertura), storyboard (câmera) |
| 2 | ajusta | grades da face oposta | Parecem transparentes: aparecem faixas, blocos e pontos claros do interior. Na foto a grade é opaca, com nervuras verticais uniformes | modelador (carcaça), lookdev |
| 3 | ajusta | face dos ventiladores, lados do X e atrás do ventilador 2 | Aparecem 5 tubos de calor brilhantes e uma chapa clara atrás das pás | modelador (cooler e carcaça), lookdev |
| 4 | ajusta | triângulos do X, nas duas faces | Foscos e cinza; na foto são preto espelhado. Braços do X e aro claros demais | lookdev |
| 5 | ajusta | pás dos ventiladores | Corda estreita: metade do disco é vão. Na foto as pás quase se sobrepõem | modelador (ventilador) |
| 6 | ajusta | cubos dos ventiladores | Cromo espelhado com estrias de alto contraste; na foto, cinza fosco torneado suave | lookdev |
| 7 | ajusta | tampas do X na face dos ventiladores | Linhas claras finas: aletas da pilha central vazando pela chapa | modelador, integrador |
| 8 | ajusta | ponta oposta ao bracket | Contornos das pontas dos tubos de calor aparecem na chapa; a referência mostra só 2 furos pequenos | modelador (cooler e carcaça) |
| 9 | ajusta | a0.1 a a0.4, a7.5, a1.3, a1.4, a2.1, a2.2 | A placa aparece sempre de baixo, de cabeça para baixo; no a0.2 o "RTX PRO 6000" fica ilegível; o ato 0 não mostra os ventiladores; placa cortada pela borda no a0.2 e no a2.2 | storyboard |
| 10 | ajusta | sombra do chão | Laje escura de borda dura atrás ou acima da placa, como um objeto fantasma | lookdev |
| 11 | ajusta | a2.9, a2.10, a3.2 | Destaques na face escondida; caminho âmbar sobre a memória do verso; caminho ciano não chega às portas | storyboard |
| 12 | ajusta | selo do a2.10 | `io.board` (forma ilustrativa) em destaque sem o selo "Ilustrativo" | storyboard |
| 13 | ajusta | a2.7, a3.3, a2.2, a2.4 | Haste branca vertical cruza o quadro (provável peça explodida vista de quina); tracejados na borda esquerda | storyboard |
| 14 | ajusta | a2.4 | Adaptador PCIe pequeno e de quina | storyboard |
| 15 | ajusta | saídas DisplayPort | Brancas e estouradas; na foto são aberturas pretas | lookdev |
| 16 | ajusta | cabo flat | Prata brilhante; na foto, marrom-âmbar com reforço preto | lookdev |
| 17 | ajusta | bracket | A aba termina 11,5 mm além dos contatos; os renders dão de 15,0 a 16,7. Faltam marcas regulatórias e etiquetas | modelador (I/O) |
| 18 | nota | logotipo e texto | Dourado alaranjado; os renders dão champanhe e as fotos, cinza-prata. Escolher a referência | lookdev |
| 19 | nota | logotipo | O olho fica dentro de um bloco dourado retangular que não existe no real | modelador (carcaça) |
| 20 | nota | memória e package | Chips como placas metálicas claras; falta o anel verde do substrato | lookdev |
| 21 | nota | contatos e adaptador | Adaptador 5,6 mm mais longo; contatos 13,9 mm abaixo da carcaça contra 11,4 a 12,8 | assembly |
| 22 | nota | README do viewer, ferramenta de comparação | Referencial antigo no README; folha de referência com vistas não equivalentes | viewer, lookdev |
| 23 | nota | a1.1 | A linha de chamada cruza o ventilador 2 | storyboard |
| 24 | nota | a2.5 e a2.6, fora do corte do seminário | Âncora em fixador e cabos com forma `inferred` sem o selo "Provável" | storyboard |

Selos no corte do seminário: "Provável" aparece no a2.8, a2.9, a2.10, a2.11, a3.3 e a7.5, e "Ilustrativo" no a2.7. Falha só o a2.10.

## O que o auditor não verificou
O interior do cooler (sem referência desta placa); a ponta oposta e a borda dos contatos sem referência ortogonal; a contagem de aletas; o sentido de giro em animação; a qualidade com acumulação completa (renders com 4 amostras), em movimento, na qualidade alta e com luz fria ou quente; os beats fora do corte do seminário. A foto `chiphell/pcb-b.jpg` parece espelhada em relação às outras; não pesa contra o modelo.
