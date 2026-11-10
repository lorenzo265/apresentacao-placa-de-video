# Fact-check independente: gate de fatos da F6 (conteúdo de tela dos atos 4 a 6)

- Data: 2026-11-10
- Auditor: agente `fact-checker` (Fable), em contexto separado de quem produziu.
- Escopo: `harness/content/pt-BR/beats.json` (25 beats), os 8 diagramas de `harness/diagrams/` (JSON, scripts e prévias) e `harness/spec/card.spec.json` (os fatos citados em `claims` e uma amostra do resto).
- Resultado: **não aprovado na primeira passada**: 3 achados bloqueavam, 16 pediam ajuste e 5 eram notas. **A segunda passada ainda não foi feita.**
- Padrão dos erros: **todos os números conferem** com o spec e com a fonte. Os problemas eram de desenho (campos de bits que não somam 128, códigos Xid na coluna errada), de texto que divergia do trecho auditado, e de atribuição: duas coisas declaradas "nossas" têm fonte oficial (o arranjo do chip e a troca de warp sem custo).

## Método do auditor
- Leitura direta, local: `spec/sources/*.md`, os exemplos compilados (linha a linha contra `chip.isa`), as notas `08` e `11` do roteiro.
- Busca literal nas cópias baixadas: texto e páginas do whitepaper (p. 8, 9 e Fig. 5), Blackwell Tuning Guide, PTX ISA, catálogo de Xid, guia CUDA 13.5 (capítulo 3.2.2).
- Web reaberta em um ponto só (arquivos de falhas do driver), por resumo automático. A sessão principal confirmou depois com busca literal: registro em `spec/sources/mmu-interrupts-sources.md`, "Conferência direta, terceira rodada".
- Todas as contas foram refeitas à mão.

## O que passou sem erro
- **Beats:** a4.1, a4.2, a4.3, a4.4, a4.5, a5.1, a5.4, a5.7, a5.8, a5.10, a5.11, a5.12, a5.13, a5.15, a6.1, a6.5.
- **Diagramas:** `chip.warp`, `chip.sm` (fiel à Fig. 5), `chip.risc` (reflete a seção 08 aprovada, sem as evidências derrubadas na auditoria anterior), `chip.memhier`.
- **`chip.isa`:** as 12 correspondências de PTX para SASS e as duas palavras hexadecimais da `FFMA` conferem com os arquivos do exemplo.
- **`sys.mmu`:** campos, níveis, paradas de 512 MB e 2 MB e as quatro contas conferem.
- **Spec:** todos os fatos citados em `claims` conferem em valor, classe e fonte.
- **Contas dos textos, todas certas:** 92,2 bilhões ÷ 750 = 122,9 milhões por mm²; 65.536 ÷ 1.536 = 42,67; 255 × 32 = 8.160; 10 × 32 × 48 = 15.360; 876,7 ÷ 358 = 2,45; 131.072 ÷ 98.304 = 1,333; 16 × 8 × 16 = 2.048; 16 × 8 × 32 = 4.096.

## Achados e resolução
| # | Severidade | Onde | Achado | Resolução prevista |
|---|---|---|---|---|
| 1 | bloqueia | a5.9, fala | Dizia que `LDC` e `LDCU` não têm par no PTX, contra o diagrama do mesmo beat. Só duas cargas não têm par | fala reescrita |
| 2 | bloqueia | `chip.isa`, campos da palavra | Cinco caixas lado a lado sob "128 bits" somavam 142 ou mais: opcode e predicado ficam dentro dos 91 bits de instrução | redesenhado em duas linhas |
| 3 | bloqueia | `sys.irq`, Xid 13 e 31 | Desenhados sob `trap`. Nenhuma fonte liga `trap` aos Xid, e o Xid 31 é falha da MMU | Xid 31 foi para o mecanismo 3; Xid 13 para uma faixa "como o erro aparece no log" |
| 4 | ajusta | a6.2; `sys.irq` | "O canal fica parado" não é o que a fonte diz. O literal: a falha impede a preempção do canal, e os **outros** canais ficam parados ("fault and stall") | texto e nó corrigidos; fato `fault.stall` criado |
| 5 | ajusta | `sys.irq`, buffer, lote, repetição | `confirmed` com um fato que não cobria os três | fatos `fault.buffer_batch` e `fault.replay` criados, com trecho por busca literal |
| 6 | ajusta | a6.2, fala | Faltava a ponte com a CPU; "canal" definido sem fonte | fala reescrita, com "no nosso entendimento" |
| 7 | ajusta | a6.4, legenda | Preempção sem a ressalva da Pascal | acrescentada |
| 8 | ajusta | t1.1; `chip.floorplan` | "A posição é escolha nossa" não procede: o arranjo é o da Fig. 3 do whitepaper (diagrama de blocos oficial). Era redesenho sem crédito | texto, título, aviso e fonte corrigidos; fato `chip.block_diagram` criado |
| 9 | ajusta | `chip.floorplan`, contadores | "Habilitados" e "apagadas" afirmam um mecanismo que o whitepaper não dá | rótulos trocados para "nesta placa" e "a menos que o chip completo" |
| 10 | ajusta | a5.6, fala | "Leitura nossa" para a troca de warp sem salvar registradores: é texto do guia CUDA | fala e fonte corrigidas; fato `sched.warp_switch_no_cost` criado |
| 11 | ajusta | a5.5, fala | Dizia que a NVIDIA não publica como o escalonador escolhe: o guia diz que escolhe um warp com threads prontas | fala corrigida |
| 12 | ajusta | a5.2, fala | "O hardware as emite juntas"; a latência escondida é leitura do grupo | fala corrigida, com "na nossa leitura" |
| 13 | ajusta | a5.1, a5.2, a5.16; spec | SIMT e divergência sem fato no spec | fatos `simt.per_thread_state`, `simt.divergence`, `sched.warp_scheduler` criados e citados |
| 14 | ajusta | a5.16, fala | A ressalva citada vinha de outra página, lida por resumo | substituída pelo trecho de 3.2.2.1.1 |
| 15 | ajusta | t2.1 | "É um processador completo" é contestável | legenda e fonte reescritas |
| 16 | ajusta | `sys.mmu` | "Geração anterior" para a Pascal (2016); destino "GDDR7" sem fonte | rótulos corrigidos |
| 17 | ajusta | a5.5 | O item pipeline do enunciado só tinha uma frase falada | lacuna dita na legenda |
| 18 | ajusta | `Requisitos da disciplina.md` | Quatro linhas da tabela de cobertura desatualizadas | atualizadas |
| 19 | ajusta | `sys.irq`, fluxo da interrupção | Fluxo `inferred` desenhado igual aos outros | passou a `derived`, com a lacuna reescrita |
| 20 | nota | `chip.isa` | Faltavam as setas de `mul.wide` e `add` para `IMAD.WIDE` e de `%tid.x` para `S2R` | acrescentadas |
| 21 | nota | spec | Notas hesitantes sobre LD/ST e PAM3; SFU sem fato | notas corrigidas; fato `sm.block_sfu` criado |
| 22 | nota | a4.3 | "Se contradiz" é forte | "não batem" |
| 23 | nota | vários | "Cerca de 42" é piso; "contador de instrução"; fonte de a5.4 sem a p. 11 | corrigidos |
| 24 | nota | viewer | Notas e procedência de nó não aparecem na tela | aceito por ora; fica para a etapa de design |

**Estado das resoluções em 2026-11-10:** aplicadas as de fatos e fontes (os fatos novos dos achados 4, 5, 8, 10, 13 e 21 já estão no spec, com o trecho literal registrado). **Pendentes** as de texto (`beats.json`) e as de diagrama: entram depois que o `storyboard-director` entregar, para o material não mudar durante o trabalho dele.

## O que o auditor não conseguiu verificar
- Jia et al. e Jarmusch et al. não foram reabertos: fica em aberto se opcode e predicado estão dentro dos 91 bits, e se a latência de "memória global" corresponde ao degrau da GDDR7.
- "Hardware execution may differ" (guia CUDA, 1.2.2.2): a página não estava na cópia local.
- Datasheet, documento da Pascal, whitepaper do P100 e a contagem de 258 mnemônicos.
- A saída do `ptxas -v` ("Used 10 registers"): não há log salvo no repositório (a sessão principal reproduziu em 2026-11-09).
- Se o viewer mostra de fato o aviso do diagrama e os selos: as prévias não os renderizam (a sessão principal viu que sim nas capturas do viewer).

## Estado
Nada aprovado. O gate pede as correções aplicadas, uma segunda passada do `fact-checker` e, depois, a aprovação humana do animatic.
