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
bracket, y a partir da ponta dos contatos PCIe, z da face B, em z = 0, para a face A dos
ventiladores, em z = card_thickness; sistema destro). Visto de +z, a placa aparece como em
pny/front: bracket à esquerda, contatos embaixo. As camadas layer_* são espessuras: a face B
e o aro ocupam de z = 0 a layer_end_face_b_grid; a chapa da face A, de card_thickness menos
a espessura da chapa até card_thickness. (Referencial corrigido em 2026-11-10: antes a face A
ficava em z = 0, o que espelhava a placa; assembly-plan, seção 11.) O GLB sai em metros com
Y para cima, (x, y, z) -> (x, z, -y) / 1000, como no blockout. Um nó por id; as âncoras do
assembly viram nós vazios filhos. harness/parts/integrate.py troca as caixas do blockout por
estas peças em build/card.glb.

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
    "edge_fillet_a": (3.0, "inferred", "arredondamento da aresta entre a face A e as laterais; os renders mostram aresta macia, sem cota"),
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
    "lam_overlap": (0.15, "inferred", "sobreposição das lâminas em V (vista de frente): a dobra de cada lâmina avança (passo - espessura + sobreposição) em x, de modo que nenhuma linha reta no plano xz atravessa a grade; na foto (pny/front, pny/back, sr-4) as grades são opacas, com nervuras verticais uniformes; dobra e ângulo sem foto de perfil"),
    # extremidade do lado das portas
    "dp_clear": (0.3, "inferred", "folga das aberturas dos DisplayPort na placa de extremidade"),
    # face B, aro e tampas
    "rim_w": (2.2, "derived", "largura do aro visto de frente: faixa clara de 2,2 mm no contorno (pny/back)"),
    "rim_fillet": (1.0, "inferred", "arredondamento da aresta externa do aro"),
    "grille_inset_b": (6.2, "derived", "distância do contorno até as lâminas da grade da face B: 6,2 a 6,6 mm (pny/back)"),
    "cover_edge_off_b": (1.4, "derived", "a borda das tampas fica 1,4 mm (perpendicular) para dentro da linha do X que passa pelo cruzamento (pny/back, linhas a 15 e 30 mm do centro)"),
    "x_band_b": (4.8, "derived", "largura perpendicular da estrutura do X entre a tampa e a grade, com o fio claro da borda da tampa: 4,5 a 4,8 mm em pny/back (linhas 350, 365 e 380 do render de 800 px, 2,27 px/mm pela largura da carcaça; 14 a 15 px na horizontal vezes sen 46,5 graus); era 8,0 e os braços do X ficavam grossos (pedido do agente de materiais, 2026-11-11)"),
    "apex_r_b": (7.0, "derived", "raio do vértice das tampas: vão vertical de 9,7 mm entre os vértices (pny/back)"),
    "win_r_b": (3.4, "derived", "raio do vértice das grades junto ao cruzamento: ponta a 10,8 mm do cruzamento (pny/back)"),
    "lam_pitch_b": (1.45, "derived", "passo das lâminas da grade da face B: cerca de 1,45 mm (pny/back)"),
    "lam_t_b": (0.6, "inferred", "espessura das lâminas da face B"),
    "lam_recess_b": (0.5, "inferred", "recuo das lâminas da face B em relação à moldura"),
    "relief_floor_t": (0.1, "inferred", "espessura do fundo que fecha o rebaixo do E5 sob a grade da face B, encostado no fundo da cabeça do parafuso (N7)"),
    "adapter_clear": (0.5, "inferred", "folga do recorte da faixa do adaptador PCIe na face B, no aro e na fenda da parede inferior (o recorte aparece em gn-20, sem cota)"),
    "rim_screw_yz": ((22.86, 1.6), "inferred", "centro (y, z) do parafuso do aro (fasteners.e2_rim), com o eixo em x na ponta do bracket: y = iface_shroud_y_min + 9 (posição do blockout), z no meio do aro; sem foto (falta gn-16 em resolução maior, o quadro do vídeo da GN no passo 2 ou a ponta da placa sem o bracket)"),
    "rim_screw_head": ((2.4, 0.9), "inferred", "diâmetro e altura da cabeça do parafuso do aro; a cabeça fica de x = 0 até a altura, dentro do recuo da placa de extremidade (shroud_end_plate_recess), escondida pelo bracket"),
    "rim_screw_shank_d": (1.4, "inferred", "diâmetro do corpo do parafuso do aro, que vai até a face interna do aro (rim_w)"),
    "rim_screw_clear": (0.15, "inferred", "folga radial do furo do aro em volta da cabeça e do corpo do parafuso"),
    # borda inferior
    "notch_r": (0.3, "inferred", "raio dos cantos do entalhe ao lado dos contatos PCIe; era 1,5: o canto côncavo arredondado, com normais suaves, virava uma faixa vertical branca sob luz rasante (a 'haste' dos beats a2.7 e a3.3, em x 145,5 a 147, de z 3 a 40); sem cota na referência"),
    # canal da borda superior
    "ch_lip_a": (4.0, "inferred", "borda do lado da face A entre a aresta e o canal, medida da face A para dentro"),
    "ch_pcb_clear": (1.5, "inferred", "folga entre o fim do canal (lado da face B) e a face do PCB, para o fundo do canal não cruzar o PCB"),
    "ch_corner_r": (0.5, "inferred", "raio dos cantos do canal no plano xz; era 2,0: os cantos côncavos nas pontas do canal brilhavam como traços curtos sob luz rasante; sem cota na referência"),
    "slot_w": (2.0, "inferred", "largura das duas fendas do canal (proporção em perspectiva, pny/3qtr-top-right)"),
    "slot_z": ((7.5, 11.5), "inferred", "centros das fendas, medidos da face A para dentro (perspectiva, pny/3qtr-top-right)"),
    "slot_x_margin": (8.0, "inferred", "distância do começo do canal ao começo das fendas"),
    "slot_end_gap": (5.0, "inferred", "distância do fim das fendas à luva do túnel do conector, medida no fundo do canal"),
    "pad_len_x": (40.0, "inferred", "comprimento da placa lisa elevada do canal, do lado do bracket"),
    "pad_z": ((15.0, 28.0), "inferred", "faixa da placa lisa do canal, medida da face A para dentro (do lado da face B)"),
    "pad_h": (0.4, "inferred", "altura da placa lisa sobre o fundo do canal"),
    "pw_hood": (1.5, "inferred", "quanto a luva do túnel do conector de energia avança para trás da face de encaixe, em volta da boca do corpo (sem foto do interior)"),
    "pw_body_clear": (0.3, "inferred", "folga entre o corpo do conector e o furo do colar no fundo da luva (do lado da trava soma-se a altura da trava, p16_latch do io_parts.py)"),
    "pw_mouth": ("boca", "inferred",
                 "boca do túnel: um rebaixo retangular na ponta do canal, da profundidade do canal (shroud_channel_depth), que cobre o túnel do "
                 "topo até o fundo do canal; a abertura fica um retângulo limpo no plano do fundo do canal, como em pny/3qtr-top-right (antes "
                 "o contorno tinha um degrau onde o túnel a 45 graus cruzava a ponta do canal e o lábio de baixo dele: visual-qa-placa-final-2, N3)"),
    "pw_reach": (60.0, "inferred", "comprimento auxiliar do túnel ao longo da direção de encaixe, além da carcaça (só garante que o corte atravessa a parede; não é medida)"),
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
Z_FACE_B = M("layer_end_face_b_grid")           # base das paredes; a face B (grade e aro) fica de 0 até aqui
T_A = M("shroud_face_a_plate_thickness")         # chapa da face A, de T - T_A a T
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
        fillet(s.vertices().filter_by(is_bb), bracket_bottom_corner_r())
    return s.sketch


def bracket_bottom_corner_r():
    """Raio do canto entre a ponta do bracket e a borda dos contatos (CSV, promovido do frame.py)."""
    return M("shroud_corner_radius_bracket_bottom")


def adapter_outline():
    """Contorno do adaptador PCIe no plano xy, do io_parts.py (mesma fonte da peça)."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import io_parts as IO
    return poly(IO.adapter_outline_xy())


def adapter_outline_xy_pts():
    """Contorno do adaptador como lista de pontos (x, y) (io_parts.py)."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import io_parts as IO
    return [tuple(map(float, p)) for p in IO.adapter_outline_xy()]


def adapter_strip_cut():
    """Caixa do recorte da faixa do adaptador (face B, aro e parede inferior da carcaça):
    de iface_adapter_x_min a _max, da ponta dos contatos até a faixa, aberta até a face B e até
    a face do adaptador do lado do PCB (iface_adapter_board_z_max), com a folga adapter_clear."""
    c = g("adapter_clear")
    return (M("iface_adapter_x_min") - c, M("iface_adapter_x_max") + c, -1.0, M("pcie_adapter_strip_height") + c,
            -1.0, M("iface_adapter_board_z_max") + c)


def e5_heads():
    return [a["pos"][:2] for a in PARTS["fasteners.e5_plate"]["anchors"]]


def reliefs(z_top):
    """Rebaixos por baixo da face B e das tampas: sob as 4 cabeças do E5 (fundo em
    iface_cover_relief_e5_z_min) e sobre a aba do adaptador com a presilha e as cabeças do E4
    (fundo em iface_cover_relief_adapter_z_min), até z_top."""
    cl = M("cover_relief_clear")
    r5 = M("fastener_e5_head_diameter") / 2 + cl
    out = [ext(Pos(x, y) * Circle(r5), M("iface_cover_relief_e5_z_min"), z_top) for x, y in e5_heads()]
    out.append(ext(offset(adapter_outline(), cl, kind=Kind.ARC), M("iface_cover_relief_adapter_z_min"), z_top))
    return out


def rim_screw():
    """Parafuso do aro (fasteners.e2_rim): (y, z, diâmetro da cabeça, altura, diâmetro do corpo,
    comprimento do corpo), eixo em x a partir de x = 0."""
    (y, z), (hd, hh), sd = g("rim_screw_yz"), g("rim_screw_head"), g("rim_screw_shank_d")
    assert hh <= M("shroud_end_plate_recess"), "cabeça do parafuso do aro maior que o recuo"
    return y, z, hd, hh, sd, g("rim_w") - hh


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


def chevron_louvres(region, pitch, t, z0, z1, clip):
    """Lâminas verticais (ao longo de y) com perfil em V no plano xz, de z0 a z1, recortadas pela
    região (esboço xy). Espessura t em x; a dobra no meio da profundidade avança
    pitch - t + lam_overlap em x: o canal entre duas lâminas desvia mais do que a própria largura,
    e nenhuma linha reta no plano xz (de frente ou oblíqua) atravessa a grade. As lâminas passam
    pitch - t + lam_overlap + t além da borda da janela (por baixo da chapa, dentro de clip), para
    nenhum pedaço de lâmina ficar solto onde a dobra cruza a borda."""
    amp = pitch - t + g("lam_overlap")
    zm = (z0 + z1) / 2
    bb = region.bounding_box()
    xs = np.arange(pitch / 2 + 0.11, L, pitch)       # fase deslocada: nenhuma face de lâmina coincide com a borda da janela
    xs = xs[(xs > bb.min.X - pitch - amp) & (xs < bb.max.X + pitch)]
    prof = Sketch()
    for xc in xs:
        x0 = xc - t / 2
        prof = prof + Face(Wire.make_polygon([Vector(x0, z0, 0), Vector(x0 + t, z0, 0), Vector(x0 + t + amp, zm, 0),
                                              Vector(x0 + t, z1, 0), Vector(x0, z1, 0), Vector(x0 + amp, zm, 0)], close=True))
    y_lo, y_hi = bb.min.Y - 1, bb.max.Y + 1
    vanes = extrude(Plane.XZ.offset(-y_hi) * prof, y_hi - y_lo, dir=(0, -1, 0))
    reach = offset(region, amp + t, kind=Kind.ARC) & clip
    return vanes & ext(reach, z0, z1), amp


def drop_loose(shape, pid):
    """Tira pedaços soltos (lâmina em V cortada pela curva do contorno interno, por exemplo): fica
    só o sólido maior, e a nota registra o que saiu."""
    sols = sorted(shape.solids(), key=lambda so: -so.volume)
    if len(sols) > 1:
        note(pid, "%d pedaços soltos de lâmina retirados (%.2f mm3 no total), onde a dobra cruza o contorno interno" % (len(sols) - 1, sum(so.volume for so in sols[1:])))
    return sols[0]


def power_axis():
    """Eixo do conector de energia no plano xy (CSV): centro do corpo c, direção de encaixe u e
    direção através das fileiras n (u girado de +90 graus), como em io_parts.build_power_connector."""
    cx, cy = M("power_connector_center_from_bracket_end"), M("power_connector_center_y")
    a = math.radians(M("power_connector_rotation_deg") + 90.0)
    return np.array([cx, cy]), np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])


def connector_profile():
    """Perfil do corpo do conector (io_parts.G): largura da parte de potência através das fileiras
    (p16_across), extensão em z da faixa dos 4 pinos de sinal (p16_sense_len_z) e altura da trava
    (p16_latch), para o furo do colar seguir o corpo."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import io_parts as IO
    return IO.G["p16_across"][0], IO.G["p16_sense_len_z"][0], IO.G["p16_latch"][0][2]


def power_tunnel_half_width():
    """Meia largura do túnel através das fileiras: metade de power_connector_body_across mais a
    folga shroud_power_opening_clear (a mesma folga do contrato em z)."""
    return M("power_connector_body_across") / 2 + M("shroud_power_opening_clear")


def power_tunnel_xy(grow, s0, s1):
    """Contorno xy (lista de pontos) do túnel do conector: |t| <= meia largura + grow, s de s0 a s1
    ao longo da direção de encaixe, a partir do centro do corpo."""
    c, u, n = power_axis()
    hw = power_tunnel_half_width() + grow
    return [tuple(c + s * u + t * n) for s, t in ((s0, -hw), (s1, -hw), (s1, hw), (s0, hw))]


def power_tunnel(grow, s0, s1):
    """Prisma do túnel: contorno de power_tunnel_xy, z de iface_shroud_power_opening_z_min - grow
    a iface_shroud_power_opening_z_max + grow."""
    return ext(poly(power_tunnel_xy(grow, s0, s1)), M("iface_shroud_power_opening_z_min") - grow,
               M("iface_shroud_power_opening_z_max") + grow)


def power_tunnel_x_at(y, t):
    """x da linha do túnel de coordenada através t no nível y."""
    c, u, n = power_axis()
    s = (y - c[1] - t * n[1]) / u[1]
    return float(c[0] + s * u[0] + t * n[0])


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


def channel_z_range():
    """Faixa em z do canal (sem a parede): da face A menos a borda ch_lip_a até a frente do
    PCB mais a folga, para o fundo do canal não cruzar o PCB."""
    return M("iface_pcb_front_z") + g("ch_pcb_clear") + WALL, T - g("ch_lip_a")


def keepouts():
    """Volumes internos da carcaça que as peças vizinhas não podem ocupar, em caixas
    alinhadas aos eixos (x0, x1, y0, y1, z0, z1). Usado pelo blockout e pela integração."""
    cx0, cx1 = channel_x_range()
    cz0, cz1 = channel_z_range()
    floor = Y1 - M("shroud_channel_depth") - WALL
    nx0, nx1 = M("shroud_pcie_side_notch_x_start"), M("shroud_pcie_side_notch_x_end")
    nd = M("shroud_pcie_side_notch_depth")
    rec, tE = M("shroud_end_plate_recess"), M("shroud_end_plate_thickness")
    return {
        "canal": (cx0 - WALL, cx1 + WALL, floor, Y1, cz0 - WALL, cz1 + WALL),
        "entalhe": (nx0 - WALL, nx1 + WALL, Y0, Y0 + nd + WALL, Z_FACE_B, T - T_A),
        "parede_inferior": (0, L, Y0, Y0 + WALL, Z_FACE_B, T),
        "parede_superior": (0, L, Y1 - WALL, Y1, Z_FACE_B, T),
        "placa_de_extremidade": (0, rec + tE, Y0, Y1, Z_FACE_B, T),
        "parede_da_ponta": (L - WALL, L, Y0, Y1, Z_FACE_B, T),
        "chapa_da_face_a": (0, L, Y0, Y1, T - T_A, T),
        # caixa da boca do túnel do conector na borda superior (o túnel corre a 45 graus para dentro)
        "encaixe_do_conector": (power_tunnel_x_at(Y1 - M("shroud_channel_depth") - WALL, power_tunnel_half_width() + WALL),
                                power_tunnel_x_at(Y1, -power_tunnel_half_width() - WALL),
                                Y1 - M("shroud_channel_depth") - WALL, Y1, M("iface_shroud_power_opening_z_min") - WALL,
                                M("iface_shroud_power_opening_z_max") + WALL),
        "fenda_do_adaptador": adapter_strip_cut()[:2] + (Y0, adapter_strip_cut()[3], M("iface_adapter_board_z_min") - g("adapter_clear"), adapter_strip_cut()[5]),
    }


# ---------------------------------------------------------------------------
# Peças
# ---------------------------------------------------------------------------
NOTES = {i: [] for i in IDS}


def note(pid, txt):
    NOTES[pid].append(txt)


def build_shroud():
    pid = "frame.shroud"
    O = outline()
    tA = T_A
    inner = inset(O, WALL)

    # corpo: casca aberta do lado da face B (z = Z_FACE_B), aresta da face A (z = T) arredondada
    body = ext(O, Z_FACE_B, T)
    body = fillet(body.edges().filter_by(lambda e: e.center().Z > T - 1e-3), g("edge_fillet_a"))
    body = body - ext(inner, Z_FACE_B - 1, T - tA)

    # placa de extremidade do lado das portas, recuada dentro das bordas laterais
    rec, tE = M("shroud_end_plate_recess"), M("shroud_end_plate_thickness")
    # o vão do recuo é o contorno interno deslocado até x = 0: sobram as bordas de cima e de
    # baixo e a parede curva do canto
    body = body - (ext(Pos(-WALL - 0.5, 0) * inner, Z_FACE_B - 1, T - tA) & box3(-1, rec, Y0 - 1, Y1 + 1, -1, T + 1))
    plate = ext(inner, Z_FACE_B, T - tA) & box3(rec, rec + tE, Y0 - 1, Y1 + 1, -1, T + 1)
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
        body = body - ext(Pos(fx, FAN_Y) * Circle(R_OPEN), T - tA - 0.01, T + 1)
        ring = Pos(fx, FAN_Y) * Circle(R_OPEN + WALL) - Pos(fx, FAN_Y) * Circle(R_OPEN)
        body = body + (ext(ring, T - duct_z, T - tA + 0.01) & ext(inner, T - duct_z - 1, T - tA + 0.02))
    note(pid, "duto cilíndrico de parede %.1f mm atrás de cada anel, de z = %.1f (layer_end_fan_ring = %.0f mm abaixo da face A) a %.1f: interior da carcaça sem foto" % (WALL, T - duct_z, duct_z, T - tA))

    # X da face A: tampas lisas rebaixadas, faixa lisa e grades
    pod = inset(O, g("pod_frame_w"))
    tris = face_a_triangles()
    tris_exp = face_a_triangles(g("rib_w_a"))
    disks = [Pos(fx, FAN_Y) * Circle(R_RING) for fx in FAN_X]
    rec_reg = (tris[0] + tris[1]) & inset(O, g("tri_rim_a"))
    body = body - ext(rec_reg, T - g("tri_recess_a"), T + 1)
    half_t = 90.0 - math.degrees(ANG)          # setor até o ponto de tangência do X com o anel
    w_x = pod - tris_exp[0] - tris_exp[1] - disks[0] - disks[1]
    w_x = w_x & sector(FAN_X[0], FAN_Y, 0.0, half_t) & sector(FAN_X[1], FAN_Y, 180.0, half_t)
    w_x = w_x & rect(FAN_X[0], FAN_X[1], Y0, Y1)
    w_x = round_convex(w_x, g("win_r_a"))
    w_c = ((pod - disks[0]) & rect(-1, FAN_X[0], Y0, Y1)) + ((pod - disks[1]) & rect(FAN_X[1], L + 1, Y0, Y1))
    w_c = round_convex(w_c, g("win_r_a"))
    body = body - ext(w_x, T - tA - 0.01, T + 1) - ext(w_c, T - tA - 0.01, T + 1)
    clip_a = inner - tris[0] - tris[1]
    for fx in FAN_X:
        clip_a = clip_a - Pos(fx, FAN_Y) * Circle(R_OPEN + 0.2)
    lam, amp_a = chevron_louvres(w_c + w_x, g("lam_pitch_a"), g("lam_t_a"), T - tA - g("lam_depth_a"), T - g("lam_recess_a"), clip_a)
    body = body + lam
    note(pid, "janelas do X da face A com a mesma grade dos cantos: em pny/front os braços do X entre as tampas e os anéis mostram nervuras verticais uniformes, como os cantos; antes ficavam abertas e mostravam tubos de calor e a câmara (visual-qa-placa-final, achado 3)")
    note(pid, "lâminas das grades da face A (cantos e braços do X) em V no plano xz: passo %.1f (derived), espessura %.1f, recuo %.1f e profundidade de z = %.1f a %.1f (palpite); a dobra avança %.2f mm em x, mais que o vão entre lâminas (%.2f), e a grade fica opaca de frente e em vista oblíqua (achados 2 e 3)" % (
        g("lam_pitch_a"), g("lam_t_a"), g("lam_recess_a"), T - tA - g("lam_depth_a"), T - g("lam_recess_a"), amp_a, g("lam_pitch_a") - g("lam_t_a")))

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
    body = body + ext(u_wall, Z_FACE_B, T - tA + 0.01)
    # fenda da faixa do adaptador PCIe na parede inferior (e na perna da parede em U do entalhe)
    x0s, x1s, _, y1s, _, z1s = adapter_strip_cut()
    z0s = M("iface_adapter_board_z_min") - g("adapter_clear")
    body = body - box3(x0s, x1s, Y0 - 1, y1s, z0s, z1s)
    note(pid, "fenda na parede inferior para a faixa do adaptador PCIe: x de %.2f a %.2f (iface_adapter_x_min e _max com a folga), z de %.2f a %.2f (adaptador no plano da pcb.plate)" % (x0s, x1s, z0s, z1s))

    # canal da borda superior
    cx0, cx1 = channel_x_range()
    cz0, cz1 = channel_z_range()          # z0 do lado do PCB, z1 do lado da face A
    d = M("shroud_channel_depth")
    r = g("ch_corner_r")
    tub = xz_extrude(rrect_xz(cx0 - WALL, cx1 + WALL, cz0 - WALL, cz1 + WALL, r + WALL), Y1, d + WALL)
    body = body + (tub & ext(O, Z_FACE_B, T))
    body = body - xz_extrude(rrect_xz(cx0, cx1, cz0, cz1, r), Y1 + 1, d + 1)
    floor_y = Y1 - d
    sx0 = cx0 + g("slot_x_margin")
    ox = M("iface_shroud_power_opening_x")
    a_open = [a["pos"] for a in PARTS[pid]["anchors"] if a["id"].endswith("power_opening")][0]
    oz0, oz1 = M("iface_shroud_power_opening_z_min"), M("iface_shroud_power_opening_z_max")
    assert abs((oz0 + oz1) / 2 - a_open[2]) < 0.05, "abertura do conector fora da âncora"
    assert abs(a_open[0] - ox) < 0.05
    # fendas: terminam slot_end_gap antes da luva do túnel do conector, medido no fundo do canal
    hw = power_tunnel_half_width()
    sx1 = power_tunnel_x_at(floor_y - WALL, hw + WALL) - g("slot_end_gap")
    assert sx1 > sx0 + 10, "fendas curtas demais"
    for dz in g("slot_z"):
        zc = T - dz
        body = body - xz_extrude(rrect_xz(sx0, sx1, zc - g("slot_w") / 2, zc + g("slot_w") / 2, g("slot_w") / 2 - 0.01), floor_y + 0.5, WALL + 1)
    pd0, pd1 = g("pad_z")
    body = body + xz_extrude(rrect_xz(sx0, sx0 + g("pad_len_x"), T - pd1, T - pd0, r), floor_y + g("pad_h"), g("pad_h") + 0.01)

    # túnel do conector de energia: o corpo fica a 45 graus no canto chanfrado do PCB, com a face de
    # encaixe para (+x, +y) (contrato: power_connector_rotation_deg); a carcaça abre um túnel ao longo
    # da direção de encaixe, da boca do corpo até a borda superior, para o plugue entrar e para a face
    # 2 x 6 aparecer de fora, como em pny/3qtr-top-right e storagereview/sr-3. Uma luva de parede
    # WALL fecha o túnel por dentro (de fora não se vê o interior da placa pela abertura).
    s_face = M("power_connector_body_depth") / 2
    s_hood = s_face - g("pw_hood")
    canal_void = xz_extrude(rrect_xz(cx0, cx1, cz0, cz1, r), Y1 + 1, d + 1)
    # boca: rebaixo retangular da profundidade do canal sobre o túnel (x do lado de menor x do túnel no
    # fundo do canal ao lado de maior x no topo), com uma cuba de parede WALL por baixo
    mx0, mx1 = power_tunnel_x_at(floor_y, hw), power_tunnel_x_at(Y1, -hw)
    mouth = box3(mx0, mx1, floor_y, Y1 + 1, oz0, oz1)
    mouth_tub = (box3(mx0 - WALL, mx1 + WALL, floor_y - WALL, Y1, oz0 - WALL, oz1 + WALL) & ext(O, Z_FACE_B, T)) - canal_void
    body = body + mouth_tub - mouth
    # luva do túnel: peça à parte (submalha frame.shroud.tunel, para o lookdev pintar de preto o interior)
    t_outer = power_tunnel(WALL, s_hood - WALL, g("pw_reach")) & ext(O, Z_FACE_B, T)
    t_inner = power_tunnel(0.0, s_hood - 1.0, g("pw_reach"))
    sleeve = t_outer - canal_void - mouth - t_inner
    body = body - t_outer - t_inner
    # colar no fundo da luva: fecha o túnel em volta do corpo (de fora não se vê o PCB pelas folgas)
    c_ax, u_ax, n_ax = power_axis()
    bc = g("pw_body_clear")
    w_pw, sense_z, lh = connector_profile()
    across = M("power_connector_body_across")
    t_lo = -across / 2 - bc                         # lado oposto à faixa de sinal
    t_pw = -across / 2 + w_pw + bc                  # fim da parte de potência
    t_hi = across / 2 + lh + bc                     # faixa de sinal com a trava
    zb0, zb1 = M("iface_pcb_front_z"), M("iface_pcb_front_z") + M("power_connector_body_height_z") + bc
    zc_b = M("iface_pcb_front_z") + M("power_connector_body_height_z") / 2
    s_c0, s_c1 = s_hood - WALL, s_hood

    def slab(ta, tb, za, zz):
        return ext(poly([tuple(c_ax + sv * u_ax + tv * n_ax) for sv, tv in ((s_c0 - 1, ta), (s_c1 + 1, ta), (s_c1 + 1, tb), (s_c0 - 1, tb))]), za, zz)
    hole = slab(t_lo, t_pw, zb0, zb1) + slab(t_pw - 0.5, t_hi, zc_b - sense_z / 2 - bc, zc_b + sense_z / 2 + bc)
    t_hi_note = t_hi
    collar = power_tunnel(0.0, s_c0, s_c1) - hole
    tunnel_piece = sleeve + collar
    x_open = (power_tunnel_x_at(Y1, hw), power_tunnel_x_at(Y1, -hw))
    assert x_open[0] < ox < x_open[1], "a boca do túnel não contém iface_shroud_power_opening_x"
    assert abs((power_tunnel_x_at(Y1, 0.0)) - ox) < 0.05, "o eixo do conector não cruza o topo em iface_shroud_power_opening_x"
    note(pid, "canal da borda superior de x = %.1f a %.1f (onde as bordas da tampa lisa da face A chegam ao topo) e z = %.1f a %.1f; profundidade, fendas, placa lisa e abertura do conector com medidas de palpite (sem cota nas referências)" % (cx0, cx1, cz0, cz1))
    note(pid, "túnel do conector de energia a 45 graus, ao longo da direção de encaixe (power_connector_rotation_deg + 90), da boca do corpo (power_connector_body_depth / 2 = %.2f do centro, menos pw_hood) até fora da carcaça: %.2f mm através (power_connector_body_across + 2 x shroud_power_opening_clear) por z = %.2f a %.2f (iface_shroud_power_opening_z_min e _max); o eixo cruza o topo em x = %.2f (iface_shroud_power_opening_x) e a boca na borda superior vai de x = %.2f a %.2f" % (
        s_face, 2 * hw, oz0, oz1, power_tunnel_x_at(Y1, 0.0), x_open[0], x_open[1]))
    note(pid, "luva de parede %.1f em volta do túnel, do topo até %.1f mm atrás da face de encaixe, recortada pelo vão do canal: de fora, pela abertura, só aparecem a face 2 x 6 e as paredes da luva (antes a abertura era um rasgo vertical sobre o canal e mostrava a lateral do corpo, componentes e o PCB: visual-qa-placa-final, achado 1)" % (WALL, g("pw_hood")))
    note(pid, "colar de %.1f mm no fundo da luva (s de %.2f a %.2f do centro do corpo), com furo no perfil do corpo mais %.1f de folga (parte de potência: t de %.2f a %.2f, z de %.2f a %.2f; faixa de sinal com a trava até t = %.2f, em %.1f mm de z): fecha as folgas entre o corpo e a luva (antes, pelo lado da faixa de sinal, via-se o PCB)" % (WALL, s_c0, s_c1, bc, t_lo, t_pw, zb0, zb1, t_hi_note, sense_z + 2 * bc))
    note(pid, "fendas do canal até x = %.2f (%.1f mm antes da luva, no fundo do canal)" % (sx1, g("slot_end_gap")))
    note(pid, "boca do túnel: rebaixo retangular de x = %.2f a %.2f e z = %.2f a %.2f com o fundo no fundo do canal (y = %.2f), cuba de parede %.1f; a abertura vista de cima é um retângulo limpo no plano do fundo do canal (visual-qa-placa-final-2, N3)" % (
        mx0, mx1, oz0, oz1, floor_y, WALL))
    note(pid, "luva e colar do túnel numa submalha à parte, frame.shroud.tunel (paredes internas do túnel e moldura em volta da face do conector): acabamento preto no lookdev, como as outras aberturas")
    note(pid, "logotipo NVIDIA da borda superior não modelado (detalhe de superfície do passo do Blender)")
    tp = sorted(tunnel_piece.solids(), key=lambda so: -so.volume)
    return drop_loose(body, pid), (tp[0] if len(tp) == 1 else Compound(tp))


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
    z1 = Z_FACE_B                         # a face B vai de z = 0 (face externa) a z1
    frame = ext(in_rim - covers[0] - covers[1], 0, z1)
    frame = frame - ext(wins, -1, z1 + 1)
    lam, amp_b = chevron_louvres(wins, g("lam_pitch_b"), g("lam_t_b"), g("lam_recess_b"), z1, in_rim - covers[0] - covers[1])
    part = frame + lam
    # recorte da faixa do adaptador PCIe (gn-20 mostra a placa adaptadora num rebaixo da face B),
    # aberto até a face; a aba fica por dentro, sob um rebaixo que não aparece de fora
    part = part - box3(*adapter_strip_cut())
    for r in reliefs(z1 + 1):
        part = part - r
    # onde um rebaixo do E5 cai sob a grade, as lâminas voltam até o fundo da cabeça do parafuso (sem a folga
    # cover_relief_clear) e um fundo fino fecha o rebaixo ali: de fora a grade continua com as mesmas lâminas e
    # frestas sombreadas, sem deixar ver a cabeça (antes, quatro marcas que pny/back e gn-08 não mostram:
    # visual-qa-placa-final-2, N7)
    r5 = M("fastener_e5_head_diameter") / 2 + M("cover_relief_clear")
    z_head = M("layer_center_covers") - M("fastener_e5_head_height")
    n_floor = 0
    for x, y in e5_heads():
        disc = (Pos(x, y) * Circle(r5)) & wins
        if disc.faces() and disc.area > 1e-3:
            part = part + (lam & ext(disc, M("iface_cover_relief_e5_z_min") - 0.01, z_head)) + ext(disc, z_head - g("relief_floor_t"), z_head)
            n_floor += 1
    # a face B não passa da pcb.plate (que começa em z = layer_center_covers)
    pcx, pcy = M("iface_pcb_center_x"), M("iface_pcb_center_y")
    ztop_plate = M("layer_center_covers")
    part = part - box3(pcx - M("pcb_plate_outline_x") / 2, pcx + M("pcb_plate_outline_x") / 2,
                       pcy - M("pcb_plate_outline_y") / 2, pcy + M("pcb_plate_outline_y") / 2, ztop_plate, z1 + 1)
    note(pid, "estrutura do X e moldura das grades na mesma peça; as grades são lâminas reais (passo %.2f, espessura %.1f; espessura e recuo são palpite)" % (g("lam_pitch_b"), g("lam_t_b")))
    note(pid, "lâminas em V no plano xz, de z = %.1f a %.1f: a dobra avança %.2f mm em x, mais que o vão entre lâminas (%.2f); de frente e em vista oblíqua a grade fica opaca, com nervuras verticais uniformes, como em pny/back (antes as lâminas eram retas e o interior aparecia: visual-qa-placa-final, achado 2); forma da dobra sem foto de perfil (inferred)" % (
        g("lam_recess_b"), z1, amp_b, g("lam_pitch_b") - g("lam_t_b")))
    note(pid, "recorte para a faixa do adaptador PCIe ao longo da borda dos contatos, de iface_adapter_x_min a _max (folga %.1f mm), aberto da face até z = %.2f (iface_adapter_board_z_max): forma vista em gn-20, sem cota" % (g("adapter_clear"), M("iface_adapter_board_z_max")))
    note(pid, "rebaixos por baixo (não aparecem de fora): sob as 4 cabeças de fasteners.e5_plate (diâmetro %.1f, fundo em z = %.1f) e sobre a aba do adaptador com a presilha e as cabeças do E4 (contorno da aba mais %.1f, fundo em z = %.1f)" % (
        M("fastener_e5_head_diameter") + 2 * M("cover_relief_clear"), M("iface_cover_relief_e5_z_min"), M("cover_relief_clear"), M("iface_cover_relief_adapter_z_min")))
    note(pid, "a parte da face B sobre a pcb.plate vai só até z = %.1f (face da placa), não até %.1f: escolha para não cruzar a pcb.plate" % (ztop_plate, z1))
    note(pid, "%d rebaixos do E5 caem sob a grade (furos de canto do lado longe do bracket): ali as lâminas vão até z = %.1f (fundo da cabeça, sem folga) e um fundo de %.1f mm fecha o rebaixo; de fora só se veem as lâminas (N7); em gn-20 os 4 parafusos da pcb.plate aparecem sobre o X, não sob as grades: a posição dos furos (iface_plate_holes_*, inferred) é pendência do contrato" % (
        n_floor, z_head, g("relief_floor_t")))
    note(pid, "divisão: as grades das duas pontas e o X ficam numa peça só, como no assembly; na placa real elas parecem fazer parte das carcaças das pontas (gn-27), sem foto da junção")
    return part


def build_center_covers():
    pid = "frame.center_covers"
    _, _, covers, _ = face_b_regions()
    z1 = M("layer_center_covers")
    lower = ext(covers[1], 0, z1)
    upper = ext(covers[0], 0, z1)
    for r in reliefs(z1 + 1):
        lower = lower - r
        upper = upper - r
    note(pid, "duas tampas, inferior (instância 1, borda dos contatos) e superior (instância 2, com o texto), espessura layer_center_covers; vértices arredondados; a tampa da foto gn-20 tem uma aba na borda que não foi modelada (sem cota)")
    note(pid, "texto RTX PRO 6000 não gravado: só a caixa em extras (passo do Blender)")
    note(pid, "rebaixos por baixo das tampas: sob as cabeças de fasteners.e5_plate (fundo em z = %.1f, pele de %.1f) e, na tampa inferior, sobre a aba do adaptador PCIe, a presilha e as cabeças do E4 (fundo em z = %.1f): vistos ao tirar as tampas em gn-20 e gn-22, medidas por conta (assembly-plan 12.4)" % (
        M("iface_cover_relief_e5_z_min"), M("iface_cover_relief_e5_z_min"), M("iface_cover_relief_adapter_z_min")))
    return [lower, upper]


def build_rim():
    pid = "frame.rim"
    O = outline()
    rim = ext(O - inset(O, g("rim_w")), 0, Z_FACE_B)
    try:
        top_outer = [e for e in rim.edges() if e.center().Z < 1e-3 and _on_outline(e)]
        rim = fillet(top_outer, g("rim_fillet"))
    except Exception as ex:  # o arredondamento é cosmético
        note(pid, "arredondamento externo do aro falhou (%s); aro sem arredondamento" % ex)
    rim = rim - box3(*adapter_strip_cut())
    y, z, hd, hh, sd, sl = rim_screw()
    cl = g("rim_screw_clear")
    rim = rim - extrude(Plane.YZ.offset(-1) * (Pos(y, z) * Circle(hd / 2 + cl)), hh + 1 + cl)
    rim = rim - extrude(Plane.YZ.offset(hh) * (Pos(y, z) * Circle(sd / 2 + cl)), sl + 0.5)
    note(pid, "recorte da faixa do adaptador PCIe (o mesmo da face B)")
    note(pid, "furo do parafuso do aro (fasteners.e2_rim) com eixo em x na ponta do bracket, em y = %.2f e z = %.1f: rebaixo de %.1f mm para a cabeça (dentro do recuo da placa de extremidade, escondida pelo bracket) e furo de %.1f mm até a face interna do aro; posição sem foto (inferred)" % (
        y, z, hd + 2 * cl, sd + 2 * cl))
    note(pid, "aro como uma faixa de largura constante no contorno da face B, de z = 0 a %.0f; gn-17 mostra um aro fino, mas o desenho exato (se acompanha também o X) não dá para ler" % Z_FACE_B)
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
        "canto do bracket junto aos contatos quase reto": "derived (shroud_corner_radius_bracket_bottom; pny/front, pny/back)",
        "fenda do adaptador": "inferred (contrato de 2026-11-11, assembly-plan 12.3 e 12.4)",
        "túnel do conector a 45 graus com luva": "derived (eixo, ângulo e z do CSV; pny/3qtr-top-right, storagereview/sr-3); inferred (luva)",
        "anéis e aberturas dos ventiladores": "derived (CSV)",
        "X da face A (cruzamento e ângulo)": "derived (CSV)",
        "vértices, faixas e moldura das cápsulas da face A": "derived (pny/front; nesta tarefa)",
        "grades dos cantos e dos braços do X da face A": "derived (posição, passo); inferred (lâminas em V)",
        "entalhe PCIe": "derived (CSV)",
        "canal da borda superior: extensão em x": "derived (geometria do X; pny/front)",
        "canal: profundidade, fendas, placa lisa, abertura": "inferred (vistos em perspectiva, sem cota)",
        "paredes, espessuras, placa de extremidade, dutos": "inferred",
    },
    "frame.face_b": {
        "grades e estrutura do X (posição, faixas, vértices)": "derived (pny/back; nesta tarefa)",
        "lâminas (passo)": "derived (pny/back); espessura, recuo e perfil em V inferred",
        "recorte do adaptador PCIe": "derived (gn-20, forma); inferred (medida)",
        "rebaixos sob as cabeças do E5 e sobre a aba do adaptador": "inferred (assembly-plan 12.4)",
    },
    "frame.center_covers": {
        "contorno das tampas": "derived (pny/back; nesta tarefa)",
        "espessura": "inferred (layer_center_covers, orçamento)",
        "rebaixos por baixo": "inferred (assembly-plan 12.4; gn-20, gn-22)",
        "caixa do texto": "derived (CSV)",
    },
    "frame.rim": {
        "contorno": "derived (CSV)",
        "largura": "derived (pny/back; nesta tarefa)",
        "espessura e arredondamento": "inferred",
        "furo do parafuso do aro": "inferred (posição sem foto)",
    },
}


def shroud_zones():
    """Zonas de acabamento da carcaça (lidas pelo blender_pass.py, acab carcaca_a): as tampas lisas do X
    da face A (topo rebaixado, normal +z) e as lâminas das grades da face A (cantos e braços do X)."""
    return [
        {"name": "tampas_do_x_face_a", "material": "carcaca.tampa_x", "normal_z_min": 0.95, "z": round(T - g("tri_recess_a"), 3), "tol": 0.02,
         "nota": "topo rebaixado das tampas lisas do X da face A; preto espelhado como as tampas da face B (storagereview/sr-5, pny/front)"},
        {"name": "laminas_da_face_a", "material": "carcaca.grade", "z_min": round(T - T_A - g("lam_depth_a"), 3), "z_max": round(T - g("lam_recess_a"), 3), "tol": 0.02,
         "nota": "lâminas em V das grades da face A (cantos e braços do X); o fundo da chapa (z = card_thickness - shroud_face_a_plate_thickness), por dentro, cai na mesma faixa e não aparece"},
    ]


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
        kind = a.get("kind", "surface")
        if kind == "opening":
            # âncora de abertura ou vão (marcada no assembly): basta ficar na caixa envolvente
            lo, hi = mesh.bounds
            ok = bool(np.all(np.asarray(a["pos"]) >= lo - 1e-6) and np.all(np.asarray(a["pos"]) <= hi + 1e-6))
        else:
            ok = d <= TOL_ANCHOR
        res.append({"anchor": a["id"], "pos": a["pos"], "kind": kind, "dist_mm": round(d, 3), "inside": bool(isin),
                    "ok": ok})
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shroud_body, tunnel_piece = build_shroud()
    subs = {"frame.shroud": [("tunel", tunnel_piece, "preto fosco do interior das aberturas (luva e colar do túnel do conector)")]}
    shapes = {
        "frame.shroud": [shroud_body],
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
        sub_meshes = [(nm, to_mesh(sh), ac) for nm, sh, ac in subs.get(pid, [])]
        mesh = trimesh.util.concatenate(meshes + [m for _, m, _ in sub_meshes])
        ntri = int(len(mesh.faces))
        total_tris += ntri
        closed = [bool(m.is_watertight and m.is_winding_consistent and m.volume > 0) for m in meshes + [m for _, m, _ in sub_meshes]]
        lo, hi = mesh.bounds
        lo_all, hi_all = np.minimum(lo_all, lo), np.maximum(hi_all, hi)
        anchors = anchor_check(pid, mesh)
        extras = {
            "id": pid, "stage": p["stage"], "fidelity": p["fidelity"],
            "exists_provenance": p["exists_provenance"], "shape_provenance": "derived",
            "shape_provenance_features": FEATURE_PROV[pid],
            "guess": True, "guess_notes": NOTES[pid],
            "blockout": False, "units_cad": "mm", "up_cad": "+Z", "origin": "card.envelope_min",
            "referencial": "face B em z = 0, face A (ventiladores) em z = card_thickness",
            "explode_cad": p["explode"],
        }
        if pid == "frame.shroud":
            extras["material_zones_cad_mm"] = shroud_zones()
        spec = []
        if len(meshes) == 1:
            spec.append((pid, extras, meshes[0], None, None))
            for nm, sm, ac in sub_meshes:
                spec.append(("%s.%s" % (pid, nm), {"submesh": nm, "part": pid, "acabamento": ac, "shape_provenance": "inferred"}, sm, None, 0))
        else:
            extras["count"] = p["count"]["value"]
            extras["count_provenance"] = p["count"]["provenance"]
            extras["text_box_cad_mm"] = {"corners_xy": text_box(), "z": 0.0, "text": "RTX PRO 6000",
                                         "angle_deg_cad": text_angle_cad(),
                                         "reading_dir_xy": [round(math.cos(math.radians(text_angle_cad())), 4), round(math.sin(math.radians(text_angle_cad())), 4)],
                                         "letter_up_xy": [round(math.sin(math.radians(text_angle_cad())), 4), round(-math.cos(math.radians(text_angle_cad())), 4)],
                                         "note": "direções tiradas de pny/back e passadas para (x, y) do assembly; o texto fica na face externa da face B (z = 0) e lê certo visto de -z com os contatos para cima, como em pny/back",
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
        comp = shapes[pid][0] if len(shapes[pid]) == 1 and not subs.get(pid) else Compound(list(shapes[pid]) + [sh for _, sh, _ in subs.get(pid, [])])
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
            print("    %-36s dist %.2f mm %s%s" % (a["anchor"], a["dist_mm"], "OK" if a["ok"] else "ACIMA DE %.0f mm" % TOL_ANCHOR,
                                               " (âncora de abertura, dentro da caixa da peça)" if a["kind"] == "opening" else ""))
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
