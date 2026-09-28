# S11 · Documento de política e defesa

> Passo 11 de 11 do [`ROADMAP.md`](../processo/ROADMAP.md). Depende do S10. **→ Fecha o entregável 2.**
>
> ✅ **CONCLUÍDO em 2026-09-23** — 3 páginas, dentro do limite do professor, 167 testes verdes.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S11.1 | Preenchimento do template do professor | 3/3 | ✅ | — |
| S11.2 | Números do pipeline, nada digitado à mão | 3/3 | ✅ | — |
| S11.3 | O confronto com a meta de 15% de ROI | 3/3 | ✅ | — |
| S11.4 | Caber em 2–3 páginas | 3/3 | ✅ | — |
| S11.5 | Conferência visual renderizada | 3/3 | ✅ | — |

## Objetivo

`documento_politica_AutoCred.docx` — o texto que acompanha o CSV e sustenta as
decisões diante do professor.

## 🔑 Preencher o template, não escrever um documento novo

O professor mandou um `.docx` com oito seções e cinco tabelas. Havia dois
caminhos:

| | Como | Por que não / por que sim |
| - | ---- | ------------------------- |
| Gerar do zero | montar um documento novo com a mesma estrutura | corre-se o risco de divergir do que ele espera encontrar, e a formatação dele se perde |
| **Preencher no lugar** | abrir o template e trocar o texto dos parágrafos-guia | **mantém estilo, numeração e tabelas exatamente como ele montou** |

Escolhemos preencher. `_escrever()` troca o texto do **primeiro run** do
parágrafo em vez de atribuir `paragrafo.text`, porque a atribuição direta
descartaria os runs e, com eles, a formatação do template.

## Nenhum número digitado à mão

Todo valor do documento vem do pipeline no momento da geração: o modelo é
retreinado, a base C é escorada, a política é reconstruída e o motor de ROI roda
os três cenários. Rodar de novo depois de mexer em qualquer parâmetro produz um
documento coerente sozinho — não há um segundo lugar onde o número possa
envelhecer.

Os percentuais saem por `pct()` e `num()`, que formatam no padrão brasileiro. A
primeira versão misturava "59.5%" com "1,57%" na mesma frase, porque os
f-strings usavam ponto e o texto fixo usava vírgula.

## 🔑 O único indicador que não batemos — e por que isso está escrito

A tabela de indicadores do template tem cinco linhas. Projetamos:

| Indicador | Projeção | Limite do professor | |
| --------- | -------- | ------------------- | - |
| Taxa de aprovação | 59,5% | mínimo de 35% | ✅ |
| Volume originado | R$ 66,7 mi | mínimo de R$ 40 mi | ✅ |
| Inadimplência | 6,3% | máximo de 8% | ✅ |
| Taxa média ao mês | 1,91% | teto de 3,5% | ✅ |
| **ROI anualizado** | **11,3%** | **meta acima de 15%** | ❌ |

Medimos a fronteira antes de escrever qualquer coisa. A primeira versão deste
documento usou a varredura do S09 (960 políticas); depois o [S12](S12_FRONTEIRA_ROI_VOLUME.md)
refez a conta com a grade aberta, e **é o número do S12 que está no documento
entregue**:

- **4.044 das 5.600 políticas batem 15% de ROI. Nenhuma é viável.** A de maior
  volume entre elas origina R$ 20,5 milhões — metade do mínimo exigido.
- **Só o volume as bloqueia.** Inadimplência (mínimo de 5,26%) e aprovação
  (máximo de 68,7%) passam folgado.
- **O melhor ROI compatível com os quatro guard-rails é 11,46%**, e a nossa
  política entrega 11,33%.

> ⚠️ **Um número foi corrigido aqui.** A redação anterior dizia "com volume
> acima de R$ 40 milhões, o teto é 11,9%". Aquele 11,86% saiu de um filtro só
> por volume, sem exigir os demais guard-rails nos três cenários — não era um
> teto viável. O teto viável é 11,46%. Citar 11,9% no documento e 11,46% na
> defesa teria virado pergunta na banca.

Ou seja: **sob as nossas premissas de elasticidade, a meta de 15% e o piso de
R$ 40 milhões são incompatíveis.** O documento declara isso em vez de omitir.

O argumento de que a meta é alvo e não limite está na escolha de palavras do
próprio enunciado — os outros quatro são "mínimo", "máximo" e "teto"; este é
"meta". E a saída fica registrada: se o simulador do professor for menos
elástico do que supusemos, a fronteira inteira sobe e 15% volta ao alcance sem
violar nada. Ver o item 4 do [`DEBITO_TECNICO.md`](../processo/DEBITO_TECNICO.md).

## Caber em três páginas

O template pede de 2 a 3 páginas; a primeira versão saiu com 4. O princípio que
guiou o corte: **onde o texto corrido repetia uma linha de tabela, ficou a
tabela.** Três parágrafos saíram inteiros por isso — o de estratégia de
validação (seção 2), e os de taxa por faixa e de entrada mínima (seção 5), todos
duplicatas do que a tabela ao lado já dizia.

O resto veio de espaçamento, não de conteúdo: os títulos vinham com 18 pt de
respiro antes e 8 depois, e oito seções custavam quase meia página só nisso.
Ficaram 8 e 4.

Dois detalhes do Word que custaram uma página cada e só apareceram no render:

- **Parágrafos vazios do template** entre as seções — invisíveis na leitura do
  XML, quase uma página somados.
- **O parágrafo obrigatório depois da última tabela.** Sem escrevê-lo, o Word
  inventa um de 11 pt ao abrir o arquivo; como a tabela terminava rente à margem
  da página 3, isso sozinho gerava uma quarta página em branco. Escrevemos um de
  1 pt com espaçamento zero.

## A conferência é visual, não programática

Contar caracteres não diz quantas páginas o Word vai gerar. O documento é
convertido para PDF via COM do Word — o mesmo motor que o professor vai usar — e
depois para PNG, e as páginas são olhadas uma a uma.

Foi só assim que apareceram: o "XGBOOST" em caixa alta, o separador decimal
misturado, o título da seção 3 órfão no pé da página 1, e o parágrafo encostado
na borda da tabela.

---

## Subetapas

### S11.1 · Preenchimento do template
`python/relatorios/11_documento_politica.py`.

**DoD:** ✅ as oito seções preenchidas · ✅ as cinco tabelas preenchidas ·
✅ formatação do professor preservada.

### S11.2 · Números do pipeline
**DoD:** ✅ nenhum valor digitado à mão · ✅ regenerar reflete mudança de
parâmetro · ✅ formato numérico brasileiro em todo o documento.

### S11.3 · O confronto com a meta
**DoD:** ✅ fronteira ROI × volume medida na varredura do S09 · ✅ a lacuna
declarada no documento, com número · ✅ a condição de reversão registrada.

### S11.4 · Três páginas
**DoD:** ✅ dentro do limite de 2–3 · ✅ nenhum argumento perdido no corte ·
✅ sem página em branco no fim.

### S11.5 · Conferência visual
**DoD:** ✅ renderizado pelo Word · ✅ as três páginas inspecionadas · ✅ sem
título órfão nem texto colado.

---

## DoD do S11 (o passo inteiro)

- [x] `documento_politica_AutoCred.docx` gerado a partir do template do professor
- [x] Todos os números vindos do pipeline
- [x] O indicador que não batemos declarado, com a medição que sustenta a escolha
- [x] 3 páginas, dentro do limite
- [x] Conferido visualmente no render do Word
- [x] Reprodutível por um comando
- [x] `pytest` verde

## O que fica pendente

- **Nomes dos integrantes** de Modelagem (PD) e Negócio e defesa. O script avisa
  em cada execução enquanto estiverem "a definir".
- **O e-mail de entrega** e o documento *"AutoCred — Regras da Competição"*,
  ambos a confirmar com o professor.
