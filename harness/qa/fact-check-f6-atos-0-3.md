# Fact-check da F6: textos da placa física (atos 0 a 3, a7.5 e a7.6)

- Data: 2026-11-10
- Auditor: agente `fact-checker` (Fable), em contexto separado do `technical-writer`, que escreveu os textos.
- Escopo: as 32 entradas novas de `harness/content/pt-BR/beats.json` (a0.1 a a0.4, a1.1 a a1.6, a2.1 a a2.12, a3.1 a a3.7, a7.5 e a7.6). Na mesma rodada, a terceira passada dos fatos físicos do spec (`fact-check-fisico-atos-0-3.md`).
- Resultado dos textos: **não aprovado na primeira passada**: 2 achados bloqueavam (a3.3 e a2.10), 11 pediam ajuste. Correções aplicadas no mesmo dia pela sessão principal. **Segunda passada no mesmo dia: aprovado com ressalvas**, com a condição de aplicar literalmente a correção N1 (seção no fim), o que foi feito.
- Resultado do spec (terceira passada): **aprovado com ressalvas**. N1 a N6 fechados, sem erro novo. Ressalvas: a regra de classe do teardown espera decisão humana; o texto da Gamers Nexus foi conferido só por extração dirigida; `standards-sources.md` não foi auditado como um todo.
- Padrão dos erros: todos os números na tela batem com o spec. Os problemas eram de redação que ia além da fonte (posição tratada como chip, trajeto de cabo afirmado sem fonte), de classe ("provável" onde a regra dá "derivado") e de negativa universal.

## Método do auditor
- **Leitura direta (imagem):** datasheet p. 3 (conferem 24.064 núcleos, 96 GB GDDR7 com ECC, 512 bits, 1792 GB/s, PCIe 5.0 x16, 4 DisplayPort 2.1b, 600 W de potência total, "1x PCIe CEM5 16-pin", 5,4" por 12", dois slots); foto gn-25 (adaptador PCIe). Das passadas anteriores: guia rápido, datasheet p. 1, cinco páginas da Intel 613768 e 12 fotos.
- **Extração automática:** comunicado da PCI-SIG (32 GT/s, 2019); Gamers Nexus (as passagens das rodadas anteriores).
- **Arquivos locais:** `beats.json`, `card.spec.json`, `physical-card-sources.md`, `video-plan.md`, `storyboard.json`, `proposal.md`, `ARCHITECTURE.md`, `viewer/src/header.js`, `revisao-artigo.md`, `Proposta formal.md`.

## O que passou sem erro
a0.2, a0.3, a1.2, a1.3, a1.5, a1.6, a2.1, a2.2, a2.3, a2.4, a2.5, a2.6, a2.7, a2.8, a2.12, a3.1, a3.2, a3.5, a3.6, a3.7 (20 beats), com notas pequenas em a0.2, a2.1 e a2.12.

Restrições respeitadas: 600 W como potência da placa; variante do conector em aberto; ar que atravessa a placa e sai pelo topo, sem saída única nem face de entrada; sem número de pás; bracket de I/O como primeira peça, com a identificação marcada como nossa; pasta térmica nesta placa.

## Achados e resolução
| # | Severidade | Onde | Achado | Resolução |
|---|---|---|---|---|
| 1 | bloqueia | a3.3, caption | "Em média 2 chips por controlador" trocava posição por chip e tirava a condição | caption reescrito: 32 posições, em média 2 por controlador; "se todas tiverem chip" |
| 2 | bloqueia | a2.10 | A ordem "adaptador, cabos flat, chip" dizia que os cabos ligam o adaptador ao chip. A proposta aprovada diz que o adaptador encaixa por conector de placa a placa, visto em gn-25, e que o cabo largo levaria o vídeo às saídas. "O trajeto é o da RTX 5090" não tinha fato | caption, fala e fonte reescritos: o cabo flat até as saídas é proposta nossa, provável |
| 3 | ajusta | a2.11 | "Provável" para a câmara de vapor contrariava a regra (placa irmã é `derived`) e a decisão D5. Negativa universal na fala | "derivada da RTX 5090 e de um revisor"; "o teardown que lemos não abre o cooler" |
| 4 | ajusta | a7.5, fala | A definição de "derivado" omitia a placa irmã | acrescentada. A de "confirmado" depende da decisão humana da regra de classe |
| 5 | ajusta | a3.3, fala | Negativa universal; "dois canais por controlador" não batia com a proposta aprovada (16 bits por chip) | reescrita |
| 6 | ajusta | a3.4, fala | "512 pinos de dados": a fonte diz interface de 512 bits | "512 bits de interface" |
| 7 | ajusta | a1.4 | "Não do conector" lia-se como negação; faltava "pela norma"; a fonte dos pinos é a PCIe CEM 5.1 via guia da Intel | caption e fonte reescritos, sem ponto e vírgula |
| 8 | ajusta | a2.9 | Não dizia de onde vem o 150 W | fala e fonte reescritas |
| 9 | ajusta | a1.1, caption | "Face A" é vocabulário interno; "ou seja" afirmava desta placa o que o datasheet não diz | reescrito |
| 10 | ajusta | a0.4 | "Cinco níveis" contra quatro nomes na trilha do cabeçalho | os cinco níveis passaram a ser enumerados; a trilha fica para a etapa de design |
| 11 | ajusta | a7.6 | "Lista completa: ver a documentação escrita" não se sustenta (o artigo não cita todas as fontes); faltavam os artigos acadêmicos | "Fontes principais"; a lista completa com data de acesso vai nos créditos do tour (ainda a montar) |
| 12 | ajusta | a0.1, headline | "Anatomia de uma GPU: da placa ao chip" só existe neste arquivo; o artigo entregue tem outro título | mantido como título do tour; a linha de fonte passou a citar o título do trabalho. **Decisão do grupo pendente** |
| 13 | ajusta | `video-plan.md` (a1.1, a1.3, a2.6, a2.10, a3.1); storyboard em rascunho | O plano estava atrás do spec (7 pás, sentido do ar, "mola de pressão", "em U", trajeto do cabo) | cinco linhas atualizadas. Os selos de a2.7, a1.5 e a2.9 no storyboard ficam para o `storyboard-director` |
| nota | | a2.1 | "Os sete passos" sugeria que a fonte numera | "em sete passos na nossa contagem" |
| nota | | a2.12 | Duas grafias da marcação | grafia da fonte nos dois |
| nota | | a0.2 | "A ar" sem fato | `card.airflow_pathways` acrescentado |
| nota | | `proposal.md`, `proposal.json`, `assembly.json` | Aviso de tela dizia "a NVIDIA não publica o número de fases" | "não achamos fonte com o número de fases" |

## Cobertura do plano
Cada beat dos atos 0 a 3 diz o que o plano pede. Os cortes têm justificativa (pás e sentido do ar são lacunas; o estágio E8 é proposta; "em U" foi corrigido no spec). O único corte sem justificativa era a data de acesso das fontes em a7.6, tratado no achado 11.

## O que o auditor não conseguiu verificar
- Tempo de fala e regra de leitura: o storyboard desses beats está em rascunho, com `hold` 0.
- Whitepaper (p. 8, 12, 13, 30 e Tab. 4): só pelos excertos locais, auditados em rodadas anteriores.
- A lista de referências do artigo entregue: usou o que `revisao-artigo.md` registra.
- O texto da Gamers Nexus sobre a 5090 FE que `proposal.md` cita para o cabo flat: não está em `spec/sources/`.
- `standards-sources.md` como um todo; a codificação 128b/130b segue só em fonte secundária (o beat a3.6 vale com ou sem ela: 28,4 ou 28,0 vezes).

## Segunda passada (2026-11-10)
Veredito do auditor: **aprovado com ressalvas, sob uma condição**. Os 13 achados e as notas fecharam. A correção criou um erro pequeno de precisão (N1), em parte vindo dos textos substitutos do próprio auditor. Com N1 aplicado literalmente, os 32 textos ficam aprovados sem nova passada.

| # | Severidade | Onde | Problema | Resolução |
|---|---|---|---|---|
| N1 | ajusta | a2.10 (fala e fonte), a2.11 (caption e fala), a2.7 (fala) | "RTX 5090" sem "Founders Edition". O PCB em três peças, a câmara de vapor e o metal líquido são da Founders Edition; as RTX 5090 de outros fabricantes têm projeto próprio | "RTX 5090 Founders Edition" nos cinco lugares, com os textos do auditor |

Sugestões do auditor que não bloqueavam, aplicadas com o texto dele: a1.4 voltou a dizer "conector de energia" (35 palavras); a3.3, fala, com "se todas tiverem chip"; a7.5, fala, com "o caminho do calor dentro do cooler" como exemplo de provável. `video-plan.md`: linhas a1.4 e a3.3 atualizadas.

Ressalvas que continuam:
- decisão humana da regra de classe do teardown (afeta a definição de "confirmado" em a7.5);
- decisão do grupo sobre o título de a0.1;
- a lista de fontes nos créditos, que a7.6 promete e ainda não existe (`STATUS.md`, fila de design, item 11);
- o texto da Gamers Nexus conferido só por extração;
- a classe do destino do cabo flat tem dois rótulos no projeto (`STATUS.md`, item 14).

Faltava neste relatório, segundo o auditor: a nota de a2.9 (a fala pode dizer que a divisão da energia com o slot não está nas fontes lidas; não aplicada, por tempo de fala) e a nota de a7.6 (os nomes dos integrantes batem com a proposta formal). Não verificado nesta passada: nenhuma fonte foi reaberta; o validador (rodado pela sessão principal: passou); a cópia do viewer e o storyboard, que segue em rascunho.

## Estado
Os 32 textos estão **aprovados com ressalvas** no gate de fatos. Faltam o storyboard desses beats e o gate humano do animatic da placa.
