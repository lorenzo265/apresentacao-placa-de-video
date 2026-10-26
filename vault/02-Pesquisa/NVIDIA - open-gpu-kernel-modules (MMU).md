---
tipo: fonte
status: rascunho
secao: Memória virtual e MMU
autor: NVIDIA
link: https://github.com/NVIDIA/open-gpu-kernel-modules
acessado: 2026-10-26
procedencia: confirmed
---
# NVIDIA - open-gpu-kernel-modules (MMU)

## Dados da fonte
- **Título:** NVIDIA Linux Open GPU Kernel Module Source, versão 615.78.08 (commit `ca2d03e6fafd4d4b56b383497d931c25b283bfcf`).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-26.
- **Alcance da leitura:** clone raso e parcial. Só entraram a pasta da MMU do driver (RM), a de interrupções, a do GSP, os cabeçalhos de registradores da Blackwell e o módulo `nvidia-uvm`. Li o código direto (busca e leitura de arquivos), sem resumo automático.
- **Natureza da fonte:** é código de driver. Não é especificação de hardware nem texto da NVIDIA sobre a GB202. Quando o texto abaixo fala da GB202, é porque o código a liga à família GB20x.
- **Auditoria:** ainda não passou pelo `fact-checker`.

## Pontos que servem à apresentação
- **A GPU tem MMU própria (a GMMU) e o driver a modela como tal.** As tabelas de página ficam em memória (por padrão, na memória de vídeo), com VA de 57 bits e 6 níveis. Cada entrada tem 8 bytes; no nível dos 2 MB a entrada é "dual" (16 bytes, uma metade para páginas de 64 KB e outra para 4 KB). Páginas de 4 KB, 64 KB, 2 MB e 512 MB. A página de **256 GB só existe na subfamília GB10x**; para a família da GB202 o código do UVM diz que a MMU "se comporta como a da Hopper" (`derived` para a GB202). Serve a [[10 - Memória virtual e MMU]].
- **A entrada de página guarda validade, onde a página está e as permissões.** Os bits de onde a página está (aperture) distinguem memória de vídeo local, memória do sistema coerente, memória do sistema não coerente e memória de outra GPU (peer). Um campo de 5 bits (PCF) escolhe privilégio, somente leitura, atômicos, cacheável e contadores de acesso. Uma entrada "esparsa" não gera falha.
- **O TLB é invalidado de duas formas e existe cache do caminho das tabelas.** O driver do kernel escreve num registrador (por espaço de endereços, com escopo de TLB e nível). O módulo de memória unificada (UVM) manda comandos pelo próprio canal da GPU, inclusive por faixa de VA. O código fala de TLBs pequenos dentro de cada GPC, de um cache de PDB e de um cache de percurso de tabelas. Tamanhos e latências não aparecem.
- **Falhas de página têm dois buffers, de 32 bytes por entrada.** Falha do SM (replayable) pára o canal até o UVM atender e a GPU repetir o acesso ("replay"). Falha do Copy Engine ou do Host (non-replayable) tira o canal do ar e o RM entrega a falha ao UVM. O UVM decide migrar a página, mapeá-la ou cancelar o acesso, e uma falha fatal vira reinício de canal pelo RM.
- **A ligação com a CPU é feita por software.** O UVM move páginas entre CPU e GPU conforme as falhas e os contadores de acesso. ATS e HMM existem no código, mas dependem da plataforma e do kernel. A memória do sistema usa endereços da API de DMA do Linux. Cada canal tem um bloco de instância com o PDB do seu espaço de endereços (um PDB por subcontexto desde a Volta), e a entrada de falha traz o ponteiro dessa instância.

> [!warning] Limites
> Não aparecem no código: tamanho, associatividade e latência dos TLBs; o algoritmo do percorredor de tabelas; o layout do bloco de instância para Hopper e Blackwell; se uma GB202 numa estação x86 usa ATS. O RM da GB202 também não foi visto, só o UVM. A lista completa de lacunas está no arquivo bruto.

## Trecho bruto salvo em
`harness/spec/sources/ogkm-mmu.md`

> [!note]
> Resumo com palavras próprias. Não cole trechos longos de terceiros aqui. Cada afirmação acima tem o arquivo e a linha no trecho bruto, com a marca `confirmed` ou `derived`.
