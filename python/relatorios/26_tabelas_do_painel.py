# -*- coding: utf-8 -*-
"""Anexa ao ``dados.json`` as tabelas de EAD e LGD, e embrulha tudo em ``.js``.

Duas coisas que o painel precisa e que a varredura não produz:

1. **As tabelas do professor.** O detalhe de um contrato mostra a cadeia
   ``PD → EAD → LGD → perda esperada``. As duas tabelas são pequenas (4×5 e
   4×5) e a regra de faixa é uma busca binária — vale replicar no navegador,
   em vez de pré-computar a perda de 5.000 contratos em 28 combinações.

2. **O embrulho.** O CSP do artifact bloqueia ``fetch``, então os dados não
   podem ser buscados: entram como ``<script src="dados.js">``, que define
   ``window.DADOS``. É a mesma origem, e é um script — o que passa.

Roda depois do ``25_dados_do_painel.py``::

    .\\scripts\\py.cmd python\\relatorios\\26_tabelas_do_painel.py
"""

from __future__ import annotations

import json
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from banking.perda import AJUSTE_AVALISTA, _BORDAS_IDADE, _BORDAS_LTV, tabelas
from banking.projeto import DIR_OUTPUTS, PROJ_ROOT
from banking.roi import TAXA_MERCADO
from banking.score import CORTES_PD


def main() -> None:
    destino = DIR_OUTPUTS / "painel" / "dados.json"
    if not destino.exists():
        raise SystemExit(f"rode antes o 25_dados_do_painel.py — falta {destino}")

    dados = json.loads(destino.read_text(encoding="utf-8"))
    tab = tabelas()

    dados["parametros"] = {
        "cortes_pd": list(CORTES_PD),
        "bordas_ltv": list(_BORDAS_LTV),
        "bordas_idade": list(_BORDAS_IDADE),
        "ajuste_avalista": AJUSTE_AVALISTA,
        # prazo -> fator por faixa de LTV
        "fator_ead": {str(p): [float(v) for v in linha]
                      for p, linha in zip(tab.fator_ead.index, tab.fator_ead.to_numpy())},
        "prazos_ead": [int(p) for p in tab.fator_ead.index],
        # faixa de idade -> LGD por faixa de LTV
        "lgd": [[float(v) for v in linha] for linha in tab.lgd.to_numpy()],
        # a taxa de referência do mercado, que ancora a curva de aceite
        "taxa_referencia": TAXA_MERCADO,
    }

    destino.write_text(json.dumps(dados, separators=(",", ":"), ensure_ascii=False),
                       encoding="utf-8")

    js = DIR_OUTPUTS / "painel" / "dados.js"
    js.write_text("window.DADOS=" + json.dumps(dados, separators=(",", ":"),
                                               ensure_ascii=False) + ";",
                  encoding="utf-8")

    # O painel vive em painel/, versionado: HTML e dados lado a lado, para que
    # um clone abra o arquivo e funcione, sem rodar nada. É a exceção à regra de
    # não versionar dado, registrada no .gitignore e no AGENTS.md.
    shutil.copyfile(js, PROJ_ROOT / "painel" / "dados.js")
    shutil.copyfile(PROJ_ROOT / "painel" / "index.html",
                    DIR_OUTPUTS / "painel" / "index.html")

    print(f"  fator_ead: {len(dados['parametros']['fator_ead'])} prazos "
          f"× {len(next(iter(dados['parametros']['fator_ead'].values())))} faixas de LTV")
    print(f"  lgd: {len(dados['parametros']['lgd'])} faixas de idade "
          f"× {len(dados['parametros']['lgd'][0])} faixas de LTV")
    print(f"  amplitude da LGD: {min(min(l) for l in dados['parametros']['lgd']):.3f} "
          f"a {max(max(l) for l in dados['parametros']['lgd']):.3f}")
    print(f"\n  {js.stat().st_size / 1e6:.2f} MB de dados, gravados em dois lugares:")
    print(f"    {PROJ_ROOT / 'painel' / 'dados.js'}  (versionado)")
    print(f"    {js}  (montagem)")
    print(f"\n  abra: {PROJ_ROOT / 'painel' / 'index.html'}")


if __name__ == "__main__":
    main()
