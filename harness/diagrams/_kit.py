"""Funções comuns dos scripts build_<id>.py (contrato em diagrams/README.md).

Só biblioteca padrão. Cada script monta um Diagram, lê os números do spec pelo
id do fato e grava diagrams/<id>.json. Nenhum número desenhado é digitado à mão:
`count=` e `claims=` apontam para fatos de spec/card.spec.json, e o kit falha
alto se o fato não existir.
"""
import json
import re
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
DIAGRAMS = HARNESS / "diagrams"
SPEC_PATH = HARNESS / "spec" / "card.spec.json"
EXAMPLES = HARNESS / "examples"

W, H = 1600, 900          # tamanho padrão
MARGIN = 12               # nada encostado na borda

_SPEC = None


def spec():
    global _SPEC
    if _SPEC is None:
        _SPEC = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    return _SPEC


def fact(fid):
    """Fato do spec pelo id; falha alto se não existir."""
    for f in spec()["facts"]:
        if f["id"] == fid:
            return f
    raise KeyError(f"fato {fid!r} não está em {SPEC_PATH.name}: não invente, declare a lacuna")


def val(fid):
    return fact(fid)["value"]


def gap(gid):
    """Lacuna declarada do spec (lista `gaps`); falha alto se não existir."""
    for g in spec()["gaps"]:
        if g["id"] == gid:
            return g
    raise KeyError(f"lacuna {gid!r} não está em {SPEC_PATH.name}")


def br(n, dec=None):
    """Número no formato PT-BR: 24064 -> '24.064', 92.2 -> '92,2'."""
    if isinstance(n, bool):
        raise TypeError("booleano não é número")
    if dec is None:
        dec = 0 if float(n).is_integer() else len(repr(float(n)).split(".")[1])
    s = f"{n:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def kb_to_mb(kb):
    mb = kb / 1024
    return br(mb)


def _r(v):
    v = round(float(v), 2)
    return int(v) if v.is_integer() else v


ID_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")
TAG_RE = re.compile(r"^[a-z0-9_\-]+$")


def _check_id(i):
    if not ID_RE.match(i):
        raise ValueError(f"id fora do padrão do schema: {i!r}")


class Diagram:
    def __init__(self, did, prefix, level, title, disclaimer, size=(W, H)):
        self.id, self.prefix, self.level = did, prefix, level
        self.title, self.disclaimer, self.size = title, disclaimer, list(size)
        self.nodes, self.flows, self.checks = [], [], []
        self._ids = set()

    # ---- nós ----
    def node(self, nid, kind, rect, label=None, sublabel=None, *, parent=None, tags=(),
             count=None, unit=None, claims=(), provenance=None, shape="illustrative",
             state=None, note=None, embed=None, mono=False, align=None, label_size=None):
        if not nid.startswith(self.prefix + "."):
            raise ValueError(f"{nid}: id fora do prefixo {self.prefix}.")
        if nid in self._ids:
            raise ValueError(f"{nid}: id repetido")
        _check_id(nid)
        for t in tags:
            if not TAG_RE.match(t):
                raise ValueError(f"{nid}: tag fora do padrão: {t!r}")
        x, y, w, h = rect
        sw, sh = self.size
        if w <= 0 or h <= 0 or x < MARGIN - 1e-6 or y < MARGIN - 1e-6 \
                or x + w > sw - MARGIN + 1e-6 or y + h > sh - MARGIN + 1e-6:
            raise ValueError(f"{nid}: retângulo {rect} encosta na borda ou sai de {self.size}")
        if parent is not None and parent not in self._ids:
            raise ValueError(f"{nid}: parent {parent} ainda não existe (contêiner antes do conteúdo)")
        n = {"id": nid, "kind": kind, "rect": [_r(v) for v in rect]}
        if label is not None:
            n["label"] = label
        if sublabel is not None:
            n["sublabel"] = sublabel
        if label_size is not None:
            n["label_size"] = label_size
        if align:
            n["align"] = align
        if mono:
            n["mono"] = True
        n["parent"] = parent
        if tags:
            n["tags"] = list(dict.fromkeys(tags))
        if state:
            n["state"] = state
        if count is not None:
            f = fact(count)
            if f["provenance"] not in ("confirmed", "derived"):
                raise ValueError(f"{nid}: contagem de {count} é {f['provenance']}")
            if isinstance(f["value"], bool) or not isinstance(f["value"], (int, float)):
                raise ValueError(f"{nid}: {count} não é número ({f['value']!r}); use claims")
            c = {"value": f["value"]}
            u = unit if unit is not None else f.get("unit")
            if u:
                c["unit"] = u
            c["claim"] = count
            c["provenance"] = f["provenance"]
            n["count"] = c
        if claims:
            for cid in claims:
                fact(cid)
            n["claims"] = list(dict.fromkeys(claims))
        if provenance:
            n["provenance"] = provenance
        n["shape_provenance"] = shape
        if embed:
            n["embed"] = embed
        if note:
            n["note"] = note
        self.nodes.append(n)
        self._ids.add(nid)
        return n

    def get(self, nid):
        for n in self.nodes:
            if n["id"] == nid:
                return n
        raise KeyError(nid)

    # ---- fluxos ----
    def flow(self, fid, src, dst, *, path="control", provenance="illustrative", label=None,
             points=None, claim=None):
        if not fid.startswith(self.prefix + "."):
            raise ValueError(f"{fid}: id de fluxo fora do prefixo {self.prefix}.")
        if any(f["id"] == fid for f in self.flows) or fid in self._ids:
            raise ValueError(f"{fid}: id repetido")
        _check_id(fid)
        for end in (src, dst):
            if end not in self._ids:
                raise ValueError(f"fluxo {fid}: nó {end} não existe")
        f = {"id": fid, "from": src, "to": dst}
        if label:
            f["label"] = label
        if points:
            f["points"] = [[_r(a), _r(b)] for a, b in points]
        f["path"] = path
        f["provenance"] = provenance
        if claim:
            fact(claim)
            f["claim"] = claim
        self.flows.append(f)
        return f

    def check(self, expr, expect):
        self.checks.append({"expr": expr, "expect": expect})

    # ---- saída ----
    def data(self, generated_by):
        return {
            "id": self.id, "level": self.level, "title": self.title,
            "disclaimer": self.disclaimer, "size": self.size,
            "generated_by": generated_by,
            "nodes": self.nodes, "flows": self.flows, "checks": self.checks,
        }

    def write(self, script_file):
        name = Path(script_file).name
        out = DIAGRAMS / f"{self.id}.json"
        out.write_text(json.dumps(self.data(f"diagrams/{name}"), ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"{out.relative_to(HARNESS)}: {len(self.nodes)} nós, {len(self.flows)} fluxos, "
              f"{len(self.checks)} contas")
        return out


def grid(x, y, w, h, cols, rows, gap_x, gap_y=None):
    """Retângulos de uma grade, em ordem de linha (esquerda para a direita, de cima para baixo)."""
    gap_y = gap_x if gap_y is None else gap_y
    cw = (w - gap_x * (cols - 1)) / cols
    ch = (h - gap_y * (rows - 1)) / rows
    return [[x + c * (cw + gap_x), y + r * (ch + gap_y), cw, ch] for r in range(rows) for c in range(cols)]


def row(x, y, w, h, n, gap):
    return grid(x, y, w, h, n, 1, gap)[:n]


def center(rect):
    x, y, w, h = rect
    return x + w / 2, y + h / 2


# ---- estimativa de texto (mesma regra do viewer em viewer/src/diagrams.js) ----
_NARROW = set("ijlI.,:;'|!()[]{}`·")
_WIDE = set("mwMW@%")


def text_em(txt, mono=False):
    """Largura aproximada do texto em em (Inter ou JetBrains Mono)."""
    if mono:
        return 0.6 * len(txt)
    s = 0.0
    for ch in txt:
        if ch == " ":
            s += 0.28
        elif ch in _NARROW:
            s += 0.28
        elif ch in _WIDE:
            s += 0.86
        elif ch.isupper():
            s += 0.68
        elif ch.isdigit():
            s += 0.6
        else:
            s += 0.55
    return s


def containers(diagram):
    ids = {n["parent"] for n in diagram["nodes"] if n.get("parent")}
    return ids | {n["id"] for n in diagram["nodes"] if n.get("embed")}


def label_boxes(node, is_container):
    """Rótulos como o viewer desenha: lista de (texto, x, y_centro, altura, âncora, classe)."""
    x, y, w, h = node["rect"]
    mono = bool(node.get("mono"))
    esq = node.get("align") == "left"
    m = min(w, h)
    sz = node.get("label_size")

    def fit(txt, pref, maxw):
        return min(pref, maxw / max(0.5, text_em(txt, mono)))

    out = []
    lab, sub = node.get("label"), node.get("sublabel")
    if lab:
        if is_container:
            hh = sz or fit(lab, m * 0.06, w * 0.8)
            out.append((lab, x + m * 0.03, y + m * 0.03 + hh / 2, hh, "start", "titulo"))
        elif sub:
            h1 = sz or fit(lab, h * 0.34, w * 0.92)
            h2 = fit(sub, min(h1 * 0.8, h * 0.26), w * 0.92)
            total = h1 + h2 * 1.15
            y1 = y + (h - total) / 2 + h1 / 2
            ax = x + h * 0.25 if esq else x + w / 2
            out.append((lab, ax, y1, h1, "start" if esq else "middle", "rotulo"))
            out.append((sub, ax, y1 + h1 / 2 + h2 * 0.65, h2, "start" if esq else "middle", "sub"))
        else:
            hh = sz or fit(lab, h * 0.5, (w - h * 0.5) if esq else w * 0.92)
            out.append((lab, x + h * 0.25 if esq else x + w / 2, y + h / 2, hh,
                        "start" if esq else "middle", "rotulo"))
    elif sub and not is_container:
        hh = fit(sub, h * 0.4, w * 0.92)
        out.append((sub, x + w / 2, y + h / 2, hh, "middle", "sub"))
    return out


def text_extent(lbl, mono):
    txt, ax, cy, hh, anchor, _ = lbl
    tw = text_em(txt, mono) * hh
    x0 = ax if anchor == "start" else ax - tw / 2
    return [x0, cy - hh / 2, tw, hh]
