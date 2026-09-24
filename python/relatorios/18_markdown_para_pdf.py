"""Converte um documento Markdown do repositório em PDF.

Não há pandoc nesta máquina, e o Word estraga tabela de Markdown. O caminho
que funciona: Markdown → HTML com folha de estilo própria → PDF pelo Edge em
modo headless, que é o mesmo motor de impressão do navegador.

Rodar::

    .\\scripts\\py.cmd python\\relatorios\\18_markdown_para_pdf.py docs\\COMPARACAO_COLEGAS.md
"""

from __future__ import annotations

import html as _html
import re
import subprocess
import sys
from pathlib import Path

from banking.projeto import DIR_OUTPUTS, PROJ_ROOT, log_step

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

# A mesma paleta dos decks, para o material do grupo parecer um conjunto.
ESTILO = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: Calibri, "Segoe UI", sans-serif;
  font-size: 10.5pt; line-height: 1.55; color: #16293A;
  margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
h1 {
  font-family: Cambria, Georgia, serif; font-size: 23pt; color: #16293A;
  margin: 0 0 4pt; padding-bottom: 8pt; border-bottom: 2.5pt solid #16293A;
}
h2 {
  font-family: Cambria, Georgia, serif; font-size: 15pt; color: #16293A;
  margin: 20pt 0 7pt; page-break-after: avoid;
}
h3 {
  font-family: Cambria, Georgia, serif; font-size: 12pt; color: #3D7A8C;
  margin: 14pt 0 5pt; page-break-after: avoid;
}
p { margin: 0 0 7pt; text-align: justify; }
blockquote {
  margin: 10pt 0; padding: 9pt 13pt; background: #F2F4F6;
  border-left: 3pt solid #3D7A8C; font-size: 9.5pt; color: #405060;
}
blockquote p { margin: 0 0 4pt; text-align: left; }
blockquote p:last-child { margin-bottom: 0; }
table {
  border-collapse: collapse; width: 100%; table-layout: fixed; margin: 9pt 0 12pt;
  font-size: 9pt; page-break-inside: avoid;
}
th {
  background: #16293A; color: #fff; text-align: left;
  padding: 5pt 7pt; font-weight: bold; font-size: 8.5pt;
}
td { padding: 4.5pt 7pt; border-bottom: 0.5pt solid #DDE3E8; vertical-align: top;
     word-break: break-word; overflow-wrap: anywhere; }
tr:nth-child(even) td { background: #F7F9FA; }
code {
  font-family: Consolas, "Courier New", monospace; font-size: 8.5pt;
  background: #F2F4F6; padding: 1pt 3pt; border-radius: 2pt; color: #16293A;
}
pre {
  font-family: Consolas, "Courier New", monospace; font-size: 9pt;
  background: #16293A; color: #F2F4F6; padding: 9pt 12pt; border-radius: 3pt;
  margin: 9pt 0 12pt; white-space: pre-wrap; word-break: break-word;
}
strong { color: #16293A; }
hr { border: none; border-top: 0.75pt solid #DDE3E8; margin: 16pt 0; }
ul, ol { margin: 0 0 8pt; padding-left: 16pt; }
li { margin-bottom: 3pt; }
a { color: #3D7A8C; text-decoration: none; }
"""


def _inline(texto: str) -> str:
    """Negrito, itálico, código e links — o suficiente para os nossos docs."""
    t = _html.escape(texto, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def _linha_de_tabela(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def para_html(markdown: str, titulo: str) -> str:
    saida: list[str] = []
    linhas = markdown.split("\n")
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        cru = linha.strip()

        if not cru:
            i += 1
            continue

        # tabela: a linha seguinte é o separador |---|---|
        if (cru.startswith("|") and i + 1 < len(linhas)
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", linhas[i + 1])):
            cabecalho = _linha_de_tabela(cru)
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                corpo.append(_linha_de_tabela(linhas[i]))
                i += 1
            saida.append("<table><thead><tr>"
                         + "".join(f"<th>{_inline(c)}</th>" for c in cabecalho)
                         + "</tr></thead><tbody>")
            for linha_corpo in corpo:
                saida.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in linha_corpo) + "</tr>")
            saida.append("</tbody></table>")
            continue

        if cru.startswith(">"):
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip().lstrip(">").strip())
                i += 1
            # Junta os parágrafos ANTES de formatar: ênfase que atravessa a
            # quebra de linha não fecha se cada linha for tratada sozinha.
            paragrafos, atual = [], []
            for linha_bloco in bloco:
                if linha_bloco:
                    atual.append(linha_bloco)
                elif atual:
                    paragrafos.append(" ".join(atual))
                    atual = []
            if atual:
                paragrafos.append(" ".join(atual))
            corpo = "".join(f"<p>{_inline(x)}</p>" for x in paragrafos)
            saida.append(f"<blockquote>{corpo}</blockquote>")
            continue

        if cru.startswith("```"):
            i += 1
            bloco = []
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                bloco.append(linhas[i])
                i += 1
            i += 1  # fecha a cerca
            texto = _html.escape("\n".join(bloco), quote=False)
            saida.append(f"<pre>{texto}</pre>")
            continue

        if cru.startswith("### "):
            saida.append(f"<h3>{_inline(cru[4:])}</h3>")
        elif cru.startswith("## "):
            saida.append(f"<h2>{_inline(cru[3:])}</h2>")
        elif cru.startswith("# "):
            saida.append(f"<h1>{_inline(cru[2:])}</h1>")
        elif cru.startswith("---"):
            saida.append("<hr>")
        elif cru.startswith(("- ", "* ")) or re.match(r"^\d+\.\s", cru):
            ordenada = bool(re.match(r"^\d+\.\s", cru))
            marcador = r"^\d+\.\s" if ordenada else r"^[-*]\s"
            itens, atual = [], None
            while i < len(linhas):
                bruta = linhas[i]
                despida = bruta.strip()
                if re.match(marcador, despida):
                    if atual is not None:
                        itens.append(" ".join(atual))
                    atual = [re.sub(marcador, "", despida)]
                elif despida and bruta.startswith(("  ", "	")) and atual is not None:
                    atual.append(despida)  # continuação do item
                else:
                    break
                i += 1
            if atual is not None:
                itens.append(" ".join(atual))
            tag = "ol" if ordenada else "ul"
            saida.append(f"<{tag}>" + "".join(f"<li>{_inline(x)}</li>" for x in itens)
                         + f"</{tag}>")
            continue
        else:
            # parágrafo: junta as linhas até a próxima em branco
            bloco = []
            while i < len(linhas) and linhas[i].strip() and not linhas[i].strip().startswith(
                    ("#", ">", "|", "---", "- ", "* ", "```")):
                bloco.append(linhas[i].strip())
                i += 1
            saida.append(f"<p>{_inline(' '.join(bloco))}</p>")
            continue
        i += 1

    return (f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
            f"<title>{_html.escape(titulo)}</title><style>{ESTILO}</style></head>"
            f"<body>{''.join(saida)}</body></html>")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        log_step("uso: 18_markdown_para_pdf.py <caminho.md> [saida.pdf]", "erro")
        return 1

    origem = Path(argv[1])
    if not origem.is_absolute():
        origem = PROJ_ROOT / origem
    if not origem.exists():
        log_step(f"não encontrado: {origem}", "erro")
        return 1

    destino = (Path(argv[2]) if len(argv) > 2
               else DIR_OUTPUTS / "documentos" / f"{origem.stem}.pdf")
    destino.parent.mkdir(parents=True, exist_ok=True)

    if not EDGE.exists():
        log_step(f"Edge não encontrado em {EDGE}", "erro")
        return 1

    markdown = origem.read_text(encoding="utf-8")
    titulo = next((l[2:].strip() for l in markdown.split("\n") if l.startswith("# ")),
                  origem.stem)
    html = para_html(markdown, titulo)

    temporario = destino.with_suffix(".html")
    temporario.write_text(html, encoding="utf-8")

    log_step(f"convertendo {origem.name}")
    subprocess.run(
        [str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={destino}", temporario.as_uri()],
        check=True, capture_output=True, timeout=180,
    )
    temporario.unlink(missing_ok=True)

    if not destino.exists():
        log_step("o Edge não produziu o arquivo", "erro")
        return 1
    log_step(f"PDF gerado: {destino} ({destino.stat().st_size/1024:.0f} KB)", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
