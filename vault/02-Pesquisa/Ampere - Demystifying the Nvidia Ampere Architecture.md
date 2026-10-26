---
tipo: fonte
status: rascunho
secao: Instruções
autor: Abdelkhalik, Arafa, Santhi, Badawy
link: https://arxiv.org/abs/2208.11174
acessado: 2026-10-19
procedencia: derived
---
# Ampere - Demystifying the Nvidia Ampere Architecture

## Dados da fonte
- **Título:** Demystifying the Nvidia Ampere Architecture through Microbenchmarking and Instruction-level Analysis (arXiv 2208.11174, 2022).
- **Autores:** Hamdy Abdelkhalik, Yehia Arafa, Nandakishore Santhi, Abdel-Hameed Badawy (conferido na ficha do arXiv em 2026-10-26).
- **Link:** no frontmatter.
- **Data de acesso:** 2026-10-19.
- **Alcance da leitura:** versão ar5iv, por resumo automático. Ainda não auditada.

## Por que é `derived`
As medições são de uma **A100** (Ampere), duas gerações antes da Blackwell. Serve para mostrar o método e a continuidade do conjunto de instruções, não para dar números da nossa placa.

## Pontos que servem à apresentação
- O artigo diz que o SASS é **código fechado e compatível apenas dentro de uma família de arquiteturas**, e que o PTX é uma representação intermediária entre o CUDA e o SASS. Isso sustenta a explicação das duas camadas em [[08 - Instruções PTX e SASS, RISC ou CISC]].
- **Método:** os autores escrevem microbenchmarks em PTX, leem o SASS gerado em tempo de execução e ajustam o PTX por tentativa e erro até obter a instrução desejada.
- **Exemplos de mapeamento PTX para SASS na Ampere:** `add.u32` vira `IADD` (ou `IADD3`/`IMAD.IADD` com dependências), `add.f32` vira `FADD`, `mul.lo.u32` vira `IMAD`, `mad.rn.f32` e `fma.rn.f32` viram `FFMA`, e `wmma.mma.sync` (m16n16k16, f16) vira duas instruções `HMMA.16816.F16`.
- **Latências medidas na A100:** 2 ciclos por instrução em operações simples independentes (por exemplo `FADD` e `FFMA`), 4 ciclos em `DADD`/`DFMA`, e 8 ciclos em `HMMA.16816`. Memória: L1 33, L2 200 e global 290 ciclos.
- A instrução `HMMA.16816.F32` já existia na Ampere, o que mostra a **continuidade do mnemônico** até o `sm_120` (ver `harness/examples/mma/`).

> [!warning] Limites
> O artigo não trata da largura da instrução, do banco de registradores nem do número de escalonadores por SM. A latência de 2 ciclos da A100 não deve ser comparada com os 4 ciclos medidos na GB203 sem cuidado: os métodos e as placas diferem.
