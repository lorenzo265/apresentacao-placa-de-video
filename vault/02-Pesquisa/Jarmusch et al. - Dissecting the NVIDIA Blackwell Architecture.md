---
tipo: fonte
status: pronto
secao: Pipeline e caches
autor: Jarmusch, Graddon, Chandrasekaran
link: https://arxiv.org/abs/2507.10789
acessado: 2026-10-19
procedencia: derived
---
# Jarmusch et al. - Dissecting the NVIDIA Blackwell Architecture

## Dados da fonte
- **Título:** Dissecting the NVIDIA Blackwell Architecture with Microbenchmarks (arXiv 2507.10789, 2025).
- **Autores:** Jarmusch, Graddon, Chandrasekaran (Universidade de Delaware).
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-19.
- **Alcance da leitura:** versão HTML, por resumo automático.

## Por que é `derived`
As medições são da **GeForce RTX 5080 (chip GB203)**, comparada com a H100 PCIe. Não são da GB202 da nossa placa. As duas são Blackwell de consumo (arquitetura `sm_120a` segundo o artigo), mas número de SMs, L2 e memória diferem. Os valores abaixo são evidência de **família**, não da nossa placa.

## Pontos que servem à apresentação
- Cada SM tem **quatro partições de unidades de execução** (sub-cores). Na GB203 as unidades INT32 e FP32 são unificadas.
- A latência medida de uma instrução INT32 ou FP32 é de **4 ciclos** (Tab. III). O FP64 é exceção: cerca de 63,6 ciclos na GB203.
- Latências de memória na GB203: L1 entre 30 e 40 ciclos, acerto no L2 por volta de 358 ciclos e acesso à memória global por volta de 876,7 ciclos (seção VI). Serve a [[09 - Hierarquia de memória e caches]].
- Tamanhos que batem com o whitepaper da GB202: 256 KB de registradores por SM e 128 KB de L1 por SM (Tab. II).
- Instruções de matriz: o PTX `mma.sync` vira HMMA na Hopper. Na Blackwell (GB203) vira QMMA para FP8 e FP6, e também para FP4 sem escala (alternativa usada pelo software da época). OMMA só foi observado no teste com escala por bloco `ue8m0`, e o artigo não especifica o tipo das entradas desse teste (seção V-B). A legenda da Tab. V diz que `e8m0` não foi testado, o que contradiz o texto. Serve a [[08 - Instruções PTX e SASS, RISC ou CISC]].

> [!warning] Limitações declaradas pelos autores
> O código não foi publicado na época do artigo, alguns resultados da GB203 não foram explicados e o suporte a instruções novas (FP4, FP6, `tcgen05`) ainda era limitado em `sm_120a`. O artigo não trata de codificação de instruções nem de organização do banco de registradores.
