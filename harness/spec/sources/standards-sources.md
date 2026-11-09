# Fontes de normas e padrões (rodada de 2026-11-09)

**Rodada NÃO AUDITADA.** Nenhum item abaixo passou pelo `fact-checker`. Acesso em 2026-11-09.

Método e limites:
- As normas originais (PCI-SIG, VESA, JEDEC) são pagas. Aqui entram: (a) cópias hospedadas e comunicados, (b) guias de fabricante que reproduzem a norma, (c) fontes secundárias, e Wikipedia só como último recurso ("baixa autoridade").
- Os PDFs foram abertos páginas a páginas como imagem (ferramenta Read) e **os números dos desenhos foram lidos a olho por mim**. Risco de leitura errada em cotas pequenas; o `fact-checker` deve reabrir cada cota marcada "leitura de desenho". Numeração de páginas: página do PDF = página impressa nos dois documentos.
- Procedência: `confirmed (norma)` = texto da entidade da norma, de cópia dela ou de documento de fabricante que cita a norma, na revisão indicada. `derived` = secundária, conta minha ou revisão diferente da da placa. Contas minhas estão marcadas "conta".
- **Revisão importa.** A única cópia da norma PCI-SIG aberta é a CEM **3.0 (2013)**. A placa usa CEM **5.x**. O que vem da 3.0 vale para mecânica e potência do slot, e deve ser reconferido na 5.x antes de virar fato da placa.
- Fontes só com snippet de busca estão na seção "Só snippet" e **não valem como fato**.

## 1. PCI-SIG, PCI Express Card Electromechanical Specification, Rev. 3.0 (cópia)
URL: https://cdck-file-uploads-global.s3.dualstack.us-west-2.amazonaws.com/nvidia/original/3X/2/0/20a75bdbb6bc42db8b2cb0b7c77f3e492a274508.pdf
Cópia da norma (21 de julho de 2013) enviada ao fórum de desenvolvedores da NVIDIA, não ao site da PCI-SIG. Autoridade: norma, revisão 3.0. Procedência: `confirmed (norma, rev 3.0)`.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Rails do slot | "All PCI Express add-in card require two power rails: +12V and +3.3V, with a third, optional 3.3Vaux rail" | 4.1, p. 43 |
| Slot de 75 W | +12 V: 5,5 A máx, ±8%; +3,3 V: 3,0 A máx, ±9%; +3,3Vaux 375 mA com wake-up | Tabela 4-1, p. 44 |
| Soma | "the sum of the draw on the two rails cannot exceed 75 W" | 4.2, p. 45 |
| Cartão de 150/225/300 W | "can draw a maximum of 75 W from the standard CEM connector. Additional power, up to 75 W, is provided through an additional connector" (150 W); 225/300 W: "maximum of 75 W through the standard connector"; o resto por conectores auxiliares (150 W / 225 W) | 1.7 p. 18, 1.8 p. 19 |
| Corrente por contato do slot | "contact carrying capability being 1.1 A per pin" | 6.1, p. 89 |
| Passo entre slots | 20,32 mm [0,800 in] entre conectores adjacentes | Fig. 1-3 (p. 18), Fig. 1-4 (p. 19) |
| Dual-slot | "has the same dimensions as a standard height full length card, except the component side height restriction is reduced to 34.80 mm"; triple: 55,12 mm; single: 14,47 mm (tabela da Fig. 9-1) | 9.1, p. 127; Fig. 9-1, p. 128 |
| Folga do dual-slot | 34,8 mm máx [1,370 in] de área reservada do lado dos componentes (Fig. 1-3) | p. 18 |
| Altura padrão | "standard height of 111.28 mm (4.376 inches) maximum" (texto) e "111.28 mm (4.381 inches)" (Tabela 9-1); Fig. 9-1 cota 111,15 [4,376]; "height of the standard height graphics card is required to be fixed: 111.15 mm ±0.13 mm" | p. 127, 128, 133 (conflito, ver abaixo) |
| Altura, referência | "card height is measured from the bottom of the edge finger to the top of the card" | p. 127 |
| Perfil baixo | 68,90 mm [2,731 in] máx | Tabela 9-1 |
| Comprimento | full-length: DIM M 312,00 máx [12,283]; 3/4: 254,00; meio: 167,65 | Fig. 9-2, p. 129 |
| Recomendação de comprimento | "strongly recommended that PCI Express DUAL-SLOT add-in cards be designed with a 241.30 mm (9.5 inches) maximum length" | p. 127 |
| Espessura do PCB | 1,57 REF [0,062] | Fig. 9-1, p. 128 |
| Tolerância geral | ±0,13 [0,005] "unless otherwise specified" | notas das Fig. 9-1 e 9-2 |
| Conector x16 (corpo) | 164 posições; DIM 'B' 89,00 [3,504]; passo 1,00 mm ("The connector has a 1.00 mm contact pitch") | Fig. 6-1 p. 90; p. 93; leitura de desenho |
| Dedos de borda x16 | passo 1,00 mm; DIM 'B' 72,15 [2,841]; grupo inicial 12,15 [0,478]; 10,00 [0,394]; pino PRSNT B81 | Fig. 6-3, p. 92; leitura de desenho |
| Furo de posicionamento | 2 furos Ø 2,35 mm; posição DIM 'A' 73,15 [2,880] (x16) | Fig. 6-2, p. 91 |
| Bracket padrão de E/S | altura total 120,02 REF [4,725]; 112,75 REF [4,439]; largura do slot 18,42 [0,725]; chapa 0,86 ±0,08 mm [0,034 ±0,003] (20 ga); abertura de conectores 89,90 REF [3,539]; rosca "#4-40"; tolerância ±0,25 | Fig. 9-5, p. 134; leitura de desenho |
| Furos de fixação do cartão | Ø 3,18 REF (2 furos) na extremidade direita do cartão de 312 mm, "required only on the right end of the full-length card" | Fig. 9-1, p. 128 e p. 131 |
| Retenção | "All graphics cards are required to be retention ready"; entalhe "hockey stick" | p. 131, 133 |
| Cabo auxiliar | só 2x3 (75 W) e 2x4 (150 W) nesta revisão; **não há 16 pinos** | capítulos 7 e 8, p. 106 a 126 |

Não achei nas páginas lidas: o termo "extended height"; desenho de bracket de dois slots.

## 2. Intel, ATX12VO (12V Only) Desktop Power Supply Design Guide, Rev. 2.11, maio de 2024 (doc. 613768)
URL: https://cdrdv2-public.intel.com/613768/613768_2.11.pdf
Guia de projeto de fonte de fabricante que cita e reproduz trechos da PCIe CEM 5.1 (diz no texto: "PCI Express Card Electromechanical Specification, Revision 5.1"). Autoridade: fabricante citando a norma. Procedência: `confirmed (norma, via Intel, CEM 5.1)`. O PDF tem criptografia; a leitura foi como imagem.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Conectores da CEM 5.1 | "defines three 12V Auxiliary Power Connectors": "75 W 2x3", "150 W 2x4", "600 W 12V-2x6" | 3.2, p. 25 |
| Corrente por conector | 2x3: 75 W, 6,75 A; 2x4: 150 W, 13,5 A; 12V-2x6: 150 W/13,75 A, 300 W/27,5 A, 450 W/41,25 A, **600 W/55 A** "(Max RMS)"; tensão +5%/-8%; "maximum current slew rate ... no more than 5.0 A/µs" | Tabela 3-5, p. 25 |
| Potência não inclui o slot | "maximum sustained power supported by this Auxiliary Power Connector alone, and do not include power drawn separately through the motherboard card edge connector" | 3.3.1, p. 26 e 27 |
| Soma com outras fontes | "An Add-in Card may draw up to the maximum permitted power defined in this table in addition to other power sources" | Tabela 3-6, nota 3, p. 27 |
| Sinais laterais | quatro: SENSE0 e SENSE1 (obrigatórios), CARD_PWR_STABLE (opcional), CARD_CBL_PRES# (obrigatório/opcional) | 3.3, p. 26 |
| Tabela SENSE | Ground/Ground: 375 W inicial, 600 W sustentado; Open/Ground: 225/450 W; Ground/Open: 150/300 W; Short (SENSE0 ligado a SENSE1): 100/150 W; Open/Open: 0/0 W | Tabela 3-6, p. 27 |
| Efeito do Open/Open | "no power may be drawn by the load"; é o estado novo "0 watt" que não existia no 12VHPWR | 5.2.2.4, p. 63 |
| Pinos | 12 de potência, em 16 AWG ("All 12 pins must be connected ... with no depopulation"); 4 de sinal, 28 AWG | p. 63 |
| Pinagem | pinos 1 a 6: +12V; 7 a 12: COM; S1 CARD_PWR_STABLE; S2 CARD_CBL_PRES#; S3 SENSE0; S4 SENSE1 | Tabela 5-10, p. 67 e 68 |
| Relação das siglas | "The 12VHPWR connector, introduced in the earlier 2.0 revision of this document and the PCIe CEM 5.0 Specification, has been deprecated and replaced with the 12V-2x6 connector, as shown in th PCIe CEM 5.1 specification" (sic). "mechanically identical ... in most respects" | p. 63 |
| O que mudou | "The power pins have been lengthened and the sideband pins have been shortened in the PCB Header to ensure first-mate/last break engagement of the power pins" | p. 63 |
| Marcação | cabeçote do 12V-2x6 marcado "H++"; o 12VHPWR era "H+" | p. 63 e Fig. 5-10, p. 66 |
| Passo dos pinos de potência | cabeçote, vista frontal: 5 intervalos entre pinos de uma fileira somando 15,00; cota 3,00 | Fig. 5-7, p. 65; leitura de desenho |
| Passo dos pinos de sinal | 4 pinos, cotas 2,00 e 6,00 (3 intervalos de 2,00); leitura de desenho | Fig. 5-7, p. 65 |
| Largura do cabeçote | 18,85 (vista frontal); plugue do cabo 20,85 (Fig. 5-5, p. 62); tolerância geral X.XX = ±0,20, X.X = ±0,25 | Fig. 5-7; leitura de desenho |
| Outras cotas do cabeçote | vista lateral: 7,40; 6,86; 1,51; 2,95 ±0,1; 4,60; 4,32; 3,00; 5,85; 2,33; vista superior: 9,91 e 1,60. **Não identifiquei o que cada uma mede** (datums B, C, D) | Fig. 5-8 a 5-10, p. 65 e 66 |
| Contato | "Temperature Rise ... Not to exceed 30°C"; LLCR < 6 mΩ | p. 67 |
| Excursão de potência | R máx: 2,5 (rail +12 V do conector, até 100 µs) e 3 (potência total do cartão >75 W, até 100 µs); 1 em 1 s ou mais; "No excursions are permitted on the 3.3V and 3.3Vaux" | Tabela 3-1, p. 21; 3.1, p. 20 |
| Sustentada | "Sustained Power, the average power delivered though a single power cable in a 1-second moving interval" | p. 20 |

Corrente por pino **não é dada em nenhuma tabela deste guia**; a conta está na seção "Contas".

## 3. Molex, Micro-Fit+ Connector System, apresentação para clientes (PCIe 12V-2x6)
URL: https://www.marubun.co.jp/wp-content/uploads/2025/08/Micro-FitPCIe_PRES.pdf (cópia do distribuidor Marubun). Autoridade: fabricante do conector. Procedência: `confirmed (fabricante)`.

| Dado | Trecho ou valor | Onde |
|---|---|---|
| Descrição | "PCIe 12V-2x6 Auxiliary Connector System — a CEM (card electromechanical) hybrid solution supporting next-gen PCIe 5.0 and 6.0 applications" | slide 1 |
| Pinos e corrente | "12x9.5A-capable power pins and 4x sideband signal pins"; "Current Rating: 9.5A (Power)/1.0A (Signal)"; "Voltage Rating: 600V AC/DC"; "Temperature Rise: 30°C max" | slides 1 e 2 |
| Potência | "675W add-in card ready"; "ampere interrupting capacities (AICs) up to 675W with 9.5A per pin" | slides 1 e 6 |
| Séries | 219116 cabeçote 16 circuitos (12 de potência, 4 de sinal); 219114 receptáculo; terminais 220226 (16 AWG) e 219197 (28 AWG) | slide 2 |
| Compatibilidade | "mechanically keyed to comply with next-gen CEM 5.0/6.0 base specification requirements, so they are not intended to mate with legacy 2x3 and 2x4 PCIe connectors" | slide 3 |
| Contatos | "4 independent contact points on each power pin"; "make first, break last (MFBL)" entre potência e sinal | slide 3 |
| Passo | **não consta** nesta apresentação ("low pitch") | slide 3 |

## 4. Hardware Busters, "ATX v3.1 and PCIe CEM 5.1 are official" (secundária)
URL: https://hwbusters.com/psus/atx-v3-1-pcie-cem-5-1-are-official/ . Autoridade: imprensa técnica. Procedência: `derived`.

| Dado | Trecho ou valor |
|---|---|
| Nome | "The 12VHPWR connector name has been changed throughout the document to '12V-2×6'" |
| Potência e pinos | "rated for up to 600W, with twelve power pins at 3.0mm spacing and four smaller sideband pins"; "Power pins are rated at 9.2A each" |
| Lançamento | ATX v3.1 lançado em 13 de setembro de 2023 |
| Excursão no slot | antes o limite era 5,5 A; agora picos de 13,75 A por 0,1 ms, "165W at a nominal 12V"; nada em 3,3 V e 3,3Vaux |
| Erro na própria fonte | diz "the pins should be able to deliver up to 1324.8W" (12 × 9,2 A × 12 V). Um comentário corrige para 6 × 12 × 9,2 = 662,4 W: só 6 pinos levam corrente de ida |
| Comprimento dos pinos | só diz "lengthened/shortened", **sem milímetros** |

## 5. VESA, comunicado sobre DisplayPort 2.1b (6 de janeiro de 2025)
URL: https://www.displayport.org/pr/vesa-to-update-displayport-2-1-with-new-active-cable-specification-for-up-to-3x-longer-dp80-cables/ . Autoridade: entidade da norma (comunicado). Procedência: `confirmed (VESA)`. Lido por resumo automático do WebFetch.

| Dado | Trecho ou valor |
|---|---|
| Versão | "DisplayPort version 2.1b, which will be released in the spring of 2025" |
| UHBR20 | "UHBR20 – the highest-performance UHBR tier in the DisplayPort 2.1 spec" |
| 80 Gbps | "a maximum throughput of 80 Gbps" para UHBR20 em quatro pistas |
| Novidade | cabos ativos DP80LL: UHBR20 "over an active cable up to three meters"; "up to 3X the cable length" dos DP80 passivos (1 m) |

O comunicado não diz "20 Gbps por pista" nem "4 pistas" com essas palavras; a divisão 80 ÷ 4 é conta (ver Wikipedia, seção 7).

## 6. Molex 47272, receptáculo DisplayPort de 20 circuitos (peça 472720001)
URL: https://extranet.mandieselturbo.com/electronics/datasheets/Molex/47272%20Series/472720001.pdf (página de produto Molex, gerada em 2026-03-23). Autoridade: fabricante. Procedência: `confirmed (fabricante, peça específica)`.

| Dado | Valor |
|---|---|
| Descrição | "1.00mm Pitch DisplayPort Receptacle, Right-Angle, Surface Mount ... 20 Circuits" |
| Fileiras / passo | 2 fileiras; passo de acoplamento 1,00 mm; passo de terminação 1,00 mm |
| Elétrico | 0,5 A por contato; 40 V AC |
| Mecânica | com trava (latch holes), blindagem EMI, "Panel Mount: Without Flange" |
| Dimensões externas | **não constam** (estão no desenho `472720001_sd.pdf`, não aberto) |

## 7. Wikipedia, DisplayPort (baixa autoridade)
URL: https://en.wikipedia.org/wiki/DisplayPort . Só lidos os primeiros 100.000 caracteres. Procedência: `derived`.

| Dado | Trecho ou valor |
|---|---|
| Receptáculo | "The standard DisplayPort receptacle has dimensions of 16.10 mm (width) × 4.76 mm (height) × 8.88 mm (depth)" |
| Pinos | 20 |
| UHBR20 | 20,0 Gbit/s por pista, 4 pistas, 80,00 Gbit/s; "effective data rate of 77.37 Gbit/s, using 128b/132b encoding" |
| 2.1b | acrescentou a especificação de cabo ativo DP80LL (até 3 m) |

## 8. JEDEC, comunicado "JEDEC Publishes GDDR7 Graphics Memory Standard" (5 de março de 2024), cópia na Design & Reuse
URL: https://www.design-reuse.com/news/55819/jedec-gddr7-graphics-memory-standard.html . Texto do comunicado da entidade, republicado por terceiro; leitura por resumo automático. A página da JEDEC (jedec.org) deu 403 e a Business Wire também. Procedência: `confirmed (JEDEC, comunicado)`.

| Dado | Trecho ou valor |
|---|---|
| Norma | JESD239 GDDR7 SGRAM; "free to download from its website" (o comunicado diz que é gratuita no site da JEDEC; **eu não consegui abri-la**) |
| Banda | "double the bandwidth over GDDR6, reaching up to 192 GB/s per device" |
| Sinalização | primeira DRAM da JEDEC com PAM; PAM3 leva 3 bits em 2 ciclos (NRZ: 2 bits em 2 ciclos) |
| Canais | canais independentes de 2 (GDDR6) para 4 (GDDR7). **Largura de cada canal não consta** |
| Densidades | 16 Gbit a 32 Gbit |
| Modo de 2 canais | "2-channel mode to double system capacity" (paráfrase do resumo; a palavra "clamshell" não aparece) |
| RAS | on-die ECC, data poison, error check and scrub, paridade de comando/endereço |

## 9. Micron, tabela GDDR6 x GDDR7 (via Jon Peddie Research)
URL: https://www.jonpeddie.com/news/ray-tracing-loves-memory-micron-returns-the-love/ . Tabela de um blog da Micron reproduzida por JPR. Autoridade: fabricante, via secundária. Procedência: `derived`.

| Campo | GDDR6 | GDDR7 |
|---|---|---|
| Ball count | 180 | **266** |
| Package | 12 × 14 × 1,2 mm | **12 × 14 × 1,1 mm** |
| Ball pitch | 0,75 mm | "0.75mm/O.73mm" (typo evidente: provável 0,75/0,73) |
| Clam shell | Yes | **Yes** |
| Device width (I/O) | 32 bits | **32 bits** |
| Channels/package | 2 | **4** |
| Max data rate | 18 Gb/s | 32 Gb/s |
| Tensão / sinal | 1,35 V, NRZ | 1,2 V, PAM3 |

## 10. Micron, página de produto GDDR7
URL: https://www.micron.com/products/memory/graphics-memory/gddr7 . Autoridade: fabricante. Procedência: `confirmed (fabricante)`.
Taxa de dados 32 Gb/s; "greater than 1.5 TB/s" com barramento de 384 bits; PAM3 (GDDR6: NRZ); 1,2 V; ECC on-die, paridade de CA, CRC de 9 bits; "Not compatible with GDDR6 or GDDR6X". Não cobre densidades, encapsulamento, clamshell nem JEDEC.

## 11. Samsung, página GDDR7
URL: https://semiconductor.samsung.com/dram/gddr/gddr7/ . Autoridade: fabricante. Procedência: `confirmed (fabricante)`.
"first DRAM to feature PAM3 signaling"; "40+Gbps" na legenda; até 25% mais velocidade por pino que a geração anterior. **Não** diz densidade, encapsulamento nem largura.

## 12. Club386, "Samsung unveils 3GB GDDR7 memory with 30% higher efficiency" (secundária, 2024-10-17)
URL: https://www.club386.com/samsung-unveils-3gb-gddr7-memory-with-30-higher-efficiency/ . Procedência: `derived`.
24 Gb (3 GB) por chip; até 42,5 Gbps; nó "5th-gen 10nm"; cerca de 30% mais eficiente; produção em massa prevista para o início do ano seguinte; encapsulamento não citado. A nota de imprensa da Samsung (news.samsung.com) deu timeout e **não foi aberta**.

## 13. HWCooling.net, "GDDR7 memory for next-gen GPUs is ready" (secundária)
URL: https://www.hwcooling.net/en/gddr7-memory-for-next-gen-gpus-is-ready-up-to-48ghz-clocks/ . Procedência: `derived`.
"clamshell configuration, where twice the number of chips are used (two on a single 32bit interface)"; "It should still have a 32-bit data width"; "chip sizes of 16 Gb to 32 Gb"; "a middle ground in the form of 24Gb/3GB chips"; "up to 48 Gb/s per bus bit". O próprio texto usa "should" e "apparently": é previsão, não leitura da norma.

## 14. Wikipedia, GDDR7 SDRAM (baixa autoridade)
URL: https://en.wikipedia.org/wiki/GDDR7_SDRAM . Procedência: `derived`.
PAM3, 32 Gbps/pino inicial, até 48 Gbps/pino na norma, 1,2 V. **Não cobre** encapsulamento, 24 Gbit, clamshell nem JESD239.

## 15. PCI-SIG, comunicado "PCI-SIG Achieves 32GT/s with New PCI Express 5.0 Specification" (29 de maio de 2019), cópia na Design & Reuse
URL: https://www.design-reuse.com/news/46222/32gt-s-pci-express-5-0-specification.html . Autoridade: comunicado da entidade, republicado. Procedência: `confirmed (PCI-SIG, comunicado)`.
"Delivers 32 GT/s raw bit rate and up to 128 GB/s via x16 configuration"; "Maintains backwards compatibility with PCIe 4.0, 3.x, 2.x and 1.x". **Não cita codificação** nem diz se 128 GB/s soma as duas direções.

## 16. Wikipedia, PCI Express (baixa autoridade)
URL: https://en.wikipedia.org/wiki/PCI_Express . Só os primeiros 100.000 caracteres. Procedência: `derived`.
PCIe 5.0: 32,0 GT/s; 3,938 GB/s por pista; x16 63,015 GB/s por direção; 128b/130b desde o 3.0 ("PCI Express 3.0 upgraded the line encoding scheme to 128b/130b"; a tabela não repete a codificação nas linhas 4.0 e 5.0); slot x16: "up to 5.5 A at +12 V (66 W) and 75 W combined" e 3 A em 3,3 V (9,9 W); conector x16: 89 mm (slot) e 84,3 mm (placa); altura 111,15 mm; comprimento 312,00 mm.

## 17. connectorselection.com, "PCIe Form Factor Guide" (secundária)
URL: https://connectorselection.com/articles/pcie-add-in-card-bracket-form-factor-guide/ . Procedência: `derived`.
Altura 111,15 mm (4,376 in), bracket 120,65 mm (4,750 in), comprimento 312,00 mm; slot de bracket 18,42 mm; "confirmed per PCI-SIG CEM Rev 5.0" (afirmação do site, sem página). **Diverge** do bracket da CEM 3.0 (120,02 mm), ver Conflitos.

## Contas

### C1. Energia: 600 W ÷ 12 V = 50 A, e o conector único de 600 W
| Passo | Conta | Resultado | Estado |
|---|---|---|---|
| Corrente nominal | 600 W ÷ 12 V | 50 A | fecha com a conta, mas **a norma tabela 55 A** (Intel, Tabela 3-5) |
| Fator da tabela | 150/12 = 12,5; 300/12 = 25; 450/12 = 37,5; 600/12 = 50; × 1,10 = 13,75; 27,5; 41,25; 55 | as 4 linhas batem com × 1,10 | conta minha; a fonte **não explica** o 10% (provável margem de tensão/RMS) |
| Tensão mínima | +5%/-8% → 12 × 0,92 = 11,04 V; 600 ÷ 11,04 | 54,3 A | conta minha; coerente com 55 A, não é a explicação declarada |
| Por pino | 6 pinos +12 V (pinos 1 a 6) e 6 COM | 50/6 = 8,33 A nominal; 55/6 = 9,17 A no teto | conta |
| Contra a classificação do contato | Molex: 9,5 A por pino | 9,5 ÷ 9,17 = 1,036 (folga de 3,6% no teto de 55 A); 9,5 ÷ 8,33 = 1,14 | conta |
| Capacidade dos 6 contatos | 6 × 9,5 A × 12 V | 684 W | conta; a Molex diz "675 W" sem mostrar a conta |
| Conflito 9,2 A | hwbusters diz 9,2 A por pino; 55/6 = 9,17 ≈ 9,2 | os dois **não são a mesma coisa que 9,5 A** | ver Conflitos |

Veredito: 600 ÷ 12 = 50 A fecha como corrente nominal sobre 6 pinos de ida; o texto não deve dizer "50 A" como limite do conector, porque a norma usa 55 A.

### C2. Placa de 600 W de TBP e um único conector de 600 W
- O conector de 600 W (SENSE Ground/Ground) permite **600 W sustentados** só por ele (Intel p. 26 e 27: o valor "alone", sem o slot).
- O slot x16 dá até 75 W (+12 V: 5,5 A = 66 W; +3,3 V: 3,0 A = 9,9 W; soma ≤ 75 W; CEM 3.0, p. 44 e 45).
- Teto elétrico somado: 600 + 75 = 675 W. A Molex anuncia "675W add-in card ready" (slide 1). Que 600 + 75 = 675 é conta minha; a Molex não explica o número.
- Fecha: 600 W de TBP cabem nos 600 W do conector, e o slot dá folga de até 75 W. **Não está nas fontes** como a NVIDIA reparte a carga entre slot e conector, nem que a placa dependa do slot. "Total board power" pode incluir o slot; o datasheet não diz.
- Picos: R = 2,5 no rail +12 V do conector e R = 3 na potência total, até 100 µs (Intel Tabela 3-1). Conta minha para 600 W: 1.500 W e 1.800 W de pico por até 100 µs. Excursão no slot (13,75 A por 0,1 ms) vem só de fonte secundária (hwbusters).
- Não fecha por fonte: o slot de 75 W vem da CEM **3.0**; o valor da CEM 5.x não foi aberto.

### C3. Memória: 32 posições × 3 GB = 96 GB e 16 controladores de 32 bits
| Passo | Conta | Estado |
|---|---|---|
| 24 Gbit em GB | 24 ÷ 8 = 3 GB | conta; chip de 24 Gbit existe (Samsung, via Club386; Micron só em snippet) |
| 32 × 3 GB | 96 GB | fecha |
| 16 × 32 bits | 512 bits | fecha |
| 32 chips ÷ 16 controladores | 2 chips por controlador de 32 bits | **possível pela norma**: JEDEC cita modo de 2 canais para "double system capacity"; Micron lista "Clam shell: Yes" e largura 32 bits; HWCooling diz "two on a single 32bit interface" |
| Cada chip em modo de 2 canais | 4 canais por encapsulamento, 32 bits: 32 ÷ 4 = 8 bits por canal; 2 canais = 16 bits por chip | conta minha, **não está em nenhuma fonte**. Largura de canal da JESD239 é lacuna |
| Banda | 28 Gbps × 512 ÷ 8 = 1.792 GB/s | fecha; 28 Gbps está dentro dos 32 Gb/s da Micron e do teto de 48 Gbps (192 GB/s por dispositivo ÷ 4 B = 48 Gbps, conta que fecha) |
| Mecânica | 2 chips por controlador, um por face, é o "clamshell" | o encapsulamento de 266 esferas, 12 × 14 × 1,1 mm (Micron) com o modo clamshell sustenta a viabilidade; a **ligação ponto a ponto, quem fica em cada face e as esferas ligadas em cada modo** não estão em fonte aberta |

Veredito: 96 GB com 32 chips de 3 GB em 16 controladores é compatível com a norma (modo de 2 canais) e com o encapsulamento da Micron. Não prova que a placa seja assim: "3 GB por chip" na RTX PRO 6000 continua `derived`.

### C4. PCIe 5.0 x16
- 32 GT/s × 128/130 = 31,508 Gbit/s por pista; ÷ 8 = 3,938 GB/s; × 16 = **63,015 GB/s por direção** (conta minha, igual ao valor da Wikipedia). Bruto sem codificação: 32 × 16 ÷ 8 = 64 GB/s por direção; o "128 GB/s" do comunicado é, por conta, o bruto das duas direções (o texto não diz).
- Comparação: 1.792 ÷ 63,015 = 28,4 vezes. Contra 64 GB/s: 28 vezes.
- A codificação 128b/130b para 5.0 só consta de Wikipedia (baixa autoridade).

### C5. DisplayPort UHBR20
- 4 pistas × 20 Gbps = 80 Gbps (Wikipedia; VESA diz 80 Gbps "four-lane").
- Com 128b/132b: 80 × 128/132 = 77,58 Gbps. A Wikipedia diz 77,37. **Diferença de 0,2 Gbps não explicada** na fonte (overhead adicional não identificado).

## Conflitos
1. **Altura padrão na CEM 3.0.** `conflict: true`. Texto p. 127: "111.28 mm (4.376 inches)"; Tabela 9-1: "111.28 mm (4.381 inches)"; Fig. 9-1 e p. 133: 111,15 [4,376]. 111,15 mm = 4,376 in; 111,28 mm = 4,381 in. Três números na mesma norma. Usar 111,15 ±0,13 (p. 133 diz que é o valor fixo para placas gráficas).
2. **Comprimento.** `conflict: true`. p. 93: "321.00 mm (12.283 inches)"; todas as demais: 312,00 mm; 12,283 in = 312,0 mm. Provável erro de digitação na norma.
3. **Altura do datasheet x CEM.** `conflict: true`. Datasheet: 5,4" (137,16 mm). CEM 3.0: 111,15 mm. A placa excede a altura padrão em cerca de 26 mm. "Extended height" não aparece nas páginas lidas da CEM 3.0. A cota 137,15 [5,400] da Fig. 9-1 é uma posição ao longo do **comprimento** do cartão, não altura: coincidência de número.
4. **Corrente por pino.** `conflict: true`. Molex: 9,5 A por pino de potência (fabricante). hwbusters: 9,2 A (secundária). Intel: 55 A no conector, que dá 9,17 A por pino (conta). Não são medidas da mesma coisa: 9,5 A é a classificação do terminal; 55 A ÷ 6 é a exigência da norma.
5. **600 W x 675 W.** Intel: 600 W sustentado pelo conector. Molex: "675W add-in card ready". Não é conflito se 675 = 600 + 75 do slot, mas **nenhuma das duas fontes diz isso**.
6. **Bracket.** CEM 3.0: 120,02 REF (4,725 in). connectorselection: 120,65 (4,750 in), atribuindo à CEM 5.0. A diferença é 0,63 mm. Revisão diferente ou cota de referência: não decidido.
7. **hwbusters, 1324,8 W.** Erro da própria fonte, corrigido num comentário para 662,4 W. Não usar.
8. **UHBR20 efetivo.** 77,37 (Wikipedia) x 77,58 (conta): ver C5.
9. **Nome do conector.** Datasheet da placa: "PCIe CEM5 16-pin". Pela Intel, 12VHPWR é da CEM 5.0 e 12V-2x6 da CEM 5.1. O datasheet não diz qual das duas. A placa pode ter H+ ou H++; as fontes do projeto (Gamers Nexus: "12VHPWR"; revendedor: "12V-2x6") também divergem.

## Só snippet (não valem como fato)
- Micron, GDDR7 product brief (`my.micron.com/.../gddr7-product-brief.pdf`): snippet diz 266 esferas, 12 × 14 × 1,1 mm, passo 0,75/0,73 mm, clamshell. Arquivo rejeitado pelo servidor ("Request Rejected"). O mesmo dado está na seção 9 por uma segunda via, aberta.
- AccuriTech, prévia da JESD239.01: snippet diz que o índice lista a figura "266-ball BGA ball-out". Página 403.
- TrendForce / Guru3D / Wccftech: Micron com 24 Gb a 28 e 32 GT/s; Samsung 24 Gb a 42,5 Gbps (Tom's Hardware, texto cortado). Guru3D 403; TrendForce e Wccftech não abertos.
- Comprimento dos pinos do 12V-2x6 (Wikipedia/Cliffipedia): sense de 4 mm para 2,75 mm, ponto de contato a 3 mm; outro resultado fala em "0,1 mm". Duas versões, não abertas. O valor 2,75 aparece como cota "(2.75) END OF PIN CHAMFER" na Fig. 5-9 da Intel, mas sem rótulo claro do que é.
- Distribuidor: Molex 2191160161 com 9,2 A (potência) e 1,0 A (sinal). Não aberto.
- knightli.com: tabela SENSE de cinco linhas. Substituída pela Tabela 3-6 da Intel, aberta.
- Samsung: nota de imprensa de 24 Gb (news.samsung.com). Timeout.

## Não abertas
pcisig.com (bloqueada pela ferramenta); jedec.org e Business Wire (403); AccuriTech (403); Molex 987651-9552 e página de peça 2191160161 (503); AnandTech 21287 (redirecionamento e 503); TechPowerUp (403); Intel 336521 (ATX 3.x completo, não aberto); a norma CEM 5.x; a JESD239; a norma DisplayPort 2.1b; desenho `472720001_sd.pdf`.

## Lacunas
1. **CEM 5.x.** Nenhuma cópia dela aberta. Mecânica e slot vêm da 3.0 (2013). Confirmar na 5.x: altura, comprimento, bracket, potência do slot x16 (aqui 5,5 A em +12 V e 3 A em 3,3 V), furação.
2. **"Extended height"** e **bracket de dois slots**: sem definição nem desenho nas páginas lidas. Só o bracket de um slot (Fig. 9-5) e o passo de 20,32 mm. Largura de bracket de dois slots não está registrada; 2 × 20,32 = 40,64 mm é conta de passo, não cota de bracket.
3. **Furação da bracket.** Só "#4-40" e as cotas da Fig. 9-5, que eu não consegui separar em furo a furo com segurança.
4. **12V-2x6.** Comprimento dos pinos de potência e de sinal em mm (diferença 12V-2x6 x 12VHPWR); significado das cotas de altura e profundidade do cabeçote (Fig. 5-8 a 5-10); altura total do cabeçote.
5. **A placa usa 12VHPWR ou 12V-2x6?** O datasheet só diz "CEM5 16-pin".
6. **Como a placa divide 600 W entre conector e slot**, e se o "total board power" inclui o slot.
7. **DisplayPort.** Dimensões do receptáculo só em Wikipedia (baixa autoridade). Norma VESA e desenho da Molex não abertos. Como o DP 2.1b da placa chega a UHBR20 (cabo, nível de certificação) não está nas fontes.
8. **GDDR7.** JESD239 não aberta: largura de cada canal, quais esferas mudam no modo de 2 canais, desenho do encapsulamento (266 esferas, 12 × 14 × 1,1 mm vêm da Micron via JPR). Qual fabricante e qual densidade a placa usa: não consta nestas fontes. Densidade de 24 Gbit confirmada só por imprensa (Samsung) e snippet (Micron).
9. **PCIe 5.0.** Codificação 128b/130b só em Wikipedia; norma não aberta. O "128 GB/s" do comunicado não diz se é por direção.
10. **Arquitetura do chip.** Fora do escopo desta rodada.
