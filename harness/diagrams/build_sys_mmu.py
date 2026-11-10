#!/usr/bin/env python3
"""sys.mmu (nível 4): tradução de endereço virtual de 57 bits em 6 níveis, segundo o driver oficial.

Os campos saem de mmu.va_bits, mmu.index_bits e mmu.page_sizes. Para cada tamanho de
página, bits de índice = 57 - log2(página); a conta confere com a soma dos campos.
A página de 2 MB termina no PDE0 e a de 512 MB no PDE1 (consequência das contas).
"""
import math
import re

from _kit import Diagram, center, gap, row, val

VA = val("mmu.va_bits")                                            # 57
DIR_BITS = [int(b) for b in re.findall(r"\d+", val("mmu.index_bits"))]   # 1, 9, 9, 9, 8
LEVELS = ["PDE4", "PDE3", "PDE2", "PDE1", "PDE0", "PTE"]
assert len(LEVELS) == val("mmu.levels") == len(DIR_BITS) + 1

UNITS = {"KB": 10, "MB": 20, "GB": 30}
PAGES = [(f"{n} {u}", int(math.log2(int(n))) + UNITS[u])
         for n, u in re.findall(r"(\d+) (KB|MB|GB)", val("mmu.page_sizes"))]   # (rótulo, bits de deslocamento)
assert [p[0] for p in PAGES] == ["4 KB", "64 KB", "2 MB", "512 MB"], PAGES

OFF_4K = dict(PAGES)["4 KB"]                       # 12
PTE_4K = VA - sum(DIR_BITS) - OFF_4K               # 9
FIELD_BITS = DIR_BITS + [PTE_4K, OFF_4K]           # 1, 9, 9, 9, 8, 9, 12
assert sum(FIELD_BITS) == VA
# página que termina antes do PTE: quantos níveis de diretório ela usa
STOPS = {}
for name, off in PAGES:
    idx = VA - off
    acc = 0
    for k, b in enumerate(DIR_BITS):
        acc += b
        if acc == idx:
            STOPS[name] = k                        # 2 MB -> PDE0 (4), 512 MB -> PDE1 (3)
assert STOPS == {"2 MB": 4, "512 MB": 3}, STOPS

d = Diagram(
    "sys.mmu", "mmu", 4, "MMU: endereço virtual de 57 bits em 6 níveis",
    "Segundo o driver oficial (o GB202 usa o formato de MMU da Hopper). Larguras dos campos "
    "proporcionais aos bits; caixas e posições ilustrativas.",
)

d.node("mmu.head", "header", [40, 24, 980, 50], f"Endereço virtual de {VA} bits (página de 4 KB)",
       tags=["header", "va"], count="mmu.va_bits", claims=["mmu.format_family", "mmu.gb202_in_gb20x"])
d.node("mmu.count.levels", "counter", [1040, 24, 250, 50], f"{len(LEVELS)} níveis", tags=["counter", "level"],
       count="mmu.levels")
d.node("mmu.note.driver", "note", [1310, 24, 250, 50], "segundo o driver oficial", tags=["note", "driver"],
       claims=["mmu.format_family", "mmu.gb202_in_gb20x"],
       note="Código de driver mostra o que o software programa, não o circuito (uvm_hal.c, uvm_hopper_mmu.c).")

# ---------------- barra do endereço ----------------
BX, BW, BY, BH = 40, 1520, 92, 78
MIN_W = 64
per_bit = (BW - MIN_W) / (VA - 1)
widths = [MIN_W if b == 1 else b * per_bit for b in FIELD_BITS]
assert abs(sum(widths) - BW) < 1e-6
hi = VA - 1
x = BX
fields = []
for k, (b, w) in enumerate(zip(FIELD_BITS, widths)):
    lo = hi - b + 1
    rng = f"[{hi}]" if b == 1 else f"[{hi}:{lo}]"
    is_off = k == len(FIELD_BITS) - 1
    fid = "mmu.va.offset" if is_off else f"mmu.va.idx{k}"
    sub = f"{b} bits: deslocamento" if is_off else (f"{b} bit" if b == 1 else f"{b} bits")
    d.node(fid, "field", [x, BY, w, BH], rng, sub, mono=True,
           tags=["va", "field", "offset" if is_off else f"idx-{k}"],
           claims=["mmu.index_bits"] if k < len(DIR_BITS) else ["mmu.page_sizes", "mmu.va_bits"],
           provenance="confirmed" if k < len(DIR_BITS) else "derived",
           note=None if k < len(DIR_BITS) else f"{VA} - {sum(DIR_BITS)} - {OFF_4K} = {PTE_4K} bits no PTE para 4 KB"
           if not is_off else "4 KB = 2^12")
    fields.append((fid, [x, BY, w, BH]))
    x += w
    hi = lo - 1

# ---------------- níveis da tabela ----------------
LY, LH = 250, 92
lv_rects = row(40, LY, 1520, LH, len(LEVELS) + 1, 30)
for k, name in enumerate(LEVELS):
    nid = f"mmu.level.{k}"
    tags = ["level", f"level-{k}", name.lower()]
    d.node(nid, "step", lv_rects[k], name, f"nível {k + 1}", tags=tags, claims=["mmu.levels"],
           provenance="confirmed")
    fid, fr = fields[k]
    fx = fr[0] + fr[2] / 2
    lx = lv_rects[k][0] + lv_rects[k][2] / 2
    d.flow(f"mmu.flow.idx{k}", fid, nid, path="control", provenance="confirmed",
           points=[(fx, BY + BH), (fx, 208), (lx, 208), (lx, LY)])
    if k:
        a, b = lv_rects[k - 1], lv_rects[k]
        cy = a[1] + a[3] / 2
        d.flow(f"mmu.flow.walk{k}", f"mmu.level.{k - 1}", nid, path="data", provenance="illustrative",
               points=[(a[0] + a[2], cy), (b[0], cy)])
page = lv_rects[-1]
d.node("mmu.page", "memory", page, "página de 4 KB", val("mem.type"), tags=["page", "dram"], label_size=22,
       claims=["mem.type", "mmu.page_sizes"], provenance="confirmed")
a = lv_rects[len(LEVELS) - 1]
d.flow("mmu.flow.walk_page", f"mmu.level.{len(LEVELS) - 1}", "mmu.page", path="data", provenance="illustrative",
       points=[(a[0] + a[2], a[1] + a[3] / 2), (page[0], page[1] + page[3] / 2)])
ofid, ofr = fields[-1]
ox = ofr[0] + ofr[2] / 2
pcx, _ = center(page)
d.flow("mmu.flow.offset", ofid, "mmu.page", path="control", provenance="confirmed",
       points=[(ox, BY + BH), (ox, 208), (pcx, 208), (pcx, LY)])

# onde a tradução termina antes
for name, k in STOPS.items():
    tag = "stop-512m" if name == "512 MB" else "stop-2m"
    r = lv_rects[k]
    d.node(f"mmu.stop.{tag[5:]}", "note", [r[0], LY + LH + 16, r[2], 70], f"fim: {name}",
           f"{VA - dict(PAGES)[name]} + {dict(PAGES)[name]} bits", tags=[tag, "stop"],
           claims=["mmu.page_sizes", "mmu.index_bits"], provenance="derived",
           note=f"A página de {name} termina em {LEVELS[k]}, sem descer ao PTE (conta: {VA} - "
                f"{dict(PAGES)[name]} = {sum(DIR_BITS[:k + 1])} bits de índice).")
    d.flow(f"mmu.flow.{tag.replace('-', '_')}", f"mmu.level.{k}", f"mmu.stop.{tag[5:]}", path="control", provenance="derived",
           points=[(r[0] + r[2] / 2, LY + LH), (r[0] + r[2] / 2, LY + LH + 16)])

# ---------------- tamanhos de página ----------------
d.node("mmu.pages.head", "header", [40, 470, 1520, 44], "tamanho de página = bits de índice + deslocamento",
       tags=["header", "page-sizes"], claims=["mmu.page_sizes"])
for (name, off), r in zip(PAGES, row(40, 524, 1520, 96, len(PAGES), 20)):
    idx = VA - off
    key = name.replace(" ", "").lower()
    d.node(f"mmu.pages.{key}", "cell", r, name, f"{idx} + {off} = {VA} bits",
           tags=["page-sizes", f"page-{key}"] + (["stop-512m"] if name == "512 MB" else ["stop-2m"] if name == "2 MB" else []),
           claims=["mmu.page_sizes", "mmu.index_bits", "mmu.va_bits"], provenance="derived", label_size=28)
    d.check(f"{idx} + {off}", VA)

# ---------------- comparação, lacuna ----------------
d.node("mmu.pascal", "note", [40, 650, 600, 90], f"Pascal: {val('mmu.pascal.va_bits')} bits, "
       f"{val('mmu.pascal.levels')} níveis", "geração anterior, para comparar", tags=["pascal"],
       count="mmu.pascal.va_bits", claims=["mmu.pascal.levels"], provenance="derived")
d.node("mmu.gap.tlb", "gap", [660, 650, 900, 90], "TLB: tamanho, níveis e política", "não são públicos",
       tags=["gap", "tlb"], note=gap("mmu.tlb")["description"])
d.node("mmu.gap.per_process", "gap", [40, 760, 1520, 90], "Espaço de endereços por programa",
       "nenhuma fonte descreve", tags=["gap"], note=gap("mmu.address_space_per_program")["description"])

if __name__ == "__main__":
    d.write(__file__)
