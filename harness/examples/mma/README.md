# Exemplo: instruções de matriz em PTX e SASS (`sm_120`)

Dois kernels mínimos que fazem **uma** multiplicação-acumulação de matrizes por warp, compilados para o alvo da RTX PRO 6000 Blackwell (compute capability 12.0). Mesmos comandos e versões de `harness/examples/saxpy/README.md` (`ptxas` 12.9.86, `nvdisasm` 13.4.92).

```bash
$V/cuda_nvcc/bin/ptxas -v -arch=sm_120 mma.ptx -o mma.cubin
$V/cu13/bin/nvdisasm -c -hex mma.cubin > mma.sm_120.sass
```
Os comentários do PTX precisam ser ASCII: o `ptxas` recusa acentos.

## O que a saída mostra
| PTX | SASS | Tamanho da tile (M×N×K) | Multiplicações-acumulações por instrução |
|---|---|---|---|
| `mma.sync.aligned.m16n8k16.row.col.f32.f16.f16.f32` | `HMMA.16816.F32` | 16 × 8 × 16 | 2.048 |
| `mma.sync.aligned.m16n8k32.row.col.f32.e4m3.e4m3.f32` | `QMMA.16832.F32.E4M3.E4M3` | 16 × 8 × 32 | 4.096 |

- **Uma instrução SASS por `mma`.** Cada `mma.sync` do PTX virou uma única instrução SASS, que o warp inteiro executa em conjunto sobre os Tensor Cores. O número de multiplicações-acumulações é o produto M × N × K da tile (conta nossa).
- **O mnemônico carrega a forma.** `16816` e `16832` repetem M, N e K, e o sufixo `E4M3.E4M3` diz o formato dos operandos. Isto é leitura do texto desmontado, não um campo documentado.
- **Sufixo `.reuse`.** As instruções `MOV` mostram `R4.reuse`. O artigo da Volta descreve um cache de reuso de registradores controlado por marcas desse tipo; aqui vemos a marca na saída de `sm_120`, mas não sabemos se o mecanismo é o mesmo.
- **O resto é igual ao SAXPY:** `LDC`/`LDCU` para o parâmetro, `S2R` para o id da thread, `STG` para gravar, `EXIT` no fim. Ambos os kernels usam 10 registradores por thread.

## Limites
Os dados de entrada são fictícios (o id da thread repetido). O objetivo é só mostrar a instrução gerada, não o resultado numérico.
