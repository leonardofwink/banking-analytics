/**
 * Apresentação 3 — A política de crédito (S07 + S09).
 *
 * Público: professor e analistas de dados plenos/seniores, poucos com
 * background de banking.
 *
 * O arco: uma política é uma tabela de regras → a antiga não precificava risco
 * → temos quatro limites inegociáveis → buscamos 960 candidatas → a busca
 * degenerou e a premissa estava errada → a tabela final, e por que ela nega o
 * que nega.
 *
 * Gerar:  node apresentacoes/03_politica_credito.js
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
pres.author = "Grupo 3";
pres.title = "AutoCred — Política de crédito";

const cartao = (slide, opts) => C.cartao(pres, slide, opts);

/* ========================================================================== */
/* 1 · Capa                                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("DESAFIO AUTOCRED · ENTREGÁVEL 2", {
    x: M, y: 1.9, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true, isTextBox: true, margin: 0,
  });
  s.addText("A política de crédito", {
    x: M, y: 2.35, w: W - 2 * M, h: 1.1,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "A quem conceder, a que preço, em que prazo, com quanta entrada —\ne por que negar o resto",
    { x: M, y: 3.5, w: 9.0, h: 1.0, fontSize: 17, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 26, isTextBox: true, margin: 0 }
  );

  [
    { v: "11,3%", r: "ROI anualizado\nno cenário central" },
    { v: "59,5%", r: "das propostas aprovadas\n(mínimo: 35%)" },
    { v: "12,7%", r: "de folga até o\nguard-rail mais apertado" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 3.9, y: 5.05, w: 3.5, valor: d.v, rotulo: d.r, cor: WHITE, tamanho: 34, corRotulo: GREY_ESCURO });
  });
}

/* ========================================================================== */
/* 2 · O que é uma política                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Uma política de crédito é uma tabela", "Não é um modelo. O modelo ordena risco; a tabela decide o que fazer com ele");

  const alavancas = [
    { t: "Aprovar ou negar", d: "O corte de score define o perfil da carteira.", c: "Cortar fundo demais derruba a originação — e a empresa precisa crescer." },
    { t: "Taxa de juros", d: "É a receita. Precisa cobrir a perda esperada da faixa e ainda sobrar.", c: "Preço alto afasta o cliente e atrai o cliente errado." },
    { t: "Prazo máximo", d: "Prazo longo cabe no bolso do cliente.", c: "Mas alonga a exposição ao risco. Encurtar demais inviabiliza a parcela." },
    { t: "Entrada mínima", d: "Reduz o LTV — e LTV menor derruba PD e LGD ao mesmo tempo.", c: "Exigir muito derruba o aceite e corta o ticket. Duplo golpe no volume." },
  ];

  alavancas.forEach((a, i) => {
    const x = M + (i % 2) * 6.0;
    const y = 1.9 + Math.floor(i / 2) * 2.3;
    cartao(s, { x, y, w: 5.7, h: 2.05, fill: WHITE });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.3, y: y + 0.25, w: 0.55, h: 0.55, fill: { color: NAVY }, line: { color: NAVY, width: 0 },
    });
    s.addText(String(i + 1), {
      x: x + 0.3, y: y + 0.36, w: 0.55, h: 0.35,
      fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(a.t, {
      x: x + 1.0, y: y + 0.25, w: 4.4, h: 0.35,
      fontSize: 17, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(a.d, {
      x: x + 1.0, y: y + 0.62, w: 4.4, h: 0.6,
      fontSize: 12.5, color: NAVY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0,
    });
    s.addText(a.c, {
      x: x + 1.0, y: y + 1.25, w: 4.4, h: 0.65,
      fontSize: 12, italic: true, color: CORAL, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "As quatro se contradizem. Qualquer uma puxada até o fim quebra outra — é isso que torna a decisão difícil.");
}

/* ========================================================================== */
/* 3 · O diagnóstico                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O PONTO DE PARTIDA", {
    x: M, y: 0.8, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("A política que queremos substituir", {
    x: M, y: 1.2, w: 11, h: 0.8,
    fontSize: 36, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M, y: 2.3, w: 5.9, h: 3.3, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("O QUE A BASE A MOSTRA", {
    x: M + 0.35, y: 2.52, w: 5.2, h: 0.3,
    fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  [
    ["score 10", "0,2% de default", "1,57%"],
    ["score 5", "11,4%", "1,61%"],
    ["score 1", "69,6%", "1,64%"],
  ].forEach((l, i) => {
    const y = 2.95 + i * 0.72;
    s.addText(l[0], { x: M + 0.35, y, w: 1.5, h: 0.3, fontSize: 13, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0 });
    s.addText(l[1], { x: M + 0.35, y: y + 0.28, w: 2.4, h: 0.28, fontSize: 11, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0 });
    s.addText(l[2], { x: M + 3.6, y: y + 0.02, w: 1.95, h: 0.4, fontSize: 22, bold: true, color: CORAL, fontFace: SERIF, align: "right", isTextBox: true, margin: 0 });
  });
  s.addText("Correlação entre taxa e risco: +0,125", {
    x: M + 0.35, y: 5.15, w: 5.2, h: 0.32,
    fontSize: 12.5, italic: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });

  s.addText("O mecanismo", {
    x: M + 6.4, y: 2.4, w: 5.5, h: 0.4,
    fontSize: 20, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    "Todo mundo paga quase o mesmo, qualquer que seja o risco",
    "O cliente bom está pagando pelo risco alheio",
    "Ele compara, encontra preço melhor e sai",
    "Sobra o cliente ruim — que estava subsidiado e continua",
    "A carteira piora, e a taxa média teria de subir de novo",
  ].forEach((t, i) => {
    const y = 2.95 + i * 0.52;
    s.addText(String(i + 1), {
      x: M + 6.4, y, w: 0.3, h: 0.3, fontSize: 12, bold: true, color: CORAL, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(t, {
      x: M + 6.8, y, w: 5.1, h: 0.45, fontSize: 13, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
  s.addText("É seleção adversa clássica — e é o que «o problema está na porta de entrada» quer dizer.", {
    x: M + 6.4, y: 5.6, w: 5.5, h: 0.6,
    fontSize: 12.5, italic: true, color: CORAL, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 4 · Os guard-rails                                                          */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Quatro limites inegociáveis", "Furar qualquer um corta a nota de política pela metade");

  const rails = [
    { t: "Taxa de aprovação", v: "≥ 35%", d: "das 5.000 propostas" },
    { t: "Teto de taxa (CET)", v: "≤ 3,5%", d: "ao mês" },
    { t: "Inadimplência", v: "≤ 8%", d: "dos contratos fechados" },
    { t: "Volume originado", v: "≥ R$ 40 mi", d: "efetivamente contratados" },
  ];
  rails.forEach((r, i) => {
    const x = M + i * 3.05;
    cartao(s, { x, y: 1.9, w: 2.8, h: 1.9, fill: WHITE });
    s.addText(r.t, {
      x: x + 0.25, y: 2.1, w: 2.3, h: 0.5,
      fontSize: 12.5, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(r.v, {
      x: x + 0.25, y: 2.65, w: 2.3, h: 0.55,
      fontSize: 26, bold: true, color: CORAL, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(r.d, {
      x: x + 0.25, y: 3.25, w: 2.3, h: 0.35,
      fontSize: 11, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 4.1, w: 11.9, h: 2.2, fill: NAVY, linha: NAVY });
  s.addText("A meta de 15% NÃO é guard-rail — e a distinção muda o que otimizar", {
    x: M + 0.4, y: 4.35, w: 11.1, h: 0.4,
    fontSize: 19, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "O conselho QUER ROI acima de 15%, mas a rubrica não cobra isso: o ROI vale 25 pontos ", options: { color: GREY_ESCURO } },
      { text: "relativos ao melhor grupo", options: { color: WHITE, bold: true } },
      { text: ". Os quatro limites acima, sim, são absolutos.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 4.85, w: 11.1, h: 0.55, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );
  s.addText(
    [
      { text: "E não é escolha de conveniência: medimos. Das ", options: { color: WHITE } },
      { text: "5.600 políticas", options: { color: CORAL, bold: true } },
      { text: " que varremos, ", options: { color: WHITE } },
      { text: "4.044 batem os 15% — e nenhuma é viável", options: { color: CORAL, bold: true } },
      { text: ". A de maior volume origina R$ 20,5 mi, metade do mínimo. Só o volume as bloqueia; inadimplência e aprovação passam. O teto viável é 11,46%.", options: { color: WHITE } },
    ],
    { x: M + 0.4, y: 5.45, w: 11.1, h: 0.75, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 5 · Como buscamos                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Seis parâmetros, 960 candidatas", "Deixar as 40 células livres seria impossível de buscar e de defender");

  const params = [
    ["corte", "a partir de que score aprovamos", "7 · 6 · 5 · 4"],
    ["taxa_base", "o preço da melhor faixa", "1,50% a 2,50%"],
    ["k_risco", "quanto a taxa sobe com a perda da faixa", "0 · 0,1 · 0,2 · 0,3"],
    ["prazo_max", "teto de prazo", "48 · 60"],
    ["entrada_base", "entrada mínima da melhor faixa", "0% · 5% · 10%"],
    ["entrada_passo", "quanto sobe a cada faixa pior", "0 · 4 p.p."],
  ];
  cartao(s, { x: M, y: 1.85, w: 7.3, h: 3.6, fill: WHITE });
  params.forEach((p, i) => {
    const y = 2.1 + i * 0.55;
    s.addText(p[0], {
      x: M + 0.3, y, w: 2.0, h: 0.32,
      fontSize: 12, color: NAVY, fontFace: "Courier New", isTextBox: true, margin: 0,
    });
    s.addText(p[1], {
      x: M + 2.4, y, w: 3.3, h: 0.32,
      fontSize: 11.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(p[2], {
      x: M + 5.75, y, w: 1.75, h: 0.32,
      fontSize: 11.5, bold: true, color: CORAL, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M + 7.75, y: 1.85, w: 4.15, h: 1.7, fill: NAVY, linha: NAVY });
  s.addText("A regra de preço", {
    x: M + 8.05, y: 2.05, w: 3.55, h: 0.32,
    fontSize: 14, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText("taxa = taxa_base\n   + k_risco × perda", {
    x: M + 8.05, y: 2.42, w: 3.55, h: 0.7,
    fontSize: 12.5, color: CORAL, fontFace: "Courier New", lineSpacing: 18, isTextBox: true, margin: 0,
  });
  s.addText("Precificação por risco — o que a antiga não fazia.", {
    x: M + 8.05, y: 3.1, w: 3.55, h: 0.35,
    fontSize: 11, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 7.75, y: 3.75, w: 4.15, h: 1.7, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("O contrafactual embutido", {
    x: M + 8.05, y: 3.95, w: 3.55, h: 0.32,
    fontSize: 14, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Com k_risco = 0 a fórmula reproduz a política antiga: mesmo preço para todo risco. Deixar esse valor na grade foi deliberado.",
    { x: M + 8.05, y: 4.32, w: 3.55, h: 1.0, fontSize: 11.5, color: NAVY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0 }
  );

  fecho(s, "Cada parâmetro tem significado de negócio — e a parametrização garante a monotonicidade por construção.");
}

/* ========================================================================== */
/* 6 · A busca degenerou                                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "A primeira busca degenerou", "E o resultado foi o sintoma de que a premissa estava errada");

  cartao(s, { x: M, y: 1.9, w: 5.8, h: 2.3, fill: CORAL_SOFT, linha: CORAL_SOFT });
  s.addText("O que aconteceu", {
    x: M + 0.35, y: 2.12, w: 5.1, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "896 das 960 políticas morreram por volume", options: { bold: true, breakLine: true, color: NAVY } },
      { text: "e a vencedora usava PREÇO ÚNICO para todo risco — exatamente a patologia que o conselho diagnosticou.", options: { color: NAVY } },
    ],
    { x: M + 0.35, y: 2.55, w: 5.1, h: 1.5, fontSize: 14, fontFace: SANS, lineSpacing: 20, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.4, w: 5.8, h: 1.9, fill: NAVY, linha: NAVY });
  s.addText("A leitura", {
    x: M + 0.35, y: 4.62, w: 5.1, h: 0.35,
    fontSize: 16, bold: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Um resultado que reproduz a doença é sintoma de premissa errada — não de política certa. O problema não estava na busca; estava na elasticidade que assumimos.",
    { x: M + 0.35, y: 5.05, w: 5.1, h: 1.1, fontSize: 13.5, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.25, y: 1.9, w: 5.65, h: 4.4, fill: WHITE });
  s.addText("A âncora que corrigiu", {
    x: M + 6.6, y: 2.15, w: 5.0, h: 0.35,
    fontSize: 16, bold: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "O professor impôs um teto de 3,5% ao mês como guard-rail.",
    { x: M + 6.6, y: 2.58, w: 5.0, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addText(
    "Um teto só é guard-rail se as políticas quiserem chegar perto dele.\n\nSe o aceite morresse a 2% ao mês — como a nossa primeira calibração supunha —, o teto de 3,5% seria decorativo. Ninguém o alcançaria.\n\nA existência do teto implica que o simulador permite operar bem acima do mercado. Recalibramos para que cobrar no teto deixe um aceite baixo, mas não nulo.",
    { x: M + 6.6, y: 3.1, w: 5.0, h: 3.0, fontSize: 13, color: GREY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  s.addNotes(
    "Registrar isso é importante: mudar premissa depois de ver resultado é perigoso. A diferença aqui é que a mudança veio de um argumento sobre o desenho do desafio, não de querer um número melhor — e está documentada no débito técnico."
  );
}

/* ========================================================================== */
/* 7 · A decisão que não foi do algoritmo                                      */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Onde o algoritmo parou e a decisão começou", "Entre as dez melhores, a diferença de ROI é de 0,2 ponto — isso é quase-empate");

  const cands = [
    { n: "A", t: "Máximo ROI", roi: "11,4%", folga: "7,7%", ap: "68,7%", inad: "7,4%", risco: "sim", cor: GREY },
    { n: "C", t: "Escolhida", roi: "11,3%", folga: "12,7%", ap: "59,5%", inad: "6,6%", risco: "sim", cor: CORAL },
    { n: "B", t: "Máxima folga", roi: "10,6%", folga: "19,7%", ap: "50,5%", inad: "6,1%", risco: "NÃO", cor: GREY },
  ];
  cands.forEach((c, i) => {
    const x = M + i * 4.05;
    const destaque = c.n === "C";
    cartao(s, { x, y: 1.85, w: 3.75, h: 3.4, fill: destaque ? CORAL_SOFT : WHITE, linha: destaque ? CORAL_SOFT : GREY_LIGHT });
    s.addText(`${c.n} · ${c.t}`, {
      x: x + 0.3, y: 2.08, w: 3.15, h: 0.35,
      fontSize: 15, bold: true, color: destaque ? NAVY : GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    [
      ["ROI central", c.roi],
      ["Folga", c.folga],
      ["Aprovação", c.ap],
      ["Inadimplência (pior)", c.inad],
      ["Precifica risco?", c.risco],
    ].forEach((l, j) => {
      const y = 2.55 + j * 0.5;
      s.addText(l[0], {
        x: x + 0.3, y, w: 2.1, h: 0.3,
        fontSize: 11.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
      });
      s.addText(l[1], {
        x: x + 2.4, y, w: 1.05, h: 0.3,
        fontSize: 12.5, bold: true,
        color: l[1] === "NÃO" ? CORAL : NAVY,
        fontFace: SANS, align: "right", isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: M, y: 5.45, w: 11.9, h: 1.3, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "O critério declarado tratava 1 ponto percentual como empate — sobre uma base de 11%, isso é 9% relativo, e não é empate. ", options: { color: GREY_ESCURO } },
      { text: "Em vez de estreitar a janela depois de ver o resultado, levamos as três candidatas ao responsável pela frente: é decisão de apetite a risco, não técnica.", options: { color: WHITE, bold: true } },
    ],
    { x: M + 0.4, y: 5.68, w: 11.1, h: 0.9, fontSize: 13.5, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 8 · A TABELA                                                                */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "A política", "Aprovar score ≥ 5 · taxa = 1,50% + 0,1 × perda esperada · prazo até 48 meses · entrada mínima 10%");

  const linhas = [
    ["Score", "Faixa de PD", "Decisão", "Taxa a.m.", "Prazo", "Entrada", "Perda esp."],
    ["10", "até 2,5%", "APROVAR", "1,634%", "48", "10%", "1,34%"],
    ["9", "2,5 – 3,5%", "APROVAR", "1,707%", "48", "10%", "2,07%"],
    ["8", "3,5 – 5,0%", "APROVAR", "1,792%", "48", "10%", "2,92%"],
    ["7", "5,0 – 7,0%", "APROVAR", "1,907%", "48", "10%", "4,07%"],
    ["6", "7,0 – 9,5%", "APROVAR", "2,077%", "48", "10%", "5,77%"],
    ["5", "9,5 – 13%", "APROVAR", "2,292%", "48", "10%", "7,92%"],
    ["4", "13 – 18%", "NEGAR", "—", "—", "—", "11,18%"],
    ["3", "18 – 25%", "NEGAR", "—", "—", "—", "15,61%"],
    ["2", "25 – 35%", "NEGAR", "—", "—", "—", "21,28%"],
    ["1", "acima de 35%", "NEGAR", "—", "—", "—", "33,31%"],
  ];
  const COLS = [
    { x: M + 0.3, w: 0.75, a: "left" },
    { x: M + 1.15, w: 1.9, a: "left" },
    { x: M + 3.15, w: 1.35, a: "center" },
    { x: M + 4.65, w: 1.3, a: "right" },
    { x: M + 6.1, w: 0.9, a: "right" },
    { x: M + 7.15, w: 1.1, a: "right" },
    { x: M + 8.45, w: 1.4, a: "right" },
  ];

  cartao(s, { x: M, y: 1.85, w: 10.2, h: 4.55, fill: WHITE });
  linhas.forEach((linha, i) => {
    const y = 2.05 + i * 0.4;
    const cab = i === 0;
    const negada = linha[2] === "NEGAR";

    if (negada && !cab) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.15, y: y - 0.03, w: 9.9, h: 0.36,
        fill: { color: "F7F8F9" }, line: { color: "F7F8F9", width: 0 },
      });
    }
    linha.forEach((celula, j) => {
      s.addText(celula, {
        x: COLS[j].x, y, w: COLS[j].w, h: 0.32,
        fontSize: cab ? 10.5 : 12,
        bold: cab || j === 0 || (j === 3 && !negada),
        color: cab ? GREY : negada ? GREY : (j === 3 ? CORAL : NAVY),
        italic: cab,
        fontFace: SANS, align: COLS[j].a, isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: M + 10.5, y: 1.85, w: 1.4, h: 4.55, fill: NAVY, linha: NAVY });
  s.addText("A TAXA\nVAI DE", {
    x: M + 10.65, y: 2.15, w: 1.1, h: 0.6,
    fontSize: 10, bold: true, color: CORAL, fontFace: SANS, align: "center", lineSpacing: 13, isTextBox: true, margin: 0,
  });
  s.addText("1,63%", {
    x: M + 10.6, y: 2.8, w: 1.2, h: 0.4,
    fontSize: 17, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
  });
  s.addText("a", {
    x: M + 10.6, y: 3.25, w: 1.2, h: 0.3,
    fontSize: 11, color: GREY, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
  });
  s.addText("2,29%", {
    x: M + 10.6, y: 3.55, w: 1.2, h: 0.4,
    fontSize: 17, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
  });
  s.addText("A antiga variava 7 pontos-base em toda a régua.", {
    x: M + 10.6, y: 4.2, w: 1.2, h: 1.4,
    fontSize: 10, italic: true, color: GREY_ESCURO, fontFace: SANS, align: "center", lineSpacing: 13, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 9 · Por que negamos                                                         */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Por que negar as quatro piores faixas", "Não é conservadorismo — é que nenhuma taxa legal cobre");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "Perda esperada (% do valor financiado)", labels: ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"], values: [0.0134, 0.0207, 0.0292, 0.0407, 0.0577, 0.0792, 0.1118, 0.1561, 0.2128, 0.3331] },
    ],
    {
      x: M, y: 1.95, w: 7.3, h: 4.1,
      barDir: "col", chartColors: [CORAL],
      showTitle: true, title: "Perda esperada por faixa de score", titleFontSize: 12, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0%",
      dataLabelFontSize: 9, dataLabelColor: NAVY, dataLabelFontFace: SANS,
      valAxisLabelFormatCode: "0%",
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valGridLine: { color: GREY_LIGHT, size: 1 }, catGridLine: { style: "none" },
      showLegend: false,
    }
  );
  s.addText("← aprovadas (score 10 a 5)                                    negadas (4 a 1) →", {
    x: M, y: 5.95, w: 7.3, h: 0.3,
    fontSize: 10, color: GREY, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 7.75, y: 1.95, w: 4.15, h: 1.9, fill: NAVY, linha: NAVY });
  numerao(s, { x: M + 8.0, y: 2.2, w: 3.65, valor: "33%", rotulo: "do valor financiado é a perda esperada da pior faixa", cor: CORAL, tamanho: 40, corRotulo: GREY_ESCURO });

  cartao(s, { x: M + 7.75, y: 4.05, w: 4.15, h: 2.0, fill: WHITE });
  s.addText("A aritmética que fecha", {
    x: M + 8.05, y: 4.25, w: 3.55, h: 0.32,
    fontSize: 14, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "Cobrar perto do teto de 3,5% afastaria justamente quem tem alternativa — sobraria quem não tem, que é quem quebra.\n\nA faixa não fica cara: ela fica vazia e ruim ao mesmo tempo.",
    { x: M + 8.05, y: 4.62, w: 3.55, h: 1.3, fontSize: 12, color: GREY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 10 · O desempenho                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O que a política entrega", "Os quatro guard-rails passam nos três cenários");

  s.addChart(
    pres.ChartType.bar,
    [
      { name: "Volume originado", labels: ["Otimista", "Central", "Pessimista"], values: [86.1, 66.7, 45.1] },
      { name: "Mínimo exigido", labels: ["Otimista", "Central", "Pessimista"], values: [40, 40, 40] },
    ],
    {
      x: M, y: 1.95, w: 6.1, h: 4.0,
      barDir: "col", chartColors: [CORAL, NAVY],
      showTitle: true, title: "Volume originado (R$ milhões)", titleFontSize: 12, titleColor: NAVY, titleFontFace: SANS,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
      dataLabelFontSize: 10, dataLabelColor: NAVY, dataLabelFontFace: SANS,
      catAxisLabelColor: NAVY, catAxisLabelFontSize: 11, catAxisLabelFontFace: SANS,
      valAxisLabelColor: GREY, valAxisLabelFontSize: 9, valAxisLabelFontFace: SANS,
      valGridLine: { color: GREY_LIGHT, size: 1 }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: NAVY, legendFontFace: SANS,
    }
  );

  cartao(s, { x: M + 6.55, y: 1.95, w: 5.35, h: 4.0, fill: WHITE });
  const tab = [
    ["", "Otim.", "Central", "Pess.", "Limite"],
    ["ROI anual", "11,5%", "11,3%", "11,1%", "—"],
    ["Inadimplência", "6,2%", "6,3%", "6,6%", "≤ 8%"],
    ["Aprovação", "59,5%", "59,5%", "59,5%", "≥ 35%"],
    ["Volume (R$ mi)", "86,1", "66,7", "45,1", "≥ 40"],
    ["Aceite médio", "79,5%", "61,4%", "41,4%", "—"],
    ["Contratos", "2.366", "1.829", "1.233", "—"],
  ];
  const CX = [
    { x: M + 6.85, w: 1.5, a: "left" },
    { x: M + 8.4, w: 0.78, a: "right" },
    { x: M + 9.22, w: 0.82, a: "right" },
    { x: M + 10.08, w: 0.78, a: "right" },
    { x: M + 10.95, w: 0.75, a: "right" },
  ];
  // 0,47 por linha: com 0,52 a última linha ("Contratos") encostava na frase
  // da folga logo abaixo — e a sobreposição só aparece no render.
  tab.forEach((linha, i) => {
    const y = 2.2 + i * 0.47;
    const cab = i === 0;
    linha.forEach((celula, j) => {
      s.addText(celula, {
        x: CX[j].x, y, w: CX[j].w, h: 0.32,
        fontSize: cab ? 10 : 12,
        bold: cab || j === 0 || j === 2,
        color: cab ? GREY : j === 4 ? CORAL : NAVY,
        fontFace: SANS, align: CX[j].a, isTextBox: true, margin: 0,
      });
    });
  });
  s.addText("Folga até o guard-rail mais apertado: 12,7%", {
    x: M + 6.85, y: 5.55, w: 4.85, h: 0.32,
    fontSize: 12.5, bold: true, italic: true, color: TEAL, fontFace: SANS, isTextBox: true, margin: 0,
  });

  fecho(s, "O ROI quase não muda entre cenários porque é uma razão. O que muda é o volume — e é por ele que a folga foi medida.");
}

/* ========================================================================== */
/* 11 · Fecho                                                                  */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O QUE ESTAMOS ENTREGANDO", {
    x: M, y: 1.0, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Uma decisão defensável,\nnão um número otimizado", {
    x: M, y: 1.4, w: 8.5, h: 1.5,
    fontSize: 36, bold: true, color: WHITE, fontFace: SERIF, lineSpacing: 44, isTextBox: true, margin: 0,
  });

  const pontos = [
    { t: "Cada faixa paga o seu risco", d: "A taxa vai de 1,63% a 2,29% conforme a perda esperada — contra os 7 pontos-base da política antiga." },
    { t: "As negativas têm aritmética", d: "A partir de 13% de PD, a perda esperada passa de 11% do financiado. Nenhuma taxa dentro do teto cobre isso sem esvaziar a faixa." },
    { t: "A folga é deliberada", d: "12,7% até o limite mais apertado. Só submetemos uma vez, e a elasticidade real do aceite é desconhecida." },
    { t: "As premissas estão nomeadas", d: "Aceite e seleção adversa são cenários declarados, não constantes escondidas. O que é medido e o que é assumido está separado." },
  ];
  pontos.forEach((p, i) => {
    const y = 3.15 + i * 0.95;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.08, w: 0.22, h: 0.22, fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(p.t, {
      x: M + 0.42, y, w: 3.3, h: 0.35,
      fontSize: 14, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(p.d, {
      x: M + 3.9, y, w: 7.9, h: 0.75,
      fontSize: 12.5, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  s.addText("Modelo é meio. Decisão é o fim.", {
    x: M, y: 6.85, w: 8, h: 0.45,
    fontSize: 16, bold: true, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
pres.writeFile({ fileName: path.join(destino, "03_politica_credito.pptx") }).then((f) => {
  console.log("Gerado:", f);
});
