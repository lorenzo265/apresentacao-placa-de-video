# Conector de energia, interface, cooler e teardown (rodada de 2026-10-26)

Coleta da fase F1 para a seção 02 do roteiro ("Energia, dados e calor na placa"). Só entram fontes realmente abertas nesta rodada. Os PDFs não são versionados (direitos do fabricante); para reproduzir, baixar a URL.

**Como cada fonte foi lida.** WebFetch devolve um resumo automático e pode errar. Por isso:
- PDFs da NVIDIA (S01, S02, S04, S05) foram lidos **página a página, renderizados como imagem** (não pelo resumo). Os trechos entre aspas desses são conferidos.
- Páginas web (S03, S06 a S24) foram lidas por **resumo automático**. Os trechos entre aspas vêm desse resumo; os de S06 (GamersNexus) e S07 (Jon Peddie) foram pedidos mais de uma vez e vieram coerentes entre si. Nas demais, uma leitura só.
- Cinco fotos do teardown da própria placa (S06) foram baixadas e vistas. Ver a seção 3.

**Regra de procedência (ARCHITECTURE.md, seção 3).** `confirmed` = documento oficial da NVIDIA ou teardown/review da própria RTX PRO 6000 Workstation Edition. `derived` = placa irmã com o mesmo chip GB202 (RTX 5090 Founders Edition) ou informação genérica (padrão de conector, padrão GDDR7). Dado da 5090 **nunca** é `confirmed` para a RTX PRO 6000. Variante da apresentação: Workstation Edition (600 W). A Max-Q (300 W) é outra placa e só aparece como contraste.

Data de acesso de todas as fontes: **2026-10-26**.

---

## 1. Fontes abertas

### Documentos oficiais da NVIDIA (RTX PRO 6000)

**S01. NVIDIA RTX PRO Blackwell Architecture, Quick Start Guide** (PDF com pelo menos 20 páginas; lidas as p. 1 a 20, em EN e começo do FR)
- URL: https://images.nvidia.com/aem-dam/Solutions/design-visualization/quadro-product-literature/rtx-pro-blackwell-online-qsg-210x148mm-20250718-r14.pdf
- Procedência: `confirmed` (guia do fabricante). O nome do arquivo traz "20250718-r14" (isso é só o nome; a data de publicação não está no documento lido).
- Lido por renderização das páginas. Páginas citadas são as do PDF (p. 1 = capa).

**S02. NVIDIA RTX PRO 6000 Blackwell Workstation Edition, Datasheet** (PDF, 3 páginas)
- URL: https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf (o link está na página do produto S03)
- Procedência: `confirmed`. O rodapé lido na imagem diz "© 2026 NVIDIA Corporation" e "JUN26".
- Lido por renderização. Tabela de especificações na p. 3.

**S03. NVIDIA, página do produto RTX PRO 6000 Blackwell Workstation Edition**
- URL: https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/
- Procedência: `confirmed`. Já registrada em `nvidia-rtx-pro-6000-product-page.md` (2026-10-19). Reaberta hoje só para achar o link do datasheet e a linha de cooler.
- Resumo automático.

**S05. NVIDIA, whitepaper RTX Blackwell GPU Architecture v1.1** (já registrado em `nvidia-rtx-pro-blackwell-architecture-v1.1.md`)
- URL: https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf
- Procedência: `confirmed`. Reaberto hoje só nas p. 12 a 14 (memória e Tabela 1), por renderização.

### Documento genérico da NVIDIA

**S04. NVIDIA, Power Guidelines for Workstation Products, Application Note DA-07261-001_v11 (abril de 2022)**
- URL: https://www.nvidia.com/workstationpowerguidelines (devolveu o PDF; é o link que o S01 manda usar)
- Procedência: `derived` para esta placa. É uma nota de aplicação genérica de 2022; a tabela de modelos termina na RTX A6000 e **não lista a RTX PRO 6000**. Serve só para a regra geral de potência de slot e de conector de 8 pinos.
- Lido por renderização. As páginas citadas (p. 3 e p. 5) são as impressas no rodapé do documento.

### Teardown e reviews da própria RTX PRO 6000 Workstation Edition

**S06. GamersNexus, "NVIDIA RTX PRO 6000 Blackwell Benchmarks & Tear-Down" (térmica, jogos, LLM, acústica)**
- URL: https://gamersnexus.net/gpus/nvidia-rtx-pro-6000-blackwell-benchmarks-tear-down-thermals-gaming-llm-acoustic-tests
- Data: página diz 2025-09-25 (nota do editor: publicado originalmente como vídeo em 2025-06-24). Créditos: Steve Burke, Tannen Williams, Jimmy Thang.
- Procedência: `confirmed` (teardown da própria placa). Única fonte de teardown físico aberta para a placa.

**S07. Jon Peddie Research, "The Nvidia RTX Pro 6000 Blackwell Edition"** (Alex Herrera, 2025-11-17)
- URL: https://www.jonpeddie.com/reviews/the-nvidia-rtx-pro-6000-blackwell-edition/
- Procedência: `confirmed` (review da própria placa; o artigo cita o chassi Dell Pro Max T2).

**S08. StorageReview, "NVIDIA RTX PRO 6000 Workstation GPU Review: Blackwell Architecture and 96 GB for Pro Workflows"** (Dylan Dougherty, 2025-10-07)
- URL: https://www.storagereview.com/review/nvidia-rtx-pro-6000-workstation-gpu-review-blackwell-architecture-and-96-gb-for-pro-workflows
- Procedência: `confirmed` (review da própria placa).

**S09. Puget Systems, ficha de produto "NVIDIA RTX PRO 6000 Blackwell Workstation Edition 96GB PCI-E" (16221)**
- URL: https://www.pugetsystems.com/parts/Video-Card/NVIDIA-RTX-PRO-6000-Blackwell-Workstation-Edition-96GB-PCI-E-16221/
- Procedência: `confirmed`, **fonte secundária** (ficha de revendedor; copia especificações).

**S10. Puget Systems, "NVIDIA RTX PRO 6000 Blackwell Workstation Content Creation Review"** (publicado 2025-06-11, modificado 2025-07-16)
- URL: https://www.pugetsystems.com/labs/articles/nvidia-rtx-pro-6000-blackwell-workstation-content-creation-review/
- Procedência: `confirmed` (review da própria placa). Não cita conector nem dimensões.

**S11. PNY, página "NVIDIA RTX PRO 6000 Blackwell Workstation Edition"**
- URL: https://www.pny.com/nvidia-rtx-pro-6000-blackwell-ws
- Procedência: `confirmed`, **fonte secundária** (parceiro que vende a placa). Duas leituras iguais.

**S12. BuildCores, ficha "NVIDIA RTX PRO 6000 Blackwell Workstation Edition 96GB GDDR7"**
- URL: https://www.buildcores.com/products/GPU/eblltkoej/NVIDIA-RTX-PRO-6000-Blackwell-Workstation-Edition-96GB-GDDR7
- Procedência: `confirmed`, **fonte secundária** (agregador de especificações).

**S13. AEC Magazine, "Review: Nvidia RTX Pro Blackwell GPUs"** (Greg Corke, 2026-02-03)
- URL: https://aecmag.com/workstations/review-nvidia-rtx-pro-blackwell-series-gpus/
- Procedência: `confirmed` (review). A frase sobre o cabo vale para "RTX Pro 4000 e acima"; o artigo não cita a 6000 nominalmente nessa frase.

### Padrão do conector e do GDDR7 (genérico)

**S14. Wikipedia, "16-pin 12VHPWR connector"**
- URL: https://en.wikipedia.org/wiki/16-pin_12VHPWR_connector
- Procedência: `derived` (padrão de conector, não é a placa). Fonte secundária enciclopédica.

**S23. Cópia do comunicado do JEDEC sobre o GDDR7** (design-reuse, 2024-03-05)
- URL: https://us.design-reuse.com/news/55819/jedec-gddr7-graphics-memory-standard.html
- Procedência: `derived` (padrão genérico). O site do JEDEC (jedec.org/node/9394) deu 403.

**S24. HWCooling, "GDDR7 memory for next-gen GPUs is ready, up to 48GHz clocks"** (2024-03-12)
- URL: https://www.hwcooling.net/en/gddr7-memory-for-next-gen-gpus-is-ready-up-to-48ghz-clocks/
- Procedência: `derived` (padrão genérico, texto de imprensa de 2024).

### Placa irmã com o mesmo chip GB202: RTX 5090 Founders Edition (tudo `derived`)

**S15. NVIDIA GeForce News, anúncio da série RTX 50** (seção "Founders Edition Revolutionary Double Flow Through Design")
- URL: https://www.nvidia.com/en-us/geforce/news/rtx-50-series-graphics-cards-gpu-laptop-announcements/
- Data de publicação não aparece no resumo lido. Resumo automático.

**S16. NVIDIA, página da GeForce RTX 5090**
- URL: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
- Resumo automático. Data não aparece.

**S17. Club386, "Nvidia GeForce RTX 5090 Founders Edition review"** (Parm Mann, 2025-01-23)
- URL: https://www.club386.com/nvidia-geforce-rtx-5090-review/
- Review com desmontagem parcial do cooler.

**S18. Notebookcheck, "Nvidia shares what makes the Founders Edition RTX 5090 special"** (2025-01-27)
- URL: https://www.notebookcheck.net/Nvidia-shares-what-makes-the-Founders-Edition-RTX-5090-special.951354.0.html
- Relata afirmações da NVIDIA (não é medição de terceiros).

**S19. Wccftech, "NVIDIA Explains The Marvelous Design Of The GeForce RTX 5090 Founders Edition"** (2025-01-23)
- URL: https://wccftech.com/nvidia-explains-the-marvelous-design-of-the-geforce-rtx-5090-founders-edition/amp/
- Relata afirmações da NVIDIA.

**S20. HotHardware, "NVIDIA Details Cool Engineering That Lead To A Smaller GeForce RTX 5090"** (2025-01-22)
- URL: https://hothardware.com/news/nvidia-details-rtx-5090-fe-cooler
- Relata afirmações da NVIDIA.

**S21. Notebookcheck, teardown da Northridge Fix da 5090 FE** (2025-10-27)
- URL: https://www.notebookcheck.net/Nvidia-RTX-5090-Founders-Edition-teardown-reveals-fragile-modular-design-that-repair-experts-call-a-disaster.1147864.0.html
- Relata a opinião de uma oficina de reparo. A página mostra também um carimbo de atualização malformado ("2026-10- 5").

**S22. Wccftech, "NVIDIA GeForce RTX 5090 PCB Leaks Out"** (2024-12-25)
- URL: https://wccftech.com/nvidia-geforce-rtx-5090-pcb-leak-gargantuan-gb202-gpu-16-gddr7-memory-single-16-pin-connector/
- **Vazamento pré-lançamento** (Chiphell). Peso baixo; usado só para contagem de pacotes de memória e como estimativa de fases.

---

## 2. Fatos

Colunas: `id`, dado, valor, fonte (localização), placa a que o dado se refere, procedência, `conflict`. Quando `conflict` é `true`, a seção 4 lista as duas leituras.

### 2.1 Conector de energia

| id | Dado | Valor | Fonte | Placa | Procedência | conflict |
|---|---|---|---|---|---|---|
| pwr.connector.count | Quantidade de conectores de energia | 1 | S02 p. 3 ("1x"); S08 ("a single 16-pin power connector"); S09; S12 | RTX PRO 6000 WS | confirmed | false |
| pwr.connector.name.nvidia | Nome na ficha da NVIDIA | "1x PCIe CEM5 16-pin" | S02 p. 3 (Power Connector); S11 (mesma frase); S13 ("PCIe CEM5 16-pin cable") | RTX PRO 6000 WS | confirmed | **true** (nome, ver K1) |
| pwr.connector.name.qsg | Nome no guia de instalação | "16-pin PCIe Gen5 connector" | S01 p. 10 (passo 8) | RTX PRO 6000 WS | confirmed | **true** (K1) |
| pwr.connector.name.12v2x6 | Nome em fichas de revendedor | "12V-2x6" (1 conector) | S09; S12 ("PCIe 12V-2x6", contagem 1) | RTX PRO 6000 WS | confirmed (secundária) | **true** (K1) |
| pwr.connector.name.12vhpwr | Nome no teardown | "Like the 5090, the card uses a 12VHPWR cable." | S06 (texto do teardown) | RTX PRO 6000 WS | confirmed | **true** (K1) |
| pwr.connector.pins | Número de pinos | 16 (nome "16-pin"); no padrão 12V-2x6/12VHPWR são 12 pinos de potência e 4 de sinal (sense) | nome: S01, S02, S08; detalhe 12+4: S14 | RTX PRO 6000 WS (16); padrão genérico (12+4) | confirmed (16); derived (12+4) | false |
| pwr.connector.location | Posição do conector na placa | borda superior da placa ("on the top edge of the RTX PRO 6000"). Na Max-Q, na borda lateral ("east edge") | S01 p. 10; S07 ("top middle of the card"); S08 ("Along the top edge") | RTX PRO 6000 WS | confirmed | false |
| pwr.tbp | Potência total da placa | "Total board power: 600 W" | S02 p. 3; S03 ("600 W"); S05 (TGP 600 W, via nota existente); S09 (TGP 600 W); S08 ("600 W configurable TDP"); S13 ("up to 600W"); S10 ("up to 600 Watts") | RTX PRO 6000 WS | confirmed | false (valor igual; o nome varia: total board power, TGP, TDP, max power consumption) |
| pwr.tbp.definition | Definição de TGP da NVIDIA | "The total graphics power (TGP) represents the maximum amount of graphics board power that the system power supply should be able to provide to the graphics card." | S04 p. 3 | família de placas de workstation (genérico, 2022) | derived | false |
| pwr.connector.rating | Potência máxima do conector 12V-2x6 | "up to 600 W" | S14 | padrão genérico | derived | false |
| pwr.slot.rating | Potência do slot PCIe x16 | "Typically, the PCIe slot is rated for 75 W" | S04 p. 5 (genérico) | placas PCIe de workstation, não específico desta | derived | false |
| pwr.8pin.rating | Potência de um conector PCIe de 8 pinos | "the 8-pin PCIe connector is rated for 150 W" | S04 p. 5 | genérico | derived | false |
| pwr.adapter.box | Adaptador na caixa | 1x "Auxiliary Power Cable (4x PCIe 8-pin (PSU) to 1x PCIe Gen5 16-pin (GPU) power adapter)" | S01 p. 5 (tabela Equipment, coluna RTX PRO 6000 Workstation Edition) | RTX PRO 6000 WS | confirmed | **true** (K2: S11 mostra outro rótulo) |
| pwr.adapter.instruction | Instrução de ligação | "For RTX PRO 6000, connect four separate PCIe 8-pin cables from the system power supply to the NVIDIA Quad PCIe 8-pin power adapter as necessary." | S01 p. 10 | RTX PRO 6000 WS | confirmed | false |
| pwr.adapter.warning | Aviso do fabricante | "Use only the included NVIDIA power connector adapter for your NVIDIA RTX PRO graphics card. Ensure a secure connection by firmly plugging the power dongle into the graphics card." | S01 p. 12 | RTX PRO 6000 WS | confirmed | false |
| pwr.adapter.review | Adaptador citado em review | "channeled to Nvidia's more recent auxiliary power connector with a 4x 8-pin pigtail adapter"; também "4x 150 W auxiliary GPU ... power cables" (esta última só na primeira leitura de S07, não repetida na segunda) | S07 | RTX PRO 6000 WS | confirmed | false |
| pwr.extender.box | Acessório "Enhanced Straight Extender" | 1 unidade incluída apenas na RTX PRO 6000 Workstation Edition; o guia não explica o que é nem onde se usa | S01 p. 5 (tabela Equipment) | RTX PRO 6000 WS | confirmed (existência); função é lacuna | false |
| pwr.maxq.adapter | Adaptador da Max-Q | 1x cabo 2x PCIe 8-pin para 1x 16-pin; conector na borda lateral | S01 p. 5, p. 10, p. 11 | **RTX PRO 6000 Max-Q** (não é a placa do projeto; só contraste) | confirmed | false |
| pwr.cable.requirement | Exigência de cabo | "The RTX Pro 4000 and above require a PCIe CEM5 16-pin cable ... adapters are available for power supplies with older 6-pin and 8-pin PCIe connectors" (frase de série; não nomeia a 6000) | S13 | série RTX PRO (4000 e acima) | confirmed (fraco) | false |
| pwr.12v2x6.history | Relação 12VHPWR e 12V-2x6 | 12V-2x6 é uma revisão menor do 12VHPWR (2023): mudou o lado dos soquetes (GPU e fonte), para os pinos de sinal só fecharem contato com o plugue bem encaixado; cabos e plugues não mudaram. Definido no PCIe CEM 5.1. Marcação: "H+" (12VHPWR) e "H++" (12V-2x6) | S14 | padrão genérico | derived | false |

### 2.2 Interface PCIe, slots, dimensões e saídas

| id | Dado | Valor | Fonte | Placa | Procedência | conflict |
|---|---|---|---|---|---|---|
| pcie.interface | Interface do sistema | "PCIe 5.0 x16" | S02 p. 3 (System Interface); S09; S11; S12; S08; S06; S05 (Gen 5, Tab. 4 via nota existente) | RTX PRO 6000 WS | confirmed | false |
| pcie.gen5.claim | Afirmação da NVIDIA sobre Gen 5 | "Support for PCIe Gen 5 provides double the bandwidth of PCIe Gen 4" | S02 p. 1 e p. 2 | RTX PRO 6000 WS | confirmed | false |
| pcie.motherboard | Requisito mínimo de placa-mãe | "PCI Express (PCIe) x16 slot" | S01 p. 3 | família RTX PRO Blackwell | confirmed | false |
| pcie.slot.adapter | Ligação física do conector PCIe | "The card's PCIe slot is connected via a customized pinout adapter." (a fonte não detalha mais; a foto 7-37 mostra os dedos de ouro do PCIe saindo da carcaça) | S06 | RTX PRO 6000 WS | confirmed | false |
| dim.formfactor | Formato | "5.4" H x 12" L, dual slot, extended height" | S02 p. 3; S03 ("5.4" H x 12.0" L, dual slot"); S11 ("5.4" H x 12" L, XHFL Dual Slot") | RTX PRO 6000 WS | confirmed | false |
| dim.mm.hl | Altura x comprimento em mm | 137 mm x 304 mm (12,0 pol = 304,8 mm; 5,4 pol = 137,2 mm) | S09 ("304 mm (12.0 in) ... 137 mm (5.4 in)"); S08; S12 (304 mm) | RTX PRO 6000 WS | confirmed | false |
| dim.mm.thickness | Espessura | 42 mm (1,7 pol) em S09; 40 mm em S08 | S09; S08 | RTX PRO 6000 WS | confirmed | **true** (K3) |
| dim.weight | Peso | 1,860 kg (4,1 lb) em S09; "4 pounds, 3 ounces" (= 1,899 kg) em S07 | S09; S07 | RTX PRO 6000 WS | confirmed | **true** (K4) |
| slot.count | Slots ocupados | 2 (dual-slot); exige tirar duas tampas de slot vizinhas | S01 p. 8 e p. 9; S02 p. 3; S09 ("2 slots"); S12 ("Total Slot Width 2") | RTX PRO 6000 WS | confirmed | false |
| out.displayport | Saídas de vídeo | 4x DisplayPort 2.1b (a página S03 escreve "4x DisplayPort 2.1"); o guia mostra 4 conectores na plaqueta | S02 p. 1 e p. 3; S01 p. 13 (figura); S03 | RTX PRO 6000 WS | confirmed | false |

### 2.3 Memória

| id | Dado | Valor | Fonte | Placa | Procedência | conflict |
|---|---|---|---|---|---|---|
| mem.capacity | Capacidade e tipo | 96 GB GDDR7 com ECC | S02 p. 3; S05 p. 12 e p. 14 | RTX PRO 6000 WS | confirmed | false |
| mem.bus | Largura do barramento | 512 bits | S02 p. 3; S05 p. 14 (Tabela 1); S09; S12 | RTX PRO 6000 WS | confirmed | false |
| mem.rate | Taxa por pino | 28 Gbps | S05 p. 12 e p. 14; S10 (barramento de 512 bits a 28 Gbps, parafraseado pelo resumo); S08 ("1750 MHz (28 Gbps effective)") | RTX PRO 6000 WS | confirmed | false |
| mem.bandwidth | Largura de banda | 1.792 GB/s | S02 p. 3; S05 p. 14; S08 ("1.79 TB/s") | RTX PRO 6000 WS | confirmed | false |
| mem.packages.total | Locais de memória na placa | "We counted 32 total memory locations, which means that they are 3GB memory modules." | S06 (texto do teardown) | RTX PRO 6000 WS | confirmed (uma fonte de teardown) | false |
| mem.packages.back | Memórias no verso | "We counted 16 memory modules on the back with the clay type of thermal pads." | S06 | RTX PRO 6000 WS | confirmed | false |
| mem.packages.front | Memórias na frente | 16 (32 menos 16; **não dito pela fonte**) | conta sobre S06 | RTX PRO 6000 WS | derived | false |
| mem.chip.density | Densidade por chip | 3 GB = 24 Gbit (96 GB / 32 chips; S06 diz "3GB memory modules"). A faixa de densidades do GDDR7 no JEDEC é "16 Gbit to 32 Gbit", que inclui 24 Gbit | S06; conta; S23 | RTX PRO 6000 WS | confirmed (3 GB, via S06); derived (24 Gbit) | false |
| mem.clamshell.generic | Definição de clamshell no GDDR7 | "clamshell configuration, where twice the number of chips are used (two on a single 32bit interface)"; o JEDEC fala em "2-Channel mode to double system capacity" | S24; S23 | padrão genérico | derived | false |
| mem.clamshell.card | A placa usa clamshell? | **A palavra "clamshell" não aparece em nenhuma fonte aberta sobre a placa.** A conta fecha: 16 controladores de 32 bits (S05 p. 8, via nota existente) x 2 chips por controlador = 32 chips, o que bate com os 32 locais contados em S06. É dedução, não afirmação de fonte | conta sobre S05, S06, S24 | RTX PRO 6000 WS | derived | false |
| mem.hypothesis.24x32Gb | Hipótese "24 chips de 32 Gb" | **Não sustentada.** 24 chips de 32 bits seriam 768 bits, e o datasheet dá 512 bits. S06 conta 32 locais, não 24. Nenhuma fonte cita 24 chips. A conta que fecha é 32 chips x 3 GB (24 Gbit) | S02; S06; conta | RTX PRO 6000 WS | derived | false |

### 2.4 Cooler (a própria placa)

| id | Dado | Valor | Fonte | Placa | Procedência | conflict |
|---|---|---|---|---|---|---|
| cool.nvidia.name | Solução térmica segundo a NVIDIA | "Double-flow-through" (tabela); "Double flow through thermal design" (Key Features); "double-flow-through cooling design ... to sustain peak performance under 600W power loads" | S02 p. 1, p. 2, p. 3; S03; S11 | RTX PRO 6000 WS | confirmed | **true** (K10, só de nome) |
| cool.fans | Ventiladores | 2 ventiladores grandes na frente: "a 2-slot card with 2 large fans on the front"; "two-fan, two-slot, blow-through cooler"; "dual-axial fan layout"; ficha "2 Fans" | S06; S10; S08; S12 | RTX PRO 6000 WS | confirmed | false |
| cool.flow | Fluxo de ar | "The design is full flow-through, which pushes air straight through the card rather than into a PCB." (S06). "It draws air in from beneath the card and vents it out of the top." (S13). Na ficha da Puget, "Open Air Type" (S09) | S06; S13; S09 | RTX PRO 6000 WS | confirmed | **true** (K10, nomes) |
| cool.pcb.position | Posição da placa de circuito | no centro do cooler, entre as duas pilhas de aletas: "The PCB is in the center of the card and you can see where the fins start to get taller." | S06; fotos 13-32 e 15-7 (ver seção 3) | RTX PRO 6000 WS | confirmed | false |
| cool.top.vents | Saída superior | "The top of the RTX Pro 6000 retains the angle on the card's vented slats." | S06 | RTX PRO 6000 WS | confirmed | false |
| cool.vc | Câmara de vapor | "bilateral 3D vapor chambers sandwiched between dual heatsinks and fans" (S07); "Each fan is engineered to push airflow through the full-length 3D vapor chamber" (S08). S06 não cita câmara de vapor nem heatpipes no texto | S07; S08 | RTX PRO 6000 WS | confirmed | **true** (K5: plural contra singular; número não confirmado) |
| cool.shroud | Carcaça | "aluminum shroud" que "channels air efficiently across the fin stack" | S08 | RTX PRO 6000 WS | confirmed | false |
| cool.kinship | Parentesco com o cooler da 5090 | "nearly identical to the GeForce RTX 5090" (S10, sobre a carcaça); a ficha S09 diz que usa o mesmo tipo de cooler da RTX 5090 | S10; S09 | RTX PRO 6000 WS (afirmação de revisores) | confirmed (como afirmação do revisor; não é medida) | false |
| cool.heatpipes | Heatpipes (número, diâmetro) | **não encontrado** para a RTX PRO 6000 | n/a | RTX PRO 6000 WS | lacuna | n/a |
| cool.fins | Material e número de aletas | **não encontrado** | n/a | RTX PRO 6000 WS | lacuna | n/a |

### 2.5 Placa de circuito, memória, VRM e interface térmica (teardown da própria placa)

| id | Dado | Valor | Fonte | Placa | Procedência | conflict |
|---|---|---|---|---|---|---|
| pcb.density | Densidade | "The PCB is crazy dense, which is an engineering challenge."; "lots of little tiny components" | S06 | RTX PRO 6000 WS | confirmed | false |
| pcb.layers | Camadas do PCB | **não encontrado** | n/a | RTX PRO 6000 WS | lacuna | n/a |
| pcb.count | Número de placas de circuito | **não dito** no texto de S06 (só "customized pinout adapter" para o PCIe) | S06 | RTX PRO 6000 WS | lacuna | n/a |
| vrm.inductors | Indutores e pads | "half of the inductors are actually covered by a thermal pad"; "One of them only had about a third of the inductor covered." | S06 | RTX PRO 6000 WS | confirmed | false |
| vrm.phases | Número de fases do VRM | **não encontrado** (S06 não cita fases nem controlador) | n/a | RTX PRO 6000 WS | lacuna | n/a |
| tim.die | Interface térmica do die | "Pulling off the PCB, we were expecting to see liquid metal, but we saw thermal paste instead." (a 5090 FE usa metal líquido, ver 2.6). A foto 15-7 mostra, na base do dissipador, uma mancha retangular que parece resíduo de pasta | S06; foto 15-7 | RTX PRO 6000 WS | confirmed | false |
| tim.memory | Interface térmica das memórias | pads "clay type"; "making clear contact, though we did see some pads that were smashed over the sides a bit" | S06; fotos 15-7 e 18-13 | RTX PRO 6000 WS | confirmed | false |
| tim.thickness | Espessura e material exato dos pads | **não encontrado** | n/a | RTX PRO 6000 WS | lacuna | n/a |

### 2.6 Placa irmã: RTX 5090 Founders Edition (mesmo chip GB202; tudo `derived`)

| id | Dado | Valor | Fonte | Placa | Procedência | conflict |
|---|---|---|---|---|---|---|
| fe5090.size | Tamanho | "2-slot, 304mm long x 137mm high x 2-slot wide" | S15; S16 (304 mm, 137 mm, "2-Slot"); S17 | RTX 5090 FE | derived | **true** (K9, S16 também diz "3-slot card (61mm)" numa seção) |
| fe5090.tgp | Potência | 575 W | S16 | RTX 5090 FE | derived | false |
| fe5090.power | Alimentação | S16: "4x PCIe 8-pin cables (adapter in box) OR 1x 600 W PCIe Gen 5 cable". S17: "tweaked 12VHPWR connector". S22 (vazamento): "single 16-pin connector based on the newest 12V-2x6 standard" | S16; S17; S22 | RTX 5090 FE | derived | **true** (K7, nome) |
| fe5090.cooler.flow | Fluxo | "revolutionary new double flow through design" (S15); "dual-blowthrough configuration" (S17); "two-thirds blow-through cooling system" (S18, como afirmação da NVIDIA) | S15; S17; S18 | RTX 5090 FE | derived | **true** (K10) |
| fe5090.cooler.vc | Câmara de vapor e heatpipes | "A 3D Vapor Chamber with integrated heat pipes and active fins" (S16); "3D vapor chamber with artery wicks" (S18); "copper heat pipes running all along the side of the VC" (S19); "heatpipes extend horizontally through the fin stacks each side of the central PCB" (S17) | S16; S18; S19; S17 | RTX 5090 FE | derived | false |
| fe5090.tim | Interface térmica | "Liquid Metal thermal interface material (TIM)" (S15); metal líquido no die com "custom rubber gasket" (S18); "slim rubber ring", placa de contato niquelada (S17) | S15; S18; S17 | RTX 5090 FE | derived | false |
| fe5090.pcb.parts | Divisão da placa de circuito | "a unique 3-piece PCB" (S15). S20: "sliced up the PCB into four separate parts". S19 lista placa principal, filha de PCIe, filha de I/O e PCB flexível | S15; S20; S19 | RTX 5090 FE | derived | **true** (K6) |
| fe5090.pcb.link | Ligação entre a placa e o PCIe | "a proprietary internal cable attaches PCB to PCIe connector" (S17); a GPU liga ao conector PCIe por um conector FPC fino, e o técnico não achou peça de reposição (S21, opinião de oficina de reparo) | S17; S21 | RTX 5090 FE | derived | false |
| fe5090.mem | Memória | 32 GB GDDR7, 512 bits (S16). Vazamento pré-lançamento: "a total of 16 GDDR7 sites which confirm up to 32 GB" (S22). Conta: 16 x 32 bits = 512 bits; 32 GB / 16 = 2 GB por chip | S16; S22 | RTX 5090 FE | derived | false |
| fe5090.vrm | Fases do VRM | só estimativa de vazamento pré-lançamento: "around 30 VRM phases" (S22). **Nenhuma contagem de teardown com a placa de varejo foi aberta** | S22 | RTX 5090 FE | derived (fraco) | false |

---

## 3. Fotos do teardown da própria placa (S06)

Cinco imagens do artigo da GamersNexus foram baixadas e vistas. A página não tem legenda nem texto alternativo; as descrições abaixo são do que se vê nas imagens. Prefixo comum das URLs:

`https://gamersnexus.net/u/styles/large_responsive_no_watermark_/public/inline-images/NVIDIA%20RTX%20PRO%206000%20Blackwell%20Benchmarks%20%26%20Tear-Down%20_%20Thermals%2C%20Gaming%2C%20LLM%2C%20%26%20Acoustic%20Tests%20`

| Sufixo | O que se vê |
|---|---|
| `9-8%20screenshot.png.webp` | Placa montada com o cabo adaptador na mão do apresentador; o cabo termina em vários plugues grandes pretos do lado da fonte (três a quatro visíveis; contagem não nítida). O conector de 16 pinos da placa não aparece nítido. |
| `7-37%20screenshot.png.webp` | Lado das saídas: plaqueta com 4 DisplayPort, etiqueta "PRO 6000 96GB", etiqueta de modelo "RTX PRO 6000" e "Made in Vietnam". Ao fundo, os dedos de ouro do PCIe saindo da placa. |
| `13-32%20screenshot.jpg.webp` | Placa de circuito já fora da carcaça, entre as duas pilhas de aletas; conector placa a placa dourado numa ponta; restos brancos de pad térmico sobre os componentes. |
| `15-7%20screenshot.png.webp` | Base do dissipador, vista de dentro: área de contato do chip com mancha retangular que parece resíduo de pasta térmica, faixas de pad em volta, pilhas de aletas dos dois lados. |
| `18-13%20screenshot.png.webp` | Borda da placa de circuito: pacote do GPU no alto, pads brancos grandes sobre componentes, fileira de indutores com resíduo de interface térmica, circuito integrado com marcação parcialmente legível. A marcação não foi confirmada, então não se registra fabricante. |

Direitos das imagens: da GamersNexus. Não foram copiadas para o repositório; a lista serve só de referência.

---

## 4. Conflitos (`conflict: true`)

Duas ou mais leituras registradas; nenhuma foi descartada.

| Código | Assunto | Leitura A | Leitura B (e C, D) | Observação |
|---|---|---|---|---|
| K1 | Nome do conector de energia da RTX PRO 6000 WS | "1x PCIe CEM5 16-pin" (S02, S11, S13) e "16-pin PCIe Gen5 connector" (S01) | "12V-2x6" (S09, S12); "12VHPWR cable" (S06) | S14 diz que 12V-2x6 é revisão do 12VHPWR com plugue e cabo iguais; a mudança está nos soquetes. Pode ser só nomenclatura, mas nenhuma fonte aberta mostra a marcação "H+" ou "H++" do soquete da placa. O número de pinos (16) não diverge. |
| K2 | Acessório de energia na caixa | S01 p. 5: 1x cabo "4x PCIe 8-pin (PSU) to 1x PCIe Gen5 16-pin (GPU)" | S11: lista "One (1) Auxiliary Power Cable" e a imagem do acessório tem o rótulo "Auxiliary Power Cable - 8-Pin to Dual 6-Pin Adapter" | S01 é o documento do fabricante e é coerente com S07 (4x 8 pinos) e S16 (adaptador da 5090). O rótulo de S11 pode ser erro de cadastro, mas isso é suposição; fica registrado como conflito. |
| K3 | Espessura da placa | 42 mm (S09) | 40 mm (S08) | A NVIDIA só diz "dual slot" (S02). |
| K4 | Peso | 1,860 kg (S09) | 4 lb 3 oz = 1,899 kg (S07) | Diferença de cerca de 2%. |
| K5 | Câmaras de vapor do cooler | "bilateral 3D vapor chambers" (plural, S07) | "the full-length 3D vapor chamber" (singular, S08); S06 não cita | Número não confirmado. |
| K6 | Número de partes da placa de circuito da 5090 FE | "unique 3-piece PCB" (NVIDIA, S15) | "four separate parts" (S20); S19 lista 4 itens, contando o PCB flexível | Pode ser contagem diferente (com ou sem o flexível). Placa irmã, `derived`. |
| K7 | Nome do conector da 5090 FE | "tweaked 12VHPWR" (S17) | "12V-2x6" (S22, vazamento); S16 fala em "1x 600 W PCIe Gen 5 cable" | Placa irmã. |
| K8 | RT TFLOPS da RTX PRO 6000 WS | 380 (S05, Tabela 1, p. 14) | 382 (S02 p. 3, "RT Core Performance") | Divergência entre dois documentos da NVIDIA. Fora do escopo de energia e calor, mas registrada. |
| K9 | Largura em slots da 5090 FE na página da NVIDIA | "2-Slot" (tabela de especificações de S16) | "3-slot card (61mm)" (seção de folga de gabinete da mesma página S16) | Inconsistência interna da fonte. Não afeta a RTX PRO 6000 (S01 e S02 dizem dois slots). |
| K10 | Nome do fluxo de ar | PRO 6000: "Double-flow-through" (NVIDIA, S02); "full flow-through" (S06); "double-flow through active cooling" (S07) | PRO 6000: "blow-through" (S10); "Open Air Type" (S09). 5090 FE: "two-thirds blow-through" (S18, como dito pela NVIDIA); "dual-blowthrough" (S17) | Nomes diferentes para o mesmo tipo de cooler, ou desenhos diferentes? As fontes não esclarecem. S10 e S09 afirmam que o cooler da PRO 6000 é parecido com o da 5090. |

---

## 5. Contas conferidas

| Conta | Resultado |
|---|---|
| 512 bits x 28 Gbps / 8 = 1.792 GB/s | fecha com S02, S05 e S10 (28 Gbps e 512 bits citados em S10) |
| 96 GB / 32 chips = 3 GB = 24 Gbit; 32 chips x 16 bits = 512 bits | fecha **supondo** que cada chip trabalhe em 16 bits (modo clamshell). O "16 bits por chip" não está em nenhuma fonte da placa; é dedução (derived) |
| 16 controladores de 32 bits (S05 p. 8, pela nota existente) x 2 chips por controlador = 32 chips | fecha com a contagem de S06 (32 locais) e com a definição de clamshell em S24 |
| 24 chips x 32 Gb = 96 GB (hipótese do pedido) | capacidade fecha (24 x 4 GB), mas 24 x 32 bits = 768 bits, e o datasheet dá 512 bits. **Não fecha** com a largura do barramento e não casa com os 32 locais de S06 |
| 4 conectores de 8 pinos x 150 W = 600 W | igual ao 600 W de S02 (150 W por conector: S04 p. 5; 4 x 8 pinos: S01 p. 5) |
| Soma teórica slot + conectores = 75 W + 600 W = 675 W | passa dos 600 W da placa. **Nenhuma fonte diz como os 600 W se dividem entre slot e conector.** Registrado como lacuna, sem conclusão |
| Conector 12V-2x6 "até 600 W" (S14) contra TBP 600 W (S02) | igual (no limite do conector) |
| 24.064 núcleos CUDA x 2 x 2,617 GHz = 125,95 TFLOPS | fecha com o "126 TFLOPS" de S02 (boost de 2617 MHz em S05 p. 14) |
| 24.064 núcleos CUDA / 188 SMs = 128 por SM | fecha com S05 p. 14 (Tabela 1) |
| MIG: 4 x 24 GB = 2 x 48 GB = 1 x 96 GB | fecha com S02 p. 3 |
| 5,4 pol = 137,2 mm; 12,0 pol = 304,8 mm | bate com 137 x 304 mm de S08 e S09 |
| Página do produto (S03) contra datasheet (S02) | iguais em 600 W, 5,4" x 12", dois slots, 4 DisplayPort, 96 GB, 1.792 GB/s |
| RT TFLOPS: 380 (S05) contra 382 (S02) | **não fecha** (K8) |
| Peso: 1,860 kg = 4,10 lb (S09, consistente consigo mesmo); 4 lb 3 oz = 1,899 kg (S07) | duas fontes diferem em cerca de 2% (K4) |
| 5090 FE: 16 chips x 32 bits = 512 bits; 32 GB / 16 = 2 GB por chip | fecha (derived) |

---

## 6. O que não foi encontrado

- **Divisão da corrente entre o slot PCIe (75 W, regra geral em S04) e o conector de 16 pinos** para esta placa. Nenhuma fonte aberta traz medição nem documento da NVIDIA com essa divisão.
- Ficha da NVIDIA com **corrente por pino** ou mapeamento dos pinos do conector. O datasheet (S02) só dá o nome do conector.
- **Número de fases do VRM** da RTX PRO 6000, controlador e estágios de potência. S06 só fala dos indutores. Na 5090 FE, nenhum teardown da placa de varejo foi aberto (ver seção 7).
- **Camadas do PCB**, para a RTX PRO 6000 e para a 5090 FE.
- **Número de placas de circuito** da RTX PRO 6000 e como se ligam (S06 só cita o adaptador de PCIe).
- Interior do cooler da RTX PRO 6000: número e diâmetro dos heatpipes, número de câmaras de vapor (K5), material e número de aletas, ventiladores (modelo, diâmetro).
- **Posição exata** dos 32 pacotes de memória em relação ao GPU, fabricante e código das memórias da RTX PRO 6000.
- A palavra "clamshell" em qualquer fonte sobre a RTX PRO 6000. Também não achei fonte que diga que os chips operam em 16 bits.
- Espessura e material exato dos pads (S06 só diz "clay type").
- Para que serve o "Enhanced Straight Extender" que vem na caixa (S01 só lista).
- Marcação "H+" ou "H++" do soquete de 16 pinos da placa (resolveria K1).
- Documento de teardown de terceiros com fotos legendadas de todas as faces da placa. O S06 tem fotos, mas sem legenda, e só cinco foram vistas.
- Data de publicação de S15 e S16 (a NVIDIA não mostra no resumo lido).
- O "Power Guidelines" da NVIDIA (S04) é de 2022 e não lista a RTX PRO 6000. Não achei, nesta rodada, versão mais nova do documento que a inclua.

## 7. Fontes tentadas e não abertas (nenhum dado foi aproveitado)

Falharam (403, 402, 429, redirecionamento ou resumo truncado): TechPowerUp (GPU database da placa, matérias sobre vazamento de PCB, sobre os módulos de 3 GB e as análises da 5090 FE), Tom's Hardware (duas matérias sobre o PCB da 5090 FE e a da Northridge Fix), VideoCardz, Guru3D, TweakTown, LTT Labs, Noobfeed, Igor's Lab, Hardforum, inkl, topcpu.net, JEDEC (jedec.org), AnandTech.

**Pistas para quem for atrás (não são fatos desta rodada).** Os resumos de busca trouxeram, sem que eu abrisse as páginas: contagens divergentes de fases do VRM da 5090 FE (30 e 34 num lado, 19 mais 8 no outro), um vazamento citando PCB de 14 camadas na 5090 e um review que fala em três placas de circuito e 32 chips de 3 GB na RTX PRO 6000. Tudo isso precisa ser aberto e conferido antes de virar fato.

---

## 8. Lacunas para o `architecture-inferencer` (skill `gpu-assembly-proposal`)

Sem suposição: o que falta, e o que já é restrição confirmada.

**Restrições confirmadas da RTX PRO 6000 WS** (podem entrar como `confirmed` no `card.spec.json`, com a fonte indicada):
- 600 W de potência total da placa (S02); 1 conector "PCIe CEM5 16-pin" na borda superior (S02, S01); adaptador de 4x 8 pinos na caixa (S01).
- PCIe 5.0 x16 (S02); 5,4" x 12" (cerca de 137 x 304 mm), dois slots (S02); 4 DisplayPort 2.1b (S02).
- 96 GB GDDR7 ECC, 512 bits, 28 Gbps, 1.792 GB/s (S02, S05); 32 locais de memória de 3 GB, 16 no verso (S06).
- 2 ventiladores na frente, cooler "double-flow-through", PCB no centro entre duas pilhas de aletas (S02, S06); pasta térmica no die, pads nas memórias e em parte dos indutores (S06).

**Lacunas (viram `inferred` ou pendência):**
1. Número de fases, controlador e estágios de potência do VRM, e onde ficam (frente ou verso, em volta do GPU).
2. Camadas do PCB e se a placa é uma peça só ou várias (a 5090 FE tem 3 ou 4 partes, K6; na PRO 6000, só se sabe do adaptador de PCIe).
3. Heatpipes e câmara de vapor da PRO 6000: quantidade e traçado. A 5090 FE (derived) tem câmara de vapor com heatpipes de cobre pelas laterais, mas dado da 5090 não prova a PRO 6000.
4. Posição dos 16 pacotes de memória da frente em relação ao GPU.
5. Mapeamento dos 12 pinos de potência do conector até o VRM e o papel dos 4 pinos de sinal; divisão slot x conector (75 W do slot só é regra geral, S04).
6. Espessura, material e área dos pads térmicos; material do dissipador.
7. Orçamento de potência: fechar GPU + 32 chips GDDR7 + VRM + ventiladores dentro de 600 W. Só o total (600 W) é confirmado.
8. Dados da 5090 FE que o inferencer pode usar como análogo (`derived`, sempre com o selo): câmara de vapor com heatpipes, PCB dividido em partes ligadas por cabo/FPC, metal líquido (**a PRO 6000 usa pasta**, então esse ponto não se transfere).
9. O "Enhanced Straight Extender" da caixa: função desconhecida; não modelar sem fonte.
