#!/usr/bin/env python3
"""Gera o PDF da proposta a partir de vault/01-Briefing/Proposta formal.md e grupo.json.

Uso: python3 build.py
Requer: pandoc, node com o pacote playwright (Chromium).
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOTA = AQUI.parents[1] / "vault" / "01-Briefing" / "Proposta formal.md"

CSS = """
:root { --navy:#0B1F3A; --teal:#0E7C86; --amber:#F2A900; --ink:#1B2433; --mute:#4A5B73; --line:#D5DCE6; --zebra:#F4F7FA; }
@page { size: A4; }
* { box-sizing: border-box; }
html { font-family: Inter, 'Helvetica Neue', Arial, sans-serif; font-size: 9.6pt; line-height: 1.5; color: var(--ink); }
body { margin: 0; }
header.topo { display:flex; align-items:center; gap:7mm; padding-bottom:5mm; border-bottom:2px solid var(--navy); margin-bottom:4mm; }
header.topo .logo { width:62mm; flex:none; }
header.topo .logo svg { width:100%; height:auto; display:block; }
header.topo .kicker { margin:0; font-size:8pt; letter-spacing:.12em; text-transform:uppercase; color:var(--teal); font-weight:600; }
header.topo h1 { margin:1mm 0 1.5mm; font-size:16.5pt; line-height:1.2; color:var(--navy); font-weight:800; letter-spacing:-.01em; }
header.topo .meta { margin:0; color:var(--mute); font-size:8.8pt; }
.rascunho { background:#FFF4E5; border:1.5px solid var(--amber); color:#7A4B00; padding:2mm 3mm; border-radius:2mm; font-weight:600; margin:0 0 4mm; font-size:8.8pt; }
table.grupo { margin:0 0 3mm; }
table.grupo th { width:30mm; background:var(--zebra); }
table.grupo ol { margin:0; padding-left:5mm; }
h2 { font-size:11.6pt; color:var(--navy); margin:5.5mm 0 1.8mm; padding-bottom:.8mm; border-bottom:1px solid var(--line); break-after:avoid; font-weight:700; }
h2 .n { color:var(--teal); }
p { margin:0 0 2mm; }
ul, ol { margin:0 0 2.2mm; padding-left:5.5mm; }
li { margin:0 0 .8mm; }
strong { color:var(--navy); }
a { color:var(--teal); text-decoration:none; overflow-wrap:anywhere; word-break:break-all; }
code { font-family:'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size:.88em; background:var(--zebra); padding:0 .8mm; border-radius:1mm; }
table { border-collapse:collapse; width:100%; margin:1mm 0 3mm; font-size:8.7pt; line-height:1.4; break-inside:auto; }
th, td { border:1px solid var(--line); padding:1.3mm 2mm; text-align:left; vertical-align:top; }
thead th { background:var(--navy); color:#fff; font-weight:600; border-color:var(--navy); }
tbody tr:nth-child(even) td { background:var(--zebra); }
tr { break-inside:avoid; }
p:has(+ table), p:has(+ ul), p:has(+ ol) { break-after:avoid; }
"""


def ler_grupo():
    return json.loads((AQUI / "grupo.json").read_text(encoding="utf-8"))


def preparar_markdown(texto, nomes):
    # frontmatter
    texto = re.sub(r"\A---\n.*?\n---\n", "", texto, flags=re.S)
    # título H1 (vai para o cabeçalho)
    texto = re.sub(r"^# .*\n", "", texto, count=1, flags=re.M)
    # callouts do Obsidian (linhas que começam com ">")
    texto = re.sub(r"(?m)^>.*\n?", "", texto)
    # linha de wikilinks
    texto = re.sub(r"(?m)^Ver também:.*\n?", "", texto)
    for i, nome in enumerate(nomes, start=1):
        texto = texto.replace("{{I%d}}" % i, nome or "Integrante %d" % i)
    sobra = re.findall(r"\{\{[^}]*\}\}", texto)
    if sobra:
        sys.exit("Marcadores sem substituição: %s" % sobra)
    return texto.strip() + "\n"


def md_para_html(md):
    r = subprocess.run(
        ["pandoc", "-f", "markdown+lists_without_preceding_blankline+autolink_bare_uris",
         "-t", "html", "--wrap=none"],
        input=md, capture_output=True, text=True, check=True,
    )
    corpo = r.stdout
    # numera os títulos de seção já numerados no texto ("1. Tema ...") em destaque
    corpo = re.sub(r"<h2([^>]*)>(\d+)\.\s", r'<h2\1><span class="n">\2.</span> ', corpo)
    return corpo


def main():
    g = ler_grupo()
    nomes = [n.strip() for n in g["integrantes"]]
    faltam = [i + 1 for i, n in enumerate(nomes) if not n]
    md = preparar_markdown(NOTA.read_text(encoding="utf-8"), nomes)
    corpo = md_para_html(md)

    logo = (AQUI / "logo.svg").read_text(encoding="utf-8")
    logo = re.sub(r"<\?xml.*?\?>", "", logo)

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
<table class="grupo"><tbody>
<tr><th>Nome do grupo</th><td><strong>{html.escape(g['nome_grupo'])}</strong></td></tr>
<tr><th>Integrantes</th><td><ol>{lista}</ol></td></tr>
<tr><th>Identidade visual</th><td>{g['identidade']}</td></tr>
</tbody></table>
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
