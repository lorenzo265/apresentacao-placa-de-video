# Fact-check independente: segunda leva de 2026-11-09

- Data: 2026-11-09
- Auditor: agente `fact-checker` (Fable), em contexto separado de quem produziu os arquivos.
- Escopo: `harness/qa/revisao-artigo.md` (primeira versão), a análise RISC ou CISC de `vault/03-Roteiro/08`, as seções `10` e `11` do roteiro, `harness/spec/sources/mmu-interrupts-sources.md`, as contas de `harness/spec/sources/standards-sources.md`, a seção 5 de `harness/design/assembly-plan.md` e 17 beats de `harness/story/video-plan.md`. Fora do escopo: o catálogo de fotos e `measurements.csv`, que são do `visual-qa`.
- Resultado: **não aprovado na primeira passada**: 7 achados bloqueavam, 13 pediam ajuste e 9 eram notas. Correções aplicadas no mesmo dia pela sessão principal. **A segunda passada ainda não foi feita.**
- Padrão dos erros: os fatos novos conferem (57 bits, 6 níveis, tamanhos de página, descrições de instrução, contas). Os problemas estavam na revisão do artigo, que "corrigia" quatro afirmações com fonte oficial, e em inferências do grupo escritas como fato.

## Método do auditor
- **Leitura direta** (PDF baixado, páginas vistas como imagem): whitepaper Blackwell v1.1, p. 8 a 11 e 44 a 48; whitepaper P100, p. 27 a 30; Huerta et al., p. 1 a 6 e 9 a 11; apresentação Molex Micro-Fit+.
- **Resumo automático** (sem busca literal): os arquivos do driver aberto, Binary Utilities 13.5, guia CUDA 13.5 e 12.9.1, Blackwell Tuning Guide, catálogo de Xid, README do GSP, comunicado da JEDEC.
- Por isso o auditor pediu busca literal da sessão principal para os achados 4, 10 e 11. Essa busca foi feita com `grep` nos arquivos baixados, e a Fig. 5 do whitepaper foi renderizada e vista. Registro em `mmu-interrupts-sources.md`, "Conferência direta, segunda rodada".

## Achados e resolução
| # | Severidade | Achado | Resolução |
|---|---|---|---|
| 1 | bloqueia | A revisão dizia que "quatro escalonadores por SM" era dado de outras GPUs. A Fig. 5 do whitepaper (p. 10) mostra os quatro blocos, cada um com "Warp Scheduler" e "Register File (16,384 x 32-bit)". A página não tinha sido lida | Item retirado da revisão. Figura vista pela sessão principal. Seções `06` e `07` e os beats a5.4, a5.5 e a5.6 passam a citar a figura como `confirmed` |
| 2 | bloqueia | A revisão dizia que a descrição de divergência do artigo não tinha fonte. Guia CUDA 13.5, 3.2.2.1: "the warp executes each branch path taken, disabling threads that are not on that path" | Item retirado. Trecho conferido por leitura direta. Beat a5.16 passa a `confirmed` |
| 3 | bloqueia | A revisão dizia que "o driver compila o PTX na hora" estava acima da fonte. Guia CUDA C++ 12.9.1, 6.1.1.2, diz exatamente isso | Item retirado. Trecho conferido por leitura direta |
| 4 | bloqueia | A revisão mandava "dizer RISC-V só do AMP". O código do driver trata o núcleo do GSP como RISC-V | Corrigido: o artigo acerta o fato e erra a referência. Conferido com `grep` em `kernel_gsp_tu102.c` (família Turing; `derived` para o GB202) |
| 5 | bloqueia | Seção `08`: `UMEMSETS` não é cópia de memória para memória; a frase do seminário chamava de "instruções de acelerador" operações que ISAs RISC também têm; "matrizes inteiras" era ambíguo e errado | Lista de evidências reduzida a `LDGSTS` e `UTMALDG`. Frase reescrita com `TEX`, `HMMA`/`QMMA` ("um bloco de matriz por warp") e a cópia assíncrona. Beat a5.12 atualizado, com o selo "análise do grupo" na tela |
| 6 | bloqueia | "Os SMs não têm interrupção no sentido de uma CPU" não está em fonte nenhuma | Seção `11` e beat a6.4: passou a `inferred`, com linguagem de probabilidade e selo "provável" |
| 7 | bloqueia | O veredito da revisão ("dois erros", "seis afirmações", "apresentar as correções como avanço") dependia dos achados 1 a 4 | Revisão reescrita (segunda versão). Sobram um dado desatualizado, uma generalização e cinco afirmações sem fonte ou com a fonte errada |
| 8 | ajusta | Gravidade do item RISC ou CISC: a tabela do artigo diz "LDG, STG, LDC e parecidas", e a NVIDIA lista a `LDGSTS` entre as instruções de carga e armazenamento. O operando de constante não aparece em `sm_120` | Rebaixado de "erro" para "generalização a partir de um exemplo". Operando de constante marcado `derived` |
| 9 | ajusta | Os três tamanhos de página do artigo não são erro; "a Blackwell foi além" está errado: o formato de 57 bits é o da Hopper, e a Ampere ainda tem 49 | Item limitado aos 49 bits. Texto: "a família GB20x usa o formato da Hopper" |
| 10 | ajusta | Procedência da MMU inconsistente entre arquivos. O GB202 está listado na família GB20x em `ctrl2080mc.h` | Conferido com `grep`. `confirmed` com o escopo "segundo o driver oficial" nos três lugares, citando a exceção GB20B |
| 11 | ajusta | A lista de tamanhos de página dada como "não localizada" existe: `page_sizes_ampere`, herdada pela Hopper | Conferido com `grep`. Lacuna fechada |
| 12 | ajusta | A conta "1 + 9 + 9 + 9 + 8 mais 21" só vale para página de 2 MB | Seção `10` traz a conta para os quatro tamanhos. Beat a6.1: "seis índices mais o deslocamento" |
| 13 | ajusta | Falhas de página: só CE e PBDMA fazem "fault and switch"; as de outros motores são fatais; faltava que a falha reproduzível segura a preempção do canal | Seção `11` e beat a6.2 reescritos. Trechos conferidos com `grep` |
| 14 | ajusta | "Por MSI ou MSI-X" e "como em qualquer driver": o driver recua para a linha legada, e a generalização não tem fonte | Corrigido para "MSI-X, MSI ou linha legada, conforme o driver consegue habilitar". Generalização retirada |
| 15 | ajusta | "Espaço de endereços virtual por programa" não está na fonte citada | Virou pendência na seção `10` |
| 16 | ajusta | A revisão não tratava quatro afirmações do artigo sem fonte | Incluídas na segunda versão (linha F10 e seção 7) |
| 17 | ajusta | A comparação de corrente por pino usava o par mais folgado e três suposições sem fonte | `assembly-plan.md`: as duas folgas (14% e 3,6%) e as três suposições declaradas |
| 18 | ajusta | "A norma tabela 55 A": o que foi lido é o guia Intel, não a norma | Texto corrigido. Continua não reaberto pela auditoria |
| 19 | ajusta | Beat a1.4, "ou 50 A em 12 V": conta sem selo | "cerca de 50 A se tudo viesse em 12 V (conta nossa)" |
| 20 | ajusta | O comunicado da JEDEC cita o modo de 2 canais, mas não o liga a dois chips por controlador | `assembly-plan.md`: a ligação passou a "leitura nossa" |
| 21 | ajusta | Categorias erradas de `UBLKCP`, `DECOMPRESS` e `SPARSIFY`; contagem de 258, não 257 | `isa-sources.md` corrigido. O script da sessão principal, corrigido, também deu 258 |
| 22 | ajusta | Texto antigo na seção `08` e na tabela de cobertura ("255 a confirmar") | Atualizados |
| 23 | ajusta | Beats a5.2 e a5.16 sem classe | `confirmed`, com a ressalva do guia |
| 24 | ajusta | Beats a1.1, a2.1, a2.2, a2.12 e a3.1 com selo acima da base: identificação por foto | Rebaixados para `derived` no que depende só da imagem, até o `visual-qa`. Nota equivalente em `assembly-plan.md` |
| 25 | nota | Os 960 GB/s da RTX 6000 Ada no artigo são o valor da Tab. 4 | Rebaixado para observação |
| 26 | nota | 63 GB/s do PCIe é teto por direção | Beat a3.6: "no máximo", "por direção" |
| 27 | nota | A diferença de altura supõe a mesma referência de medida | Suposições declaradas |
| 28 | nota | "Feita para CPUs dos anos 1980" sem fonte | Frase retirada |
| 29 | nota | Seção 10 do arquivo de fontes e P100: tudo o que foi reaberto confere | Nenhuma |

## O que o auditor não conseguiu verificar
- Guia Intel ATX12VO 2.11 (erro de rede): a tabela dos 55 A, os pinos de sense e os picos.
- Cópia da norma CEM 3.0: 34,80 mm, 20,32 mm e 111,15 mm.
- Documento "Pascal MMU Format Changes".
- PTX ISA 9.5, 9.7.21.4 (`trap`): conferido só pela sessão principal.
- Whitepaper: Tab. 1 e p. 12 e 25.
- Figura 4 do artigo: é imagem. A linha "saída idêntica" se apoia na comparação feita pela sessão principal.
- Concorrentes e datas da seção 3 do artigo; Lindholm; Hennessy e Patterson; Stallings.
- Comunicados da VESA e da PCI-SIG, tabela da Micron, Wikipedia.

## Estado após as correções
Os 29 achados têm resolução aplicada. Nada desta leva está **aprovado**: falta a segunda passada do `fact-checker`, a passada do `visual-qa` sobre as fotos e a aprovação humana da conclusão RISC ou CISC.
