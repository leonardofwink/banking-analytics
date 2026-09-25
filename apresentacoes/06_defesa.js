/**
 * Apresentação 6 — A defesa, ao professor.
 *
 * Público: o professor e a banca. Vale os 20 pontos do bloco de defesa.
 *
 * Estruturada pelo princípio da pirâmide (Barbara Minto): a resposta vem
 * primeiro, e tudo abaixo existe para sustentá-la. Ninguém precisa refazer
 * a jornada da análise para saber aonde ela chegou.
 *
 * As regras que a estrutura segue:
 *   1. Toda afirmação resume as que estão abaixo dela.
 *   2. Ideias do mesmo grupo são da mesma natureza.
 *   3. Cada bloco tem exatamente TRÊS sustentações — MECE, sem sobreposição.
 *
 * A divisão em quatro blocos não é estética: cada um é um integrante, e cada
 * bloco abre com a afirmação que aquela pessoa precisa defender. Quem
 * apresenta decora a afirmação do topo, não os números.
 *
 * Gerar:  node apresentacoes/06_defesa.js
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
pres.title = "AutoCred — Política de crédito, a defesa";

const cartao = (slide, opts) => C.cartao(pres, slide, opts);
const MONO = "Courier New";

/** Abre um bloco: quem fala, a afirmação que ele sustenta, e as três razões. */
function abrirBloco(s, { numero, quem, papel, afirmacao, razoes, minutos }) {
  s.background = { color: NAVY };

  s.addText(`BLOCO ${numero}  ·  ${quem.toUpperCase()}  ·  ${papel}`, {
    x: M, y: 0.95, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s.addText(`~${minutos} min`, {
    x: W - M - 1.6, y: 0.95, w: 1.6, h: 0.35,
    fontSize: 12, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
  });

  s.addText(afirmacao, {
    x: M, y: 1.45, w: W - 2 * M, h: 1.5,
    fontSize: 32, bold: true, color: WHITE, fontFace: SERIF, lineSpacing: 40,
    isTextBox: true, margin: 0,
  });

  s.addText("Sustenta-se em três coisas:", {
    x: M, y: 3.3, w: 6, h: 0.35,
    fontSize: 14, italic: true, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  razoes.forEach((r, i) => {
    const y = 3.85 + i * 1.0;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.03, w: 0.45, h: 0.45,
      fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(String(i + 1), {
      x: M, y: y + 0.09, w: 0.45, h: 0.32,
      fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0,
    });
    s.addText(r, {
      x: M + 0.72, y: y, w: 11.1, h: 0.8,
      fontSize: 17, color: WHITE, fontFace: SANS, lineSpacing: 23,
      isTextBox: true, margin: 0,
    });
  });
}

/* ========================================================================== */
/* 1 · Capa                                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("DESAFIO AUTOCRED  ·  GRUPO 3  ·  SETEMBRO DE 2026", {
    x: M, y: 1.7, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true,
    isTextBox: true, margin: 0,
  });
  s.addText("Política de crédito", {
    x: M, y: 2.15, w: W - 2 * M, h: 1.1,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Por que aprovamos quem aprovamos, por que cobramos o que cobramos,\ne onde este retorno quebra",
    { x: M, y: 3.3, w: 10.5, h: 1.0, fontSize: 17, color: GREY_ESCURO, fontFace: SANS,
      lineSpacing: 26, isTextBox: true, margin: 0 }
  );

  [
    { v: "59,5%", r: "das propostas\naprovadas" },
    { v: "11,3%", r: "ROI anualizado\nno cenário central" },
    { v: "6,3%", r: "inadimplência\nprojetada" },
    { v: "4 de 4", r: "guard-rails\nrespeitados" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 2.95, y: 4.85, w: 2.7, valor: d.v, rotulo: d.r,
                 cor: WHITE, tamanho: 34, corRotulo: GREY_ESCURO });
  });

  s.addText("Deni Alan  ·  Leonardo Wink  ·  Marcelo Félix  ·  Renato", {
    x: M, y: 6.55, w: W - 2 * M, h: 0.35,
    fontSize: 13, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 2 · A TESE — a pirâmide inteira num slide                                   */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };

  s.addText("A RESPOSTA, ANTES DO CAMINHO", {
    x: M, y: 0.45, w: W - 2 * M, h: 0.3,
    fontSize: 11.5, bold: true, color: TEAL, fontFace: SANS, charSpacing: 2,
    isTextBox: true, margin: 0,
  });

  // o topo da pirâmide
  cartao(s, { x: M + 1.4, y: 0.9, w: 9.1, h: 1.35, fill: NAVY, linha: NAVY });
  s.addText(
    "Aprovar score 5 ou melhor, com preço proporcional à perda\nde cada faixa, rende 11,3% ao ano dentro dos quatro limites",
    { x: M + 1.7, y: 1.18, w: 8.5, h: 0.9, fontSize: 19, bold: true, color: WHITE,
      fontFace: SERIF, align: "center", lineSpacing: 28, isTextBox: true, margin: 0 }
  );

  // as três pernas
  const pernas = [
    {
      t: "O modelo ordena risco\nfora da amostra",
      d: "AuROC de 0,7234 em 2024, com a variável que envenenaria o modelo removida e travada em teste",
      quem: "Deni",
    },
    {
      t: "O preço cobre a perda\nde cada faixa",
      d: "Uma conta auditável em uma linha, monotônica no risco, que corrige o preço único da política de 2022",
      quem: "Léo",
    },
    {
      t: "O retorno sobrevive\naos três cenários",
      d: "Escolhido com 12,7% de folga até o limite mais apertado, em vez do ROI máximo disponível",
      quem: "Renato",
    },
  ];

  pernas.forEach((p, i) => {
    const x = M + i * 4.03;
    // conector
    s.addShape(pres.ShapeType.line, {
      x: x + 1.91, y: 2.25, w: 0, h: 0.4,
      line: { color: GREY_LIGHT, width: 1.5 },
    });
    cartao(s, { x, y: 2.65, w: 3.83, h: 2.25, fill: WHITE });
    s.addText(p.t, {
      x: x + 0.28, y: 2.9, w: 3.3, h: 0.75,
      fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, lineSpacing: 21,
      isTextBox: true, margin: 0,
    });
    s.addText(p.d, {
      x: x + 0.28, y: 3.68, w: 3.3, h: 0.95,
      fontSize: 12, color: GREY, fontFace: SANS, lineSpacing: 16,
      isTextBox: true, margin: 0,
    });
    s.addText(`defende: ${p.quem}`, {
      x: x + 0.28, y: 4.52, w: 3.3, h: 0.28,
      fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 5.15, w: 11.9, h: 1.5, fill: CORAL_SOFT, linha: CORAL });
  s.addText("E a pergunta que não vamos esperar que façam", {
    x: M + 0.4, y: 5.35, w: 11.1, h: 0.35,
    fontSize: 15.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "«Por que 11,3% e não os 15% pedidos?»  ", options: { bold: true, color: NAVY } },
      { text: "Porque 15% é incompatível com o piso de volume: das 5.600 políticas que varremos, 4.044 batem a meta e ", options: { color: NAVY } },
      { text: "nenhuma", options: { bold: true, color: CORAL } },
      { text: " respeita os R$ 40 milhões. O bloco 3 mostra a medição.", options: { color: NAVY } },
    ],
    { x: M + 0.4, y: 5.75, w: 11.1, h: 0.75, fontSize: 13, fontFace: SANS,
      lineSpacing: 18, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 3 · SCQA — o problema                                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O problema que a AutoCred trouxe", "O conselho quer crescer sem perder a mão no risco — e a política de 2022 não distingue risco");

  const blocos = [
    { r: "SITUAÇÃO", t: "A AutoCred financia veículos e quer crescer",
      d: "10.000 contratos originados entre 2022 e 2024, e uma carteira nova de 5.000 propostas esperando decisão." },
    { r: "COMPLICAÇÃO", t: "A política atual cobra o mesmo preço de todo risco",
      d: "1,57% ao mês de quem tem 0,2% de inadimplência e 1,64% de quem tem 69,6%. Correlação entre taxa e risco: +0,125." },
    { r: "PERGUNTA", t: "A quem conceder, a que preço, em que prazo",
      d: "E com quanta entrada — respeitando quatro limites inegociáveis do conselho." },
  ];

  blocos.forEach((b, i) => {
    const y = 1.95 + i * 1.35;
    cartao(s, { x: M, y, w: 11.9, h: 1.15, fill: WHITE });
    s.addText(b.r, {
      x: M + 0.35, y: y + 0.2, w: 1.9, h: 0.3,
      fontSize: 11, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1.5,
      isTextBox: true, margin: 0,
    });
    s.addText(b.t, {
      x: M + 2.4, y: y + 0.16, w: 9.1, h: 0.35,
      fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(b.d, {
      x: M + 2.4, y: y + 0.56, w: 9.1, h: 0.45,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 6.0, w: 11.9, h: 0.9, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "RESPOSTA   ", options: { bold: true, color: CORAL } },
      { text: "Aprovar score 5 ou melhor, com preço proporcional à perda esperada de cada faixa. ", options: { color: WHITE } },
      { text: "O resto desta apresentação sustenta essa frase.", options: { color: GREY_ESCURO, italic: true } },
    ],
    { x: M + 0.4, y: 6.25, w: 11.1, h: 0.45, fontSize: 14, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 4 · BLOCO 1 — Deni                                                          */
/* ========================================================================== */
{
  const s = pres.addSlide();
  abrirBloco(s, {
    numero: 1, quem: "Deni", papel: "MODELAGEM", minutos: 4,
    afirmacao: "O modelo ordena risco fora da amostra,\ne sabemos por que confiar nele",
    razoes: [
      "Removemos a variável que daria o melhor AuROC de treino e destruiria o modelo na aplicação",
      "Medimos out-of-time, com o critério de escolha escrito antes de existir resultado",
      "Descartamos o segundo colocado por calibração, não por AuROC — porque preço precisa de nível, não só de ordem",
    ],
  });
}

/* ========================================================================== */
/* 5 · Deni 1 — a armadilha                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "1 · A variável que envenenaria o modelo",
         "A mais correlacionada com o alvo, e a que destruiria a aplicação — sem levantar um único erro");

  cartao(s, { x: M, y: 1.95, w: 11.9, h: 1.2, fill: NAVY, linha: NAVY });
  s.addText("qtd_parcelas_em_atraso_12m", {
    x: M + 0.4, y: 2.15, w: 6.2, h: 0.42,
    fontSize: 20, bold: true, color: WHITE, fontFace: MONO, isTextBox: true, margin: 0,
  });
  s.addText("correlação de 0,74 com o alvo na base de desenvolvimento", {
    x: M + 0.4, y: 2.6, w: 6.5, h: 0.35,
    fontSize: 13, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText("vale ZERO em toda linha das bases B e C", {
    x: M + 7.2, y: 2.35, w: 4.3, h: 0.45,
    fontSize: 16, bold: true, color: CORAL, fontFace: SANS, align: "right",
    isTextBox: true, margin: 0,
  });

  const cols = [
    { t: "Por que ela engana", d: "É a variável mais correlacionada com o alvo. Qualquer seleção automática a escolhe primeiro." },
    { t: "Por que ela destrói", d: "É pós-concessão: só existe depois que o contrato começou. Na hora de decidir, ela não existe." },
    { t: "O que aconteceria", d: "O AuROC despencaria para ~0,50 na Base B. Sem erro, sem aviso, sem exceção." },
  ];
  cols.forEach((c, i) => {
    const x = M + i * 4.03;
    cartao(s, { x, y: 3.4, w: 3.83, h: 1.85, fill: WHITE });
    s.addText(c.t, {
      x: x + 0.28, y: 3.62, w: 3.3, h: 0.35,
      fontSize: 15, bold: true, color: i === 2 ? CORAL : NAVY, fontFace: SERIF,
      isTextBox: true, margin: 0,
    });
    s.addText(c.d, {
      x: x + 0.28, y: 4.02, w: 3.3, h: 1.1,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 5.45, w: 11.9, h: 1.05, fill: CORAL_SOFT, linha: CORAL });
  s.addText(
    [
      { text: "Como nos protegemos:  ", options: { bold: true, color: NAVY } },
      { text: "a coluna sai na ingestão, e há um teste que falha se ela reaparecer. Outras três saíram pelo mesmo raciocínio — ", options: { color: NAVY } },
      { text: "taxa_juros_am", options: { color: NAVY, fontFace: MONO } },
      { text: ", ", options: { color: NAVY } },
      { text: "parcela_mensal", options: { color: NAVY, fontFace: MONO } },
      { text: " e ", options: { color: NAVY } },
      { text: "comprometimento_renda", options: { color: NAVY, fontFace: MONO } },
      { text: ", esta última por criar circularidade com o preço que nós mesmos ofertamos.", options: { color: NAVY } },
    ],
    { x: M + 0.4, y: 5.68, w: 11.1, h: 0.65, fontSize: 12.5, fontFace: SANS,
      lineSpacing: 17, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 6 · Deni 2 — validação                                                      */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "2 · Medimos como vamos aplicar",
         "A aplicação é out-of-time, então a validação também é — e o critério estava escrito antes do resultado");

  cartao(s, { x: M, y: 1.95, w: 5.75, h: 2.1, fill: WHITE });
  s.addText("Split temporal, não 70/30 aleatório", {
    x: M + 0.35, y: 2.15, w: 5.05, h: 0.38,
    fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Treino 2022–2023 (6.670 contratos), validação 2024 (3.330). Vamos escorar contratos futuros: um split aleatório mediria a coisa errada e daria um número mais bonito.",
    { x: M + 0.35, y: 2.6, w: 5.05, h: 1.3, fontSize: 12.5, color: GREY, fontFace: SANS,
      lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 1.95, w: 5.75, h: 2.1, fill: WHITE });
  s.addText("A validação foi medida uma vez só", {
    x: M + 6.5, y: 2.15, w: 5.05, h: 0.38,
    fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Os hiperparâmetros saíram de validação cruzada temporal em três dobras dentro do treino, sem tocar em 2024. O modelo final foi retreinado na base completa antes de escorar a Base B.",
    { x: M + 6.5, y: 2.6, w: 5.05, h: 1.3, fontSize: 12.5, color: GREY, fontFace: SANS,
      lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  const linhas = [
    ["", "Val. cruzada", "Validação 2024", "Decisão"],
    ["Regressão logística", "0,6391", "0,6489", "referência"],
    ["Random Forest", "—", "0,7159", "descartado por calibração"],
    ["XGBoost", "0,6948", "0,7234", "escolhido"],
  ];
  const cx = [M + 0.35, M + 4.6, M + 6.6, M + 8.9];
  const cw = [4.1, 1.8, 2.1, 3.0];

  cartao(s, { x: M, y: 4.3, w: 11.9, h: 1.85, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = 4.5 + r * 0.38;
    const cab = r === 0;
    const escolhido = linha[0] === "XGBoost";
    if (escolhido) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.2, y: y - 0.03, w: 11.5, h: 0.36,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((cel, c) => {
      s.addText(cel, {
        x: cx[c], y, w: cw[c], h: 0.32,
        fontSize: cab ? 11 : 12.5, bold: cab || escolhido,
        italic: cab, color: cab ? GREY : NAVY, fontFace: SANS,
        align: c === 0 || c === 3 ? "left" : "center", isTextBox: true, margin: 0,
      });
    });
  });

  fecho(s, "Ganhar nas duas medidas, e não em uma só, é o que afasta a hipótese de sorte em um conjunto específico.");
}

/* ========================================================================== */
/* 7 · Deni 3 — calibração                                                     */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "3 · Por que o segundo colocado foi descartado",
         "Para ordenar risco, empate técnico. Para precificar, inviável — e nós precisamos precificar");

  cartao(s, { x: M, y: 2.0, w: 11.9, h: 1.8, fill: WHITE });
  [
    { v: "0,7159", r: "AuROC do Random Forest\nempate técnico com o XGBoost", cor: NAVY },
    { v: "42,3%", r: "PD média que ele projetava\ncom reponderação de classes", cor: CORAL },
    { v: "7,2%", r: "inadimplência real\nobservada na base", cor: NAVY },
    { v: "6×", r: "o erro de nível\nque isso significa", cor: CORAL },
  ].forEach((d, i) => {
    numerao(s, { x: M + 0.3 + i * 2.87, y: 2.25, w: 2.7, valor: d.v, rotulo: d.r,
                 cor: d.cor, tamanho: 28, corRotulo: GREY });
  });

  cartao(s, { x: M, y: 4.1, w: 11.9, h: 2.2, fill: NAVY, linha: NAVY });
  s.addText("Ordenar não é o bastante quando o número vira preço", {
    x: M + 0.4, y: 4.35, w: 11.1, h: 0.4,
    fontSize: 19, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "A perda esperada é ", options: { color: GREY_ESCURO } },
      { text: "PD × EAD × LGD", options: { color: WHITE, bold: true } },
      { text: ", e a taxa de cada faixa sai dela. Uma PD seis vezes maior que a realidade produz preço absurdo — o cliente vai embora e o modelo parecia ótimo no AuROC.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 4.85, w: 11.1, h: 0.8, fontSize: 14, fontFace: SANS,
      lineSpacing: 20, isTextBox: true, margin: 0 }
  );
  s.addText(
    "É por isso que o critério de escolha, escrito antes de rodar, tinha duas linhas: ordenação E calibração.",
    { x: M + 0.4, y: 5.7, w: 11.1, h: 0.4, fontSize: 13.5, italic: true, color: CORAL,
      fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 8 · BLOCO 2 — Léo                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  abrirBloco(s, {
    numero: 2, quem: "Léo", papel: "POLÍTICA E PRECIFICAÇÃO", minutos: 4,
    afirmacao: "O preço de cada faixa cobre a perda dela,\npor uma regra que cabe em uma linha",
    razoes: [
      "As faixas têm cortes absolutos de PD, então significam a mesma coisa em qualquer base",
      "A taxa é 1,50% ao mês mais 10% da perda esperada da faixa — auditável e monotônica no risco",
      "Prazo e entrada são alavancas de risco, não de preço, e estão fixas por decisão declarada",
    ],
  });
}

/* ========================================================================== */
/* 9 · Léo 1 — cortes absolutos                                                */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "1 · Cortes absolutos, não quantis",
         "Porque a Base C é outra população — e uma faixa precisa significar a mesma coisa nas duas");

  cartao(s, { x: M, y: 1.95, w: 5.75, h: 2.35, fill: WHITE });
  s.addText("O que o quantil faria", {
    x: M + 0.35, y: 2.15, w: 5.05, h: 0.35,
    fontSize: 16, bold: true, color: GREY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Dividir cada base em dez partes iguais. Simples — mas o décimo pior de uma população boa e o décimo pior de uma população ruim não são o mesmo risco, e não podem custar o mesmo preço.",
    { x: M + 0.35, y: 2.58, w: 5.05, h: 1.5, fontSize: 12.5, color: GREY, fontFace: SANS,
      lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 1.95, w: 5.75, h: 2.35, fill: NAVY, linha: NAVY });
  s.addText("O que o corte absoluto garante", {
    x: M + 6.5, y: 2.15, w: 5.05, h: 0.35,
    fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "A faixa 5 significa ", options: { color: GREY_ESCURO } },
      { text: "«PD entre 9,5% e 13%»", options: { color: WHITE, bold: true } },
      { text: " em qualquer base, em qualquer ano. O preço dela cobre aquele risco — e aquele risco é o mesmo em toda parte.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 6.5, y: 2.58, w: 5.05, h: 1.5, fontSize: 12.5, fontFace: SANS,
      lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.55, w: 11.9, h: 1.8, fill: CORAL_SOFT, linha: CORAL });
  s.addText("A Base C é mesmo outra população — medimos", {
    x: M + 0.4, y: 4.78, w: 11.1, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  [
    { v: "5,93", r: "PSI em qtd_restricoes_ativas" },
    { v: "0,50", r: "PSI em score_bureau" },
    { v: "549 vs 645", r: "score de bureau mediano" },
    { v: "1,70 vs 0,63", r: "restrições ativas, em média" },
  ].forEach((d, i) => {
    s.addText(d.v, {
      x: M + 0.4 + i * 2.87, y: 5.25, w: 2.7, h: 0.4,
      fontSize: 19, bold: true, color: CORAL, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0,
    });
    s.addText(d.r, {
      x: M + 0.4 + i * 2.87, y: 5.68, w: 2.7, h: 0.3,
      fontSize: 11, color: GREY, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
    });
  });
  s.addText("As duas variáveis mais preditivas do modelo são exatamente as que mais mudaram.", {
    x: M + 0.4, y: 6.0, w: 11.1, h: 0.3,
    fontSize: 12, italic: true, color: NAVY, fontFace: SANS, align: "center",
    isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 10 · Léo 2 — a regra de preço                                               */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "2 · A regra de preço, e a tabela que sai dela",
         "Quem traz mais risco paga mais — e o quanto mais é proporcional ao risco que traz");

  cartao(s, { x: M, y: 1.85, w: 11.9, h: 0.95, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "taxa da faixa  =  ", options: { color: GREY_ESCURO } },
      { text: "1,50%", options: { color: WHITE, bold: true } },
      { text: "  +  ", options: { color: GREY_ESCURO } },
      { text: "10%", options: { color: CORAL, bold: true } },
      { text: "  ×  perda esperada da faixa", options: { color: WHITE, bold: true } },
    ],
    { x: M, y: 2.12, w: 11.9, h: 0.45, fontSize: 21, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0 }
  );

  const linhas = [
    ["Score", "Faixa de PD", "Decisão", "Taxa a.m.", "Prazo", "Entrada", "Perda esp.", "ROI"],
    ["10", "0,0–2,5%", "APROVAR", "1,634%", "48m", "10%", "1,34%", "10,5%"],
    ["9", "2,5–3,5%", "APROVAR", "1,707%", "48m", "10%", "2,07%", "10,8%"],
    ["8", "3,5–5,0%", "APROVAR", "1,792%", "48m", "10%", "2,92%", "11,2%"],
    ["7", "5,0–7,0%", "APROVAR", "1,907%", "48m", "10%", "4,07%", "11,5%"],
    ["6", "7,0–9,5%", "APROVAR", "2,077%", "48m", "10%", "5,77%", "12,1%"],
    ["5", "9,5–13,0%", "APROVAR", "2,292%", "48m", "10%", "7,92%", "12,5%"],
    ["4 a 1", "acima de 13%", "NEGAR", "—", "—", "—", "11,2% a 33,3%", "—"],
  ];
  const cx = [M + 0.15, M + 1.0, M + 2.6, M + 4.3, M + 5.7, M + 6.9, M + 8.3, M + 10.3];
  const cw = [0.8, 1.5, 1.6, 1.3, 1.1, 1.3, 1.9, 1.4];

  cartao(s, { x: M, y: 2.95, w: 11.9, h: 3.3, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = 3.1 + r * 0.385;
    const cab = r === 0;
    const negar = linha[2] === "NEGAR";
    if (cab) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.08, y: y - 0.04, w: 11.74, h: 0.36,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
    } else if (r % 2 === 0) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.08, y: y - 0.04, w: 11.74, h: 0.36,
        fill: { color: "F7F9FA" }, line: { color: "F7F9FA", width: 0 },
      });
    }
    linha.forEach((cel, c) => {
      s.addText(cel, {
        x: cx[c], y, w: cw[c], h: 0.3,
        fontSize: cab ? 10.5 : 12, bold: cab || c === 0,
        color: cab ? WHITE : (negar ? GREY : NAVY), fontFace: SANS,
        align: "center", isTextBox: true, margin: 0,
      });
    });
  });

  fecho(s, "Na faixa 8, que perde 2,92%: 1,50% + 0,29% = 1,792%. Dá para conferir cada linha com uma calculadora.");
}

/* ========================================================================== */
/* 11 · Léo 3 — prazo e entrada                                                */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "3 · Prazo e entrada não são alavancas de preço",
         "São de risco — e fixá-las foi decisão declarada, não omissão");

  const alav = [
    {
      t: "Prazo de 48 meses para todas as faixas",
      d: "Prazo maior rende mais juros, mas alonga a exposição e reduz a margem por ano. Testamos 24, 36, 48 e 60 em todas as combinações: 48 é o ótimo, e a 24 meses o teto viável cai para 7,6%.",
      n: "48m",
    },
    {
      t: "Entrada mínima de 10% para todas",
      d: "A entrada reduz o LTV e, com ele, PD e LGD ao mesmo tempo — medimos re-escorando com o LTV ofertado, em vez de assumir. Não exigimos mais porque ela ataca o volume duas vezes.",
      n: "10%",
    },
  ];

  alav.forEach((a, i) => {
    const y = 1.95 + i * 1.75;
    cartao(s, { x: M, y, w: 11.9, h: 1.55, fill: WHITE });
    s.addText(a.n, {
      x: M + 0.4, y: y + 0.45, w: 1.5, h: 0.6,
      fontSize: 28, bold: true, color: CORAL, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0,
    });
    s.addText(a.t, {
      x: M + 2.2, y: y + 0.25, w: 9.3, h: 0.38,
      fontSize: 16.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(a.d, {
      x: M + 2.2, y: y + 0.68, w: 9.3, h: 0.75,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 5.5, w: 11.9, h: 1.0, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "O teto de 3,5% ao mês não é a restrição que morde.  ", options: { color: WHITE, bold: true } },
      { text: "A política antiga praticou média de 1,59%, e é esse o preço que o cliente encontra no concorrente. Quem limita o nosso preço é o aceite, não o CET — cobrar 3% num mercado de 1,6% não é ilegal, é apenas não ter o cliente.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 5.72, w: 11.1, h: 0.62, fontSize: 12.5, fontFace: SANS,
      lineSpacing: 17, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 12 · BLOCO 3 — Renato                                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  abrirBloco(s, {
    numero: 3, quem: "Renato", papel: "RESULTADO E RISCO", minutos: 4,
    afirmacao: "O retorno sobrevive aos três cenários,\ne sabemos exatamente onde ele quebra",
    razoes: [
      "Projetamos em três cenários de aceite, não em um — porque a submissão é única e a reação do cliente é desconhecida",
      "Escolhemos 12,7% de folga até o limite mais apertado, em vez do ROI máximo disponível",
      "A meta de 15% não é alcançável dentro dos guard-rails, e medimos isso em vez de argumentar",
    ],
  });
}

/* ========================================================================== */
/* 13 · Renato 1 — os três cenários                                            */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "1 · Três cenários, porque submetemos uma vez",
         "A Base C reage às nossas decisões, e a intensidade dessa reação não é revelada");

  const linhas = [
    ["", "Otimista", "Central", "Pessimista", "Guard-rail"],
    ["Taxa de aprovação", "59,5%", "59,5%", "59,5%", "mínimo de 35%"],
    ["Volume originado", "R$ 86,1 mi", "R$ 66,7 mi", "R$ 45,1 mi", "mínimo de R$ 40 mi"],
    ["Inadimplência", "6,2%", "6,3%", "6,6%", "máximo de 8%"],
    ["Taxa média ao mês", "1,91%", "1,91%", "1,91%", "teto de 3,5%"],
    ["ROI anualizado", "11,5%", "11,3%", "11,1%", "meta acima de 15%"],
  ];
  const cx = [M + 0.35, M + 3.6, M + 5.5, M + 7.4, M + 9.5];
  const cw = [3.1, 1.8, 1.8, 1.8, 2.3];

  cartao(s, { x: M, y: 1.95, w: 11.9, h: 2.6, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = 2.12 + r * 0.375;
    const cab = r === 0;
    const roi = linha[0] === "ROI anualizado";
    if (cab) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.1, y: y - 0.04, w: 11.7, h: 0.35,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
    } else if (roi) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.1, y: y - 0.04, w: 11.7, h: 0.35,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((cel, c) => {
      s.addText(cel, {
        x: cx[c], y, w: cw[c], h: 0.3,
        fontSize: cab ? 11 : 12.5, bold: cab || c === 0 || roi,
        color: cab ? WHITE : (c === 4 ? GREY : NAVY), fontFace: SANS,
        align: c === 0 ? "left" : (c === 4 ? "left" : "center"),
        isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: M, y: 4.75, w: 5.75, h: 1.6, fill: WHITE });
  s.addText("O ROI varia pouco. O volume, muito.", {
    x: M + 0.35, y: 4.95, w: 5.05, h: 0.35,
    fontSize: 15, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "O ROI é uma razão, e o aceite move numerador e denominador juntos. Foi pelo volume que medimos a folga — é ele que separa uma política robusta de uma que deu certo por pouco.",
    { x: M + 0.35, y: 5.35, w: 5.05, h: 0.9, fontSize: 12, color: GREY, fontFace: SANS,
      lineSpacing: 16, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 4.75, w: 5.75, h: 1.6, fill: NAVY, linha: NAVY });
  s.addText("12,7% de folga, por escolha", {
    x: M + 6.5, y: 4.95, w: 5.05, h: 0.35,
    fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "O ROI máximo viável era 0,1 ponto maior e deixava metade dessa margem. Violar um guard-rail corta a nota de política pela metade — o ganho era pequeno e certo, o risco grande e binário.",
    { x: M + 6.5, y: 5.35, w: 5.05, h: 0.9, fontSize: 12, color: GREY_ESCURO, fontFace: SANS,
      lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 14 · Renato 2 — a pergunta dos 15%                                          */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("A PERGUNTA QUE ESPERAMOS", {
    x: M, y: 0.6, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s.addText("Por que 11,3% e não os 15% que o conselho pede", {
    x: M, y: 1.0, w: 11.5, h: 0.7,
    fontSize: 32, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("Fomos medir, em vez de argumentar.", {
    x: M, y: 1.72, w: 11, h: 0.4,
    fontSize: 14, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  [
    { v: "5.600", r: "políticas varridas\ncorte × preço × prazo × entrada" },
    { v: "4.044", r: "batem a meta\nde 15% de ROI" },
    { v: "0", r: "delas são\nviáveis", cor: CORAL },
    { v: "11,46%", r: "o teto compatível\ncom os quatro limites" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 2.95, y: 2.4, w: 2.7, valor: d.v, rotulo: d.r,
                 cor: d.cor || WHITE, tamanho: 36, corRotulo: GREY_ESCURO });
  });

  cartao(s, { x: M, y: 4.0, w: 5.75, h: 2.45, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("Um único limite bloqueia a meta", {
    x: M + 0.35, y: 4.2, w: 5.05, h: 0.38,
    fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    ["Inadimplência", "mínimo de 5,26%", "máx. 8%", true],
    ["Taxa de aprovação", "máximo de 68,7%", "mín. 35%", true],
    ["Volume originado", "máximo de R$ 20,5 mi", "mín. R$ 40 mi", false],
  ].forEach((l, i) => {
    const y = 4.72 + i * 0.5;
    s.addText(l[3] ? "✓" : "✕", {
      x: M + 0.35, y, w: 0.3, h: 0.3,
      fontSize: 14, bold: true, color: l[3] ? TEAL : CORAL, fontFace: SANS,
      isTextBox: true, margin: 0,
    });
    s.addText(l[0], {
      x: M + 0.7, y, w: 1.9, h: 0.3,
      fontSize: 11.5, color: l[3] ? GREY_ESCURO : WHITE, bold: !l[3], fontFace: SANS,
      isTextBox: true, margin: 0,
    });
    s.addText(l[1], {
      x: M + 2.6, y, w: 1.8, h: 0.3,
      fontSize: 11.5, color: l[3] ? GREY_ESCURO : CORAL, bold: !l[3], fontFace: SANS,
      isTextBox: true, margin: 0,
    });
    s.addText(l[2], {
      x: M + 4.4, y, w: 1.05, h: 0.3,
      fontSize: 10.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
  s.addText("Risco e seletividade passam. Só o volume mata.", {
    x: M + 0.35, y: 6.1, w: 5.05, h: 0.3,
    fontSize: 12, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 6.15, y: 4.0, w: 5.75, h: 2.45, fill: CORAL, linha: CORAL });
  s.addText("5×", {
    x: M + 6.5, y: 4.2, w: 5.05, h: 0.8,
    fontSize: 46, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("menos sensível a preço", {
    x: M + 6.5, y: 5.0, w: 5.05, h: 0.3,
    fontSize: 14, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "é o quanto o cliente teria que ser para a primeira política de 15% sobreviver aos limites. Nesse mundo, cobrar 45% acima do mercado quase não afastaria ninguém — e o enunciado diz o contrário.",
    { x: M + 6.5, y: 5.38, w: 5.05, h: 1.0, fontSize: 12, color: CORAL_SOFT, fontFace: SANS,
      lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 15 · Renato 3 — riscos                                                      */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "3 · Onde este número quebra",
         "Quatro riscos, dois deles apontados no próprio enunciado — nomeá-los é mais barato que ser pego neles");

  const riscos = [
    { c: CORAL, t: "Inferência de rejeitados",
      d: "A Base C tem score de bureau 96 pontos menor e 2,7× mais restrições. A ordenação sobrevive à mudança de população; o nível da PD, não — e é o nível que vira preço.",
      m: "Daí parte da margem que deixamos." },
    { c: CORAL, t: "A elasticidade do aceite é premissa, não medida",
      d: "Assumimos que cobrar no teto de 3,5% deixaria aceite baixo mas não nulo, ancorados em que um teto só é guard-rail se as políticas quiserem chegar perto dele.",
      m: "Se o simulador for mais elástico, o volume frustra — e volume é guard-rail." },
    { c: TEAL, t: "As duas faixas aprovadas mais arriscadas rodam acima do limite",
      d: "A faixa 6 projeta 9,1% de inadimplência e a faixa 5, 13,3%, contra os 8% do guard-rail. Cabem porque as faixas boas diluem o conjunto, que fecha em 6,3%.",
      m: "Se a realizada surpreender, a correção é cortar em score 6." },
    { c: TEAL, t: "Deriva de safra",
      d: "A inadimplência caiu de 8,9% em 2023 para 7,2% em 2024. Se 2025 voltar ao patamar de 2023, a projeção sobe junto.",
      m: "O PSI contra a Base B é de 0,002 — estabilidade que vale o curto prazo." },
  ];

  riscos.forEach((r, i) => {
    const y = 1.9 + i * 1.22;
    cartao(s, { x: M, y, w: 11.9, h: 1.08, fill: WHITE });
    s.addShape(pres.ShapeType.rect, {
      x: M, y, w: 0.07, h: 1.08, fill: { color: r.c }, line: { color: r.c, width: 0 },
    });
    s.addText(r.t, {
      x: M + 0.32, y: y + 0.12, w: 11.3, h: 0.3,
      fontSize: 14.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(r.d, {
      x: M + 0.32, y: y + 0.44, w: 11.3, h: 0.4,
      fontSize: 11.5, color: GREY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0,
    });
    s.addText(r.m, {
      x: M + 0.32, y: y + 0.8, w: 11.3, h: 0.25,
      fontSize: 11, italic: true, color: r.c, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "São oito itens no total, documentados com o que pulamos, o risco que corremos e o que faríamos com mais tempo.");
}

/* ========================================================================== */
/* 16 · Fecho — a cadeia completa                                              */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O ENCADEAMENTO, DE PONTA A PONTA", {
    x: M, y: 0.7, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s.addText("Uma proposta vira um preço em seis passos", {
    x: M, y: 1.1, w: 11, h: 0.7,
    fontSize: 32, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const etapas = [
    { t: "PD", v: "XGBoost\n0,7234" },
    { t: "EAD", v: "tabela\n0,98 a 1,04" },
    { t: "LGD", v: "tabela\n~68% médio" },
    { t: "Perda", v: "1,34% a\n7,92%" },
    { t: "Preço", v: "1,634% a\n2,292%" },
    { t: "ROI", v: "11,3%\nao ano" },
  ];
  const largura = 1.78, gap = 0.24;
  etapas.forEach((e, i) => {
    const x = M + i * (largura + gap);
    const fim = i === 5;
    cartao(s, { x, y: 2.15, w: largura, h: 1.9, fill: fim ? CORAL : NAVY_MID,
                linha: fim ? CORAL : "3A5468" });
    s.addText(e.t, {
      x, y: 2.38, w: largura, h: 0.45,
      fontSize: 21, bold: true, color: WHITE, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0,
    });
    s.addText(e.v, {
      x: x + 0.1, y: 2.95, w: largura - 0.2, h: 0.8,
      fontSize: 11.5, bold: true, color: fim ? WHITE : GREY_ESCURO, fontFace: SANS,
      align: "center", lineSpacing: 15, isTextBox: true, margin: 0,
    });
    if (i < 5) {
      s.addText("›", {
        x: x + largura, y: 2.8, w: gap, h: 0.5,
        fontSize: 22, color: CORAL, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
      });
    }
  });

  cartao(s, { x: M, y: 4.35, w: 11.9, h: 1.5, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("Percorremos essa cadeia nos dois sentidos", {
    x: M + 0.4, y: 4.55, w: 11.1, h: 0.35,
    fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "→  ", options: { color: CORAL, bold: true } },
      { text: "«Por que esta proposta pagou 2,29%?»  ", options: { color: WHITE } },
      { text: "porque a PD dela caiu na faixa 5, cuja perda esperada é 7,92%, e a regra é 1,50% + 10% disso.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 4.97, w: 11.1, h: 0.3, fontSize: 12.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addText(
    [
      { text: "←  ", options: { color: CORAL, bold: true } },
      { text: "«De onde vêm os 11,3%?»  ", options: { color: WHITE } },
      { text: "da soma de 2.976 ofertas, ponderadas pela probabilidade de o cliente aceitar cada uma.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 5.33, w: 11.1, h: 0.3, fontSize: 12.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );

  s.addText(
    [
      { text: "3.000", options: { color: CORAL, bold: true } },
      { text: " PDs na Base B   ·   ", options: { color: GREY_ESCURO } },
      { text: "5.000", options: { color: CORAL, bold: true } },
      { text: " decisões na Base C   ·   ", options: { color: GREY_ESCURO } },
      { text: "167", options: { color: CORAL, bold: true } },
      { text: " testes automatizados   ·   ", options: { color: GREY_ESCURO } },
      { text: "0", options: { color: CORAL, bold: true } },
      { text: " passos manuais no caminho", options: { color: GREY_ESCURO } },
    ],
    { x: M, y: 6.15, w: W - 2 * M, h: 0.4, fontSize: 14, fontFace: SANS, align: "center",
      isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */

const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
// O nome do arquivo e o que o professor ve no anexo: sem numero de
// ordem interno e sem jargao de metodo.
const arquivo = path.join(destino, "AutoCred - Política de Crédito 2026 - Grupo 3.pptx");
pres.writeFile({ fileName: arquivo }).then(() => console.log("Gerado:", arquivo));
