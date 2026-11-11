#!/usr/bin/env python3
"""Integração da placa (F4): gera build/card.glb, o GLB que o tour usa.

Parte dos corpos do blockout (parts/blockout.py, um corpo simples por peça do assembly) e
troca a geometria de toda peça que já tem versão detalhada em build/parts/<id>.glb. Não há
lista de peças no código: qualquer arquivo build/parts/<id>.glb cujo <id> esteja no
assembly entra; peça sem arquivo continua em blockout. Nome do nó, hierarquia, âncoras e
extras (stage, group, procedência, explode_cad) vêm sempre do assembly, nunca do arquivo
da peça; o arquivo da peça só fornece a malha (e as notas dela, em extras.detail).

Peça detalhada com uma malha: o nó <id> recebe a malha. Peça detalhada com instâncias
(nós <id>.1, <id>.2, ... no arquivo da peça): viram instâncias do nó <id>, como no blockout.
Submalha nomeada (nó com extras.submesh = <nome>, filho do nó do id ou de uma instância, com o
nome <pai>.<nome>): vira nó filho com a própria malha, para o lookdev dar outro acabamento
(substrato dos chips, copo dos ventiladores, luva do túnel do conector); entra nas conferências
como corpo da peça.

Referencial: CAD em mm, Z para cima, origem em card.envelope_min, face B em z = 0 e face A
(ventiladores) em z = card_thickness (assembly-plan, seção 11). O GLB sai em metros com Y
para cima, (x, y, z) -> (x, z, -y) / 1000, com normais por vértice nas peças detalhadas
(sombreamento suave, quebra acima de 30 graus); o blockout segue sem normais (sombreamento
plano no viewer). Sem Draco (o arquivo único abre por file://); sem meshopt por enquanto.

Conferências: envelope sem o bracket contra o CSV; todos os ids e âncoras com nó; distância
das âncoras ao corpo (âncora "opening" do assembly só precisa ficar na caixa da peça);
malhas fechadas, orientadas e com volume; interferências da peça detalhada com as vizinhas
e entre as caixas do blockout; releitura do GLB (escala e eixos); tamanho do arquivo.

Determinística: mesma entrada, mesmo arquivo (amostragens com semente fixa, sem data).

Uso:   python3 -I harness/parts/integrate.py [--sem-imagens]
Saídas: harness/build/card.glb, harness/build/integration-report.json,
        harness/build/integration-report.md, harness/dist/integracao/*.png
"""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blockout as B  # noqa: E402

HARNESS = B.HARNESS
PARTS_DIR = HARNESS / "build" / "parts"
OUT = HARNESS / "build" / "card.glb"
REPORT_JSON = HARNESS / "build" / "integration-report.json"
REPORT_MD = HARNESS / "build" / "integration-report.md"
DIST = HARNESS / "dist" / "integracao"

TOL_ENV = 0.5          # mm
TOL_ANCHOR = 2.0       # mm
TOL_OVERLAP = 0.5      # mm
CREASE_DEG = 30.0      # quebra das normais suaves
N_SAMPLES = 60000      # pontos por superfície detalhada na conferência de interferência
SEED = 7

# Interferências esperadas (não são erro) e pendências conhecidas, com o dono. A lista é de
# pares de peças; a conferência mede todos e só usa esta tabela para classificar.
EXPECTED = {
    frozenset(("cooler.fins.1", "cooler.heatpipes")): "os tubos de calor atravessam a pilha de aletas (é assim que o calor chega às aletas)",
    frozenset(("cooler.fins.2", "cooler.heatpipes")): "os tubos de calor atravessam a pilha de aletas",
    frozenset(("cooler.fins.3", "cooler.heatpipes")): "os tubos de calor atravessam a pilha central",
}
# Resolvidas pelo contrato de 2026-11-11 (assembly-plan 12.4) e tiradas daqui: adaptador
# contra face B, tampas, aro, pcb.plate e parafusos do E5; cabeças do E4 e do E5 sob as tampas;
# mola contra pcb.back_frame e memória do verso; parafuso do aro sem furo; package contra memória.
# Resolvida em 2026-11-11 (achado 21 da segunda passada visual): adaptador PCIe contra a cabeça do
# parafuso da mola, com o rebaixo do lado do PCB da aba (io_parts.py).
ISSUES = {}


# ---------------------------------------------------------------------------
# Leitura das peças detalhadas
# ---------------------------------------------------------------------------
def read_glb(path):
    data = path.read_bytes()
    magic, ver, total = struct.unpack_from("<III", data, 0)
    assert magic == 0x46546C67 and ver == 2, path
    jlen, _ = struct.unpack_from("<II", data, 12)
    js = json.loads(data[20:20 + jlen])
    blen, _ = struct.unpack_from("<II", data, 20 + jlen)
    binary = data[28 + jlen:28 + jlen + blen]
    return js, binary


def accessor(js, binary, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    dt = {5126: "<f4", 5125: "<u4", 5123: "<u2"}[a["componentType"]]
    n = {"VEC3": 3, "SCALAR": 1}[a["type"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    arr = np.frombuffer(binary, dtype=dt, count=a["count"] * n, offset=off)
    return arr.reshape(-1, n) if n > 1 else arr


def from_gltf(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]] * 1000.0


def detailed_body(mesh_v, mesh_f):
    """Corpo com normais suaves quebradas acima de CREASE_DEG."""
    m = trimesh.Trimesh(mesh_v, mesh_f, process=False)
    m.merge_vertices(digits_vertex=5)
    sm = trimesh.graph.smooth_shade(m, angle=math.radians(CREASE_DEG))
    b = B.Body.__new__(B.Body)
    b.v = np.asarray(sm.vertices, float)
    b.f = np.asarray(sm.faces, np.int64)
    b.convex = False
    b.vn = np.asarray(sm.vertex_normals, float)
    b._ax = None
    b.solid = m          # malha soldada, para as conferências de malha fechada
    return b


def load_detailed(asm):
    ids = {p["id"] for p in asm["parts"]}
    found, ignored = {}, []
    for path in sorted(PARTS_DIR.glob("*.glb")):
        pid = path.stem
        if pid not in ids:
            ignored.append(path.name)
            continue
        js, binary = read_glb(path)
        names = {n.get("name"): n for n in js["nodes"]}

        def body_of(node):
            prim = js["meshes"][node["mesh"]]["primitives"][0]
            v = from_gltf(accessor(js, binary, prim["attributes"]["POSITION"]))
            f = accessor(js, binary, prim["indices"]).reshape(-1, 3).astype(np.int64)
            return detailed_body(v, f)
        root = names.get(pid)
        if root is None:
            raise SystemExit("%s: o arquivo não tem nó com o nome do id" % path)
        inst = sorted((n for n in js["nodes"] if n.get("name", "").startswith(pid + ".") and n.get("name")[len(pid) + 1:].isdigit()
                       and "mesh" in n), key=lambda n: int(n["name"][len(pid) + 1:]))
        if "mesh" in root:
            entry = {"bodies": [body_of(root)]}
        elif inst:
            entry = {"instances": [[body_of(n)] for n in inst]}
        else:
            raise SystemExit("%s: nó %s sem malha e sem instâncias" % (path, pid))
        # submalhas nomeadas: nós com extras.submesh = <nome>, filhos do nó do id ou de uma instância,
        # com o nome <pai>.<nome>; viram nós filhos no card.glb (acabamento próprio no lookdev)
        parents = {pid} | {n["name"] for n in inst}
        subs = []
        for k, n in enumerate(js["nodes"]):
            sname = (n.get("extras") or {}).get("submesh")
            if not sname or "mesh" not in n:
                continue
            par = [m.get("name") for m in js["nodes"] if k in m.get("children", [])]
            if not par or par[0] not in parents or n.get("name") != "%s.%s" % (par[0], sname):
                raise SystemExit("%s: submalha %s fora do padrão <pai>.<nome> (pai: %s)" % (path, n.get("name"), par))
            subs.append((par[0], sname, body_of(n)))
        if subs:
            entry["subs"] = subs
        ex = root.get("extras", {})
        keep = {k: ex[k] for k in ("guess", "guess_notes", "shape_provenance_features", "text_box_cad_mm", "material_zones_cad_mm",
                                   "referencial") if k in ex}
        keep["source"] = "build/parts/%s" % path.name
        keep["generator"] = js.get("asset", {}).get("generator")
        keep["sha256_12"] = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        found[pid] = (entry, keep)
    return found, ignored


# ---------------------------------------------------------------------------
# Conferências
# ---------------------------------------------------------------------------
def bvh(mesh):
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils.bvhtree import BVHTree
    return BVHTree.FromPolygons(np.asarray(mesh.vertices).tolist(), np.asarray(mesh.faces).tolist(), epsilon=0.0)


def inside_mesh(tree, pts):
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


def solid_of(b):
    return getattr(b, "solid", None) or b.mesh()


def mesh_quality(R, detailed):
    rows = []
    for pid in R:
        for k, b in enumerate(B.all_bodies(R, pid), 1):
            m = solid_of(b)
            ok = bool(m.is_watertight and m.is_winding_consistent and m.volume > 0)
            if not ok or pid in detailed:
                rows.append({"part": pid, "body": k, "detailed": pid in detailed, "triangles": int(len(m.faces)),
                             "watertight": bool(m.is_watertight), "winding_consistent": bool(m.is_winding_consistent),
                             "volume_mm3": round(float(m.volume), 1), "ok": ok})
    return rows


def surface_points(b, n, seed):
    m = solid_of(b)
    pts = trimesh.sample.sample_surface(m, n, seed=seed)[0] if n else np.empty((0, 3))
    return np.vstack([m.vertices, pts])


def depth_in_convex(pts, body):
    m = body.mesh()
    nrm = m.face_normals
    d = np.einsum("ij,ij->i", nrm, m.triangles[:, 0])
    sd = pts @ nrm.T - d[None, :]
    inside = np.all(sd < -1e-3, axis=1)
    return float((-sd[inside]).min(axis=1).max()) if inside.any() else 0.0


def interferences(asm, R, detailed):
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils import Vector as V3
    P = {p["id"]: p for p in asm["parts"]}
    desc = B.descendants(asm["parts"])
    out = []
    trees = {}
    for pid in detailed:
        for k, b in enumerate(B.all_bodies(R, pid)):
            trees[(pid, k)] = (bvh(solid_of(b)), solid_of(b))
    ids = list(P)
    for i, a_id in enumerate(ids):
        for b_id in ids[i + 1:]:
            a_det, b_det = a_id in detailed, b_id in detailed
            # entre caixas do blockout, filhos não contam contra a mãe (pás no cubo, chips no
            # PCB); a peça detalhada é conferida contra todas, inclusive mãe e filhas (a
            # carcaça é mãe dos ventiladores, das aletas e da base)
            if not (a_det or b_det) and (b_id in desc[a_id] or a_id in desc[b_id]):
                continue
            best = 0.0
            if not a_det and not b_det:
                for ba in B.all_bodies(R, a_id):
                    for bb in B.all_bodies(R, b_id):
                        if ba.convex and bb.convex:
                            best = max(best, B.penetration(ba, bb))
            else:
                for x_id, y_id in ((a_id, b_id), (b_id, a_id)):
                    if x_id not in detailed:
                        continue
                    for kx, bx in enumerate(B.all_bodies(R, x_id)):
                        tree, solid = trees[(x_id, kx)]
                        lo, hi = solid.bounds
                        for by in B.all_bodies(R, y_id):
                            if np.any(by.hi < lo - 0.5) or np.any(by.lo > hi + 0.5):
                                continue
                            # pontos da peça detalhada dentro do vizinho
                            px = surface_points(bx, N_SAMPLES if y_id not in detailed else N_SAMPLES // 4, SEED)
                            sel = np.all((px >= by.lo - 1e-6) & (px <= by.hi + 1e-6), axis=1)
                            if sel.any():
                                if by.convex:
                                    best = max(best, depth_in_convex(px[sel], by))
                                elif y_id in detailed:
                                    ty, _ = trees[(y_id, B.all_bodies(R, y_id).index(by))]
                                    q = px[sel][:: max(1, sel.sum() // 3000)]
                                    ins = inside_mesh(ty, q)
                                    if ins.any():
                                        best = max(best, max(ty.find_nearest(V3(p))[3] for p in q[ins]))
                            # pontos do vizinho dentro da peça detalhada
                            py = surface_points(by, 400 if by.convex else 2000, SEED)
                            sel = np.all((py >= lo - 1e-6) & (py <= hi + 1e-6), axis=1)
                            if sel.any():
                                q = py[sel]
                                ins = inside_mesh(tree, q)
                                if ins.any():
                                    best = max(best, max(tree.find_nearest(V3(p))[3] for p in q[ins]))
            if best > TOL_OVERLAP:
                key = frozenset((a_id, b_id))
                cls = "esperada" if key in EXPECTED else ("pendencia" if key in ISSUES else "nova")
                row = {"a": a_id, "b": b_id, "stage_a": P[a_id]["stage"], "stage_b": P[b_id]["stage"],
                       "penetration_mm": round(best, 2), "detalhada": bool(a_det or b_det), "classe": cls}
                if key in EXPECTED:
                    row["motivo"] = EXPECTED[key]
                if key in ISSUES:
                    row["dono"], row["motivo"] = ISSUES[key]
                out.append(row)
    return out


def anchor_report(asm, R):
    import bpy  # noqa: F401  (carrega mathutils)
    from mathutils import Vector as V3
    desc = B.descendants(asm["parts"])
    rows = []
    for p in asm["parts"]:
        pid = p["id"]
        bodies = B.all_bodies(R, pid) or [b for d in desc[pid] for b in B.all_bodies(R, d)]
        for a in p["anchors"]:
            pt = np.array(a["pos"], float)
            kind = a.get("kind", "surface")
            best = math.inf
            for b in bodies:
                m = solid_of(b)
                if b.convex:
                    d = float(np.linalg.norm(np.maximum(np.maximum(b.lo - pt, pt - b.hi), 0)))
                else:
                    t = bvh(m)
                    d = 0.0 if inside_mesh(t, [pt])[0] else float(t.find_nearest(V3(pt))[3])
                best = min(best, d)
            lo = np.min([b.lo for b in bodies], axis=0)
            hi = np.max([b.hi for b in bodies], axis=0)
            in_box = bool(np.all(pt >= lo - 1e-6) and np.all(pt <= hi + 1e-6))
            ok = in_box if kind == "opening" else best <= TOL_ANCHOR
            rows.append({"anchor": a["id"], "part": pid, "kind": kind, "dist_mm": round(best, 2), "in_part_box": in_box, "ok": bool(ok)})
    return rows


def envelope(asm, R):
    P = {p["id"] for p in asm["parts"]}
    bracket = {"io.bracket", "fasteners.e1_bracket"}
    bs = [b for pid in P if pid not in bracket for b in B.all_bodies(R, pid)]
    lo = np.min([b.lo for b in bs], axis=0)
    hi = np.max([b.hi for b in bs], axis=0)
    want = [B.M("card_envelope_length"), B.M("card_envelope_height"), B.M("card_thickness")]
    res = {}
    for ax, e0, e1, w in zip("xyz", lo, hi, want):
        res[ax] = {"min": round(float(e0), 3), "max": round(float(e1), 3), "extent": round(float(e1 - e0), 3), "target": w,
                   "error": round(float(e1 - e0 - w), 3), "ok": bool(abs(e1 - e0 - w) <= TOL_ENV and abs(e0) <= TOL_ENV)}
    return res


BRACKET = ("io.bracket", "fasteners.e1_bracket")


def reread(path, asm):
    """Relê o GLB: nomes, ids, âncoras e escala. A escala é conferida sem o bracket (como o
    envelope): as línguas do bracket ficam abaixo de y = 0 e a chapa em x negativo."""
    data = path.read_bytes()
    js, binary = read_glb(path)
    names = [n.get("name") for n in js["nodes"]]
    dup = sorted({n for n in names if names.count(n) > 1})
    ids = [p["id"] for p in asm["parts"]]
    anchors = [a["id"] for p in asm["parts"] for a in p["anchors"]]
    sc = trimesh.load(path, force="scene")
    ext_all = sc.extents
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for n in js["nodes"]:
        nm = n.get("name", "")
        if "mesh" not in n or any(nm == b or nm.startswith(b + ".") for b in BRACKET):
            continue
        assert "matrix" not in n and not n.get("translation") and not n.get("rotation") and not n.get("scale"), nm
        v = accessor(js, binary, js["meshes"][n["mesh"]]["primitives"][0]["attributes"]["POSITION"])
        lo, hi = np.minimum(lo, v.min(0)), np.maximum(hi, v.max(0))
    ext = hi - lo
    return {"bytes": len(data), "sha256_12": hashlib.sha256(data).hexdigest()[:12], "nodes": len(js["nodes"]),
            "meshes": len(js["meshes"]), "ids_missing": [i for i in ids if i not in names],
            "anchors_missing": [a for a in anchors if a not in names], "duplicate_names": dup,
            "extents_m_gltf": [round(float(e), 4) for e in ext], "extents_m_gltf_com_bracket": [round(float(e), 4) for e in ext_all],
            "scale_ok": bool(abs(ext[0] - 0.3048) < 0.004 and abs(ext[1] - 0.040) < 0.001 and abs(ext[2] - 0.1372) < 0.002)}


# ---------------------------------------------------------------------------
# Imagens
# ---------------------------------------------------------------------------
def views(asm, R, detailed):
    DIST.mkdir(parents=True, exist_ok=True)
    L, H, T = B.M("card_envelope_length"), B.M("card_envelope_height"), B.M("card_thickness")
    c = np.array([L / 2, H / 2, T / 2])
    items = []
    for pid in (p["id"] for p in asm["parts"]):
        col = B.COLORS[B.group_of(pid)]
        if pid in detailed:
            col = (0.42, 0.45, 0.50)
        for b in B.all_bodies(R, pid):
            items.append((b, col, np.zeros(3)))
    size = (1400, 800)
    shots = [
        ("01-face-a-ventiladores.png", c + np.array([0, 0, 720]), [0, 1, 0], 26, "card.glb integrado: face A (ventiladores), vista de +z; bracket à esquerda e contatos embaixo, como pny/front"),
        ("02-face-b.png", c + np.array([0, 0, -720]), [0, -1, 0], 26, "card.glb integrado: face B, vista de -z com os contatos para cima, como pny/back"),
        ("03-topo.png", c + np.array([0, 720, 0]), [0, 0, 1], 26, "card.glb integrado: borda superior, vista de +y (face A em cima)"),
        ("04-tres-quartos.png", c + np.array([330, 420, 520]), [0, 1, 0], 30, "card.glb integrado: três quartos (face A e borda superior), como pny/3qtr-top-right"),
    ]
    for name, eye, up, fov, title in shots:
        B.render(items, eye, c, up, fov, size, DIST / name, title)
    # estágio E7: só as peças do PCB (o que sai no passo 7 da desmontagem), frente e verso
    P = {p["id"]: p for p in asm["parts"]}
    e7 = [(b, col, off) for (b, col, off), pid in zip(items, (pid for pid in P for _ in B.all_bodies(R, pid))) if P[pid]["stage"] == "E7"]
    ce = np.array([B.M("iface_pcb_center_x"), B.M("iface_pcb_center_y"), B.M("iface_pcb_front_z")])
    e7_shots = [
        ("05-estagio-e7-frente.png", ce + np.array([150, -230, 330]), [0, 1, 0], 30, "card.glb integrado: estágio E7 (PCB e componentes), frente do PCB (lado da face A), três quartos"),
        ("06-estagio-e7-verso.png", ce + np.array([-60, -120, -420]), [0, 1, 0], 30, "card.glb integrado: estágio E7, verso do PCB (lado da face B)"),
    ]
    for name, eye, up, fov, title in e7_shots:
        B.render(e7, eye, ce, up, fov, size, DIST / name, title)
    return [s[0] for s in shots + e7_shots]


# ---------------------------------------------------------------------------
def write_md(rep):
    L = []
    w = L.append
    w("# Relatório de integração: build/card.glb")
    w("")
    w("Gerado por `harness/parts/integrate.py` (não editar à mão). Referencial: face B em z = 0, face A (ventiladores) em z = 40; visto de +z, bracket à esquerda e contatos embaixo (assembly-plan, seção 11).")
    w("")
    g = rep["glb"]
    w("## GLB")
    w("")
    w("- Arquivo: `harness/build/card.glb`, %.1f kB, %d nós, %d malhas, sha256 %s." % (g["bytes"] / 1024, g["nodes"], g["meshes"], g["sha256_12"]))
    w("- Peças detalhadas: %s. As outras %d continuam em blockout." % (", ".join("`%s`" % d for d in rep["detalhadas"]), rep["n_partes"] - len(rep["detalhadas"])))
    w("- Releitura: extensão em metros (glTF, Y para cima) %s; escala %s. Ids sem nó: %s. Âncoras sem nó: %s. Nomes repetidos: %s." % (
        g["extents_m_gltf"], "ok" if g["scale_ok"] else "FALHA", g["ids_missing"] or "nenhum", g["anchors_missing"] or "nenhuma", g["duplicate_names"] or "nenhum"))
    w("- Compressão: nenhuma (sem Draco, que não abre por file://; meshopt fica para quando o arquivo crescer).")
    w("")
    w("## Envelope (sem o bracket)")
    w("")
    w("| eixo | mínimo | máximo | extensão | alvo | erro | ok |")
    w("|---|---|---|---|---|---|---|")
    for ax, e in rep["envelope"].items():
        w("| %s | %.2f | %.2f | %.2f | %.2f | %+.2f | %s |" % (ax, e["min"], e["max"], e["extent"], e["target"], e["error"], "sim" if e["ok"] else "NÃO"))
    w("")
    w("## Malhas")
    w("")
    bad = [m for m in rep["malhas"] if not m["ok"]]
    w("Corpos das peças detalhadas: %s. Corpos com problema: %s." % (
        ", ".join("%s (%d triângulos)" % (m["part"] + ("" if m["body"] == 1 else " #%d" % m["body"]), m["triangles"]) for m in rep["malhas"] if m["detailed"]),
        ", ".join("%s #%d" % (m["part"], m["body"]) for m in bad) or "nenhum"))
    w("")
    w("## Âncoras")
    w("")
    fa = [a for a in rep["ancoras"] if not a["ok"]]
    op = [a for a in rep["ancoras"] if a["kind"] == "opening"]
    w("%d âncoras, %d com problema. Âncoras de abertura (kind = opening no assembly; só precisam ficar na caixa da peça): %s." % (
        len(rep["ancoras"]), len(fa), ", ".join("`%s` (%.2f mm do corpo)" % (a["anchor"], a["dist_mm"]) for a in op) or "nenhuma"))
    for a in fa:
        w("- PROBLEMA `%s` (%s): %.2f mm" % (a["anchor"], a["part"], a["dist_mm"]))
    w("")
    w("## Interferências acima de %.1f mm" % TOL_OVERLAP)
    w("")
    w("| a | b | estágios | mm | classe | dono | motivo |")
    w("|---|---|---|---|---|---|---|")
    for q in sorted(rep["interferencias"], key=lambda q: ({"nova": 0, "pendencia": 1, "esperada": 2}[q["classe"]], -q["penetration_mm"])):
        w("| %s | %s | %s, %s | %.2f | %s | %s | %s |" % (q["a"], q["b"], q["stage_a"] or "fixa", q["stage_b"] or "fixa", q["penetration_mm"], q["classe"],
                                                     q.get("dono", ""), q.get("motivo", "")))
    w("")
    w("Classes: **nova** é interferência sem explicação (corrigir antes de seguir); **pendencia** é conflito de interface com dono, que depende de medida ou de decisão de outro agente (não foi corrigido em silêncio); **esperada** é sobreposição de propósito.")
    w("")
    w("## Vistas")
    w("")
    for v in rep["vistas"]:
        w("- `harness/dist/integracao/%s`" % v)
    w("")
    return "\n".join(L) + "\n"


def main():
    asm = json.loads(B.ASSEMBLY.read_text(encoding="utf-8"))
    R = B.build_parts(asm)
    found, ignored = load_detailed(asm)
    detail = {}
    for pid, (entry, keep) in found.items():
        R[pid] = entry
        detail[pid] = keep
    gltf, binary, idx = B.build_scene(asm, R, detail=detail, generator="harness/parts/integrate.py")
    gltf["asset"]["extras"]["referencial"] = "face B em z = 0, face A (ventiladores) em z = card_thickness; visto de +z, bracket à esquerda e contatos embaixo"
    B.write_glb(OUT, gltf, binary)
    print("GLB: %s (%d peças detalhadas: %s)" % (OUT.relative_to(HARNESS.parent), len(detail), ", ".join(sorted(detail))))
    if ignored:
        print("Arquivos em build/parts sem id no assembly (ignorados): %s" % ", ".join(ignored))
    rep = {"detalhadas": sorted(detail), "n_partes": len(asm["parts"]), "ignorados": ignored,
           "detalhe": {k: {kk: vv for kk, vv in v.items() if kk in ("source", "sha256_12", "generator")} for k, v in sorted(detail.items())}}
    rep["glb"] = reread(OUT, asm)
    rep["envelope"] = envelope(asm, R)
    rep["malhas"] = mesh_quality(R, detail)
    rep["ancoras"] = anchor_report(asm, R)
    rep["interferencias"] = interferences(asm, R, detail)
    rep["vistas"] = [] if "--sem-imagens" in sys.argv else views(asm, R, detail)
    REPORT_JSON.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    REPORT_MD.write_text(write_md(rep), encoding="utf-8")

    g = rep["glb"]
    print("Arquivo: %.1f kB, %d nós, %d malhas; extensão glTF (m) %s, escala %s" % (g["bytes"] / 1024, g["nodes"], g["meshes"], g["extents_m_gltf"], "ok" if g["scale_ok"] else "FALHA"))
    print("Ids sem nó: %s; âncoras sem nó: %s; nomes repetidos: %s" % (g["ids_missing"] or "nenhum", g["anchors_missing"] or "nenhuma", g["duplicate_names"] or "nenhum"))
    print("Envelope sem o bracket:")
    for ax, e in rep["envelope"].items():
        print("    %s: %.2f a %.2f = %.2f contra %.2f (erro %+.2f) %s" % (ax, e["min"], e["max"], e["extent"], e["target"], e["error"], "OK" if e["ok"] else "FALHA"))
    bad = [m for m in rep["malhas"] if not m["ok"]]
    print("Malhas com problema: %s" % (", ".join("%s #%d" % (m["part"], m["body"]) for m in bad) or "nenhuma"))
    fa = [a for a in rep["ancoras"] if not a["ok"]]
    print("Âncoras: %d, com problema: %s" % (len(rep["ancoras"]), ", ".join(a["anchor"] for a in fa) or "nenhuma"))
    for a in rep["ancoras"]:
        if a["kind"] == "opening" or a["dist_mm"] > 0.5:
            print("    %-40s %-22s %5.2f mm %s%s" % (a["anchor"], a["part"], a["dist_mm"], a["kind"], "" if a["ok"] else " PROBLEMA"))
    print("Interferências acima de %.1f mm:" % TOL_OVERLAP)
    for q in sorted(rep["interferencias"], key=lambda q: ({"nova": 0, "pendencia": 1, "esperada": 2}[q["classe"]], -q["penetration_mm"])):
        print("    %-10s %-24s x %-24s %5.2f mm  %s" % (q["classe"], q["a"], q["b"], q["penetration_mm"], q.get("dono", "")))
    print("Relatórios: %s e %s" % (REPORT_JSON.relative_to(HARNESS.parent), REPORT_MD.relative_to(HARNESS.parent)))
    ok = (all(e["ok"] for e in rep["envelope"].values()) and not g["ids_missing"] and not g["anchors_missing"]
          and not g["duplicate_names"] and g["scale_ok"] and not bad and not fa
          and not [q for q in rep["interferencias"] if q["classe"] == "nova"])
    print("Resultado: %s" % ("OK" if ok else "FALHA (ver relatório)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
