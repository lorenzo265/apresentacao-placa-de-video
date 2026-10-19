# NVIDIA RTX PRO Blackwell GPU Architecture, v1.1 (whitepaper)

- Publicador: NVIDIA
- URL: https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf
- Acessado em: 2026-10-19
- Procedência: `confirmed` (documento oficial do fabricante)
- O PDF não é versionado neste repositório (direitos do fabricante). Para reproduzir: baixar a URL e rodar `pdftotext -layout`.

## Números conferidos

Páginas conforme o rodapé do PDF. "Tab. 4" é a tabela de especificações completas do Apêndice A (p. 46 a 48).

| Dado | Valor | Onde |
|---|---|---|
| Chip completo GB202 | 12 GPCs, 96 TPCs, 192 SMs, 24.576 núcleos CUDA | p. 8 e p. 45 |
| Interface de memória | 512 bits, dezesseis controladores de 32 bits | p. 8 |
| RTX PRO 6000 Workstation | 12 GPCs, **94 TPCs, 188 SMs, 24.064 núcleos CUDA** | Tab. 4 |
| Por SM | 128 núcleos CUDA FP32, 4 Tensor Cores (5ª ger.), 1 RT Core (4ª ger.), 4 unidades de textura | p. 9 |
| Por SM, memória | 256 KB de banco de registradores, 128 KB de L1/memória compartilhada | p. 9 |
| FP64 | 2 núcleos por SM, taxa de 1/64 da FP32 | nota da Fig. 3, p. 8 |
| GPC | 1 Raster Engine, 2 partições de ROP (8 ROPs cada), 8 TPCs | p. 9 |
| TPC | 1 PolyMorph Engine e 2 SMs | p. 9 |
| L2 | 131.072 KB (128 MB) | p. 9 e Tab. 4 |
| L1/compartilhada total | 24.064 KB | Tab. 4 |
| Banco de registradores total | 48.128 KB | Tab. 4 |
| Memória | 96 GB GDDR7, 28 Gbps, 512 bits, 1.792 GB/s | Tab. 4 |
| ECC | correção de erro simples (SEC), sempre ligada, sem opção de desligar | p. 13 (nota da v1.1) |
| Sinalização GDDR7 | 3 níveis, 1,5 bit por ciclo (PAM3) | p. 12 |
| PCI Express | Gen 5 | Tab. 4 |
| TGP | 600 W (Workstation), 300 W (Max-Q) | Tab. 4 |
| Processo | TSMC 4N (custom NVIDIA) | Tab. 4 |
| Transistores e die | 92,2 bilhões, 750 mm² | Tab. 4 |
| Tensor Cores | FP16, BF16, TF32, INT8, FP8; novos FP4 e FP6 | p. 15 |
| AMP (AI Management Processor) | escalonador de contextos programável, implementado com um processador RISC-V dedicado na frente do pipeline da GPU | p. 25 |
| MIG | até 4 instâncias de GPU | p. 44 |
| DisplayPort | 2.1b, até 80 Gbps | p. 30 |

## Contas que fecham
- 94 TPCs × 2 SMs = 188 SMs; 188 × 128 = 24.064 núcleos CUDA.
- 188 × 256 KB = 48.128 KB de registradores; 188 × 128 KB = 24.064 KB de L1/compartilhada.
- 28 Gbps × 512 bits ÷ 8 = 1.792 GB/s.
- 256 KB ÷ 4 B = 65.536 registradores de 32 bits por SM (conta derivada, não está no texto).

## Inconsistências do documento (tratar com cuidado)
1. O texto da p. 8 diz que as RTX PRO 6000 "usam o GB202 completo" (192 SMs), mas as tabelas (Tab. 1 e 4) dão 188 SMs e 94 TPCs. Usamos as tabelas, que são consistentes entre si e com as demais contas.
2. A largura de banda da RTX 6000 Ada aparece como 1.008 GB/s na Tab. 1 e como 960 GB/s na Tab. 4. Qualquer comparação com a Ada precisa citar a origem do número e registrar a divergência.

## O que o documento NÃO cobre
Memória virtual e MMU, interrupções, conjunto de instruções (PTX e SASS), profundidade do pipeline do SM, política dos caches, organização do banco de registradores. Esses itens dependem de outras fontes (ver `vault/01-Briefing/Plano de pesquisa.md`).
