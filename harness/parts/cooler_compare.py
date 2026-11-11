#!/usr/bin/env python3
"""Comparação do interior do cooler (cooler.py) com as referências (F3).

Renderiza em Blender (Cycles), com os materiais do viewer (viewer/src/materials.json: cor,
metal e rugosidade de cada peça; sem as texturas procedurais), e grava em
harness/dist/parts/cooler/:

  01-face-b-lado-a-lado.png    pny/back | card.glb integrado (aletas em lâminas) | o mesmo com as
                               pilhas das pontas como caixa (como era no blockout), vista
                               ortográfica de -z com os contatos para cima, na escala do render
  02-face-b-zoom.png           recorte da grade do lado do bracket nas três imagens, ampliado
  03-tres-quartos.png          pny/3qtr-top-right | card.glb integrado, câmera de fan_compare.py
                               (ajustada à silhueta do render)
  04-cooler-face-a.png         cooler isolado (7 peças), do lado dos ventiladores, ao lado de
                               rtx5090/wccftech-cooler-3 e -4 (placa irmã)
  05-cooler-base.png           cooler isolado do lado da face B (face de contato, moldura,
                               tubos), ao lado de rtx5090/wccftech-cooler-1 e -5 e de gn-34
  06-cooler-explodido.png      as 7 peças afastadas como no estágio E8 (direções do assembly)
  comparacao.json              números: brilho médio, percentis, contraste e período das listras
                               nas regiões das grades (referência, modelo e modelo com caixa)

Calibração da vista da face B: a de frame_compare.py (comprimento da carcaça sem o bracket,
centro vertical da silhueta). As imagens de referência são material de terceiros: só lidas.

Uso:   python3 -I harness/parts/cooler_compare.py
"""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cooler as C  # noqa: E402
import frame_compare as FC  # noqa: E402

HARNESS = C.HARNESS
REF = HARNESS / "spec" / "references" / "cache"
DIST = HARNESS / "dist" / "parts" / "cooler"
CARD = HARNESS / "build" / "card.glb"
MATS = json.loads((HARNESS / "viewer" / "src" / "materials.json").read_text(encoding="utf-8"))
SS = 2                    # supersampling dos renders ortográficos
SAMPLES = 48
# regiões de medida na face B (mm, referencial CAD): miolo das duas grades, longe do X, do aro
# e do recorte do adaptador PCIe
REGIONS = {"grade_bracket": (22.0, 82.0, 45.0, 118.0), "grade_ponta": (225.0, 285.0, 30.0, 118.0)}

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
except OSError:
    FONT = ImageFont.load_default()


# ---------------------------------------------------------------------------
# Blender
# ---------------------------------------------------------------------------
def srgb_lin(h):
    c = [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def material_key(obj):
    """Material do viewer pela mesma ordem de materials.json: id do nó ou de um ancestral,
    padrão de nome, grupo, padrão."""
    o = obj
    names = []
    while o is not None:
        names.append(re.sub(r"\.\d{3}$", "", o.name))
        o = o.parent
    for n in names:
        if n in MATS["pecas"]:
            return MATS["pecas"][n]
    for n in names:
        for p in MATS["padroes"]:
            if re.search(p["regex"], n):
                return p["material"]
    for n in names:
        grp = n.split(".")[0]
        if grp in ("frame",):
            return "carcaca.anodizado"
        if grp in ("cooler",):
            return MATS["grupos"]["cooler"]
        if grp in ("pcb", "gpu"):
            return "pcb.mascara"
        if grp in ("io",):
            return MATS["grupos"]["io"]
    return MATS["padrao"]


def bl_reset():
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "Standard"
    return sc


def bl_import(paths):
    import bpy
    for p in paths:
        bpy.ops.import_scene.gltf(filepath=str(p))
    mats = {}
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        k = material_key(o)
        if k not in mats:
            spec = MATS["materiais"][k]
            m = bpy.data.materials.new(k)
            m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]
            b.inputs["Base Color"].default_value = (*srgb_lin(spec["cor"]), 1)
            b.inputs["Metallic"].default_value = spec.get("metal", 0.0)
            b.inputs["Roughness"].default_value = spec.get("rug", 0.5)
            mats[k] = m
        o.data.materials.clear()
        o.data.materials.append(mats[k])
    return mats


def bl_studio(sc, bg=1.0):
    """Estúdio claro e difuso, como os renders de produto da PNY."""
    import bpy
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (bg, bg, bg, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.55
    sc.world = w
    for rot, en in (((-0.6, 0.4, 0.2), 2.2), ((2.5, -0.3, 0.4), 1.6), ((0.9, 0.9, 2.2), 0.8)):
        L = bpy.data.lights.new("sol", "SUN")
        L.energy = en
        L.angle = 0.25
        lo = bpy.data.objects.new("sol", L)
        sc.collection.objects.link(lo)
        lo.rotation_euler = rot


def bl_camera(sc, r, u, pos_mm, size, ortho_mm=None, lens_px=None):
    import bpy
    from mathutils import Matrix, Vector
    cam = bpy.data.cameras.new("cam")
    r, u = Vector(r).normalized(), Vector(u).normalized()
    z = r.cross(u)
    if ortho_mm:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho_mm / 1000.0
    else:
        cam.sensor_fit = "HORIZONTAL"
        cam.sensor_width = 36.0
        cam.lens = lens_px / size[0] * 36.0
    cam.clip_start = 0.001
    cam.clip_end = 10
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    pos = Vector(pos_mm) / 1000.0
    m = Matrix.Identity(4)
    for i in range(3):
        m[i][0], m[i][1], m[i][2], m[i][3] = r[i], u[i], z[i], pos[i]
    co.matrix_world = m
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100


def bl_render(sc, path, transparent=True):
    import bpy
    sc.render.film_transparent = transparent
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def boxify(prefixes):
    """Troca as malhas cujos nomes começam pelos prefixos pela caixa envolvente (a pilha de
    aletas como era no blockout), com o mesmo material."""
    import bpy
    import bmesh
    from mathutils import Vector
    for o in list(bpy.data.objects):
        if o.type != "MESH" or not any(o.name.startswith(p) for p in prefixes):
            continue
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = Vector((min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws)))
        hi = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
        me = bpy.data.meshes.new(o.name + "_caixa")
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector(((v.co.x + 0.5) * (hi.x - lo.x) + lo.x, (v.co.y + 0.5) * (hi.y - lo.y) + lo.y, (v.co.z + 0.5) * (hi.z - lo.z) + lo.z))
        bm.to_mesh(me)
        bm.free()
        me.materials.append(o.data.materials[0])
        nb = bpy.data.objects.new(o.name + "_caixa", me)
        bpy.context.scene.collection.objects.link(nb)
        o.hide_render = True


# ---------------------------------------------------------------------------
# Medidas nas imagens
# ---------------------------------------------------------------------------
STAGE = (12, 13, 15)      # fundo quase preto do tema Keynote


def on_white(path, bg=(255, 255, 255)):
    im = Image.open(path).convert("RGBA")
    return Image.alpha_composite(Image.new("RGBA", im.size, (*bg, 255)), im).convert("RGB")


def alpha_of(path, size):
    return np.asarray(Image.open(path).convert("RGBA").resize(size, Image.LANCZOS))[..., 3] / 255.0


def lum(im):
    a = np.asarray(im).astype(float)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def region_px(cal, reg):
    x0, x1, y0, y1 = reg
    p0 = FC.to_px(cal, x0, y0)
    p1 = FC.to_px(cal, x1, y1)
    return int(round(min(p0[0], p1[0]))), int(round(max(p0[0], p1[0]))), int(round(min(p0[1], p1[1]))), int(round(max(p0[1], p1[1])))


def stats(L, box, s):
    a0, a1, b0, b1 = box
    sub = L[b0:b1, a0:a1]
    prof = sub.mean(axis=0) - sub.mean()
    spec = np.abs(np.fft.rfft(prof * np.hanning(len(prof))))
    fr = np.fft.rfftfreq(len(prof), d=1.0 / s)          # ciclos por mm
    band = (fr > 1 / 4.0) & (fr < 1 / 0.6)
    k = np.argmax(np.where(band, spec, 0))
    p10, p50, p90 = np.percentile(sub, [10, 50, 90])
    return {"media": round(float(sub.mean()), 1), "p10": round(float(p10), 1), "mediana": round(float(p50), 1),
            "p90": round(float(p90), 1), "desvio_colunas": round(float(prof.std()), 2),
            "periodo_listras_mm": round(float(1 / fr[k]), 3) if fr[k] > 0 else None,
            "forca_listras": round(float(spec[k] / max(spec[band].mean(), 1e-9)), 2)}


def label(im, txt, xy=(8, 6), fill=(30, 30, 30)):
    ImageDraw.Draw(im).text(xy, txt, font=FONT, fill=fill)
    return im


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------
def face_b(rep):
    cal = FC.ref_calibration(REF / "pny" / "back.png", True)
    s = cal["s"]
    W = H = 800
    # centro da imagem no CAD e câmera ortográfica de -z, contatos para cima
    xc = (W / 2 - cal["x0"]) / s
    yc = C.YC + (H / 2 - cal["pyc"]) / s
    outs = {}
    for tag, box in (("modelo", False), ("caixa", True)):
        sc = bl_reset()
        bl_import([CARD])
        if box:
            boxify(("cooler.fins.1", "cooler.fins.2"))
        bl_studio(sc)
        bl_camera(sc, (1, 0, 0), (0, -1, 0), (xc, yc, -500.0), (W * SS, H * SS), ortho_mm=W / s)
        p = DIST / ("_face_b_%s.png" % tag)
        bl_render(sc, p)
        outs[tag] = on_white(p, STAGE).resize((W, H), Image.LANCZOS)
        outs[tag + "_alfa"] = alpha_of(p, (W, H))
        p.unlink()
    ref = on_white(REF / "pny" / "back.png", STAGE)
    res = {"calibracao": {"px_por_mm": round(s, 4), "x0_px": round(cal["x0"], 2), "pyc_px": round(cal["pyc"], 2)}, "regioes_mm": REGIONS}
    Ls = {"referencia": lum(ref), "modelo": lum(outs["modelo"]), "caixa": lum(outs["caixa"])}
    for rn, reg in REGIONS.items():
        bx = region_px(cal, reg)
        res[rn] = {k: stats(Lk, bx, s) for k, Lk in Ls.items()}
        a0, a1, b0, b1 = bx
        for k in ("modelo", "caixa"):
            res[rn][k]["fracao_vazada"] = round(float(1 - outs[k + "_alfa"][b0:b1, a0:a1].mean()), 3)
    rep["face_b"] = res
    # lado a lado com as regiões marcadas
    sheet = Image.new("RGB", (W * 3, H + 30), STAGE)
    for k, (im, t) in enumerate(((ref, "pny/back (render da PNY)"), (outs["modelo"], "modelo: aletas em lâminas (cooler.py)"),
                                 (outs["caixa"], "modelo com as pilhas das pontas em caixa (antes)"))):
        im = im.copy()
        d = ImageDraw.Draw(im)
        for reg in REGIONS.values():
            a0, a1, b0, b1 = region_px(cal, reg)
            d.rectangle([a0, b0, a1, b1], outline=(0, 170, 255), width=1)
        sheet.paste(im, (k * W, 30))
        label(sheet, t + " (fundo do tema Keynote)", (k * W + 8, 6), (230, 230, 230))
    sheet.save(DIST / "01-face-b-lado-a-lado.png")
    # zoom da grade do lado do bracket
    a0, a1, b0, b1 = region_px(cal, (14.0, 64.0, 60.0, 100.0))
    z = 6
    tiles = [im.crop((a0, b0, a1, b1)).resize(((a1 - a0) * z, (b1 - b0) * z), Image.NEAREST) for im in (ref, outs["modelo"], outs["caixa"])]
    zs = Image.new("RGB", (tiles[0].width * 3 + 20, tiles[0].height + 30), STAGE)
    for k, (t, txt) in enumerate(zip(tiles, ("pny/back", "lâminas", "caixa (antes)"))):
        zs.paste(t, (k * (t.width + 10), 30))
        label(zs, txt + ", grade do lado do bracket (x 14 a 64, y 60 a 100 mm), %dx" % z, (k * (t.width + 10) + 6, 6), (230, 230, 230))
    zs.save(DIST / "02-face-b-zoom.png")
    for rn in REGIONS:
        r = res[rn]
        print("[face B] %-14s média %5.1f / %5.1f / %5.1f  p10 %5.1f / %5.1f / %5.1f  listras %s / %s / %s mm (ref / lâminas / caixa)" % (
            rn, r["referencia"]["media"], r["modelo"]["media"], r["caixa"]["media"], r["referencia"]["p10"], r["modelo"]["p10"], r["caixa"]["p10"],
            r["referencia"]["periodo_listras_mm"], r["modelo"]["periodo_listras_mm"], r["caixa"]["periodo_listras_mm"]))
        print("         vazado (fundo visto através da placa): lâminas %.3f, caixa %.3f" % (r["modelo"]["fracao_vazada"], r["caixa"]["fracao_vazada"]))


def fan_camera():
    """Câmera de três quartos ajustada por fan_compare.py à silhueta de pny/3qtr-top-right."""
    import fan_compare as FNC
    js = json.loads((HARNESS / "dist" / "parts" / "fan" / "comparacao.json").read_text(encoding="utf-8"))["tres_quartos"]["camera"]
    cam = [math.radians(js["az_deg"]), math.radians(js["el_deg"]), math.radians(js["roll_deg"]), js["dist_mm"], js["focal_px"], *js["alvo"]]
    f, r, u = FNC.basis(*cam[:3])
    tgt = np.array(cam[5:])
    return f, r, u, tgt - f * cam[3], cam[4]


def three_quarter(rep):
    ref = on_white(REF / "pny" / "3qtr-top-right.png", STAGE)
    size = ref.size[0]
    f, r, u, eye, foc = fan_camera()
    out = {}
    for tag, box in (("modelo", False), ("caixa", True)):
        sc = bl_reset()
        bl_import([CARD])
        if box:
            boxify(("cooler.fins.1", "cooler.fins.2"))
        bl_studio(sc)
        bl_camera(sc, r, u, eye, (size * SS, size * SS), lens_px=foc * SS)
        p = DIST / ("_3q_%s.png" % tag)
        bl_render(sc, p)
        out[tag] = on_white(p, STAGE).resize(ref.size, Image.LANCZOS)
        p.unlink()
    # brilho no anel dos dois rotores (onde as aletas aparecem entre as pás), projetado
    import fan_compare as FNC
    js = json.loads((HARNESS / "dist" / "parts" / "fan" / "comparacao.json").read_text(encoding="utf-8"))["tres_quartos"]["camera"]
    cam = [math.radians(js["az_deg"]), math.radians(js["el_deg"]), math.radians(js["roll_deg"]), js["dist_mm"], js["focal_px"], *js["alvo"]]
    res = {}
    for k, fx in enumerate((C.M("fan1_center_from_bracket_end"), C.M("fan2_center_from_bracket_end"))):
        th = np.linspace(0, 2 * math.pi, 180)
        mask = Image.new("L", ref.size, 0)
        dr = ImageDraw.Draw(mask)
        ro = [(fx + 54 * math.cos(t), C.YC + 54 * math.sin(t), C.T - 2) for t in th]
        ri = [(fx + 24 * math.cos(t), C.YC + 24 * math.sin(t), C.T - 2) for t in th]
        qo, *_ = FNC.project(np.array(ro), cam, size)
        qi, *_ = FNC.project(np.array(ri), cam, size)
        dr.polygon([tuple(p) for p in qo], fill=1)
        dr.polygon([tuple(p) for p in qi], fill=0)
        mk = np.asarray(mask, bool)
        res["ventilador_%d" % (k + 1)] = {t: {"media": round(float(lum(im)[mk].mean()), 1), "p10": round(float(np.percentile(lum(im)[mk], 10)), 1)}
                                         for t, im in (("referencia", ref), ("modelo", out["modelo"]), ("caixa", out["caixa"]))}
    rep["tres_quartos"] = {"camera": "fan_compare.py (dist/parts/fan/comparacao.json)", "anel_dos_rotores": res}
    sheet = Image.new("RGB", (size * 3, ref.size[1] + 30), STAGE)
    for k, (im, t) in enumerate(((ref, "pny/3qtr-top-right"), (out["modelo"], "card.glb integrado, aletas em lâminas"), (out["caixa"], "pilhas das pontas em caixa (antes)"))):
        sheet.paste(im, (k * size, 30))
        label(sheet, t, (k * size + 8, 6), (230, 230, 230))
    sheet.save(DIST / "03-tres-quartos.png")
    for k, v in res.items():
        print("[três quartos] %s: anel dos rotores, média %.1f / %.1f / %.1f, p10 %.1f / %.1f / %.1f (ref / lâminas / caixa)" % (
            k, v["referencia"]["media"], v["modelo"]["media"], v["caixa"]["media"], v["referencia"]["p10"], v["modelo"]["p10"], v["caixa"]["p10"]))


def cooler_only(explode=False):
    import bpy
    sc = bl_reset()
    bl_import([C.OUT / ("%s.glb" % pid) for pid in C.IDS])
    if explode:
        for o in bpy.data.objects:
            ex = o.get("explode_cad")
            if ex and o.parent is None:
                d = ex["dir"]
                k = 0.35 if o.name.startswith("cooler.fins.") and o.name != "cooler.fins.3" else 1.0
                o.location = (o.location[0] + d[0] * ex["distance"] * k / 1000, o.location[1] + d[1] * ex["distance"] * k / 1000,
                              o.location[2] + d[2] * ex["distance"] * k / 1000)
        # dentro do E8 a câmara, os tubos e a pilha central saem juntos com a base; aqui eles
        # se separam um pouco para mostrar o interior (só nesta imagem)
        for o in bpy.data.objects:
            if o.name == "cooler.fins.3":
                o.location[2] += 0.030
            if o.name.startswith("cooler.heatpipes"):
                o.location[2] += 0.012
    bl_studio(sc, bg=0.9)
    return sc


def look(eye, tgt, up=(0, 0, 1)):
    f = np.array(tgt, float) - np.array(eye, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    return r, np.cross(r, f)


def photo_tile(path, w, h):
    im = Image.open(path).convert("RGB")
    im.thumbnail((w, h), Image.LANCZOS)
    t = Image.new("RGB", (w, h), (255, 255, 255))
    t.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return t


def cooler_views(rep):
    c = np.array([C.L / 2, C.YC, 15.0])
    w, h = 900, 680
    shots = [
        ("04-cooler-face-a.png", c + np.array([-40, -330, 520]), False, ["rtx5090/wccftech-cooler-3.jpg", "rtx5090/wccftech-cooler-4.jpg"],
         "cooler isolado (cooler.py), do lado dos ventiladores"),
        ("05-cooler-base.png", c + np.array([60, -260, -430]), False, ["rtx5090/wccftech-cooler-1.jpg", "rtx5090/wccftech-cooler-5.jpg", "gn/gn-34.png"],
         "cooler isolado, do lado da face B: face de contato, moldura, tubos, mola"),
        ("06-cooler-explodido.png", c + np.array([-90, -420, 360]), True, [],
         "as 7 peças afastadas (direções do assembly; pilhas das pontas a 35 % da distância)"),
    ]
    for name, eye, ex, photos, title in shots:
        sc = cooler_only(ex)
        r, u = look(eye, c)
        bl_camera(sc, r, u, eye, (w * SS, h * SS), lens_px=1.55 * w * SS)
        p = DIST / ("_%s" % name)
        bl_render(sc, p)
        im = on_white(p).resize((w, h), Image.LANCZOS)
        p.unlink()
        tiles = [im] + [photo_tile(REF / ph, w, h) for ph in photos]
        sheet = Image.new("RGB", (w * len(tiles), h + 30), (255, 255, 255))
        for k, t in enumerate(tiles):
            sheet.paste(t, (k * w, 30))
            label(sheet, title if k == 0 else "%s (%s)" % (photos[k - 1], "placa irmã, RTX 5090 FE" if "rtx5090" in photos[k - 1] else "esta placa"), (k * w + 8, 6))
        sheet.save(DIST / name)
    rep["cooler_isolado"] = {"vistas": [s[0] for s in shots], "nota": "comparação de forma com a placa irmã, sem câmera ajustada nem medida"}


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    rep = {"fonte": "harness/parts/cooler_compare.py", "materiais": "viewer/src/materials.json (cor, metal, rugosidade; sem texturas)",
           "contagens": json.loads((C.OUT / "cooler-report.json").read_text(encoding="utf-8"))["counts"]}
    face_b(rep)
    three_quarter(rep)
    cooler_views(rep)
    (DIST / "comparacao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Saídas em %s" % DIST.relative_to(HARNESS.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
