#!/usr/bin/env python3
"""close.gaps (nível 4): o que sabemos e onde as fontes lidas param, por item do enunciado.

Uma linha por item: o que sabemos (curto, com claims) e a lacuna (kind gap), tirada do
array `gaps` do spec e do que os outros diagramas já declaram como gap.
"""
from _kit import Diagram, br, gap, val

d = Diagram(
    "close.gaps", "gaps", 4, "O que sabemos e o que falta",
    "Lacunas declaradas: o que as fontes lidas não cobrem. 'O que sabemos' resume fatos já citados "
    "nas seções anteriores; a disposição é ilustrativa.",
)

d.node("gaps.head.item", "header", [40, 24, 290, 46], "item do enunciado", tags=["header"])
d.node("gaps.head.known", "header", [340, 24, 620, 46], "o que sabemos", tags=["header", "head-known"])
d.node("gaps.head.gap", "header", [970, 24, 590, 46], "onde as fontes lidas param", tags=["header", "head-gap"])

ROWS = [
    # slug, item, sabemos, kw de sabemos, lacuna, ids de lacuna do spec (None = declarada em outro diagrama)
    ("registradores", "Registradores",
     f"{br(val('sm.regfile_entries'))} por SM; até {val('sm.max_regs_per_thread')} por thread",
     dict(count="sm.regfile_entries", claims=["sm.max_regs_per_thread"]),
     ("bancos e portas: sem fonte da Blackwell", "só há medidas de Volta, Turing e Ampere"), ["regfile.organization"]),
    ("instrucoes", "Instruções",
     f"{val('isa.instruction_bytes')} bytes cada; {val('isa.sass_mnemonics')} mnemônicos (contagem nossa)",
     dict(count="isa.instruction_bytes", claims=["isa.sass_mnemonics"], provenance="derived"),
     ("bits de controle do sm_120: sem fonte da Blackwell", "medidos só em Volta, Turing e Ampere"),
     ["isa.control_bits_blackwell", "isa.ldc_ldcu_saxpy"]),
    ("risc-cisc", "RISC ou CISC",
     "formato fixo; carga e armazenamento como regra",
     dict(claims=["isa.instruction_bytes", "isa.ptx_load_store"], provenance="confirmed"),
     ("microcódigo: nada público", "modos de endereçamento: não levantamos"), None),
    ("mmu", "MMU",
     f"{val('mmu.va_bits')} bits, {val('mmu.levels')} níveis, 4 tamanhos de página",
     dict(count="mmu.va_bits", claims=["mmu.levels", "mmu.page_sizes"]),
     ("TLB: tamanho, níveis e política sem fonte", "doc. de hardware: só lemos o da Pascal"), ["mmu.tlb", "mmu.hardware_doc"]),
    ("interrupcoes", "Interrupções",
     "MSI-X ou MSI, duas metades, trap, Xid",
     dict(claims=["irq.modes", "irq.top_half", "irq.bottom_half", "irq.ptx_trap", "irq.xid13"], provenance="confirmed"),
     ("preempção na Blackwell, interrupção no SM: sem fonte", "caminho dentro da GPU: nv.c lido em parte"),
     ["sched.preemption_blackwell", "irq.sm_level", "irq.exit_path"]),
    ("memoria", "Gerenciamento de memória",
     "falhas em lote e repetição; carveout do L1",
     dict(claims=["fault.buffer_batch", "fault.replay", "mem.l1_carveout"], provenance="confirmed"),
     ("espaço por programa: sem fonte", "memória unificada: não levantamos"),
     ["mmu.address_space_per_program", "cuda.smem_per_sm_cc120"]),
    ("pipeline", "Pipeline",
     f"{val('sm.blocks')} escalonadores, {val('sm.block_dispatch_threads_per_clk')} threads por ciclo cada",
     dict(count="sm.blocks", claims=["sm.block_dispatch_threads_per_clk"]),
     ("profundidade e instruções por ciclo", "nada oficial; só estágios medidos na Ampere"), ["pipeline.depth"]),
    ("cache", "Cache",
     f"L1 de {val('sm.l1_shared_kb')} KB por SM; L2 de {val('chip.l2_kb') // 1024} MB",
     dict(count="sm.l1_shared_kb", claims=["chip.l2_kb"]),
     ("substituição, escrita, associatividade, linha", "o whitepaper não cobre"), ["cache.policy"]),
]
assert ROWS[0][2].startswith("65.536"), ROWS[0][2]

RY, RH, RS = 80, 88, 96
for i, (slug, item, known, kw, lac, gids) in enumerate(ROWS):
    y = RY + i * RS
    rt = f"row-{slug}"
    d.node(f"gaps.{slug.replace('-', '_')}.item", "header", [40, y, 290, RH], item, tags=[rt, "item"],
           label_size=19)
    d.node(f"gaps.{slug.replace('-', '_')}.known", "cell", [340, y, 620, RH], known, tags=[rt, "known"],
           align="left", label_size=20, **kw)
    note = " | ".join(gap(g)["description"] for g in gids) if gids else \
        "Declarado em chip.risc: nenhuma informação pública sobre microcódigo; modos de endereçamento não levantados."
    d.node(f"gaps.{slug.replace('-', '_')}.gap", "gap", [970, y, 590, RH], lac[0], lac[1], tags=[rt, "gap"],
           align="left", label_size=19, note=note)

if __name__ == "__main__":
    d.write(__file__)
