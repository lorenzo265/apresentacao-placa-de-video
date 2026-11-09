#!/usr/bin/env python3
"""Valida os contratos do harness.

Uso:  python3 harness/tools/validate.py            # valida os arquivos reais que existirem
      python3 harness/tools/validate.py --examples # valida os exemplos de harness/schemas/examples/

Além do JSON Schema, confere regras que o schema não expressa:
limite de palavras do texto, tempo de leitura, referências entre arquivos e as
contas declaradas nos diagramas. Sai com código 1 se houver erro.
"""
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HARNESS = Path(__file__).resolve().parent.parent
SCHEMAS = HARNESS / "schemas"

MAX_HEADLINE_WORDS = 8
MAX_CAPTION_WORDS = 35
SECONDS_PER_WORD = 0.4   # regra de leitura de story/video-plan.md, seção 6
READING_MARGIN_S = 2.0

REAL = {
    "card.spec": [HARNESS / "spec" / "card.spec.json"],
    "assembly": [HARNESS / "design" / "assembly.json"],
    "storyboard": [HARNESS / "story" / "storyboard.json"],
    "beats": [HARNESS / "content" / "pt-BR" / "beats.json"],
    "diagram": sorted((HARNESS / "diagrams").glob("*.json")),
}
EXAMPLES = {name: [SCHEMAS / "examples" / f"{name}.example.json"] for name in REAL}


def words(text):
    return len(text.split())


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(name, data):
    validator = Draft202012Validator(load(SCHEMAS / f"{name}.schema.json"))
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "(raiz)"
        yield f"{where}: {err.message}"


def check_beats_text(beats):
    for beat_id, text in beats["beats"].items():
        if words(text["headline"]) > MAX_HEADLINE_WORDS:
            yield f"{beat_id}: headline com mais de {MAX_HEADLINE_WORDS} palavras"
        if words(text["caption"]) > MAX_CAPTION_WORDS:
            yield f"{beat_id}: caption com mais de {MAX_CAPTION_WORDS} palavras"
        if re.search(r"\d", text["headline"] + text["caption"]) and not text["source_line"].strip():
            yield f"{beat_id}: texto com número e sem source_line"


def check_storyboard(story, beats, spec, diagram_ids):
    ids = [b["id"] for b in story["beats"]]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        yield f"{dup}: id de beat repetido"
    for cut, rule in story["cuts"].items():
        for ref in rule.get("beats", []):
            if ref not in ids:
                yield f"corte {cut}: beat {ref} não existe"
    for b in story["beats"]:
        if b["status"] != "ready":
            continue
        text = (beats or {}).get("beats", {}).get(b["id"])
        if beats is not None and text is None:
            yield f"{b['id']}: beat pronto sem texto em beats.json"
        if text is not None:
            need = words(text["caption"]) * SECONDS_PER_WORD + READING_MARGIN_S
            if b["hold"] < need:
                yield f"{b['id']}: hold de {b['hold']} s, a leitura pede {need:.1f} s"
            if spec is not None:
                known = {f["id"] for f in spec["facts"]}
                for claim in text["claims"]:
                    if claim not in known:
                        yield f"{b['id']}: claim {claim} não está em card.spec.json"
        if not b["provenance"]:
            yield f"{b['id']}: beat pronto sem procedência"
        if b.get("diagram") and diagram_ids is not None and b["diagram"] not in diagram_ids:
            yield f"{b['id']}: diagrama {b['diagram']} não existe"


def check_diagram(diagram, spec):
    counts = {n["id"]: n["count"]["value"] for n in diagram["nodes"] if "count" in n}
    facts = {f["id"]: f["value"] for f in spec["facts"]} if spec else None
    for node in diagram["nodes"]:
        claim = node.get("count", {}).get("claim")
        if claim and facts is not None:
            if claim not in facts:
                yield f"{node['id']}: claim {claim} não está em card.spec.json"
            elif facts[claim] != node["count"]["value"]:
                yield f"{node['id']}: desenha {node['count']['value']}, o spec diz {facts[claim]}"
    for check in diagram["checks"]:
        expr = check["expr"]
        if not re.fullmatch(r"[a-z0-9_. +\-*/()]+", expr):
            yield f"conta não aceita: {expr}"
            continue
        for node_id in sorted(counts, key=len, reverse=True):
            expr = expr.replace(node_id, repr(counts[node_id]))
        if re.search(r"[a-z_]", expr):
            yield f"conta usa nó sem contagem: {check['expr']}"
            continue
        got = eval(expr, {"__builtins__": {}})  # só números e operadores, filtrado acima
        if got != check["expect"]:
            yield f"conta não fecha: {check['expr']} = {got}, esperado {check['expect']}"


def main():
    files = EXAMPLES if "--examples" in sys.argv else REAL
    loaded, errors, seen = {}, [], 0
    for name, paths in files.items():
        loaded[name] = []
        for path in paths:
            if not path.exists():
                continue
            seen += 1
            data = load(path)
            loaded[name].append(data)
            errors += [f"{path.relative_to(HARNESS)}: {e}" for e in schema_errors(name, data)]
    if errors:  # sem schema válido, as regras cruzadas não fazem sentido
        print("\n".join(errors))
        return 1

    def first(name):
        return loaded[name][0] if loaded[name] else None

    spec, beats, story = first("card.spec"), first("beats"), first("storyboard")
    diagram_ids = {d["id"] for d in loaded["diagram"]} if loaded["diagram"] else None
    if beats:
        errors += [f"beats: {e}" for e in check_beats_text(beats)]
    if story:
        errors += [f"storyboard: {e}" for e in check_storyboard(story, beats, spec, diagram_ids)]
    for diagram in loaded["diagram"]:
        errors += [f"diagrama {diagram['id']}: {e}" for e in check_diagram(diagram, spec)]

    print("\n".join(errors) if errors else f"ok: {seen} arquivo(s) válido(s)")
    if seen == 0:
        print("nenhum contrato encontrado ainda (use --examples para testar os schemas)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
