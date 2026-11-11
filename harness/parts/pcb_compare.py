#!/usr/bin/env python3
"""Comparação do PCB principal modelado com as fotos retificadas (F3).

1. --retificar: retifica chiphell/pcb-b.jpg (frente do PCB nu) pelos 8 furos (4 da mola,
   pelo CSV; 4 de canto, medidos em a_board.png) para o quadro da frente vista de +z, a
   10 px/mm na escala da base: px = (u_b + 10) * 10, py = (131,5 - v_b) * 10, com
   (u_b, v_b) = (u, v) x chiphell_pcb_a_scale_factor. Grava no cache (não versionado):
   spec/references/cache/visualqa/pcb_b_front.png.
2. Vistas de topo do modelo (Blender, câmera ortográfica) na escala das fotos corrigida
   pelo fator (10 x 1,013 px por mm real; quadros em pcb_layout.py: front_px, back_px):
   frente no quadro acima; verso no quadro de visualqa/a_board.png. Lado a lado e sobreposta.
3. Medidas: centro do campo de esferas de cada uma das 16 posições de memória nas duas fotos
   (automático: ilhas pequenas em grade de cerca de 0,75 mm, agrupadas em duas metades por
   chip) contra a grade arbitrada; passo e distância entre as fileiras laterais; campo de
   esferas do GB202.
4. Vista em perspectiva da frente contra sabareesh/wb-bare-pcb.jpg e três quartos (pule com
   --so-topo, que deixa só as vistas de topo e as medidas).
5. --integrado: vista do estágio E7 (PCB afastado) a partir de build/card.glb.

Uso:   python3 -I harness/parts/pcb_compare.py [--retificar] [--so-topo] [--integrado]
Saídas: harness/dist/parts/pcb/*.png e comparacao.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pcb_layout as PL  # noqa: E402

HARNESS = PL.HARNESS
CACHE = PL.CACHE
DIST = HARNESS / "dist" / "parts" / "pcb"
PARTS_DIR = HARNESS / "build" / "parts"
FRONT_PNG = PL.FRONT_PNG
BACK_PNG = PL.BACK_PNG
PCB_IDS = ("pcb.main", "gpu.package", "mem.front", "mem.back", "power.inductors", "power.vrm.gpu", "power.vrm.mem",
           "power.controller", "power.aux", "io.aux_header", "pcb.smd", "pcb.back_frame")


# ---------------------------------------------------------------------------
# Quadros das fotos (pcb_layout.py; escala corrigida pelo fator do pcb-a)
# ---------------------------------------------------------------------------
front_px, front_uv, back_px, back_uv = PL.front_px, PL.front_uv, PL.back_px, PL.back_uv


def rectify():
    """Homografia pelos 8 furos de chiphell/pcb-b.jpg (DLT) e reamostragem."""
    im = np.asarray(Image.open(CACHE / "chiphell" / "pcb-b.jpg").convert("RGB")).astype(int)
    g = im.mean(2)

    def fit(xs, ys):
        A = np.c_[2 * xs, 2 * ys, np.ones(len(xs))]
        c = np.linalg.lstsq(A, xs ** 2 + ys ** 2, rcond=None)[0]
        return c[0], c[1], math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)

    def ring(x, y, R, mode):
        ys, xs = np.mgrid[y - R:y + R, x - R:x + R]
        win, gg = im[y - R:y + R, x - R:x + R], g[y - R:y + R, x - R:x + R]
        m = ((gg > 150) & (np.abs(win[..., 0] - win[..., 2]) < 40)) if mode == "w" else ((win[..., 0] - win[..., 2] > 30) & (gg > 90))
        xx, yy = xs[m].astype(float), ys[m].astype(float)
        for _ in range(4):
            cx, cy, r = fit(xx, yy)
            k = np.abs(np.hypot(xx - cx, yy - cy) - r) < 3
            xx, yy = xx[k], yy[k]
        return cx, cy
    # o quadro da retificação fica na escala da base: (u, v) reais x F
    cu, cv = PL.GU * PL.F, PL.GV * PL.F
    sx, sy = PL.M("iface_spring_holes_dx") / 2 * PL.F, PL.M("iface_spring_holes_dy") / 2 * PL.F
    # (u, v) dos furos na escala da base: mola pelo CSV; cantos medidos em a_board.png (um dos quatro do CSV não confirmado)
    pts = [((cu + sx, cv + sy), (518, 442, 22, "w")), ((cu + sx, cv - sy), (1042, 459, 22, "w")),
           ((cu - sx, cv + sy), (502, 880, 22, "w")), ((cu - sx, cv - sy), (1039, 885, 22, "w")),
           ((112.0, 111.64), (442, 264, 14, "c")), ((112.0, 10.1), (1125, 279, 14, "c")),
           ((6.47, 112.0), (410, 975, 14, "c")), ((6.8, 10.14), (1120, 985, 14, "c"))]
    src = np.array([ring(*p[1]) for p in pts])
    dst = np.array([PL.base_front_px(*p[0]) for p in pts])
    A = []
    for (x, y), (X, Y) in zip(src, dst):
        A.append([-x, -y, -1, 0, 0, 0, x * X, y * X, X])
        A.append([0, 0, 0, -x, -y, -1, x * Y, y * Y, Y])
    H = np.linalg.svd(np.array(A))[2][-1].reshape(3, 3)
    H /= H[2, 2]

    def ap(Hm, p):
        p = np.c_[p, np.ones(len(p))] @ Hm.T
        return p[:, :2] / p[:, 2:]
    res = np.hypot(*(ap(H, src) - dst).T) / 10.0
    W, Hh = int(139.6 * 10), int(141.5 * 10)
    ys, xs = np.mgrid[0:Hh, 0:W]
    q = ap(np.linalg.inv(H), np.c_[xs.ravel(), ys.ravel()])
    rgb = np.asarray(Image.open(CACHE / "chiphell" / "pcb-b.jpg").convert("RGB"))
    xi = np.clip(np.round(q[:, 0]).astype(int), 0, rgb.shape[1] - 1)
    yi = np.clip(np.round(q[:, 1]).astype(int), 0, rgb.shape[0] - 1)
    Image.fromarray(rgb[yi, xi].reshape(Hh, W, 3)).save(FRONT_PNG)
    print("frente retificada: %s; resíduo nos 8 furos %.2f a %.2f mm" % (FRONT_PNG.name, res.min(), res.max()))
    return {"residual_mm": [round(float(r), 2) for r in res]}


# ---------------------------------------------------------------------------
# Blender
# ---------------------------------------------------------------------------
MATS = {
    "pcb.main": ((0.025, 0.035, 0.03), 0.0, 0.42),
    "gpu.package": ((0.55, 0.47, 0.36), 0.2, 0.45),
    "mem": ((0.035, 0.035, 0.04), 0.0, 0.5),
    "power.inductors": ((0.04, 0.04, 0.045), 0.0, 0.55),
    "power.vrm": ((0.20, 0.20, 0.21), 0.0, 0.65),
    "power.controller": ((0.10, 0.10, 0.11), 0.0, 0.55),
    "power.aux": ((0.50, 0.48, 0.45), 0.0, 0.6),
    "io.aux_header": ((0.03, 0.03, 0.035), 0.0, 0.5),
    "pcb.smd": ((0.42, 0.33, 0.22), 0.2, 0.45),
    "pcb.back_frame": ((0.03, 0.03, 0.035), 0.2, 0.5),
}


def mat_for(name):
    for k in sorted(MATS, key=len, reverse=True):
        if name.startswith(k):
            return k
    return None


def bl_scene(glbs, explode_stage=None):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for f in glbs:
        bpy.ops.import_scene.gltf(filepath=str(f))
    mats = {}
    for k, (c, met, r) in MATS.items():
        m = bpy.data.materials.new(k)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*c, 1)
        b.inputs["Metallic"].default_value = met
        b.inputs["Roughness"].default_value = r
        mats[k] = m
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        k = mat_for(o.name)
        if k:
            o.data.materials.clear()
            o.data.materials.append(mats[k])
    if explode_stage:
        order = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
        lim = order.index(explode_stage)
        for o in bpy.data.objects:
            ex = o.get("explode_cad")
            st = o.get("stage")
            if ex and st in order and order.index(st) <= lim:
                d = ex["dir"]
                o.location = (o.location[0] + d[0] * ex["distance"] / 1000, o.location[1] + d[1] * ex["distance"] / 1000,
                              o.location[2] + d[2] * ex["distance"] / 1000)
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.52, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    sc.world = w
    for rot, en in (((-0.5, 0.35, 0.3), 2.5), ((0.6, -0.4, 2.5), 1.0), ((2.6, 0.2, 0.0), 1.2)):
        L = bpy.data.lights.new("sol", "SUN")
        L.energy = en
        L.angle = 0.3
        lo = bpy.data.objects.new("sol", L)
        sc.collection.objects.link(lo)
        lo.rotation_euler = rot
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "Standard"
    return sc


def bl_camera(sc, center_mm, right, up, ortho_mm=None, size=(1400, 1400), eye_mm=None, lens=50):
    import bpy
    from mathutils import Matrix, Vector
    cam = bpy.data.cameras.new("cam")
    r, u = Vector(right).normalized(), Vector(up).normalized()
    z = r.cross(u)
    if ortho_mm:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho_mm / 1000.0
        pos = Vector(center_mm) / 1000.0 + z * 0.5
    else:
        cam.lens = lens
        pos = Vector(eye_mm) / 1000.0
    cam.clip_start = 0.001
    cam.clip_end = 5
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    m = Matrix.Identity(4)
    for i in range(3):
        m[i][0], m[i][1], m[i][2], m[i][3] = r[i], u[i], z[i], pos[i]
    co.matrix_world = m
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    return co


def look_at(eye, target, up=(0, 0, 1)):
    f = np.array(target, float) - np.array(eye, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return r, u


def render(sc, path, transparent=False):
    import bpy
    sc.render.film_transparent = transparent
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------------------
# Medidas nas fotos
# ---------------------------------------------------------------------------
def copper_mask(im):
    r, b = im[..., 0].astype(int), im[..., 2].astype(int)
    L = im.mean(2)
    return ((r - b > 28) & (L > 95)) | ((L > 170) & (r > 150))


def field_center(mask, to_px, to_uv, u, v, half_u, half_v, search=4.0):
    """Centro do campo de esferas perto de (u, v): caixa de ilhas pequenas mais densa
    (janela deslizante do tamanho do campo), procurada a até `search` mm."""
    from scipy import ndimage
    best = None
    x0, y0 = to_px(u - half_u - search, v - half_v - search)
    x1, y1 = to_px(u + half_u + search, v + half_v + search)
    xa, xb = int(min(x0, x1)), int(max(x0, x1))
    ya, yb = int(min(y0, y1)), int(max(y0, y1))
    sub = mask[max(ya, 0):yb, max(xa, 0):xb].astype(float)
    # ilhas grandes (passivos, indutores) não contam
    lab, n = ndimage.label(sub > 0)
    sizes = ndimage.sum(sub > 0, lab, range(1, n + 1))
    small = np.isin(lab, 1 + np.nonzero(sizes <= 12)[0])
    dens = small.astype(float)
    # janela do campo no quadro da imagem
    pu = abs(to_px(u + half_u, v)[0] - to_px(u - half_u, v)[0]) + abs(to_px(u + half_u, v)[1] - to_px(u - half_u, v)[1])
    pv = abs(to_px(u, v + half_v)[0] - to_px(u, v - half_v)[0]) + abs(to_px(u, v + half_v)[1] - to_px(u, v - half_v)[1])
    horiz_u = abs(to_px(u + 1, v)[0] - to_px(u, v)[0]) > 0.5
    wx, wy = (int(pu), int(pv)) if horiz_u else (int(pv), int(pu))
    s = ndimage.uniform_filter(dens, size=(wy, wx), mode="constant")
    iy, ix = np.unravel_index(np.argmax(s), s.shape)
    px, py = ix + max(xa, 0), iy + max(ya, 0)
    return to_uv(px + 0.5, py + 0.5)


# Leituras manuais do modelador anterior (escala da base, antes da arbitragem), guardadas só
# como histórico; a conferência agora é automática (memory_fields) e na escala corrigida.
MANUAL_ANTIGO = {
    "borda_de_energia_frente": {"u_centros": [31.1, 45.6, 59.75, 74.1], "v_centro": 97.75},
    "borda_de_energia_verso": {"u_centros": [31.5, 45.6, 59.0, 73.25], "v_centro": 97.75},
    "lateral_do_bracket_verso": {"v_centros": [32.85, 47.25, 61.5, 75.5, 89.6], "u_centro": 9.1},
    "nota": "escala da base (dividir pelo fator para comparar); o passo de 14,1 a 14,2 lido aqui dá 13,95 corrigido, como a arbitragem",
}


def photo_balls(path, to_uv):
    """Centros das ilhas pequenas que formam grade de esferas (vizinhas a 0,5 a 0,95 mm), em
    (u, v) reais. Três máscaras, porque o cobre muda de cor ao longo da foto."""
    from scipy import ndimage
    from scipy.spatial import cKDTree
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    L = im.mean(2)
    r, b = im[..., 0], im[..., 2]
    th = L - ndimage.grey_opening(L, size=(9, 9))
    out = []
    for m in (((r - b > 25) & (L > 90)) | ((L > 165) & (r > 140)), (th > 28) & (L > 70), (th > 40) & (L > 60)):
        lab, n = ndimage.label(m)
        idx = np.arange(1, n + 1)
        area = ndimage.sum(m, lab, idx)
        cm = np.array(ndimage.center_of_mass(m, lab, idx))[(area >= 3) & (area <= 30)]
        uv = np.array([to_uv(px, py) for py, px in cm])
        t = cKDTree(uv)
        cnt = np.array([len(x) - 1 for x in t.query_ball_point(uv, 1.05)])
        near = t.query(uv, k=2)[0][:, 1]
        out.append(uv[(cnt >= 3) & (near > 0.5) & (near < 0.95)])
    return out


def field_at(B, u, v, expect):
    """Campo de esferas de um chip perto de (u, v): as duas maiores manchas de ilhas em grade a
    menos de 7,5 mm; centro e extensão pelos percentis 1 e 99."""
    import scipy.sparse as sp
    import scipy.sparse.csgraph as cg
    from scipy.spatial import cKDTree
    Q = B[(np.abs(B[:, 0] - u) < 10) & (np.abs(B[:, 1] - v) < 10)]
    if len(Q) < 50:
        return None
    pairs = cKDTree(Q).query_pairs(1.1, output_type="ndarray")
    A = sp.coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(Q), len(Q)))
    nc, lab = cg.connected_components(A, directed=False)
    sizes = np.bincount(lab)
    cents = [Q[lab == i].mean(0) for i in range(nc)]
    good = sorted([i for i in range(nc) if sizes[i] >= 40 and math.hypot(*(cents[i] - [u, v])) < 7.5], key=lambda i: -sizes[i])[:2]
    if len(good) < 2:
        return None
    Z = Q[np.isin(lab, good)]
    lo, hi = np.percentile(Z, 1, 0), np.percentile(Z, 99, 0)
    ext = hi - lo
    return abs(ext[0] - expect[0]) + abs(ext[1] - expect[1]), (lo + hi) / 2, ext, len(Z)


def memory_fields():
    """Centro do campo de esferas de cada posição de memória nas duas fotos contra a grade.
    Campo esperado de cerca de 13,2 x 11,1 mm (lado de 14 x lado de 12 do chip)."""
    grid, _ = PL.memory_grid()
    res = {}
    for face, path, to_uv in (("frente", FRONT_PNG, front_uv), ("verso", BACK_PNG, back_uv)):
        Bs = photo_balls(path, to_uv)
        rows = []
        for k, (u, v, kind) in enumerate(grid, 1):
            expect = (11.1, 13.2) if kind == "energia" else (13.2, 11.1)
            cands = [c for c in (field_at(B, u, v, expect) for B in Bs) if c is not None and c[0] < 0.8]
            if not cands:
                rows.append({"posicao": k, "fileira": kind, "grade_uv": [round(u, 2), round(v, 2)], "foto_uv": None})
                continue
            _, c, ext, n = min(cands, key=lambda c: c[0])
            rows.append({"posicao": k, "fileira": kind, "grade_uv": [round(u, 2), round(v, 2)],
                         "foto_uv": [round(float(c[0]), 2), round(float(c[1]), 2)], "du": round(float(c[0] - u), 2),
                         "dv": round(float(c[1] - v), 2), "campo_uv": [round(float(ext[0]), 2), round(float(ext[1]), 2)], "ilhas": int(n)})
        ok = [r for r in rows if r["foto_uv"]]
        d = np.array([[r["du"], r["dv"]] for r in ok])
        R_ = {r["posicao"]: r for r in ok}
        pitch = [R_[b]["foto_uv"][1] - R_[a]["foto_uv"][1] for a, b in ((1, 2), (2, 3), (3, 4), (4, 5), (6, 7), (7, 8), (8, 9), (9, 10)) if a in R_ and b in R_]
        pitch += [R_[b]["foto_uv"][0] - R_[a]["foto_uv"][0] for a, b in ((11, 12), (12, 13), (13, 14)) if a in R_ and b in R_]
        lat = [R_[a + 5]["foto_uv"][0] - R_[a]["foto_uv"][0] for a in range(1, 6) if a in R_ and a + 5 in R_]
        res[face] = {"posicoes": rows, "achadas": len(ok),
                     "du_media": round(float(d[:, 0].mean()), 2), "dv_media": round(float(d[:, 1].mean()), 2),
                     "desvio_max": round(float(np.abs(d).max()), 2),
                     "desvio_max_sem_media": round(float(np.abs(d - d.mean(0)).max()), 2),
                     "passo_medio": round(float(np.mean(pitch)), 3), "passo_n": len(pitch),
                     "entre_laterais": [round(float(x), 2) for x in lat], "entre_laterais_grade": round(2 * PL.M("mem_rows_du_from_gpu"), 2)}
    return res


def measure(rows):
    out = {"memoria": memory_fields(), "memoria_manual_antiga": MANUAL_ANTIGO, "gpu": {}}
    im = np.asarray(Image.open(FRONT_PNG).convert("RGB"))
    mask = copper_mask(im)
    bx, by = PL.M("gb202_bga_field_x") / 2, PL.M("gb202_bga_field_y") / 2
    mu, mv = field_center(mask, front_px, front_uv, PL.GU, PL.GV, bx, by, search=4.0)
    out["gpu"] = {"modelo_uv": [PL.GU, PL.GV], "foto_uv": [round(mu, 2), round(mv, 2)], "du": round(mu - PL.GU, 2),
                  "dv": round(mv - PL.GV, 2), "nota": "centro do campo de esferas de %.1f x %.1f na frente retificada (automático, densidade de ilhas; menos confiável que o da memória)" % (2 * bx, 2 * by)}
    grids(out)
    return out


def grids(out):
    """Recortes com grade de 1 mm (u em magenta, v em verde) para conferir as leituras."""
    def crop(png, tp, u0, u1, v0, v1, name, s=2):
        im = Image.open(png).convert("RGB")
        xs = [tp(u, v)[0] for u in (u0, u1) for v in (v0, v1)]
        ys = [tp(u, v)[1] for u in (u0, u1) for v in (v0, v1)]
        x0, y0 = int(min(xs)), int(min(ys))
        c = im.crop((x0, y0, int(max(xs)), int(max(ys))))
        c = c.resize((c.width * s, c.height * s), Image.LANCZOS)
        d = ImageDraw.Draw(c)
        for u in range(int(u0), int(u1) + 1):
            a, b = tp(u, v0), tp(u, v1)
            d.line([((a[0] - x0) * s, (a[1] - y0) * s), ((b[0] - x0) * s, (b[1] - y0) * s)], fill=(255, 0, 255) if u % 5 == 0 else (90, 0, 90))
            if u % 5 == 0:
                d.text(((a[0] - x0) * s + 2, (a[1] - y0) * s + 2), "u%d" % u, fill=(255, 0, 255))
        for v in range(int(v0), int(v1) + 1):
            a, b = tp(u0, v), tp(u1, v)
            d.line([((a[0] - x0) * s, (a[1] - y0) * s), ((b[0] - x0) * s, (b[1] - y0) * s)], fill=(0, 255, 0) if v % 5 == 0 else (0, 90, 0))
            if v % 5 == 0:
                d.text(((a[0] - x0) * s + 2, (a[1] - y0) * s + 2), "v%d" % v, fill=(0, 255, 0))
        c.save(DIST / name)
        out.setdefault("grades", []).append(name)
    crop(FRONT_PNG, front_px, 20, 85, 84, 106, "grade-frente-borda-de-energia.png")
    crop(BACK_PNG, back_px, 20, 85, 84, 106, "grade-verso-borda-de-energia.png")
    crop(BACK_PNG, back_px, 0, 21, 22, 96, "grade-verso-lateral-do-bracket.png")


# ---------------------------------------------------------------------------
# Composição
# ---------------------------------------------------------------------------
def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def label(im, txt, xy=(12, 10), sz=22):
    d = ImageDraw.Draw(im)
    f = font(sz)
    x, y = xy
    for line in txt.split("\n"):
        d.text((x + 1, y + 1), line, fill=(0, 0, 0), font=f)
        d.text((x, y), line, fill=(255, 255, 255), font=f)
        y += sz + 4


OUTLINE_COLORS = {"mem": (0, 200, 255), "gpu": (255, 230, 0), "power.inductors": (255, 40, 40), "power.vrm": (255, 140, 0),
                  "power.controller": (255, 0, 255), "power.aux": (255, 0, 255), "io.aux_header": (255, 0, 255), "pcb.smd": (60, 255, 60)}


def compose(photo, rend, name, title, outline_px, rows, face, to_px):
    ph = Image.open(photo).convert("RGB")
    rd = Image.open(rend).convert("RGBA")
    rd_rgb = Image.alpha_composite(Image.new("RGBA", rd.size, (235, 235, 238, 255)), rd).convert("RGB")
    side = Image.new("RGB", (ph.width + rd.width + 20, max(ph.height, rd.height)), (20, 20, 22))
    side.paste(ph, (0, 0))
    side.paste(rd_rgb, (ph.width + 20, 0))
    label(side, title + "\nesquerda: foto retificada (10 px/mm na escala da base, %.2f px por mm real); direita: modelo na mesma escala" % PL.PHOTO_S)
    side.save(DIST / ("%s-lado-a-lado.png" % name))
    ov = ph.convert("RGBA")
    a = np.asarray(rd).astype(float)
    a[..., 3] *= 0.35
    ov = Image.alpha_composite(ov, Image.fromarray(a.astype(np.uint8)))
    d = ImageDraw.Draw(ov)
    for r in rows:
        if r["lado"] != face:
            continue
        col = next((c for k, c in OUTLINE_COLORS.items() if r["part"].startswith(k)), (255, 255, 255))
        if r["part"] == "gpu.package":
            pts = PL.rect_poly(r["x"], r["y"], PL.M("gb202_bga_field_x"), PL.M("gb202_bga_field_y"), 0)
        else:
            pts = PL.rect_poly(r["x"], r["y"], r["comprimento"], r["largura"], r["rot_deg"])
        q = [to_px(*PL.xy2uv(x, y)) for x, y in pts]
        d.line(q + [q[0]], fill=col + (255,), width=1 if r["part"] == "pcb.smd" else 2)
    for hx, hy, dr, od, k in PL.holes_xy():
        cx, cy = to_px(*PL.xy2uv(hx, hy))
        R = od * 5
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 0, 255, 255), width=2)
    d.line(outline_px + [outline_px[0]], fill=(255, 0, 255, 255), width=2)
    ov = ov.convert("RGB")
    label(ov, title + "\nmodelo a 35 % sobre a foto; contorno, furos e componentes do modelo em linhas\n(memória azul, package e campo de esferas amarelo, indutores vermelho, estágios laranja, passivos verde)")
    ov.save(DIST / ("%s-sobreposta.png" % name))


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    rep = {}
    if "--retificar" in sys.argv or not FRONT_PNG.exists():
        rep["retificacao_frente"] = rectify()
    rows = PL.read_layout()
    glbs = [PARTS_DIR / ("%s.glb" % i) for i in PCB_IDS]
    out = DIST
    # vistas de topo
    sc = bl_scene(glbs)
    # frente: vista de +z, u para a direita, v para cima, no quadro da foto (PHOTO_S px por mm real)
    fw, fh = Image.open(FRONT_PNG).size
    cx, cy = PL.uv2xy(*front_uv(fw / 2, fh / 2))
    bl_camera(sc, (cx, cy, 20), (1, 0, 0), (0, 1, 0), ortho_mm=max(fw, fh) / PL.PHOTO_S, size=(fw, fh))
    render(sc, out / "_frente.png", transparent=True)
    # verso no quadro de a_board.png: direita = +y, cima = +x, olhando de -z
    bw, bh = Image.open(BACK_PNG).size
    cx, cy = PL.uv2xy(*back_uv(bw / 2, bh / 2))
    bl_camera(sc, (cx, cy, 0), (0, 1, 0), (1, 0, 0), ortho_mm=max(bw, bh) / PL.PHOTO_S, size=(bw, bh))
    render(sc, out / "_verso.png", transparent=True)
    poly = PL.outline_uv()
    compose(FRONT_PNG, out / "_frente.png", "01-frente", "Frente do PCB (chip, face A), vista de +z: chiphell/pcb-b retificada pelos 8 furos",
            [front_px(u, v) for u, v in poly], rows, "frente", front_px)
    compose(BACK_PNG, out / "_verso.png", "02-verso", "Verso do PCB (face B), quadro de visualqa/a_board.png (girado 90 graus, como a foto)",
            [back_px(u, v) for u, v in poly], rows, "verso", back_px)
    if "--so-topo" in sys.argv:
        return finish(rep, rows, out)
    # perspectiva da frente, enquadrada como sabareesh/wb-bare-pcb.jpg (contatos embaixo)
    cx, cy = PL.uv2xy(PL.W / 2, PL.H / 2)
    eye = (cx + 4, cy - 30, PL.ZF + 330)
    r, u = look_at(eye, (cx, cy, PL.ZF), up=(0, 1, 0))
    bl_camera(sc, None, r, u, size=(768, 1024), eye_mm=eye, lens=50)
    sc.camera.data.sensor_fit = "VERTICAL"
    sc.camera.data.sensor_height = 36
    # a foto mostra a largura do PCB em 568 de 768 px: lente equivalente a cerca de 55 mm
    sc.camera.data.lens = (36 * 768 / 1024 / 2) / (math.tan(math.atan(PL.W / 2 / 330)) * 768 / 568)
    render(sc, out / "_obliqua.png")
    sab = Image.open(CACHE / "sabareesh" / "wb-bare-pcb.jpg").convert("RGB")
    ob = Image.open(out / "_obliqua.png").convert("RGB")
    side = Image.new("RGB", (sab.width + ob.width + 20, max(sab.height, ob.height)), (20, 20, 22))
    side.paste(sab, (0, 0))
    side.paste(ob, (sab.width + 20, 0))
    label(side, "Frente com componentes: sabareesh/wb-bare-pcb (esquerda) e modelo (direita)\nsem pads térmicos nem pasta; perspectiva parecida, não igual", sz=18)
    side.save(out / "03-obliqua-sabareesh.png")
    # três quartos, para ver alturas
    eye = (cx + 150, cy - 170, PL.ZF + 120)
    r, u = look_at(eye, (cx + 5, cy, PL.ZF))
    bl_camera(sc, None, r, u, size=(1400, 900), eye_mm=eye, lens=50)
    render(sc, out / "04-tres-quartos.png")
    return finish(rep, rows, out)


def finish(rep, rows, out):
    rep["escala"] = {"chiphell_pcb_a_scale_factor": PL.F, "px_por_mm_real": round(PL.PHOTO_S, 3),
                     "centro_do_chip_px": {"frente": [round(c, 2) for c in PL.FRONT_C], "verso": [round(c, 2) for c in PL.BACK_C]}}
    rep["medidas"] = measure(rows)
    if "--integrado" in sys.argv:
        sc = bl_scene([HARNESS / "build" / "card.glb"], explode_stage="E7")
        tgt = (155, 70, -22)
        eye = (330, -150, 10)
        r, u = look_at(eye, tgt)
        bl_camera(sc, None, r, u, size=(1600, 1000), eye_mm=eye, lens=40)
        render(sc, out / "integrado.png")
        im = Image.open(out / "integrado.png").convert("RGB")
        label(im, "build/card.glb no estágio E7: E1 a E7 explodidos (PCB a 40 mm para a face B); frente do PCB, com o chip, voltada para a base do cooler", sz=20)
        im.save(out / "integrado.png")
    for f in ("_frente.png", "_verso.png", "_obliqua.png"):
        (out / f).unlink(missing_ok=True)
    (out / "comparacao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    m = rep["medidas"]
    for face, r in m["memoria"].items():
        print("memória, %s: %d de 16 campos achados; desvio médio (du %+.2f, dv %+.2f), máximo %.2f (%.2f sem o desvio médio); passo medido %.3f (n = %d); entre as fileiras laterais %s (grade %.2f)" % (
            face, r["achadas"], r["du_media"], r["dv_media"], r["desvio_max"], r["desvio_max_sem_media"], r["passo_medio"], r["passo_n"], r["entre_laterais"], r["entre_laterais_grade"]))
    print("GB202, campo de esferas: du %+.2f dv %+.2f" % (m["gpu"]["du"], m["gpu"]["dv"]))
    print("saídas em %s" % DIST.relative_to(HARNESS.parent))


if __name__ == "__main__":
    main()
