#!/usr/bin/env python3
"""Remedição da carcaça nos renders quase ortogonais da PNY (F4, 2026-11-10).

Resolve as divergências entre o CSV e a medição do modelador da carcaça:
  - altura da carcaça (CSV 124 contra cerca de 122,4 do modelador);
  - centro dos ventiladores (CSV 58,5 contra cerca de 61,2 do modelador);
  - entalhe da borda dos contatos (CSV 138 a 158), por causa da interferência com o PCB.

Calibração: a escala vem do comprimento da carcaça sem o bracket (card_envelope_length),
medido com subpixel pelo alfa nas linhas em que o bracket não aparece (perto da borda
superior, fora dos cantos arredondados). A calibração de frame_compare.py incluía a aba do
bracket (cerca de 3 px a mais), o que encolhia as medidas em 0,5 %.

Métodos (dois ou mais por grandeza):
  altura      bordas superior e inferior por coluna com subpixel pelo alfa; soma do alfa da
              coluna (independe de limiar). Colunas nos módulos dos ventiladores e na seção
              central, separadas, porque a seção central é mais baixa.
  ventilador  círculo ajustado à crista de brilho do aro, à borda externa do aro e à borda do
              cubo, por raios a partir de um centro inicial.
  entalhe     recuo da borda inferior por coluna, de 0,5 em 0,5 mm.

A foto storagereview/sr-4 (placa real, em perspectiva) foi tentada com retificação pelas
quatro bordas e pelos anéis: as pontas da carcaça somem no fundo escuro e no bracket, e os
anéis retificados saem com 8 a 10 % de excentricidade, então a foto não entra nas medidas.

Uso:   python3 -I harness/parts/frame_remeasure.py
Saída: harness/dist/parts/frame/remedicao.json (as imagens de referência são só lidas)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

HARNESS = Path(__file__).resolve().parent.parent
REF = HARNESS / "spec" / "references" / "cache" / "pny"
OUT = HARNESS / "dist" / "parts" / "frame" / "remedicao.json"
L = 304.8      # card_envelope_length (escala)

# Faixas de busca, em mm a partir do plano do bracket (não são medidas da peça)
POD_COLS = [*np.arange(20, 46, 5.0), *np.arange(225, 286, 5.0)]
CENTER_COLS = np.arange(165, 211, 5.0)
FAN_GUESS = (61.0, 243.5)


def alpha(name):
    a = np.asarray(Image.open(REF / name).convert("RGBA")).astype(float)
    return a[:, :, 3] / 255.0, gaussian_filter(a[:, :, :3].mean(2), 0.7)


def runs(v, thr=0.02):
    idx = np.nonzero(v > thr)[0]
    cuts = np.nonzero(np.diff(idx) > 1)[0]
    return list(zip(np.r_[idx[0], idx[cuts + 1]], np.r_[idx[cuts], idx[-1]]))


def length_px(al):
    """Extremos da carcaça com subpixel, nas linhas mais compridas sem o bracket: o bracket
    aparece como um trecho separado ou alonga a linha; as linhas da carcaça pura têm o maior
    comprimento estável perto da borda que não toca o bracket."""
    best = []
    for y in range(al.shape[0]):
        r = runs(al[y]) if al[y].max() > 0.02 else []
        if len(r) != 1:
            continue
        s, e = r[0]
        best.append((y, s + 1 - al[y, s], e + al[y, e]))
    best = np.array(best)
    span = best[:, 2] - best[:, 1]
    # só as linhas do corpo (até 6 px do comprimento típico; as abas do bracket alongam poucas
    # linhas e ficam de fora); nelas há dois platôs: com o
    # bracket (cerca de 3 px a mais) e sem ele. O mais curto, com pelo menos 8 linhas, é a
    # carcaça sem o bracket.
    body = np.abs(span - np.percentile(span, 75)) <= 6
    cands = sorted(set(np.round(span[body] * 2) / 2))
    target = next(v for v in cands if np.sum(body & (np.abs(span - v) <= 0.75)) >= 8)
    sel = best[body & (np.abs(span - target) <= 0.75)]
    return float(np.median(sel[:, 1])), float(np.median(sel[:, 2])), int(len(sel))


def column(al, px):
    col = al[:, px]
    r = runs(col)
    s, e = max(r, key=lambda t: col[t[0]:t[1] + 1].sum())
    return s + 1 - col[s], e + col[e], col[s:e + 1].sum()


def heights(al, x0, s, cols):
    out = []
    for xm in cols:
        top, bot, cov = column(al, int(round(x0 + s * xm)))
        out.append((xm, (bot - top) / s, cov / s))
    a = np.array(out)
    return {"colunas_mm": a[:, 0].tolist(), "bordas_subpixel_mm": round(float(a[:, 1].mean()), 2),
            "bordas_dispersao_mm": round(float(a[:, 1].std()), 2), "soma_alfa_mm": round(float(a[:, 2].mean()), 2)}


def circle(p):
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    c = np.linalg.lstsq(A, (p ** 2).sum(1), rcond=None)[0]
    return c[:2], math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)


def robust_circle(p):
    k = np.ones(len(p), bool)
    for _ in range(6):
        c, r = circle(p[k])
        res = np.abs(np.hypot(*(p - c).T) - r)
        k = res < max(0.5, 2.5 * np.median(res[k]))
    return c, r, int(k.sum())


def radial(G, c, rlo, rhi, mode):
    pts = []
    for th in np.radians(np.arange(0, 360, 1.0)):
        r = np.arange(rlo, rhi, 0.1)
        xs, ys = c[0] + r * np.cos(th), c[1] + r * np.sin(th)
        ok = (xs > 1) & (xs < G.shape[1] - 2) & (ys > 1) & (ys < G.shape[0] - 2)
        if ok.sum() < 10:
            continue
        v = map_coordinates(G, [ys[ok], xs[ok]], order=1)
        i = int(np.argmax(v)) if mode == "crista" else int(np.argmax(-np.gradient(v)))
        pts.append((xs[ok][i], ys[ok][i]))
    return np.array(pts)


def main():
    rep = {"calibracao": {}, "altura": {}, "ventiladores": [], "entalhe": {}}
    for view, name in (("face_a", "front.png"), ("face_b", "back.png")):
        al, G = alpha(name)
        x0, x1, n = length_px(al)
        s = (x1 - x0) / L
        rep["calibracao"][view] = {"x0_px": round(x0, 2), "x1_px": round(x1, 2), "px_por_mm": round(s, 4), "linhas": n}
        rep["altura"][view] = {"modulos": heights(al, x0, s, POD_COLS), "secao_central": heights(al, x0, s, CENTER_COLS)}
        # entalhe da borda dos contatos (front: base da imagem; back: topo)
        flip = view == "face_b"
        prof = []
        for xm in np.arange(128, 166, 0.5):
            col = al[:, int(x0 + s * xm)]
            idx = np.nonzero(col > 0.5)[0]
            prof.append((xm, idx.min() if flip else idx.max()))
        prof = np.array(prof, float)
        ref = np.median(prof[prof[:, 0] > 160, 1])
        rec = prof[np.abs(prof[:, 1] - ref) > 4] if not flip else prof[np.abs(prof[:, 1] - ref) > 4]
        inner = rec[(rec[:, 1] < ref) if not flip else (rec[:, 1] > ref)]
        rep["entalhe"][view] = {"x_inicio_visivel": float(inner[:, 0].min()), "x_fim": float(inner[:, 0].max()),
                                "profundidade_mm": round(float(abs(np.median(inner[:, 1]) - ref) / s), 2),
                                "nota": "antes do entalhe, de x 133 a 145, o lóbulo do adaptador desce abaixo da carcaça e esconde o começo do entalhe"}
        if view == "face_a":
            top, bot, _ = column(al, int(round(x0 + s * 30)))
            yc = (top + bot) / 2
            for k, gx in enumerate(FAN_GUESS, 1):
                c0 = (x0 + s * gx, yc)
                res = {}
                for met, (rlo, rhi, mode) in {"aro_crista": (52, 62, "crista"), "aro_borda_externa": (54, 62, "borda"),
                                               "cubo_borda": (17, 23, "borda")}.items():
                    c, r, npts = robust_circle(radial(G, c0, rlo * s, rhi * s, mode))
                    res[met] = {"x_mm": round((c[0] - x0) / s, 2), "y_acima_do_centro_dos_modulos_mm": round((yc - c[1]) / s, 2),
                                "diametro_mm": round(2 * r / s, 2), "pontos": npts}
                rep["ventiladores"].append({"ventilador": k, **res})
    rep["decisao"] = {
        "shroud_height_proposed": 123.3, "shroud_center_section_height": 122.0,
        "fan1_center_from_bracket_end": 61.2, "fan2_center_from_bracket_end": 243.3,
        "shroud_pcie_side_notch_x_start": 145.5, "shroud_pcie_side_notch_x_end": 158.0,
        "nota": "valores lançados no CSV em 2026-11-10 (derived); as medidas acima são a base",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    for view in ("face_a", "face_b"):
        c = rep["calibracao"][view]
        h = rep["altura"][view]
        print("[%s] carcaça de %.2f a %.2f px (%d linhas), %.4f px/mm" % (view, c["x0_px"], c["x1_px"], c["linhas"], c["px_por_mm"]))
        print("    altura nos módulos: bordas %.2f (dispersão %.2f), soma do alfa %.2f mm" % (
            h["modulos"]["bordas_subpixel_mm"], h["modulos"]["bordas_dispersao_mm"], h["modulos"]["soma_alfa_mm"]))
        print("    altura na seção central: bordas %.2f, soma do alfa %.2f mm" % (
            h["secao_central"]["bordas_subpixel_mm"], h["secao_central"]["soma_alfa_mm"]))
        print("    entalhe: %s" % {k: v for k, v in rep["entalhe"][view].items() if k != "nota"})
    for f in rep["ventiladores"]:
        print("ventilador %d: " % f["ventilador"] + "; ".join("%s x %.2f, y %+.2f, diâmetro %.2f" % (
            m, f[m]["x_mm"], f[m]["y_acima_do_centro_dos_modulos_mm"], f[m]["diametro_mm"]) for m in ("aro_crista", "aro_borda_externa", "cubo_borda")))
    print("Relatório: %s" % OUT.relative_to(HARNESS.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
