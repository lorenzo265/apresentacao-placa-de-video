#!/usr/bin/env python3
"""Prévia estática dos diagramas, sem o viewer.

Uso:  python3 harness/diagrams/preview.py [--png] [id ...]

Gera harness/dist/diagram-preview/<id>.svg (retângulos, rótulos e fluxos, cores
neutras por kind; os diagramas embutidos aparecem dentro do nó hospedeiro). Com
--png, converte para PNG com o Chromium do Playwright (instalado globalmente).
Imprime avisos de rótulo que sai do retângulo ou que encosta em outro rótulo.
Os rótulos seguem a mesma regra de ajuste do viewer (_kit.label_boxes).
"""
import json
import os
import subprocess
import sys
from html import escape
from pathlib import Path

from _kit import DIAGRAMS, HARNESS, containers, label_boxes, text_extent

OUT = HARNESS / "dist" / "diagram-preview"

FILL = {
    "die": "#20242b", "frame": "#262b33", "gpc": "#2b3440", "tpc": "#34404f", "sm": "#4a6178",
    "block": "#2c3440", "sched": "#8a5a1c", "regfile": "#1f5566", "core": "#3d6b2a", "tensor": "#5f8f2a",
    "rt": "#9a9a2a", "tex": "#2a4f8f", "ldst": "#7a2a2a", "sfu": "#8f3a3a", "cache": "#1f5f66",
    "memory": "#2a5a3a", "memctl": "#3a4a6a", "field": "#3a3f55", "table": "#262b33", "cell": "#2c323c",
    "header": "#39414d", "codeline": "#1c2026", "actor": "#3a3f55", "lane": "#1d2229", "step": "#2f4a60",
    "thread": "#4a6178", "thread-alt": "#e07b1f", "counter": "#30383f", "note": "#2f3337", "gap": "#3a2626",
}
STROKE = {"gap": "#d06060", "note": "#888", "counter": "#7fb3d5", "thread-alt": "#ffb066"}
FLOW = {"data": "#3fc6d8", "energy": "#e3a83a", "heat": "#e05050", "control": "#c8c8c8"}


def load_all():
    return {json.loads(p.read_text(encoding="utf-8"))["id"]: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(DIAGRAMS.glob("*.json"))}


def fit_embed(child_size, rect):
    cw, ch = child_size
    x, y, w, h = rect
    s = min(w / cw, h / ch)
    return s, x + (w - cw * s) / 2, y + (h - ch * s) / 2


def render(diag, all_d, out, depth=0):
    cont = containers(diag)
    for n in diag["nodes"]:
        x, y, w, h = n["rect"]
        k = n["kind"]
        dis = n.get("state") == "disabled"
        fill = FILL.get(k, "#262b33")
        st = STROKE.get(k, "#6b7785")
        dash = ' stroke-dasharray="6 4"' if k == "gap" else ""
        op = ' opacity="0.35"' if dis else ""
        rx = min(w, h) * 0.04
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx:.2f}" fill="{fill}" '
                   f'stroke="{st}" stroke-width="{max(0.4, min(w, h) * 0.01):.2f}"{dash}{op}/>')
        if dis:
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#hach)"/>')
        if n.get("embed") and n["embed"] in all_d and depth < 3:
            c = all_d[n["embed"]]
            s, ox, oy = fit_embed(c["size"], n["rect"])
            out.append(f'<g transform="translate({ox} {oy}) scale({s})">')
            render(c, all_d, out, depth + 1)
            out.append("</g>")
        for lb in label_boxes(n, n["id"] in cont):
            txt, ax, cy, hh, anchor, cls = lb
            fam = "DejaVu Sans Mono, monospace" if n.get("mono") else "DejaVu Sans, Inter, sans-serif"
            col = "#ffffff" if cls != "sub" else "#c9d1d9"
            wgt = 600 if cls == "titulo" or k in ("counter", "header") else 500
            out.append(f'<text x="{ax:.2f}" y="{cy:.2f}" font-size="{hh:.2f}" font-family="{fam}" '
                       f'font-weight="{wgt}" fill="{col}" text-anchor="{anchor}" dominant-baseline="central" '
                       f'xml:space="preserve">{escape(txt)}</text>')
    for f in diag["flows"]:
        byid = {n["id"]: n for n in diag["nodes"]}
        pts = f.get("points")
        if not pts:
            a, b = byid[f["from"]]["rect"], byid[f["to"]]["rect"]
            pts = [[a[0] + a[2] / 2, a[1] + a[3] / 2], [b[0] + b[2] / 2, b[1] + b[3] / 2]]
        d = "M" + " L".join(f"{p[0]},{p[1]}" for p in pts)
        col = FLOW.get(f.get("path", "control"))
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.2" opacity="0.85" '
                   f'marker-end="url(#arr-{f.get("path", "control")})"/>')


def lint(diag, min_px_full=None):
    """Avisos: rótulo maior que o retângulo e rótulos que se sobrepõem."""
    cont = containers(diag)
    boxes, warns = [], []
    for n in diag["nodes"]:
        r = n["rect"]
        for lb in label_boxes(n, n["id"] in cont):
            e = text_extent(lb, n.get("mono"))
            if e[0] < r[0] - 0.5 or e[0] + e[2] > r[0] + r[2] + 0.5 or e[1] < r[1] - 0.5 or e[1] + e[3] > r[1] + r[3] + 0.5:
                warns.append(f"{n['id']}: rótulo '{lb[0]}' sai do retângulo")
            boxes.append((n["id"], lb[0], e))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][2], boxes[j][2]
            if boxes[i][0] == boxes[j][0]:
                continue
            if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                warns.append(f"rótulos se sobrepõem: {boxes[i][0]} '{boxes[i][1]}' e {boxes[j][0]} '{boxes[j][1]}'")
    return warns


def svg_for(diag, all_d):
    w, h = diag["size"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           '<defs><pattern id="hach" patternUnits="userSpaceOnUse" width="8" height="8">'
           '<path d="M-2,2 L2,-2 M0,8 L8,0 M6,10 L10,6" stroke="#999" stroke-width="1"/></pattern>']
    for k, c in FLOW.items():
        out.append(f'<marker id="arr-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                   f'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    out.append(f'</defs><rect width="{w}" height="{h}" fill="#101318"/>')
    render(diag, all_d, out)
    out.append("</svg>")
    return "\n".join(out)


SHOT = r"""
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2];
  const files = process.argv.slice(3);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, f + '.svg'), 'utf8');
    const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    const w = +m[1], h = +m[2];
    const W = w >= h ? 1920 : Math.round(1080 * w / h), H = Math.round(W * h / w);
    await page.setViewportSize({ width: W, height: H });
    await page.setContent(`<html><body style="margin:0;background:#101318">${svg.replace(/width="[\d.]+" height="[\d.]+"/, `width="${W}" height="${H}"`)}</body></html>`);
    await page.screenshot({ path: path.join(dir, f + '.png') });
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    all_d = load_all()
    ids = args or sorted(all_d)
    OUT.mkdir(parents=True, exist_ok=True)
    nwarn = 0
    for did in ids:
        (OUT / f"{did}.svg").write_text(svg_for(all_d[did], all_d), encoding="utf-8")
        for w in lint(all_d[did]):
            print(f"{did}: {w}")
            nwarn += 1
    print(f"{len(ids)} SVG em {OUT.relative_to(HARNESS)}; {nwarn} aviso(s)")
    if "--png" in sys.argv:
        js = OUT / "_shot.cjs"
        js.write_text(SHOT, encoding="utf-8")
        env = dict(os.environ)
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        subprocess.run(["node", str(js), str(OUT), *ids], check=True, env=env)
        print("PNG gerados")


if __name__ == "__main__":
    main()
