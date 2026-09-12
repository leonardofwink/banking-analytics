"""Âncora do projeto Banking Analytics — equivalente Python do ``scripts/_setup.R``.

Importar no topo de todo script Python do projeto::

    from banking.projeto import DIR_BRUTOS, DIR_PROCESSADOS, SEMENTE, log_step

Define a raiz do projeto, os diretórios padrão, a semente de reprodutibilidade e
o helper de log. Convenções: ver ``AGENTS.md``.

⚠️ Nunca use ``os.chdir()`` nem caminho absoluto solto — sempre as constantes
``DIR_*`` daqui. Elas resolvem a partir da raiz do repositório, de modo que o
script roda igual seja chamado da raiz, de dentro de ``python/`` ou de um notebook.
"""

from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from typing import Literal

__all__ = [
    "PROJ_ROOT",
    "DIR_DADOS",
    "DIR_BRUTOS",
    "DIR_INTERMED",
    "DIR_PROCESSADOS",
    "DIR_OUTPUTS",
    "DIR_FIGURAS",
    "DIR_TABELAS",
    "DIR_RELATORIOS",
    "DIR_DOCS",
    "SEMENTE",
    "log_step",
    "semear",
]

# --- Raiz do projeto ---------------------------------------------------------
# Sobe a partir deste arquivo até achar a pasta que contém o .git. Robusto a
# qualquer profundidade e ao diretório de onde o script foi chamado — é o
# equivalente ao que o pacote `here` faz no lado R.


def _achar_raiz(inicio: Path) -> Path:
    for candidato in (inicio, *inicio.parents):
        if (candidato / ".git").exists():
            return candidato
    # Fallback: dois níveis acima deste arquivo (python/banking/projeto.py)
    return inicio.parents[1]


PROJ_ROOT: Path = _achar_raiz(Path(__file__).resolve().parent)

# --- Diretórios padrão -------------------------------------------------------
# Camadas de dado — NENHUMA é versionada (ver .gitignore).
DIR_DADOS = PROJ_ROOT / "dados"
DIR_BRUTOS = DIR_DADOS / "brutos"  # como chegou, intocado — somente leitura
DIR_INTERMED = DIR_DADOS / "intermediarios"  # limpo/padronizado
DIR_PROCESSADOS = DIR_DADOS / "processados"  # base analítica (ABT)

DIR_OUTPUTS = PROJ_ROOT / "outputs"  # saídas geradas — NÃO versionar
DIR_FIGURAS = DIR_OUTPUTS / "figuras"
DIR_TABELAS = DIR_OUTPUTS / "tabelas"
DIR_RELATORIOS = DIR_OUTPUTS / "relatorios"

DIR_DOCS = PROJ_ROOT / "docs"

# Cria os diretórios de dados/saída se ainda não existirem (idempotente).
# Eles não são versionados, então num clone novo não existem — é aqui (e no
# lado R, no _setup.R) que a árvore de pastas do projeto é reconstruída.
for _d in (
    DIR_BRUTOS,
    DIR_INTERMED,
    DIR_PROCESSADOS,
    DIR_FIGURAS,
    DIR_TABELAS,
    DIR_RELATORIOS,
):
    _d.mkdir(parents=True, exist_ok=True)

# --- Reprodutibilidade -------------------------------------------------------
# Mesmo valor do lado R (scripts/_setup.R). Modelagem de crédito envolve
# amostragem (treino/teste, bootstrap, validação cruzada): semente fixa é o que
# garante que rodar de novo dá o mesmo número.
SEMENTE = 42


def semear(valor: int = SEMENTE) -> None:
    """Fixa a semente de todos os geradores aleatórios em uso.

    Chame no início de qualquer script que amostre, particione ou treine modelo.
    ``numpy`` só é semeado se estiver instalado, para a âncora não exigir a
    dependência de quem não precisa dela.

    :param valor: Semente a aplicar. Padrão: a constante ``SEMENTE`` do projeto.
    """
    random.seed(valor)
    try:
        import numpy as np

        np.random.seed(valor)
    except ImportError:  # pragma: no cover - ambiente sem numpy
        pass


semear()

# --- Helper de log -----------------------------------------------------------
# Mesma semântica de cor do lado R, para a saída dos dois parecer a mesma coisa:
# ciano = progresso · verde = sucesso · amarelo = aviso · vermelho = erro.
_CORES = {
    "info": "\033[36m",
    "ok": "\033[32m",
    "aviso": "\033[33m",
    "erro": "\033[31m",
}
_RESET = "\033[0m"

Nivel = Literal["info", "ok", "aviso", "erro"]


def log_step(msg: str, nivel: Nivel = "info") -> None:
    """Loga uma etapa com timestamp e semântica de cor.

    :param msg: Mensagem a exibir.
    :param nivel: ``"info"`` (ciano, progresso), ``"ok"`` (verde, sucesso),
        ``"aviso"`` (amarelo) ou ``"erro"`` (vermelho).
    """
    cor = _CORES.get(nivel, _CORES["info"])
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{cor}[{ts}] {msg}{_RESET}")
