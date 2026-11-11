#!/usr/bin/env python3
"""Comparação das peças de I/O (parts/io_parts.py) com as fotos de referência.

Lê as peças em build/parts/<id>.glb e as fotos em spec/references/cache/ (não versionada) e
grava em dist/parts/io/:

  01-bracket-sr1.png        bracket de frente (vista de -x, como sr-1: y para a direita, face B
                            em cima) ao lado da foto retificada na mesma escala, e o contorno do
                            modelo desenhado sobre a foto; medidas de borda no relatório
  02-adaptador-chiphell.png adaptador visto da face do J3 sobre a retificação do visual-qa
                            (am_adapter), na grade da foto e na escala do CSV
  03-conector.png           conector de 16 pinos: vista de cima e vista da face, ao lado das
                            fotos (sabareesh, pny/3qtr-top-right, furos do Chiphell)
  04-pecas.png              as peças em três quartos
  integrado.png             card.glb integrado, ponta do bracket e borda dos contatos
  comparacao.json           números

Uso: python3 -I harness/parts/io_compare.py [--so-integrado]
"""
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("io_parts", HERE / "io_parts.py")
IOP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IOP)

HARNESS = HERE.parent
CACHE = HARNESS / "spec" / "references" / "cache"
PARTS = HARNESS / "build" / "parts"
DIST = HARNESS / "dist" / "parts" / "io"
RES = {}


# ---------------------------------------------------------------------------
def read_glb(path):
    data = path.read_bytes()
    jlen, _ = struct.unpack_from("<II", data, 12)
    js = json.loads(data[20:20 + jlen])
    blen, _ = struct.unpack_from("<II", data, 20 + jlen)
    return js, data[28 + jlen:28 + jlen + blen]


def meshes_of(pid):
    js, binary = read_glb(PARTS / ("%s.glb" % pid))
    out = []
    for n in js["nodes"]:
        if "mesh" not in n:
            continue
        prim = js["meshes"][n["mesh"]]["primitives"][0]

        def acc(i):
            a = js["accessors"][i]
            bv = js["bufferViews"][a["bufferView"]]
            dt = {5126: "<f4", 5125: "<u4"}[a["componentType"]]
            k = 3 if a["type"] == "VEC3" else 1
            return np.frombuffer(binary, dtype=dt, count=a["count"] * k, offset=bv.get("byteOffset", 0)).reshape(-1, k) if k > 1 else \
                np.frombuffer(binary, dtype=dt, count=a["count"], offset=bv.get("byteOffset", 0))
        v = acc(prim["attributes"]["POSITION"]).astype(float)
        v = np.c_[v[:, 0], -v[:, 2], v[:, 1]] * 1000.0
        f = acc(prim["indices"]).reshape(-1, 3).astype(np.int64)
        out.append((v, f))
    return out


def ortho(items, axes, origin, ppmm, size, bg=(12, 13, 16), light=(0.35, 0.45, 0.82), depth_cue=0.0):
    """Projeção ortográfica com z-buffer: axes = (direita, cima, para o observador), vetores 3D
    unitários; items = lista de (v, f, cor). Supersample 2x."""
    S = 2
    W, H = size[0] * S, size[1] * S
    R, U, F = (np.asarray(a, float) for a in axes)
    img = np.zeros((H, W, 3), np.float32) + np.array(bg, np.float32) / 255
    zb = np.full((H, W), -np.inf, np.float32)
    L = np.asarray(light, float)
    L /= np.linalg.norm(L)
    allv = [v for v, _, _ in items]
    dmax = max(float(((v - np.asarray(origin)) @ F).max()) for v in allv)
    for v, f, col in items:
        rel = v - np.asarray(origin, float)
        px = W / 2 + rel @ R * ppmm * S
        py = H / 2 - rel @ U * ppmm * S
        dep = rel @ F
        t = v[f]
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        nl = np.linalg.norm(n, axis=1)
        nl[nl == 0] = 1
        n /= nl[:, None]
        nf = n @ F
        sh = 0.25 + 0.75 * np.clip(np.c_[n @ R, n @ U, nf] @ L, 0, 1)
        if depth_cue:
            sh = sh * np.clip(1 - (dmax - dep[f].mean(1)) * depth_cue, 0.25, 1)
        for i in np.nonzero(nf > 1e-6)[0]:
            ia, ib, ic = f[i]
            x0, x1, x2 = px[ia], px[ib], px[ic]
            y0, y1, y2 = py[ia], py[ib], py[ic]
            xmin, xmax = int(max(math.floor(min(x0, x1, x2)), 0)), int(min(math.ceil(max(x0, x1, x2)), W - 1))
            ymin, ymax = int(max(math.floor(min(y0, y1, y2)), 0)), int(min(math.ceil(max(y0, y1, y2)), H - 1))
            if xmin > xmax or ymin > ymax:
                continue
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-12:
                continue
            gx, gy = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den
            l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den
            l2 = 1 - l0 - l1
            m = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not m.any():
                continue
            z = l0 * dep[ia] + l1 * dep[ib] + l2 * dep[ic]
            sub = zb[ymin:ymax + 1, xmin:xmax + 1]
            win = m & (z > sub)
            sub[win] = z[win]
            img[ymin:ymax + 1, xmin:xmax + 1][win] = np.array(col) * sh[i]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return im.resize(size, Image.LANCZOS)


def label(im, txt, xy=(10, 8), fill=(235, 235, 235)):
    ImageDraw.Draw(im).multiline_text(xy, txt, fill=fill, spacing=3)
    return im


# ---------------------------------------------------------------------------
# 1. Bracket contra sr-1
# ---------------------------------------------------------------------------
SR_PX_Y, SR_X0 = 6.39, 243.3     # px/mm na horizontal; px da ponta das línguas
SR_PX_Z, SR_Y0 = 6.35, 526.0     # px/mm na vertical; px da borda do lado da face B


def sr_to_px(y, z):
    return SR_X0 + (y - IOP.Y_TIP) * SR_PX_Y, SR_Y0 + (z - (IOP.BR_Z0)) * SR_PX_Z


def bracket_cmp():
    sr = Image.open(CACHE / "storagereview" / "sr-1.jpg").convert("RGB")
    g = np.asarray(sr.convert("L"), float)
    ppmm = 7.0
    yc = IOP.Y_TIP + 62.0
    zc = (IOP.BR_Z0 + IOP.BR_Z1) / 2
    W, H = int(132 * ppmm), int(50 * ppmm)
    # vista de -x: direita = +y, cima = -z, para o observador = -x
    items = [(v, f, (0.55, 0.56, 0.6)) for v, f in meshes_of("io.bracket")]
    items += [(v, f, (0.85, 0.85, 0.9)) for v, f in meshes_of("fasteners.e1_bracket")]
    items += [(v, f, (0.75, 0.7, 0.4)) for v, f in meshes_of("io.board.dp")]
    model = ortho(items, ((0, 1, 0), (0, 0, -1), (-1, 0, 0)), (0, yc, zc), ppmm, (W, H))
    # foto retificada na mesma grade (vizinho mais próximo de uma afim)
    jj, ii = np.meshgrid(np.arange(W), np.arange(H))
    yy = yc + (jj + 0.5 - W / 2) / ppmm
    zz = zc + (ii + 0.5 - H / 2) / ppmm
    px, py = sr_to_px(yy, zz)
    arr = np.asarray(sr)
    ok = (px >= 0) & (px < sr.width - 1) & (py >= 0) & (py < sr.height - 1)
    rect = np.zeros((H, W, 3), np.uint8)
    rect[ok] = arr[py[ok].astype(int), px[ok].astype(int)]
    rect = Image.fromarray(rect)
    # contorno do modelo sobre a foto
    m = np.asarray(model.convert("L"), float) > 20
    edge = m ^ np.roll(m, 1, 0) | m ^ np.roll(m, 1, 1)
    ov = np.asarray(rect).copy()
    ov[edge] = (60, 255, 90)
    over = Image.fromarray(ov)
    # medidas de borda na foto: borda do lado da face A (contra a madeira) e pontas das línguas
    res = {}
    zs = []
    for y in np.arange(IOP.Y_TIP + 12, IOP.Y_TIP + 112, 2.0):
        x, _ = sr_to_px(y, 0)
        col = g[int(SR_Y0 + 25 * SR_PX_Z):int(SR_Y0 + 45 * SR_PX_Z), int(x) - 1:int(x) + 2].mean(1)
        k = np.argmax(np.diff(col))           # escuro (chapa) para claro (madeira)
        zs.append(IOP.BR_Z0 + (SR_Y0 + 25 * SR_PX_Z + k + 0.5 - SR_Y0) / SR_PX_Z)
    res["borda_face_a_z_foto_mediana"] = round(float(np.median(zs)), 2)
    res["borda_face_a_z_modelo"] = round(IOP.BR_Z1, 2)
    tips = []
    (u0, u1), (l0, l1) = IOP.g("br_tongue_z")
    for z in np.linspace(l0 + 1.5, l1 - 1.5, 9):
        _, yp = sr_to_px(0, z + IOP.DZ)
        row = g[int(yp), int(SR_X0 - 4 * SR_PX_Y):int(SR_X0 + 4 * SR_PX_Y)]
        k = np.argmin(np.diff(row))           # claro (madeira) para escuro (chapa)
        tips.append((k + 0.5 - 4 * SR_PX_Y) / SR_PX_Y)
    res["ponta_lingua_face_a_dy_mm"] = round(float(np.median(tips)), 2)
    # aberturas dos DisplayPort: centro de cada abertura escura na foto contra o modelo
    rowz = IOP.DP_ZC
    _, yp = sr_to_px(0, rowz)
    prof = g[int(yp) - 2:int(yp) + 3, :].mean(0)
    dark = prof < 22
    centers = []
    for yc_m in IOP.DP_Y:
        x0, _ = sr_to_px(yc_m - 12, 0)
        x1, _ = sr_to_px(yc_m + 12, 0)
        seg = np.nonzero(dark[int(x0):int(x1)])[0]
        if len(seg):
            runs = np.split(seg, np.where(np.diff(seg) > 3)[0] + 1)
            big = max(runs, key=len)
            cpx = int(x0) + (big[0] + big[-1]) / 2
            centers.append(round(float(IOP.Y_TIP + (cpx - SR_X0) / SR_PX_Y), 2))
    res["dp_centros_foto_y"] = centers
    res["dp_centros_modelo_y"] = [round(v, 2) for v in IOP.DP_Y]
    res["dp_dif_mm"] = [round(a - b, 2) for a, b in zip(IOP.DP_Y, centers)]
    res["passo_linguas_mm"] = round((l0 + l1) / 2 - (u0 + u1) / 2, 2)
    res["passo_slot_norma_mm"] = 20.32
    RES["bracket"] = res
    canvas = Image.new("RGB", (W, 3 * H + 120), (12, 13, 16))
    canvas.paste(rect, (0, 40))
    canvas.paste(model, (0, H + 70))
    canvas.paste(over, (0, 2 * H + 100))
    label(canvas, "Bracket de frente (vista de -x; y para a direita, face B em cima). Em cima: storagereview/sr-1 retificada (6,39 x 6,35 px/mm); "
                  "no meio: modelo; embaixo: contorno do modelo sobre a foto.", (10, 8))
    label(canvas, "Aberturas: modelo menos foto %s mm (passo do CSV %.1f contra %.2f na foto). Borda da face A: foto %.2f, modelo %.2f. "
                  "Ponta da língua: %+.2f mm." % (res["dp_dif_mm"], IOP.PITCH, IOP.g("dp_photo_pitch"), res["borda_face_a_z_foto_mediana"],
                                                  res["borda_face_a_z_modelo"], res["ponta_lingua_face_a_dy_mm"]), (10, 22))
    canvas.save(DIST / "01-bracket-sr1.png")


# ---------------------------------------------------------------------------
# 2. Adaptador contra am_adapter
# ---------------------------------------------------------------------------
def adapter_cmp():
    am = Image.open(CACHE / "visualqa" / "am_adapter.png").convert("RGB")
    s = 12.8
    f, s_u, s_v, x0 = IOP.ad_xform()

    def card_to_img(x, y, sv):
        yi = IOP.AD_END_YI - (x - x0) / s_u
        xi = IOP.AD_EDGE_XI - y / sv
        return ((xi - 240) * s, (yi - 10) * s)
    meshes = meshes_of("pcie.adapter")
    v, fc = meshes[0]
    # silhueta do modelo vista de +z (face do J3), na grade da foto: rasteriza os triângulos
    out = {}
    for tag, sv in (("contorno_transcrito", s_v), ("medidas_csv_na_grade", 1.0)):
        mask = Image.new("L", am.size, 0)
        d = ImageDraw.Draw(mask)
        P = np.array([card_to_img(x, y, sv) for x, y in v[:, :2]])
        for t in fc:
            d.polygon([tuple(P[t[0]]), tuple(P[t[1]]), tuple(P[t[2]])], fill=255)
        out[tag] = np.asarray(mask) > 0
    # máscara da placa na foto (mesmo método do visual-qa: escuro, linhas da grade removidas)
    from scipy import ndimage as nd
    im = np.asarray(am).astype(int)
    R, G_, B = im[..., 0], im[..., 1], im[..., 2]
    line = ((R > 150) & (G_ < 80) & (B < 80)) | ((B > 100) & (R < 60) & (G_ < 60)) | ((G_ > 170) & (B > 170) & (R < 120))
    dk = (im.max(2) < 110).astype(float)
    dk[line] = 0.5
    ph = nd.median_filter(dk, size=5) > 0.5
    ph = nd.binary_opening(ph, iterations=2)
    lab, n = nd.label(ph)
    ph = lab == (np.argmax(nd.sum(ph, lab, range(1, n + 1))) + 1)
    ph = nd.binary_fill_holes(ph)
    res = {}
    for tag, mk in out.items():
        inter = (mk & ph).sum()
        uni = (mk | ph).sum()
        e_m = mk ^ nd.binary_erosion(mk)
        dist = nd.distance_transform_edt(~(ph ^ nd.binary_erosion(ph)))
        dd = dist[e_m] / s
        res[tag] = {"iou": round(float(inter / uni), 4), "dist_borda_media_mm": round(float(dd.mean()), 3),
                    "dist_borda_p95_mm": round(float(np.percentile(dd, 95)), 3)}
    res["alturas_modelo"] = {"sem_lobulo": round(IOP.M("pcie_adapter_total_height_without_lobe"), 2),
                             "faixa": round((IOP.AD_EDGE_XI - 264.15) * s_v, 2), "com_lobulo": round(float(v[:, 1].max()), 2),
                             "comprimento": round(float(v[:, 0].max() - v[:, 0].min()), 2)}
    res["alturas_csv"] = {"sem_lobulo": 34.5, "faixa": IOP.M("pcie_adapter_strip_height"), "com_lobulo": IOP.M("pcie_adapter_total_height"),
                          "comprimento": IOP.M("pcie_adapter_length")}
    res["alturas_grade_da_foto"] = {"sem_lobulo": round(IOP.AD_EDGE_XI - 246.05, 2), "faixa": round(IOP.AD_EDGE_XI - 264.15, 2),
                                    "com_lobulo": round(IOP.AD_EDGE_XI - 242.42, 2), "comprimento": round(116.5 - 14.3, 2)}
    res["zona_contatos_foto_mm"] = round(114.5 - 30.3, 2)
    res["zona_contatos_csv_mm"] = IOP.M("pcie_finger_zone_total")
    res["zona_contatos_norma_mm"] = IOP.M("edge_finger_x16_zone_length")
    res["j3_centro_y_modelo_csv"] = IOP.M("pcie_adapter_connector_center_y")
    res["j3_centro_y_foto"] = round(f(*IOP.AD_J3_IMG)[1], 2)
    RES["adaptador"] = res
    # imagem: foto com os dois contornos
    base = am.copy()
    arr = np.asarray(base).copy()
    for tag, col in (("contorno_transcrito", (40, 255, 80)), ("medidas_csv_na_grade", (255, 80, 220))):
        mk = out[tag]
        e = mk ^ nd.binary_erosion(mk, iterations=2)
        arr[e] = col
    ov = Image.fromarray(arr)
    # modelo renderizado (vista de +z) ao lado
    items = [(v, fc, (0.35, 0.38, 0.36))]
    ppmm = 8.0
    rend = ortho(items, ((0, -1, 0), (-1, 0, 0), (0, 0, 1)), (97.2, 19.0, 2.5), ppmm, (int(46 * ppmm), int(110 * ppmm)))
    W = ov.width + rend.width + 30
    canvas = Image.new("RGB", (W, max(ov.height, rend.height) + 90), (12, 13, 16))
    canvas.paste(ov, (0, 80))
    canvas.paste(rend, (ov.width + 30, 80))
    r1, r2 = res["contorno_transcrito"], res["medidas_csv_na_grade"]
    label(canvas, "Adaptador PCIe sobre am_adapter (chiphell/pcb-a retificada, grade de 1 mm). Verde: contorno do modelo levado de volta à foto (confere a\n"
                  "transcrição); rosa: o modelo em mm na grade da foto (as alturas do CSV ficam 5,5 %% menores que a grade). IoU %.3f / %.3f; borda média %.2f / %.2f mm. À direita: modelo visto da face do J3.\n"
                  "Alturas (sem lóbulo, faixa, com lóbulo): modelo %s; grade %s." % (
                      r1["iou"], r2["iou"], r1["dist_borda_media_mm"], r2["dist_borda_media_mm"],
                      [res["alturas_modelo"][k] for k in ("sem_lobulo", "faixa", "com_lobulo")],
                      [res["alturas_grade_da_foto"][k] for k in ("sem_lobulo", "faixa", "com_lobulo")]), (8, 8))
    canvas.save(DIST / "02-adaptador-chiphell.png")


# ---------------------------------------------------------------------------
# 3. Conector
# ---------------------------------------------------------------------------
def connector_cmp():
    v, f = meshes_of("power.connector")[0]
    cx, cy = IOP.M("power_connector_center_from_bracket_end"), IOP.M("power_connector_center_y")
    ang = math.radians(IOP.M("power_connector_rotation_deg") + 90)
    n = np.array([math.cos(ang), math.sin(ang), 0])
    c = np.array([-math.sin(ang), math.cos(ang), 0])
    zc = IOP.M("iface_pcb_front_z") + IOP.M("conn16_header_width") / 2
    ppmm = 14.0
    col = (0.42, 0.42, 0.45)
    top = ortho([(v, f, col)], ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (cx, cy, zc), ppmm, (int(32 * ppmm), int(32 * ppmm)), depth_cue=0.04)
    # linha do chanfro do PCB como no blockout (a meia profundidade de 11 mm, para fora)
    d = ImageDraw.Draw(top)
    W = top.width

    def p2(x, y):
        return (W / 2 + (x - cx) * ppmm, W / 2 - (y - cy) * ppmm)
    e = np.array([math.cos(ang - math.pi / 2), math.sin(ang - math.pi / 2)])
    q = np.array([cx, cy]) + 5.5 * n[:2]
    d.line([p2(*(q - 20 * e)), p2(*(q + 20 * e))], fill=(60, 200, 90), width=2)
    d.text(p2(*(q + 9 * e + 1.2 * n[:2])), "chanfro do PCB (blockout)", fill=(60, 200, 90))
    face = ortho([(v, f, col)], (tuple(-c), (0, 0, 1), tuple(n)), (cx, cy, zc), ppmm, (int(32 * ppmm), int(32 * ppmm)), depth_cue=0.12)
    label(top, "modelo, vista de +z (face A)\n+x para a direita, +y para cima")
    label(face, "modelo, vista da face de encaixe\nlado longo (18,85) em z")
    sab = Image.open(CACHE / "sabareesh" / "wb-bare-pcb.jpg").convert("RGB").crop((500, 250, 700, 420)).resize((448, 381), Image.LANCZOS)
    label(sab, "sabareesh/wb-bare-pcb (face do chip):\ncorpo alto, 2 tiras lado a lado")
    pny = Image.open(CACHE / "pny" / "3qtr-top-right.png").convert("RGBA")
    bg = Image.new("RGBA", pny.size, (255, 255, 255, 255))
    pny = Image.alpha_composite(bg, pny).convert("RGB").crop((400, 300, 560, 420)).resize((448, 336), Image.LANCZOS)
    label(pny, "pny/3qtr-top-right: 2 x 6 com o\nlado longo na espessura (z)", fill=(20, 20, 20))
    ab = Image.open(CACHE / "visualqa" / "ab_conn.png").convert("RGB").resize((448, 379), Image.LANCZOS)
    label(ab, "furos no PCB (Chiphell, visualqa/ab_conn):\n1 furo alongado por fileira, 4 de sinal em linha,\ntodos na direção de encaixe", fill=(255, 40, 40))
    tiles = [top, face, sab, pny, ab]
    Wc = 3 * 470
    canvas = Image.new("RGB", (Wc, 2 * 470 + 60), (12, 13, 16))
    for k, t in enumerate(tiles):
        canvas.paste(t, ((k % 3) * 470, 50 + (k // 3) * 470))
    across = IOP.g("p16_across") + IOP.g("p16_sense_w")
    res = {"atraves_modelo_mm": round(across, 2), "atraves_so_potencia_mm": IOP.g("p16_across"), "profundidade_modelo_mm": IOP.g("p16_depth"),
           "sabareesh_topo_mm": {"atraves": [10.3, 9.6], "encaixe": [12.2, 11.3]}, "sabareesh_escala": "PCB de 119,6 mm em 572 px (4,78 px/mm); segundo valor corrigido pela ampliação de 1,08 do topo do corpo",
           "afastamento_das_fileiras_modelo_mm": IOP.M("conn16_power_pin_pitch"), "afastamento_das_tiras_sabareesh_mm": 3.5, "pe_das_tiras_atras_do_corpo_sabareesh_mm": 7.0, "pe_das_laminas_modelo_mm": IOP.g("p16_blade")[1],
           "afastamento_dos_furos_chiphell_mm": 2.8, "passo_furos_sinal_chiphell_mm": 1.45,
           "altura_corpo_modelo_mm": [IOP.M("iface_pcb_front_z"), round(IOP.M("iface_pcb_front_z") + IOP.M("conn16_header_width"), 2)],
           "abertura_da_carcaca_z": [round(20 - (IOP.M("conn16_header_width") + 3) / 2, 2), round(20 + (IOP.M("conn16_header_width") + 3) / 2, 2)]}
    RES["conector"] = res
    label(canvas, "Conector de 16 pinos: através das fileiras %.2f mm com a faixa de sinal (topo em sabareesh: 9,6 corrigido), profundidade %.2f (11,3 corrigido); "
                  "fileiras a %.1f mm (tiras 3,5 em perspectiva; furos 2,8).\nCorpo de z %.1f a %.2f; a abertura da carcaça vai de z %.2f a %.2f (centro 20 contra %.2f do corpo)." % (
                      across, IOP.g("p16_depth"), IOP.M("conn16_power_pin_pitch"), res["altura_corpo_modelo_mm"][0],
                      res["altura_corpo_modelo_mm"][1], *res["abertura_da_carcaca_z"], sum(res["altura_corpo_modelo_mm"]) / 2), (10, 8))
    canvas.save(DIST / "03-conector.png")


# ---------------------------------------------------------------------------
def parts_view():
    cols = {"io.bracket": (0.45, 0.46, 0.5), "fasteners.e1_bracket": (0.8, 0.8, 0.85), "io.board": (0.25, 0.5, 0.3),
            "io.board.dp": (0.8, 0.8, 0.82), "pcie.adapter": (0.3, 0.42, 0.36), "power.connector": (0.55, 0.5, 0.4)}
    shots = []
    for pid, cen, axes, ppmm, size in (
            ("io", (0, 50, 20), None, 4.2, (700, 560)),
            ("pcie.adapter", (97, 19, 2), None, 5.5, (700, 420)),
            ("power.connector", (190, 123, 17), None, 18, (700, 560))):
        ids = ["io.bracket", "fasteners.e1_bracket", "io.board", "io.board.dp"] if pid == "io" else [pid]
        items = [(v, f, cols[i]) for i in ids for v, f in meshes_of(i)]
        R = np.array([0.8, 0.6, 0.0]) if pid != "io" else np.array([-0.55, 0.83, 0.0])
        Fv = np.array([-0.35, 0.47, 0.81]) if pid != "io" else np.array([-0.62, -0.41, 0.67])
        Fv /= np.linalg.norm(Fv)
        R = R - (R @ Fv) * Fv
        R /= np.linalg.norm(R)
        U = np.cross(Fv, R)
        shots.append(label(ortho(items, (R, U, Fv), cen, ppmm, size), pid if pid != "io" else "io.bracket, parafusos, io.board, io.board.dp"))
    W = sum(s.width for s in shots)
    canvas = Image.new("RGB", (W, max(s.height for s in shots)), (12, 13, 16))
    x = 0
    for s in shots:
        canvas.paste(s, (x, 0))
        x += s.width
    canvas.save(DIST / "04-pecas.png")


# ---------------------------------------------------------------------------
def integrated_view():
    import trimesh
    sc = trimesh.load(HARNESS / "build" / "card.glb", force="scene")
    mine = {"io.bracket", "fasteners.e1_bracket", "io.board", "io.board.dp", "pcie.adapter", "power.connector"}
    frame = {"frame.shroud", "frame.face_b", "frame.center_covers", "frame.rim"}
    allp = []
    for node in sc.graph.nodes_geometry:
        tf, gname = sc.graph[node]
        geo = sc.geometry[gname]
        v = trimesh.transform_points(geo.vertices, tf)
        v = np.c_[v[:, 0], -v[:, 2], v[:, 1]] * 1000.0
        pid = node
        while pid not in mine and pid not in frame and "." in pid and not pid.startswith("io.board.dp"):
            pid = pid.rsplit(".", 1)[0]
        if node.startswith("io.board.dp"):
            pid = "io.board.dp"
        col = (0.85, 0.62, 0.25) if pid in mine else ((0.40, 0.42, 0.46) if pid in frame else (0.26, 0.36, 0.30))
        allp.append((pid, v, np.asarray(geo.faces), col))

    def view(Fv, up, cen, ppmm, size, skip=()):
        Fv = np.asarray(Fv, float)
        Fv /= np.linalg.norm(Fv)
        R = np.cross(up, Fv)
        R /= np.linalg.norm(R)
        U = np.cross(Fv, R)
        return ortho([(v, f, c) for pid, v, f, c in allp if pid not in skip], (R, U, Fv), cen, ppmm, size)
    a = label(view((-0.70, -0.45, 0.55), (0, 0, 1.0), (60, 45, 20), 3.6, (900, 640)),
              "card.glb integrado: ponta do bracket e face A (peças de I/O em laranja, carcaça em cinza)")
    b = label(view((-0.25, -0.55, -0.80), (0, 1.0, 0), (100, 30, 5), 4.2, (900, 640)),
              "face B e borda dos contatos: adaptador PCIe na camada da face B")
    c = label(view((0.45, 0.55, 0.70), (0, 0, 1.0), (192, 124, 15), 9.0, (900, 640), skip=frame | {"cooler.fins.3", "cooler.base", "cooler.vapor_chamber", "cooler.heatpipes", "cooler.fins.2"}),
              "conector de 16 pinos no canto do PCB (carcaça e cooler ocultos)")
    canvas = Image.new("RGB", (2700, 640), (12, 13, 16))
    for k, im in enumerate((a, b, c)):
        canvas.paste(im, (900 * k, 0))
    canvas.save(DIST / "integrado.png")


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    if "--so-integrado" not in sys.argv:
        bracket_cmp()
        adapter_cmp()
        connector_cmp()
        parts_view()
        (DIST / "comparacao.json").write_text(json.dumps(RES, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(RES, ensure_ascii=False, indent=1))
    if (HARNESS / "build" / "card.glb").exists():
        integrated_view()
    print("Imagens em %s" % DIST.relative_to(HARNESS.parent))


if __name__ == "__main__":
    main()
