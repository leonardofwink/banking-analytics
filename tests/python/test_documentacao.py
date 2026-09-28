"""S13.9 · Testes da documentação — os ponteiros que envelhecem em silêncio.

Documentação quebrada não levanta exceção. Um link que aponta para o nada e um
hash de commit que não existe mais continuam parecendo corretos na leitura, e só
falham quando alguém clica — normalmente o avaliador.

Dois defeitos concretos motivaram este arquivo:

* **37 links relativos quebrados**, todos do mesmo tipo — caminho errado entre
  ``docs/``, ``docs/processo/`` e ``docs/specs/``. O ``ROADMAP.md`` sozinho
  tinha 18, e o ``README.md`` manda a banca para vários deles.
* **Hashes inválidos na coluna ``Commit`` das specs**, duas vezes: primeiro na
  reescrita de histórico que removeu atribuição de IA (``c669c20``), depois num
  rebase de pilha de PRs. O ``AGENTS.md`` diz que essa coluna *"liga a spec ao
  código e permite auditar depois"* — apontando para o nada, ela não liga nada.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

import pytest

from banking.projeto import PROJ_ROOT

# Captura o destino de um link markdown, separando a âncora (``#secao``), que
# não é caminho de arquivo. Links absolutos e de e-mail ficam de fora.
LINK = re.compile(r"\]\(([^)#][^)]*?)(?:#[^)]*)?\)")

#: A coluna `Commit` das specs, em backticks: 7 a 40 hexadecimais.
HASH_EM_SPEC = re.compile(r"\|\s*`([0-9a-f]{7,40})`\s*\|")


def _markdowns() -> list[Path]:
    """Todo markdown que descreve o projeto — não o que é gerado dentro de outputs."""
    arquivos = sorted(PROJ_ROOT.glob("docs/**/*.md"))
    for solto in ("AGENTS.md", "CLAUDE.md", "README.md"):
        caminho = PROJ_ROOT / solto
        if caminho.exists():
            arquivos.append(caminho)
    return arquivos


def test_ha_markdown_para_conferir():
    """Guarda contra o teste passar por não ter encontrado nada."""
    assert len(_markdowns()) >= 15


def test_links_relativos_resolvem():
    """Todo link relativo aponta para um arquivo que existe.

    O ``unquote`` é essencial e já produziu falso positivo: link markdown com
    espaço **precisa** de ``%20``, então ``painel/A%20B.html`` está certo e
    ``painel/A B.html`` é que estaria errado. Um verificador que não decodifica
    "conserta" o link certo e quebra o que funcionava.
    """
    quebrados = []
    for arquivo in _markdowns():
        base = arquivo.parent
        for destino in LINK.findall(arquivo.read_text(encoding="utf-8")):
            if destino.startswith(("http://", "https://", "mailto:")):
                continue
            if not (base / unquote(destino)).exists():
                quebrados.append(f"{arquivo.relative_to(PROJ_ROOT)} -> {destino}")

    assert not quebrados, "links relativos quebrados:\n  " + "\n  ".join(quebrados)


def test_sem_caracteres_de_controle():
    """Nenhum arquivo de texto carrega byte de controle além de quebra e tabulação.

    O ``README.md`` tinha um **0x05** no meio de um caminho: ``python\\modelagem``
    seguido do byte 5 e de ``_desafiantes.py``. Foi um ``\\05`` interpretado como
    escape octal em algum ponto da escrita.

    É invisível na leitura — o texto parece um caminho normal —, o comando
    documentado não roda, e nenhuma revisão humana pega. Só um teste pega.
    """
    import unicodedata

    alvos = list(_markdowns())
    for padrao in ("python/**/*.py", "tests/**/*.py", "apresentacoes/*.js", "scripts/*"):
        alvos += [p for p in PROJ_ROOT.glob(padrao) if p.is_file()]

    sujos = []
    for arquivo in alvos:
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binário não é texto; não é o que este teste guarda
        for i, c in enumerate(texto):
            if unicodedata.category(c) == "Cc" and c not in "\n\t\r":
                linha = texto.count("\n", 0, i) + 1
                sujos.append(
                    f"{arquivo.relative_to(PROJ_ROOT)}:{linha} byte 0x{ord(c):02x}"
                )

    assert not sujos, "caracteres de controle encontrados:\n  " + "\n  ".join(sujos)


def test_specs_citam_commits_que_existem():
    """Os hashes na coluna `Commit` das specs resolvem no histórico.

    Rebase e reescrita de histórico trocam todo hash. Se a spec não for
    atualizada junto, a rastreabilidade que ela promete deixa de existir — e
    ninguém percebe, porque um hash inválido continua parecendo um hash.
    """
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], cwd=PROJ_ROOT,
                       capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("fora de um repositório git")

    invalidos = []
    for spec in sorted(PROJ_ROOT.glob("docs/specs/*.md")):
        for hash_curto in HASH_EM_SPEC.findall(spec.read_text(encoding="utf-8")):
            r = subprocess.run(
                ["git", "cat-file", "-t", hash_curto],
                cwd=PROJ_ROOT, capture_output=True, text=True,
            )
            if r.returncode != 0 or r.stdout.strip() != "commit":
                invalidos.append(f"{spec.relative_to(PROJ_ROOT)} -> {hash_curto}")

    assert not invalidos, (
        "specs citam commits que não existem:\n  " + "\n  ".join(invalidos)
    )
