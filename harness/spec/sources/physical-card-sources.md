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

---

# 18. Referências para modelagem, levantamento de 2026-11-10

Escopo: só referência visual e dimensional para o modelo 3D. Nada daqui entrou em `card.spec.json`; o que virar fato passa por auditoria. Acesso: 2026-11-10, ferramentas WebSearch e WebFetch (sem navegador, sem download para o repositório). Convenções: "lida" = a página foi aberta e o texto lido; "vista" = a imagem foi baixada pela ferramenta e olhada por esta sessão; "não vista" = só a URL foi obtida. As imagens que vi ficaram em cache temporário da ferramenta (`/root/.claude/projects/-home-user-apresentacao-placa-de-video/d0df145e-544a-598b-a026-2d5c595df2a2/tool-results/`), que não é durável: a sessão principal deve baixar de novo pelas URLs. Medidas tiradas de foto por mim são `derived`, com erro não quantificado (uma foto, sem correção de perspectiva).

## 18.1 Chiphell via gamegpu: PCB nu "RTX PRO 6000" com régua em mm (a melhor referência de contorno)
- URL da página: https://en.gamegpu.com/news/zhelezo/poyavilis-foto-pechatnoj-platy-rtx-pro-6000-blackwell-96-gb (lida). Publicada em 2025-05-01 pelo gamegpu; as fotos são do usuário "O-EtaIXVII" do fórum Chiphell (post datado 2025-5-1 13:03, título do post "无意中买到了PCB", ou seja, "comprei o PCB sem querer"). Não achei a URL do tópico original.
- Classe: `derived`. A atribuição à PRO 6000 Workstation vem do texto de terceiros (gamegpu: layout "de uma estação com fluxo duplo, como a Founders Edition"; VideoCardz e Guru3D, só snippet, dizem que a placa curta é a Workstation e não a Max-Q). Não há texto oficial.
- Imagens (vistas, capturas de tela do fórum com marca d'água chiphell.com, 253 KB e 286 KB):
  - https://gamegpu.com/images/1_2025/NEWS/q2/Gp2wQyObgAABmMr.jpg : PCB principal nu, uma face, mais a placa PCIe separada, sobre tapete de corte com régua em mm (marcas 100 a 290).
  - https://gamegpu.com/images/1_2025/NEWS/q2/Gp2wQyUagAALW8r.jpg : a outra face (a do chip: grande área de esferas BGA no centro) e a placa PCIe com logotipo NVIDIA e etiqueta de código QR; no anexo aparece "IMG_6236(1).jpg (542,13 KB)".
- O que se vê: contorno quase quadrado com moldura de ruptura ainda presa (trilhos), degrau diagonal no canto superior direito de uma face (o canto do conector de energia), furos de fixação do cooler (5 a 6 visíveis em volta do chip), pegadas de memória em colunas nos quatro lados em ambas as faces, fileiras de pegadas de indutores e MOSFETs nas bordas esquerda e direita, pegadas de conectores finos (FPC) na borda esquerda de uma face. A placa PCIe é uma peça estreita e comprida com dedos dourados, separada do principal. Não há conector de energia soldado (TechPowerUp, só snippet, fala em "quatro pontos de solda").
- Medida tirada de foto por mim (`derived`, a conferir pelo `visual-qa`): régua a cerca de 6,7 a 7,0 px/mm. Imagem 2: PCB principal com trilhos cerca de 132 x 123 mm; placa PCIe cerca de 37 mm de largura; região dos dedos dourados cerca de 82 mm (valor compatível com a região de contatos de um x16, o que valida a escala; conferir na norma CEM antes de usar). Imagem 1 dá cerca de 134 x 121 mm. Coerente com o desenho do water block da Bykski (altura 121,82 mm, seção 18.2). Não contei memórias nem indutores: as colunas de pegadas não permitem contagem segura a esta resolução.
- Não é fonte de altura de componente.

## 18.2 Bykski, water block N-RTXPRO6000-WS-SR (desenho com cotas do bloco e do backplate)
- URL: https://www.bykski.us/products/bykski-durable-metal-pom-gpu-water-block-and-backplate-for-nvidia-rtx-pro-6000-blackwell-workstation-edition-n-rtxpro6000-ws-sr-continuous-usage (lida). Fabricante, sem data de publicação (versões de imagem `v=1792758679`, não é data). Classe `derived` (terceiro; "usinado só para as placas listadas").
- Texto: bloco 233,85 x 121,82 x 20,70 mm (a largura inclui conexões), 1,5 kg, cobre niquelado, G1/4, resfria GPU, memória e VRM, backplate CNC. Sem manual impresso nem foto de PCB nu.
- Imagem com cotas (vista): bloco em vista de topo e de lado com 233,85 mm, 121,82 mm e 20,70 mm; backplate com 222,16 mm, 121,82 mm e 4,96 mm, com recorte em degrau no canto superior direito (o canto do conector de energia) e furos. É a única vista ortogonal cotada encontrada com o contorno da área da placa (PCB principal mais placa de I/O), embora seja do bloco e não do PCB.
- Imagens: principal (cotas), vista: https://www.bykski.us/cdn/shop/files/products_2FzCa1tB1Vvkj1nou7lVzR_2F1792623077007-N-RTXPRO6000-WS-SR.jpg?v=1792758689&width=1400 ; foto principal do bloco (não vista): https://www.bykski.us/cdn/shop/files/products_2FzCa1tB1Vvkj1nou7lVzR_2F1790375163130-N-RTXPRO6000-WS-SR_20_3_4a9b9c9c-6159-41e9-ae46-2d14b0617933.jpg?v=1792758679&width=1400 ; galeria (não vistas, miniaturas de 260 px; trocar `width=260` por `width=1400`): `...1792623076099-B-FRD-RTXPRO6000-WS-SR-360.jpg?v=1792758681`, `...1792623075666-B-FRD-RTXPRO6000-WS-SR-360_20_4.jpg?v=1792758683`, `...1792687889740-B-FRD-RTXPRO6000-WS-SR-360.png?v=1792758685`, `...1792623073982-B-FRD-RTXPRO6000-WS-SR-360_20_3.jpg?v=1792758687` (todas sob `https://www.bykski.us/cdn/shop/files/products_2FzCa1tB1Vvkj1nou7lVzR_2F`). Essas quatro são do kit AIO, não do bloco avulso.
- Compatibilidade conflitante entre revendedores: FormulaMod (https://www.formulamod.net/blogs/new/nvidia-rtx-pro-6000-blackwell-96gb-water-cooling-guide-the-h100-killer-for-home-ai-labs, lida, HuangLiang, 2026-04-04, atualizada 2026-04-22) lista o N-RTXPRO6000-SR (US$ 200) e o N-RTXPRO6000-WS-SR (US$ 216, "orientação de portas diferente") e diz que cobrem "32 módulos GDDR7" (afirmação de loja, `derived`). Sem foto de PCB nem desenho nesse artigo.

## 18.3 Alphacool ES RTX 6000 Pro Workstation / RTX 5090 Founders Edition (artigo 5100182): um mesmo bloco serve às duas placas
- Ficha técnica oficial: https://download.alphacool.com/datasheet/ENG_5100182_Alphacool_ES_RTX_6000_Pro_Workstation-RTX_5090_Founders_Edition_datasheet.pdf (lida como imagem, 1 página, "V. 1.012 // 10.2026"). Classe `derived` (terceiro), mas é afirmação explícita do fabricante. Trecho: "Compatibility: Nvidia GeForce RTX 5090 Founders Edition, 32GB GDDR7, HDMI, 3x DP" e "Nvidia RTX PRO 6000 Blackwell Workstation-Edition, 96 GB GDDR7"; "compact 1.5-slot design and intelligently positioned ports"; "Active cooling of the rear side via the backplate"; fundo de cobre cromado.
- Implicação (`derived`, interpretação nossa): o mesmo bloco usinado serve às duas placas, o que indica furação e posição de chip e conectores iguais entre o PCB principal da 5090 FE e o da PRO 6000 Workstation. Não diz nada sobre a altura dos componentes nem sobre o verso (a 5090 FE não tem memória no verso, a PRO tem). A Bykski, que faz um bloco para cada placa, dá 234,35 x 121,82 mm (5090 FE) e 233,85 x 121,82 mm (PRO), diferença de 0,5 mm, também compatível com contorno quase igual.
- Imagem da ficha (vista): render em perspectiva do bloco com backplate de fibra de carbono, 16 parafusos, recorte no canto do conector, portas cromadas na extremidade direita. É do bloco; não mostra o PCB.
- Manual: https://download.alphacool.com/manual/5100182_Alphacool_ES_RTX_6000_Pro_Workstation-RTX_5090_Founders_Edition_Manual.pdf (URL fornecida pela busca; **não lido**: a ferramenta recusou o arquivo por passar de 10 MB). **Prioridade para a sessão principal baixar e ler**: manuais Alphacool costumam trazer a lista de parafusos do cooler original, a ordem de desmontagem e os pads por posição.
- Páginas de produto: https://www.titanrig.com/alphacool-es-rtx-6000-pro-workstationrtx-5090-founders-edition.html (lida; "compatible with Nvidia GeForce RTX 5090 Founders Edition / RTX PRO 6000 Blackwell Workstation Edition", "1.5-slot"). Imagens (não vistas): `https://www.titanrig.com/media/catalog/product/cache/887962ebeeea3600f5b013f9c6b58b30/p/r/product_images_03-20_ac-0508-01_03-20-ac-0508-01_main_3.19.2026_8.52.52_am.jpg` e as `alt1` (`.../cache/06c2d3067612874ad38ddb25fb9a6ad3/...alt1_3.19.2026_8.53.24_am.jpg`), `alt2` (`.../cache/69656da952eb38b32a10b05ec0211d02/...alt2_3.19.2026_8.53.15_am.jpg`), `alt3` (`.../cache/17a3eb77c2d57ce4e768f7f2e4e86cb3/...alt3_3.19.2026_8.53.04_am.jpg`). Anúncio: https://www.alphacool.com/en/news/new-es-rtx-6000-pro-gpu-cooler (lido; data 2026-03-10 pelo nome da pasta; só a legenda cita a Workstation e a 5090 FE; imagens `https://api.alphacool.com/storage/filemanager/news/Launch_10_03_2026/news-01.webp` e `news-02.webp`, não vistas).
- Cuidado: o Alphacool 19450 "1-Slot-Design" (267,80 x 95,58 x 19,20 mm) é da **Server Edition**, outra placa e outro PCB. Não usar.
- Vortez (https://www.vortez.net/news_story/alphacool_introduces_es_rtx_6000_pro_gpu_water_coolers.html), aio.lv e watercoolinguk deram 403: só snippet.

## 18.4 PCGamesN, PCB da RTX 5090 Founders Edition em mão (Ben Hardwidge, atualizado em 2025-01-23)
- URL: https://www.pcgamesn.com/nvidia/geforce-rtx-5090-pcb (lida). Placa irmã, `derived`.
- Texto: PCB "a menor que a publicação já viu" em uma placa NVIDIA; os 32 GB de GDDR7 ficam todos na frente; o verso tem "componentes básicos, pontos de solda e um conector"; conector de 16 pinos na borda superior.
- Imagem do verso (vista): https://www.pcgamesn.com/wp-content/sites/pcgamesn/2025/01/nvidia-geforce-rtx-5090-pcb-rear.jpg (1920 x 1080 aprox.). Mostra o PCB principal na palma da mão (escala de mão adulta, sem instrumento), contorno quase quadrado com canto superior direito chanfrado onde o conector de energia preto fica **inclinado em relação à borda** (leitura de foto), duas fileiras de componentes retangulares pretos (indutores ou capacitores) na borda superior, coluna de cerca de 12 na borda direita e duas colunas na esquerda, dois conectores FPC largos no lado esquerdo, uma região central com quatro componentes grandes e pinos de mola ("pogo"), etiqueta com número de série. Serve para a forma do PCB e o ângulo do conector (o primeiro retrato nítido do conector inclinado), não para a PRO 6000 (que tem memória também no verso).
- Outras imagens do artigo (não vistas): https://www.pcgamesn.com/wp-content/sites/pcgamesn/2025/01/nvidia-geforce-rtx-5090-pcb-front-776x436.jpg ; `.../nvidia-geforce-rtx-5090-pcb-power-connector.jpg` ; `.../nvidia-geforce-rtx-5090-pcb-angle.jpg` (mesmo diretório).

## 18.5 PC Games Hardware (Sven Bauduin), "Geforce RTX 5090 FE: High-Density PCB und Kühler mit Double Pass Through" (2025-01-15)
- URL: https://www.pcgameshardware.de/Geforce-RTX-5090-Grafikkarte-281029/Specials/Founders-Edition-mit-High-Density-PCB-und-Double-Pass-Through-1463646/ (lida). Placa irmã, `derived` (imagens de origem NVIDIA e der8auer).
- Texto: 304 mm de comprimento, 137 mm "de largura", "2 slots de altura"; PCB formado por "três placas individuais" (der8auer); "dez heatpipes" (contraste com "cinco" na seção 18.6); 34 fases para GPU e memória; 12V-2x6.
- Imagem NVIDIA do PCB com os heatpipes (vista): https://www.pcgameshardware.de/screenshots/960x/2025/01/High-Density-PCB-pcgh.png : render com o PCB principal visto de cima em perspectiva, **cinco tubos saindo para a esquerda e cinco para a direita** (os tubos atravessam a câmara de vapor, que fica sob o PCB), o chip no centro com componentes ao redor, fileira de estágios de potência na borda inferior, conector FPC no topo. Reconcilia "cinco" com "dez": cinco por lado, dez no total (leitura do render).
- Outras (não vistas): https://www.pcgameshardware.de/screenshots/960x/2025/01/Next-Gen-pcgh.png (comparação de coolers) ; https://www.pcgameshardware.de/screenshots/390x/2025/01/Double-Flow-Through-Thermal-Design-pcgh.png ; https://www.pcgameshardware.de/screenshots/390x/2025/01/RTX-5090_2-pcgh.png e `RTX-5090-1-pcgh.png` (der8auer, PCB) ; https://www.pcgameshardware.de/screenshots/1000x562/2025/01/Geforce-RTX-5090-pcgh_artwork1.jpg ; `.../390x/2025/01/5090-3-pcgh.png`, `5080-2-pcgh.png`, `5070-3-pcgh.png`, `SFF-pcgh.png`.

## 18.6 wccftech (Hassan Mujtaba, 2025-01-15), projeto térmico "Double Flow Through" da família RTX 50 FE
- URL: https://wccftech.com/nvidia-rtx-50-double-flow-through-founders-edition-thermal-solution-teardown-dual-fans-dual-slot-600w-cooling/amp/ (lida). Placa irmã, `derived`.
- Texto: câmara de vapor 3D sobre o PCB central; cinco heatpipes grandes; três blocos de aletas de alumínio (dois laterais ligados pelos tubos e um central preso sob o PCB); dois ventiladores axiais.
- Imagem da peça térmica desmontada (vista): https://cdn.wccftech.com/wp-content/uploads/2025/01/Photo-2025-01-09-13-28-55-scaled.jpg (cerca de 2560 x 1920). Foto de mesa do cooler da 5090 FE: dois pacotes de aletas pretas (um em cada ponta), a base prateada com a placa de contato do die (retângulo cinza com marca de pasta, cerca de uma dezena de furos de parafuso nos cantos), tampas de alumínio com sulcos paralelos nas bordas, pacote inferior com recortes em "dentes" que encaixam entre os componentes do PCB, aletas finas e curvas na extremidade. É a melhor vista de aletas e câmara de vapor encontrada; a PRO difere (pasta, memória nos dois lados, bilateral).
- Outras (não vistas): https://cdn.wccftech.com/wp-content/uploads/2025/01/Photo-2025-01-09-13-29-05-scaled.jpg (aletas e ventiladores) ; `.../Photo-2025-01-09-13-29-08-scaled.jpg` ; `.../Photo-2025-01-09-13-32-26-scaled.jpg` ; `.../Photo-2025-01-09-13-32-35-scaled.jpg` ; `.../Photo-2025-01-09-13-32-53-728x546.jpg` ; `.../NVIDIA-GeForce-RTX-5090-_6.png` ; `.../2025-01-15_20-32-05.png` ; `.../2025-01-15_20-36-04.png` (todas sob `https://cdn.wccftech.com/wp-content/uploads/2025/01/`).

## 18.7 Puget Systems, ficha da RTX PRO 6000 Blackwell Workstation Edition (galeria de 8 imagens)
- URL: https://www.pugetsystems.com/parts/Video-Card/NVIDIA-RTX-PRO-6000-Blackwell-Workstation-Edition-96GB-PCI-E-16221/ (lida). Revendedor, `derived`. Texto: 304 x 137 x 42 mm, 1,860 kg (4,1 lb); a Puget já aparece na seção 5 como revisão de conteúdo; esta é a ficha de produto. Sem metodologia de medida (valor de ficha, possivelmente dado do fabricante); ressalva de peso: é peso líquido listado, não balança própria.
- Imagens (renders de produto, vistas as ids 89581, 89583, 89585 e 89589; o restante não visto):
  - https://account.pugetsystems.com/pic_disp.php?id=89581&height=1000&width=1000 : render 3/4 pela frente (face A) com os dois ventiladores, **9 pás por ventilador a conferir**, X central com superfície lisa, as 4 DisplayPort em uma fileira, adaptador PCIe em prolongamento com dedos dourados saindo pela borda. Melhor vista frontal obtida.
  - https://account.pugetsystems.com/pic_disp.php?id=89583&height=1000&width=1000 : vista oblíqua baixa da outra face (também dois ventiladores com X central escuro), dedos dourados na borda, extremidade oposta ao bracket lisa com dois pontos (furos ou parafusos) na face lateral.
  - https://account.pugetsystems.com/pic_disp.php?id=89585&height=1000&width=1000 : vista da **borda superior**, com o painel do topo mostrando duas fendas longas e o encaixe do conector de 16 pinos entre os ventiladores, e o logotipo NVIDIA dourado na lateral. É a melhor referência para o recorte do conector e as fendas (pendência "fendas da borda superior").
  - https://account.pugetsystems.com/pic_disp.php?id=89589&height=750&width=750 : bracket com 4 DisplayPort numeradas de 1 a 4 e **grade de ventilação abaixo das portas**, com 4 parafusos. **Conflito com gn-11 e com o guia oficial p. 13** (chapa lisa, sem grade na PRO 6000 Workstation): esta imagem parece ser de uma Max-Q ou imagem genérica. Não usar para o bracket sem confirmação.
  - Não vistas: ids 89582, 89584, 89586, 89587, 89588 (mesmo padrão de URL com `height=1000&width=1000`).

## 18.8 NVIDIA datasheet via PNY (VCNRTXPRO6000B-PB)
- URL: https://www.pny.com/File%20Library/Company/Support/Product%20Brochures/NVIDIA%20RTX/English/NVIDIA-RTX-PRO-6000-Blackwell-Workstation-Edition.pdf (lida como imagem, 1 página). `confirmed` como cópia do datasheet NVIDIA (mesma capa e mesmo texto da seção 17), com o número de peça PNY. Traz uma imagem 2263 x 865 px (CMYK) na capa: render em perspectiva da face superior com o X central, o texto "RTX PRO 6000" no X, a lateral com logotipo NVIDIA e a borda com a fenda da PCIe. Sem dimensões nem desenho. Pouco novo em relação à seção 17.

## 18.9 Outras fontes abertas sobre a 5090 FE (resumo; só texto)
- Gamegpu, Notebookcheck e gsmgotech (Northridge Fix): já na seção 11.
- Tom's Hardware, "More GeForce RTX 5090 Founders Edition mysteries revealed: backside of the PCB" (https://www.tomshardware.com/pc-components/gpus/more-geforce-rtx-5090-founders-edition-mysteries-revealed-backside-of-the-pcb): **só snippet**, corpo truncado. Snippet: 34 fases (30 na frente, 4 atrás), conectores mezanino e pogo pins no verso. Compatível com a foto do PCGamesN (4 componentes grandes com pogo no centro do verso, seção 18.4), que eu vi.
- Bykski N-RTX5090FE-SR (https://www.bykski.us/products/bykski-durable-metal-pom-gpu-water-block-and-backplate-for-nvidia-geforce-rtx-5090-founders-edition-continuous-usage, lida): bloco 234,35 x 121,82 x 22,70 mm; backplate 222,16 x 121,82 x 10,96 mm; comprimento da placa de cobre 136,55 mm; sem desenho (a galeria tem, não vista): https://www.bykski.us/cdn/shop/files/products_2FCWLjat7yf30Vscte6h4Q_2F1791332226576-N-RTX5090FE-SR.jpg?v=1793146572&width=1400 e `...1793146360228-N-RTX5090FE-SR-p02.png?v=1793146578` até `p07` (mesmo prefixo, `width=1400`). A placa de cobre (136,55 mm) é a única medida de comprimento do conjunto PCB principal da 5090 FE e se aproxima dos 132 a 134 mm lidos na foto do PCB nu da seção 18.1.
- EK: o Quantum Vector3 FE RTX 5090 foi feito "para o projeto de PCB em três partes" (Guru3D, snippet). Manual não achado. O EK-Pro GPU WB RTX PRO 6000 é para a **Server Edition e a Max-Q**, não serve à Workstation (listagem de loja, snippet; ekwb.com devolveu 403). Não há bloco EK para esta placa.
- Watercool (Heatkiller): manual achado é de outra placa (ASUS TUF 5090), não serve. Optimus, Barrow e Phanteks: nada para a PRO 6000 Workstation.

## 18.10 Modelos 3D encontrados
Nenhum modelo gratuito da PRO 6000 ou da 5090 FE confirmado. Candidatos, **todos com licença e formato não verificados** (403 ou só snippet):
- MakerWorld modelo 1659118, réplica imprimível de uma 5090 ("conector 12VHPWR e número exato de aletas", segundo o snippet): https://www.makerworld.com/en/models/1659118 (403; licença e formato desconhecidos; não está provado que seja gratuito).
- Printables, "RTX 5090 FE PCB Drink Coaster": https://www.printables.com/model/1304784-rtx-5090-fe-pcb-drink-coaster (403; um porta-copos com a silhueta do PCB; licença e formato desconhecidos; sem valor para medida).
- Pagos, listados só para não serem usados: CGTrader (5090 FE, cerca de US$ 16; PRO 6000 Workstation Edition, preço não visto), APC3D (modelo no fórum da Unreal, sem informação de preço).
- Fórum NVIDIA: pedido de modelo 3D da Server Edition, sem resposta vista (https://forums.developer.nvidia.com/t/rtx-pro-6000-blackwell-server-edition-3d-model-request/371361, só snippet). NVIDIA não oferece modelo 3D na página do produto (verificado em https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000.md: sem galeria, sem press kit, sem 3D).
- Sketchfab e GrabCAD: a busca não devolveu nada. Não foi possível pesquisar nas próprias plataformas.

## 18.11 Peças padronizadas (desenhos e normas)
- 12V-2x6 / 12VHPWR: a busca não achou desenho de fabricante (Molex, Amphenol, TE) do receptáculo de 16 pinos; só cabeçalhos de outras famílias. Lacuna. O PCI-SIG tem a especificação CEM 5.x só para membros.
- Bracket PCIe de dois slots: sem desenho de fabricante. Secundárias: Intel NUC 12 Extreme (https://edc.intel.com/content/www/us/en/publications/specification-nuc12dcm-nuc12edb/add-in-card-limitations/, snippet, não aberta) cita para placa de dois slots 300 mm, 39 mm de espessura total (34,8 mm de componentes frontais, 2,7 mm de backplate, 1,7 mm de PCB) e 131 mm de altura; Thomas-Krenn (https://www.thomas-krenn.com/en/wiki/Size_specification_/_form_factor_of_additional_cards, snippet) cita altura de 111 mm (4,376 pol) para placa de altura total. Já temos CEM 3.0 em `standards-sources.md`.
- Receptáculo DisplayPort: sem desenho de fabricante achado. Imagem 89589 da Puget (seção 18.7) e gn-11 mostram o encaixe, sem cota.

## 18.12 Conflitos novos desta rodada
1. **Heatpipes da 5090 FE (`conflict: true`).** wccftech: "cinco heatpipes grandes"; TechPowerUp (snippet): "cinco tubos de 8 mm"; PCGH: "dez heatpipes". O render da NVIDIA mostra cinco de cada lado (dez pontas). Pode ser cinco tubos que atravessam (cada tubo com duas pontas) ou dez tubos. Não resolvido. Não vale para a PRO 6000 (nenhum teardown da PRO descreve os tubos).
2. **Espessura (`conflict: true`).** Puget: PRO 6000 e 5090 FE com 42 mm (ficha); NVIDIA e GPU-Monkey: 5090 FE 40 mm; LTT Labs (snippet): 40 mm; Notebookcheck: 132 de profundidade e 40 de altura, diferença entre convenções. Soma-se ao conflito 3 desta página.
3. **Bracket (`conflict: true`).** Puget (imagem 89589): grade abaixo das 4 DP. Guia NVIDIA p. 13 e gn-11: chapa lisa. Não resolvido; a evidência oficial e a do teardown da própria placa dizem "lisa".
4. **Peso:** 1,860 kg (Puget, ficha) contra 1,9 kg (Jon Peddie, seção 4). Compatíveis, sem instrumento em nenhuma.

## 18.13 Lacunas depois desta rodada
- Vistas ortogonais frontal, do verso, do topo e da ponta da placa montada: continuam sem fonte (só renders em perspectiva da Puget e capturas da GN).
- Altura de componentes e do conjunto PCB mais cooler: lacuna. O manual Alphacool 5100182 (não lido por tamanho) e os manuais de EK e Bykski para a 5090 FE são as melhores apostas.
- Contagem de indutores, fases e controladores da PRO 6000: lacuna.
- Pás do ventilador: o render da Puget sugere 9, a conferir; diâmetro sem fonte.
- Padrão do X e das grades: a Puget 89581 e 89583 mostram X liso e grades finas; sem cotas.
- Interior do cooler da PRO 6000: só a placa irmã (seções 18.5 e 18.6).
- Cabos flat e placa de I/O na PRO 6000: o PCB nu (18.1) mostra a placa PCIe separada e pegadas de FPC no principal; a placa de I/O não aparece.
- Conector de energia: ângulo inclinado só visto na 5090 FE (18.4); marca H+ ou H++ sem fonte.
- Parafusos: lacuna (T6 e 4 do slot cover só em snippet da 5090 FE).
- Peças padronizadas (12V-2x6, bracket, DisplayPort): sem desenho de fabricante.
- Sites que bloquearam: TechPowerUp, Tom's Hardware, Guru3D, TweakTown, VideoCardz (402), Vortez, aio.lv, MakerWorld, Printables, EKWB.
