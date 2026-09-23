/**
 * Apresentação 4 — A submissão (S06 + S10).
 *
 * Público: professor e analistas de dados plenos/seniores.
 *
 * O arco: o arquivo É o entregável → há uma decisão de formato que vale 10
 * pontos → o validador recusa antes de enviar → e cada regra dele foi testada
 * quebrando o arquivo de propósito.
 *
 * Gerar:  node apresentacoes/04_submissao.js
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
pres.title = "AutoCred — A submissão";

const cartao = (slide, opts) => C.cartao(pres, slide, opts);
const MONO = "Courier New";

/* ========================================================================== */
/* 1 · Capa                                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("DESAFIO AUTOCRED · O QUE VAI SER ENTREGUE", {
    x: M, y: 1.9, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true, isTextBox: true, margin: 0,
  });
  s.addText("A submissão", {
    x: M, y: 2.35, w: W - 2 * M, h: 1.1,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Dois arquivos, 8.000 linhas e uma decisão de formato\nque vale dez pontos",
    { x: M, y: 3.5, w: 9.0, h: 1.0, fontSize: 17, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 26, isTextBox: true, margin: 0 }
  );

  [
    { v: "8.000", r: "linhas submetidas\nentre os dois arquivos" },
    { v: "11", r: "verificações antes\nde o arquivo existir" },
    { v: "0", r: "passos manuais\nno caminho" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 3.9, y: 5.05, w: 3.5, valor: d.v, rotulo: d.r, cor: WHITE, tamanho: 34, corRotulo: GREY_ESCURO });
  });
}

/* ========================================================================== */
/* 2 · Os dois arquivos                                                        */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Dois arquivos, dois blocos de nota", "Cada um responde a uma pergunta diferente, e são avaliados separadamente");

  const arquivos = [
    {
      nome: "submissao_modelo.csv",
      base: "BASE B · 3.000 contratos",
      cols: "id_contrato, pd",
      pergunta: "O seu modelo teria acertado quem ia quebrar?",
      como: "O professor guardou o alvo. Ele cruza as nossas PDs com o gabarito dele e calcula o AuROC.",
      nota: "30 pontos",
      cor: TEAL,
    },
    {
      nome: "submissao_politica.csv",
      base: "BASE C · 5.000 propostas",
      cols: "id_proposta, pd, score_1a10, decisao,\ntaxa_am, prazo_meses, pct_entrada_minima",
      pergunta: "Quanto a sua decisão teria rendido?",
      como: "As propostas entram no simulador dele com as condições que ofertamos, e o ROI apurado é a nota.",
      nota: "40 pontos",
      cor: CORAL,
    },
  ];

  arquivos.forEach((a, i) => {
    const x = M + i * 6.05;
    cartao(s, { x, y: 1.85, w: 5.75, h: 4.4, fill: WHITE });
    s.addText(a.base, {
      x: x + 0.35, y: 2.08, w: 5.05, h: 0.3,
      fontSize: 10.5, bold: true, color: a.cor, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
    });
    s.addText(a.nome, {
      x: x + 0.35, y: 2.4, w: 5.05, h: 0.4,
      fontSize: 18, bold: true, color: NAVY, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(a.cols, {
      x: x + 0.35, y: 2.88, w: 5.05, h: 0.6,
      fontSize: 10.5, color: GREY, fontFace: MONO, lineSpacing: 14, isTextBox: true, margin: 0,
    });
    s.addText(a.pergunta, {
      x: x + 0.35, y: 3.6, w: 5.05, h: 0.45,
      fontSize: 15, bold: true, italic: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(a.como, {
      x: x + 0.35, y: 4.15, w: 5.05, h: 1.1,
      fontSize: 13, color: GREY, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0,
    });
    s.addText(a.nota, {
      x: x + 0.35, y: 5.5, w: 5.05, h: 0.45,
      fontSize: 22, bold: true, color: a.cor, fontFace: SERIF, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "Nenhuma política encosta na base B, e nenhum AuROC sai da base C. Misturar contaminaria as duas notas.");
}

/* ========================================================================== */
/* 3 · A decisão de formato                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Qual PD vai no arquivo?", "Há duas, e escolher errado custa os dez pontos de coerência");

  cartao(s, { x: M, y: 1.85, w: 5.75, h: 2.0, fill: WHITE });
  s.addText("PD DO PEDIDO", {
    x: M + 0.35, y: 2.08, w: 5.05, h: 0.3,
    fontSize: 11, bold: true, color: TEAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText("Escorada com o LTV e o prazo que o cliente pediu.", {
    x: M + 0.35, y: 2.42, w: 5.05, h: 0.5,
    fontSize: 14, color: NAVY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0,
  });
  s.addText("É ela que gerou o score, que gerou a decisão.", {
    x: M + 0.35, y: 3.0, w: 5.05, h: 0.6,
    fontSize: 13.5, bold: true, color: TEAL, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 6.15, y: 1.85, w: 5.75, h: 2.0, fill: WHITE });
  s.addText("PD DA OFERTA", {
    x: M + 6.5, y: 2.08, w: 5.05, h: 0.3,
    fontSize: 11, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText("Re-escorada com o LTV depois da entrada exigida.", {
    x: M + 6.5, y: 2.42, w: 5.05, h: 0.5,
    fontSize: 14, color: NAVY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0,
  });
  s.addText("É menor — e não bate com o score reportado.", {
    x: M + 6.5, y: 3.0, w: 5.05, h: 0.6,
    fontSize: 13.5, bold: true, color: CORAL, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M, y: 4.05, w: 11.9, h: 1.35, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("O problema", {
    x: M + 0.4, y: 4.25, w: 11.1, h: 0.3,
    fontSize: 14, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Exigir 10% de entrada de quem ofereceu 5% reduz o LTV — e o LTV é preditora do modelo, então a PD cai. Reportar essa PD menor ao lado do score que veio da PD maior deixaria a dupla inconsistente.",
    { x: M + 0.4, y: 4.6, w: 11.1, h: 0.7, fontSize: 13.5, color: NAVY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 5.6, w: 11.9, h: 1.25, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "Decisão: vai a PD do pedido. ", options: { bold: true, color: WHITE } },
      { text: "O CSV é o registro de uma decisão, e a decisão foi tomada com aquela PD. Assim ", options: { color: GREY_ESCURO } },
      { text: "score_1a10 == score_de_pd(pd)", options: { color: CORAL, fontFace: MONO } },
      { text: " é verdade nas 5.000 linhas — auditável por qualquer um.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 5.9, w: 11.1, h: 0.75, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );

  s.addNotes(
    "O efeito da entrada sobre o risco não se perde: ele está no motor de ROI e no documento de política, que é onde serve para argumentar. O CSV é registro de decisão, não relatório de risco."
  );
}

/* ========================================================================== */
/* 4 · As condições vêm da tabela                                              */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "As condições saem da tabela, não do caso", "Taxa, prazo e entrada são lidos da linha da faixa — nunca ajustados proposta a proposta");

  cartao(s, { x: M, y: 1.95, w: 5.6, h: 2.1, fill: WHITE });
  s.addText("1 · Coerência", {
    x: M + 0.35, y: 2.18, w: 4.9, h: 0.35,
    fontSize: 16, bold: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "A rubrica confere se o submetido bate com a tabela de faixas. Valor que varia dentro da mesma faixa levanta a pergunta: «então qual é a sua política?»",
    { x: M + 0.35, y: 2.6, w: 4.9, h: 1.2, fontSize: 13.5, color: GREY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.3, y: 1.95, w: 5.6, h: 2.1, fill: WHITE });
  s.addText("2 · Consistência com a defesa", {
    x: M + 6.65, y: 2.18, w: 4.9, h: 0.35,
    fontSize: 16, bold: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "O ROI de 11,3% foi calculado assumindo exatamente esses valores. Submeter outra coisa tornaria a projeção da defesa incompatível com o arquivo entregue.",
    { x: M + 6.65, y: 2.6, w: 4.9, h: 1.2, fontSize: 13.5, color: GREY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.3, w: 11.9, h: 1.95, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("Um detalhe de nomenclatura que evita confusão", {
    x: M + 0.4, y: 4.52, w: 11.1, h: 0.35,
    fontSize: 16, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "A coluna se chama ", options: { color: GREY_ESCURO } },
      { text: "pct_entrada_minima", options: { color: CORAL, fontFace: MONO } },
      { text: ": é o ", options: { color: GREY_ESCURO } },
      { text: "requisito", options: { color: WHITE, bold: true } },
      { text: ", não a entrada efetiva. Quem já oferecia 30% continua oferecendo 30% — isso entra na economia do contrato, não no arquivo. Ninguém é obrigado a dar menos entrada do que queria dar.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 4.95, w: 11.1, h: 1.1, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 5 · O validador                                                             */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("NENHUM ARQUIVO SAI SEM PASSAR", {
    x: M, y: 0.72, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Onze verificações antes de o arquivo existir", {
    x: M, y: 1.12, w: 11.5, h: 0.75,
    fontSize: 34, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const checks = [
    ["5.000 linhas", "o professor cruza por id"],
    ["ids idênticos à base C", "sem faltar nem sobrar"],
    ["sem duplicados", "id repetido quebra o merge"],
    ["pd em [0, 1]", "erro de unidade"],
    ["score coerente com a pd", "a checagem da rubrica"],
    ["decisao em maiúsculas", "formato do exemplo"],
    ["NEGAR com campos vazios", "como o exemplo mostra"],
    ["APROVAR com tudo preenchido", "linha sem oferta é incompleta"],
    ["taxa ≤ 3,5% a.m.", "guard-rail"],
    ["mesma faixa, mesmas condições", "coerência com a tabela"],
    ["aprovação ≥ 35%", "guard-rail"],
  ];
  checks.forEach((c, i) => {
    const x = M + (i % 2) * 6.0;
    const y = 2.15 + Math.floor(i / 2) * 0.72;
    s.addShape(pres.ShapeType.ellipse, {
      x, y: y + 0.08, w: 0.2, h: 0.2, fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(c[0], {
      x: x + 0.38, y, w: 3.1, h: 0.32,
      fontSize: 13, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(c[1], {
      x: x + 3.5, y: y + 0.02, w: 2.2, h: 0.3,
      fontSize: 10.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  s.addText(
    "Erro de formato custa a nota inteira do bloco — e só aparece depois do prazo, quando o professor roda o parser dele.",
    { x: M, y: 6.6, w: W - 2 * M, h: 0.45, fontSize: 14, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 6 · Testar quebrando                                                        */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Um validador que aceita tudo é pior que nenhum", "Cada regra foi testada adulterando o arquivo de propósito");

  const casos = [
    { t: "score trocado numa linha", r: "recusado: «incoerente com a pd»" },
    { t: "taxa diferente na mesma faixa", r: "recusado: «diferente da tabela»" },
    { t: "NEGAR com taxa preenchida", r: "recusado" },
    { t: "APROVAR sem prazo", r: "recusado" },
    { t: "«aprovar» em minúsculas", r: "recusado" },
    { t: "pd multiplicada por 100", r: "recusado: fora de [0, 1]" },
    { t: "uma linha a menos", r: "recusado" },
    { t: "colunas fora de ordem", r: "recusado" },
  ];
  casos.forEach((c, i) => {
    const x = M + (i % 2) * 6.0;
    const y = 1.9 + Math.floor(i / 2) * 1.05;
    cartao(s, { x, y, w: 5.7, h: 0.88, fill: WHITE });
    s.addText(c.t, {
      x: x + 0.3, y: y + 0.13, w: 5.1, h: 0.3,
      fontSize: 13, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(c.r, {
      x: x + 0.3, y: y + 0.45, w: 5.1, h: 0.3,
      fontSize: 11.5, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 6.1, w: 11.9, h: 0.95, fill: NAVY, linha: NAVY });
  s.addText(
    "Um teste que nunca falhou não provou nada: pode estar verificando a coisa errada. Quebrar de propósito é o que mostra que a proteção existe.",
    { x: M + 0.4, y: 6.35, w: 11.1, h: 0.5, fontSize: 14, italic: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 7 · O arquivo, lado a lado                                                  */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O arquivo entregue", "Conferido linha a linha contra o exemplo do professor");

  cartao(s, { x: M, y: 1.95, w: 5.75, h: 2.4, fill: NAVY, linha: NAVY });
  s.addText("O EXEMPLO DO PROFESSOR", {
    x: M + 0.3, y: 2.15, w: 5.15, h: 0.28,
    fontSize: 10, bold: true, color: GREY, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText(
    "id_proposta,pd,score_1a10,decisao,\ntaxa_am,prazo_meses,pct_entrada_minima\nP000001,0.0166,10,APROVAR,0.0155,60,0.0\nP000007,0.1873,3,NEGAR,,,",
    { x: M + 0.3, y: 2.5, w: 5.15, h: 1.7, fontSize: 10, color: GREY_ESCURO, fontFace: MONO, lineSpacing: 16, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 1.95, w: 5.75, h: 2.4, fill: NAVY, linha: NAVY });
  s.addText("O NOSSO", {
    x: M + 6.45, y: 2.15, w: 5.15, h: 0.28,
    fontSize: 10, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText(
    "id_proposta,pd,score_1a10,decisao,\ntaxa_am,prazo_meses,pct_entrada_minima\nP000002,0.10562,5,APROVAR,0.022923,48,0.1\nP000001,0.158389,4,NEGAR,,,",
    { x: M + 6.45, y: 2.5, w: 5.15, h: 1.7, fontSize: 10, color: WHITE, fontFace: MONO, lineSpacing: 16, isTextBox: true, margin: 0 }
  );

  const confs = [
    { t: "Cabeçalho", d: "idêntico, na mesma ordem" },
    { t: "Linhas negadas", d: "terminam em «,NEGAR,,,» — três campos vazios" },
    { t: "Prazo", d: "inteiro no arquivo, não «48.0»" },
    { t: "Total", d: "5.001 linhas: cabeçalho + 5.000" },
  ];
  confs.forEach((c, i) => {
    const x = M + (i % 2) * 6.05;
    const y = 4.6 + Math.floor(i / 2) * 1.0;
    cartao(s, { x, y, w: 5.75, h: 0.85, fill: WHITE });
    s.addText(c.t, {
      x: x + 0.3, y: y + 0.12, w: 1.9, h: 0.3,
      fontSize: 13, bold: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(c.d, {
      x: x + 2.15, y: y + 0.14, w: 3.35, h: 0.55,
      fontSize: 11.5, color: GREY, fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "O teste do formato lê o CSV cru, não o DataFrame: é o arquivo que o professor abre, não o objeto em memória.");
}

/* ========================================================================== */
/* 8 · A distribuição                                                          */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O que foi decidido para as 5.000 propostas", "2.976 aprovadas (59,5%) e 2.024 negadas");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "Aprovadas", labels: ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"], values: [337, 432, 627, 610, 520, 450, 0, 0, 0, 0] },
      { name: "Negadas", labels: ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"], values: [0, 0, 0, 0, 0, 0, 461, 521, 544, 498] },
    ],
    {
      x: M, y: 1.95, w: 7.3, h: 4.1,
      barDir: "col", barGrouping: "stacked",
      chartColors: [TEAL, CORAL],
      showTitle: true, title: "Propostas por faixa de score", titleFontSize: 12, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "ctr",
      // As duas séries têm o mesmo comprimento (empilhadas), então cada faixa
      // carrega um zero da série oposta. A quarta seção vazia da máscara
      // ("positivo;negativo;zero;texto") esconde esses zeros.
      dataLabelFormatCode: "#,##0;;;",
      dataLabelFontSize: 9, dataLabelColor: WHITE, dataLabelFontFace: SANS,
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valGridLine: { color: GREY_LIGHT, size: 1 }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: NAVY, legendFontFace: SANS,
    }
  );

  cartao(s, { x: M + 7.75, y: 1.95, w: 4.15, h: 1.95, fill: NAVY, linha: NAVY });
  numerao(s, { x: M + 8.0, y: 2.2, w: 3.65, valor: "59,5%", rotulo: "de aprovação — bem acima do mínimo de 35%", cor: CORAL, tamanho: 40, corRotulo: GREY_ESCURO });

  cartao(s, { x: M + 7.75, y: 4.1, w: 4.15, h: 1.95, fill: WHITE });
  s.addText("A fronteira", {
    x: M + 8.05, y: 4.3, w: 3.55, h: 0.32,
    fontSize: 14, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Entre a faixa 5 e a 4, a perda esperada salta de 7,92% para 11,18% do valor financiado.\n\nÉ ali que nenhuma taxa dentro do teto passa a cobrir.",
    { x: M + 8.05, y: 4.65, w: 3.55, h: 1.3, fontSize: 12, color: GREY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 9 · Fecho                                                                   */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("STATUS", {
    x: M, y: 1.1, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Os dois entregáveis estão prontos", {
    x: M, y: 1.5, w: 10, h: 0.85,
    fontSize: 38, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const itens = [
    { a: "submissao_modelo.csv", d: "3.000 PDs · PD média 0,0788 · 3.000 valores distintos", ok: true },
    { a: "submissao_politica.csv", d: "5.000 decisões · 59,5% aprovadas · coerente com a tabela", ok: true },
    { a: "Documento de política", d: "o template .docx do professor — é o próximo passo", ok: false },
  ];
  itens.forEach((it, i) => {
    const y = 2.8 + i * 1.05;
    cartao(s, { x: M, y, w: 11.9, h: 0.9, fill: it.ok ? NAVY_MID : NAVY, linha: it.ok ? NAVY_MID : "3A5468" });
    s.addShape(pres.ShapeType.ellipse, {
      x: M + 0.35, y: y + 0.32, w: 0.26, h: 0.26,
      fill: { color: it.ok ? TEAL : "3A5468" }, line: { color: it.ok ? TEAL : "3A5468", width: 0 },
    });
    s.addText(it.a, {
      x: M + 0.85, y: y + 0.26, w: 4.2, h: 0.35,
      fontSize: 14, bold: true, color: it.ok ? WHITE : GREY, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(it.d, {
      x: M + 5.3, y: y + 0.28, w: 6.2, h: 0.35,
      fontSize: 12.5, color: it.ok ? GREY_ESCURO : GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 6.05, w: 11.9, h: 0.95, fill: NAVY_MID, linha: NAVY_MID });
  s.addText(
    [
      { text: "Pendente do professor:  ", options: { color: GREY_ESCURO } },
      { text: "o e-mail de destino da entrega", options: { bold: true, color: WHITE } },
      { text: "  e o documento «AutoCred — Regras da Competição», citado no enunciado e ainda não recebido.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 6.3, w: 11.1, h: 0.5, fontSize: 13.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
pres.writeFile({ fileName: path.join(destino, "04_submissao.pptx") }).then((f) => {
  console.log("Gerado:", f);
});
