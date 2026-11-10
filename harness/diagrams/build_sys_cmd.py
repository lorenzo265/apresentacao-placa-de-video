#!/usr/bin/env python3
"""sys.cmd (nível 4): como o trabalho chega à GPU, segundo o driver oficial.

O driver grava comandos num pushbuffer, reserva uma entrada da GPFIFO do canal e avança
o ponteiro PUT (write_gpu_put); a GPU consome a fila do canal. A GPFIFO é um anel com
GET e PUT. Descrito para os canais do próprio driver (UVM); o caminho de um programa
CUDA comum passa pela parte fechada do driver (cmd.user_path, derived).
"""
import math

from _kit import Diagram, grid

d = Diagram(
    "sys.cmd", "cmd", 4, "Como o trabalho chega à GPU: canais e GPFIFO",
    "Segundo o driver oficial, para os canais do próprio driver. Número de entradas do anel, "
    "posições de GET e PUT, caixas e posições são ilustrativos.",
)
SUBMIT, RING, CHAN = "cmd.submit", "cmd.gpfifo", "cmd.channel"

# ---------------- faixas ----------------
d.node("cmd.lane.cpu", "lane", [40, 24, 1100, 176], "CPU (driver)", tags=["lane", "lane-cpu"], label_size=22)
d.node("cmd.chan", "frame", [40, 214, 1100, 360], "um canal", tags=["channel"], label_size=22,
       claims=[CHAN], provenance="confirmed",
       note="Cada canal tem um número fixo de entradas de GPFIFO (segundo o driver oficial).")
d.node("cmd.lane.gpu", "lane", [40, 588, 1100, 176], "GPU", tags=["lane", "lane-gpu"], label_size=22)

# ---------------- passos do driver ----------------
STEPS = [("s1", "1. grava os comandos", "no pushbuffer", ["pushbuffer"]),
         ("s2", "2. reserva uma entrada", "da GPFIFO do canal", ["gpfifo"]),
         ("s3", "3. avança o ponteiro PUT", "write_gpu_put", ["gpfifo"])]
srect = grid(210, 64, 910, 100, 3, 1, 20)
for (key, lab, sub, tg), r in zip(STEPS, srect):
    d.node(f"cmd.{key}", "step", r, lab, sub, parent="cmd.lane.cpu", tags=["step", "submit"] + tg,
           claims=[SUBMIT], provenance="confirmed", label_size=22)

# ---------------- pushbuffer ----------------
PB = [80, 280, 330, 260]
d.node("cmd.pushbuffer", "memory", PB, "pushbuffer", parent="cmd.chan", tags=["pushbuffer"],
       claims=[SUBMIT], provenance="confirmed", label_size=22)
for i, r in enumerate(grid(PB[0] + 16, PB[1] + 50, PB[2] - 32, PB[3] - 66, 1, 5, 8)):
    d.node(f"cmd.pushbuffer.cmd{i}", "codeline", r, "comando", parent="cmd.pushbuffer",
           tags=["pushbuffer", "pb-entry"], label_size=16, note="Conteúdo dos comandos: ilustrativo.")

# ---------------- GPFIFO em anel ----------------
N, CX, CY, R = 8, 770, 394, 118
EW, EH = 74, 44
GET_I, PUT_I = 5, 1          # de GET até PUT - 1 (dando a volta) estão na fila (ilustrativo)
LAST = (PUT_I - 1) % N
d.node("cmd.ring", "frame", [CX - 200, CY - 170, 400, 340], "GPFIFO (anel)", parent="cmd.chan",
       tags=["gpfifo"], claims=[RING], provenance="confirmed", label_size=20)
cells = []
for i in range(N):
    a = -math.pi / 2 + 2 * math.pi * i / N
    x, y = CX + R * math.cos(a) - EW / 2, CY + R * math.sin(a) - EH / 2
    queued = (i - GET_I) % N < (PUT_I - GET_I) % N
    d.node(f"cmd.ring.e{i}", "step" if queued else "cell", [x, y, EW, EH], parent="cmd.ring",
           tags=["gpfifo", "gpfifo-entry", "queued" if queued else "free"], claims=[RING],
           note="Entrada com trabalho a consumir (ilustrativo)." if queued else None)
    cells.append((x, y, a))
d.node("cmd.ring.center", "header", [CX - 70, CY - 22, 140, 44], "GPFIFO", parent="cmd.ring",
       tags=["gpfifo"], label_size=22)
for name, idx in (("get", GET_I), ("put", PUT_I)):
    x, y, a = cells[idx]
    px, py = CX + (R + 74) * math.cos(a) - 36, CY + (R + 70) * math.sin(a) - 18
    d.node(f"cmd.ptr.{name}", "field", [px, py, 72, 36], name.upper(), parent="cmd.ring", mono=True,
           tags=["gpfifo", f"ptr-{name}", "pointer"], claims=[RING], provenance="confirmed", label_size=20)
    d.flow(f"cmd.flow.ptr_{name}", f"cmd.ptr.{name}", f"cmd.ring.e{idx}", path="control",
           provenance="illustrative")

# ---------------- a GPU consome ----------------
d.node("cmd.s4", "step", [460, 628, 620, 100], "4. a GPU consome a fila do canal", parent="cmd.lane.gpu",
       tags=["step", "gpfifo", "channel"], claims=[RING, CHAN], provenance="confirmed", label_size=24)

s1, s2, s3 = srect
d.flow("cmd.flow.s1_pb", "cmd.s1", "cmd.pushbuffer", path="data", provenance="confirmed", claim=SUBMIT,
       points=[(s1[0] + 120, s1[1] + s1[3]), (s1[0] + 120, PB[1])])
e = cells[LAST]
d.flow("cmd.flow.s2_entry", "cmd.s2", f"cmd.ring.e{LAST}", path="control", provenance="confirmed",
       claim=SUBMIT, points=[(e[0] + EW / 2, s2[1] + s2[3]), (e[0] + EW / 2, e[1])])
p = d.get("cmd.ptr.put")["rect"]
d.flow("cmd.flow.s3_put", "cmd.s3", "cmd.ptr.put", path="control", provenance="confirmed", claim=SUBMIT,
       points=[(s3[0] + 150, s3[1] + s3[3]), (s3[0] + 150, p[1] + p[3] / 2), (p[0] + p[2], p[1] + p[3] / 2)])
g = d.get("cmd.ptr.get")["rect"]
d.flow("cmd.flow.get_gpu", "cmd.ptr.get", "cmd.s4", path="data", provenance="confirmed", claim=RING,
       points=[(g[0] + g[2] / 2, g[1] + g[3]), (g[0] + g[2] / 2, 628)])

# ---------------- ao lado ----------------
PX, PW = 1170, 390
d.node("cmd.channels", "frame", [PX, 24, PW, 250], "canais: filas de execução independentes",
       tags=["channel"], claims=[CHAN], provenance="confirmed", label_size=16)
for i, r in enumerate(grid(PX + 16, 66, PW - 32, 190, 2, 2, 10)):
    d.node(f"cmd.channels.c{i}", "block", r, "canal" if i < 3 else "…", parent="cmd.channels",
           tags=["channel"], label_size=20, note="Quantidade de canais: ilustrativa.")
d.node("cmd.note.user", "note", [PX, 290, PW, 120], "descrito para os canais do driver",
       "CUDA: parte fechada do driver", tags=["note", "user-path"],
       claims=["cmd.user_path"], provenance="derived", label_size=20,
       note="Descrito para os canais do próprio driver; o caminho de um programa CUDA passa pela parte "
            "fechada do driver. Supor o mesmo esquema de canal e GPFIFO é leitura nossa.")
d.node("cmd.note.driver", "note", [PX, 426, PW, 80], "segundo o driver oficial", "uvm_channel.c, uvm_pushbuffer.h",
       tags=["note", "driver"], label_size=20)

if __name__ == "__main__":
    d.write(__file__)
