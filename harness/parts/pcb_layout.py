#!/usr/bin/env python3
"""Tabela de posicionamento do PCB principal (F3): harness/parts/pcb/layout.csv.

Uma linha por componente instanciado no PCB principal (pcb.main) da RTX PRO 6000 Blackwell
Workstation Edition: memória das duas faces, package do GB202, indutores, estágios de
potência, controladores, conversores auxiliares, conector auxiliar e os passivos
representativos (pcb.smd). harness/parts/pcb.py instancia a geometria a partir desta
tabela; nenhum componente é modelado um a um.

Referencial (ARCHITECTURE.md, seção 7.6): mm, Z para cima, origem em card.envelope_min;
x a partir do plano do bracket, y a partir da ponta dos contatos PCIe; face B em z = 0 e
face A (ventiladores) em z = 40. O PCB vai de iface_pcb_back_z (verso, voltado para a
face B) a iface_pcb_front_z (frente, com o chip, voltada para a face A). No PCB, (u, v)
contam a partir do canto entre a borda do lado do bracket e a borda dos contatos:
x = pcb_main_card_x_min + u, y = pcb_main_card_y_min + v (assembly-plan, seção 10.2).

Fontes das posições, por ordem de prioridade:
  1. measurements.csv, pela chave (grade da memória, package, furos, faixas dos indutores);
  2. âncoras do assembly.json (memória: conferidas contra a grade do CSV);
  3. medidas tiradas nesta tarefa nas fotos retificadas (G, procedência "derived"):
     visualqa/a_board.png (verso, 10 px/mm, do visual-qa) e chiphell/pcb-b.jpg retificada
     aqui pelos 8 furos (frente; resíduo de 0,2 a 0,8 mm), e a foto sabareesh/wb-bare-pcb;
  4. palpites sem referência (G, "inferred") e o que é só ilustração ("illustrative").

Passivos (pcb.smd): as posições saem das ilhas de cobre do PCB nu (pares de ilhas
parecidas, a 0,5 a 6 mm uma da outra), nas duas faces retificadas; tipo, altura e quantidade
são ilustrativos (a placa montada não foi fotografada de perto nas duas faces). Sem as
imagens do cache (não versionado), a tabela de passivos já gravada é mantida.

Uso:   python3 -I harness/parts/pcb_layout.py [--refazer-passivos]
Saída: harness/parts/pcb/layout.csv
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HARNESS = Path(__file__).resolve().parent.parent
ASSEMBLY = HARNESS / "design" / "assembly.json"
MEASURES = HARNESS / "design" / "measurements.csv"
LAYOUT = HARNESS / "parts" / "pcb" / "layout.csv"
CACHE = HARNESS / "spec" / "references" / "cache"
SCRATCH_FRONT = None          # caminho da frente retificada (gerada por pcb_compare.py)

# ---------------------------------------------------------------------------
# Valores sem linha no CSV: (valor, procedência, nota)
# ---------------------------------------------------------------------------
G = {
    # contorno e furos (medidos nesta tarefa em a_board.png, 10 px/mm, no referencial (u, v))
    "corner_cut": ([(0.0, -5.2), (-6.0, -5.0), (-23.0, -15.0), (-25.0, -12.0), (-25.5, -4.5), (-30.0, 0.0)], "derived",
                   "canto do conector: pontos (du, dv) a partir do canto (u máx, v máx), lidos em a_board.png (verso retificado): a borda da ponta oposta acaba em v = H - 5,2, desce 6 mm pela fresa, corta até o vértice do V (u = W - 23, v = H - 15), volta por u = W - 25 e sai a 45 graus até a borda superior a 30 mm do canto; tolerância de cerca de 1,5 mm (sombra da borda e trilho do painel na foto)"),
    "spring_hole_drill": (3.4, "derived", "furo da mola: interior escuro de cerca de 3,5 mm (a_board.png)"),
    "spring_ring_od": (5.0, "derived", "anel claro em volta do furo da mola: 4,4 a 4,9 mm (a_board.png); costura de vias a cerca de 5,6 mm fica na textura"),
    "corner_hole_drill": (2.2, "derived", "furo cobreado de canto: interior de cerca de 2 mm (a_board.png)"),
    "corner_ring_od": (3.2, "derived", "anel de cobre do furo de canto: cerca de 2,7 a 3,2 mm (a_board.png)"),
    "ring_t": (0.05, "inferred", "o anel sobressai da máscara (cobre mais acabamento): exagerado para aparecer na malha"),
    # package do GB202
    "gpu_ball_h": (0.45, "inferred", "altura das esferas e do underfill sob o substrato (prática de mercado para BGA grande)"),
    "gpu_substrate_t": (1.2, "inferred", "espessura do substrato; a soma com as esferas e o die fecha em gb202_die_top_above_pcb"),
    "gpu_stiff_t": (0.8, "inferred", "altura da moldura de reforço sobre o substrato (fica abaixo do topo do die, gn-33)"),
    "gpu_stiff_inset": (0.3, "inferred", "a moldura fica um pouco para dentro da borda do substrato (gn-33 mostra a borda verde)"),
    "gpu_window_r": (1.0, "inferred", "raio dos cantos da janela da moldura"),
    "gpu_die_chamfer": (0.15, "inferred", "chanfro das arestas do die"),
    "gpu_die_caps": (True, "illustrative", "capacitores do substrato em volta do die, na janela (gn-33 mostra fileiras; posição e quantidade ilustrativas)"),
    # memória
    "mem_standoff": (0.25, "inferred", "esferas sob o chip GDDR7: a altura total segue gddr7_package_thickness"),
    "mem_chamfer": (0.12, "inferred", "chanfro das arestas de cima do encapsulamento"),
    # indutores e estágios (posições lidas na foto sabareesh, frente; perspectiva não corrigida)
    "ind_h": (2.8, "inferred", "altura dos indutores: a moldura da base do cooler começa em iface_die_contact_z (3,0 mm acima da frente); o indutor real deve ser mais alto e entrar num rebaixo da base, sem foto de perfil"),
    "ind_fillet": (0.35, "inferred", "arredondamento das arestas do corpo moldado"),
    "ind_term_w": (3.6, "inferred", "largura das abas dos terminais"),
    "ind_term_h": (1.1, "inferred", "altura das abas dos terminais"),
    "ind_top_side": (5.0, "derived", "indutores menores da borda superior: cerca de 0,77 do lado dos da borda dos contatos na mesma foto (sabareesh)"),
    "contact_u_first": (47.5, "derived", "primeiro indutor da borda dos contatos: centro das ilhas em u 47,5 a 47,7 (pcb-b retificada; sabareesh); a fileira vai até u 107"),
    "contact_u_pitch": (6.6, "derived", "passo das células da borda dos contatos: 6,5 a 6,6 mm (pcb-b retificada; sabareesh 6,6); com o lado de 6,5 do CSV sobram 0,1 mm entre corpos, o que sugere indutor menor (relatório)"),
    "top_u_first": (44.0, "derived", "primeiro indutor da borda superior (pcb-b retificada 44,3; sabareesh 43,8)"),
    "top_u_pitch": (6.2, "derived", "passo das células da borda superior: 6,3 na pcb-b retificada, 6,4 na sabareesh; 6,2 tira o último estágio de dentro do corpo do power.connector detalhado (0,6 mm com 6,3)"),
    "far_u": ((108.9, 115.9), "inferred", "pares da ponta oposta: dois indutores lado a lado na faixa entre a memória (u 105,2) e a borda; conta sobre vrm_inductor_side"),
    "far_v_pitch": (18.4, "derived", "passo dos pares da ponta oposta: 17,4 a 18,9 (sabareesh)"),
    "far_single_uv": ((114.3, 107.3), "derived", "indutor isolado ao lado do conector de energia (sabareesh)"),
    "stage_contact": ((6.0, 5.0, 0.9), "derived", "estágio de potência (cinza, para dentro de cada indutor): cerca de 5,9 x 5,2 mm (sabareesh); altura inferred"),
    "stage_top": ((5.0, 4.0, 0.9), "inferred", "estágio da borda superior, menor como o indutor; altura inferred"),
    "stage_gap": (0.2, "inferred", "folga entre indutor e estágio"),
    "vrm_mem_v": ((21.6, 95.2), "illustrative", "power.vrm.mem: posição sem fonte (assembly); os 4 estágios ficam em duas células da ponta oposta que a foto mostra ocupadas e que a contagem representativa de power.inductors não usa"),
    "controller": ((5.0, 5.0, 0.9), "inferred", "power.controller: QFN quadrado (gn-40, sem medida)"),
    "controller_uv": (((30.0, 13.4), (46.2, 28.5)), "derived", "o primeiro na ilha quadrada de cerca de 6 mm junto à borda dos contatos (pcb-b retificada), como o CI de gn-40; o segundo sem fonte (ilustrativo), entre os chips de memória da borda dos contatos"),
    "aux": ((4.0, 4.0, 2.0), "inferred", "power.aux: indutores pequenos 4R7 e 330 (gn-33, gn-38, sabareesh)"),
    "aux_uv": (((47.7, 22.0), (53.6, 22.0), (59.6, 22.0)), "derived", "um 4R7 visto em u 59,6, v 22 (sabareesh); os outros dois ao lado, ilustrativos"),
    # conectores
    "aux_header_depth": (4.0, "inferred", "profundidade do conector auxiliar em y: a mesma do blockout, porque a moldura da cooler.base (ainda blockout) é recortada em volta dele; a foto sabareesh sugere cerca de 6 mm"),
    "aux_header_h": (6.0, "inferred", "altura do conector auxiliar (a mesma do blockout; a moldura da base é recortada em volta)"),
    "aux_header_pitch": (2.0, "inferred", "passo dos pinos: 2 fileiras de 7 em 14 mm"),
    "aux_header_clear": (0.3, "inferred", "folga do conector até o fundo do canal da carcaça"),
    "fan_conn_uv": ((35.3, 118.2), "derived", "conector pequeno de 4 vias na borda superior, entre o conector auxiliar e os indutores (sabareesh: u 29,9 a 40,6)"),
    "fan_conn": ((10.7, 5.0, 2.8), "inferred", "corpo do conector de 4 vias; altura limitada pela base do cooler"),
    # passivos
    "smd_types": ({"0201": (0.6, 0.3, 0.3), "0402": (1.0, 0.5, 0.5), "0603": (1.6, 0.8, 0.8), "0805": (2.0, 1.25, 0.85),
                   "1206": (3.2, 1.6, 0.9), "bloco": (None, None, 1.0)}, "illustrative",
                  "tipos por distância entre as ilhas do par (< 0,8; < 1,3; < 2,0; < 2,9; < 4,2 mm; acima disso, bloco do tamanho das ilhas); alturas de catálogo, não medidas"),
    "smd_back_hmax": (1.0, "inferred", "altura máxima dos passivos do verso: a pcb.plate e os pads ficam abaixo (layer_back_mem_pad = 2,1)"),
    "smd_front_hmax": (0.9, "inferred", "altura máxima dos passivos da frente (abaixo da base do cooler)"),
    "smd_margin": (0.4, "inferred", "folga entre passivo e as peças maiores"),
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

X0, Y0 = M("pcb_main_card_x_min"), M("pcb_main_card_y_min")
W, H = M("pcb_main_width"), M("pcb_main_height")
ZB, ZF = M("iface_pcb_back_z"), M("iface_pcb_front_z")
DCX, DCY = M("iface_die_center_x"), M("iface_die_center_y")
GU, GV = M("gpu_center_u"), M("gpu_center_v")


def uv2xy(u, v):
    return X0 + u, Y0 + v


def xy2uv(x, y):
    return x - X0, y - Y0


# ---------------------------------------------------------------------------
# Contorno do PCB em (u, v), sentido anti-horário visto de +z
# ---------------------------------------------------------------------------
def outline_uv():
    rd = M("pcb_main_contact_edge_recess_depth")
    r0, r1 = M("pcb_main_contact_edge_recess_u_start"), M("pcb_main_contact_edge_recess_u_end")
    pts = [(0.0, 0.0), (r0, 0.0), (r0, rd), (r1, rd), (r1, 0.0), (W, 0.0)]
    pts += [(W + du, H + dv) for du, dv in g("corner_cut")]
    pts += [(0.0, H)]
    return pts


def outline_xy():
    return [uv2xy(u, v) for u, v in outline_uv()]


def in_poly(pts, poly):
    """Ponto dentro do polígono (paridade), vetorizado."""
    pts = np.atleast_2d(pts)
    x, y = pts[:, 0], pts[:, 1]
    inside = np.zeros(len(pts), bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / ((y2 - y1) + 1e-12) + x1)
        inside ^= c
    return inside


def dist_to_outline(pts, poly):
    pts = np.atleast_2d(pts)
    d = np.full(len(pts), np.inf)
    n = len(poly)
    for i in range(n):
        a, b = np.array(poly[i]), np.array(poly[(i + 1) % n])
        ab = b - a
        t = np.clip(((pts - a) @ ab) / (ab @ ab), 0, 1)
        d = np.minimum(d, np.linalg.norm(pts - (a + t[:, None] * ab), axis=1))
    return d


def holes_xy():
    """(x, y, furo, anel externo, tipo) dos 8 furos do PCB."""
    out = []
    sx, sy = M("iface_spring_holes_dx") / 2, M("iface_spring_holes_dy") / 2
    for kx in (-1, 1):
        for ky in (-1, 1):
            out.append((DCX + kx * sx, DCY + ky * sy, g("spring_hole_drill"), g("spring_ring_od"), "mola"))
    cx, cy = M("iface_pcb_center_x"), M("iface_pcb_center_y")
    px, py = M("pcb_corner_plated_holes_dx") / 2, M("pcb_corner_plated_holes_dy") / 2
    for kx in (-1, 1):
        for ky in (-1, 1):
            out.append((cx + kx * px, cy + ky * py, g("corner_hole_drill"), g("corner_ring_od"), "canto"))
    return out


# ---------------------------------------------------------------------------
# Componentes grandes
# ---------------------------------------------------------------------------
FIELDS = ["id", "part", "instance", "tipo", "x", "y", "rot_deg", "lado", "provenance", "comprimento", "largura",
          "altura", "z_base", "representativo", "aviso_viewer", "nota"]


def row(pid, inst, tipo, x, y, rot, lado, prov, L, Wd, h, rep=False, nota=""):
    z = ZF if lado == "frente" else ZB
    return {"id": "%s.%d" % (pid, inst) if inst else pid, "part": pid, "instance": inst, "tipo": tipo,
            "x": round(x, 3), "y": round(y, 3), "rot_deg": round(rot, 2), "lado": lado, "provenance": prov,
            "comprimento": round(L, 3), "largura": round(Wd, 3), "altura": round(h, 3), "z_base": z,
            "representativo": "sim" if rep else "não",
            "aviso_viewer": "sim" if (prov in ("inferred", "illustrative") or rep) else "não", "nota": nota}


def memory_rows():
    """Grade mem_* do CSV; as âncoras do assembly são conferidas contra ela."""
    gw, gl, gt = M("gddr7_package_width"), M("gddr7_package_length"), M("gddr7_package_thickness")
    M("mem_footprint_along_row"); M("mem_footprint_across_row")
    grid = []
    for i in range(5):
        grid.append((M("mem_side_bracket_u"), M("mem_side_v_first") + i * M("mem_side_v_pitch"), "lateral"))
    for i in range(5):
        grid.append((M("mem_side_opposite_u"), M("mem_side_v_first") + i * M("mem_side_v_pitch"), "lateral"))
    for i in range(4):
        grid.append((M("mem_power_edge_u_first") + i * M("mem_power_edge_u_pitch"), M("mem_power_edge_v"), "borda"))
    for u in (M("mem_contact_edge_u_1"), M("mem_contact_edge_u_2")):
        grid.append((u, M("mem_contact_edge_v"), "borda"))
    rows, obs = [], []
    for pid, lado in (("mem.front", "frente"), ("mem.back", "verso")):
        anchors = PARTS[pid]["anchors"]
        for k, (u, v, kind) in enumerate(grid, 1):
            x, y = uv2xy(u, v)
            a = anchors[k - 1]["pos"]
            if abs(a[0] - x) > 0.05 or abs(a[1] - y) > 0.05:
                obs.append("%s.%d: âncora (%.2f, %.2f) fora da grade do CSV (%.2f, %.2f)" % (pid, k, a[0], a[1], x, y))
            # lado de 14 mm atravessado na fileira: em u nas laterais (rot 0), em v nas bordas (rot 90)
            rot = 0.0 if kind == "lateral" else 90.0
            prov = "derived"
            rows.append(row(pid, k, "GDDR7 12 x 14 mm", x, y, rot, lado, prov, gl, gw, gt,
                            nota="posição pela grade mem_* (foto retificada); encapsulamento pela tabela da Micron"
                            + ("" if lado == "verso" else "; na frente do PCB nu (pcb-b retificada) os campos ficam nas mesmas posições do verso, e as duas faces diferem da grade do CSV (pcb_compare.py, MANUAL)")))
    return rows, obs


def gpu_rows():
    return [row("gpu.package", 0, "GB202 (package, moldura, die)", DCX, DCY, 0.0, "frente", "derived",
                M("gb202_package_x"), M("gb202_package_y"), M("gb202_die_top_above_pcb"),
                nota="centro em (gpu_center_u, gpu_center_v) = (iface_die_center_x, iface_die_center_y); lado longo em x")]


def power_rows():
    rows = []
    s = M("vrm_inductor_side")
    h = g("ind_h")
    gap = g("stage_gap")
    sl, sw, sh = g("stage_contact")
    tl, tw, th = g("stage_top")
    yc = M("iface_contact_edge_band_y")
    yp = M("iface_power_edge_band_y")
    fx, fy = M("iface_far_end_inductor_band_x"), M("iface_far_end_inductor_band_y")
    n_c = int(M("power_inductors_contact_edge_count"))
    n_t = int(M("power_inductors_top_edge_count"))
    n_tot = PARTS["power.inductors"]["count"]["value"]
    n_f = n_tot - n_c - n_t
    M("power_inductors_far_end_count")
    ind, stg = [], []
    # borda dos contatos: indutor junto à borda, estágio para dentro (+y)
    for k in range(n_c):
        x = X0 + g("contact_u_first") + k * g("contact_u_pitch")
        ind.append((x, yc, 0.0, s, s, "contatos", "derived"))
        stg.append((x, yc + s / 2 + gap + sw / 2, 0.0, sl, sw, "contatos"))
    # borda superior: indutor menor junto à borda, estágio para dentro (-y)
    st = g("ind_top_side")
    for k in range(n_t):
        x = X0 + g("top_u_first") + k * g("top_u_pitch")
        ind.append((x, yp, 0.0, st, st, "superior", "derived"))
        stg.append((x, yp - st / 2 - gap - tw / 2, 0.0, tl, tw, "superior"))
    # ponta oposta: pares (dois indutores lado a lado em u), estágios acima (+y); o par do
    # meio fica na âncora (iface_far_end_inductor_band_y); um isolado junto ao conector
    n_pairs = (n_f - 1) // 2
    vs = [fy + g("far_v_pitch") * (k - (n_pairs - 1) / 2) for k in range(n_pairs)]
    for yy in vs:
        for u in g("far_u"):
            x = X0 + u
            ind.append((x, yy, 0.0, s, s, "ponta oposta", "derived"))
            stg.append((x, yy + s / 2 + gap + sw / 2, 0.0, sl, sw, "ponta oposta"))
    for _ in range(n_f - 2 * n_pairs):
        x, yy = uv2xy(*g("far_single_uv"))
        ind.append((x, yy, 0.0, s, s, "ponta oposta (isolado)", "derived"))
        stg.append((x, yy - s / 2 - gap - sw / 2, 0.0, sl, sw, "ponta oposta (isolado)"))
    for k, (x, y, rot, L, Wd, band, prov) in enumerate(ind, 1):
        rows.append(row("power.inductors", k, "indutor 85N", x, y, rot, "frente", prov, L, Wd, h, rep=True,
                        nota="fileira: %s; quantidade representativa (assembly: 24); terminais nos lados %s" % (band, "em y" if rot == 0 else "em x")))
    for k, (x, y, rot, L, Wd, band) in enumerate(stg, 1):
        hh = sh if band != "superior" else th
        rows.append(row("power.vrm.gpu", k, "estágio de potência", x, y, rot, "frente", "inferred", L, Wd, hh, rep=True,
                        nota="fileira: %s; para dentro do indutor %d, como os blocos cinza da foto sabareesh; fase representativa" % (band, k)))
    # memória: 4 estágios em duas células da ponta oposta (posição sem fonte)
    k = 0
    for v in g("vrm_mem_v"):
        for u in g("far_u"):
            k += 1
            x, y = uv2xy(u, v)
            rows.append(row("power.vrm.mem", k, "estágio de potência (memória)", x, y, 0.0, "frente", "illustrative", sl, sw, sh,
                            rep=True, nota="posição sem fonte: célula livre da ponta oposta"))
    cl, cw, ch = g("controller")
    for k, (u, v) in enumerate(g("controller_uv"), 1):
        x, y = uv2xy(u, v)
        rows.append(row("power.controller", k, "controlador PWM (QFN)", x, y, 0.0, "frente", "derived" if k == 1 else "illustrative", cl, cw, ch,
                        nota="marcação lida como MPS MP29816-A (gn-40, a reconferir); posição sem fonte"))
    al, aw, ah = g("aux")
    for k, (u, v) in enumerate(g("aux_uv"), 1):
        x, y = uv2xy(u, v)
        rows.append(row("power.aux", k, "indutor auxiliar (4R7 ou 330)", x, y, 0.0, "frente", "derived" if k == 3 else "illustrative",
                        al, aw, ah, rep=True, nota="um 4R7 visto aqui (sabareesh)" if k == 3 else "ao lado do 4R7 visto; ilustrativo"))
    return rows


def channel_floor_y():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import frame  # noqa: E402  (só para a interface do canal da carcaça)
    return frame.keepouts()["canal"][2]


def connector_rows():
    rows = []
    au, al = M("aux_header_u"), M("aux_header_length")
    d = g("aux_header_depth")
    top = min(Y0 + H, channel_floor_y() - g("aux_header_clear"))
    rows.append(row("io.aux_header", 0, "conector auxiliar (2 x 7 pinos)", X0 + au, top - d / 2, 0.0, "frente", "derived",
                    al, d, g("aux_header_h"), nota="posição em u e comprimento do CSV (escala antiga: reconferir); fica %.2f mm para dentro da borda, abaixo do fundo do canal da carcaça" % (Y0 + H - top)))
    fl, fw, fh = g("fan_conn")
    x, y = uv2xy(*g("fan_conn_uv"))
    rows.append(row("pcb.smd", 0, "conector pequeno de 4 vias", x, y, 0.0, "frente", "derived", fl, fw, fh,
                    nota="visto na foto sabareesh, sem id no assembly (função provável: ventilador, inferred); entra em pcb.smd até ganhar id próprio"))
    return rows


# ---------------------------------------------------------------------------
# Passivos a partir das ilhas de cobre do PCB nu
# ---------------------------------------------------------------------------
def rect_poly(x, y, L, Wd, rot, m=0.0):
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    hx, hy = L / 2 + m, Wd / 2 + m
    return [(x + c * px - s * py, y + s * px + c * py) for px, py in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy))]


def keepouts(face, big_rows):
    """Polígonos (x, y) em que não entram passivos."""
    m = g("smd_margin")
    out = []
    for r in big_rows:
        if r["lado"] != face:
            continue
        if r["part"] == "mem.front" or r["part"] == "mem.back":
            # pegada do campo de esferas (mem_footprint) mais a folga
            L, Wd = M("mem_footprint_across_row"), M("mem_footprint_along_row")
            out.append(rect_poly(r["x"], r["y"], L, Wd, r["rot_deg"], m))
        else:
            out.append(rect_poly(r["x"], r["y"], r["comprimento"], r["largura"], r["rot_deg"], m))
    if face == "frente":
        out.append(rect_poly(DCX, DCY, M("gb202_package_x"), M("gb202_package_y"), 0, m))
        # conector de energia (corpo do blockout: cabeçote girado; peça de outro modelador)
        cx, cy = M("power_connector_center_from_bracket_end"), M("power_connector_center_y")
        out.append(rect_poly(cx, cy, M("conn16_header_width"), 11.0, M("power_connector_rotation_deg"), 1.0))
    else:
        # mola em X (anel, braços) e anéis da pcb.back_frame: os passivos do verso não sobem até ela
        ww, wh = M("leaf_spring_window_x") / 2, M("leaf_spring_window_y") / 2
        rw = 8.0
        ring = [rect_poly(DCX, DCY, 2 * (ww + rw), 2 * (wh + rw), 0, m)]
        out.append(("anel", ring[0], rect_poly(DCX, DCY, 2 * ww, 2 * wh, 0, -m)))
        sx, sy = M("iface_spring_holes_dx") / 2, M("iface_spring_holes_dy") / 2
        for kx in (-1, 1):
            for ky in (-1, 1):
                c = np.array([DCX + kx * sx, DCY + ky * sy])
                r_ = np.array([DCX + kx * (ww + rw), DCY + ky * (wh + rw)])
                mid = (c + r_) / 2
                ang = math.degrees(math.atan2(*(r_ - c)[::-1]))
                out.append(rect_poly(mid[0], mid[1], np.linalg.norm(r_ - c) + 8, rw, ang, m))
        # conector de placa a placa do adaptador (J3) e a pegada longa ao lado: sem peça (relatório)
        out.append(rect_poly(*uv2xy(28.5, 12.2), 25.0, 6.5, 90.0, m))
        out.append(rect_poly(*uv2xy(52.8, 30.0), 24.0, 6.5, 90.0, m))
    for hx, hy, _, ring_od, kind in holes_xy():
        r = 3.2 if kind == "mola" else 2.4
        out.append(rect_poly(hx, hy, 2 * r, 2 * r, 0, 0))
    return out


def blocked(pts, kos):
    pts = np.atleast_2d(pts)
    b = np.zeros(len(pts), bool)
    for k in kos:
        if isinstance(k, tuple) and k and k[0] == "anel":
            b |= in_poly(pts, k[1]) & ~in_poly(pts, k[2])
        else:
            b |= in_poly(pts, k)
    return b


def detect_pads(face, front_png=None):
    from PIL import Image
    from scipy import ndimage
    if face == "verso":
        im = np.asarray(Image.open(CACHE / "visualqa" / "a_board.png").convert("RGB")).astype(int)

        def to_uv(px, py):
            # calibração pelos 4 furos da mola (centro em 683,3; 705,6 px; 10 px/mm; x = v, y = -u)
            return GU - (py - 705.6) / 10.0, GV + (px - 683.3) / 10.0
        swap = True
    else:
        im = np.asarray(Image.open(front_png).convert("RGB")).astype(int)

        def to_uv(px, py):
            return px / 10.0 - 10.0, 131.5 - py / 10.0
        swap = False
    r, b = im[..., 0], im[..., 2]
    L = im.mean(2)
    mask = ((r - b > 28) & (L > 95)) | ((L > 170) & (r > 150))
    lab, n = ndimage.label(mask)
    out = []
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        sub = lab[s] == i
        a = sub.sum()
        if a < 4:
            continue
        cy, cx = ndimage.center_of_mass(sub)
        u, v = to_uv(cx + s[1].start, cy + s[0].start)
        hh, ww = (s[0].stop - s[0].start) / 10.0, (s[1].stop - s[1].start) / 10.0
        du, dv = (hh, ww) if swap else (ww, hh)
        out.append((u, v, du, dv, a / 100.0))
    return np.array(out)


def smd_rows(big_rows, front_png):
    from scipy.spatial import cKDTree
    types = g("smd_types")
    poly = outline_xy()
    rows = []
    stats = {}
    for face in ("frente", "verso"):
        P = detect_pads(face, front_png)
        P = P[(P[:, 4] >= 0.06) & (P[:, 4] <= 25.0)]
        xy = np.c_[X0 + P[:, 0], Y0 + P[:, 1]]
        tree = cKDTree(xy)
        used = np.zeros(len(P), bool)
        kos = keepouts(face, big_rows)
        hmax = g("smd_front_hmax") if face == "frente" else g("smd_back_hmax")
        cand = []
        for i in np.argsort(-P[:, 4]):
            if used[i]:
                continue
            d, j = tree.query(xy[i], k=6)
            for dd, jj in zip(d[1:], j[1:]):
                if jj >= len(P) or used[jj] or dd > 6.0 or dd < 0.45:
                    continue
                a1, a2 = P[i, 4], P[jj, 4]
                if max(a1, a2) / min(a1, a2) > 2.2:
                    continue
                vec = xy[jj] - xy[i]
                ang = math.degrees(math.atan2(vec[1], vec[0]))
                ax = abs(math.cos(math.radians(ang)))
                if 0.25 < ax < 0.97:          # só pares alinhados a x ou a y
                    continue
                rot = 0.0 if ax >= 0.97 else 90.0
                # ilha mais estreita na direção do par que na perpendicular (forma de ilha de passivo)
                ext_par = P[i, 2] if rot == 0 else P[i, 3]
                ext_perp = P[i, 3] if rot == 0 else P[i, 2]
                if ext_par > dd * 0.95:
                    continue
                if dd < 0.8:
                    t = "0201"
                elif dd < 1.3:
                    t = "0402"
                elif dd < 2.0:
                    t = "0603"
                elif dd < 2.9:
                    t = "0805"
                elif dd < 4.2:
                    t = "1206"
                else:
                    t = "bloco"
                L_, W_, h_ = types[t]
                if t == "bloco":
                    L_, W_, h_ = dd + ext_par * 0.8, max(ext_perp * 0.95, 1.2), h_
                c = (xy[i] + xy[jj]) / 2
                cand.append((c[0], c[1], rot, L_, W_, min(h_, hmax), t))
                used[i] = used[jj] = True
                break
        cand = np.array(cand, dtype=object)
        if not len(cand):
            continue
        pts = np.array([[c[0], c[1]] for c in cand], float)
        ok = in_poly(pts, poly) & (dist_to_outline(pts, poly) > 1.0) & ~blocked(pts, kos)
        # cantos do corpo também fora das áreas proibidas
        for k in np.nonzero(ok)[0]:
            x, y, rot, L_, W_, h_, t = cand[k]
            corners = np.array(rect_poly(x, y, L_, W_, rot))
            if blocked(corners, kos).any() or not in_poly(corners, poly).all():
                ok[k] = False
        # sem sobreposição entre passivos (o maior fica)
        keep = []
        boxes = []
        order = sorted(np.nonzero(ok)[0], key=lambda k: -cand[k][3] * cand[k][4])
        for k in order:
            x, y, rot, L_, W_, h_, t = cand[k]
            hx, hy = (L_ / 2, W_ / 2) if rot == 0 else (W_ / 2, L_ / 2)
            bb = (x - hx - 0.05, x + hx + 0.05, y - hy - 0.05, y + hy + 0.05)
            if any(not (bb[1] < o[0] or bb[0] > o[1] or bb[3] < o[2] or bb[2] > o[3]) for o in boxes):
                continue
            boxes.append(bb)
            keep.append(k)
        keep.sort(key=lambda k: (round(cand[k][1], 1), round(cand[k][0], 1)))
        for k in keep:
            x, y, rot, L_, W_, h_, t = cand[k]
            rows.append(row("pcb.smd", 0, t, float(x), float(y), rot, face, "illustrative", L_, W_, h_, rep=True,
                            nota="posição de um par de ilhas do PCB nu (%s); tipo, altura e quantidade ilustrativos" %
                            ("a_board.png" if face == "verso" else "pcb-b retificada")))
            stats[(face, t)] = stats.get((face, t), 0) + 1
    return rows, stats


def write_layout(rows):
    LAYOUT.parent.mkdir(parents=True, exist_ok=True)
    with open(LAYOUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_layout():
    with open(LAYOUT, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("x", "y", "rot_deg", "comprimento", "largura", "altura", "z_base"):
            r[k] = float(r[k])
        r["instance"] = int(r["instance"])
    return rows


def big_rows():
    mem, obs = memory_rows()
    return mem + gpu_rows() + power_rows() + connector_rows(), obs


def main():
    rows, obs = big_rows()
    front_png = Path(sys.argv[sys.argv.index("--frente") + 1]) if "--frente" in sys.argv else None
    redo = "--refazer-passivos" in sys.argv
    old_smd = []
    if LAYOUT.exists():
        old_smd = [r for r in read_layout() if r["part"] == "pcb.smd" and r["tipo"] != "conector pequeno de 4 vias"]
    if redo:
        if front_png is None or not front_png.exists() or not (CACHE / "visualqa" / "a_board.png").exists():
            raise SystemExit("--refazer-passivos precisa do cache de referências e de --frente <png retificada> (pcb_compare.py --retificar)")
        smd, stats = smd_rows(rows, front_png)
        print("passivos detectados:", ", ".join("%s %s: %d" % (f, t, n) for (f, t), n in sorted(stats.items())))
    else:
        smd = old_smd
        if not smd:
            print("aviso: sem passivos (rode com --refazer-passivos)")
    for o in obs:
        print("OBS", o)
    for r in smd:
        r["aviso_viewer"] = "sim"
    all_rows = rows + smd
    write_layout(all_rows)
    print("layout: %s (%d linhas, %d passivos)" % (LAYOUT.relative_to(HARNESS.parent), len(all_rows), len(smd)))


if __name__ == "__main__":
    main()
