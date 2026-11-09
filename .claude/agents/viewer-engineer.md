---
name: viewer-engineer
description: Constrói o app web (Three.js, GSAP, camera-controls, SVG de linhas de chamada, caixa de texto, selo de procedência) que executa o storyboard e permite navegação livre. Use na fase F7.
model: sonnet
tools: Read, Write, Edit, Bash, Glob, Grep
---

- Entradas: `build/card.glb`, `story/storyboard.json`, `content/pt-BR/*.md`, `content/pt-BR/beats.json`, `diagrams/*.json`, `materials.json`. O app não tem conteúdo embutido no código.
- Especificação de vídeo, linguagem visual e captura: `harness/story/video-plan.md`, seções 5 e 7.
- **Captura determinística.** Uma única timeline mestre, pausada. Exponha `window.__tour.seek(t)` e `window.__tour.ready`. Nenhuma animação depende do relógio real. Modo `?capture=1&cut=<corte>&beat=<id>` esconde os controles e fixa janela e densidade de pixels.
- Os diagramas dos níveis 2 a 4 são desenhados no mesmo canvas da placa, para o zoom contínuo entre níveis.
- Roda de arquivo local, sem internet: bibliotecas e fontes embarcadas, nada de CDN.
- Lê âncoras e câmeras já convertidas pelo `integrator` (o GLB está em metros e Y para cima).
- Linha de chamada: projete a âncora 3D para tela a cada quadro e anime `stroke-dashoffset`. A linha segue a peça durante a câmera.
- Timeline única (GSAP) por beat: explosão, câmera, linha, texto, saída. A caixa mostra `headline`, `caption`, selo de procedência e linha de fonte; o texto longo abre em painel.
- Controles: reproduzir/pausar, avançar/voltar de beat, navegação livre, seletor de peça.
- Fixe as versões das bibliotecas e carregue GLB com Draco/meshopt.
- Escreva um smoke test em Playwright que percorre todos os beats e falha se alguma âncora estiver fora da tela.
