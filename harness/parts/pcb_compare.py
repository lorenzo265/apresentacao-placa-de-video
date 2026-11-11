#!/usr/bin/env python3
"""Comparação do PCB principal modelado com as fotos retificadas (F3).

1. --retificar: retifica chiphell/pcb-b.jpg (frente do PCB nu) pelos 8 furos (4 da mola,
   pelo CSV; 4 de canto, medidos em a_board.png) para o quadro da frente vista de +z, a
   10 px/mm: px = (u + 10) * 10, py = (131,5 - v) * 10. Grava no cache (não versionado):
   spec/references/cache/visualqa/pcb_b_front.png.
2. Vistas de topo do modelo (Blender, câmera ortográfica) na escala das fotos: frente no
   quadro acima; verso no quadro de visualqa/a_board.png (px = 683,3 + 10 (v - 61),
   py = 705,6 - 10 (u - 52,7), calibrado pelos 4 furos da mola). Lado a lado e sobreposta.
3. Medidas: centro dos campos de esferas de cada chip de memória nas duas fotos contra a
   tabela, campo de esferas do GB202, bordas do PCB.
4. Vista em perspectiva da frente contra sabareesh/wb-bare-pcb.jpg.
5. --integrado: vista do estágio E7 (PCB afastado) a partir de build/card.glb.

Uso:   python3 -I harness/parts/pcb_compare.py [--retificar] [--integrado]
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
FRONT_PNG = CACHE / "visualqa" / "pcb_b_front.png"
BACK_PNG = CACHE / "visualqa" / "a_board.png"
PCB_IDS = ("pcb.main", "gpu.package", "mem.front", "mem.back", "power.inductors", "power.vrm.gpu", "power.vrm.mem",
           "power.controller", "power.aux", "io.aux_header", "pcb.smd")


# ---------------------------------------------------------------------------
# Quadros das fotos
# ---------------------------------------------------------------------------
def front_px(u, v):
    return (u + 10.0) * 10.0, (131.5 - v) * 10.0


def back_px(u, v):
    return 683.3 + 10.0 * (v - PL.GV), 705.6 - 10.0 * (u - PL.GU)


def front_uv(px, py):
    return px / 10.0 - 10.0, 131.5 - py / 10.0


def back_uv(px, py):
    return PL.GU - (py - 705.6) / 10.0, PL.GV + (px - 683.3) / 10.0


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
    cu, cv = PL.GU, PL.GV
    sx, sy = PL.M("iface_spring_holes_dx") / 2, PL.M("iface_spring_holes_dy") / 2
    # (u, v) dos furos: mola pelo CSV; cantos medidos em a_board.png (um dos quatro do CSV não confirmado)
    pts = [((cu + sx, cv + sy), (518, 442, 22, "w")), ((cu + sx, cv - sy), (1042, 459, 22, "w")),
           ((cu - sx, cv + sy), (502, 880, 22, "w")), ((cu - sx, cv - sy), (1039, 885, 22, "w")),
           ((112.0, 111.64), (442, 264, 14, "c")), ((112.0, 10.1), (1125, 279, 14, "c")),
           ((6.47, 112.0), (410, 975, 14, "c")), ((6.8, 10.14), (1120, 985, 14, "c"))]
    src = np.array([ring(*p[1]) for p in pts])
    dst = np.array([front_px(*p[0]) for p in pts])
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


def measure(rows):
    out = {"memoria": {}, "gpu": {}}
    for face, png, to_px, to_uv, pid in (("verso", BACK_PNG, back_px, back_uv, "mem.back"),
                                         ("frente", FRONT_PNG, front_px, front_uv, "mem.front")):
        im = np.asarray(Image.open(png).convert("RGB"))
        mask = copper_mask(im)
        lst = []
        for r in sorted([r for r in rows if r["part"] == pid], key=lambda r: r["instance"]):
            u, v = PL.xy2uv(r["x"], r["y"])
            # campo de esferas: 13 ao longo da fileira, 15,5 atravessado (CSV)
            a, c = PL.M("mem_footprint_across_row") / 2, PL.M("mem_footprint_along_row") / 2
            hu, hv = (a, c) if r["rot_deg"] == 0 else (c, a)
            mu, mv = field_center(mask, to_px, to_uv, u, v, hu, hv)
            lst.append({"instance": r["instance"], "modelo_uv": [round(u, 2), round(v, 2)], "foto_uv": [round(mu, 2), round(mv, 2)],
                        "du": round(mu - u, 2), "dv": round(mv - v, 2)})
        out["memoria"][face] = lst
        if face == "frente":
            bx, by = PL.M("gb202_bga_field_x") / 2, PL.M("gb202_bga_field_y") / 2
            mu, mv = field_center(mask, to_px, to_uv, PL.GU, PL.GV, bx, by, search=4.0)
            out["gpu"] = {"modelo_uv": [PL.GU, PL.GV], "foto_uv": [round(mu, 2), round(mv, 2)],
                          "du": round(mu - PL.GU, 2), "dv": round(mv - PL.GV, 2),
                          "nota": "centro do campo de esferas de %.0f x %.0f na frente retificada" % (2 * bx, 2 * by)}
    return out


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


def compose(photo, rend, name, title, outline_px):
    ph = Image.open(photo).convert("RGB")
    rd = Image.open(rend).convert("RGBA")
    rd_rgb = Image.alpha_composite(Image.new("RGBA", rd.size, (235, 235, 238, 255)), rd).convert("RGB")
    side = Image.new("RGB", (ph.width + rd.width + 20, max(ph.height, rd.height)), (20, 20, 22))
    side.paste(ph, (0, 0))
    side.paste(rd_rgb, (ph.width + 20, 0))
    label(side, title + "\nesquerda: foto retificada (10 px/mm); direita: modelo na mesma escala")
    side.save(DIST / ("%s-lado-a-lado.png" % name))
    ov = ph.convert("RGBA")
    a = np.asarray(rd).astype(float)
    a[..., 3] *= 0.55
    ov = Image.alpha_composite(ov, Image.fromarray(a.astype(np.uint8)))
    d = ImageDraw.Draw(ov)
    d.line(outline_px + [outline_px[0]], fill=(255, 0, 255, 255), width=2)
    ov = ov.convert("RGB")
    label(ov, title + "\nmodelo a 55 %% sobre a foto; contorno do modelo em magenta")
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
    # frente: vista de +z, u para a direita, v para cima; quadro de 139,6 x 141,5 mm
    cx, cy = PL.uv2xy(59.8, 60.75)
    bl_camera(sc, (cx, cy, 20), (1, 0, 0), (0, 1, 0), ortho_mm=141.5, size=(1396, 1415))
    render(sc, out / "_frente.png", transparent=True)
    # verso no quadro de a_board.png: direita = +y, cima = +x, olhando de -z
    u0, u1 = back_uv(0, 1330)[0], back_uv(0, 0)[0]
    v0, v1 = back_uv(0, 0)[1], back_uv(1400, 0)[1]
    cx, cy = PL.uv2xy((u0 + u1) / 2, (v0 + v1) / 2)
    bl_camera(sc, (cx, cy, 0), (0, 1, 0), (1, 0, 0), ortho_mm=140.0, size=(1400, 1330))
    render(sc, out / "_verso.png", transparent=True)
    poly = PL.outline_uv()
    compose(FRONT_PNG, out / "_frente.png", "01-frente", "Frente do PCB (chip, face A), vista de +z: chiphell/pcb-b retificada pelos 8 furos",
            [front_px(u, v) for u, v in poly])
    compose(BACK_PNG, out / "_verso.png", "02-verso", "Verso do PCB (face B), quadro de visualqa/a_board.png (girado 90 graus, como a foto)",
            [back_px(u, v) for u, v in poly])
    # perspectiva da frente, enquadrada como sabareesh/wb-bare-pcb.jpg (contatos embaixo)
    cx, cy = PL.uv2xy(59.8, 60.75)
    eye = (cx + 4, cy - 30, PL.ZF + 330)
    r, u = look_at(eye, (cx, cy, PL.ZF), up=(0, 1, 0))
    bl_camera(sc, None, r, u, size=(768, 1024), eye_mm=eye, lens=50)
    sc.camera.data.sensor_fit = "VERTICAL"
    sc.camera.data.sensor_height = 36
    # a foto mostra os 119,6 mm do PCB em 568 de 768 px: lente equivalente a cerca de 55 mm
    sc.camera.data.lens = (36 * 768 / 1024 / 2) / (math.tan(math.atan(59.8 / 330)) * 768 / 568)
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
    for face, lst in m["memoria"].items():
        du = np.array([x["du"] for x in lst])
        dv = np.array([x["dv"] for x in lst])
        print("memória %-6s: du médio %+.2f (%+.2f a %+.2f), dv médio %+.2f (%+.2f a %+.2f) mm" % (face, du.mean(), du.min(), du.max(), dv.mean(), dv.min(), dv.max()))
        for x in lst:
            if abs(x["du"]) > 1.0 or abs(x["dv"]) > 1.0:
                print("    %d: du %+.2f dv %+.2f" % (x["instance"], x["du"], x["dv"]))
    print("GB202, campo de esferas: du %+.2f dv %+.2f" % (m["gpu"]["du"], m["gpu"]["dv"]))
    print("saídas em %s" % DIST.relative_to(HARNESS.parent))


if __name__ == "__main__":
    main()
