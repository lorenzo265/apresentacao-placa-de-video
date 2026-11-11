# Batedor: water blocks, guias de instalação e reparo (2026-11-10)

Território: quem abre a placa. Só material aberto. Legenda: **VISTA** = abri a página e olhei a imagem; **PÁGINA** = li a página, não vi a imagem; **SNIPPET** = só resultado de busca; **403/BLOQUEADO** = site recusou, URL registrada para baixar com outra ferramenta. Toda afirmação de "qual placa" diz como sei.

## Aviso de identidade de placa (leia antes de usar qualquer imagem)

- **Workstation Edition (WS)**: a placa do projeto. Cooler de fluxo duplo, PCB compacto no centro, dois dissipadores laterais.
- **Server Edition / Max-Q / RTX PRO 5000 48 GB**: PCB diferente. Watercool diz expressamente que seu bloco HEATKILLER INOX Pro NÃO serve à Workstation Edition (resultado de busca, repetido pela arvutitark.ee; a loja Watercool deu 404 ao abrir). Logo, o mapa de pads da Watercool (item 1) NÃO é do PCB da WS. EK-Pro (SE/Max-Q) também não serve à WS (afirmação de terceiros, não vista na EK, PDF deu 403).
- Alphacool 5100182 e Bykski N-RTXPRO6000-WS-SR: servem à WS (afirmação do fabricante, abaixo).

## 1. Watercool, manual HEATKILLER INOX Pro para RTX 5000/6000 Blackwell (PDF)
- Página/arquivo: https://shop.watercool.de/mediafiles/Manuals/MA_HK_GPU_RTX_6000_BLACKWELL.pdf
- Autor: Watercool GmbH. Data: PDF modificado em 2026-01-22 (metadado). VISTA (renderizei a página única, 595 x 4784 pt, bem estreita; baixa resolução na minha leitura).
- Placa: **não é a WS**. Título do manual: "for NVIDIA RTX 5000 / 6000 BLACKWELL"; lojas dizem Server Edition, Max-Q e PRO 5000 48 GB; WS listada como incompatível. Serve só de referência de PROCESSO, não de layout.
- Conteúdo visto: ferramentas; aviso (remover cooler original anula garantia); "Demontage des Luftkühlers / Backplate" (remover cooler e backplate, parafusos do backplate); render do conjunto bloco + backplate pré-montado; **mapa de pads térmicos** em duas vistas do PCB (frente e verso) com retângulos rosados e cotas por pad (ex. 54x15x1, 67,5x15x1, 12x15x1, 8x8x1, 12x8x1; texto "all Pads are 1mm"; pasta térmica no GPU); montagem do bloco; montagem do backplate e do slot bracket (cabo flat cinza visível no render, pasta no ponto marcado); dimensões do cooler (cota "216" visível).
- URL direta do PDF: https://shop.watercool.de/mediafiles/Manuals/MA_HK_GPU_RTX_6000_BLACKWELL.pdf (2,3 MB; sessão principal deve rasterizar em alta para ler as cotas).
- Valor: pads de 1 mm em todo o PCB SE/Max-Q (altura relativa dos componentes), render do cabo flat. Não aplicar à WS sem prova.

## 2. sabareesh.com, "4x RTX PRO 6000 Blackwell on Water" (as fotos)
- Página: https://sabareesh.com/posts/blackwell-waterblock/ . Autor: Sabareesh. Data: 2026-06-12. Espelho: https://banyan-god-github-io.pages.dev/posts/blackwell-waterblock/ (mesmas 7 imagens, caminhos relativos).
- Placa: **Workstation Edition** ("RTX PRO 6000 Blackwell Workstation (GB202, 96 GB GDDR7, 600 W)"), bloco Bykski full-cover sem modelo citado. Confirmo também pelas fotos: PCB compacto único com GB202 e conector de energia angulado.
- Fotos (URLs diretas, domínio confirmado: baixei as 4 abaixo):
  1. https://sabareesh.com/blog-images/wb-bare-pcb.jpg . **VISTA**. JPEG 215 KB, retrato (vista no tamanho 768x1024). PCB nu da WS, lado do GPU (frente da matriz), bloco removido: IHS dourado do GB202 com o die/região central com pasta, 2 colunas de GDDR7 (cinco fileiras à esquerda com pad de pasta aderido e quatro-cinco módulos à direita, mais fileira superior de quatro), 10 a 12 indutores "85N" ao longo da borda inferior, indutores em colunas à direita, conector de energia preto angulado no canto superior direito, conector de cabo flat (preto) no canto superior esquerdo, furos de fixação visíveis (3 a 4 em volta do GPU). **Melhor foto individual do PCB da WS** neste território. Fundo azul (tapete de oficina) com texto em chinês cortado.
  2. https://sabareesh.com/blog-images/wb-empty-pad.jpg . **VISTA**. 352 KB, retrato. Close do canto superior direito do PCB: borda superior do PCB com fileira de GDDR7 coberta de resíduo branco, furo de fixação com anel dourado, conector flat/energia preto à direita, MOSFET/DrMOS e passivos, local do indutor faltante (duas ilhas de solda) ao lado da bolsa de plástico onde está o indutor. Mostra a borda do PCB e a escala dos passivos.
  3. https://sabareesh.com/blog-images/wb-choke-found.jpg . **VISTA**. 289 KB. Indutor solto (cerca de 3 mm, preto, dois terminais metálicos) em tecido bege. Dá a escala e o formato do indutor SMD.
  4. https://sabareesh.com/blog-images/wb-choke-85n.jpg . **PÁGINA** (baixei, não abri a imagem; 303 KB). Mesmo indutor com a marcação "85N" visível, segundo o alt.
  5. https://sabareesh.com/blog-images/wb-rig-4gpu.jpg . **VISTA**. 463 KB, 1500x2000 aprox. Bancada com 4 GPUs em bloco, mangueiras e duas fontes be quiet. Só contexto; os blocos aparecem de lado (pouco útil para modelagem).
  6. https://sabareesh.com/blog-images/wb-radiator-fans.jpg . **PÁGINA** (só alt). Radiador XT45 1260 mm com 3x3 ventiladores de 140 mm. Sem relação com a placa.
  7. https://sabareesh.com/blog-images/wb-radiators-pair.jpg . **PÁGINA** (só alt). Os dois radiadores no loop. Sem relação com a placa.
- Texto: sem tipo de parafuso nem espessura de pad.

## 3. Alphacool, ES RTX 6000 Pro Workstation / RTX 5090 Founders Edition (5100182)
- Compatibilidade declarada pelo fabricante (datasheet V1.009, 04/2026, vista; loja Alphacool, vista): "Nvidia GeForce RTX 5090 Founders Edition, 32GB GDDR7, HDMI, 3x DP" e "Nvidia RTX PRO 6000 Blackwell Workstation-Edition, 96 GB GDDR7". Mesmo bloco serve às duas.
- Datasheet (**VISTA**, via espelho regard.ru, 6 páginas A4, 764 KB; o original alphacool já foi baixado): https://download.alphacool.com/datasheet/ENG_5100182_Alphacool_ES_RTX_6000_Pro_Workstation-RTX_5090_Founders_Edition_datasheet.pdf . Espelho: https://www.regard.ru/api/site/files/goodspdf/download/31538 . Há mais dados do que o já registrado:
  - Escopo de entrega, **lista de pads com espessura** (dá altura relativa de componentes): 2x 54x15x1; 4x 67,5x15x1; 4x 12x15x1; 5x 12x8x1; 1x 61,5x8x1; 1x 45x8x1; 9x 8x8x1; 5x 8x8x3 mm (todos 1 mm exceto os 5 de 3 mm). Mais: backplate ativo, pasta, espátula, 6x parafuso M2x18, 6x M2x4, 2x arruela, 2x porca M4, 1x slot bracket PCIe. Pads 7 W/mK, 35 Shore 00.
  - Cooler: 231,10 x 119,40 x 13,40 mm, 1,5 slot, 2x G1/4", placa de contato 3,30 mm. Backplate: 208,97 x 120,90 x 10,93 mm, placa 2,5 mm.
  - Capa: render isométrico do backplate de carbono com 14 parafusos e recorte no canto superior direito (VISTA).
  - O datasheet cita um zip "…_pics.zip" de fotos de produto, sem URL visível; **não inventei a URL** (provavelmente na pasta download.alphacool.com, a sessão principal deve procurar o link no PDF).
- Fotos de produto (URLs diretas; **PÁGINA**, não abri as imagens; loja alphacool.shop-cdn.com, mesma ref. 5100182, alt igual em todas):
  - https://alphacool.shop-cdn.com/media/image/07/a1/4f/5100182_01JBrcWZ8Lqojyk..jpg
  - https://alphacool.shop-cdn.com/media/image/2f/90/d0/5100182_02QmunrbDd0klpE..jpg
  - https://alphacool.shop-cdn.com/media/image/13/9b/ed/5100182_03wNoOAWT95zvC9..jpg
  - https://alphacool.shop-cdn.com/media/image/ff/0c/34/5100182_0448DpGxBuOq3eN..jpg
  - https://alphacool.shop-cdn.com/media/image/16/74/c2/5100182_05QhmCph2xoyZRZ..jpg
  - Página: https://shop.alphacool.com/en/detail/index/sArticle/22711 . Lista geral de compatibilidade: https://download.alphacool.com/homepage/compatibility_list_Nvidia.pdf (não aberta).
- Anúncio: https://www.alphacool.com/en/news/new-es-rtx-6000-pro-gpu-cooler (lançamento 2026-03-10; **PÁGINA**). Imagens: https://api.alphacool.com/storage/filemanager/news/Launch_10_03_2026/news-01.webp (alt: ES RTX 6000 Pro Workstation / RTX 5090 FE) e .../news-02.webp (sem alt). Baixadas como binário, não visualizadas.
- Manual PDF (já temos): o download direto estourou 10 MB no meu fetch, confirma que é grande e provavelmente rico em imagens.
- pausehardware.com (Wael K., atualizado 2026-03-11, crédito VideoCardz; **PÁGINA**, imagens não vistas): https://pausehardware.com/alphacool-rtx-pro-6000-blackwell/ ; 11 imagens, ex. https://pausehardware.com/wp-content/uploads/2026/03/alphacool-announces-rtx-pro-6000-blackwell-water-b-3-1024x742.jpg e -b-2-, -b-4 a -b-10 (mesmo padrão, sem sufixo de tamanho a partir da 4) e .../resized_alphacool-announces-rtx-pro-6000-blackwell-water-b-1024x617.jpg.
- Loja britânica https://www.watercoolinguk.co.uk/product/alphacool-es-rtx-6000-pro-workstation-rtx-5090-founders-edition/ : **403**, não vista.

## 4. Bykski N-RTXPRO6000-WS-SR (bloco + backplate, Workstation Edition)
- Página: https://www.bykski.us/products/bykski-durable-metal-pom-gpu-water-block-and-backplate-for-nvidia-rtx-pro-6000-blackwell-workstation-edition-n-rtxpro6000-ws-sr-continuous-usage (**PÁGINA**).
- Compatibilidade pelo fabricante: "machined for" a WS apenas; "combine o modelo exato, não a família". Não cita a 5090 FE. Variante SR (N-RTXPRO6000-SR) serve à Server, Max-Q, 6000D e PRO 5000: não é da WS.
- Na caixa (texto do fabricante): pads de 1,5 mm cortados, pasta, arruelas de 0,5 mm, parafusos com mola. Base de cobre niquelado com microcanais (película de ~0,35 mm segundo o texto). Há comentários de usuário sobre dois furos mal feitos (anedótico).
- Imagem principal (URL direta, do oembed): https://cdn.shopify.com/s/files/1/0069/8102/5892/files/products_2FzCa1tB1Vvkj1nou7lVzR_2F1790375163130-N-RTXPRO6000-WS-SR_20_3_4a9b9c9c-6159-41e9-ae46-2d14b0617933.jpg?v=1792758679 (não vista). Outras imagens ficam em www.bykski.us/cdn/shop/files/ com nomes parciais (…N-RTXPRO6000-WS-SR_20_3…, …B-FRD-RTXPRO6000-WS-SR-360…), cujo caminho completo não consegui extrair; **a sessão principal deve abrir o HTML da página**. A página cita uma foto de PCB de referência num URL Cloud Run, que não consegui obter.
- Também existe um AIO 360 Bykski para a WS (B-FRD-RTXPRO6000-WS-SR-360), mesma família de fotos.
- Artigo FormulaMod (**PÁGINA**): https://www.formulamod.net/blogs/new/nvidia-rtx-pro-6000-blackwell-96gb-water-cooling-guide-the-h100-killer-for-home-ai-labs . Sem passo a passo nem pads. Diz que a NVIDIA usa pasta (não metal líquido) na WS. Imagem de capa: https://www.formulamod.net/cdn/shop/articles/jpg_2e07b766-df24-4650-8628-872ea4ed0c12.jpg?v=1776841162&width=1100 (não vista).

## 5. Optimus (Titan Rig), RTX PRO 6000 Blackwell WS GPU Water Block
- Página: https://www.titanrig.com/optimus-rtx-pro-6000-blackwell-ws-gpu-water-block.html (**PÁGINA**). Part number op-gpu-rtxpro-6000-brass-cu, bloco de slot único com placa intermediária de latão, backplate incluso. Nome "WS" indica Workstation, mas a página diz só "RTX PRO 6000 Blackwell graphics cards" (compatibilidade com 5090 FE: nada). Sem dimensões, sem pads, sem manual.
- Fotos (URLs diretas):
  - https://www.titanrig.com/media/catalog/product/cache/828bae0ab509c88591c3b2b844d2c4ac/p/r/product_images_03-20_op-0118-01_03-20-op-0118-01_alt1_1.2.2026_12.31.38_pm.jpg . **VISTA**, 294 KB, ~2000x2000. Vista isométrica do **backplate/lado do verso** em alumínio escovado com 13 a 14 furos de parafuso, recorte no canto superior esquerdo-fundo, placa de latão dourada abaixo, bloco preto na ponta (bloco de conectores/portas), slot bracket à direita. Dá o contorno e a espessura do conjunto.
  - https://www.titanrig.com/media/catalog/product/cache/887962ebeeea3600f5b013f9c6b58b30/p/r/product_images_03-20_op-0118-01_03-20-op-0118-01_main_1.2.2026_2.05.35_pm.jpg . não vista.
  - https://www.titanrig.com/media/catalog/product/cache/828bae0ab509c88591c3b2b844d2c4ac/p/r/product_images_03-20_op-0118-01_03-20-op-0118-01_alt2_1.2.2026_12.31.53_pm.jpg . não vista.
- Variante SE (não é a WS): https://www.titanrig.com/optimus-rtx-pro-6000-blackwell-se-gpu-block-server-edition.html (só snippet).
- Avadirect, Optimus WS cold plate (MPN OP-PRO-6000-BLK-WS-BC), só snippet: https://www.avadirect.com/RTX-Pro-6000-Blackwell-WS-Brass-Copper-Cold-Plate/Product/19754316

## 6. Reparo: NorthridgeFix (canal YouTube, vídeo não encontrado) e cobertura
- O reparador abriu uma RTX PRO 6000 com o conector PCIe quebrado em trânsito (história de nov/2025). Cobertura:
  - hardware.com.br (William R. Plaza, 2025-11-17, **PÁGINA/VISTA de 1 foto**): https://www.hardware.com.br/noticias/nvidia-rtx-pro-6000-5090-design-modular-irreparavel/amp/ . A matéria trata de DOIS casos: 5090 FE e RTX Pro 6000; descreve 3 módulos (PCB principal, placa de saídas de vídeo, placa PCIe).
    - https://hardware.com.br/wp-content/uploads/2025/11/50125-NorthridgeFix-RTX-6000-1.jpg . **VISTA**, 144 KB, 1440x823 aprox. Frame do vídeo: técnico segura a placa aberta, **PCB compacto no centro com o suporte do GPU e fileiras de GDDR7, dois dissipadores de aletas verticais nas laterais, a placa PCIe preta com dedos dourados sendo segurada em frente ao PCB, e o cabo flat branco saindo do PCB para essa placa**. Mostra a arquitetura em 3 peças de perto. **Ambiguidade de placa**: o nome do arquivo diz RTX-6000 e a legenda diz RTX Pro 6000, mas a matéria também fala da 5090 FE e a foto não distingue as duas (mesmo layout de fluxo duplo). Tratar como "família Blackwell FE/WS, a confirmar".
    - https://hardware.com.br/wp-content/uploads/2025/11/50125-NorthridgeFix-RTX-6000-2.jpg . **PÁGINA** (descrição do fetch: close do conector PCIe dourado com borda escura). Não baixei.
    - https://hardware.com.br/wp-content/uploads/2025/11/rtx-6000-pro.jpg . hero, técnico segurando o PCB. Não baixei.
  - Notebookcheck (David Odejide, 2025-11-16, atualizada 2026-10-05; **PÁGINA**): https://www.notebookcheck.net/US-10-000-Nvidia-RTX-Pro-6000-rendered-useless-after-PCIe-connector-snaps-No-replacement-part-available.1164100.0.html . Não nomeia a edição. Imagem: https://www.notebookcheck.net/fileadmin/Notebooks/News/_nc5/A-10000-Nvidia-RTX-Pro-6000-became-useless-after-the-PCIe-broke-Image-source-NorthbridgeFix-on-YouTube.jpg (1600x1200, não vista).
  - Tom's Hardware: https://www.tomshardware.com/pc-components/gpus/usd10-000-rtx-pro-6000-blackwell-workstation-gpu-reportedly-snaps-under-its-own-weight-during-transit-severs-pcie-connector-lack-of-replacement-parts-renders-card-useless-despite-its-modular-design (fetch devolveu só o título; imagens não vistas). Menciona "Workstation" no título.
  - TweakTown (SNIPPET): https://www.tweaktown.com/news/108910/this-10-000-nvidia-rtx-pro-6000-turns-into-a-brick-over-an-irreplaceable-broken-pcie-connector/index.html e https://www.tweaktown.com/news/108969/nvidia-offers-replacement-for-damaged-rtx-pro-6000-worth-10k-used-pcie-boards-now-in-china/index.html (placas PCIe de terceiros na China).
  - PC Games Hardware (SNIPPET): https://www.pcgameshardware.de/Grafikkarten-Grafikkarte-97980/News/Nvidia-RTX-6000-Pro-Teurer-Elektroschrott-gebrochene-Platine-1486934/
  - purepc.pl tag: https://www.purepc.pl/tagi/northridgefix (SNIPPET).
- Divergência: Brasil e Notebookcheck divergem sobre qual caso (5090 FE ou PRO 6000) o reparador mostrou; não resolvi.

## 7. Outros achados (não abertos ou fora do escopo)
- Guru3D, "RTX PRO 6000 Blackwell Workstation Edition PCB Layout Leak": https://www.guru3d.com/story/nvidia-rtx-pro-6000-blackwell-workstation-edition-pcb-layout-leak/ . **403**, não vista. Snippet: PCB em 3 partes, memória em ambos os lados.
- gamegpu, fotos do PCB: https://en.gamegpu.com/news/zhelezo/poyavilis-foto-pechatnoj-platy-rtx-pro-6000-blackwell-96-gb (já registrada na seção 18.1; só snippet aqui).
- EK, manuais EK-Pro RTX PRO 6000 SE/Max-Q (**403**, não vistos; **não servem à WS**): https://www.ekwb.com/shop/EK-IM/EK-IM-3831129901728.pdf e https://www.ekwb.com/shop/EK-IM/EK-IM-3831109822241.pdf . Snippet cita pads 30x15x3 mm no chip e 2 mm em VRAM/VRM, para a SE.
- Level1Techs guia de setup (só snippet, sem fotos de abertura): https://forum.level1techs.com/t/wip-blackwell-rtx-6000-pro-max-q-quickie-setup-guide-on-ubuntu-24-04-lts-25-04/230521?page=17
- Club386 / wccftech, PCB da RTX 6000D (84 GB, 28 módulos; **não é a WS**): https://www.club386.com/?p=133989 e https://wccftech.com/nvidia-rtx-6000d-84-gb-pcb-spotted-uses-a-28x-3gb-gddr7-chips-layout/ (SNIPPET).
- Espelho do blog sabareesh num agregador do Hacker News: https://hackernews-dynamic.seasondane.workers.dev/news/48508550 (só snippet; irrelevante).

## Inconsistências e conferências
- Pads Alphacool: itens somam 2+4+4+5+1+1+9+5 = 31 pads no datasheet (todos listados); nenhuma tabela interna contradiz.
- Alphacool diz cooler com 13,40 mm de altura e backplate de 10,93 mm; a cota Bykski já registrada é 20,70 mm de espessura total do bloco: são produtos diferentes, não conflito.
- Pad térmico: Bykski usa 1,5 mm cortado; Alphacool 1 mm e 3 mm; Watercool (SE/Max-Q) 1 mm. Diferenças de espessura entre fabricantes refletem folgas de projeto de cada bloco, não necessariamente a altura real dos componentes.

## Não achei
- Foto do PCB da WS **com componentes no verso** (lado oposto ao GPU), limpa ou com pads. Só a foto sabareesh de uma face (lado do GPU) e a Watercool (outra placa).
- Diagrama de pads da WS (fabricante). Alphacool e Bykski só dão lista de pads, sem mapa; o manual Alphacool pode ter (não consegui abri-lo, 10 MB+).
- Desmontagem do cooler original da WS: contagem e tipo de parafusos. Nenhum guia a traz; Watercool fala em "remover cooler e backplate" sem números.
- Foto do cooler original aberto e da base de contato. Nenhuma neste território.
- Barrow, Granzon, Phanteks, Thermal Grizzly, Corsair, Aqua Computer, EKWB para a WS: sem produto encontrado (EKWB só SE/Max-Q).
- Reddit, overclock.net, HardForum: nada aberto (busca não devolveu threads).
- Vídeo do NorthridgeFix: URL do YouTube não encontrada.
