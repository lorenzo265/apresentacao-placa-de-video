# Viewer do tour

Página que executa o tour guiado por `story/storyboard.json`: placa 3D (níveis 0 e 1) e diagramas SVG (níveis 2 a 4). Não tem conteúdo embutido: textos, rótulos e posições vêm dos JSON. Versões fixadas em `package.json`: three 0.170.0, gsap 3.15.1, camera-controls 3.1.2, vite 8.3.7, fontes por `@fontsource/inter` e `@fontsource/jetbrains-mono` 5.3.0.

## Rodar

```
cd harness/viewer
npm install
npm run dev          # desenvolvimento (roda o sync antes)
npm run build        # gera dist/ (roda o sync antes)
npm run preview      # serve o dist/ para ver o build
```

O `scripts/sync-data.mjs` copia para `public/data/` (não versionado) `story/storyboard.json`, `content/pt-BR/beats.json`, `diagrams/<id>.json` (ignora `README.md`, scripts e arquivos que não sejam diagrama; se o storyboard for o de exemplo, usa também os diagramas de exemplo, para o conjunto casar; `SYNC_REAL_DIAGRAMS=1` força os reais), `build/card.glb` e `design/measurements.csv` (vira `measurements.json`). O que faltar é trocado pelo exemplo de `schemas/examples/`; `data/manifest.json` diz o que é `real` e o que é `examples`. Depois do build não precisa de internet. Precisa de um servidor HTTP local (qualquer um): abrir `index.html` por `file://` não funciona, porque o navegador bloqueia módulos e `fetch`.

Parâmetros da URL: `?cut=seminario` (padrão `completo`), `?capture=1` (sem controles, palco fixo de 1920 x 1080, sem laço de animação), `?beat=<id>` (começa no fim da chamada do beat), `?acumula=N` (quadros acumulados com a cena parada no modo realista; 0 desliga; ver abaixo).

Temas de estilo: `?tema=keynote|estudio|blueprint` (o autor escolheu o Keynote em 2026-11-10; ele é o padrão do arquivo único, ver abaixo). No servidor de desenvolvimento, sem `?tema` o viewer é o de sempre (conferido quadro a quadro contra as capturas anteriores). `?leve=1` desliga os efeitos caros do tema (desfoque da caixa, brilho do nó-alvo, halos). Parâmetros em `src/temas.js` (fundo, luzes, materiais, arestas, sombra de contato, raio de canto, fluxos), estilo em `src/temas.css` (só regras sob `:root[data-tema]`), cotas da placa montada no tema blueprint em `src/cotas.js` (só medidas auditadas de `measurements.json`). Capturas e folhas de contato: `node harness/tools/estilo.cjs` (grava `harness/dist/estilo/`); quadros por segundo ao vivo: `node harness/tools/estilo.cjs --perf`. Os dois smokes aceitam `--tema <nome>`.

Teclado: setas (beat anterior e próximo), espaço (tocar e pausar), `N` (notas do apresentador: `speaker`, `fala` e beats `draft` e `blocked`). Em beat 3D com o tour pausado dá para orbitar com o mouse; ao avançar, a câmera volta ao storyboard.

## Testar e capturar

```
node harness/tools/smoke.cjs [--cut completo] [--acumula 2]   # percorre todos os beats; salva harness/dist/frames/<id>.png
node harness/tools/capture.cjs --cut completo [--fps 30] [--beats a4.2,a5.5] [--out harness/dist]
```

O smoke abre com `acumula=2` (padrão do teste, para caber no tempo com render por software; `--acumula N` troca) e confere, por beat: console sem erro, `headline` igual ao de `beats.json`, limites de palavras e regra do tempo de leitura, caption sem estouro e com corpo de 28 px, caixa dentro da tela, âncora na tela e fora da caixa, foco inteiro na tela e fora da caixa, e determinismo (mesmo instante, com um `seek` no meio, dá PNG idêntico). A captura grava `harness/dist/capture/<corte>/<beat>/%05d.png`, pula o beat se o hash (beat, texto, diagramas, GLB, bundle) não mudou e monta `harness/dist/tour-<corte>.mp4`.

```
node harness/tools/smoke.cjs --fixture3d       # beats 3D reais: usa schemas/examples/fixture3d.*.example.json
```

Com `--fixture3d` o smoke serve uma cópia do `dist` com o storyboard de exemplo de beats 3D (montada, E1, E4, E7 e um mergulho para diagrama) e o GLB real, e confere por beat 3D: âncora resolvida e dentro da tela, caixa fora da âncora, nível de explosão no fim do beat igual ao pedido, e determinismo com `seek` no meio da entrada (onde a explosão está a meio caminho).

Polimento (acumulação, caminhos, mergulho):

```
node harness/tools/determinismo-polimento.cjs [--acumula 8]     # acumulação num beat parado, mergulho t1.1 a meio, caminho a2.10 a meio
node harness/tools/polimento.cjs [--quadros a0.2@settle,t1.1@0.5,a2.9@s+3] [--extra acumula=0] [--sufixo x]
```

O `polimento.cjs` grava em `harness/dist/polimento/` e imprime o tempo de cada seek; o instante é `settle`, `fim`, `s+N` (N s depois do settle) ou uma fração da entrada do beat.

## Enquadrar a câmera 3D (`frame3d.cjs`)

```
node harness/tools/frame3d.cjs --pos 520,-480,480 --target 152,68,80 --fov 35 \
  --explode E7 --part gpu.package --anchor anchor.gpu.package.1 --box left-center [--out nome] [--no-build]
```

Grava `harness/dist/frames3d/<nome>.png` (1920 x 1080) em cerca de 4 s (um quadro, sem o tour) e imprime a posição da âncora na tela, se está dentro do quadro e se a caixa a cobre (código de saída 1 em caso de âncora fora, caixa cobrindo ou âncora inexistente). `--explode` é `assembled` ou `E1` a `E8`; `--part` esmaece o resto; `--anchor` com `--box` desenha a linha de chamada e uma caixa de exemplo (`left|right-top|center|bottom`). Os valores de `--pos` e `--target` são os mesmos de `camera.pos` e `camera.target` do storyboard.

Referencial: mm, Z para cima, origem no canto `envelope_min` do CAD (o mesmo do storyboard). O GLB está em metros e Y para cima; o viewer converte.

| Eixo | Faixa (mm) | O que é |
|---|---|---|
| x | 0 a 304,8 | comprimento; o espelho de E/S fica em x = 0 (de -0,9 a 0) |
| y | 0 a 137,16 | altura da placa |
| z | 0 a 40 | espessura (dois slots) |

Referencial corrigido em 2026-11-10 (`harness/ARCHITECTURE.md`, seção 7.6): z vai da face B para a face A. A face B (grades e X com "RTX PRO 6000", `frame.face_b`, `frame.rim`) fica em z = 0 (de 0 a 3); a face A dos ventiladores (`cooler.fan.*`) em z alto, perto de 40 (pás e cubo de cerca de 25 a 39). A placa de circuito fica entre elas, perto da face B (z de 6 a 8). O desmonte sai pela face B: os estágios E2 a E7 afastam as peças para z negativo (no E7, a placa de circuito anda 40 mm para -z), e o E8 afasta os ventiladores para z alto (+40). Centros dos ventiladores: x = 61 e x = 244, y = 74,2. Para ver os ventiladores, a câmera tem de estar em z alto (acima de 40); com z negativo a tela mostra a face B. Vista de +z, a placa aparece como em `pny/front` (bracket à esquerda, contatos embaixo); vista de -z com os contatos para cima, como em `pny/back`. Câmera de partida: `--pos 520,-380,260 --target 152,68,20`.

## Arquivo único para apresentar

```
cd harness/viewer && npm run build:single        # gera harness/dist/tour.html
node harness/tools/smoke-single.cjs [--cut seminario] [--no-build]
```

`harness/dist/tour.html` leva código, estilos, fontes e dados embutidos. Abre no tema Keynote e na qualidade média com escolha automática (padrão gravado pelo `build-single.mjs` em `window.__TOUR_PADRAO__`); a URL ainda manda: `?tema=estudio`, `?tema=nenhum` (visual sem tema), `?qualidade=alta`. Abre com dois cliques, sem servidor e sem internet. Teclas: seta para a direita e para a esquerda, espaço, `N` para as notas. O corte se troca no seletor da barra ou com `?cut=seminario` no fim do endereço. O `smoke-single` abre o arquivo por `file://` com a rede desligada, confere que abriu no tema Keynote (ou no pedido por `--tema`; `--tema nenhum` para o visual sem tema), que nada é pedido de fora, que as fontes carregam, que a seta leva a cada beat e que o título na tela é o de `beats.json`. Se `harness/build/card.glb` existir (gerado por `harness/parts/integrate.py`; ou o `card_final.glb` do passo do Blender, quando for do `card.glb` atual), ele vai embutido em base64 e o teste confere que carregou e que as peças respondem pelo id do assembly. O arquivo único só aceita GLB sem compressão Draco (meshopt pode). Sem GLB, o 3D é o marcador desenhado pelo próprio viewer.

## Modo realista da placa (tema Keynote, `src/lookdev.js`)

No tema Keynote a placa não tem contorno nem halo: o verde de acento fica na interface, nos diagramas, no destaque dos diagramas e na linha de chamada. A imagem da placa sai de `src/lookdev.js`, com parâmetros em `src/temas.js` (`TEMAS.keynote.cena.realista`) e materiais em `src/materials.json`.

- **Materiais** (`src/materials.json`): cada malha recebe um material da tabela, nesta ordem: nome do material no GLB (só os listados em `materiais_glb`, que são os slots do passo do Blender), id do nó ou de um ancestral (inclui `instance_of`), padrão de nome (regex), grupo (`extras.group`) e o padrão (`plastico.preto`). Cores em sRGB, `metal` e `rug` de 0 a 1, e uma `nota` com o material real e as referências usadas. Texturas procedurais (grão de metal jateado, cubo torneado com anisotropia concêntrica, aletas, máscara de solda com trilhas e serigrafia, capacitores, contatos PCIe, package com moldura e anel do substrato, abertura de conector com interior escuro, cabo flat com reforço nas pontas) são geradas no carregamento, com semente fixa, e usam o atributo `uv2` (projeção em caixa, em mm, plana na caixa envolvente da malha, ou `cavidade`: casca sobre a caixa envolvente contra faces de dentro, com oclusão procedural no interior). Medidas citadas pela tabela (`{"medida": ...}`) vêm de `measurements.json`. Malha sem normais ganha normais planas. Se o GLB trouxer mapas próprios (passo do Blender), eles valem canal a canal: cor, normal, rugosidade e metal do GLB substituem os da textura procedural, e o canal que o GLB não traz continua procedural (a peça que só ganhou oclusão assada mantém o grão da tabela; a carcaça com cor, normal e oclusão assadas mantém a rugosidade com grão). A oclusão do GLB (`aoMap`, na UV 0) vale com a força `ao` do material (padrão 1) na luz do ambiente e, com `micro_sombra` (0 a 1), também na luz direta rasante (micro-sombra no estilo da HDRP: `sat(|N.L| + 2 ao² - 1)`), porque o mapa de sombra não resolve frestas de décimos de milímetro; `env` multiplica a luz do ambiente do material. No destaque, o recorte de luz (Fresnel) é multiplicado por ao³: as paredes rasantes dentro das frestas não acendem, só o contorno. `interior` (0 a 1) marca as peças de dentro da carcaça (cooler, placa de circuito, chips, cabos): com a placa montada, a luz delas cai para essa fração, porque só a luz principal faz sombra e o ambiente não sabe da carcaça (sem isso o interior acende pelas grades e por trás das pás); volta a 1 conforme o desmonte abre a carcaça (`interior_aberto`, níveis de explosão). Verniz (`verniz`, só na qualidade média e alta) com `especular_base: 0` faz laca sob verniz: o reflexo é só o do verniz, nítido (tampas do X). `window.__cena.materiais()` lista malha, material e o motivo da escolha.
- **Estúdio**: ambiente pré-filtrado (PMREM) feito de um HDR de estúdio escurecido mais cinco caixas de luz (a de cima e ao fundo com degradê na largura e quatro faixas de borda nítida na altura: nas faces planas o reflexo lê como foto de produto e, nas tampas do X, que são espelho preto, ganha bordas em vez de virar um cinza chapado; e uma larga e fraca no zênite, para o reflexo largo e escuro das tampas vistas de frente), e três luzes diretas (principal com sombra, preenchimento frio, recorte). O estúdio acompanha a câmera como numa mesa giratória: gira com o azimute dela e, quando a câmera passa para a outra face da placa (z abaixo do meio da espessura, faixa de `virada` mm), vira de lado de forma contínua. Assim a face vista sempre recebe a luz principal, nos beats que olham os ventiladores e nos que olham a face oposta. É função só da pose da câmera: determinístico na captura.
- **Chão**: invisível, só recebe a sombra da luz principal e uma sombra de contato (núcleo justo e penumbra larga, desenhados uma vez). Só aparece com a câmera do lado dos ventiladores, como a placa deitada sobre uma mesa vista de cima: do lado da face oposta o chão viraria um teto atrás da placa e a sombra, uma laje solta no fundo preto. Some também com a câmera rasante ao plano da placa (elevação entre `chao.elev_min` e `chao.elev_cheia` graus, padrão 12 e 28: a sombra se descolaria da placa), durante a virada e com a explosão (as peças atravessariam o chão).
- **Destaque**: nada fica translúcido. As peças fora do destaque escurecem e perdem a cor (`apaga`); a destacada ganha um recorte de luz fino (Fresnel, `realce`), só quando alguma peça de fato escurece.
- **Tons e efeitos**: AgX com exposição 1,0; pós-processamento próprio (cena em meia precisão com MSAA, oclusão de ambiente GTAO na alta, profundidade de campo com foco na distância até o alvo da câmera do beat, pontilhado fixo contra faixas). O canal alfa é preservado: o fundo do tema continua sendo o canvas 2D sob a cena.
- **Acumulação de quadros** (média e alta): com a cena parada, cada quadro novo é mais uma amostra da mesma imagem, com deslocamento de subpixel (filtro em tenda de 1 px, sequência de Halton), a luz principal tratada como luz de área (um disco de 5 graus: sombra com penumbra) e a espiral da profundidade de campo girada; a tela mostra a média (linear, já com tons, em meia precisão; a mistura usa a cor constante do blend com peso 1/(k+1), sem cópia de ida e volta). Some o moiré das grades, as bordas ficam limpas e a sombra suave. A amostra 0 é o quadro normal, então durante as transições nada muda e nada custa a mais além de uma passada de cópia. Uma assinatura do estado (câmera, explosão, destaque, afastamento do mergulho, qualidade) diz se algo se mexeu; mexeu, a média recomeça. Ao vivo, uma amostra por quadro até 32 (média) ou 64 (alta), cerca de meio segundo a 60 qps; convergida, a cena 3D não é redesenhada (o canvas guarda a imagem) e a GPU fica livre. Na captura, o seek de um instante parado (depois da entrada do beat) desenha de uma vez as amostras que faltam, na mesma sequência fixa: o mesmo instante dá sempre o mesmo PNG, chegando de onde for. `?acumula=N` troca o número (0 desliga). Parâmetros em `TEMAS.keynote.cena.realista.acumula` (`filtro_px`, `luz_graus`). A troca automática de qualidade só mede quadros desenhados em seguida (a pausa depois da média não conta como lentidão).

Parâmetros da URL: `?qualidade=alta|media|baixa` e `?luz=fria|quente` (conferência de material em luz de 7500 K e de 3000 K).

| Qualidade | Sombra | Pós | AO | Profundidade de campo | Resolução máx. | Texturas | Materiais | Acumulação parada |
|---|---|---|---|---|---|---|---|---|
| baixa | só a de contato | não (antialias do canvas) | não | não | 1x | 256 px | Standard | não |
| media (padrão) | mapa 2048, PCF suave | MSAA 4x, meia precisão | não | 12 amostras | 1,25x | 512 px | Physical onde há anisotropia ou verniz | 32 quadros |
| alta | mapa 4096 | MSAA 4x | GTAO | 24 amostras | 2x | 1024 px | idem | 64 quadros |

Sem `?qualidade`, o viewer começa na média e mede os 60 quadros depois dos 20 primeiros ao vivo: abaixo de 28 quadros por segundo, cai para a baixa (uma vez, nunca no modo de captura). Medição: `node harness/tools/lookdev.cjs --qualidades baixa,media,alta --tempo` mede o tempo de desenho por quadro, esperando o quadro terminar (grava `harness/dist/lookdev/tempos.json`); `node harness/tools/estilo.cjs --perf --qualidades baixa,media,alta` mede quadros por segundo ao vivo, mas com render por software (SwiftShader, abaixo de 1 qps) o número vira ruído: use-o só numa máquina com GPU. Em 2026-11-11, no SwiftShader, a média custou cerca de 1,6 vez a baixa e a alta de 2,9 a 3,8 vezes. Quadros do lookdev: `node harness/tools/lookdev.cjs [--qualidades media,alta] [--luzes neutra,fria,quente]` grava `harness/dist/lookdev/<qualidade>[-<luz>]/<beat>.png`, a folha `folha.png` e `referencia.png` (cada beat ao lado da referência da mesma face e de ângulo parecido, pela tabela `REFS` do script; referências de terceiros, só locais). `--acumula N` troca o número de amostras, `--saida pasta` a pasta de saída e `--so-folha` refaz as duas folhas com os quadros que já estão na pasta (para juntar beats capturados em cortes diferentes).

**Ambiente HDR**: "Studio Small 08", de Sergej Majboroda, Poly Haven (https://polyhaven.com/a/studio_small_08), licença CC0. Baixado uma vez (arquivo de 1k), reduzido a 256 x 128 e escurecido fora das luzes por `scripts/ambiente-hdr.py`; o resultado vai embutido em `src/ambiente-hdr.js` (171 kB em base64). Nada é baixado em tempo de execução.

## Contrato do passo do Blender

O passo do Blender (ARCHITECTURE.md, seção 5.2) recebe o GLB ou o STEP da peça e devolve um GLB que casa com estes materiais. O `integrator` confere o envelope depois.

1. **Nós e dados**: nomes dos nós iguais aos ids do assembly; `extras` intactos (`group`, `stage`, `explode_cad`, `instance_of`, procedência); metros, Y para cima, origem no `envelope_min`; nenhuma dimensão muda (chanfro só dentro da tolerância da linha do CSV).
2. **Nomes de material**: iguais aos ids de `materiais` em `src/materials.json` (por exemplo `carcaca.anodizado`, `carcaca.tampa_x`, `carcaca.grade`, `carcaca.logo`, `ventilador.pa`, `ventilador.cubo`, `aletas.pretas`, `pcb.mascara`, `pcb.contatos_pcie`, `chip.package`, `chip.epoxi`, `cobre.niquelado`). Uma peça com acabamentos diferentes usa um slot por acabamento (vira uma primitiva por material no GLB). Nome novo de material entra primeiro em `materiais_glb` e em `materiais`.
3. **UV**: `TEXCOORD_0` única, sem sobreposição, para os mapas assados, com margem de 8 px entre ilhas. Densidade: 6 a 8 px por mm nas peças de fidelidade A que a câmera vê de perto (carcaça, tampas do X, cubos, package, adaptador PCIe), 2 a 4 px por mm no resto. O viewer usa `uv2` para o grão procedural; não exporte `TEXCOORD_2`.
4. **Mapas por peça** (glTF padrão, sem extensão nova): `baseColorTexture` (sRGB), `metallicRoughnessTexture` com a oclusão no canal R (o mesmo arquivo serve de `occlusionTexture`: ORM) ou, quando a rugosidade e o metal ficam com a tabela e o grão procedural, só a `occlusionTexture` (PNG em tons de cinza), `normalTexture` em espaço tangente, convenção OpenGL (+Y), com `TANGENT` exportado. Assar: oclusão de ambiente (64 amostras ou mais, distância de 6 mm), normais da malha de alta para a de baixa onde houver (grades, aletas, roscas), curvatura usada dentro do Blender para clarear de leve as arestas na cor e baixar a rugosidade nelas (desgaste de uso), entregue já dentro da cor e do ORM, não como mapa à parte.
5. **Texto e marcas**: "RTX PRO 6000" no X e o logotipo NVIDIA da borda, dourados, só onde uma referência mostra (`pny/back`, `pny/3qtr-top-right`). Preferência: pintados nos mapas da própria peça (região com cor `#c9a45c`, metal 1, rugosidade 0,32, como `ouro.serigrafia`); alternativa: primitiva própria com o material `carcaca.logo`, afastada no máximo 0,02 mm da superfície. Serigrafia do PCB e marcas dos chips: na cor e no ORM do `pcb.mascara` e do `chip.epoxi`, a partir de foto quando houver; sem foto, fica a textura procedural (ilustrativa).
6. **Tamanho e formato**: 2048 x 2048 no máximo por mapa (carcaça e face B), 1024 nas demais peças, 512 nas pequenas; orçamento total de texturas de 12 MB no GLB (o arquivo único cresce um terço com o base64). PNG para normal e ORM, JPEG de qualidade 90 ou WebP (`EXT_texture_webp`) para a cor. Sem KTX2 ou Basis (o transcodificador não abre por `file://`).
7. **Compressão**: sem Draco (o decodificador não abre por `file://`; `build-single.mjs` recusa). Malha com meshopt (`EXT_meshopt_compression`) pode: o decodificador já vai embutido. As texturas vão embutidas no GLB (bufferView), não em arquivo ao lado.
8. **Conferência**: depois do passo, rodar `node harness/tools/lookdev.cjs` e comparar com as referências; o `visual-qa` aprova (quem cria não aprova).

**Implementação (2026-11-11): `harness/parts/blender_pass.py`.** Roda com o Python que tem o `bpy` 5.3.0 (`python -I harness/parts/blender_pass.py`), lê `build/card.glb` e grava `build/card_final.glb` e `build/blender-pass-report.json`. O `sync-data` copia o `card_final.glb` para `public/data/card.glb` quando ele foi feito do `card.glb` atual (sha256 em `asset.extras.blender_pass`); senão, avisa e usa o `card.glb` (o caminho sem Blender continua igual). O que o script entrega hoje:
- Carcaça (`frame.shroud`, `frame.face_b`, `frame.rim`, as duas tampas do X) e bracket: UV própria, cor (JPEG 90, com desgaste leve nas arestas e as marcas douradas), normal (chanfro de 0,4 mm assado com o nó Bevel do Cycles: a geometria não muda) e oclusão (PNG cinza). A `frame.face_b` sai com duas primitivas: `carcaca.grade` (lâminas e paredes das frestas) e `carcaca.anodizado` (estrutura do X e moldura).
- Ventiladores (cubo e pás), pilhas de aletas, base do cooler e PCB principal: só oclusão; cor, rugosidade, metal e normal seguem a tabela e as texturas procedurais.
- A oclusão de cada peça é assada só contra as peças que se movem junto com ela na explosão (mesma cadeia de `explode_cad`), para não ficar sombra pintada de uma vizinha que sai.
- A cor assada vem de `src/materials.json` no momento do passo: mudou a cor de um material com mapa de cor, rode o passo de novo (os mapas crus ficam em `build/blender-cache/`, e a composição leva segundos).
- Marcas: "RTX PRO 6000" na tampa superior (`frame.center_covers.2`), pelas linhas `face_b_text_*` do CSV, e o logotipo NVIDIA (forma simplificada desenhada no script) na borda superior, sobre o ventilador da ponta; posição e tamanho do logotipo medidos nas referências, sem linha no CSV (`asset.extras.blender_pass.marcas`).
- Geometria comprimida sem perda com `EXT_meshopt_compression` por `scripts/meshopt-glb.mjs` (pacote `meshoptimizer` 1.3.0, dependência de desenvolvimento do viewer): atributos sem filtro e sem quantização, índices no modo de triângulos; o script decodifica e confere antes de gravar. Sem `node` ou sem o pacote, o GLB sai sem compressão, com aviso (`--sem-meshopt` força).
- Determinístico (semente 0, amostras fixas); o tempo e o tamanho de cada mapa ficam no relatório.

## API `window.__tour`

`ready` (Promise; também `window.__tourReady = true`), `duration`, `fps`, `cut`, `beats` (`{id, start, entrada, settle, end, level, mergulho}`; `entrada` é o fim da entrada do beat), `seek(t)` (posiciona a timeline e desenha um quadro de forma síncrona), `play()`, `pause()`, `next()` (toca até o `settle` do próximo beat e pausa), `prev()`, `goto(id)`, `time()`, `estado()` (`{expl, mix, via, acum, cam, vb}`: explosão, mistura e traçado do caminho quantizados, amostras da acumulação `{n, alvo}`, câmera 3D e enquadramento do diagrama, para teste), `probe(id)` (`{anchor, focus, box, captionOverflow, headline}` em pixels do palco; só vale para o beat ativo; `anchor` vale também nos beats 3D).

## Onde mexer

- Estilo dos `kind` dos diagramas: `src/kinds.css` (classe `k-<kind>`; kind desconhecido cai no estilo de `frame`).
- Caixa, cabeçalho, controles: `src/style.css`. Constantes de layout e de nível de detalhe: `src/layout.js`.
- Módulos: `world.js` (espaço único e `embed`), `diagrams.js` (camada SVG), `scene3d.js`, `timeline.js`, `callout.js`, `header.js`, `controls.js`, `tour.js` (junta tudo).

## Decisões que vale conhecer

- O enquadramento de diagrama não usa a tela inteira: o foco, com o `padding`, é ajustado à área que a caixa de texto não ocupa, para a caixa nunca cobrir o foco.
- Em nó largo na tela, o ponto da chamada vai para a borda voltada para a caixa (e não para o centro), para a linha não riscar o rótulo.
- Sem gradientes CSS e com pouco traço tracejado: a rasterização do Chromium dessas coisas varia com o histórico e quebra o determinismo byte a byte.
- Com `card.glb` o viewer aplica escala 1000 e rotação de +90 graus em X (metros e Y para cima para mm e Z para cima). A origem do GLB é o canto `envelope_min` do CAD, o mesmo referencial do storyboard. Testado com o blockout real (`smoke.cjs --fixture3d`).
- Explosão em 3D: `explode_state` vira um nível contínuo (assembled = 0, En = n) animado na entrada do beat, com a mesma duração e `ease` da câmera. A peça de estágio k tem progresso `suave(clamp(nível - (k-1), 0, 1))`; por isso, de E4 para E7, os estágios 5, 6 e 7 saem em sequência. O deslocamento é `explode_cad.dir * distance` (mm, referencial da peça-mãe); mover o nó leva os filhos. Beat de diagrama e beat sem `explode_state` mantêm o nível anterior.
- Destaque em 3D: `part` mais os ids de `highlight` (e `tag:<grupo>`, que casa com `group` da peça) ficam com opacidade 1; o resto vai a 0,15 (no modo realista, em vez de opacidade, o resto escurece e perde a cor; ver acima), junto com os descendentes e as instâncias (`instance_of`). Sem `part` nem `highlight`, nada esmaece. Cada malha ganha uma cópia própria do material no carregamento; os materiais do GLB não são alterados. Beat de diagrama herda o destaque do último beat 3D.
- Âncora 3D: posição mundial do nó `anchor.<peça>.<n>` projetada a cada quadro, depois da explosão e da câmera.
- Caminhos na placa (`overlay.path` em beat 3D: a2.9 energia, a2.10 dados, a2.11 calor): `src/caminhos3d.js` desenha numa camada SVG sobre o canvas uma linha de luz que percorre as peças do caminho, na linguagem dos fluxos dos diagramas (traço base, cauda em camadas, núcleo claro, halo, nós luminosos em cada peça). O mapeamento de peças está em `src/caminhos.json` (proposto pelo diretor de storyboard e aceito pela sessão principal em 2026-11-11), como árvore de trechos com pontos tirados das caixas das peças, das instâncias e das âncoras do GLB a cada quadro: o traçado acompanha a explosão e a troca do GLB. Depois da entrada do beat o traço avança da origem ao fim (2,2 s, `S.via` na timeline) e os pulsos correm com o tempo da timeline; sai junto com a caixa. Sem traço tracejado nem filtro (os pulsos são trechos de polilinha calculados, para o determinismo). O caminho dos dados passa do adaptador ao chip pelo conector de placa a placa J3 e pela placa principal, nunca pelo cabo flat; o cabo flat só aparece no ramo do vídeo, que é a proposta do grupo. O calor termina em anéis que se abrem nos ventiladores, sem seta: por qual face o ar entra e sai é lacuna (`airflow.direction`). A camada fica fora da acumulação de quadros.
- Mergulho da placa para o chip (beat t1.1, `src/mergulho.json`, configuração do viewer): quando um beat de diagrama listado ali entra vindo do 3D, a câmera 3D avança até a face externa do package, quase de frente, e o retângulo do die no diagrama fica colado ao package projetado na tela (proporção do die, por dentro do package) durante a descida; nos últimos 20% da entrada ele passa para o enquadramento do beat. A pose final da câmera é calculada para o package projetado coincidir com esse enquadramento, então a passagem não dá salto. O cooler e a carcaça, que na explosão E7 ficam sobre o package e tapariam a câmera, saem para trás e para cima na primeira parte da entrada, como mais um passo da explosão. A fusão 3D para diagrama começa aos 22% da entrada. Os diagramas vizinhos já entram apagados quando o beat anterior é 3D. Tudo é função do tempo da timeline.
