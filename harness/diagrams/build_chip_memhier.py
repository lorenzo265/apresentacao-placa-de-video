#!/usr/bin/env python3
"""chip.memhier (nível 3): a escada de memória, do mais rápido ao maior.

Tamanhos são oficiais (confirmed). Latências são medidas na RTX 5080 (GB203, mesma
família) e ficam derived, em nós separados (tag latency) para o storyboard poder
destacá-las sozinhas. A latência do banco de registradores não tem medida no spec.
"""
from _kit import Diagram, br, gap, kb_to_mb, val

SM = val("chip.sm_count")

d = Diagram(
    "chip.memhier", "memh", 3, "Hierarquia de memória: tamanho e latência",
    "Tamanhos oficiais (whitepaper); latências medidas na RTX 5080 (GB203), outra placa da "
    "mesma família. Larguras dos degraus ilustrativas.",
)

d.node("memh.head.steps", "header", [30, 30, 1000, 44], "do mais rápido (em cima) ao maior (embaixo)",
       tags=["header"])
d.node("memh.head.lat", "header", [1060, 30, 240, 44], "latência", tags=["header", "latency"])
d.node("memh.head.total", "header", [1320, 30, 250, 44], "total na placa", tags=["header", "total"])

STEP_Y = [90 + i * 166 for i in range(4)]
SH = 148
STEP_W = [400, 600, 800, 1000]
STEPS = [
    ("regs", "regfile", "Registradores", f"{val('sm.regfile_kb')} KB por SM", "sm.regfile_kb", []),
    ("l1", "cache", "L1 / memória compartilhada", f"{val('sm.l1_shared_kb')} KB por SM", "sm.l1_shared_kb", []),
    ("l2", "cache", "L2", f"{kb_to_mb(val('chip.l2_kb'))} MB no chip", "chip.l2_kb", []),
    ("dram", "memory", val("mem.type"), f"{val('mem.capacity_gb')} GB na placa", "mem.capacity_gb", ["mem.type"]),
]
for i, (key, kind, name, size, claim, extra) in enumerate(STEPS):
    y = STEP_Y[i]
    d.node(f"memh.step.{key}", kind, [30, y, STEP_W[i], SH], name, size,
           tags=["step", f"step-{i + 1}", key, "size"], count=claim, claims=extra, provenance="confirmed",
           label_size=30)

LAT = [
    None,
    ("l1", f"{val('lat.l1_cycles')} ciclos", None, ["lat.l1_cycles"]),
    ("l2", f"≈ {br(val('lat.l2_cycles'))} ciclos", "lat.l2_cycles", []),
    ("dram", f"≈ {br(val('lat.global_cycles'))} ciclos", "lat.global_cycles", []),
]
for i, item in enumerate(LAT):
    r = [1060, STEP_Y[i] + 14, 240, SH - 28]
    if item is None:
        d.node("memh.lat.regs", "gap", r, "sem medida levantada", None, tags=["latency", "regs", "gap"], label_size=19,
               note="O spec não tem latência de acesso ao banco de registradores. lat.int_fp_cycles "
                    "(4 ciclos) é latência de instrução, não de acesso.")
        continue
    key, text, cnt, cl = item
    d.node(f"memh.lat.{key}", "counter", r, text, "RTX 5080 (GB203)", tags=["latency", key], label_size=24,
           count=cnt, claims=cl, provenance="derived",
           note="Jarmusch et al., medida na RTX 5080 (GB203); 'cerca de' na fonte." if cnt else
           "Jarmusch et al., RTX 5080 (GB203), seção VI-B.")

# carveout do L1 (beat a5.14): a divisão entre cache e memória compartilhada é escolhida em tempo de execução
cy0 = STEP_Y[1] + 6
CNOTE = "Divisão desenhada ilustrativa; os tamanhos possíveis na compute capability 12.0 não foram levantados."
d.node("memh.carveout.l1", "cache", [650, cy0, 170, 50], "cache L1", tags=["carveout", "l1"],
       claims=["mem.l1_carveout", "sm.l1_shared_kb"], provenance="confirmed", label_size=20, note=CNOTE)
d.node("memh.carveout.smem", "memory", [826, cy0, 214, 50], "compartilhada", tags=["carveout", "l1"],
       claims=["mem.l1_carveout", "sm.l1_shared_kb"], provenance="confirmed", label_size=20, note=CNOTE)
d.node("memh.carveout.note", "note", [650, cy0 + 56, 390, 36], "divisão escolhida em tempo de execução",
       tags=["carveout", "l1"], claims=["mem.l1_carveout"], provenance="confirmed", label_size=18)
d.node("memh.carveout.gap", "note", [650, cy0 + 98, 390, 40], "compartilhada: 0, 8, 16, 32, 64 ou 100 KB",
       tags=["carveout", "sizes"], claims=["mem.shared_sizes_cc120"], provenance="confirmed", label_size=18,
       note="Guia CUDA 13.5, 3.2.6, para a compute capability 12.0. " + gap("cuda.smem_per_sm_cc120")["description"])
assert cy0 + 138 <= STEP_Y[1] + SH

d.node("memh.total.regs", "counter", [1320, STEP_Y[0] + 24, 250, SH - 48],
       f"{br(val('card.regfile_total_kb'))} KB", f"{SM} × {val('sm.regfile_kb')} KB",
       tags=["total", "regs"], label_size=26, count="card.regfile_total_kb", claims=["chip.sm_count", "sm.regfile_kb"])
d.node("memh.total.l1", "counter", [1320, STEP_Y[1] + 24, 250, SH - 48],
       f"{br(val('card.l1_total_kb'))} KB", f"{SM} × {val('sm.l1_shared_kb')} KB",
       tags=["total", "l1"], label_size=26, count="card.l1_total_kb", claims=["chip.sm_count", "sm.l1_shared_kb"])

d.node("memh.note.lat", "note", [30, 772, 760, 100], "latências: RTX 5080 (GB203)",
       "mesma família, outra placa: valores derivados", tags=["note", "latency"],
       claims=["lat.l1_cycles", "lat.l2_cycles", "lat.global_cycles"], provenance="derived")
d.node("memh.gap.policy", "gap", [810, 772, 760, 100], "Política e associatividade dos caches",
       "não são públicas", tags=["gap", "cache-policy"], note=gap("cache.policy")["description"])

d.check(f"memh.step.regs * {SM}", val("card.regfile_total_kb"))
d.check(f"memh.step.l1 * {SM}", val("card.l1_total_kb"))

if __name__ == "__main__":
    d.write(__file__)
