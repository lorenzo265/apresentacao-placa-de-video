#!/usr/bin/env python3
"""Comparação da carcaça (frame.*) com os renders da PNY.

Lê harness/build/parts/frame.*.glb (gerados por frame.py), traça raios nas mesmas escala e
posição das imagens pny/front.png e pny/back.png e grava em harness/dist/parts/frame/:

  01-face-a-lado-a-lado.png   referência | modelo (face dos ventiladores)
  02-face-a-sobreposta.png    contornos do modelo sobre a referência
  03-face-b-lado-a-lado.png   idem, face oposta
  04-face-b-sobreposta.png
  05-topo.png                 borda superior do modelo (ortogonal) ao lado das perspectivas
  06-perspectiva.png          modelo em três quartos, para conferir o volume
  comparacao.json             medidas tiradas da referência e do modelo, com a diferença

Calibração (a mesma para tudo): na referência, a carcaça vai do primeiro ao último pixel da
silhueta na altura do centro (304,8 mm, card_envelope_length) e a escala é a mesma nos dois
eixos; o centro vertical da silhueta da carcaça (mediana do topo e da base fora dos contatos)
é y = iface_shroud_center_y. Os renders são quase ortogonais (incerteza de 2 a 3 %, ver
qa/visual-qa-referencias-modelagem.md).

As imagens de referência são material de terceiros (cache não versionado): só lidas.
Rode com:  python3 -I harness/parts/frame_compare.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame as F  # noqa: E402  (medidas e parâmetros da peça)

HARNESS = F.HARNESS
REF = HARNESS / "spec" / "references" / "cache"
DIST = HARNESS / "dist" / "parts" / "frame"
SS = 2                       # supersampling das vistas (pixels do modelo por pixel da referência)
COLORS = {"frame.shroud": (60, 220, 255), "frame.face_b": (255, 210, 40),
          "frame.center_covers": (255, 80, 220), "frame.rim": (90, 255, 120)}
TINT = {"frame.shroud": (0.62, 0.64, 0.68), "frame.face_b": (0.55, 0.57, 0.62),
        "frame.center_covers": (0.80, 0.80, 0.84), "frame.rim": (0.45, 0.47, 0.52)}


# ---------------------------------------------------------------------------
def load_parts():
    meshes = {}
    for pid in F.IDS:
        sc = trimesh.load(F.OUT / ("%s.glb" % pid), force="scene")
        m = sc.to_geometry()
        v = m.vertices
        m = trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]] * 1000.0, m.faces, process=False)
        meshes[pid] = m
    return meshes


class Tracer:
    def __init__(self, meshes):
        import bpy  # noqa: F401
        from mathutils.bvhtree import BVHTree
        V, Fc, pid = [], [], []
        off = 0
        self.ids = list(meshes)
        for k, (p, m) in enumerate(meshes.items()):
            V.append(m.vertices)
            Fc.append(m.faces + off)
            pid.append(np.full(len(m.faces), k))
            off += len(m.vertices)
        self.V, self.F = np.vstack(V), np.vstack(Fc)
        self.pid = np.concatenate(pid)
        self.tree = BVHTree.FromPolygons(self.V.tolist(), self.F.tolist(), epsilon=0.0)

    def cast(self, origins, dirs):
        from mathutils import Vector
        n = len(origins)
        t = np.full(n, np.nan)
        nrm = np.zeros((n, 3))
        part = np.full(n, -1)
        ray = self.tree.ray_cast
        for i in range(n):
            loc, no, idx, dist = ray(Vector(origins[i]), Vector(dirs[i]))
            if loc is not None:
                t[i] = dist
                nrm[i] = no
                part[i] = self.pid[idx]
        return t, nrm, part


def ref_calibration(path, flip):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    fg = (a[:, :, 3] > 128) & (a[:, :, :3].min(2) < 235)
    H, W = fg.shape
    tops, bots = np.full(W, -1), np.full(W, -1)
    for x in range(W):
        c = np.nonzero(fg[:, x])[0]
        if len(c):
            tops[x], bots[x] = c.min(), c.max()
    # comprimento: maior trecho contínuo de cada linha; nas linhas do corpo (trecho de pelo
    # menos 95 % do maior) as pontas têm mediana estável (a aba do bracket fica de fora)
    runs = []
    for y in range(H):
        idx = np.nonzero(fg[y])[0]
        if not len(idx):
            continue
        cuts = np.nonzero(np.diff(idx) > 1)[0]
        starts = np.r_[idx[0], idx[cuts + 1]]
        ends = np.r_[idx[cuts], idx[-1]]
        j = int(np.argmax(ends - starts))
        runs.append((y, starts[j], ends[j]))
    runs = np.array(runs)
    big = runs[(runs[:, 2] - runs[:, 1]) >= 0.95 * (runs[:, 2] - runs[:, 1]).max()]
    x0, x1 = float(np.median(big[:, 1])), float(np.median(big[:, 2]) + 1)
    yrow = int(np.median(big[:, 0]))
    # essas linhas incluem a aba do bracket (cerca de 3 px a mais); a calibração de
    # frame_remeasure.py usa só as linhas da carcaça, com subpixel (correção de 2026-11-10)
    import frame_remeasure as RM
    x0, x1, _ = RM.length_px(a[:, :, 3] / 255.0)
    s = (x1 - x0) / F.L
    W_ = x1 - x0
    mid = slice(int(x0 + 0.6 * W_), int(x0 + 0.9 * W_))          # sem contatos nem bracket
    if not flip:
        top, bot = np.median(tops[mid]), np.median(bots[mid]) + 1
    else:
        top, bot = np.median(tops[mid]), np.median(bots[mid]) + 1
    pyc = (top + bot) / 2
    return {"x0": float(x0), "x1": float(x1), "s": float(s), "pyc": float(pyc), "top": float(top), "bot": float(bot),
            "fg": fg, "flip": flip, "row": yrow}


def to_px(cal, x, y):
    sy = 1 if cal["flip"] else -1
    return cal["x0"] + cal["s"] * x, cal["pyc"] + sy * cal["s"] * (y - F.YC)


def ortho_face(tr, cal, size, from_b):
    W, H = size[0] * SS, size[1] * SS
    px = (np.arange(W) + 0.5) / SS
    py = (np.arange(H) + 0.5) / SS
    gx, gy = np.meshgrid(px, py)
    x = (gx - cal["x0"]) / cal["s"]
    sy = 1 if cal["flip"] else -1
    y = F.YC + (gy - cal["pyc"]) / (sy * cal["s"])
    if from_b:      # face B em z = 0: vista de -z
        o = np.c_[x.ravel(), y.ravel(), np.full(x.size, -100.0)]
        d = np.tile([0, 0, 1.0], (x.size, 1))
    else:           # face A em z = T: vista de +z
        o = np.c_[x.ravel(), y.ravel(), np.full(x.size, F.T + 100)]
        d = np.tile([0, 0, -1.0], (x.size, 1))
    t, n, p = tr.cast(o, d)
    return t.reshape(H, W), n.reshape(H, W, 3), p.reshape(H, W), d[0]


def shade(t, n, p, ids, view_dir, light):
    """Luz de frente (na direção da câmera) mais uma luz de recorte; light aponta da
    superfície para a fonte."""
    H, W = t.shape
    img = np.zeros((H, W, 3)) + np.array([0.08, 0.085, 0.10])
    hit = ~np.isnan(t)
    vd = np.asarray(view_dir, float) if view_dir is not None else -np.asarray(light, float)
    lam = 0.55 * np.clip(-(n @ vd), 0, 1) ** 2 + 0.45 * np.clip(n @ np.asarray(light, float), 0, 1)
    for k, pid in enumerate(ids):
        m = hit & (p == k)
        img[m] = np.array(TINT[pid]) * (0.25 + 0.75 * lam[m, None])
    return img


def edges(t, n, p):
    hit = ~np.isnan(t)
    tt = np.where(hit, t, 1e6)
    e = np.zeros(t.shape, bool)
    for ax in (0, 1):
        for sh in (1,):
            a = np.roll(tt, sh, axis=ax)
            na = np.roll(n, sh, axis=ax)
            pa = np.roll(p, sh, axis=ax)
            ha = np.roll(hit, sh, axis=ax)
            de = np.abs(tt - a) > 0.35
            dn = (np.sum(n * na, axis=2) < math.cos(math.radians(28))) & hit & ha
            dp = (p != pa) & hit & ha
            e |= de | dn | dp | (hit != ha)
    e[0, :] = e[:, 0] = False
    return e


def edge_owner(t, p):
    """Peça dona de cada pixel de contorno (a mais próxima da câmera entre os vizinhos)."""
    tt = np.where(np.isnan(t), 1e6, t)
    best = tt.copy()
    own = p.copy()
    for ax in (0, 1):
        for sh in (1, -1):
            a = np.roll(tt, sh, axis=ax)
            pa = np.roll(p, sh, axis=ax)
            m = a < best
            best[m] = a[m]
            own[m] = pa[m]
    return own


def side_by_side(ref, model, path, titles):
    W = ref.width + model.width
    out = Image.new("RGB", (W, max(ref.height, model.height) + 28), (20, 20, 24))
    out.paste(ref, (0, 28))
    out.paste(model, (ref.width, 28))
    d = ImageDraw.Draw(out)
    d.text((8, 8), titles[0], fill=(235, 235, 235))
    d.text((ref.width + 8, 8), titles[1], fill=(235, 235, 235))
    out.save(path)


def overlay(ref_img, e, own, ids, path, title, cal, extra_lines=()):
    big = ref_img.convert("RGB").resize((ref_img.width * SS, ref_img.height * SS), Image.LANCZOS)
    arr = np.asarray(big).astype(float) * 0.85
    for k, pid in enumerate(ids):
        m = e & (own == k)
        arr[m] = COLORS[pid]
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for (xa, ya, xb, yb, col) in extra_lines:
        pa, pb = to_px(cal, xa, ya), to_px(cal, xb, yb)
        d.line([pa[0] * SS, pa[1] * SS, pb[0] * SS, pb[1] * SS], fill=col, width=1)
    d.rectangle([0, 0, im.width, 30], fill=(20, 20, 24))
    d.text((8, 8), title, fill=(235, 235, 235))
    y = 40
    for k, pid in enumerate(ids):
        d.rectangle([8, y, 22, y + 10], fill=COLORS[pid])
        d.text((28, y - 1), pid, fill=(235, 235, 235))
        y += 16
    im.save(path)


def crop_box(cal, margin_mm=12):
    xa, ya = to_px(cal, -margin_mm, F.Y0 - margin_mm - 15)
    xb, yb = to_px(cal, F.L + margin_mm, F.Y1 + margin_mm)
    x0, x1 = sorted((xa, xb))
    y0, y1 = sorted((ya, yb))
    return [int(x0), int(y0), int(x1), int(y1)]


# ---------------------------------------------------------------------------
# Medidas na referência
# ---------------------------------------------------------------------------
def silhouette_profiles(cal, hitmask):
    """Topo e base da silhueta por coluna (mm), na referência e no modelo."""
    fg = cal["fg"]
    H, W = fg.shape
    res = []
    hm = hitmask[SS // 2::SS, SS // 2::SS]
    for xm in np.arange(4.0, F.L - 4.0, 1.0):
        px = int(round(cal["x0"] + cal["s"] * xm))
        cr = np.nonzero(fg[:, px])[0]
        cm = np.nonzero(hm[:, px])[0] if px < hm.shape[1] else []
        if len(cr) == 0 or len(cm) == 0:
            continue
        def ymm(py):
            sy = 1 if cal["flip"] else -1
            return F.YC + (py - cal["pyc"]) / (sy * cal["s"])
        if not cal["flip"]:
            rt, rb, mt, mb = ymm(cr.min() - 0.5), ymm(cr.max() + 0.5), ymm(cm.min() - 0.5), ymm(cm.max() + 0.5)
        else:
            rt, rb, mt, mb = ymm(cr.max() + 0.5), ymm(cr.min() - 0.5), ymm(cm.max() + 0.5), ymm(cm.min() - 0.5)
        res.append((xm, rt, rb, mt, mb))
    return np.array(res)


def end_profiles(cal, hitmask):
    fg = cal["fg"]
    hm = hitmask[SS // 2::SS, SS // 2::SS]
    res = []
    for ym in np.arange(F.Y0 + 4, F.Y1 - 4, 1.0):
        _, py = to_px(cal, 0, ym)
        py = int(round(py))
        rr = np.nonzero(fg[py])[0]
        mm = np.nonzero(hm[py])[0]
        if len(rr) == 0 or len(mm) == 0:
            continue
        res.append((ym, (rr.max() + 0.5 - cal["x0"]) / cal["s"], (mm.max() + 0.5 - cal["x0"]) / cal["s"]))
    return np.array(res)


def track_x_edges(path, cal, xc0):
    """Bordas das tampas lisas (chanfro claro) ao longo das quatro nervuras; ajuste de reta."""
    g = np.asarray(Image.open(path).convert("RGBA").convert("L"), float)
    k = math.tan(F.ANG)
    out = {}
    for arm, (sx, sy) in {"sup_esq": (-1, 1), "sup_dir": (1, 1), "inf_esq": (-1, -1), "inf_dir": (1, -1)}.items():
        pts = []
        for dy in np.arange(10, 50, 2.0):
            y = F.YC + sy * dy
            xl = xc0 + sx * dy / k
            px, py = to_px(cal, xl, y)
            lo, hi = int(px - 14), int(px + 14)
            row = g[int(round(py)), lo:hi]
            i = int(np.argmax(row))
            pts.append((dy, (lo + i + 0.5 - cal["x0"]) / cal["s"]))
        pts = np.array(pts)
        c = np.polyfit(pts[:, 0], pts[:, 1], 1)
        out[arm] = {"x_no_centro": float(c[1]), "ang_deg": float(math.degrees(math.atan(1 / abs(c[0]))))}
    xs = [v["x_no_centro"] for v in out.values()]
    ang = [v["ang_deg"] for v in out.values()]
    return {"cruzamento_x": float(np.mean(xs)), "cruzamento_dispersao": float(np.std(xs)),
            "angulo_deg": float(np.mean(ang)), "por_nervura": out}


def fit_ring(path, cal, cx_mm, r_lo, r_hi):
    """Borda externa do anel: maior salto de brilho para fora, em 120 raios."""
    g = np.asarray(Image.open(path).convert("RGBA").convert("L"), float)
    cx, cy = to_px(cal, cx_mm, F.FAN_Y)
    pts = []
    for th in np.linspace(0, 2 * np.pi, 120, endpoint=False):
        rs = np.arange(r_lo * cal["s"], r_hi * cal["s"], 0.5)
        xs, ys = cx + rs * np.cos(th), cy + rs * np.sin(th)
        ok = (xs > 1) & (xs < g.shape[1] - 2) & (ys > 1) & (ys < g.shape[0] - 2)
        if ok.sum() < 6:
            continue
        v = g[ys[ok].astype(int), xs[ok].astype(int)]
        i = int(np.argmax(v))
        pts.append((xs[ok][i], ys[ok][i]))
    p = np.array(pts)
    for _ in range(3):
        A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
        c = np.linalg.lstsq(A, (p ** 2).sum(1), rcond=None)[0]
        R = math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)
        res = np.abs(np.hypot(p[:, 0] - c[0], p[:, 1] - c[1]) - R)
        p = p[res < max(2.0, 2.5 * np.median(res))]
    sy = 1 if cal["flip"] else -1
    return {"centro_x": (c[0] - cal["x0"]) / cal["s"], "centro_y": F.YC + (c[1] - cal["pyc"]) / (sy * cal["s"]),
            "diametro": 2 * R / cal["s"], "pontos": int(len(p))}


def corner_fits(cal, mask_img, win_mm=26.0):
    """Raio de cada canto da silhueta: círculo ajustado aos pixels de borda que se afastam
    mais de 0,6 mm das duas retas do contorno. mask_img: máscara na escala da referência."""
    from scipy.ndimage import binary_erosion
    b = mask_img & ~binary_erosion(mask_img)
    pys, pxs = np.nonzero(b)
    sy = 1 if cal["flip"] else -1
    xm = (pxs + 0.5 - cal["x0"]) / cal["s"]
    ym = F.YC + (pys + 0.5 - cal["pyc"]) / (sy * cal["s"])
    out = {}
    for name, (cxe, cye) in {"sup_bracket": (0, F.Y1), "sup_ponta": (F.L, F.Y1),
                             "inf_bracket": (0, F.Y0), "inf_ponta": (F.L, F.Y0)}.items():
        m = (np.abs(xm - cxe) < win_mm) & (np.abs(ym - cye) < win_mm)
        # retas do contorno estimadas pelos próprios pixels longe do canto
        far_x = m & (np.abs(xm - cxe) > win_mm * 0.8)
        far_y = m & (np.abs(ym - cye) > win_mm * 0.8)
        if far_x.sum() < 3 or far_y.sum() < 3:
            out[name] = None
            continue
        ye = np.median(ym[far_x])
        xe = np.median(xm[far_y])
        k = m & (np.abs(ym - ye) > 0.6) & (np.abs(xm - xe) > 0.6)
        if k.sum() < 6:
            out[name] = {"raio_mm": 0.0, "pontos": int(k.sum())}
            continue
        P = np.c_[xm[k], ym[k]]
        A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
        c = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0]
        R = math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)
        out[name] = {"raio_mm": round(R, 1), "pontos": int(k.sum())}
    return out


def notch_from_profile(prof):
    xs, rb = prof[:, 0], prof[:, 2]
    sel = (xs > 130) & (xs < 175)
    base = np.median(rb[(xs > 170) & (xs < 230)])
    m = sel & (rb > base + 1.5)
    if not m.any():
        return None
    return {"x_inicio_visivel": float(xs[m].min()), "x_fim": float(xs[m].max()), "profundidade": float(np.median(rb[m]) - base)}


# ---------------------------------------------------------------------------
def perspective(tr, eye, target, up, fov, size):
    eye, target, up = (np.array(a, float) for a in (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    W, H = size
    foc = 0.5 * H / math.tan(math.radians(fov) / 2)
    gx, gy = np.meshgrid(np.arange(W) + 0.5 - W / 2, np.arange(H) + 0.5 - H / 2)
    d = f[None] * foc + gx.ravel()[:, None] * r[None] - gy.ravel()[:, None] * u[None]
    d /= np.linalg.norm(d, axis=1)[:, None]
    o = np.tile(eye, (len(d), 1))
    t, n, p = tr.cast(o, d)
    return t.reshape(H, W), n.reshape(H, W, 3), p.reshape(H, W), f


NEIGHBORS = ["cooler.fan.1", "cooler.fan.2", "cooler.fan.1.blade", "cooler.fan.2.blade", "cooler.fins.1",
             "cooler.fins.2", "cooler.fins.3", "pcb.main", "io.bracket", "io.board", "io.board.dp", "pcie.adapter",
             "power.connector", "pcb.plate", "fasteners.end_plate", "fasteners.e2_rim", "fasteners.e5_plate",
             "io.aux_header", "flex.dp"]


def clearances(meshes, n_pts=150000):
    """Folga e interferência de cada peça da carcaça com as vizinhas do blockout.
    As vizinhas são corpos convexos (caixas, prismas, cilindros): um ponto está dentro se
    fica atrás de todos os planos das faces, e a profundidade é a menor distância a esses
    planos. Amostra densa da superfície da carcaça: interferência = maior profundidade de
    um ponto da carcaça dentro da vizinha; folga = menor distância entre as superfícies
    (pela árvore da vizinha), quando não há interferência. Corpos não convexos do blockout
    (o bracket) usam só a folga até a superfície."""
    import bpy  # noqa: F401
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import blockout as B
    R = B.build_parts(F.ASM)
    samples = {pid: np.vstack([m.vertices, trimesh.sample.sample_surface(m, n_pts, seed=7)[0]]) for pid, m in meshes.items()}
    out = []
    for nid in NEIGHBORS:
        for pid, pts in samples.items():
            pen, gap = 0.0, np.inf
            for body in B.all_bodies(R, nid):
                lo, hi = body.lo - 3.5, body.hi + 3.5
                sel = np.all((pts >= lo) & (pts <= hi), axis=1)
                if not sel.any():
                    continue
                q = pts[sel]
                bm = body.mesh()
                if body.convex:
                    nrm = bm.face_normals
                    d = np.einsum("ij,ij->i", nrm, bm.triangles[:, 0])
                    sd = q @ nrm.T - d[None, :]             # > 0 fora do plano
                    inside = np.all(sd < -1e-3, axis=1)
                    if inside.any():
                        pen = max(pen, float((-sd[inside]).min(axis=1).max()))
                        continue
                tree = BVHTree.FromPolygons(bm.vertices.tolist(), bm.faces.tolist(), epsilon=0.0)
                step = max(1, len(q) // 4000)
                gap = min(gap, min(tree.find_nearest(Vector(x))[3] for x in q[::step]))
            if pen == 0.0 and gap > 3.0:
                continue
            out.append({"carcaca": pid, "vizinha": nid, "estagio_vizinha": F.PARTS[nid]["stage"] if nid in F.PARTS else None,
                        "interferencia_mm": round(pen, 2), "folga_mm": 0.0 if pen > 0 else round(float(gap), 2)})
    print("\nFolgas e interferências com as peças do blockout (até 3 mm de folga)")
    for r in sorted(out, key=lambda r: (-r["interferencia_mm"], r["folga_mm"])):
        print("    %-20s x %-22s interferência %5.2f mm  folga %5.2f mm" % (r["carcaca"], r["vizinha"], r["interferencia_mm"], r["folga_mm"]))
    return out


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    meshes = load_parts()
    tr = Tracer(meshes)
    ids = tr.ids
    rep = {"calibracao": {}, "silhueta": {}, "feicoes": {}}

    for view, fname, from_b, flip in (("face_a", "front.png", False, False), ("face_b", "back.png", True, True)):
        path = REF / "pny" / fname
        cal = ref_calibration(path, flip)
        rep["calibracao"][view] = {k: v for k, v in cal.items() if k not in ("fg",)}
        ref = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", ref.size, (255, 255, 255, 255))
        ref = Image.alpha_composite(bg, ref).convert("RGB")
        t, n, p, vd = ortho_face(tr, cal, ref.size, from_b)
        light = np.array([-0.45, 0.55, -0.70 if from_b else 0.70])
        light /= np.linalg.norm(light)
        img = shade(t, n, p, ids, vd, light)
        e = edges(t, n, p)
        # só contornos da camada vista (face A ou face B) e da silhueta: o que se vê pelas
        # aberturas (o outro lado da carcaça) não entra na sobreposição
        zhit = np.where(np.isnan(t), np.nan, (t - 100) if from_b else (F.T + 100 - t))
        layer = (zhit <= F.Z_FACE_B + 0.6) if from_b else (zhit >= F.T - F.T_A - F.g("lam_depth_a") - 0.6)
        from scipy.ndimage import binary_fill_holes
        sil = np.zeros_like(e)
        hit = binary_fill_holes(~np.isnan(t))
        for ax in (0, 1):
            sil |= hit != np.roll(hit, 1, axis=ax)
        layer_n = layer.copy()
        for ax in (0, 1):
            for sh_ in (1, -1):
                layer_n |= np.roll(layer, sh_, axis=ax)
        e = (e & layer_n) | sil
        own = edge_owner(t, p)
        model = Image.fromarray((img * 255).clip(0, 255).astype(np.uint8))
        box = crop_box(cal)
        box2 = [b * SS for b in box]
        refc = ref.resize((ref.width * SS, ref.height * SS), Image.LANCZOS).crop(box2)
        n_ = "01" if view == "face_a" else "03"
        side_by_side(refc, model.crop(box2), DIST / ("%s-%s-lado-a-lado.png" % (n_, view.replace("_", "-"))),
                     ("referência: pny/%s (render de terceiro, quase ortogonal)" % fname,
                      "modelo: frame.* na mesma escala (%.3f px/mm x %d)" % (cal["s"], SS)))
        # linhas de referência do CSV: eixos do X e centros dos ventiladores
        xc = F.XA if view == "face_a" else F.XB
        k = math.tan(F.ANG)
        dl = (F.Y1 - F.YC) / k
        extra = [(xc - dl, F.YC + (F.Y1 - F.YC), xc + dl, F.YC - (F.Y1 - F.YC), (255, 90, 90)),
                 (xc - dl, F.YC - (F.Y1 - F.YC), xc + dl, F.YC + (F.Y1 - F.YC), (255, 90, 90))]
        if view == "face_a":
            for fx in F.FAN_X:
                extra += [(fx - 4, F.FAN_Y, fx + 4, F.FAN_Y, (255, 90, 90)), (fx, F.FAN_Y - 4, fx, F.FAN_Y + 4, (255, 90, 90))]
        n_ = "02" if view == "face_a" else "04"
        ov_path = DIST / ("%s-%s-sobreposta.png" % (n_, view.replace("_", "-")))
        overlay(ref, e, own, ids, ov_path,
                "contornos do modelo sobre pny/%s; vermelho: eixos do X e centros dos ventiladores pelo CSV" % fname, cal, extra)
        full = Image.open(ov_path)
        hdr = full.crop([0, 0, full.width, 30 + 16 * len(ids) + 12])
        body = full.crop(box2)
        out = Image.new("RGB", (max(body.width, 700), body.height + hdr.height), (20, 20, 24))
        out.paste(hdr.crop([0, 0, out.width, hdr.height]), (0, 0))
        out.paste(body, (0, hdr.height))
        out.save(ov_path)

        # medidas
        hit = ~np.isnan(t)
        prof = silhouette_profiles(cal, hit)
        ends = end_profiles(cal, hit)
        xs = prof[:, 0]
        clean_top = (xs > 25) & (xs < F.L - 25)
        f0, f1 = F.M("pcie_fingers_start_from_bracket_end"), F.M("shroud_pcie_side_notch_x_end")
        clean_bot = clean_top & ~((xs > f0 - 3) & (xs < f1 + 3))
        dt = prof[clean_top, 1] - prof[clean_top, 3]
        db = prof[clean_bot, 2] - prof[clean_bot, 4]
        de = ends[:, 1] - ends[:, 2]
        sil = {
            "topo_ref_menos_modelo_mm": {"media": round(float(dt.mean()), 2), "max_abs": round(float(np.abs(dt).max()), 2)},
            "base_ref_menos_modelo_mm": {"media": round(float(db.mean()), 2), "max_abs": round(float(np.abs(db).max()), 2)},
            "ponta_oposta_ref_menos_modelo_mm": {"media": round(float(de.mean()), 2), "max_abs": round(float(np.abs(de).max()), 2)},
            "altura_ref_mm": round(float(np.median(prof[clean_bot, 1] - prof[clean_bot, 2])), 2),
            "altura_modelo_mm": round(float(np.median(prof[clean_bot, 3] - prof[clean_bot, 4])), 2),
        }
        # raio dos cantos: círculo ajustado à borda da silhueta, na referência e no modelo
        from scipy.ndimage import binary_fill_holes
        hm = binary_fill_holes(hit)[SS // 2::SS, SS // 2::SS]
        cf_ref, cf_mod = corner_fits(cal, cal["fg"]), corner_fits(cal, hm)
        cr = {k_: {"ref": cf_ref[k_], "modelo": cf_mod[k_]} for k_ in cf_ref}
        cr["inf_bracket"]["nota"] = "ajuste contaminado pelo bracket; vale a subida da base perto da ponta (canto_inf_bracket_subida_mm)"
        sil["raio_dos_cantos"] = cr
        # canto entre o bracket e a borda dos contatos: subida da base em x = 6, 8 e 10 mm
        base_ref = np.median(prof[(xs > 20) & (xs < 40), 2])
        base_mod = np.median(prof[(xs > 20) & (xs < 40), 4])
        sub = {}
        for xq in (6.0, 8.0, 10.0):
            j = int(np.argmin(np.abs(xs - xq)))
            sub["x=%.0f" % xq] = {"ref": round(float(prof[j, 2] - base_ref), 2), "modelo": round(float(prof[j, 4] - base_mod), 2),
                                  "raio_18_daria": round(float(F.RC - math.sqrt(max(F.RC ** 2 - (F.RC - xq) ** 2, 0))), 2)}
        sil["canto_inf_bracket_subida_mm"] = sub
        rep["silhueta"][view] = sil
        feat = {}
        xt = track_x_edges(path, cal, xc)
        feat["x_bordas_das_tampas_ref"] = xt
        feat["x_modelo"] = {"cruzamento_x": xc, "angulo_deg": math.degrees(F.ANG)}
        if view == "face_a":
            rings = []
            for fx in F.FAN_X:
                rf = fit_ring(path, cal, fx, 50, 62)
                rings.append({"ref": {k_: round(v, 2) for k_, v in rf.items()},
                              "modelo": {"centro_x": fx, "centro_y": F.FAN_Y, "diametro_aro": 2 * F.R_RING, "diametro_boca": 2 * F.R_OPEN}})
            feat["aneis"] = rings
            feat["entalhe_ref"] = notch_from_profile(prof)
            feat["entalhe_modelo"] = {"x_inicio": F.M("shroud_pcie_side_notch_x_start"), "x_fim": F.M("shroud_pcie_side_notch_x_end"),
                                      "profundidade": F.M("shroud_pcie_side_notch_depth")}
        else:
            feat["entalhe_ref"] = notch_from_profile(prof)
        rep["feicoes"][view] = feat
        print("[%s] calibração x0 %.1f px, %.4f px/mm, centro vertical %.1f px" % (view, cal["x0"], cal["s"], cal["pyc"]))
        print("    silhueta: topo %+.2f (máx %.2f), base %+.2f (máx %.2f), ponta oposta %+.2f (máx %.2f) mm; altura ref %.2f, modelo %.2f" % (
            sil["topo_ref_menos_modelo_mm"]["media"], sil["topo_ref_menos_modelo_mm"]["max_abs"],
            sil["base_ref_menos_modelo_mm"]["media"], sil["base_ref_menos_modelo_mm"]["max_abs"],
            sil["ponta_oposta_ref_menos_modelo_mm"]["media"], sil["ponta_oposta_ref_menos_modelo_mm"]["max_abs"],
            sil["altura_ref_mm"], sil["altura_modelo_mm"]))
        print("    canto bracket/contatos, subida da base (ref / modelo / raio 18 daria): " + ", ".join("%s %.2f/%.2f/%.2f" % (k_, v["ref"], v["modelo"], v["raio_18_daria"]) for k_, v in sil["canto_inf_bracket_subida_mm"].items()))
        print("    raio dos cantos (ref / modelo): " + ", ".join("%s %s/%s" % (k_, v["ref"] and v["ref"]["raio_mm"], v["modelo"] and v["modelo"]["raio_mm"]) for k_, v in cr.items()))
        print("    X: ref cruza em %.1f (dispersão %.1f), %.1f graus; modelo %.1f, %.1f graus" % (
            xt["cruzamento_x"], xt["cruzamento_dispersao"], xt["angulo_deg"], xc, math.degrees(F.ANG)))
        if view == "face_a":
            for r_ in feat["aneis"]:
                print("    anel: ref centro (%.1f, %.1f) diâmetro %.1f; modelo (%.1f, %.1f) aro %.1f" % (
                    r_["ref"]["centro_x"], r_["ref"]["centro_y"], r_["ref"]["diametro"], r_["modelo"]["centro_x"], r_["modelo"]["centro_y"], r_["modelo"]["diametro_aro"]))
        print("    entalhe (silhueta da ref): %s" % feat["entalhe_ref"])

    # topo: ortogonal de cima, lado a lado com as perspectivas
    s = 3.0
    W, H = int((F.L + 20) * s), int((F.T + 20) * s)
    gx, gy = np.meshgrid((np.arange(W) + 0.5) / s - 10, (np.arange(H) + 0.5) / s - 10)
    o = np.c_[gx.ravel(), np.full(gx.size, F.Y1 + 100), (F.T - gy).ravel()]
    d = np.tile([0, -1.0, 0], (gx.size, 1))
    t, n, p = tr.cast(o, d)
    t, n, p = t.reshape(H, W), n.reshape(H, W, 3), p.reshape(H, W)
    light = np.array([-0.3, 0.85, 0.4])
    light /= np.linalg.norm(light)
    img = shade(t, n, p, ids, None, light)
    depth = np.where(np.isnan(t), 0, t - 100)            # mm abaixo do topo da carcaça
    img *= np.clip(1 - 0.12 * depth, 0.25, 1)[..., None]
    top = Image.fromarray((img * 255).clip(0, 255).astype(np.uint8))
    dtop = ImageDraw.Draw(top)
    dtop.text((6, 4), "modelo, borda superior vista de cima (face A, dos ventiladores, em cima; bracket à esquerda), %.0f px/mm" % s, fill=(235, 235, 235))
    persp = [Image.open(REF / "pny" / "3qtr-top-right.png").convert("RGBA"), Image.open(REF / "pny" / "3qtr-top-left.png").convert("RGBA")]
    persp = [Image.alpha_composite(Image.new("RGBA", q.size, (255, 255, 255, 255)), q).convert("RGB").resize((460, 460)) for q in persp]
    sheet = Image.new("RGB", (max(top.width, 920), top.height + 490), (20, 20, 24))
    sheet.paste(top, (0, 0))
    sheet.paste(persp[0], (0, top.height + 30))
    sheet.paste(persp[1], (460, top.height + 30))
    ImageDraw.Draw(sheet).text((6, top.height + 10), "referências em perspectiva (sem escala): pny/3qtr-top-right e pny/3qtr-top-left", fill=(235, 235, 235))
    sheet.save(DIST / "05-topo.png")

    # perspectiva de conferência (referencial corrigido: sem espelhar a imagem)
    c = np.array([F.L / 2, (F.Y0 + F.Y1) / 2, F.T / 2])
    t, n, p, f = perspective(tr, c + np.array([-260, 330, 330]), c, [0, 1, 0], 34, (1100, 800))
    light = np.array([-0.4, 0.8, 0.45])
    light /= np.linalg.norm(light)
    img = shade(t, n, p, ids, f, light)
    im = Image.fromarray((img * 255).clip(0, 255).astype(np.uint8))
    ImageDraw.Draw(im).text((8, 8), "modelo em três quartos (face A e borda superior), como pny/3qtr-top-right", fill=(235, 235, 235))
    im.save(DIST / "06-perspectiva.png")
    t, n, p, f = perspective(tr, c + np.array([260, 330, -400]), c, [0, 1, 0], 34, (1100, 800))
    light = np.array([0.4, 0.8, -0.45])
    light /= np.linalg.norm(light)
    img = shade(t, n, p, ids, f, light)
    im = Image.fromarray((img * 255).clip(0, 255).astype(np.uint8))
    ImageDraw.Draw(im).text((8, 8), "modelo em três quartos (face B e borda superior)", fill=(235, 235, 235))
    im.save(DIST / "07-perspectiva-face-b.png")

    rep["folgas"] = clearances(meshes)
    (DIST / "comparacao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("Imagens e comparacao.json em %s" % DIST.relative_to(HARNESS.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
