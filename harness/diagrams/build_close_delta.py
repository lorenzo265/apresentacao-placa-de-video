#!/usr/bin/env python3
"""close.delta (nível 4): RTX 6000 Ada contra RTX PRO 6000 Blackwell, barras pareadas.

Uma linha por grandeza; as barras são proporcionais dentro da linha (não entre linhas).
A razão Blackwell / Ada é conta nossa (derived). A banda da Ada tem conflito no próprio
whitepaper (Tab. 4 contra Tab. 1): adotamos a Tab. 4 e declaramos o conflito.
"""
from _kit import Diagram, br, val

d = Diagram(
    "close.delta", "delta", 4, "RTX 6000 Ada contra RTX PRO 6000 Blackwell Workstation Edition",
    "Valores oficiais da Workstation Edition (whitepaper, Tab. 4, e datasheet); a variante Max-Q tem 300 W. "
    "As razões são contas nossas. Barras proporcionais dentro de cada linha, não entre linhas.",
)

ROWS = [  # chave, grandeza, unidade no rótulo, fato Ada, fato Blackwell
    ("sm", "SMs", "", "ada.sm_count", "chip.sm_count"),
    ("l2", "L2", "KB", "ada.l2_kb", "chip.l2_kb"),
    ("mem", "Memória", "GB", "ada.mem_gb", "mem.capacity_gb"),
    ("tgp", "Potência", "W", "ada.tgp_w", "card.tgp_w"),
    ("bw", "Banda de memória", "GB/s", "ada.bandwidth_gbs", "mem.bandwidth_gbs"),
]
NOTES = {
    "tgp": "As duas da linha 'TGP (Total Graphics Power)' da Tab. 4. O datasheet chama os 600 W de 'Total board power'.",
    "bw": f"Ada: 960 GB/s da Tab. 4; confere com {val('ada.bus_bits')} bits × {val('ada.pin_rate_gbps')} Gbps ÷ 8. A Tab. 1 diz 1.008.",
}

# legenda
d.node("delta.head.item", "header", [40, 24, 260, 46], "grandeza", tags=["header"])
d.node("delta.legend.ada", "cell", [320, 24, 300, 46], "RTX 6000 Ada", tags=["legend", "ada"])
d.node("delta.legend.bw", "sm", [630, 24, 380, 46], "RTX PRO 6000 Blackwell", tags=["legend", "blackwell"])
d.node("delta.head.ratio", "header", [1320, 24, 240, 46], "Blackwell / Ada", tags=["header", "ratio"])

BX, BMAX, RY, RH, RS = 320, 980, 86, 124, 138
for i, (key, name, unit, fa, fb) in enumerate(ROWS):
    y = RY + i * RS
    a, b = val(fa), val(fb)
    rt = f"row-{key}"
    d.node(f"delta.{key}.name", "header", [40, y, 260, RH], name, unit or None,
           tags=[rt, "row-name"], label_size=24)
    wa, wb = BMAX * a / max(a, b), BMAX * b / max(a, b)
    u = f" {unit}" if unit else ""
    d.node(f"delta.{key}.ada", "cell", [BX, y + 6, wa, 52], f"Ada: {br(a)}{u}", tags=[rt, "ada", "bar"],
           count=fa, align="left", label_size=22, provenance="confirmed",
           claims=["ada.bus_bits", "ada.pin_rate_gbps"] if key == "bw" else (),
           note=NOTES.get(key))
    d.node(f"delta.{key}.bw", "sm", [BX, y + 66, wb, 52], f"Blackwell: {br(b)}{u}", tags=[rt, "blackwell", "bar"],
           count=fb, align="left", label_size=22, provenance="confirmed", note=NOTES.get(key) if key == "tgp" else None)
    r = b / a
    d.node(f"delta.{key}.ratio", "counter", [1320, y + 22, 240, 80], f"× {br(round(r, 2), 2)}",
           "(Tab. 4)" if key == "bw" else None, tags=[rt, "ratio"], claims=[fa, fb], provenance="derived",
           label_size=30, note=f"Conta nossa: {br(b)} / {br(a)}.")
    d.check(f"delta.{key}.bw / delta.{key}.ada", r)

b2 = val("ada.bandwidth_gbs_tab1")
d.node("delta.note.conflict", "note", [40, 786, 1520, 90],
       f"Banda da Ada: {br(val('ada.bandwidth_gbs'))} GB/s na Tab. 4 e {br(b2)} GB/s na Tab. 1",
       f"mesmo documento; adotamos a Tab. 4 (com a Tab. 1, a razão seria × {br(round(val('mem.bandwidth_gbs') / b2, 2), 2)})",
       tags=["conflict", "row-bw", "ada"], count="ada.bandwidth_gbs_tab1",
       claims=["ada.bandwidth_gbs", "mem.bandwidth_gbs"], label_size=24)

# contas inteiras que o desenho afirma
d.check("delta.mem.ada * 2", val("mem.capacity_gb"))
d.check("delta.tgp.ada * 2", val("card.tgp_w"))
d.check("delta.l2.ada * 4 / 3", val("chip.l2_kb"))

if __name__ == "__main__":
    d.write(__file__)
