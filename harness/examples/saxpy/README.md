# Exemplo: SAXPY de PTX a SASS (`sm_120`)

Kernel `y[i] = a * x[i] + y[i]`, escrito em PTX à mão e compilado para o alvo da RTX PRO 6000 Blackwell (compute capability 12.0, `sm_120`). Não precisa de GPU: só monta e desmonta.

## Como reproduzir
```bash
python3 -m venv venv
./venv/bin/pip install nvidia-cuda-nvcc-cu12 nvidia-cuda-nvdisasm
V=venv/lib/python3*/site-packages/nvidia
$V/cuda_nvcc/bin/ptxas -v -arch=sm_120 saxpy.ptx -o saxpy.cubin
$V/cu13/bin/nvdisasm -c -hex saxpy.cubin > saxpy.sm_120.sass
```
Versões usadas em 2026-10-19: `ptxas` 12.9.86 e `nvdisasm` 13.4.92. O `.cubin` não é versionado.

## O que a saída mostra
1. **Largura fixa.** O SASS tem 32 instruções e os endereços avançam sempre de 0x10 em 0x10: cada instrução ocupa 16 bytes (128 bits), mostrados pelo `nvdisasm` como duas palavras de 64 bits.
2. **Memória só por instruções próprias.** Acesso à memória global só por `LDG` e `STG`; leitura de constantes por `LDC` e `LDCU`. As instruções aritméticas (`IMAD`, `FFMA`, `ISETP`) têm só registradores como operandos. Isto vale para este kernel, não prova a regra para toda a ISA.
3. **Parâmetros no banco de constantes.** Os quatro parâmetros do kernel são lidos de `c[0x0][...]` (banco de constantes 0).
4. **Três famílias de registradores:** `R` (por thread), `UR` (prefixo U: caminho uniforme) e `P` (predicados).
5. **Predicação.** `ISETP` escreve o predicado `P0` e `@P0 EXIT` encerra as threads fora do vetor.
6. **Menos instruções que no PTX.** O PTX tem 20 instruções. O SASS tem 19 úteis até o `EXIT`: o `cvta` desaparece e `mul.wide` mais `add.s64` viram uma única `IMAD.WIDE`.
7. **Preenchimento.** Depois do `EXIT` há uma `BRA` para si mesma e 12 `NOP` até completar 512 bytes. É interpretação nossa que seja preenchimento e trava de segurança.
8. **Registradores.** `ptxas -v`: 10 registradores por thread, 0 bytes de spill.

## Correspondência PTX para SASS
| PTX | SASS gerado |
|---|---|
| `ld.param.*` (4) | `LDC`, `LDC.64`, `LDCU`, `LDCU.64` |
| `mov %ctaid.x`, `mov %tid.x`, `mad.lo.s32` | `S2UR`, `S2R`, `IMAD` |
| `setp.ge.s32` e `@%p1 bra` | `ISETP.GE.AND P0` e `@P0 EXIT` |
| `cvta.to.global` (2) | (eliminado) |
| `mul.wide.s32` e `add.s64` (2) | `IMAD.WIDE` (2) |
| `ld.global.f32` (2) | `LDG.E` (2) |
| `fma.rn.f32` | `FFMA` |
| `st.global.f32` | `STG.E` |
| `ret` | `EXIT` |

## Limites
Um kernel pequeno não representa toda a ISA. Os campos do segundo bloco de 64 bits (controle de escalonamento) não são documentados para `sm_120`. O artigo da Volta descreve esses campos só para a Volta.
