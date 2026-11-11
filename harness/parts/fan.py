#!/usr/bin/env python3
"""Ventiladores da RTX PRO 6000 Blackwell Workstation Edition (F3).

Gera, em build123d, os dois ventiladores da face A com os ids e as âncoras do assembly:

  cooler.fan.N          cubo do rotor (copo, anel de reforço, ranhura e tampa) e suporte do
                        motor atrás do rotor (prato, quatro braços com ressalto e parafuso)
  cooler.fan.N.blade    as 7 pás (fan_blade_count), uma instância por pá (nós
                        cooler.fan.N.blade.1 a .7), cada uma um sólido fechado

Pá: loft de seções aerodinâmicas finas sobre cilindros de raio r, aparado entre o raio da
raiz (cubo menos a sobreposição) e o raio do rotor. Em cada raio: posição angular da borda de
ataque medida em pny/front (varredura), extensão angular projetada (vão escuro medido entre as
pás), altura axial (passo quase constante, o que dá a torção), arqueamento e espessura com
borda de ataque redonda e borda de fuga fina. A borda de ataque fica do lado anti-horário
(visto de +z) e em z alto, a borda de fuga do lado horário e em z baixo: o ar entra pela face A
e sai para a face B; o giro que isso implica (anti-horário visto de +z) é dedução (Q12).

Sem anel externo nas pontas: em gn-26, gn-02, sr-4 e club386 as pontas terminam livres e o
anel que aparece é o da carcaça (frame.shroud). Usinagem concêntrica da tampa: não é geometria
(sulcos de centésimos de milímetro estourariam o orçamento); fica para textura anisotrópica no
passo do Blender, com centro e raio em extras.surface_detail.

Contrato: CAD em mm, Z para cima, origem em card.envelope_min, face A (ventiladores) em
z = card_thickness, face B em z = 0 (ARCHITECTURE.md, 7.6). O GLB sai em metros com Y para
cima, (x, y, z) -> (x, z, -y) / 1000, com as coordenadas absolutas gravadas nos vértices (sem
transformação de nó), como frame.py; harness/parts/integrate.py troca as caixas do blockout
por estas malhas. Medidas do CSV pela chave; o que não tem linha está em G, com a procedência.

Uso:   python3 -I harness/parts/fan.py
Saídas: harness/build/parts/cooler.fan.{1,2}.glb e .step (cubo, suporte e as pás como nós
        filhos), cooler.fan.{1,2}.blade.glb e .step (as 7 instâncias, que o integrate.py lê),
        harness/build/parts/fan-report.json
"""
import csv
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import (Compound, Pos, Rot, Solid, Spline, Vector, Wire, export_step, fillet)

HARNESS = Path(__file__).resolve().parent.parent
ASSEMBLY = HARNESS / "design" / "assembly.json"
MEASURES = HARNESS / "design" / "measurements.csv"
OUT = HARNESS / "build" / "parts"

# Tolerâncias das conferências e da malha (não são medidas da peça)
TOL_ANCHOR = 2.0       # mm, âncora fora da peça
TOL_OVERLAP = 0.5      # mm, interferência aceita pelo integrate.py
TESS_BLADE = (0.06, 0.38)   # desvio linear (mm) e angular (rad) da tesselagem das pás
TESS_HUB = (0.03, 0.20)
TRI_BUDGET = 60_000    # triângulos por ventilador (cubo, suporte e 7 pás)
CREASE_DEG = 30.0      # quebra das normais suaves (o mesmo do integrate.py)

# ---------------------------------------------------------------------------
# Valores sem linha no CSV: (valor, procedência, nota)
# ---------------------------------------------------------------------------
G = {
    # varredura e planta da pá, medidas nesta tarefa em pny/front (2,2716 px/mm, calibração de
    # frame_remeasure.py); ângulos em graus, anti-horário visto de +z
    "le_sweep_r": ((22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56), "derived",
                   "raios em que a borda de ataque foi medida (maior queda de brilho no sentido anti-horário, 7 pás, pny/front)"),
    "le_sweep_deg": ((0.0, 1.58, 3.34, 5.16, 7.01, 9.00, 10.88, 12.74, 14.55, 16.12, 17.73, 19.14, 20.54, 21.89, 23.29, 24.76, 26.36, 28.15), "derived",
                     "posição angular da borda de ataque relativa à de r = 22, média dos dois ventiladores (diferença entre eles até 0,17 grau; dispersão entre pás 0,2 a 0,8 grau)"),
    "phase_deg": ((14.40, 13.50), "derived",
                  "ângulo da borda de ataque da pá 1 em r = 22 no render (posição do rotor na foto, sem significado físico; mantida para a comparação)"),
    "gap_deg": (11.8, "derived",
                "vão projetado entre pás vistas de frente (extensão projetada da pá = 360/7 menos o vão). Correção de 2026-11-11 (achado 5 do visual-qa): "
                "a faixa escura de pny/front (12,9 a 13,6 graus, limiar de 12 %; valor anterior 13,2) inclui a borda de fuga da pá seguinte na sombra e é "
                "só um teto do vão; em gn-02 (foto, aletas visíveis pelos vãos) a fração do disco em que o interior aparece, medida pela textura das aletas "
                "na mesma escala do render do modelo, fica 0,03 a 0,05 abaixo da do modelo de 13,2 graus: vão real de cerca de 11,3 a 12,3 graus"),
    "tip_round_start": (46.0, "derived", "raio a partir do qual o canto da borda de fuga começa a arredondar (pny/front: o vão escuro alarga de r = 46 em diante)"),
    "tip_round_k": (0.02, "derived",
                    "coeficiente do encurtamento da corda angular perto da ponta, (r - tip_round_start)^2 graus por mm^2. Antes 0,057, ajustado ao vão "
                    "escuro de pny/front (14,4 graus em r = 50, 17,8 em 55); em gn-02 o vão com aletas visíveis quase não alarga na faixa de r = 50 a 56 "
                    "(fração 0,29 a 0,33 contra 0,29 a 0,31 no meio da pá): o alargamento de pny/front era sombra; mantido um arredondamento pequeno do canto"),
    # perfil axial (sem vista lateral: palpite dentro do orçamento fan_axial_depth)
    "hub_top_recess": (0.8, "inferred", "o anel do cubo fica 0,8 mm abaixo da face A; nos renders de três quartos o cubo parece rente à face, sem cota"),
    "le_z_below_face": (1.4, "inferred", "a borda de ataque fica 1,4 mm abaixo da face A, dentro da boca da chapa (shroud_face_a_plate_thickness)"),
    "blade_h_root": (10.8, "inferred", "altura axial da pá na raiz (da borda de ataque à de fuga); com a corda projetada isso dá cerca de 39 graus de passo na raiz"),
    "blade_h_tip": (10.0, "inferred", "altura axial na ponta; passo quase constante (hélice), cerca de 17 graus na ponta: torção de cerca de 22 graus"),
    "camber_root": (0.05, "inferred", "flecha do arqueamento na raiz, fração da corda; convexo para +z (lado de sucção, da entrada de ar)"),
    "camber_tip": (0.035, "inferred", "flecha do arqueamento na ponta, fração da corda"),
    "t_root": (2.0, "inferred", "espessura máxima da pá na raiz; gn-26 mostra raiz grossa, sem cota"),
    "t_tip": (1.1, "inferred", "espessura máxima da pá na ponta"),
    "t_te": (0.35, "inferred", "espessura da borda de fuga"),
    "root_embed": (0.3, "inferred", "a raiz entra 0,3 mm no cubo, para a junção ficar fechada sem passar da tolerância de interferência do integrate.py (0,5)"),
    # cubo: proporções de rtx5090/club386 (placa irmã, derived) e de pny/front
    "cap_r": (18.1, "derived", "raio da tampa usinada: 145 de 160 px do raio do cubo em club386 (RTX 5090 FE, placa irmã)"),
    "groove_r": (19.4, "derived", "anel escuro entre a tampa e o anel de reforço até r = 19,4 (club386, placa irmã; o mesmo aparece em gn-26 e pny/front)"),
    "groove_depth": (0.4, "inferred", "profundidade da ranhura escura"),
    "cap_drop": (0.1, "inferred", "a tampa fica 0,1 mm abaixo do anel de reforço"),
    "rim_fillet": (0.4, "inferred", "arredondamento da aresta externa do anel de reforço"),
    "cap_fillet": (0.15, "inferred", "arredondamento da borda da tampa"),
    # suporte do motor atrás do rotor
    "stator_gap": (0.3, "inferred", "folga axial do suporte para o rotor e para as aletas (fins em z <= card_thickness - layer_end_fan_ring)"),
    "stator_plate_r": (21.0, "inferred", "raio do prato do motor atrás do cubo (escondido pelo rotor)"),
    "boss_r_pos": (25.0, "derived", "raio dos ressaltos com parafuso vistos entre as pás: cerca de 23 a 26 mm (gn-02, ventilador 1) e 25 a 26 (club386, placa irmã)"),
    "boss_ang_deg": ((25.0, -25.0, 155.0, 205.0), "derived",
                     "quatro ressaltos em dois pares a 50 graus: gn-02 mostra dois a 140 e 192 graus e club386 dois a 27 e -23 (separação 50 a 52); adotados pares simétricos em 0 e 180 graus (incerteza de cerca de 10 graus pela perspectiva)"),
    "boss_rad": (2.8, "derived", "raio do ressalto: cerca de 15 px em gn-02 (5,4 px/mm)"),
    "screw_head_r": (1.6, "inferred", "raio da cabeça do parafuso"),
    "screw_head_h": (0.5, "inferred", "altura da cabeça do parafuso"),
    "arm_w": (4.0, "inferred", "largura dos braços do prato até os ressaltos (não vistos: escondidos pelas pás)"),
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

T = M("card_thickness")
FAN_X = (M("fan1_center_from_bracket_end"), M("fan2_center_from_bracket_end"))
FAN_Y = M("iface_fan_center_y")
R_TIP = M("fan_rotor_diameter") / 2
R_HUB = M("fan_hub_diameter") / 2
DEPTH = M("fan_axial_depth")
NB = int(M("fan_blade_count"))
assert NB == PARTS["cooler.fan.1.blade"]["count"]["value"] == PARTS["cooler.fan.2.blade"]["count"]["value"], \
    "contagem de pás do CSV diferente da do assembly"
PITCH = 360.0 / NB
Z0 = T - DEPTH                                   # fundo do rotor
Z_HUB = T - g("hub_top_recess")                  # topo do anel do cubo
Z_LE = T - g("le_z_below_face")                  # borda de ataque
Z_FINS = T - M("layer_end_fan_ring")             # topo das aletas das pontas (orçamento)
R_ROOT = R_HUB - g("root_embed")

_SW = np.polyfit(np.array(g("le_sweep_r"), float), np.array(g("le_sweep_deg"), float), 3)


def sweep(r):
    """Posição angular da borda de ataque (graus) relativa à de r = 22."""
    return float(np.polyval(_SW, r))


def span_deg(r):
    """Extensão angular projetada da pá (da borda de fuga à de ataque)."""
    d = PITCH - g("gap_deg")
    if r > g("tip_round_start"):
        d -= g("tip_round_k") * (r - g("tip_round_start")) ** 2
    return d


def lerp_r(a, b, r):
    w = min(max((r - R_ROOT) / (R_TIP - R_ROOT), 0.0), 1.0)
    return a + (b - a) * w


# ---------------------------------------------------------------------------
# Pá
# ---------------------------------------------------------------------------
N_SEC = 26      # pontos por lado da seção (não é medida)


def section_pts(r):
    """Seção da pá no raio r, em (s, z) com s = r * theta (mm de arco); u = 0 na borda de
    ataque, 1 na de fuga. Devolve a lista fechada (extradorso da fuga à ataque, intradorso da
    ataque à fuga)."""
    th_le = math.radians(sweep(r))
    dth = math.radians(span_deg(r))
    h = lerp_r(g("blade_h_root"), g("blade_h_tip"), r)
    s_le, z_le = r * th_le, Z_LE
    cs = r * dth
    L = math.hypot(cs, h)
    d = np.array([-cs, -h]) / L                  # da ataque para a fuga
    n = np.array([-h, cs]) / L                   # normal para +z (lado de sucção)
    u = (1 - np.cos(np.linspace(0, math.pi, N_SEC))) / 2
    cam = lerp_r(g("camber_root"), g("camber_tip"), r) * L
    mean = np.array([s_le, z_le])[None] + u[:, None] * L * d[None] + (4 * cam * u * (1 - u))[:, None] * n[None]
    # tangente e normal da linha média
    tg = np.gradient(mean, axis=0)
    tg /= np.linalg.norm(tg, axis=1)[:, None]
    nn = np.c_[-tg[:, 1], tg[:, 0]]
    nn *= np.sign(nn[:, 1:2] + 1e-12)
    tmax = lerp_r(g("t_root"), g("t_tip"), r)
    naca = (1.4845 * np.sqrt(u) - 0.63 * u - 1.758 * u ** 2 + 1.4215 * u ** 3 - 0.5075 * u ** 4)
    thick = (tmax - g("t_te")) * naca / naca.max() * (1 - u * 0.0) + g("t_te") * np.sqrt(u)
    up = mean + nn * thick[:, None] / 2
    lo = mean - nn * thick[:, None] / 2
    return np.vstack([up[::-1], lo[1:]])


def section_wire(r, planar=False):
    sz = section_pts(r)
    if planar:
        # seção de ponta (fora da faixa aparada): plana, perpendicular ao raio do meio da corda
        am = math.radians(sweep(r) - span_deg(r) / 2)
        c, sn = math.cos(am), math.sin(am)
        P = [(r * c - (s - r * am) * sn, r * sn + (s - r * am) * c, z) for s, z in sz]
    else:
        P = [(r * math.cos(s / r), r * math.sin(s / r), z) for s, z in sz]
    pts = [Vector(*p) for p in P] + [Vector(*P[0])]
    return Wire([Spline(*pts)])


SEC_R = (R_ROOT - 3.7, R_ROOT - 1.7, R_ROOT, 23.0, 26.5, 30.0, 34.0, 38.0, 42.0, 46.0, 49.5, 52.5, 55.0, R_TIP,
         R_TIP + 1.6, R_TIP + 3.6)


def build_blade():
    """Pá no referencial local do ventilador (centro na origem do plano xy), com a borda de
    ataque em r = 22 no ângulo 0."""
    secs = [section_wire(r, planar=(i in (0, len(SEC_R) - 1))) for i, r in enumerate(SEC_R)]
    loft = Solid.make_loft(secs)
    ann = Pos(0, 0, Z0 - 2) * (Solid.make_cylinder(R_TIP, DEPTH + 4) - Solid.make_cylinder(R_ROOT, DEPTH + 4))
    b = loft & ann
    sol = b.solids()
    assert len(sol) == 1 and sol[0].is_valid, "pá inválida"
    return sol[0]


# ---------------------------------------------------------------------------
# Cubo e suporte
# ---------------------------------------------------------------------------
def build_hub():
    cup = Pos(0, 0, Z0) * Solid.make_cylinder(R_HUB, Z_HUB - Z0)
    cup = fillet(cup.edges().filter_by(lambda e: e.center().Z > Z_HUB - 1e-3 and e.radius > R_HUB - 0.01), g("rim_fillet"))
    gd = g("groove_depth")
    cup = cup - Pos(0, 0, Z_HUB - gd) * (Solid.make_cylinder(g("groove_r"), gd + 1) - Solid.make_cylinder(g("cap_r"), gd + 1))
    cup = cup - Pos(0, 0, Z_HUB - g("cap_drop")) * Solid.make_cylinder(g("cap_r"), 1)
    try:
        cup = fillet(cup.edges().filter_by(lambda e: abs(e.center().Z - (Z_HUB - g("cap_drop"))) < 1e-3
                                           and abs(e.radius - g("cap_r")) < 0.01), g("cap_fillet"))
    except Exception:
        pass
    return cup


def build_stator():
    z0 = Z_FINS + g("stator_gap")
    z1 = Z0 - g("stator_gap")
    zh = z1 - g("screw_head_h")                  # topo do prato e dos ressaltos
    plate = Pos(0, 0, z0) * Solid.make_cylinder(g("stator_plate_r"), zh - z0)
    for a in g("boss_ang_deg"):
        arm = Pos(0, 0, z0) * Rot(0, 0, a) * Pos(0, -g("arm_w") / 2, 0) * Solid.make_box(g("boss_r_pos"), g("arm_w"), zh - z0)
        boss = Pos(0, 0, z0) * Rot(0, 0, a) * Pos(g("boss_r_pos"), 0, 0) * Solid.make_cylinder(g("boss_rad"), zh - z0)
        head = Pos(0, 0, zh - 0.05) * Rot(0, 0, a) * Pos(g("boss_r_pos"), 0, 0) * Solid.make_cylinder(g("screw_head_r"), g("screw_head_h") + 0.05)
        plate = plate + arm + boss + head
    return plate


# ---------------------------------------------------------------------------
# Malha e GLB
# ---------------------------------------------------------------------------
def to_mesh(shape, tess):
    v, f = shape.tessellate(*tess)
    m = trimesh.Trimesh(np.array([[p.X, p.Y, p.Z] for p in v]), np.array(f), process=False)
    m.merge_vertices(digits_vertex=3)
    m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    return m


def place(mesh, ang_deg, cx, cy):
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)
    v = mesh.vertices
    out = np.c_[c * v[:, 0] - s * v[:, 1] + cx, s * v[:, 0] + c * v[:, 1] + cy, v[:, 2]]
    return trimesh.Trimesh(out, mesh.faces.copy(), process=False)


def to_gltf(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]] / 1000.0


MATERIALS = [
    {"name": "rotor", "pbrMetallicRoughness": {"baseColorFactor": [0.11, 0.115, 0.125, 1.0], "metallicFactor": 0.0, "roughnessFactor": 0.62}},
]


def write_glb(path, nodes_spec, root_extras):
    """nodes_spec: lista de (nome, extras, malha ou None, índice do pai ou None). As malhas
    saem com normais suaves (quebra acima de CREASE_DEG)."""
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
        nodes.append(n)
        if parent is not None:
            nodes[parent].setdefault("children", []).append(len(nodes) - 1)
    for k, (name, extras, mesh, parent) in enumerate(nodes_spec):
        if extras.get("anchor"):
            nodes[k]["translation"] = [float(t) for t in to_gltf([extras["pos_cad"]])[0]]
    gltf = {
        "asset": {"version": "2.0", "generator": "harness/parts/fan.py", "extras": root_extras},
        "scene": 0, "scenes": [{"name": nodes_spec[0][0], "nodes": [0]}], "nodes": nodes, "meshes": meshes,
        "materials": MATERIALS, "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}],
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
    return BVHTree.FromPolygons(mesh.vertices.tolist(), mesh.faces.tolist(), epsilon=0.0)


def inside(tree, pts):
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils import Vector as V3
    dirs = [V3((0.31, 0.52, 0.79)).normalized(), V3((-0.67, 0.21, 0.71)).normalized(), V3((0.13, -0.91, 0.39)).normalized()]
    out = np.zeros(len(pts), bool)
    for i, p in enumerate(pts):
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
        out[i] = votes >= 2
    return out


def overlap_depth(a, b, n=20000):
    """Maior profundidade de um ponto da superfície de a dentro de b (e vice-versa)."""
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils import Vector as V3
    best = 0.0
    for x, y in ((a, b), (b, a)):
        ty = bvh(y)
        p = np.vstack([x.vertices, trimesh.sample.sample_surface(x, n, seed=7)[0]])
        lo, hi = y.bounds
        p = p[np.all((p >= lo - 1e-6) & (p <= hi + 1e-6), axis=1)]
        if not len(p):
            continue
        p = p[:: max(1, len(p) // 4000)]
        ins = inside(ty, p)
        if ins.any():
            best = max(best, max(ty.find_nearest(V3(q))[3] for q in p[ins]))
    return best


def min_gap(a, b, n=6000):
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils import Vector as V3
    tb = bvh(b)
    p = np.vstack([a.vertices, trimesh.sample.sample_surface(a, n, seed=7)[0]])
    return float(min(tb.find_nearest(V3(q))[3] for q in p[:: max(1, len(p) // 6000)]))


def geometry_table():
    """Números da pá por raio: posição da borda de ataque, corda angular, passo (ângulo da corda
    com o plano de giro), corda e espessura."""
    rows = []
    for r in (R_ROOT, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, R_TIP):
        dth = span_deg(r)
        h = lerp_r(g("blade_h_root"), g("blade_h_tip"), r)
        cs = r * math.radians(dth)
        rows.append({"r": round(r, 2), "borda_de_ataque_deg": round(sweep(r), 2), "corda_angular_deg": round(dth, 2),
                     "corda_mm": round(math.hypot(cs, h), 2), "altura_axial_mm": round(h, 2),
                     "passo_deg": round(math.degrees(math.atan2(h, cs)), 1),
                     "espessura_max_mm": round(lerp_r(g("t_root"), g("t_tip"), r), 2)})
    return rows


FEATURE_PROV = {
    "cooler.fan": {
        "centro, diâmetro do cubo, profundidade axial": "derived (CSV) e inferred (fan_axial_depth)",
        "anel de reforço, ranhura e tampa do cubo": "derived (proporções de club386, placa irmã; pny/front, gn-26); alturas inferred",
        "usinagem concêntrica da tampa": "textura do passo do Blender (não é geometria)",
        "suporte do motor: ressaltos com parafuso": "derived (gn-02; club386, placa irmã); posição angular com incerteza de 10 graus",
        "suporte do motor: prato e braços": "inferred (escondidos pelo rotor)",
    },
    "cooler.fan.blade": {
        "contagem (7)": "derived (CSV fan_blade_count; assembly count)",
        "varredura da borda de ataque": "derived (pny/front, nesta tarefa)",
        "corda angular projetada e canto arredondado da ponta": "derived (pny/front, nesta tarefa)",
        "raio da ponta, raio da raiz": "inferred (fan_rotor_diameter) e derived (fan_hub_diameter)",
        "altura axial, passo, torção, arqueamento, espessura": "inferred (sem vista lateral)",
        "lado da borda de ataque (z alto, anti-horário) e sentido de giro": "inferred (sombreamento de pny/front; Q12 em aberto)",
        "sem anel nas pontas": "derived (gn-26, gn-02, sr-4, club386)",
    },
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blade_local = build_blade()
    hub_local = build_hub()
    stator_local = build_stator()
    m_blade = to_mesh(blade_local, TESS_BLADE)
    m_hub = to_mesh(hub_local, TESS_HUB)
    m_stator = to_mesh(stator_local, TESS_HUB)
    geo = geometry_table()
    report = {"guess_values": {k: {"value": v[0], "provenance": v[1], "note": v[2]} for k, v in G.items()},
              "blade_geometry": geo, "parts": {}}
    all_ok = True
    root_extras = {"units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z", "origin": "card.envelope_min",
                   "map": "gltf = (x, z, -y) / 1000"}
    print("Pá por raio (r, borda de ataque, corda angular, corda, passo, espessura):")
    for row in geo:
        print("    r %5.2f  ataque %6.2f  corda %5.2f graus  %5.2f mm  passo %4.1f graus  t %.2f" % (
            row["r"], row["borda_de_ataque_deg"], row["corda_angular_deg"], row["corda_mm"], row["passo_deg"], row["espessura_max_mm"]))

    for n in (1, 2):
        pid, bid = "cooler.fan.%d" % n, "cooler.fan.%d.blade" % n
        p, pb = PARTS[pid], PARTS[bid]
        cx, cy = FAN_X[n - 1], FAN_Y
        phase = g("phase_deg")[n - 1]
        angs = [phase + PITCH * k for k in range(NB)]
        hub = place(trimesh.util.concatenate([m_hub, m_stator]), 0.0, cx, cy)
        blades = [place(m_blade, a, cx, cy) for a in angs]
        notes = [
            "7 pás de perfil arqueado (borda de ataque redonda, borda de fuga de %.2f mm), varredura medida em pny/front (%.1f graus da raiz à ponta), torção de %.0f graus (passo %.0f na raiz e %.0f na ponta, palpite)" % (
                g("t_te"), sweep(R_TIP) - sweep(R_ROOT), geo[0]["passo_deg"] - geo[-1]["passo_deg"], geo[0]["passo_deg"], geo[-1]["passo_deg"]),
            "sem anel nas pontas das pás: o anel visível nas fotos é o da carcaça",
            "borda de ataque do lado anti-horário (visto de +z) e em z alto; giro anti-horário visto de +z por dedução (Q12)",
            "usinagem concêntrica da tampa: textura do passo do Blender (extras.surface_detail)",
            "suporte do motor com 4 ressaltos e parafusos a r = %.0f (dois pares a 50 graus; vistos em gn-02 e club386); prato e braços escondidos, palpite" % g("boss_r_pos"),
            "posição angular das pás igual à do render pny/front (sem significado físico)",
        ]
        extras = {
            "id": pid, "stage": p["stage"], "fidelity": p["fidelity"], "exists_provenance": p["exists_provenance"],
            "shape_provenance": "derived", "shape_provenance_features": FEATURE_PROV["cooler.fan"],
            "guess": True, "guess_notes": notes, "blockout": False, "units_cad": "mm", "up_cad": "+Z",
            "origin": "card.envelope_min", "referencial": "face B em z = 0, face A (ventiladores) em z = card_thickness",
            "explode_cad": p["explode"], "rotation_sense_cad": {"value": "anti-horário visto de +z", "provenance": "inferred"},
            "surface_detail": {"usinagem_concentrica": {"centro_cad_mm": [cx, cy, Z_HUB - g("cap_drop")], "raio_mm": g("cap_r"),
                                                        "tipo": "anisotropia circular (sulcos concêntricos de torno)",
                                                        "passo": "Blender"}},
        }
        bextras = {"id": bid, "stage": pb["stage"], "fidelity": pb["fidelity"], "exists_provenance": pb["exists_provenance"],
                   "shape_provenance": "derived", "shape_provenance_features": FEATURE_PROV["cooler.fan.blade"],
                   "guess": True, "guess_notes": notes[:3], "count": pb["count"]["value"], "count_provenance": pb["count"]["provenance"],
                   "blockout": False, "explode_cad": pb["explode"], "referencial": extras["referencial"]}

        def inst(k):
            return ("%s.%d" % (bid, k + 1), {"instance_of": bid, "instance": k + 1, "stage": pb["stage"],
                                             "angle_deg_cad": round(angs[k] % 360, 3), "shape_provenance": "derived", "guess": True},
                    blades[k])
        # arquivo do ventilador: cubo e suporte no nó do id, pás como nós filhos
        spec = [(pid, extras, hub, None), (bid, bextras, None, 0)]
        spec += [(*inst(k), 1) for k in range(NB)]
        for a in p["anchors"]:
            spec.append((a["id"], {"anchor": True, "part": pid, "pos_cad": a["pos"]}, None, 0))
        write_glb(OUT / ("%s.glb" % pid), spec, root_extras)
        # arquivo das pás (o integrate.py lê as instâncias <id>.1 a .7)
        specb = [(bid, bextras, None, None)] + [(*inst(k), 0) for k in range(NB)]
        write_glb(OUT / ("%s.glb" % bid), specb, root_extras)
        # STEP
        moved = [Pos(cx, cy, 0) * Rot(0, 0, a) * blade_local for a in angs]
        hub_s = Pos(cx, cy, 0) * hub_local
        st_s = Pos(cx, cy, 0) * stator_local
        hub_s.label, st_s.label = "%s.hub" % pid, "%s.stator" % pid
        for k, s in enumerate(moved):
            s.label = "%s.%d" % (bid, k + 1)
        cb = Compound(moved)
        cb.label = bid
        export_step(cb, str(OUT / ("%s.step" % bid)))
        cf = Compound([hub_s, st_s, Compound(moved, label=bid)])
        cf.label = pid
        export_step(cf, str(OUT / ("%s.step" % pid)))

        # conferências
        tri_hub = int(len(hub.faces))
        tri_bl = int(sum(len(b.faces) for b in blades))
        allm = trimesh.util.concatenate([hub] + blades)
        lo, hi = allm.bounds
        pen_hub = overlap_depth(blades[0], place(m_hub, 0.0, cx, cy))
        pen_st = overlap_depth(blades[0], place(m_stator, 0.0, cx, cy))
        gap_bb = min_gap(blades[0], blades[1])
        r_xy = np.hypot(allm.vertices[:, 0] - cx, allm.vertices[:, 1] - cy)
        bl_v = np.vstack([b.vertices for b in blades])
        r_bl = np.hypot(bl_v[:, 0] - cx, bl_v[:, 1] - cy)
        anchors = []
        th = bvh(hub)
        import bpy  # noqa: F401  (carrega mathutils)
        from mathutils import Vector as V3
        for a in p["anchors"]:
            d = 0.0 if inside(th, [a["pos"]])[0] else float(th.find_nearest(V3(a["pos"]))[3])
            anchors.append({"anchor": a["id"], "dist_mm": round(d, 3), "ok": d <= TOL_ANCHOR})
        ok_closed = closed(hub) and all(closed(b) for b in blades) and closed(m_blade)
        checks = {
            "malhas_fechadas": ok_closed,
            "triangulos": {"cubo_e_suporte": tri_hub, "pas": tri_bl, "total": tri_hub + tri_bl, "orcamento": TRI_BUDGET,
                           "ok": tri_hub + tri_bl <= TRI_BUDGET},
            "z": {"min": round(float(lo[2]), 3), "max": round(float(hi[2]), 3), "ok": bool(lo[2] >= Z_FINS - 1e-6 and hi[2] <= T + 1e-6)},
            "raio_das_pas": {"min": round(float(r_bl.min()), 3), "max": round(float(r_bl.max()), 3)},
            "raio_max": round(float(r_xy.max()), 3),
            "pa_no_cubo_mm": round(pen_hub, 3), "pa_no_suporte_mm": round(pen_st, 3),
            "folga_entre_pas_mm": round(gap_bb, 3),
            "ancoras": anchors,
        }
        ok = (ok_closed and checks["triangulos"]["ok"] and checks["z"]["ok"] and pen_hub <= TOL_OVERLAP
              and pen_st <= TOL_OVERLAP and gap_bb > 0.05 and all(a["ok"] for a in anchors) and r_bl.max() <= R_TIP + 0.01)
        checks["ok"] = bool(ok)
        all_ok &= ok
        report["parts"][pid] = checks
        print("\n%s: %d triângulos (cubo e suporte %d, pás %d em %d nós), fechadas: %s" % (
            pid, tri_hub + tri_bl, tri_hub, tri_bl, NB, "sim" if ok_closed else "NÃO"))
        print("    z de %.2f a %.2f; raio das pás %.2f a %.2f (rotor %.2f); pá no cubo %.2f mm, no suporte %.2f; folga entre pás %.2f mm" % (
            lo[2], hi[2], r_bl.min(), r_bl.max(), R_TIP, pen_hub, pen_st, gap_bb))
        for a in anchors:
            print("    %-24s dist %.2f mm %s" % (a["anchor"], a["dist_mm"], "OK" if a["ok"] else "LONGE"))
    report["csv_keys_used"] = sorted(USED)
    (OUT / "fan-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nRelatório: %s" % (OUT / "fan-report.json").relative_to(HARNESS.parent))
    print("Resultado (malhas fechadas, orçamento, z, sobreposições, âncoras): %s" % ("OK" if all_ok else "FALHA"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
