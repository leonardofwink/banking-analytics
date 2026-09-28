# S13 · Post-mortem e política de recuperação

> Passo não previsto no plano original. Entrou depois da apuração de 26/09/2026, em que o Grupo 3 ficou em **terceiro nas duas etapas**.
>
> 🔄 **EM ANDAMENTO.** Diagnóstico em [`processo/POST_MORTEM.md`](../processo/POST_MORTEM.md).
>
> ⚠️ **A submissão é imutável.** Nada em `outputs/submissao/`, `POLITICA_ESCOLHIDA` ou `docs/QA_DEFESA.md` é alterado. A recuperação é **aditiva**, em `python/recuperacao/` e `outputs/recuperacao/`. O estado entregue segue recuperável pela tag `entrega-final`.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| [S13.1](#s131--o-post-mortem) | `processo/POST_MORTEM.md` | 4/4 | ✅ | `0cd2675` |
| [S13.2](#s132--os-registros-antes-do-uso) | PRD · GLOSSARIO · AGENTS | 4/4 | ✅ | `dc97755` |
| [S13.3](#s133--a-premissa-vira-parâmetro) | `Premissas` em `banking/roi.py` | 4/4 | ✅ | `dc357df` |
| [S13.4](#s134--a-âncora-de-mercado) | `recuperacao/27_ancora_de_mercado.py` | 4/4 | ✅ | `15ac0de` |
| [S13.5](#s135--a-calibração-do-aceite) | `recuperacao/28_calibrar_o_aceite.py` | 4/5 | 🔄 | |
| [S13.6](#s136--a-política-sob-o-piso) | `recuperacao/29_politica_sob_piso.py` | 0/4 | ⬜ | |
| [S13.7](#s137--a-submissão-alternativa) | `recuperacao/30_submissao_alternativa.py` | 0/3 | ⬜ | |
| [S13.8](#s138--os-testes-que-impedem-a-volta) | 5 testes em `tests/python/` | 1/5 | 🔄 | |
| [S13.9](#s139--as-correções-de-artefato) | 8 correções | 1/8 | 🔄 | |
| **Passo** | **DoD do S13** | **1/6** | 🔄 | |

## Objetivo

Entender por que perdemos, registrar o diagnóstico antes de mexer em qualquer alavanca, e então produzir uma política alternativa que trate os **15% de ROI como guard-rail**, maximizando ROI acima desse piso.

## Por que este passo existe

O professor foi explícito sobre a causa:

> *"O problema não estava na varredura, estava numa premissa. O grupo assumiu que o aceite desabaria acima de 2% ao mês. O Grupo 2 cobrou 2,506% e manteve 63,9% de aceite. E a própria política do Grupo 3, com apenas 0,7 ponto a mais na taxa, teria entregue 16,27% de ROI com R$ 62,8 milhões originados, dentro dos quatro guard-rails."*

Duas coisas decorrem disso, e as duas justificam um passo inteiro:

**A primeira é que o exercício mudou de natureza.** Até a apuração, a elasticidade do aceite era premissa — `DEBITO_TECNICO.md § 4` afirmava, corretamente para a época, que *"não há como calibrar"*. Agora há: temos o ROI e o volume realizados da nossa própria política, o aceite do Grupo 2 a um preço conhecido, e um contrafactual dado pelo professor. **A premissa virou parâmetro estimável.**

**A segunda é que a premissa estava escondida numa constante de módulo.** `TAXA_MERCADO` e `CENARIOS` são globais em `banking/roi.py`: ninguém precisa declará-las para usá-las, e por isso ninguém as questionou. Enquanto forem constantes, o erro pode voltar.

## ⛔ O que **não** fazemos neste passo

- **Não alteramos a submissão.** `outputs/submissao/`, `POLITICA_ESCOLHIDA` (`politica.py:200-207`) e os três cenários originais (`roi.py:96-100`) ficam como estão. São o registro do que foi defendido, e preservá-los é o que mantém a comparação honesta.
- **Não mexemos em `docs/QA_DEFESA.md`.** A defesa já aconteceu; consertar resposta ensaiada para pergunta que não será feita não tem valor.
- **Não redesenhamos as bordas das faixas** (`CORTES_PD`). Medido: rende 1,6 pontos-base e custa risco de coerência. O que muda é o **teto de PD aceito**, que é outra coisa.
- **Não perseguimos os 15%.** Eles entram como **piso declarado uma vez**, e o objetivo é o máximo ROI acima dele. Nenhum script pode conter `0.15` fora da definição do guard-rail.
- **Não usamos o contrafactual do professor para calibrar.** Ele é gabarito de validação e não se repete — gastá-lo no ajuste destrói a única verificação externa que temos.

---

### S13.1 · O post-mortem

Diagnóstico escrito **antes** de qualquer ajuste, para o conserto não reescrever a história do erro.

**DoD — pronto quando:**

1. ✅ As dez causas estão em ordem, cada uma com arquivo e linha ou número da apuração.
2. ✅ Existe seção de hipóteses **derrubadas com medição**, para o diagnóstico não parecer escolhido a dedo.
3. ✅ As medições contaminadas por `β_taxa = 1,5` estão marcadas como tais, em vez de apagadas.
4. ✅ A prestação de contas da IA está no documento.

**Entrega:** [`docs/processo/POST_MORTEM.md`](../processo/POST_MORTEM.md).

---

### S13.2 · Os registros, antes do uso

Regras críticas 4 e 5 do [`AGENTS.md`](../../AGENTS.md): decisão de modelagem se registra **antes** de ser usada, e termo novo vai para o glossário.

**DoD — pronto quando:**

1. `PRD.md` ganha a seção **Decisões de modelagem** — que **não existia**, embora o `AGENTS.md` aponte para ela — com as duas decisões deste passo: usar **referência externa (BCB)** como âncora de preço, e trocar minimax por **piso de 15% com máximo ROI**.
2. O registro da âncora externa cita a razão anterior para recusá-la **e diz que estava errada**. Decisão revertida sem o motivo registrado volta a ser tomada.
3. `GLOSSARIO.md` ganha **elasticidade do aceite**, **âncora de preço**, **restrição monotônica** e **RAROC**, cada um na seção certa.
4. `AGENTS.md` ganha a regra crítica **"conclusão negativa exige teste de premissa"**.

---

### S13.3 · A premissa vira parâmetro

`TAXA_MERCADO` (`roi.py:49`) e `CENARIOS` (`roi.py:96-100`) deixam de ser constantes implícitas e passam a ser um objeto nomeado.

```python
@dataclass(frozen=True)
class Premissas:
    nome: str
    taxa_mercado: float
    cenarios: dict[str, Cenario]

PREMISSAS_SUBMETIDAS = Premissas("submetidas", 0.0159, CENARIOS)
```

**DoD — pronto quando:**

1. `simular(ofertas, cenario, premissas=PREMISSAS_SUBMETIDAS)` — o **default reproduz o comportamento atual**.
2. **Os 166 testes passam sem alteração.** Se algum precisar mudar, a assinatura está errada.
3. `s09_busca.csv` e `s12_fronteira_roi_volume.csv` são reproduzidos **bit a bit**.
4. Mesmo tratamento para `score_de_pd(pd, cortes=CORTES_PD)` e `faixa_de_score`, pelo mesmo motivo.

> Aproveitar a passagem para corrigir `roi.py:242`: `simular()` chama `carregar_parametros_ead_lgd()` a cada execução (**18,6 ms**) em vez do memoizado `banking.perda.tabelas()`. Confirmado numericamente idêntico nas três tabelas; é só custo.

---

### S13.4 · A âncora de mercado

A correção da causa nº 1 do post-mortem. **Primeiro script, porque a âncora entra no denominador do `excesso`** — calibrar elasticidade sobre a âncora errada só move o erro de lugar.

**DoD — pronto quando:**

1. O output traz **mediana e quartis** das instituições no período da Base C, a partir de série pública do BCB, com **fonte, identificador da série e data de extração no cabeçalho**.
2. A nossa taxa média (**1,911%**) e a do vencedor (**2,506%**) estão posicionadas nessa distribuição, e a afirmação do professor — *2,54% acima da mediana das 45 instituições e abaixo do topo* — é reproduzida ou explicitamente contestada com número.
3. A distância entre `TAXA_MERCADO = 1,59%` e a mediana de mercado está medida em pontos percentuais.
4. `docs/FONTES_EXTERNAS.md` registra a procedência, e `dados/externos/` respeita a regra de `brutos/`: **somente leitura**, fora do git.

> **Dependência externa declarada.** Exige a API do SGS/BCB. Sem rede, o script aceita CSV baixado à mão — e falha com mensagem clara se o cabeçalho de procedência estiver ausente. **Dado externo sem procedência não entra.**

---

### S13.5 · A calibração do aceite

Até a apuração a elasticidade era premissa; agora é estimável. Três observações independentes:

| # | Observação | Fonte |
| - | ---------- | ----- |
| 1 | `POLITICA_ESCOLHIDA` → ROI **11,21%** | apuração |
| 2 | `POLITICA_ESCOLHIDA` → volume **R$ 84,4 MM** | apuração |
| 3 | taxa **2,506%** → aceite **63,9%** | Grupo 2 |

**DoD — pronto quando:**

1. O cenário calibrado reproduz as **três** âncoras ao mesmo tempo: ROI **11,21% ± 0,05**, volume **R$ 84,4 MM ± 1**, aceite **63,9% ± 1** a 2,506%.
2. **Validação fora da amostra:** com os parâmetros ajustados nas três, simular `POLITICA_ESCOLHIDA` com **+0,7 pp** na taxa devolve **16,27% ± 0,3** e **R$ 62,8 MM ± 3**, nos quatro guard-rails. **Se não fechar, a calibração está errada.**
3. O resultado é uma **região** de `(a0, β_taxa, γ)` compatível, não um ponto.
4. O que não for identificável com três observações está **escrito como não identificável**, com os parâmetros fixados e o motivo.
5. Os três cenários originais seguem intocados em `roi.py:96-100`.

#### Resultado, em 28/09/2026 — e por que o item 1 do DoD **não** está cumprido

| | mediana (1,820%) | ponderada por volume (2,021%) |
| - | ---------------- | ----------------------------- |
| `a0` | 0,862 | 0,838 |
| `beta_taxa` | 0,830 | **1,186** |
| `gama` | 0,813 | 1,072 |
| validação: ROI | 16,31% (+0,04 pp) | 16,37% (+0,10 pp) |
| validação: volume | R$ 62,7 MM (−0,09) | R$ 62,1 MM (−0,74) |
| validação: guard-rails | ❌ inadimplência 8,2% | ✅ **todos os quatro** |

**A âncora ponderada por volume vence** por um critério que não entrou no
ajuste: o professor afirma que a política com +0,7 pp fica *"dentro dos quatro
guard-rails"*. Sob a ponderada, o motor concorda. Sob a mediana, ele acusa
inadimplência de 8,2%. É uma terceira informação, qualitativa e independente
de ROI e volume, e ela discrimina.

**O item 1 do DoD não está cumprido, e a tolerância não vai ser afrouxada.**
Os resíduos, sob a ponderada:

| observação | alvo | previsto | erro | dentro? |
| ---------- | ---- | -------- | ---- | ------- |
| nossa · ROI | 11,21% | 11,56% | +0,35 pp | ❌ (±0,05) |
| nossa · volume | R$ 84,4 MM | R$ 84,4 MM | −0,01 MM | ✅ |
| Grupo 2 · aceite | 63,9% | 62,3% | −1,59 pp | ❌ (±1) |

Os resíduos têm **o mesmo sinal nas duas âncoras**, o que aponta para erro
sistemático, não ruído de otimização. A causa mais provável é a aproximação
declarada nº 1: a política do Grupo 2 é reconstruída sobre a **nossa** PD, e o
otimizador sacrifica o ajuste do nosso ROI para acomodar os números deles.

**O que fecharia o item:** reduzir a tensão entre as duas políticas — por
exemplo, calibrando só nas observações da nossa política e usando as do Grupo 2
apenas como validação. Fica registrado como pendente, não como resolvido.

> **Por que a nº 1 sozinha não basta:** acertar o ROI e errar o volume foi exatamente o que escondeu o problema até a apuração. O ROI é uma razão e o aceite move numerador e denominador juntos — ele perdoa erro de elasticidade. O volume não.

---

### S13.6 · A política sob o piso

Maximizar ROI no cenário calibrado, sujeito aos **cinco** limites — sem minimax, sem `EMPATE_ROI`. Refaz a varredura inteira, que até aqui rodou sob `β_taxa = 1,5`.

Três alavancas que a busca antiga não tinha:

- **teto de PD aceito** como variável de primeira classe (o nosso foi 13,00%; o do vencedor, 7,88%), em vez de `corte` sobre bordas fixas;
- **tabela fixa por faixa** e **retorno-alvo** ao lado do cost-plus;
- **prazo pedido pelo cliente** contra prazo fixo.

**DoD — pronto quando:**

1. O relatório informa **quantas** políticas atendem os cinco limites — não se existe alguma.
2. Reporta lado a lado o que **cada critério** escolheria: minimax, `EMPATE_ROI` e piso-com-máximo-ROI, isolando o custo de cada camada.
3. A política escolhida é reportada **também** sob o cenário severo. Se desmorona, é aposta declarada.
4. Controle de regressão: sob `PREMISSAS_SUBMETIDAS`, o script reproduz **11,3294%** para `POLITICA_ESCOLHIDA`.

---

### S13.7 · A submissão alternativa

**DoD — pronto quando:**

1. `outputs/recuperacao/` tem os arquivos no formato do enunciado, 5.000 linhas.
2. `validar_submissao_politica` e `validar_monotonicidade` passam, espelhando `10_submissao_politica.py`.
3. `outputs/submissao/` e `POLITICA_ESCOLHIDA` seguem **inalterados** — verificado por `git status` e por diff do CSV.

---

### S13.8 · Os testes que impedem a volta

Cada defeito encontrado na auditoria nasceu num vão da suíte.

**DoD — pronto quando:**

1. Fixture **não-plana** para `aplicar_politica`. A atual usa mesma taxa, prazo e entrada em toda faixa, então um off-by-one no mapeamento faixa→linha produz saída idêntica e **os 173 passam**. É o único elo da cadeia sem teste capaz de falhar.
2. ✅ As nove elasticidades de `CENARIOS` ficam **fixadas por teste** — é o que deixou `S08_MOTOR_DE_ROI.md` derivar e permanecer errado. Junto, `PREMISSAS_CALIBRADAS` e a direção da âncora (a calibrada tem de ficar **acima** da submetida, senão alguém reverteu a régua para o livro próprio).
3. `perda_por_faixa` é extraído para `banking.perda` e testado uma vez, em vez de replicado em **11 arquivos**.
4. Existe teste afirmando a relação entre `POLITICA_ESCOLHIDA` e o que `09_buscar_politica.py` seleciona.
5. `validar_monotonicidade` ganha teste de **empate**: preço único e truncagem no teto produzem `diff == 0` e têm de passar.

---

### S13.9 · As correções de artefato

Defeitos vivos hoje. `outputs/submissao/` não se altera — corrige-se o **gerador**, e o defeito do artefato entregue fica registrado no post-mortem.

**DoD — pronto quando, cada um verificado:**

1. `12_fronteira_roi_volume.py` deixa de misturar cenários (`roi_central` com `volume_pior`) e publica as duas versões lado a lado.
2. `09_buscar_politica.py:50` — o script volta a selecionar o que foi submetido, **ou** registra em código que a escolha final foi humana. Decisão do responsável pela política.
3. `11_documento_politica.py:266` — a frase *"o melhor ROI compatível com os guard-rails é 11,5% e é onde estamos"* sai; o teto é 11,4569% e o nosso é 11,3294%.
4. `ENTREGAVEL_1_MODELO.md:90` — documenta a PD ao contrário do que foi submetido.
5. `S08_MOTOR_DE_ROI.md:85-91` — as **nove** elasticidades e o exemplo de aceite.
6. `ENTREGAVEL_2_POLITICA.md § 2` (tabela vazia) e `MATRIZ_RISCOS.md` (template não preenchido).
7. ✅ **Ponteiros que envelheceram, com teste que impede a volta.** O diagnóstico inicial estava errado em três pontos, e a correção registra o que de fato se achou:
   - **37 links relativos quebrados** (não "uma referência cruzada"), todos por caminho errado entre `docs/`, `docs/processo/` e `docs/specs/`. O `ROADMAP.md` sozinho tinha 18.
   - **Um byte de controle `0x05`** no `README.md:124` — não "dois caminhos inexistentes". Era `python\modelagem\05_...` com o `\0` interpretado como escape octal. Invisível na leitura.
   - **As specs S10 e S11 estavam certas:** eram **167 testes** na data em que fecharam, medido em `6b0cf63`. O número caiu para 166 quando `2de6840` removeu o R e, com ele, `test_semente_bate_com_o_lado_r`. Quem envelheceu foi o `README.md` e o `AGENTS.md`, que falam do presente.
   - `README.md` e `AGENTS.md` apontavam para `DEBITO_TECNICO.md` como registro da remoção do R. Esse arquivo **nunca mencionou R**.
   - Guardado por `tests/python/test_documentacao.py`: links resolvem, hashes das specs existem, nenhum caractere de controle.
8. `README.md` — a **bifurcação no topo** entre a submissão e a recuperação, para quem clonar saber qual dos dois números é "o" número.

---

## DoD do passo

**Pronto quando:**

1. O post-mortem está escrito, com as dez causas verificáveis. ✅
2. A calibração fecha nas três âncoras **e** passa na validação fora da amostra.
3. Existe política que atende os cinco limites, ou está medido e escrito sob que condições ela não existe.
4. `pytest -q` passa com **173**, incluindo os guardas de documentação e as premissas fixadas.
5. Nenhum script de recuperação contém `0.15` fora da definição do piso.
6. `outputs/submissao/` e `POLITICA_ESCOLHIDA` inalterados ao fim do passo.

## Depende de

S09 (a política submetida), S12 (a fronteira), e a **apuração do professor** — que é insumo externo e não se repete.
