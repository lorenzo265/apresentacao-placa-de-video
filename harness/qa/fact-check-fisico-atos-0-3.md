# Fact-check independente: fatos físicos dos atos 0 a 3 (F1, rodada de 2026-11-10)

- Data: 2026-11-10
- Auditor: agente `fact-checker` (Fable), em contexto separado do `spec-researcher`, que produziu o material.
- Escopo: 36 fatos novos e 8 lacunas em `harness/spec/card.spec.json`; seções 14 a 17 de `harness/spec/sources/physical-card-sources.md`.
- Resultado: **não aprovado na primeira passada**: 1 achado bloqueava (a classe dos fatos tirados do teardown), 13 pediam ajuste e 6 eram notas. Correções aplicadas no mesmo dia pela sessão principal. **A segunda passada ainda não foi feita.**
- Padrão dos erros: nenhum valor numérico errado e nenhuma citação divergente; as três contas fecham. Os problemas estavam na classe, em âncoras, em três lacunas e em redação.
- Origem do achado que bloqueava: o briefing da sessão principal ao `spec-researcher` dizia "Gamers Nexus é sempre `derived`". Isso não está na regra escrita, que dá `confirmed` ao teardown da própria placa.

## Método do auditor
**Leitura direta (imagem):**
- Guia rápido da NVIDIA: PDF baixado, p. 1 a 18 (a parte em inglês vai até a p. 15).
- Datasheet, p. 1 (`references/cache/nvidia/nv-13-p-1.png`).
- Intel 613768 rev. 2.11: p. 25, 26, 63, 67 e 68.
- Fotos gn-02, gn-11, gn-15, gn-16, gn-17, gn-29, gn-30, gn-31, gn-33 e gn-42, a 52% da resolução original.

**Extração automática (não é leitura humana):**
- Gamers Nexus: 4 passagens dirigidas, conferindo frase a frase e pedindo as frases vizinhas. A ferramenta não devolve a seção inteira.
- Página e anúncio da RTX 5090, Puget, Jon Peddie: 1 passagem cada.

## O que passou
- **Guia rápido (seção 14), literal:** tabela Equipment da p. 5 (cabo de 4x 8 pinos para 1x 16 pinos, extender), "dual-slot" (p. 8), conector "on the top edge" e "four separate PCIe 8-pin cables" (p. 10), avisos da p. 12, desenho de 12 posições grandes e 4 pequenas (p. 10), desenho do bracket com 4 DisplayPort em fileira e sem grade (p. 13). O guia não traz watts, "12VHPWR", "12V-2x6", peso nem dimensões.
- **Datasheet p. 1 (seção 17):** título, "600 W power design", "dual axial pathways", os quatro itens de Key Features e o render conferem.
- **Gamers Nexus (seção 15):** as 9 frases dos passos 1 a 7 existem, na ordem registrada, sem outro passo entre elas. Conferem também as de aletas, aberturas, PCB, fluxo, memória e adaptador.
- **Norma (Intel):** Tabela 3-5 (2x4 = 150 W e 13,5 A; 12V-2x6 = 600 W e 55 A), p. 63 (12 pinos ligados), p. 26 (quatro sinais laterais), Tabela 5-10.
- **Contas:** 4 x 150 W = 600 W; 600 W / 12 V = 50 A; 1792 / 63,015 = 28,44.
- **Fatos sem erro de valor nem de classe:** `card.model_name`, `card.slots`, `card.power_connector_position`, `card.power_adapter`, `card.power_adapter_inputs`, `card.power_current_12v_a`, `card.airflow_pathways`, `card.face_b_layout`, `card.bracket_layout`, `card.housing_vs_5090`, `teardown.step_count`, `pcb.shape`, `ref5090.thermal_interface`, `ref5090.pcb_pieces`, `ref5090.vapor_chamber`, `card.vapor_chamber_jpr`, `card.mem_vs_pcie_ratio`, `card.dp_max_gbps`.
- **`mem.back_layout`:** a foto sustenta. O auditor contou em gn-29 5 à esquerda, 5 à direita, 4 na borda do conector de energia e 2 na borda oposta; gn-30 e gn-31 repetem. A faixa de 15 a 16 é honesta.
- **Lacunas:** nenhuma diz "a NVIDIA não publica".

## Achados e resolução
| # | Severidade | Onde | Achado | Resolução |
|---|---|---|---|---|
| 1 | bloqueia | 12 fatos novos e 6 antigos; arquivo de fontes | A mesma fonte (teardown da Gamers Nexus) tinha duas classes: `confirmed` nos fatos antigos, `derived` nos novos. `ARCHITECTURE.md`, seção 3, diz `confirmed` = "fonte oficial ou teardown da própria placa", e a auditoria anterior manteve os passos E1 a E7 como `confirmed`. O auditor pediu decisão humana entre manter a regra escrita (caminho A) ou mudá-la (caminho B) | Aplicado o **caminho A**, que é a regra escrita: sobem a `confirmed` `teardown.e3` a `e7`, `card.airflow_through`, `card.exhaust_slats`, `card.pcie_adapter_separate` e `card.fins_taller_depression`. Ficam `derived`, com a nota dizendo o que é frase da fonte e o que é leitura nossa de foto: `teardown.e1`, `teardown.e2`, `pcb.position`. `teardown.step_count` continua `derived`. Frase "sem exceção" corrigida no arquivo de fontes. **Fica para o humano confirmar ou trocar pelo caminho B** |
| 2 | ajusta | lacuna `airflow.direction`; `card.exhaust_slats` | A lacuna dizia "nenhuma fonte diz". A Gamers Nexus diz por onde o ar sai: "This projects the air out at an angle that’s up and away from the card." | frase registrada; lacuna reescrita (falta só a face de entrada); o beat a1.3 pode afirmar a saída pelo topo |
| 3 | ajusta | 6 fatos do guia rápido | A âncora da seção 14 não existia | corrigida nos 6 fatos |
| 4 | ajusta | `mem.positions_per_controller` | A âncora não continha a conta 32 / 16 | aponta para `standards-sources.md`, conta C3 |
| 5 | ajusta | `card.power_connector_pins` | `conflict: true` sem fonte que discorde; faltavam a p. 26 e a Tabela 5-10 | marca retirada; nota completada (6 de +12 V e 6 de retorno) |
| 6 | ajusta | `card.power_adapter_nominal_w` | "Não é limite do conector" lia-se como se 600 W não fosse o teto | nota reescrita |
| 7 | ajusta | `mem.back_layout` | "Em U" contradiz os quatro grupos | valor reescrito: nos quatro lados, com a faixa de 15 a 16 |
| 8 | ajusta | `vrm.inductor_row`; lacuna `vrm.inductor_count` | "Uma fileira" estava incompleto; "de 10 a 20" não serve | valor: fileiras em mais de uma borda; lacuna reescrita com a pista do blog (23 mais 1), marcada como pista |
| 9 | ajusta | lacuna `card.mem_pairing_mechanism` | Pressupunha 32 chips; o que é `confirmed` são 32 posições | reescrita ("se as 32 posições estiverem ocupadas") |
| 10 | ajusta | lacuna `pcb.plate_function` | Negativa universal | "não achamos fonte que descreva" |
| 11 | ajusta | `card.power_per_8pin_w` | `confirmed` para valor de norma não está previsto na regra escrita | nota acrescentada; a regra entra na mesma decisão humana do achado 1. Id não renomeado |
| 12 | ajusta | `teardown.e4`, `e5`, `e6` | Tradução imprecisa | "grampo que prende o slot PCIe à placa", "desencaixa-se com alavanca", "mola de lâmina" |
| 13 | ajusta | `card.fins_taller_depression` | Juntava duas frases de trechos diferentes; "placa do PCB" lia-se como o PCB | separado em duas afirmações, com as frases e a ressalva da face |
| 14 | ajusta | arquivo de fontes, trechos antigos | Contradiziam as seções novas | marcados como superados |
| 15 | nota | seção 14 | Remissão à p. 9 inexata; a data vem só do nome do arquivo | corrigido |
| 16 | nota | seção 14 | Os desenhos das p. 9 e 10 mostram dois ventiladores e o conector no topo | registrado; citado em `card.fans` |
| 17 | nota | seção 15 | Faltavam frases e as datas do artigo e do vídeo | registradas |
| 18 | nota | `teardown.e1` | "Não existe placa traseira lisa" é negativa universal | nota reescrita |
| 19 | nota | lacuna `power.connector_variant` | A marca "H++" ou "H+" no cabeçote resolveria | caminho registrado na lacuna; foto em resolução cheia fica para o `visual-qa` |
| 20 | nota | `Requisitos da disciplina.md`; `CLAUDE.md` | Guia rápido fora da tabela de fontes; contagem de fatos desatualizada | atualizados |

## Decisão que fica para o humano
A regra de procedência escrita só cobre parte do que o spec já faz. Estão sem definição escrita:
- se a frase literal do teardown de terceiro sobre esta placa é `confirmed` (hoje é, pela regra escrita) ou `derived`;
- o uso de `derived` para conta nossa, norma aplicada à placa, revisor e leitura de foto;
- o uso de `confirmed` para valor de norma;
- o significado do campo `conflict`.

Se a regra mudar (caminho B), os seis fatos antigos (`card.fans`, `card.power_connector_gn`, `card.thermal_interface`, `chip.marking`, `mem.positions`, `mem.back_modules`) e os nove desta rodada descem para `derived`, e a mudança se propaga para beats, planos e notas do vault. Efeito a pesar: "pasta térmica" (esta placa) e "metal líquido" (5090) passariam a ter a mesma classe.

## O que o auditor não conseguiu verificar
- O texto da Gamers Nexus por leitura humana: a extração não devolve a seção inteira. O vídeo não foi visto.
- Fotos não abertas: gn-03, gn-08, gn-09, gn-13, gn-21, gn-25 a gn-27, gn-36, gn-38, gn-40 (fendas da borda superior, a placa do passo 5, fileiras diagonais de indutores, adaptador PCIe).
- Em gn-33, se as duas fileiras de indutores estão em bordas diferentes do PCB ou se uma é a de gn-42 vista de outro ângulo.
- Datasheet p. 3 e whitepaper p. 30: não reabertos nesta rodada.
- `standards-sources.md` continua não auditado como um todo; a codificação 128b/130b segue só em fonte de baixa autoridade.

## Estado
Correções aplicadas. Nada desta leva está aprovado: falta a segunda passada do `fact-checker` e a confirmação humana da regra de classe (achado 1).
