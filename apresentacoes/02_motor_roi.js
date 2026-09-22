/**
 * Apresentação 2 — O motor de simulação do ROI (S08).
 *
 * Público: professor e analistas de dados plenos/seniores, poucos com
 * background de banking.
 *
 * O arco: não temos simulador e só submetemos uma vez → construímos o nosso,
 * peça por peça da fórmula oficial → validamos contra o dado → e o dado revelou
 * por que a AutoCred quebrou.
 *
 * Gerar:  node apresentacoes/02_motor_roi.js
 */

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const C = require("./_comum");

const {
  NAVY, NAVY_MID, CORAL, CORAL_SOFT, OFFWHITE, WHITE, TEAL, GREY, GREY_LIGHT, GREY_ESCURO,
  SERIF, SANS, W, M, titulo, numerao, fecho,
} = C;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Leonardo Wink";
pres.title = "AutoCred — Motor de ROI";

const cartao = (slide, opts) => C.cartao(pres, slide, opts);

/* ========================================================================== */
/* 1 · Capa                                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("DESAFIO AUTOCRED · A POLÍTICA DE CRÉDITO", {
    x: M, y: 1.9, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true, isTextBox: true, margin: 0,
  });
  s.addText("O motor de ROI", {
    x: M, y: 2.35, w: W - 2 * M, h: 1.1,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Construir o simulador que não recebemos — e o que o dado\nrevelou sobre por que a AutoCred estava perdendo dinheiro",
    { x: M, y: 3.5, w: 9.0, h: 1.0, fontSize: 17, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 26, isTextBox: true, margin: 0 }
  );

  [
    { v: "0,0003%", r: "erro da Tabela Price\ncontra a base A" },
    { v: "+0,125", r: "correlação entre taxa\ne risco na política antiga" },
    { v: "3", r: "cenários de aceite,\nporque só submetemos uma vez" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 3.9, y: 5.05, w: 3.5, valor: d.v, rotulo: d.r, cor: WHITE, tamanho: 28, corRotulo: GREY_ESCURO });
  });

  s.addNotes(
    "Este deck cobre o S08 — o motor de simulação. A tabela de política em si (as quatro alavancas por faixa) é o passo seguinte."
  );
}

/* ========================================================================== */
/* 2 · O problema                                                              */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O problema", "Precisamos decidir o preço sem poder testar a decisão");

  cartao(s, { x: M, y: 1.85, w: 7.4, h: 2.3, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("O que o enunciado diz", {
    x: M + 0.35, y: 2.08, w: 6.7, h: 0.35,
    fontSize: 15, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "«A direção de cada efeito está declarada. A intensidade, não — e não há como descobri-la por tentativa e erro, porque vocês só submetem uma vez. O caminho é raciocinar sobre o trade-off, não otimizá-lo às cegas.»",
    { x: M + 0.35, y: 2.5, w: 6.7, h: 1.5, fontSize: 14.5, italic: true, color: NAVY, fontFace: SANS, lineSpacing: 21, isTextBox: true, margin: 0 }
  );

  const consequencias = [
    { t: "Sem feedback", d: "Nenhuma submissão de teste. O primeiro e único número sai no dia 26." },
    { t: "Sem calibração", d: "Não dá para ajustar a política observando o resultado — ele não existe antes da apuração." },
    { t: "Decisão sob premissa", d: "Se não sabemos a intensidade, ela tem de virar premissa explícita — não número escondido no código." },
  ];
  consequencias.forEach((c, i) => {
    const y = 1.85 + i * 1.6;
    cartao(s, { x: M + 7.75, y, w: 4.15, h: 1.4, fill: WHITE });
    s.addText(c.t, {
      x: M + 8.05, y: y + 0.18, w: 3.6, h: 0.3,
      fontSize: 14, bold: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(c.d, {
      x: M + 8.05, y: y + 0.52, w: 3.6, h: 0.75,
      fontSize: 11.5, color: GREY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 4.35, w: 7.4, h: 1.9, fill: NAVY, linha: NAVY });
  s.addText("A saída: construir o nosso", {
    x: M + 0.35, y: 4.58, w: 6.7, h: 0.4,
    fontSize: 20, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Os parâmetros do professor permitem calcular o ROI de qualquer política — desde que se saiba quem aceitou a oferta. Só o aceite vira cenário; o resto é conta.",
    { x: M + 0.35, y: 5.05, w: 6.7, h: 1.05, fontSize: 14, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );

  fecho(s, "O valor do motor não é acertar o número do professor — é comparar políticas sob a mesma premissa.");
}

/* ========================================================================== */
/* 3 · A fórmula, peça por peça                                                */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "A fórmula oficial, peça por peça", "Cada termo precisa vir de algum lugar — e nenhum pode vir de chute");

  cartao(s, { x: M, y: 1.8, w: W - 2 * M, h: 0.85, fill: NAVY, linha: NAVY });
  s.addText("ROI anual  =  [ ( juros recebidos  −  perda realizada )  ÷  volume financiado ]  ÷  prazo médio em anos", {
    x: M + 0.3, y: 2.0, w: W - 2 * M - 0.6, h: 0.45,
    fontSize: 17, bold: true, color: WHITE, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
  });

  const pecas = [
    { t: "Parcela", d: "Tabela Price. Validada contra a base A.", f: "P × i / (1 − (1+i)⁻ⁿ)", cor: TEAL },
    { t: "Juros de quem paga tudo", d: "O total pago menos o principal devolvido.", f: "parcela × n − P", cor: TEAL },
    { t: "Juros de quem quebra", d: "Só a parte de juros das parcelas pagas até o calote.", f: "parcela × m − (P − saldoₘ)", cor: CORAL },
    { t: "Quando ele quebra", d: "Distribuição do mês do default: média 6,9, pico do 5º ao 8º.", f: "tabela do professor", cor: CORAL },
    { t: "Perda realizada", d: "As funções de EAD e LGD validadas no passo anterior.", f: "fator_EAD × P × LGD", cor: CORAL },
    { t: "Volume financiado", d: "Soma dos contratos EFETIVADOS — proposta recusada não existe.", f: "Σ financiado aceito", cor: GREY },
  ];
  pecas.forEach((p, i) => {
    const x = M + (i % 3) * 4.05;
    const y = 2.95 + Math.floor(i / 3) * 1.75;
    cartao(s, { x, y, w: 3.75, h: 1.5, fill: WHITE });
    s.addText(p.t, {
      x: x + 0.28, y: y + 0.18, w: 3.2, h: 0.3,
      fontSize: 13.5, bold: true, color: p.cor, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(p.d, {
      x: x + 0.28, y: y + 0.5, w: 3.2, h: 0.55,
      fontSize: 11, color: GREY, fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
    });
    s.addText(p.f, {
      x: x + 0.28, y: y + 1.08, w: 3.2, h: 0.3,
      fontSize: 11, color: NAVY, fontFace: "Courier New", isTextBox: true, margin: 0,
    });
  });
}

/* ========================================================================== */
/* 4 · A validação da Price                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Antes de confiar no motor, validar a base dele", "A base A traz a parcela calculada pelo professor — dá para conferir");

  cartao(s, { x: M, y: 2.0, w: 5.4, h: 3.0, fill: NAVY, linha: NAVY });
  numerao(s, { x: M + 0.3, y: 2.45, w: 4.8, valor: "0,0003%", rotulo: "erro relativo médio entre a nossa Tabela Price\ne a coluna parcela_mensal dos 10.000 contratos", cor: WHITE, tamanho: 44, corRotulo: GREY_ESCURO });

  cartao(s, { x: M + 5.85, y: 2.0, w: 6.05, h: 3.0, fill: WHITE });
  s.addText("Por que isso importa mais do que parece", {
    x: M + 6.2, y: 2.25, w: 5.4, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Toda a receita do motor sai da parcela.", options: { bold: true, breakLine: true, color: NAVY } },
      { text: "Se a Price estivesse errada, o ROI de qualquer política sairia errado na mesma proporção — e nada denunciaria.", options: { breakLine: true, color: GREY } },
      { text: " ", options: { breakLine: true, fontSize: 8 } },
      { text: "Com o gabarito do professor na mão, a conferência custou uma linha de código e eliminou uma classe inteira de erro silencioso.", options: { color: GREY } },
    ],
    { x: M + 6.2, y: 2.7, w: 5.4, h: 2.1, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );

  fecho(s, "Mesmo padrão do passo anterior: EAD e LGD também foram validados contra os 826 contratos que realmente quebraram.");
}

/* ========================================================================== */
/* 5 · Parcela não é receita                                                   */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "A armadilha da amortização", "Quem quebra no mês 6 pagou seis parcelas — mas parcela não é receita");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "Juros (receita)", labels: ["6 parcelas pagas"], values: [919.6] },
      { name: "Amortização (devolução do principal)", labels: ["6 parcelas pagas"], values: [877.0] },
    ],
    {
      x: M, y: 2.0, w: 6.0, h: 3.6,
      barDir: "col", barGrouping: "stacked",
      chartColors: [CORAL, NAVY],
      showTitle: true, title: "Contrato de R$ 10.000 · 1,59% a.m. · 48 meses",
      titleFontSize: 12, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: 'R$ #,##0',
      dataLabelFontSize: 12, dataLabelColor: WHITE, dataLabelFontFace: SANS,
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 12, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valGridLine: { color: GREY_LIGHT, size: 1 }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: NAVY, legendFontFace: SANS,
    }
  );

  cartao(s, { x: M + 6.45, y: 2.0, w: 5.45, h: 1.55, fill: NAVY, linha: NAVY });
  numerao(s, { x: M + 6.7, y: 2.2, w: 4.95, valor: "51%", rotulo: "da parcela é juros nos primeiros meses — o resto é dinheiro voltando", cor: CORAL, tamanho: 38, corRotulo: GREY_ESCURO });

  cartao(s, { x: M + 6.45, y: 3.75, w: 5.45, h: 1.85, fill: WHITE });
  s.addText("O erro que isso evita", {
    x: M + 6.75, y: 3.98, w: 4.85, h: 0.32,
    fontSize: 15, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Contar a parcela inteira como receita superestimaria o ROI de toda carteira com inadimplência — e quanto pior a carteira, maior o erro. O motor conta só os juros, e apura a perda sobre o saldo que ficou.",
    { x: M + 6.75, y: 4.35, w: 4.85, h: 1.15, fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0 }
  );

  fecho(s, "Eu mesmo errei aqui: assumi que os juros seriam menos de 50% da parcela. São 51% — o teste corrigiu a suposição.");
}

/* ========================================================================== */
/* 6 · O grande achado                                                         */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O QUE A BASE REVELOU", {
    x: M, y: 0.7, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("A política antiga não precificava risco", {
    x: M, y: 1.1, w: 11, h: 0.8,
    fontSize: 38, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  s.addChart(
    pres.ChartType.bar,
    [{ name: "Default real", labels: ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"], values: [0.002, 0.009, 0.015, 0.048, 0.079, 0.114, 0.181, 0.272, 0.352, 0.696] }],
    {
      x: M, y: 2.1, w: 7.3, h: 3.6,
      barDir: "col", chartColors: [CORAL],
      showTitle: true, title: "Inadimplência real por faixa de score (base A)",
      titleFontSize: 12, titleColor: WHITE, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0%",
      dataLabelFontSize: 9, dataLabelColor: WHITE, dataLabelFontFace: SANS,
      catAxisLabelColor: GREY_ESCURO, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY_ESCURO, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valAxisLabelFormatCode: "0%",
      valGridLine: { color: NAVY_MID, size: 1 }, catGridLine: { style: "none" },
      showLegend: false,
    }
  );
  s.addText("← melhor risco                                                     pior risco →", {
    x: M, y: 5.8, w: 7.3, h: 0.3,
    fontSize: 10, color: GREY, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 7.75, y: 2.1, w: 4.15, h: 3.6, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("A TAXA QUE ELA COBRAVA", {
    x: M + 8.05, y: 2.32, w: 3.55, h: 0.3,
    fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  [
    ["score 10", "0,2% de default", "1,57%"],
    ["score 7", "4,8%", "1,59%"],
    ["score 4", "18,1%", "1,61%"],
    ["score 1", "69,6%", "1,64%"],
  ].forEach((linha, i) => {
    const y = 2.75 + i * 0.62;
    s.addText(linha[0], {
      x: M + 8.05, y, w: 1.3, h: 0.28,
      fontSize: 12, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(linha[1], {
      x: M + 8.05, y: y + 0.26, w: 1.9, h: 0.26,
      fontSize: 10, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(linha[2], {
      x: M + 10.0, y: y + 0.02, w: 1.55, h: 0.35,
      fontSize: 17, bold: true, color: CORAL, fontFace: SERIF, align: "right", isTextBox: true, margin: 0,
    });
  });
  s.addText("7 pontos-base separando 0,2% de 69,6%", {
    x: M + 8.05, y: 5.28, w: 3.55, h: 0.35,
    fontSize: 11.5, italic: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });

  s.addText(
    "Correlação entre taxa e PD: +0,125.  O cliente bom pagava pelo risco alheio — e ia para o concorrente. Sobrava o ruim, subsidiado.",
    { x: M, y: 6.3, w: W - 2 * M, h: 0.5, fontSize: 14, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addNotes(
    "Este é o diagnóstico do conselho traduzido em números. 'O problema não está na cobrança, e sim na porta de entrada' — a porta de entrada cobrava o mesmo de todo mundo."
  );
}

/* ========================================================================== */
/* 7 · A consequência: quem limita o preço                                     */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Quem limita o preço não é o regulador", "A descoberta muda qual restrição a política precisa respeitar");

  cartao(s, { x: M, y: 1.95, w: 5.6, h: 2.1, fill: WHITE });
  s.addText("O QUE PARECIA A RESTRIÇÃO", {
    x: M + 0.32, y: 2.18, w: 5.0, h: 0.3,
    fontSize: 10.5, bold: true, color: GREY, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText("Teto de 3,5% ao mês", {
    x: M + 0.32, y: 2.5, w: 5.0, h: 0.45,
    fontSize: 24, bold: true, color: GREY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("O guard-rail de CET do conselho.", {
    x: M + 0.32, y: 3.0, w: 5.0, h: 0.35,
    fontSize: 13, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText("Está 2,2× acima do que o mercado pratica.", {
    x: M + 0.32, y: 3.4, w: 5.0, h: 0.35,
    fontSize: 13, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 6.05, y: 1.95, w: 5.85, h: 2.1, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("O QUE É A RESTRIÇÃO DE VERDADE", {
    x: M + 6.37, y: 2.18, w: 5.2, h: 0.3,
    fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText("O aceite do cliente", {
    x: M + 6.37, y: 2.5, w: 5.2, h: 0.45,
    fontSize: 24, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Ele tem concorrente. Cobrar 3% num mercado de 1,6% não é ilegal — é só não ter esse cliente.",
    { x: M + 6.37, y: 3.0, w: 5.2, h: 0.8, fontSize: 13, color: NAVY, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.35, w: 11.9, h: 1.9, fill: NAVY, linha: NAVY });
  s.addText("A referência de mercado saiu do dado, não de chute", {
    x: M + 0.35, y: 4.6, w: 11.2, h: 0.4,
    fontSize: 18, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "1,59% ao mês", options: { bold: true, color: CORAL } },
      { text: "  é a taxa média que a política antiga praticou nos 10.000 contratos da base A (p05 1,38% · p95 1,80%). É a melhor proxy disponível do preço que o cliente encontra no concorrente — e é sobre ela que o modelo de aceite mede o «excesso».", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.35, y: 5.08, w: 11.2, h: 1.0, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );

  fecho(s, "Precificar acima do mercado é possível — mas cada ponto cobrado a mais compra menos carteira. O motor mede essa troca.");
}

/* ========================================================================== */
/* 8 · Medido × premissa                                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O que é medido e o que é premissa", "A separação precisa ser explícita — senão a premissa vira fato por descuido");

  cartao(s, { x: M, y: 1.85, w: 5.9, h: 4.4, fill: WHITE });
  s.addText("MEDIDO", {
    x: M + 0.35, y: 2.1, w: 5.2, h: 0.32,
    fontSize: 12, bold: true, color: TEAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Parcela e juros", options: { bullet: true, breakLine: true, bold: true } },
      { text: "Tabela Price, validada contra a base A", options: { bullet: false, breakLine: true, fontSize: 12.5, color: GREY } },
      { text: "EAD e LGD", options: { bullet: true, breakLine: true, bold: true } },
      { text: "tabelas do professor, conferidas contra 826 contratos reais", options: { bullet: false, breakLine: true, fontSize: 12.5, color: GREY } },
      { text: "Quando o default acontece", options: { bullet: true, breakLine: true, bold: true } },
      { text: "distribuição do professor: média 6,9 meses", options: { bullet: false, breakLine: true, fontSize: 12.5, color: GREY } },
      { text: "Efeito da entrada sobre a PD", options: { bullet: true, breakLine: true, bold: true } },
      { text: "entrada reduz o LTV, e o LTV é preditora do modelo — então re-escoramos, em vez de supor uma elasticidade", options: { bullet: false, fontSize: 12.5, color: GREY } },
    ],
    { x: M + 0.35, y: 2.55, w: 5.2, h: 3.5, fontSize: 14.5, color: NAVY, fontFace: SANS, paraSpaceAfter: 5, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.3, y: 1.85, w: 5.6, h: 4.4, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("PREMISSA (vira cenário)", {
    x: M + 6.65, y: 2.1, w: 4.9, h: 0.32,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Quanto o aceite cai com a taxa", options: { bullet: true, breakLine: true, bold: true } },
      { text: "a direção o professor declara; a intensidade, não", options: { bullet: false, breakLine: true, fontSize: 12.5, color: GREY } },
      { text: "Quanto cai com a entrada exigida", options: { bullet: true, breakLine: true, bold: true } },
      { text: "e com o encurtamento do prazo pedido", options: { bullet: false, breakLine: true, fontSize: 12.5, color: GREY } },
      { text: "Intensidade da seleção adversa", options: { bullet: true, breakLine: true, bold: true } },
      { text: "quem aceita pagar caro costuma ser quem não tem alternativa — mas quanto?", options: { bullet: false, fontSize: 12.5, color: GREY } },
    ],
    { x: M + 6.65, y: 2.55, w: 4.9, h: 2.8, fontSize: 14.5, color: NAVY, fontFace: SANS, paraSpaceAfter: 5, isTextBox: true, margin: 0 }
  );
  s.addText(
    "Cada premissa vira um parâmetro nomeado, com três valores. Nenhuma fica escondida como constante mágica no código.",
    { x: M + 6.65, y: 5.4, w: 4.9, h: 0.75, fontSize: 12.5, italic: true, color: NAVY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 9 · Os três cenários                                                        */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Três cenários, não uma aposta", "A política escolhida tem de sobreviver aos três — não ser ótima no central");

  const linhas = [
    ["", "Otimista", "Central", "Pessimista"],
    ["Aceite na referência", "95%", "85%", "70%"],
    ["Sensibilidade à taxa", "1,5", "3,0", "5,0"],
    ["Sensibilidade à entrada", "1,5", "3,0", "5,0"],
    ["Sensibilidade ao prazo", "0,5", "1,0", "2,0"],
    ["Seleção adversa", "0,2", "0,5", "1,0"],
  ];
  cartao(s, { x: M, y: 1.9, w: 6.6, h: 3.5, fill: WHITE });

  // Posições explícitas por coluna: o rótulo à esquerda e três colunas de
  // valor com a mesma largura. Calcular a posição dentro do laço convidava ao
  // erro que a primeira versão cometeu — a última coluna saiu fora do cartão.
  const COL_ROTULO = { x: M + 0.3, w: 2.55 };
  const COLS = [
    { x: M + 3.0, w: 1.05 },
    { x: M + 4.15, w: 1.05 }, // Central — a coluna destacada
    { x: M + 5.3, w: 1.05 },
  ];

  s.addShape(pres.ShapeType.roundRect, {
    x: COLS[1].x - 0.12, y: 2.05, w: COLS[1].w + 0.24, h: 3.2, rectRadius: 0.05,
    fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
  });

  linhas.forEach((linha, i) => {
    const y = 2.12 + i * 0.52;
    const cab = i === 0;

    s.addText(linha[0], {
      x: COL_ROTULO.x, y, w: COL_ROTULO.w, h: 0.35,
      fontSize: cab ? 11.5 : 13, bold: true,
      color: cab ? GREY : NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });

    COLS.forEach((col, j) => {
      const destacada = j === 1;
      s.addText(linha[j + 1], {
        x: col.x, y, w: col.w, h: 0.35,
        fontSize: cab ? 11.5 : 13,
        bold: cab || destacada,
        color: cab ? (destacada ? CORAL : GREY) : NAVY,
        fontFace: SANS, align: "center", isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: M + 7.0, y: 1.9, w: 4.9, h: 3.5, fill: NAVY, linha: NAVY });
  s.addText("PARA CALIBRAR A INTUIÇÃO", {
    x: M + 7.3, y: 2.12, w: 4.3, h: 0.3,
    fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText("No cenário central:", {
    x: M + 7.3, y: 2.5, w: 4.3, h: 0.3,
    fontSize: 13, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });
  [
    ["Cobrar 2,0% a.m.", "26% acima do mercado", "aceite cai para 46%  ·  PD sobe 13%"],
    ["Cobrar 3,0% a.m.", "89% acima do mercado", "aceite cai para 7%  ·  PD sobe 45%"],
  ].forEach((b, i) => {
    const y = 2.95 + i * 1.15;
    s.addText(b[0], {
      x: M + 7.3, y, w: 4.3, h: 0.32,
      fontSize: 15, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(b[1], {
      x: M + 7.3, y: y + 0.3, w: 4.3, h: 0.28,
      fontSize: 11, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(b[2], {
      x: M + 7.3, y: y + 0.58, w: 4.3, h: 0.3,
      fontSize: 12, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "O aceite entra como peso, não como sorteio: duas políticas idênticas têm de dar exatamente o mesmo número.");
}

/* ========================================================================== */
/* 10 · O primeiro resultado                                                   */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O motor em uso: a primeira candidata", "Aprovar score ≥ 7, taxas de 1,45% a 1,95% conforme a faixa");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "ROI anualizado da política", labels: ["Otimista", "Central", "Pessimista"], values: [0.102, 0.100, 0.098] },
      { name: "ROI exigido pelo conselho", labels: ["Otimista", "Central", "Pessimista"], values: [0.15, 0.15, 0.15] },
    ],
    {
      x: M, y: 1.95, w: 6.3, h: 4.0,
      barDir: "col", chartColors: [CORAL, NAVY],
      showTitle: true, title: "ROI por cenário contra a meta", titleFontSize: 12, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0%",
      dataLabelFontSize: 10, dataLabelColor: NAVY, dataLabelFontFace: SANS,
      valAxisLabelFormatCode: "0%",
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valGridLine: { color: GREY_LIGHT, size: 1 }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: NAVY, legendFontFace: SANS,
    }
  );

  cartao(s, { x: M + 6.75, y: 1.95, w: 5.15, h: 2.2, fill: WHITE });
  s.addText("O QUE MAIS MUDA ENTRE CENÁRIOS", {
    x: M + 7.05, y: 2.15, w: 4.55, h: 0.3,
    fontSize: 10.5, bold: true, color: GREY, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  [
    ["Volume", "R$ 60,5 mi", "R$ 48,1 mi", "R$ 34,8 mi"],
    ["Aceite médio", "81,8%", "64,7%", "46,7%"],
  ].forEach((l, i) => {
    const y = 2.55 + i * 0.72;
    s.addText(l[0], {
      x: M + 7.05, y, w: 1.6, h: 0.3,
      fontSize: 12.5, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    [1, 2, 3].forEach((j) => {
      s.addText(l[j], {
        x: M + 8.5 + (j - 1) * 1.05, y, w: 1.0, h: 0.3,
        fontSize: 11, color: j === 3 ? CORAL : GREY, bold: j === 3,
        fontFace: SANS, align: "right", isTextBox: true, margin: 0,
      });
    });
  });
  s.addText("otimista · central · pessimista", {
    x: M + 8.5, y: 3.98, w: 3.1, h: 0.25,
    fontSize: 9, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 6.75, y: 4.35, w: 5.15, h: 1.6, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("O problema que o próximo passo resolve", {
    x: M + 7.05, y: 4.55, w: 4.55, h: 0.32,
    fontSize: 14, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "ROI de 10% contra os 15% exigidos, e o volume fura no cenário pessimista. Subir o preço mata o aceite; aprovar mais fundo sobe a inadimplência.",
    { x: M + 7.05, y: 4.92, w: 4.55, h: 1.0, fontSize: 12, color: NAVY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );

  fecho(s, "O ROI quase não muda entre cenários porque é uma razão — o aceite afeta numerador e denominador juntos. Quem quebra é o volume.");
}

/* ========================================================================== */
/* 11 · Fecho                                                                  */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O QUE O MOTOR ENTREGA", {
    x: M, y: 1.35, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Uma régua para decidir,\nnão uma previsão do resultado", {
    x: M, y: 1.75, w: 8.5, h: 1.5,
    fontSize: 36, bold: true, color: WHITE, fontFace: SERIF, lineSpacing: 44, isTextBox: true, margin: 0,
  });

  s.addText(
    "As elasticidades de aceite são nossas premissas, não a verdade do simulador oficial. O que o motor garante é que duas políticas sejam comparadas sob a MESMA premissa — e que a escolhida sobreviva aos três cenários, não apenas ao mais favorável.",
    { x: M, y: 3.4, w: 7.6, h: 1.5, fontSize: 15, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 23, isTextBox: true, margin: 0 }
  );

  const proximos = [
    "Decidir o corte de aprovação dentro da janela viável: score ≥ 7 a ≥ 4",
    "Precificar cada faixa cobrindo a perda esperada e ainda sobrando",
    "Testar candidatas no motor, sob os três cenários",
    "Escolher a robusta, não a máxima — furar guard-rail corta a nota pela metade",
  ];
  s.addText("O PRÓXIMO PASSO: A TABELA DE POLÍTICA", {
    x: M + 8.1, y: 1.75, w: 4.5, h: 0.3,
    fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  proximos.forEach((t, i) => {
    const y = 2.2 + i * 0.95;
    s.addShape(pres.ShapeType.ellipse, {
      x: M + 8.1, y: y + 0.06, w: 0.22, h: 0.22, fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(t, {
      x: M + 8.5, y, w: 4.1, h: 0.8,
      fontSize: 12.5, color: WHITE, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  s.addText("Modelo é meio. Decisão é o fim.", {
    x: M, y: 6.3, w: 8, h: 0.45,
    fontSize: 16, bold: true, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
pres.writeFile({ fileName: path.join(destino, "02_motor_roi.pptx") }).then((f) => {
  console.log("Gerado:", f);
});
