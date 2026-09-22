/**
 * Apresentação 1 de 3 — Entregável 1: o modelo de PD.
 *
 * Público: professor e analistas de dados plenos/seniores, poucos com
 * background de banking. Por isso cada conceito de crédito é definido na hora,
 * e as decisões de modelagem são explicadas, não só apresentadas.
 *
 * Gerar:  node apresentacoes/01_modelo_pd.js
 * Saída:  outputs/apresentacoes/01_modelo_pd.pptx  (fora do git, regenerável)
 */

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

// --- Paleta: a identidade da AutoCred, dos slides do professor --------------
const NAVY = "16293A";
const NAVY_MID = "24455E";
const CORAL = "E05A4F";
const CORAL_SOFT = "F7DDDB";
const OFFWHITE = "F2F4F6";
const WHITE = "FFFFFF";
const TEAL = "3D7A8C";
const GREY = "667885";
const GREY_LIGHT = "DDE3E8";
const GREY_ESCURO = "B7C4CE"; // cinza para texto sobre fundo navy

const SERIF = "Cambria";
const SANS = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Leonardo Wink";
pres.title = "AutoCred — Modelo de PD";

const W = 13.3;
const H = 7.5;
const M = 0.7; // margem lateral

/** Título padrão das páginas claras. */
function titulo(slide, texto, subtitulo) {
  slide.addText(texto, {
    x: M, y: 0.45, w: W - 2 * M, h: 0.75,
    fontSize: 34, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  if (subtitulo) {
    slide.addText(subtitulo, {
      x: M, y: 1.18, w: W - 2 * M, h: 0.42,
      fontSize: 15, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  }
}

/** Cartão com tinta de fundo — o motivo visual repetido no deck. */
function cartao(slide, { x, y, w, h, fill = WHITE, linha = GREY_LIGHT }) {
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: fill },
    line: { color: linha, width: 1 },
  });
}

/** Número grande com rótulo — usado nos destaques. */
function numerao(slide, { x, y, w, valor, rotulo, cor = CORAL, tamanho = 44, corRotulo = GREY }) {
  slide.addText(valor, {
    x, y, w, h: 0.85,
    fontSize: tamanho, bold: true, color: cor, fontFace: SERIF,
    align: "center", isTextBox: true, margin: 0,
  });
  slide.addText(rotulo, {
    x, y: y + 0.82, w, h: 0.6,
    fontSize: 12, color: corRotulo, fontFace: SANS,
    align: "center", isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 1 · Capa                                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("DESAFIO AUTOCRED · ENTREGÁVEL 1 DE 2", {
    x: M, y: 1.9, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true,
    isTextBox: true, margin: 0,
  });
  s.addText("O modelo de PD", {
    x: M, y: 2.35, w: W - 2 * M, h: 1.1,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Como construímos a régua que ordena o risco de cada contrato —\nescopo, metodologia e resultados",
    {
      x: M, y: 3.5, w: 8.5, h: 1.0,
      fontSize: 17, color: "B7C4CE", fontFace: SANS, lineSpacing: 26,
      isTextBox: true, margin: 0,
    }
  );

  const stats = [
    { v: "0,7234", r: "AuROC na validação" },
    { v: "0,3660", r: "KS" },
    { v: "3.000", r: "contratos escorados" },
  ];
  stats.forEach((d, i) => {
    numerao(s, { x: M + i * 3.0, y: 5.1, w: 2.6, valor: d.v, rotulo: d.r, cor: WHITE, tamanho: 30, corRotulo: GREY_ESCURO });
  });

  s.addText("Leonardo Wink · setembro de 2026", {
    x: M, y: 6.75, w: 8, h: 0.35,
    fontSize: 11, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Entregável 1 de 2. Esta apresentação cobre só o modelo de PD. A política de crédito e a defesa de negócio têm decks próprios."
  );
}

/* ========================================================================== */
/* 2 · Escopo                                                                  */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Escopo", "O que este entregável é — e o que deliberadamente não é");

  cartao(s, { x: M, y: 1.85, w: 5.9, h: 4.4, fill: WHITE });
  s.addText("ESTÁ NO ESCOPO", {
    x: M + 0.35, y: 2.1, w: 5.2, h: 0.35,
    fontSize: 12, bold: true, color: TEAL, fontFace: SANS, charSpacing: 1.5,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Estimar a PD 90/12 de cada contrato", options: { bullet: true, breakLine: true, bold: true } },
      { text: "a probabilidade de atingir 90 dias de atraso nos 12 meses após a concessão", options: { bullet: false, breakLine: true, fontSize: 13, color: GREY } },
      { text: "Escolher o algoritmo e os hiperparâmetros", options: { bullet: true, breakLine: true, bold: true } },
      { text: "logística, Random Forest e XGBoost, na mesma régua", options: { bullet: false, breakLine: true, fontSize: 13, color: GREY } },
      { text: "Escorar a base B e entregar o CSV", options: { bullet: true, breakLine: true, bold: true } },
      { text: "3.000 contratos de jan–jun/2025, medidos por AuROC", options: { bullet: false, fontSize: 13, color: GREY } },
    ],
    { x: M + 0.35, y: 2.55, w: 5.2, h: 3.5, fontSize: 15, color: NAVY, fontFace: SANS, paraSpaceAfter: 6, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.3, y: 1.85, w: 5.4, h: 4.4, fill: WHITE });
  s.addText("FORA DO ESCOPO", {
    x: M + 6.65, y: 2.1, w: 4.7, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Modelar EAD e LGD", options: { bullet: true, breakLine: true, bold: true } },
      { text: "vêm prontos, em tabela, no material do professor", options: { bullet: false, breakLine: true, fontSize: 13, color: GREY } },
      { text: "Decidir a política de crédito", options: { bullet: true, breakLine: true, bold: true } },
      { text: "a quem conceder, a que preço, em que prazo — é o entregável 2", options: { bullet: false, breakLine: true, fontSize: 13, color: GREY } },
      { text: "Medir o modelo final", options: { bullet: true, breakLine: true, bold: true } },
      { text: "ele foi treinado na base A inteira e não tem conjunto de teste; só o professor pode medi-lo", options: { bullet: false, fontSize: 13, color: GREY } },
    ],
    { x: M + 6.65, y: 2.55, w: 4.7, h: 3.5, fontSize: 15, color: NAVY, fontFace: SANS, paraSpaceAfter: 6, isTextBox: true, margin: 0 }
  );

  s.addText(
    "O modelo não decide nada. Ele ordena risco — quem decide é a política.",
    { x: M, y: 6.5, w: W - 2 * M, h: 0.4, fontSize: 14, italic: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 3 · Glossário rápido                                                        */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Quatro termos, antes de começar", "Para quem não vem de crédito — são os que voltam em todos os slides");

  const termos = [
    { sigla: "PD", nome: "Probability of Default", txt: "A chance de o contrato virar calote. Aqui: 90 dias de atraso nos 12 meses após a concessão." },
    { sigla: "AuROC", nome: "Área sob a curva ROC", txt: "De todos os pares (um bom, um mau), em que fração o modelo deu nota pior ao que quebrou? 0,5 é moeda; crédito bom fica entre 0,65 e 0,78." },
    { sigla: "KS", nome: "Kolmogorov-Smirnov", txt: "Máxima distância entre as acumuladas de bons e maus. A métrica preferida do mercado, porque responde: existe um corte que separa bem?" },
    { sigla: "PSI", nome: "Population Stability Index", txt: "Quanto a população mudou entre duas bases. Não olha o alvo. Acima de 0,25 já é instável." },
  ];

  termos.forEach((t, i) => {
    const y = 1.85 + i * 1.18;
    cartao(s, { x: M, y, w: W - 2 * M, h: 1.0, fill: WHITE });
    s.addShape(pres.ShapeType.ellipse, {
      x: M + 0.25, y: y + 0.19, w: 0.62, h: 0.62, fill: { color: NAVY }, line: { color: NAVY, width: 0 },
    });
    s.addText(t.sigla.slice(0, 3), {
      x: M + 0.25, y: y + 0.32, w: 0.62, h: 0.36,
      fontSize: 11, bold: true, color: WHITE, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(
      [
        { text: t.sigla + "  ", options: { bold: true, fontSize: 16, color: NAVY } },
        { text: t.nome, options: { fontSize: 12, color: CORAL, italic: true } },
      ],
      { x: M + 1.05, y: y + 0.16, w: 4.0, h: 0.35, fontFace: SANS, isTextBox: true, margin: 0 }
    );
    s.addText(t.txt, {
      x: M + 1.05, y: y + 0.5, w: 10.4, h: 0.45,
      fontSize: 13, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
}

/* ========================================================================== */
/* 4 · As três bases                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "As três bases", "Cada uma responde a uma pergunta diferente");

  const bases = [
    { letra: "A", nome: "Desenvolvimento", n: "10.000", per: "2022 – 2024", alvo: "COM alvo", txt: "Onde treinamos e validamos. Traz também EAD e LGD realizados — o gabarito que usamos para conferir os parâmetros.", cor: TEAL },
    { letra: "B", nome: "Teste do modelo", n: "3.000", per: "jan – jun/2025", alvo: "SEM alvo", txt: "O professor guardou o alvo. Entregamos as 3.000 PDs, ele cruza com o gabarito e calcula o AuROC.", cor: CORAL },
    { letra: "C", nome: "Propostas", n: "5.000", per: "jul – dez/2025", alvo: "SEM alvo", txt: "Mar aberto: inclui perfis que a política antiga recusava. É onde a política será aplicada — entregável 2.", cor: GREY },
  ];

  bases.forEach((b, i) => {
    const x = M + i * 4.05;
    cartao(s, { x, y: 1.85, w: 3.75, h: 4.3, fill: WHITE });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.3, y: 2.1, w: 0.7, h: 0.7, fill: { color: b.cor }, line: { color: b.cor, width: 0 },
    });
    s.addText(b.letra, {
      x: x + 0.3, y: 2.24, w: 0.7, h: 0.42,
      fontSize: 20, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(b.nome, {
      x: x + 1.12, y: 2.18, w: 2.5, h: 0.32,
      fontSize: 15, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(b.alvo, {
      x: x + 1.12, y: 2.5, w: 2.5, h: 0.3,
      fontSize: 11, bold: true, color: b.cor, fontFace: SANS, charSpacing: 1, isTextBox: true, margin: 0,
    });
    s.addText(b.n, {
      x: x + 0.3, y: 3.05, w: 3.15, h: 0.6,
      fontSize: 32, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText("contratos · " + b.per, {
      x: x + 0.3, y: 3.65, w: 3.15, h: 0.3,
      fontSize: 11, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(b.txt, {
      x: x + 0.3, y: 4.1, w: 3.15, h: 1.8,
      fontSize: 12.5, color: NAVY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  s.addText(
    "As bases A e B só contêm contratos APROVADOS pela política antiga. A base C é mar aberto — o descasamento tem nome: inferência de rejeitados.",
    { x: M, y: 6.45, w: W - 2 * M, h: 0.5, fontSize: 13, italic: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 5 · A armadilha (slide escuro)                                              */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("A PRIMEIRA DECISÃO FOI O QUE NÃO USAR", {
    x: M, y: 0.75, w: W - 2 * M, h: 0.35,
    fontSize: 12, color: CORAL, fontFace: SANS, bold: true, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("A armadilha da base", {
    x: M, y: 1.15, w: 7.5, h: 0.8,
    fontSize: 38, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  s.addText("qtd_parcelas_em_atraso_12m", {
    x: M, y: 2.1, w: 6.6, h: 0.45,
    fontSize: 19, bold: true, color: CORAL, fontFace: "Courier New", isTextBox: true, margin: 0,
  });
  s.addText(
    "O dicionário marca a coluna como «não disponível na concessão» — ela é apurada DEPOIS, ao longo da janela de performance. Mas ela está presente nas três bases.",
    { x: M, y: 2.6, w: 6.6, h: 1.0, fontSize: 15, color: "B7C4CE", fontFace: SANS, lineSpacing: 22, isTextBox: true, margin: 0 }
  );

  const passos = [
    "Quem não lê o dicionário inclui a variável — ela domina o modelo",
    "O AuROC na validação fica excelente: a validação também sai da base A",
    "Na base B, a coluna vale ZERO para os 3.000 contratos",
    "O termo dominante vira constante e o modelo colapsa",
    "AuROC na avaliação ≈ 0,50 — e os 30 pontos vão embora",
  ];
  passos.forEach((t, i) => {
    const y = 3.75 + i * 0.58;
    s.addText(String(i + 1), {
      x: M, y, w: 0.35, h: 0.35,
      fontSize: 13, bold: true, color: CORAL, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(t, {
      x: M + 0.42, y, w: 6.3, h: 0.45,
      fontSize: 13, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: 7.9, y: 2.1, w: 4.7, h: 3.5, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("O QUE OS DADOS MOSTRAM", {
    x: 8.25, y: 2.35, w: 4.0, h: 0.3,
    fontSize: 11, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  numerao(s, { x: 8.25, y: 2.8, w: 4.0, valor: "0,74", rotulo: "correlação com o alvo na base A", cor: WHITE, tamanho: 46, corRotulo: GREY_ESCURO });
  numerao(s, { x: 8.25, y: 4.25, w: 4.0, valor: "0,00", rotulo: "valor em TODAS as linhas das bases B e C", cor: CORAL, tamanho: 46, corRotulo: GREY_ESCURO });

  s.addText(
    "Nenhum passo levanta exceção. O código roda, o modelo treina, o CSV sai bonito.",
    { x: M, y: 6.75, w: W - 2 * M, h: 0.4, fontSize: 14, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addNotes(
    "Este é o ponto em que a maioria dos grupos provavelmente perde os 30 pontos do AuROC. Removemos a coluna na ingestão, não na hora de treinar, e há um teste dedicado que falha se ela escapar."
  );
}

/* ========================================================================== */
/* 6 · Metodologia: split temporal                                             */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Metodologia · o split", "Fixado antes de qualquer modelo ser treinado");

  const blocos = [
    { x: M, w: 4.3, cor: TEAL, t: "TREINO", p: "2022 – 2023", n: "6.670 contratos", d: "587 defaults · 8,80%" },
    { x: M + 4.55, w: 3.3, cor: CORAL, t: "VALIDAÇÃO", p: "2024", n: "3.330 contratos", d: "239 defaults · 7,18%" },
    { x: M + 8.1, w: 3.8, cor: GREY, t: "BASE B", p: "jan – jun/2025", n: "3.000 contratos", d: "o professor mede aqui" },
  ];
  blocos.forEach((b) => {
    cartao(s, { x: b.x, y: 1.9, w: b.w, h: 1.85, fill: WHITE });
    s.addText(b.t, {
      x: b.x + 0.3, y: 2.12, w: b.w - 0.6, h: 0.3,
      fontSize: 11, bold: true, color: b.cor, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
    });
    s.addText(b.p, {
      x: b.x + 0.3, y: 2.42, w: b.w - 0.6, h: 0.45,
      fontSize: 22, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(b.n, {
      x: b.x + 0.3, y: 2.92, w: b.w - 0.6, h: 0.28,
      fontSize: 13, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(b.d, {
      x: b.x + 0.3, y: 3.2, w: b.w - 0.6, h: 0.28,
      fontSize: 11.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
  [M + 4.35, M + 7.9].forEach((x) => {
    s.addText("→", { x, y: 2.5, w: 0.25, h: 0.4, fontSize: 18, color: GREY, fontFace: SANS, align: "center", isTextBox: true, margin: 0 });
  });

  cartao(s, { x: M, y: 4.1, w: 5.75, h: 2.25, fill: WHITE });
  s.addText("Por que temporal, e não aleatório", {
    x: M + 0.3, y: 4.35, w: 5.15, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Embaralhar os anos deixa o modelo aprender com contratos de 2024 para prever 2022 — o que nunca acontece na vida real. Como a avaliação é out-of-time, a validação precisa imitar essa condição.",
    { x: M + 0.3, y: 4.75, w: 5.15, h: 1.4, fontSize: 13.5, color: GREY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 4.1, w: 5.75, h: 2.25, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("Por que fixar ANTES", {
    x: M + 6.45, y: 4.35, w: 5.15, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Quem testa vários splits e fica com o melhor AuROC não escolheu o melhor modelo: escolheu o split mais sortudo. E sorte não se repete na base B, que é onde a nota acontece.",
    { x: M + 6.45, y: 4.75, w: 5.15, h: 1.4, fontSize: 13.5, color: NAVY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  s.addNotes(
    "A prevalência difere entre treino (8,80%) e validação (7,18%). Por isso comparamos modelos por AuROC e KS, que medem ordenação, e não por acurácia, que depende da prevalência."
  );
}

/* ========================================================================== */
/* 7 · Metodologia: o Pipeline                                                 */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Metodologia · o Pipeline", "Anti-vazamento por construção, não por disciplina");

  cartao(s, { x: M, y: 1.85, w: 6.6, h: 2.0, fill: WHITE });
  s.addText("O problema", {
    x: M + 0.3, y: 2.08, w: 6.0, h: 0.32,
    fontSize: 15, bold: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "A imputação aprende uma mediana. Se ela for calculada sobre treino + validação juntos, a validação influenciou o treino — e o AuROC medido fica otimista, sem nenhum erro aparecer.",
    { x: M + 0.3, y: 2.45, w: 6.0, h: 1.25, fontSize: 14, color: NAVY, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.05, w: 6.6, h: 2.3, fill: WHITE });
  s.addText("A solução", {
    x: M + 0.3, y: 4.28, w: 6.0, h: 0.32,
    fontSize: 15, bold: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Todo o pré-processamento dentro de um Pipeline do scikit-learn. O fit acontece só no treino por construção — a garantia deixa de depender de alguém lembrar.",
    { x: M + 0.3, y: 4.65, w: 6.0, h: 1.0, fontSize: 14, color: NAVY, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );
  s.addText("É item explícito da rubrica: 10 pontos de qualidade técnica.", {
    x: M + 0.3, y: 5.75, w: 6.0, h: 0.35,
    fontSize: 13, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });

  const etapas = [
    { t: "Numéricas · imputação pela mediana", d: "+ INDICADOR DE AUSÊNCIA: quem não tem score de bureau quebra 10,1% contra 8,8%. A ausência é informação de risco, não ruído." },
    { t: "Numéricas · padronização", d: "A logística é sensível à escala dos coeficientes." },
    { t: "Categóricas · moda + one-hot", d: "com handle_unknown=ignore: categoria nova na base C não pode derrubar a escoragem no dia da entrega." },
    { t: "Estimador final", d: "É a única coisa que muda entre os três modelos comparados — o que torna a comparação legítima." },
  ];
  etapas.forEach((e, i) => {
    const y = 1.85 + i * 1.15;
    cartao(s, { x: M + 6.95, y, w: 4.95, h: 1.0, fill: WHITE });
    s.addText(String(i + 1), {
      x: M + 7.15, y: y + 0.2, w: 0.3, h: 0.3,
      fontSize: 13, bold: true, color: CORAL, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(e.t, {
      x: M + 7.5, y: y + 0.16, w: 4.25, h: 0.3,
      fontSize: 12.5, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(e.d, {
      x: M + 7.5, y: y + 0.44, w: 4.25, h: 0.5,
      fontSize: 10.5, color: GREY, fontFace: SANS, lineSpacing: 13, isTextBox: true, margin: 0,
    });
  });
}

/* ========================================================================== */
/* 8 · Os três modelos                                                         */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Os três candidatos", "O que cada um faz, e por que cada um estava na disputa");

  const modelos = [
    {
      nome: "Regressão logística",
      tipo: "O BASELINE",
      cor: TEAL,
      como: "Soma ponderada das variáveis, passada por uma curva em S que devolve probabilidade.",
      pro: "Explicável coeficiente a coeficiente. É o padrão do mercado de crédito justamente por isso: dá para justificar variável a variável.",
      contra: "Só enxerga relação linear. Não captura interação — «LTV alto É pior quando o carro é velho» passa despercebido.",
    },
    {
      nome: "Random Forest",
      tipo: "DESAFIANTE 1",
      cor: CORAL,
      como: "Centenas de árvores de decisão, cada uma treinada num pedaço diferente do dado. A previsão é a média dos votos.",
      pro: "Captura interação e não-linearidade sem ajuste fino. Robusto a valor extremo.",
      contra: "A média dos votos não é uma probabilidade calibrada. E a explicação vira «importância de variável», mais fraca que um coeficiente.",
    },
    {
      nome: "XGBoost",
      tipo: "DESAFIANTE 2",
      cor: NAVY,
      como: "Árvores em sequência: cada nova árvore aprende a corrigir o erro que as anteriores deixaram (gradient boosting).",
      pro: "Costuma ser o melhor em dado tabular. Aprende padrões sutis que a soma linear não alcança.",
      contra: "Sobreajusta com facilidade — decora o treino. Com 587 defaults, exige regularização deliberada.",
    },
  ];

  modelos.forEach((m, i) => {
    const x = M + i * 4.05;
    cartao(s, { x, y: 1.8, w: 3.75, h: 4.55, fill: WHITE });
    s.addText(m.tipo, {
      x: x + 0.3, y: 2.02, w: 3.15, h: 0.28,
      fontSize: 10, bold: true, color: m.cor, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
    });
    s.addText(m.nome, {
      x: x + 0.3, y: 2.3, w: 3.15, h: 0.45,
      fontSize: 19, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText("COMO FUNCIONA", {
      x: x + 0.3, y: 2.85, w: 3.15, h: 0.25,
      fontSize: 9.5, bold: true, color: GREY, fontFace: SANS, charSpacing: 1, isTextBox: true, margin: 0,
    });
    s.addText(m.como, {
      x: x + 0.3, y: 3.1, w: 3.15, h: 0.95,
      fontSize: 11.5, color: NAVY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0,
    });
    s.addText("A FAVOR", {
      x: x + 0.3, y: 4.05, w: 3.15, h: 0.25,
      fontSize: 9.5, bold: true, color: TEAL, fontFace: SANS, charSpacing: 1, isTextBox: true, margin: 0,
    });
    s.addText(m.pro, {
      x: x + 0.3, y: 4.3, w: 3.15, h: 0.95,
      fontSize: 11.5, color: NAVY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0,
    });
    s.addText("O CUSTO", {
      x: x + 0.3, y: 5.25, w: 3.15, h: 0.25,
      fontSize: 9.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1, isTextBox: true, margin: 0,
    });
    s.addText(m.contra, {
      x: x + 0.3, y: 5.5, w: 3.15, h: 0.8,
      fontSize: 11.5, color: NAVY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });

  s.addNotes(
    "Os três rodaram com o MESMO pré-processamento, o MESMO split e a MESMA semente. Só o estimador final mudou — sem isso, não saberíamos a que atribuir a diferença de AuROC."
  );
}

/* ========================================================================== */
/* 9 · A busca de hiperparâmetros                                              */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Como escolhemos os hiperparâmetros", "A validação 2024 não participou da busca");

  cartao(s, { x: M, y: 1.85, w: 7.0, h: 2.5, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("A tentação que evitamos", {
    x: M + 0.35, y: 2.1, w: 6.3, h: 0.35,
    fontSize: 17, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Testar 12 configurações na validação e ficar com a melhor. O número que sobra não seria performance — seria o máximo de 12 sorteios. E esse máximo não se repete na base B.",
    { x: M + 0.35, y: 2.55, w: 6.3, h: 1.6, fontSize: 15, color: NAVY, fontFace: SANS, lineSpacing: 22, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.55, w: 7.0, h: 1.8, fill: WHITE });
  s.addText("O que fizemos", {
    x: M + 0.35, y: 4.78, w: 6.3, h: 0.35,
    fontSize: 17, bold: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Validação cruzada temporal em 3 dobras, dentro do treino. A validação 2024 foi tocada UMA única vez, no fim, com a configuração já escolhida.",
    { x: M + 0.35, y: 5.2, w: 6.3, h: 1.0, fontSize: 15, color: NAVY, fontFace: SANS, lineSpacing: 22, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 7.45, y: 1.85, w: 4.45, h: 4.5, fill: NAVY, linha: NAVY });
  s.addText("CONFIGURAÇÃO VENCEDORA", {
    x: M + 7.75, y: 2.1, w: 3.85, h: 0.3,
    fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText("XGBoost", {
    x: M + 7.75, y: 2.42, w: 3.85, h: 0.5,
    fontSize: 26, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  const params = [
    ["max_depth", "4"],
    ["learning_rate", "0,05"],
    ["min_child_weight", "20"],
    ["n_estimators", "300"],
    ["subsample", "0,8"],
  ];
  params.forEach((p, i) => {
    const y = 3.15 + i * 0.44;
    s.addText(p[0], {
      x: M + 7.75, y, w: 2.5, h: 0.35,
      fontSize: 12, color: "B7C4CE", fontFace: "Courier New", isTextBox: true, margin: 0,
    });
    s.addText(p[1], {
      x: M + 10.25, y, w: 1.35, h: 0.35,
      fontSize: 12, bold: true, color: WHITE, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
    });
  });
  s.addText("Árvores rasas e regularizadas: com 587 defaults no treino, profundidade vira decoreba.", {
    x: M + 7.75, y: 5.5, w: 3.85, h: 0.7,
    fontSize: 11, italic: true, color: "B7C4CE", fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 10 · Resultados                                                             */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Resultados", "Validação 2024 — medida uma única vez, com a configuração já escolhida");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "AuROC na CV (dentro do treino)", labels: ["Logística", "Random Forest", "XGBoost"], values: [0.6391, 0.6915, 0.6948] },
      { name: "AuROC na validação 2024", labels: ["Logística", "Random Forest", "XGBoost"], values: [0.6489, 0.7159, 0.7234] },
    ],
    {
      x: M, y: 1.85, w: 6.5, h: 4.4,
      barDir: "col",
      chartColors: [GREY, CORAL],
      showTitle: true, title: "Poder de ordenação (AuROC)", titleFontSize: 14, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000",
      dataLabelFontSize: 10, dataLabelColor: NAVY, dataLabelFontFace: SANS,
      valAxisMinVal: 0.5, valAxisMaxVal: 0.78,
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valGridLine: { color: GREY_LIGHT, size: 1 },
      catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: NAVY, legendFontFace: SANS,
    }
  );

  cartao(s, { x: M + 6.95, y: 1.85, w: 4.95, h: 4.4, fill: WHITE });
  s.addText("A TABELA COMPLETA", {
    x: M + 7.25, y: 2.08, w: 4.35, h: 0.3,
    fontSize: 10.5, bold: true, color: GREY, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });

  const linhas = [
    ["", "AuROC", "KS", "Brier"],
    ["Logística", "0,6489", "0,2432", "0,0648"],
    ["Random Forest", "0,7159", "0,3390", "0,1888"],
    ["XGBoost", "0,7234", "0,3660", "0,0621"],
  ];
  linhas.forEach((linha, i) => {
    const y = 2.48 + i * 0.48;
    const ehCabecalho = i === 0;
    const ehVencedor = i === 3;
    if (ehVencedor) {
      s.addShape(pres.ShapeType.roundRect, {
        x: M + 7.15, y: y - 0.06, w: 4.55, h: 0.46, rectRadius: 0.05,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((celula, j) => {
      s.addText(celula, {
        x: M + 7.25 + j * 1.13, y, w: j === 0 ? 1.4 : 1.0, h: 0.35,
        fontSize: ehCabecalho ? 10.5 : 12.5,
        bold: ehCabecalho || ehVencedor || j === 0,
        color: ehCabecalho ? GREY : NAVY,
        fontFace: SANS, align: j === 0 ? "left" : "right",
        isTextBox: true, margin: 0,
      });
    });
  });

  s.addText(
    [
      { text: "XGBoost vence nas DUAS medidas.  ", options: { bold: true, color: NAVY } },
      { text: "Ganhar na CV interna e na validação afasta a hipótese de sorte em um conjunto só.", options: { color: GREY } },
    ],
    { x: M + 7.25, y: 4.55, w: 4.35, h: 0.9, fontSize: 12.5, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0 }
  );
  s.addText(
    [
      { text: "Brier", options: { bold: true, color: NAVY } },
      { text: " mede calibração, não ordenação: o quanto a probabilidade prevista acerta o nível. Menor é melhor.", options: { color: GREY } },
    ],
    { x: M + 7.25, y: 5.4, w: 4.35, h: 0.8, fontSize: 12, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 11 · O caso do Random Forest                                                */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Por que o Random Forest foi descartado", "AuROC alto e modelo inútil podem conviver");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "PD média prevista", labels: ["Logística", "Random Forest", "XGBoost"], values: [0.0869, 0.423, 0.0851] },
      { name: "Taxa de default real", labels: ["Logística", "Random Forest", "XGBoost"], values: [0.0718, 0.0718, 0.0718] },
    ],
    {
      x: M, y: 1.9, w: 6.3, h: 4.3,
      barDir: "col",
      chartColors: [CORAL, NAVY],
      showTitle: true, title: "Calibração: a PD prevista bate com a realidade?", titleFontSize: 13, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0%",
      dataLabelFontSize: 10, dataLabelColor: NAVY, dataLabelFontFace: SANS,
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valAxisLabelFormatCode: "0%",
      valGridLine: { color: GREY_LIGHT, size: 1 },
      catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: NAVY, legendFontFace: SANS,
    }
  );

  cartao(s, { x: M + 6.75, y: 1.9, w: 5.15, h: 2.1, fill: NAVY, linha: NAVY });
  numerao(s, { x: M + 7.0, y: 2.15, w: 4.65, valor: "6×", rotulo: "a PD do Random Forest ficou seis vezes acima da taxa real", cor: CORAL, tamanho: 42, corRotulo: GREY_ESCURO });

  cartao(s, { x: M + 6.75, y: 4.2, w: 5.15, h: 2.0, fill: WHITE });
  s.addText("A causa: class_weight = balanced", {
    x: M + 7.05, y: 4.42, w: 4.55, h: 0.32,
    fontSize: 14, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      {
        text: "A busca escolheu essa opção porque ela melhora a ordenação. Mas reponderar as classes empurra a probabilidade para perto de 0,5.",
        options: { color: GREY, breakLine: true },
      },
      { text: " ", options: { breakLine: true, fontSize: 6 } },
      {
        text: "Para ORDENAR, não atrapalha. Para PRECIFICAR, inviabiliza.",
        options: { color: NAVY, bold: true },
      },
    ],
    { x: M + 7.05, y: 4.8, w: 4.55, h: 1.3, fontSize: 12.5, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0 }
  );

  s.addText(
    "A perda esperada é PD × EAD × LGD. Com a PD seis vezes maior, o preço sairia absurdo e a política inteira quebraria.",
    { x: M, y: 6.5, w: W - 2 * M, h: 0.45, fontSize: 13.5, italic: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addNotes(
    "Este é o slide que mostra por que o Brier entrou na decisão, e não só o AuROC. Se a escolha fosse por poder de ordenação apenas, o Random Forest estaria tecnicamente empatado com o XGBoost."
  );
}

/* ========================================================================== */
/* 12 · O que não sabemos (limitações)                                         */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O que este modelo não resolve", "Limitações reconhecidas, medidas quando possível");

  const lim = [
    {
      t: "A base C é outra população",
      n: "PSI 5,93",
      d: "As bases A e B só têm contratos aprovados pela política antiga; a C é mar aberto. E o desalinhamento está justamente nas duas variáveis mais preditivas: qtd_restricoes_ativas (PSI 5,93) e score_bureau (0,50).",
      c: CORAL,
    },
    {
      t: "Ordenação sobrevive, nível não",
      n: "risco de preço",
      d: "A ordenação tende a resistir à mudança de população; o nível da PD, não. Em mar aberto o modelo provavelmente SUBESTIMA o risco de quem a política velha recusava — e é o nível que vira preço.",
      c: CORAL,
    },
    {
      t: "Sem tratamento de rejeitados",
      n: "por prazo",
      d: "O tratamento formal (reject inference) não entrou nesta entrega. Mitigação: tratar a PD como ordenação confiável e nível suspeito, com margem de segurança no preço das faixas baixas.",
      c: GREY,
    },
    {
      t: "Folga treino-validação de 0,147",
      n: "0,87 → 0,72",
      d: "O XGBoost marca 0,8701 no treino e 0,7234 na validação. O número honesto é o da validação, e a CV foi ainda mais conservadora (0,6948). Nossa expectativa para a base B é 0,69–0,72, não 0,87.",
      c: GREY,
    },
  ];

  lim.forEach((l, i) => {
    const x = M + (i % 2) * 6.0;
    const y = 1.85 + Math.floor(i / 2) * 2.35;
    cartao(s, { x, y, w: 5.7, h: 2.1, fill: WHITE });
    s.addText(l.t, {
      x: x + 0.3, y: y + 0.22, w: 3.6, h: 0.35,
      fontSize: 15, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(l.n, {
      x: x + 3.95, y: y + 0.24, w: 1.5, h: 0.32,
      fontSize: 13, bold: true, color: l.c, fontFace: SERIF, align: "right", isTextBox: true, margin: 0,
    });
    s.addText(l.d, {
      x: x + 0.3, y: y + 0.65, w: 5.1, h: 1.3,
      fontSize: 12, color: GREY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0,
    });
  });

  s.addText(
    "Reconhecer a limitação com precisão é parte do trabalho: nomear o risco permite precificá-lo.",
    { x: M, y: 6.6, w: W - 2 * M, h: 0.4, fontSize: 13.5, italic: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 13 · O entregável                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O ENTREGÁVEL", {
    x: M, y: 0.85, w: 6, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("submissao_modelo.csv", {
    x: M, y: 1.25, w: 8, h: 0.75,
    fontSize: 36, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M, y: 2.35, w: 5.5, h: 2.35, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("id_contrato,pd\nT000001,0.034359\nT000002,0.054537\nT000003,0.089824", {
    x: M + 0.35, y: 2.6, w: 4.8, h: 1.4,
    fontSize: 14, color: WHITE, fontFace: "Courier New", lineSpacing: 22, isTextBox: true, margin: 0,
  });
  s.addText("3.000 linhas · PD média 0,0788 · 3.000 valores distintos", {
    x: M + 0.35, y: 4.15, w: 4.8, h: 0.35,
    fontSize: 11.5, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  const checks = [
    "3.000 linhas, ids idênticos aos da base B",
    "Sem duplicados, sem nulos, PD dentro de [0, 1]",
    "Distribuição não degenerada — a última barreira contra a armadilha",
    "6 casas decimais: arredondar demais cria empate e derruba o AuROC",
    "Reprodutível: duas execuções, arquivo idêntico",
  ];
  s.addText("O VALIDADOR CONFERE, ANTES DO ENVIO", {
    x: M + 6.0, y: 2.35, w: 6.0, h: 0.3,
    fontSize: 11, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  checks.forEach((c, i) => {
    const y = 2.78 + i * 0.5;
    s.addShape(pres.ShapeType.ellipse, {
      x: M + 6.0, y: y + 0.07, w: 0.2, h: 0.2, fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(c, {
      x: M + 6.35, y, w: 5.6, h: 0.42,
      fontSize: 13, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  s.addText("Erro de formato custa os 30 pontos inteiros, e só aparece quando já não dá para corrigir.", {
    x: M, y: 5.35, w: W - 2 * M, h: 0.4,
    fontSize: 13, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M, y: 5.95, w: 11.9, h: 0.95, fill: NAVY_MID, linha: NAVY_MID });
  s.addText(
    [
      { text: "Próximo entregável:  ", options: { color: "B7C4CE" } },
      { text: "a política de crédito", options: { bold: true, color: WHITE } },
      { text: "  —  transformar esta régua em decisão: a quem conceder, a que preço, em que prazo, com quanta entrada.", options: { color: "B7C4CE" } },
    ],
    { x: M + 0.35, y: 6.2, w: 11.2, h: 0.5, fontSize: 14, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
pres.writeFile({ fileName: path.join(destino, "01_modelo_pd.pptx") }).then((f) => {
  console.log("Gerado:", f);
});
