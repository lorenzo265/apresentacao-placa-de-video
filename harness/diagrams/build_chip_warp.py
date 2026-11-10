#!/usr/bin/env python3
"""chip.warp (nível 4): um warp de 32 threads em grade 8 x 4, embutido no escalonador do bloco 0.

As threads 28 a 31 são `thread-alt` (seguiram outro caminho): é o logotipo do grupo,
32 quadrados com 4 em laranja.
"""
from _kit import Diagram, br, grid, val

WARP = val("warp.size")            # 32
COLS, ROWS = 8, 4
assert COLS * ROWS == WARP, "o spec mudou o tamanho do warp: rever a grade"
DIVERGED = range(WARP - 4, WARP)   # 28, 29, 30, 31

d = Diagram(
    "chip.warp", "warp", 4, "Um warp: 32 threads",
    "Diagrama ilustrativo: 32 threads por warp e 48 warps por SM são oficiais; a grade e "
    "as 4 threads divergentes são ilustração (o logotipo do grupo).",
)

cells = grid(130, 28, 1340, 660, COLS, ROWS, 20, 20)
for i, cr in enumerate(cells):
    alt = i in DIVERGED
    d.node(f"warp.thread.{i}", "thread-alt" if alt else "thread", cr, str(i), label_size=84,
           tags=["thread", f"thread-{i}", f"lane-row-{i // COLS}"] + (["diverged"] if alt else ["converged"]),
           note="Seguiu o outro caminho do desvio: executa enquanto as demais ficam desabilitadas."
           if alt else None)

c = grid(130, 718, 1340, 150, 3, 1, 20)
d.node("warp.count.size", "counter", c[0], f"{WARP} threads", "por warp (WARP_SZ)",
       tags=["counter", "warp-size"], count="warp.size")
d.node("warp.count.max_warps", "counter", c[1], f"até {val('sm.max_warps')} warps", "por SM",
       tags=["counter", "occupancy"], count="sm.max_warps")
d.node("warp.count.threads_sm", "counter", c[2], f"{br(val('sm.max_threads'))} threads",
       f"por SM ({val('sm.max_warps')} × {WARP})", tags=["counter", "occupancy"],
       count="sm.max_threads", claims=["sm.max_warps", "warp.size"], provenance="derived")

d.check("warp.count.max_warps * warp.count.size", val("sm.max_threads"))
d.check("warp.count.threads_sm", val("sm.max_warps") * WARP)

if __name__ == "__main__":
    d.write(__file__)
