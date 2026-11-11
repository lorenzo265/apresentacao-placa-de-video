#!/usr/bin/env python3
"""Comparação dos ventiladores (cooler.fan.*) com as referências da PNY.

Lê harness/build/parts/cooler.fan.{1,2}.glb e frame.shroud.glb (vista frontal) e
harness/build/card.glb (três quartos, depois do integrate.py), traça raios e grava em
harness/dist/parts/fan/:

  01-frente-lado-a-lado.png    pny/front | modelo, mesma escala e posição (vista de +z)
  02-frente-sobreposta.png     contornos das pás e do cubo sobre pny/front (e zoom no ventilador 1)
  03-tres-quartos-lado-a-lado.png  pny/3qtr-top-right | card.glb com a câmera ajustada
  04-tres-quartos-sobreposta.png   contornos do modelo sobre a referência
  integrado.png                card.glb integrado, três quartos da face A e da borda superior
  comparacao.json              medidas na referência e no modelo, com a diferença

Calibração da vista frontal: a mesma de frame_remeasure.py (comprimento da carcaça sem o
bracket, 2,2716 px/mm; centro vertical da silhueta = iface_shroud_center_y). A câmera de três
quartos é ajustada à silhueta da placa no render (maior sobreposição do contorno convexo, mais
os centros dos dois cubos marcados na imagem): é uma comparação de forma, sem medida.

Medidas por raio (r de 22 a 56 mm): posição angular da borda de ataque (na referência, a maior
queda de brilho no sentido anti-horário; no modelo, o fim de cada pá na máscara projetada),
vão entre pás (faixa escura na referência; vão da máscara no modelo), raio da ponta, centro e
diâmetro do cubo. As imagens de referência são material de terceiros: só lidas.

Uso:   python3 -I harness/parts/fan_compare.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter1d, map_coordinates

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fan as FN  # noqa: E402
import integrate as I  # noqa: E402

HARNESS = FN.HARNESS
REF = HARNESS / "spec" / "references" / "cache" / "pny"
DIST = HARNESS / "dist" / "parts" / "fan"
SS = 2
# calibração de pny/front (frame_remeasure.py, dist/parts/frame/remedicao.json)
CAL = {"x0": 66.9, "s": 2.2716, "pyc": 376.0}
YC = FN.M("iface_shroud_center_y")
RADII = np.arange(22.0, 56.1, 2.0)
DARK_FRAC = 0.12          # limiar da faixa escura (o mesmo da medida do vão em fan.py)
# pontos marcados à mão em pny/3qtr-top-right (px), para fixar a câmera: centros dos dois
# cubos e centro do encaixe do conector de energia na borda superior
QTR_MARKS = ((182.0, 275.0), (535.0, 585.0), (477.0, 365.0))

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except OSError:
    FONT = ImageFont.load_default()
COL = {"blade": (0.34, 0.345, 0.36), "hub": (0.38, 0.385, 0.40), "cap": (0.42, 0.43, 0.45),
       "shroud": (0.26, 0.265, 0.28), "other": (0.20, 0.20, 0.22)}
EDGE_COL = {"blade": (60, 230, 255), "hub": (255, 200, 40), "cap": (255, 200, 40), "shroud": (255, 90, 200), "other": (140, 140, 140)}


# ---------------------------------------------------------------------------
# Leitura das malhas
# ---------------------------------------------------------------------------
def glb_meshes(path):
    js, binary = I.read_glb(path)
    out = {}
    for n in js["nodes"]:
        if "mesh" not in n:
            continue
        prim = js["meshes"][n["mesh"]]["primitives"][0]
        v = I.from_gltf(I.accessor(js, binary, prim["attributes"]["POSITION"]))
        f = I.accessor(js, binary, prim["indices"]).reshape(-1, 3).astype(np.int64)
        out[n["name"]] = trimesh.Trimesh(v, f, process=False)
    return out


def category(name):
    if ".blade." in name:
        return "blade"
    if name.startswith("cooler.fan."):
        return "hub"
    if name.startswith("frame.shroud"):
        return "shroud"
    return "other"


class Tracer:
    def __init__(self, named):
        import bpy  # noqa: F401
        from mathutils.bvhtree import BVHTree
        V, F, N, tag = [], [], [], []
        self.cats = []
        off = 0
        for name, m in named:
            sm = trimesh.graph.smooth_shade(m, angle=math.radians(30))
            V.append(sm.vertices)
            F.append(sm.faces + off)
            N.append(sm.vertex_normals)
            c = category(name)
            if c not in self.cats:
                self.cats.append(c)
            tag.append(np.full(len(sm.faces), self.cats.index(c)))
            off += len(sm.vertices)
        self.V, self.F, self.N = np.vstack(V), np.vstack(F), np.vstack(N)
        self.tag = np.concatenate(tag)
        self.tree = BVHTree.FromPolygons(self.V.tolist(), self.F.tolist(), epsilon=0.0)

    def cast(self, o, d):
        from mathutils import Vector
        n = len(o)
        t = np.full(n, np.nan)
        loc = np.zeros((n, 3))
        idx = np.full(n, -1)
        rc = self.tree.ray_cast
        for i in range(n):
            hit = rc(Vector(o[i]), Vector(d[i]))
            if hit[0] is not None:
                loc[i] = hit[0]
                idx[i] = hit[2]
                t[i] = hit[3]
        nrm = np.zeros((n, 3))
        h = idx >= 0
        tri = self.F[idx[h]]
        a, b, c = self.V[tri[:, 0]], self.V[tri[:, 1]], self.V[tri[:, 2]]
        p = loc[h]
        v0, v1, v2 = b - a, c - a, p - a
        d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
        d20, d21 = (v2 * v0).sum(1), (v2 * v1).sum(1)
        den = d00 * d11 - d01 ** 2
        den[den == 0] = 1
        w1 = (d11 * d20 - d01 * d21) / den
        w2 = (d00 * d21 - d01 * d20) / den
        w0 = 1 - w1 - w2
        nn = w0[:, None] * self.N[tri[:, 0]] + w1[:, None] * self.N[tri[:, 1]] + w2[:, None] * self.N[tri[:, 2]]
        nn /= np.linalg.norm(nn, axis=1)[:, None] + 1e-12
        nn *= np.where((nn * np.asarray(d)[h]).sum(1) > 0, -1, 1)[:, None]
        nrm[h] = nn
        cat = np.full(n, -1)
        cat[h] = self.tag[idx[h]]
        return t, nrm, cat, loc


def shade(tr, t, n, cat, loc, view, key, cap_r=None):
    H, W = t.shape
    img = np.zeros((H, W, 3)) + 0.035
    hit = ~np.isnan(t)
    key = np.asarray(key, float) / np.linalg.norm(key)
    fill = np.array([0.5, -0.3, 0.8])
    fill /= np.linalg.norm(fill)
    vd = np.asarray(view, float)
    half = key - vd
    half /= np.linalg.norm(half)
    lam = 0.75 * np.clip(n @ key, 0, 1) + 0.20 * np.clip(n @ fill, 0, 1)
    spec = np.clip(n @ half, 0, 1)
    depth = np.clip((FN.T - loc[..., 2]) / 12.0, 0, 1)      # mais fundo, mais escuro (oclusão aproximada)
    for k, c in enumerate(tr.cats):
        m = hit & (cat == k)
        base = np.array(COL[c])
        col = base[None] * (0.30 + 1.7 * lam[m, None]) + (0.35 if c in ("hub",) else 0.18) * spec[m, None] ** 24
        img[m] = col * (1 - 0.65 * depth[m, None])
    return np.clip(img, 0, 1)


def edges(t, n, cat):
    hit = ~np.isnan(t)
    tt = np.where(hit, t, 1e6)
    e = np.zeros(t.shape, bool)
    for ax in (0, 1):
        a = np.roll(tt, 1, axis=ax)
        na = np.roll(n, 1, axis=ax)
        ca = np.roll(cat, 1, axis=ax)
        ha = np.roll(hit, 1, axis=ax)
        e |= (np.abs(tt - a) > 0.6) | ((np.sum(n * na, axis=2) < math.cos(math.radians(35))) & hit & ha) | ((cat != ca) & hit & ha) | (hit != ha)
    e[0, :] = e[:, 0] = False
    own = cat.copy()
    for ax in (0, 1):
        for sh in (1, -1):
            a = np.roll(tt, sh, axis=ax)
            m = a < tt
            own[m] = np.roll(cat, sh, axis=ax)[m]
    return e, own


# ---------------------------------------------------------------------------
# Vista frontal
# ---------------------------------------------------------------------------
def px(x, y):
    return CAL["x0"] + CAL["s"] * x, CAL["pyc"] - CAL["s"] * (y - YC)


def ortho_front(tr, size):
    W, H = size[0] * SS, size[1] * SS
    gx, gy = np.meshgrid((np.arange(W) + 0.5) / SS, (np.arange(H) + 0.5) / SS)
    x = (gx - CAL["x0"]) / CAL["s"]
    y = YC - (gy - CAL["pyc"]) / CAL["s"]
    o = np.c_[x.ravel(), y.ravel(), np.full(x.size, FN.T + 50)]
    d = np.tile([0, 0, -1.0], (x.size, 1))
    t, n, c, loc = tr.cast(o, d)
    return t.reshape(H, W), n.reshape(H, W, 3), c.reshape(H, W), loc.reshape(H, W, 3)


def ref_gray(name):
    a = np.asarray(Image.open(REF / name).convert("RGBA")).astype(float)
    return a[:, :, :3].mean(2), a


def ref_le_gap(g, fx):
    cx, cy = px(fx, FN.FAN_Y)
    th = np.arange(0, 360, 0.1)
    T = np.radians(th)
    out = []
    for r in RADII:
        v = map_coordinates(g, [cy - CAL["s"] * r * np.sin(T), cx + CAL["s"] * r * np.cos(T)], order=1)
        v = gaussian_filter1d(v, 3, mode="wrap")
        dv = np.gradient(v)
        pk = []
        for i in np.argsort(dv):
            if all(min(abs(th[i] - th[j]), 360 - abs(th[i] - th[j])) > 20 for j in pk):
                pk.append(i)
            if len(pk) == FN.NB:
                break
        les = np.sort(th[pk])
        v2 = gaussian_filter1d(map_coordinates(g, [cy - CAL["s"] * r * np.sin(T), cx + CAL["s"] * r * np.cos(T)], order=1), 2, mode="wrap")
        lo, hi = np.percentile(v2, 3), np.percentile(v2, 90)
        gap = (v2 < lo + DARK_FRAC * (hi - lo)).mean() * 360 / FN.NB
        out.append((r, les, gap))
    return out


def model_le_gap(mask, fx):
    """mask: pás vistas de +z, na escala SS x da referência."""
    cx, cy = px(fx, FN.FAN_Y)
    th = np.arange(0, 360, 0.1)
    T = np.radians(th)
    out = []
    for r in RADII:
        cov = map_coordinates(mask.astype(float), [(cy - CAL["s"] * r * np.sin(T)) * SS - 0.5, (cx + CAL["s"] * r * np.cos(T)) * SS - 0.5], order=1) > 0.5
        ends = th[np.nonzero(cov & ~np.roll(cov, -1))[0]]            # fim anti-horário de cada pá
        out.append((r, np.sort(ends), (~cov).mean() * 360 / FN.NB))
    return out


def match(ref_les, mod_les):
    """Diferença angular média (modelo - referência) casando cada borda com a mais próxima."""
    d = []
    for a in ref_les:
        dd = (mod_les - a + 180) % 360 - 180
        d.append(dd[np.argmin(np.abs(dd))])
    return np.array(d)


def tip_radius(img, fx, scale=1.0):
    """Raio da ponta: onde a amplitude do harmônico de ordem 7 (o padrão das pás) cai à
    metade do valor em r = 50, de 0,05 em 0,05 mm. img: brilho da referência ou máscara das
    pás do modelo; scale: pixels da imagem por pixel da referência."""
    cx, cy = px(fx, FN.FAN_Y)
    th = np.radians(np.arange(0, 360, 0.25))
    rs = np.arange(50, 60, 0.05)
    amp = []
    for r in rs:
        v = map_coordinates(img, [(cy - CAL["s"] * r * np.sin(th)) * scale - (scale - 1) / 2,
                                  (cx + CAL["s"] * r * np.cos(th)) * scale - (scale - 1) / 2], order=1)
        amp.append(abs(np.sum(v * np.exp(-1j * FN.NB * th))))
    amp = np.array(amp)
    j = int(np.argmax(amp < 0.5 * amp[0]))
    a0, a1 = amp[j - 1], amp[j]
    return float(rs[j - 1] + (a0 - 0.5 * amp[0]) / (a0 - a1) * 0.05)


def circle_fit(pts):
    A = np.c_[2 * pts[:, 0], 2 * pts[:, 1], np.ones(len(pts))]
    c = np.linalg.lstsq(A, (pts ** 2).sum(1), rcond=None)[0]
    return c[0], c[1], math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)


def hub_ref(g, fx):
    """Borda do cubo: maior salto de brilho entre r = 17 e 23 mm, em 180 raios."""
    cx, cy = px(fx, FN.FAN_Y)
    pts = []
    for a in np.radians(np.arange(0, 360, 2.0)):
        rs = np.arange(17, 23, 0.05)
        v = gaussian_filter1d(map_coordinates(g, [cy - CAL["s"] * rs * np.sin(a), cx + CAL["s"] * rs * np.cos(a)], order=1), 1.5)
        j = int(np.argmax(np.abs(np.gradient(v))))
        pts.append((cx + CAL["s"] * rs[j] * np.cos(a), cy - CAL["s"] * rs[j] * np.sin(a)))
    p = np.array(pts)
    for _ in range(3):
        x, y, R = circle_fit(p)
        res = np.abs(np.hypot(p[:, 0] - x, p[:, 1] - y) - R)
        p = p[res < max(1.0, 2.5 * np.median(res))]
    return (x - CAL["x0"]) / CAL["s"], YC - (y - CAL["pyc"]) / CAL["s"], 2 * R / CAL["s"]


def hub_model(cat_hub_mask, fx):
    """Disco do cubo visto de +z (só o rotor: z acima do fundo do rotor, sem o suporte)."""
    ys, xs = np.nonzero(cat_hub_mask)
    xm = (xs + 0.5) / SS
    ym = (ys + 0.5) / SS
    x = (xm - CAL["x0"]) / CAL["s"]
    y = YC - (ym - CAL["pyc"]) / CAL["s"]
    sel = np.hypot(x - fx, y - FN.FAN_Y) < 30
    # contorno do disco do cubo
    m = np.zeros_like(cat_hub_mask)
    m[ys[sel], xs[sel]] = True
    from scipy.ndimage import binary_erosion, binary_fill_holes
    m = binary_fill_holes(m)
    b = m & ~binary_erosion(m)
    ys, xs = np.nonzero(b)
    pts = np.c_[(xs + 0.5) / SS, (ys + 0.5) / SS]
    x, y, R = circle_fit(pts)
    return (x - CAL["x0"]) / CAL["s"], YC - (y - CAL["pyc"]) / CAL["s"], 2 * R / CAL["s"]


def front(rep):
    named = []
    for n in (1, 2):
        named += list(glb_meshes(FN.OUT / ("cooler.fan.%d.glb" % n)).items())
    named += list(glb_meshes(FN.OUT / "frame.shroud.glb").items())
    tr = Tracer(named)
    ref = Image.open(REF / "front.png").convert("RGBA")
    ref = Image.alpha_composite(Image.new("RGBA", ref.size, (255, 255, 255, 255)), ref).convert("RGB")
    t, n, c, loc = ortho_front(tr, ref.size)
    img = shade(tr, t, n, c, loc, [0, 0, -1.0], [-0.35, 0.55, 0.75])
    model = Image.fromarray((img * 255).astype(np.uint8))
    x0, y0 = px(-6, FN.M("iface_shroud_y_min") + FN.M("shroud_height_proposed") + 6)
    x1, y1 = px(FN.M("card_envelope_length") + 6, FN.M("iface_shroud_y_min") - 16)
    box = [int(x0 * SS), int(y0 * SS), int(x1 * SS), int(y1 * SS)]
    refb = ref.resize((ref.width * SS, ref.height * SS), Image.LANCZOS)
    a, b = refb.crop(box), model.crop(box)
    out = Image.new("RGB", (a.width, a.height * 2 + 56), (20, 20, 24))
    out.paste(a, (0, 28))
    out.paste(b, (0, a.height + 56))
    d = ImageDraw.Draw(out)
    d.text((8, 8), "referência: pny/front (render de terceiro, quase ortogonal), %.4f px/mm x %d" % (CAL["s"], SS), font=FONT, fill=(235, 235, 235))
    d.text((8, a.height + 36), "modelo: cooler.fan.1 e .2 (pás, cubo, suporte) com frame.shroud, mesma escala, vista de +z", font=FONT, fill=(235, 235, 235))
    out.save(DIST / "01-frente-lado-a-lado.png")

    e, own = edges(t, n, c)
    keep = np.zeros_like(e)
    for k, cname in enumerate(tr.cats):
        if cname in ("blade", "hub"):
            keep |= own == k
    e &= keep
    arr = np.asarray(refb).astype(float) * 0.8
    for k, cname in enumerate(tr.cats):
        arr[e & (own == k)] = EDGE_COL[cname]
    ov = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    dd = ImageDraw.Draw(ov)
    for fx in FN.FAN_X:
        cx, cy = px(fx, FN.FAN_Y)
        dd.line([(cx - 6) * SS, cy * SS, (cx + 6) * SS, cy * SS], fill=(255, 60, 60), width=2)
        dd.line([cx * SS, (cy - 6) * SS, cx * SS, (cy + 6) * SS], fill=(255, 60, 60), width=2)
    full = ov.crop(box)
    zx0, zy0 = px(FN.FAN_X[0] - 62, FN.FAN_Y + 62)
    zx1, zy1 = px(FN.FAN_X[0] + 62, FN.FAN_Y - 62)
    zoom = ov.crop([int(zx0 * SS), int(zy0 * SS), int(zx1 * SS), int(zy1 * SS)])
    zoom = zoom.resize((zoom.width * 2, zoom.height * 2), Image.LANCZOS)
    sheet = Image.new("RGB", (max(full.width, zoom.width), full.height + zoom.height + 60), (20, 20, 24))
    sheet.paste(full, (0, 30))
    sheet.paste(zoom, (0, full.height + 60))
    d = ImageDraw.Draw(sheet)
    d.text((8, 8), "contornos do modelo sobre pny/front: ciano = pás, amarelo = cubo; cruz vermelha = centro pelo CSV", font=FONT, fill=(235, 235, 235))
    d.text((8, full.height + 38), "zoom no ventilador 1 (lado do bracket)", font=FONT, fill=(235, 235, 235))
    sheet.save(DIST / "02-frente-sobreposta.png")

    # medidas
    g, _ = ref_gray("front.png")
    kb = tr.cats.index("blade")
    kh = tr.cats.index("hub")
    res = []
    for i, fx in enumerate(FN.FAN_X):
        rl, ml = ref_le_gap(g, fx), model_le_gap(c == kb, fx)
        rows = []
        for (r, rles, rgap), (_, mles, mgap) in zip(rl, ml):
            dif = match(rles, mles)
            rows.append({"r": r, "borda_de_ataque_dif_media_deg": round(float(dif.mean()), 2),
                         "borda_de_ataque_dif_max_deg": round(float(np.abs(dif).max()), 2),
                         "vao_ref_deg": round(float(rgap), 2), "vao_modelo_deg": round(float(mgap), 2)})
        # varredura total (r = 22 a 56): para cada pá, a borda em r = 56 mais próxima no
        # sentido anti-horário da borda em r = 22, média das 7 pás
        def sweep_of(lst):
            a0, a1 = lst[0][1], lst[-1][1]
            return float(np.mean([((a1 - a) % 360).min() for a in a0]))
        sw_r = sweep_of(rl)
        sw_m = sweep_of(ml)
        hr = hub_ref(g, fx)
        hm = hub_model((c == kh) & (loc[..., 2] > FN.Z0 + 0.5), fx)
        tip_r = tip_radius(g, fx)
        tip_m = tip_radius((c == kb).astype(float), fx, SS)
        dif_all = np.array([q["borda_de_ataque_dif_media_deg"] for q in rows])
        entry = {
            "ventilador": i + 1,
            "por_raio": rows,
            "borda_de_ataque": {"dif_media_deg": round(float(dif_all.mean()), 2), "dif_rms_deg": round(float(np.sqrt((dif_all ** 2).mean())), 2),
                                "dif_max_deg": round(float(max(q["borda_de_ataque_dif_max_deg"] for q in rows)), 2)},
            "varredura_r22_a_r56_deg": {"ref": round(sw_r, 2), "modelo": round(sw_m, 2), "dif": round(sw_m - sw_r, 2),
                                        "sentido": "anti-horário visto de +z para fora" if sw_r > 0 else "horário"},
            "vao_medio_deg": {"ref": round(float(np.mean([q["vao_ref_deg"] for q in rows])), 2),
                              "modelo": round(float(np.mean([q["vao_modelo_deg"] for q in rows])), 2)},
            "raio_da_ponta_mm": {"ref": round(tip_r, 2), "modelo": round(tip_m, 2), "modelo_geometria": FN.R_TIP, "dif": round(tip_m - tip_r, 2),
                                 "metodo": "metade da amplitude do harmônico de ordem 7"},
            "cubo": {"ref": {"x": round(hr[0], 2), "y": round(hr[1], 2), "diametro": round(hr[2], 2)},
                     "modelo": {"x": round(hm[0], 2), "y": round(hm[1], 2), "diametro": round(hm[2], 2)},
                     "dif": {"x": round(hm[0] - hr[0], 2), "y": round(hm[1] - hr[1], 2), "diametro": round(hm[2] - hr[2], 2)}},
        }
        res.append(entry)
        print("[frente] ventilador %d: borda de ataque modelo - ref média %+.2f, rms %.2f, máx %.2f graus; varredura ref %.2f, modelo %.2f graus (%s)" % (
            i + 1, entry["borda_de_ataque"]["dif_media_deg"], entry["borda_de_ataque"]["dif_rms_deg"], entry["borda_de_ataque"]["dif_max_deg"],
            sw_r, sw_m, entry["varredura_r22_a_r56_deg"]["sentido"]))
        print("    vão médio ref %.2f, modelo %.2f graus; raio da ponta ref %.2f, modelo %.2f mm" % (
            entry["vao_medio_deg"]["ref"], entry["vao_medio_deg"]["modelo"], tip_r, tip_m))
        print("    cubo ref (%.2f, %.2f) diâmetro %.2f; modelo (%.2f, %.2f) diâmetro %.2f" % (*hr, *hm))
    rep["frente"] = res


# ---------------------------------------------------------------------------
# Três quartos
# ---------------------------------------------------------------------------
def basis(az, el, roll):
    d = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])   # do alvo para o olho
    f = -d
    up0 = np.array([0, 0, 1.0]) if abs(d[2]) < 0.95 else np.array([0, 1.0, 0])
    r = np.cross(f, up0)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    cr, sr = math.cos(roll), math.sin(roll)
    return f, r * cr + u * sr, -r * sr + u * cr


def project(p, cam, size):
    az, el, roll, dist, foc, tx, ty, tz = cam
    f, r, u = basis(az, el, roll)
    tgt = np.array([tx, ty, tz])
    eye = tgt - f * dist
    rel = np.asarray(p) - eye
    zc = rel @ f
    return np.c_[size / 2 + foc * (rel @ r) / zc, size / 2 - foc * (rel @ u) / zc], eye, tgt, f, r, u


def hull_mask(pts, size):
    from scipy.spatial import ConvexHull
    h = ConvexHull(pts)
    im = Image.new("L", (size, size), 0)
    ImageDraw.Draw(im).polygon([tuple(pts[i]) for i in h.vertices], fill=1)
    return np.asarray(im, bool)


def fit_camera(card_pts, ref_mask):
    from scipy.optimize import minimize
    size = ref_mask.shape[0]
    from scipy.spatial import ConvexHull
    ys, xs = np.nonzero(ref_mask)
    P = np.c_[xs, ys].astype(float)
    hv = ConvexHull(P).vertices
    im = Image.new("L", (size, size), 0)
    ImageDraw.Draw(im).polygon([tuple(P[i]) for i in hv], fill=1)
    ref_h = np.asarray(im, bool)
    sub = card_pts[:: max(1, len(card_pts) // 6000)]
    hubs3 = marks3d()

    def score(cam):
        if cam[3] < 150 or cam[4] < 100:
            return 10.0
        q, *_ = project(sub, cam, size)
        m = hull_mask(q, size)
        iou = (m & ref_h).sum() / max((m | ref_h).sum(), 1)
        hq, *_ = project(hubs3, cam, size)
        dh = np.linalg.norm(hq - np.array(QTR_MARKS), axis=1).mean() / size
        return (1 - iou) + 6.0 * dh
    c0 = np.array([FN.M("card_envelope_length") / 2, YC, FN.T / 2])
    cands = []
    for az in np.radians(np.arange(0, 360, 20)):
        for el in np.radians(np.arange(10, 81, 10)):
            for roll in np.radians(np.arange(-180, 180, 20)):
                cam = [az, el, roll, 700.0, 1600.0, *c0]
                cands.append((score(cam), cam))
    cands.sort(key=lambda q: q[0])
    best = None
    for _, cam in cands[:6]:          # Nelder-Mead a partir dos 6 melhores pontos da grade
        for dist in (450.0, 900.0):
            cam = list(cam)
            cam[3], cam[4] = dist, 1600.0 * dist / 700.0
            r_ = minimize(score, cam, method="Nelder-Mead", options={"maxiter": 4000, "xatol": 1e-4, "fatol": 1e-7})
            if best is None or r_.fun < best.fun:
                best = r_
    r = best
    cam = r.x
    q, *_ = project(sub, cam, size)
    m = hull_mask(q, size)
    iou = float((m & ref_h).sum() / (m | ref_h).sum())
    hq, *_ = project(hubs3, cam, size)
    return cam, iou, np.linalg.norm(hq - np.array(QTR_MARKS), axis=1).tolist()


def marks3d():
    a = [x["pos"] for x in FN.PARTS["frame.shroud"]["anchors"] if x["id"].endswith("power_opening")][0]
    return np.array([[fx, FN.FAN_Y, FN.Z_HUB] for fx in FN.FAN_X] + [a])


def persp(tr, cam, size):
    W = H = size * SS
    _, eye, tgt, f, r, u = project(np.zeros((1, 3)), cam, size)
    foc = cam[4] * SS
    gx, gy = np.meshgrid(np.arange(W) + 0.5 - W / 2, np.arange(H) + 0.5 - H / 2)
    d = f[None] * foc + gx.ravel()[:, None] * r[None] - gy.ravel()[:, None] * u[None]
    d /= np.linalg.norm(d, axis=1)[:, None]
    o = np.tile(eye, (len(d), 1))
    t, n, c, loc = tr.cast(o, d)
    return t.reshape(H, W), n.reshape(H, W, 3), c.reshape(H, W), loc.reshape(H, W, 3), f, r, u


def card_named():
    meshes = glb_meshes(HARNESS / "build" / "card.glb")
    return list(meshes.items())


def three_quarter(rep):
    named = card_named()
    tr = Tracer(named)
    ref = Image.open(REF / "3qtr-top-right.png").convert("RGBA")
    alpha = np.asarray(ref)[:, :, 3] > 128
    refc = Image.alpha_composite(Image.new("RGBA", ref.size, (255, 255, 255, 255)), ref).convert("RGB")
    pts = np.vstack([m.vertices for _, m in named])
    cam, iou, dh = fit_camera(pts, alpha)
    print("[três quartos] câmera ajustada: sobreposição da silhueta %.3f; cubos e encaixe do conector a %.1f, %.1f e %.1f px das marcas" % (iou, *dh))
    size = ref.size[0]
    t, n, c, loc, f, r, u = persp(tr, cam, size)
    key = -f * 0.75 + u * 0.55 - r * 0.35
    img = shade(tr, t, n, c, loc, f, key)
    model = Image.fromarray((img * 255).astype(np.uint8)).resize(ref.size, Image.LANCZOS)
    out = Image.new("RGB", (ref.width * 2, ref.height + 28), (20, 20, 24))
    out.paste(refc, (0, 28))
    out.paste(model, (ref.width, 28))
    d = ImageDraw.Draw(out)
    d.text((8, 8), "referência: pny/3qtr-top-right (render de terceiro, perspectiva)", font=FONT, fill=(235, 235, 235))
    d.text((ref.width + 8, 8), "modelo: card.glb integrado, câmera ajustada à silhueta (IoU %.3f)" % iou, font=FONT, fill=(235, 235, 235))
    out.save(DIST / "03-tres-quartos-lado-a-lado.png")
    e, own = edges(t, n, c)
    keep = np.zeros_like(e)
    for k, cname in enumerate(tr.cats):
        if cname in ("blade", "hub"):
            keep |= own == k
    e &= keep
    big = np.asarray(refc.resize((ref.width * SS, ref.height * SS), Image.LANCZOS)).astype(float) * 0.8
    for k, cname in enumerate(tr.cats):
        big[e & (own == k)] = EDGE_COL[cname]
    ov = Image.fromarray(big.clip(0, 255).astype(np.uint8))
    ImageDraw.Draw(ov).text((8, 8), "contornos do modelo (ciano = pás, amarelo = cubo) sobre pny/3qtr-top-right", font=FONT, fill=(30, 30, 30))
    ov.save(DIST / "04-tres-quartos-sobreposta.png")
    rep["tres_quartos"] = {"camera": {"az_deg": math.degrees(cam[0]), "el_deg": math.degrees(cam[1]), "roll_deg": math.degrees(cam[2]),
                                      "dist_mm": cam[3], "focal_px": cam[4], "alvo": list(cam[5:])},
                           "iou_silhueta": round(iou, 4), "marcas_dist_px": [round(x, 1) for x in dh]}
    # vista do conjunto integrado, um pouco mais aberta, para o relatório
    cam2 = np.array(cam, float)
    cam2[3] *= 1.0
    t, n, c, loc, f, r, u = persp(tr, cam2, 1000)
    img = shade(tr, t, n, c, loc, f, -f * 0.75 + u * 0.55 - r * 0.35)
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((1000, 1000), Image.LANCZOS)
    ImageDraw.Draw(im).text((10, 10), "card.glb integrado (ventiladores e carcaça detalhados, demais peças em blockout), três quartos como pny/3qtr-top-right", font=FONT, fill=(230, 230, 230))
    im.save(DIST / "integrado.png")


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    rep = {"calibracao_frente": CAL}
    front(rep)
    three_quarter(rep)
    (DIST / "comparacao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("Imagens e comparacao.json em %s" % DIST.relative_to(HARNESS.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
