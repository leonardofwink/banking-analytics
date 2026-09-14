# Roadmap — o objetivo final quebrado em passos

> **Como ler:** o objetivo final ("entregar o modelo e a política até 25/09") é grande demais para ser executado. Aqui ele vira **11 passos pequenos**, cada um com um resultado verificável. Cada passo é uma **spec**: a spec detalhada nasce em `docs/specs/` **quando o passo começa**, não antes — escrever as onze de uma vez seria adivinhar decisões que ainda não temos informação para tomar.
>
> **Requisitos:** [`DESAFIO.md`](DESAFIO.md) · **Decisões macro:** [`ENTREGAVEL_1_MODELO.md`](ENTREGAVEL_1_MODELO.md), [`ENTREGAVEL_2_POLITICA.md`](ENTREGAVEL_2_POLITICA.md) · **Dados:** [`DICIONARIO_DADOS.md`](DICIONARIO_DADOS.md)

## O que estamos construindo, em uma frase

A AutoCred perde dinheiro na **porta de entrada**. Nós vamos construir a régua que mede o risco de cada proposta (**o modelo de PD**) e as regras que transformam essa régua em decisão de negócio (**a política**), de forma que a carteira resultante dê **ROI acima de 15% ao ano** sem furar quatro limites.

## A cadeia que precisa fechar

```
    S01          S03→S06            S07         S02+S08         S09→S10
  ingestão  →  modelo de PD  →  faixa de   →   perda      →   política   →  ROI
   (dado)      (probabilidade)     score      esperada       (4 alavancas)
                                              PD×EAD×LGD
```

Cada seta é uma tradução: probabilidade vira faixa, faixa vira dinheiro, dinheiro vira decisão. **Se qualquer elo quebrar, o número final não significa nada** — e a defesa (20 pontos) é justamente explicar essa cadeia inteira.

---

## Fase 0 — Fundação

### S01 · Ingestão e contrato de dados

**O que é:** ler os três CSVs, remover as colunas proibidas, conferir tipos e contagens, gravar em Parquet em `dados/processados/`.

**Por que existe:** todo o resto depende de a base estar certa. E, principalmente, porque a remoção das [colunas proibidas](DICIONARIO_DADOS.md#colunas-proibidas-pós-concessão) precisa acontecer **em um lugar só**. Se cada script remover por conta própria, um vai esquecer — e o esquecimento custa 30 pontos, sem dar erro.

**Como faremos:** uma função `carregar(base)` que aplica a lista de exclusão e devolve o DataFrame limpo. Um teste que **falha** se qualquer coluna proibida sobreviver.

**DoD — pronto quando:** as três bases carregam com 10.000 / 3.000 / 5.000 linhas, nenhuma coluna proibida presente, e o teste passa.

**Depende de:** nada. É o primeiro.

---

### S02 · Perda esperada (EAD e LGD)

**O que é:** transformar as duas tabelas do professor em funções: `fator_ead(prazo, ltv)` e `lgd(idade_veiculo, ltv, tem_avalista)`, e com elas `perda_esperada = pd × fator_ead × valor_financiado × lgd`.

**Por que existe:** é o elo que transforma probabilidade em **dinheiro**. Sem ele, a PD é um número abstrato e não dá para decidir preço nenhum. É também o passo que a defesa cobra explicitamente ("encadeamento PD → EAD → LGD → perda").

**Como faremos:** ler o `.xlsx`, mapear as faixas de LTV (`até 60%`, `60-70%`, `70-80%`, `80-90%`, `acima de 90%`) e de idade do veículo, e aplicar o ajuste de −0,061 quando há avalista.

**DoD — pronto quando:** os valores calculados **batem com `ead_realizado` e `lgd_realizado` dos inadimplentes da base A**. Esse é um luxo raro: temos o gabarito para conferir. Se não bater, ou entendemos a faixa errado, ou a tabela tem outra convenção — e é melhor descobrir agora do que na apuração.

**Depende de:** S01. **Pode rodar em paralelo com todo o bloco do modelo.**

---

## Fase 1 — O modelo de PD (entregável 1, 40 pontos)

### S03 · Exploratória e split temporal

**O que é:** olhar as variáveis (distribuição, missing, relação com o alvo) e **fixar** a divisão treino/validação: treino 2022–2023 (6.670 contratos), validação 2024 (3.330).

**Por que existe:** duas razões. A primeira é óbvia — você precisa conhecer o dado antes de modelar. A segunda é sutil e mais importante: **o split tem que ser fixado antes de ver qualquer resultado**. Quem testa vários splits e fica com o que deu o melhor número está escolhendo o mais sortudo, não o melhor — e o número bonito não se repete na base B.

**Como faremos:** um relatório de EDA (tabelas e gráficos em `outputs/`) e uma função de split determinística.

**DoD — pronto quando:** o split está em código, a EDA aponta quais variáveis parecem discriminar e onde estão os missing.

**Depende de:** S01.

---

### S04 · Baseline: regressão logística

**O que é:** o primeiro modelo, dentro de um `Pipeline` do scikit-learn: imputação dos missing + tratamento das categóricas + regressão logística. Medir **AuROC** e **KS** na validação 2024.

**Por que existe:** baseline é a **régua**. Sem ela você não sabe se um AuROC de 0,72 é bom ou ruim — pode ser que o problema seja fácil e 0,72 seja fraco, ou que seja difícil e 0,72 seja ótimo. E a logística não é só régua: é **candidata séria**, porque é explicável coeficiente a coeficiente, e a defesa vale 20 pontos.

**Como faremos:** `Pipeline` com todo o pré-processamento dentro. Isso não é preciosismo — é o que garante que a imputação seja **aprendida só no treino** e aplicada na validação, em vez de vazar a média do conjunto inteiro. É item explícito da nota.

**DoD — pronto quando:** AuROC e KS reportados na validação, e rodar duas vezes dá o mesmo número.

**Depende de:** S03.

---

### S05 · Desafiantes: Random Forest e XGBoost

**O que é:** treinar os dois com **o mesmo pipeline, o mesmo split e a mesma semente**, e comparar na mesma tabela.

**Por que existe:** modelos de árvore capturam interação e não-linearidade que a logística não vê. Normalmente ganham em AuROC. A comparação existe para descobrir **quanto** ganham — e se o ganho paga a perda de explicabilidade.

**Como faremos:** mesma estrutura do S04, trocando só o estimador final. Se a diferença for menor que 0,01 de AuROC, **fica o mais simples** — o AuROC vale 30 pontos relativos ao melhor grupo, mas a defesa vale 20 absolutos.

**DoD — pronto quando:** tabela comparativa dos três, com a escolha justificada por escrito.

**Depende de:** S04.

---

### S06 · Escoragem e submissão do modelo

**O que é:** retreinar o modelo escolhido em **toda a base A** (2022–2024) e escorar a base B → `submissao_modelo.csv` (só duas colunas: `id_contrato`, `pd`).

**Por que a base B precisa ser escorada, se a política é aplicada na C:** porque **o professor tirou o alvo da base B e guardou**. Ele tem o gabarito, nós temos a régua — e o AuROC só existe cruzando os dois. Mandamos as 3.000 PDs, ele cruza pelo `id_contrato` e calcula. Sem essa entrega, os 30 pontos do AuROC ficam sem nota. É o formato de competição: o participante entrega as previsões, o organizador tem o resultado real.

**Nenhuma política encosta na base B.** Ali os contratos **já foram fechados** sob a política antiga — ela inclusive traz `taxa_juros_am` e `prazo_meses` preenchidos. Não há o que decidir: a única pergunta é *"seu modelo teria acertado quem ia quebrar?"*. A base C é o oposto: não tem taxa nem prazo porque o negócio ainda não aconteceu, e quem decide somos nós.

| | Base B | Base C |
| - | ------ | ------ |
| O que entregamos | só `id_contrato, pd` | `pd`, `score`, `decisao`, `taxa`, `prazo`, `entrada` |
| O que é medido | **AuROC** (30 pts) | **ROI + coerência + volume** (40 pts) |
| Aplicamos política? | **não** | sim |

**Por que o AuROC não sai da base C:** ela não tem desfecho fixo — reage às nossas decisões, então não há "verdadeiro" estável contra o qual medir ordenação. E os dois blocos são avaliados separadamente de propósito: a B mede a **régua**, a C mede a **decisão**. Misturar faria um erro de política contaminar a nota do modelo.

**Por que retreinar em A inteira:** a validação 2024 serviu para **escolher**. Escolhido o modelo, treinar com mais dado melhora a estimativa — mesma receita, mais ingredientes. O que não pode é escolher olhando 2025, que não temos.

**Como faremos:** ajustar o pipeline em A inteira, prever `predict_proba` em B, gravar `id_contrato,pd`.

**DoD — pronto quando:** 3.000 linhas, ids idênticos aos da base B, `pd` em [0,1] com distribuição plausível (sem massa em 0 ou 1).

**Depende de:** S05. **→ Entregável 1 pronto.**

---

## Fase 2 — A política (entregável 2, 40 pontos)

### S07 · Faixas de score (PD → 1 a 10)

**O que é:** decidir como agrupar as PDs em dez faixas, sendo 1 o pior risco e 10 o melhor.

**Por que existe:** o enunciado é explícito — *"toda decisão de política se apoia no score, não na PD bruta"*, e *"como agrupar as PDs nessas dez faixas é escolha de vocês, e é uma escolha com consequência"*. Faixa larga demais junta riscos diferentes no mesmo preço; estreita demais cria faixas com pouca gente e sem significado.

**Como faremos:** faixas por **corte de PD**, não por quantil. Quantil muda de sentido quando a população muda — e a base C é outra população (score de bureau 96 pontos menor). Se a faixa 5 significar "PD entre 8% e 11%", ela quer dizer a mesma coisa em qualquer base.

**DoD — pronto quando:** função determinística `pd → score`, com a distribuição das 5.000 propostas por faixa documentada.

**Depende de:** S06 (ou uma PD provisória, para não bloquear).

---

### S08 · Motor de simulação do ROI

**O que é:** uma função que recebe uma política e um cenário e devolve os quatro números que importam: **ROI anualizado, inadimplência, volume originado e taxa de aprovação**.

**Por que existe:** este é o passo que **substitui o simulador que não temos**. Sem ele, decidir a taxa de cada faixa é chute. Com ele, dá para comparar políticas antes de submeter — e só submetemos uma vez.

**Como faremos:** implementar a fórmula oficial, peça por peça:
- **Parcela** pela Tabela Price, com a taxa e o prazo que ofertarmos.
- **Juros de quem paga até o fim:** `parcela × prazo − financiado`.
- **Juros de quem quebra:** só até o mês do calote — ponderado pela [distribuição do mês do default](DICIONARIO_DADOS.md#parâmetros-de-ead-e-lgd-dados-não-modelados) (média 6,9, pico entre o 5º e o 8º mês).
- **Perda realizada:** `fator_ead × financiado × lgd` (vem do S02).
- **Aceite e seleção adversa:** como não sabemos a intensidade, entram como **cenários** — otimista, central, pessimista.

**DoD — pronto quando:** testado contra casos de resposta conhecida (carteira sem nenhum default → ROI = juros ÷ volume ÷ anos) e reproduzindo a fórmula oficial.

**Depende de:** S02.

---

### S09 · A tabela de política

**O que é:** decidir, para cada uma das dez faixas, as quatro alavancas: **aprovar ou negar, taxa, prazo, entrada mínima**.

**Por que existe:** é o entregável. Uma política de crédito é uma tabela de regras — não um modelo.

**Como faremos:** piso analítico por faixa (a taxa que cobre a perda esperada), depois simular candidatas no motor do S08 sob os três cenários, descartando quem fura guard-rail em **qualquer** cenário razoável. Escolher a **robusta**, não a máxima: como se submete uma vez só, uma política que entrega 18% nos três cenários vence uma que entrega 24% no central e fura o volume no pessimista — porque furar corta a nota pela metade.

**DoD — pronto quando:** tabela monotônica (score melhor nunca recebe condição pior), guard-rails verificados por script, e **cada linha com uma frase de justificativa** — que é o insumo da defesa.

**Depende de:** S07 e S08.

---

### S10 · Aplicação à base C e submissão

**O que é:** aplicar a política às 5.000 propostas e gerar `submissao_politica.csv`.

**Por que existe:** é a entrega. E tem uma sutileza: a base C **não tem** `ltv`, `prazo_meses` nem `comprometimento_renda` — só as versões *desejadas* — porque essas variáveis dependem da nossa decisão. Escoramos em duas passagens: com o desejado para achar a faixa, com o ofertado para estimar o risco real do contrato.

**Como faremos:** gerar o CSV e rodar um **validador** que confere linha a linha: ids completos, score coerente com a PD, taxa/prazo/entrada iguais aos da tabela de faixas, campos vazios em todo `NEGAR`, taxa ≤ 3,5%, aprovação ≥ 35%. **Nenhum arquivo é enviado sem passar.**

**DoD — pronto quando:** 5.000 linhas e validador limpo.

**Depende de:** S09. **→ Entregável 2 pronto.**

---

## Fase 3 — A defesa (20 pontos)

### S11 · Documento de política e narrativa

**O que é:** preencher o `template_documento_politica.docx` e montar a apresentação ao conselho.

**Por que existe:** vale 20 pontos e, segundo o professor, **decide o desafio**: *"o grupo que vencer não será o que tiver o maior AuROC, será o que conseguir explicar por que aprovou quem aprovou, por que cobrou o que cobrou, e por que isso dava o retorno que dava"*.

**Como faremos:** a narrativa segue a cadeia: PD → EAD → LGD → perda esperada → preço → ROI. Cada decisão da tabela do S09 já tem a frase de justificativa escrita; aqui elas viram argumento. Incluir o que **não** fizemos e por quê — a armadilha que evitamos, o viés de seleção que reconhecemos.

**DoD — pronto quando:** alguém de fora consegue seguir o raciocínio do número final até a proposta individual.

**Depende de:** S06 e S10.

---

## Dependências e paralelismo

```
S01 ──┬── S02 ──────────────┬── S08 ──┐
      │                     │         ├── S09 ── S10 ──┐
      └── S03 ── S04 ── S05 ── S06 ── S07 ─────────────┴── S11
```

**As duas frentes só se encontram no S09.** O bloco de dados (S01–S02) libera as duas; o modelo segue por S03–S06 e a política por S07–S08. Quem cuida da política **não precisa esperar o modelo final**: pode trabalhar com uma PD provisória, porque o que S09 consome é o *contrato* `pd → score`, não o modelo que a produziu.

## Ordem sugerida

| Quando | Passos | Observação |
| ------ | ------ | ---------- |
| Primeiro | **S01** | Bloqueia tudo |
| Em seguida, em paralelo | **S02** e **S03** | S02 é curto e valida contra gabarito |
| Bloco do modelo | S04 → S05 → S06 | Baseline antes de desafiante, sempre |
| Bloco da política | S07 → S08 → S09 → S10 | S08 é o mais trabalhoso da frente |
| Por último | S11 | Mas anotar as justificativas **desde o S09** |
