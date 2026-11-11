#!/usr/bin/env python3
"""Passo do Blender da cadeia de fidelidade (ARCHITECTURE, seção 5.2): build/card.glb -> build/card_final.glb.

Recebe o GLB integrado (integrate.py) e devolve o mesmo GLB com detalhe de superfície, sem mudar
nenhuma dimensão, nome de nó, hierarquia, âncora ou extras dos nós. Contrato em
harness/viewer/README.md (seção "Contrato do passo do Blender").

O que faz, peça a peça (tabela PECAS):
  1. UV (TEXCOORD_0) por projeção inteligente do Blender, com margem de 8 px entre ilhas. Antes do
     empacotamento, cada ilha é escalada pela visibilidade das suas faces (raios para fora, contra o
     conjunto rígido da peça): parede interna e fundo de fresta ficam com menos texels, a face vista
     fica com mais. A ilha onde fica uma marca (texto, logotipo) ganha densidade extra.
  2. Assa em Cycles, na CPU, com semente e amostras fixas:
       - oclusão de ambiente (64 amostras, distância de 6 mm), só contra as peças que se movem junto
         com a peça na explosão (o "conjunto rígido": mesma cadeia de explode_cad), para a sombra de
         uma vizinha não ficar pintada quando ela sai;
       - normal em espaço tangente (OpenGL, +Y) com o nó Bevel do Cycles: o chanfro de 0,4 mm das
         arestas vivas vira mapa de normal, sem mexer em um vértice (a silhueta não muda);
       - posição (só nas peças com marca) e índice de material (peça com mais de um acabamento).
  3. Compõe em numpy: cor (sRGB, JPEG 90) a partir dos materiais de viewer/src/materials.json, com um
     desgaste leve nas arestas (curvatura tirada do próprio mapa de normal: 1 - nz) e as marcas
     douradas ("RTX PRO 6000" na tampa do X, logotipo NVIDIA na borda superior) com a cor de
     ouro.serigrafia; oclusão (PNG em tons de cinza, occlusionTexture); normal (PNG).
  4. Grava o GLB: só as malhas da tabela ganham UV, TANGENT, mapas e um material por acabamento (uma
     primitiva por material, nomes de materials.json: carcaca.anodizado, carcaca.tampa_x,
     carcaca.grade); posições e normais são as do arquivo de entrada, vértice a vértice (os vértices
     só se duplicam onde a UV ou a tangente corta). Sem Draco; texturas embutidas no bufferView.
     Depois da conferência, a geometria é comprimida sem perda com EXT_meshopt_compression
     (viewer/scripts/meshopt-glb.mjs, pacote meshoptimizer do viewer; o decodificador vai embutido no
     viewer e abre por file://). Sem node ou sem o pacote, o GLB sai sem compressão, com aviso.
  5. Confere: nós, filhos, extras e malhas fora da tabela idênticos; nas malhas trocadas, mesmo número
     de triângulos e o mesmo conjunto de posições; orçamento de texturas (12 MB).

Cor e marcas não ficam no cache: mudou materials.json, rode de novo e só a composição é refeita (os
mapas assados ficam em build/blender-cache/, chaveados pelo sha256 do card.glb e dos parâmetros).

Marcas (procedência):
  - "RTX PRO 6000": posição, ângulo, comprimento e altura das linhas face_b_text_* do CSV (derived,
    pny/back) e de extras.text_box_cad_mm de frame.center_covers; "RTX PRO" em negrito e "6000" em
    peso normal, como em pny/back e pny/3qtr-back-right. Fonte: Inter (a do viewer), não a da NVIDIA.
  - Logotipo NVIDIA: forma vetorial simples desenhada aqui (símbolo do olho e "nVIDIA" em Inter), sem
    arquivo de terceiros. Posição e tamanho medidos neste passo em pny/3qtr-top-right,
    pny/3qtr-back-right e storagereview/sr-3 (borda superior, sobre o ventilador da ponta, lendo do
    bracket para a ponta, topo das letras para a face B): illustrative, sem linha no CSV.

Determinístico: mesma entrada, mesmo arquivo (semente 0, amostras fixas, sem data, PNG e JPEG com
parâmetros fixos). Tempo medido (CPU de 4 núcleos, 2026-11-11): ver build/blender-pass-report.json.

Uso:   <python com bpy 5.3> -I harness/parts/blender_pass.py [--pecas id,id] [--sem-cache] [--escala 0.5] [--sem-meshopt]
Saídas: harness/build/card_final.glb, harness/build/blender-pass-report.json
"""
import argparse
import hashlib
import io
import json
import math
import os
import struct
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HARNESS = Path(__file__).resolve().parents[1]
SRC = HARNESS / "build" / "card.glb"
OUT = HARNESS / "build" / "card_final.glb"
REPORT = HARNESS / "build" / "blender-pass-report.json"
CACHE = HARNESS / "build" / "blender-cache"
MATS = HARNESS / "viewer" / "src" / "materials.json"
CSV = HARNESS / "design" / "measurements.csv"
FONTES = HARNESS / "viewer" / "node_modules" / "@fontsource" / "inter" / "files"

VERSAO = 4                 # muda quando o que é assado muda (invalida o cache)
AO_AMOSTRAS = 64
AO_DIST_MM = 6.0
BEVEL_MM = 0.4             # chanfro das arestas vivas (contrato: até 0,3 a 0,5 mm)
BEVEL_AMOSTRAS = 16
MARGEM_PX = 8
AO_SUAVE_PX = 1.2          # desfoque da oclusão (sigma, px) contra o ruído das 64 amostras
NORMAL_SUAVE_PX = 0.7      # idem no mapa de normal do chanfro
ORCAMENTO_MB = 12.0
JPEG_Q = 90

# id da malha -> resolução e mapas. 'acab' diz o material de cada triângulo (função em ACABAMENTOS);
# 'cor' gera baseColor (desgaste e marcas), 'normal' o chanfro, 'ao' a oclusão.
CARCACA = dict(cor=True, normal=True, ao=True)
SO_AO = dict(cor=False, normal=False, ao=True)
PECAS = {
    "frame.shroud": dict(res=2048, acab="carcaca_a", marca="logo", **CARCACA),
    "frame.face_b": dict(res=2048, acab="face_b", **CARCACA),
    "frame.rim": dict(res=1024, acab="carcaca", **CARCACA),
    "frame.center_covers.1": dict(res=1024, acab="tampa", **CARCACA),
    "frame.center_covers.2": dict(res=1024, acab="tampa", marca="texto", **CARCACA),
    "io.bracket": dict(res=1024, acab="bracket", **CARCACA),
    "cooler.fan.1": dict(res=1024, **SO_AO),
    "cooler.fan.2": dict(res=1024, **SO_AO),
    **{"cooler.fan.%d.blade.%d" % (f, b): dict(res=512, **SO_AO) for f in (1, 2) for b in range(1, 8)},
    "cooler.fins.1": dict(res=1024, ilhas=False, **SO_AO),
    "cooler.fins.2": dict(res=1024, ilhas=False, **SO_AO),
    "cooler.fins.3": dict(res=1024, ilhas=False, **SO_AO),
    "cooler.base": dict(res=1024, **SO_AO),
    "pcb.main": dict(res=1024, **SO_AO),
}
# slots de material: nome no GLB (ids de materials.json listados em materiais_glb, ou o id da peça)
ACABAMENTOS = {
    "carcaca": ["carcaca.anodizado"],
    # carcaça com a face A: tampas lisas do X (preto espelhado, como as tampas da face B) e lâminas das
    # grades; os triângulos de cada slot vêm das zonas que frame.py grava em material_zones_cad_mm
    "carcaca_a": ["carcaca.anodizado", "carcaca.tampa_x", "carcaca.grade"],
    "face_b": ["carcaca.anodizado", "carcaca.grade"],
    "tampa": ["carcaca.tampa_x"],
    "bracket": ["aco.bracket"],
}
# desgaste do fio da aresta (fração da cor de COR_DESGASTE): as tampas do X são preto brilhante sob verniz
# (viewer/src/materials.json, carcaca.tampa_x) e quase não mostram metal na aresta; o fio claro do X vem
# do chanfro dos braços (carcaca.anodizado), como em storagereview/sr-2
DESGASTE = {"carcaca.anodizado": 0.22, "carcaca.tampa_x": 0.04, "carcaca.grade": 0.0, "aco.bracket": 0.25}
COR_DESGASTE = "#8c8f93"   # alumínio sob o anodizado, visto só no fio da aresta

# Logotipo NVIDIA da borda superior (illustrative: medido neste passo nas referências, ver docstring)
LOGO = {"centro_x": 245.0, "centro_z": 20.0, "comprimento": 35.0, "altura_simbolo": 6.6}

GL = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


# ---------------------------------------------------------------------------------------------
# GLB: leitura e escrita
# ---------------------------------------------------------------------------------------------
def le_glb(path):
    b = path.read_bytes()
    assert b[:4] == b"glTF"
    L = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + L])
    o = 20 + L
    BL = struct.unpack("<I", b[o:o + 4])[0]
    return j, b[o + 8:o + 8 + BL], b


def acessor(j, binario, i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    n = NCOMP[a["type"]]
    dt = GL[a["componentType"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride")
    item = np.dtype(dt).itemsize * n
    if stride and stride != item:
        raw = np.frombuffer(binario, dtype=np.uint8, count=stride * a["count"], offset=off).reshape(-1, stride)[:, :item]
        arr = raw.copy().view(dt)
    else:
        arr = np.frombuffer(binario, dtype=dt, count=a["count"] * n, offset=off).copy()
    return arr.reshape(-1, n) if n > 1 else arr


class Escritor:
    """Monta o buffer binário e as listas de bufferViews e accessors do GLB de saída."""

    def __init__(self):
        self.partes, self.views, self.accs, self.off = [], [], [], 0

    def _view(self, dados, alvo=None):
        pad = (-self.off) % 4
        if pad:
            self.partes.append(b"\0" * pad)
            self.off += pad
        v = {"buffer": 0, "byteOffset": self.off, "byteLength": len(dados)}
        if alvo:
            v["target"] = alvo
        self.partes.append(dados)
        self.off += len(dados)
        self.views.append(v)
        return len(self.views) - 1

    def acessor(self, arr, tipo, alvo, minmax=False, normalizado=False):
        arr = np.ascontiguousarray(arr)
        ct = {np.dtype(np.float32): 5126, np.dtype(np.uint32): 5125, np.dtype(np.uint16): 5123}[arr.dtype]
        v = self._view(arr.tobytes(), alvo)
        a = {"bufferView": v, "componentType": ct, "count": int(arr.shape[0]), "type": tipo}
        if minmax:
            m = arr.reshape(arr.shape[0], -1)
            a["min"] = [float(x) for x in m.min(0)]
            a["max"] = [float(x) for x in m.max(0)]
        if normalizado:
            a["normalized"] = True
        self.accs.append(a)
        return len(self.accs) - 1

    def copia(self, j, binario, i):
        """Copia um accessor do arquivo de entrada byte a byte (mesmo tipo, mesmos min e max)."""
        a = dict(j["accessors"][i])
        arr = acessor(j, binario, i)
        bv = j["bufferViews"][a["bufferView"]]
        a["bufferView"] = self._view(np.ascontiguousarray(arr).tobytes(), bv.get("target"))
        a.pop("byteOffset", None)
        self.accs.append(a)
        return len(self.accs) - 1

    def imagem(self, dados, mime):
        return self._view(dados), mime

    def binario(self):
        b = b"".join(self.partes)
        return b + b"\0" * ((-len(b)) % 4)


def grava_glb(path, j, binario):
    js = json.dumps(j, ensure_ascii=False, separators=(",", ":"), sort_keys=False).encode("utf-8")
    js += b" " * ((-len(js)) % 4)
    total = 12 + 8 + len(js) + 8 + len(binario)
    out = struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<I4s", len(js), b"JSON") + js
    out += struct.pack("<I4s", len(binario), b"BIN\0") + binario
    path.write_bytes(out)
    return out


# ---------------------------------------------------------------------------------------------
# Dados do projeto
# ---------------------------------------------------------------------------------------------
def medidas():
    import csv
    with CSV.open(encoding="utf-8") as f:
        return {r["feature"]: float(r["value_mm"]) for r in csv.DictReader(f) if r["value_mm"].strip()}


def srgb_lin(h):
    c = np.array([int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def cad(p_m):
    """GLB (metros, Y para cima) -> CAD (mm, Z para cima): (x, y, z)_cad = (x, -z, y) * 1000."""
    p = np.asarray(p_m, dtype=np.float64) * 1000.0
    return np.stack([p[..., 0], -p[..., 2], p[..., 1]], -1)


def conjuntos_rigidos(j):
    """Chave do movimento de cada nó na explosão: cadeia (nó, direção, distância) dos ancestrais que se movem."""
    pai = {c: i for i, n in enumerate(j["nodes"]) for c in n.get("children", [])}
    chave = {}
    for i, n in enumerate(j["nodes"]):
        k, a = [], i
        while a is not None:
            e = j["nodes"][a].get("extras", {}).get("explode_cad")
            if e and e.get("distance", 0):
                k.append((j["nodes"][a]["name"], tuple(e["dir"]), e["distance"]))
            a = pai.get(a)
        chave[n["name"]] = tuple(k)
    return chave


# ---------------------------------------------------------------------------------------------
# Marcas: rasters em mm no plano da marca (u ao longo da leitura, v para o topo das letras)
# ---------------------------------------------------------------------------------------------
def fonte(peso, px):
    nomes = {700: "inter-latin-700-normal.woff", 600: "inter-latin-600-normal.woff", 400: "inter-latin-400-normal.woff"}
    p = FONTES / nomes[peso]
    if not p.exists():
        p = Path("/usr/share/fonts/opentype/inter/%s.otf" % {700: "Inter-Bold", 600: "Inter-SemiBold", 400: "Inter-Regular"}[peso])
    return ImageFont.truetype(str(p), px)


PXMM = 40  # resolução dos rasters das marcas


def raster_texto(trechos, comprimento, altura_max, larga=1.2):
    """Texto em uma linha: [(texto, peso), ...] com o comprimento dado (mm). A altura das maiúsculas sai
    da proporção da fonte com a letra alargada (as letras da placa são largas) e não passa de altura_max.
    Devolve o raster e a altura usada (mm)."""
    T = 400
    ims = []
    for txt, peso in trechos:
        f = fonte(peso, T)
        x0, y0, x1, y1 = f.getbbox(txt, anchor="ls")
        im = Image.new("L", (x1 - x0 + 4, T * 2), 0)
        ImageDraw.Draw(im).text((2 - x0, int(T * 1.4)), txt, font=f, fill=255, anchor="ls")
        ims.append((im, f.getbbox("H", anchor="ls")))
    cap = -ims[0][1][1]                        # altura do H (px) na fonte de 400 px
    W = sum(im.width for im, _ in ims)
    lin = Image.new("L", (W, T * 2), 0)
    x = 0
    for im, _ in ims:
        lin.paste(im, (x, 0))
        x += im.width
    caixa = lin.getbbox()
    lin = lin.crop((caixa[0], int(T * 1.4) - cap, caixa[2], int(T * 1.4)))
    h_mm = min(altura_max, comprimento * lin.height / (lin.width * larga))
    out = lin.resize((max(1, int(round(comprimento * PXMM))), max(1, int(round(h_mm * PXMM)))), Image.LANCZOS)
    return np.asarray(out, dtype=np.float32) / 255.0, h_mm


def raster_logo(comprimento, altura_simbolo):
    """Logotipo NVIDIA simplificado: símbolo (retângulo à direita, olho em amêndoa saindo pela esquerda,
    espiral aberta para a direita em volta da pupila) e a palavra 'nVIDIA' em letra larga."""
    S = 600                                    # px por altura do símbolo
    ws = int(S * 1.42)
    sim = Image.new("L", (ws, S), 0)
    d = ImageDraw.Draw(sim)

    def lente(cx, cy, meia_larg, meia_alt, n=160):
        # amêndoa: dois arcos de círculo que passam pelas pontas (cx +- meia_larg, cy)
        R = (meia_larg ** 2 + meia_alt ** 2) / (2 * meia_alt)
        a = math.asin(meia_larg / R)
        pts = []
        for t in np.linspace(-a, a, n):
            pts.append((cx + R * math.sin(t), cy - (R * math.cos(t) - (R - meia_alt))))
        for t in np.linspace(a, -a, n):
            pts.append((cx + R * math.sin(t), cy + (R * math.cos(t) - (R - meia_alt))))
        return pts

    cx, cy = ws * 0.42, S * 0.5
    d.rectangle([ws * 0.30, 0, ws - 1, S - 1], fill=255)            # bloco da direita
    d.polygon(lente(cx, cy, ws * 0.42, S * 0.40), fill=255)           # olho (sai pela esquerda)
    d.polygon(lente(cx, cy, ws * 0.33, S * 0.29), fill=0)             # miolo escuro
    r1, r2 = S * 0.22, S * 0.13
    d.pieslice([cx - r1, cy - r1, cx + r1, cy + r1], 35, 325, fill=255)   # espiral: anel aberto à direita
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=0)
    r3 = S * 0.075
    d.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], fill=255)            # pupila
    # palavra
    f = fonte(600, 520)
    x0, y0, x1, y1 = f.getbbox("nVIDIA", anchor="ls")
    pal = Image.new("L", (x1 - x0 + 8, 800), 0)
    ImageDraw.Draw(pal).text((4 - x0, 640), "nVIDIA", font=f, fill=255, anchor="ls")
    cap = -f.getbbox("V", anchor="ls")[1]
    pal = pal.crop((0, 640 - cap, pal.width, 640))
    pal = pal.crop((pal.getbbox()[0], 0, pal.getbbox()[2], pal.height))
    # composição: altura das letras = 0,5 da altura do símbolo, espaço de 0,2 símbolo, letra larga
    h_let = int(S * 0.5)
    pal = pal.resize((int(pal.width * h_let / pal.height * 1.25), h_let), Image.LANCZOS)
    gap = int(S * 0.2)
    W = ws + gap + pal.width
    im = Image.new("L", (W, S), 0)
    im.paste(sim, (0, 0))
    im.paste(pal, (ws + gap, S - h_let - int(S * 0.1)))
    escala = comprimento / W                    # mm por px
    alt = S * escala
    out = im.resize((int(round(comprimento * PXMM)), int(round(alt * PXMM))), Image.LANCZOS)
    assert abs(alt - altura_simbolo) < 1.5, "logotipo com proporção inesperada (%.2f mm)" % alt
    return np.asarray(out, dtype=np.float32) / 255.0


def amostra_raster(R, u, v):
    """Raster R (linhas = v de cima para baixo, colunas = u), centrado em (0, 0) mm; bilinear, 0 fora."""
    H, W = R.shape
    x = u * PXMM + W / 2 - 0.5
    y = -v * PXMM + H / 2 - 0.5
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    out = np.zeros(u.shape, np.float32)
    for dx, dy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi, yi = x0 + dx, y0 + dy
        ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
        out[ok] += (R[yi[ok], xi[ok]] * w[ok]).astype(np.float32)
    return out


def dentro_tri(q, T):
    """Pontos q (n, 2) dentro de algum triângulo T (m, 3, 2)."""
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    v0, v1 = c - a, b - a
    d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
    den = d00 * d11 - d01 * d01
    ok = np.abs(den) > 1e-12
    a, v0, v1, d00, d01, d11, den = a[ok], v0[ok], v1[ok], d00[ok], d01[ok], d11[ok], den[ok]
    v2 = q[:, None, :] - a[None]
    d20, d21 = (v2 * v0).sum(2), (v2 * v1).sum(2)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    return ((v >= -1e-6) & (w >= -1e-6) & (v + w <= 1 + 1e-6)).any(1)


def desvio_texto(j, c, r, up, M, H, folga=0.6):
    """Quanto (mm) o texto desce, perpendicular à leitura, para caber inteiro na face externa da tampa
    com folga: a caixa do CSV encosta na borda da tampa modelada. Limite: a tolerância das linhas do CSV."""
    no = next(n for n in j["nodes"] if n["name"] == "frame.center_covers.2")
    b = _GLB["bin"]
    p = j["meshes"][no["mesh"]]["primitives"][0]
    P = cad(acessor(j, b, p["attributes"]["POSITION"]))
    I = acessor(j, b, p["indices"]).reshape(-1, 3)
    T = P[I]
    T = T[np.all(np.abs(T[:, :, 2]) < 0.01, axis=1)][:, :, :2]
    L = M["face_b_text_length"]
    gu, gv = np.meshgrid(np.linspace(-L / 2 - folga, L / 2 + folga, 36), np.linspace(-H / 2 - folga, H / 2 + folga, 7))
    for d in np.arange(0.0, 3.01, 0.1):
        q = (c - up * d)[None] + gu.reshape(-1, 1) * r + gv.reshape(-1, 1) * up
        if dentro_tri(q, T).all():
            _GLB["desvio_texto_mm"] = round(float(d), 2)
            return d
    raise SystemExit("o texto não cabe na tampa dentro da tolerância do CSV (3 mm)")


_GLB = {}


def mascara_marca(peca, pos_cad, texel_mm, M, j):
    """Máscara (0 a 1) da marca da peça em cada texel, a partir do mapa de posição (CAD, mm)."""
    cfg = PECAS[peca]
    if cfg.get("marca") == "texto":
        no = next(n for n in j["nodes"] if n["name"] == "frame.center_covers")
        tb = no["extras"]["detail"]["text_box_cad_mm"]
        c = np.array([M["face_b_text_center_x"], M["iface_face_b_text_y"]])
        r = np.array(tb["reading_dir_xy"], float)
        r /= np.linalg.norm(r)
        up = np.array(tb["letter_up_xy"], float)
        up /= np.linalg.norm(up)
        R, h = raster_texto([("RTX PRO ", 700), ("6000", 400)], M["face_b_text_length"], M["face_b_text_height"])
        assert abs(h - M["face_b_text_height"]) <= 3.0, "altura do texto fora da tolerância do CSV"
        _GLB["altura_texto_mm"] = round(h, 2)
        c = c - up * desvio_texto(j, c, r, up, M, h)
        d = pos_cad[..., :2] - c
        u, v = d @ r, d @ up
        na_face = np.abs(pos_cad[..., 2] - tb["z"]) < 0.05
    else:  # logotipo na borda superior: leitura +x, topo das letras para a face B (-z)
        topo = M.get("card_envelope_height", 137.16)
        R = raster_logo(LOGO["comprimento"], LOGO["altura_simbolo"])
        u = pos_cad[..., 0] - LOGO["centro_x"]
        v = -(pos_cad[..., 2] - LOGO["centro_z"])
        na_face = np.abs(pos_cad[..., 1] - topo) < 0.05
    # filtro do tamanho do texel (antisserrilhado): desfoca o raster na escala do texel
    sig = max(0.5, 0.5 * texel_mm * PXMM)
    Rb = np.asarray(Image.fromarray((R * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig)), np.float32) / 255.0
    m = amostra_raster(Rb, u, v)
    return np.where(na_face, m, 0.0).astype(np.float32), float((R > 0.5).sum() / PXMM ** 2)


# ---------------------------------------------------------------------------------------------
# Blender
# ---------------------------------------------------------------------------------------------
def bl_cena(threads):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.seed = 0
    sc.cycles.use_animated_seed = False
    sc.cycles.use_denoising = False
    sc.cycles.use_adaptive_sampling = False
    sc.render.threads_mode = "FIXED"
    sc.render.threads = threads
    w = bpy.data.worlds.new("mundo")
    w.use_nodes = True
    sc.world = w
    w.light_settings.distance = AO_DIST_MM / 1000.0
    b = sc.render.bake
    b.margin_type = "EXTEND"
    b.use_clear = True
    b.use_selected_to_active = False
    return sc


def bl_objeto(nome, P, I, N):
    import bpy
    me = bpy.data.meshes.new(nome)
    me.vertices.add(len(P))
    me.vertices.foreach_set("co", P.astype(np.float32).ravel())
    me.loops.add(len(I) * 3)
    me.loops.foreach_set("vertex_index", I.astype(np.int32).ravel())
    me.polygons.add(len(I))
    me.polygons.foreach_set("loop_start", np.arange(0, len(I) * 3, 3, dtype=np.int32))
    me.update(calc_edges=True)
    if N is not None:
        me.polygons.foreach_set("use_smooth", np.ones(len(I), bool))
        me.normals_split_custom_set_from_vertices(N.astype(np.float32))
    ob = bpy.data.objects.new(nome, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def visibilidade(ob_alvo, oclusores, n_raios=24, dist=0.06):
    """Fração de raios que escapam de cada face (hemisfério da normal, 60 mm), contra o conjunto rígido."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import bpy
    dg = bpy.context.evaluated_depsgraph_get()
    vs, ps, base = [], [], 0
    for ob in oclusores:
        me = ob.data
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get("co", co)
        vi = np.empty(len(me.loops), np.int32)
        me.loops.foreach_get("vertex_index", vi)
        vs.append(co.reshape(-1, 3))
        ps.append(vi.reshape(-1, 3) + base)
        base += len(me.vertices)
    V = np.concatenate(vs)
    F = np.concatenate(ps)
    bvh = BVHTree.FromPolygons([tuple(v) for v in V.tolist()], [tuple(f) for f in F.tolist()], epsilon=0.0)
    me = ob_alvo.data
    n = len(me.polygons)
    cen = np.empty(n * 3, np.float32)
    me.polygons.foreach_get("center", cen)
    nor = np.empty(n * 3, np.float32)
    me.polygons.foreach_get("normal", nor)
    cen, nor = cen.reshape(-1, 3), nor.reshape(-1, 3)
    # direções fixas (espiral de Fibonacci na esfera), viradas para o lado da normal
    k = np.arange(n_raios) + 0.5
    z = 1 - 2 * k / n_raios
    t = math.pi * (1 + 5 ** 0.5) * k
    D = np.stack([np.sqrt(1 - z * z) * np.cos(t), np.sqrt(1 - z * z) * np.sin(t), z], 1)
    vis = np.zeros(n, np.float32)
    for i in range(n):
        nn = nor[i]
        o = cen[i] + nn * 2e-5
        esc, tot = 0, 0
        for d in D:
            c = float(d @ nn)
            if c <= 0.05:
                continue
            tot += c
            hit = bvh.ray_cast(Vector(o), Vector(d), dist)
            if hit[0] is None:
                esc += c
        vis[i] = esc / tot if tot else 0.0
    return vis


def bl_uv(ob, cfg, vis, foco):
    """Projeção inteligente, escala das ilhas pela visibilidade (e pela marca) e empacotamento."""
    import bmesh
    import bpy
    from bpy_extras import bmesh_utils
    res = cfg["res"]
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.0, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    n_ilhas = None
    if cfg.get("ilhas", True):
        bm = bmesh.from_edit_mesh(ob.data)
        uvl = bm.loops.layers.uv.active
        bm.faces.ensure_lookup_table()
        ilhas = bmesh_utils.bmesh_linked_uv_islands(bm, uvl)
        n_ilhas = len(ilhas)
        for ilha in ilhas:
            idx = np.array([f.index for f in ilha])
            area = np.array([f.calc_area() for f in ilha]) + 1e-12
            w = float((vis[idx] * area).sum() / area.sum())
            s = 0.3 + 0.7 * min(1.0, w / 0.6)            # fundo de fresta e parede interna: 0,3
            if foco is not None and foco[idx].any():
                s *= 2.2                                 # ilha da marca: mais texels
            uvs = [l[uvl].uv for f in ilha for l in f.loops]
            c = sum((uv.copy() for uv in uvs), uvs[0].copy() * 0) / len(uvs)
            for f in ilha:
                for l in f.loops:
                    l[uvl].uv = c + (l[uvl].uv - c) * s
        bmesh.update_edit_mesh(ob.data)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(rotate=True, margin_method="FRACTION", margin=MARGEM_PX / res, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")
    return n_ilhas


def bl_materiais(ob, slots, idx_mat, img):
    """Um material de assar por slot: Principled com o Bevel na normal, emissão = índice do slot."""
    import bpy
    ob.data.materials.clear()
    for k, nome in enumerate(slots):
        m = bpy.data.materials.new("%s|%s" % (ob.name, nome))
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        bev = nt.nodes.new("ShaderNodeBevel")
        bev.inputs["Radius"].default_value = BEVEL_MM / 1000.0
        bev.samples = BEVEL_AMOSTRAS
        nt.links.new(bev.outputs["Normal"], bsdf.inputs["Normal"])
        bsdf.inputs["Emission Strength"].default_value = 1.0
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.name = "slot"
        rgb.outputs[0].default_value = ((k + 1) / 8.0, 0, 0, 1)
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        soma = nt.nodes.new("ShaderNodeVectorMath")
        soma.name = "posicao"
        soma.operation = "ADD"
        soma.inputs[1].default_value = (1.0, 1.0, 1.0)      # posição + 1 m: emissão sempre positiva
        nt.links.new(geo.outputs["Position"], soma.inputs[0])
        nt.links.new(rgb.outputs[0], bsdf.inputs["Emission Color"])
        no = nt.nodes.new("ShaderNodeTexImage")
        no.image = img
        nt.nodes.active = no
        ob.data.materials.append(m)
    if len(slots) > 1:
        ob.data.polygons.foreach_set("material_index", idx_mat.astype(np.int32))
    ob.data.update()


def bl_emissao(ob, fonte_no):
    """Liga a emissão dos materiais da peça ao nó 'slot' (índice) ou 'posicao' (posição + 1 m)."""
    for m in ob.data.materials:
        nt = m.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        no = nt.nodes[fonte_no]
        nt.links.new(no.outputs[0], bsdf.inputs["Emission Color"])


def bl_assa(sc, ob, img, tipo, amostras):
    import bpy
    sc.cycles.samples = amostras
    sc.render.bake.margin = MARGEM_PX if img.size[0] >= 1024 else MARGEM_PX // 2
    kw = {}
    if tipo == "NORMAL":
        kw = dict(normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y", normal_b="POS_Z")
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.bake(type=tipo, **kw)
    W, H = img.size
    a = np.empty(W * H * 4, np.float32)
    img.pixels.foreach_get(a)
    return np.flipud(a.reshape(H, W, 4))      # linha 0 = topo da imagem = v do glTF em 0


def bl_cantos(ob):
    """UV por canto de triângulo (as tangentes saem de tangentes(), em numpy)."""
    me = ob.data
    nl = len(me.loops)
    uv = np.empty(nl * 2, np.float32)
    me.uv_layers.active.data.foreach_get("uv", uv)
    vi = np.empty(nl, np.int32)
    me.loops.foreach_get("vertex_index", vi)
    return uv.reshape(-1, 2), vi


# ---------------------------------------------------------------------------------------------
# Acabamentos (material de cada triângulo)
# ---------------------------------------------------------------------------------------------
def idx_acabamento(peca, P_cad, I):
    """Índice do slot de cada triângulo. Face B: lâminas da grade (topo em z = 0,5 e paredes das frestas
    abaixo dele, retas ou em V) no slot 1 (carcaca.grade); estrutura do X e moldura no slot 0.
    Carcaça com a face A (acab carcaca_a): zonas de material_zones_cad_mm do nó (frame.py), cada uma
    com material (nome do slot) e regras: normal_z_min (componente z mínima da normal), z (centro do
    triângulo nesse z, com tol), z_min e z_max (triângulo inteiro entre eles, com tol)."""
    cfg = PECAS[peca]
    T = P_cad[I]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
    zmin, zmax, zc = T[:, :, 2].min(1), T[:, :, 2].max(1), T[:, :, 2].mean(1)
    if cfg.get("acab") == "carcaca_a":
        slots = ACABAMENTOS["carcaca_a"]
        zonas = (_GLB.get("zonas") or {}).get(peca) or []
        assert zonas, "frame.shroud sem material_zones_cad_mm no card.glb (rode frame.py e integrate.py)"
        idx = np.zeros(len(I), np.int32)
        for zn in zonas:
            tol = zn.get("tol", 0.02)
            m = np.ones(len(I), bool)
            if "normal_z_min" in zn:
                m &= n[:, 2] >= zn["normal_z_min"]
            if "z" in zn:
                m &= np.abs(zc - zn["z"]) < tol
            if "z_min" in zn:
                m &= zmin >= zn["z_min"] - tol
            if "z_max" in zn:
                m &= zmax <= zn["z_max"] + tol
            idx[m & (idx == 0)] = slots.index(zn["material"])
        return idx
    if cfg.get("acab") != "face_b":
        return np.zeros(len(I), np.int32)
    topo_lamina = (n[:, 2] < -0.95) & (np.abs(zc - 0.5) < 0.02)
    # paredes das lâminas: retas (normal em x) ou em V (normal inclinada no plano xz), sempre abaixo do
    # topo das lâminas; as paredes das janelas começam em z = 0 e ficam de fora
    parede = (np.abs(n[:, 2]) < 0.95) & (np.abs(n[:, 1]) < 0.05) & (zmin >= 0.49)
    return (topo_lamina | parede).astype(np.int32)


# ---------------------------------------------------------------------------------------------
# Passo principal
# ---------------------------------------------------------------------------------------------
def png(arr, modo):
    b = io.BytesIO()
    Image.fromarray(arr, modo).save(b, "PNG", optimize=False, compress_level=9)
    return b.getvalue()


def jpeg(arr):
    b = io.BytesIO()
    Image.fromarray(arr, "RGB").save(b, "JPEG", quality=JPEG_Q, subsampling=0, optimize=False, progressive=False)
    return b.getvalue()


def chave_cache(src_sha, peca, cfg, escala):
    s = json.dumps({"v": VERSAO, "src": src_sha, "peca": peca, "cfg": cfg, "escala": escala, "ao": [AO_AMOSTRAS, AO_DIST_MM],
                    "bevel": [BEVEL_MM, BEVEL_AMOSTRAS], "margem": MARGEM_PX}, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def assa_pecas(j, binario, alvos, escala, usa_cache, src_sha, log):
    """Assa (ou lê do cache) UV, tangentes e mapas crus de cada peça da tabela."""
    rig = conjuntos_rigidos(j)
    _GLB["zonas"] = {n["name"]: (n.get("extras", {}).get("detail", {}) or {}).get("material_zones_cad_mm") for n in j["nodes"]}
    malhas = {}
    for n in j["nodes"]:
        if "mesh" not in n:
            continue
        pr = j["meshes"][n["mesh"]]["primitives"]
        assert len(pr) == 1, "esperava uma primitiva por malha no card.glb"
        p = pr[0]
        P = acessor(j, binario, p["attributes"]["POSITION"])
        I = acessor(j, binario, p["indices"]).reshape(-1, 3) if "indices" in p else np.arange(len(P)).reshape(-1, 3)
        N = acessor(j, binario, p["attributes"]["NORMAL"]) if "NORMAL" in p["attributes"] else None
        malhas[n["name"]] = (P, I, N)
    CACHE.mkdir(parents=True, exist_ok=True)
    crus, faltam = {}, []
    for peca in alvos:
        cfg = dict(PECAS[peca])
        f = CACHE / ("%s-%s.npz" % (peca, chave_cache(src_sha, peca, cfg, escala)))
        if usa_cache and f.exists():
            crus[peca] = dict(np.load(f))
            log("  %s: do cache" % peca)
        else:
            faltam.append((peca, f))
    if not faltam:
        return crus, malhas, {}
    import bpy  # noqa: F401  (só quando há o que assar)
    sc = bl_cena(os.cpu_count() or 4)
    obs = {nm: bl_objeto(nm, *malhas[nm]) for nm in malhas}
    tempos = {}
    for peca, f in faltam:
        t0 = time.time()
        cfg = PECAS[peca]
        res = max(256, int(cfg["res"] * escala))
        cfg_r = dict(cfg, res=res)
        P, I, N = malhas[peca]
        ob = obs[peca]
        grupo = [nm for nm in malhas if rig[nm] == rig[peca]]
        for nm, o in obs.items():
            o.hide_render = nm not in grupo
        P_cad = cad(P)
        foco = None
        if cfg.get("marca") == "logo":
            Tc = P_cad[I].mean(1)
            foco = (Tc[:, 1] > 137.0) & (np.abs(Tc[:, 0] - LOGO["centro_x"]) < 40)
        elif cfg.get("marca") == "texto":
            Tc = P_cad[I].mean(1)
            foco = Tc[:, 2] < 0.05
        vis = visibilidade(ob, [obs[nm] for nm in grupo]) if cfg.get("ilhas", True) else None
        t_vis = time.time() - t0
        n_ilhas = bl_uv(ob, cfg_r, vis, foco)
        t_uv = time.time() - t0 - t_vis
        img = bpy.data.images.new("assa_" + peca, res, res, alpha=False, float_buffer=True)
        img.colorspace_settings.name = "Non-Color"
        slots = ACABAMENTOS.get(cfg.get("acab"), [peca])
        idx = idx_acabamento(peca, P_cad, I)
        bl_materiais(ob, slots, idx, img)
        out = {}
        out["ao"] = bl_assa(sc, ob, img, "AO", AO_AMOSTRAS)[..., 0].astype(np.float16)
        if cfg["normal"]:
            out["normal"] = bl_assa(sc, ob, img, "NORMAL", BEVEL_AMOSTRAS)[..., :3].astype(np.float16)
        if cfg["cor"] and len(slots) > 1:
            bl_emissao(ob, "slot")
            out["slot"] = np.clip(np.rint(bl_assa(sc, ob, img, "EMIT", 4)[..., 0] * 8 - 1), 0, len(slots) - 1).astype(np.uint8)
        if cfg.get("marca"):
            bl_emissao(ob, "posicao")
            out["pos"] = (bl_assa(sc, ob, img, "EMIT", 1)[..., :3] - 1.0).astype(np.float32)
        uv, vi = bl_cantos(ob)
        out.update(uv=uv, vi=vi, idx=idx, tempo=np.float32(round(time.time() - t0, 1)))
        np.savez_compressed(f, **out)
        crus[peca] = out
        tempos[peca] = round(time.time() - t0, 1)
        bpy.data.images.remove(img)
        log("  %s: %d px, %s ilhas, visibilidade %.0f s, UV %.0f s, total %.0f s" % (
            peca, res, n_ilhas, t_vis, t_uv, tempos[peca]))
    return crus, malhas, tempos


def suaviza(a, sigma):
    """Desfoque gaussiano separável (borda repetida), para tirar o ruído das amostras do Cycles: a
    oclusão e o chanfro variam devagar perto do texel, o ruído não (e o ruído é o que pesa no PNG)."""
    r = max(1, int(math.ceil(sigma * 3)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    out = a.astype(np.float32)
    for eixo in (0, 1):
        pad = [(0, 0)] * out.ndim
        pad[eixo] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        n = out.shape[eixo]
        for i, w in enumerate(k):
            acc += w * (p[i:i + n] if eixo == 0 else p[:, i:i + n])
        out = acc
    return out


def compoe(peca, cru, malha, M, MAT, j):
    """Mapas finais (bytes) e estatísticas de uma peça."""
    cfg = PECAS[peca]
    res = cru["ao"].shape[0]
    ao = np.clip(suaviza(cru["ao"], AO_SUAVE_PX), 0, 1)
    mapas, est = {}, {"res": res, "ao_media": round(float(ao.mean()), 3)}
    mapas["ao"] = (png((ao * 255 + 0.5).astype(np.uint8), "L"), "image/png")
    if cfg["normal"]:
        v = suaviza(cru["normal"].astype(np.float32) * 2 - 1, NORMAL_SUAVE_PX)
        v /= np.maximum(np.linalg.norm(v, axis=2, keepdims=True), 1e-6)
        nrm = np.clip(v * 0.5 + 0.5, 0, 1)
        mapas["normal"] = (png((nrm * 255 + 0.5).astype(np.uint8), "RGB"), "image/png")
    if cfg["cor"]:
        slots = ACABAMENTOS[cfg["acab"]]
        sl = cru["slot"] if "slot" in cru else np.zeros((res, res), np.uint8)
        base = np.stack([srgb_lin(MAT[s]["cor"]) for s in slots])[sl]
        k = np.array([DESGASTE.get(s, 0.0) for s in slots])[sl]
        if cfg["normal"]:
            nz = np.clip(cru["normal"][..., 2].astype(np.float32) * 2 - 1, 0, 1)
            aresta = np.clip((1 - nz) * 3.0, 0, 1)
        else:
            aresta = np.zeros((res, res), np.float32)
        cor = base * (1 - (k * aresta)[..., None]) + srgb_lin(COR_DESGASTE) * (k * aresta)[..., None]
        if cfg.get("marca"):
            pos = cad(cru["pos"])
            P, I, _ = malha
            # tamanho do texel em mm: área 3D da malha / área UV ocupada
            T = cad(P)[I]
            a3 = np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1).sum() / 2
            U = cru["uv"].reshape(-1, 3, 2)
            e1, e2 = U[:, 1] - U[:, 0], U[:, 2] - U[:, 0]
            au = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]).sum() / 2
            texel = math.sqrt(a3 / (au * res * res))
            m, area = mascara_marca(peca, pos, texel, M, j)
            ouro = srgb_lin(MAT["ouro.serigrafia"]["cor"])
            cor = cor * (1 - m[..., None]) + ouro * m[..., None]
            est.update(marca=cfg["marca"], marca_area_mm2=round(area, 1), texel_medio_mm=round(texel, 3),
                       texels_na_marca=int((m > 0.5).sum()))
        mapas["cor"] = (jpeg((lin_srgb(cor) * 255 + 0.5).astype(np.uint8)), "image/jpeg")
    est["bytes"] = {k: len(v[0]) for k, v in mapas.items()}
    return mapas, est


def tangentes(P, N, uv, tri):
    """Tangentes por vértice (glTF TANGENT: xyz e o sinal da bitangente em w), pela derivada da UV de cada
    triângulo somada nos vértices e ortogonalizada contra a normal (Lengyel). Calculadas aqui, em numpy,
    porque Mesh.calc_tangents do Blender muda nos últimos bits de uma execução para outra (paralelismo);
    numa face plana com UV contínua dá a mesma base do mikktspace com que o Blender assou o mapa."""
    p = P[tri].astype(np.float64)
    t = uv[tri].astype(np.float64)
    e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
    d1, d2 = t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]
    det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(det) > 1e-20, 1.0 / np.where(det == 0, 1, det), 0.0)[:, None]
    T = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) * r
    B = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) * r
    # peso pela área do triângulo (em vez de 1 por triângulo)
    a = np.linalg.norm(np.cross(e1, e2), axis=1)[:, None]
    nt = np.linalg.norm(T, axis=1, keepdims=True)
    nb = np.linalg.norm(B, axis=1, keepdims=True)
    T = T / np.maximum(nt, 1e-30) * a
    B = B / np.maximum(nb, 1e-30) * a
    Tv = np.zeros((len(P), 3))
    Bv = np.zeros((len(P), 3))
    for k in range(3):
        np.add.at(Tv, tri[:, k], T)
        np.add.at(Bv, tri[:, k], B)
    n = N.astype(np.float64)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30)
    Tv -= n * (n * Tv).sum(1, keepdims=True)
    ln = np.linalg.norm(Tv, axis=1, keepdims=True)
    # vértice sem direção de UV (degenerado): qualquer perpendicular à normal
    alt = np.cross(n, np.where(np.abs(n[:, :1]) < 0.9, [[1.0, 0, 0]], [[0, 1.0, 0]]))
    Tv = np.where(ln > 1e-12, Tv / np.maximum(ln, 1e-30), alt / np.maximum(np.linalg.norm(alt, axis=1, keepdims=True), 1e-30))
    w = np.where((np.cross(n, Tv) * Bv).sum(1) < 0, -1.0, 1.0)
    return np.concatenate([Tv, w[:, None]], 1).astype(np.float32)


def nova_malha(cru, malha):
    """Vértices novos (um por combinação de vértice e UV), tangentes e índices por slot."""
    P, I, N = malha
    vi, uv = cru["vi"], cru["uv"]
    assert np.array_equal(vi, I.ravel().astype(np.int32)), "a ordem dos cantos mudou no Blender"
    q = np.concatenate([vi[:, None].astype(np.float64), np.round(uv.astype(np.float64) * 2 ** 20)], 1)
    _, primeiro, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    ordem = np.argsort(primeiro)                     # vértices na ordem em que aparecem (estável)
    novo = np.empty_like(ordem)
    novo[ordem] = np.arange(len(ordem))
    cantos = primeiro[ordem]
    idx_v = novo[inv.ravel()].reshape(-1, 3).astype(np.uint32)
    pos = P[vi[cantos]]
    nor = N[vi[cantos]] if N is not None else None
    uv_bl = uv[cantos]
    uv_gl = np.stack([uv_bl[:, 0], 1.0 - uv_bl[:, 1]], 1).astype(np.float32)
    tan = tangentes(pos, nor, uv_bl, idx_v.astype(np.int64)) if nor is not None else None
    return pos.astype(np.float32), nor, uv_gl, tan, idx_v, cru["idx"]


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pecas", default=None, help="só estas peças (ids separados por vírgula)")
    ap.add_argument("--sem-cache", action="store_true")
    ap.add_argument("--escala", type=float, default=1.0, help="fator de resolução dos mapas (teste rápido)")
    ap.add_argument("--saida", default=str(OUT))
    ap.add_argument("--sem-meshopt", action="store_true", help="não comprime a geometria (EXT_meshopt_compression)")
    a = ap.parse_args()
    t_ini = time.time()
    log = lambda s: print(s, flush=True)  # noqa: E731
    j, binario, bruto = le_glb(SRC)
    _GLB["bin"] = binario
    src_sha = hashlib.sha256(bruto).hexdigest()
    alvos = [p for p in PECAS if (a.pecas is None or p in a.pecas.split(","))]
    nomes = {n["name"] for n in j["nodes"]}
    faltando = [p for p in alvos if p not in nomes]
    if faltando:
        log("aviso: peças sem nó no card.glb: %s" % ", ".join(faltando))
        alvos = [p for p in alvos if p in nomes]
    M = medidas()
    MAT = json.loads(MATS.read_text(encoding="utf-8"))["materiais"]
    log("passo do Blender: %d peças, card.glb %s" % (len(alvos), src_sha[:12]))
    crus, malhas, tempos = assa_pecas(j, binario, alvos, a.escala, not a.sem_cache, src_sha, log)
    t_assa = time.time() - t_ini

    # --- GLB de saída ----------------------------------------------------------------------
    jo = json.loads(json.dumps(j))
    E = Escritor()
    jo["images"], jo["textures"], jo["samplers"] = [], [], [{"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071}]
    mats_out = list(j.get("materials", []))
    relat = {}
    no_por_malha = {n["mesh"]: n["name"] for n in j["nodes"] if "mesh" in n}

    def textura(dados, mime, nome):
        v, _ = E.imagem(dados, mime)
        jo["images"].append({"bufferView": v, "mimeType": mime, "name": nome})
        jo["textures"].append({"sampler": 0, "source": len(jo["images"]) - 1})
        return len(jo["textures"]) - 1

    for mi, mesh in enumerate(j["meshes"]):
        nome = no_por_malha.get(mi)
        p0 = mesh["primitives"][0]
        if nome not in crus:
            prims = []
            for p in mesh["primitives"]:
                q = dict(p)
                q["attributes"] = {k: E.copia(j, binario, v) for k, v in p["attributes"].items()}
                if "indices" in p:
                    q["indices"] = E.copia(j, binario, p["indices"])
                prims.append(q)
            jo["meshes"][mi]["primitives"] = prims
            continue
        cfg = PECAS[nome]
        mapas, est = compoe(nome, crus[nome], malhas[nome], M, MAT, j)
        pos, nor, uv, tan, idx_v, idx_t = nova_malha(crus[nome], malhas[nome])
        attrs = {"POSITION": E.acessor(pos, "VEC3", 34962, minmax=True)}
        if nor is not None:
            attrs["NORMAL"] = E.acessor(nor.astype(np.float32), "VEC3", 34962)
        assert uv.min() >= 0 and uv.max() <= 1, "UV fora de [0, 1]"
        attrs["TEXCOORD_0"] = E.acessor(np.round(uv * 65535).astype(np.uint16), "VEC2", 34962, normalizado=True)
        if cfg["normal"]:
            attrs["TANGENT"] = E.acessor(tan, "VEC4", 34962)
        tx = {k: textura(d, mime, "%s.%s" % (nome, k)) for k, (d, mime) in mapas.items()}
        slots = ACABAMENTOS.get(cfg.get("acab"), ["%s.mapas" % nome])
        prims = []
        for k, s in enumerate(slots):
            tri = idx_v[idx_t == k]
            if not len(tri):
                continue
            pbr = {"metallicFactor": 1.0, "roughnessFactor": 1.0}
            if "cor" in tx:
                pbr["baseColorTexture"] = {"index": tx["cor"]}
            else:
                pbr["baseColorFactor"] = j["materials"][p0["material"]]["pbrMetallicRoughness"]["baseColorFactor"] if "material" in p0 else [1, 1, 1, 1]
                pbr["metallicFactor"] = 0.0
            mat = {"name": s, "pbrMetallicRoughness": pbr, "occlusionTexture": {"index": tx["ao"]},
                   "extras": {"blender_pass": {"peca": nome, "mapas": sorted(tx)}}}
            if "normal" in tx:
                mat["normalTexture"] = {"index": tx["normal"]}
            mats_out.append(mat)
            ind = tri.ravel().astype(np.uint16 if len(pos) < 65536 else np.uint32)
            prims.append({"attributes": dict(attrs), "indices": E.acessor(ind, "SCALAR", 34963), "material": len(mats_out) - 1})
        jo["meshes"][mi]["primitives"] = prims
        est.update(vertices_antes=int(len(malhas[nome][0])), vertices_depois=int(len(pos)), triangulos=int(len(idx_v)),
                   slots={s: int((idx_t == k).sum()) for k, s in enumerate(slots)},
                   tempo_assar_s=tempos.get(nome, round(float(crus[nome]["tempo"]), 1) if "tempo" in crus[nome] else None))
        relat[nome] = est
    jo["materials"] = mats_out
    jo["accessors"], jo["bufferViews"] = E.accs, E.views
    binario_out = E.binario()
    jo["buffers"] = [{"byteLength": len(binario_out)}]
    if not jo["images"]:
        for k in ("images", "textures", "samplers"):
            jo.pop(k)
    jo["asset"] = dict(j["asset"])
    jo["asset"]["generator"] = "harness/parts/integrate.py + harness/parts/blender_pass.py"
    ex = dict(j["asset"].get("extras", {}))
    ex["blender_pass"] = {
        "fonte_sha256_12": src_sha[:12], "versao": VERSAO, "bpy": "5.3.0",
        "ao": {"amostras": AO_AMOSTRAS, "distancia_mm": AO_DIST_MM, "oclusores": "conjunto rígido da peça (mesma cadeia de explode_cad)"},
        "chanfro_normal_mm": BEVEL_MM, "pecas": sorted(relat),
        "marcas": {
            "texto": {"texto": "RTX PRO 6000", "peca": "frame.center_covers.2", "procedencia": "derived (CSV face_b_text_*, pny/back)",
                      "desvio_perpendicular_mm": _GLB.get("desvio_texto_mm"), "altura_maiusculas_mm": _GLB.get("altura_texto_mm"),
                      "nota": "comprimento e ângulo do CSV; altura das maiúsculas pela proporção das letras largas de pny/back e pny/3qtr-back-right (a linha face_b_text_height, 4,5 ± 3, é a da caixa); a caixa do CSV encosta na borda da tampa modelada e o texto desce o mínimo para caber com 0,6 mm de folga (tolerância do CSV: 3 mm)"},
            "logotipo": {"peca": "frame.shroud", "centro_cad_mm": [LOGO["centro_x"], 137.16, LOGO["centro_z"]],
                          "comprimento_mm": LOGO["comprimento"], "altura_simbolo_mm": LOGO["altura_simbolo"],
                          "procedencia": "illustrative (forma simplificada; posição e tamanho medidos em pny/3qtr-top-right, pny/3qtr-back-right e storagereview/sr-3)"},
        },
    }
    jo["asset"]["extras"] = ex
    out_bytes = grava_glb(Path(a.saida), jo, binario_out)
    tex_bytes = sum(v["byteLength"] for v in (jo["bufferViews"][im["bufferView"]] for im in jo.get("images", [])))

    # --- conferência --------------------------------------------------------------------------
    j2, b2, _ = le_glb(Path(a.saida))
    assert [n["name"] for n in j2["nodes"]] == [n["name"] for n in j["nodes"]], "nomes dos nós mudaram"
    for n1, n2 in zip(j["nodes"], j2["nodes"]):
        for k in ("children", "extras", "mesh", "translation", "rotation", "scale", "matrix"):
            assert n1.get(k) == n2.get(k), "nó %s: %s mudou" % (n1["name"], k)
    for mi, mesh in enumerate(j["meshes"]):
        nome = no_por_malha.get(mi)
        P1 = acessor(j, binario, mesh["primitives"][0]["attributes"]["POSITION"])
        prs = j2["meshes"][mi]["primitives"]
        P2 = acessor(j2, b2, prs[0]["attributes"]["POSITION"])
        if nome in crus:
            ntri = sum(j2["accessors"][p["indices"]]["count"] for p in prs) // 3
            assert ntri == len(malhas[nome][1]), "%s: número de triângulos mudou" % nome
            usados = np.unique(malhas[nome][1])
            assert np.array_equal(np.unique(P1[usados], axis=0), np.unique(P2, axis=0)), "%s: posições mudaram" % nome
        else:
            assert np.array_equal(P1, P2), "%s: malha mudou" % nome
    # --- meshopt (sem perda) na geometria: harness/viewer/scripts/meshopt-glb.mjs ----------------
    bytes_sem = len(out_bytes)
    meshopt = False
    script = HARNESS / "viewer" / "scripts" / "meshopt-glb.mjs"
    if not a.sem_meshopt:
        import shutil
        import subprocess
        tmp = Path(a.saida).with_suffix(".sem-meshopt.glb")
        Path(a.saida).replace(tmp)
        r = subprocess.run(["node", str(script), str(tmp), str(a.saida)], cwd=str(script.parent.parent),
                           capture_output=True, text=True) if shutil.which("node") else None
        if r is not None and r.returncode == 0:
            log("  " + r.stdout.strip())
            tmp.unlink()
            out_bytes = Path(a.saida).read_bytes()
            meshopt = True
        else:
            tmp.replace(Path(a.saida))
            log("aviso: sem meshopt (%s); GLB sem compressão" % ((r.stderr.strip()[-300:] if r else "node não encontrado")))
    rel = {
        "entrada": "harness/build/card.glb", "entrada_sha256_12": src_sha[:12],
        "meshopt": meshopt, "bytes_sem_meshopt": bytes_sem,
        "saida": "harness/build/card_final.glb", "saida_sha256_12": hashlib.sha256(out_bytes).hexdigest()[:12],
        "bytes": len(out_bytes), "texturas_bytes": tex_bytes, "texturas_mb": round(tex_bytes / 2 ** 20, 2),
        "orcamento_mb": ORCAMENTO_MB, "tempo_total_s": round(time.time() - t_ini, 1), "tempo_assar_s": round(t_assa, 1),
        "escala": a.escala, "pecas": relat,
    }
    if a.saida == str(OUT) and a.pecas is None:
        REPORT.write_text(json.dumps(rel, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    log("card_final.glb: %.1f MB (texturas %.2f MB de %.0f), sha256 %s, %.0f s" % (
        len(out_bytes) / 2 ** 20, tex_bytes / 2 ** 20, ORCAMENTO_MB, rel["saida_sha256_12"], rel["tempo_total_s"]))
    if tex_bytes / 2 ** 20 > ORCAMENTO_MB:
        log("ERRO: texturas acima do orçamento")
        sys.exit(1)


if __name__ == "__main__":
    principal()
