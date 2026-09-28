# Post-mortem do desafio AutoCred — por que ficamos em último

> **Por que este documento existe:** o Grupo 3 terminou em **terceiro lugar nas duas etapas**. O time tinha o simulador de ROI mais preciso da turma, a melhor leitura de inferência de rejeitados e um repositório com 166 testes passando — e ainda assim perdeu por 12,6 pontos. Um resultado desses não se explica por descuido, e é por isso que vale escrever.
>
> Cada causa traz: o que assumimos, qual o número que prova o erro, e onde no código ele mora.
>
> **A regra deste documento:** nenhuma causa entra sem evidência verificável — arquivo e linha, ou número da apuração do professor. E a seção *"O que checamos e não era"* existe para o diagnóstico não parecer escolhido a dedo.

---

## 1. O resultado

| | Modelo (40) | Política (40) | Bônus | Parcial (80) |
| - | ----------- | ------------- | ----- | ------------ |
| Grupo 2 · vencedor | **40,0** | 39,2 | 4 | **83,2** |
| Grupo 1 | 38,3 | 33,6 | 3 | 74,9 |
| **Grupo 3 (nós)** | **36,6** | **29,0** | **5** | **70,6** |

Diferença de **12,6 pontos** para o primeiro: **−10,2 em política**, −3,4 em modelo, **+1,0 no bônus**.

| | AUC na Base B | ROI na Base C | Volume | Inadimplência |
| - | ------------- | ------------- | ------ | ------------- |
| Grupo 2 | 0,7711 | **16,53%** | R$ 50,1 MM | **4,75%** |
| Grupo 1 | 0,7646 | 14,97% | R$ 68,6 MM | — |
| **Nós** | 0,7495 | **11,21%** | **R$ 84,4 MM** | 6,33% |

### O que acertamos, e importa registrar

- **O ROI projetado foi o mais preciso da turma:** erramos por **−0,09 pp** (11,30% projetado contra 11,21% realizado). O Grupo 2 errou por +0,13 pp; o Grupo 1, por −1,16 pp.
- **Ganhamos o bônus de inferência de rejeitados: 5 pontos**, o maior dos três. Nota do professor: *"os três trataram o tema e os três o quantificaram. O Grupo 3 teve a leitura mais precisa."*
- **A coerência entre a tabela de faixas e o arquivo submetido saiu perfeita:** zero defeitos em 5.000 linhas.

Nada disso foi suficiente, e é justamente esse o ponto do documento.

---

## 2. O veredito do professor

Slide dedicado ao Grupo 3, intitulado **"A meta era inalcançável"**:

> *"O problema não estava na varredura, estava numa premissa. O grupo **assumiu** que o aceite desabaria acima de 2% ao mês — 'cobrar 3% num mercado de 1,6% não é ilegal, é apenas não ter o cliente'. **O Grupo 2 cobrou 2,506% e manteve 63,9% de aceite.** E a própria política do Grupo 3, **com apenas 0,7 ponto a mais na taxa, teria entregue 16,27% de ROI com R$ 62,8 milhões originados, dentro dos quatro guard-rails.**"*

⚠️ **A frase entre aspas é nossa.** Está em [`python/relatorios/11_documento_politica.py:240`](../../python/relatorios/11_documento_politica.py) e foi no documento entregue. O professor citou o nosso próprio relatório como a premissa que nos afundou.

E o mecanismo, no slide *"Por que o Grupo 2 venceu — não foi o modelo, foi o preço"*:

> *"O Grupo 2 cobrou 2,506% ao mês em média; o Grupo 1, 2,364%; o Grupo 3, 1,876%. Essa diferença de **seis décimos de ponto percentual ao mês**, capitalizada ao longo de três anos e meio de carteira, virou **cinco pontos de ROI anual**."*
>
> *"**Aprovar menos e cobrar mais caro de quem entra rendeu mais do que aprovar muito e cobrar barato.** O Grupo 3 aprovou 59,5% a 1,876% e ficou em último. O Grupo 2 aprovou 44,8% a 2,506% e venceu, com **R$ 34 milhões a menos de capital imobilizado**."*

**O desafio inteiro coube numa alavanca:** 0,6 ponto percentual ao mês × 3,5 anos de carteira = 5 pontos de ROI anual.

---

## 3. As dez causas, em ordem

### 3.1 🔴 A âncora de preço era o nosso próprio livro, não o mercado

`TAXA_MERCADO = 0.0159` ([`banking/roi.py:49`](../../python/banking/roi.py)) é a média do livro da **própria AutoCred**, usada no código como *"a melhor proxy do preço que o cliente encontra no concorrente"*.

Não é. O concorrente é o mercado, e **o preço do mercado é público**.

O Grupo 2 comparou a taxa proposta com **dados do Banco Central** e mostrou que 2,54% a.m. fica **acima da mediana das 45 instituições e abaixo do topo**. O professor: *"fez o que nenhum outro fez… preço defensável, não arbitrado."*

O efeito é aritmético e não depende de acertar a elasticidade. Como `excesso = taxa / TAXA_MERCADO − 1` (`roi.py:216`):

| Âncora | `excesso` a 2,506% | Aceite com o **nosso** β=1,5 |
| ------ | ------------------ | ---------------------------- |
| 1,59% (livro da AutoCred) | 0,576 | **42%** |
| ~2,3% (mediana BCB) | 0,090 | **~74%** |

Observado: **63,9%**. Corrigir **só a âncora**, mantendo a elasticidade errada, já explicaria a maior parte da diferença.

**O agravante:** o defeito estava nomeado nas nossas próprias notas — *"a dispersão de preço da Base A é o livro da AutoCred, não o mercado"* — e foi registrado como âncora rejeitada, sem ação.

### 3.2 🔴 A elasticidade era duas a três vezes alta demais

`β_taxa = 1,5` no cenário central, com os três cenários cobrindo de 0,8 a 2,5 (`roi.py:96-100`).

A realidade, extraída do dado do Grupo 2 — 63,9% de aceite a 2,506%:

```
excesso = 2,506 / 1,59 − 1 = 0,576
0,639 = a0 · exp(−β · 0,576)   →   β ≈ 0,50 a 0,69
```

**A faixa inteira dos três cenários não continha o mundo real.** O erro não foi escolher o central em vez do otimista.

Confirmação independente, pela apuração: o volume realizado (**R$ 84,4 MM**) bate o nosso cenário **otimista** (R$ 86,1 MM), não o central (R$ 66,7 MM). Subprojetamos o volume em **26,5%** — e fomos o único grupo a errar para baixo.

O ROI acertou **por compensação**: o aceite move numerador e denominador juntos, como o nosso próprio deck afirma. Um erro de 26,5% no volume não apareceu no ROI.

### 3.3 🔴 Não testamos nenhuma das duas premissas

Varremos **5.600 combinações de política** e **zero de premissa**. Todo o rigor foi para as variáveis de decisão; nenhum para as suposições que as dominavam.

E o instrumento existia. [`python/analises/21_premissa_de_aceite.py:131-137`](../../python/analises/21_premissa_de_aceite.py) faz exatamente essa varredura de elasticidade:

```python
print("\n  Escalando as elasticidades do cenario central por um fator f:")
o_deni = ofertas_deni(True)
for f in (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5):
```

O laço roda **só sobre `o_deni`** — a política de um colega, para checar se estávamos sendo injustos com ele. O objeto `of_leo` está no mesmo escopo, usado nas seções A e B da mesma página, e nunca entrou no laço.

**Uma linha separava o projeto de encontrar o próprio erro.**

### 3.4 🔴 A evidência que "provou" a impossibilidade misturava cenários

As colunas de `outputs/tabelas/s12_fronteira_roi_volume.csv`:

```
corte, taxa_base, k_risco, prazo_max, entrada_base, entrada_passo,
roi_central, aprovacao, inadimplencia_pior, volume_pior, viavel
```

**O ROI vem do cenário central. O volume e a inadimplência vêm do pessimista.** Sobre essa tabela, o slide 9 da defesa afirma:

> *"A meta de 15% é incompatível com o piso de volume — **e isso foi medido, não argumentado**."*

Foi medido comparando o ROI de um mundo com o volume de **outro**. Não é fronteira de mundo nenhum. O "volume máximo de R$ 20,5 mi entre as 4.044 políticas" é volume **pessimista**.

Na apuração, o piso de R$ 40 MM ficou folgado para os três grupos (68,6 · 50,1 · 84,4 MM). **O guard-rail que dissemos bloquear a meta nunca mordeu em mundo nenhum.**

Este é o elo que transforma uma premissa num fato publicado: o critério conservador não ficou só no filtro — vazou para dentro da evidência, no nome de uma coluna.

### 3.5 🟠 Aprovamos gente demais

| | PD máxima aceita | Propostas aprovadas |
| - | ---------------- | ------------------- |
| Grupo 2 | **7,88%** | 44,8% |
| Grupo 1 | 15,00% | 61,6% |
| **Nós** | **13,00%** | 59,5% |

O professor: *"o mesmo número de score significa risco diferente em cada grupo. O score 4 do Grupo 1 aceita PD de até 15,0%; o do Grupo 2, até 7,88%; no Grupo 3, o score 4 já é recusa."*

O `corte` nomeia uma faixa; o que decide é o **teto de risco** que ela carrega.

O vencedor ancorou as faixas nos **decis da Base B** — população melhor que a C — e obteve seletividade automaticamente. E foi explícito: *"reconheceu que a Base C era outra população — PD média de 14,4% contra 7,8% — e ajustou a política a isso."*

Nós medimos o mesmo deslocamento (PSI de 0,39) e escolhemos cortes **absolutos de PD** justamente para **não** ajustar — com um argumento que continua bom no papel: *"quantil muda de sentido quando a população muda"*. A consequência é que a mesma régua, numa população pior, deixou entrar risco pior.

### 3.6 🟠 Quando o conjunto ficou vazio, cedeu a exigência do cliente

Os quatro limites do enunciado foram tratados como invioláveis. A exigência de viabilidade nos **três cenários** — que é invenção nossa ([`09_buscar_politica.py:6-8`](../../python/modelagem/09_buscar_politica.py)) — também.

Quando nada fechou, foi o **15% exigido pelo conselho** que cedeu.

> **A assimetria é a lição:** quando um conjunto de restrições é inviável, relaxe primeiro as **suas premissas**, depois as **exigências de quem pediu**. Fizemos o inverso.

Camada adicional: `EMPATE_ROI = 0.01` (`09_buscar_politica.py:50`). ROI é fração, então essa é uma janela de empate de **1 ponto percentual**, não de 0,1–0,2 pp como a narrativa do projeto supõe — e o log a imprime como `{:.0%}` → "1%", que lê como inofensivo. Ela admite **29 das 70 políticas viáveis**, e o desempate por folga escolhe a mais barata e mais plana.

### 3.7 🟠 Cost-plus em vez de preço defensável

Só nós usamos `taxa = taxa_base + k_risco × perda` ([`banking/politica.py:94`](../../python/banking/politica.py)), com `taxa_base` e `k_risco` escolhidos por nós.

| | Regra de preço | Taxa praticada |
| - | -------------- | -------------- |
| Grupo 2 | **tabela fixa por faixa**, validada contra o BCB | 2,30–2,90% · média 2,561% |
| Grupo 1 | **retorno-alvo**: menor taxa que dê ROI de 14%, contrato a contrato | 1,96–3,09% · média 2,425% |
| **Nós** | cost-plus: 1,50% + 10% da perda esperada | 1,63–2,29% · média 1,911% |

O Grupo 2 **começa** a cobrar em 2,30%. Nós **terminamos** em 2,29%, na pior faixa que aprovamos. **A nossa política inteira era mais barata que a primeira linha da dele.**

Nota do professor sobre o retorno-alvo do Grupo 1: *"é um algoritmo, não uma tabela de política. Funciona, mas é difícil de defender num comitê."* **A tabela defensável venceu o algoritmo.**

### 3.8 🟡 Zero feature engineering

Catorze colunas cruas, nenhuma derivada, nenhum WOE ou binning — registrado em `DEBITO_TECNICO.md § 3` como débito consciente.

O conteúdo concreto do que faltou está descrito no Grupo 1: **LightGBM com calibração isotônica, Optuna penalizando instabilidade entre safras, e flags de ausência** — porque falta de bureau é informativa. PSI de 0,003 entre as bases.

Separou 0,0216 de AUC entre nós e o primeiro. É pouco em AUC e são pontos relativos.

### 3.9 🟡 Sem restrições monotônicas no modelo

O vencedor usou. O professor: *"as restrições monotônicas impedem o modelo de aprender que mais restrições reduzem o risco, proteção de bom senso que **custa pouco AUC e compra muita defensabilidade**."*

Nunca cogitamos. É uma linha de configuração no XGBoost.

### 3.10 🟡 Prazo fixo em 48 meses para todos

Fomos o **único** grupo a não respeitar o prazo pedido pelo cliente — o Grupo 1 deu o pedido, o Grupo 2 deu o pedido limitado a 60 meses.

Sob a elasticidade real, forçar encurtamento custa aceite. A nossa própria análise já media **49% dos aprovados recebendo prazo diferente do que pediram**.

---

## 4. O que checamos e não era

Oito hipóteses levantadas e **derrubadas com medição** durante a análise. Estão aqui para o diagnóstico não parecer escolhido a dedo.

| Hipótese | Veredito |
| -------- | -------- |
| A âncora está defasada no tempo (Selic de 2022 ≠ 2025) | **Falsa.** Taxa **estacionária** nos 42 meses observáveis: regressão contra o tempo com R² de 0,000004 e p de 0,81; ANOVA por trimestre p de 0,94. A Base B tem `taxa_juros_am` e mede 2025-S1 direto: **1,5896%** |
| A âncora deveria ser condicional ao risco | **Falsa, e piora.** Perda esperada diluída no prazo vale 3–62 p.b./mês, então a âncora só varia ~15 p.b. em toda a carteira. E 83% do volume aprovado tem preço justo *abaixo* de 1,59% |
| Redesenhar as bordas das faixas liberaria ROI | **Falsa** ⚠️ — ganho máximo de **1,6 pontos-base** em 6 vetores × 877.716 políticas |
| Faixas por quantil resolveriam | **Falsa** ⚠️ — decis põem a aprovação em múltiplos de 10% |
| As faixas reproduzem o subsídio cruzado do conselho | **Falsa.** Maior razão p75/p25 é **1,355**; a política antiga tinha **uma** faixa cobrindo 350× |
| A grade grossa do S12 causou a perda | **Falsa como causa.** Pulou políticas viáveis no central, mas o critério dos três cenários as excluiria igual |
| Sobreajuste do modelo (AuROC 0,8576 in-sample) | **Falsa.** Otimismo de resubstituição de um GBM de 300 árvores; o gap já estava medido e publicado em `s05_sobreajuste.csv:4`, e `modelo.py:288-293` **se recusa** a reportar o número in-sample |
| Exigir robustez (minimax) foi o erro | **Falsa.** O vencedor **também** fez: *"testou subir a taxa em 0,3 ponto, viu que romperia dois guard-rails no cenário severo e desistiu. Sabia onde estava a fronteira."* Mesma prudência — régua diferente |

> ⚠️ **Contaminação de premissa.** As linhas marcadas foram medidas sob `β_taxa = 1,5` — a premissa que o professor identificou como causa. São 5,3 milhões de avaliações corretas sobre base errada, e os vereditos voltam para a fila depois da recalibração. **O próprio ato de listá-las repete o erro que o documento diagnostica**, e por isso a marca fica visível em vez de a linha ser apagada.

---

## 5. A lição

> *"Rigor analítico sobre uma premissa errada produz uma conclusão errada e com muita confiança. A varredura de 5.600 combinações estava correta; a elasticidade que ela assumia, não. Antes de confiar no resultado de uma simulação (**principalmente de IA**), vale checar a premissa que a sustenta, **ainda mais quando o resultado é 'não dá para fazer'**."*
>
> — o professor, slide *"O risco mais perigoso da profissão"*

O que torna isso difícil de enxergar de dentro: **nenhum artefato interno acusou nada**. A spec passou no DoD. Os 166 testes passaram. Os números reproduziram. A coerência saiu perfeita em 5.000 linhas. O ROI projetado foi o mais preciso da turma.

Tudo correto, sobre base errada.

A regra que sai daqui está registrada em [`AGENTS.md`](../../AGENTS.md):

> **Conclusão negativa exige teste de premissa.** Antes de publicar que algo *"não dá para fazer"*, varra a premissa que sustenta a conclusão, não só as variáveis de decisão. Um resultado negativo fecha a porta para a ação e ninguém volta a abri-la — carrega ônus de prova **maior**, não menor.
>
> Sintoma de violação: milhares de combinações das variáveis que você escolhe e **zero** da suposição que as domina.

### A prestação de contas da IA

Este post-mortem foi escrito com assistência de IA, e o processo reproduziu o erro que ele diagnostica. Fica registrado porque é o mesmo padrão:

- A **elasticidade** foi declarada descartada no meio da análise, com base em o ROI projetado ter errado por apenas 0,09 pp. Era a causa raiz. A reversão só veio quando chegou o dado de volume realizado.
- **A jogada vencedora foi escrita e descartada.** Ao investigar a âncora, o raciocínio registrado foi: *"há uma versão com referência externa — o BCB publica taxas médias para aquisição de veículos… mas é trazer dado de fora para um exercício fechado, arriscado na banca."* O professor descreve a mesma ideia como *"o que nenhum outro fez… preço defensável, não arbitrado."* A referência externa foi tratada como risco de defesa quando **era** a defesa.
- Foram testadas **duas variantes erradas** da hipótese da âncora — defasagem temporal e condicionalidade ao risco — e nunca a única que importava.

Velocidade de análise não substitui checagem de premissa. Amplifica o custo de errá-la.

---

## 6. O que fica para a recuperação

A submissão está encerrada e é registro histórico. O trabalho de recuperação — tratar os **15% como guard-rail** e refazer a política sob âncora e elasticidade corrigidas — está especificado no passo **S13**, em `docs/specs/`.

O alvo é conhecido, e é o próprio professor quem o dá:

> *"a própria política do Grupo 3, com apenas 0,7 ponto a mais na taxa, teria entregue **16,27% de ROI com R$ 62,8 milhões** originados, dentro dos quatro guard-rails."*

Esse número é o **gabarito de validação** da recalibração — e não se repete. Calibra-se nos dados realizados e confere-se se ele sai sozinho.
