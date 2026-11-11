#!/usr/bin/env python3
"""Peças de I/O e de conexão da RTX PRO 6000 Blackwell Workstation Edition (F3).

Gera, em build123d, as peças que substituem as caixas do blockout, com os mesmos ids do
assembly:

  io.bracket            chapa do bracket de dois slots: contorno com as duas línguas e o
                        entalhe entre elas, aba dobrada do lado da borda superior com dois
                        rasgos em U, painel em relevo com as 4 aberturas dos DisplayPort,
                        etiquetas como áreas planas (relevo de 0,1 mm)
  fasteners.e1_bracket  os 4 parafusos do bracket (cabeça com fenda hexalobular), 4 instâncias
  io.board              placa das saídas (forma ilustrativa, D6)
  io.board.dp           os 4 receptáculos DisplayPort (casca, língua e contatos), 4 instâncias
  pcie.adapter          placa adaptadora PCIe: contorno da foto retificada, contatos dourados
                        nas duas faces, chave, rasgo e gancho da ponta, lóbulo, furos e o
                        conector J3 de placa a placa
  power.connector       conector de 16 pinos em ângulo reto: corpo, 12 cavidades grandes em
                        2 x 6 e 4 pequenas de sinal, trava, lâminas de saída e base

Referencial (ARCHITECTURE.md, 7.6): mm, Z para cima, origem em card.envelope_min; x a partir
do plano do bracket (a chapa fica em x negativo), y a partir da ponta dos contatos PCIe, face B
em z = 0 e face A dos ventiladores em z = card_thickness. O GLB sai em metros com Y para cima,
(x, y, z) -> (x, z, -y) / 1000. Um nó por id (ou nós <id>.1, <id>.2 ... para instâncias); as
âncoras do assembly viram nós vazios filhos. harness/parts/integrate.py troca as caixas do
blockout por estas peças em build/card.glb.

Medidas: do CSV pela chave (M) ou do assembly. O que não tem linha no CSV está em G, com a
procedência: "derived" quando foi medido nesta tarefa em foto de terceiro (método na nota) e
"inferred" quando é palpite. Este script não lê a pasta de referências (não versionada): os
pontos medidos nas fotos estão escritos aqui, e harness/parts/io_compare.py refaz as
comparações sobre as fotos.

Posição da fileira de DisplayPort (contrato de 2026-11-11, assembly-plan 12.3): as âncoras de
io.board.dp (y 29,44 a 92,14; z 13,5) saem da arbitragem do visual-qa (bracket_top_below_shroud_top,
dp_row_center_z, dp_row_from_bracket_tip, dp_port_pitch). O padrão (modo âncoras) centra o
conjunto do bracket nas âncoras; --foto posiciona pela foto (topo do bracket a
bracket_top_below_shroud_top do topo da carcaça). Os dois modos coincidem; o relatório traz a
diferença.

Uso:   python3 -I harness/parts/io_parts.py [--foto] [--pecas=io.bracket,fasteners.e1_bracket]
Saídas: harness/build/parts/<id>.glb e .step, harness/build/parts/io-report.json
"""
import csv
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from build123d import (Axis, Compound, Face, Location, Plane, Pos, Rot, Vector, Wire, export_step,
                       extrude)

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
ASSEMBLY = HARNESS / "design" / "assembly.json"
MEASURES = HARNESS / "design" / "measurements.csv"
OUT = HARNESS / "build" / "parts"

TOL_ANCHOR = 2.0       # mm
TESS_TOL = 0.02        # mm
TESS_ANG = 0.25        # rad
TRI_BUDGET = 40_000    # triângulos, todas as peças deste script
MODE = "foto" if "--foto" in sys.argv else "ancoras"

# ---------------------------------------------------------------------------
# Valores sem linha no CSV: (valor, procedência, nota)
# Calibração das fotos usada nas notas "derived":
#  sr-1: bracket de frente, quase ortogonal; escala horizontal pelo comprimento total do bracket
#        (bracket_height_overall = 120,02 em 767 px: 6,39 px/mm); vertical pela largura de dois
#        slots (bracket_slot_width_single + pcie_slot_pitch = 38,74 em 246 px: 6,35 px/mm).
#        Conferência: as duas línguas ficam a 20,5 mm uma da outra (passo de slot da norma: 20,32).
#  am_adapter: retificação do visual-qa (chiphell/pcb-a) a 12,8 px/mm na grade sobreposta;
#        a grade da base sai 1,3 % grande sobre o PCB (chiphell_pcb_a_scale_factor). O contorno
#        vai para o modelo com o comprimento e as alturas da arbitragem (pcie_adapter_length,
#        _strip_height, _total_height_without_lobe, _total_height): escala única em x e mapa
#        linear por trechos na altura (0; faixa; sem lóbulo; com lóbulo). Os furos e o J3 vêm
#        das linhas iface_adapter_*_hole_* e iface_j3_center_* do CSV.
#  gn-25: adaptador quase de frente; régua = passo dos contatos (1,00 mm, norma).
#  sabareesh/wb-bare-pcb e visualqa/ab_conn (furos do conector no PCB do Chiphell): conector.
# ---------------------------------------------------------------------------
G = {
    # bracket (sr-1)
    "br_flange_above_contacts": (104.86, "confirmed (norma rev 3.0)",
                                 "altura da aba de fixação do bracket (topo) acima do datum W, a borda dos contatos PCIe: 104,86 ± 0,52 (CEM 3.0, Fig. 9-3, p. 130; "
                                 "datum W na Fig. 9-1, p. 128); com bracket_height_overall (120,02, Fig. 9-5) a ponta das línguas fica 15,16 mm além dos contatos. "
                                 "Conferência nos renders quase ortogonais (2,2716 px/mm, bordas pelo alfa): pny/front aba a 104,55 e ponta a 16,68 além dos contatos; "
                                 "pny/back 104,6 e 15,0. Substitui, para a posição em y do bracket, a conta por bracket_top_below_shroud_top (ponta a 11,46), que "
                                 "dependia da altura da carcaça sobre os contatos (Q1); achado 17 do visual-qa de 2026-11-11"),
    "br_face_a_flush": (0.0, "derived", "a borda do bracket do lado da face A fica rente à face A (sr-1); a outra borda sai da largura de dois slots (conta)"),
    "br_tongue_z": (((7.10, 16.50), (27.60, 37.06)), "derived", "faixas em z das duas línguas (sr-1); centros a 20,46 mm, passo de slot da norma 20,32"),
    "br_tongue_len": ((9.9, 7.3), "derived", "comprimento das línguas, do lado da face B e do lado da face A, até a borda da chapa (sr-1)"),
    "br_notch": ((6.8, 11.0, 20.8, 24.5), "derived", "entalhe entre as línguas: começa a 6,8 da ponta, fundo a 11,0, com chanfros de 45 graus até z 20,8 e 24,5 (sr-1)"),
    "br_label_zone_z": ((3.5, 39.2), "derived", "a chapa da região das marcas regulatórias é mais estreita que o painel: z de 3,5 a 39,2 (sr-1)"),
    "br_panel_y0": (28.43, "derived", "início do painel em relevo, medido da ponta das línguas (sr-1)"),
    "br_panel_y1": (117.17, "derived", "fim do painel em relevo, medido da ponta das línguas (sr-1)"),
    "br_panel_relief": (0.40, "inferred", "altura do relevo do painel para fora (-x); sr-1 e gn-11 mostram a borda do painel com brilho, sem medida de altura"),
    "br_panel_margin": (0.8, "inferred", "folga entre a borda do painel em relevo e a borda da chapa em cima, embaixo e na ponta"),
    "br_corner_r": (0.6, "inferred", "raio dos cantos do contorno da chapa"),
    "br_flange_clear": (0.1, "inferred", "folga da dobra da ponta de cima até a carcaça (a dobra cabe no recuo da placa de extremidade)"),
    "br_bend_chamfer": (0.6, "inferred", "chanfro da aresta externa da dobra"),
    "br_dp_open": ((18.0, 6.6), "derived", "abertura do bracket para cada DisplayPort, largura (y) e altura (z) (sr-1)"),
    "br_dp_chamfer": (2.2, "derived", "chanfro do canto da abertura do lado (-y, +z) (sr-1)"),
    "br_dp_open_r": (0.8, "inferred", "raio dos outros cantos da abertura"),
    "br_screws": (((33.16, 7.4), (112.36, 7.4), (33.16, 33.5), (112.36, 33.5)), "derived", "centros (y da ponta das línguas, z) dos 4 parafusos do painel (sr-1); casam com os insertos de canto da placa de extremidade em gn-16"),
    "screw_head": ((3.9, 1.2), "derived", "diâmetro da cabeça (sr-1) e altura (inferred)"),
    "screw_recess": ((1.9, 0.6), "inferred", "fenda hexalobular: diâmetro externo e profundidade (sr-1 mostra estrela de 6 pontas, sem medida)"),
    "labels": ((("etiqueta_vbios", "escura", 42.13, 56.60, 21.18, 26.15),
                ("etiqueta_modelo", "escura", 42.13, 67.17, 26.70, 36.40),
                ("etiqueta_qr", "branca", 67.70, 93.20, 24.20, 37.25)),
               "derived", "etiquetas do painel (y da ponta das línguas e z); sr-1; o texto e o QR ficam para o passo do Blender"),
    "label_t": (0.10, "inferred", "espessura das etiquetas como relevo"),
    "regulatory_zone": ((11.5, 27.5, 4.5, 38.0), "derived", "área das marcas regulatórias impressas (CE, UKCA, FCC, UL, KC e outras), y da ponta e z (sr-1)"),
    # io.board
    "io_board_clear": (0.3, "inferred", "folga da placa das saídas até a parede interna, a grade da face B e o duto do ventilador 1"),
    # DisplayPort
    "dp_shell_chamfer": (2.0, "inferred", "chanfro do canto da casca do receptáculo (forma de norma, tamanho sem desenho aberto)"),
    "dp_shell_t": (0.3, "inferred", "espessura da casca metálica"),
    "dp_cavity_depth": (7.0, "inferred", "profundidade da boca do receptáculo"),
    "dp_tongue": ((11.0, 1.2), "inferred", "largura e espessura da língua de contatos"),
    "dp_contact_w": (0.4, "inferred", "largura de cada contato (10 por face, passo dp_contact_pitch)"),
    # adaptador PCIe (am_adapter, gn-25)
    "ad_outline_img": ("am_adapter", "derived", "contorno, lóbulo, rasgo, gancho e furos medidos em am_adapter (retificação do visual-qa sobre chiphell/pcb-a), pontos em AD_IMG"),
    "ad_key": ((1.55, 8.1), "derived", "largura e profundidade da chave entre os grupos de contatos (gn-25, passo de 1,00 mm como régua)"),
    "ad_pad": ((0.70, 0.35, 5.47), "derived", "contatos: largura (gn-25) e faixa em y de 0,35 a 5,47 (am_adapter)"),
    "ad_pad_t": (0.04, "inferred", "espessura do dourado como relevo"),
    "ad_bevel": (0.4, "inferred", "chanfro da borda de inserção nas duas faces"),
    "ad_holes": ((2.0, 3.8, 2.5, 2.0), "derived", "diâmetros: furo com anel de cobre e anel (gn-25), furo do lóbulo, furos da faixa"),
    "ad_ring_t": (0.035, "inferred", "espessura do anel de cobre como relevo"),
    "j3_width": (5.63, "derived", "largura do J3 em y (am_adapter: 5,7 na grade / chiphell_pcb_a_scale_factor)"),
    "j3_slot": ((21.0, 1.6, 0.6), "inferred", "fenda central do J3: comprimento, largura, profundidade (menor que a altura do plugue, iface_j3_mating_z - iface_adapter_board_z_max)"),
    "j3_contacts": ((42, 0.5, 0.25), "inferred", "contatos por fileira, passo e largura (gn-25 mostra duas fileiras finas, sem contagem legível)"),
    # conector de 16 pinos
    "p16_across": (7.40, "inferred", "parte do corpo com as duas fileiras de potência, através delas: cota 7,40 da vista lateral da Intel 613768 (Fig. 5-8, sem rótulo identificado); o resto de power_connector_body_across (9,7) é a faixa dos 4 pinos de sinal; o corpo inteiro fica centrado em (power_connector_center_from_bracket_end, power_connector_center_y)"),
    "p16_sense_len_z": (9.0, "inferred", "extensão em z da faixa de sinal"),
    "p16_cavity": ((2.3, 6.5), "inferred", "cavidade de potência: lado e profundidade"),
    "p16_pin": (0.64, "inferred", "lado dos pinos de potência dentro das cavidades"),
    "p16_sense_cavity": ((1.1, 4.0, 0.4), "inferred", "cavidade de sinal: lado, profundidade e lado do pino"),
    "p16_latch": ((4.0, 2.5, 0.7), "inferred", "trava do lado dos pinos de sinal: extensão em z, comprimento e altura"),
    "p16_blade": ((0.8, 6.5), "derived", "lâminas de saída das duas fileiras: espessura (inferred) e alcance atrás do corpo; o PCB do Chiphell (visualqa/ab_conn) mostra um furo alongado por fileira, na direção de encaixe, e sabareesh mostra duas tiras metálicas"),
    "p16_base": ((6.5, 1.2), "inferred", "base atrás do corpo (organizador das lâminas), só sob as lâminas: comprimento e altura"),
}


def g(k):
    return G[k][0]


def load_measures():
    out = {}
    with open(MEASURES, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["feature"]] = float(r["value_mm"])
    return out


MEAS = load_measures()
USED = set()


def M(k):
    USED.add(k)
    return MEAS[k]


ASM = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
PARTS = {p["id"]: p for p in ASM["parts"]}
T = M("card_thickness")
Y0 = M("iface_shroud_y_min")
Y1 = Y0 + M("shroud_height_proposed")
WALL = M("shroud_wall")
NOTES = {}
ZONES = {}


def note(pid, txt):
    NOTES.setdefault(pid, []).append(txt)


def zone(pid, name, kind, **kw):
    ZONES.setdefault(pid, []).append(dict(name=name, material=kind, **{k: (np.round(v, 3).tolist() if isinstance(v, (list, tuple, np.ndarray)) else v) for k, v in kw.items()}))


# ---------------------------------------------------------------------------
# Auxiliares de geometria
# ---------------------------------------------------------------------------
def round_poly(pts, r, nseg=6):
    """Arredonda cada vértice de um polígono (convexo ou côncavo) com raio r (escalar ou lista)."""
    P = np.asarray(pts, float)
    n = len(P)
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    out = []
    for i in range(n):
        p0, p1, p2 = P[i - 1], P[i], P[(i + 1) % n]
        rr = rs[i]
        a, b = p0 - p1, p2 - p1
        la, lb = np.linalg.norm(a), np.linalg.norm(b)
        if rr <= 0 or la < 1e-9 or lb < 1e-9:
            out.append(p1)
            continue
        a, b = a / la, b / lb
        ang = math.acos(max(-1.0, min(1.0, float(a @ b))))
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append(p1)
            continue
        t = rr / math.tan(ang / 2)
        t = min(t, 0.45 * la, 0.45 * lb)
        rr = t * math.tan(ang / 2)
        q0, q1 = p1 + a * t, p1 + b * t
        bis = (a + b) / np.linalg.norm(a + b)
        c = p1 + bis * rr / math.sin(ang / 2)
        a0 = math.atan2(*(q0 - c)[::-1])
        a1 = math.atan2(*(q1 - c)[::-1])
        sw = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(nseg + 1):
            th = a0 + sw * k / nseg
            out.append(c + rr * np.array([math.cos(th), math.sin(th)]))
    # remove pontos repetidos
    res = [out[0]]
    for p in out[1:]:
        if np.linalg.norm(p - res[-1]) > 1e-4:
            res.append(p)
    if np.linalg.norm(res[0] - res[-1]) < 1e-4:
        res.pop()
    return [tuple(map(float, p)) for p in res]


def rrect(u0, u1, v0, v1, r, nseg=6):
    return round_poly([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], r, nseg)


def circle(cu, cv, r, n=24):
    return [(cu + r * math.cos(2 * math.pi * k / n), cv + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def face_on(pts, plane):
    w = Wire.make_polygon([Vector(u, v, 0) for u, v in pts], close=True)
    return plane * Face(w)


def prism_x(pts_yz, x0, x1):
    """Contorno no plano (y, z) extrudado de x0 a x1."""
    return extrude(face_on(pts_yz, Plane.YZ.offset(x0)), x1 - x0, dir=(1, 0, 0))


def prism_z(pts_xy, z0, z1):
    return extrude(face_on(pts_xy, Plane.XY.offset(z0)), z1 - z0, dir=(0, 0, 1))


def prism_y(pts_xz, y0, y1):
    """Contorno no plano (x, z) extrudado de y0 a y1."""
    f = face_on(pts_xz, Plane.XZ)          # Plane.XZ: u = x, v = z, normal -y
    return Pos(0, y1, 0) * extrude(f, y1 - y0, dir=(0, -1, 0))


def box(x0, x1, y0, y1, z0, z1):
    return prism_z([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def union(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out + s
    return out


# ---------------------------------------------------------------------------
# Posição do conjunto do bracket (ver docstring)
# ---------------------------------------------------------------------------
def io_placement():
    """Ponta das línguas (y), deslocamento em z do conjunto e centro da fileira de DisplayPort.
    Devolve também a diferença entre o modo pelas âncoras e o modo pela foto."""
    dp = [a["pos"] for a in PARTS["io.board.dp"]["anchors"]]
    yc_a = float(np.mean([p[1] for p in dp]))
    zc_a = float(np.mean([p[2] for p in dp]))
    tip_a = yc_a - M("dp_row_from_bracket_tip")
    dz_a = zc_a - M("dp_row_center_z")
    tip_f = M("card_envelope_height") - M("bracket_top_below_shroud_top") - M("bracket_height_overall")
    diff = {"y_tip_ancoras_menos_foto": round(tip_a - tip_f, 3), "dz_ancoras_menos_foto": round(dz_a, 3)}
    if MODE == "ancoras":
        return tip_a, dz_a, yc_a, zc_a, diff
    return tip_f, 0.0, tip_f + M("dp_row_from_bracket_tip"), M("dp_row_center_z"), diff


Y_TIP, DZ, DP_YC, DP_ZC, MODE_DIFF = io_placement()
# Achado 17 (visual-qa, 2026-11-11): a ponta das línguas sai da norma (aba a br_flange_above_contacts
# acima da borda dos contatos), nos dois modos. As aberturas dos DisplayPort continuam nas âncoras
# de io.board.dp (DP_Y); enquanto o contrato não mudar, a fileira fica DP_ROW_SHIFT acima do lugar
# que sr-1 dá dentro do bracket (dp_row_from_bracket_tip). Mudança proposta no relatório.
Y_TIP_ROW = Y_TIP                                       # ponta que a fileira (sr-1) e o modo implicam
Y_TIP = g("br_flange_above_contacts") - M("bracket_height_overall")
DP_ROW_SHIFT = (DP_YC - Y_TIP) - M("dp_row_from_bracket_tip")
MODE_DIFF["y_tip_norma_menos_modo"] = round(Y_TIP - Y_TIP_ROW, 3)
MODE_DIFF["fileira_dp_acima_de_sr1_no_bracket"] = round(DP_ROW_SHIFT, 3)
BR_Z0 = T - (M("bracket_slot_width_single") + M("pcie_slot_pitch")) + DZ     # borda do lado da face B
BR_Z1 = T + DZ                                                              # borda do lado da face A
PITCH = M("dp_port_pitch")
DP_Y = [DP_YC + (k - 1.5) * PITCH for k in range(4)]


def bz(z_rel):
    """z medido em sr-1 (bracket de z = 1,26 a 40 no modo foto) para o z do modelo."""
    return z_rel + DZ


def by(y_rel):
    return Y_TIP + y_rel


# ---------------------------------------------------------------------------
# io.bracket e fasteners.e1_bracket
# ---------------------------------------------------------------------------
def dp_shape(cu, cv, w, h, ch, r):
    """Forma de DisplayPort no plano (y, z): retângulo com o canto (-y, +z) chanfrado."""
    pts = [(cu - w / 2, cv - h / 2), (cu + w / 2, cv - h / 2), (cu + w / 2, cv + h / 2),
           (cu - w / 2 + ch, cv + h / 2), (cu - w / 2, cv + h / 2 - ch)]
    return round_poly(pts, [r, r, r, r * 0.5, r * 0.5], 4)


def build_bracket():
    pid = "io.bracket"
    t = M("bracket_thickness")
    L = M("bracket_height_overall")
    (u0, u1), (l0, l1) = g("br_tongue_z")
    tl_b, tl_a = g("br_tongue_len")
    n0, n1, nz0, nz1 = g("br_notch")
    zl0, zl1 = g("br_label_zone_z")
    p0, p1 = g("br_panel_y0"), g("br_panel_y1")
    zb0 = BR_Z0 - DZ          # 1,26 no referencial de sr-1
    prof = [(0, u0), (tl_b, u0), (tl_b, zl0), (p0 - (zl0 - zb0), zl0), (p0, zb0), (L, zb0), (L, T),
            (p0, T), (p0 - (T - zl1), zl1), (tl_a, zl1), (tl_a, l1), (0, l1), (0, l0), (n0, l0),
            (n1, nz1), (n1, nz0), (n0, u1), (0, u1)]
    rad = [g("br_corner_r")] * len(prof)
    prof = round_poly([(by(y), bz(z)) for y, z in prof], rad, 4)
    plate = prism_x(prof, -t, 0.0)

    # painel em relevo para fora, com borda inclinada
    m = g("br_panel_margin")
    rel = g("br_panel_relief")
    pan = rrect(by(p0), by(p1), bz(zb0 + m), bz(T - m), 2.0, 5)
    pan_out = rrect(by(p0) + rel, by(p1) - rel, bz(zb0 + m) + rel, bz(T - m) - rel, 2.0 - rel, 5)
    panel = extrude(face_on(pan_out, Plane.YZ.offset(-t - rel)), rel + 0.01, dir=(1, 0, 0), taper=-45)
    body = plate + panel
    x_out = -t - rel                                        # face externa do painel

    # dobra da ponta de cima (para +x), contida no recuo da placa de extremidade da carcaça
    fl = M("shroud_end_plate_recess") - g("br_flange_clear")
    yt = by(L)
    fz0 = max(bz(zb0) + 0.3, M("layer_end_face_b_grid") + g("br_flange_clear"))
    fz1 = min(bz(T) - 0.3, T - M("shroud_face_a_plate_thickness") - g("br_flange_clear"))
    flange = round_poly([(-t, fz0), (fl, fz0), (fl, fz1), (-t, fz1)], [0, 0.5, 0.5, 0], 3)
    body = body + prism_y([(x, z) for x, z in flange], yt - t, yt)
    c = g("br_bend_chamfer")
    body = body - prism_z([(-t - 0.01, yt - c), (-t - 0.01, yt + 0.01), (-t + c, yt + 0.01)], -5, T + 5)
    note(pid, "dobra da ponta de cima para +x (lado da placa) com %.2f mm além do plano do bracket, dentro do recuo da placa de extremidade (shroud_end_plate_recess) e entre a grade da face B e a chapa da face A: sr-1 e gn-11 mostram a dobra de perfil, sem a aba de parafuso de um bracket de norma; se a aba real for mais longa, a carcaça precisa de rasgo" % fl)

    # aberturas dos DisplayPort
    ow, oh = g("br_dp_open")
    for y in DP_Y:
        body = body - prism_x(dp_shape(y, DP_ZC, ow, oh, g("br_dp_chamfer"), g("br_dp_open_r")), -5, 1)
    # etiquetas como áreas planas
    lt = g("label_t")
    for name, kind, ya, yb, za, zb in g("labels"):
        lab = rrect(by(ya), by(yb), bz(za), bz(zb), 0.6, 3)
        body = body + prism_x(lab, x_out - lt, x_out + 0.05)
        zone(pid, name, "etiqueta_" + kind, plane_x=x_out - lt, y=[by(ya), by(yb)], z=[bz(za), bz(zb)])
    ya, yb, za, zb = g("regulatory_zone")
    zone(pid, "marcas_regulatorias", "serigrafia_branca", plane_x=-t, y=[by(ya), by(yb)], z=[bz(za), bz(zb)])
    zone(pid, "chapa", "aco_pintado_preto_fosco", note="todo o resto da peça")
    note(pid, "contorno: comprimento e espessura da norma (bracket_height_overall, bracket_thickness), largura de dois slots por conta; línguas, entalhe, painel, aberturas e etiquetas medidos em sr-1")
    note(pid, "posição em y pela norma (br_flange_above_contacts, CEM 3.0 Fig. 9-3): ponta das línguas em y = %.2f (%.2f além da borda dos contatos), ponta de cima em %.2f (%.2f abaixo do topo da carcaça; bracket_top_below_shroud_top = %.1f no CSV); o modo %s dava a ponta em %.2f" % (
        Y_TIP, -Y_TIP, Y_TIP + L, M("card_envelope_height") - Y_TIP - L, M("bracket_top_below_shroud_top"), MODE, Y_TIP_ROW))
    if abs(DP_ROW_SHIFT) > 0.05:
        note(pid, "aberturas dos DisplayPort nas âncoras de io.board.dp: centro da fileira a %.2f da ponta das línguas, %.2f acima dos %.2f de sr-1 (dp_row_from_bracket_tip); some quando as âncoras descerem para y = ponta + dp_row_from_bracket_tip (mudança de contrato pedida)" % (
            DP_YC - Y_TIP, DP_ROW_SHIFT, M("dp_row_from_bracket_tip")))
    note(pid, "painel em relevo de %.1f mm para fora com borda inclinada (palpite de forma: a borda aparece em sr-1 e gn-11)" % rel)
    return body


def build_screws():
    pid = "fasteners.e1_bracket"
    d, h = g("screw_head")
    rd, rdep = g("screw_recess")
    x_out = -M("bracket_thickness") - g("br_panel_relief")      # cabeça apoiada no painel
    out = []
    for yr, zr in g("br_screws"):
        cy, cz = by(yr), bz(zr)
        n = 36
        head = prism_x(circle(cy, cz, d / 2, n), x_out - h + 0.45, x_out)
        head = head + prism_x(circle(cy, cz, d / 2 - 0.5, n), x_out - h + 0.1, x_out - h + 0.46)
        head = head + prism_x(circle(cy, cz, d / 2 - 1.0, n), x_out - h, x_out - h + 0.11)
        star = []
        for k in range(12):
            a = math.pi / 6 * k + math.pi / 12
            rr = rd / 2 if k % 2 == 0 else rd / 2 * 0.62
            star.append((cy + rr * math.cos(a), cz + rr * math.sin(a)))
        star = round_poly(star, 0.12, 2)
        head = head - prism_x(star, x_out - h - 1, x_out - h + rdep)
        out.append(head)
    zone(pid, "cabecas", "aco_oxidado_preto")
    note(pid, "4 cabeças de panela com fenda hexalobular nas posições de sr-1; diâmetro %.1f (sr-1), altura %.1f e perfil em degraus (palpite); sem corpo roscado (escondido)" % (d, h))
    return out


# ---------------------------------------------------------------------------
# io.board e io.board.dp
# ---------------------------------------------------------------------------
def build_io_board():
    pid = "io.board"
    x0 = M("dp_receptacle_depth")
    x1 = x0 + M("pcb_thickness")
    cl = g("io_board_clear")
    ylo, yhi = Y0 + WALL + cl, Y1 - WALL - cl
    zlo = M("layer_end_face_b_grid") + cl
    zhi = T - M("layer_end_fan_ring") - cl
    Lb, Sb = M("io_board_outline_long"), M("io_board_outline_short")
    y0, y1 = max(DP_YC - Lb / 2, ylo), min(DP_YC + Lb / 2, yhi)
    z0, z1 = max(DP_ZC - Sb / 2, zlo), min(DP_ZC + Sb / 2, zhi)
    a = PARTS[pid]["anchors"][0]["pos"]
    y0, y1 = min(y0, a[1] - 1), max(y1, a[1] + 1)
    z0, z1 = min(z0, a[2] - 1), max(z1, min(a[2] + 1, zhi))
    board = prism_x(rrect(y0, y1, z0, z1, 1.5, 4), x0, x1)
    for yy in (y0 + 3.5, y1 - 3.5):
        for zz in (z0 + 3.0, z1 - 3.0):
            board = board - prism_x(circle(yy, zz, 1.1, 16), x0 - 1, x1 + 1)
    zone(pid, "placa", "pcb_mascara_preta")
    note(pid, "forma ilustrativa (D6, sem foto): placa normal a x atrás dos receptáculos, de y %.1f a %.1f e z %.1f a %.1f, limitada pela parede interna, pela grade da face B e pelo duto do ventilador 1; 4 furos de fixação de palpite" % (y0, y1, z0, z1))
    return board


def build_dp():
    pid = "io.board.dp"
    W, H, D = M("dp_receptacle_width"), M("dp_receptacle_height"), M("dp_receptacle_depth")
    st = g("dp_shell_t")
    ch = g("dp_shell_chamfer")
    tw, tt = g("dp_tongue")
    cw = g("dp_contact_w")
    pitch = M("dp_contact_pitch")
    out = []
    for y in DP_Y:
        zc = DP_ZC
        shell = prism_x(dp_shape(y, zc, W, H, ch, 0.5), 0.0, D)
        shell = shell - prism_x(dp_shape(y, zc, W - 2 * st, H - 2 * st, ch - st * 0.6, 0.3), -1.0, g("dp_cavity_depth"))
        # língua de contatos presa ao fundo, deslocada para o lado sem chanfro (-z)
        tz = zc - 0.35
        tongue = box(1.2, g("dp_cavity_depth") + 0.01, y - tw / 2, y + tw / 2, tz - tt / 2, tz + tt / 2)
        for k in range(10):
            yy = y + (k - 4.5) * pitch
            for s in (-1, 1):
                z_face = tz + s * tt / 2
                tongue = tongue + box(1.6, g("dp_cavity_depth") - 0.2, yy - cw / 2, yy + cw / 2,
                                      min(z_face, z_face + s * 0.06), max(z_face, z_face + s * 0.06))
        out.append(shell + tongue)
    zone(pid, "casca", "aco_niquelado")
    zone(pid, "lingua", "plastico_preto")
    zone(pid, "contatos", "dourado", note="20 contatos, 10 por face da língua, passo dp_contact_pitch")
    note(pid, "receptáculo pelas cotas do CSV (%.2f x %.2f x %.2f), boca de %.1f mm, casca de %.1f, chanfro do canto (-y, +z) e língua com 20 contatos: forma de norma sem desenho aberto (palpites em G)" % (W, H, D, g("dp_cavity_depth"), st))
    dev = max(abs(y - a["pos"][1]) for y, a in zip(DP_Y, PARTS[pid]["anchors"]))
    note(pid, "centros da fileira: y %s, z %.2f (dp_row_center_z), passo dp_port_pitch (%.1f, arbitragem); maior distância às âncoras em y: %.3f mm" % (
        ", ".join("%.2f" % v for v in DP_Y), DP_ZC, PITCH, dev))
    return out


# ---------------------------------------------------------------------------
# pcie.adapter
# ---------------------------------------------------------------------------
# Contorno em am_adapter (xi, yi em mm da grade): xi cresce para a borda dos contatos, yi cresce
# para o lado do bracket. Borda dos contatos em xi 282,6; ponta do lado do bracket em yi 116,5.
AD_EDGE_XI, AD_END_YI = 282.6, 116.5
AD_IMG = [
    (282.6, 116.5), (282.6, 30.3), (280.0, 30.3), (280.0, 29.6), (273.9, 29.6), (273.9, 27.0),
    (280.0, 27.0), (280.0, 16.8), (278.0, 14.3), (274.1, 14.3), (274.1, 20.0), (247.5, 20.0),
    (246.05, 21.5), (246.05, 33.5),
    # lóbulo e diagonal (bordas medidas linha a linha na máscara, passo de 1 mm)
    (245.7, 34), (245.08, 35), (244.45, 36), (243.91, 37), (243.36, 38), (242.97, 39), (242.6, 40),
    (242.73, 41), (243.05, 42), (243.5, 43), (244.3, 44), (245.2, 45), (246.2, 46), (247.27, 47),
    (248.2, 48), (249.22, 49), (250.15, 50), (251.17, 51), (252.19, 52), (253.12, 53), (254.1, 54),
    (255.1, 55), (256.1, 56), (257.1, 57), (258.0, 58), (259.1, 59), (260.08, 60), (261.0, 61),
    (261.9, 62), (262.6, 63), (263.1, 64), (263.5, 65), (263.8, 66), (264.0, 67), (264.15, 69),
    (264.15, 115.3), (265.4, 116.5)]
AD_RING_HOLES = [(249.1, 23.1), (261.1, 23.1), (249.4, 42.6), (261.4, 55.1)]
AD_LOBE_HOLE = (245.2, 38.5)
AD_STRIP_HOLES = [(266.95, 76.8), (266.95, 112.3)]
AD_J3_IMG = (255.35, 37.55)          # centro do J3 na foto
AD_GOLD = ((114.5, 103.5), (101.6, 30.3))   # grupos de contatos (yi), curto e longo
AD_KEY_YI = 102.55


AD_STRIP_XI, AD_TAB_XI = 264.15, 246.05            # borda da faixa e topo da aba sem o lóbulo
AD_H_IMG = (AD_EDGE_XI - AD_STRIP_XI, AD_EDGE_XI - AD_TAB_XI, AD_EDGE_XI - min(p[0] for p in AD_IMG))


def ad_xform():
    """Grade de am_adapter para o modelo: escala única em x (pcie_adapter_length) a partir do J3
    (iface_j3_center_x) e mapa linear por trechos na altura, que leva a faixa, a aba sem o lóbulo
    e o lóbulo às alturas da arbitragem."""
    s_u = M("pcie_adapter_length") / (AD_END_YI - 14.3)
    h_csv = (M("pcie_adapter_strip_height"), M("pcie_adapter_total_height_without_lobe"), M("pcie_adapter_total_height"))
    x0 = M("iface_j3_center_x") - (AD_END_YI - AD_J3_IMG[1]) * s_u

    def f(xi, yi):
        return (x0 + (AD_END_YI - yi) * s_u, float(np.interp(AD_EDGE_XI - xi, (0.0,) + AD_H_IMG, (0.0,) + h_csv)))
    return f, s_u, h_csv, x0


def adapter_outline_xy():
    """Contorno do adaptador no plano xy do modelo (sem arredondar), para a carcaça e o blockout."""
    f = ad_xform()[0]
    return [f(*p) for p in AD_IMG]


def adapter_holes():
    """Furos do CSV: 4 com anel (presilha), 1 no lóbulo, 2 na faixa, como (x, y, diâmetro, tipo)."""
    hd, rd, lobe_d, sd = g("ad_holes")
    out = [(M("iface_adapter_ring_hole_%d_x" % k), M("iface_adapter_ring_hole_%d_y" % k), hd, "anel") for k in (1, 2, 3, 4)]
    out.append((M("iface_adapter_lobe_hole_x"), M("iface_adapter_lobe_hole_y"), lobe_d, "lobulo"))
    out += [(M("iface_adapter_strip_hole_%d_x" % k), M("iface_adapter_strip_hole_%d_y" % k), sd, "faixa") for k in (1, 2)]
    return out


def poly_edge_dist(pts, q):
    P = np.asarray(pts, float)
    best = np.inf
    for a, b in zip(P, np.roll(P, -1, axis=0)):
        e = b - a
        t = np.clip(np.dot(q - a, e) / max(np.dot(e, e), 1e-12), 0, 1)
        best = min(best, float(np.linalg.norm(a + t * e - q)))
    return best


CONFLICTS = []


def build_adapter():
    pid = "pcie.adapter"
    f, s_u, h_csv, x0 = ad_xform()
    za = M("iface_adapter_board_z_min")
    zb = za + M("pcb_thickness")
    assert abs(zb - M("iface_adapter_board_z_max")) < 0.02, "espessura do adaptador fora do contrato"
    pts = [f(*p) for p in AD_IMG]
    raw = list(pts)
    xmin, xmax = min(p[0] for p in pts), max(p[0] for p in pts)
    for k, v in (("iface_adapter_x_min", xmin), ("iface_adapter_x_max", xmax)):
        if abs(v - M(k)) > 0.05:
            CONFLICTS.append({"peca": pid, "tema": k, "modelo": round(v, 3), "csv": M(k), "dono": "assembly-planner"})
    rad = [0.5] * len(pts)
    pts = round_poly(pts, rad, 3)
    board = prism_z(pts, za, zb)
    # chave entre os grupos de contatos
    kw, kd = g("ad_key")
    kx = f(0, AD_KEY_YI)[0]
    key = round_poly([(kx - kw / 2, -1), (kx + kw / 2, -1), (kx + kw / 2, kd), (kx - kw / 2, kd)], [0, 0, kw / 2 - 0.01, kw / 2 - 0.01], 6)
    board = board - prism_z(key, za - 1, zb + 1)
    # furos
    hd, rd, lobe_d, sd = g("ad_holes")
    rt = g("ad_ring_t")
    holes = [((hx, hy), d) for hx, hy, d, _ in adapter_holes()]
    for (hx, hy), d in holes:
        dist = poly_edge_dist(raw, np.array([hx, hy]))
        margin = dist - d / 2
        if margin < 0.3:
            CONFLICTS.append({"peca": pid, "tema": "furo de %.1f mm em (%.2f; %.2f) a %.2f mm da borda (folga mínima de 0,3)" % (d, hx, hy, margin),
                              "dono": "visual-qa, assembly-planner",
                              "motivo": "furo do CSV (iface_adapter_*_hole_*, escala / 1,013 a partir do J3) contra o contorno com as alturas arbitradas (pcie_adapter_total_height = %.1f); as duas medidas vêm da mesma foto com correções diferentes" % M("pcie_adapter_total_height")})
    # anéis de cobre nas duas faces
    for (cx, cy), _ in holes[:4]:
        ring = circle(cx, cy, rd / 2, 28)
        board = board + prism_z(ring, zb - 0.01, zb + rt) + prism_z(ring, za - rt, za + 0.01)
    for (cx, cy), d in holes:
        board = board - prism_z(circle(cx, cy, d / 2, 24), za - 1, zb + 1)
    # contatos dourados nas duas faces
    pw, py0, py1 = g("ad_pad")
    pt = g("ad_pad_t")
    pads = []
    for (ya, yb) in AD_GOLD:
        xa, xb = f(0, ya)[0], f(0, yb)[0]
        n = int(round(xb - xa))
        n = 11 if n <= 12 else 71
        start = (xa + xb) / 2 - (n - 1) / 2 * M("edge_finger_pitch")
        for k in range(n):
            pads.append(start + k * M("edge_finger_pitch"))
    pad_shapes = []
    for px in pads:
        for z0, z1 in ((zb - 0.01, zb + pt), (za - pt, za + 0.01)):
            pad_shapes.append(box(px - pw / 2, px + pw / 2, py0, py1, z0, z1))
    board = board + Compound(pad_shapes)
    # chanfro da borda de inserção, só na zona dos contatos
    bv = g("ad_bevel")
    fx0, fx1 = f(0, AD_END_YI)[0] - 1, f(0, AD_GOLD[1][1])[0] + 0.3
    for w in ([(-0.01, zb + pt + 0.01), (bv, zb + pt + 0.01), (-0.01, zb + pt - bv)],
              [(-0.01, za - pt - 0.01), (bv, za - pt - 0.01), (-0.01, za - pt + bv)]):
        board = board - prism_x(w, fx0, fx1)
    # conector J3 de placa a placa (face do lado do PCB)
    jx, jy = M("iface_j3_center_x"), M("iface_j3_center_y")
    jl, jw, jh = M("pcie_adapter_connector_length"), g("j3_width"), M("iface_j3_mating_z") - zb
    sl, sw_, sdp = g("j3_slot")
    nc, cp, cw = g("j3_contacts")
    j3 = prism_z(round_poly([(jx - jl / 2, jy - jw / 2), (jx + jl / 2, jy - jw / 2), (jx + jl / 2, jy + jw / 2), (jx - jl / 2, jy + jw / 2)], 0.6, 3), zb - 0.01, zb + jh)
    j3 = j3 - prism_z(round_poly([(jx - sl / 2, jy - sw_ / 2), (jx + sl / 2, jy - sw_ / 2), (jx + sl / 2, jy + sw_ / 2), (jx - sl / 2, jy + sw_ / 2)], 0.3, 2), zb + jh - sdp, zb + jh + 1)
    cts = []
    for k in range(int(nc)):
        cx = jx - (nc - 1) / 2 * cp + k * cp
        for s in (-1, 1):
            cts.append(box(cx - cw / 2, cx + cw / 2, jy + s * sw_ / 2 - (0.35 if s > 0 else 0), jy + s * sw_ / 2 + (0 if s > 0 else 0.35),
                           zb + jh - sdp - 0.01, zb + jh - sdp + 0.5))
    j3 = j3 + Compound(cts)
    body = board + j3
    zone(pid, "placa", "pcb_mascara_preta")
    zone(pid, "contatos", "dourado", y=[py0, py1], x=[min(pads) - pw / 2, max(pads) + pw / 2], note="%d por face, nas duas faces" % len(pads))
    zone(pid, "aneis", "cobre", centers=[h[0] for h in holes[:4]])
    zone(pid, "j3_corpo", "plastico_preto", x=[jx - jl / 2, jx + jl / 2], y=[jy - jw / 2, jy + jw / 2])
    zone(pid, "j3_contatos", "dourado")
    note(pid, "contorno da foto retificada do Chiphell (am_adapter) com o comprimento (pcie_adapter_length, %.1f) e as alturas da arbitragem (faixa %.1f, sem lóbulo %.1f, com lóbulo %.1f): escala única em x e mapa linear por trechos na altura (a grade dava %.2f, %.2f e %.2f); sem o fator antigo de 0,9439" % (
        M("pcie_adapter_length"), *h_csv, *AD_H_IMG))
    note(pid, "posição em x pelo J3 em iface_j3_center_x (interface com o receptáculo do verso do PCB): placa de x = %.2f a %.2f (iface_adapter_x_min e _max: %.2f e %.2f); contatos de x = %.2f a %.2f (%d por face, passo edge_finger_pitch)" % (
        xmin, xmax, M("iface_adapter_x_min"), M("iface_adapter_x_max"), min(pads) - pw / 2, max(pads) + pw / 2, len(pads)))
    note(pid, "no plano da pcb.plate: placa de z = %.2f a %.2f (iface_adapter_board_z_min e _max)" % (za, zb))
    note(pid, "J3 centrado em (iface_j3_center_x, iface_j3_center_y); a grade da foto põe o centro em y = %.2f com o mapa da altura" % f(*AD_J3_IMG)[1])
    note(pid, "plugue do J3 de %.2f mm, até o plano de encaixe iface_j3_mating_z (%.2f); o receptáculo fica em pcb.smd, de %.2f até o verso do PCB (%.2f); divisão da altura sem fonte" % (
        jh, M("iface_j3_mating_z"), M("iface_j3_mating_z"), M("iface_pcb_back_z")))
    note(pid, "furos: 4 com anel de cobre (presilha, gn-25), 1 no lóbulo, 2 na faixa (fixação, gn-22), nas linhas iface_adapter_*_hole_* do CSV: centros em %s" % ", ".join("(%.2f; %.2f)" % h[0] for h in holes))
    for c in CONFLICTS:
        if c["peca"] == pid:
            note(pid, "CONFLITO DE INTERFACE (não corrigido): %s; dono: %s" % (c["tema"], c["dono"]))
    return body, holes


# ---------------------------------------------------------------------------
# power.connector
# ---------------------------------------------------------------------------
def build_power_connector():
    pid = "power.connector"
    w = g("p16_across")
    d = M("power_connector_body_depth")
    H = M("power_connector_body_height_z")
    assert abs(H - M("conn16_header_width")) < 1e-6
    z0 = M("iface_pcb_front_z")
    zc = z0 + H / 2
    sw = M("power_connector_body_across") - w          # faixa dos 4 pinos de sinal
    # corpo principal no referencial local: X = direção de encaixe, Y = através das fileiras
    body = box(-d / 2, d / 2, -w / 2, w / 2, z0, z0 + H)
    sl = g("p16_sense_len_z")
    body = body + box(-d / 2, d / 2, w / 2 - 0.01, w / 2 + sw, zc - sl / 2, zc + sl / 2)
    # cavidades de potência: 2 fileiras (Y = +-1,5) x 6 posições ao longo de z
    pp = M("conn16_power_pin_pitch")
    span = M("conn16_power_pin_span")
    cs, cdep = g("p16_cavity")
    pin = g("p16_pin")
    pins = []
    for col in (-0.5, 0.5):
        yy = col * pp
        for k in range(6):
            zz = zc - span / 2 + k * span / 5
            cav = round_poly([(yy - cs / 2, zz - cs / 2), (yy + cs / 2, zz - cs / 2), (yy + cs / 2, zz + cs / 2), (yy - cs / 2, zz + cs / 2)],
                             [0.15, 0.15, 0.55 if col > 0 else 0.15, 0.55 if col < 0 else 0.15], 2)
            body = body - prism_x(cav, d / 2 - cdep, d / 2 + 1)
            pins.append(box(d / 2 - cdep - 0.01, d / 2 - 1.0, yy - pin / 2, yy + pin / 2, zz - pin / 2, zz + pin / 2))
    # cavidades de sinal: 4, passo conn16_sense_pin_pitch, na faixa lateral
    sp = M("conn16_sense_pin_pitch")
    scs, sdep, spin = g("p16_sense_cavity")
    ys = w / 2 + sw / 2
    for k in range(4):
        zz = zc + (k - 1.5) * sp
        body = body - box(d / 2 - sdep, d / 2 + 1, ys - scs / 2, ys + scs / 2, zz - scs / 2, zz + scs / 2)
        pins.append(box(d / 2 - sdep - 0.01, d / 2 - 0.8, ys - spin / 2, ys + spin / 2, zz - spin / 2, zz + spin / 2))
    # trava (rampa) na face externa da faixa de sinal, perto da boca
    lz, ll, lh = g("p16_latch")
    yo = w / 2 + sw
    ramp = [(d / 2 - 0.4 - ll, yo - 0.01), (d / 2 - 0.4, yo - 0.01), (d / 2 - 0.4, yo + lh)]
    body = body + prism_z(ramp, zc - lz / 2, zc + lz / 2)
    # lâminas de saída (uma por fileira) e base atrás do corpo
    bt, reach = g("p16_blade")
    bl, bh = g("p16_base")
    blades = []
    for col in (-0.5, 0.5):
        yy = col * pp
        prof = [(-d / 2 + 0.01, z0 + H - 1.5), (-d / 2 - 1.2, z0 + H - 1.5), (-d / 2 - reach, z0 + 0.0),
                (-d / 2 - reach + 2.2, z0 + 0.0), (-d / 2 + 0.01, z0 + H - 4.2)]
        blades.append(prism_y(prof, yy - bt / 2, yy + bt / 2))
    base = box(-d / 2 - bl, -d / 2 + 0.01, -pp / 2 - bt / 2 - 0.6, pp / 2 + bt / 2 + 0.6, z0, z0 + bh)
    local = Pos(0, -sw / 2, 0) * (body + base + Compound(blades) + Compound(pins))   # corpo de 9,7 centrado
    ang = M("power_connector_rotation_deg") + 90.0
    cx, cy = M("power_connector_center_from_bracket_end"), M("power_connector_center_y")
    shape = Pos(cx, cy, 0) * Rot(0, 0, ang) * local
    zone(pid, "corpo", "plastico_preto")
    zone(pid, "pinos", "estanhado", note="12 de potência e 4 de sinal, dentro das cavidades")
    zone(pid, "laminas", "estanhado")
    note(pid, "orientação decidida pelas fotos: o lado longo do cabeçote (conn16_header_width, %.2f) fica em z, perpendicular ao PCB; as duas fileiras de 6 ficam lado a lado no plano do PCB, através do chanfro, e a face de encaixe aponta para (+x, +y) a %.0f graus de +x. Fontes: furos no PCB do Chiphell (um furo alongado por fileira e os 4 de sinal em linha, todos na direção de encaixe), sabareesh (corpo alto, duas tiras metálicas lado a lado), pny/3qtr-top-right (lado longo em z na abertura) e a 5090 (pcgamesn-pcb-power)" % (H, ang))
    note(pid, "corpo de %.2f através (power_connector_body_across: %.2f das fileiras de potência mais %.2f da faixa de sinal) x %.2f na direção de encaixe (power_connector_body_depth) x %.2f de altura (power_connector_body_height_z, de z = %.1f a %.2f), centrado em (%.2f; %.2f) (power_connector_center_from_bracket_end, power_connector_center_y); centro da face de encaixe em (%.2f; %.2f; %.2f)" % (
        w + sw, w, sw, d, H, z0, z0 + H, cx, cy, cx + d / 2 * math.cos(math.radians(ang)), cy + d / 2 * math.sin(math.radians(ang)), zc))
    note(pid, "faixa dos 4 pinos de sinal e trava do lado (-x, +y); lâminas e base atrás do corpo: forma de palpite")
    note(pid, "power_connector_rotation_deg (%.0f) passa a ser lido como o eixo através das fileiras, não como a fileira de 6: a direção de encaixe continua a 45 graus" % M("power_connector_rotation_deg"))
    return shape


# ---------------------------------------------------------------------------
# Malha, GLB e conferências
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


COLORS = {"io.bracket": [0.05, 0.05, 0.055], "fasteners.e1_bracket": [0.04, 0.04, 0.045], "io.board": [0.06, 0.08, 0.06],
          "io.board.dp": [0.62, 0.63, 0.65], "pcie.adapter": [0.07, 0.09, 0.08], "power.connector": [0.05, 0.05, 0.05]}


def write_glb(path, pid, nodes_spec, root_extras):
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
        "asset": {"version": "2.0", "generator": "harness/parts/io_parts.py", "extras": root_extras},
        "scene": 0, "scenes": [{"name": nodes_spec[0][0], "nodes": [0]}], "nodes": nodes, "meshes": meshes,
        "materials": [{"name": pid, "pbrMetallicRoughness": {"baseColorFactor": COLORS[pid] + [1.0],
                                                             "metallicFactor": 0.0, "roughnessFactor": 0.7}}],
        "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}],
    }
    js = json.dumps(gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    js += b" " * (-len(js) % 4)
    binary = bytes(buf) + b"\0" * (-len(buf) % 4)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binary)))
        fh.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        fh.write(struct.pack("<II", len(binary), 0x004E4942) + binary)


def anchor_check(pid, mesh):
    sys.path.insert(0, str(HERE))
    import frame as FR
    return FR.anchor_check(pid, mesh) if PARTS[pid]["anchors"] else []


FEATURE_PROV = {
    "io.bracket": {"comprimento e espessura": "confirmed (CEM 3.0, Fig. 9-5)", "largura de dois slots": "derived (conta 18,42 + 20,32)",
                   "línguas, entalhe, painel, aberturas, etiquetas": "derived (storagereview/sr-1)",
                   "posição na placa": "confirmed (CEM 3.0 Fig. 9-3: aba a 104,86 da borda dos contatos; conferida em pny/front e pny/back); z pela arbitragem (dp_row_center_z)",
                   "relevo do painel e dobra da ponta": "inferred"},
    "fasteners.e1_bracket": {"quantidade e posição": "derived (sr-1, gn-11)", "diâmetro da cabeça": "derived (sr-1)", "altura e fenda": "inferred"},
    "io.board": {"forma": "illustrative (D6)"},
    "io.board.dp": {"cotas do receptáculo": "derived (fonte secundária, CSV)", "passo dos contatos": "confirmed (Molex)",
                    "passo das portas": "derived (arbitragem, CSV)", "posição da fileira": "derived (arbitragem: dp_row_center_z e âncoras do assembly; os dois modos coincidem)",
                    "casca, chanfro, língua": "inferred"},
    "pcie.adapter": {"comprimento, alturas, J3, furos": "derived (CSV: arbitragem e contrato de 2026-11-11, chiphell/pcb-a)", "contorno, lóbulo, gancho, rasgo": "derived (am_adapter, gn-25)",
                     "plano em z": "inferred (iface_adapter_board_z_min, escolha de contrato)",
                     "passo e número dos contatos": "confirmed (CEM 3.0)", "chave": "derived (gn-25)", "altura do J3, chanfro, relevos": "inferred"},
    "power.connector": {"passos e largura do cabeçote": "confirmed (Intel 613768, CEM 5.1)", "posição e ângulo de encaixe": "derived (CSV)",
                        "profundidade do corpo": "derived (power_connector_body_depth)", "espessura através": "inferred (power_connector_body_across)",
                        "orientação (lado longo em z)": "derived (chiphell/ab_conn, sabareesh, pny/3qtr-top-right, 5090; nesta tarefa)",
                        "espessura, profundidade, cavidades, trava, lâminas": "inferred"},
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # --pecas=id1,id2 gera só essas peças e atualiza só as entradas delas no io-report.json
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--pecas=")), None)
    builders = {
        "io.bracket": lambda: [build_bracket()],
        "fasteners.e1_bracket": build_screws,
        "io.board": lambda: [build_io_board()],
        "io.board.dp": build_dp,
        "pcie.adapter": lambda: [build_adapter()[0]],
        "power.connector": lambda: [build_power_connector()],
    }
    shapes = {pid: f() for pid, f in builders.items() if only is None or pid in only}
    report = {"mode": MODE, "parts": {}, "guess_values": {k: {"value": v[0], "provenance": v[1], "note": v[2]} for k, v in G.items()},
              "placement": {"y_tip": round(Y_TIP, 3), "dz": round(DZ, 3), "dp_row_center_y": round(DP_YC, 3), "dp_row_z": round(DP_ZC, 3),
                            "dp_y": [round(v, 3) for v in DP_Y], "bracket_z": [round(BR_Z0, 3), round(BR_Z1, 3)],
                            "diferenca_entre_modos": MODE_DIFF}}
    total = 0
    all_ok = True
    for pid, sh in shapes.items():
        p = PARTS[pid]
        meshes = [to_mesh(s) for s in sh]
        mesh = trimesh.util.concatenate(meshes)
        ntri = int(len(mesh.faces))
        total += ntri
        closed = [bool(m.is_watertight and m.is_winding_consistent and m.volume > 0) for m in meshes]
        lo, hi = mesh.bounds
        anchors = anchor_check(pid, mesh)
        extras = {"id": pid, "stage": p["stage"], "fidelity": p["fidelity"], "exists_provenance": p["exists_provenance"],
                  "shape_provenance": p["shape_provenance"], "shape_provenance_features": FEATURE_PROV[pid],
                  "guess": True, "guess_notes": NOTES.get(pid, []), "material_zones_cad_mm": ZONES.get(pid, []),
                  "blockout": False, "units_cad": "mm", "up_cad": "+Z", "origin": "card.envelope_min",
                  "referencial": "face B em z = 0, face A (ventiladores) em z = card_thickness", "explode_cad": p["explode"],
                  "placement_mode": MODE}
        spec = []
        if len(meshes) == 1 and "count" not in p:
            spec.append((pid, extras, meshes[0], None, None))
        else:
            extras["count"] = p["count"]["value"]
            extras["count_provenance"] = p["count"]["provenance"]
            spec.append((pid, extras, None, None, None))
            for k, m in enumerate(meshes, 1):
                spec.append(("%s.%d" % (pid, k), {"instance_of": pid, "instance": k, "stage": p["stage"], "guess": True}, m, None, 0))
        for a in p["anchors"]:
            spec.append((a["id"], {"anchor": True, "part": pid}, None, to_gltf([a["pos"]])[0], 0))
        glb = OUT / ("%s.glb" % pid)
        write_glb(glb, pid, spec, {"units": "m", "up": "+Y", "cad_units": "mm", "cad_up": "+Z", "origin": "card.envelope_min",
                                   "map": "gltf = (x, z, -y) / 1000"})
        step = OUT / ("%s.step" % pid)
        comp = sh[0] if len(sh) == 1 else Compound(sh)
        comp.label = pid
        export_step(comp, str(step))
        sc = trimesh.load(glb, force="scene")
        back = sc.to_geometry()
        bl = np.c_[back.vertices[:, 0], -back.vertices[:, 2], back.vertices[:, 1]] * 1000.0
        reread_ok = bool(np.allclose(bl.min(axis=0), lo, atol=0.01) and np.allclose(bl.max(axis=0), hi, atol=0.01))
        report["parts"][pid] = {"triangles": ntri, "vertices": int(len(mesh.vertices)), "bodies": len(meshes), "closed": closed,
                                "bbox_min": lo.round(3).tolist(), "bbox_max": hi.round(3).tolist(), "glb_bytes": glb.stat().st_size,
                                "step_bytes": step.stat().st_size, "glb_reread_bbox_ok": reread_ok, "anchors": anchors,
                                "notes": NOTES.get(pid, []), "zones": ZONES.get(pid, [])}
        all_ok &= all(closed) and reread_ok
        print("%-22s %6d triângulos, %5.0f kB GLB, %5.0f kB STEP, fechada: %s" % (pid, ntri, glb.stat().st_size / 1024, step.stat().st_size / 1024,
                                                                             "sim" if all(closed) else "NÃO %s" % closed))
        print("    caixa: (%.2f, %.2f, %.2f) a (%.2f, %.2f, %.2f)" % (*lo, *hi))
        for a in anchors:
            print("    %-34s dist %6.2f mm %s" % (a["anchor"], a["dist_mm"], "OK" if a["ok"] else "ACIMA DE %.0f mm" % TOL_ANCHOR))
    report["triangle_budget"] = TRI_BUDGET
    report["csv_keys_used"] = sorted(USED)
    report["interface_conflicts"] = CONFLICTS
    if only is not None and (OUT / "io-report.json").exists():
        old = json.loads((OUT / "io-report.json").read_text(encoding="utf-8"))
        old["parts"].update(report["parts"])
        total = sum(v["triangles"] for v in old["parts"].values())
        old["csv_keys_used"] = sorted(set(old.get("csv_keys_used", [])) | USED)
        if "pcie.adapter" not in only:
            report["interface_conflicts"] = old.get("interface_conflicts", [])
        old.update({k: report[k] for k in ("mode", "guess_values", "placement", "triangle_budget", "interface_conflicts")})
        report = old
    report["triangles_total"] = total
    for c in CONFLICTS:
        print("CONFLITO DE INTERFACE (%s): %s; dono: %s" % (c["peca"], c["tema"], c["dono"]))
    all_ok &= total <= TRI_BUDGET
    (OUT / "io-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nModo de posição: %s (ponta das línguas em y = %.2f; fileira de DisplayPort em y = %.2f, z = %.2f); âncoras menos foto: %.3f mm em y, %.3f em z" % (
        MODE, Y_TIP, DP_YC, DP_ZC, MODE_DIFF["y_tip_ancoras_menos_foto"], MODE_DIFF["dz_ancoras_menos_foto"]))
    print("Triângulos no total: %d (orçamento %d) %s" % (total, TRI_BUDGET, "OK" if total <= TRI_BUDGET else "ACIMA"))
    print("Relatório: %s" % (OUT / "io-report.json").relative_to(HARNESS.parent))
    print("Resultado (malhas fechadas, orçamento, releitura): %s" % ("OK" if all_ok else "FALHA"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
