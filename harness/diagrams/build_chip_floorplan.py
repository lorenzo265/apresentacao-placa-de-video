#!/usr/bin/env python3
"""chip.floorplan (nível 2): planta do GB202 nesta placa, a partir do spec.

A grade nasce de chip.gpc_count x chip.tpc_per_gpc x chip.sm_per_tpc (posições do
chip completo); chip.tpc_count diz quantas estão habilitadas. As posições
desabilitadas são escolha ilustrativa: a NVIDIA não diz quais são.
"""
from _kit import Diagram, br, center, fact, gap, grid, kb_to_mb, val

GPCS = val("chip.gpc_count")            # 12
TPC_PER_GPC = val("chip.tpc_per_gpc")   # 8
SM_PER_TPC = val("chip.sm_per_tpc")     # 2
TPC_ON = val("chip.tpc_count")          # 94
TPC_FULL = val("chip.tpc_count_full")   # 96
SM_ON = val("chip.sm_count")            # 188
CORES_SM = val("sm.cuda_cores")         # 128
MCS = val("chip.mem_controllers")       # 16
MC_BITS = val("chip.mem_controller_bits")
assert GPCS * TPC_PER_GPC == TPC_FULL, "o spec não fecha: GPCs x TPCs por GPC != TPCs do chip completo"

# Posições apagadas (ilustrativas) e o SM que abre o zoom (perto do centro, junto do L2)
N_OFF = TPC_FULL - TPC_ON
DISABLED = [(4, 6), (7, 1)][:N_OFF]
assert len(DISABLED) == N_OFF, "o spec mudou: rever as posições apagadas"
ZOOM = (2, 7, 1)  # GPC 2, TPC 7, SM 1
DISABLED_NOTE = ("A NVIDIA não informa quais posições de TPC estão desabilitadas nesta placa "
                 "(lacuna chip.tpc_gpc_distribution); a escolha desta posição é ilustrativa.")

d = Diagram(
    "chip.floorplan", "chip", 2, "Planta do GB202 nesta placa",
    "Diagrama ilustrativo: as contagens são oficiais (whitepaper, Tab. 4); posições, formas "
    "e quais TPCs estão apagados não são.",
)

# ---------------- moldura do die ----------------
DIE = [330, 24, 1246, 842]
d.node("chip.die", "die", DIE, val("chip.name"), parent=None, tags=["die"], label_size=28,
       claims=["chip.name"], provenance="confirmed")
proc = val("chip.process").split(" (")[0]
d.node("chip.data", "note", [470, 36, 560, 50],
       f"{br(val('chip.die_area_mm2'))} mm² · {br(val('chip.transistors_billion'))} bilhões de transistores",
       proc, parent="chip.die", tags=["data", "die-data"], count="chip.die_area_mm2", unit="mm²",
       claims=["chip.transistors_billion", "chip.process"], provenance="confirmed")
d.node("chip.amp", "block", [1050, 36, 210, 50], "AMP", val("chip.amp_isa"),
       parent="chip.die", tags=["amp", "outside-gpc", "risc-v"],
       claims=["chip.amp_isa", "sched.amp"], provenance="confirmed",
       note="AI Management Processor: escalonador de contextos em processador RISC-V (whitepaper, p. 25). Posição ilustrativa.")
d.node("chip.pcie", "block", [1278, 36, 210, 50], val("card.pcie"), "interface com a CPU",
       parent="chip.die", tags=["pcie", "outside-gpc"], claims=["card.pcie"], provenance="confirmed",
       note="Interface de sistema do datasheet; posição no die ilustrativa.")

# ---------------- GPCs, TPCs e SMs ----------------
GX, GW, GH, GGAP = 418, 1070, 316, 10
ROWS_Y = [96, 532]
COLS = GPCS // 2
gpc_rects = []
for r, y in enumerate(ROWS_Y):
    gpc_rects += grid(GX, y, GW, GH, COLS, 1, GGAP)
assert len(gpc_rects) == GPCS

sm_seen = 0
for g, gr in enumerate(gpc_rects):
    gid = f"chip.gpc.{g}"
    x, y, w, h = gr
    d.node(gid, "gpc", gr, f"GPC {g}", parent="chip.die", label_size=16,
           tags=["gpc", f"gpc-{g}", "gpc-row-top" if g < COLS else "gpc-row-bottom"])
    tpcs = grid(x + 8, y + 28, w - 16, h - 36, 2, TPC_PER_GPC // 2, 6)
    for t, tr in enumerate(tpcs):
        tid = f"{gid}.tpc.{t}"
        off = (g, t) in DISABLED
        d.node(tid, "tpc", tr, parent=gid,
               tags=["tpc", f"gpc-{g}", "tpc-disabled" if off else "tpc-enabled"],
               state="disabled" if off else None, note=DISABLED_NOTE if off else None)
        tx, ty, tw, th = tr
        sms = grid(tx + 3, ty + 3, tw - 6, th - 6, SM_PER_TPC, 1, 3)
        for s, sr in enumerate(sms):
            sid = f"{tid}.sm.{s}"
            zoom = (g, t, s) == ZOOM
            tags = ["sm", f"gpc-{g}", "sm-disabled" if off else "sm-enabled"]
            if zoom:
                assert not off, "o SM do zoom não pode estar apagado"
                tags.append("sm-zoom")
            d.node(sid, "sm", sr, parent=tid, tags=tags,
                   state="disabled" if off else None, note=DISABLED_NOTE if off else None,
                   embed="chip.sm" if zoom else None)
            sm_seen += 0 if off else 1
assert sm_seen == SM_ON, f"desenhei {sm_seen} SMs habilitados, o spec diz {SM_ON}"

# ---------------- L2 e controladores de memória ----------------
L2 = [GX, 424, GW, 96]
d.node("chip.l2", "cache", L2, "L2", f"{kb_to_mb(val('chip.l2_kb'))} MB, compartilhado pelos GPCs",
       parent="chip.die", tags=["l2", "cache", "memory-path"], count="chip.l2_kb",
       provenance="confirmed")

mc_l = grid(342, 96, 60, 752, 1, MCS // 2, 10)
mc_r = grid(1504, 96, 60, 752, 1, MCS // 2, 10)
l2cx, l2cy = center(L2)
for i, mr in enumerate(mc_l + mc_r):
    left = i < MCS // 2
    mid = f"chip.memctl.{i}"
    d.node(mid, "memctl", mr, "MC", f"{MC_BITS} bits", parent="chip.die",
           tags=["memctl", "memory-path", "memctl-left" if left else "memctl-right"],
           count="chip.mem_controller_bits", provenance="confirmed")
    _, cy = center(mr)
    if left:
        pts = [(L2[0], l2cy), (410, l2cy), (410, cy), (mr[0] + mr[2], cy)]
    else:
        pts = [(L2[0] + L2[2], l2cy), (1496, l2cy), (1496, cy), (mr[0], cy)]
    d.flow(f"chip.flow.l2_mc{i}", "chip.l2", mid, path="data", points=pts, provenance="illustrative",
           claim="chip.mem_controller_bits")

# ---------------- coluna lateral: contagens, chave, conflito, lacuna ----------------
SX, SW = 24, 290
d.node("chip.count.gpc", "counter", [SX, 24, SW, 70], f"{GPCS} GPCs", "Graphics Processing Clusters",
       tags=["counter", "count-gpc"], count="chip.gpc_count")
d.node("chip.count.tpc", "counter", [SX, 104, SW, 70], f"{TPC_ON} TPCs", "habilitados nesta placa",
       tags=["counter", "count-tpc"], count="chip.tpc_count")
d.node("chip.count.sm", "counter", [SX, 184, SW, 70], f"{SM_ON} SMs",
       f"habilitados ({TPC_ON} × {SM_PER_TPC})", tags=["counter", "count-sm"], count="chip.sm_count",
       claims=["chip.tpc_count", "chip.sm_per_tpc"])
d.node("chip.count.cores", "counter", [SX, 264, SW, 70], f"{br(val('chip.cuda_cores'))} núcleos CUDA",
       f"{SM_ON} × {CORES_SM}", tags=["counter", "count-cores"], count="chip.cuda_cores",
       claims=["chip.sm_count", "sm.cuda_cores"])
d.node("chip.count.mc", "counter", [SX, 344, SW, 70], f"{MCS} controladores",
       f"{MCS} × {MC_BITS} bits = {val('mem.bus_bits')} bits", tags=["counter", "count-mc", "memory-path"],
       count="chip.mem_controllers", claims=["chip.mem_controller_bits", "mem.bus_bits"])

d.node("chip.key.tpc_per_gpc", "note", [SX, 426, SW, 44], f"1 GPC = {TPC_PER_GPC} TPCs",
       tags=["key", "key-gpc"], count="chip.tpc_per_gpc",
       note="Valor do chip completo (p. 9). Com 94 TPCs a divisão por GPC não é inteira.")
d.node("chip.key.sm_per_tpc", "note", [SX, 478, SW, 44], f"1 TPC = {SM_PER_TPC} SMs",
       tags=["key", "key-tpc"], count="chip.sm_per_tpc")
d.node("chip.key.cores_per_sm", "note", [SX, 530, SW, 44], f"1 SM = {CORES_SM} núcleos CUDA",
       tags=["key", "key-sm"], count="sm.cuda_cores")

d.node("chip.note.conflict", "note", [SX, 588, SW, 84], f"Chip completo: {val('chip.sm_count_full')} SMs",
       f"Tab. 4 desta placa: {SM_ON} SMs", tags=["note", "conflict", "full-chip"],
       count="chip.sm_count_full", claims=["chip.sm_count", "chip.tpc_count_full", "chip.tpc_count"],
       note=fact("chip.sm_count_full")["note"] + ". Valor adotado: " + str(SM_ON)
       + " (Tab. 4, confere com " + f"{TPC_ON} × {SM_PER_TPC} e com o datasheet).")
d.node("chip.note.disabled", "note", [SX, 684, SW, 84], f"{N_OFF} posições de TPC apagadas",
       "quais: escolha ilustrativa", tags=["note", "disabled-key"],
       claims=["chip.tpc_count", "chip.tpc_count_full"], note=DISABLED_NOTE)
d.node("chip.gap.sm_reason", "gap", [SX, 780, SW, 86], f"Por que {SM_ON} e não {val('chip.sm_count_full')}?",
       "o whitepaper não explica", tags=["gap"], note=gap("chip.sm_count_reason")["description"])

# ---------------- contas ----------------
d.check("chip.count.tpc * chip.key.sm_per_tpc", SM_ON)
d.check("chip.count.sm * chip.key.cores_per_sm", val("chip.cuda_cores"))
d.check("chip.count.gpc * chip.key.tpc_per_gpc", TPC_FULL)
d.check("chip.count.mc * chip.memctl.0", val("mem.bus_bits"))

if __name__ == "__main__":
    d.write(__file__)
