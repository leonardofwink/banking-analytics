# S12 · A meta de 15% de ROI é alcançável?

> Verificação posterior ao S11, feita para responder a uma pergunta da defesa.
> Não estava no [`ROADMAP.md`](../ROADMAP.md) original.
>
> ✅ **CONCLUÍDO em 2026-09-23** — 5.600 políticas testadas, nenhuma viável bate a meta.

## Status das subetapas

| Subetapa | Entrega | DoD | Status |
| -------- | ------- | --- | ------ |
| S12.1 | Abrir as alavancas que o S09 manteve estreitas | 2/2 | ✅ |
| S12.2 | Varredura e fronteira medida | 3/3 | ✅ |
| S12.3 | Diagnóstico: qual guard-rail bloqueia | 2/2 | ✅ |

## A pergunta

A tabela de indicadores do template pede **ROI anualizado acima de 15%**. A
nossa política projeta **11,3%**. Duas explicações possíveis, e elas levam a
respostas opostas na defesa:

| | Se for isso | O que fazer |
| - | ---------- | ----------- |
| **Busca incompleta** | existe uma combinação que bate a meta e nós não procuramos direito | achar e trocar a política |
| **Restrição do problema** | a meta é incompatível com os guard-rails | declarar, com a medição que prova |

Não dá para escolher entre as duas por argumento. Só medindo.

## 🔑 O que o S09 não tinha testado

A grade original tinha 960 políticas, mas duas alavancas ficaram estreitas — e
são exatamente as que alguém perguntaria primeiro:

| Alavanca | S09 | S12 |
| -------- | --- | --- |
| Corte de aprovação | 7, 6, 5, 4 | igual |
| Taxa base | 1,50% a 2,50% | 1,50% a **3,00%** |
| k de risco | 0 a 0,30 | 0 a **0,50** |
| **Prazo máximo** | **48, 60** | **24, 36, 48, 60** |
| **Entrada base** | **0, 5%, 10%** | **0, 10%, 20%, 30%, 40%** |
| Passo de entrada | 0, 4pp | igual |
| **Total** | **960** | **5.600** |

**O prazo não pode passar de quatro valores.** A tabela de EAD do professor
define fatores para 24, 36, 48 e 60 meses e mais nada — `fator_ead()` levanta
`KeyError` em qualquer outro. Ofertar 30 ou 42 meses tornaria a perda esperada
incalculável com os parâmetros dados.

## O resultado

| | S09 | S12 |
| - | --- | --- |
| Políticas testadas | 960 | **5.600** |
| Viáveis nos três cenários | 70 | 106 |
| **Melhor ROI viável** | 11,42% | **11,46%** |
| Batem a meta de 15% | 543 | **4.044** |
| **Dessas, viáveis** | **0** | **0** |

Sextuplicar o espaço de busca encontrou **4.044 políticas que batem a meta e
nenhuma que sobrevive aos guard-rails**. O teto viável subiu 0,04 ponto
percentual.

## 🔑 Um único guard-rail bloqueia a meta

Olhando só as 4.044 que batem 15%, no melhor valor que cada uma atinge:

| Guard-rail | Melhor entre elas | Limite | |
| ---------- | ----------------- | ------ | - |
| Inadimplência da carteira | 5,26% | máximo de 8% | ✅ passa |
| Taxa de aprovação | 68,7% | mínimo de 35% | ✅ passa |
| **Volume originado** | **R$ 20,5 mi** | **mínimo de R$ 40 mi** | ❌ **bloqueia** |

**Não é risco e não é seletividade — é volume, e só volume.** A única forma de
chegar a 15% é originar cerca de metade do mínimo exigido.

Isso é coerente com o desenho do enunciado, que diz que o conselho quer *"ROI
dentro do apetite de risco, **e sem parar de crescer**"*. O ROI é uma razão —
retorno por real emprestado por ano — e a forma fácil de melhorá-la é emprestar
menos, para os melhores, mais caro. O piso de volume existe para fechar essa
saída.

## Por que toda alavanca troca ROI por volume

> **Estendida em 25/09/2026.** O painel interativo varre a mesma fronteira
> numa grade que **contém** esta — cortes de 1 a 10, taxa de 1,00% a 3,50% e
> entrada até 50%, num total de **26.400 políticas**. O resultado não muda:
> **16.820 passam dos 15% de ROI e nenhuma respeita os quatro limites nos três
> cenários.** O `25_dados_do_painel.py` confere a continência antes de varrer e
> aborta se algum valor desta grade não couber na dele.

A correlação de Pearson entre ROI e volume na varredura é **−0,767**
(Spearman: −0,840). Não é acaso da
grade; é a estrutura do problema:

| Alavanca | Efeito no ROI | Efeito no volume |
| -------- | ------------- | ---------------- |
| Subir a taxa | ⬆️ mais juros | ⬇️⬇️ aceite cai (β=1,5) **e** PD sobe por seleção adversa (γ=0,5) |
| Exigir mais entrada | ⬆️ PD e LGD caem | ⬇️⬇️ financia-se menos por contrato **e** aceite cai (β=2,0) |
| Encurtar o prazo | ⬇️ **piora** — ver abaixo | ⬇️ aceite cai (β=0,8) |
| Subir o corte | ⬆️ carteira melhor | ⬇️ menos aprovados |

A única alavanca que escaparia da troca seria **um modelo de PD melhor**:
prever melhor permite cobrar mais barato de quem merece e recusar melhor quem
não merece, ganhando margem sem perder volume. Está limitada pelo AuROC de
0,7234 que os dados permitiram.

## 🔑 Encurtar o prazo piora o ROI, não melhora

| Prazo | Viáveis | Melhor ROI |
| ----- | ------- | ---------- |
| 24 meses | 8 | **7,63%** |
| 36 meses | 34 | 11,05% |
| **48 meses** | **49** | **11,46%** ← o escolhido |
| 60 meses | 15 | 10,81% |

A intuição diz o contrário: o ROI é dividido pelo prazo em anos, então prazo
menor deveria render mais. **A intuição está errada, e por causa da Tabela
Price.** Com a nossa taxa média de 1,91% ao mês:

| Prazo | Juros totais sobre o principal | ÷ anos | ROI antes da perda |
| ----- | ------------------------------ | ------ | ------------------ |
| 24m | 25,6% | ÷ 2 | 12,8% |
| 36m | 39,2% | ÷ 3 | 13,1% |
| 48m | 53,6% | ÷ 4 | 13,4% |
| 60m | 68,9% | ÷ 5 | 13,8% |

Em prazo longo o saldo devedor amortiza mais devagar, então você cobra juros
sobre um saldo médio maior. O efeito de escala vence o do divisor.

O contra-argumento seria a exposição: prazo longo, mais EAD. Mas **o fator de
EAD varia só de 0,98 a 1,04** na tabela do professor — não é alavanca de
política. Por isso 60 meses perde para 48 por pouco (perda maior), e 24 meses
desaba (juros muito menores).

## A entrada tem ótimo interior, e ele é raso

| Entrada mínima | Viáveis | Melhor ROI | Volume no pior cenário |
| -------------- | ------- | ---------- | ---------------------- |
| 0% | 43 | 11,39% | R$ 45,4 mi |
| **10%** | 37 | 11,42% | **R$ 46,9 mi** ← o escolhido |
| 20% | 20 | **11,46%** | R$ 40,9 mi ⚠️ |
| 30% | 6 | 9,04% | R$ 41,3 mi |
| 40% | **0** | — | — |

Exigir 20% renderia **+0,04 ponto de ROI** e custaria **R$ 6 milhões de
volume**, deixando ~2% de folga até o guard-rail contra os 12,7% de hoje.

Na rubrica: ROI vale 25 pontos relativos, e 0,04 ponto sobre uma base de 11,4%
é 0,4% relativo — menos de 0,1 ponto de nota. Violar o volume corta a nota de
política pela metade, ou seja, **20 pontos**. A troca é ruim por duas ordens de
grandeza.

Acima de 30% a entrada vira destrutiva, e em 40% não sobra política viável
alguma.

## Consequência para a defesa

A política do S09 **não muda**. Ela está a 0,13 ponto do teto de tudo que é
viável, com a melhor folga do conjunto.

O que muda é o argumento. Antes o documento sustentava a escolha pela leitura
do enunciado — os outros quatro indicadores são "mínimo", "máximo" e "teto",
este é "meta". Agora sustenta pela medição, que é mais difícil de contestar.

---

## Subetapas

### S12.1 · Abrir as alavancas
**DoD:** ✅ prazo e entrada varridos até o limite que o problema permite ·
✅ o limite de prazo documentado (tabela de EAD do professor).

### S12.2 · A varredura
`python/modelagem/12_fronteira_roi_volume.py`.

**DoD:** ✅ 5.600 políticas × 3 cenários · ✅ tabela completa gravada ·
✅ reprodutível por um comando.

### S12.3 · Diagnóstico
**DoD:** ✅ identificado qual guard-rail bloqueia a meta · ✅ efeito isolado de
prazo e entrada medido.

---

## DoD do S12 (o passo inteiro)

- [x] As duas alavancas estreitas do S09 abertas
- [x] Fronteira ROI × volume medida
- [x] O guard-rail que bloqueia a meta identificado, e é só um
- [x] A conclusão registrada no documento de política
- [x] Reprodutível
