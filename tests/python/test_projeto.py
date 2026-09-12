"""Testes da âncora do projeto (``banking.projeto``).

Não testam regra de negócio — testam que o ambiente está de pé: o pacote é
importável, a raiz foi encontrada e os caminhos apontam para dentro do
repositório. É o teste que falha primeiro quando o setup do Python quebra,
e a mensagem dele diz o que houve.

Rodar:  .\\scripts\\py.cmd -m pytest
"""

from __future__ import annotations

from pathlib import Path

from banking.projeto import (
    DIR_BRUTOS,
    DIR_PROCESSADOS,
    PROJ_ROOT,
    SEMENTE,
    log_step,
    semear,
)


def test_raiz_do_projeto_e_o_repositorio() -> None:
    """A raiz encontrada tem que ser a pasta que contém o .git."""
    assert (PROJ_ROOT / ".git").exists()
    assert (PROJ_ROOT / "AGENTS.md").is_file()


def test_diretorios_de_dados_existem_e_ficam_dentro_da_raiz() -> None:
    """A âncora cria as pastas de dado — elas não são versionadas."""
    for d in (DIR_BRUTOS, DIR_PROCESSADOS):
        assert d.is_dir(), f"diretório não criado pela âncora: {d}"
        assert PROJ_ROOT in d.parents, f"caminho fora do repositório: {d}"


def test_semente_bate_com_o_lado_r() -> None:
    """SEMENTE é duplicada em scripts/_setup.R — os dois lados têm que bater.

    Constante duplicada entre linguagens é dívida aceita conscientemente (ver
    AGENTS.md § A fronteira entre as duas linguagens); este teste é o que
    impede que ela se perca.
    """
    setup_r = (PROJ_ROOT / "scripts" / "_setup.R").read_text(encoding="utf-8")
    assert f"SEMENTE <- {SEMENTE}" in setup_r, (
        "SEMENTE divergente entre python/banking/projeto.py e scripts/_setup.R"
    )


def test_semear_e_reprodutivel() -> None:
    """Duas chamadas com a mesma semente produzem a mesma sequência."""
    import random

    semear()
    primeira = [random.random() for _ in range(5)]
    semear()
    segunda = [random.random() for _ in range(5)]
    assert primeira == segunda


def test_log_step_nao_explode(capsys) -> None:
    """Os quatro níveis de log imprimem alguma coisa e não levantam erro."""
    for nivel in ("info", "ok", "aviso", "erro"):
        log_step(f"teste de {nivel}", nivel)  # type: ignore[arg-type]
    saida = capsys.readouterr().out
    assert "teste de erro" in saida


def test_gitignore_bloqueia_dado() -> None:
    """Regra crítica nº 1: formato de dado não pode entrar no git."""
    gitignore = (PROJ_ROOT / ".gitignore").read_text(encoding="utf-8")
    for padrao in ("dados/", "*.csv", "*.parquet", "*.xlsx", ".Renviron"):
        assert padrao in gitignore, f"padrão ausente no .gitignore: {padrao}"


def test_biblioteca_nao_tem_efeito_colateral_de_escrita() -> None:
    """`banking` é biblioteca: só a âncora pode criar diretório."""
    modulos = [p for p in (PROJ_ROOT / "python" / "banking").glob("*.py")]
    assert modulos, "pacote banking vazio"
    for modulo in modulos:
        if modulo.name in ("projeto.py", "__init__.py"):
            continue  # a âncora cria os diretórios por definição
        fonte = modulo.read_text(encoding="utf-8")
        assert "mkdir(" not in fonte, (
            f"{modulo.name} escreve no disco — isso é papel de pipeline, não de biblioteca"
        )
