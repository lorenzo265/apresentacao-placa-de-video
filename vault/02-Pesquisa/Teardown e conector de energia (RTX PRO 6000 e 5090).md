---
tipo: fonte
status: rascunho
secao: Energia, dados e calor na placa
autor: NVIDIA; GamersNexus; Jon Peddie Research; StorageReview; Club386 e outros (lista abaixo)
link: https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf
acessado: 2026-10-26
procedencia: mista   # confirmed (RTX PRO 6000) e derived (RTX 5090 FE e padrões genéricos)
---
# Teardown e conector de energia (RTX PRO 6000 e 5090)

## Dados da fonte
- **Título:** conjunto de fontes sobre conector de energia, cooler e teardown. Mistura documentos da própria RTX PRO 6000 Workstation Edition (`confirmed`) e da irmã RTX 5090 Founders Edition, que usa o mesmo chip GB202 (`derived`).
- **Autor / publicador:** NVIDIA (datasheet e guia de instalação); GamersNexus (teardown); Jon Peddie Research, StorageReview e Puget Systems (reviews); Club386 e relatos da NVIDIA sobre a 5090 FE.
- **Links principais:**
  - Datasheet da NVIDIA: o link do frontmatter.
  - Guia de instalação da NVIDIA: https://images.nvidia.com/aem-dam/Solutions/design-visualization/quadro-product-literature/rtx-pro-blackwell-online-qsg-210x148mm-20250718-r14.pdf
  - Teardown da própria placa: https://gamersnexus.net/gpus/nvidia-rtx-pro-6000-blackwell-benchmarks-tear-down-thermals-gaming-llm-acoustic-tests
  - Review: https://www.jonpeddie.com/reviews/the-nvidia-rtx-pro-6000-blackwell-edition/
  - Placa irmã (5090 FE): https://www.club386.com/nvidia-geforce-rtx-5090-review/
  - A lista completa, com URL e data de cada fonte, está no arquivo bruto abaixo.
- **Data de acesso:** 2026-10-26.

## Pontos que servem à apresentação
- **Conector de energia (resolve a pendência da [[02 - Energia, dados e calor na placa]]).** A ficha da NVIDIA diz que a placa tem 1 conector "PCIe CEM5 16-pin", na borda superior, e 600 W de potência total. Na caixa vem um adaptador que junta 4 cabos de 8 pinos da fonte num plugue de 16 pinos. Fontes diferentes chamam o conector de 12V-2x6 ou de 12VHPWR; o número de pinos é o mesmo e a diferença de nome ficou registrada como conflito. Procedência `confirmed`.
- **PCIe e tamanho.** Interface PCIe 5.0 x16, 5,4" x 12" (cerca de 137 x 304 mm) e dois slots. A espessura varia entre fontes (40 ou 42 mm, conflito registrado); a NVIDIA só informa "dois slots". Procedência `confirmed`.
- **Cooler e teardown da própria placa (GamersNexus).** Dois ventiladores na frente, fluxo de ar que atravessa as aletas (a NVIDIA chama de "double flow through"), placa de circuito no centro, bem densa. No chip há pasta térmica (a 5090 FE usa metal líquido). A memória está em 32 locais de 3 GB, 16 no verso, com pads térmicos; 32 x 3 GB dá os 96 GB e bate com o barramento de 512 bits se cada chip usar 16 bits (dedução, a palavra "clamshell" não aparece em fonte da placa). Procedência `confirmed`, mas de uma só fonte de teardown.
- **Placa irmã 5090 FE.** A NVIDIA fala em placa de circuito de 3 peças, câmara de vapor com heatpipes e metal líquido; outras fontes contam 4 partes. Serve de análogo para o interior do cooler, sempre com o selo `derived`, nunca como fato da RTX PRO 6000.
- **O que falta.** Número de fases do VRM, camadas do PCB, divisão da corrente entre o slot e o conector, heatpipes e câmara de vapor da RTX PRO 6000. Essas lacunas vão para a proposta de arquitetura (`gpu-assembly-proposal`) como `inferred`.

## Trecho bruto salvo em
`harness/spec/sources/power-connector-teardown.md` (tabela com id, valor, fonte, placa e procedência; conflitos; contas conferidas; lacunas).

> [!note]
> Resumo com palavras próprias. Não cole trechos longos de terceiros aqui. Dado da 5090 FE nunca vira `confirmed` para a RTX PRO 6000.

> [!warning]
> O arquivo bruto foi lido em parte por resumo automático (páginas web), então números críticos devem passar pelo `fact-checker` antes de entrar no texto final.
