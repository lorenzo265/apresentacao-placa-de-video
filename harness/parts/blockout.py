#!/usr/bin/env python3
"""Blockout da RTX PRO 6000 Blackwell Workstation Edition (F3, primeiro passo).

Lê design/assembly.json e design/measurements.csv e gera build/blockout.glb:
uma caixa (ou cilindro) por peça, só para aprovar câmera, ordem de explosão e textos.
Não é o modelo final. O GLB que o tour usa (build/card.glb) sai de parts/integrate.py,
que parte destes corpos e troca os das peças que já têm versão detalhada.

Contrato: CAD em mm, Z para cima, origem em card.envelope_min: x a partir do plano do
bracket, y a partir da ponta dos contatos PCIe, z da face B (z = 0) para a face A dos
ventiladores (z = card_thickness), sistema destro. Visto de +z, a placa aparece como em
pny/front (bracket à esquerda, contatos embaixo). As caixas respeitam a carcaça detalhada:
os volumes internos dela vêm de frame.keepouts(). O GLB sai em metros, com Y para cima:
(x, y, z) do CAD vira (x, z, -y) / 1000. Um nó por peça, com o nome igual ao id e a
hierarquia de `parent`. A geometria já está na posição montada (coordenadas de mundo); os
nós têm transformação identidade, então mover um nó (explosão) move também os filhos.
Âncoras viram nós vazios filhos, com o id da âncora.

Uso:  python3 -I harness/parts/blockout.py [--sem-imagens]
Saídas: harness/build/blockout.glb, harness/build/blockout-report.json,
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
    "screw_d_big": 5.0,         # cabeça com arruela (o E5 e o E6 usam fastener_e5/e6_head_diameter do CSV)
    "bracket_clear": 0.2,       # folga das aberturas de DisplayPort no bracket
    "blade_w": 12.0,            # largura tangencial da pá
    "fan_back_t": 1.5,          # espessura do disco traseiro do rotor
    "flex_t": 0.3,              # espessura dos cabos flat
    "spring_ring_w": 8.0,       # largura do anel e dos braços da mola
    "back_ring_d": 6.0,         # diâmetro dos anéis da pcb.back_frame
    "smd_h": 0.8,               # altura do bloco de componentes do verso
    "substrate_t": 1.0,         # substrato do package
    "stiff_t": 1.0,             # altura da moldura do package
    "base_plate_t": 1.0,        # placa de contato da base
    "base_frame_t": 4.0,        # altura da moldura da base (igual à câmara de vapor)
    "inductor_h": 3.0,          # altura dos indutores
    "stage_side": 5.0,          # lado dos estágios de potência (meio estágio de 2,5 em iface_vrm_gpu_anchor_y)
    "stage_gap": 0.2,           # folga entre o indutor e o estágio (iface_vrm_gpu_anchor_y)
    "aux_conn_h": 6.0,          # altura do conector auxiliar
    "aux_conn_depth": 4.0,
    "p16_depth_chamfer": 11.0,  # profundidade usada para pôr a linha do chanfro do PCB (não muda o PCB)
    "clear": 0.3,               # folga entre as caixas do blockout e a carcaça detalhada
    "adapter_conn_w": 5.63,     # largura em y do plugue J3 (a mesma do io_parts.py)
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
        self.vn = None          # normais por vértice (só as peças detalhadas levam)
        self._ax = None

    def shifted(self, d):
        b = Body.__new__(Body)
        b.v = self.v + np.asarray(d, float)
        b.f = self.f
        b.convex = self.convex
        b.vn = self.vn
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

    # Referencial: face B em z = 0, face A (ventiladores) em z = T. As camadas layer_* são
    # espessuras empilhadas a partir de cada face: grade e aro da face B de 0 a gT; tampas,
    # pcb.plate e pads a partir de z = 0 até o verso do PCB (pz_b); ventilador e aro a partir
    # de z = T para baixo.
    L, T = M("card_envelope_length"), M("card_thickness")
    wall = M("shroud_wall")
    y0 = M("iface_shroud_y_min")
    y1 = y0 + M("shroud_height_proposed")
    cy = M("iface_shroud_center_y")
    gT = M("layer_end_face_b_grid")
    zb = gT                                      # base das paredes (a grade e o aro ficam abaixo)
    tA = M("shroud_face_a_plate_thickness")
    hx = G["screw_head_h"]
    clr = G["clear"]
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
    pz_b, pz_f = M("iface_pcb_back_z"), M("iface_pcb_front_z")      # pz_b < pz_f: o verso olha para a face B
    zc = M("iface_die_contact_z")
    # volumes internos da carcaça detalhada (frame.py), que as caixas vizinhas respeitam
    KO = carcass_keepouts()
    floor_y = KO["canal"][2]                     # fundo do canal da borda superior, por fora
    notch_top = KO["entalhe"][3]                 # topo da parede em U em volta do entalhe PCIe
    end_in = KO["placa_de_extremidade"][1]       # face interna da placa de extremidade

    R["card"] = {"bodies": []}

    # --- carcaça (substituída pela peça detalhada na integração) ----------------
    ox = M("iface_shroud_power_opening_x")
    ow = KO["encaixe_do_conector"][1] - KO["encaixe_do_conector"][0] - 2 * wall     # largura em x da abertura do frame.py
    oz0, oz1 = M("iface_shroud_power_opening_z_min"), M("iface_shroud_power_opening_z_max")
    sh = [*carve(box(0, L, y0, y0 + wall, zb, T), (KO["fenda_do_adaptador"],), 0.0),     # fenda da faixa do adaptador
          box(0, ox - ow / 2, y1 - wall, y1, zb, T), box(ox + ow / 2, L, y1 - wall, y1, zb, T),
          box(ox - ow / 2, ox + ow / 2, y1 - wall, y1, oz1, T), box(ox - ow / 2, ox + ow / 2, y1 - wall, y1, zb, oz0),
          box(hx, hx + wall, y0 + wall, y1 - wall, zb, T),
          box(L - wall, L, y0 + wall, y1 - wall, zb, T)]
    guess("frame.shroud", "abertura retangular da borda superior para o conector de energia: x = iface_shroud_power_opening_x, largura em x de %.1f (a do frame.py, palpite), z de %.2f a %.2f (iface_shroud_power_opening_z_min e _max)" % (ow, oz0, oz1))
    guess("frame.shroud", "recuo da parede de extremidade (altura das cabeças dos parafusos): %.1f mm" % hx)
    guess("frame.shroud", "placas da face A só nas pontas, com o recorte do aro de %.0f mm; o centro é a pilha cooler.fins.3" % (ring_r * 2))
    for fx, xa, xb in ((fan_x[0], hx + wall, cen_x0), (fan_x[1], cen_x1, L - wall)):
        plate = b3box(xa, xb, y0 + wall, y1 - wall, T - wall, T) - b3cyl_z(fx, fan_y, T - wall - 1, T + 1, ring_r)
        sh.append(from_b3d(plate))
    R["frame.shroud"] = {"bodies": sh}

    R["frame.face_b"] = {"bodies": [
        box(hx + wall, fin1_len, y0 + wall, y1 - wall, 0, gT),
        box(L - fin2_len, L - wall, y0 + wall, y1 - wall, 0, gT)]}

    # parafusos da placa de extremidade
    dp_a = A["io.board.dp"]
    yp = sorted(a[1] for a in dp_a)
    mid = [(yp[i] + yp[i + 1]) / 2 for i in range(len(yp) - 1)]
    ys5 = [max(yp[0] - M("dp_port_pitch"), y0 + 15), *mid, min(yp[-1] + M("dp_port_pitch"), y1 - 15)]   # fora da parede curva dos cantos
    zc_dp = float(np.mean([a[2] for a in dp_a]))      # fileira de DisplayPort (dp_row_center_z)
    inst = []
    for yy in (y0 + 15, y1 - 15):          # fora da parede curva dos cantos da carcaça
        for zz in (gT + G["screw_d_big"] / 2 + clr, T - tA - G["screw_d_big"] / 2 - clr):   # entre a face B e a chapa da face A
            inst.append([cyl_x(0, hx, yy, zz, G["screw_d_big"] / 2)])
    for yy in ys5:
        for zz in (zc_dp - 8, zc_dp + 8):          # acima e abaixo dos receptáculos
            inst.append([cyl_x(0, hx, yy, zz, G["screw_d"] / 2)])
    R["fasteners.end_plate"] = {"instances": inst}
    guess("fasteners.end_plate", "posições dos 14 parafusos (4 nos cantos com arruela, 10 em volta dos DisplayPort) e tamanho: sem medida")

    # placa das saídas de vídeo e portas
    depth = M("dp_receptacle_depth")
    io_x1 = depth + M("pcb_thickness")
    # em z, entre a grade da face B e o duto do ventilador 1 (que desce até T - layer_end_fan_ring)
    io_z1 = min(T / 2 + M("io_board_outline_short") / 2, T - M("layer_end_fan_ring") - clr)
    io_z0 = max(io_z1 - M("io_board_outline_short"), gT + clr)
    R["io.board"] = {"bodies": [box(depth, io_x1,
                                    cy - M("io_board_outline_long") / 2, cy + M("io_board_outline_long") / 2,
                                    io_z0, io_z1)]}
    guess("io.board", "orientação (placa normal a x, contorno longo em y, curto em z): pendência do planejador; em z, de %.1f a %.1f, entre a grade da face B e o duto do ventilador 1 (o contorno curto de %.0f mm fica com %.1f)"
          % (io_z0, io_z1, M("io_board_outline_short"), io_z1 - io_z0))
    R["io.board.dp"] = {"instances": [[box(0, depth, a[1] - M("dp_receptacle_width") / 2, a[1] + M("dp_receptacle_width") / 2,
                                           a[2] - M("dp_receptacle_height") / 2, a[2] + M("dp_receptacle_height") / 2)]
                                      for a in dp_a]}
    guess("io.board.dp", "largura do receptáculo ao longo de y e altura ao longo de z (orientação)")

    # bracket
    bt = M("bracket_thickness")
    bh = M("bracket_height_overall")
    br_y1 = M("card_envelope_height") - M("bracket_top_below_shroud_top")
    br_y0 = br_y1 - bh
    br = b3box(-bt, 0, br_y0, br_y1, 0, T)
    cl = G["bracket_clear"]
    for a in dp_a:
        br = br - b3box(-bt - 1, 1, a[1] - M("dp_receptacle_width") / 2 - cl, a[1] + M("dp_receptacle_width") / 2 + cl,
                        a[2] - M("dp_receptacle_height") / 2 - cl, a[2] + M("dp_receptacle_height") / 2 + cl)
    R["io.bracket"] = {"bodies": [from_b3d(br)]}
    guess("io.bracket", "folga de %.1f mm nas aberturas dos DisplayPort; largura em z igual à espessura da placa (não é o bracket de norma); y de %.2f a %.2f (bracket_top_below_shroud_top)" % (cl, br_y0, br_y1))
    R["fasteners.e1_bracket"] = {"instances": [
        [cyl_x(-bt - hx, -bt, yy, zz, G["screw_d"] / 2)]
        for yy in (br_y0 + 33, br_y1 - 8) for zz in (7.5, 33.5)]}
    guess("fasteners.e1_bracket", "posição, tamanho e altura das cabeças")

    # aro e tampas (face B, de z = 0 para dentro)
    R["frame.rim"] = {"bodies": frame_boxes(0, L, y0, y1, 0, gT, wall, L - wall, y0 + wall, y1 - wall)}
    guess("frame.rim", "largura do aro igual à parede da carcaça")
    ry, rz, rhd, rhh, rsd, rsl = rim_screw()
    R["fasteners.e2_rim"] = {"instances": [[cyl_x(0, rhh, ry, rz, rhd / 2), cyl_x(rhh, rhh + rsl, ry, rz, rsd / 2)]]}
    guess("fasteners.e2_rim", "posição e tamanho sem foto (frame.py, rim_screw): eixo em x na ponta do bracket, cabeça de x = 0 a %.1f dentro do recuo da placa de extremidade, corpo até a face interna do aro, que tem o furo" % rhh)
    ct = M("layer_center_covers")
    xa, xb = fin1_len, L - fin2_len
    ylo, yhi = y0 + wall, y1 - wall
    R["frame.center_covers"] = {"instances": [
        [prism([(xa, ylo), (xb, ylo), (dcx, dcy)], 0, ct)],
        [prism([(xa, yhi), (xb, yhi), (dcx, dcy)], 0, ct)]]}
    guess("frame.center_covers", "contorno das duas tampas triangulares (aqui: inferior e superior, com vértice no centro do die)")

    # adaptador PCIe (entre a face B e o verso do PCB)
    az0 = M("iface_adapter_board_z_min")
    az1 = M("iface_adapter_board_z_max")
    ad_x0, ad_x1 = M("iface_adapter_x_min"), M("iface_adapter_x_max")
    cx_c, cn_y = M("iface_j3_center_x"), M("iface_j3_center_y")
    cn_len = M("pcie_adapter_connector_length")
    tab_x0, tab_x1 = adapter_tab_range()
    ad_boxes = [(ad_x0, ad_x1, 0, M("pcie_adapter_strip_height")), (tab_x0, tab_x1, 0, M("pcie_adapter_total_height"))]
    j3 = (cx_c - cn_len / 2, cx_c + cn_len / 2, cn_y - G["adapter_conn_w"] / 2, cn_y + G["adapter_conn_w"] / 2)
    R["pcie.adapter"] = {"bodies": [box(a, b, c, d, az0, az1) for a, b, c, d in ad_boxes] + [box(*j3, az1, M("iface_j3_mating_z"))]}
    guess("pcie.adapter", "faixa de iface_adapter_x_min a _max e aba de x = %.2f a %.2f (contorno do io_parts.py) com a altura do lóbulo, em caixas; plugue J3 de %.2f mm em y até iface_j3_mating_z" % (tab_x0, tab_x1, G["adapter_conn_w"]))
    e4h, e4r = M("fastener_e4_head_height"), M("fastener_e4_head_diameter") / 2
    R["fasteners.e4_pcie"] = {"instances": [[cyl_z(hx_, hy_, az0 - e4h, az0, e4r)] for hx_, hy_, _d, kind in adapter_holes() if kind != "lobulo"]}
    guess("fasteners.e4_pcie", "6 cabeças nos furos iface_adapter_*_hole_* (4 com anel e 2 da faixa; o furo do lóbulo fica sem parafuso), diâmetro e altura fastener_e4_head_*: sem medida")

    # placa central e parafusos
    ph = M("iface_plate_holes_dx") / 2
    pv = M("iface_plate_holes_dy") / 2
    pw = M("pcb_plate_window") / 2
    pz0, pz1 = M("layer_center_covers"), M("layer_center_covers") + M("layer_pcb_plate")
    pac = M("pcb_plate_adapter_clear")
    # recortes: aba, faixa e J3 do adaptador (que fica no plano da placa) e alívios sob as cabeças do E6
    e6r = M("fastener_e6_head_diameter") / 2 + M("cover_relief_clear")
    sx6, sy6 = M("iface_spring_holes_dx") / 2, M("iface_spring_holes_dy") / 2
    plate_ko = [(a - pac, b + pac, c - pac, d + pac, pz0 - 1, pz1 + 1) for a, b, c, d in ad_boxes + [j3]]
    plate_ko += [(dcx + sx * sx6 - e6r, dcx + sx * sx6 + e6r, dcy + sy * sy6 - e6r, dcy + sy * sy6 + e6r, pz0 - 1, pz1 + 1)
                 for sx in (-1, 1) for sy in (-1, 1)]
    R["pcb.plate"] = {"bodies": [b for bb in frame_boxes(pcx - M("pcb_plate_outline_x") / 2, pcx + M("pcb_plate_outline_x") / 2,
                                                         pcy - M("pcb_plate_outline_y") / 2, pcy + M("pcb_plate_outline_y") / 2,
                                                         pz0, pz1, dcx - pw, dcx + pw, dcy - pw, dcy + pw)
                                 for b in carve(bb, plate_ko, 0.0)]}
    guess("pcb.plate", "janela do furo centrada no die; sem as 4 abas nem os pads; contorno de 104 x 108 (escala antiga) é menor que o padrão de furos de 106 x 102; recortes em caixa em volta do adaptador e do J3 (folga pcb_plate_adapter_clear) e alívios quadrados sob as cabeças do E6 (no modelo final, furos redondos)")
    e5h, e5r = M("fastener_e5_head_height"), M("fastener_e5_head_diameter") / 2
    R["fasteners.e5_plate"] = {"instances": [[cyl_z(pcx + sx * ph, pcy + sy * pv, pz0 - e5h, pz0, e5r)]
                                             for sx in (-1, 1) for sy in (-1, 1)]}
    guess("fasteners.e5_plate", "diâmetro e altura da cabeça (fastener_e5_head_*, sem medida)")

    # cabos flat (sobre o verso do PCB, do lado da face B)
    ft = G["flex_t"]
    fw = M("flex_dp_width")
    R["flex.dp"] = {"bodies": [box(io_x1, pcb_x0, pcb_y0, pcb_y0 + fw, pz_b - ft, pz_b)]}
    guess("flex.dp", "espessura; trecho reto do conector até a placa das portas (%.0f mm), menor que flex_dp_length (%.0f mm), que inclui as curvas"
          % (pcb_x0 - io_x1, M("flex_dp_length")))
    ffw = M("flex_fan_width")
    R["flex.fan.1"] = {"bodies": [box(fan_x[0], pcb_x0, 40, 40 + ffw, pz_b - ft, pz_b)]}
    R["flex.fan.2"] = {"bodies": [box(pcb_x1, fan_x[1], 40, 40 + ffw, pz_b - ft, pz_b)]}
    for k in ("flex.fan.1", "flex.fan.2"):
        guess(k, "posição, trajeto e espessura (posição não medida)")

    # mola (sobre o verso do PCB)
    sx_, sy_ = M("iface_spring_holes_dx") / 2, M("iface_spring_holes_dy") / 2
    st = M("leaf_spring_thickness")
    rw = G["spring_ring_w"]
    # anel limitado por leaf_spring_ring_max_* (entre as fileiras de memória do verso); a janela encolhe junto
    ro_x = min(M("leaf_spring_window_x") / 2 + rw, M("leaf_spring_ring_max_x") / 2)
    ro_y = min(M("leaf_spring_window_y") / 2 + rw, M("leaf_spring_ring_max_y") / 2)
    ww, wh = ro_x - rw, ro_y - rw
    zs0, zs1 = M("iface_spring_z_min"), M("iface_spring_z_max")
    assert abs(zs1 - zs0 - st) < 1e-6
    sp = frame_boxes(dcx - ro_x, dcx + ro_x, dcy - ro_y, dcy + ro_y, zs0, zs1, dcx - ww, dcx + ww, dcy - wh, dcy + wh)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c, r = (dcx + sx * sx_, dcy + sy * sy_), (dcx + sx * ro_x, dcy + sy * ro_y)
            dv = np.array(r) - np.array(c)
            nv = np.array([-dv[1], dv[0]]) / np.linalg.norm(dv) * rw / 2
            sp.append(prism([np.array(c) - nv, np.array(c) + nv, np.array(r) + nv, np.array(r) - nv], zs0, zs1))
    R["cooler.leaf_spring"] = {"bodies": sp}
    guess("cooler.leaf_spring", "largura do anel e dos 4 braços (%.0f mm) e formato em X; anel de %.1f x %.1f (limite leaf_spring_ring_max_*), de z = %.1f a %.1f (iface_spring_z_*)" % (rw, 2 * ro_x, 2 * ro_y, zs0, zs1))
    R["fasteners.e6_spring"] = {"instances": [[cyl_z(dcx + sx * sx_, dcy + sy * sy_, zs0 - M("fastener_e6_head_height"), zs0, M("fastener_e6_head_diameter") / 2)]
                                              for sx in (-1, 1) for sy in (-1, 1)]}
    guess("fasteners.e6_spring", "diâmetro e altura da cabeça (fastener_e6_head_*, sem medida): sob a mola, nos alívios da pcb.plate")

    # PCB e o que está nele
    ca = math.radians(M("pcb_main_chamfer_angle_deg"))
    cxp0, cyp0 = M("power_connector_center_from_bracket_end"), M("power_connector_center_y")
    off = G["p16_depth_chamfer"] / 2      # a linha do chanfro fica a meia profundidade do corpo, para fora
    px0, py0 = cxp0 + off * math.sin(ca), cyp0 + off * math.cos(ca)
    t_top = (py0 - pcb_y1) / math.sin(ca)
    x_top = px0 + t_top * math.cos(ca)
    t_r = (pcb_x1 - px0) / math.cos(ca)
    y_r = py0 - t_r * math.sin(ca)
    rd = M("pcb_main_contact_edge_recess_depth")
    r0, r1 = pcb_x0 + M("pcb_main_contact_edge_recess_u_start"), pcb_x0 + M("pcb_main_contact_edge_recess_u_end")
    R["pcb.main"] = {"bodies": [
        prism([(pcb_x0, pcb_y0 + rd), (pcb_x1, pcb_y0 + rd), (pcb_x1, y_r), (x_top, pcb_y1), (pcb_x0, pcb_y1)], pz_b, pz_f),
        box(pcb_x0, r0, pcb_y0, pcb_y0 + rd, pz_b, pz_f), box(r1, pcb_x1, pcb_y0, pcb_y0 + rd, pz_b, pz_f)]}
    guess("pcb.main", "tamanho do chanfro (catetos de %.1f mm em x e %.1f mm em y): sem medida, a linha passa a meia profundidade do corpo do conector (%.0f mm, valor de bloqueio); sem o recorte em V" %
          (pcb_x1 - x_top, pcb_y1 - y_r, G["p16_depth_chamfer"]))
    R["pcb.back_frame"] = {"instances": [[cyl_z(dcx + sx * sx_, dcy + sy * sy_, pz_b - M("pcb_back_frame_thickness"), pz_b, G["back_ring_d"] / 2)]
                                         for sx in (-1, 1) for sy in (-1, 1)]}
    guess("pcb.back_frame", "contorno e espessura sem dados: só 4 anéis nos furos da mola")
    sw = M("pcb_plate_window") / 2 - 2
    R["pcb.smd"] = {"bodies": [box(dcx - sw, dcx + sw, dcy - sw, dcy + sw, pz_b - G["smd_h"], pz_b)]}
    guess("pcb.smd", "bloco único atrás do chip, sem quantidade nem medidas")

    # package: substrato, moldura e die (z cresce para a face A; a frente do PCB é pz_f)
    px, py = M("gb202_package_x") / 2, M("gb202_package_y") / 2   # lado longo em x
    wx, wy = M("gb202_window_x") / 2, M("gb202_window_y") / 2
    dx, dy = M("gb202_die_x") / 2, M("gb202_die_y") / 2
    die_top = pz_f + M("gb202_die_top_above_pcb")
    sub1 = pz_f + G["substrate_t"]
    R["gpu.package"] = {"bodies": [
        box(dcx - px, dcx + px, dcy - py, dcy + py, pz_f, sub1),
        *frame_boxes(dcx - px, dcx + px, dcy - py, dcy + py, sub1, sub1 + G["stiff_t"], dcx - wx, dcx + wx, dcy - wy, dcy + wy),
        box(dcx - dx, dcx + dx, dcy - dy, dcy + dy, sub1, die_top)]}
    guess("gpu.package", "espessura do substrato (%.1f) e da moldura (%.1f); a altura do die sai de gb202_die_top_above_pcb" % (G["substrate_t"], G["stiff_t"]))
    R["gpu.tim"] = {"bodies": [box(dcx - dx, dcx + dx, dcy - dy, dcy + dy, die_top, zc)]}

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
        grid.append((pcb_x0 + u, pcb_y0 + M("mem_contact_edge_v"), gw, gl))      # na borda dos contatos o chip gira
    for a_id, zlo, zhi in (("mem.back", pz_b - gt, pz_b), ("mem.front", pz_f, pz_f + gt)):
        for k, a in enumerate(A[a_id]):
            if abs(a[0] - grid[k][0]) > 0.01 or abs(a[1] - grid[k][1]) > 0.01:
                OBS.append("%s.%d: âncora (%.2f, %.2f) difere da grade mem_* do CSV (%.2f, %.2f)" % (a_id, k + 1, a[0], a[1], grid[k][0], grid[k][1]))
        R[a_id] = {"instances": [[box(gx - w / 2, gx + w / 2, gy - h / 2, gy + h / 2, zlo, zhi)] for gx, gy, w, h in grid]}

    # energia (na frente do PCB, do lado da face A)
    ang = M("power_connector_rotation_deg")
    cxp = M("power_connector_center_from_bracket_end")
    cyp = M("power_connector_center_y")
    cw = M("conn16_header_width")
    # de pé: lado longo do cabeçote em z; power_connector_rotation_deg é o eixo através das fileiras
    # (largura power_connector_body_across) e a profundidade fica na direção de encaixe
    p16_w, p16_d, p16_h = M("power_connector_body_across"), M("power_connector_body_depth"), M("power_connector_body_height_z")
    conn = _rot_centered(cxp, cyp, pz_f, pz_f + p16_h, p16_w, p16_d, ang)
    if conn.hi[1] > floor_y - clr:
        OBS.append("power.connector: o corpo sobe até y = %.2f, acima do fundo do canal da carcaça menos a folga (%.2f)" % (conn.hi[1], floor_y - clr))
    R["power.connector"] = {"bodies": [conn]}
    guess("power.connector", "caixa do corpo de pé (%.2f através x %.2f na direção de encaixe x %.2f de altura), sem lâminas nem trava" % (p16_w, p16_d, p16_h))
    au = M("aux_header_u")
    al = M("aux_header_length")
    ah_top = min(pcb_y1, floor_y - clr)
    R["io.aux_header"] = {"bodies": [box(pcb_x0 + au - al / 2, pcb_x0 + au + al / 2, ah_top - G["aux_conn_depth"], ah_top,
                                         pz_f, pz_f + G["aux_conn_h"])]}
    guess("io.aux_header", "profundidade e altura do corpo; o corpo fica abaixo do fundo do canal da carcaça (y até %.2f), %.2f mm para dentro da borda do PCB" % (ah_top, pcb_y1 - ah_top))

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
    R["power.inductors"] = {"instances": [[box(x - s / 2, x + s / 2, y - s / 2, y + s / 2, pz_f, pz_f + G["inductor_h"])] for x, y in pos]}
    guess("power.inductors", "altura (%.0f mm), repartição 13 + 11 e passo (8 mm na borda dos contatos): representativos" % G["inductor_h"])
    ss = G["stage_side"] / 2
    so = s / 2 + G["stage_gap"] + ss          # do centro do indutor ao centro do estágio, para dentro da placa
    st_pos = ([(x, y + so) for x, y in pos[:n_c]] + [(x, y - so) for x, y in pos[n_c:n_c + n_t]]
              + [(x - so, y) for x, y in pos[n_c + n_t:]])
    R["power.vrm.gpu"] = {"instances": [[box(x - ss, x + ss, y - ss, y + ss, pz_f, M("iface_vrm_gpu_anchor_z"))] for x, y in st_pos]}
    guess("power.vrm.gpu", "na frente do PCB, um estágio para dentro de cada indutor (como iface_vrm_gpu_anchor_*), lado %.1f e topo em iface_vrm_gpu_anchor_z: sem fonte" % G["stage_side"])
    xb = far_x + 1.2     # coluna livre perto da ponta longe do bracket, abaixo dos indutores
    R["power.vrm.mem"] = {"instances": [[box(xb - 2.5, xb + 2.5, y - 2.5, y + 2.5, pz_f, pz_f + 1.5)] for y in (26.5, 32.0, 37.5, 43.0)]}
    R["power.aux"] = {"instances": [[box(x - 2, x + 2, 23 - 2, 23 + 2, pz_f, pz_f + 1.5)] for x in (197.5, 202.5, 207.5)]}
    R["power.controller"] = {"instances": [[box(pcb_x0 + 6 - 3, pcb_x0 + 6 + 3, pcb_y0 + v - 3, pcb_y0 + v + 3, pz_f, pz_f + 1.0)] for v in (9, 17)]}
    for k in ("power.vrm.mem", "power.aux", "power.controller"):
        guess(k, "posição e dimensões inventadas só para o bloqueio (a proposta não as define)")
        NOTES[k].append("position_unknown")

    # --- cooler -------------------------------------------------------------
    fd = M("fan_axial_depth")
    rr = M("fan_rotor_diameter") / 2
    hr = M("fan_hub_diameter") / 2
    nb = parts["cooler.fan.1.blade"]["count"]["value"]
    zf0 = T - fd                                   # o ventilador ocupa de T - fd até a face A
    for n in (1, 2):
        fx = fan_x[n - 1]
        R["cooler.fan.%d" % n] = {"bodies": [cyl_z(fx, fan_y, zf0, T, hr), cyl_z(fx, fan_y, zf0, zf0 + G["fan_back_t"], rr)]}
        guess("cooler.fan.%d" % n, "espessura do disco traseiro do rotor (%.1f mm)" % G["fan_back_t"])
        R["cooler.fan.%d.blade" % n] = {"instances": [
            [rot_box_z(fx, fan_y, zf0 + G["fan_back_t"], T, rr - hr, G["blade_w"], 360.0 * i / nb, off=hr)] for i in range(nb)]}
        guess("cooler.fan.%d.blade" % n, "forma da pá: caixa radial de %.0f mm de largura (a forma real é pendência)" % G["blade_w"])

    # pilhas das pontas: entre a grade da face B e o duto do ventilador; respeitam a placa de
    # extremidade, a placa das portas, as paredes, os cantos arredondados e o fundo do canal
    fh = M("fin_stack_end_height_y")
    z_f1 = T - M("layer_end_fan_ring")
    z_f0 = z_f1 - M("fin_stack_end_depth_z")
    fy0, fy1 = max(cy - fh / 2, y0 + wall + clr), min(cy + fh / 2, y1 - wall - clr, floor_y - clr)
    f1_x0 = max(end_in, io_x1) + clr
    f2_x1 = L - wall - clr
    R["cooler.fins.1"] = {"bodies": [prism(rounded_box_pts(f1_x0, fin1_len, fy0, fy1, inner_corners=("x0",), clear=clr), z_f0, z_f1)]}
    R["cooler.fins.2"] = {"bodies": [prism(rounded_box_pts(L - fin2_len, f2_x1, fy0, fy1, inner_corners=("x1",), clear=clr), z_f0, z_f1)]}
    for k in ("cooler.fins.1", "cooler.fins.2"):
        guess(k, "pilha inteira em um prisma; as 60 aletas não são modeladas; contorno recortado pela carcaça (cantos de raio shroud_corner_radius - shroud_wall, paredes e folga de %.1f mm)" % clr)
    guess("cooler.fins.1", "começa em x = %.2f, depois da placa das portas (io.board), e não em 0" % f1_x0)

    bx, by = M("cooler_base_frame_outline_x") / 2, M("cooler_base_frame_outline_y") / 2
    vx, vy = M("vapor_chamber_contact_plate_x") / 2, M("vapor_chamber_contact_plate_y") / 2
    vt = M("vapor_chamber_thickness")
    # a moldura respeita a carcaça (entalhe e canal) e os componentes altos da frente do PCB
    tall = [tuple(np.ravel(np.c_[b.lo, b.hi])) for k in ("power.connector", "io.aux_header") for b in R[k]["bodies"]]
    base = [b for bb in frame_boxes(pcx - bx, pcx + bx, pcy - by, pcy + by, zc, zc + G["base_frame_t"], dcx - vx, dcx + vx, dcy - vy, dcy + vy)
            for b in carve(bb, (KO["entalhe"], KO["canal"], *tall), clr)]
    R["cooler.base"] = {"bodies": [*base, box(dcx - vx, dcx + vx, dcy - vy, dcy + vy, zc, zc + G["base_plate_t"])]}
    guess("cooler.base", "altura da moldura e espessura da placa de contato; a placa de contato sobrepõe a câmara de vapor (peça filha); a moldura é recortada em volta do entalhe PCIe, do canal da borda superior da carcaça, do conector de energia e do conector auxiliar")
    R["cooler.vapor_chamber"] = {"bodies": [box(dcx - vx, dcx + vx, dcy - vy, dcy + vy, zc, zc + vt)]}
    R["cooler.fins.3"] = {"bodies": [box(cen_x0, cen_x1, max(dcy - by, notch_top + clr), min(dcy + by, floor_y - clr),
                                         T - M("layer_center_fins_face_a"), T - tA - clr)]}
    guess("cooler.fins.3", "extensão em y (moldura da base, recortada pela parede do entalhe e pelo fundo do canal da carcaça): proposta não define; termina sob a chapa da face A")

    hd = M("heatpipe_diameter") / 2
    hl = M("heatpipe_length_per_side")
    nh = parts["cooler.heatpipes"]["count"]["value"]
    per = nh // 2
    zhp = M("iface_heatpipe_axis_z")     # eixo dos tubos (o mesmo do cooler.py)
    hp = []
    for side in (-1, 1):
        for i in range(per):
            yy = dcy + M("heatpipe_pitch_chamber") * (i - (per - 1) / 2)
            xa_, xb_ = dcx + side * vx, dcx + side * (vx + hl)
            hp.append([cyl_x(min(xa_, xb_), max(xa_, xb_), yy, zhp, hd)])
    R["cooler.heatpipes"] = {"instances": hp}
    guess("cooler.heatpipes", "traçado reto com o passo da câmara (heatpipe_pitch_chamber) e o eixo em iface_heatpipe_axis_z; o trajeto em S do cooler.py não entra no blockout; atravessam as pilhas de aletas de propósito")

    missing = [i for i in parts if i not in R]
    if missing:
        raise SystemExit("peças sem construtor: %s" % missing)
    return R


def _parts_path():
    if str(Path(__file__).resolve().parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).resolve().parent))


def carcass_keepouts():
    """Volumes internos da carcaça detalhada (frame.py), na mesma forma (caixas)."""
    _parts_path()
    import frame as FR
    return FR.keepouts()


def rim_screw():
    """Parafuso do aro, na posição em que o frame.py abre o furo."""
    _parts_path()
    import frame as FR
    return FR.rim_screw()


def adapter_holes():
    """Furos do adaptador (x, y, diâmetro, tipo), os mesmos do io_parts.py (linhas do CSV)."""
    _parts_path()
    import io_parts as IO
    return IO.adapter_holes()


def adapter_tab_range():
    """Faixa em x da aba do adaptador acima da faixa dos contatos, pelo contorno do io_parts.py."""
    _parts_path()
    import io_parts as IO
    pts = IO.adapter_outline_xy()
    hs = M("pcie_adapter_strip_height") + 0.5
    xs = [x for x, y in pts if y > hs]
    return min(xs), max(xs)


def carve(b, keepouts, clr):
    """Caixa b (Body de 8 vértices) menos as caixas de exclusão (expandidas da folga): devolve
    caixas que não se sobrepõem a nenhuma delas."""
    out = [(b.lo.copy(), b.hi.copy())]
    for k in keepouts:
        klo = np.array([k[0], k[2], k[4]]) - clr
        khi = np.array([k[1], k[3], k[5]]) + clr
        nxt = []
        for lo, hi in out:
            if np.any(hi <= klo) or np.any(lo >= khi):
                nxt.append((lo, hi))
                continue
            lo, hi = lo.copy(), hi.copy()
            for ax in range(3):
                if lo[ax] < klo[ax]:
                    a_hi = hi.copy()
                    a_hi[ax] = klo[ax]
                    nxt.append((lo.copy(), a_hi))
                    lo[ax] = klo[ax]
                if hi[ax] > khi[ax]:
                    a_lo = lo.copy()
                    a_lo[ax] = khi[ax]
                    nxt.append((a_lo, hi.copy()))
                    hi[ax] = khi[ax]
            # o que sobra (lo, hi) está dentro da exclusão e sai
        out = nxt
    return [box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]) for lo, hi in out if np.all(hi - lo > 1e-6)]


def rounded_box_pts(x0, x1, y0, y1, inner_corners=(), clear=0.0, n=8):
    """Contorno convexo de uma caixa no plano xy com os cantos do lado x0 ou x1 cortados pelo
    contorno interno arredondado da carcaça (raio shroud_corner_radius - shroud_wall, centro a
    shroud_corner_radius das bordas externas), menos a folga."""
    L = M("card_envelope_length")
    rc = M("shroud_corner_radius")
    ri = rc - M("shroud_wall") - clear
    sy0 = M("iface_shroud_y_min")
    sy1 = sy0 + M("shroud_height_proposed")
    pts = []
    for side in ("x0", "x1"):
        xe = x0 if side == "x0" else x1
        for ye, ccy in ((y0, sy0 + rc), (y1, sy1 - rc)):
            ccx = rc if side == "x0" else L - rc
            if side in inner_corners and math.hypot(xe - ccx, ye - ccy) > ri and (xe - ccx) * (1 if side == "x1" else -1) > 0 \
                    and (ye - ccy) * (1 if ye == y1 else -1) > 0:
                # arco do contorno interno entre as retas x = xe e y = ye
                sx = 1 if side == "x1" else -1
                sy = 1 if ye == y1 else -1
                a0 = math.atan2(0, sx)            # direção horizontal
                a1 = a0 + (math.pi / 2 if sx * sy > 0 else -math.pi / 2)   # até a vertical, pelo arco curto
                # pontos do arco que ficam dentro da caixa
                for t in np.linspace(0, 1, n + 1):
                    a = a0 + (a1 - a0) * t
                    px, py = ccx + ri * math.cos(a), ccy + ri * math.sin(a)
                    px = min(max(px, x0), x1)
                    py = min(max(py, y0), y1)
                    pts.append((px, py))
            else:
                pts.append((xe, ye))
    from scipy.spatial import ConvexHull
    p = np.unique(np.round(np.array(pts), 6), axis=0)
    return p[ConvexHull(p).vertices].tolist()


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


def build_scene(asm, R, detail=None, generator="harness/parts/blockout.py"):
    """detail: id -> extras da peça detalhada (integrate.py); essas peças saem com
    blockout = False e com as notas da peça no lugar das notas de bloqueio."""
    detail = detail or {}
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
        N = None
        if all(b.vn is not None for b in bodies):
            N = np.vstack([to_gltf(b.vn) * 1000.0 for b in bodies]).astype("<f4")
        out = []
        for data, target in ((V, 34962), (F, 34963)) + (((N, 34962),) if N is not None else ()):
            while len(buf) % 4:
                buf.append(0)
            views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": data.nbytes, "target": target})
            buf.extend(data.tobytes())
            out.append(len(views) - 1)
        accs.append({"bufferView": out[0], "componentType": 5126, "count": len(V), "type": "VEC3",
                     "min": V.min(axis=0).tolist(), "max": V.max(axis=0).tolist()})
        accs.append({"bufferView": out[1], "componentType": icode, "count": len(F), "type": "SCALAR"})
        attrs = {"POSITION": len(accs) - 2}
        idx_acc = len(accs) - 1
        if N is not None:
            accs.append({"bufferView": out[2], "componentType": 5126, "count": len(N), "type": "VEC3"})
            attrs["NORMAL"] = len(accs) - 1
        meshes.append({"name": name, "primitives": [{"attributes": attrs, "indices": idx_acc,
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
        if pid in detail:
            ex.update({"blockout": False, "blockout_guess": False, "blockout_notes": [], "detail": detail[pid]})
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
                      "shape_provenance": p["shape_provenance"], "group": g, "blockout": pid not in detail,
                      "blockout_guess": bool(notes) and pid not in detail, "instance_of": pid, "instance": k}
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
            ax = {"anchor": True, "part": p["id"]}
            if a.get("kind"):
                ax["kind"] = a["kind"]
            aid = new_node(a["id"], ax, trans=to_gltf([a["pos"]])[0])
            link(tgt, aid)
    roots = [idx[p["id"]] for p in parts if not p["parent"]]
    gltf = {
        "asset": {"version": "2.0", "generator": generator,
                  "extras": {"blockout": not detail, "detailed_parts": sorted(detail), "units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z",
                             "origin": "card.envelope_min", "map": "gltf = (x, z, -y) / 1000",
                             "referencial": "face B em z = 0, face A (ventiladores) em z = card_thickness; visto de +z, bracket à esquerda e contatos embaixo"}},
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
    render(items(False), c + np.array([-120, -260, 560]), c, [0, 1, 0], 30, size, DIST / "01-frente-face-a.png",
           "Blockout: face A (ventiladores)")
    render(items(False), c + np.array([120, -260, -560]), c, [0, 1, 0], 30, size, DIST / "02-verso-face-b.png",
           "Blockout: face B (X central)")
    ce = c + np.array([-50, 0, -90])
    render(items(True), ce + np.array([-520, -560, -620]), ce, [0, 1, 0], 32, (1600, 1000), DIST / "03-explodida-por-estagio.png",
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
    out = BUILD / "blockout.glb"
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
