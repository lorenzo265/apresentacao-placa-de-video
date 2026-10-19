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
Versões usadas em 2026-10-19: `ptxas` 12.9.86 e `nvdisasm` 13.4.92. O `.cubin` não é versionado. Os comentários do PTX precisam ser ASCII.

## O que a saída mostra
1. **Largura fixa.** O SASS tem 32 instruções e os endereços avançam sempre de 0x10 em 0x10: 16 bytes (128 bits) por instrução, mostrados pelo `nvdisasm` como duas palavras de 64 bits. A documentação do Binary Utilities (apêndice do formato JSON) diz o mesmo: "The instruction size is 16 bytes".
2. **Memória.** Acesso à global só por `LDG` e `STG`; leitura de constantes por `LDC` e `LDCU`. Nenhuma instrução aritmética (`IMAD`, `FFMA`, `ISETP`) tem endereço de memória como operando neste kernel, mas elas aceitam registradores e **imediatos** (`IMAD.WIDE R2, R7, 0x4, R2`). Em outros exemplos da documentação (seção 3.1.1) instruções aritméticas aceitam operando direto de constante, `c[0x0][0x0]`, então a regra "só carga e armazenamento" tem exceção.
3. **Parâmetros no banco de constantes 0.** Os parâmetros do kernel são lidos de `c[0x0][...]` (tabela abaixo).
4. **Três famílias de registradores:** `R` (por thread), `UR` (prefixo U: caminho uniforme; a tabela 4.4 do Binary Utilities descreve `LDCU` e `S2UR` como cargas para registrador uniforme) e `P` (predicados).
5. **Predicação.** `ISETP` escreve o predicado `P0` e `@P0 EXIT` encerra as threads fora do vetor.
6. **Contagem.** O PTX tem 20 instruções. O SASS tem 19 úteis até o último `EXIT`: o `cvta` some (−2), `mul.wide` e dois `add.s64` viram duas `IMAD.WIDE` (−1) e aparecem duas instruções sem par no PTX (+2).
7. **Preenchimento.** Depois do `EXIT` há uma `BRA` para si mesma e 12 `NOP` até completar 512 bytes. É interpretação nossa que seja preenchimento e trava de segurança.
8. **Registradores.** `ptxas -v`: 10 registradores por thread, 0 bytes de spill.

## Correspondência PTX para SASS
| PTX | SASS gerado |
|---|---|
| parâmetro `px` (`ld.param.u64`) | `LDC.64 R2, c[0x0][0x380]` |
| parâmetro `py` (`ld.param.u64`) | `LDC.64 R4, c[0x0][0x388]` |
| parâmetro `pa` (`ld.param.f32`) | `LDCU UR6, c[0x0][0x390]` |
| parâmetro `pn` (`ld.param.u32`) | `LDCU UR5, c[0x0][0x394]` |
| `mov %ntid.x` | `LDC R7, c[0x0][0x360]` |
| `mov %tid.x` | `S2R R0, SR_TID.X` |
| `mov %ctaid.x` | `S2UR UR4, SR_CTAID.X` |
| `mad.lo.s32` | `IMAD R7, R7, UR4, R0` |
| `setp.ge.s32` e `@%p1 bra` | `ISETP.GE.AND P0, ...` e `@P0 EXIT` |
| `cvta.to.global` (2) | (eliminado) |
| `mul.wide.s32` e `add.s64` (2) | `IMAD.WIDE` (2) |
| `ld.global.f32` (2) | `LDG.E` (2) |
| `fma.rn.f32` | `FFMA` |
| `st.global.f32` | `STG.E` |
| `ret` | `EXIT` |
| (sem par no PTX) | `LDC R1, c[0x0][0x37c]` e `LDCU.64 UR4, c[0x0][0x358]` |

As duas últimas linhas não têm par no PTX e a função delas não é documentada. Hipótese do grupo (`inferred`): a primeira inicializa o `R1` e a segunda carrega o descritor de memória usado por `desc[UR4]` nas instruções `LDG` e `STG`. O exemplo da seção 2.1.1 do Binary Utilities (compilado para `sm_100`) mostra os mesmos deslocamentos de constantes.

## Limites
Um kernel pequeno não representa toda a ISA. Os campos do segundo bloco de 64 bits (controle de escalonamento) não são documentados para `sm_120`. O artigo da Volta descreve esses campos só para a Volta.
