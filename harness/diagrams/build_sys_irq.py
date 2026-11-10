#!/usr/bin/env python3
"""sys.irq (nível 4): interrupções e exceções entre GPU e CPU, segundo as fontes lidas.

Três mecanismos documentados (tags mech-1, mech-2, mech-3), em faixas para GPU,
barramento PCIe e CPU (driver). Ao lado, AMP e MIG. Lacunas e a leitura do grupo
("não achamos rotina de interrupção no SM") ficam declaradas.
"""
from _kit import Diagram, gap, grid, val

d = Diagram(
    "sys.irq", "irq", 4, "Interrupções: GPU, barramento e CPU",
    "Mecanismos segundo o driver oficial, o PTX ISA e o catálogo de Xid; faixas, caixas e "
    "posições ilustrativas. A preempção vem da Pascal.",
)

# ---------------- faixas ----------------
LX, LW = 40, 1140
LANES = [("gpu", "GPU", 24, 320), ("bus", "PCIe", 354, 70), ("cpu", "CPU (driver)", 434, 290)]
for key, name, y, h in LANES:
    d.node(f"irq.lane.{key}", "lane", [LX, y, LW, h], name, tags=["lane", f"lane-{key}"], label_size=22)

C1, C2, C3 = (210, 290), (520, 260), (800, 340)   # colunas dos mecanismos (x, largura)
for (x, w), n, title in [(C1, 1, "1 · a GPU interrompe a CPU"), (C2, 2, "2 · o programa aborta"),
                         (C3, 3, "3 · falha de página e preempção")]:
    d.node(f"irq.mech{n}.head", "header", [x, 32, w, 40], title, parent="irq.lane.gpu",
           tags=[f"mech-{n}", "header"])

# ---------------- mecanismo 1 ----------------
x, w = C1
d.node("irq.m1.s1", "step", [x, 82, w, 80], "1. evento na GPU", "pedido de interrupção", parent="irq.lane.gpu",
       label_size=20,
       tags=["mech-1", "step"], provenance="confirmed", claims=["irq.modes"])
d.node("irq.m1.s2", "step", [x, 362, w, 54], "2. MSI-X, MSI ou linha legada", parent="irq.lane.bus",
       tags=["mech-1", "step", "msi"], claims=["irq.modes"], provenance="confirmed",
       note=val("irq.modes") + ". " + gap("irq.exit_path")["description"])
d.node("irq.m1.s3", "step", [x, 446, w, 110], "3. metade de cima",
       f"{val('irq.top_half')} → rm_isr", label_size=20, parent="irq.lane.cpu", tags=["mech-1", "step", "top-half"],
       claims=["irq.top_half"], provenance="confirmed",
       note="Roda no contexto da interrupção e faz o mínimo (nv.c).")
d.node("irq.m1.s4", "step", [x, 576, w, 84], "4. metade de baixo",
       f"{val('irq.bottom_half')} → rm_isr_bh", label_size=20, parent="irq.lane.cpu", tags=["mech-1", "step", "bottom-half"],
       claims=["irq.bottom_half"], provenance="confirmed",
       note="Registrada com request_threaded_irq (nv.c).")
d.node("irq.m1.kthread", "note", [x, 668, w, 44], "roda em thread do kernel", parent="irq.lane.cpu",
       tags=["mech-1", "bottom-half"], claims=["irq.bottom_half"], provenance="confirmed")
cx = x + w / 2
d.flow("irq.flow.m1_12", "irq.m1.s1", "irq.m1.s2", path="control", provenance="derived",
       points=[(cx, 162), (cx, 362)])
d.flow("irq.flow.m1_23", "irq.m1.s2", "irq.m1.s3", path="control", provenance="confirmed",
       points=[(cx, 416), (cx, 446)], claim="irq.top_half")
d.flow("irq.flow.m1_34", "irq.m1.s3", "irq.m1.s4", path="control", provenance="confirmed",
       points=[(cx, 556), (cx, 576)], claim="irq.bottom_half")

# ---------------- mecanismo 2 ----------------
x, w = C2
d.node("irq.m2.trap", "step", [x, 82, w, 56], "trap", "instrução PTX", parent="irq.lane.gpu", mono=True,
       tags=["mech-2", "step", "trap"], claims=["irq.ptx_trap", "isa.op.bpt"], provenance="confirmed",
       note="No SASS da Blackwell existe BPT, 'BreakPoint/Trap' (Binary Utilities 13.5).")
words = val("irq.ptx_trap").split()
half = min(range(1, len(words)), key=lambda k: max(len(" ".join(words[:k])), len(" ".join(words[k:]))))
d.node("irq.m2.quote", "note", [x, 146, w, 110], "“" + " ".join(words[:half]),
       " ".join(words[half:]) + "”", parent="irq.lane.gpu", label_size=16, tags=["mech-2", "trap", "quote"],
       claims=["irq.ptx_trap"], provenance="confirmed", note="PTX ISA 9.5, 9.7.21.4.")
d.node("irq.m2.host", "step", [x, 446, w, 60], "interrupção na CPU", parent="irq.lane.cpu", label_size=20,
       tags=["mech-2", "step"], claims=["irq.ptx_trap"], provenance="confirmed")
cx = x + w / 2
d.flow("irq.flow.m2_trap", "irq.m2.quote", "irq.m2.host", path="control", provenance="confirmed",
       points=[(cx, 256), (cx, 446)], claim="irq.ptx_trap")

# ---------------- mecanismo 3 ----------------
x, w = C3
FAULT = "fault.replayable_blocks_preemption"
DRV = "Segundo o driver oficial (UVM)."
STEPS = [  # id, rótulo, sublinha, y, altura, fatos
    ("fault", "1. falha de página no acesso", None, 82, 40, [FAULT]),
    ("buffer", "2. a falha vai para o buffer", None, 128, 40, ["fault.buffer_batch"]),
    ("stall", "3. o canal não pode ser trocado", "os outros esperam (fault and stall)", 174, 60, ["fault.stall", FAULT]),
    ("replay", "5. a GPU repete o acesso", None, 240, 40, ["fault.replay"]),
]
for key, text, sub, y, h, cl in STEPS:
    d.node(f"irq.m3.{key}", "step", [x, y, w, h], text, sub, parent="irq.lane.gpu", label_size=20,
           tags=["mech-3", "step", "fault"], claims=cl, provenance="confirmed", align="left",
           note=DRV + " " + "; ".join(str(val(c)) for c in cl if isinstance(val(c), str)))
ry = {k: (y, h) for k, _, _, y, h, _ in STEPS}
d.node("irq.m3.preempt", "step", [x, 286, w, 54], "preempção no nível de instrução", "Pascal; Blackwell sem fonte",
       parent="irq.lane.gpu", label_size=18, tags=["mech-3", "preemption"], claims=["sched.preemption_instruction_level"],
       provenance="derived", note=gap("sched.preemption_blackwell")["description"])
d.node("irq.m3.batch", "step", [x, 446, w, 80], "4. o driver resolve um lote", "e manda a GPU repetir",
       label_size=20,
       parent="irq.lane.cpu", tags=["mech-3", "step", "fault"], claims=["fault.buffer_batch", "fault.replay"],
       provenance="confirmed", note=DRV)
d.node("irq.m3.xid31", "cell", [x, 540, w, 94], "Xid 31", val("irq.xid31"), parent="irq.lane.cpu",
       tags=["mech-3", "xid", "fault"], claims=["irq.xid31"], provenance="confirmed",
       note="Catálogo de Xid: registrado quando a MMU reporta uma falha, como acesso a endereço ilegal; "
            "catálogo geral, não cita a Blackwell.")
for a, b, cl in [("fault", "buffer", "fault.buffer_batch"), ("buffer", "stall", "fault.stall")]:
    y0 = ry[a][0] + ry[a][1]
    d.flow(f"irq.flow.m3_{a}_{b}", f"irq.m3.{a}", f"irq.m3.{b}", path="control", provenance="confirmed",
           points=[(x + 40, y0), (x + 40, ry[b][0])], claim=cl)
RX = x + w + 20
sy = ry["stall"][0] + ry["stall"][1] / 2
d.flow("irq.flow.m3_stall_cpu", "irq.m3.stall", "irq.m3.batch", path="control", provenance="confirmed",
       points=[(x + w, sy), (RX, sy), (RX, 486), (x + w, 486)], claim="fault.buffer_batch")
rpy = ry["replay"][0] + ry["replay"][1] / 2
d.flow("irq.flow.m3_replay", "irq.m3.batch", "irq.m3.replay", path="control", provenance="confirmed",
       points=[(x, 486), (x - 10, 486), (x - 10, rpy), (x, rpy)], claim="fault.replay")

# ---------------- ao lado: AMP e MIG ----------------
PX, PW = 1200, 370
d.node("irq.amp", "actor", [PX, 24, PW, 130], f"AMP ({val('chip.amp_isa')})", "escalonador de contextos",
       tags=["amp", "sched"], claims=["sched.amp", "chip.amp_isa"], provenance="confirmed",
       note=val("sched.amp") + " (whitepaper, p. 25).")
n_mig = val("sched.mig_instances")
d.node("irq.mig", "frame", [PX, 170, PW, 290], f"MIG: até {n_mig} instâncias", tags=["mig"],
       count="sched.mig_instances", label_size=24)
for i, r in enumerate(grid(PX + 14, 214, PW - 28, 232, 2, n_mig // 2, 10)):
    d.node(f"irq.mig.{i}", "block", r, f"instância {i + 1}", parent="irq.mig", tags=["mig", f"mig-{i}"])
d.node("irq.note.driver", "note", [PX, 476, PW, 86], "segundo o driver oficial", "nv.c, nv-msi.c, UVM",
       tags=["note", "driver"], note="Código de driver mostra o que o software programa, não o circuito.")

# ---------------- como o erro aparece no log (fora dos três mecanismos) ----------------
d.node("irq.xidlog", "frame", [PX, 576, PW, 148], "como o erro aparece no log do driver",
       tags=["xid-log"], label_size=16, claims=["irq.xid13"],
       note="Nenhuma fonte liga o trap a um código Xid específico.")
d.node("irq.xid13", "cell", [PX + 14, 608, PW - 28, 102], "Xid 13", val("irq.xid13"), parent="irq.xidlog",
       tags=["xid-log", "xid"], claims=["irq.xid13"], provenance="confirmed",
       note="Catálogo de Xid: falhas gerais de aplicação do usuário; catálogo geral, não cita a Blackwell.")

# ---------------- lacunas e leitura do grupo ----------------
d.node("irq.gap.cmd", "gap", [40, 740, 1530, 60], "Como a CPU envia comandos à GPU: ainda não lido",
       tags=["gap", "command-submission"], note=gap("cpu.command_submission")["description"])
d.node("irq.note.sm", "note", [40, 812, 1530, 64], "Não achamos rotina de interrupção executada pelo próprio SM",
       "análise do grupo", tags=["note", "sm-level", "inferred"], provenance="inferred",
       note=gap("irq.sm_level")["description"])

if __name__ == "__main__":
    d.write(__file__)
