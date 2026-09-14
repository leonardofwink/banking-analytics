# SPEC 01 — Modelo de PD

> **Entregável 1** do [desafio AutoCred](DESAFIO.md). Vale **40 pontos**: 30 pelo AuROC (relativo ao melhor grupo) + 10 por qualidade técnica.
>
> **Status:** aguardando as bases. As decisões abaixo são as que dá para tomar antes do dado chegar — e tomá-las antes evita decidir sob pressão, com o resultado já na tela.
>
> Metodologia: **SDD** — esta spec é o contrato. Código que diverge dela está errado até a spec ser atualizada.

## 1. Objetivo

Estimar `P(default)` de cada contrato, onde **default = atingir 90 dias de atraso nos 12 meses após a concessão** (PD 90/12).

Saída: probabilidade em fração `[0, 1]` por contrato.

## 2. Decisões de modelagem (fechadas)

| Decisão | Valor | Por quê |
| ------- | ----- | ------- |
| Definição de default | 90+ dias de atraso | Dado pelo professor |
| Janela de performance | 12 meses após a concessão | Dado pelo professor |
| Unidade de análise | contrato | O alvo e a submissão são por contrato/proposta |
| Métrica de seleção | **AuROC** | É a métrica oficial. Selecionar por outra é otimizar o que não é cobrado |
| Semente | 42 (`SEMENTE`) | Reprodutibilidade é item de nota |

## 3. ⚠️ A base B não tem o alvo — a seleção de modelo acontece dentro da A

Consequência prática, e é a decisão mais importante desta spec: **não dá para comparar regressão logística × random forest × XGBoost medindo AuROC na base B** — ela não tem o alvo. Quem tem o gabarito é o professor.

Então a comparação tem de acontecer **dentro da base A**, e o split precisa **imitar** a condição real da avaliação: modelo treinado no passado, medido no futuro.

**Split decidido — temporal (out-of-time), não aleatório:**

```
Base A (2022–2024, 10.000 contratos)
├── treino      2022 – 2023        ajusta o modelo
└── validação   2024               escolhe o modelo e o hiperparâmetro
                                   ↓
Base B (2025) ─────────────────► o professor mede o AuROC aqui
```

Split aleatório superestimaria a performance: embaralhar anos deixa o modelo ver o futuro. Como a avaliação é out-of-time (2025 contra 2022–2024), validar out-of-time é a única estimativa honesta do que vai acontecer.

**Modelo final:** depois de escolhida a família e os hiperparâmetros na validação 2024, **retreinar em toda a base A** antes de escorar a B — mais dado, mesma receita. O que não pode é escolher olhando o resultado de 2025.

## 4. Modelos a testar

Nesta ordem, e a ordem tem motivo:

| # | Modelo | Papel |
| - | ------ | ----- |
| 1 | **Regressão logística** (com WOE/binning) | **Baseline e candidato sério.** É o padrão do mercado de crédito porque é explicável coeficiente a coeficiente — e a defesa vale 20 pontos |
| 2 | **Random Forest** | Captura não-linearidade e interação sem tuning pesado |
| 3 | **XGBoost** | Normalmente o melhor AuROC bruto. Custa explicabilidade — mitigar com SHAP |

**Critério de escolha:** maior AuROC na validação 2024. Empate técnico (diferença < 0,01) → **vence o mais simples/explicável**, porque a defesa é parte da nota e o AuROC é relativo ao melhor grupo, não absoluto.

**Todos os três** entram no relatório de comparação, mesmo os perdedores — mostrar o que foi testado e descartado é parte da qualidade técnica.

## 5. Qualidade técnica (os 10 pontos)

A rubrica cobra quatro coisas explicitamente. Cada uma vira requisito verificável:

| Exigência | Como cumprimos |
| --------- | -------------- |
| **Sem vazamento** | Nenhuma variável que só existe depois da concessão (atraso, pagamentos, cobrança, status). Regra de bolso: **se o campo não existiria no momento da proposta, ele não entra**. IV > 0,5 é suspeito até provar o contrário |
| **Split correto** | Temporal, conforme § 3. Todo pré-processamento (imputação, binning, escala) **ajustado só no treino** e aplicado na validação — nunca no conjunto inteiro |
| **Pipeline** | `sklearn.pipeline.Pipeline` de ponta a ponta: pré-processamento + modelo num objeto só. É o que garante que treino e escoragem façam exatamente a mesma coisa |
| **Reprodutibilidade** | `semear()` antes de tudo; versões travadas em `requirements.lock.txt`; o script roda do zero sem passo manual |

## 6. ⚠️ Risco central: as bases A e B são de aprovados, a base C é mar aberto

As bases A e B **só contêm contratos aprovados pela política antiga**. A base C é de **mar aberto** — inclui perfis que a política de 2022 recusava e sobre os quais não existe histórico.

Isso é **viés de seleção** (o *reject inference* do [glossário](GLOSSARIO.md#3-modelagem-e-scorecard)), e tem uma consequência desagradável:

> O modelo pode ter **AuROC ótimo na base B e PD mal calibrada na base C** — e a política, que vale outros 40 pontos, é construída em cima dessa PD.

O AuROC mede **ordenação**, e ordenação tende a sobreviver à mudança de população. O **nível** da probabilidade não: treinado só em aprovados, o modelo tende a **subestimar** a PD de quem a política antiga recusava. Subestimar PD em mar aberto significa **cobrar barato demais de quem é caro** — e o ROI cai onde mais dói.

**O que faremos:**
1. Comparar a distribuição das variáveis de A/B contra C (PSI). Onde C tem massa que A não tem, o modelo está extrapolando.
2. Tratar a PD como **ordenação confiável, nível suspeito** ao montar a política — e deixar margem de segurança no preço das faixas baixas.
3. Documentar isso na defesa. É exatamente o tipo de raciocínio que o bloco de 20 pontos cobra.

## 7. Contrato de saída

O modelo entrega uma função estável, que é o que a política consome:

```python
escorar(df_propostas) -> pd.Series  # índice = id, valor = PD em [0, 1]
```

- Artefato do modelo serializado, versionado **fora do git** (regra crítica nº 1 do [`AGENTS.md`](../AGENTS.md)).
- Fronteira com o resto do projeto: **Parquet** em `dados/processados/`.
- Quem consome não precisa saber qual família venceu — trocar o modelo não pode quebrar a política.

## 8. Critérios de aceite

- [ ] AuROC na validação 2024 reportado para os três modelos, na mesma tabela
- [ ] Nenhuma variável pós-concessão na lista final (revisão campo a campo, registrada)
- [ ] Pré-processamento dentro do `Pipeline`, ajustado só no treino
- [ ] Rodar duas vezes do zero produz o mesmo AuROC
- [ ] PSI de A/B contra C calculado e comentado
- [ ] Distribuição da PD em C sem massa absurda nos extremos (0 ou 1)
- [ ] `escorar()` funciona na base C sem ajuste manual
