/**
 * Apresentação 5 — Visão geral para o grupo.
 *
 * Público: os outros três integrantes do Grupo 3. NÃO é material de defesa —
 * é alinhamento interno, antes de juntarmos o que cada um fez.
 *
 * Por isso o tom muda: os outros quatro decks defendem decisões diante do
 * professor; este mostra o caminho inteiro, o que decidimos e por quê, onde
 * cada coisa está e o que ainda falta. Quem for defender precisa saber
 * reconstruir o raciocínio, não decorar números.
 *
 * Gerar:  node apresentacoes/_superados/05_visao_geral_grupo.js
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
pres.title = "AutoCred — Visão geral do que fizemos";

const cartao = (slide, opts) => C.cartao(pres, slide, opts);
const MONO = "Courier New";

/* ========================================================================== */
/* 1 · Capa                                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("DESAFIO AUTOCRED · GRUPO 3 · ALINHAMENTO INTERNO", {
    x: M, y: 1.75, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true, isTextBox: true, margin: 0,
  });
  s.addText("O caminho inteiro", {
    x: M, y: 2.2, w: W - 2 * M, h: 1.1,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Do dado bruto à submissão: o que decidimos, por que decidimos assim,\ne onde ainda estamos expostos",
    { x: M, y: 3.35, w: 9.6, h: 1.0, fontSize: 17, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 26, isTextBox: true, margin: 0 }
  );

  [
    { v: "12", r: "passos, do ETL\nao documento" },
    { v: "3", r: "entregáveis\nprontos" },
    { v: "167", r: "testes\nautomatizados" },
    { v: "11,3%", r: "ROI projetado\nno cenário central" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 2.95, y: 4.95, w: 2.7, valor: d.v, rotulo: d.r, cor: WHITE, tamanho: 34, corRotulo: GREY_ESCURO });
  });

  s.addText("Deni Alan  ·  Leonardo Wink  ·  Marcelo Félix  ·  Renato", {
    x: M, y: 6.6, w: W - 2 * M, h: 0.35,
    fontSize: 13, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */
/* 2 · As siglas                                                               */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "As siglas, antes de tudo", "Crédito é um campo com vocabulário próprio — vale fixar isto antes de olhar qualquer número");

  // A fórmula da perda, que é o eixo de tudo.
  cartao(s, { x: M, y: 1.9, w: 11.9, h: 2.15, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "EL", options: { color: CORAL, bold: true } },
      { text: "  =  ", options: { color: GREY_ESCURO } },
      { text: "PD", options: { color: WHITE, bold: true } },
      { text: "  ×  ", options: { color: GREY_ESCURO } },
      { text: "EAD", options: { color: WHITE, bold: true } },
      { text: "  ×  ", options: { color: GREY_ESCURO } },
      { text: "LGD", options: { color: WHITE, bold: true } },
    ],
    { x: M, y: 2.1, w: 11.9, h: 0.55, fontSize: 28, fontFace: SERIF, align: "center", isTextBox: true, margin: 0 }
  );
  s.addText("a conta que sustenta o preço de cada faixa", {
    x: M, y: 2.68, w: 11.9, h: 0.3,
    fontSize: 12.5, italic: true, color: GREY_ESCURO, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
  });

  [
    { g: "EL", n: "Expected Loss", d: "perda esperada — quanto,\nem média, se perde" },
    { g: "PD", n: "Probability of Default", d: "chance de o cliente\nficar 90 dias em atraso" },
    { g: "EAD", n: "Exposure at Default", d: "quanto ainda se deve\nna hora do calote" },
    { g: "LGD", n: "Loss Given Default", d: "quanto não se recupera\ndepois de tomar o carro" },
  ].forEach((x, i) => {
    const px = M + 0.35 + i * 2.87;
    s.addText(x.g, {
      x: px, y: 3.08, w: 2.7, h: 0.32,
      fontSize: 16, bold: true, color: CORAL, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(x.n, {
      x: px, y: 3.4, w: 2.7, h: 0.26,
      fontSize: 10.5, italic: true, color: WHITE, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(x.d, {
      x: px, y: 3.64, w: 2.7, h: 0.4,
      fontSize: 10.5, color: GREY_ESCURO, fontFace: SANS, align: "center", lineSpacing: 13, isTextBox: true, margin: 0,
    });
  });

  // As outras, em dois blocos.
  const blocos = [
    {
      t: "Como se mede um modelo",
      itens: [
        ["AuROC", "de 0,5 (chute) a 1,0 (perfeito): o quanto o modelo ordena bem quem vai quebrar"],
        ["KS", "a maior distância entre as curvas de bons e maus — quanto ele separa os dois"],
        ["PSI", "deriva: o quanto a população mudou entre duas bases. Acima de 0,25 é muita"],
        ["Brier", "calibração: se o modelo diz 7%, quebram 7% — e não 42%"],
      ],
    },
    {
      t: "Como se descreve um contrato",
      itens: [
        ["LTV", "Loan to Value: quanto do carro está financiado. Entrada de 10% dá LTV de 90%"],
        ["ROI", "aqui sempre anualizado: (juros − perda) ÷ volume ÷ prazo em anos"],
        ["CET", "Custo Efetivo Total — o teto regulatório de 3,5% ao mês é sobre ele"],
        ["a.m.", "ao mês. Uma taxa de 1,63% a.m. é ~21% ao ano"],
      ],
    },
  ];

  blocos.forEach((b, i) => {
    const x = M + i * 6.15;
    cartao(s, { x, y: 4.25, w: 5.75, h: 2.4, fill: WHITE });
    s.addText(b.t, {
      x: x + 0.35, y: 4.45, w: 5.05, h: 0.32,
      fontSize: 14.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    b.itens.forEach((it, j) => {
      const y = 4.85 + j * 0.45;
      s.addText(it[0], {
        x: x + 0.35, y, w: 0.85, h: 0.3,
        fontSize: 12, bold: true, color: CORAL, fontFace: MONO, isTextBox: true, margin: 0,
      });
      s.addText(it[1], {
        x: x + 1.25, y, w: 4.15, h: 0.42,
        fontSize: 10.5, color: GREY, fontFace: SANS, lineSpacing: 13, isTextBox: true, margin: 0,
      });
    });
  });
}

/* ========================================================================== */
/* 3 · O que está pronto                                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O que já existe", "Os três artefatos que vão para o professor — todos gerados por pipeline, nenhum passo manual");

  const itens = [
    {
      n: "1", t: "submissao_modelo.csv", sub: "Entregável 1 · 40 pontos",
      d: "3.000 linhas com a PD de cada contrato da Base B. XGBoost, AuROC 0,7234 na validação de 2024.",
    },
    {
      n: "2", t: "submissao_politica.csv", sub: "Entregável 2 · 40 pontos",
      d: "5.000 decisões na Base C. 59,5% aprovadas, taxa de 1,634% a 2,292% a.m., prazo 48m, entrada 10%.",
    },
    {
      n: "3", t: "documento_politica_AutoCred.docx", sub: "Defesa · 20 pontos",
      d: "3 páginas no template do professor. Cada número vem do pipeline na hora da geração.",
    },
  ];

  itens.forEach((it, i) => {
    const y = 1.95 + i * 1.55;
    cartao(s, { x: M, y, w: 11.9, h: 1.35, fill: WHITE });
    s.addShape(pres.ShapeType.ellipse, {
      x: M + 0.35, y: y + 0.4, w: 0.55, h: 0.55, fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(it.n, {
      x: M + 0.35, y: y + 0.47, w: 0.55, h: 0.4,
      fontSize: 18, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(it.t, {
      x: M + 1.15, y: y + 0.22, w: 5.2, h: 0.35,
      fontSize: 16, bold: true, color: NAVY, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(it.sub, {
      x: M + 1.15, y: y + 0.62, w: 5.2, h: 0.3,
      fontSize: 12, color: CORAL, fontFace: SANS, bold: true, isTextBox: true, margin: 0,
    });
    s.addText(it.d, {
      x: M + 6.6, y: y + 0.25, w: 4.9, h: 0.9,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "Rodar qualquer um deles de novo reproduz o arquivo byte a byte — não há número digitado à mão em lugar nenhum.");
}

/* ========================================================================== */
/* 3 · O encadeamento — o que vale os 20 pontos da defesa                      */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O ENCADEAMENTO", {
    x: M, y: 0.6, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Uma proposta vira um preço em seis passos", {
    x: M, y: 1.0, w: 11, h: 0.7,
    fontSize: 34, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "É esta cadeia que o professor disse que decide o desafio. Quem defender precisa percorrê-la nos dois sentidos.",
    { x: M, y: 1.72, w: 11, h: 0.4, fontSize: 14, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0 }
  );

  const etapas = [
    { t: "PD", d: "probabilidade\nde calote", v: "XGBoost\n0,7234 AuROC" },
    { t: "EAD", d: "quanto estará\nexposto", v: "tabela do prof.\n0,98 a 1,04" },
    { t: "LGD", d: "quanto se perde\nse calotear", v: "tabela do prof.\n~70% médio" },
    { t: "Perda", d: "PD × EAD × LGD", v: "1,34% a 7,92%\npor faixa" },
    { t: "Preço", d: "1,50% + 10%\nda perda", v: "1,634% a\n2,292% a.m." },
    { t: "ROI", d: "(juros − perda)\n÷ volume ÷ anos", v: "11,3%\nno central" },
  ];

  const largura = 1.78;
  const gap = 0.24;
  etapas.forEach((e, i) => {
    const x = M + i * (largura + gap);
    const destaque = i === 5;
    cartao(s, { x, y: 2.45, w: largura, h: 2.6, fill: destaque ? CORAL : NAVY_MID, linha: destaque ? CORAL : "3A5468" });
    s.addText(e.t, {
      x, y: 2.65, w: largura, h: 0.45,
      fontSize: 22, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(e.d, {
      x: x + 0.1, y: 3.18, w: largura - 0.2, h: 0.8,
      fontSize: 11, color: destaque ? CORAL_SOFT : GREY_ESCURO, fontFace: SANS, align: "center", lineSpacing: 14, isTextBox: true, margin: 0,
    });
    s.addText(e.v, {
      x: x + 0.1, y: 4.12, w: largura - 0.2, h: 0.75,
      fontSize: 11.5, bold: true, color: WHITE, fontFace: SANS, align: "center", lineSpacing: 15, isTextBox: true, margin: 0,
    });
    if (i < 5) {
      s.addText("›", {
        x: x + largura, y: 3.35, w: gap, h: 0.5,
        fontSize: 22, color: CORAL, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
      });
    }
  });

  cartao(s, { x: M, y: 5.35, w: 11.9, h: 1.35, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("Os dois sentidos que precisamos saber responder", {
    x: M + 0.4, y: 5.55, w: 11.1, h: 0.35,
    fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "→  ", options: { color: CORAL, bold: true } },
      { text: "«Por que esta proposta pagou 2,29%?»  ", options: { color: WHITE } },
      { text: "porque a PD dela caiu na faixa 5, cuja perda esperada é 7,92%, e a regra é 1,50% + 10% disso.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 5.95, w: 11.1, h: 0.3, fontSize: 12.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addText(
    [
      { text: "←  ", options: { color: CORAL, bold: true } },
      { text: "«De onde vêm os 11,3%?»  ", options: { color: WHITE } },
      { text: "da soma de 2.976 ofertas aceitas, ponderadas pela probabilidade de o cliente aceitar cada uma.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 6.28, w: 11.1, h: 0.3, fontSize: 12.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 4 · A metodologia                                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Como trabalhamos", "Spec Driven Development — a spec antes do código, e o DoD como fração verificável");

  cartao(s, { x: M, y: 1.95, w: 5.75, h: 2.35, fill: WHITE });
  s.addText("A regra", {
    x: M + 0.35, y: 2.15, w: 5.05, h: 0.35,
    fontSize: 17, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Nenhum passo começa sem uma spec que diga ", options: {} },
      { text: "o que é, por que existe, como faremos", options: { bold: true } },
      { text: " e ", options: {} },
      { text: "pronto quando", options: { bold: true } },
      { text: ". O «pronto quando» é uma lista de itens conferíveis, não uma opinião — por isso aparece como fração: 3/3, 5/5.", options: {} },
    ],
    { x: M + 0.35, y: 2.6, w: 5.05, h: 1.5, fontSize: 13, color: GREY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 1.95, w: 5.75, h: 2.35, fill: WHITE });
  s.addText("Por que isso importa aqui", {
    x: M + 6.5, y: 2.15, w: 5.05, h: 0.35,
    fontSize: 17, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Modelagem de crédito tem muita decisão que parece detalhe e não é. Escrever o critério ", options: {} },
      { text: "antes de ver o resultado", options: { bold: true, color: CORAL } },
      { text: " impede a gente de racionalizar depois. Foi assim que escolhemos o modelo e a política.", options: {} },
    ],
    { x: M + 6.5, y: 2.6, w: 5.05, h: 1.5, fontSize: 13, color: GREY, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  const passos = [
    ["S01–S02", "ETL e parâmetros", "as três bases, e as tabelas de EAD/LGD do professor validadas"],
    ["S03–S05", "EDA e modelos", "a armadilha encontrada, logística de base, XGBoost e RF desafiantes"],
    ["S06–S07", "Submissão e score", "PD na Base B, e os cortes que viram as 10 faixas"],
    ["S08–S09", "ROI e política", "o motor de simulação, e a busca da tabela de preços"],
    ["S10–S12", "Entrega e defesa", "CSV da política, documento, e a fronteira ROI × volume"],
  ];

  passos.forEach((p, i) => {
    const y = 4.55 + i * 0.44;
    s.addText(p[0], {
      x: M, y, w: 1.15, h: 0.36,
      fontSize: 12, bold: true, color: CORAL, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(p[1], {
      x: M + 1.2, y, w: 2.5, h: 0.36,
      fontSize: 12.5, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(p[2], {
      x: M + 3.8, y, w: 8.1, h: 0.36,
      fontSize: 12.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
}

/* ========================================================================== */
/* 5 · A armadilha                                                             */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "A armadilha que quase pegou", "Uma coluna que parece a melhor preditora do conjunto — e destrói o modelo em silêncio");

  cartao(s, { x: M, y: 1.95, w: 11.9, h: 1.25, fill: NAVY, linha: NAVY });
  s.addText("qtd_parcelas_em_atraso_12m", {
    x: M + 0.4, y: 2.15, w: 6, h: 0.42,
    fontSize: 20, bold: true, color: WHITE, fontFace: MONO, isTextBox: true, margin: 0,
  });
  s.addText("correlação de 0,74 com o alvo na base de desenvolvimento", {
    x: M + 0.4, y: 2.62, w: 6.5, h: 0.35,
    fontSize: 13.5, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "e vale ZERO em toda linha das bases B e C", options: { color: CORAL, bold: true } },
    ],
    { x: M + 7.3, y: 2.35, w: 4.2, h: 0.45, fontSize: 16, fontFace: SANS, align: "right", isTextBox: true, margin: 0 }
  );

  const colunas = [
    {
      t: "Por que ela engana",
      d: "É a variável mais correlacionada com o alvo. Qualquer seleção automática a escolhe primeiro, e o AuROC de treino fica ótimo.",
      cor: NAVY,
    },
    {
      t: "Por que ela destrói",
      d: "É pós-concessão: só existe depois que o contrato começou. Na hora de decidir, ela não existe — por isso vale zero nas bases de aplicação.",
      cor: NAVY,
    },
    {
      t: "O que aconteceria",
      d: "O modelo apoiaria a decisão numa coluna constante, e o AuROC despencaria para ~0,50 na Base B. Sem erro, sem aviso, sem exceção.",
      cor: CORAL,
    },
  ];

  colunas.forEach((c, i) => {
    const x = M + i * 4.03;
    cartao(s, { x, y: 3.45, w: 3.83, h: 2.2, fill: WHITE });
    s.addText(c.t, {
      x: x + 0.28, y: 3.68, w: 3.3, h: 0.38,
      fontSize: 15.5, bold: true, color: c.cor, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(c.d, {
      x: x + 0.28, y: 4.12, w: 3.3, h: 1.4,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 5.85, w: 11.9, h: 0.85, fill: CORAL_SOFT, linha: CORAL });
  s.addText(
    [
      { text: "Como nos protegemos:  ", options: { bold: true, color: NAVY } },
      { text: "a coluna sai na ingestão, e existe um teste que falha se ela reaparecer. ", options: { color: NAVY } },
      { text: "Mais três foram descartadas pelo mesmo raciocínio — taxa_juros_am, parcela_mensal e comprometimento_renda.", options: { color: GREY } },
    ],
    { x: M + 0.4, y: 6.07, w: 11.1, h: 0.45, fontSize: 13, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 6 · As decisões do modelo                                                   */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "As três decisões do modelo", "Cada uma com o critério escrito antes de rodar");

  const decisoes = [
    {
      t: "Split temporal, não 70/30 aleatório",
      d: "Treino 2022–2023, validação 2024. A aplicação real é out-of-time: vamos escorar contratos futuros. Split aleatório mediria a coisa errada e daria um número mais bonito.",
      n: "6.670 / 3.330",
    },
    {
      t: "XGBoost, e não só por AuROC",
      d: "Ganhou nas duas medidas: 0,6948 na validação cruzada temporal e 0,7234 na validação de 2024, contra 0,6391 e 0,6489 da logística. Ganhar nas duas afasta a hipótese de sorte.",
      n: "0,7234",
    },
    {
      t: "Random Forest descartado por calibração",
      d: "AuROC 0,7159, tecnicamente empatado. Mas projetava PD média de 42,3% contra 7,2% reais. Para ordenar risco não atrapalha; para precificar, inviabiliza — a perda é PD × EAD × LGD.",
      n: "42,3% vs 7,2%",
    },
  ];

  decisoes.forEach((d, i) => {
    const y = 1.95 + i * 1.6;
    cartao(s, { x: M, y, w: 11.9, h: 1.4, fill: WHITE });
    s.addText(d.t, {
      x: M + 0.4, y: y + 0.22, w: 7.8, h: 0.38,
      fontSize: 16.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(d.d, {
      x: M + 0.4, y: y + 0.65, w: 7.8, h: 0.65,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
    s.addText(d.n, {
      x: M + 8.5, y: y + 0.42, w: 3.0, h: 0.6,
      fontSize: 22, bold: true, color: CORAL, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
  });

  fecho(s, "O que nos protege do «escolhemos porque deu certo»: em todos os três casos, o critério estava escrito na spec antes de existir resultado.");
}

/* ========================================================================== */
/* 7 · Do score à política                                                     */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Do score ao preço", "Duas decisões que sustentam toda a política");

  cartao(s, { x: M, y: 1.95, w: 5.75, h: 2.5, fill: WHITE });
  s.addText("1 · Cortes absolutos, não quantis", {
    x: M + 0.35, y: 2.15, w: 5.05, h: 0.38,
    fontSize: 17, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Quantil é mais simples, mas o significado da faixa muda quando a população muda — e a Base C ", options: {} },
      { text: "é outra população", options: { bold: true, color: CORAL } },
      { text: " (PSI de 5,93 em restrições ativas). Com corte absoluto, «faixa 5» significa «PD entre 9,5% e 13%» em qualquer base, e o preço dela é defensável em qualquer base.", options: {} },
    ],
    { x: M + 0.35, y: 2.6, w: 5.05, h: 1.7, fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M + 6.15, y: 1.95, w: 5.75, h: 2.5, fill: WHITE });
  s.addText("2 · Preço = 1,50% + 10% da perda", {
    x: M + 6.5, y: 2.15, w: 5.05, h: 0.38,
    fontSize: 17, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Uma conta que cabe em uma linha e se audita sozinha. Na faixa 8, que perde 2,92%: 1,50% + 0,29% = ", options: {} },
      { text: "1,792%", options: { bold: true, color: CORAL } },
      { text: ". Quem traz mais risco paga mais, e o quanto mais é proporcional ao risco que traz — não a um valor arbitrado.", options: {} },
    ],
    { x: M + 6.5, y: 2.6, w: 5.05, h: 1.7, fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 4.7, w: 11.9, h: 1.95, fill: NAVY, linha: NAVY });
  s.addText("O que estamos corrigindo na política de 2022", {
    x: M + 0.4, y: 4.92, w: 11.1, h: 0.4,
    fontSize: 19, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "A AutoCred cobrava ", options: { color: GREY_ESCURO } },
      { text: "1,57%", options: { color: WHITE, bold: true } },
      { text: " de quem tinha 0,2% de inadimplência e ", options: { color: GREY_ESCURO } },
      { text: "1,64%", options: { color: WHITE, bold: true } },
      { text: " de quem tinha 69,6%. Correlação entre taxa e risco: ", options: { color: GREY_ESCURO } },
      { text: "+0,125", options: { color: CORAL, bold: true } },
      { text: ".", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 5.4, w: 11.1, h: 0.4, fontSize: 14, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addText(
    "Isto é preço único para todo risco. Os bons pagavam pelos ruins e iam embora para o concorrente; sobravam os ruins. É seleção adversa, e é o que a nossa política ataca.",
    { x: M + 0.4, y: 5.85, w: 11.1, h: 0.65, fontSize: 13.5, color: WHITE, fontFace: SANS, lineSpacing: 19, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 8 · O motor de ROI e os três cenários                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Por que projetamos em três cenários", "A Base C reage às nossas decisões, e a intensidade dessa reação não é revelada");

  const reacoes = [
    { t: "Taxa alta afasta", d: "o cliente tem concorrente. Preço acima do mercado derruba o aceite, e proposta não aceita não gera receita nenhuma." },
    { t: "Taxa alta piora quem fica", d: "quem aceita pagar caro costuma ser quem não tem alternativa. Seleção adversa está no simulador." },
    { t: "Entrada reduz risco de verdade", d: "LTV menor significa PD e LGD menores. Mas cada ponto de entrada a mais também derruba o aceite." },
  ];

  reacoes.forEach((r, i) => {
    const x = M + i * 4.03;
    cartao(s, { x, y: 1.95, w: 3.83, h: 1.75, fill: WHITE });
    s.addText(r.t, {
      x: x + 0.28, y: 2.15, w: 3.3, h: 0.38,
      fontSize: 14.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(r.d, {
      x: x + 0.28, y: 2.58, w: 3.3, h: 1.0,
      fontSize: 12, color: GREY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 3.95, w: 11.9, h: 2.45, fill: WHITE });
  s.addText("Uma submissão só, e a reação é desconhecida — então a política tem de sobreviver aos três", {
    x: M + 0.4, y: 4.15, w: 11.1, h: 0.38,
    fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const linhas = [
    ["", "Otimista", "Central", "Pessimista", "Guard-rail"],
    ["ROI anualizado", "11,5%", "11,3%", "11,1%", "meta de 15%"],
    ["Volume originado", "R$ 86,1 mi", "R$ 66,7 mi", "R$ 45,1 mi", "mín. R$ 40 mi"],
    ["Inadimplência", "6,2%", "6,3%", "6,6%", "máx. 8%"],
    ["Taxa de aprovação", "59,5%", "59,5%", "59,5%", "mín. 35%"],
  ];

  const colX = [M + 0.4, M + 3.5, M + 5.3, M + 7.1, M + 9.2];
  const colW = [3.0, 1.7, 1.7, 1.7, 2.3];

  linhas.forEach((linha, r) => {
    const y = 4.55 + r * 0.355;
    const cabecalho = r === 0;
    if (r === 1) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.3, y: y - 0.03, w: 11.3, h: 0.34,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((celula, c) => {
      s.addText(celula, {
        x: colX[c], y, w: colW[c], h: 0.32,
        fontSize: cabecalho ? 11.5 : 12.5,
        bold: cabecalho || c === 0 || r === 1,
        color: cabecalho ? GREY : (c === 4 ? GREY : NAVY),
        fontFace: SANS,
        align: c === 0 ? "left" : (c === 4 ? "left" : "center"),
        isTextBox: true, margin: 0,
      });
    });
  });

  fecho(s, "O ROI varia pouco porque é uma razão — o aceite move os dois lados. O que varia é o volume, e é por ele que medimos a folga.");
}

/* ========================================================================== */
/* 9 · Como escolhemos a política                                              */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Como a política foi escolhida", "Critério declarado na spec antes de a busca rodar — e um desempate que não é o óbvio");

  const criterios = [
    { n: "1", t: "Descartar quem viola", d: "qualquer guard-rail, em qualquer um dos três cenários. Sobraram 106 de 5.600." },
    { n: "2", t: "Maximizar o ROI central", d: "entre as sobreviventes. O teto encontrado foi 11,46%." },
    { n: "3", t: "Desempatar por folga", d: "distância até o guard-rail mais apertado, no pior cenário. Ficamos com 12,7%." },
  ];

  criterios.forEach((c, i) => {
    const x = M + i * 4.03;
    cartao(s, { x, y: 1.95, w: 3.83, h: 1.95, fill: i === 2 ? NAVY : WHITE, linha: i === 2 ? NAVY : GREY_LIGHT });
    s.addText(c.n, {
      x: x + 0.28, y: 2.15, w: 0.5, h: 0.45,
      fontSize: 24, bold: true, color: CORAL, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(c.t, {
      x: x + 0.85, y: 2.22, w: 2.75, h: 0.38,
      fontSize: 14.5, bold: true, color: i === 2 ? WHITE : NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(c.d, {
      x: x + 0.28, y: 2.78, w: 3.3, h: 1.0,
      fontSize: 12, color: i === 2 ? GREY_ESCURO : GREY, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 4.15, w: 11.9, h: 1.3, fill: CORAL_SOFT, linha: CORAL });
  s.addText("Por que o critério 3 existe — e por que ele é o mais importante", {
    x: M + 0.4, y: 4.35, w: 11.1, h: 0.35,
    fontSize: 15.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Uma política que entrega 0,1 ponto a mais de ROI e fica a 0,2 ponto de furar o volume é pior que a alternativa: o ganho é pequeno e certo, o risco é grande e binário. Violar um guard-rail corta a nota de política pela metade — 20 pontos — para ganhar menos de 1.",
    { x: M + 0.4, y: 4.72, w: 11.1, h: 0.65, fontSize: 13, color: NAVY, fontFace: SANS, lineSpacing: 18, isTextBox: true, margin: 0 }
  );

  s.addText("A política escolhida", {
    x: M, y: 5.7, w: 3.2, h: 0.35,
    fontSize: 14, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    { v: "score ≥ 5", r: "aprovamos 59,5%" },
    { v: "1,63–2,29%", r: "taxa ao mês" },
    { v: "48 meses", r: "prazo máximo" },
    { v: "10%", r: "entrada mínima" },
  ].forEach((d, i) => {
    numerao(s, { x: M + 3.4 + i * 2.15, y: 5.6, w: 2.0, valor: d.v, rotulo: d.r, cor: NAVY, tamanho: 19, corRotulo: GREY });
  });
}

/* ========================================================================== */
/* 10 · Quem aprovamos e quem negamos                                          */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };

  s.addText("QUEM APROVAMOS E QUEM NEGAMOS", {
    x: M, y: 0.45, w: W - 2 * M, h: 0.3,
    fontSize: 11.5, bold: true, color: TEAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Aprovamos 59,5% das propostas: bureau 206 pontos mais alto, renda 70% maior e um terço das restrições", {
    x: M, y: 0.8, w: W - 2 * M, h: 0.85,
    fontSize: 25, bold: true, color: NAVY, fontFace: SERIF, lineSpacing: 30, isTextBox: true, margin: 0,
  });

  // --- a tabela, à esquerda ---
  const TX = M;
  const TW = 8.45;
  const colX = [TX + 0.25, TX + 4.3, TX + 6.4];
  const colW = [3.9, 2.0, 2.0];

  const linhas = [
    ["Indicador  (média do grupo)", "Aprovados  (score 5 a 10)", "Negados  (score 1 a 4)"],
    ["Propostas", "2.976  (59,5%)", "2.024  (40,5%)"],
    ["PD média", "5,9%", "28,0%"],
    ["Score de bureau médio", "634", "428"],
    ["Renda mediana", "R$ 5.076", "R$ 2.981"],
    ["Com restrição ativa", "49%", "91%"],
    ["Autônomos", "17,5%", "30,7%"],
    ["Fora do domínio de treino", "12%", "72%"],
  ];

  const ALT = 0.485;
  cartao(s, { x: TX, y: 1.85, w: TW, h: ALT * linhas.length + 0.1, fill: WHITE });

  linhas.forEach((linha, r) => {
    const y = 1.9 + r * ALT;
    const cab = r === 0;
    const destaque = linha[0] === "Fora do domínio de treino";

    if (cab) {
      s.addShape(pres.ShapeType.rect, {
        x: TX + 0.05, y: y, w: TW - 0.1, h: ALT,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
    } else if (destaque) {
      s.addShape(pres.ShapeType.rect, {
        x: TX + 0.05, y: y, w: TW - 0.1, h: ALT,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    } else if (r % 2 === 0) {
      s.addShape(pres.ShapeType.rect, {
        x: TX + 0.05, y: y, w: TW - 0.1, h: ALT,
        fill: { color: "F7F9FA" }, line: { color: "F7F9FA", width: 0 },
      });
    }

    linha.forEach((cel, c) => {
      s.addText(cel, {
        x: colX[c], y: y + 0.11, w: colW[c], h: 0.3,
        fontSize: cab ? 11 : 12.5,
        bold: cab || c === 0 || destaque,
        color: cab ? WHITE : NAVY,
        fontFace: SANS,
        align: c === 0 ? "left" : "center",
        isTextBox: true, margin: 0,
      });
    });
  });

  s.addText("Cada coluna resume um grupo inteiro de propostas: são médias, não um cliente só.", {
    x: TX + 0.25, y: 1.85 + ALT * linhas.length + 0.18, w: TW - 0.5, h: 0.3,
    fontSize: 11, italic: true, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });

  // --- a coluna de perguntas, à direita ---
  const QX = M + 8.95;
  const QW = 2.95;

  s.addText("O QUE A BANCA VAI PERGUNTAR", {
    x: QX, y: 1.9, w: QW, h: 0.3,
    fontSize: 10.5, bold: true, color: TEAL, fontFace: SANS, charSpacing: 1.5, isTextBox: true, margin: 0,
  });
  s.addText(
    "Explicar por que aprovou quem aprovou e por que cobrou o que cobrou vale 20 pontos.",
    { x: QX, y: 2.22, w: QW, h: 0.65, fontSize: 11.5, color: NAVY, fontFace: SANS, lineSpacing: 15, isTextBox: true, margin: 0 }
  );

  s.addShape(pres.ShapeType.line, {
    x: QX, y: 2.95, w: QW, h: 0,
    line: { color: GREY_LIGHT, width: 1 },
  });

  const perguntas = [
    {
      q: "Por que negar o score 4, com PD de 15,3%?",
      a: "A perda esperada da faixa é 11,18%. A nossa regra cobraria 2,62% ao mês para cobri-la — 65% acima do mercado de 1,59%, onde quase ninguém aceita.",
    },
    {
      q: "Mas aprovar o score 4 não daria mais ROI?",
      a: "Daria: 11,42% contra 11,33%. Recusamos 0,09 ponto para manter 12,7% de folga até o guard-rail, em vez de 7,6%.",
    },
    {
      q: "Os negados são só o perfil fora do domínio?",
      a: "Não. 72% deles estão fora, mas 28% são perfis que o modelo conhece bem — e mesmo assim têm PD alta.",
    },
  ];

  let qy = 3.1;
  perguntas.forEach((pq) => {
    s.addText(pq.q, {
      x: QX, y: qy, w: QW, h: 0.5,
      fontSize: 11.5, bold: true, color: NAVY, fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
    });
    s.addText(pq.a, {
      x: QX, y: qy + 0.42, w: QW, h: 0.85,
      fontSize: 10.5, color: GREY, fontFace: SANS, lineSpacing: 13, isTextBox: true, margin: 0,
    });
    qy += 1.24;
  });
}

/* ========================================================================== */
/* 11 · O achado dos 15%                                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O ACHADO MAIS RECENTE", {
    x: M, y: 0.6, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Por que 11,3% e não os 15% que o professor pede", {
    x: M, y: 1.0, w: 11.5, h: 0.7,
    fontSize: 32, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "É a pergunta mais provável da banca. Fomos medir em vez de argumentar.",
    { x: M, y: 1.72, w: 11, h: 0.4, fontSize: 14, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0 }
  );

  [
    { v: "5.600", r: "políticas varridas\ncorte × preço × prazo × entrada" },
    { v: "4.044", r: "batem a meta\nde 15% de ROI" },
    { v: "0", r: "delas são\nviáveis", cor: CORAL },
    { v: "11,46%", r: "o teto compatível\ncom os guard-rails" },
  ].forEach((d, i) => {
    numerao(s, { x: M + i * 2.95, y: 2.45, w: 2.7, valor: d.v, rotulo: d.r, cor: d.cor || WHITE, tamanho: 36, corRotulo: GREY_ESCURO });
  });

  cartao(s, { x: M, y: 4.05, w: 5.75, h: 2.5, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("Um único guard-rail bloqueia a meta", {
    x: M + 0.35, y: 4.25, w: 5.05, h: 0.38,
    fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  [
    ["Inadimplência", "mínimo de 5,26%", "máx. 8%", true],
    ["Taxa de aprovação", "máximo de 68,7%", "mín. 35%", true],
    ["Volume originado", "máximo de R$ 20,5 mi", "mín. R$ 40 mi", false],
  ].forEach((l, i) => {
    const y = 4.78 + i * 0.52;
    s.addText(l[3] ? "✓" : "✕", {
      x: M + 0.35, y, w: 0.3, h: 0.32,
      fontSize: 14, bold: true, color: l[3] ? TEAL : CORAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(l[0], {
      x: M + 0.7, y, w: 1.9, h: 0.32,
      fontSize: 11.5, color: l[3] ? GREY_ESCURO : WHITE, bold: !l[3], fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(l[1], {
      x: M + 2.6, y, w: 1.75, h: 0.32,
      fontSize: 11.5, color: l[3] ? GREY_ESCURO : CORAL, bold: !l[3], fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(l[2], {
      x: M + 4.35, y, w: 1.1, h: 0.32,
      fontSize: 11, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
  s.addText("Risco e seletividade passam. Só o volume mata.", {
    x: M + 0.35, y: 6.15, w: 5.05, h: 0.32,
    fontSize: 12, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: M + 6.15, y: 4.05, w: 5.75, h: 2.5, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("E as alavancas óbvias não salvam", {
    x: M + 6.5, y: 4.25, w: 5.05, h: 0.38,
    fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Encurtar o prazo piora. ", options: { color: WHITE, bold: true } },
      { text: "A 24 meses o teto viável cai para 7,63% — na Tabela Price o saldo amortiza rápido, e os juros perdidos superam o ganho de dividir por menos anos.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 6.5, y: 4.75, w: 5.05, h: 0.85, fontSize: 12, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
  s.addText(
    [
      { text: "Mais entrada não compensa. ", options: { color: WHITE, bold: true } },
      { text: "Exigir 20% em vez de 10% rende 0,04 ponto de ROI e custa R$ 6 milhões de volume. Acima de 30% vira destrutivo; em 40% não sobra política viável.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 6.5, y: 5.68, w: 5.05, h: 0.85, fontSize: 12, fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 11 · O que ficou de fora                                                    */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O que deixamos de fazer", "Registrado por escrito — porque na defesa é melhor nomear o buraco do que ser pego nele");

  const itens = [
    {
      c: CORAL, t: "Inferência de rejeitados",
      d: "A Base C tem score de bureau 96 pontos menor e 2,7× mais restrições. A ordenação do modelo sobrevive à mudança de população; o nível da PD, não — e é o nível que vira preço.",
      m: "Mitigação: margem na política, e a PD tratada como ordenação confiável e nível suspeito.",
    },
    {
      c: CORAL, t: "As elasticidades da Base C são premissa",
      d: "O simulador não revela o quanto o cliente foge quando o preço sobe. Assumimos que cobrar no teto de 3,5% deixa aceite baixo mas não nulo — ancorados em que um teto só é guard-rail se as políticas quiserem chegar perto dele.",
      m: "Mitigação: três cenários, e a política escolhida sobrevive ao pior deles.",
    },
    {
      c: TEAL, t: "Feature engineering mínima e sem calibração formal",
      d: "Usamos as variáveis como vieram, sem cruzamentos. E não calibramos a PD com Platt ou isotônica — só verificamos que o XGBoost já saía próximo da frequência observada.",
      m: "Mitigação: o Brier foi conferido, e o RF foi descartado justamente por falhar aí.",
    },
  ];

  itens.forEach((it, i) => {
    const y = 1.95 + i * 1.58;
    cartao(s, { x: M, y, w: 11.9, h: 1.4, fill: WHITE });
    s.addShape(pres.ShapeType.rect, {
      x: M, y, w: 0.07, h: 1.4, fill: { color: it.c }, line: { color: it.c, width: 0 },
    });
    s.addText(it.t, {
      x: M + 0.35, y: y + 0.18, w: 11.2, h: 0.35,
      fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(it.d, {
      x: M + 0.35, y: y + 0.55, w: 11.2, h: 0.55,
      fontSize: 12.5, color: GREY, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
    s.addText(it.m, {
      x: M + 0.35, y: y + 1.06, w: 11.2, h: 0.3,
      fontSize: 12, italic: true, color: it.c, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  fecho(s, "São oito itens em docs/DEBITO_TECNICO.md — cada um com o risco que corremos e o que faríamos com mais tempo.");
}

/* ========================================================================== */
/* 12 · Onde está cada coisa                                                   */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "Onde está cada coisa", "Para quem quiser rodar, conferir ou aproveitar um pedaço");

  cartao(s, { x: M, y: 1.95, w: 5.75, h: 2.9, fill: WHITE });
  s.addText("O pipeline, na ordem", {
    x: M + 0.35, y: 2.15, w: 5.05, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    ["01–02", "etl/", "ingestão e parâmetros de EAD/LGD"],
    ["03–05", "modelagem/", "EDA, baseline e desafiantes"],
    ["06–07", "modelagem/", "submissão do modelo e faixas"],
    ["09–10", "modelagem/", "busca da política e submissão"],
    ["11", "relatorios/", "o documento de política"],
    ["12", "modelagem/", "a fronteira ROI × volume"],
  ].forEach((l, i) => {
    const y = 2.6 + i * 0.36;
    s.addText(l[0], {
      x: M + 0.35, y, w: 0.75, h: 0.3,
      fontSize: 11, bold: true, color: CORAL, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(l[1], {
      x: M + 1.15, y, w: 1.3, h: 0.3,
      fontSize: 11, color: NAVY, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(l[2], {
      x: M + 2.5, y, w: 2.9, h: 0.3,
      fontSize: 11, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M + 6.15, y: 1.95, w: 5.75, h: 2.9, fill: WHITE });
  s.addText("A documentação", {
    x: M + 6.5, y: 2.15, w: 5.05, h: 0.35,
    fontSize: 16, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    ["DESAFIO.md", "o briefing do professor, capturado fielmente"],
    ["ROADMAP.md", "os 12 passos, com DoD e status de cada um"],
    ["specs/S01..S12", "uma spec por passo — o porquê de cada decisão"],
    ["GLOSSARIO.md", "os termos de banking, para quem não tem o background"],
    ["DEBITO_TECNICO.md", "os oito itens que ficaram de fora"],
    ["DICIONARIO_DADOS.md", "as três bases, a armadilha e as colunas proibidas"],
  ].forEach((l, i) => {
    const y = 2.6 + i * 0.36;
    s.addText(l[0], {
      x: M + 6.5, y, w: 2.0, h: 0.3,
      fontSize: 10.5, bold: true, color: NAVY, fontFace: MONO, isTextBox: true, margin: 0,
    });
    s.addText(l[1], {
      x: M + 8.55, y, w: 3.0, h: 0.3,
      fontSize: 10.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: M, y: 5.1, w: 11.9, h: 1.5, fill: NAVY, linha: NAVY });
  s.addText("Para rodar tudo do zero", {
    x: M + 0.4, y: 5.3, w: 11.1, h: 0.35,
    fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    ".\\scripts\\setup_python.ps1        →  cria o ambiente e instala as dependências\n" +
    ".\\scripts\\py.cmd python\\etl\\01_ingestao.py    →  e assim por diante, na ordem numérica\n" +
    ".\\scripts\\py.cmd -m pytest        →  167 testes, incluindo os que guardam a armadilha",
    { x: M + 0.4, y: 5.72, w: 11.1, h: 0.8, fontSize: 11.5, color: GREY_ESCURO, fontFace: MONO, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 13 · O volume foi o problema?                                               */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: OFFWHITE };
  titulo(s, "O volume foi o problema?", "Não da nossa política — mas é ele que limita o que ela pode ambicionar");

  cartao(s, { x: M, y: 1.9, w: 11.9, h: 1.1, fill: WHITE });
  [
    { v: "R$ 167,1 mi", r: "teto teórico\ntodas aprovadas, aceite de 100%", cor: GREY },
    { v: "R$ 66,7 mi", r: "o que entregamos\n40% do teto", cor: NAVY },
    { v: "R$ 45,1 mi", r: "no pior cenário\nainda 12,7% de folga", cor: NAVY },
    { v: "R$ 40,0 mi", r: "o piso do guard-rail\n24% do teto", cor: CORAL },
  ].forEach((d, i) => {
    s.addText(d.v, {
      x: M + 0.3 + i * 2.87, y: 2.05, w: 2.7, h: 0.4,
      fontSize: 19, bold: true, color: d.cor, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(d.r, {
      x: M + 0.3 + i * 2.87, y: 2.45, w: 2.7, h: 0.45,
      fontSize: 10.5, color: GREY, fontFace: SANS, align: "center", lineSpacing: 13, isTextBox: true, margin: 0,
    });
  });

  s.addText("Movendo uma alavanca de cada vez, a partir da nossa política", {
    x: M, y: 3.15, w: 11.9, h: 0.32,
    fontSize: 14, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const linhas = [
    ["", "ROI", "vs hoje", "Volume", "vs hoje", ""],
    ["k de risco 0,10 → 0,00  (preço único)", "8,72%", "−2,60pp", "R$ 87,9 mi", "+21,2", "viável"],
    ["taxa base 1,50% → 1,25%", "9,63%", "−1,70pp", "R$ 79,6 mi", "+12,9", "viável"],
    ["corte score 5 → 4  (aprovar 68,7%)", "11,42%", "+0,09pp", "R$ 71,1 mi", "+4,4", "viável"],
    ["prazo 48 → 60 meses", "11,14%", "−0,19pp", "R$ 68,9 mi", "+2,2", "FURA"],
    ["entrada 10% → 0%", "11,24%", "−0,08pp", "R$ 67,7 mi", "+1,1", "viável"],
    ["nossa política", "11,33%", "—", "R$ 66,7 mi", "—", "viável"],
    ["taxa base 1,50% → 1,75%", "13,09%", "+1,76pp", "R$ 52,7 mi", "−14,0", "FURA"],
    ["k de risco 0,10 → 0,20", "13,54%", "+2,21pp", "R$ 48,0 mi", "−18,6", "FURA"],
  ];

  const cx = [M + 0.3, M + 5.0, M + 6.3, M + 7.6, M + 9.2, M + 10.4];
  const cw = [4.6, 1.2, 1.2, 1.5, 1.1, 1.3];

  linhas.forEach((linha, r) => {
    const y = 3.44 + r * 0.322;
    const cab = r === 0;
    const nossa = linha[0] === "nossa política";
    if (nossa) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.15, y: y - 0.03, w: 11.6, h: 0.31,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((cel, c) => {
      const fura = cel === "FURA";
      s.addText(cel, {
        x: cx[c], y, w: cw[c], h: 0.3,
        fontSize: cab ? 10.5 : 11.5,
        bold: cab || nossa || (c === 0),
        italic: cab,
        color: cab ? GREY : (fura ? CORAL : (c === 5 ? GREY : NAVY)),
        fontFace: SANS,
        align: c === 0 ? "left" : (c === 5 ? "left" : "right"),
        isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: M, y: 6.35, w: 11.9, h: 0.75, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "Só uma alavanca dá volume E ROI ao mesmo tempo:  ", options: { color: GREY_ESCURO } },
      { text: "baixar o corte para score 4", options: { color: WHITE, bold: true } },
      { text: "  (+R$ 4,4 mi e +0,09pp). Deixamos de fazer por folga: a de corte 4 sobra 7,7% até o guard-rail, a nossa sobra 12,7%.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 6.55, w: 11.1, h: 0.4, fontSize: 12, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 14 · O que precisaria ser verdade                                           */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("A PERGUNTA INVERTIDA", {
    x: M, y: 0.6, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("O que precisaria ser verdade para os 15% saírem", {
    x: M, y: 1.0, w: 11.5, h: 0.7,
    fontSize: 32, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Em vez de perguntar «qual política chega lá», perguntamos «que mundo teria que existir». Escalamos todas as elasticidades de aceite por um fator e refizemos a varredura.",
    { x: M, y: 1.72, w: 11.3, h: 0.45, fontSize: 13.5, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 2.35, w: 6.5, h: 3.2, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("Sensibilidade do cliente a preço", {
    x: M + 0.35, y: 2.55, w: 5.8, h: 0.32,
    fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const fs = [
    ["1,0 ×", "a nossa premissa", "11,42%", "0", false],
    ["0,5 ×", "metade", "13,87%", "0", false],
    ["0,3 ×", "um terço", "14,86%", "0", false],
    ["0,2 ×", "um quinto", "15,05%", "1", true],
    ["0,1 ×", "um décimo", "16,78%", "6", true],
  ];
  s.addText("fator", { x: M + 0.35, y: 2.95, w: 0.9, h: 0.25, fontSize: 9.5, italic: true, color: GREY, fontFace: SANS, isTextBox: true, margin: 0 });
  s.addText("melhor ROI viável", { x: M + 3.1, y: 2.95, w: 1.6, h: 0.25, fontSize: 9.5, italic: true, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0 });
  s.addText("com 15%", { x: M + 4.9, y: 2.95, w: 1.2, h: 0.25, fontSize: 9.5, italic: true, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0 });

  fs.forEach((l, i) => {
    const y = 3.28 + i * 0.43;
    if (l[4]) {
      s.addShape(pres.ShapeType.rect, {
        x: M + 0.25, y: y - 0.04, w: 5.95, h: 0.4,
        fill: { color: "3A2A2E" }, line: { color: "3A2A2E", width: 0 },
      });
    }
    s.addText(l[0], { x: M + 0.35, y, w: 0.9, h: 0.3, fontSize: 13, bold: true, color: l[4] ? CORAL : WHITE, fontFace: SANS, isTextBox: true, margin: 0 });
    s.addText(l[1], { x: M + 1.3, y: y + 0.02, w: 1.7, h: 0.3, fontSize: 11, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0 });
    s.addText(l[2], { x: M + 3.1, y, w: 1.6, h: 0.3, fontSize: 13, bold: true, color: l[4] ? CORAL : WHITE, fontFace: SANS, align: "right", isTextBox: true, margin: 0 });
    s.addText(l[3], { x: M + 4.9, y, w: 1.2, h: 0.3, fontSize: 13, bold: true, color: l[4] ? CORAL : GREY_ESCURO, fontFace: SANS, align: "right", isTextBox: true, margin: 0 });
  });

  cartao(s, { x: M + 6.9, y: 2.35, w: 5.0, h: 3.2, fill: CORAL, linha: CORAL });
  s.addText("5×", {
    x: M + 7.25, y: 2.6, w: 4.3, h: 0.85,
    fontSize: 52, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("menos sensível a preço", {
    x: M + 7.25, y: 3.45, w: 4.3, h: 0.3,
    fontSize: 14, bold: true, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(
    "é o quanto o cliente teria que ser para a primeira política de 15% sobreviver aos guard-rails. Nesse mundo, cobrar 45% acima do mercado quase não afastaria ninguém.",
    { x: M + 7.25, y: 3.85, w: 4.3, h: 1.3, fontSize: 12.5, color: CORAL_SOFT, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: M, y: 5.75, w: 11.9, h: 1.15, fill: NAVY_MID, linha: NAVY_MID });
  s.addText(
    [
      { text: "E o próprio enunciado diz o contrário:  ", options: { color: WHITE, bold: true } },
      { text: "«Taxa alta afasta o cliente. Ele tem concorrente. Preço acima do mercado derruba a taxa de aceite, e proposta não aceita não gera receita nenhuma.»", options: { color: GREY_ESCURO, italic: true } },
    ],
    { x: M + 0.4, y: 5.95, w: 11.1, h: 0.45, fontSize: 12.5, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0 }
  );
  s.addText(
    "A saída que sobra não é de política, é de modelo: prever melhor permite cobrar menos de quem merece e recusar melhor quem não merece — margem sem preço. É a única alavanca que não troca ROI por volume.",
    { x: M + 0.4, y: 6.4, w: 11.1, h: 0.4, fontSize: 12.5, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================================== */
/* 15 · O que falta — a conversa de hoje                                       */
/* ========================================================================== */
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addText("O QUE PRECISAMOS DECIDIR JUNTOS", {
    x: M, y: 1.1, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("A pauta de hoje", {
    x: M, y: 1.5, w: 10, h: 0.85,
    fontSize: 38, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });

  const pauta = [
    { t: "Comparar os resultados de cada frente", d: "combinamos que todos fariam tudo e juntaríamos o melhor de cada um. Vale comparar AuROC dos modelos e ROI das políticas antes de fixar a submissão." },
    { t: "Quem defende o quê", d: "o encadeamento PD → EAD → LGD → perda → preço → ROI vale 20 pontos e é a parte que o professor disse que decide o desafio." },
    { t: "A resposta sobre os 15%", d: "é a pergunta mais provável da banca. A resposta medida está pronta; falta combinarmos quem a dá e como." },
    { t: "Confirmar com o professor", d: "o e-mail de destino da entrega e o documento «AutoCred — Regras da Competição», citado no enunciado e ainda não recebido." },
  ];

  pauta.forEach((p, i) => {
    const y = 2.65 + i * 1.02;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.12, w: 0.42, h: 0.42, fill: { color: CORAL }, line: { color: CORAL, width: 0 },
    });
    s.addText(String(i + 1), {
      x: M, y: y + 0.17, w: 0.42, h: 0.32,
      fontSize: 14, bold: true, color: WHITE, fontFace: SERIF, align: "center", isTextBox: true, margin: 0,
    });
    s.addText(p.t, {
      x: M + 0.7, y: y + 0.05, w: 11.0, h: 0.35,
      fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(p.d, {
      x: M + 0.7, y: y + 0.44, w: 11.0, h: 0.5,
      fontSize: 12.5, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  s.addText("Prazo de entrega: 25/09 às 23h59  ·  leaderboard em 26/09", {
    x: M, y: 6.75, w: W - 2 * M, h: 0.35,
    fontSize: 13, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================================== */

const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
const arquivo = path.join(destino, "05_visao_geral_grupo.pptx");
pres.writeFile({ fileName: arquivo }).then(() => console.log("Gerado:", arquivo));
