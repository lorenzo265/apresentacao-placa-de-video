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

Parâmetros da URL: `?cut=seminario` (padrão `completo`), `?capture=1` (sem controles, palco fixo de 1920 x 1080, sem laço de animação), `?beat=<id>` (começa no fim da chamada do beat).

Temas de estilo (proposta da etapa de design, ainda sem escolha do autor): `?tema=keynote|estudio|blueprint`. Sem `?tema` o viewer é o de sempre (conferido quadro a quadro contra as capturas anteriores). `?leve=1` desliga os efeitos caros do tema (desfoque da caixa, brilho do nó-alvo, halos). Parâmetros em `src/temas.js` (fundo, luzes, materiais, arestas, sombra de contato, raio de canto, fluxos), estilo em `src/temas.css` (só regras sob `:root[data-tema]`), cotas da placa montada no tema blueprint em `src/cotas.js` (só medidas auditadas de `measurements.json`). Capturas e folhas de contato: `node harness/tools/estilo.cjs` (grava `harness/dist/estilo/`); quadros por segundo ao vivo: `node harness/tools/estilo.cjs --perf`. Os dois smokes aceitam `--tema <nome>`.

Teclado: setas (beat anterior e próximo), espaço (tocar e pausar), `N` (notas do apresentador: `speaker`, `fala` e beats `draft` e `blocked`). Em beat 3D com o tour pausado dá para orbitar com o mouse; ao avançar, a câmera volta ao storyboard.

## Testar e capturar

```
node harness/tools/smoke.cjs [--cut completo]      # percorre todos os beats; salva harness/dist/frames/<id>.png
node harness/tools/capture.cjs --cut completo [--fps 30] [--beats a4.2,a5.5] [--out harness/dist]
```

O smoke confere, por beat: console sem erro, `headline` igual ao de `beats.json`, limites de palavras e regra do tempo de leitura, caption sem estouro e com corpo de 28 px, caixa dentro da tela, âncora na tela e fora da caixa, foco inteiro na tela e fora da caixa, e determinismo (mesmo instante, com um `seek` no meio, dá PNG idêntico). A captura grava `harness/dist/capture/<corte>/<beat>/%05d.png`, pula o beat se o hash (beat, texto, diagramas, GLB, bundle) não mudou e monta `harness/dist/tour-<corte>.mp4`.

```
node harness/tools/smoke.cjs --fixture3d       # beats 3D reais: usa schemas/examples/fixture3d.*.example.json
```

Com `--fixture3d` o smoke serve uma cópia do `dist` com o storyboard de exemplo de beats 3D (montada, E1, E4, E7 e um mergulho para diagrama) e o GLB real, e confere por beat 3D: âncora resolvida e dentro da tela, caixa fora da âncora, nível de explosão no fim do beat igual ao pedido, e determinismo com `seek` no meio da entrada (onde a explosão está a meio caminho).

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

Face A (ventiladores, cooler.fan.*) fica em z baixo (z de 0 a 13); a face B (tampa traseira, `frame.face_b`) em z alto (37 a 40). A placa de circuito fica entre elas (z de 32 a 34). O estágio E7 afasta a placa para z alto (+40) e o E8 afasta os ventiladores para z baixo (-40). Centros dos ventiladores: x = 61 e x = 244, y = 74,2. Para ver os ventiladores, a câmera tem de estar em z negativo; com z positivo a tela mostra a face B. Câmera de partida: `--pos 520,-380,260 --target 152,68,20`.

## Arquivo único para apresentar

```
cd harness/viewer && npm run build:single        # gera harness/dist/tour.html
node harness/tools/smoke-single.cjs [--cut seminario] [--no-build]
```

`harness/dist/tour.html` leva código, estilos, fontes e dados embutidos (cerca de 1,3 MB). Abre com dois cliques, sem servidor e sem internet. Teclas: seta para a direita e para a esquerda, espaço, `N` para as notas. O corte se troca no seletor da barra ou com `?cut=seminario` no fim do endereço. O `smoke-single` abre o arquivo por `file://` com a rede desligada, confere que nada é pedido de fora, que as fontes carregam, que a seta leva a cada beat e que o título na tela é o de `beats.json`. Se `harness/build/card.glb` existir (gerado por `harness/parts/blockout.py`), ele vai embutido em base64 e o teste confere que carregou e que as peças respondem pelo id do assembly. O arquivo único só aceita GLB sem compressão Draco. Sem GLB, o 3D é o marcador desenhado pelo próprio viewer.

## API `window.__tour`

`ready` (Promise; também `window.__tourReady = true`), `duration`, `fps`, `cut`, `beats` (`{id, start, settle, end, level}`), `seek(t)` (posiciona a timeline e desenha um quadro de forma síncrona), `play()`, `pause()`, `next()` (toca até o `settle` do próximo beat e pausa), `prev()`, `goto(id)`, `time()`, `estado()` (`{expl, mix}` quantizados, para teste), `probe(id)` (`{anchor, focus, box, captionOverflow, headline}` em pixels do palco; só vale para o beat ativo; `anchor` vale também nos beats 3D).

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
- Destaque em 3D: `part` mais os ids de `highlight` (e `tag:<grupo>`, que casa com `group` da peça) ficam com opacidade 1; o resto vai a 0,15, junto com os descendentes e as instâncias (`instance_of`). Sem `part` nem `highlight`, nada esmaece. Cada malha ganha uma cópia própria do material no carregamento; os materiais do GLB não são alterados. Beat de diagrama herda o destaque do último beat 3D.
- Âncora 3D: posição mundial do nó `anchor.<peça>.<n>` projetada a cada quadro, depois da explosão e da câmera.
- `overlay.path` em beat 3D é aceito e ignorado, com o aviso `[3D] overlay ainda sem mapeamento de peças`. O mapeamento de peças por caminho é decisão de conteúdo e ainda não existe.
- No mergulho (3D para diagrama) a câmera 3D fica parada na última pose e o diagrama entra por mistura de opacidade; a câmera não se aproxima do chip por conta própria. Se o diretor quiser o mergulho com zoom, o beat 3D anterior precisa terminar com a câmera já perto da peça.
