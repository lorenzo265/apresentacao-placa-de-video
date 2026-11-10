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

Teclado: setas (beat anterior e próximo), espaço (tocar e pausar), `N` (notas do apresentador: `speaker`, `fala` e beats `draft` e `blocked`). Em beat 3D com o tour pausado dá para orbitar com o mouse; ao avançar, a câmera volta ao storyboard.

## Testar e capturar

```
node harness/tools/smoke.cjs [--cut completo]      # percorre todos os beats; salva harness/dist/frames/<id>.png
node harness/tools/capture.cjs --cut completo [--fps 30] [--beats a4.2,a5.5] [--out harness/dist]
```

O smoke confere, por beat: console sem erro, `headline` igual ao de `beats.json`, limites de palavras e regra do tempo de leitura, caption sem estouro e com corpo de 28 px, caixa dentro da tela, âncora na tela e fora da caixa, foco inteiro na tela e fora da caixa, e determinismo (mesmo instante, com um `seek` no meio, dá PNG idêntico). A captura grava `harness/dist/capture/<corte>/<beat>/%05d.png`, pula o beat se o hash (beat, texto, diagramas, GLB, bundle) não mudou e monta `harness/dist/tour-<corte>.mp4`.

## API `window.__tour`

`ready` (Promise; também `window.__tourReady = true`), `duration`, `fps`, `cut`, `beats` (`{id, start, settle, end, level}`), `seek(t)` (posiciona a timeline e desenha um quadro de forma síncrona), `play()`, `pause()`, `next()` (toca até o `settle` do próximo beat e pausa), `prev()`, `goto(id)`, `time()`, `probe(id)` (`{anchor, focus, box, captionOverflow, headline}` em pixels do palco; só vale para o beat ativo).

## Onde mexer

- Estilo dos `kind` dos diagramas: `src/kinds.css` (classe `k-<kind>`; kind desconhecido cai no estilo de `frame`).
- Caixa, cabeçalho, controles: `src/style.css`. Constantes de layout e de nível de detalhe: `src/layout.js`.
- Módulos: `world.js` (espaço único e `embed`), `diagrams.js` (camada SVG), `scene3d.js`, `timeline.js`, `callout.js`, `header.js`, `controls.js`, `tour.js` (junta tudo).

## Decisões que vale conhecer

- O enquadramento de diagrama não usa a tela inteira: o foco, com o `padding`, é ajustado à área que a caixa de texto não ocupa, para a caixa nunca cobrir o foco.
- Em nó largo na tela, o ponto da chamada vai para a borda voltada para a caixa (e não para o centro), para a linha não riscar o rótulo.
- Sem gradientes CSS e com pouco traço tracejado: a rasterização do Chromium dessas coisas varia com o histórico e quebra o determinismo byte a byte.
- Com `card.glb` o viewer aplica escala 1000 e rotação de +90 graus em X (metros e Y para cima para mm e Z para cima). A origem do GLB precisa casar com o canto do envelope usado pelo storyboard. Não testado com GLB real.
