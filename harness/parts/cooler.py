#!/usr/bin/env python3
"""Interior do cooler da RTX PRO 6000 Blackwell Workstation Edition (F3).

Gera, em build123d, as peças do interior do cooler com os ids e as âncoras do assembly:

  cooler.fins.1         pilha de aletas do lado do bracket: lâminas reais no plano yz, no passo
                        fin_pitch, com espessura fin_thickness, furadas para os 5 tubos do lado
  cooler.fins.2         pilha da ponta oposta, igual (mais curta: fin_stack_end_2_length_x)
  cooler.fins.3         pilha central sobre a câmara de vapor: lâminas com o recorte em X (faixa
                        rebaixada sob as nervuras do X da face A, placa lisa do X por cima),
                        degraus nos triângulos de cima e de baixo e entalhes para os tubos
  cooler.base           moldura preta da base (furo da câmara, recortes da carcaça e dos
                        conectores, colunas roscadas nos 8 furos) e a face de contato do die
  cooler.vapor_chamber  corpo da câmara de vapor sobre a face de contato
  cooler.heatpipes      10 tubos (5 por lado), instâncias cooler.heatpipes.1 a .10: trecho reto
                        na pilha, curva em S no plano xy até a borda da câmara, trecho sobre a
                        câmara com ponta arredondada e um pé soldado na lateral da câmara
  cooler.leaf_spring    mola de lâmina do verso: anel em volta da janela, 4 braços e 4 orelhas
                        com furo (forma de gn-29 e gn-32, desta placa)

Procedência (proposta aprovada, D5): o interior do cooler desta placa não tem foto. Existência
da câmara e dos tubos: derived (RTX 5090 Founders Edition, placa irmã, e Jon Peddie). Arranjo
copiado da placa irmã (três pilhas, X central em degraus, 5 tubos por lado que atravessam as
pilhas das pontas, moldura com face de contato embutida): derived, das fotos
rtx5090/wccftech-cooler-1 a -6. Medidas sem linha no CSV: inferred, no dicionário G, com
guess: true nos extras. A parte vista de fora (aletas pelas grades e pelos anéis, pilha central
pelas janelas do X, face de contato e mola) tem referência desta placa (pny/, gn-26, gn-29,
gn-32, gn-34).

Decisão sobre os tubos (conflito "cinco ou dez"): as fotos da placa irmã mostram 5 pontas de
tubo em cada lado (wccftech-cooler-4: 5 furos na ponta da pilha; -1 e -3: 5 tubos entre cada
pilha e o centro). Isso fecha com "dez tubos" (PCGH) e também com "cinco tubos de comprimento
duplo" (TechPowerUp, só resumo): de fora as duas leituras são iguais. Mantida a contagem do
assembly (10, derived), modelada como 10 tubos que terminam sobre a câmara, cada um com um pé
soldado na lateral dela ("3D vapor chamber with integrated heat pipes", NVIDIA).

Contrato: CAD em mm, Z para cima, origem em card.envelope_min, face B em z = 0 e face A
(ventiladores) em z = card_thickness (ARCHITECTURE.md, 7.6). O GLB sai em metros com Y para
cima, (x, y, z) -> (x, z, -y) / 1000, com as coordenadas absolutas nos vértices (sem
transformação de nó), como frame.py e fan.py; harness/parts/integrate.py troca as caixas do
blockout por estas malhas. Medidas do CSV pela chave; volumes internos da carcaça por
frame.keepouts(); conectores altos do PCB pela caixa das peças detalhadas em build/parts.

Uso:   python3 -I harness/parts/cooler.py
Saídas: harness/build/parts/<id>.glb e <id>.step para os 7 ids, harness/build/parts/cooler-report.json
"""
import csv
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import (Align, BuildSketch, Circle, Compound, Face, Kind, Locations, Plane, Pos,
                       Rectangle, Sketch, Solid, Spline, Vector, Wire, Line, export_step, extrude,
                       fillet, offset, sweep)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame as FR  # noqa: E402  (só leitura: contorno e volumes internos da carcaça)

HARNESS = Path(__file__).resolve().parent.parent
ASSEMBLY = HARNESS / "design" / "assembly.json"
MEASURES = HARNESS / "design" / "measurements.csv"
OUT = HARNESS / "build" / "parts"

IDS = ("cooler.fins.1", "cooler.fins.2", "cooler.fins.3", "cooler.base", "cooler.vapor_chamber",
       "cooler.heatpipes", "cooler.leaf_spring")

# Tolerâncias das conferências e da malha (não são medidas da peça)
TOL_ANCHOR = 2.0       # mm, âncora fora da peça
TOL_OVERLAP = 0.5      # mm, interferência aceita pelo integrate.py
TESS = {"fin": (0.05, 0.30), "pipe": (0.04, 0.26), "body": (0.03, 0.20)}   # desvio linear (mm) e angular (rad)
TRI_BUDGET = 250_000   # triângulos, as 7 peças juntas
CREASE_DEG = 30.0      # quebra das normais suaves (o mesmo do integrate.py)

# ---------------------------------------------------------------------------
# Valores sem linha no CSV: (valor, procedência, nota)
# ---------------------------------------------------------------------------
G = {
    # folgas
    "clear": (0.3, "inferred", "folga entre as peças do cooler e a carcaça, os conectores e a placa de portas (a mesma do blockout)"),
    "window_gap": (0.25, "inferred", "folga entre a câmara (e a face de contato) e o furo da moldura"),
    # base e câmara
    "contact_plate_t": (1.0, "inferred", "espessura da face de contato (parte de cooler.base no assembly); a câmara fica com vapor_chamber_thickness menos isto, para o conjunto ter os 4 mm do CSV"),
    "base_frame_t": (4.0, "inferred", "altura da moldura da base, igual à câmara com a face de contato (como no blockout); topo rente ao topo da câmara"),
    "base_corner_r": (2.0, "inferred", "raio dos cantos da moldura"),
    "chamber_corner_r": (4.0, "derived", "cantos arredondados da face de contato: cerca de 4 mm em gn-34 e wccftech-cooler-5 (placa irmã), proporção"),
    "chamber_top_fillet": (0.6, "inferred", "arredondamento da aresta de cima da câmara"),
    "post_r": (2.5, "inferred", "raio das colunas roscadas sob a moldura nos 8 furos (4 da mola e 4 da pcb.plate); gn-34 e gn-39 mostram colunas com parafuso, sem cota"),
    "post_hole_r": (1.2, "inferred", "raio do furo roscado das colunas (M2,5 suposto)"),
    "post_hole_depth": (2.5, "inferred", "profundidade do furo roscado"),
    # tubos
    "hp_pitch_stack": (18.0, "derived", "passo dos 5 tubos na pilha da ponta: os 5 furos ocupam cerca de 70 % da altura da placa de ponta em wccftech-cooler-4 (placa irmã); com 18 mm os furos ficam a 3,6 mm do contorno das aletas da ponta"),
    "hp_pitch_chamber": (12.5, "inferred", "passo dos 5 tubos sobre a câmara (cabem nos 68 mm da face de contato com 4,5 mm entre tubos)"),
    "hp_center_gap": (3.0, "inferred", "vão entre as pontas dos tubos dos dois lados no meio da câmara"),
    "hp_joint_len": (2.5, "inferred", "comprimento em x do pé soldado do tubo na lateral da câmara"),
    # pilha central
    "c_side_drop": (2.0, "inferred", "nas cunhas laterais (vistas pelas janelas do X da face A) as aletas ficam 2 mm abaixo do topo; em wccftech-cooler-4 essas cunhas são mais baixas que os triângulos de cima e de baixo"),
    "c_x_band": (6.0, "derived", "meia largura (perpendicular) da faixa do X sem aletas altas: proporção da faixa lisa em wccftech-cooler-3 (placa irmã)"),
    "c_x_drop": (7.0, "inferred", "rebaixo das aletas sob a faixa do X, a partir do topo"),
    "c_x_plate_t": (0.8, "inferred", "espessura da placa lisa do X apoiada nas aletas rebaixadas (wccftech-cooler-3 e -4 mostram o X liso)"),
    "c_step": (8.0, "inferred", "largura (em y) de cada degrau dos triângulos de cima e de baixo; 3 degraus (gn-26, desta placa; wccftech-cooler-3, placa irmã)"),
    "c_step_drop": (2.5, "inferred", "altura de cada degrau; o degrau mais alto fica longe do cruzamento do X"),
    # mola
    "spring_ring_wx": (8.0, "inferred", "largura do anel da mola nos lados (em x), como no blockout"),
    "spring_ring_wy": (5.0, "inferred", "largura do anel em cima e embaixo (em y): limitada pelas fileiras de memória do verso (mem.back) para não cruzá-las"),
    "spring_window_r": (6.0, "derived", "raio dos cantos da janela: janela de cantos bem arredondados em gn-29 e gn-32"),
    "spring_arm_w": (5.0, "inferred", "largura dos 4 braços (limitada pela memória do verso junto aos furos)"),
    "spring_tab_r": (3.5, "inferred", "raio das orelhas em volta dos furos (limitado pela memória do verso)"),
    "spring_hole_r": (1.6, "inferred", "raio do furo do parafuso"),
    "spring_round": (1.0, "inferred", "raio de concordância entre braços e anel e dos cantos"),
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

L = M("card_envelope_length")
T = M("card_thickness")
Y0 = M("iface_shroud_y_min")
Y1 = Y0 + M("shroud_height_proposed")
YC = M("iface_shroud_center_y")
WALL = M("shroud_wall")
RC = M("shroud_corner_radius")
T_A = M("shroud_face_a_plate_thickness")
CLR = g("clear")
DCX, DCY = M("iface_die_center_x"), M("iface_die_center_y")
PCX, PCY = M("iface_pcb_center_x"), M("iface_pcb_center_y")
ZC = M("iface_die_contact_z")
P_FIN = M("fin_pitch")
T_FIN = M("fin_thickness")
HD = M("heatpipe_diameter") / 2
VX, VY = M("vapor_chamber_contact_plate_x") / 2, M("vapor_chamber_contact_plate_y") / 2
VT = M("vapor_chamber_thickness")
Z_CP1 = ZC + g("contact_plate_t")                 # topo da face de contato, fundo da câmara
Z_TOP = ZC + VT                                   # topo da câmara e da moldura
assert abs(g("base_frame_t") - VT) < 1e-9, "moldura e câmara com topos diferentes"
Z_HP = Z_TOP + HD                                 # eixo dos tubos: apoiados na câmara e na moldura
# pilhas das pontas: entre a grade da face B e o ventilador
Z_F1 = T - M("layer_end_fan_ring")
Z_F0 = Z_F1 - M("fin_stack_end_depth_z")
# pilha central: da câmara até a chapa da face A
Z_C_FULL = T - T_A - CLR
ANG = math.radians(M("x_rib_angle_deg"))
K = math.tan(ANG)
XA = M("x_rib_cross_face_a_from_bracket_end")
KO = FR.keepouts()


def neighbor_box(pid):
    """Caixa (lo, hi) de uma peça vizinha já detalhada em build/parts (conectores altos)."""
    import integrate as I
    path = OUT / ("%s.glb" % pid)
    js, binary = I.read_glb(path)
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for n in js["nodes"]:
        if "mesh" not in n:
            continue
        prim = js["meshes"][n["mesh"]]["primitives"][0]
        v = I.from_gltf(I.accessor(js, binary, prim["attributes"]["POSITION"]))
        lo, hi = np.minimum(lo, v.min(0)), np.maximum(hi, v.max(0))
    return lo, hi


CONN = neighbor_box("power.connector")
AUX = neighbor_box("io.aux_header")
REPORT_EXTRA = {}


def front_parts():
    """Caixas das instâncias das peças da frente do PCB (para não pôr coluna sobre componente)."""
    import integrate as I
    out = []
    for pid in ("power.inductors", "mem.front", "power.aux", "power.controller", "power.vrm.mem", "gpu.package", "io.aux_header", "power.connector"):
        path = OUT / ("%s.glb" % pid)
        if not path.exists():
            continue
        js, binary = I.read_glb(path)
        for n in js["nodes"]:
            if "mesh" not in n:
                continue
            prim = js["meshes"][n["mesh"]]["primitives"][0]
            v = I.from_gltf(I.accessor(js, binary, prim["attributes"]["POSITION"]))
            out.append((n["name"], v))
    return out


def hull_dist(v, x, y):
    """Distância em xy do ponto ao contorno convexo dos vértices (0 se dentro)."""
    from scipy.spatial import ConvexHull
    p = np.asarray(v)[:, :2]
    h = p[ConvexHull(p).vertices]
    q = np.array([x, y])
    inside = True
    best = np.inf
    for a, b in zip(h, np.roll(h, -1, axis=0)):
        e = b - a
        if e[0] * (q - a)[1] - e[1] * (q - a)[0] < 0:
            inside = False
        t = np.clip(np.dot(q - a, e) / np.dot(e, e), 0, 1)
        best = min(best, float(np.linalg.norm(a + t * e - q)))
    return 0.0 if inside else best


FRONT_PARTS = front_parts()
IO_X1 = M("dp_receptacle_depth") + M("pcb_thickness")       # face interna de io.board (como no blockout)

NOTES = {i: [] for i in IDS}


def note(pid, txt):
    NOTES[pid].append(txt)


# ---------------------------------------------------------------------------
# Auxiliares 2D e 3D
# ---------------------------------------------------------------------------
def poly(pts):
    return Sketch() + Face(Wire.make_polygon([Vector(a, b, 0) for a, b in pts], close=True))


def rect(a0, a1, b0, b1):
    return Pos((a0 + a1) / 2, (b0 + b1) / 2) * Rectangle(a1 - a0, b1 - b0)


def rrect(a0, a1, b0, b1, r):
    with BuildSketch() as s:
        with Locations(((a0 + a1) / 2, (b0 + b1) / 2)):
            Rectangle(a1 - a0, b1 - b0)
        if r > 0:
            fillet(s.vertices(), r)
    return s.sketch


def ext_z(sk, z0, z1):
    return Pos(0, 0, z0) * extrude(sk, z1 - z0, dir=(0, 0, 1))


def fin_solid(sk_yz, x0, t):
    """Lâmina: esboço em coordenadas locais (u = y, v = z), extrudado de x0 a x0 + t."""
    return extrude(Plane.YZ.offset(x0) * sk_yz, t)


# ---------------------------------------------------------------------------
# Contorno interno da carcaça (para as pilhas das pontas)
# ---------------------------------------------------------------------------
def corners():
    """Centros e raios dos cantos do contorno da carcaça (frame.outline): canto do bracket
    junto aos contatos quase reto (frame.G), os outros com shroud_corner_radius."""
    rb = FR.g("bracket_bottom_corner_r")
    return [(rb, Y0 + rb, rb, -1, -1), (RC, Y1 - RC, RC, -1, 1), (L - RC, Y0 + RC, RC, 1, -1), (L - RC, Y1 - RC, RC, 1, 1)]


def y_limits(x, y0, y1):
    """Faixa em y livre dentro do contorno interno da carcaça (menos parede e folga) em x."""
    for cx, cy, r, sx, sy in corners():
        ri = r - WALL - CLR
        if (x - cx) * sx > 0:
            d = abs(x - cx)
            if d >= ri:
                return None
            dy = math.sqrt(ri * ri - d * d)
            if sy > 0:
                y1 = min(y1, cy + dy)
            else:
                y0 = max(y0, cy - dy)
    return y0, y1


# ---------------------------------------------------------------------------
# Tubos: trajeto
# ---------------------------------------------------------------------------
def stack_ranges():
    """Faixa em x de cada pilha da ponta e posição das lâminas (face de menor x)."""
    end_in = KO["placa_de_extremidade"][1]
    a0 = max(end_in, IO_X1) + CLR
    a1 = M("fin_stack_end_1_length_x")
    b0 = L - M("fin_stack_end_2_length_x")
    b1 = L - WALL - CLR
    n1 = int(math.floor((a1 - a0 - T_FIN) / P_FIN + 1e-9)) + 1
    n2 = int(math.floor((b1 - b0 - T_FIN) / P_FIN + 1e-9)) + 1
    xs1 = [a1 - T_FIN - k * P_FIN for k in range(n1)][::-1]        # a lâmina de dentro encosta no PCB
    xs2 = [b0 + k * P_FIN for k in range(n2)]
    return (a0, a1, xs1), (b0, b1, xs2)


S1, S2 = stack_ranges()
FIN_Y0 = max(YC - M("fin_stack_end_height_y") / 2, Y0 + WALL + CLR)
FIN_Y1 = min(YC + M("fin_stack_end_height_y") / 2, Y1 - WALL - CLR, KO["canal"][2] - CLR)


def pipe_y_stack(i):
    return YC + g("hp_pitch_stack") * (i - 2)


def pipe_y_chamber(i):
    return DCY + g("hp_pitch_chamber") * (i - 2)


def pipe_layout(side):
    """Pontos do trajeto de um lado: side = -1 (bracket, fins.1) ou +1 (ponta, fins.2).
    Devolve (x_externo, x_pilha, x_camara, x_ponta)."""
    if side < 0:
        x_out, x_in = xs_first(S1), S1[1]
        x_ch = DCX - VX
        x_tip = DCX - g("hp_center_gap") / 2 - HD
    else:
        x_out, x_in = S2[2][-1] + T_FIN, S2[0]
        x_ch = DCX + VX
        x_tip = DCX + g("hp_center_gap") / 2 + HD
    return x_out, x_in, x_ch, x_tip


def xs_first(S):
    return S[2][0]


def pipe_y_at(i, side, x):
    """y do eixo do tubo i em x (curva em S com tangente paralela a x nas duas pontas)."""
    x_out, x_in, x_ch, x_tip = pipe_layout(side)
    ys, yc = pipe_y_stack(i), pipe_y_chamber(i)
    u = (x - x_in) / (x_ch - x_in)
    if u <= 0:
        return ys
    if u >= 1:
        return yc
    h = 3 * u * u - 2 * u ** 3
    return ys + (yc - ys) * h


def pipe_on_x(side, x):
    """O tubo do lado existe nesta posição x?"""
    x_out, x_in, x_ch, x_tip = pipe_layout(side)
    lo, hi = sorted((x_out, x_tip + side * HD))
    return lo <= x <= hi


# ---------------------------------------------------------------------------
# Peças
# ---------------------------------------------------------------------------
def build_end_stack(n):
    pid = "cooler.fins.%d" % n
    S = S1 if n == 1 else S2
    side = -1 if n == 1 else 1
    cache, fins = {}, []
    for x in S[2]:
        lim0 = y_limits(x, FIN_Y0, FIN_Y1)
        lim1 = y_limits(x + T_FIN, FIN_Y0, FIN_Y1)
        y0, y1 = max(lim0[0], lim1[0]), min(lim0[1], lim1[1])
        key = (round(y0, 3), round(y1, 3))
        if key not in cache:
            sk = rect(y0, y1, Z_F0, Z_F1)
            for i in range(5):
                yy = pipe_y_stack(i)
                assert yy - HD > y0 + 0.5 and yy + HD < y1 - 0.5, "furo do tubo fora da lâmina em x = %.2f" % x
                sk = sk - Pos(yy, Z_HP) * Circle(HD)
            cache[key] = (sk, fin_solid(sk, 0.0, T_FIN))
        fins.append((x, key))
    note(pid, "%d lâminas de %.2f mm no passo de %.2f mm (fin_pitch e fin_thickness, inferred), de x = %.2f a %.2f; a contagem sai do passo e do comprimento da pilha, não de foto" % (
        len(S[2]), T_FIN, P_FIN, S[2][0], S[2][-1] + T_FIN))
    note(pid, "lâminas no plano yz de z = %.1f (grade da face B) a %.1f (layer_end_fan_ring abaixo da face A), y de %.2f a %.2f (fin_stack_end_height_y), com os cantos da ponta recortados pelo contorno interno da carcaça" % (Z_F0, Z_F1, FIN_Y0, FIN_Y1))
    note(pid, "5 furos de %.0f mm para os tubos em z = %.1f, passo de %.0f mm em y (derived da placa irmã: wccftech-cooler-4)" % (2 * HD, Z_HP, g("hp_pitch_stack")))
    note(pid, "golas (colarinhos) dos furos, dobras das bordas e as placas de fixação dos ventiladores da placa irmã não modeladas")
    if n == 1:
        note(pid, "começa em x = %.2f, depois da placa de portas (io.board) e da placa de extremidade da carcaça" % S[0])
    return fins, cache


def build_center_stack():
    pid = "cooler.fins.3"
    lc = M("fin_stack_center_length_x")
    n = int(math.floor((lc - T_FIN) / P_FIN + 1e-9)) + 1
    span = (n - 1) * P_FIN + T_FIN
    xs = [DCX - span / 2 + k * P_FIN for k in range(n)]
    bw = g("c_x_band") / math.cos(ANG)            # meia faixa do X medida em y
    zs = Z_C_FULL - g("c_side_drop")
    zx = Z_C_FULL - g("c_x_drop")
    nx0, nx1 = KO["entalhe"][0] - CLR, KO["entalhe"][1] + CLR
    y_top_wall = KO["canal"][2] - CLR
    fins, plate_pts = [], []
    for x in xs:
        xm = x + T_FIN / 2
        y0 = max(DCY - M("cooler_base_frame_outline_y") / 2, Y0 + WALL + CLR)
        if x + T_FIN > nx0 and x < nx1:
            y0 = max(y0, KO["entalhe"][3] + CLR)
        y1 = min(y_top_wall, Y1 - WALL - CLR)
        # degraus em y: |y - YC| - K |x - XA| = s
        d = K * abs(xm - XA)
        cuts = [d - bw, d + bw, d + bw + g("c_step"), d + bw + 2 * g("c_step")]
        levels = [zs, zx, Z_C_FULL - 2 * g("c_step_drop"), Z_C_FULL - g("c_step_drop"), Z_C_FULL]

        def level(t):
            for c, z in zip(cuts, levels):
                if t < c:
                    return z
            return levels[-1]
        # pontos de quebra em y (os dois lados de YC)
        br = sorted({y0, y1} | {YC + sg * c for c in cuts for sg in (-1, 1) if y0 < YC + sg * c < y1})
        segs = []
        for a, b in zip(br[:-1], br[1:]):
            segs.append((a, b, level(abs((a + b) / 2 - YC))))
        pts = [(y0, Z_TOP)]
        for a, b, z in segs:
            pts += [(a, z), (b, z)]
        pts.append((y1, Z_TOP))
        clean = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - clean[-1][0]) > 1e-6 or abs(p[1] - clean[-1][1]) > 1e-6:
                clean.append(p)
        sk = poly(clean)
        # entalhes dos tubos (o tubo e o pé atravessam a lâmina por baixo)
        for side in (-1, 1):
            if not (pipe_on_x(side, x) or pipe_on_x(side, x + T_FIN)):
                continue
            for i in range(5):
                yy = pipe_y_at(i, side, xm)
                sk = sk - Pos(yy, Z_HP) * Circle(HD) - rect(yy - HD, yy + HD, Z_TOP - 1, Z_HP)
        # conector de energia (caixa da peça detalhada)
        if x + T_FIN > CONN[0][0] - CLR and x < CONN[1][0] + CLR:
            sk = sk - rect(CONN[0][1] - CLR, Y1 + 5, Z_TOP - 1, CONN[1][2] + CLR)
        fins.append((x, sk))
        plate_pts.append(xm)
    # placa lisa do X apoiada nas aletas rebaixadas
    zp0, zp1 = zx, zx + g("c_x_plate_t")
    x0, x1 = xs[0], xs[-1] + T_FIN
    band = Sketch()
    for sg in (-1, 1):
        # faixa |(y - YC) - sg K (x - XA)| <= bw, cortada em x
        band = band + poly([(x0, YC + sg * K * (x0 - XA) - bw), (x1, YC + sg * K * (x1 - XA) - bw),
                            (x1, YC + sg * K * (x1 - XA) + bw), (x0, YC + sg * K * (x0 - XA) + bw)])
    y0p = max(DCY - M("cooler_base_frame_outline_y") / 2, Y0 + WALL + CLR, KO["entalhe"][3] + CLR)
    band = band & rect(x0, x1, y0p, y_top_wall)
    if CONN[0][0] - CLR < x1:
        band = band - rect(CONN[0][0] - CLR, x1 + 1, CONN[0][1] - CLR, Y1 + 5)
    plate = ext_z(band, zp0, zp1)
    note(pid, "%d lâminas de %.2f mm no passo de %.2f mm, de x = %.2f a %.2f (fin_stack_center_length_x = %.0f centrado no die)" % (n, T_FIN, P_FIN, xs[0], xs[-1] + T_FIN, lc))
    note(pid, "recorte em X: sob as nervuras do X da face A (cruzamento em x_rib_cross_face_a, ângulo x_rib_angle_deg) as lâminas descem %.1f mm e recebem uma placa lisa de %.1f mm (o X liso da placa irmã, wccftech-cooler-3 e -4); cunhas laterais, vistas pelas janelas do X da face A, %.1f mm abaixo do topo; triângulos de cima e de baixo em 3 degraus de %.1f mm subindo para longe do cruzamento (gn-26, desta placa)" % (
        g("c_x_drop"), g("c_x_plate_t"), g("c_side_drop"), g("c_step_drop")))
    note(pid, "de z = %.1f (topo da câmara e da moldura) a %.1f (chapa da face A menos a folga); em y da borda da base até o fundo do canal da borda superior, recortada no entalhe PCIe e em volta do conector de energia" % (Z_TOP, Z_C_FULL))
    note(pid, "entalhes por baixo para os tubos que correm sobre a câmara; pad branco da borda superior (gn-21, gn-30) não modelado")
    return fins, plate


def frame_sketch():
    bx, by = M("cooler_base_frame_outline_x") / 2, M("cooler_base_frame_outline_y") / 2
    sk = rrect(PCX - bx, PCX + bx, PCY - by, PCY + by, g("base_corner_r"))
    cuts = [
        ("entalhe da carcaça", (KO["entalhe"][0] - CLR, KO["entalhe"][1] + CLR, Y0 - 5, KO["entalhe"][3] + CLR)),
        ("canal da borda superior", (KO["canal"][0] - CLR, KO["canal"][1] + CLR, KO["canal"][2] - CLR, Y1 + 5)),
        ("conector de energia", (CONN[0][0] - CLR, CONN[1][0] + CLR, CONN[0][1] - CLR, Y1 + 5)),
        ("conector auxiliar", (AUX[0][0] - CLR, AUX[1][0] + CLR, AUX[0][1] - CLR, Y1 + 5)),
    ]
    for _, (a0, a1, b0, b1) in cuts:
        sk = sk - rect(a0, a1, b0, b1)
    return sk, [c[0] for c in cuts]


def holes8():
    sx, sy = M("iface_spring_holes_dx") / 2, M("iface_spring_holes_dy") / 2
    px, py = M("iface_plate_holes_dx") / 2, M("iface_plate_holes_dy") / 2
    return ([(DCX + a * sx, DCY + b * sy) for a in (-1, 1) for b in (-1, 1)],
            [(PCX + a * px, PCY + b * py) for a in (-1, 1) for b in (-1, 1)])


def build_base():
    pid = "cooler.base"
    sk, cut_names = frame_sketch()
    wg = g("window_gap")
    sk_frame = sk - rrect(DCX - VX - wg, DCX + VX + wg, DCY - VY - wg, DCY + VY + wg, g("chamber_corner_r") + wg)
    # bolsos dos pés dos tubos (lateral da câmara)
    for side in (-1, 1):
        xe = DCX + side * VX
        xa, xb = sorted((xe, xe + side * (g("hp_joint_len") + CLR)))
        for i in range(5):
            yy = pipe_y_chamber(i)
            sk_frame = sk_frame - rect(xa, xb, yy - HD - CLR, yy + HD + CLR)
    frame = ext_z(sk_frame, ZC, Z_TOP)
    plate = ext_z(rrect(DCX - VX, DCX + VX, DCY - VY, DCY + VY, g("chamber_corner_r")), ZC, Z_CP1)
    spring_h, plate_h = holes8()
    z_pcb = M("iface_pcb_front_z")
    posts = []
    skipped = []
    for (hx, hy) in spring_h + plate_h:
        hit = [n for n, v in FRONT_PARTS if v[:, 2].min() < ZC and hull_dist(v, hx, hy) < g("post_r")]
        if hit:
            skipped.append(((round(hx, 2), round(hy, 2)), hit))
            continue
        foot = (Pos(hx, hy) * Circle(g("post_r"))) & sk_frame
        post = ext_z(foot, z_pcb, ZC + 0.01)
        post = post - ext_z(Pos(hx, hy) * Circle(g("post_hole_r")), z_pcb - 1, z_pcb + g("post_hole_depth"))
        posts.append(post)
    body = frame
    for p in posts:
        body = body + p
    note(pid, "moldura de %.1f x %.1f mm (cooler_base_frame_outline, centrada no PCB), de z = %.1f a %.1f, com furo para a câmara (folga %.2f) e bolsos para os 10 pés dos tubos" % (
        2 * M("cooler_base_frame_outline_x") / 2, M("cooler_base_frame_outline_y"), ZC, Z_TOP, wg))
    note(pid, "recortes: %s (caixas de frame.keepouts() e das peças detalhadas, com folga de %.1f)" % (", ".join(cut_names), CLR))
    note(pid, "face de contato de %.0f x %.0f mm e %.1f mm (vapor_chamber_contact_plate), no furo da moldura, centrada no die; é a face acobreada de gn-34 (pertence a cooler.base no assembly)" % (2 * VX, 2 * VY, g("contact_plate_t")))
    note(pid, "8 colunas roscadas de r = %.1f de z = %.1f (frente do PCB) até a moldura, nos furos da mola (iface_spring_holes) e da pcb.plate (iface_plate_holes)" % (g("post_r"), z_pcb))
    for (h, hit) in skipped:
        note(pid, "sem coluna no furo (%.2f; %.2f): %s ocupa o lugar (posição de componente inferred; pendência do pcb-layout-modeler)" % (h[0], h[1], ", ".join(hit)))
    REPORT_EXTRA["colunas_omitidas"] = [{"furo": h, "pecas": hit} for h, hit in skipped]
    note(pid, "blocos de alumínio sobre a memória e os indutores (gn-34, wccftech-cooler-5) não modelados: dependem da grade da memória, que vai mudar; a moldura é lisa por baixo")
    note(pid, "marca da pasta e datamatrix da face de contato: textura (extras.surface_detail)")
    return body, plate


def build_chamber():
    pid = "cooler.vapor_chamber"
    sk = rrect(DCX - VX, DCX + VX, DCY - VY, DCY + VY, g("chamber_corner_r"))
    ch = ext_z(sk, Z_CP1, Z_TOP)
    try:
        ch = fillet(ch.edges().filter_by(lambda e: e.center().Z > Z_TOP - 1e-3), g("chamber_top_fillet"))
    except Exception as ex:   # cosmético
        note(pid, "arredondamento da aresta de cima falhou (%s)" % ex)
    note(pid, "corpo plano de %.0f x %.0f mm, de z = %.1f (sobre a face de contato) a %.1f: %.1f mm, para o conjunto com a face de contato ter vapor_chamber_thickness = %.0f mm" % (
        2 * VX, 2 * VY, Z_CP1, Z_TOP, Z_TOP - Z_CP1, VT))
    note(pid, "interior (pavio, colunas) não modelado; o 3D da câmara é a ligação com os tubos (pés soldados na lateral, em cooler.heatpipes)")
    return ch


N_RING = 20       # lados do tubo na malha (não é medida)
N_BEND = 17       # anéis na curva em S
N_CAP = 5         # anéis da ponta arredondada


def tube_mesh(center, d_end):
    """Malha fechada de um tubo: anéis ao longo do eixo (plano em z constante), tampa plana no
    começo e meia esfera no fim (direção d_end)."""
    c = np.asarray(center, float)
    tg = np.gradient(c, axis=0)
    tg /= np.linalg.norm(tg, axis=1)[:, None]
    zh = np.array([0.0, 0.0, 1.0])
    rings = []
    th = np.linspace(0, 2 * math.pi, N_RING, endpoint=False)
    for p, t in zip(c, tg):
        n = np.cross(zh, t)
        n /= np.linalg.norm(n)
        rings.append([p + HD * (math.cos(a) * n + math.sin(a) * zh) for a in th])
    n_end = np.cross(zh, d_end)
    n_end /= np.linalg.norm(n_end)
    for ph in np.linspace(0, math.pi / 2, N_CAP + 1)[1:-1]:
        p = c[-1] + d_end * HD * math.sin(ph)
        rings.append([p + HD * math.cos(ph) * (math.cos(a) * n_end + math.sin(a) * zh) for a in th])
    V = np.array([q for r in rings for q in r])
    nr = len(rings)
    F = []
    for j in range(nr - 1):
        for k in range(N_RING):
            a, b = j * N_RING + k, j * N_RING + (k + 1) % N_RING
            F += [[a, b, b + N_RING], [a, b + N_RING, a + N_RING]]
    i0 = len(V)
    i1 = i0 + 1
    V = np.vstack([V, c[0], c[-1] + d_end * HD])
    for k in range(N_RING):
        F.append([i0, (k + 1) % N_RING, k])
        a, b = (nr - 1) * N_RING + k, (nr - 1) * N_RING + (k + 1) % N_RING
        F.append([a, b, i1])
    m = trimesh.Trimesh(V, np.array(F), process=False)
    if m.volume < 0:
        m.invert()
    return m


def box_mesh(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    b.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return b


def build_pipes():
    """Devolve, por tubo, (sólidos para o STEP, malha para o GLB). A malha é feita aqui (anéis),
    não pela tesselagem da varredura, que sai densa e com costura aberta."""
    pid = "cooler.heatpipes"
    out = []
    for side in (-1, 1):
        x_out, x_in, x_ch, x_tip = pipe_layout(side)
        d = np.array([np.sign(x_tip - x_out), 0.0, 0.0])
        for i in range(5):
            ys, yc = pipe_y_stack(i), pipe_y_chamber(i)
            xb = np.linspace(x_in, x_ch, N_BEND)
            center = [(x_out, ys, Z_HP)] + [(x, pipe_y_at(i, side, x), Z_HP) for x in xb] + [(x_tip, yc, Z_HP)]
            A, D = Vector(*center[0]), Vector(*center[-1])
            S = [Vector(*p) for p in center[1:-1]]
            dv = Vector(*d)
            path = Wire([Line(A, S[0]), Spline(*S, tangents=[dv, dv]), Line(S[-1], D)])
            tube = sweep(Plane(origin=A, z_dir=dv) * Circle(HD), path=path)
            tube = tube + Pos(x_tip, yc, Z_HP) * Solid.make_sphere(HD)
            # pé soldado na lateral da câmara (3D vapor chamber): bloco do fundo da câmara até o
            # tubo, encostado na lateral dela
            ja, jb = sorted((x_ch, x_ch + side * g("hp_joint_len")))
            joint = Pos(ja, yc - HD, Z_CP1) * Solid.make_box(jb - ja, 2 * HD, Z_TOP - Z_CP1)
            m = trimesh.util.concatenate([tube_mesh(center, d), box_mesh(ja, jb, yc - HD, yc + HD, Z_CP1, Z_TOP)])
            out.append(([tube, joint], m))
    note(pid, "10 tubos de %.0f mm (heatpipe_diameter), 5 por lado; eixo em z = %.1f, apoiado no topo da câmara e da moldura (%.1f)" % (2 * HD, Z_HP, Z_TOP))
    note(pid, "trajeto: reto pela pilha da ponta (passo %.0f mm), curva em S no plano xy entre a pilha e a borda da câmara (passo %.1f mm sobre a câmara), reto sobre a câmara até %.1f mm do centro, ponta arredondada" % (
        g("hp_pitch_stack"), g("hp_pitch_chamber"), g("hp_center_gap") / 2 + HD))
    note(pid, "pé soldado de %.1f mm na lateral da câmara, de z = %.1f até o tubo; os tubos atravessam as lâminas das pilhas das pontas pelos furos e a pilha central pelos entalhes" % (g("hp_joint_len"), Z_CP1))
    note(pid, "comprimentos por lado: %.1f (bracket) e %.1f (ponta), contra heatpipe_length_per_side = %.0f do CSV (a revisar, como o próprio CSV diz)" % tuple(
        [abs(pipe_layout(s)[3] - pipe_layout(s)[0]) for s in (-1, 1)] + [M("heatpipe_length_per_side")]))
    return out


def build_spring():
    pid = "cooler.leaf_spring"
    ww, wh = M("leaf_spring_window_x") / 2, M("leaf_spring_window_y") / 2
    wx, wy = g("spring_ring_wx"), g("spring_ring_wy")
    t = M("leaf_spring_thickness")
    z1 = M("iface_pcb_back_z")
    z0 = z1 - t
    spring_h, _ = holes8()
    outer = rrect(DCX - ww - wx, DCX + ww + wx, DCY - wh - wy, DCY + wh + wy, 3.0)
    sk = outer
    aw = g("spring_arm_w")
    for hx, hy in spring_h:
        sx, sy = math.copysign(1, hx - DCX), math.copysign(1, hy - DCY)
        yb = DCY + sy * (wh + wy / 2)                 # meio da faixa de cima (ou de baixo) do anel
        # braço em L: a faixa do anel continua em x até o furo e sobe (ou desce) até ele; com o
        # braço em diagonal ele passaria sobre a memória do verso (mem.back) junto aos furos
        sk = sk + rect(*sorted((DCX + sx * (ww + wx / 2), hx + sx * aw / 2)), yb - wy / 2, yb + wy / 2)
        sk = sk + rect(hx - aw / 2, hx + aw / 2, *sorted((yb, hy)))
        sk = sk + Pos(hx, hy) * Circle(g("spring_tab_r"))
    r = g("spring_round")
    sk = offset(offset(sk, r, kind=Kind.ARC), -r, kind=Kind.ARC)      # concordância côncava
    sk = offset(offset(sk, -r, kind=Kind.ARC), r, kind=Kind.ARC)      # cantos convexos
    sk = sk - rrect(DCX - ww, DCX + ww, DCY - wh, DCY + wh, g("spring_window_r"))
    for hx, hy in spring_h:
        sk = sk - Pos(hx, hy) * Circle(g("spring_hole_r"))
    body = ext_z(sk, z0, z1)
    note(pid, "anel em volta da janela de %.0f x %.0f (leaf_spring_window, centrada no die), 4 braços até os furos iface_spring_holes (%.1f x %.1f), orelhas de r = %.1f e furos de r = %.1f" % (
        2 * ww, 2 * wh, M("iface_spring_holes_dx"), M("iface_spring_holes_dy"), g("spring_tab_r"), g("spring_hole_r")))
    note(pid, "chapa plana de %.1f mm de z = %.2f a %.2f (encostada no verso do PCB); a curvatura de uma mola de lâmina não aparece nas fotos e não foi modelada" % (t, z0, z1))
    note(pid, "anel mais estreito em cima e embaixo (%.0f mm) que nos lados (%.0f mm) para não passar sobre a memória do verso" % (wy, wx))
    return body


# ---------------------------------------------------------------------------
# Malha, GLB e STEP
# ---------------------------------------------------------------------------
def to_mesh(shape, tess):
    v, f = shape.tessellate(*tess)
    m = trimesh.Trimesh(np.array([[p.X, p.Y, p.Z] for p in v]), np.array(f), process=False)
    m.merge_vertices(digits_vertex=4)
    m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    return m


def shifted(m, dx):
    v = m.vertices.copy()
    v[:, 0] += dx
    return trimesh.Trimesh(v, m.faces.copy(), process=False)


def to_gltf(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]] / 1000.0


MATERIAL = {   # cor base de viewer/src/materials.json (sRGB), só para quem abre o GLB solto
    "cooler.fins.1": ("aletas.pretas", "#1a1b1d", 0.0, 0.5), "cooler.fins.2": ("aletas.pretas", "#1a1b1d", 0.0, 0.5),
    "cooler.fins.3": ("aletas.pretas", "#1a1b1d", 0.0, 0.5), "cooler.base": ("aluminio.jateado", "#a6a8ab", 1.0, 0.46),
    "cooler.vapor_chamber": ("cobre.niquelado", "#c3bcb2", 1.0, 0.3), "cooler.heatpipes": ("cobre.niquelado", "#c3bcb2", 1.0, 0.3),
    "cooler.leaf_spring": ("aco.mola", "#34363a", 1.0, 0.38),
}


def srgb_to_lin(hexs):
    c = [int(hexs[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def write_glb(path, pid, nodes_spec, root_extras):
    """nodes_spec: lista de (nome, extras, malha ou None, índice do pai ou None)."""
    nodes, meshes, accs, views = [], [], [], []
    buf = bytearray()

    def add_view(data, target):
        while len(buf) % 4:
            buf.append(0)
        views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": data.nbytes, "target": target})
        buf.extend(data.tobytes())
        return len(views) - 1

    for name, extras, mesh, parent in nodes_spec:
        n = {"name": name, "extras": extras}
        if mesh is not None:
            sm = trimesh.graph.smooth_shade(mesh, angle=math.radians(CREASE_DEG))
            V = to_gltf(sm.vertices).astype("<f4")
            N = (to_gltf(sm.vertex_normals) * 1000.0).astype("<f4")
            F = np.asarray(sm.faces).astype("<u4").reshape(-1)
            iv, i_n, i_f = add_view(V, 34962), add_view(N, 34962), add_view(F, 34963)
            accs.append({"bufferView": iv, "componentType": 5126, "count": len(V), "type": "VEC3",
                         "min": V.min(axis=0).tolist(), "max": V.max(axis=0).tolist()})
            accs.append({"bufferView": i_n, "componentType": 5126, "count": len(N), "type": "VEC3"})
            accs.append({"bufferView": i_f, "componentType": 5125, "count": len(F), "type": "SCALAR"})
            meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": len(accs) - 3, "NORMAL": len(accs) - 2},
                                                         "indices": len(accs) - 1, "material": 0, "mode": 4}]})
            n["mesh"] = len(meshes) - 1
        if extras.get("anchor"):
            n["translation"] = [float(t) for t in to_gltf([extras["pos_cad"]])[0]]
        nodes.append(n)
        if parent is not None:
            nodes[parent].setdefault("children", []).append(len(nodes) - 1)
    mname, hexs, met, rough = MATERIAL[pid]
    gltf = {
        "asset": {"version": "2.0", "generator": "harness/parts/cooler.py", "extras": root_extras},
        "scene": 0, "scenes": [{"name": nodes_spec[0][0], "nodes": [0]}], "nodes": nodes, "meshes": meshes,
        "materials": [{"name": mname, "pbrMetallicRoughness": {"baseColorFactor": srgb_to_lin(hexs) + [1.0],
                                                               "metallicFactor": met, "roughnessFactor": rough}}],
        "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}],
    }
    js = json.dumps(gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    js += b" " * (-len(js) % 4)
    binary = bytes(buf) + b"\0" * (-len(buf) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binary)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binary), 0x004E4942) + binary)


# ---------------------------------------------------------------------------
# Conferências
# ---------------------------------------------------------------------------
def closed(m):
    return bool(m.is_watertight and m.is_winding_consistent and m.volume > 0)


def bvh(mesh):
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils.bvhtree import BVHTree
    return BVHTree.FromPolygons(np.asarray(mesh.vertices).tolist(), np.asarray(mesh.faces).tolist(), epsilon=0.0)


def anchor_dist(mesh, pos):
    import integrate as I
    import bpy  # noqa: F401
    from mathutils import Vector as V3
    t = bvh(mesh)
    if I.inside_mesh(t, [pos])[0]:
        return 0.0
    return float(t.find_nearest(V3(pos))[3])


def overlap_depth(a, b, n=20000):
    """Maior profundidade de um ponto da superfície de a dentro de b (e vice-versa)."""
    import integrate as I
    import bpy  # noqa: F401
    from mathutils import Vector as V3
    best = 0.0
    for x, y in ((a, b), (b, a)):
        lo, hi = y.bounds
        lo2, hi2 = x.bounds
        if np.any(hi2 < lo - 0.5) or np.any(lo2 > hi + 0.5):
            continue
        ty = bvh(y)
        p = np.vstack([x.vertices, trimesh.sample.sample_surface(x, n, seed=7)[0]])
        p = p[np.all((p >= lo - 1e-6) & (p <= hi + 1e-6), axis=1)]
        if not len(p):
            continue
        p = p[:: max(1, len(p) // 3000)]
        ins = I.inside_mesh(ty, p)
        if ins.any():
            best = max(best, max(ty.find_nearest(V3(q))[3] for q in p[ins]))
    return best


FEATURE_PROV = {
    "cooler.fins.1": {
        "existência, cor preta e orientação das lâminas (empilhadas ao longo de x)": "derived (gn-02, gn-29, gn-31; pny/back)",
        "faixa em x (do fim de io.board até o PCB), altura e profundidade": "derived (CSV) e inferred (fin_stack_end_depth_z)",
        "passo e espessura": "inferred (fin_pitch, fin_thickness)",
        "cantos da ponta acompanhando a carcaça": "derived (placa irmã, wccftech-cooler-3 e -6; contorno da carcaça do CSV)",
        "5 furos dos tubos": "derived (placa irmã, wccftech-cooler-4); posição em z inferred",
    },
    "cooler.fins.3": {
        "pilha central sob as janelas do X e sob a borda superior do PCB": "derived (gn-21, gn-26, gn-30, gn-34)",
        "recorte em X, placa lisa do X e degraus": "derived (forma: wccftech-cooler-3 e -4, placa irmã; degraus também em gn-26); alturas inferred",
        "entalhes dos tubos": "inferred",
    },
    "cooler.base": {
        "moldura preta com face de contato embutida e colunas roscadas": "derived (gn-32, gn-34, gn-39; wccftech-cooler-1 e -5)",
        "contorno e face de contato": "derived (CSV)",
        "espessuras e raios": "inferred",
    },
    "cooler.vapor_chamber": {"existência": "derived (placa irmã; Jon Peddie)", "forma e espessura": "inferred"},
    "cooler.heatpipes": {
        "contagem (10, 5 por lado)": "derived (PCGH; 5 pontas por lado em wccftech-cooler-1, -3 e -4)",
        "passo na pilha": "derived (wccftech-cooler-4)",
        "trajeto, curva em S, pé soldado, altura em z": "inferred",
    },
    "cooler.leaf_spring": {
        "anel com janela, 4 braços e 4 furos": "derived (gn-29, gn-32, desta placa)",
        "furos e janela": "derived (CSV)",
        "larguras, raios e espessura": "inferred",
    },
}
FEATURE_PROV["cooler.fins.2"] = FEATURE_PROV["cooler.fins.1"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    root_extras = {"units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z", "origin": "card.envelope_min",
                   "map": "gltf = (x, z, -y) / 1000"}
    report = {"guess_values": {k: {"value": v[0], "provenance": v[1], "note": v[2]} for k, v in G.items()}, "parts": {}}
    meshes, steps, inst = {}, {}, {}

    # pilhas das pontas: uma lâmina por forma, copiada ao longo de x
    for n in (1, 2):
        pid = "cooler.fins.%d" % n
        fins, cache = build_end_stack(n)
        tm = {k: to_mesh(s, TESS["fin"]) for k, (_, s) in cache.items()}
        meshes[pid] = trimesh.util.concatenate([shifted(tm[k], x) for x, k in fins])
        steps[pid] = [Pos(x, 0, 0) * cache[k][1] for x, k in fins]
        report.setdefault("counts", {})[pid] = len(fins)
    # pilha central
    fins3, xplate = build_center_stack()
    parts3 = [fin_solid(sk, x, T_FIN) for x, sk in fins3]
    meshes["cooler.fins.3"] = trimesh.util.concatenate([to_mesh(s, TESS["fin"]) for s in parts3] + [to_mesh(xplate, TESS["body"])])
    steps["cooler.fins.3"] = parts3 + [xplate]
    report["counts"]["cooler.fins.3"] = len(fins3)
    # base, câmara, tubos, mola
    base_frame, base_plate = build_base()
    meshes["cooler.base"] = trimesh.util.concatenate([to_mesh(base_frame, TESS["body"]), to_mesh(base_plate, TESS["body"])])
    steps["cooler.base"] = [base_frame, base_plate]
    ch = build_chamber()
    meshes["cooler.vapor_chamber"] = to_mesh(ch, TESS["body"])
    steps["cooler.vapor_chamber"] = [ch]
    pipes = build_pipes()
    inst["cooler.heatpipes"] = [m for _, m in pipes]
    meshes["cooler.heatpipes"] = trimesh.util.concatenate(inst["cooler.heatpipes"])
    steps["cooler.heatpipes"] = [Compound(sol, label="cooler.heatpipes.%d" % (k + 1)) for k, (sol, _) in enumerate(pipes)]
    sp = build_spring()
    meshes["cooler.leaf_spring"] = to_mesh(sp, TESS["body"])
    steps["cooler.leaf_spring"] = [sp]

    all_ok = True
    total = 0
    for pid in IDS:
        p = PARTS[pid]
        m = meshes[pid]
        bodies = inst.get(pid, [m])
        ok_closed = all(closed(b) for b in bodies) and bool(m.is_watertight and m.is_winding_consistent)
        ntri = int(len(m.faces))
        total += ntri
        anchors = []
        for a in p["anchors"]:
            d = anchor_dist(m, a["pos"])
            anchors.append({"anchor": a["id"], "dist_mm": round(d, 3), "ok": d <= TOL_ANCHOR})
        extras = {
            "id": pid, "stage": p["stage"], "fidelity": p["fidelity"], "exists_provenance": p["exists_provenance"],
            "shape_provenance": p["shape_provenance"], "shape_provenance_features": FEATURE_PROV[pid],
            "guess": True, "guess_notes": NOTES[pid], "blockout": False, "units_cad": "mm", "up_cad": "+Z",
            "origin": "card.envelope_min", "referencial": "face B em z = 0, face A (ventiladores) em z = card_thickness",
            "explode_cad": p["explode"],
        }
        if "count" in p:
            extras["count_assembly"] = p["count"]["value"]
            extras["count_provenance"] = p["count"]["provenance"]
        if pid in report["counts"]:
            extras["count_model"] = report["counts"][pid]
        if pid == "cooler.base":
            extras["surface_detail"] = {"marca_da_pasta_e_datamatrix": {"plano_z_cad_mm": ZC, "centro_cad_mm": [DCX, DCY],
                                                                         "face_mm": [2 * VX, 2 * VY], "ref": ["gn-34", "gn-32"],
                                                                         "passo": "Blender"}}
        spec = []
        if pid in inst:
            spec.append((pid, extras, None, None))
            for k, b in enumerate(inst[pid], 1):
                spec.append(("%s.%d" % (pid, k), {"instance_of": pid, "instance": k, "stage": p["stage"],
                                                  "side": "bracket" if k <= 5 else "ponta", "shape_provenance": "inferred", "guess": True}, b, 0))
        else:
            spec.append((pid, extras, m, None))
        for a in p["anchors"]:
            spec.append((a["id"], {"anchor": True, "part": pid, "pos_cad": a["pos"]}, None, 0))
        glb = OUT / ("%s.glb" % pid)
        write_glb(glb, pid, spec, root_extras)
        comp = Compound(steps[pid])
        comp.label = pid
        export_step(comp, str(OUT / ("%s.step" % pid)))
        lo, hi = m.bounds
        ok = ok_closed and all(a["ok"] for a in anchors)
        all_ok &= ok
        report["parts"][pid] = {"triangles": ntri, "bodies": int(m.body_count),
                                "closed": ok_closed, "bbox_min": lo.round(3).tolist(), "bbox_max": hi.round(3).tolist(),
                                "glb_bytes": glb.stat().st_size, "anchors": anchors, "notes": NOTES[pid]}
        print("%-22s %7d triângulos, fechada: %s, caixa (%.2f, %.2f, %.2f) a (%.2f, %.2f, %.2f)" % (
            pid, ntri, "sim" if ok_closed else "NÃO", *lo, *hi))
        for a in anchors:
            print("    %-34s dist %.2f mm %s" % (a["anchor"], a["dist_mm"], "OK" if a["ok"] else "LONGE"))

    # sobreposições entre as peças do cooler (as dos tubos com as aletas são de propósito)
    expected = {frozenset(("cooler.fins.1", "cooler.heatpipes")), frozenset(("cooler.fins.2", "cooler.heatpipes")),
                frozenset(("cooler.fins.3", "cooler.heatpipes"))}
    pairs = []
    for i, a in enumerate(IDS):
        for b in IDS[i + 1:]:
            d = max(overlap_depth(ma, mb) for ma in inst.get(a, [meshes[a]]) for mb in inst.get(b, [meshes[b]]))
            pairs.append({"a": a, "b": b, "mm": round(d, 3), "esperada": frozenset((a, b)) in expected})
            bad = d > TOL_OVERLAP and frozenset((a, b)) not in expected
            all_ok &= not bad
            if d > 0.05:
                print("    sobreposição %-20s x %-20s %.2f mm%s" % (a, b, d, " (esperada)" if frozenset((a, b)) in expected else (" ACIMA" if bad else "")))
    report["internal_overlaps"] = pairs
    report.update(REPORT_EXTRA)
    report["triangles_total"] = total
    report["triangle_budget"] = TRI_BUDGET
    report["csv_keys_used"] = sorted(USED)
    report["neighbors_used"] = {"power.connector": [CONN[0].round(2).tolist(), CONN[1].round(2).tolist()],
                                "io.aux_header": [AUX[0].round(2).tolist(), AUX[1].round(2).tolist()]}
    all_ok &= total <= TRI_BUDGET
    print("Triângulos no total: %d (orçamento %d) %s" % (total, TRI_BUDGET, "OK" if total <= TRI_BUDGET else "ACIMA"))
    print("Lâminas: %s" % ", ".join("%s %d" % kv for kv in report["counts"].items()))
    (OUT / "cooler-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Relatório: %s" % (OUT / "cooler-report.json").relative_to(HARNESS.parent))
    print("Resultado (malhas fechadas, âncoras, orçamento, sobreposições internas): %s" % ("OK" if all_ok else "FALHA"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
