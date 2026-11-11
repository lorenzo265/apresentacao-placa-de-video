# Fact-check do roteiro conciso (corte do seminário, commit b4cad83)

- Data: 2026-11-11
- Auditor: agente `fact-checker`, em contexto separado de quem escreveu os textos. O agente não tinha ferramenta de escrita: o relatório foi gravado pela sessão de roteiro a partir do texto dele, sem mudar o conteúdo dos achados.
- Escopo: os 27 beats de prioridade 1 de `harness/story/storyboard.json` com texto novo em `harness/content/pt-BR/beats.json`, mais o beat novo a2.13.
- Regra aplicada (combinada com o autor): o selo carrega a procedência de `confirmed` e `derived`. `inferred` precisa de "provável" na tela ou na fala. Ressalva retirada só é erro se a frase virar falsa ou se um `inferred` parecer fato.
- **Veredito: não aprovado.** 3 bloqueios, 16 beats com ajuste, 9 ok.
- Padrão dos erros: os números batem com o spec. Os problemas vieram do encurtamento: frases que ficaram absolutas, uma causa sem fonte e listas de `claims` que não acompanharam a fusão de beats.

## Método e limites
- Leitura local: `beats.json`, `storyboard.json`, `card.spec.json`, `spec/sources/*.md`, `examples/saxpy-cu/`, `examples/mma/README.md`, diagramas `sys.irq` e `chip.memhier`, seção 08 do roteiro, relatórios `fact-check-f6-*.md`.
- Contas refeitas: 188 x 128 = 24.064. 4 x 16.384 = 65.536. 65.536 x 4 B = 256 KB. 65.536 / (255 x 32) = 8,03. 10 x 32 x 48 = 15.360. 1.792 / 63,015 = 28,4. 20 instruções PTX e 19 SASS até o último EXIT. Todas conferem.
- Não verificado: o texto antigo (`b4cad83^`), por falta de terminal. "Regressão" quer dizer contra a resolução registrada nos relatórios anteriores. Nenhuma fonte externa foi reaberta.

## Bloqueios
| # | Beat | Onde | Problema | Correção sugerida |
|---|---|---|---|---|
| B1 | a5.13 | caption | "Do registrador à GDDR7, cada degrau é maior e mais lento" é falso no primeiro degrau: registradores 256 KB por SM, L1 128 KB | "Do L1 à GDDR7, cada degrau é maior e mais lento." |
| B2 | a5.12 | fala | "Memória só por carga e armazenamento" é absoluto. A seção 08 diz "como regra" e o Binary Utilities 3.1.1 mostra operando do banco de constantes | "como regra" |
| B3 | a3.1 | fala | "Perto do chip, para o sinal aguentar 28 Gbps por pino": causa sem fonte, `inferred` dito como fato | cortar a causa ou marcar como provável |

## Veredito por beat
| Beat | Veredito | Achado | Correção sugerida |
|---|---|---|---|
| a0.1 | ok | | |
| a1.1 | ajuste | "sai pelo topo" lê-se como saída única (lacuna `airflow.direction`). Datasheet na fonte sem fato | aberturas do topo lançam ar para cima, acrescentar `card.airflow_pathways` |
| a2.1 | ajuste | a fonte tira os parafusos da mola, não a mola. Cabos flat sumiram. Faltam claims | listar cabos flat e parafusos da mola, acrescentar `teardown.e2` a `e6` e `card.pcie_adapter_separate` |
| a2.13 | ajuste | sem entrada no storyboard. "Daqui entramos no chip" só vale depois de a3.6 | criar no storyboard ou trocar a frase |
| a3.1 | bloqueia | B3. 28 Gbps vem da Tab. 4 do whitepaper, fora da fonte. Falta `mem.back_layout` | B3, fonte e claim |
| a3.6 | ajuste | "os dados ficam na placa enquanto a GPU calcula" é absoluto e contradiz a6.2. 63 GB/s é por direção | "compensa manter os dados na memória da placa", "por direção" |
| t1.1 | ok | | |
| a4.2 | ajuste | "O SM é o processador de fato" (achado 15 da primeira passada). `chip.tpc_per_gpc` sobra | "O SM é quem executa as instruções" |
| a4.4 | ajuste | "compartilhado pelos 12 GPCs" sem trecho salvo. "Dois níveis" ignora o L0 i-Cache. Falta `chip.block_diagram` | "no centro do diagrama", "cache de dados", headline com controladores |
| t2.1 | ok | | |
| a5.5 | ajuste | caption "não é público" contra a regra E3 | "não achamos nas fontes lidas" |
| a5.1 | ajuste | mistura escalonador do sistema operacional e de hardware | "Na CPU, o sistema operacional escalona threads. Aqui, o hardware escalona warps a cada ciclo" |
| a5.2 | ok | | |
| a5.16 | ajuste | custo só quando divergem. "reconvergem" deveria ser "podem reconvergir" | |
| a5.6 | ok | literal do guia CUDA 3.2.2.2 | |
| a5.7 | ok | | |
| a5.8 | ok | | |
| a5.9 | ok | | |
| a5.10 | ajuste | "controle de escalonamento" mais estreito que a fonte. "só a largura está documentada" é falso | "parte dos bits era de controle", "do formato dos bits, só achamos a largura" |
| a5.12 | bloqueia | B2. Falta "provável" e `isa.ptx_load_store` | B2, "provável", claim |
| a5.13 | bloqueia | B1 | B1 |
| a5.14 | ajuste | "de 0 a 100 KB" sugere faixa contínua | listar 0, 8, 16, 32, 64 ou 100 KB |
| a6.1 | ajuste | faltam `mmu.format_family` e `mmu.gb202_in_gb20x` | |
| a6.2 | ajuste | "o canal espera" é regressão do achado 4. Faltam `irq.xid31` e `irq.top_half` | "o canal não pode ser trocado" |
| a6.3 | ok | | |
| a6.4 | ajuste | o terceiro mecanismo do diagrama é falha de página e preempção. Faltam `fault.*` | caption e claims |
| a7.4 | ajuste | "quase nunca" é negativa geral | "Do funcionamento interno, pouco." |
| a7.5 | ajuste | "Derivado" omite outra geração | "placa irmã, outra geração ou conta nossa" |

## Cobertura do enunciado
Os oito itens têm beat no corte: registradores (a5.6 a a5.8), instruções (a5.9, a5.10), CISC ou RISC (a5.12), MMU (a6.1), interrupções (a6.4), gerenciamento de memória (a3.1, a5.14, a6.2), pipeline (a5.5), cache (a5.13).

## Correções aplicadas (sessão de roteiro, 2026-11-11)
Todas as correções sugeridas foram aplicadas, inclusive B1, B2 e B3 (em a3.1, a causa foi cortada: "Em volta do chip, a 28 Gbps por pino"). O beat a2.13 continua sem entrada no storyboard, porque quem cria é a sessão de câmera. A fala dele virou "Daqui, a memória e depois o chip". Falta a segunda passada estreita.
