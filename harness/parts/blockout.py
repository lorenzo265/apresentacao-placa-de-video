#!/usr/bin/env python3
"""Blockout da RTX PRO 6000 Blackwell Workstation Edition (F3, primeiro passo).

Lê design/assembly.json e design/measurements.csv e gera build/card.glb:
uma caixa (ou cilindro) por peça, só para aprovar câmera, ordem de explosão e textos.
Não é o modelo final.

Contrato: CAD em mm, Z para cima, origem em card.envelope_min. O GLB sai em metros,
com Y para cima: (x, y, z) do CAD vira (x, z, -y) / 1000. Um nó por peça, com o
nome igual ao id e a hierarquia de `parent`. A geometria já está na posição montada
(coordenadas de mundo); os nós têm transformação identidade, então mover um nó
(explosão) move também os filhos. Âncoras viram nós vazios filhos, com o id da âncora.

Uso:  python3 harness/parts/blockout.py [--sem-imagens]
Saídas: harness/build/card.glb, harness/build/blockout-report.json,
        harness/dist/blockout/*.png
"""
import csv
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import Align, Box, Cylinder, Pos

HARNESS = Path(__file__).resolve().parent.parent
ASSEMBLY = HARNESS / "design" / "assembly.json"
MEASURES = HARNESS / "design" / "measurements.csv"
BUILD = HARNESS / "build"
DIST = HARNESS / "dist" / "blockout"

SECTIONS = 32            # lados dos cilindros
TOL_ENV = 0.5            # mm, envelope
TOL_ANCHOR = 2.0         # mm, âncora fora do volume da peça
TOL_OVERLAP = 0.5        # mm, interpenetração

# ---------------------------------------------------------------------------
# Valores de bloqueio SEM base no CSV. Cada um é marcado no nó (blockout_guess).
# ---------------------------------------------------------------------------
G = {
    "screw_head_h": 1.2,        # altura das cabeças das fixações da placa de extremidade e do bracket
    "screw_d": 3.0,             # diâmetro de cabeça pequena
    "screw_d_big": 5.0,         # cabeça com arruela
    "bracket_clear": 0.2,       # folga das aberturas de DisplayPort no bracket
    "blade_w": 12.0,            # largura tangencial da pá
    "fan_back_t": 1.5,          # espessura do disco traseiro do rotor
    "flex_t": 0.3,              # espessura dos cabos flat
    "spring_ring_w": 8.0,       # largura do anel e dos braços da mola
    "back_ring_d": 6.0,         # diâmetro dos anéis da pcb.back_frame
    "back_frame_t": 0.8,        # espessura da pcb.back_frame
    "smd_h": 0.8,               # altura do bloco de componentes do verso
    "substrate_t": 1.0,         # substrato do package
    "stiff_t": 1.0,             # altura da moldura do package
    "base_plate_t": 1.0,        # placa de contato da base
    "base_frame_t": 4.0,        # altura da moldura da base (igual à câmara de vapor)
    "inductor_h": 3.0,          # altura dos indutores
    "stage_side": 4.0,          # lado dos estágios de potência
    "stage_h": 1.2,
    "aux_conn_h": 6.0,          # altura do conector auxiliar
    "aux_conn_depth": 4.0,
    "p16_depth": 11.0,          # profundidade (no plano) do conector de 16 pinos
    "p16_h": 7.0,               # altura do conector de 16 pinos
    "adapter_conn_w": 8.0,      # largura em y do conector J3
    "hp_pitch": 10.0,           # passo dos tubos de calor
}

NOTES = {}          # id -> lista de notas de bloqueio
OBS = []            # contradições e observações


def guess(pid, nota):
    NOTES.setdefault(pid, []).append(nota)


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def load_measures():
    out = {}
    with open(MEASURES, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["feature"]] = float(r["value_mm"])
    return out


MEAS = load_measures()


def M(k):
    return MEAS[k]


# ---------------------------------------------------------------------------
# Corpos (volumes simples, cada um fechado)
# ---------------------------------------------------------------------------
class Body:
    def __init__(self, verts, faces, convex=True):
        m = trimesh.Trimesh(np.asarray(verts, float), np.asarray(faces), process=False)
        m.merge_vertices()
        m.update_faces(m.nondegenerate_faces())
        m.remove_unreferenced_vertices()
        if m.volume < 0:
            m.invert()
        self.v = np.asarray(m.vertices, float)
        self.f = np.asarray(m.faces, np.int64)
        self.convex = convex
        self._ax = None

    def shifted(self, d):
        b = Body.__new__(Body)
        b.v = self.v + np.asarray(d, float)
        b.f = self.f
        b.convex = self.convex
        b._ax = None
        return b

    @property
    def lo(self):
        return self.v.min(axis=0)

    @property
    def hi(self):
        return self.v.max(axis=0)

    def mesh(self):
        return trimesh.Trimesh(self.v, self.f, process=False)

    def axes(self):
        if self._ax is None:
            m = self.mesh()
            nrm = np.round(m.face_normals, 5)
            nrm = np.unique(np.where(nrm[:, [0]] < 0, -nrm, nrm), axis=0)
            e = m.vertices[m.edges_unique[:, 1]] - m.vertices[m.edges_unique[:, 0]]
            ln = np.linalg.norm(e, axis=1)
            e = e[ln > 1e-9] / ln[ln > 1e-9, None]
            e = np.unique(np.round(np.where(e[:, [0]] < 0, -e, e), 4), axis=0)
            self._ax = (nrm, e)
        return self._ax


def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return Body(m.vertices, m.faces)


def cyl_z(cx, cy, z0, z1, r):
    m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=SECTIONS)
    m.apply_translation([cx, cy, (z0 + z1) / 2])
    return Body(m.vertices, m.faces)


def cyl_x(x0, x1, cy, cz, r):
    m = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=SECTIONS)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation([(x0 + x1) / 2, cy, cz])
    return Body(m.vertices, m.faces)


def prism(pts, z0, z1):
    """Prisma de polígono convexo (pontos em xy, ordem qualquer)."""
    p = np.array(pts, float)
    c = p.mean(axis=0)
    p = p[np.argsort(np.arctan2(p[:, 1] - c[1], p[:, 0] - c[0]))]
    n = len(p)
    v = np.vstack([np.c_[p, np.full(n, z0)], np.c_[p, np.full(n, z1)]])
    f = []
    for i in range(1, n - 1):
        f.append([0, i + 1, i])            # base inferior (normal para baixo)
        f.append([n, n + i, n + i + 1])    # base superior
    for i in range(n):
        j = (i + 1) % n
        f.append([i, j, n + j])
        f.append([i, n + j, n + i])
    return Body(v, f)


def rot_box_z(cx, cy, z0, z1, along, across, ang_deg, off=0.0):
    """Caixa de comprimento `along` (direção do ângulo) e largura `across`,
    cujo início está a `off` do centro (cx, cy)."""
    a = math.radians(ang_deg)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    c = np.array([cx, cy])
    p0, p1 = c + d * off, c + d * (off + along)
    pts = [p0 - n * across / 2, p0 + n * across / 2, p1 + n * across / 2, p1 - n * across / 2]
    return prism(pts, z0, z1)


def from_b3d(shape, convex=False):
    verts, tris = shape.tessellate(0.05)
    v = np.array([[p.X, p.Y, p.Z] for p in verts])
    return Body(v, np.array(tris), convex=convex)


def b3box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def b3cyl_z(cx, cy, z0, z1, r):
    return Pos(cx, cy, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def frame_boxes(x0, x1, y0, y1, z0, z1, hx0, hx1, hy0, hy1):
    """Quadro retangular com janela (hx0..hx1, hy0..hy1), em 4 caixas."""
    return [
        box(x0, x1, y0, hy0, z0, z1), box(x0, x1, hy1, y1, z0, z1),
        box(x0, hx0, hy0, hy1, z0, z1), box(hx1, x1, hy0, hy1, z0, z1),
    ]


# ---------------------------------------------------------------------------
# Peças. Cada construtor devolve {"bodies": [...]}  ou  {"instances": [[...], ...]}
# ---------------------------------------------------------------------------
def build_parts(asm):
    parts = {p["id"]: p for p in asm["parts"]}
    A = {p["id"]: [a["pos"] for a in p["anchors"]] for p in asm["parts"]}
    R = {}

    L, T = M("card_envelope_length"), M("card_thickness")
    wall = M("shroud_wall")
    y0 = M("iface_shroud_y_min")
    y1 = y0 + M("shroud_height_proposed")
    cy = M("iface_shroud_center_y")
    gT = M("layer_end_face_b_grid")
    zt = T - gT                                  # topo das paredes (a grade e o aro ficam acima)
    hx = G["screw_head_h"]
    fin1_len = M("fin_stack_end_1_length_x")
    fin2_len = M("fin_stack_end_2_length_x")
    dcx, dcy = M("iface_die_center_x"), M("iface_die_center_y")
    pcx, pcy = M("iface_pcb_center_x"), M("iface_pcb_center_y")
    cen_x0, cen_x1 = dcx - M("fin_stack_center_length_x") / 2, dcx + M("fin_stack_center_length_x") / 2
    fan_x = [M("fan1_center_from_bracket_end"), M("fan2_center_from_bracket_end")]
    fan_y = M("iface_fan_center_y")
    ring_r = M("fan_ring_outer_diameter") / 2
    pcb_x0, pcb_y0 = M("pcb_main_card_x_min"), M("pcb_main_card_y_min")
    pcb_x1, pcb_y1 = pcb_x0 + M("pcb_main_width"), pcb_y0 + M("pcb_main_height")
    pz_b, pz_f = M("iface_pcb_back_z"), M("iface_pcb_front_z")
    zc = M("iface_die_contact_z")

    R["card"] = {"bodies": []}

    # --- carcaça -----------------------------------------------------------
    ox = M("iface_shroud_power_opening_x")
    ow = M("conn16_header_width") + 2.0
    oz0, oz1 = 19.0, 36.0
    sh = [box(0, L, y0, y0 + wall, 0, zt),
          box(0, ox - ow / 2, y1 - wall, y1, 0, zt), box(ox + ow / 2, L, y1 - wall, y1, 0, zt),
          box(ox - ow / 2, ox + ow / 2, y1 - wall, y1, 0, oz0), box(ox - ow / 2, ox + ow / 2, y1 - wall, y1, oz1, zt),
          box(hx, hx + wall, y0 + wall, y1 - wall, 0, zt),
          box(L - wall, L, y0 + wall, y1 - wall, 0, zt)]
    guess("frame.shroud", "abertura retangular da borda superior para o conector de energia: x = iface_shroud_power_opening_x, largura = conn16_header_width + 2 mm, z de %.0f a %.0f mm (valor de bloqueio)" % (oz0, oz1))
    guess("frame.shroud", "recuo da parede de extremidade (altura das cabeças dos parafusos): %.1f mm" % hx)
    guess("frame.shroud", "placas da face A só nas pontas, com o recorte do aro de %.0f mm; o centro é a pilha cooler.fins.3" % (ring_r * 2))
    for fx, xa, xb in ((fan_x[0], hx + wall, cen_x0), (fan_x[1], cen_x1, L - wall)):
        plate = b3box(xa, xb, y0 + wall, y1 - wall, 0, wall) - b3cyl_z(fx, fan_y, -1, wall + 1, ring_r)
        sh.append(from_b3d(plate))
    R["frame.shroud"] = {"bodies": sh}

    R["frame.face_b"] = {"bodies": [
        box(hx + wall, fin1_len, y0 + wall, y1 - wall, zt, T),
        box(L - fin2_len, L - wall, y0 + wall, y1 - wall, zt, T)]}

    # parafusos da placa de extremidade
    dp_a = A["io.board.dp"]
    yp = sorted(a[1] for a in dp_a)
    mid = [(yp[i] + yp[i + 1]) / 2 for i in range(len(yp) - 1)]
    ys5 = [yp[0] - M("dp_port_pitch"), *mid, yp[-1] + M("dp_port_pitch")]
    zc_dp = T / 2
    inst = []
    for yy in (y0 + wall + 4, y1 - wall - 4):
        for zz in (4, T - 4):
            inst.append([cyl_x(0, hx, yy, zz, G["screw_d_big"] / 2)])
    for yy in ys5:
        for zz in (zc_dp - 9, zc_dp + 9):
            inst.append([cyl_x(0, hx, yy, zz, G["screw_d"] / 2)])
    R["fasteners.end_plate"] = {"instances": inst}
    guess("fasteners.end_plate", "posições dos 14 parafusos (4 nos cantos com arruela, 10 em volta dos DisplayPort) e tamanho: sem medida")

    # placa das saídas de vídeo e portas
    depth = M("dp_receptacle_depth")
    R["io.board"] = {"bodies": [box(depth, depth + M("pcb_thickness"),
                                    cy - M("io_board_outline_long") / 2, cy + M("io_board_outline_long") / 2,
                                    T / 2 - M("io_board_outline_short") / 2, T / 2 + M("io_board_outline_short") / 2)]}
    guess("io.board", "orientação (placa normal a x, contorno longo em y, curto em z): pendência do planejador")
    R["io.board.dp"] = {"instances": [[box(0, depth, a[1] - M("dp_receptacle_width") / 2, a[1] + M("dp_receptacle_width") / 2,
                                           a[2] - M("dp_receptacle_height") / 2, a[2] + M("dp_receptacle_height") / 2)]
                                      for a in dp_a]}
    guess("io.board.dp", "largura do receptáculo ao longo de y e altura ao longo de z (orientação)")

    # bracket
    bt = M("bracket_thickness")
    bh = M("bracket_height_overall")
    br = b3box(-bt, 0, cy - bh / 2, cy + bh / 2, 0, T)
    cl = G["bracket_clear"]
    for a in dp_a:
        br = br - b3box(-bt - 1, 1, a[1] - M("dp_receptacle_width") / 2 - cl, a[1] + M("dp_receptacle_width") / 2 + cl,
                        a[2] - M("dp_receptacle_height") / 2 - cl, a[2] + M("dp_receptacle_height") / 2 + cl)
    R["io.bracket"] = {"bodies": [from_b3d(br)]}
    guess("io.bracket", "folga de %.1f mm nas aberturas dos DisplayPort; largura em z igual à espessura da placa (não é o bracket de norma)" % cl)
    R["fasteners.e1_bracket"] = {"instances": [
        [cyl_x(-bt - hx, -bt, yy, zz, G["screw_d"] / 2)]
        for yy in (cy - bh / 2 + 5, cy + bh / 2 - 5) for zz in (5, T - 5)]}
    guess("fasteners.e1_bracket", "posição, tamanho e altura das cabeças")

    # aro e tampas
    R["frame.rim"] = {"bodies": frame_boxes(0, L, y0, y1, zt, T, wall, L - wall, y0 + wall, y1 - wall)}
    guess("frame.rim", "largura do aro igual à parede da carcaça")
    R["fasteners.e2_rim"] = {"instances": [[cyl_z(wall / 2, y0 + 9, T - 0.8, T, wall * 0.4)]]}
    guess("fasteners.e2_rim", "posição e tamanho (rente ao aro, para não passar da espessura)")
    ct = M("layer_center_covers")
    xa, xb = fin1_len, L - fin2_len
    ylo, yhi = y0 + wall, y1 - wall
    R["frame.center_covers"] = {"instances": [
        [prism([(xa, ylo), (xb, ylo), (dcx, dcy)], T - ct, T)],
        [prism([(xa, yhi), (xb, yhi), (dcx, dcy)], T - ct, T)]]}
    guess("frame.center_covers", "contorno das duas tampas triangulares (aqui: inferior e superior, com vértice no centro do die)")

    # adaptador PCIe
    az0 = M("iface_adapter_board_z_min")
    az1 = az0 + M("pcb_thickness")
    f0 = M("pcie_fingers_start_from_bracket_end")
    cx_c = M("pcie_adapter_connector_x")
    tabw = M("pcie_adapter_tab_width")
    cn_len = M("pcie_adapter_connector_length")
    cn_y = M("pcie_adapter_connector_center_y")
    R["pcie.adapter"] = {"bodies": [
        box(f0, f0 + M("pcie_adapter_length"), 0, M("pcie_adapter_strip_height"), az0, az1),
        box(cx_c - tabw / 2, cx_c + tabw / 2, 0, M("pcie_adapter_total_height"), az0, az1),
        box(cx_c - cn_len / 2, cx_c + cn_len / 2, cn_y - G["adapter_conn_w"] / 2, cn_y + G["adapter_conn_w"] / 2, pz_b, az0)]}
    guess("pcie.adapter", "largura em y do conector J3 (%.0f mm) e início da tira junto aos contatos" % G["adapter_conn_w"])
    sc = G["screw_d"] / 2
    hz = 0.9
    R["fasteners.e4_pcie"] = {"instances": [[cyl_z(px, py, az1, az1 + hz, sc)] for px, py in
                                            [(cx_c - 16, 10), (cx_c + 16, 10), (cx_c - 16, 30), (cx_c + 16, 30), (60, 8), (95, 8)]]}
    guess("fasteners.e4_pcie", "posição e tamanho das 6 cabeças")

    # placa central e parafusos
    ph = M("iface_plate_holes_dx") / 2
    pv = M("iface_plate_holes_dy") / 2
    pw = M("pcb_plate_window") / 2
    pz0, pz1 = T - M("layer_center_covers") - M("layer_pcb_plate"), T - M("layer_center_covers")
    R["pcb.plate"] = {"bodies": frame_boxes(pcx - M("pcb_plate_outline_x") / 2, pcx + M("pcb_plate_outline_x") / 2,
                                            pcy - M("pcb_plate_outline_y") / 2, pcy + M("pcb_plate_outline_y") / 2,
                                            pz0, pz1, dcx - pw, dcx + pw, dcy - pw, dcy + pw)}
    guess("pcb.plate", "janela do furo centrada no die; sem as 4 abas nem os pads; contorno de 104 x 108 (escala antiga) é menor que o padrão de furos de 106 x 102")
    R["fasteners.e5_plate"] = {"instances": [[cyl_z(pcx + sx * ph, pcy + sy * pv, pz1, pz1 + 1.5, G["screw_d_big"] / 2)]
                                             for sx in (-1, 1) for sy in (-1, 1)]}
    guess("fasteners.e5_plate", "diâmetro e altura da cabeça")

    # cabos flat
    ft = G["flex_t"]
    fw = M("flex_dp_width")
    R["flex.dp"] = {"bodies": [box(depth + M("pcb_thickness"), pcb_x0, pcb_y0, pcb_y0 + fw, pz_b, pz_b + ft)]}
    guess("flex.dp", "espessura; trecho reto do conector até a placa das portas (%.0f mm), menor que flex_dp_length (%.0f mm), que inclui as curvas"
          % (pcb_x0 - depth - M("pcb_thickness"), M("flex_dp_length")))
    ffw = M("flex_fan_width")
    R["flex.fan.1"] = {"bodies": [box(fan_x[0], pcb_x0, 40, 40 + ffw, pz_b, pz_b + ft)]}
    R["flex.fan.2"] = {"bodies": [box(pcb_x1, fan_x[1], 40, 40 + ffw, pz_b, pz_b + ft)]}
    for k in ("flex.fan.1", "flex.fan.2"):
        guess(k, "posição, trajeto e espessura (posição não medida)")

    # mola
    sx_, sy_ = M("iface_spring_holes_dx") / 2, M("iface_spring_holes_dy") / 2
    st = M("leaf_spring_thickness")
    ww, wh = M("leaf_spring_window_x") / 2, M("leaf_spring_window_y") / 2
    rw = G["spring_ring_w"]
    ro_x, ro_y = ww + rw, wh + rw
    zs0, zs1 = pz_b, pz_b + st
    sp = frame_boxes(dcx - ro_x, dcx + ro_x, dcy - ro_y, dcy + ro_y, zs0, zs1, dcx - ww, dcx + ww, dcy - wh, dcy + wh)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c, r = (dcx + sx * sx_, dcy + sy * sy_), (dcx + sx * ro_x, dcy + sy * ro_y)
            dv = np.array(r) - np.array(c)
            nv = np.array([-dv[1], dv[0]]) / np.linalg.norm(dv) * rw / 2
            sp.append(prism([np.array(c) - nv, np.array(c) + nv, np.array(r) + nv, np.array(r) - nv], zs0, zs1))
    R["cooler.leaf_spring"] = {"bodies": sp}
    guess("cooler.leaf_spring", "largura do anel e dos 4 braços (%.0f mm) e formato em X" % rw)
    R["fasteners.e6_spring"] = {"instances": [[cyl_z(dcx + sx * sx_, dcy + sy * sy_, zs1, pz_b + M("layer_back_mem_pad"), G["screw_d_big"] / 2)]
                                              for sx in (-1, 1) for sy in (-1, 1)]}
    guess("fasteners.e6_spring", "diâmetro da cabeça; altura = layer_back_mem_pad menos a espessura da mola")

    # PCB e o que está nele
    ca = math.radians(M("pcb_main_chamfer_angle_deg"))
    cxp0, cyp0 = M("power_connector_center_from_bracket_end"), M("power_connector_center_y")
    off = G["p16_depth"] / 2          # a linha do chanfro fica a meia profundidade do corpo, para fora
    px0, py0 = cxp0 + off * math.sin(ca), cyp0 + off * math.cos(ca)
    t_top = (py0 - pcb_y1) / math.sin(ca)
    x_top = px0 + t_top * math.cos(ca)
    t_r = (pcb_x1 - px0) / math.cos(ca)
    y_r = py0 - t_r * math.sin(ca)
    rd = M("pcb_main_contact_edge_recess_depth")
    r0, r1 = pcb_x0 + M("pcb_main_contact_edge_recess_u_start"), pcb_x0 + M("pcb_main_contact_edge_recess_u_end")
    R["pcb.main"] = {"bodies": [
        prism([(pcb_x0, pcb_y0 + rd), (pcb_x1, pcb_y0 + rd), (pcb_x1, y_r), (x_top, pcb_y1), (pcb_x0, pcb_y1)], pz_f, pz_b),
        box(pcb_x0, r0, pcb_y0, pcb_y0 + rd, pz_f, pz_b), box(r1, pcb_x1, pcb_y0, pcb_y0 + rd, pz_f, pz_b)]}
    guess("pcb.main", "tamanho do chanfro (catetos de %.1f mm em x e %.1f mm em y): sem medida, a linha passa a meia profundidade do corpo do conector (%.0f mm, valor de bloqueio); sem o recorte em V" %
          (pcb_x1 - x_top, pcb_y1 - y_r, G["p16_depth"]))
    R["pcb.back_frame"] = {"instances": [[cyl_z(dcx + sx * sx_, dcy + sy * sy_, pz_b, pz_b + G["back_frame_t"], G["back_ring_d"] / 2)]
                                         for sx in (-1, 1) for sy in (-1, 1)]}
    guess("pcb.back_frame", "contorno e espessura sem dados: só 4 anéis nos furos da mola")
    sw = M("pcb_plate_window") / 2 - 2
    R["pcb.smd"] = {"bodies": [box(dcx - sw, dcx + sw, dcy - sw, dcy + sw, pz_b, pz_b + G["smd_h"])]}
    guess("pcb.smd", "bloco único atrás do chip, sem quantidade nem medidas")

    # package: substrato, moldura e die (z cresce para a face B; a frente do PCB é pz_f, a face A fica abaixo)
    px, py = M("gb202_package_x") / 2, M("gb202_package_y") / 2   # lado longo em x
    wx, wy = M("gb202_window_x") / 2, M("gb202_window_y") / 2
    dx, dy = M("gb202_die_x") / 2, M("gb202_die_y") / 2
    die_top = pz_f - M("gb202_die_top_above_pcb")
    sub0 = pz_f - G["substrate_t"]
    R["gpu.package"] = {"bodies": [
        box(dcx - px, dcx + px, dcy - py, dcy + py, sub0, pz_f),
        *frame_boxes(dcx - px, dcx + px, dcy - py, dcy + py, sub0 - G["stiff_t"], sub0, dcx - wx, dcx + wx, dcy - wy, dcy + wy),
        box(dcx - dx, dcx + dx, dcy - dy, dcy + dy, die_top, sub0)]}
    guess("gpu.package", "espessura do substrato (%.1f) e da moldura (%.1f); a altura do die sai de gb202_die_top_above_pcb" % (G["substrate_t"], G["stiff_t"]))
    R["gpu.tim"] = {"bodies": [box(dcx - dx, dcx + dx, dcy - dy, dcy + dy, zc, die_top)]}

    # memória
    gt = M("gddr7_package_thickness")
    gw, gl = M("mem_footprint_across_row"), M("mem_footprint_along_row")   # lateral: x atravessa a fileira, y é ao longo dela
    grid = []
    for i in range(5):
        grid.append((pcb_x0 + M("mem_side_bracket_u"), pcb_y0 + M("mem_side_v_first") + i * M("mem_side_v_pitch"), gw, gl))
    for i in range(5):
        grid.append((pcb_x0 + M("mem_side_opposite_u"), pcb_y0 + M("mem_side_v_first") + i * M("mem_side_v_pitch"), gw, gl))
    for i in range(4):
        grid.append((pcb_x0 + M("mem_power_edge_u_first") + i * M("mem_power_edge_u_pitch"), pcb_y0 + M("mem_power_edge_v"), gl, gw))
    for u in (M("mem_contact_edge_u_1"), M("mem_contact_edge_u_2")):
        grid.append((pcb_x0 + u, pcb_y0 + M("mem_contact_edge_v"), gl, gw))
    for a_id, zlo, zhi in (("mem.back", pz_b, pz_b + gt), ("mem.front", pz_f - gt, pz_f)):
        for k, a in enumerate(A[a_id]):
            if abs(a[0] - grid[k][0]) > 0.01 or abs(a[1] - grid[k][1]) > 0.01:
                OBS.append("%s.%d: âncora (%.2f, %.2f) difere da grade mem_* do CSV (%.2f, %.2f)" % (a_id, k + 1, a[0], a[1], grid[k][0], grid[k][1]))
        R[a_id] = {"instances": [[box(gx - w / 2, gx + w / 2, gy - h / 2, gy + h / 2, zlo, zhi)] for gx, gy, w, h in grid]}

    # energia
    ang = M("power_connector_rotation_deg")
    cxp = M("power_connector_center_from_bracket_end")
    cw = M("conn16_header_width")
    R["power.connector"] = {"bodies": [_rot_centered(cxp, M("power_connector_center_y"), pz_f - G["p16_h"], pz_f, cw, G["p16_depth"], ang)]}
    guess("power.connector", "profundidade (%.0f) e altura (%.0f) do corpo; o centro y vem de power_connector_center_y, que o CSV declara escolha de bloqueio" % (G["p16_depth"], G["p16_h"]))
    au = M("aux_header_u")
    al = M("aux_header_length")
    R["io.aux_header"] = {"bodies": [box(pcb_x0 + au - al / 2, pcb_x0 + au + al / 2, pcb_y1 - G["aux_conn_depth"], pcb_y1,
                                         pz_f - G["aux_conn_h"], pz_f)]}
    guess("io.aux_header", "profundidade e altura do corpo")

    s = M("vrm_inductor_side")
    yc, yp_ = M("iface_contact_edge_band_y"), M("iface_power_edge_band_y")
    n_ind = parts["power.inductors"]["count"]["value"]
    n_c = int(M("power_inductors_contact_edge_count"))
    n_t = int(M("power_inductors_top_edge_count"))
    n_f = n_ind - n_c - n_t
    OBS.append("power.inductors: CSV pede %d + %.1f + %d (soma %.1f), o assembly tem count %d; a ponta longe do bracket ficou com %d"
               % (n_c, M("power_inductors_far_end_count"), n_t, n_c + M("power_inductors_far_end_count") + n_t, n_ind, n_f))
    far_x, far_y = M("iface_far_end_inductor_band_x"), M("iface_far_end_inductor_band_y")
    pos = ([(dcx + 8.0 * (k - n_c // 2 + 1), yc) for k in range(n_c)]
           + [(dcx + 7.0 * (k - (n_t - 1) / 2), yp_) for k in range(n_t)]
           + [(far_x, far_y + 8.0 * (k - (n_f - 1) / 2)) for k in range(n_f)])
    guess("power.inductors", "passos entre indutores (8 e 7 mm) e contagem %d na ponta longe do bracket (o CSV dá %.1f; total fixado pelo assembly)" % (n_f, M("power_inductors_far_end_count")))
    R["power.inductors"] = {"instances": [[box(x - s / 2, x + s / 2, y - s / 2, y + s / 2, pz_f - G["inductor_h"], pz_f)] for x, y in pos]}
    guess("power.inductors", "altura (%.0f mm), repartição 13 + 11 e passo (8 mm na borda dos contatos): representativos" % G["inductor_h"])
    ss = G["stage_side"] / 2
    R["power.vrm.gpu"] = {"instances": [[box(x - ss, x + ss, y - ss, y + ss, pz_b, pz_b + G["stage_h"])] for x, y in pos]}
    guess("power.vrm.gpu", "posição (verso, atrás de cada indutor) e tamanho: sem fonte")
    xb = far_x + 1.2     # coluna livre perto da ponta longe do bracket, abaixo dos indutores
    R["power.vrm.mem"] = {"instances": [[box(xb - 2.5, xb + 2.5, y - 2.5, y + 2.5, pz_f - 1.5, pz_f)] for y in (26.5, 32.0, 37.5, 43.0)]}
    R["power.aux"] = {"instances": [[box(x - 2, x + 2, 23 - 2, 23 + 2, pz_f - 1.5, pz_f)] for x in (197.5, 202.5, 207.5)]}
    R["power.controller"] = {"instances": [[box(pcb_x0 + 6 - 3, pcb_x0 + 6 + 3, pcb_y0 + v - 3, pcb_y0 + v + 3, pz_f - 1.0, pz_f)] for v in (9, 17)]}
    for k in ("power.vrm.mem", "power.aux", "power.controller"):
        guess(k, "posição e dimensões inventadas só para o bloqueio (a proposta não as define)")
        NOTES[k].append("position_unknown")

    # --- cooler -------------------------------------------------------------
    fd = M("fan_axial_depth")
    rr = M("fan_rotor_diameter") / 2
    hr = M("fan_hub_diameter") / 2
    nb = parts["cooler.fan.1.blade"]["count"]["value"]
    for n in (1, 2):
        fx = fan_x[n - 1]
        R["cooler.fan.%d" % n] = {"bodies": [cyl_z(fx, fan_y, 0, fd, hr), cyl_z(fx, fan_y, fd - G["fan_back_t"], fd, rr)]}
        guess("cooler.fan.%d" % n, "espessura do disco traseiro do rotor (%.1f mm)" % G["fan_back_t"])
        R["cooler.fan.%d.blade" % n] = {"instances": [
            [rot_box_z(fx, fan_y, 0, fd - G["fan_back_t"], rr - hr, G["blade_w"], 360.0 * i / nb, off=hr)] for i in range(nb)]}
        guess("cooler.fan.%d.blade" % n, "forma da pá: caixa radial de %.0f mm de largura (a forma real é pendência)" % G["blade_w"])

    fh = M("fin_stack_end_height_y")
    z_f0 = M("layer_end_fan_ring")
    z_f1 = z_f0 + M("fin_stack_end_depth_z")
    R["cooler.fins.1"] = {"bodies": [box(0, fin1_len, cy - fh / 2, cy + fh / 2, z_f0, z_f1)]}
    R["cooler.fins.2"] = {"bodies": [box(L - fin2_len, L, cy - fh / 2, cy + fh / 2, z_f0, z_f1)]}
    for k in ("cooler.fins.1", "cooler.fins.2"):
        guess(k, "pilha inteira em uma caixa; as 60 aletas não são modeladas")

    bx, by = M("cooler_base_frame_outline_x") / 2, M("cooler_base_frame_outline_y") / 2
    vx, vy = M("vapor_chamber_contact_plate_x") / 2, M("vapor_chamber_contact_plate_y") / 2
    vt = M("vapor_chamber_thickness")
    R["cooler.base"] = {"bodies": [
        *frame_boxes(pcx - bx, pcx + bx, pcy - by, pcy + by, zc - G["base_frame_t"], zc, dcx - vx, dcx + vx, dcy - vy, dcy + vy),
        box(dcx - vx, dcx + vx, dcy - vy, dcy + vy, zc - G["base_plate_t"], zc)]}
    guess("cooler.base", "altura da moldura e espessura da placa de contato; a placa de contato sobrepõe a câmara de vapor (peça filha)")
    R["cooler.vapor_chamber"] = {"bodies": [box(dcx - vx, dcx + vx, dcy - vy, dcy + vy, zc - vt, zc)]}
    R["cooler.fins.3"] = {"bodies": [box(cen_x0, cen_x1, dcy - by, dcy + by, 0, M("layer_center_fins_face_a"))]}
    guess("cooler.fins.3", "extensão em y (igual à moldura da base): proposta não define")

    hd = M("heatpipe_diameter") / 2
    hl = M("heatpipe_length_per_side")
    nh = parts["cooler.heatpipes"]["count"]["value"]
    per = nh // 2
    zhp = zc - vt / 2
    hp = []
    for side in (-1, 1):
        for i in range(per):
            yy = dcy + G["hp_pitch"] * (i - (per - 1) / 2)
            xa_, xb_ = dcx + side * vx, dcx + side * (vx + hl)
            hp.append([cyl_x(min(xa_, xb_), max(xa_, xb_), yy, zhp, hd)])
    R["cooler.heatpipes"] = {"instances": hp}
    guess("cooler.heatpipes", "passo entre tubos (%.0f mm) e altura em z (meio da câmara); traçado reto" % G["hp_pitch"])

    missing = [i for i in parts if i not in R]
    if missing:
        raise SystemExit("peças sem construtor: %s" % missing)
    return R


def _rot_centered(cx, cy, z0, z1, w, d, ang_deg):
    a = math.radians(ang_deg)
    e1 = np.array([math.cos(a), math.sin(a)])
    e2 = np.array([-e1[1], e1[0]])
    c = np.array([cx, cy])
    pts = [c + s1 * e1 * w / 2 + s2 * e2 * d / 2 for s1 in (-1, 1) for s2 in (-1, 1)]
    return prism(pts, z0, z1)


# ---------------------------------------------------------------------------
# Grupos e cores
# ---------------------------------------------------------------------------
def group_of(pid):
    if pid.startswith("fasteners."):
        return "fixadores"
    if pid.startswith("mem."):
        return "memoria"
    if pid.startswith("power."):
        return "energia"
    if pid.startswith("io.") or pid == "pcie.adapter":
        return "io"
    if pid.startswith("cooler."):
        return "cooler"
    if pid.startswith("frame."):
        return "carcaca"
    return "pcb"


COLORS = {
    "carcaca": (0.30, 0.32, 0.36), "cooler": (0.55, 0.60, 0.66), "pcb": (0.16, 0.45, 0.30),
    "memoria": (0.78, 0.62, 0.20), "energia": (0.78, 0.35, 0.22), "io": (0.30, 0.52, 0.80),
    "fixadores": (0.85, 0.85, 0.85),
}


# ---------------------------------------------------------------------------
# Cena e GLB
# ---------------------------------------------------------------------------
def to_gltf(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]] / 1000.0


def build_scene(asm, R):
    parts = asm["parts"]
    nodes = []
    idx = {}
    mats = list(COLORS)
    meshes = []
    buf = bytearray()
    views, accs = [], []

    def add_mesh(name, bodies, group):
        v_all, f_all, off = [], [], 0
        for b in bodies:
            v_all.append(to_gltf(b.v))
            f_all.append(b.f + off)
            off += len(b.v)
        V = np.vstack(v_all).astype("<f4")
        F = np.vstack(f_all)
        ityp, icode = (np.dtype("<u2"), 5123) if len(V) < 65535 else (np.dtype("<u4"), 5125)
        F = F.astype(ityp).reshape(-1)
        out = []
        for data, target in ((V, 34962), (F, 34963)):
            while len(buf) % 4:
                buf.append(0)
            views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": data.nbytes, "target": target})
            buf.extend(data.tobytes())
            out.append(len(views) - 1)
        accs.append({"bufferView": out[0], "componentType": 5126, "count": len(V), "type": "VEC3",
                     "min": V.min(axis=0).tolist(), "max": V.max(axis=0).tolist()})
        accs.append({"bufferView": out[1], "componentType": icode, "count": len(F), "type": "SCALAR"})
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": len(accs) - 2}, "indices": len(accs) - 1,
                                                     "material": mats.index(group), "mode": 4}]})
        return len(meshes) - 1

    def new_node(name, extras, mesh=None, trans=None):
        n = {"name": name, "extras": extras}
        if mesh is not None:
            n["mesh"] = mesh
        if trans is not None:
            n["translation"] = [float(t) for t in trans]
        nodes.append(n)
        return len(nodes) - 1

    def link(parent, child):
        nodes[parent].setdefault("children", []).append(child)

    for p in parts:
        pid = p["id"]
        g = group_of(pid) if p["parent"] else None
        notes = [n for n in NOTES.get(pid, []) if n != "position_unknown"]
        ex = {"stage": p["stage"], "fidelity": p["fidelity"], "exists_provenance": p["exists_provenance"],
              "shape_provenance": p["shape_provenance"],
              "blockout": True, "blockout_guess": bool(notes), "blockout_notes": notes,
              "explode_cad": p["explode"]}
        if g:
            ex["group"] = g
        if "position_unknown" in NOTES.get(pid, []):
            ex["position_unknown"] = True
        if "count" in p:
            ex["count"] = p["count"]["value"]
            ex["count_provenance"] = p["count"]["provenance"]
            if p["count"].get("representative"):
                ex["count_representative"] = True
        r = R[pid]
        if "bodies" in r:
            mesh = add_mesh(pid, r["bodies"], g) if r["bodies"] else None
            idx[pid] = new_node(pid, ex, mesh)
        else:
            idx[pid] = new_node(pid, ex)
            for k, bodies in enumerate(r["instances"], 1):
                ie = {"stage": p["stage"], "fidelity": p["fidelity"], "exists_provenance": p["exists_provenance"],
                      "shape_provenance": p["shape_provenance"], "group": g, "blockout": True,
                      "blockout_guess": bool(notes), "instance_of": pid, "instance": k}
                iid = new_node("%s.%d" % (pid, k), ie, add_mesh("%s.%d" % (pid, k), bodies, g))
                link(idx[pid], iid)
                idx["%s.%d" % (pid, k)] = iid
    for p in parts:
        if p["parent"]:
            link(idx[p["parent"]], idx[p["id"]])
    # âncoras: nós vazios com o id da âncora, filhos da peça (ou da instância, se 1 para 1)
    for p in parts:
        n_inst = len(R[p["id"]].get("instances", []))
        for k, a in enumerate(p["anchors"], 1):
            tgt = idx[p["id"]]
            if n_inst > 1 and len(p["anchors"]) == n_inst:
                tgt = idx["%s.%d" % (p["id"], k)]
            aid = new_node(a["id"], {"anchor": True, "part": p["id"]}, trans=to_gltf([a["pos"]])[0])
            link(tgt, aid)
    roots = [idx[p["id"]] for p in parts if not p["parent"]]
    gltf = {
        "asset": {"version": "2.0", "generator": "harness/parts/blockout.py",
                  "extras": {"blockout": True, "units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z",
                             "origin": "card.envelope_min", "map": "gltf = (x, z, -y) / 1000"}},
        "scene": 0, "scenes": [{"name": "card", "nodes": roots}], "nodes": nodes, "meshes": meshes,
        "materials": [{"name": m, "pbrMetallicRoughness": {"baseColorFactor": [*COLORS[m], 1.0], "metallicFactor": 0.0, "roughnessFactor": 0.85}}
                      for m in mats],
        "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}],
    }
    return gltf, bytes(buf), idx


def write_glb(path, gltf, binary):
    js = json.dumps(gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    js += b" " * (-len(js) % 4)
    binary += b"\0" * (-len(binary) % 4)
    total = 12 + 8 + len(js) + 8 + len(binary)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binary), 0x004E4942) + binary)


# ---------------------------------------------------------------------------
# Conferências
# ---------------------------------------------------------------------------
def descendants(parts):
    kids = {}
    for p in parts:
        kids.setdefault(p["parent"], []).append(p["id"])
    out = {}

    def walk(i):
        s = set()
        for c in kids.get(i, []):
            s |= {c} | walk(c)
        out[i] = s
        return s
    for p in parts:
        if not p["parent"]:
            walk(p["id"])
    return out


def all_bodies(R, pid):
    r = R[pid]
    return r["bodies"] if "bodies" in r else [b for inst in r["instances"] for b in inst]


def penetration(a, b):
    lo, hi = np.maximum(a.lo, b.lo), np.minimum(a.hi, b.hi)
    if np.any(hi - lo <= 0):
        return 0.0
    na, ea = a.axes()
    nb, eb = b.axes()
    ax = list(na) + list(nb)
    if len(ea) <= 12 and len(eb) <= 12:
        for x in ea:
            for y in eb:
                c = np.cross(x, y)
                n = np.linalg.norm(c)
                if n > 1e-6:
                    ax.append(c / n)
    best = math.inf
    for d in ax:
        pa, pb = a.v @ d, b.v @ d
        ov = min(pa.max(), pb.max()) - max(pa.min(), pb.min())
        if ov <= 0:
            return 0.0
        best = min(best, ov)
    return best


def checks(asm, R):
    parts = asm["parts"]
    P = {p["id"]: p for p in parts}
    desc = descendants(parts)
    rep = {}
    ok_all = True

    # 1. envelope (bracket e filhos fora)
    bracket = {"io.bracket"} | desc["card"] & {"fasteners.e1_bracket"}
    bs = [b for pid in P for b in all_bodies(R, pid) if pid not in bracket]
    lo = np.min([b.lo for b in bs], axis=0)
    hi = np.max([b.hi for b in bs], axis=0)
    ext = hi - lo
    want = [M("card_envelope_length"), M("card_envelope_height"), M("card_thickness")]
    print("\n[1] Envelope do GLB (sem o bracket), mm")
    rep["envelope"] = {}
    for name, e, w, l_, h_ in zip("xyz", ext, want, lo, hi):
        ok = abs(e - w) <= TOL_ENV
        ok_all &= ok
        print("    %s: %.2f (min %.2f, max %.2f) contra %.2f  erro %+.2f  %s" % (name, e, l_, h_, w, e - w, "OK" if ok else "FALHA"))
        rep["envelope"][name] = {"extent": round(float(e), 3), "min": round(float(l_), 3), "max": round(float(h_), 3), "target": w, "ok": bool(ok)}
    om = np.abs(lo)
    print("    origem: mínimo do envelope em (%.2f, %.2f, %.2f), esperado (0, 0, 0)" % tuple(lo))
    bb = [b for pid in bracket for b in all_bodies(R, pid)]
    blo, bhi = np.min([b.lo for b in bb], axis=0), np.max([b.hi for b in bb], axis=0)
    print("    bracket (à parte): x %.2f a %.2f, y %.2f a %.2f, z %.2f a %.2f" % (blo[0], bhi[0], blo[1], bhi[1], blo[2], bhi[2]))
    rep["bracket"] = {"min": blo.round(3).tolist(), "max": bhi.round(3).tolist()}

    # 2. ids
    print("\n[2] Nós por id")
    miss = [i for i in P if i not in NODE_IDX]
    print("    %d de %d ids com nó%s" % (len(P) - len(miss), len(P), "" if not miss else "; faltam %s" % miss))
    rep["ids_sem_no"] = miss
    ok_all &= not miss

    # 3. âncoras
    print("\n[3] Âncoras fora do volume da peça (distância ao corpo mais próximo, caixa envolvente do corpo)")
    far, near = [], 0
    for pid, p in P.items():
        bodies = all_bodies(R, pid) or [b for d in desc[pid] for b in all_bodies(R, d)]
        for a in p["anchors"]:
            pt = np.array(a["pos"])
            dist = min(np.linalg.norm(np.maximum(np.maximum(b.lo - pt, pt - b.hi), 0)) for b in bodies)
            if dist > 0.5:
                far.append((a["id"], pid, dist))
            else:
                near += 1
    for aid, pid, d in sorted(far, key=lambda t: -t[2]):
        print("    %-28s %-24s %6.2f mm  %s" % (aid, pid, d, "ACIMA DE %.0f mm" % TOL_ANCHOR if d > TOL_ANCHOR else "(até %.0f mm)" % TOL_ANCHOR))
    print("    %d âncoras dentro do volume (até 0,5 mm); %d fora, das quais %d acima de %.0f mm" %
          (near, len(far), sum(1 for f in far if f[2] > TOL_ANCHOR), TOL_ANCHOR))
    rep["ancoras_fora"] = [{"anchor": a, "part": p_, "dist_mm": round(float(d), 2)} for a, p_, d in far]

    # 4. interpenetração
    ids = list(P)
    pairs = {"mesmo_estagio": [], "estagios_diferentes": []}
    skipped = [i for i in ids if any(not b.convex for b in all_bodies(R, i))]
    for i, a_id in enumerate(ids):
        for b_id in ids[i + 1:]:
            if b_id in desc[a_id] or a_id in desc[b_id]:
                continue
            best = 0.0
            for ba in all_bodies(R, a_id):
                if not ba.convex:
                    continue
                for bb_ in all_bodies(R, b_id):
                    if bb_.convex:
                        best = max(best, penetration(ba, bb_))
            if best > TOL_OVERLAP:
                same = P[a_id]["stage"] == P[b_id]["stage"]
                pairs["mesmo_estagio" if same else "estagios_diferentes"].append(
                    {"a": a_id, "b": b_id, "stage": P[a_id]["stage"], "penetration_mm": round(best, 2)})
    print("\n[4] Interpenetração acima de %.1f mm (filhos de uma peça não contam contra ela)" % TOL_OVERLAP)
    print("    Mesmo estágio: %d pares" % len(pairs["mesmo_estagio"]))
    for q in sorted(pairs["mesmo_estagio"], key=lambda q: str(q["stage"])):
        print("      %-4s %-26s x %-26s %.2f mm" % (q["stage"], q["a"], q["b"], q["penetration_mm"]))
    watch = {"pcie.adapter", "fasteners.e5_plate", "power.connector", "pcb.plate"}
    cross = pairs["estagios_diferentes"]
    print("    Estágios diferentes: %d pares no total (lista completa em build/blockout-report.json). Os que envolvem as interferências avisadas:" % len(cross))
    for q in cross:
        if q["a"] in watch or q["b"] in watch:
            print("      %-26s (%s) x %-26s (%s) %.2f mm" % (q["a"], P[q["a"]]["stage"], q["b"], P[q["b"]]["stage"], q["penetration_mm"]))
    print("    Fora desta conta (corpo não convexo, só caixa envolvente): %s" % ", ".join(skipped))
    rep["interpenetracao"] = pairs
    rep["corpos_nao_convexos_ignorados"] = skipped
    return rep, ok_all


# ---------------------------------------------------------------------------
# Imagens
# ---------------------------------------------------------------------------
def offsets(asm):
    P = {p["id"]: p for p in asm["parts"]}
    memo = {}

    def off(i):
        if i is None:
            return np.zeros(3)
        if i not in memo:
            e = P[i]["explode"]
            memo[i] = off(P[i]["parent"]) + np.array(e["dir"], float) * e["distance"]
        return memo[i]
    return {i: off(i) for i in P}


def render(items, eye, target, up, fov, size, path, title):
    from PIL import Image, ImageDraw
    S = 2
    W, Hh = size[0] * S, size[1] * S
    eye, target, up = (np.array(a, float) for a in (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    focal = 0.5 * Hh / math.tan(math.radians(fov) / 2)
    img = np.zeros((Hh, W, 3), np.float32) + np.array([0.04, 0.045, 0.055])
    zb = np.zeros((Hh, W), np.float32)
    light = -f * 0.6 + u * 0.5 + r * 0.4
    light /= np.linalg.norm(light)
    for body, color, off in items:
        v = body.v + off
        rel = v - eye
        cam = np.c_[rel @ r, rel @ u, rel @ f]
        sx = W / 2 + focal * cam[:, 0] / cam[:, 2]
        sy = Hh / 2 - focal * cam[:, 1] / cam[:, 2]
        iz = 1.0 / cam[:, 2]
        tri = v[body.f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nl = np.linalg.norm(n, axis=1)
        nl[nl == 0] = 1
        n /= nl[:, None]
        facing = (n @ f) < 0
        shade = 0.30 + 0.70 * np.clip(n @ light, 0, 1)
        for t in np.nonzero(facing)[0]:
            ia, ib, ic = body.f[t]
            x0, x1, x2 = sx[ia], sx[ib], sx[ic]
            y0, y1, y2 = sy[ia], sy[ib], sy[ic]
            xmin, xmax = int(max(math.floor(min(x0, x1, x2)), 0)), int(min(math.ceil(max(x0, x1, x2)), W - 1))
            ymin, ymax = int(max(math.floor(min(y0, y1, y2)), 0)), int(min(math.ceil(max(y0, y1, y2)), Hh - 1))
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
            z = l0 * iz[ia] + l1 * iz[ib] + l2 * iz[ic]
            sub = zb[ymin:ymax + 1, xmin:xmax + 1]
            win = m & (z > sub)
            sub[win] = z[win]
            img[ymin:ymax + 1, xmin:xmax + 1][win] = np.array(color) * shade[t]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    ImageDraw.Draw(im).text((12, 10), title, fill=(230, 230, 230))
    im.save(path)


def make_images(asm, R):
    DIST.mkdir(parents=True, exist_ok=True)
    off = offsets(asm)
    P = {p["id"]: p for p in asm["parts"]}
    L, H, T = M("card_envelope_length"), M("card_envelope_height"), M("card_thickness")
    c = np.array([L / 2, H / 2, T / 2])
    size = (1400, 800)

    def items(exploded, skip=()):
        out = []
        for pid in P:
            if pid in skip:
                continue
            col = COLORS[group_of(pid)]
            for b in all_bodies(R, pid):
                out.append((b, col, off[pid] if exploded else np.zeros(3)))
        return out
    render(items(False), c + np.array([-120, -260, -560]), c, [0, 1, 0], 30, size, DIST / "01-frente-face-a.png",
           "Blockout: face A (ventiladores)")
    render(items(False), c + np.array([120, -260, 560]), c, [0, 1, 0], 30, size, DIST / "02-verso-face-b.png",
           "Blockout: face B (X central)")
    ce = c + np.array([-50, 0, 90])
    render(items(True), ce + np.array([-520, -560, 620]), ce, [0, 1, 0], 32, (1600, 1000), DIST / "03-explodida-por-estagio.png",
           "Blockout: explosao E1 a E8 (deslocamentos do assembly, relativos a peca-mae)")
    print("\n[5] Imagens em %s" % DIST.relative_to(HARNESS.parent))
    for f in sorted(DIST.glob("*.png")):
        print("    %s" % f.name)


# ---------------------------------------------------------------------------
def main():
    asm = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    R = build_parts(asm)
    # corpos fechados e com volume positivo
    bad = []
    for pid in R:
        for b in all_bodies(R, pid):
            m = b.mesh()
            if not (m.is_watertight and m.is_winding_consistent and m.volume > 0):
                bad.append(pid)
    gltf, binary, idx = build_scene(asm, R)
    global NODE_IDX
    NODE_IDX = idx
    BUILD.mkdir(parents=True, exist_ok=True)
    out = BUILD / "card.glb"
    write_glb(out, gltf, binary)
    n_meshes = len(gltf["meshes"])
    print("GLB: %s, %.1f kB, %d nós (%d peças + instâncias + âncoras), %d malhas" %
          (out.relative_to(HARNESS.parent), out.stat().st_size / 1024, len(gltf["nodes"]), len(asm["parts"]), n_meshes))
    print("Corpos não fechados ou sem volume: %s" % (sorted(set(bad)) or "nenhum"))
    # releitura
    sc = trimesh.load(out)
    print("Releitura com trimesh: %d geometrias, extensão (m) %s" % (len(sc.geometry), np.round(sc.extents, 4).tolist()))
    rep, ok = checks(asm, R)
    rep["glb"] = {"bytes": out.stat().st_size, "nodes": len(gltf["nodes"]), "meshes": n_meshes}
    rep["bloqueio_sem_base_no_csv"] = {k: [n for n in v if n != "position_unknown"] for k, v in sorted(NOTES.items())}
    rep["observacoes"] = OBS
    rep["corpos_nao_fechados"] = sorted(set(bad))
    (BUILD / "blockout-report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nPeças com valor de bloqueio sem base no CSV: %d" % len(NOTES))
    for o in OBS:
        print("Observação: " + o)
    if "--sem-imagens" not in sys.argv:
        make_images(asm, R)
    print("\nResultado das conferências automáticas (1 e 2): %s" % ("OK" if ok else "FALHA"))
    return 0 if ok and not bad else 1


NODE_IDX = {}

if __name__ == "__main__":
    sys.exit(main())
