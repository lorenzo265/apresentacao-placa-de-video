# Revisão do artigo entregue em 2026-11-09 (segunda versão)

- Documento: "Estudo da arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell (chip GB202)", 13 páginas, grupo Warp 32. Entregue como documentação escrita (1,5 ponto).
- Revisor: sessão principal (Fable). Quem escreveu o artigo foi outro integrante, fora deste repositório.
- **Esta versão substitui a primeira, do mesmo dia.** A auditoria independente (`fact-check-segunda-leva.md`) mostrou que a primeira versão acusava o artigo de quatro erros que não eram erros. A seção 6 lista o que foi retirado.
- Método: cada afirmação comparada com as fontes de `harness/spec/sources/`. "Leitura direta" quer dizer que o revisor abriu o documento, a figura ou o código-fonte baixado. O experimento da seção 4.4 foi refeito: `harness/examples/saxpy-cu/`.

## 1. Veredito

O artigo é melhor do que a primeira versão desta revisão dizia. Cumpre a proposta entregue em 26/10, trata os nove itens, tem um experimento real e reproduzível, e quase todas as afirmações técnicas têm fonte oficial.

O que sobra de problema:

1. **Um dado desatualizado em item que o professor cobra:** os 49 bits de endereço virtual são da Pascal; o driver atual usa 57 bits para a família desta placa.
2. **Uma generalização na análise RISC ou CISC:** a tabela conclui "só carga e armazenamento acessam a memória" a partir de um único exemplo.
3. **Cinco afirmações sem fonte ou com a fonte errada** (seção 3).
4. **Profundidade:** cache e pipeline só com tamanhos; nenhuma separação entre o que é desta placa e o que vem de outra geração.

Recomendação para o seminário: apresentar **só o item 1 como atualização** ("fomos ao código do driver e o formato mudou"), e a análise RISC ou CISC como **aprofundamento**, não como correção. O resto se resolve na fala, sem mencionar o artigo.

## 2. O que confere

| Afirmação do artigo | Fonte | Como foi conferido |
|---|---|---|
| Listagem SASS da Figura 4, 10 registradores, 0 de spill, 16 bytes por instrução | `nvcc` e `cuobjdump` 13.5.37 | refeito: saída idêntica (comparação do revisor contra a imagem do PDF; o auditor não viu a figura) |
| 65.536 registradores de 32 bits por SM; até 255 por thread; até 48 warps por SM | Blackwell Tuning Guide 13.5, 1.4.1.1 | leitura direta. O artigo cita a versão 13.4.1; a conferência foi na 13.5 |
| **Quatro escalonadores de warp por SM** | whitepaper, Fig. 5, p. 10: quatro blocos, cada um com "L0 i-Cache + Warp Scheduler + Dispatch (32 thread/clk)" e "Register File (16,384 x 32-bit)" | leitura direta da figura |
| **Divergência: o warp executa um caminho e depois o outro** | guia CUDA 13.5, 3.2.2.1: "the warp executes each branch path taken, disabling threads that are not on that path" | leitura direta |
| **O driver compila o PTX na hora em GPU mais nova** | guia CUDA C++ 12.9.1, 6.1.1.2: "Any PTX code loaded by an application at runtime is compiled further to binary code by the device driver. This is called just-in-time compilation." | leitura direta. Não achamos o trecho equivalente no guia 13.5 |
| **O GSP é um processador RISC-V** | código do driver, `kernel_gsp_tu102.c`: "prepares RISCV core to run GSP-RM", "RISC-V core is not enabled." | leitura direta. O arquivo é da família Turing; para o GB202 é `derived`. **A referência do artigo está errada** (ver F2) |
| `trap` para a execução e gera interrupção para a CPU | PTX ISA 9.5, 9.7.21.4 | leitura direta |
| Xid 31 em endereço inválido; Xid 13 em acesso fora do vetor | catálogo de Xid | leitura direta |
| 126 TFLOPS; MIG com 4 instâncias de 24 GB; "4 nm"; linha da RTX 6000 Ada na Tabela 1 | whitepaper, Tab. 4, p. 44 a 48 | leitura direta do auditor |
| Pascal: 49 bits, falhas de página, memória unificada, preempção no nível de instrução; páginas de 4 KB, 64 KB e 2 MB | whitepaper do P100, p. 27 e 30; "Pascal MMU Format Changes" | P100 por leitura direta do auditor; o documento da Pascal por outro agente |
| Páginas de 4 KB, 64 KB e 2 MB | continuam valendo na geração atual (`page_sizes_ampere`, herdada) | leitura direta |
| Núcleos unificados para inteiro e ponto flutuante | whitepaper, p. 11 e Fig. 5 ("FP32 / INT32") | leitura direta. Ver F5 para a ressalva |
| Bits de controle gravados pelo compilador | Huerta et al., seção 4 | leitura direta do auditor |
| AMP é RISC-V e escalona contextos | whitepaper, p. 25 | já auditado |

## 3. O que não confere ou não tem fonte

| # | Tipo | Onde | O que o artigo diz | O que a fonte diz | No seminário |
|---|---|---|---|---|---|
| F1 | **desatualizado** | 4.8 MMU | "Desde a arquitetura Pascal, a GPU usa endereços virtuais de 49 bits" | O driver oficial lista o GB202 na família GB20x (`ctrl2080mc.h`) e diz "GB20x MMU behaves as Hopper MMU" (`uvm_hal.c`). O formato da Hopper tem **57 bits** e **6 níveis** (`uvm_hopper_mmu.c`). A Ampere ainda tinha 49 bits. Leitura direta | Mostrar a tabela de 6 níveis: "o formato mudou na Hopper, e a família desta placa usa o novo" |
| F2 | referência errada | 4.9 | GSP é RISC-V "(NVIDIA, 2026d)" | O fato confere, mas o README citado não contém a palavra RISC. A fonte é o código do driver | Citar o código |
| F3 | sem fonte | 4.1 | 188 de 192 SMs porque "as partes com problema são desligadas" | O whitepaper não dá motivo. A p. 8 diz "The RTX PRO 6000 GPUs use the full GB202 GPU" e as tabelas dão 188 | "A NVIDIA não explica, e o documento se contradiz" |
| F4 | não confere com o exemplo | 4.2 | "encontramos ... um registrador que sempre vale zero (RZ)" | `RZ` não aparece na listagem da Figura 4 nem na reprodução | Não citar `RZ`, ou mostrar outro código |
| F5 | simplificação | 4.6 | os 128 núcleos fazem inteiro ou ponto flutuante | p. 11: "only operate as either FP32 or INT32 ... in any given clock cycle"; nem toda operação inteira dobra | Acrescentar "um tipo por ciclo" |
| F6 | generalização | 4.5, Tabela 4 | "Acesso à memória: só LDG, STG, LDC e parecidas"; conclusão "RISC" | Vale para o exemplo. No conjunto inteiro há `LDGSTS`, "Asynchronous Global to Shared Memcopy", que a própria NVIDIA lista entre as instruções de carga e armazenamento, e instruções de textura e de matriz. É uma tabela montada sobre um exemplo de 20 instruções | Aprofundar com a lista oficial de 258 mnemônicos. Ver `vault/03-Roteiro/08` |
| F7 | derivado sem aviso | 4.6 | pesquisadores "fazem testes na placa" | Huerta et al. mediram Ampere e uma Turing, nenhuma Blackwell | Dizer em que GPUs foi medido |
| F8 | impreciso | 4.3 | o PTX "é igual para todas as gerações" | É estável e versionado (9.5) | "Estável entre gerações" |
| F9 | contradição interna | 4.2 e 4.9 | 4.2: os registradores não são salvos na troca. 4.9: a preempção salva o estado | Valem em níveis diferentes: entre warps nada é salvo; entre programas o contexto vai para a memória (P100, p. 30) | Separar os dois níveis |
| F10 | sem fonte | 4.8, 4.9, 4.10 | cada programa tem "o seu próprio espaço de endereços"; os SMs "não funcionam assim" quanto a interrupções; interrupção "quando termina um trabalho"; blocos "distribuídos entre os SMs que têm espaço livre" | Nenhuma das fontes abertas diz isso com essas palavras. São leituras razoáveis, mas são do grupo | Tratar como análise do grupo, com linguagem de probabilidade |
| F11 | termo | Tabela 2 | "Frequência máxima" | A Tab. 4 chama de "GPU Boost Clock" | Usar o nome da fonte |

Observações menores: a Tabela 1 usa 960 GB/s para a RTX 6000 Ada, que é o valor da Tab. 4 do whitepaper (a Tab. 1 do mesmo documento dá 1.008); na memória unificada o P100 descreve migração **ou** mapeamento pelo barramento; os superlativos e os dados de concorrentes vêm de fontes secundárias que não conferimos.

## 4. O que o seminário acrescenta

| Item | No artigo | No seminário |
|---|---|---|
| MMU | 49 bits (Pascal) | 57 bits, 6 níveis, 4 KB a 512 MB, pelo driver oficial |
| Interrupções | "manda uma interrupção pelo PCIe" | o caminho no driver: MSI-X, MSI ou linha legada; duas metades; falha de página gravada em buffer, com o canal parado até o driver resolver |
| Mecanismo de cache | só tamanhos | latências medidas na RTX 5080 (`derived`); L1 e memória compartilhada no mesmo bloco de 128 KB |
| Pipeline | "não divulgado" | os quatro blocos da Fig. 5 (`confirmed`); 4 ciclos em INT32 e FP32 (`derived`) |
| Registradores | 65.536 por SM | 4 bancos de 16.384 (Fig. 5); 4 × 16.384 = 65.536 |
| Conjunto de instruções | o exemplo | 258 mnemônicos em 13 categorias; instruções de Tensor Core compiladas (`harness/examples/mma/`) |
| Código aberto do driver | não citado (a proposta entregue lista entre o que seria usado) | base de MMU e interrupções |
| O que é desta placa e o que é de outra geração | não separado | selo de procedência em todo beat |

## 5. Observações de forma

- A proposta entregue e o artigo têm cinco integrantes; a nota do enunciado no vault diz até quatro.
- A seção 4.11 atribui o tour 3D ao integrante que a proposta indica como responsável por ele.
- Referências ausentes para conteúdo usado: CUDA Binary Utilities (lista de instruções SASS) e o código do driver (GSP).

## 6. Erros da primeira versão desta revisão

Registrado para não repetir. A primeira versão marcava como erro ou "acima da fonte" quatro afirmações do artigo que têm fonte oficial. A causa foi a mesma nas quatro: a coleta não tinha aberto a página certa, e a revisão tratou "não achei" como "não existe".

| Item retirado | O que a primeira versão dizia | O que a fonte diz |
|---|---|---|
| Quatro escalonadores (antigo E7) | "derivado de outras GPUs; o whitepaper não escreve quatro" | Fig. 5, p. 10, mostra os quatro. A página não tinha sido lida |
| Divergência (antigo E8, primeira metade) | "a frase não aparece no guia" | guia CUDA 13.5, 3.2.2.1. Só a seção 1.2.2.2 tinha sido aberta |
| JIT pelo driver (antigo E9, primeira metade) | "acima da fonte" | guia CUDA C++ 12.9.1, 6.1.1.2 |
| GSP RISC-V (antigo E4) | "RISC-V só está documentado para o AMP" | o código do driver trata o núcleo do GSP como RISC-V. Só a referência do artigo está errada |

Também foram rebaixados: a acusação sobre os tamanhos de página (os três tamanhos do artigo continuam valendo) e a gravidade do item RISC ou CISC (de "erro" para "generalização").

## 7. O que não foi verificado

- Dados de concorrentes da Tabela 1 e da seção 3, e as datas das gerações.
- Lindholm et al. (2008), Hennessy e Patterson (2019) e Stallings (2017): não abertos.
- O documento "Pascal MMU Format Changes": lido por outro agente, não reaberto.
- Jarmusch et al. além do resumo: o artigo diz que a unificação "ajuda principalmente programas que misturam os dois tipos de conta", e o resumo não diz isso.
- Tabela 4 do artigo, "modos de endereçamento: poucos": apoiada em um exemplo.
