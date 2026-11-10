# Fontes do hardware físico (rodada de 2026-11-09)

> **STATUS: auditada com ressalvas em 2026-11-09** (`harness/qa/fact-check-fisico.md`). O `fact-checker` reabriu o datasheet (leitura direta), a Gamers Nexus, a Jon Peddie, a Puget e as duas páginas NVIDIA da RTX 5090. As demais fontes **não foram reabertas**. Naquela data ninguém tinha visto as imagens nem o vídeo do teardown. **Superado em parte em 2026-11-10:** as fotos foram catalogadas (`harness/spec/references/index.md`) e as seções 14 a 17 foram auditadas em `harness/qa/fact-check-fisico-atos-0-3.md`; o vídeo continua não visto.

Convenções desta rodada:
- Todas as páginas foram lidas por resumo automático (WebFetch). O resumo extrai trechos, mas não é leitura humana da página. Os dois PDFs da NVIDIA foram lidos como imagem de página (ferramenta Read), e a tabela de especificações foi lida visualmente.
- "**só snippet**" = apareceu apenas no resumo da busca, a página não foi aberta ou veio bloqueada. **Não vale como fato.** Fica registrado para o `fact-checker` ou o grupo reabrir.
- Procedência: `confirmed` = fonte oficial NVIDIA sobre esta placa ou teardown/foto desta placa. `derived` = placa irmã (RTX 5090 Founders Edition, mesmo GB202) ou geração anterior. Revisões de terceiros sobre esta placa (Jon Peddie, Puget, sabareesh) ficam como `derived`, com a fonte nomeada, por recomendação do `fact-checker`: a classe "confirmed (terceiro)" usada na coleta não existe na regra do projeto. Está aberta para o humano a decisão de `confirmed` incluir "observação direta desta placa por terceiro identificado".
- Acesso: 2026-11-09 para tudo.
- Variante: "Workstation Edition" (600 W, 2 ventiladores). Max-Q (300 W, blower) e Server são outros coolers e não entram.

## 1. NVIDIA, datasheet da RTX PRO 6000 Blackwell Workstation Edition (PDF)
URL: https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf (`confirmed`)
Aberto e lido como imagem (3 páginas). Rodapé: "5349469. JUN26" (revisão de junho de 2026). Link descoberto na página do produto ("View Datasheet").

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Conector de energia | "Power Connector: 1x PCIe CEM5 16-pin" | tabela Specifications, p. 3 |
| Potência | "Power Consumption: Total board power: 600 W" | p. 3 |
| Form factor | "5.4" H x 12" L, dual slot, extended height" | p. 3 |
| Térmica | "Thermal Solution: Double-flow-through" | p. 3 |
| Fluxo de ar | "double-flow-through cooling system channels airflow through dual axial pathways" | p. 1 |
| Cooler | "innovative double-flow-through cooling design ... sustain peak performance under 600W power loads" | p. 2 |
| Saídas | "Display Connectors: 4x DisplayPort 2.1b" | p. 3 |
| Interface | "System Interface: PCIe 5.0 x16" | p. 3 |
| Memória | "GPU Memory: 96 GB GDDR7 with ECC"; "Memory Interface: 512-bit"; "Memory Bandwidth: 1792 GB/s" | p. 3 |
| Núcleos CUDA | "NVIDIA CUDA Cores: 24,064" | p. 3 |
| Capa | render da placa: shroud preto com duas áreas de grade fina (o auditor não distinguiu pás; **face não identificada**, pode ser a de saída do ar), texto "RTX PRO 6000" na face superior e logotipo NVIDIA na lateral | p. 1 (observação visual) |

Não consta no datasheet: peso, dimensões em mm, conteúdo da caixa (adaptador), ventiladores (quantidade, diâmetro), material.
Há uma cópia equivalente no PNY (https://www.pny.com/File%20Library/Company/Support/Product%20Brochures/NVIDIA%20RTX/English/NVIDIA-RTX-PRO-6000-Blackwell-Workstation-Edition.pdf), com o mesmo texto da p. 1 e o código PNY VCNRTXPRO6000B-PB. Só a p. 1 foi lida.
Conferência: 24.064 / 128 = 188 SMs, igual ao whitepaper já registrado. 512 bits / 8 = 64 B por ciclo de interface; 1792 GB/s / 64 B = 28 Gb/s por pino (`derived`, conta nossa).

## 2. NVIDIA, página do produto (já registrada, só o que é novo)
URL: https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/ (`confirmed`)
- "5.4” H x 12.0” L, dual slot"; "Thermal: Double Flow Through"; "4x DisplayPort 2.1". Confirma a leitura anterior. Não informa peso nem conector.

## 3. Gamers Nexus, "NVIDIA RTX PRO 6000 Blackwell Benchmarks & Tear-Down" (teardown da própria placa)
URL: https://gamersnexus.net/gpus/nvidia-rtx-pro-6000-blackwell-benchmarks-tear-down-thermals-gaming-llm-acoustic-tests (`confirmed`, teardown desta placa)
> As linhas "Ordem de desmontagem" e "Saída de ar" da tabela abaixo são paráfrases de 2026-11-09 e foram **superadas pelos trechos literais da seção 15** (a peça do passo 1 é o bracket de I/O; o que sai para cima e para longe é o ar, não a aba). A linha "Aletas" ("placa do PCB") continua próxima do literal.
Página aberta (resumo automático da seção de teardown). A página é texto da transcrição de vídeo, com 35 imagens sem legenda. Não li o vídeo.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Formato | "The RTX Pro 6000 we tested is a 2-slot card with 2 large fans on the front" | teardown |
| Ordem de desmontagem | 1) tira a placa traseira (back plate); 2) um parafuso e puxa a moldura externa; 3) parafusos ao redor do centro e as tampas centrais; 4) solta o grampo (clamp) do suporte do slot PCIe e retira o adaptador PCIe; 5) descola uma placa (plate) para expor o PCB; 6) retira cabos flat (ribbon) e parafusos da mola de pressão (leaf spring) para chegar à GPU; 7) puxa o PCB e limpa a pasta da GPU | teardown |
| Parafusos | só "um parafuso" da moldura e "parafusos ao redor do centro". Tipos e contagem: **não informados** | teardown |
| Memória (verso) | "16 memory modules on the back", sobre "clay type" thermal pads; "32 total memory locations". A fonte conclui na mesma frase: "which means that they are 3GB memory modules as that totals 96GB" (dedução da fonte, sem leitura de marcação do chip). A fonte não diz "16 na frente" nem que as 32 posições estão ocupadas | teardown |
| Interface térmica | "we were expecting to see liquid metal, but we saw thermal paste instead" | teardown |
| Densidade | PCB "crazy dense", "lots of little tiny components" | teardown |
| Pads | "half of the inductors are actually covered by a thermal pad. One of them only had about a third of the inductor covered." Frase ambígua (metade dos indutores ou metade de cada indutor): **não usar como contagem**. Um pad passou da borda do PCB | teardown |
| Posição do PCB | "The PCB is in the center of the card" | teardown |
| Fluxo | "The design is full flow-through, which pushes air straight through the card rather than into a PCB" | teardown |
| Substrato | "We also saw a massive GPU substrate" | teardown |
| Aletas | ficam mais altas onde termina a placa do PCB; leve depressão para reduzir perda de pressão. Material e contagem: não informados | teardown |
| Die | "GB 202-870-A1" (grafia da fonte, que chama de "SKU"; a marcação não foi lida em foto por nós), "This is a 5090 die, just a fuller version of it" | teardown |
| PCIe | "a customized pinout adapter" | teardown |
| Energia | "Like the 5090, the card uses a 12VHPWR cable" | teardown |
| Saída de ar | aberturas ("vented slats") anguladas para cima e para longe da placa | teardown |

Não consta: diâmetro dos ventiladores, câmara de vapor e heatpipes, fabricante e código dos chips de memória, fases do VRM, dimensões do package, material do shroud, peso.

> **Correção de 2026-11-09 (catálogo de fotos).** O artigo tem 75 imagens no corpo, não 35; 38 mostram esta placa e uma (PCB) é da RTX 5090 FE. As fotos mostram que a peça retirada no passo 1 é o **bracket**: a fonte diz "back plate", mas não existe placa traseira lisa nesta placa. O passo 2 retira um aro fino. Catálogo em `harness/spec/references/index.md`.

## 4. Jon Peddie Research, "The Nvidia RTX Pro 6000 Blackwell Edition" (2025-11-17)
URL: https://www.jonpeddie.com/reviews/the-nvidia-rtx-pro-6000-blackwell-edition/ (`derived`: revisor que avalia a variante Workstation de 600 W, sem abrir a placa)

| Dado | Trecho ou valor | Observação |
|---|---|---|
| Peso | "tops out at a monstrous 4 pounds, 3 ounces", cerca de 60% mais pesada que a RTX Pro 6000 Ada (cerca de 2 lb 10 oz) | 4 lb 3 oz = 1.899 g (`derived`, conversão nossa). Ada: 2 lb 10 oz = 1.191 g |
| Cooler | "bilateral 3D vapor chambers sandwiched between dual heatsinks and fans"; legenda "double-flow through active cooling" | não é teardown, é descrição do revisor. A figura 3 é creditada "Source: Nvidia": pode existir ilustração oficial do cooler, **a localizar** |
| Energia | quatro cabos auxiliares de 150 W unidos por "Nvidia's 4-to-1 adapter" ligado à "central, topside interface" | indica adaptador 4x8 pinos para 16 pinos |
| Posição do conector | "this one connects from the top middle of the card" (não pela traseira) | |
| Tamanho | "notably thicker, longer, and wider" que a Ada | sem números |

## 5. Puget Systems, "NVIDIA RTX PRO 6000 Blackwell Workstation Content Creation Review"
URL: https://www.pugetsystems.com/labs/articles/nvidia-rtx-pro-6000-blackwell-workstation-content-creation-review/ (`derived`: juízo comparativo de revisor)
- "a two-fan, two-slot, blow-through cooler designed for use in desktop workstations"; "a housing nearly identical to the GeForce RTX 5090"; "configured to draw up to 600 Watts". A Max-Q é descrita como "a two-slot cooler in a blower-fan configuration" de 300 W.

## 6. NVIDIA, anúncio da GeForce RTX 50 (Founders Edition da RTX 5090)
URL: https://www.nvidia.com/en-us/geforce/news/rtx-50-series-graphics-cards-gpu-laptop-announcements/ (`derived`: placa irmã)

| Dado | Trecho | 
|---|---|
| Dimensões | "2-slot, 304mm long x 137mm high x 2-slot wide" |
| Cooler | "a revolutionary new double flow through design" |
| PCB e interface térmica | "Liquid Metal thermal interface material (TIM), and a unique 3-piece PCB" |
Não consta nessa página: câmara de vapor, ventiladores, conector. O artigo de design detalhado de que se falava (URL `.../rtx-50-series-founders-edition-design/`) deu **404**; o artigo de 2018 `geforce-rtx-founders-graphics-card-breakdown` é sobre a RTX 20 e não vale.

## 7. NVIDIA, página da GeForce RTX 5090
URL: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/ (`derived`)
- "A 3D Vapor Chamber with integrated heat pipes and active fins further increases thermal performance."
- "Advanced PCBs and thermal design provides double the airflow of a traditional graphics card configuration."
- Dimensões: "304 mm" x "137 mm", "2-Slot". Energia: "4x PCIe 8-pin cables (adapter in box) OR 1x 600 W PCIe Gen 5 cable". TGP 575 W.
- A mesma página, no guia de instalação: "Must have space for 12" (304mm) x 5.4" (137mm) x 3-slot card (61mm)" (ver conflitos).

## 8. Puget Systems, ficha da RTX 5090 Founders Edition
URL: https://www.pugetsystems.com/parts/Video-Card/NVIDIA-GeForce-RTX-5090-32GB-Founders-Edition-16029/ (`derived`)
- "304 mm (12.0 in)" x "137 mm (5.4 in)" x "42 mm (1.7 in)"; peso "1.825 kg (4.0 lbs)"; "12V-2x6"; "Slot Width: 2". Loja revendedora, não NVIDIA.

## 9. wccftech, "Hands-On With NVIDIA's ... GeForce RTX 5090 ... Compact PCB" (5090 FE)
URL: https://wccftech.com/hands-on-nvidia-powerful-geforce-rtx-5090-gpu-impressive-compact-pcb/ (`derived`)
- "16 GDDR7 memory chips scattered around it"; PCB "is equipped with a total of 30 phases"; GB202 "in the center of the main PCB, with a large IHS" (chip da semana 38 de 2024); conector 16 pinos (12V-2x6) "placed at an angle on the same board as the GPU"; PCB principal mais dois módulos (PCIe e saídas) ligados por "tiny connectors". Sem dimensões do PCB.

## 10. Notebookcheck, "Nvidia shares what makes the Founders Edition RTX 5090 special" (5090 FE)
URL: https://www.notebookcheck.net/Nvidia-shares-what-makes-the-Founders-Edition-RTX-5090-special.951354.0.html (`derived`, resumo de vídeo da NVIDIA por terceiro)
- "3D vapor chamber with artery wicks"; metal líquido no die "secured by a custom rubber gasket to prevent leaks that could damage the PCB"; "semi-pass-through design" com "two-thirds blow-through cooling system"; "modular PCB"; "repositioned power connector ports". Sem milímetros nem ventiladores.

## 11. Northridge Fix via gamegpu, gsmgotech e Notebookcheck (5090 FE)
URLs: https://en.gamegpu.com/iron/The-disassembly-of-the-RTX-5090-Founders-Edition-ended-with-the-death-of-the-card. ; https://www.gsmgotech.com/2025/10/nvidia-rtx-5090-founders-edition.html ; https://www.notebookcheck.net/Nvidia-RTX-5090-Founders-Edition-teardown-reveals-fragile-modular-design-that-repair-experts-call-a-disaster.1147864.0.html (`derived`; segunda mão do vídeo, que não foi visto)
- Projeto dividido em várias placas; o PCIe fica em módulo separado, ligado por um "thin flexible printed circuit (FPC) connector", frágil (um pino torto e outro quebrado). "a labyrinth of screws, brackets, and shields" (gsmgotech). Sem ordem de desmontagem, sem tipos de parafuso.

## 12. sabareesh.com, "4x RTX PRO 6000 Blackwell on Water" (conserto e water block)
URL: https://sabareesh.com/posts/blackwell-waterblock/ (`derived`: blog pessoal de quem abriu esta placa, "GB202, 96 GB GDDR7, 600 W"; baixa autoridade, uma passagem de leitura)
- Pads sobre memória e VRM; os GDDR7 do verso "also need cooling"; indutores (choke) marcados "85N" entre os MOSFETs do VRM e o núcleo; "multi-layer GPU PCB"; um choke saiu junto com o pad, descrito como "identical to the 23 still on the board" (pista de 24 indutores desse tipo, **não usar como contagem**). Aquece a placa a cerca de 90 °C antes de abrir. Sem tipos de parafuso nem contagem de fases. Fonte de baixa autoridade.

## 13. Só snippet (páginas não abertas; não valem como fato)
| Fonte | O que o snippet diz | Por que não abriu |
|---|---|---|
| TechPowerup, teardown da 5090 FE https://www.techpowerup.com/review/nvidia-geforce-rtx-5090-founders-edition-unboxing/4.html (e `.../nvidia-geforce-rtx-5090-founders-edition/5.html`) | 16 chips Samsung GDDR7 (K4VAF3257C-SC28); 19 fases GPU + 8 memória, DrMOS da MPS; GB202 ocupa quase 1/3 da placa; 12V-2x6 num canto; 4 parafusos do slot cover e 4 parafusos T6 do suporte metálico da GPU; placa principal ligada por FPC a duas placas (PCIe e saídas) | 403 |
| TechPowerup/Guru3D/TweakTown, vazamento de PCB da PRO 6000 (https://www.techpowerup.com/336219/..., https://www.guru3d.com/story/nvidia-rtx-pro-6000-blackwell-workstation-edition-pcb-layout-leak/, https://www.tweaktown.com/news/104854/...) | 16 pads por face, 32 no total, 3 GB cada; atribuição ao Max-Q ou ao Workstation diverge | 403 |
| VideoCardz https://videocardz.com/newz/nvidia-10k-rtx-pro-6000-blackwell-gpu-with-broken-pcie-connector-no-replacement-part-available e Tom's Hardware (mesmo caso) | PRO 6000 e 5090 FE "made up of three primary PCBs", um só para PCIe | 402 e corpo truncado |
| Tom's Hardware, "RTX Pro 6000 up close" | variantes Workstation, Max-Q e Server | corpo truncado |
| Tom's Hardware / TweakTown, 5090 FE (30 e 34 fases; 16+6+7; 14 camadas) | números de fases divergentes | truncado ou 403 |
| B&H (OEM) | "16 pin GPU power adapter" incluído; "6.1 lb" é peso de embalagem | não aberta |
| LTT Labs https://www.lttlabs.com/products/graphics-cards/nvidia-rtx-pro-6000-blackwell-workstation-edition | "Power Connections: 12V-2x6" | 403 |
| Club386/VideoCardz, RTX 6000D | 28 chips de 3 GB, 84 GB | outra placa, não usar |

## Conflitos entre fontes
1. **Interface térmica (`conflict: true`).** 5090 FE: NVIDIA diz metal líquido (fonte 6) e Notebookcheck descreve o metal líquido com junta de borracha (fonte 10). PRO 6000: o teardown da Gamers Nexus encontrou **pasta térmica** (fonte 3). Registro as duas. Para a PRO 6000, vale o teardown da própria placa (`confirmed`).
2. **Número de fases do VRM da 5090 FE (`conflict: true`).** 30 (wccftech, aberto) contra 19+8=27 (TechPowerup, só snippet) contra 34 (snippet que cita o verso do PCB). Nenhum número serve para a PRO 6000. A GN não contou fases.
3. **Espessura da 5090 FE (`conflict: true`).** Página NVIDIA da 5090: "2-Slot", mas o guia de instalação pede "3-slot card (61mm)"; Puget dá 42 mm de largura. O guia provavelmente reserva folga, mas isso é interpretação, não está na fonte.
4. **Nome do conector.** Datasheet da PRO 6000: "PCIe CEM5 16-pin". Gamers Nexus: "12VHPWR". Outras fontes: "12V-2x6". Não provei que o CEM5 16-pin do datasheet seja o mesmo que o 12V-2x6; é a leitura dos revisores. Registrar como `derived` até haver texto oficial.
5. **Quantidade de peças do PCB.** NVIDIA diz "3-piece" (5090 FE). Um snippet de busca falou em quatro partes com placa de I/O separada, sem URL aberta. Fica 3 partes (5090 FE), não confirmado na PRO 6000 por texto oficial. A GN cita adaptador PCIe, ribbon cables e "plate", compatível com várias placas, mas não conta peças.
6. **Atribuição do vazamento de PCB da PRO 6000** (Max-Q ou Workstation): só snippet, divergente.
7. **Resolução de "fluxo".** NVIDIA: "dual axial pathways"; Puget: "blow-through"; Jon Peddie: "double-flow through active cooling"; Notebookcheck (5090 FE): "two-thirds blow-through". Termos diferentes para o mesmo cooler, sem contradição numérica.

## Respostas por item (resumo)
1. Exterior: 5,4" x 12,0" = 137,2 x 304,8 mm (`derived`, conversão do datasheet; a 5090 FE tem 137 x 304 x 42 mm). Peso 1,9 kg (JPR, `derived`). Dois ventiladores na frente (GN, `confirmed`); "axiais" vem do datasheet ("dual axial pathways") e é `derived`. Dois caminhos de ar axiais, "double flow through". Traseira com placa traseira (GN) mais pilha de aletas (**superado**: a face B é grade com X central, e a peça que a GN chama de "back plate" é o bracket de I/O; ver seções 15 e 16). Conector 16 pinos no topo, posição "top middle" (JPR). Disposição dos DP e grade da bracket: lacuna.
2. Energia: 1x PCIe CEM5 16-pin, 600 W (datasheet). Adaptador: 4 x 150 W para 1 (JPR); a caixa não foi vista.
3. PCB: teardown da GN mostra adaptador PCIe separado, cabos flat e placa principal; três partes é comprovado só na 5090 FE (NVIDIA). Medidas do PCB: lacuna.
4. Memória: 16 módulos no verso e 32 posições (GN, `confirmed`). 3 GB por chip é dedução da própria GN (`derived`); 16 chips na frente e 32 chips montados também são `derived`. As fontes não excluem 24 chips de 4 GB. O arranjo em duas faces com 16 bits por chip (clamshell) é `inferred`: nenhuma fonte o descreve, e a 5090 FE usa um chip de 32 bits por controlador. Fabricante: lacuna na PRO 6000.
5. VRM: lacuna na PRO 6000. Apenas indutores "85N" (blog).
6. Térmica: pasta (GN), pads de argila sobre a memória, 3D vapor chambers bilaterais (JPR, descrição), aletas com depressão (GN). Diâmetro do ventilador, heatpipes: lacuna.
7. Package: "GB 202-870-A1" (GN). Dimensões do package/stiffener: lacuna.
8. Ordem: seção 3, sete passos da GN. Tipos de parafuso: lacuna (T6 só em snippet da 5090 FE).
9. Imagens: abaixo.

## Referências visuais (somente URLs)
- Datasheet NVIDIA, capa: render 3/4 superior da placa, mostra shroud, bracket e logotipo (URL da seção 1, p. 1).
- Gamers Nexus, teardown: 35 imagens (capturas do vídeo), sem legenda, da placa aberta ("placa traseira", que é o bracket de I/O conforme a seção 15, moldura, tampas centrais, PCB com memória no verso, aletas, pasta no die). Caminho base, host conforme a página: `https://gamersnexus.net/u/styles/large_responsive_no_watermark_/public/inline-images/` mais o prefixo `NVIDIA RTX PRO 6000 Blackwell Benchmarks & Tear-Down _ Thermals, Gaming, LLM, & Acoustic Tests ` e o nome do arquivo (por exemplo `9-8 screenshot.png.webp`, `12-3 screenshot.png.webp`, `15-7 screenshot.png.webp`). **O conteúdo de cada imagem não foi visto por mim.** (Superado: o catálogo `harness/spec/references/index.md` descreve as imagens, e as seções 15 e 16 trazem o que foi visto em 2026-11-10.)
- Press kit/galeria NVIDIA: **não achado**.

## Lacunas desta rodada
- Dimensões do PCB principal, posição do GB202 e das placas-filhas na PRO 6000.
- Fabricante e código dos chips GDDR7 da PRO 6000; contagem na face frontal.
- Fases do VRM (GPU e memória), controladores, estágios de potência na PRO 6000.
- Câmara de vapor 3D e heatpipes na PRO 6000 confirmados só por texto de revisor (JPR); nenhum teardown da PRO 6000 os descreve. Diâmetro dos ventiladores, contagem de aletas.
- Material e acabamento do shroud e da moldura, textura da placa traseira.
- Disposição dos 4 DisplayPort na bracket, grade de exaustão na bracket.
- Ângulo do conector 16 pinos e posição exata (só "top middle", JPR).
- Conteúdo da caixa: **resolvido em 2026-11-10** pelo guia de início rápido oficial (seção 14). Resta o que o "Enhanced Straight Extender" da mesma tabela é (a tabela não explica).
- Dimensões do package do GB202 e do die visível; stiffener.
- Tipos de parafuso e quantidades.
- Peso oficial NVIDIA; o 1,9 kg vem de revisor.
- Teardowns da RTX 6000 Ada não buscados (fora do tempo).
- Fotos oficiais do press kit; TechPowerup, VideoCardz, Tom's Hardware, Guru3D e TweakTown bloquearam o acesso automático.

---

# Complemento de 2026-11-10 (F1, fatos físicos dos atos 0 a 3)

Método desta seção: o PDF do guia foi baixado e **lido como imagem de página** (ferramenta Read), então os trechos abaixo são leitura visual literal. Os trechos do teardown da Gamers Nexus vieram de **resumo automático dirigido (WebFetch) pedindo citação literal**, sem leitura humana da página: valem como o resumo entregou, e o `fact-checker` deve reabrir. Fotos: vistas por esta sessão em 2026-11-10 (gn-11, gn-29) e pelo catálogo `harness/spec/references/index.md`. Acesso: 2026-11-10 para tudo. Classe da Gamers Nexus: a frase literal do teardown desta placa é `confirmed`, como dizem a linha de procedência no alto deste arquivo, o cabeçalho da seção 3 e `harness/ARCHITECTURE.md`, seção 3. O que é leitura nossa de foto, contagem nossa ou identificação de peça é `derived`. (Corrigido em 2026-11-10: a primeira versão desta seção dizia "`derived`, sem exceção", por um erro do briefing da sessão principal, apontado pelo `fact-checker`.)

## 14. NVIDIA, "NVIDIA RTX PRO Blackwell Architecture, Quick Start Guide" (r14, 2025-07-18)
URL: https://images.nvidia.com/aem-dam/Solutions/design-visualization/quadro-product-literature/rtx-pro-blackwell-online-qsg-210x148mm-20250718-r14.pdf (`confirmed`, documento oficial NVIDIA; nome do arquivo "20250718 r14"; hospedado em images.nvidia.com). A data 2025-07-18 vem só do nome do arquivo. Acesso: 2026-11-10. Lido como imagem, páginas 1 a 14 do PDF (formato A5 paisagem); o `fact-checker` releu as p. 1 a 18 (a parte em inglês vai até a p. 15). Uma versão anterior do mesmo guia (https://images.nvidia.com/aem-dam/en-zz/Solutions/design-visualization/quadro-product-literature/nvidia-rtx-pro-blackwell-online-qsg.pdf, metadado de modificação 2025-03-25) só teve a capa lida; não é usada.

| Dado | Trecho literal | Onde (página do PDF) |
|---|---|---|
| Itens incluídos | tabela "Equipment: Included equipment with each NVIDIA RTX PRO Blackwell graphics card"; coluna "RTX PRO 6000 Workstation Edition": "Quick Start Card" = 1; "Auxiliary Power Cable (4x PCIe 8-pin (PSU) to 1x PCIe Gen5 16-pin (GPU) power adapter)" = 1; "Enhanced Straight Extender" = 1. A coluna "RTX PRO 6000 Max-Q Workstation Edition" traz "Auxiliary Power Cable (2x PCIe 8-pin (PSU) to 1x PCIe Gen5 16-pin (GPU) power adapter)" = 1 e "–" para o extender | p. 5 |
| Slots | "The RTX PRO 6000, RTX PRO 6000 Max-Q, RTX PRO 5000, RTX PRO 4500, RTX PRO 4000 SFF, and RTX PRO 2000 are dual-slot GPUs and will require removing two adjacent slot covers." | p. 8 (a p. 9 diz outra coisa: "will cover the adjacent slot") |
| Posição e tipo do conector | "Connect the auxiliary power cable from the power supply to the 16-pin PCIe Gen5 connector on the top edge of the RTX PRO 6000, or on the east edge of the RTX PRO 6000 Max-Q, RTX PRO 5000, RTX PRO 4500, or RTX PRO 4000 GPU." | p. 10, passo 8 |
| Quatro cabos | "For RTX PRO 6000, connect four separate PCIe 8-pin cables from the system power supply to the NVIDIA Quad PCIe 8-pin power adapter as necessary." | p. 10 |
| Aviso | "Attention: Use only the included NVIDIA power connector adapter for your NVIDIA RTX PRO graphics card. Ensure a secure connection by firmly plugging the power dongle into the graphics card." Nota: "Use the recommended power connector guidelines at www.nvidia.com/workstationpowerguidelines." | p. 12 |
| Saídas e bracket | página "Connecting To The Display": desenho do bracket da "RTX PRO 6000" com legenda "DisplayPort Connectors (x4)"; as quatro portas ficam em uma fileira, a chapa não tem grade de ventilação (a da Max-Q, no mesmo desenho, tem) | p. 13 (observação visual do desenho) |
| Desenho do conector | no passo 8, o desenho do encaixe mostra 16 posições: 12 grandes e uma fileira de 4 pequenas | p. 10 (observação visual do desenho, sem texto) |
| Placa | "PCI Express (PCIe) x16 slot" como requisito de placa-mãe | p. 3 |
| Ventiladores e conector | os desenhos mostram dois ventiladores numa face e o conector na borda superior, entre eles: apoio oficial para `card.fans` e para o "top middle" da Jon Peddie | p. 9 e 10 (observação visual do desenho, vista pelo `fact-checker`) |

Não consta no guia: potência da placa (o desenho não traz watts), nome "12VHPWR" ou "12V-2x6", peso, dimensões. Consta só "PCIe Gen5 16-pin". O guia **não resolve** a equivalência com "CEM5 16-pin" (datasheet), 12VHPWR (GN) ou 12V-2x6 (revendedores).
O documento "Power Guidelines for Workstation Products" (www.nvidia.com/workstationpowerguidelines, DA-07261-001_v11, abril de 2022) foi aberto pelo `spec-researcher` e **não serve** (afirmação não auditada: o `fact-checker` não abriu este documento nem a versão anterior do guia): a tabela vai até a RTX A6000 e não cita esta placa nem o conector de 16 pinos.
Conta (`derived`, nossa): 4 conectores de 8 pinos x 150 W = 600 W de capacidade nominal (150 W por 2x4: Intel 613768 Tabela 3-5, `standards-sources.md` seção 2). A NVIDIA não diz que o adaptador entrega 600 W nem que usa o teto de cada conector.

## 15. Gamers Nexus, trechos literais do teardown (releitura de 2026-11-10)
URL: a mesma da seção 3. Artigo de 2025-09-25; vídeo de 2025-06-24 (não visto). Resumo automático dirigido, pedindo citação literal (sem leitura humana). O `fact-checker` conferiu frase a frase em 2026-11-10, também por extração dirigida: as frases existem, na ordem abaixo, sem outro passo entre elas. A fonte usa apóstrofo curvo.

| Passo ou dado | Trecho literal |
|---|---|
| 1 | "Starting disassembly, we removed the card’s back plate." |
| 2 | "Then we removed a single screw, which allowed us to pull off the card’s exterior frame." |
| 3 | "From here, we removed some screws around the center of the card to remove the center covers." |
| 4 | "Next, we unscrewed the clamp that holds the PCIe slot to the card." e "Here’s a close look at the removed PCIe adapter." |
| 5 | "From here, we pried a plate off of the card, exposing the PCB." |
| 6 | "We then proceeded to remove ribbon cables and screws to the leaf spring to access the GPU." |
| 7 | "Pulling off the PCB, we were expecting to see liquid metal, but we saw thermal paste instead." e "Finally, we cleaned off the thermal paste off of the GPU, exposing the GB 202-870-A1 SKU." |
| Aletas mais altas | "The PCB is in the center of the card and you can see where the fins start to get taller." e, em seguida, "This indicates where the PCB plate ends." A fonte não explica "PCB plate": o termo aparece uma vez só, na descrição do exterior, antes da desmontagem; pode ser o próprio PCB ou a placa do passo 5 |
| Depressão nas aletas | "If you look at the backside of the card where the fans are, you’ll notice a slight depression down towards the middle of the fins.", seguido de "This is supposed to help with pressure drop." O texto não deixa claro qual face é essa |
| Saída de ar | "The top of the RTX Pro 6000 retains the angle on the card’s vented slats." e, na frase seguinte, "This projects the air out at an angle that’s up and away from the card." (o que sai para cima e para longe é o ar; a seção 3 parafraseou como se as abas fossem anguladas para cima; a fonte não diz que todo o ar sai por ali). gn-13 mostra duas fendas longas no painel do topo, ao lado do plugue |
| PCB | "The PCB is in the center of the card" |
| Fluxo | "pushes air straight through the card rather than into a PCB" |
| Memória | "We counted 16 memory modules on the back" e "32 total memory locations" |
| Adaptador | "The card’s PCIe slot is connected via a customized pinout adapter." |
| Outra face | "The other side of the card looks very similar to a 5090." |

Identificação do passo 1 (`derived`, por foto): o texto diz "back plate"; as fotos gn-14 a gn-16 do catálogo mostram que a peça removida é o **bracket de I/O** (chapa com as 4 DisplayPort e etiquetas). Confirmei em gn-11: chapa preta com 4 DisplayPort em fileira, parafusos visíveis (o catálogo conta 4), etiquetas "PRO 6000 96GB", código de barras e etiqueta NVIDIA.

## 16. Observações visuais desta rodada (2026-11-10)
- gn-11 (captura 7-37, GN, placa montada): "4 DisplayPort em uma fileira, igualmente espaçadas, sobre chapa preta lisa com etiquetas". Vista por esta sessão. O guia oficial (seção 14, p. 13) mostra o mesmo desenho.
- gn-29 (captura 13-38, GN, PCB em perspectiva entre as duas carcaças de aletas): vi o PCB central entre as duas pilhas de aletas, pads cinza cobrindo posições em volta do chip (cerca de 5 na esquerda, 5 na direita, 4 embaixo e 2 em cima, pads com resíduo cobrindo os chips), reforço preto em X sobre o verso do chip, dois conectores finos e um cabo flat saindo para a carcaça, conector de energia preto com cavidades na borda, fila de componentes quadrados na borda. O catálogo (`references/index.md`, seção e) descreve a mesma disposição: "16 chips de memória, contagem razoavelmente segura (faixa de 15 a 16)", em U: 5 de cada lado, 4 na borda superior, 2 na borda dos dedos PCIe. Fica `derived`, com faixa de 15 a 16.
- Catálogo (`references/index.md`, seção f): indutores "em fileira ao longo da borda superior, junto ao conector de energia" (gn-33, gn-36, gn-42), total visível "entre 10 e 20, sem contagem total segura". Não reconferi nesta rodada.
- Indutores, visto pelo `fact-checker` em 2026-11-10: gn-42 confirma uma fileira ao lado do conector de energia; gn-33 mostra indutores em duas bordas opostas do quadro, pelo menos 14 numa só foto. Não ficou claro se uma das fileiras de gn-33 é a de gn-42 vista de outro ângulo. A faixa "entre 10 e 20" do catálogo não serve.
- Memória no verso, recontada pelo `fact-checker`: gn-29 (5 à esquerda, 5 à direita, 4 na borda do conector de energia, 2 na borda oposta), gn-30 (os 4 da borda do conector, de perto) e gn-31 (a mesma disposição vista de cima). Os chips ficam nos quatro lados, então "em U" não descreve bem.
- gn-40, vista pelo `fact-checker` na segunda passada: uma fileira de 8 ou mais indutores junto à borda em degrau; ao lado, um CI com marca que parece "MPS" (leitura incerta a 52%; pista para a lacuna `power.vrm.phases`, sem valor de fato, a conferir pelo `visual-qa` em resolução cheia). gn-30 mostra as 12 cavidades grandes do conector de energia; os 4 contatos de sinal não aparecem.
- Catálogo (seção e): contorno do PCB "quase quadrado, com um degrau na borda superior junto ao conector"; sem medida (proporção grosseira em foto oblíqua).

## 17. Datasheet, trechos literais da p. 1 (releitura visual de 2026-11-10)
URL da seção 1, lido como imagem pela sessão. Capa: "NVIDIA RTX PRO 6000 Blackwell Workstation Edition". Texto: "The RTX PRO 6000 Blackwell harnesses a 600 W power design to fuel the most demanding professional workloads"; "Its double-flow-through cooling system channels airflow through dual axial pathways"; "Key Features": "96 GB of GDDR7 memory", "PCIe Gen 5", "Four Display Port 2.1b connectors", "Double flow through thermal design". Render da capa: duas grandes áreas de grade fina separadas por um X central de superfície lisa com o texto "RTX PRO 6000", encaixe do conector na borda superior e logotipo NVIDIA na lateral.
