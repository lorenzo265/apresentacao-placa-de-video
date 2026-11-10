#!/usr/bin/env python3
"""chip.sm (nível 3): um SM, redesenho próprio da Fig. 5 do whitepaper (p. 10).

Mesma organização da figura: quatro blocos em grade 2 x 2 (escalonador, banco de
registradores, núcleos FP32/INT32, Tensor Core, LD/ST e SFU) e, embaixo, a L1 /
memória compartilhada, as unidades de textura e o RT Core. Retrato, para caber
na célula de SM da planta do chip.
"""
from _kit import Diagram, br, fact, grid, row, val

BLOCKS = val("sm.blocks")                         # 4
REGS = val("sm.block_regfile_entries")            # 16384
DISPATCH = val("sm.block_dispatch_threads_per_clk")
CORES = val("sm.cuda_cores")                      # 128
CORES_BLOCK = CORES // BLOCKS                     # 32, conta nossa (derived)
assert CORES_BLOCK * BLOCKS == CORES
LDST = val("sm.block_ldst_units")                 # 4
TEX = val("sm.tex_units")                         # 4
assert val("sm.tensor_cores") == BLOCKS, "a figura tem um Tensor Core por bloco; o spec mudou"

d = Diagram(
    "chip.sm", "sm", 3, "Um SM da Blackwell",
    "Redesenho ilustrativo da Fig. 5 do whitepaper (p. 10): as contagens são oficiais, "
    "tamanhos e posições não.",
    size=(1000, 1700),
)

d.node("sm.frame", "frame", [20, 20, 960, 1660], "SM", tags=["sm-frame"], label_size=40)

# contadores no alto: número no rótulo, unidade na sublinha
cnt = row(150, 30, 818, 70, 4, 10)
d.node("sm.count.blocks", "counter", cnt[0], f"{BLOCKS}", "blocos", parent="sm.frame",
       tags=["counter", "block"], count="sm.blocks")
d.node("sm.count.cores", "counter", cnt[1], f"{CORES}", "núcleos CUDA", parent="sm.frame",
       tags=["counter", "core"], count="sm.cuda_cores")
d.node("sm.count.regs", "counter", cnt[2], f"{br(val('sm.regfile_entries'))}", "registradores de 32 bits",
       parent="sm.frame", tags=["counter", "regfile"], count="sm.regfile_entries",
       claims=["sm.block_regfile_entries", "sm.blocks"])
d.node("sm.count.regkb", "counter", cnt[3], f"{val('sm.regfile_kb')} KB", "de registradores",
       parent="sm.frame", tags=["counter", "regfile"], count="sm.regfile_kb")

# quatro blocos
blocks = grid(40, 112, 920, 1032, 2, 2, 20, 20)
for b, (x, y, w, h) in enumerate(blocks):
    bid = f"sm.block.{b}"
    bt = f"block-{b}"
    d.node(bid, "block", [x, y, w, h], f"Bloco {b}", parent="sm.frame", tags=["block", bt],
           label_size=18, claims=["sm.blocks"])
    ix, iw = x + 10, w - 20
    sched = [ix, y + 34, iw, 64]
    d.node(f"{bid}.sched", "sched", sched, "L0 i-Cache + Warp Scheduler",
           f"Dispatch ({DISPATCH} thread/clk)", parent=bid, tags=["sched", bt], align="left", label_size=20,
           claims=["sm.block_dispatch_threads_per_clk"], provenance="confirmed",
           note="Texto da Fig. 5: 'L0 i-Cache + Warp Scheduler + Dispatch (32 thread/clk)'.")
    if b == 0:
        d.node("sm.block.0.sched.warp", "frame", [ix + iw - 98, y + 40, 92, 52],
               parent=bid, tags=["warp-zoom", "sched", bt], embed="chip.warp",
               note="Um warp de 32 threads, despachado por este escalonador.")
    d.node(f"{bid}.regfile", "regfile", [ix, y + 108, iw, 58], "Banco de registradores",
           f"{br(REGS)} × 32 bits", parent=bid, tags=["regfile", bt], label_size=22,
           count="sm.block_regfile_entries", provenance="confirmed")
    # núcleos FP32/INT32: grade 4 x 8 como na figura
    cg = [ix, y + 176, 250, 268]
    d.node(f"{bid}.cores", "frame", cg, f"FP32 / INT32 × {CORES_BLOCK}", parent=bid,
           tags=["core", "core-group", bt], label_size=17, claims=["sm.cuda_cores", "sm.blocks"],
           provenance="derived",
           note=f"{CORES} núcleos por SM / {BLOCKS} blocos = {CORES_BLOCK} (conta nossa). "
                "Cada núcleo opera como FP32 ou INT32 em cada ciclo (p. 11).")
    for c, cr in enumerate(grid(ix + 6, y + 204, 238, 234, 4, CORES_BLOCK // 4, 4, 4)):
        d.node(f"{bid}.core.{c}", "core", cr, parent=f"{bid}.cores", tags=["core", bt])
    d.node(f"{bid}.tensor", "tensor", [ix + 260, y + 176, iw - 260, 268], "Tensor Core",
           "5ª geração", parent=bid, tags=["tensor", bt], claims=["sm.tensor_cores"],
           provenance="confirmed", note="4 por SM (p. 9), um por bloco na Fig. 5.")
    units = row(ix, y + 454, iw, 46, LDST + 1, 6)
    for u in range(LDST):
        d.node(f"{bid}.ldst.{u}", "ldst", units[u], "LD/ST", parent=bid, tags=["ldst", bt],
               claims=["sm.block_ldst_units"],
               note=fact("sm.block_ldst_units")["note"] + ". Desenhadas como na Fig. 5, quatro por bloco.")
    d.node(f"{bid}.sfu", "sfu", units[LDST], "SFU", parent=bid, tags=["sfu", bt],
           claims=["sm.block_sfu"], provenance="confirmed", note="Uma SFU por bloco (Fig. 5).")

# unidades comuns aos quatro blocos
d.node("sm.l1", "cache", [40, 1164, 920, 76], "L1 / memória compartilhada",
       f"{val('sm.l1_shared_kb')} KB", parent="sm.frame", tags=["l1", "cache"],
       count="sm.l1_shared_kb", provenance="confirmed")
for t, tr in enumerate(row(40, 1252, 920, 50, TEX, 10)):
    d.node(f"sm.tex.{t}", "tex", tr, "Tex", parent="sm.frame", tags=["tex"], claims=["sm.tex_units"],
           provenance="confirmed")
d.node("sm.rt", "rt", [40, 1314, 920, 220], "RT Core", "4ª geração", parent="sm.frame",
       tags=["rt"], count="sm.rt_cores", provenance="confirmed")
d.node("sm.fp64", "note", [40, 1550, 920, 110], f"{val('sm.fp64_cores')} núcleos FP64",
       "não aparecem na Fig. 5", parent="sm.frame", tags=["fp64", "note"], count="sm.fp64_cores",
       claims=["sm.fp64_rate"],
       note=fact("sm.fp64_cores")["note"] + ". A Fig. 5 não os desenha; posição ilustrativa.")

d.check("sm.count.blocks * sm.block.0.regfile", val("sm.regfile_entries"))
d.check(f"sm.count.blocks * {CORES_BLOCK}", CORES)

if __name__ == "__main__":
    d.write(__file__)
