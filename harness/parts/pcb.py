#!/usr/bin/env python3
"""PCB principal e componentes da RTX PRO 6000 Blackwell Workstation Edition (F3).

Gera, em build123d, as peças do estágio E7 que ficam no PCB principal, com os ids e as
âncoras do assembly, a partir da tabela harness/parts/pcb/layout.csv (pcb_layout.py):

  pcb.main          contorno medido (rebaixo da borda dos contatos, corte em V do canto do
                    conector), espessura do CSV, 4 furos da mola e 4 furos cobreados de canto
                    com anel nas duas faces
  gpu.package       esferas e underfill, substrato, moldura de reforço com janela, die e os
                    capacitores do substrato
  mem.front         16 chips GDDR7 na frente (instâncias mem.front.1 a 16)
  mem.back          16 chips GDDR7 no verso (instâncias mem.back.1 a 16)
  power.inductors   24 indutores 85N (representativos), corpo moldado e terminais
  power.vrm.gpu     24 estágios de potência (representativos), para dentro de cada indutor
  power.vrm.mem     4 estágios da memória (posição ilustrativa)
  power.controller  2 controladores QFN
  power.aux         3 indutores auxiliares pequenos
  io.aux_header     conector auxiliar de duas fileiras
  pcb.smd           passivos representativos (posições das ilhas do PCB nu), o conector de
                    4 vias da borda superior (frente) e o receptáculo do J3 (verso), estes dois
                    sem id próprio no assembly (seção 12.3 do plano)
  pcb.back_frame    chapa de apoio da mola: só os 4 anéis nos furos da mola, com
                    pcb_back_frame_thickness (0,8), de iface_spring_z_max a iface_pcb_back_z

Escala: as posições tiradas das fotos do PCB (chiphell/pcb-a, pcb-b, a_board) entram
divididas por chiphell_pcb_a_scale_factor (1,013), como o CSV de 2026-11-11 (pcb_layout.py).

Referencial (ARCHITECTURE.md, seção 7.6): mm, Z para cima, origem em card.envelope_min;
face B em z = 0, face A (ventiladores) em z = 40. O verso do PCB (iface_pcb_back_z) olha
para a face B; a frente (iface_pcb_front_z), com o chip, olha para a face A. O GLB sai em
metros com Y para cima, (x, y, z) -> (x, z, -y) / 1000. Peças com instâncias levam um nó
por instância (<id>.<k>), com a malha já no lugar, porque integrate.py lê os vértices sem
aplicar transformações; as âncoras viram nós vazios filhos.

Camadas do PCB, máscara de solda, serigrafia e o texto "85N" dos indutores são detalhe de
superfície (passo do Blender, ARCHITECTURE.md, seção 5.2): entram em extras como zonas, não
como geometria.

Uso:   python3 -I harness/parts/pcb.py
Saídas: harness/build/parts/<id>.glb e .step, harness/build/parts/pcb-report.json
"""
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import (Axis, Box, Compound, Location, Plane, Polygon, Pos, Rectangle, RectangleRounded, Rot, Solid,
                       export_step, extrude, fillet, chamfer, Circle, Sketch)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pcb_layout as PL  # noqa: E402

HARNESS = PL.HARNESS
OUT = HARNESS / "build" / "parts"
M, g, G, gb = PL.M, PL.g, PL.G, PL.gb
PARTS = PL.PARTS

IDS = ("pcb.main", "gpu.package", "mem.front", "mem.back", "power.inductors", "power.vrm.gpu", "power.vrm.mem",
       "power.controller", "power.aux", "io.aux_header", "pcb.smd", "pcb.back_frame")

TESS_TOL = 0.02
TESS_ANG = 0.2
TOL_ANCHOR = 2.0
TRI_BUDGET = 150_000

ZB, ZF = PL.ZB, PL.ZF

# cores de base (o lookdev troca pelos materiais do viewer)
COLOR = {
    "pcb.main": ([0.035, 0.045, 0.040, 1.0], 0.0, 0.45),
    "gpu.package": ([0.62, 0.55, 0.43, 1.0], 0.3, 0.45),
    "mem.front": ([0.05, 0.05, 0.055, 1.0], 0.0, 0.55),
    "mem.back": ([0.05, 0.05, 0.055, 1.0], 0.0, 0.55),
    "power.inductors": ([0.06, 0.06, 0.065, 1.0], 0.0, 0.6),
    "power.vrm.gpu": ([0.22, 0.22, 0.23, 1.0], 0.0, 0.7),
    "power.vrm.mem": ([0.22, 0.22, 0.23, 1.0], 0.0, 0.7),
    "power.controller": ([0.12, 0.12, 0.13, 1.0], 0.0, 0.6),
    "power.aux": ([0.55, 0.53, 0.50, 1.0], 0.0, 0.6),
    "io.aux_header": ([0.04, 0.04, 0.045, 1.0], 0.0, 0.5),
    "pcb.smd": ([0.45, 0.36, 0.25, 1.0], 0.0, 0.5),
    "pcb.back_frame": ([0.03, 0.03, 0.035, 1.0], 0.2, 0.5),
}

NOTES = {i: [] for i in IDS}


def note(pid, txt):
    NOTES[pid].append(txt)


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def ext(sk, z0, z1):
    return Pos(0, 0, z0) * extrude(sk, z1 - z0, dir=(0, 0, 1))


def to_mesh(shape):
    v, f = shape.tessellate(TESS_TOL, TESS_ANG)
    m = trimesh.Trimesh(np.array([[p.X, p.Y, p.Z] for p in v]), np.array(f), process=False)
    m.merge_vertices(digits_vertex=5)
    m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    return m


def place(mesh, x, y, z, rot_deg, mirror_z=False):
    """Gira em torno de z, espelha em z se for o verso (o componente pendura para -z) e
    translada. A malha do gabarito tem a base em z = 0 e cresce para +z."""
    v = np.asarray(mesh.vertices, float).copy()
    f = np.asarray(mesh.faces).copy()
    a = math.radians(rot_deg)
    c, s = math.cos(a), math.sin(a)
    v[:, :2] = v[:, :2] @ np.array([[c, s], [-s, c]])
    if mirror_z:
        v[:, 2] = -v[:, 2]
        f = f[:, ::-1]
    v += [x, y, z]
    return trimesh.Trimesh(v, f, process=False)


def place_shape(shape, x, y, z, rot_deg, mirror_z=False):
    if mirror_z:
        shape = shape.mirror(Plane.XY)
    return Pos(x, y, z) * (Rot(0, 0, rot_deg) * shape)


def to_gltf(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]] / 1000.0


def write_glb(path, nodes_spec, root_extras, pid):
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
    col, met, rough = COLOR[pid]
    gltf = {
        "asset": {"version": "2.0", "generator": "harness/parts/pcb.py", "extras": root_extras},
        "scene": 0, "scenes": [{"name": nodes_spec[0][0], "nodes": [0]}], "nodes": nodes, "meshes": meshes,
        "materials": [{"name": pid, "pbrMetallicRoughness": {"baseColorFactor": col, "metallicFactor": met,
                                                             "roughnessFactor": rough}}],
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
# Gabaritos (base em z = 0, centro em (0, 0), comprimento em x)
# ---------------------------------------------------------------------------
def tpl_memory():
    gl, gw, gt = M("gddr7_package_length"), M("gddr7_package_width"), M("gddr7_package_thickness")
    so = g("mem_standoff")
    body = box(-gl / 2, gl / 2, -gw / 2, gw / 2, so, gt)
    body = chamfer(body.edges().filter_by(lambda e: e.center().Z > gt - 1e-3), g("mem_chamfer"))
    under = box(-gl / 2 + 0.5, gl / 2 - 0.5, -gw / 2 + 0.5, gw / 2 - 0.5, 0, so + 0.01)
    return body + under


def tpl_inductor(side):
    h = g("ind_h")
    body = box(-side / 2, side / 2, -side / 2, side / 2, 0, h)
    body = fillet(body.edges().filter_by(lambda e: e.center().Z > 1e-3), g("ind_fillet"))
    tw, th, tt = min(g("ind_term_w"), side * 0.6), g("ind_term_h"), 0.15
    for sy in (-1, 1):
        y0 = sy * (side / 2 - 0.05)
        y1 = sy * (side / 2 + tt)
        body = body + box(-tw / 2, tw / 2, min(y0, y1), max(y0, y1), 0, th)
    return body


def tpl_block(L, Wd, h, ch=0.08, r=0.0):
    b = box(-L / 2, L / 2, -Wd / 2, Wd / 2, 0, h)
    if r > 0:
        b = fillet(b.edges().filter_by(Axis.Z), r)
    if ch > 0:
        b = chamfer(b.edges().filter_by(lambda e: e.center().Z > h - 1e-3), ch)
    return b


def tpl_header(L, d, h, nx, ny, pitch):
    body = box(-L / 2, L / 2, -d / 2, d / 2, 0, h)
    wall = 0.7
    body = body - box(-L / 2 + wall, L / 2 - wall, -d / 2 + wall, d / 2 - wall, 1.5, h + 1)
    pins = []
    for i in range(nx):
        for j in range(ny):
            px = (i - (nx - 1) / 2) * pitch
            py = (j - (ny - 1) / 2) * pitch
            pins.append(box(px - 0.32, px + 0.32, py - 0.32, py + 0.32, 1.4, h - 0.6))
    return body + pins


def tpl_j3(L, Wd, h):
    """Receptáculo placa a placa de perfil baixo (lado do PCB do J3). Base em z = 0 (encostada
    no PCB; no verso a malha é espelhada) e face de encaixe em z = h. Carcaça isolante com a
    fenda central, abas metálicas de fixação nas pontas e as pernas de solda das duas fileiras
    de contatos, dentro da pegada L x Wd."""
    sw, sd = g("j3_slot")
    hd = g("j3_holddown")
    pitch = g("j3_contact_pitch")
    tail = 0.4
    body_w = Wd - 2 * tail
    body = box(-L / 2 + 0.2, L / 2 - 0.2, -body_w / 2, body_w / 2, 0, h)
    body = body - box(-L / 2 + hd + 0.9, L / 2 - hd - 0.9, -sw / 2, sw / 2, h - sd, h + 1)
    parts = [body]
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (L / 2 - hd), sx * L / 2))
        parts.append(box(x0, x1, -body_w / 2 - 0.1, body_w / 2 + 0.1, 0, h * 0.75))
    span = L - 2 * hd - 1.2
    n = int(span // pitch) + 1
    for sy in (-1, 1):
        y0, y1 = sorted((sy * (body_w / 2 - 0.05), sy * Wd / 2))
        for k in range(n):
            x = (k - (n - 1) / 2) * pitch
            parts.append(box(x - 0.1, x + 0.1, y0, y1, 0, 0.15))
    return parts[0].fuse(*parts[1:]).clean(), 2 * n


def tpl_fan(L, d, h):
    """Conector de 4 vias de encaixe vertical (tipo ventilador): carcaça com cavidade aberta
    para +z, chave de polarização numa parede longa e 4 pinos."""
    wall, floor = 0.5, 0.5
    pitch = g("fan_conn_pitch")
    body = box(-L / 2, L / 2, -d / 2, d / 2, 0, h)
    body = body - box(-L / 2 + wall, L / 2 - wall, -d / 2 + wall, d / 2 - wall, floor, h + 1)
    body = body - box(-1.0, 1.0, d / 2 - wall - 0.1, d / 2 + 0.1, h - 1.0, h + 1)
    pins = [box(px - 0.25, px + 0.25, -0.25, 0.25, floor - 0.01, h - 0.4) for px in ((k - 1.5) * pitch for k in range(4))]
    return body.fuse(*pins).clean()


# ---------------------------------------------------------------------------
# Peças
# ---------------------------------------------------------------------------
def build_pcb():
    pid = "pcb.main"
    sk = Sketch() + Polygon(*PL.outline_xy(), align=None)
    pcb = ext(sk, ZB, ZF)
    rt = g("ring_t")
    rings = []
    for hx, hy, drill, od, kind in PL.holes_xy():
        pcb = pcb - (Pos(hx, hy, ZB - 1) * extrude(Circle(drill / 2), ZF - ZB + 2))
        ann = Pos(hx, hy) * Circle(od / 2) - Pos(hx, hy) * Circle(drill / 2)
        rings += [ext(ann, ZF - 0.01, ZF + rt), ext(ann, ZB - rt, ZB + 0.01)]
    pcb = pcb + rings
    note(pid, "contorno: retângulo do CSV (%.2f x %.2f, corrigido pelo fator do pcb-a) com o rebaixo da borda dos contatos (CSV) e o corte do canto do conector medido em a_board.png (G corner_cut, dividido pelo fator %.3f)" % (PL.W, PL.H, PL.F))
    note(pid, "8 furos: 4 da mola (furo %.1f, anel %.1f) e 4 cobreados de canto (furo %.1f, anel %.1f); anéis %.2f mm acima da máscara nas duas faces" % (
        g("spring_hole_drill"), g("spring_ring_od"), g("corner_hole_drill"), g("corner_ring_od"), rt))
    note(pid, "camadas, máscara, serigrafia e ilhas de cobre: textura (extras.surface), não geometria; o número de camadas não tem fonte")
    return [pcb]


def build_gpu():
    pid = "gpu.package"
    cx, cy = PL.DCX, PL.DCY
    px, py = M("gb202_package_x"), M("gb202_package_y")
    bx, by = M("gb202_bga_field_x"), M("gb202_bga_field_y")
    wx, wy = M("gb202_window_x"), M("gb202_window_y")
    dx, dy = M("gb202_die_x"), M("gb202_die_y")
    M("gb202_stiffener_ring_width_x"); M("gb202_stiffener_ring_width_y")
    top = ZF + M("gb202_die_top_above_pcb")
    z1 = ZF + g("gpu_ball_h")
    z2 = z1 + g("gpu_substrate_t")
    z3 = z2 + g("gpu_stiff_t")
    balls = box(cx - bx / 2, cx + bx / 2, cy - by / 2, cy + by / 2, ZF, z1 + 0.01)
    sub = box(cx - px / 2, cx + px / 2, cy - py / 2, cy + py / 2, z1, z2)
    sub = chamfer(sub.edges().filter_by(Axis.Z), 0.6)
    si = g("gpu_stiff_inset")
    ring = (Pos(cx, cy) * RectangleRounded(px - 2 * si, py - 2 * si, 1.0)) - (Pos(cx, cy) * RectangleRounded(wx, wy, g("gpu_window_r")))
    stiff = ext(ring, z2 - 0.01, z3)
    die = box(cx - dx / 2, cx + dx / 2, cy - dy / 2, cy + dy / 2, z2 - 0.01, top)
    die = chamfer(die.edges().filter_by(lambda e: e.center().Z > top - 1e-3), g("gpu_die_chamfer"))
    caps = []
    # capacitores do substrato: uma fileira em cada lado do die, no meio do vão até a janela
    for side in (-1, 1):
        xr = cx + side * (dx / 2 + (wx - dx) / 4)
        n = int((dy - 2) // 1.5)
        for k in range(n):
            yy = cy + (k - (n - 1) / 2) * 1.5
            caps.append(box(xr - 0.25, xr + 0.25, yy - 0.5, yy + 0.5, z2 - 0.01, z2 + 0.5))
        yr = cy + side * (dy / 2 + (wy - dy) / 4)
        n = int((dx - 2) // 1.5)
        for k in range(n):
            xx = cx + (k - (n - 1) / 2) * 1.5
            caps.append(box(xx - 0.5, xx + 0.5, yr - 0.25, yr + 0.25, z2 - 0.01, z2 + 0.5))
    part = balls + sub + stiff + die + caps
    note(pid, "esferas e underfill (campo de %.0f x %.0f do CSV, %.2f mm), substrato %.0f x %.1f (%.1f mm), moldura com janela %.0f x %.0f (%.1f mm), die %.1f x %.1f com topo a %.1f mm da frente do PCB" % (
        bx, by, g("gpu_ball_h"), px, py, g("gpu_substrate_t"), wx, wy, g("gpu_stiff_t"), dx, dy, M("gb202_die_top_above_pcb")))
    note(pid, "die mais comprido em y, como no CSV; a foto sabareesh também mostra o die vertical (reconferência pedida no plano, seção 10.5)")
    note(pid, "%d capacitores do substrato em volta do die: ilustrativos (gn-33 mostra fileiras na janela)" % len(caps))
    return [part]


def rows_of(rows, pid):
    return [r for r in rows if r["part"] == pid]


def build_instanced(rows, pid, tpl_fn):
    """Uma malha por instância, a partir de gabaritos por tamanho."""
    cache = {}
    meshes, shapes, rws = [], [], []
    for r in sorted(rows_of(rows, pid), key=lambda r: r["instance"]):
        key = (r["tipo"], r["comprimento"], r["largura"], r["altura"])
        if key not in cache:
            shp = tpl_fn(r)
            cache[key] = (shp, to_mesh(shp))
        shp, m = cache[key]
        back = r["lado"] == "verso"
        meshes.append(place(m, r["x"], r["y"], r["z_base"], r["rot_deg"], back))
        shapes.append(place_shape(shp, r["x"], r["y"], r["z_base"], r["rot_deg"], back))
        rws.append(r)
    return meshes, shapes, rws


def build_smd(rows):
    """pcb.smd: caixas simples (um tipo por tamanho) a partir da tabela, numa malha só, mais
    o conector de 4 vias da borda superior e o receptáculo do J3 (sem id próprio)."""
    pid = "pcb.smd"
    boxes, shapes = [], []
    for r in rows_of(rows, pid):
        back = r["lado"] == "verso"
        if r["tipo"] == PL.J3_TIPO:
            shp, ncont = tpl_j3(r["comprimento"], r["largura"], r["altura"])
            shp = place_shape(shp, r["x"], r["y"], r["z_base"], r["rot_deg"], back)
            boxes.append(to_mesh(shp))
            shapes.append(shp)
            note(pid, "receptáculo do J3 no verso: %.1f x %.1f, de z %.2f (plano de encaixe, iface_j3_mating_z) a %.2f (verso do PCB), centrado em (iface_j3_center_x, _y) = (%.2f; %.2f); carcaça com fenda central, abas de fixação nas pontas e %d pernas de solda (passo %.1f, ilustrativo: a contagem não é fato)" % (
                r["comprimento"], r["largura"], r["z_base"] - r["altura"], r["z_base"], r["x"], r["y"], ncont, g("j3_contact_pitch")))
            continue
        if r["tipo"] == PL.FAN_TIPO:
            shp = place_shape(tpl_fan(r["comprimento"], r["largura"], r["altura"]), r["x"], r["y"], r["z_base"], r["rot_deg"], back)
            boxes.append(to_mesh(shp))
            shapes.append(shp)
            note(pid, "conector de 4 vias da borda superior (frente): %.1f (pcb_fan_header_length) x %.1f x %.1f em (u %.1f; v %.1f) = (%.2f; %.2f), cavidade aberta para +z, chave de polarização e 4 pinos de passo %.1f; profundidade, altura e passo são palpite; função provável de ventilador (inferred)" % (
                r["comprimento"], r["largura"], r["altura"], M("pcb_fan_header_u"), M("pcb_fan_header_v"), r["x"], r["y"], g("fan_conn_pitch")))
            continue
        L, Wd, h = r["comprimento"], r["largura"], r["altura"]
        b = trimesh.creation.box(extents=(L, Wd, h))
        b.apply_translation((0, 0, h / 2))
        boxes.append(place(b, r["x"], r["y"], r["z_base"], r["rot_deg"], back))
        bs = Box(L, Wd, h)
        bs = Pos(0, 0, h / 2) * bs
        shapes.append(place_shape(bs, r["x"], r["y"], r["z_base"], r["rot_deg"], back))
    n = sum(1 for r in rows_of(rows, pid) if not r["tipo"].startswith("conector"))
    note(pid, "%d passivos em caixas (tipos 0201 a 1206 e blocos): posição de pares de ilhas do PCB nu nas duas faces (fotos com a escala corrigida pelo fator do pcb-a); tipo, altura e quantidade ilustrativos; terminais metálicos ficam na textura (extras.smd_terminal_fraction)" % n)
    return [trimesh.util.concatenate(boxes)], shapes


def build_back_frame():
    """pcb.back_frame: 4 anéis nos furos da mola, de iface_spring_z_max a iface_pcb_back_z."""
    pid = "pcb.back_frame"
    t = M("pcb_back_frame_thickness")
    z1 = ZB
    z0 = z1 - t
    zs = M("iface_spring_z_max")
    od, drill = g("back_ring_od"), gb("spring_hole_drill")
    rings = []
    for hx, hy, dr, ring_od, kind in PL.holes_xy():
        if kind != "mola":
            continue
        ann = Pos(hx, hy) * Circle(od / 2) - Pos(hx, hy) * Circle(drill / 2)
        rings.append(ext(ann, z0, z1))
    note(pid, "4 anéis de %.1f mm (furo de %.2f) com %.2f mm (pcb_back_frame_thickness), de z %.2f a %.2f; a mola assenta em iface_spring_z_max = %.2f%s" % (
        od, drill, t, z0, z1, zs, "" if abs(z0 - zs) < 1e-6 else " (diferença de %.2f mm)" % (z0 - zs)))
    note(pid, "contorno da chapa sem medida (gn-30): só os anéis, como no blockout; forma inferred")
    return [Compound(rings)]


# ---------------------------------------------------------------------------
# Superfície (para o passo do Blender)
# ---------------------------------------------------------------------------
def surface_extras():
    def uvxy(u, v):
        # lidos em a_board.png na escala da base: divididos pelo fator do pcb-a
        return [round(PL.X0 + u / PL.F, 2), round(PL.Y0 + v / PL.F, 2)]
    return {
        "mask": {"color": "preto esverdeado fosco", "provenance": "derived", "source": "chiphell/pcb-a, pcb-b; sabareesh"},
        "edge_stack": {"note": "borda do PCB com faixas de cobre e FR-4 como textura; número de camadas sem fonte (illustrative)",
                       "thickness_mm": M("pcb_main_thickness"), "provenance": "illustrative"},
        "copper_pads": {"note": "ilhas de cobre expostas onde não há componente: usar a foto retificada como máscara (a_board.png no verso, pcb-b retificada na frente) só como guia; não embutir a foto (material de terceiros)", "provenance": "derived"},
        "silkscreen_back": [
            {"text": "ET4", "xy": uvxy(23.3, 77.2), "height_mm": 2.2, "reading_dir_xy": [0, 1], "provenance": "derived"},
            {"text": "E248779 / DH4 94V-0", "xy": uvxy(23.3, 88.7), "height_mm": 0.9, "reading_dir_xy": [0, 1], "provenance": "derived"},
            {"text": "0225 15-01", "xy": uvxy(19.2, 85.7), "height_mm": 0.9, "reading_dir_xy": [0, 1], "provenance": "derived"},
            {"text": "004418", "xy": uvxy(20.2, 91.2), "height_mm": 0.9, "reading_dir_xy": [0, 1], "provenance": "derived"},
            {"text": "etiqueta QR (adesivo)", "xy": uvxy(84.3, 86.7), "size_mm": [5, 5], "provenance": "derived"},
        ],
        "silkscreen_note": "posições lidas em a_board.png (verso, PCB nu do Chiphell) e corrigidas pelo fator de escala do pcb-a; o texto lê na direção +y visto do verso; tamanhos aproximados",
    }


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------
FEATURE_PROV = {
    "pcb.main": {"contorno (largura, altura, rebaixo)": "derived (CSV, escala corrigida)", "corte do canto do conector": "derived (a_board.png, escala corrigida pelo fator)",
                 "furos (posição)": "derived (CSV)", "furos (diâmetro e anel)": "derived (a_board.png, nesta tarefa)",
                 "espessura": "inferred (CSV, norma)", "camadas, máscara, serigrafia": "textura (extras.surface)"},
    "gpu.package": {"package, campo de esferas, janela, die": "derived (CSV)", "alturas de esferas, substrato, moldura": "inferred",
                    "capacitores do substrato": "illustrative"},
    "mem.front": {"posição": "derived (grade arbitrada do CSV; campos de esferas da frente conferidos na pcb-b retificada)", "encapsulamento": "derived (tabela da Micron, CSV)",
                  "giro dos 2 chips da borda dos contatos": "derived (CSV, mem_footprint_*)"},
    "mem.back": {"posição": "derived (grade arbitrada do CSV)", "encapsulamento": "derived (tabela da Micron, CSV)",
                 "giro dos 2 chips da borda dos contatos": "derived (CSV, mem_footprint_*)"},
    "power.inductors": {"fileiras (posição)": "derived (CSV, pcb-b retificada, sabareesh)", "quantidade": "inferred (representativa, assembly)",
                        "lado": "inferred (CSV)", "altura": "inferred (orçamento de camadas)"},
    "power.vrm.gpu": {"posição (para dentro de cada indutor, na frente)": "derived (sabareesh)", "quantidade": "inferred (representativa)",
                      "tamanho": "derived (sabareesh); altura inferred"},
    "power.vrm.mem": {"posição": "illustrative", "quantidade": "inferred (representativa)"},
    "power.controller": {"posição do primeiro": "derived (pcb-b retificada)", "segundo": "illustrative", "tamanho": "inferred"},
    "power.aux": {"um 4R7": "derived (sabareesh)", "os outros dois": "illustrative", "tamanho": "inferred"},
    "io.aux_header": {"posição e comprimento": "derived (CSV, escala antiga)", "profundidade, altura, pinos": "inferred"},
    "pcb.smd": {"posições": "derived (ilhas do PCB nu, escala corrigida)", "tipos, alturas, quantidade": "illustrative",
                "conector de 4 vias (posição, comprimento)": "derived (CSV pcb_fan_header_*, sabareesh); função inferred; sem id no assembly",
                "conector de 4 vias (profundidade, altura, pinos)": "inferred / illustrative",
                "receptáculo do J3 (posição, pegada, altura)": "derived (CSV iface_j3_*, pcb_j3_receptacle_*); altura inferred",
                "receptáculo do J3 (fenda, abas, pernas)": "illustrative"},
    "pcb.back_frame": {"furos (posição)": "derived (CSV iface_spring_holes)", "espessura": "inferred (CSV pcb_back_frame_thickness)",
                       "contorno (só anéis)": "inferred"},
}


def main():
    import frame  # conferência de âncoras (mesmo teste de frame.py)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = PL.read_layout()
    big, obs = PL.big_rows()
    # a tabela gravada tem de bater com as medidas atuais (passivos à parte)
    cur = {(r["id"], r["tipo"]): r for r in big}
    stale = [r["id"] for r in rows if (r["part"] != "pcb.smd" or r["tipo"].startswith("conector")) and (r["id"], r["tipo"]) in cur
             and any(abs(cur[(r["id"], r["tipo"])][k] - r[k]) > 1e-3 for k in ("x", "y", "rot_deg", "comprimento", "largura", "altura"))]
    if stale or len([r for r in rows if r["part"] != "pcb.smd" or r["tipo"].startswith("conector")]) != len(big):
        raise SystemExit("layout.csv desatualizado em relação ao CSV de medidas: rode pcb_layout.py (%s)" % stale[:5])

    shapes, meshes, inst_rows = {}, {}, {}
    shapes["pcb.main"] = build_pcb()
    shapes["gpu.package"] = build_gpu()
    for pid in ("pcb.main", "gpu.package"):
        meshes[pid] = [to_mesh(s) for s in shapes[pid]]

    def mem_t(r):
        return tpl_memory()

    def ind_t(r):
        return tpl_inductor(r["comprimento"])

    def blk_t(r):
        return tpl_block(r["comprimento"], r["largura"], r["altura"])

    def aux_t(r):
        return tpl_block(r["comprimento"], r["largura"], r["altura"], ch=0.0, r=0.4)

    def hdr_t(r):
        return tpl_header(r["comprimento"], r["largura"], r["altura"], 7, 2, g("aux_header_pitch"))

    for pid, fn in (("mem.front", mem_t), ("mem.back", mem_t), ("power.inductors", ind_t), ("power.vrm.gpu", blk_t),
                    ("power.vrm.mem", blk_t), ("power.controller", blk_t), ("power.aux", aux_t), ("io.aux_header", hdr_t)):
        ms, ss, rw = build_instanced(rows, pid, fn)
        meshes[pid], shapes[pid], inst_rows[pid] = ms, ss, rw
    note("mem.front", "16 chips de %.0f x %.0f x %.1f mm (encapsulamento da Micron) na grade arbitrada (passo %.2f, escala corrigida pelo fator do pcb-a); lado de 14 mm atravessado na fileira nas laterais e na borda de energia; os 2 chips da borda dos contatos giram (14 ao longo da borda); esferas como um bloco recuado de %.2f mm" % (
        M("gddr7_package_length"), M("gddr7_package_width"), M("gddr7_package_thickness"), M("mem_side_v_pitch"), g("mem_standoff")))
    note("mem.back", NOTES["mem.front"][0])
    note("power.inductors", "lado %.1f (vrm_inductor_side) e %.1f nos menores da borda superior, altura %.1f (limite da base do cooler); texto 85N só como área (extras)" % (
        M("vrm_inductor_side"), g("ind_top_side"), g("ind_h")))
    note("power.vrm.gpu", "estágios na frente, para dentro de cada indutor, como os blocos cinza da foto sabareesh; o blockout os punha no verso")
    note("power.vrm.mem", "posição sem fonte (assembly): duas células livres da ponta oposta")
    note("io.aux_header", "corpo preto com cavidade e 2 x 7 pinos (passo %.1f, palpite)" % g("aux_header_pitch"))
    smd_m, smd_s = build_smd(rows)
    meshes["pcb.smd"], shapes["pcb.smd"] = smd_m, smd_s
    shapes["pcb.back_frame"] = build_back_frame()
    meshes["pcb.back_frame"] = [to_mesh(shapes["pcb.back_frame"][0])]

    report = {"parts": {}, "guess_values": {k: {"value": v[0], "provenance": v[1], "note": v[2],
                                                "scale": "base (dividido por %.3f no uso)" % PL.F if k in PL.BASE_SCALE else "real"}
                                            for k, v in G.items()},
              "scale_factor": {"chiphell_pcb_a_scale_factor": PL.F, "aplicado_a": sorted(PL.BASE_SCALE) + ["passivos (quadros das fotos)", "serigrafia"]},
              "layout": str(PL.LAYOUT.relative_to(HARNESS.parent)), "layout_obs": obs, "layout_checks": PL.checks(big)}
    total = 0
    ok_all = True
    for pid in IDS:
        p = PARTS[pid]
        ms = meshes[pid]
        mesh = trimesh.util.concatenate(ms)
        ntri = int(len(mesh.faces))
        total += ntri
        closed = [bool(m.is_watertight and m.is_winding_consistent and m.volume > 0) for m in ms]
        lo, hi = mesh.bounds
        anchors = frame.anchor_check(pid, mesh) if p["anchors"] else []
        extras = {
            "id": pid, "stage": p["stage"], "fidelity": p["fidelity"], "exists_provenance": p["exists_provenance"],
            "shape_provenance": p["shape_provenance"], "shape_provenance_features": FEATURE_PROV[pid],
            "guess": True, "guess_notes": NOTES[pid], "blockout": False, "units_cad": "mm", "up_cad": "+Z",
            "origin": "card.envelope_min", "referencial": "face B em z = 0, face A (ventiladores) em z = card_thickness; frente do PCB (chip) para +z",
            "explode_cad": p["explode"], "layout": "harness/parts/pcb/layout.csv",
            "viewer_warning": p["shape_provenance"] in ("inferred", "illustrative") or p["exists_provenance"] in ("inferred", "illustrative"),
        }
        if "count" in p:
            extras["count"] = p["count"]["value"]
            extras["count_provenance"] = p["count"]["provenance"]
            extras["representative"] = bool(p["count"].get("representative", False))
        if pid == "pcb.main":
            extras["surface"] = surface_extras()
        if pid == "pcb.smd":
            extras["representative"] = True
            extras["smd_terminal_fraction"] = {"0201": 0.25, "0402": 0.25, "0603": 0.22, "0805": 0.2, "1206": 0.15, "bloco": 0.15}
        spec = []
        if pid in inst_rows and "count" in p:
            spec.append((pid, extras, None, None, None))
            for k, (m, r) in enumerate(zip(ms, inst_rows[pid]), 1):
                ex = {"instance_of": pid, "instance": k, "stage": p["stage"], "tipo": r["tipo"], "lado": r["lado"],
                      "provenance": r["provenance"], "representative": r["representativo"] == "sim", "layout_id": r["id"],
                      "guess": r["provenance"] != "confirmed", "viewer_warning": r["provenance"] in ("inferred", "illustrative")}
                if pid == "power.inductors":
                    zt = r["z_base"] + g("ind_h")
                    s = r["comprimento"] * 0.36
                    ex["text_box_cad_mm"] = {"text": "85N", "center_xy": [r["x"], r["y"]], "z": zt, "size": [2 * s, s],
                                             "reading_dir_xy": [1, 0], "engrave": False, "provenance": "derived"}
                spec.append(("%s.%d" % (pid, k), ex, m, None, 0))
        else:
            spec.append((pid, extras, ms[0] if len(ms) == 1 else mesh, None, None))
        for a in p["anchors"]:
            spec.append((a["id"], {"anchor": True, "part": pid}, None, to_gltf([a["pos"]])[0], 0))
        glb = OUT / ("%s.glb" % pid)
        write_glb(glb, spec, {"units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z", "origin": "card.envelope_min",
                              "map": "gltf = (x, z, -y) / 1000"}, pid)
        step = OUT / ("%s.step" % pid)
        comp = shapes[pid][0] if len(shapes[pid]) == 1 else Compound(shapes[pid])
        comp.label = pid
        export_step(comp, str(step))
        sc = trimesh.load(glb, force="scene")
        back = sc.to_geometry()
        bl = np.c_[back.vertices[:, 0], -back.vertices[:, 2], back.vertices[:, 1]] * 1000.0
        reread_ok = bool(np.allclose(bl.min(axis=0), lo, atol=0.01) and np.allclose(bl.max(axis=0), hi, atol=0.01))
        ok = all(closed) and reread_ok and all(a["ok"] for a in anchors)
        ok_all &= all(closed) and reread_ok
        report["parts"][pid] = {"triangles": ntri, "bodies": len(ms), "closed": all(closed), "bbox_min": lo.round(3).tolist(),
                                "bbox_max": hi.round(3).tolist(), "glb_bytes": glb.stat().st_size, "step_bytes": step.stat().st_size,
                                "glb_reread_bbox_ok": reread_ok, "anchors": anchors, "notes": NOTES[pid]}
        print("%-17s %6d triângulos, %3d corpos, %6.0f kB GLB, %7.0f kB STEP, fechada: %s%s" % (
            pid, ntri, len(ms), glb.stat().st_size / 1024, step.stat().st_size / 1024, "sim" if all(closed) else "NÃO",
            "" if ok else "  (ver âncoras)"))
        for a in anchors:
            if not a["ok"] or a["dist_mm"] > 0.5:
                print("    %-36s dist %.2f mm %s" % (a["anchor"], a["dist_mm"], "OK" if a["ok"] else "ACIMA DE %.0f mm" % TOL_ANCHOR))
    report["triangles_total"] = total
    report["triangle_budget"] = TRI_BUDGET
    report["csv_keys_used"] = sorted(PL.USED)
    ok_all &= total <= TRI_BUDGET
    print("Triângulos no total: %d (orçamento %d) %s" % (total, TRI_BUDGET, "OK" if total <= TRI_BUDGET else "ACIMA"))
    for o in obs:
        print("OBS", o)
    (OUT / "pcb-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Relatório: %s" % (OUT / "pcb-report.json").relative_to(HARNESS.parent))
    print("Resultado (malhas fechadas, releitura, orçamento): %s" % ("OK" if ok_all else "FALHA"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
