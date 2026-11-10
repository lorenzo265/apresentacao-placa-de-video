#!/usr/bin/env python3
"""Carcaça externa da RTX PRO 6000 Blackwell Workstation Edition (F3, peça-piloto).

Gera, em build123d, as quatro peças da carcaça que substituem as caixas do blockout,
com os mesmos ids e as mesmas âncoras do assembly:

  frame.shroud          corpo: face A (ventiladores) com o X, anéis e grades dos cantos,
                        paredes, placa de extremidade do lado das portas, canal da borda
                        superior com duas fendas e a abertura do conector, entalhe PCIe
  frame.face_b          face B: duas grades de lâminas e a estrutura do X
  frame.center_covers   as duas tampas lisas do X da face B (E3); posição do texto marcada
  frame.rim             aro fino que contorna a face B (E2)

Contrato: CAD em mm, Z para cima, origem em card.envelope_min (x a partir do plano do
bracket, y a partir da ponta dos contatos PCIe, z da face A para a face B). O GLB sai em
metros com Y para cima, (x, y, z) -> (x, z, -y) / 1000, como no blockout; a conversão
não é corrigida aqui. Um nó por id; as âncoras do assembly viram nós vazios filhos.

Toda medida vem do CSV (pela chave) ou do assembly. O que não tem linha no CSV está em G,
no topo, com a procedência: "derived" quando foi medido nesta tarefa nos renders da PNY
(calibração descrita em frame_compare.py) e "inferred" quando é palpite sem referência.

Uso:   python3 -I harness/parts/frame.py
Saídas: harness/build/parts/<id>.glb, harness/build/parts/<id>.step,
        harness/build/parts/frame-report.json
"""
import csv
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import (Align, BuildSketch, Circle, Compound, Face, Kind, Locations, Plane,
                       Pos, Rectangle, Sketch, Vector, Wire, export_step, extrude,
                       fillet, offset)

HARNESS = Path(__file__).resolve().parent.parent
ASSEMBLY = HARNESS / "design" / "assembly.json"
MEASURES = HARNESS / "design" / "measurements.csv"
OUT = HARNESS / "build" / "parts"

IDS = ("frame.shroud", "frame.face_b", "frame.center_covers", "frame.rim")

# Tolerâncias das conferências e da malha (não são medidas da peça)
TOL_ENV = 0.5          # mm, envelope contra o CSV
TOL_ANCHOR = 2.0       # mm, âncora fora da peça
TESS_TOL = 0.04        # mm, desvio linear da tesselagem
TESS_ANG = 0.12        # rad, desvio angular da tesselagem
TRI_BUDGET = 200_000   # triângulos, carcaça inteira

# ---------------------------------------------------------------------------
# Valores sem linha no CSV: (valor, procedência, nota)
# ---------------------------------------------------------------------------
G = {
    # face A
    "face_a_plate_t": (2.0, "inferred", "espessura da chapa da face A; nenhuma foto de perfil"),
    "edge_fillet_a": (3.0, "inferred", "arredondamento da aresta entre a face A e as laterais; os renders mostram aresta macia, sem cota"),
    "bracket_bottom_corner_r": (3.0, "derived", "canto entre a ponta do bracket e a borda dos contatos: quase reto nos dois renders (pny/front, pny/back); o CSV dá um raio só, lido nos outros cantos"),
    "pod_frame_w": (5.0, "derived", "moldura das cápsulas dos ventiladores, da borda até a grade: 4,8 a 5,2 mm (pny/front)"),
    "apex_r_a": (12.0, "derived", "raio do vértice das tampas lisas da face A: vão vertical de 10,3 mm entre os vértices no cruzamento (pny/front)"),
    "rib_w_a": (1.5, "derived", "faixa lisa entre a tampa lisa e a grade do X da face A: chanfro de 1,7 mm (pny/front)"),
    "ring_clear": (0.5, "inferred", "folga radial entre o rotor e a boca do anel; o anel fica com (aro - boca) / 2 de largura"),
    "win_r_a": (1.5, "inferred", "raio dos cantos das janelas de grade da face A"),
    "tri_recess_a": (0.8, "inferred", "rebaixo das tampas lisas da face A em relação às cápsulas"),
    "tri_rim_a": (4.0, "inferred", "borda sem rebaixo em volta das tampas lisas da face A"),
    "lam_pitch_a": (1.5, "derived", "passo das lâminas visíveis nas grades da face A: cerca de 1,5 mm (pny/front)"),
    "lam_t_a": (0.5, "inferred", "espessura das lâminas da face A"),
    "lam_recess_a": (0.4, "inferred", "recuo das lâminas da face A em relação à chapa"),
    "lam_depth_a": (1.0, "inferred", "quanto as lâminas da face A entram na carcaça além da chapa"),
    # extremidade do lado das portas
    "end_plate_recess": (1.2, "inferred", "recuo da placa de extremidade dentro das bordas laterais; igual à altura das cabeças dos parafusos do blockout (screw_head_h)"),
    "end_plate_t": (1.5, "inferred", "espessura da placa de extremidade"),
    "dp_clear": (0.3, "inferred", "folga das aberturas dos DisplayPort na placa de extremidade"),
    # face B, aro e tampas
    "rim_w": (2.2, "derived", "largura do aro visto de frente: faixa clara de 2,2 mm no contorno (pny/back)"),
    "rim_fillet": (1.0, "inferred", "arredondamento da aresta externa do aro"),
    "grille_inset_b": (6.2, "derived", "distância do contorno até as lâminas da grade da face B: 6,2 a 6,6 mm (pny/back)"),
    "cover_edge_off_b": (1.4, "derived", "a borda das tampas fica 1,4 mm (perpendicular) para dentro da linha do X que passa pelo cruzamento (pny/back, linhas a 15 e 30 mm do centro)"),
    "x_band_b": (8.0, "derived", "largura perpendicular da estrutura do X entre a tampa e a grade (pny/back)"),
    "apex_r_b": (7.0, "derived", "raio do vértice das tampas: vão vertical de 9,7 mm entre os vértices (pny/back)"),
    "win_r_b": (3.4, "derived", "raio do vértice das grades junto ao cruzamento: ponta a 10,8 mm do cruzamento (pny/back)"),
    "lam_pitch_b": (1.45, "derived", "passo das lâminas da grade da face B: cerca de 1,45 mm (pny/back)"),
    "lam_t_b": (0.6, "inferred", "espessura das lâminas da face B"),
    "lam_recess_b": (0.5, "inferred", "recuo das lâminas da face B em relação à moldura"),
    "adapter_clear": (0.5, "inferred", "folga do recorte da face B em volta do adaptador PCIe (o recorte aparece em gn-20, sem cota)"),
    # borda inferior
    "notch_r": (1.5, "inferred", "raio dos cantos do entalhe ao lado dos contatos PCIe"),
    # canal da borda superior
    "ch_lip_a": (4.0, "inferred", "borda do lado da face A entre a aresta e o canal"),
    "ch_pcb_clear": (1.5, "inferred", "folga entre o fim do canal (lado da face B) e a face do PCB, para o fundo do canal não cruzar o PCB"),
    "ch_depth": (1.5, "inferred", "profundidade do canal; as referências mostram o rebaixo sem cota (parece maior, 2 a 4 mm); limitada pela âncora anchor.frame.shroud.1 (2 mm)"),
    "ch_corner_r": (2.0, "inferred", "raio dos cantos do canal no plano xz"),
    "slot_w": (2.0, "inferred", "largura das duas fendas do canal (proporção em perspectiva, pny/3qtr-top-right)"),
    "slot_z": ((7.5, 11.5), "inferred", "centros das fendas em z, perto da face A (perspectiva, pny/3qtr-top-right)"),
    "slot_x_margin": (8.0, "inferred", "distância do começo do canal ao começo das fendas"),
    "slot_end_gap": (5.0, "inferred", "distância do fim das fendas à abertura do conector"),
    "pad_len_x": (40.0, "inferred", "comprimento da placa lisa elevada do canal, do lado do bracket"),
    "pad_z": ((15.0, 28.0), "inferred", "faixa em z da placa lisa do canal, do lado da face B"),
    "pad_h": (0.4, "inferred", "altura da placa lisa sobre o fundo do canal"),
    "open_x_depth": (8.0, "inferred", "abertura do conector ao longo de x (profundidade do cabeçote entre as fileiras; sem cota)"),
    "open_clear": (1.5, "inferred", "folga da abertura do conector além da largura do cabeçote (conn16_header_width), em z"),
}


def g(k):
    return G[k][0]


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def load_measures():
    out = {}
    with open(MEASURES, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["feature"]] = (float(r["value_mm"]), r["tolerance_mm"], r["provenance"])
    return out


MEAS = load_measures()
USED = set()


def M(k):
    USED.add(k)
    return MEAS[k][0]


ASM = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
PARTS = {p["id"]: p for p in ASM["parts"]}

# grandezas comuns
L = M("card_envelope_length")
T = M("card_thickness")
Y0 = M("iface_shroud_y_min")
Y1 = Y0 + M("shroud_height_proposed")
YC = M("iface_shroud_center_y")
WALL = M("shroud_wall")
RC = M("shroud_corner_radius")
ANG = math.radians(M("x_rib_angle_deg"))
K = math.tan(ANG)
Z_FACE_B = T - M("layer_end_face_b_grid")       # topo das paredes; a face B fica acima
BIG = 600.0                                     # extensão dos semiplanos auxiliares


# ---------------------------------------------------------------------------
# Auxiliares 2D (plano xy) e 3D
# ---------------------------------------------------------------------------
def poly(pts):
    return Sketch() + Face(Wire.make_polygon([Vector(x, y, 0) for x, y in pts], close=True))


def rect(x0, x1, y0, y1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)


def inset(sk, d):
    return offset(sk, -d, kind=Kind.ARC)


def round_convex(sk, r):
    return offset(offset(sk, -r, kind=Kind.ARC), r, kind=Kind.ARC)


def ext(sk, z0, z1):
    """Extrusão de z0 a z1, sempre para +z (a normal do esboço pode sair invertida dos booleanos)."""
    return Pos(0, 0, z0) * extrude(sk, z1 - z0, dir=(0, 0, 1))


def outline():
    """Contorno da carcaça no plano xy: 124 mm de altura, cantos de raio RC; o canto
    entre a ponta do bracket e a borda dos contatos é quase reto (G)."""
    def is_bb(v):
        return v.X < 1 and v.Y < Y0 + 1
    with BuildSketch() as s:
        with Locations((0, Y0)):
            Rectangle(L, Y1 - Y0, align=(Align.MIN, Align.MIN))
        fillet(s.vertices().filter_by(lambda v: not is_bb(v)), RC)
        fillet(s.vertices().filter_by(is_bb), g("bracket_bottom_corner_r"))
    return s.sketch


def x_triangle(xc, yc, up, off_perp):
    """Semiplano do X (tampa superior se up, inferior se não): pontos com
    |y - yc| - K |x - xc| >= off_perp / cos(ANG), do lado indicado."""
    sy = 1 if up else -1
    ay = yc + sy * off_perp / math.cos(ANG)
    return poly([(xc, ay), (xc - BIG, ay + sy * K * BIG), (xc + BIG, ay + sy * K * BIG)])


def x_wedge(xc, yc, left, c):
    """Cunha lateral do X: |y - yc| < K |x - xc| + c (c em y), do lado indicado; c < 0
    afasta a ponta do cruzamento."""
    sx = -1 if left else 1
    ax = xc - sx * c / K
    return poly([(ax, yc), (ax + sx * BIG, yc + K * BIG), (ax + sx * BIG, yc - K * BIG)])


def sector(cx, cy, a_mid_deg, half_deg):
    a0, a1 = math.radians(a_mid_deg - half_deg), math.radians(a_mid_deg + half_deg)
    pts = [(cx, cy)] + [(cx + BIG * math.cos(a), cy + BIG * math.sin(a)) for a in np.linspace(a0, a1, 7)]
    return poly(pts)


def strips(x0, x1, pitch, t):
    xs = np.arange(x0 + pitch / 2, x1, pitch)
    return Sketch() + [Pos(x, YC) * Rectangle(t, 2 * BIG) for x in xs]


def box3(x0, x1, y0, y1, z0, z1):
    return ext(rect(x0, x1, y0, y1), z0, z1)


def xz_extrude(sk_xz, y_top, depth):
    """Esboço desenhado em coordenadas locais (x, z), extrudado de y_top para baixo."""
    return extrude(Plane.XZ.offset(-y_top) * sk_xz, depth, dir=(0, -1, 0))


def rrect_xz(x0, x1, z0, z1, r):
    with BuildSketch() as s:
        with Locations(((x0 + x1) / 2, (z0 + z1) / 2)):
            Rectangle(x1 - x0, z1 - z0)
        if r > 0:
            fillet(s.vertices(), r)
    return s.sketch


# ---------------------------------------------------------------------------
# Geometria comum do X e dos ventiladores
# ---------------------------------------------------------------------------
FAN_X = (M("fan1_center_from_bracket_end"), M("fan2_center_from_bracket_end"))
FAN_Y = M("iface_fan_center_y")
R_RING = M("fan_ring_outer_diameter") / 2
R_OPEN = M("fan_rotor_diameter") / 2 + g("ring_clear")
XA = M("x_rib_cross_face_a_from_bracket_end")
XB = M("x_rib_cross_face_b_from_bracket_end")


def face_a_triangles(expand=0.0):
    out = []
    for up in (True, False):
        t = round_convex(x_triangle(XA, YC, up, 0.0), g("apex_r_a"))
        if expand:
            t = offset(t, expand, kind=Kind.ARC)
        out.append(t)
    return out


def channel_x_range():
    """O canal ocupa a borda superior da seção central: entre os pontos em que as bordas
    da tampa lisa superior da face A chegam ao topo (as cápsulas ficam dos lados)."""
    dx = (Y1 - YC) / K
    return XA - dx, XA + dx


# ---------------------------------------------------------------------------
# Peças
# ---------------------------------------------------------------------------
NOTES = {i: [] for i in IDS}


def note(pid, txt):
    NOTES[pid].append(txt)


def build_shroud():
    pid = "frame.shroud"
    O = outline()
    tA = g("face_a_plate_t")
    inner = inset(O, WALL)

    # corpo: casca aberta do lado da face B (z = Z_FACE_B), aresta da face A arredondada
    body = ext(O, 0, Z_FACE_B)
    body = fillet(body.edges().filter_by(lambda e: e.center().Z < 1e-3), g("edge_fillet_a"))
    body = body - ext(inner, tA, Z_FACE_B + 1)

    # placa de extremidade do lado das portas, recuada dentro das bordas laterais
    rec, tE = g("end_plate_recess"), g("end_plate_t")
    # o vão do recuo é o contorno interno deslocado até x = 0: sobram as bordas de cima e de
    # baixo e a parede curva do canto
    body = body - (ext(Pos(-WALL - 0.5, 0) * inner, tA, Z_FACE_B + 1) & box3(-1, rec, Y0 - 1, Y1 + 1, -1, T + 1))
    plate = ext(inner, tA, Z_FACE_B) & box3(rec, rec + tE, Y0 - 1, Y1 + 1, -1, T + 1)
    cl = g("dp_clear")
    for a in PARTS["io.board.dp"]["anchors"]:
        _, ay, az = a["pos"]
        hw, hh = M("dp_receptacle_width") / 2 + cl, M("dp_receptacle_height") / 2 + cl
        plate = plate - box3(rec - 1, rec + tE + 1, ay - hw, ay + hw, az - hh, az + hh)
    body = body + plate
    note(pid, "placa de extremidade recuada %.1f mm, %.1f mm de espessura, com as 4 aberturas dos DisplayPort nas âncoras de io.board.dp (palpite de forma; gn-16 mostra a placa e os parafusos, sem cota)" % (rec, tE))

    # aberturas dos ventiladores e dutos curtos atrás do anel
    duct_z = M("layer_end_fan_ring")
    for fx in FAN_X:
        body = body - ext(Pos(fx, FAN_Y) * Circle(R_OPEN), -1, tA + 0.01)
        ring = Pos(fx, FAN_Y) * Circle(R_OPEN + WALL) - Pos(fx, FAN_Y) * Circle(R_OPEN)
        body = body + (ext(ring, tA - 0.01, duct_z) & ext(inner, tA - 0.02, duct_z + 1))
    note(pid, "duto cilíndrico de parede %.1f mm atrás de cada anel, de z = %.1f a layer_end_fan_ring (%.0f mm): interior da carcaça sem foto" % (WALL, tA, duct_z))

    # X da face A: tampas lisas rebaixadas, faixa lisa e grades
    pod = inset(O, g("pod_frame_w"))
    tris = face_a_triangles()
    tris_exp = face_a_triangles(g("rib_w_a"))
    disks = [Pos(fx, FAN_Y) * Circle(R_RING) for fx in FAN_X]
    rec_reg = (tris[0] + tris[1]) & inset(O, g("tri_rim_a"))
    body = body - ext(rec_reg, -1, g("tri_recess_a"))
    half_t = 90.0 - math.degrees(ANG)          # setor até o ponto de tangência do X com o anel
    w_x = pod - tris_exp[0] - tris_exp[1] - disks[0] - disks[1]
    w_x = w_x & sector(FAN_X[0], FAN_Y, 0.0, half_t) & sector(FAN_X[1], FAN_Y, 180.0, half_t)
    w_x = w_x & rect(FAN_X[0], FAN_X[1], Y0, Y1)
    w_x = round_convex(w_x, g("win_r_a"))
    w_c = ((pod - disks[0]) & rect(-1, FAN_X[0], Y0, Y1)) + ((pod - disks[1]) & rect(FAN_X[1], L + 1, Y0, Y1))
    w_c = round_convex(w_c, g("win_r_a"))
    body = body - ext(w_x, -1, tA + 0.01) - ext(w_c, -1, tA + 0.01)
    lam = strips(0, L, g("lam_pitch_a"), g("lam_t_a")) & w_c
    body = body + ext(lam, g("lam_recess_a"), tA + g("lam_depth_a"))
    note(pid, "janelas do X da face A abertas, sem lâminas: no cruzamento a referência mostra as aletas centrais (cooler.fins.3) pela abertura")
    note(pid, "lâminas das grades dos cantos: espessura %.1f, recuo %.1f e profundidade são palpite; podem ser as próprias aletas vistas pela grade" % (g("lam_t_a"), g("lam_recess_a")))

    # entalhe da borda inferior ao lado dos contatos PCIe
    nx0, nx1 = M("shroud_pcie_side_notch_x_start"), M("shroud_pcie_side_notch_x_end")
    nd = M("shroud_pcie_side_notch_depth")
    with BuildSketch() as s:
        with Locations(((nx0 + nx1) / 2, Y0 + nd / 2 - 5)):
            Rectangle(nx1 - nx0, nd + 10)
        fillet(s.vertices().filter_by(lambda v: v.Y > Y0), g("notch_r"))
    notch = s.sketch
    body = body - ext(notch, -1, T + 1)
    # parede em U em volta do entalhe, para a carcaça continuar fechada
    u_wall = (offset(notch, WALL, kind=Kind.ARC) - notch) & inner
    body = body + ext(u_wall, tA - 0.01, Z_FACE_B)

    # canal da borda superior
    cx0, cx1 = channel_x_range()
    cz0 = g("ch_lip_a")
    cz1 = M("iface_pcb_front_z") - g("ch_pcb_clear") - WALL
    d = g("ch_depth")
    r = g("ch_corner_r")
    tub = xz_extrude(rrect_xz(cx0 - WALL, cx1 + WALL, cz0 - WALL, cz1 + WALL, r + WALL), Y1, d + WALL)
    body = body + (tub & ext(O, 0, Z_FACE_B))
    body = body - xz_extrude(rrect_xz(cx0, cx1, cz0, cz1, r), Y1 + 1, d + 1)
    floor_y = Y1 - d
    sx0 = cx0 + g("slot_x_margin")
    ox = M("iface_shroud_power_opening_x")
    a_open = [a["pos"] for a in PARTS[pid]["anchors"] if a["id"].endswith("power_opening")][0]
    oz = a_open[2]
    ow_z = M("conn16_header_width") + 2 * g("open_clear")
    od_x = g("open_x_depth")
    sx1 = ox - od_x / 2 - g("slot_end_gap")
    for zc in g("slot_z"):
        body = body - xz_extrude(rrect_xz(sx0, sx1, zc - g("slot_w") / 2, zc + g("slot_w") / 2, g("slot_w") / 2 - 0.01), floor_y + 0.5, WALL + 1)
    pz0, pz1 = g("pad_z")
    body = body + xz_extrude(rrect_xz(sx0, sx0 + g("pad_len_x"), pz0, pz1, r), floor_y + g("pad_h"), g("pad_h") + 0.01)
    body = body - xz_extrude(rrect_xz(ox - od_x / 2, ox + od_x / 2, oz - ow_z / 2, oz + ow_z / 2, 1.0), floor_y + 0.5, WALL + 1)
    note(pid, "canal da borda superior de x = %.1f a %.1f (onde as bordas da tampa lisa da face A chegam ao topo) e z = %.1f a %.1f; profundidade, fendas, placa lisa e abertura do conector com medidas de palpite (sem cota nas referências)" % (cx0, cx1, cz0, cz1))
    note(pid, "abertura do conector centrada em iface_shroud_power_opening_x e no z da âncora; o lado longo (largura do cabeçote, %.2f mm) fica em z, como a fileira de 6 pinos em pny/3qtr-top-right" % M("conn16_header_width"))
    note(pid, "logotipo NVIDIA da borda superior não modelado (detalhe de superfície do passo do Blender)")
    return body


def face_b_regions():
    O = outline()
    in_rim = inset(O, g("rim_w"))
    covers = []
    for up in (True, False):
        c = round_convex(x_triangle(XB, YC, up, g("cover_edge_off_b")), g("apex_r_b"))
        covers.append(c & in_rim)
    c_win = (g("cover_edge_off_b") - g("x_band_b")) / math.cos(ANG)
    wins = (x_wedge(XB, YC, True, c_win) + x_wedge(XB, YC, False, c_win)) & inset(O, g("grille_inset_b"))
    wins = round_convex(wins, g("win_r_b"))
    return O, in_rim, covers, wins


def build_face_b():
    pid = "frame.face_b"
    O, in_rim, covers, wins = face_b_regions()
    z0 = Z_FACE_B
    frame = ext(in_rim - covers[0] - covers[1], z0, T)
    frame = frame - ext(wins, z0 - 1, T + 1)
    lam = strips(0, L, g("lam_pitch_b"), g("lam_t_b")) & wins
    part = frame + ext(lam, z0, T - g("lam_recess_b"))
    # recorte do adaptador PCIe (gn-20 mostra a placa adaptadora num rebaixo da face B)
    c = g("adapter_clear")
    f0 = M("pcie_fingers_start_from_bracket_end")
    az = M("iface_adapter_board_z_min")
    # só a faixa ao longo da borda; a aba (pcie_adapter_tab_width x pcie_adapter_total_height)
    # cairia sobre a grade e o X, que pny/back mostra inteiros: a interferência fica no relatório
    part = part - box3(f0 - c, f0 + M("pcie_adapter_length") + c, -1, M("pcie_adapter_strip_height") + c, az - c, T + 1)
    # a face B não desce sobre a pcb.plate (que vai até T - layer_center_covers)
    pcx, pcy = M("iface_pcb_center_x"), M("iface_pcb_center_y")
    ztop_plate = T - M("layer_center_covers")
    part = part - box3(pcx - M("pcb_plate_outline_x") / 2, pcx + M("pcb_plate_outline_x") / 2,
                       pcy - M("pcb_plate_outline_y") / 2, pcy + M("pcb_plate_outline_y") / 2, z0 - 1, ztop_plate)
    note(pid, "estrutura do X e moldura das grades na mesma peça; as grades são lâminas reais (passo %.2f, espessura %.1f; espessura e recuo são palpite)" % (g("lam_pitch_b"), g("lam_t_b")))
    note(pid, "recorte para a faixa do adaptador PCIe ao longo da borda dos contatos (folga %.1f mm), aberto até a face: forma vista em gn-20, sem cota; a aba do adaptador não tem recorte" % c)
    note(pid, "a parte da face B sobre a pcb.plate começa em z = %.1f (topo da placa), não em %.1f: escolha para não cruzar a pcb.plate" % (ztop_plate, z0))
    note(pid, "divisão: as grades das duas pontas e o X ficam numa peça só, como no assembly; na placa real elas parecem fazer parte das carcaças das pontas (gn-27), sem foto da junção")
    return part


def build_center_covers():
    pid = "frame.center_covers"
    _, _, covers, _ = face_b_regions()
    z0 = T - M("layer_center_covers")
    lower = ext(covers[1], z0, T)
    upper = ext(covers[0], z0, T)
    note(pid, "duas tampas, inferior (instância 1, borda dos contatos) e superior (instância 2, com o texto), espessura layer_center_covers; vértices arredondados; a tampa da foto gn-20 tem uma aba na borda que não foi modelada (sem cota)")
    note(pid, "texto RTX PRO 6000 não gravado: só a caixa em extras (passo do Blender)")
    return [lower, upper]


def build_rim():
    pid = "frame.rim"
    O = outline()
    rim = ext(O - inset(O, g("rim_w")), Z_FACE_B, T)
    try:
        top_outer = [e for e in rim.edges() if e.center().Z > T - 1e-3 and _on_outline(e)]
        rim = fillet(top_outer, g("rim_fillet"))
    except Exception as ex:  # o arredondamento é cosmético
        note(pid, "arredondamento externo do aro falhou (%s); aro sem arredondamento" % ex)
    note(pid, "aro como uma faixa de largura constante no contorno da face B, de z = %.0f a %.0f; gn-17 mostra um aro fino, mas o desenho exato (se acompanha também o X) não dá para ler" % (Z_FACE_B, T))
    return rim


def _on_outline(e):
    """Aresta no contorno externo (não no interno do aro)."""
    c = e.center()
    dx = min(c.X, L - c.X)
    dy = min(c.Y - Y0, Y1 - c.Y)
    return min(dx, dy) < g("rim_w") / 2


# ---------------------------------------------------------------------------
# Malha, GLB e STEP
# ---------------------------------------------------------------------------
def to_mesh(shape):
    v, f = shape.tessellate(TESS_TOL, TESS_ANG)
    m = trimesh.Trimesh(np.array([[p.X, p.Y, p.Z] for p in v]), np.array(f), process=False)
    m.merge_vertices(digits_vertex=4)
    m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    return m


def to_gltf(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]] / 1000.0


def write_glb(path, nodes_spec, root_extras):
    """nodes_spec: lista de (nome, extras, malha ou None, translação ou None, índice do pai ou None)."""
    nodes, meshes, accs, views = [], [], [], []
    buf = bytearray()
    for name, extras, mesh, trans, parent in nodes_spec:
        n = {"name": name, "extras": extras}
        if mesh is not None:
            V = to_gltf(mesh.vertices).astype("<f4")
            F = np.asarray(mesh.faces).astype("<u4").reshape(-1)
            ids = []
            for data, target in ((V, 34962), (F, 34963)):
                while len(buf) % 4:
                    buf.append(0)
                views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": data.nbytes, "target": target})
                buf.extend(data.tobytes())
                ids.append(len(views) - 1)
            accs.append({"bufferView": ids[0], "componentType": 5126, "count": len(V), "type": "VEC3",
                         "min": V.min(axis=0).tolist(), "max": V.max(axis=0).tolist()})
            accs.append({"bufferView": ids[1], "componentType": 5125, "count": len(F), "type": "SCALAR"})
            meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": len(accs) - 2},
                                                         "indices": len(accs) - 1, "material": 0, "mode": 4}]})
            n["mesh"] = len(meshes) - 1
        if trans is not None:
            n["translation"] = [float(t) for t in trans]
        nodes.append(n)
        if parent is not None:
            nodes[parent].setdefault("children", []).append(len(nodes) - 1)
    gltf = {
        "asset": {"version": "2.0", "generator": "harness/parts/frame.py", "extras": root_extras},
        "scene": 0, "scenes": [{"name": nodes_spec[0][0], "nodes": [0]}], "nodes": nodes, "meshes": meshes,
        "materials": [{"name": "carcaca", "pbrMetallicRoughness": {"baseColorFactor": [0.30, 0.32, 0.36, 1.0],
                                                                   "metallicFactor": 0.0, "roughnessFactor": 0.85}}],
        "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}],
    }
    js = json.dumps(gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    js += b" " * (-len(js) % 4)
    binary = bytes(buf) + b"\0" * (-len(buf) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binary)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binary), 0x004E4942) + binary)


FEATURE_PROV = {
    "frame.shroud": {
        "contorno, cantos, altura e comprimento": "derived (CSV: renders da PNY)",
        "canto do bracket junto aos contatos quase reto": "derived (pny/front, pny/back; nesta tarefa)",
        "anéis e aberturas dos ventiladores": "derived (CSV)",
        "X da face A (cruzamento e ângulo)": "derived (CSV)",
        "vértices, faixas e moldura das cápsulas da face A": "derived (pny/front; nesta tarefa)",
        "grades dos cantos da face A": "derived (posição); inferred (lâminas)",
        "entalhe PCIe": "derived (CSV)",
        "canal da borda superior: extensão em x": "derived (geometria do X; pny/front)",
        "canal: profundidade, fendas, placa lisa, abertura": "inferred (vistos em perspectiva, sem cota)",
        "paredes, espessuras, placa de extremidade, dutos": "inferred",
    },
    "frame.face_b": {
        "grades e estrutura do X (posição, faixas, vértices)": "derived (pny/back; nesta tarefa)",
        "lâminas (passo)": "derived (pny/back); espessura e recuo inferred",
        "recorte do adaptador PCIe": "derived (gn-20, forma); inferred (medida)",
    },
    "frame.center_covers": {
        "contorno das tampas": "derived (pny/back; nesta tarefa)",
        "espessura": "inferred (layer_center_covers, orçamento)",
        "caixa do texto": "derived (CSV)",
    },
    "frame.rim": {
        "contorno": "derived (CSV)",
        "largura": "derived (pny/back; nesta tarefa)",
        "espessura e arredondamento": "inferred",
    },
}


def text_angle_cad():
    """O CSV dá 45 graus medidos no render pny/back, que mostra a placa com os contatos
    para cima (x para a direita, y para baixo). Passado para (x, y) do assembly, o texto
    lê de (x menor, y maior) para (x maior, y menor), ao longo da nervura esquerda da
    tampa superior: -45 graus."""
    return -M("face_b_text_angle_deg")


def text_box():
    cx, cy = M("face_b_text_center_x"), M("iface_face_b_text_y")
    a = math.radians(text_angle_cad())
    ln, ht = M("face_b_text_length"), M("face_b_text_height")
    d, n = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    c = np.array([cx, cy])
    return [(c + sl * d * ln / 2 + sh * n * ht / 2).tolist() for sl, sh in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


# ---------------------------------------------------------------------------
# Conferências
# ---------------------------------------------------------------------------
def inside(mesh, pts):
    """Teste de ponto interno por paridade de raios (3 direções, maioria)."""
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils import Vector as V3
    from mathutils.bvhtree import BVHTree
    tree = BVHTree.FromPolygons(mesh.vertices.tolist(), mesh.faces.tolist(), epsilon=0.0)
    out = []
    dirs = [V3((0.31, 0.52, 0.79)).normalized(), V3((-0.67, 0.21, 0.71)).normalized(), V3((0.13, -0.91, 0.39)).normalized()]
    for p in pts:
        votes = 0
        for d in dirs:
            n, o = 0, V3(p)
            while True:
                hit = tree.ray_cast(o, d)
                if hit[0] is None:
                    break
                n += 1
                o = hit[0] + d * 1e-4
            votes += n % 2
        out.append(votes >= 2)
    return np.array(out), tree


def anchor_check(pid, mesh):
    import bpy  # noqa: F401
    from mathutils import Vector as V3
    res = []
    anchors = PARTS[pid]["anchors"]
    ins, tree = inside(mesh, [a["pos"] for a in anchors])
    for a, isin in zip(anchors, ins):
        loc, _, _, dist = tree.find_nearest(V3(a["pos"]))
        d = 0.0 if isin else float(dist)
        res.append({"anchor": a["id"], "pos": a["pos"], "dist_mm": round(d, 3), "inside": bool(isin),
                    "ok": d <= TOL_ANCHOR})
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shapes = {
        "frame.shroud": [build_shroud()],
        "frame.face_b": [build_face_b()],
        "frame.center_covers": build_center_covers(),
        "frame.rim": [build_rim()],
    }
    report = {"parts": {}, "guess_values": {k: {"value": v[0], "provenance": v[1], "note": v[2]} for k, v in G.items()}}
    all_ok = True
    total_tris = 0
    lo_all, hi_all = np.full(3, np.inf), np.full(3, -np.inf)
    for pid in IDS:
        p = PARTS[pid]
        meshes = [to_mesh(s) for s in shapes[pid]]
        mesh = trimesh.util.concatenate(meshes)
        ntri = int(len(mesh.faces))
        total_tris += ntri
        closed = [bool(m.is_watertight and m.is_winding_consistent and m.volume > 0) for m in meshes]
        lo, hi = mesh.bounds
        lo_all, hi_all = np.minimum(lo_all, lo), np.maximum(hi_all, hi)
        anchors = anchor_check(pid, mesh)
        extras = {
            "id": pid, "stage": p["stage"], "fidelity": p["fidelity"],
            "exists_provenance": p["exists_provenance"], "shape_provenance": "derived",
            "shape_provenance_features": FEATURE_PROV[pid],
            "guess": True, "guess_notes": NOTES[pid],
            "blockout": False, "units_cad": "mm", "up_cad": "+Z", "origin": "card.envelope_min",
            "explode_cad": p["explode"],
        }
        spec = []
        if len(meshes) == 1:
            spec.append((pid, extras, meshes[0], None, None))
        else:
            extras["count"] = p["count"]["value"]
            extras["count_provenance"] = p["count"]["provenance"]
            extras["text_box_cad_mm"] = {"corners_xy": text_box(), "z": T, "text": "RTX PRO 6000",
                                         "angle_deg_cad": text_angle_cad(),
                                         "reading_dir_xy": [round(math.cos(math.radians(text_angle_cad())), 4), round(math.sin(math.radians(text_angle_cad())), 4)],
                                         "letter_up_xy": [round(math.sin(math.radians(text_angle_cad())), 4), round(-math.cos(math.radians(text_angle_cad())), 4)],
                                         "note": "direções tiradas de pny/back e passadas para (x, y) do assembly; o referencial do assembly é espelhado em relação à placa real (ver relatório), então o passo do Blender precisa conferir a leitura",
                                         "instance": 2, "engrave": False}
            spec.append((pid, extras, None, None, None))
            for k, m in enumerate(meshes, 1):
                spec.append(("%s.%d" % (pid, k), {"instance_of": pid, "instance": k, "stage": p["stage"],
                                                  "shape_provenance": "derived", "guess": True}, m, None, 0))
        for a in p["anchors"]:
            spec.append((a["id"], {"anchor": True, "part": pid}, None, to_gltf([a["pos"]])[0], 0))
        glb = OUT / ("%s.glb" % pid)
        write_glb(glb, spec, {"units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z",
                              "origin": "card.envelope_min", "map": "gltf = (x, z, -y) / 1000"})
        step = OUT / ("%s.step" % pid)
        comp = shapes[pid][0] if len(shapes[pid]) == 1 else Compound(shapes[pid])
        comp.label = pid
        export_step(comp, str(step))
        # releitura do GLB
        sc = trimesh.load(glb, force="scene")
        back = sc.to_geometry()
        bl = np.c_[back.vertices[:, 0], -back.vertices[:, 2], back.vertices[:, 1]] * 1000.0
        reread_ok = bool(np.allclose(bl.min(axis=0), lo, atol=0.01) and np.allclose(bl.max(axis=0), hi, atol=0.01))
        report["parts"][pid] = {
            "triangles": ntri, "vertices": int(len(mesh.vertices)), "bodies": len(meshes),
            "closed": closed, "bbox_min": lo.round(3).tolist(), "bbox_max": hi.round(3).tolist(),
            "glb_bytes": glb.stat().st_size, "step_bytes": step.stat().st_size,
            "glb_reread_bbox_ok": reread_ok, "anchors": anchors, "notes": NOTES[pid],
        }
        ok = all(closed) and all(a["ok"] for a in anchors) and reread_ok
        all_ok &= all(closed) and reread_ok
        print("%-20s %7d triângulos, %6.0f kB GLB, %6.0f kB STEP, fechada: %s" %
              (pid, ntri, glb.stat().st_size / 1024, step.stat().st_size / 1024, "sim" if all(closed) else "NÃO"))
        print("    caixa: (%.2f, %.2f, %.2f) a (%.2f, %.2f, %.2f)" % (*lo, *hi))
        for a in anchors:
            print("    %-36s dist %.2f mm %s" % (a["anchor"], a["dist_mm"], "OK" if a["ok"] else "ACIMA DE %.0f mm" % TOL_ANCHOR))
    # envelope
    want = {"x": (0.0, L), "y": (Y0, M("card_envelope_height")), "z": (0.0, T)}
    env = {}
    print("\nEnvelope das quatro peças contra o CSV (tolerância %.1f mm)" % TOL_ENV)
    for i, ax in enumerate("xyz"):
        w0, w1 = want[ax]
        e0, e1 = lo_all[i] - w0, hi_all[i] - w1
        ok = abs(e0) <= TOL_ENV and abs(e1) <= TOL_ENV
        all_ok &= ok
        env[ax] = {"min": round(float(lo_all[i]), 3), "max": round(float(hi_all[i]), 3), "want": [w0, w1],
                   "err_min": round(float(e0), 3), "err_max": round(float(e1), 3), "ok": bool(ok)}
        print("    %s: %.2f a %.2f contra %.2f a %.2f (erro %+.2f / %+.2f) %s" % (ax, lo_all[i], hi_all[i], w0, w1, e0, e1, "OK" if ok else "FALHA"))
    ext_y = hi_all[1] - lo_all[1]
    print("    altura da carcaça %.2f contra shroud_height_proposed %.2f" % (ext_y, M("shroud_height_proposed")))
    report["envelope"] = env
    report["triangles_total"] = total_tris
    report["triangle_budget"] = TRI_BUDGET
    report["csv_keys_used"] = sorted(USED)
    # caixa do texto dentro da tampa superior
    _, _, covers, _ = face_b_regions()
    tb = poly(text_box())
    inside_area = (tb & covers[0]).area if (tb & covers[0]).faces() else 0.0
    report["text_box_inside_cover"] = round(inside_area / tb.area, 4)
    print("\nCaixa do texto dentro da tampa superior: %.1f %% da área" % (100 * inside_area / tb.area))
    print("Triângulos no total: %d (orçamento %d) %s" % (total_tris, TRI_BUDGET, "OK" if total_tris <= TRI_BUDGET else "ACIMA"))
    all_ok &= total_tris <= TRI_BUDGET
    (OUT / "frame-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Relatório: %s" % (OUT / "frame-report.json").relative_to(HARNESS.parent))
    print("Resultado (envelope, malhas fechadas, orçamento, releitura): %s" % ("OK" if all_ok else "FALHA"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
