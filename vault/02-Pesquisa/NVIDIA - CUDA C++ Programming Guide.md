---
tipo: fonte
status: rascunho
secao: "Registradores; Latência, ocupação e divergência"
autor: NVIDIA
link: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
acessado: 2026-10-26
procedencia: confirmed
---
# NVIDIA - CUDA C++ Programming Guide

## Dados da fonte
- **Título:** CUDA C++ Programming Guide, edição "Legacy", versão 13.4 (o PDF oficial traz a data 12 de outubro de 2026).
- **Autor / publicador:** NVIDIA.
- **Link:** no frontmatter. O PDF da mesma edição está em https://docs.nvidia.com/cuda/pdf/CUDA_C_Programming_Guide.pdf.
- **Data de acesso:** 2026-10-26.
- **Aviso do próprio guia:** esta edição foi substituída por um "novo CUDA Programming Guide" e não é atualizada desde o CUDA 13.0. Só a seção 5.1 do guia novo (tabelas de compute capability) foi consultada, para conferir números.
- **Alcance da leitura:** o HTML cabe no WebFetch só até a seção 6.2.16, então os capítulos 5 a 8, 10 (parcial), 14, 20 e 24 foram lidos no PDF, página a página. Os números da compute capability 12.0 foram lidos na imagem da Tabela 27 e conferidos em uma segunda leitura. Seções sobre texturas, funções de warp, barreiras assíncronas, TMA, Cooperative Groups e Dynamic Parallelism não foram lidas.

## Pontos que servem à apresentação
- **Registradores.** Cada thread pode usar no máximo 255 registradores de 32 bits, e o SM tem 65.536 deles (64 K); um bloco também pode usar no máximo 64 K no total. A conta fecha com o whitepaper: 65.536 × 4 B = 256 KB por SM. Quando faltam registradores, o compilador joga variáveis na memória local, que fica na memória do dispositivo e passa pelo L2, com a latência e a largura de banda da memória global. O guia não informa a granularidade de alocação de registradores. Ver [[07 - Registradores]].
- **Limites do SM na compute capability 12.0 e ocupação.** Por SM cabem no máximo 1.536 threads, 48 warps e 24 blocos; um bloco tem até 1.024 threads e pode usar até 99 KB de memória compartilhada (100 KB por SM, com 1 KB reservado ao sistema). Ocupação é a razão entre warps residentes e o máximo de warps por SM. Os fatores que limitam são registradores, memória compartilhada e os tetos de blocos e de warps. Contas derivadas: com 255 registradores por thread só cabem 8 warps (16,7%); um kernel com 10 registradores por thread bate primeiro no teto de 48 warps, não nos registradores. Ver [[12 - Latência, ocupação e divergência]].
- **SIMT, divergência e pipeline.** O warp tem 32 threads e executa uma instrução por vez; num desvio, o hardware percorre cada caminho com as threads fora dele desligadas. Desde a Volta cada thread tem contador de programa e pilha próprios (independent thread scheduling), então não se pode supor lockstep. O guia descreve o pipeline do SM como em ordem e sem previsão de desvio nem execução especulativa, com 4 escalonadores de warp por SM na cc 12.0. A fórmula de latência do guia (4L instruções para esconder latência L) lista só até a cc 8.x. Ver [[12 - Latência, ocupação e divergência]] e [[05 - Modelo de execução SIMT]].
- **Hierarquia de memória e caches.** Cada thread tem memória local privada, cada bloco tem memória compartilhada (32 bancos), e a global é acessada em transações de 32, 64 ou 128 bytes, o que faz a coalescência valer. Constante e textura têm caches próprios. A partir da cc 8.0 o programador pode reservar parte do L2 para dados "persistentes" (desligado em MIG), e há dicas de cache por instrução (`__ldg`, `__ldcg`, `__stcs` e outras). O guia manda a cc 12.0 seguir o texto da cc 5.x para cache de global, então a política real de L1 e L2 da placa fica em aberto. Ver [[09 - Hierarquia de memória e caches]].
- **Divergências e o que o guia não cobre.** O guia diz que L1 + memória compartilhada somam 100 KB por SM, enquanto o whitepaper diz 128 KB (e o guia novo também): registrado como `conflict: true`, sem resolver. O guia **não trata** de interrupções (só `__trap()`, que "levanta uma interrupção no programa do host") nem da estrutura da MMU da GPU; traz apenas definições genéricas de página, tabela de páginas e TLB, a preferência por páginas de 2 MiB, falhas de página na memória unificada e a API de gerenciamento de memória virtual. Ver [[10 - Memória virtual e MMU]] e [[11 - Escalonamento, CPU e interrupções]].

## Trecho bruto salvo em
`harness/spec/sources/cuda-programming-guide.md`

> [!note]
> Resumo com palavras próprias. Não cole trechos longos de terceiros aqui. As tabelas com trecho curto, seção, página, procedência, contas de verificação, conflitos e lacunas estão no arquivo acima.
