#!/usr/bin/env python3
"""Recalcula as contas a partir da cena desenhada e falha se o desenho divergir do spec.

Uso:  python3 harness/diagrams/test_diagrams.py

Não confia nos `checks` declarados: conta os nós desenhados (células de SM
habilitadas, bancos de registradores, threads, campos de bits) e compara com o spec.
Também confere que cada JSON é exatamente o que o seu script gera (nada à mão).
"""
import json
import re
import runpy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _kit import DIAGRAMS, SPEC_PATH  # noqa: E402

SPEC = {f["id"]: f["value"] for f in json.loads(SPEC_PATH.read_text(encoding="utf-8"))["facts"]}
D = {json.loads(p.read_text(encoding="utf-8"))["id"]: json.loads(p.read_text(encoding="utf-8"))
     for p in sorted(DIAGRAMS.glob("*.json"))}
PREFIX = {"chip.floorplan": "chip.", "chip.sm": "sm.", "chip.warp": "warp.", "chip.isa": "isa.",
          "chip.risc": "risc.", "chip.memhier": "memh.", "sys.mmu": "mmu.", "sys.irq": "irq.",
          "close.delta": "delta.", "close.gaps": "gaps.", "sys.cmd": "cmd."}


def nodes(did, kind=None, tag=None, enabled=None):
    out = []
    for n in D[did]["nodes"]:
        if kind and n["kind"] != kind:
            continue
        if tag and tag not in n.get("tags", []):
            continue
        if enabled is not None and (n.get("state") != "disabled") != enabled:
            continue
        out.append(n)
    return out


def inside(a, b, tol=1e-6):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[0] + a[2] <= b[0] + b[2] + tol \
        and a[1] + a[3] <= b[1] + b[3] + tol


class Projeto(unittest.TestCase):
    def test_todos_os_diagramas_existem(self):
        self.assertEqual(set(D), set(PREFIX))

    def test_ids_unicos_no_projeto_e_prefixo(self):
        seen = {}
        for did, d in D.items():
            for item in d["nodes"] + d["flows"]:
                self.assertTrue(item["id"].startswith(PREFIX[did]), item["id"])
                self.assertNotIn(item["id"], seen, f"{item['id']} em {did} e {seen.get(item['id'])}")
                seen[item["id"]] = did

    def test_json_e_o_que_o_script_gera(self):
        for did, d in D.items():
            script = HERE / d["generated_by"].split("/")[-1]
            g = runpy.run_path(str(script), run_name="teste")["d"]
            self.assertEqual(json.loads(json.dumps(g.data(d["generated_by"]), ensure_ascii=False)), d,
                             f"{did}: o JSON difere do que {script.name} gera (editado à mão ou desatualizado)")

    def test_contagens_batem_com_o_spec(self):
        for did, d in D.items():
            for n in d["nodes"]:
                self.assertIn("shape_provenance", n)
                if "count" in n:
                    c = n["count"]
                    self.assertEqual(SPEC[c["claim"]], c["value"], n["id"])
                for cl in n.get("claims", []):
                    self.assertIn(cl, SPEC, n["id"])

    def test_contas_declaradas(self):
        for did, d in D.items():
            counts = {n["id"]: n["count"]["value"] for n in d["nodes"] if "count" in n}
            for chk in d["checks"]:
                expr = chk["expr"]
                for nid in sorted(counts, key=len, reverse=True):
                    expr = expr.replace(nid, repr(counts[nid]))
                self.assertNotRegex(expr, r"[a-z_]", chk["expr"])
                self.assertEqual(eval(expr, {"__builtins__": {}}), chk["expect"], f"{did}: {chk['expr']}")

    def test_geometria_filho_dentro_do_pai_e_embed_unico(self):
        embeds = []
        for did, d in D.items():
            byid = {n["id"]: n for n in d["nodes"]}
            for n in d["nodes"]:
                if n.get("parent"):
                    self.assertTrue(inside(n["rect"], byid[n["parent"]]["rect"]), f"{n['id']} fora de {n['parent']}")
                if n.get("embed"):
                    embeds.append(n["embed"])
                    self.assertIn(n["embed"], D)
        self.assertEqual(sorted(embeds), sorted(set(embeds)), "diagrama embutido em mais de um lugar")
        self.assertEqual(sorted(embeds), ["chip.sm", "chip.warp"])


class Planta(unittest.TestCase):
    def test_gpcs_tpcs_sms(self):
        gpcs, tpcs = nodes("chip.floorplan", "gpc"), nodes("chip.floorplan", "tpc")
        self.assertEqual(len(gpcs), SPEC["chip.gpc_count"])                                  # 12
        self.assertEqual(len(tpcs), SPEC["chip.gpc_count"] * SPEC["chip.tpc_per_gpc"])       # 96
        self.assertEqual(len(tpcs), SPEC["chip.tpc_count_full"])
        on_tpc = [t for t in tpcs if t.get("state") != "disabled"]
        self.assertEqual(len(on_tpc), SPEC["chip.tpc_count"])                                # 94
        on_sm = nodes("chip.floorplan", "sm", enabled=True)
        self.assertEqual(len(on_sm), len(on_tpc) * SPEC["chip.sm_per_tpc"])                  # 94 x 2
        self.assertEqual(len(on_sm), SPEC["chip.sm_count"])                                  # 188
        self.assertEqual(len(on_sm) * SPEC["sm.cuda_cores"], SPEC["chip.cuda_cores"])        # 24.064
        self.assertEqual(len(nodes("chip.floorplan", "sm")), SPEC["chip.sm_count_full"])     # 192 posições

    def test_cada_tpc_tem_dois_sms_no_mesmo_estado(self):
        sms = nodes("chip.floorplan", "sm")
        for t in nodes("chip.floorplan", "tpc"):
            kids = [s for s in sms if s["parent"] == t["id"]]
            self.assertEqual(len(kids), SPEC["chip.sm_per_tpc"], t["id"])
            self.assertTrue(all(s.get("state") == t.get("state") for s in kids), t["id"])
            if t.get("state") == "disabled":
                self.assertIn("note", t)

    def test_zoom_e_memoria(self):
        zoom = nodes("chip.floorplan", tag="sm-zoom")
        self.assertEqual(len(zoom), 1)
        self.assertEqual(zoom[0].get("embed"), "chip.sm")
        self.assertNotEqual(zoom[0].get("state"), "disabled")
        mcs = nodes("chip.floorplan", "memctl")
        self.assertEqual(len(mcs), SPEC["chip.mem_controllers"])
        self.assertEqual(sum(m["count"]["value"] for m in mcs), SPEC["mem.bus_bits"])        # 16 x 32
        flows = [f for f in D["chip.floorplan"]["flows"] if f["from"] == "chip.l2" and f["path"] == "data"]
        self.assertEqual(sorted(f["to"] for f in flows), sorted(m["id"] for m in mcs))


class SM(unittest.TestCase):
    def test_blocos_registradores_nucleos(self):
        blocks = nodes("chip.sm", "block")
        self.assertEqual(len(blocks), SPEC["sm.blocks"])
        regs = nodes("chip.sm", "regfile")
        self.assertEqual(len(regs), SPEC["sm.blocks"])
        self.assertEqual(sum(r["count"]["value"] for r in regs), SPEC["sm.regfile_entries"])  # 4 x 16.384
        self.assertEqual(SPEC["sm.regfile_entries"] * 4 // 1024, SPEC["sm.regfile_kb"])      # 256 KB
        self.assertEqual(len(nodes("chip.sm", "core")), SPEC["sm.cuda_cores"])               # 4 x 32
        self.assertEqual(len(nodes("chip.sm", "tensor")), SPEC["sm.tensor_cores"])
        self.assertEqual(len(nodes("chip.sm", "tex")), SPEC["sm.tex_units"])
        self.assertEqual(len(nodes("chip.sm", "rt")), SPEC["sm.rt_cores"])
        self.assertEqual(len(nodes("chip.sm", "ldst")), SPEC["sm.blocks"] * SPEC["sm.block_ldst_units"])
        for b in blocks:
            bt = [t for t in b["tags"] if t.startswith("block-")][0]
            self.assertEqual(len(nodes("chip.sm", "sched", tag=bt)), 1)

    def test_warp_no_escalonador_do_bloco_0(self):
        w = nodes("chip.sm", tag="warp-zoom")
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0]["embed"], "chip.warp")
        sched = [n for n in D["chip.sm"]["nodes"] if n["id"] == "sm.block.0.sched"][0]
        self.assertTrue(inside(w[0]["rect"], sched["rect"]))


class Warp(unittest.TestCase):
    def test_32_threads_4_divergentes(self):
        th = nodes("chip.warp", "thread") + nodes("chip.warp", "thread-alt")
        self.assertEqual(len(th), SPEC["warp.size"])
        self.assertEqual(sorted(int(t["label"]) for t in th), list(range(SPEC["warp.size"])))
        alt = sorted(int(t["label"]) for t in nodes("chip.warp", "thread-alt"))
        self.assertEqual(alt, [28, 29, 30, 31])
        self.assertEqual(alt, sorted(int(t["label"]) for t in nodes("chip.warp", tag="diverged")))
        self.assertEqual(SPEC["sm.max_warps"] * SPEC["warp.size"], SPEC["sm.max_threads"])   # 48 x 32
        xs = sorted({t["rect"][0] for t in th})
        ys = sorted({t["rect"][1] for t in th})
        self.assertEqual((len(xs), len(ys)), (8, 4))


class ISA(unittest.TestCase):
    def test_linhas_e_palavra(self):
        self.assertEqual(len(nodes("chip.isa", tag="cuda")) - 1, 6)   # 6 linhas + cabeçalho
        ptx = [n for n in nodes("chip.isa", "codeline", tag="ptx")]
        sass = [n for n in nodes("chip.isa", "codeline", tag="sass")]
        self.assertEqual(len(ptx), SPEC["ex.saxpy.ptx_instructions"])
        self.assertEqual(len(sass), 20)
        self.assertEqual(len([n for n in sass if "useful" in n["tags"]]), SPEC["ex.saxpy.sass_useful"])
        self.assertFalse(any("NOP" in n["label"] for n in sass))
        text = (HERE.parent / "examples" / "saxpy-cu" / "saxpy.sm_120.sass").read_text(encoding="utf-8")
        m = re.search(r"FFMA[^/]*/\* (0x[0-9a-f]{16}) \*/\s*/\* (0x[0-9a-f]{16}) \*/", text)
        words = [n["label"] for n in nodes("chip.isa", tag="word-hex")]
        self.assertEqual(words, [m.group(1), m.group(2)])
        maps = [f for f in D["chip.isa"]["flows"] if f["id"].startswith("isa.map.")]
        self.assertEqual(len(maps), 12 + 5)                          # Tabela 3 + tid, mul.wide, 2 add.s64
        self.assertTrue(all(f["provenance"] == "derived" for f in maps))
        row1 = nodes("chip.isa", tag="field-row-1")
        self.assertEqual(sum(n["count"]["value"] for n in row1), 8 * SPEC["isa.instruction_bytes"])  # 91+23+14
        row2 = nodes("chip.isa", tag="field-row-2")
        instr = [n for n in row1 if "field-instr" in n["tags"]][0]["rect"]
        for n in row2:   # opcode e predicado aninhados sob a caixa "instrução"
            self.assertTrue(n["rect"][0] >= instr[0] and n["rect"][0] + n["rect"][2] <= instr[0] + instr[2])
            self.assertGreater(n["rect"][1], instr[1] + instr[3] - 1e-6)
        for n in sass:
            reg_r = bool(re.search(r"(?<![A-Z_])R\d+", n["label"]))
            self.assertEqual(reg_r, "reg-r" in n["tags"], n["label"])


class MMU(unittest.TestCase):
    def test_campos_somam_57(self):
        fields = nodes("sys.mmu", "field")
        bits = []
        for f in fields:
            m = re.fullmatch(r"\[(\d+)(?::(\d+))?\]", f["label"])
            hi, lo = int(m.group(1)), int(m.group(2) or m.group(1))
            bits.append(hi - lo + 1)
        self.assertEqual(sum(bits), SPEC["mmu.va_bits"])
        self.assertEqual(bits[:5], [int(b) for b in re.findall(r"\d+", SPEC["mmu.index_bits"])])
        per_bit = [f["rect"][2] / b for f, b in zip(fields, bits) if b > 1]
        self.assertLess(max(per_bit) - min(per_bit), 1e-6, "largura dos campos não é proporcional aos bits")
        self.assertEqual(len(nodes("sys.mmu", "step", tag="level")), SPEC["mmu.levels"])

    def test_tamanhos_de_pagina(self):
        cells = nodes("sys.mmu", "cell", tag="page-sizes")
        self.assertEqual(len(cells), 4)
        for c in cells:
            a, b, total = map(int, re.findall(r"\d+", c["sublabel"]))
            self.assertEqual(a + b, total)
            self.assertEqual(total, SPEC["mmu.va_bits"])


class Sistema(unittest.TestCase):
    def test_xid_sem_ligacao_com_trap(self):
        xid13 = [n for n in D["sys.irq"]["nodes"] if n.get("label") == "Xid 13"][0]
        xid31 = [n for n in D["sys.irq"]["nodes"] if n.get("label") == "Xid 31"][0]
        self.assertNotIn("mech-2", xid13["tags"])
        self.assertIn("xid-log", xid13["tags"])
        self.assertIn("mech-3", xid31["tags"])
        trap = {n["id"] for n in nodes("sys.irq", tag="trap")}
        for f in D["sys.irq"]["flows"]:
            self.assertFalse(f["from"] in trap and f["to"] in (xid13["id"], xid31["id"]))

    def test_tres_mecanismos_e_lacunas(self):
        for k in (1, 2, 3):
            self.assertTrue(nodes("sys.irq", tag=f"mech-{k}"))
        self.assertEqual(nodes("sys.irq", "gap"), [])        # o envio de comandos agora tem fonte (sys.cmd)
        inferred = [n for n in nodes("sys.irq", "note") if n.get("provenance") == "inferred"]
        self.assertEqual(len(inferred), 1)
        mig = [n for n in D["sys.irq"]["nodes"] if n["id"] == "irq.mig"][0]
        self.assertEqual(len([n for n in nodes("sys.irq", tag="mig") if n["parent"] == "irq.mig"]),
                         mig["count"]["value"])

    def test_conclusao_risc_e_inferida(self):
        c = nodes("chip.risc", tag="conclusion")
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["provenance"], "inferred")


class Fechamento(unittest.TestCase):
    def test_barras_proporcionais_e_valores(self):
        pairs = {"sm": ("ada.sm_count", "chip.sm_count"), "l2": ("ada.l2_kb", "chip.l2_kb"),
                 "mem": ("ada.mem_gb", "mem.capacity_gb"), "tgp": ("ada.tgp_w", "card.tgp_w"),
                 "bw": ("ada.bandwidth_gbs", "mem.bandwidth_gbs")}
        byid = {n["id"]: n for n in D["close.delta"]["nodes"]}
        for k, (fa, fb) in pairs.items():
            a, b = byid[f"delta.{k}.ada"], byid[f"delta.{k}.bw"]
            self.assertEqual((a["count"]["value"], b["count"]["value"]), (SPEC[fa], SPEC[fb]))
            self.assertAlmostEqual(a["rect"][2] / b["rect"][2], SPEC[fa] / SPEC[fb], places=4)  # rect arredondado a 0,01
            self.assertIn(f"row-{k}", a["tags"])
        self.assertEqual(len(nodes("close.delta", tag="conflict")), 1)

    def test_lacunas_por_item(self):
        items = nodes("close.gaps", tag="item")
        self.assertEqual(len(items), 8)
        for it in items:
            rt = [t for t in it["tags"] if t.startswith("row-")][0]
            self.assertEqual(len([n for n in nodes("close.gaps", "gap") if rt in n["tags"]]), 1, rt)
            self.assertEqual(len([n for n in nodes("close.gaps", tag="known") if rt in n["tags"]]), 1, rt)

    def test_gpfifo(self):
        self.assertEqual(len(nodes("sys.cmd", tag="pointer")), 2)
        self.assertTrue(nodes("sys.cmd", tag="gpfifo-entry"))
        user = [n for n in D["sys.cmd"]["nodes"] if "cmd.user_path" in n.get("claims", [])]
        self.assertEqual([n["provenance"] for n in user], ["derived"])
        for n in nodes("sys.cmd", "step"):
            self.assertTrue(any(c.startswith("cmd.") for c in n.get("claims", [])), n["id"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
