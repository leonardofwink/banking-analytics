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


# Módulos de `banking/` autorizados a tocar o disco. Toda entrada aqui precisa
# estar declarada no AGENTS.md — é o que o teste seguinte cobra. A lista existe
# para que a exceção seja uma decisão consciente e documentada, não um descuido
# que virou hábito.
EXCECOES_IO = {
    "projeto.py",  # a âncora: resolve caminhos e cria os diretórios de dados
    "dados.py",  # a porta de entrada única das bases (passo S01)
}

_SINAIS_DE_ESCRITA = ("mkdir(", "write_table(", "to_parquet(", "to_csv(", "open(")


def test_biblioteca_nao_tem_efeito_colateral_de_escrita() -> None:
    """`banking` é biblioteca: só os módulos autorizados escrevem em disco.

    Pipeline que se disfarça de biblioteca é difícil de testar e impossível de
    reaproveitar: quem importa a função herda o efeito colateral sem pedir.
    """
    modulos = list((PROJ_ROOT / "python" / "banking").glob("*.py"))
    assert modulos, "pacote banking vazio"
    for modulo in modulos:
        if modulo.name in EXCECOES_IO or modulo.name == "__init__.py":
            continue
        fonte = modulo.read_text(encoding="utf-8")
        escreve = [s for s in _SINAIS_DE_ESCRITA if s in fonte]
        assert not escreve, (
            f"{modulo.name} escreve no disco ({escreve}) — isso é papel de pipeline. "
            f"Se for exceção deliberada, declare no AGENTS.md e em EXCECOES_IO."
        )


def test_excecoes_de_io_estao_declaradas_no_agents() -> None:
    """Cada módulo autorizado a escrever precisa estar justificado no AGENTS.md.

    Sem isso, `EXCECOES_IO` viraria um escape fácil: bastaria acrescentar um
    nome à lista para calar o teste anterior. Exigir a declaração no documento
    de convenções obriga a escrever *por que* a exceção existe.
    """
    agents = (PROJ_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for modulo in EXCECOES_IO:
        assert modulo in agents, (
            f"{modulo} está em EXCECOES_IO mas não aparece no AGENTS.md. "
            "Exceção não documentada é exceção esquecida."
        )
