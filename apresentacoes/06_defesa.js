/**
 * A defesa, ao professor e à banca. Vale os 20 pontos do bloco.
 *
 * Duas heranças, e elas se completam:
 *
 *   **Barbara Minto** dá o esqueleto. O título de cada slide é a AFIRMAÇÃO
 *   que ele sustenta — quem ler só os títulos, em ordem, recebe o argumento
 *   inteiro com os números dentro.
 *
 *   **A apresentação do Renato** dá a moldura de negócio: cada slide carrega
 *   a exigência do enunciado que atende e a pergunta que a banca faria ali,
 *   já respondida. E a narrativa parte de uma dor de mercado real — uma
 *   financeira que cresceu sem revisar a régua — em vez de partir do dado.
 *
 * ONZE SLIDES, para dez minutos. O que não cabe vira apêndice: material de
 * consulta para responder pergunta sem improviso, não slide de passagem.
 *
 * O slide 2 é o encadeamento inteiro. Ele vem antes de qualquer detalhe
 * porque é o mapa: quem o viu sabe onde cada slide seguinte se encaixa.
 *
 * Gerar:  node apresentacoes/06_defesa.js
 */

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const C = require("./_comum");
const L = require("./_defesa_layout");

const {
  NAVY, NAVY_MID, CORAL, CORAL_SOFT, OFFWHITE, WHITE, TEAL, GREY, GREY_LIGHT,
  GREY_ESCURO, SERIF, SANS, W, M,
} = C;
const { moldura, destaque, CORPO_L } = L;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Grupo 3";
pres.title = "AutoCred — Política de crédito 2026";

const cartao = (slide, opts) => C.cartao(pres, slide, opts);
const MONO = "Courier New";
let n = 0;
const slide = () => { n += 1; return pres.addSlide(); };

/* ========================================================== 1 · Capa */
{
  const s = slide();
  s.background = { color: NAVY };

  s.addText("MENTORIA · DESAFIO DE RISCO DE CRÉDITO · GRUPO 3", {
    x: M, y: 2.3, w: W - 2 * M, h: 0.4,
    fontSize: 13, color: CORAL, fontFace: SANS, charSpacing: 2, bold: true,
    isTextBox: true, margin: 0,
  });
  s.addText("AutoCred", {
    x: M, y: 2.75, w: W - 2 * M, h: 1.0,
    fontSize: 54, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("Nova política de concessão 2026:\nmodelo de PD e política de crédito", {
    x: M, y: 3.8, w: 10.5, h: 1.0,
    fontSize: 20, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 28,
    isTextBox: true, margin: 0,
  });

  s.addShape(pres.ShapeType.line, {
    x: M, y: 5.35, w: 4.2, h: 0, line: { color: CORAL, width: 2 },
  });

  s.addText("Deni Alan  ·  Leonardo Wink  ·  Marcelo Félix  ·  Renato", {
    x: M, y: 5.65, w: W - 2 * M, h: 0.3,
    fontSize: 14, color: WHITE, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText("Defesa da solução  ·  10 minutos", {
    x: M, y: 6.02, w: W - 2 * M, h: 0.3,
    fontSize: 12, italic: true, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================== 2 · Encadeamento */
{
  const s = slide();
  s.background = { color: NAVY };

  s.addText("O ENCADEAMENTO, DE PONTA A PONTA", {
    x: M, y: 0.6, w: W - 2 * M, h: 0.35,
    fontSize: 12, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s.addText("Uma proposta vira um preço em seis passos", {
    x: M, y: 1.0, w: 11, h: 0.7,
    fontSize: 32, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("Este é o mapa da apresentação: cada slide seguinte sustenta um destes passos.", {
    x: M, y: 1.72, w: 11, h: 0.35,
    fontSize: 13.5, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  const etapas = [
    { t: "PD", d: "probabilidade\nde calote", v: "XGBoost\n0,7234" },
    { t: "EAD", d: "quanto estará\nexposto", v: "tabela\n0,98 a 1,04" },
    { t: "LGD", d: "quanto não se\nrecupera", v: "tabela\n~68% médio" },
    { t: "Perda", d: "PD × EAD × LGD", v: "1,34% a\n7,92%" },
    { t: "Preço", d: "1,50% + 10%\nda perda", v: "1,634% a\n2,292%" },
    { t: "ROI", d: "(juros − perda)\n÷ volume ÷ anos", v: "11,3%\nao ano" },
  ];
  const largura = 1.78, gap = 0.24;
  etapas.forEach((e, i) => {
    const x = M + i * (largura + gap);
    const fim = i === 5;
    cartao(s, { x, y: 2.35, w: largura, h: 2.55,
                fill: fim ? CORAL : NAVY_MID, linha: fim ? CORAL : "3A5468" });
    s.addText(e.t, {
      x, y: 2.55, w: largura, h: 0.45,
      fontSize: 21, bold: true, color: WHITE, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0,
    });
    s.addText(e.d, {
      x: x + 0.1, y: 3.08, w: largura - 0.2, h: 0.75,
      fontSize: 10.5, color: fim ? CORAL_SOFT : GREY_ESCURO, fontFace: SANS,
      align: "center", lineSpacing: 14, isTextBox: true, margin: 0,
    });
    s.addText(e.v, {
      x: x + 0.1, y: 3.95, w: largura - 0.2, h: 0.75,
      fontSize: 11.5, bold: true, color: WHITE, fontFace: SANS, align: "center",
      lineSpacing: 15, isTextBox: true, margin: 0,
    });
    if (i < 5) {
      s.addText("›", {
        x: x + largura, y: 3.3, w: gap, h: 0.5,
        fontSize: 22, color: CORAL, fontFace: SANS, align: "center", isTextBox: true, margin: 0,
      });
    }
  });

  cartao(s, { x: M, y: 5.2, w: 11.9, h: 1.45, fill: NAVY_MID, linha: NAVY_MID });
  s.addText("A cadeia funciona nos dois sentidos, e é isso que defendemos", {
    x: M + 0.4, y: 5.38, w: 11.1, h: 0.35,
    fontSize: 15.5, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "→  ", options: { color: CORAL, bold: true } },
      { text: "«Por que esta proposta pagou 2,29%?»  ", options: { color: WHITE } },
      { text: "porque a PD dela caiu na faixa 5, cuja perda esperada é 7,92%, e a regra é 1,50% + 10% disso.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 5.8, w: 11.1, h: 0.3, fontSize: 12.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addText(
    [
      { text: "←  ", options: { color: CORAL, bold: true } },
      { text: "«De onde vêm os 11,3%?»  ", options: { color: WHITE } },
      { text: "da soma de 2.976 ofertas, ponderadas pela probabilidade de o cliente aceitar cada uma.", options: { color: GREY_ESCURO } },
    ],
    { x: M + 0.4, y: 6.16, w: 11.1, h: 0.3, fontSize: 12.5, fontFace: SANS, isTextBox: true, margin: 0 }
  );
  s.addText(String(n), {
    x: W - M - 0.5, y: 6.82, w: 0.5, h: 0.28,
    fontSize: 10, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
  });
}

/* ========================================================== 3 · Sumário */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "Sumário executivo",
    titulo: "Recomendamos aprovar 59,5% das propostas com preço proporcional ao risco,\ncom ROI de 11,3% ao ano e os quatro limites cumpridos nos três cenários",
    casoPede: "ROI anualizado acima de 15% dentro dos guard-rails. Cumprimos os quatro limites; o ROI fica em 11,3%.",
    perguntas: [{
      q: "Por que o ROI não chega a 15%?",
      a: "Das 5.600 políticas que testamos, 4.044 batem a meta e nenhuma respeita o piso de volume. O slide 9 traz a medição.",
    }],
    rodape: "ROI anualizado na Base C acima de 15%, respeitados os guard-rails de aprovação, taxa, inadimplência e volume",
    numero: n,
  });

  [
    { v: "59,5%", r: "das propostas aprovadas:\n2.976 de 5.000, score 5 a 10" },
    { v: "11,3%", r: "de ROI anualizado, de 11,1%\na 11,5% conforme o aceite" },
    { v: "4 de 4", r: "limites cumpridos, inclusive\nno cenário pessimista" },
  ].forEach((d, i) => {
    destaque(s, { x: c.x + i * 2.7, y: c.y, w: 2.55, valor: d.v, rotulo: d.r, cor: NAVY, tamanho: 33 });
  });

  s.addShape(pres.ShapeType.line, {
    x: c.x, y: 3.5, w: CORPO_L, h: 0, line: { color: GREY_LIGHT, width: 1 },
  });

  [
    // Os tres pilares espelham a cadeia: quem mede o risco, quem o preca, e
    // quanto sobra se a premissa falhar. Cada um entrega um numero — "robustez"
    // sozinho nao dizia nada.
    { n: "1 · MODELO", t: "XGBoost", d: "AuROC de 0,7234 fora do tempo, sem vazamento" },
    { n: "2 · PREÇO", t: "Corte no score 5", d: "Taxa de 1,63% a 2,29% ao mês, por faixa de risco" },
    { n: "3 · MARGEM", t: "12,7% de folga", d: "até o limite mais apertado, no pior dos três cenários" },
  ].forEach((d, i) => {
    const x = c.x + i * 2.7;
    s.addText(d.n, {
      x, y: 3.72, w: 2.55, h: 0.28,
      fontSize: 10.5, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1,
      isTextBox: true, margin: 0,
    });
    s.addText(d.t, {
      x, y: 4.02, w: 2.55, h: 0.35,
      fontSize: 15.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(d.d, {
      x, y: 4.42, w: 2.55, h: 0.6,
      fontSize: 11, color: GREY, fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: c.x, y: 5.25, w: CORPO_L, h: 1.0, fill: CORAL_SOFT, linha: CORAL });
  s.addText(
    [
      { text: "A mudança central:  ", options: { bold: true, color: NAVY } },
      { text: "hoje a AutoCred cobra 1,57% de quem tem 0,2% de inadimplência e 1,64% de quem tem 69,6%. Passamos a cobrar o risco de cada faixa — e é isso que muda o resultado.", options: { color: NAVY } },
    ],
    { x: c.x + 0.3, y: 5.48, w: CORPO_L - 0.6, h: 0.6, fontSize: 11.5, fontFace: SANS,
      lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 4 · Contexto */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "Contexto",
    titulo: "Uma financeira que cresceu rápido e nunca revisou a régua:\ninadimplência de 8,3% e preço que não distingue risco",
    casoPede: "Nova política de concessão 2026 com ROI acima de 15%, sem sufocar a originação nem estourar o apetite de risco.",
    perguntas: [
      { q: "Por que quatro limites e não só o ROI?",
        a: "Sem eles a política ideal aprovaria pouco e cobraria o teto. O piso de volume força a AutoCred a continuar crescendo." },
      { q: "Isso é problema de dado ou de negócio?",
        a: "De negócio. O dado só mostra o tamanho: quem paga em dia está financiando quem não paga, e vai embora para o concorrente." },
    ],
    rodape: "1. O caso · o que o conselho pediu: ROI anualizado acima de 15% sem sufocar a originação e sem estourar o apetite de risco",
    numero: n,
  });

  s.addText(
    "A AutoCred financia veículos leves desde 2022 e cresceu rápido. A política de concessão nunca foi revisada, e a inadimplência chegou a 8,3%.",
    { x: c.x, y: c.y, w: CORPO_L, h: 0.55, fontSize: 13.5, color: NAVY, fontFace: SANS,
      lineSpacing: 19, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: c.x, y: 2.65, w: CORPO_L, h: 1.85, fill: NAVY, linha: NAVY });
  s.addText("O preço não distingue risco — e isso tem um nome", {
    x: c.x + 0.35, y: 2.85, w: CORPO_L - 0.7, h: 0.35,
    fontSize: 16, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    { v: "1,57%", r: "cobrado de quem tem\n0,2% de inadimplência" },
    { v: "1,64%", r: "cobrado de quem tem\n69,6% de inadimplência" },
    { v: "+0,125", r: "a correlação entre\ntaxa e risco", cor: CORAL },
  ].forEach((d, i) => {
    s.addText(d.v, {
      x: c.x + 0.35 + i * 2.5, y: 3.3, w: 2.3, h: 0.45,
      fontSize: 24, bold: true, color: d.cor || WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(d.r, {
      x: c.x + 0.35 + i * 2.5, y: 3.78, w: 2.3, h: 0.55,
      fontSize: 10.5, color: GREY_ESCURO, fontFace: SANS, lineSpacing: 14,
      isTextBox: true, margin: 0,
    });
  });

  s.addText(
    [
      { text: "É seleção adversa. ", options: { bold: true, color: NAVY } },
      { text: "Com preço único, o bom cliente paga pelo ruim e vai para o concorrente; sobra quem não tem alternativa. A inadimplência sobe sozinha, e subir o preço linear acelera o ciclo.", options: { color: GREY } },
    ],
    { x: c.x, y: 4.7, w: CORPO_L, h: 0.7, fontSize: 12.5, fontFace: SANS,
      lineSpacing: 17, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: c.x, y: 5.5, w: CORPO_L, h: 0.8, fill: CORAL_SOFT, linha: CORAL });
  s.addText(
    "A pergunta: qual política maximiza o ROI sem travar a originação nem estourar o apetite de risco?",
    { x: c.x + 0.3, y: 5.72, w: CORPO_L - 0.6, h: 0.4, fontSize: 13, bold: true,
      color: NAVY, fontFace: SANS, isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 5 · O modelo */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "1 · o modelo",
    titulo: "O XGBoost ordena risco fora do tempo — depois de removermos a coluna\nque daria AuROC imbatível no treino e destruiria a aplicação",
    casoPede: "Modelo de PD 90/12 que ordene bem o risco, sem vazamento. Métrica oficial: AuROC na Base B.",
    perguntas: [
      { q: "O que é vazamento?",
        a: "É treinar o modelo com informação que só existe DEPOIS da decisão. Ele acerta o passado e fracassa no futuro, porque na hora de decidir aquele dado ainda não nasceu." },
      { q: "Por que não o Random Forest, que empata?",
        a: "Com reponderação ele projetava PD média de 42,3% contra 7,2% observados. Ordena bem, mas o nível não serve para precificar." },
    ],
    rodape: "2, 3 e 11 · modelo de PD 90/12 por AuROC na Base B · colunas disponíveis na concessão · validação temporal",
    numero: n,
  });

  cartao(s, { x: c.x, y: c.y, w: CORPO_L, h: 1.05, fill: NAVY, linha: NAVY });
  s.addText("qtd_parcelas_em_atraso_12m", {
    x: c.x + 0.3, y: c.y + 0.16, w: 4.4, h: 0.35,
    fontSize: 16, bold: true, color: WHITE, fontFace: MONO, isTextBox: true, margin: 0,
  });
  s.addText("correlação de 0,74 com o alvo · vale ZERO nas bases B e C · levaria o AuROC a 0,50", {
    x: c.x + 0.3, y: c.y + 0.55, w: 7.3, h: 0.35,
    fontSize: 11.5, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  s.addText(
    [
      { text: "Quantas parcelas o cliente atrasou ", options: { color: NAVY } },
      { text: "depois", options: { color: CORAL, bold: true } },
      { text: " de receber o crédito. Na hora de decidir, esse número ainda não existe — e é isso que se chama ", options: { color: NAVY } },
      { text: "vazamento", options: { color: NAVY, bold: true } },
      { text: ": o modelo aprende com o futuro e não sabe decidir no presente.", options: { color: NAVY } },
    ],
    { x: c.x, y: 3.1, w: CORPO_L, h: 0.5, fontSize: 12, fontFace: SANS,
      lineSpacing: 16, isTextBox: true, margin: 0 }
  );

  const linhas = [
    ["Modelo", "Val. cruzada", "Validação 2024", "Decisão"],
    ["Regressão logística", "0,6391", "0,6489", "referência"],
    ["Random Forest", "—", "0,7159", "descartado por calibração"],
    ["XGBoost", "0,6948", "0,7234", "escolhido"],
  ];
  const cx = [c.x + 0.25, c.x + 2.6, c.x + 4.1, c.x + 5.8];
  const cw = [2.3, 1.4, 1.6, 1.9];

  cartao(s, { x: c.x, y: 3.7, w: CORPO_L, h: 1.7, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = 3.85 + r * 0.37;
    const cab = r === 0;
    const esc = linha[0] === "XGBoost";
    if (esc) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.1, y: y - 0.04, w: CORPO_L - 0.2, h: 0.35,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((cel, k) => {
      s.addText(cel, {
        x: cx[k], y, w: cw[k], h: 0.3,
        fontSize: cab ? 10.5 : 12, bold: cab || esc, italic: cab,
        color: cab ? GREY : NAVY, fontFace: SANS,
        align: k === 0 || k === 3 ? "left" : "center", isTextBox: true, margin: 0,
      });
    });
  });

  s.addText("Treino 2022–2023 · validação 2024, medida uma vez só · hiperparâmetros por validação cruzada temporal", {
    x: c.x, y: 5.5, w: CORPO_L, h: 0.3,
    fontSize: 10.5, italic: true, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: c.x, y: 5.85, w: CORPO_L, h: 0.42, fill: CORAL_SOFT, linha: CORAL });
  s.addText(
    [
      { text: "Ganhar nas duas medidas afasta a sorte. ", options: { bold: true, color: NAVY } },
      { text: "E a escolha final foi por calibração, não por AuROC: a perda é PD × EAD × LGD, e a taxa sai dela.", options: { color: NAVY } },
    ],
    { x: c.x + 0.3, y: 5.94, w: CORPO_L - 0.6, h: 0.28, fontSize: 10.5, fontFace: SANS,
      isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 6 · A tabela */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "2 · a política",
    titulo: "Aprovamos o score 5 ou melhor, com taxa de 1,63% a 2,29% ao mês\nconforme a perda esperada de cada faixa",
    casoPede: "Para cada faixa: aprovar ou negar, taxa, prazo máximo e entrada mínima. A tabela é aplicada à Base C.",
    perguntas: [
      { q: "Por que a taxa varia só 0,66 ponto?",
        a: "Porque a perda é pequena diante dos juros. Taxa alta afasta o cliente e atrai o pior — o teto de 3,5% nunca chega perto de morder." },
      { q: "Por que negar o score 4?",
        a: "A perda da faixa é 11,18%; a regra cobraria 2,62%, 65% acima do mercado. Aprová-lo daria +0,09pp de ROI e cortaria a folga pela metade." },
    ],
    rodape: "6. A política · aprovar ou negar, taxa, prazo máximo e entrada mínima por faixa de score, aplicada à Base C",
    numero: n,
  });

  cartao(s, { x: c.x, y: c.y, w: CORPO_L, h: 0.62, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "taxa da faixa  =  ", options: { color: GREY_ESCURO } },
      { text: "1,50%", options: { color: WHITE, bold: true } },
      { text: "  +  ", options: { color: GREY_ESCURO } },
      { text: "10%", options: { color: CORAL, bold: true } },
      { text: "  ×  perda esperada da faixa", options: { color: WHITE, bold: true } },
    ],
    { x: c.x, y: c.y + 0.16, w: CORPO_L, h: 0.35, fontSize: 15, fontFace: SERIF,
      align: "center", isTextBox: true, margin: 0 }
  );

  const linhas = [
    ["Score", "Faixa de PD", "Decisão", "Taxa a.m.", "Prazo", "Entrada", "Perda", "ROI"],
    ["10", "0,0–2,5%", "Aprovar", "1,634%", "48 m", "10%", "1,34%", "10,5%"],
    ["9", "2,5–3,5%", "Aprovar", "1,707%", "48 m", "10%", "2,07%", "10,8%"],
    ["8", "3,5–5,0%", "Aprovar", "1,792%", "48 m", "10%", "2,92%", "11,2%"],
    ["7", "5,0–7,0%", "Aprovar", "1,907%", "48 m", "10%", "4,07%", "11,5%"],
    ["6", "7,0–9,5%", "Aprovar", "2,077%", "48 m", "10%", "5,77%", "12,1%"],
    ["5", "9,5–13,0%", "Aprovar", "2,292%", "48 m", "10%", "7,92%", "12,5%"],
    ["1 a 4", "acima de 13%", "Negar", "—", "—", "—", "11,2%+", "—"],
  ];
  const cx = [c.x + 0.1, c.x + 0.75, c.x + 1.95, c.x + 3.0, c.x + 4.1, c.x + 4.95, c.x + 5.95, c.x + 6.95];
  const cw = [0.65, 1.2, 1.05, 1.1, 0.85, 1.0, 1.0, 0.9];

  cartao(s, { x: c.x, y: 2.72, w: CORPO_L, h: 3.15, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = 2.85 + r * 0.37;
    const cab = r === 0;
    const negar = linha[2] === "Negar";
    if (cab) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.05, y: y - 0.04, w: CORPO_L - 0.1, h: 0.35,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
    } else if (r % 2 === 0) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.05, y: y - 0.04, w: CORPO_L - 0.1, h: 0.35,
        fill: { color: "F7F9FA" }, line: { color: "F7F9FA", width: 0 },
      });
    }
    linha.forEach((cel, k) => {
      s.addText(cel, {
        x: cx[k], y, w: cw[k], h: 0.3,
        fontSize: cab ? 9.5 : 11, bold: cab || k === 0,
        color: cab ? WHITE : (negar ? GREY : NAVY), fontFace: SANS,
        align: "center", isTextBox: true, margin: 0,
      });
    });
  });

  s.addText("Na faixa 8, que perde 2,92%: 1,50% + 0,29% = 1,792%. Dá para conferir cada linha com uma calculadora.", {
    x: c.x, y: 5.95, w: CORPO_L, h: 0.3,
    fontSize: 10.5, italic: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

/* ========================================================== 7 · Contrato */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "2 · do risco ao retorno",
    titulo: "Num financiamento típico do score 8, a taxa de 1,79% cobre a perda\nesperada e rende 11,3% ao ano",
    casoPede: "Perda esperada = PD × EAD × LGD. ROI anual = (juros − perda) ÷ volume ÷ prazo médio em anos.",
    perguntas: [
      { q: "Os juros contam até o fim do contrato?",
        a: "Não. Quem dá calote paga só até o mês da quebra, ponderado pela distribuição real — por isso R$ 17.401 e não R$ 17.978." },
      { q: "Por que 11,3% aqui e 11,3% na carteira?",
        a: "Coincidência de arredondamento. O contrato é um caso; a carteira mistura as seis faixas e a reação do cliente." },
    ],
    rodape: "4 e 5 · perda esperada = PD × EAD × LGD · ROI anual = [(juros − perda realizada) ÷ volume financiado] ÷ prazo médio em anos",
    numero: n,
  });

  s.addText("Veículo de R$ 40.000 · entrada de 10% · 48 meses · LTV 90% · veículo de 4 anos · score 8", {
    x: c.x, y: c.y, w: CORPO_L, h: 0.3,
    fontSize: 11.5, italic: true, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });

  const passos = [
    ["1", "PD", "4,2%", "probabilidade de calote da faixa 8"],
    ["2", "EAD", "R$ 37.440", "fator 1,040 × R$ 36.000 financiados"],
    ["3", "LGD", "74,8%", "tabela: veículo de 3 a 5 anos, LTV de 80% a 90%"],
    ["4", "Perda esperada", "R$ 1.176", "PD × EAD × LGD = 3,3% do financiado"],
    ["5", "Juros esperados", "R$ 17.401", "taxa de 1,792% ao mês, parcela de R$ 1.125"],
    ["6", "ROI anual", "11,3%", "(juros − perda) ÷ financiado ÷ 4 anos"],
  ];
  passos.forEach((p, i) => {
    const y = 2.4 + i * 0.66;
    const ultimo = i === 5;
    cartao(s, { x: c.x, y, w: CORPO_L, h: 0.56,
                fill: ultimo ? CORAL_SOFT : WHITE, linha: ultimo ? CORAL : GREY_LIGHT });
    s.addShape(pres.ShapeType.ellipse, {
      x: c.x + 0.2, y: y + 0.13, w: 0.3, h: 0.3,
      fill: { color: ultimo ? CORAL : NAVY }, line: { color: ultimo ? CORAL : NAVY, width: 0 },
    });
    s.addText(p[0], {
      x: c.x + 0.2, y: y + 0.17, w: 0.3, h: 0.22,
      fontSize: 10, bold: true, color: WHITE, fontFace: SERIF, align: "center",
      isTextBox: true, margin: 0,
    });
    s.addText(p[1], {
      x: c.x + 0.65, y: y + 0.15, w: 1.9, h: 0.28,
      fontSize: 12.5, bold: true, color: NAVY, fontFace: SANS, isTextBox: true, margin: 0,
    });
    s.addText(p[2], {
      x: c.x + 2.6, y: y + 0.13, w: 1.55, h: 0.3,
      fontSize: 13.5, bold: true, color: ultimo ? CORAL : NAVY, fontFace: SERIF,
      align: "right", isTextBox: true, margin: 0,
    });
    s.addText(p[3], {
      x: c.x + 4.35, y: y + 0.17, w: 3.4, h: 0.28,
      fontSize: 10.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
}

/* ========================================================== 8 · Limites */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "3 · os quatro limites",
    titulo: "Os quatro limites passam nos três cenários de aceite,\ncom 12,7% de folga até o mais apertado",
    casoPede: "Aprovação ≥ 35%, taxa ≤ 3,5% ao mês, inadimplência ≤ 8% e volume ≥ R$ 40 milhões. Estourar corta a nota pela metade.",
    perguntas: [
      { q: "As reações da Base C são reais?",
        a: "São suposição nossa: o enunciado dá a direção de cada efeito, não a intensidade. Por isso três cenários, e não um." },
      { q: "Por que não o ROI máximo?",
        a: "Ele era 0,1 ponto maior e deixava metade da folga. O ganho é pequeno e certo; o risco de furar é grande e binário." },
    ],
    rodape: "7. Guard-rails · aprovação ≥ 35% · taxa ≤ 3,5% ao mês · inadimplência ≤ 8% · volume ≥ R$ 40 milhões",
    numero: n,
  });

  const linhas = [
    ["Indicador", "Otimista", "Central", "Pessimista", "Limite"],
    ["Taxa de aprovação", "59,5%", "59,5%", "59,5%", "mín. 35%"],
    ["Volume originado", "R$ 86,1 mi", "R$ 66,7 mi", "R$ 45,1 mi", "mín. R$ 40 mi"],
    ["Inadimplência", "6,2%", "6,3%", "6,6%", "máx. 8%"],
    ["Taxa média ao mês", "1,91%", "1,91%", "1,91%", "teto 3,5%"],
    ["ROI anualizado", "11,5%", "11,3%", "11,1%", "meta 15%"],
  ];
  const cx = [c.x + 0.2, c.x + 2.6, c.x + 4.0, c.x + 5.4, c.x + 6.9];
  const cw = [2.3, 1.35, 1.35, 1.45, 1.4];

  cartao(s, { x: c.x, y: c.y, w: CORPO_L, h: 2.65, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = c.y + 0.15 + r * 0.39;
    const cab = r === 0;
    const roi = linha[0] === "ROI anualizado";
    if (cab) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.05, y: y - 0.05, w: CORPO_L - 0.1, h: 0.37,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
    } else if (roi) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.05, y: y - 0.05, w: CORPO_L - 0.1, h: 0.37,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((cel, k) => {
      s.addText(cel, {
        x: cx[k], y, w: cw[k], h: 0.32,
        fontSize: cab ? 10.5 : 11.5, bold: cab || k === 0 || roi,
        color: cab ? WHITE : (k === 4 ? GREY : NAVY), fontFace: SANS,
        align: k === 0 ? "left" : (k === 4 ? "left" : "center"), isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: c.x, y: 4.85, w: 3.85, h: 1.35, fill: WHITE });
  s.addText("O ROI varia pouco. O volume, muito.", {
    x: c.x + 0.28, y: 5.02, w: 3.3, h: 0.3,
    fontSize: 13, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "O ROI é uma razão, e o aceite move numerador e denominador juntos. Foi pelo volume que medimos a folga.",
    { x: c.x + 0.28, y: 5.36, w: 3.3, h: 0.7, fontSize: 11, color: GREY, fontFace: SANS,
      lineSpacing: 14, isTextBox: true, margin: 0 }
  );

  cartao(s, { x: c.x + 4.05, y: 4.85, w: 3.85, h: 1.35, fill: NAVY, linha: NAVY });
  s.addText("12,7% de folga, por escolha", {
    x: c.x + 4.33, y: 5.02, w: 3.3, h: 0.3,
    fontSize: 13, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "Violar um guard-rail corta a nota de política pela metade. Trocamos 0,1 ponto de ROI por essa margem.",
    { x: c.x + 4.33, y: 5.36, w: 3.3, h: 0.7, fontSize: 11, color: GREY_ESCURO,
      fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 9 · Os 15% */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "3 · a pergunta que esperamos",
    titulo: "A meta de 15% é incompatível com o piso de volume —\ne isso foi medido, não argumentado",
    casoPede: "ROI anualizado acima de 15%. Entregamos 11,3% e explicamos por quê, com a varredura que sustenta.",
    perguntas: [
      { q: "O que teria de ser diferente?",
        a: "O cliente teria de ser cinco vezes menos sensível a preço. Nesse mundo, cobrar 45% acima do mercado quase não afastaria ninguém." },
      { q: "E se o simulador for menos elástico?",
        a: "A fronteira inteira sobe e 15% volta ao alcance. É a nossa premissa mais frágil, e está declarada nos riscos." },
    ],
    rodape: "7. Guard-rails · a meta de ROI é o que se maximiza dentro dos quatro limites, não um quinto limite",
    numero: n,
  });

  [
    { v: "5.600", r: "políticas varridas:\ncorte × preço × prazo × entrada" },
    { v: "4.044", r: "batem a meta\nde 15% de ROI" },
    { v: "0", r: "delas respeitam\nos quatro limites", cor: CORAL },
  ].forEach((d, i) => {
    destaque(s, { x: c.x + i * 2.7, y: c.y, w: 2.55, valor: d.v, rotulo: d.r,
                  cor: d.cor || NAVY, tamanho: 33 });
  });

  cartao(s, { x: c.x, y: 3.5, w: CORPO_L, h: 1.75, fill: WHITE });
  s.addText("Um único limite bloqueia a meta", {
    x: c.x + 0.28, y: 3.68, w: 4, h: 0.3,
    fontSize: 14, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  [
    ["Inadimplência", "mínimo de 5,26%", "máx. 8%", true],
    ["Taxa de aprovação", "máximo de 68,7%", "mín. 35%", true],
    ["Volume originado", "máximo de R$ 20,5 mi", "mín. R$ 40 mi", false],
  ].forEach((l, i) => {
    const y = 4.08 + i * 0.36;
    s.addText(l[3] ? "✓" : "✕", {
      x: c.x + 0.3, y, w: 0.25, h: 0.28,
      fontSize: 12, bold: true, color: l[3] ? TEAL : CORAL, fontFace: SANS,
      isTextBox: true, margin: 0,
    });
    s.addText(l[0], {
      x: c.x + 0.6, y, w: 2.0, h: 0.28,
      fontSize: 11, color: l[3] ? GREY : NAVY, bold: !l[3], fontFace: SANS,
      isTextBox: true, margin: 0,
    });
    s.addText(l[1], {
      x: c.x + 2.6, y, w: 2.0, h: 0.28,
      fontSize: 11, color: l[3] ? GREY : CORAL, bold: !l[3], fontFace: SANS,
      isTextBox: true, margin: 0,
    });
    s.addText(l[2], {
      x: c.x + 4.7, y, w: 1.4, h: 0.28,
      fontSize: 10.5, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
    });
  });
  s.addText("Risco e seletividade passam. Só o volume mata.", {
    x: c.x + 0.28, y: 4.9, w: 4.5, h: 0.28,
    fontSize: 11, italic: true, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: c.x, y: 5.4, w: CORPO_L, h: 0.85, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "Por construção: ", options: { color: WHITE, bold: true } },
      { text: "o ROI é retorno por real emprestado, e o jeito de aumentá-lo é cobrar mais caro — o que derruba o aceite. Na varredura, a correlação entre ROI e volume é de −0,914.", options: { color: GREY_ESCURO } },
    ],
    { x: c.x + 0.3, y: 5.58, w: CORPO_L - 0.6, h: 0.55, fontSize: 11.5, fontFace: SANS,
      lineSpacing: 15, isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 10 · Riscos */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "3 · riscos e limitações",
    titulo: "Onde este número quebra: quatro riscos nomeados,\ne a política não aguenta risco real 30% maior",
    casoPede: "Riscos e limitações declarados. Nomear o buraco é mais barato do que ser pego nele.",
    perguntas: [
      { q: "Qual é o mais provável?",
        a: "O erro de nível da PD. A inferência de rejeitados o torna provável, e é o que o estresse de +30% testa." },
      { q: "O que fariam com mais tempo?",
        a: "Inferência de rejeitados de verdade, calibração formal e um piloto de preço para medir o aceite em vez de supor." },
    ],
    rodape: "8. Riscos e limitações · o que pode dar errado, com o tamanho de cada risco e a mitigação adotada",
    numero: n,
  });

  const riscos = [
    { c: CORAL, t: "Inferência de rejeitados", d: "A Base C tem bureau 96 pontos menor e 2,7× mais restrições. A ordenação sobrevive; o nível da PD, não — e é o nível que vira preço." },
    { c: CORAL, t: "A elasticidade do aceite é premissa, não medida", d: "Se o simulador for mais elástico que supusemos, o volume frustra — e volume é guard-rail." },
    { c: TEAL, t: "As duas faixas mais arriscadas rodam acima do limite", d: "A 6 projeta 9,1% e a 5, 13,3%, contra os 8%. Cabem porque as boas diluem: a carteira fecha em 6,3%." },
    { c: TEAL, t: "Deriva de safra", d: "O calote caiu de 8,9% em 2023 para 7,2% em 2024. Se 2025 voltar ao patamar anterior, a projeção sobe junto." },
  ];
  riscos.forEach((r, i) => {
    const y = c.y + i * 0.88;
    cartao(s, { x: c.x, y, w: CORPO_L, h: 0.76, fill: WHITE });
    s.addShape(pres.ShapeType.rect, {
      x: c.x, y, w: 0.06, h: 0.76, fill: { color: r.c }, line: { color: r.c, width: 0 },
    });
    s.addText(r.t, {
      x: c.x + 0.25, y: y + 0.1, w: CORPO_L - 0.45, h: 0.26,
      fontSize: 12.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
    });
    s.addText(r.d, {
      x: c.x + 0.25, y: y + 0.36, w: CORPO_L - 0.45, h: 0.35,
      fontSize: 10.5, color: GREY, fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: c.x, y: 5.55, w: CORPO_L, h: 0.7, fill: CORAL_SOFT, linha: CORAL });
  s.addText(
    [
      { text: "Testamos o risco 30% maior: ", options: { bold: true, color: NAVY } },
      { text: "a inadimplência vai a 8,2% e estoura o limite. É o cenário que mais nos preocupa, e o monitoramento por safra existe para pegá-lo cedo.", options: { color: NAVY } },
    ],
    { x: c.x + 0.3, y: 5.72, w: CORPO_L - 0.6, h: 0.45, fontSize: 11.5, fontFace: SANS,
      lineSpacing: 15, isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 11 · Plano */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "Recomendações finais",
    titulo: "Submeter a política, monitorar por faixa e medir o aceite real —\nque é a premissa mais frágil de tudo",
    casoPede: "O que avaliamos, o que recomendamos e os riscos, com a divisão do trabalho.",
    perguntas: [
      { q: "Quando revisar a política?",
        a: "Por safra, ou antes se o PSI passar de 0,1 ou o erro de calibração passar de 3 pontos." },
    ],
    rodape: "9. Recomendações finais · o que avaliamos, o que recomendamos e os riscos assumidos",
    numero: n,
  });

  const cols = [
    { r: "MODELO", t: "Submeter o XGBoost", d: "AuROC 0,7234 fora do tempo, sem vazamento. Recalibrar a cada nova safra." },
    { r: "POLÍTICA", t: "Aprovar score 5 a 10", d: "Taxa de 1,63% a 2,29%, prazo de 48 meses e entrada de 10%." },
    { r: "MONITORAR", t: "Aceite, calote e volume", d: "Por faixa, todo mês. Ajustar a taxa se a reação do cliente for pior que a projetada." },
  ];
  cols.forEach((col, i) => {
    const x = c.x + i * 2.7;
    cartao(s, { x, y: c.y, w: 2.55, h: 2.0, fill: WHITE });
    s.addText(col.r, {
      x: x + 0.22, y: c.y + 0.18, w: 2.1, h: 0.25,
      fontSize: 10, bold: true, color: CORAL, fontFace: SANS, charSpacing: 1,
      isTextBox: true, margin: 0,
    });
    s.addText(col.t, {
      x: x + 0.22, y: c.y + 0.45, w: 2.1, h: 0.55,
      fontSize: 13.5, bold: true, color: NAVY, fontFace: SERIF, lineSpacing: 17,
      isTextBox: true, margin: 0,
    });
    s.addText(col.d, {
      x: x + 0.22, y: c.y + 1.05, w: 2.1, h: 0.85,
      fontSize: 10.5, color: GREY, fontFace: SANS, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });

  cartao(s, { x: c.x, y: 4.25, w: CORPO_L, h: 1.95, fill: NAVY, linha: NAVY });
  s.addText("O passo seguinte, que o case não pede mas o negócio exige", {
    x: c.x + 0.3, y: 4.45, w: CORPO_L - 0.6, h: 0.32,
    fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Um piloto de preço. ", options: { color: CORAL, bold: true } },
      { text: "Toda a projeção de ROI depende de quanto o cliente foge quando o preço sobe, e ninguém mediu isso — nem nós, nem o mercado. Um teste A/B numa fatia da carteira, por uma safra, transforma a premissa em dado. É a diferença entre uma política defensável e uma política calibrada.", options: { color: GREY_ESCURO } },
    ],
    { x: c.x + 0.3, y: 4.85, w: CORPO_L - 0.6, h: 1.1, fontSize: 12, fontFace: SANS,
      lineSpacing: 17, isTextBox: true, margin: 0 }
  );
}

/* ================================================== 12 · Divisor do apêndice */
{
  const s = slide();
  s.background = { color: NAVY };
  s.addText("APÊNDICE", {
    x: M, y: 2.9, w: W - 2 * M, h: 0.4,
    fontSize: 13, bold: true, color: CORAL, fontFace: SANS, charSpacing: 2.5,
    isTextBox: true, margin: 0,
  });
  s.addText("Material de consulta", {
    x: M, y: 3.35, w: W - 2 * M, h: 0.9,
    fontSize: 42, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("Perfil de quem aprovamos, a mudança de população entre as bases e a escolha dos cortes de score.", {
    x: M, y: 4.3, w: 10, h: 0.5,
    fontSize: 15, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText(String(n), {
    x: W - M - 0.5, y: 6.82, w: 0.5, h: 0.28,
    fontSize: 10, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
  });
}

/* ========================================================== 13 · Perfil */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "Apêndice A1",
    titulo: "Aprovamos 59,5% das propostas: bureau 206 pontos mais alto,\nrenda 70% maior e um terço das restrições",
    casoPede: "Explicar por que aprovou quem aprovou e por que cobrou o que cobrou.",
    perguntas: [
      { q: "Os negados são só o perfil fora do domínio?",
        a: "Não. 72% deles estão fora, mas 28% são perfis que o modelo conhece bem — e mesmo assim têm PD alta." },
    ],
    rodape: "Defesa perante o conselho · por que aprovou quem aprovou e por que cobrou o que cobrou",
    numero: n,
  });

  const linhas = [
    ["Indicador (média do grupo)", "Aprovados (5 a 10)", "Negados (1 a 4)"],
    ["Propostas", "2.976  (59,5%)", "2.024  (40,5%)"],
    ["PD média", "5,9%", "28,0%"],
    ["Score de bureau médio", "634", "428"],
    ["Renda mediana", "R$ 5.076", "R$ 2.981"],
    ["Com restrição ativa", "49%", "91%"],
    ["Fora do domínio de treino", "12%", "72%"],
  ];
  const cx = [c.x + 0.2, c.x + 3.6, c.x + 5.8];
  const cw = [3.3, 2.0, 2.0];

  cartao(s, { x: c.x, y: c.y, w: CORPO_L, h: 3.05, fill: WHITE });
  linhas.forEach((linha, r) => {
    const y = c.y + 0.15 + r * 0.4;
    const cab = r === 0;
    const dest = linha[0] === "Fora do domínio de treino";
    if (cab) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.05, y: y - 0.05, w: CORPO_L - 0.1, h: 0.38,
        fill: { color: NAVY }, line: { color: NAVY, width: 0 },
      });
    } else if (dest) {
      s.addShape(pres.ShapeType.rect, {
        x: c.x + 0.05, y: y - 0.05, w: CORPO_L - 0.1, h: 0.38,
        fill: { color: CORAL_SOFT }, line: { color: CORAL_SOFT, width: 0 },
      });
    }
    linha.forEach((cel, k) => {
      s.addText(cel, {
        x: cx[k], y, w: cw[k], h: 0.32,
        fontSize: cab ? 10.5 : 12, bold: cab || k === 0 || dest,
        color: cab ? WHITE : NAVY, fontFace: SANS,
        align: k === 0 ? "left" : "center", isTextBox: true, margin: 0,
      });
    });
  });

  cartao(s, { x: c.x, y: 5.2, w: CORPO_L, h: 1.0, fill: NAVY, linha: NAVY });
  s.addText(
    [
      { text: "A linha que mais importa é a última. ", options: { color: WHITE, bold: true } },
      { text: "A Base A só tem bureau a partir de 460 e no máximo 2 restrições; a Base C vai a zero e a cinco. Onde o modelo nunca viu, ele extrapola — e é por isso que deixamos margem em vez de confiar no nível da PD.", options: { color: GREY_ESCURO } },
    ],
    { x: c.x + 0.3, y: 5.4, w: CORPO_L - 0.6, h: 0.7, fontSize: 11.5, fontFace: SANS,
      lineSpacing: 15, isTextBox: true, margin: 0 }
  );
}

/* ========================================================== 14 · Base C */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "Apêndice A2",
    titulo: "A Base C é outra população — por isso os cortes de score\nsão absolutos, e não quantis",
    casoPede: "A Base C é de mar aberto: inclui perfis que a AutoCred recusava. É a inferência de rejeitados.",
    perguntas: [
      { q: "Vocês corrigiram esse viés?",
        a: "Não. Medimos o tamanho e deixamos margem na política. Tratamos a PD como ordenação confiável e nível suspeito." },
      { q: "Por que não quantis, que é mais simples?",
        a: "O décimo pior de uma população boa e o décimo pior de uma ruim não são o mesmo risco, e não podem custar o mesmo preço." },
    ],
    rodape: "3 · construção do score de 1 a 10 · a Base C inclui perfis que a política anterior recusava",
    numero: n,
  });

  [
    { v: "5,93", r: "PSI em restrições ativas\nentre a Base A e a C" },
    { v: "549 vs 645", r: "score de bureau mediano\nna Base C contra a A" },
    { v: "12%", r: "dos aprovados estão fora\ndo domínio do treino", cor: CORAL },
  ].forEach((d, i) => {
    destaque(s, { x: c.x + i * 2.7, y: c.y, w: 2.55, valor: d.v, rotulo: d.r,
                  cor: d.cor || NAVY, tamanho: 26 });
  });

  cartao(s, { x: c.x, y: 3.5, w: CORPO_L, h: 1.35, fill: NAVY, linha: NAVY });
  s.addText("O que o corte absoluto garante", {
    x: c.x + 0.3, y: 3.68, w: CORPO_L - 0.6, h: 0.32,
    fontSize: 15, bold: true, color: WHITE, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "A faixa 5 significa ", options: { color: GREY_ESCURO } },
      { text: "«PD entre 9,5% e 13%»", options: { color: WHITE, bold: true } },
      { text: " em qualquer base, em qualquer ano. O preço dela cobre aquele risco — e aquele risco é o mesmo em toda parte. Com quantil, a mesma faixa mudaria de significado a cada safra.", options: { color: GREY_ESCURO } },
    ],
    { x: c.x + 0.3, y: 4.05, w: CORPO_L - 0.6, h: 0.7, fontSize: 12, fontFace: SANS,
      lineSpacing: 16, isTextBox: true, margin: 0 }
  );

  s.addText(
    "As duas variáveis mais preditivas do modelo são exatamente as que mais mudaram entre as bases. É por isso que o nível da PD merece desconfiança, e a ordenação não.",
    { x: c.x, y: 5.05, w: CORPO_L, h: 0.7, fontSize: 12, italic: true, color: GREY,
      fontFace: SANS, lineSpacing: 16, isTextBox: true, margin: 0 }
  );
}

/* ================================================== 15 · O capital que gira */
{
  const s = slide();
  const c = moldura(pres, s, {
    kicker: "Apêndice A3",
    titulo: "O capital não fica parado quatro anos — ele volta em parcelas,\ne isso muda a leitura do retorno",
    casoPede: "ROI anual = (juros − perda) ÷ volume financiado ÷ prazo médio em anos. É a régua oficial, e é por ela que submetemos.",
    perguntas: [
      { q: "Então o ROI de 11,3% está subestimado?",
        a: "Pela régua do conselho, não: ela é a mesma para todos os grupos. Mas ela divide pelo originado, como se o dinheiro ficasse imobilizado — e ele não fica." },
      { q: "E aplicar o que volta no CDI?",
        a: "Renderia, mas traz junto o custo de captação: o saldo devedor médio é maior que o caixa ocioso médio, então o líquido é negativo." },
    ],
    rodape: "5 · ROI anual = [(juros − perda realizada) ÷ volume financiado] ÷ prazo médio em anos",
    numero: n,
  });

  [
    { v: "R$ 66,7 mi", r: "volume originado:\no denominador da régua" },
    { v: "R$ 38,3 mi", r: "saldo devedor médio:\no capital de fato empregado" },
    { v: "57%", r: "do originado é o que\nfica realmente na rua", cor: CORAL },
  ].forEach((d, i) => {
    destaque(s, { x: c.x + i * 2.7, y: c.y, w: 2.55, valor: d.v, rotulo: d.r,
                  cor: d.cor || NAVY, tamanho: 25 });
  });

  cartao(s, { x: c.x, y: 3.45, w: 3.85, h: 1.3, fill: WHITE });
  s.addText("Pela régua do conselho", {
    x: c.x + 0.28, y: 3.62, w: 3.3, h: 0.28,
    fontSize: 12, bold: true, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText("11,33%", {
    x: c.x + 0.28, y: 3.9, w: 3.3, h: 0.45,
    fontSize: 27, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("(juros − perda) ÷ volume originado ÷ 4 anos", {
    x: c.x + 0.28, y: 4.36, w: 3.3, h: 0.28,
    fontSize: 10, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });

  cartao(s, { x: c.x + 4.05, y: 3.45, w: 3.85, h: 1.3, fill: NAVY, linha: NAVY });
  s.addText("Sobre o capital empregado", {
    x: c.x + 4.33, y: 3.62, w: 3.3, h: 0.28,
    fontSize: 12, bold: true, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });
  s.addText("19,72%", {
    x: c.x + 4.33, y: 3.9, w: 3.3, h: 0.45,
    fontSize: 27, bold: true, color: CORAL, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText("a mesma receita, sobre o saldo médio", {
    x: c.x + 4.33, y: 4.36, w: 3.3, h: 0.28,
    fontSize: 10, color: GREY_ESCURO, fontFace: SANS, isTextBox: true, margin: 0,
  });

  s.addText("E se o que volta fosse aplicado no CDI? O balanço tem dois lados.", {
    x: c.x, y: 4.92, w: CORPO_L, h: 0.3,
    fontSize: 12.5, bold: true, color: NAVY, fontFace: SERIF, isTextBox: true, margin: 0,
  });
  s.addText(
    "O saldo devedor médio (R$ 38,3 mi) é maior que o caixa ocioso médio (R$ 28,4 mi): quem capta paga mais do que quem aplica recebe.",
    { x: c.x, y: 5.22, w: CORPO_L, h: 0.28, fontSize: 10.5, italic: true,
      color: GREY, fontFace: SANS, isTextBox: true, margin: 0 }
  );

  const linhas = [
    ["CDI", "ganho no caixa ocioso", "custo de captação", "líquido"],
    ["9,0%", "+3,60 pp", "−4,86 pp", "−1,26 pp"],
    ["12,0%", "+4,74 pp", "−6,40 pp", "−1,66 pp"],
  ];
  const cx = [c.x + 0.2, c.x + 1.6, c.x + 3.9, c.x + 6.1];
  const cw = [1.3, 2.2, 2.1, 1.5];
  linhas.forEach((linha, r) => {
    const y = 5.58 + r * 0.28;
    const cab = r === 0;
    linha.forEach((cel, k) => {
      s.addText(cel, {
        x: cx[k], y, w: cw[k], h: 0.28,
        fontSize: cab ? 10 : 11.5, bold: cab || k === 0, italic: cab,
        color: cab ? GREY : (k === 3 ? CORAL : NAVY), fontFace: SANS,
        align: k === 0 ? "left" : "center", isTextBox: true, margin: 0,
      });
    });
  });

}

/* ========================================================================== */

const destino = path.join("outputs", "apresentacoes");
fs.mkdirSync(destino, { recursive: true });
// O nome do arquivo é o que o professor vê no anexo: sem número de ordem
// interno e sem jargão de método.
const arquivo = path.join(destino, "AutoCred - Política de Crédito 2026 - Grupo 3.pptx");
pres.writeFile({ fileName: arquivo }).then(() => console.log("Gerado:", arquivo));
