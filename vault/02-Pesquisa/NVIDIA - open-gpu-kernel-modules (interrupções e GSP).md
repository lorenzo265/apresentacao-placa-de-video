---
tipo: fonte
status: rascunho
secao: Escalonamento, CPU e interrupções
autor: NVIDIA
link: https://github.com/NVIDIA/open-gpu-kernel-modules
acessado: 2026-10-26
procedencia: confirmed
---
# NVIDIA - open-gpu-kernel-modules (interrupções e GSP)

## Dados da fonte
- **Título:** NVIDIA Linux Open GPU Kernel Module Source, versão 615.78.08 (commit `ca2d03e6fafd4d4b56b383497d931c25b283bfcf`).
- **Autor / publicador:** NVIDIA. Código aberto, com licença MIT nos arquivos lidos.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-26.
- **Escopo lido:** checkout **parcial**. Só entraram as pastas de interrupções (`intr`), do firmware GSP (`gsp`), da MMU (`mmu`), o módulo `nvidia-uvm` e os cabeçalhos de registradores da Blackwell. O código que registra o IRQ no Linux (MSI/MSI-X) e o código do próprio firmware **não** estão lá.

## Pontos que servem à apresentação
Servem de base para [[11 - Escalonamento, CPU e interrupções]] e, no caso das falhas de página, também para [[10 - Memória virtual e MMU]]. Cada ponto tem os números de linha em `harness/spec/sources/ogkm-interrupts.md`.

1. **A GPU avisa a CPU por uma árvore de interrupções de dois níveis.** Cada fonte (falha de página, display, timer, erro, firmware) tem um número de vetor. Registradores "folha" dizem qual vetor disparou, um registrador "topo" diz qual grupo de folhas tem algo pendente, e há registradores para habilitar, desabilitar e limpar. O código separa a árvore das notificações ("non-stall"), tratada sem o lock principal, da árvore dos demais motores. Os endereços vêm do cabeçalho do GB100 (outro chip Blackwell); para o GB202 é extrapolação, marcada como `derived` no arquivo bruto.
2. **O tratamento é em dois tempos.** O tratador curto (top half) só confirma e agenda; o trabalho pesado vai para um bottom half (fila de DPC no RM, fila de kthread no UVM). O UVM desliga a interrupção enquanto trata, para não haver "tempestade", e depois a rearma. A falha de página é o evento mais bem documentado: dois buffers circulares em hardware (replayable e non-replayable) com ponteiros GET e PUT, e 16 tipos de falha no GB202.
3. **O firmware GSP é um processador RISC-V que executa o gerenciador de recursos (RM) no lugar da CPU.** A CPU e a GSP trocam mensagens (RPC) por duas filas de 256 KB em memória do sistema. Uma resposta síncrona é esperada por polling, sem interrupção. A GSP avisa a CPU por um bit de interrupção por software (SWGEN0), e a CPU "cutuca" a GSP escrevendo num registrador de campainha. Parte do tratamento de erro de canal roda na GSP e parte na CPU.
4. **A CPU manda trabalho por canal, com fila circular e campainha.** O driver monta o pushbuffer, grava uma entrada de GPFIFO, atualiza o ponteiro `GPPut` e escreve um "token de submissão" no registrador de campainha do canal (endereço 0x30090 no GB202, com campos de vetor e de número do runlist). O escalonador de hardware aparece no código com o nome ESCHED, com runlists, TSG e preempção.
5. **O que o código não diz.** Ele **não menciona o AMP** do whitepaper, então não dá para dizer se o AMP é a GSP, o ESCHED ou outro bloco; fica como lacuna. Também não aparecem o registro de MSI/MSI-X (só uma tabela MSI-X de 12 entradas no mapa do GB100), a interrupção do copy engine, nem como a GSP percebe um comando novo na fila.

> [!warning] Limites desta fonte
> O clone é parcial. A tabela que diz quais funções o GB202 realmente usa (HAL) é gerada e não está nele. Por isso vários itens vêm de código de Turing, Hopper, Ampere ou do GB100 e estão marcados como `derived` no arquivo bruto. Nada foi revisado pelo `fact-checker` ainda.

> [!note] Divergências registradas
> O layout do registrador de campainha de usuário difere entre o GB100 e o GB202 (vale o do GB202). O cabeçalho do GB100 também se contradiz sobre o número de subárvores. Um comentário de heartbeat da GSP não bate com a conta do código. Detalhes na seção 7 do arquivo bruto. Quanto ao AMP, o whitepaper está em [[NVIDIA - Whitepaper RTX PRO Blackwell v1.1]].

## Trecho bruto salvo em
`harness/spec/sources/ogkm-interrupts.md`

> [!note]
> Resumo com palavras próprias. Não cole trechos longos de terceiros aqui.
