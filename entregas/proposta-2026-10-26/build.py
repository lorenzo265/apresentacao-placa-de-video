#!/usr/bin/env python3
"""Gera o PDF da proposta a partir de vault/01-Briefing/Proposta formal.md e grupo.json.

Estilo pedido pelo grupo: fundo branco, Arial 12, só tópicos, negrito e linhas divisórias,
sem tabelas e sem cores no texto. As únicas exceções são o gráfico do cronograma (cores
simples) e o logo.

Uso: python3 build.py
Requer: pandoc, node com o pacote playwright (Chromium).
"""
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOTA = AQUI.parents[1] / "vault" / "01-Briefing" / "Proposta formal.md"

CSS = """
@page { size: A4; }
* { box-sizing: border-box; }
html { font-family: Arial, 'Liberation Sans', Helvetica, sans-serif; font-size: 12pt; line-height: 1.4; color: #000; background: #fff; }
body { margin: 0; background: #fff; }
header.topo { display:flex; align-items:center; gap:7mm; padding-bottom:4mm; border-bottom:2px solid #000; margin-bottom:4mm; }
header.topo .logo { width:58mm; flex:none; }
header.topo .logo svg { width:100%; height:auto; display:block; }
header.topo .kicker { margin:0; font-size:10pt; text-transform:uppercase; font-weight:bold; }
header.topo h1 { margin:1mm 0 1.5mm; font-size:16pt; line-height:1.2; font-weight:bold; }
header.topo .meta { margin:0; font-size:11pt; }
.rascunho { border:2px solid #000; padding:2mm 3mm; font-weight:bold; margin:0 0 4mm; }
h2 { font-size:13pt; font-weight:bold; margin:6mm 0 2mm; padding-top:3mm; border-top:1px solid #000; break-after:avoid; }
p { margin:0 0 2.5mm; }
ul, ol { margin:0 0 3mm; padding-left:6mm; }
li { margin:0 0 1.6mm; break-inside:avoid; }
strong { font-weight:bold; }
a { color:#000; text-decoration:underline; overflow-wrap:anywhere; word-break:break-all; }
code { font-family:'Liberation Mono', 'DejaVu Sans Mono', monospace; font-size:.9em; }
p:has(+ ul), p:has(+ ol) { break-after:avoid; }
figure.grafico { margin:3mm 0 3mm; break-inside:avoid; }
figure.grafico figcaption { font-weight:bold; margin-bottom:1.5mm; }
figure.grafico svg { width:100%; height:auto; display:block; }
"""

# Gráfico do cronograma: (rótulo, início, fim). Mantenha igual aos tópicos da seção 7 da nota.
ANO = 2026
ETAPAS = [
    ("Proposta e leitura inicial", (10, 19), (10, 26)),
    ("Fontes restantes", (10, 27), (11, 1)),
    ("Redação e 1ª versão do tour", (11, 2), (11, 8)),
    ("Revisão e fechamento do texto", (11, 9), (11, 9)),
    ("Tour, slides e falas", (11, 10), (11, 14)),
    ("Ensaio geral", (11, 15), (11, 15)),
    ("Seminário", (11, 16), (11, 16)),
]
ENTREGAS = [("Proposta (0,5)", (10, 26)), ("Texto (1,5)", (11, 9)), ("Seminário (2,0)", (11, 16))]
SEMANAS = [(10, 19), (10, 26), (11, 2), (11, 9), (11, 16)]


def ler_grupo():
    return json.loads((AQUI / "grupo.json").read_text(encoding="utf-8"))


def preparar_markdown(texto, nomes):
    texto = re.sub(r"\A---\n.*?\n---\n", "", texto, flags=re.S)       # frontmatter
    texto = re.sub(r"^# .*\n", "", texto, count=1, flags=re.M)       # título (vai ao cabeçalho)
    texto = re.sub(r"(?m)^>.*\n?", "", texto)                         # callouts do Obsidian
    texto = re.sub(r"(?m)^Ver também:.*\n?", "", texto)               # wikilinks
    for i, nome in enumerate(nomes, start=1):
        texto = texto.replace("{{I%d}}" % i, nome or "Integrante %d" % i)
    sobra = re.findall(r"\{\{[^}]*\}\}", texto)
    if sobra:
        sys.exit("Marcadores sem substituição: %s" % sobra)
    if re.search(r"(?m)^\|", texto):
        sys.exit("A nota tem tabela. O PDF não usa tabelas: converta em tópicos.")
    return texto.strip() + "\n"


def md_para_html(md):
    r = subprocess.run(
        ["pandoc", "-f", "markdown+lists_without_preceding_blankline+autolink_bare_uris",
         "-t", "html", "--wrap=none"],
        input=md, capture_output=True, text=True, check=True,
    )
    return r.stdout


def grafico_cronograma():
    d0 = date(ANO, *ETAPAS[0][1])
    d1 = date(ANO, *ETAPAS[-1][2])
    ndias = (d1 - d0).days + 1
    esq, larg, topo, alt_linha = 215, 460, 34, 26
    w = esq + larg + 5
    h = topo + alt_linha * len(ETAPAS) + 28
    dw = larg / ndias

    def x(m_d, fim=False):
        return esq + ((date(ANO, *m_d) - d0).days + (1 if fim else 0)) * dw

    f = 'font-family="Arial, Liberation Sans, sans-serif"'
    o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Cronograma de 19/10 a 16/11">']
    for m_d in SEMANAS:  # grade semanal
        gx = x(m_d)
        o.append(f'<line x1="{gx:.1f}" y1="{topo - 6}" x2="{gx:.1f}" y2="{h - 22}" stroke="#bbb" stroke-width="1"/>')
        o.append(f'<text x="{gx:.1f}" y="{h - 8}" font-size="11" {f} text-anchor="middle" fill="#000">'
                 f'{m_d[1]:02d}/{m_d[0]:02d}</text>')
    for i, (rot, ini, fim) in enumerate(ETAPAS):
        y = topo + i * alt_linha
        o.append(f'<text x="{esq - 8}" y="{y + 17}" font-size="12" {f} text-anchor="end" fill="#000">{html.escape(rot)}</text>')
        bx, bw = x(ini), x(fim, fim=True) - x(ini)
        o.append(f'<rect x="{bx:.1f}" y="{y + 4}" width="{bw:.1f}" height="17" fill="#1F5FBF"/>')
    for rot, m_d in ENTREGAS:  # marcos de entrega
        mx = x(m_d, fim=True)
        o.append(f'<line x1="{mx:.1f}" y1="{topo - 6}" x2="{mx:.1f}" y2="{h - 22}" stroke="#F28C00" stroke-width="2.5"/>')
        ancora = "end"  # rótulo à esquerda da linha, para os três não se sobreporem
        o.append(f'<text x="{mx:.1f}" y="{topo - 12}" font-size="12" font-weight="bold" {f} '
                 f'text-anchor="{ancora}" fill="#000">{html.escape(rot)}</text>')
    o.append("</svg>")
    return ('<figure class="grafico"><figcaption>Cronograma (barras azuis: etapas; linhas laranja: '
            'entregas com nota)</figcaption>' + "".join(o) + "</figure>")


def main():
    g = ler_grupo()
    nomes = [n.strip() for n in g["integrantes"]]
    faltam = [i + 1 for i, n in enumerate(nomes) if not n]
    md = preparar_markdown(NOTA.read_text(encoding="utf-8"), nomes)
    corpo = md_para_html(md)
    if "<!-- grafico-cronograma -->" not in corpo:
        sys.exit("Faltou o marcador do gráfico do cronograma na nota.")
    corpo = corpo.replace("<!-- grafico-cronograma -->", grafico_cronograma())

    logo = re.sub(r"<\?xml.*?\?>", "", (AQUI / "logo.svg").read_text(encoding="utf-8"))
    lista = "".join("<li>%s</li>" % html.escape(n or "[preencher nome completo]") for n in nomes)
    aviso = ""
    if faltam:
        aviso = ('<p class="rascunho">RASCUNHO: faltam os nomes dos integrantes %s em grupo.json. '
                 "Não entregar este arquivo.</p>" % ", ".join(map(str, faltam)))

    doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Proposta de trabalho - {html.escape(g['nome_grupo'])}</title>
<style>{CSS}</style></head><body>
<header class="topo">
  <div class="logo">{logo}</div>
  <div>
    <p class="kicker">Proposta de trabalho · Linha {html.escape(g['linha'])}</p>
    <h1>{html.escape(g['titulo'])}</h1>
    <p class="meta">{html.escape(g['disciplina'])} · Entrega: {html.escape(g['entrega'])}</p>
  </div>
</header>
{aviso}
<ul>
<li><strong>Nome do grupo:</strong> {html.escape(g['nome_grupo'])}</li>
<li><strong>Integrantes:</strong><ol>{lista}</ol></li>
<li><strong>Identidade visual:</strong> {g['identidade']}</li>
</ul>
{corpo}
</body></html>
"""
    saida_html = AQUI / "proposta.html"
    saida_html.write_text(doc, encoding="utf-8")

    sufixo = " (RASCUNHO)" if faltam else ""
    pdf = AQUI / ("Proposta - %s%s.pdf" % (g["nome_grupo"], sufixo))
    for antigo in AQUI.glob("Proposta - *.pdf"):
        antigo.unlink()
    rodape = "%s · Proposta de trabalho · %s" % (g["nome_grupo"], g["disciplina"])
    subprocess.run(["node", str(AQUI / "render.js"), str(saida_html), str(pdf), rodape], check=True)
    print("PDF:", pdf)
    if faltam:
        print("ATENÇÃO: faltam nomes (integrantes %s)." % faltam)


if __name__ == "__main__":
    main()
