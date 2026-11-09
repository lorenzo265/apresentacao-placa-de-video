# Exemplo do artigo: SAXPY em CUDA C até SASS (`sm_120`)

Reprodução, em 2026-11-09, do experimento da seção 4.4 e da Figura 4 do artigo entregue ("Estudo da arquitetura da GPU NVIDIA RTX PRO 6000 Blackwell"). O artigo compila um arquivo `.cu` com o `nvcc` e mostra o SASS com o `cuobjdump`. O outro exemplo do repositório (`../saxpy/`) parte de PTX escrito à mão e usa `ptxas` e `nvdisasm`: mesma conta, parâmetros em outra ordem.

**O seminário usa este exemplo**, para o que aparece na tela ser o mesmo que está no artigo.

## Como reproduzir
Não precisa de GPU.

```bash
python3 -m venv venv
./venv/bin/pip install nvidia-cuda-nvcc==13.5.37 nvidia-cuda-cuobjdump nvidia-cuda-nvdisasm nvidia-cuda-runtime nvidia-cuda-cccl
B=venv/lib/python3*/site-packages/nvidia/cu13/bin
PATH=$B:$PATH nvcc -arch=sm_120 -cubin -Xptxas -v saxpy.cu -o saxpy.cubin
PATH=$B:$PATH cuobjdump -sass saxpy.cubin > saxpy.sm_120.sass
PATH=$B:$PATH nvcc -arch=sm_120 -ptx saxpy.cu -o saxpy.ptx
```

Versões usadas: `nvcc` 13.5.37 ("Cuda compilation tools, release 13.5"), `cuobjdump` e `nvdisasm` 13.5.37. O `cuobjdump` chama o `nvdisasm`, que precisa estar no `PATH`. O `.cubin` não é versionado.

## Resultado da conferência
| Afirmação do artigo | Reprodução | Veredito |
|---|---|---|
| Listagem SASS da Figura 4 (20 linhas, de `0x0000` a `0x0130`) | idêntica, instrução por instrução e deslocamento por deslocamento | confere |
| "Used 10 registers, used 0 barriers" | idêntico | confere |
| "0 bytes stack frame, 0 bytes spill stores, 0 bytes spill loads" | idêntico | confere |
| Cada instrução ocupa 16 bytes | endereços de `0x10` em `0x10` | confere |
| PTX versão 9.5 | o PTX gerado começa com `.version 9.5` | confere |
| Tabela 3 (PTX para SASS) | o PTX gerado tem `ld.param`, `mov %ctaid.x`, `mad.lo.s32`, `setp.ge.s32` com `bra`, `ld.global`, `fma.rn.f32`, `st.global` | confere |
| "encontramos ... um registrador que sempre vale zero (RZ)" | `RZ` **não aparece** nesta listagem | não confere com o exemplo. `RZ` existe em outros códigos SASS, mas o texto diz que foi visto aqui |
| Tempo de compilação de 771 ms | 3 ms aqui | irrelevante (depende da máquina) |

O que a figura do artigo omite: depois da `BRA 0x130` há 12 `NOP` até `0x01f0`, completando 32 instruções (512 bytes). O PTX gerado tem 20 instruções; o SASS tem 19 até o último `EXIT`.

## Onde estão os parâmetros
Assinatura: `saxpy(int n, float a, const float* x, float* y)`.

| Parâmetro | Banco de constantes | Instrução |
|---|---|---|
| `n` | `c[0x0][0x380]` | `LDCU UR5` |
| `a` | `c[0x0][0x384]` | `LDCU UR6` |
| `x` | `c[0x0][0x388]` | `LDC.64 R2` |
| `y` | `c[0x0][0x390]` | `LDC.64 R4` |
| `blockDim.x` | `c[0x0][0x360]` | `LDC R7` |

A correspondência entre deslocamento e parâmetro é leitura nossa (`derived`): segue a ordem e o tamanho dos parâmetros. As instruções `LDC R1, c[0x0][0x37c]` e `LDCU.64 UR4, c[0x0][0x358]` não têm par no código-fonte e a função delas não é documentada.
