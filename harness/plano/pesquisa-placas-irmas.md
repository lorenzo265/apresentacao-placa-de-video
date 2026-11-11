# Pesquisa: como a NVIDIA monta e como se desmonta as placas irmãs (2026-11-11)

Objetivo: preencher lacunas do `harness/design/assembly-plan.md` (seções 1, 3, 12.5): interior do cooler, separação da carcaça, VRM, lado de remoção. Regra: sem fonte, sem fato.

Classificação usada (a do pedido): **confirmed** = da própria RTX PRO 6000 (já no repo, GN); **derived** = placa irmã com o mesmo chip GB202 (RTX 5090 FE); **inferred** = outro chip ou geração (5080 FE = GB203, 5070 FE = GB205, 4090/4080 FE, 6000 Ada).

## 0. Limites da pesquisa (ler antes)

- TechPowerUp (teardown 5090/5080/5070 FE), Igor's Lab (guia de desmontagem da 4090 FE e página do cooler da 5090 FE), TweakTown e EK (manual) responderam **HTTP 403** ao fetch. O que se sabe deles vem **só de resumos do buscador**, não da página. Marcado "(resumo do buscador)": vale como pista, não como citação. Antes de virar fato no spec, abrir a página no navegador e conferir.
- **Nenhuma fonte textual encontrada diz de que lado (face dos ventiladores ou oposta) cada peça sai.** As fotos dos teardowns não foram vistas por esta pesquisa.
- Não encontrei teardown de RTX 5070 Ti FE nem 5060 Ti FE (a 5070 Ti não teve FE na linha geral; resultados são de placas de parceiros). Não encontrei teardown da RTX 6000 Ada (é blower, outro desenho).
- Nenhum número deste relatório foi estimado. Onde fontes divergem, as duas aparecem.

## 1. Tabela por placa

### 1.1 RTX PRO 6000 Blackwell WE (confirmed, já no repo)

| Item | O que a fonte diz | Fonte |
|---|---|---|
| Ordem | Placa/bracket traseiro; 1 parafuso e sai o quadro externo (shroud); parafusos em volta do centro e saem as tampas centrais; desparafusa o grampo do slot PCIe e sai o adaptador; sai uma placa que cobre o PCB (expõe 16 módulos de memória com pads tipo massa); cabos flat e parafusos da mola de pressão; o PCB sai | https://gamersnexus.net/gpus/nvidia-rtx-pro-6000-blackwell-benchmarks-tear-down-thermals-gaming-llm-acoustic-tests (releitura nesta rodada) |
| Lado | não dito no texto | idem |
| Carcaça x cooler | o quadro externo sai com 1 parafuso; o texto não menciona separar o dissipador | idem |
| Interior do cooler | **não mencionado** (sem câmara de vapor, heatpipes ou VRM no artigo) | idem |
| Interface térmica | esperavam metal líquido, encontraram pasta térmica; 32 posições de memória; indutores com contato ruim nos pads | idem |
| Chip | GB202-870-A1 | idem |

### 1.2 RTX 5090 Founders Edition (derived, mesmo GB202)

| Item | O que as fontes dizem | Fonte |
|---|---|---|
| Ordem (TPU, resumo do buscador) | 4 parafusos do slot cover; 1 parafuso marcado; levantar o quadro a partir do slot PCIe; deslizar a tampa superior (triangular, com ranhura usinada, dá acesso ao conector de 16 pinos); 2 parafusos T6 perto do PCIe; 4 T6 do conector PCIe, levantar o PCB do slot; tirar o cabo do display; 4 T6 do suporte metálico da GPU; levantar o PCB principal "from the cooler". Aviso de fita nos cabos para não danificar. | https://techpowerup.com/review/nvidia-geforce-rtx-5090-founders-edition/5.html (403; resumo do buscador) |
| Lado | "lift ... up"; sem lado explícito | idem |
| Carcaça x cooler | o quadro é levantado a partir do slot; o dissipador permanece com a carcaça; ímãs no perímetro do quadro (para a 5080 FE, ver 1.3) | TPU (resumo); https://hwcooling.net/en/nvidia-geforce-rtx-5080-fe-review-more-performance-same-price/2 |
| Câmara de vapor | "3D Vapor Chamber" sobre o PCB, coleta calor de GPU, VRAM e energia | https://wccftech.com/nvidia-rtx-50-double-flow-through-founders-edition-thermal-solution-teardown-dual-fans-dual-slot-600w-cooling/ (lido) |
| Heatpipes | **cinco**, "massive", cobre 8 mm soldado à câmara (Wccftech, TweakTown via buscador). **Conflito:** PCGH diz "insgesamt zehn Heatpipes" | Wccftech (lido); https://www.tweaktown.com/news/102629/nvidias-new-geforce-rtx-50-founders-edition-thermal-solution-teardown-dual-slot-600w-cooling/index.html (403; resumo); https://www.pcgameshardware.de/Geforce-RTX-5090-Grafikkarte-281029/Specials/Founders-Edition-mit-High-Density-PCB-und-Double-Pass-Through-1463646/ (lido) |
| Dissipadores | **três** blocos: dois laterais ligados pelos heatpipes e um central sob o PCB; "several aluminum fins" | Wccftech (lido) |
| Fixação das aletas à carcaça | não descrita em nenhuma fonte lida | n/d |
| Metal líquido | sim, com "airtight seal around the GPU die" | https://wccftech.com/nvidia-explains-the-marvelous-design-of-the-geforce-rtx-5090-founders-edition/ (lido); PCGH (lido) |
| PCB | 3 placas (principal, daughter PCIe, daughter de I/O) + PCB flexível; fibra de vidro nos substratos para o DP 2.1 | Wccftech (lido); PCGH cita CAD do der8auer: "gleich drei einzelnen Platinen" |
| VRM | PCGH: "insgesamt 34 Phasen für GPU und Grafikspeicher" (23 na 4090 FE). Controlador **não citado** nas fontes lidas. (Tom's Hardware via buscador: 30 na placa principal + 4 no verso; não conferido.) | PCGH (lido); https://www.tomshardware.com/pc-components/gpus/nvidia-shows-off-geforce-rtx-5090-fe-pcb-30-phases-of-stable-575w-power (só título lido) |
| Memória | 16 GDDR7, todos na frente do PCB, nenhum no verso; o verso tem "basic circuit components, solder points, and a connector" | https://www.pcgamesn.com/nvidia/geforce-rtx-5090-pcb (lido) |
| Fragilidade | conector FPC de alta densidade entre a placa do PCIe e a principal: 1 pino torto e 1 quebrado na remontagem; sem peça de reposição | https://www.notebookcheck.net/Nvidia-RTX-5090-Founders-Edition-teardown-reveals-fragile-modular-design-that-repair-experts-call-a-disaster.1147864.0.html (lido) |

Atenção: a 5090 FE tem **16 módulos na face da GPU** (PCGamesN); a PRO 6000 tem 16 no verso e 16 posições vazias na frente (GN, repo). Memória não é derivável da 5090.

### 1.3 RTX 5080 Founders Edition (inferred: chip GB203)

| Item | Dado | Fonte |
|---|---|---|
| Ordem | "exatamente o mesmo processo da 5090 FE"; fita nos três cabos pequenos ao soltar o PCB | TPU 5080 (403; resumo do buscador) https://techpowerup.com/review/nvidia-geforce-rtx-5080-founders-edition/5.html |
| Metal líquido | TPU: "não há metal líquido na 5080 FE". PCGH: metal líquido em todas as FE novas. **Conflito**, não resolvido | TPU (resumo); PCGH (lido) |
| Cooler | aletas abertas dos dois lados do PCB central, só a parte central é cheia; ímãs no perímetro do quadro "facilitam a montagem" e seguram parafusos; 2 parafusos na parede traseira do quadro tampam furos roscados | https://hwcooling.net/en/nvidia-geforce-rtx-5080-fe-review-more-performance-same-price/2 (lido) |
| Heatpipes, VRM | não encontrados | n/d |

### 1.4 RTX 5070 Founders Edition (inferred: GB205)

| Item | Dado | Fonte |
|---|---|---|
| Ordem (resumo do buscador) | "muito parecida com a 5090": 4 parafusos, deslizar **duas** tampas triangulares em ranhuras usinadas, 6 parafusos do PCB do PCIe, levantar o PCB, por último tirar a "backplate" | https://techpowerup.com/review/nvidia-geforce-rtx-5070-founders-edition/5.html (403) |
| Heatpipes | "quatro" aparece em um resumo do buscador e **não** se repetiu na checagem seguinte: não verificado | idem |
| 5070 Ti / 5060 Ti FE | sem teardown encontrado | n/d |

### 1.5 RTX 4090 / 4080 FE (inferred: outra geração)

| Item | Dado | Fonte |
|---|---|---|
| Desenho | fluxo axial em um lado (flow-through único), PCB longo; PCGH chama a 5090 de sucessora do "Dual Axial Flow Through" da série 4000 FE | PCGH (lido) |
| Desmontagem | TPU: "não muito diferente das FE anteriores, poucos minutos" (resumo); Igor's Lab tem guia passo a passo para quem troca por water block, FE sem selos; só trechos acessíveis | https://www.igorslab.de/en/nvidia-geforce-rtx-4090-founders-edition-correct-disassembly-guide-for-water-cooling-converters/1/ (403) |
| VRM | 23 fases (4090 FE) por comparação do PCGH; Igor: 10 fases no trilho 1 (resumo do buscador) | PCGH (lido) |

### 1.6 RTX 6000 Ada (inferred)

Blower de dois slots (ServeTheHome, https://www.servethehome.com/nvidia-rtx-6000-ada-graphics-card-review-pny/, só resumo). Sem teardown achado. Não serve de referência de montagem para o nosso modelo.

## 2. Resposta direta: "no desmonte real, de que lado as placas e componentes são removidos?"

**Nenhuma fonte textual consultada afirma o lado.** O que há:

1. Os sequências do GN (PRO 6000) e do TPU (5090/5080/5070) são verbos de "levantar", "deslizar", "tirar", sem face A ou B.
2. O que se sabe da estrutura: o quadro externo e as tampas saem primeiro; o PCB é levantado do cooler **por último** e o dissipador fica com a carcaça (confirmed na PRO 6000: carcaça, ventiladores e aletas ficam, repo seção 3).
3. A pasta na GPU fica à vista quando o PCB sai (GN), ou seja, a face do chip fica voltada para o cooler.

Conclusão honesta: o lado é **lacuna**. Fechar com uma das duas vias: (a) ver as fotos do TPU 5090 FE e as do GN no navegador; (b) manual do water block EK-Quantum Vector3 FE RTX 5090 (https://www.ekwb.com/shop/EK-IM/EK-IM-3831129901179.pdf, 403), que mostra o PCB saindo.

## 3. O que muda no nosso modelo (PROPOSTAS, não fatos)

1. **E8 continua `inferred`.** Nenhum teardown mostra o cooler da PRO 6000 aberto. A 5090 FE (derived) dá a melhor base: câmara de vapor central + heatpipes soldados + 3 blocos de aletas. A seção 12.5 já usa `heatpipe_pitch_stack` da 5090 FE; manter com a marca `derived`.
2. **Contagem de heatpipes.** Se o modelo mostra heatpipes, usar a contagem da 5090 FE só como `derived` e com a divergência registrada (cinco x dez). Sugestão: perguntar ao autor ou mostrar "vários".
3. **Separação carcaça x cooler.** Sugestão: a carcaça (quadro + grade) fica solidária ao dissipador; o que sai antes são o aro, as tampas centrais e o PCB. Coerente com GN e TPU. Não animar "carcaça se abrindo" como fato.
4. **Ímãs no perímetro do quadro** (HWCooling, 5080 FE): possível detalhe a conferir na PRO 6000 antes de modelar. Se não houver foto, não modelar.
5. **Conector FPC entre a placa do PCIe e a principal:** é o ponto frágil nas FE. Se mostrarmos o cabo flat, vale um beat curto, marcado `derived` (5090) e `confirmed` apenas para "existem cabos flat" (GN).
6. **VRM:** não há número da PRO 6000. Usar 34 fases (PCGH, 5090 FE) só como contexto `derived`, nunca como valor da placa. Os blocos de potência continuam como proposta do `architecture-inferencer`.
7. **Metal líquido x pasta:** a PRO 6000 usa pasta (GN, confirmed) enquanto a 5090 FE usa metal líquido. Manter o exemplo já previsto no plano; a dúvida sobre a 5080 FE (TPU x PCGH) fica fora do vídeo.
8. **Memória:** não derivar da 5090 FE (lá 16 módulos na frente; aqui 16 no verso e 16 posições vazias).
9. **Conferir antes de fato:** abrir TPU 5090/5080/5070 FE e o guia da 4090 FE do Igor's Lab no navegador; passar pelo `fact-checker`.
