#!/usr/bin/env python3
"""chip.risc (nível 4): RISC ou CISC? A tabela de critérios da seção 08 do roteiro.

Linhas: critério, o que as fontes mostram (curto), para que lado aponta. Ao lado,
LDGSTS, TEX e HMMA com a descrição oficial em inglês (spec). A conclusão é análise
do grupo (inferred), aprovada pelo humano em 2026-11-10.
"""
import re

from _kit import EXAMPLES, Diagram, br, row, val

d = Diagram(
    "chip.risc", "risc", 4, "RISC ou CISC? Critérios para o SASS (sm_120)",
    "Análise do grupo sobre fatos oficiais: a NVIDIA não classifica o SASS. A coluna "
    "'Aponta para' e a conclusão são inferência; a disposição é ilustrativa.",
)

TX, TW = 30, 1100
COLW = [300, 540, 244]
GAP = 8
cols_x = [TX, TX + COLW[0] + GAP, TX + COLW[0] + COLW[1] + 2 * GAP]
for i, (name, key) in enumerate([("Critério", "criterion"), ("O que as fontes mostram", "evidence"),
                                 ("Aponta para", "verdict")]):
    d.node(f"risc.head.{key}", "header", [cols_x[i], 30, COLW[i], 50], name, tags=["header", f"col-{key}"])

RISC, AWAY, NEUTRAL = "lean-risc", "lean-away", "lean-neutral"
ROWS = [
    # critério, evidência, kw da evidência, veredito, inclinação
    ("Largura da instrução", f"{val('isa.instruction_bytes')} bytes em todas as instruções",
     dict(count="isa.instruction_bytes"), "RISC", RISC),
    ("Acesso à memória", "carga e armazenamento, exceto LDGSTS e UTMALDG",
     dict(claims=["isa.ptx_load_store", "isa.op.ldgsts", "isa.op.utmaldg"], provenance="confirmed"),
     "RISC, com exceções", RISC),
    ("Modos de endereçamento", "descritor, banco de constantes, imediato",
     dict(note="Visto na listagem do SAXPY (desc[UR4][R2.64], c[0x0][...], 0x4); lista completa não levantada."),
     "não determinado", NEUTRAL),
    ("Registradores", f"{br(val('sm.regfile_entries'))} por SM; até {val('sm.max_regs_per_thread')} por thread",
     dict(count="sm.regfile_entries", claims=["sm.max_regs_per_thread"]), "RISC", RISC),
    ("Trabalho por instrução", "HMMA: bloco de matriz por warp; TEX",
     dict(claims=["ex.mma.hmma", "isa.op.hmma", "isa.op.tex"], provenance="confirmed"),
     "afasta do RISC clássico", AWAY),
    ("Tamanho do conjunto", f"{val('isa.sass_mnemonics')} mnemônicos em {val('isa.sass_categories')} categorias",
     dict(count="isa.sass_mnemonics", claims=["isa.sass_categories"], provenance="derived"), "neutro", NEUTRAL),
    ("Escalonamento no binário", f"≥ {val('isa.volta.control_bits_min')} bits de controle (Volta)",
     dict(count="isa.volta.control_bits_min", provenance="derived"), "lembra VLIW", AWAY),
    ("Microcódigo", "nenhuma informação pública", dict(), "não determinado", NEUTRAL),
]
RH, RS, RY = 70, 78, 90
for i, (crit, ev, kw, verdict, lean) in enumerate(ROWS, start=1):
    y = RY + (i - 1) * RS
    rt = [f"row-{i}"]
    d.node(f"risc.row.{i}.crit", "cell", [cols_x[0], y, COLW[0], RH], crit, tags=rt + ["col-criterion"],
           align="left", label_size=21)
    d.node(f"risc.row.{i}.ev", "gap" if crit == "Microcódigo" else "cell", [cols_x[1], y, COLW[1], RH], ev,
           tags=rt + ["col-evidence"], align="left", label_size=19, **kw)
    d.node(f"risc.row.{i}.verdict", "cell", [cols_x[2], y, COLW[2], RH], verdict,
           tags=rt + ["col-verdict", lean], provenance="inferred", label_size=18)

cy = RY + len(ROWS) * RS + 10
d.node("risc.conclusion", "note", [TX, cy, TW, 116], "RISC no formato, com instruções próprias de acelerador",
       "análise do grupo; a NVIDIA não classifica o SASS", tags=["conclusion"], provenance="inferred",
       claims=["isa.instruction_bytes", "isa.ptx_load_store", "isa.op.ldgsts", "isa.op.tex", "isa.op.hmma"],
       note="Seção 08 do roteiro, conclusão aprovada pelo humano em 2026-11-10. Fora da dicotomia: "
            "o compilador grava controle de escalonamento na instrução, o que lembra VLIW.")

# instruções de acelerador, com a descrição oficial
PX, PW = 1160, 410
d.node("risc.ops.head", "header", [PX, 30, PW, 50], "Instruções de acelerador", tags=["header", "ops"])
OPS = [("LDGSTS", "isa.op.ldgsts", "op-ldgsts"), ("TEX", "isa.op.tex", "op-tex"),
       ("HMMA", "isa.op.hmma", "op-hmma")]
for (name, claim, tag), r in zip(OPS, [[PX, 90 + k * 142, PW, 130] for k in range(3)]):
    d.node(f"risc.op.{name.lower()}", "codeline", r, name, f"“{val(claim)}”", mono=True,
           tags=["ops", tag], claims=[claim] + (["ex.mma.hmma"] if name == "HMMA" else []),
           provenance="confirmed", label_size=30,
           note="Descrição oficial: CUDA Binary Utilities 13.5, 'Blackwell and Rubin Instruction Set'.")
# par PTX -> SASS da HMMA (beat a5.11), lido de harness/examples/mma/
MMA = EXAMPLES / "mma"
hmma = val("ex.mma.hmma")
ptx_mma = [ln.strip() for ln in (MMA / "mma.ptx").read_text(encoding="utf-8").splitlines()
           if ln.strip().startswith("mma.sync") and ".f16.f16." in ln]
sass_mma = [re.sub(r"\s+", " ", m.group(1)).strip() for m in
            re.finditer(r"/\*[0-9a-f]{4}\*/\s+(" + re.escape(hmma) + r" [^;]*;)", (MMA / "mma.sm_120.sass").read_text(encoding="utf-8"))]
assert len(ptx_mma) == 1 and len(sass_mma) == 1, (ptx_mma, sass_mma)
head, tail = ptx_mma[0].split(".row", 1)
d.node("risc.mma.ptx", "codeline", [PX, 516, PW, 56], head, ".row" + tail, mono=True, align="left",
       label_size=18, tags=["mma", "ptx"], provenance="confirmed",
       note="harness/examples/mma/mma.ptx, kernel mma_f16 (operandos omitidos).")
d.node("risc.mma.sass", "codeline", [PX, 578, PW, 40], sass_mma[0], mono=True, align="left",
       tags=["mma", "sass", "op-hmma"], claims=["ex.mma.hmma"], provenance="confirmed",
       note="harness/examples/mma/mma.sm_120.sass: uma instrução SASS por mma.sync.")
d.flow("risc.flow.mma", "risc.mma.ptx", "risc.mma.sass", path="data", provenance="confirmed",
       points=[(PX + PW - 20, 572), (PX + PW - 20, 578)], claim="ex.mma.hmma")
d.node("risc.amp", "note", [PX, 626, PW, 88], f"AMP: {val('chip.amp_isa')}", "um RISC por projeto, fora do SM",
       tags=["amp"], claims=["chip.amp_isa"], provenance="confirmed")
d.node("risc.gap.microcode", "gap", [PX, cy, PW, 116], "Microcódigo, modos completos", "sem fonte pública",
       tags=["gap"], note="Microcódigo: nenhuma informação pública. Modos de endereçamento: lista completa não levantada.")

if __name__ == "__main__":
    d.write(__file__)
