#!/usr/bin/env python3
"""chip.isa (nível 4): o SAXPY do artigo em CUDA C, PTX e SASS (sm_120), lado a lado.

O código é lido dos arquivos de harness/examples/saxpy-cu/ (nada digitado à mão).
Os fluxos PTX -> SASS são só as correspondências da Tabela 3 do artigo, conferidas
na reprodução (README do exemplo). A palavra de 128 bits é a da FFMA, lida do .sass;
os campos internos são os descritos para a Volta (derived), sem posição de bit.
"""
import re

from _kit import EXAMPLES, Diagram, br, gap, row, val

SRC = EXAMPLES / "saxpy-cu"
NBSP = " "

# ---------------- leitura dos três arquivos ----------------
cuda = [ln.rstrip() for ln in (SRC / "saxpy.cu").read_text(encoding="utf-8").splitlines() if ln.strip()]


def ptx_instructions(text):
    body = text.split("{", 1)[1].rsplit("}", 1)[0]
    out = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s or s.startswith((".", "//")) or s.endswith(":"):
            continue
        out.append(re.sub(r"\s+", " ", s))
    return out


def ptx_mnemonic(ins):
    toks = ins.split()
    return (toks[1] if toks[0].startswith("@") else toks[0]).split(".")[0].rstrip(";")


ptx = ptx_instructions((SRC / "saxpy.ptx").read_text(encoding="utf-8"))

SASS_RE = re.compile(r"/\*([0-9a-f]{4})\*/\s+(.*?)\s*;?\s*/\* (0x[0-9a-f]{16}) \*/\s*\n\s*/\* (0x[0-9a-f]{16}) \*/")
sass, n_nop = [], 0
for addr, ins, w0, w1 in SASS_RE.findall((SRC / "saxpy.sm_120.sass").read_text(encoding="utf-8")):
    ins = re.sub(r"\s+", " ", ins.strip().rstrip(";").strip())
    if ins == "NOP":
        n_nop += 1
        continue
    sass.append({"addr": addr, "ins": ins, "words": (w0, w1)})

assert len(ptx) == val("ex.saxpy.ptx_instructions"), f"PTX com {len(ptx)} instruções"
last_exit = max(i for i, s in enumerate(sass) if s["ins"] == "EXIT")
assert last_exit + 1 == val("ex.saxpy.sass_useful"), "SASS útil não confere com o spec"
assert sass[0]["addr"] == "0000" and sass[-1]["addr"] == "0130" and len(sass) == 20

# ---------------- diagrama ----------------
d = Diagram(
    "chip.isa", "isa", 4, "SAXPY em CUDA C, PTX e SASS (sm_120)",
    "Código real do exemplo do artigo, compilado para sm_120. A posição das linhas é ilustrativa; "
    "os campos da palavra de 128 bits são os descritos para a Volta.",
)

LH, LS, Y0 = 32, 34, 78
COL = {"cuda": (30, 530), "ptx": (600, 390), "sass": (1080, 490)}
heads = {"cuda": "CUDA C", "ptx": "PTX (máquina virtual)", "sass": f"SASS ({val('isa.target')})"}
for k, (x, w) in COL.items():
    d.node(f"isa.head.{k}", "header", [x, 26, w, 42], heads[k], tags=["header", k],
           claims=["isa.target"] if k == "sass" else (), provenance="confirmed" if k == "sass" else None)

# CUDA C: as 6 linhas; a assinatura longa quebra em rótulo + sublinha
y = Y0
for i, ln in enumerate(cuda):
    ind = len(ln) - len(ln.lstrip(" "))
    text = NBSP * ind + ln.strip()
    if len(text) > 44 and "(" in text:
        head, tail = text.split("(", 1)
        lab, sub, h = head + "(", NBSP * 4 + tail, LH * 2 + 2
    else:
        lab, sub, h = text, None, LH
    d.node(f"isa.cuda.{i}", "codeline", [COL["cuda"][0], y, COL["cuda"][1], h], lab, sub,
           mono=True, align="left", tags=["code", "cuda", f"cuda-{i}"], provenance="confirmed",
           label_size=18 if sub else None)
    y += h + (LS - LH)

for i, ins in enumerate(ptx):
    d.node(f"isa.ptx.{i}", "codeline", [COL["ptx"][0], Y0 + i * LS, COL["ptx"][1], LH], ins,
           mono=True, align="left", tags=["code", "ptx", f"ptx-{i}", "op-" + ptx_mnemonic(ins)],
           provenance="confirmed")

NO_PAIR = {"0000", "0090"}   # LDC R1 e LDCU.64 UR4: sem par no código-fonte (README do exemplo)
sass_id = {}
for i, s in enumerate(sass):
    ins = s["ins"]
    tags = ["code", "sass", f"sass-{i}", f"addr-{s['addr']}"]
    mn = ins.split()[1] if ins.startswith("@") else ins.split()[0]
    tags.append("op-" + mn.split(".")[0].lower())
    if re.search(r"(?<![A-Z_])R\d+", ins):
        tags.append("reg-r")
    if re.search(r"\bUR\d+", ins):
        tags.append("reg-ur")
    if re.search(r"(?<![A-Z_])P(\d|T)\b", ins):
        tags.append("reg-p")
    if "SR_" in ins:
        tags.append("reg-sr")
    if mn.startswith(("LDG", "STG")):
        tags.append("mem")
    if mn.startswith(("LDC", "LDCU")):
        tags.append("const")
    tags.append("useful" if i <= last_exit else "after-exit")
    if s["addr"] in NO_PAIR:
        tags.append("no-pair")
    nid = f"isa.sass.{i}"
    sass_id[s["addr"]] = nid
    d.node(nid, "codeline", [COL["sass"][0], Y0 + i * LS, COL["sass"][1], LH],
           f"{s['addr']}{NBSP * 2}{ins} ;", mono=True, align="left", tags=tags, provenance="confirmed",
           note="Sem par no código-fonte; função não documentada (README do exemplo)." if s["addr"] in NO_PAIR else None)

# ---------------- correspondências da Tabela 3 ----------------
TABLE3 = [  # (regex na linha PTX, regex na linha SASS)
    (r"^ld\.param\.b32 %r\d+, \[saxpy_param_0\]", r"^LDCU UR5, c\[0x0\]\[0x380\]$"),
    (r"^ld\.param\.b32 %r\d+, \[saxpy_param_1\]", r"^LDCU UR6, c\[0x0\]\[0x384\]$"),
    (r"^ld\.param\.b64 %rd\d+, \[saxpy_param_2\]", r"^LDC\.64 R2, c\[0x0\]\[0x388\]$"),
    (r"^ld\.param\.b64 %rd\d+, \[saxpy_param_3\]", r"^LDC\.64 R4, c\[0x0\]\[0x390\]$"),
    (r"^mov\.u32 %r\d+, %ctaid\.x", r"^S2UR "),
    (r"^mad\.lo\.s32 ", r"^IMAD R"),
    (r"^setp\.ge\.s32 ", r"^ISETP\.GE"),
    (r"^@%p\d+ bra ", r"^@P0 EXIT$"),
    (r"^ld\.global\.b32 %r\d+, \[%rd6\]", r"^LDG\.E R2,"),
    (r"^ld\.global\.b32 %r\d+, \[%rd7\]", r"^LDG\.E R7,"),
    (r"^fma\.rn\.f32 ", r"^FFMA "),
    (r"^st\.global\.b32 ", r"^STG\.E "),
]


def only(pat, items, key=lambda v: v):
    hits = [i for i, v in enumerate(items) if re.search(pat, key(v))]
    assert len(hits) == 1, f"{pat}: {len(hits)} linhas"
    return hits[0]


PX1, SX0 = COL["ptx"][0] + COL["ptx"][1], COL["sass"][0]
# Correspondências além da Tabela 3, lidas da própria listagem (derived): %tid.x vira S2R, e o
# endereço (mul.wide + add.s64) vira as duas IMAD.WIDE. Ids isa.map.12 em diante.
EXTRA = [
    (r"^mov\.u32 %r\d+, %tid\.x", r"^S2R R0, SR_TID\.X$"),
    (r"^mul\.wide\.s32 ", r"^IMAD\.WIDE R2,"),
    (r"^mul\.wide\.s32 ", r"^IMAD\.WIDE R4,"),
    (r"^add\.s64 %rd6,", r"^IMAD\.WIDE R2,"),
    (r"^add\.s64 %rd7,", r"^IMAD\.WIDE R4,"),
    (r"^mov\.u32 %r\d+, %ntid\.x", r"^LDC R7, c\[0x0\]\[0x360\]$"),   # blockDim.x (README do exemplo)
]
for k, (pp, sp) in enumerate(TABLE3 + EXTRA):
    pi = only(pp, ptx)
    si = only(sp, sass, key=lambda s: s["ins"])
    for nid in (f"isa.ptx.{pi}", f"isa.sass.{si}"):
        tags = d.get(nid)["tags"]
        if "mapped" not in tags:
            tags.append("mapped")
        if k >= len(TABLE3) and "map-extra" not in tags:
            tags.append("map-extra")
    d.flow(f"isa.map.{k}", f"isa.ptx.{pi}", f"isa.sass.{si}", path="data", provenance="derived",
           points=[(PX1, Y0 + pi * LS + LH / 2), (SX0, Y0 + si * LS + LH / 2)])

# ---------------- contadores ----------------
cy = 330
c = row(30, cy, 530, 68, 3, 10)
d.node("isa.count.ptx", "counter", c[0], f"{val('ex.saxpy.ptx_instructions')} instruções", "PTX",
       tags=["counter", "ptx"], count="ex.saxpy.ptx_instructions")
d.node("isa.count.sass", "counter", c[1], f"{val('ex.saxpy.sass_useful')} úteis", "SASS, até o EXIT",
       tags=["counter", "sass"], count="ex.saxpy.sass_useful",
       note=f"A listagem tem {val('ex.saxpy.sass_instructions')} instruções: depois da BRA vêm NOPs, omitidos aqui.")
d.node("isa.count.regs", "counter", c[2], f"{val('ex.saxpy.registers')} registradores", "por thread",
       tags=["counter", "reg-r", "regs"], count="ex.saxpy.registers",
       claims=["ex.saxpy.spill_bytes"], note="'Used 10 registers' do ptxas -v; 0 bytes de spill.")
# limite de registradores (beat a5.8)
lim = row(30, cy + 74, 530, 54, 2, 10)
d.node("isa.count.reg_max_thread", "counter", lim[0], f"até {val('sm.max_regs_per_thread')}", "registradores por thread (limite)",
       tags=["counter", "reg-limit", "regs"], count="sm.max_regs_per_thread", label_size=20)
d.node("isa.count.reg_sm", "counter", lim[1], f"{br(val('sm.regfile_entries'))}", "registradores por SM",
       tags=["counter", "reg-limit", "regs"], count="sm.regfile_entries", label_size=20)

# ---------------- a palavra de 128 bits (FFMA) ----------------
fi = only(r"^FFMA ", sass, key=lambda s: s["ins"])
ffma = sass[fi]
d.get(f"isa.sass.{fi}")["tags"].append("ffma")
wy = 470
d.node("isa.word.ins", "header", [30, wy, 530, 40], ffma["ins"] + " ;", mono=True,
       tags=["word", "ffma"], provenance="confirmed")
halves = row(30, wy + 46, 530, 64, 2, 8)
for j, hr in enumerate(halves):
    d.node(f"isa.word.w{j}", "field", hr, ffma["words"][j], f"{j + 1}ª palavra de 64 bits", mono=True,
           tags=["word", "ffma", "word-hex"], provenance="confirmed",
           note=f"Lida de saxpy.sm_120.sass, endereço 0x{ffma['addr']}.")
d.node("isa.word.bytes", "counter", [30, wy + 116, 530, 46],
       f"{val('isa.instruction_bytes')} bytes = 128 bits por instrução",
       tags=["word", "counter", "word-size"], count="isa.instruction_bytes")

VOLTA_NOTE = "Campo descrito para a Volta (Jia et al., 2018); sem posição de bit exata em sm_120."
# linha 1: as três partes que somam 128 bits (larguras não proporcionais: são mínimos, sem posição)
FIELDS = [
    ("instr", "instrução", f"≥ {val('isa.volta.instruction_bits_min')} bits", "isa.volta.instruction_bits_min", 300),
    ("control", "controle", f"≥ {val('isa.volta.control_bits_min')} bits", "isa.volta.control_bits_min", 120),
    ("unused", "sem uso", f"{val('isa.volta.unused_bits')} bits", "isa.volta.unused_bits", 98),
]
fy = wy + 170
x = 30
for fid, name, size, claim, w in FIELDS:
    d.node(f"isa.field.{fid}", "field", [x, fy, w, 54], name, size,
           tags=["word", "volta-field", f"field-{fid}", "field-row-1"], count=claim, provenance="derived",
           label_size=20,
           note=VOLTA_NOTE)
    x += w + 6
assert abs(x - 6 - 560) < 1e-6
# linha 2: o que fica dentro dos bits de instrução, aninhado sob a caixa "instrução"
iy = fy + 56
d.node("isa.field.inside", "frame", [30, iy, 300, 108], "dentro da instrução",
       tags=["word", "volta-field", "field-inside"], label_size=16, provenance="derived",
       claims=["isa.volta.instruction_bits_min"], note=VOLTA_NOTE)
inner = row(38, iy + 30, 284, 70, 2, 8)
d.node("isa.field.opcode", "field", inner[0], "opcode", f"{val('isa.volta.opcode_bits')} bits",
       parent="isa.field.inside", tags=["word", "volta-field", "field-opcode", "field-row-2"],
       claims=["isa.volta.opcode_bits"], provenance="derived",
       note=VOLTA_NOTE + " Nos bits menos significativos da primeira metade de 64 bits.")
d.node("isa.field.pred", "field", inner[1], "predicado", f"{val('isa.volta.predicate_bits')} bits",
       parent="isa.field.inside", tags=["word", "volta-field", "field-pred", "field-row-2"],
       count="isa.volta.predicate_bits", provenance="derived", note=VOLTA_NOTE)
d.node("isa.gap.control", "gap", [340, iy, 220, 108], "Bits de controle", "no sm_120: não documentados",
       tags=["gap", "word"], note=gap("isa.control_bits_blackwell")["description"])
d.node("isa.field.note", "note", [30, iy + 116, 530, 44], "campos descritos para a Volta (2018)",
       tags=["word", "volta-field", "note"], claims=["isa.volta.instruction_bits_min"], provenance="derived")
assert iy + 116 + 44 <= 888

ffma_y = Y0 + fi * LS + LH / 2
w1y = halves[1][1] + halves[1][3] / 2
d.flow("isa.flow.ffma_word", f"isa.sass.{fi}", "isa.word.w1", path="control", provenance="confirmed",
       points=[(SX0, ffma_y), (1050, ffma_y), (1050, 776), (578, 776), (578, w1y), (560, w1y)])

# 20 PTX -> 19 SASS úteis: cvta some (-2), mul.wide + 2 add.s64 viram 2 IMAD.WIDE (-1), 2 sem par (+2)
d.check("isa.count.ptx - 2 - 1 + 2", val("ex.saxpy.sass_useful"))
# listagem completa: úteis + BRA + NOPs
d.check(f"isa.count.sass + 1 + {n_nop}", val("ex.saxpy.sass_instructions"))
d.check("isa.word.bytes * 8", 128)
# linha 1 da palavra: 91 + 23 + 14 = 128 (opcode e predicado ficam dentro dos 91)
d.check("isa.field.instr + isa.field.control + isa.field.unused", 128)
d.check("isa.count.reg_sm / 4", val("sm.block_regfile_entries"))

if __name__ == "__main__":
    d.write(__file__)
