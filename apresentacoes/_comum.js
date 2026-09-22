/**
 * Elementos compartilhados pelos decks do desafio AutoCred.
 *
 * Paleta, tipografia e os três componentes visuais que se repetem: título de
 * página, cartão e numerão. Mantê-los aqui é o que faz os três decks parecerem
 * o mesmo material — e não três apresentações que por acaso falam do mesmo
 * projeto.
 */

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
const GREY_ESCURO = "B7C4CE"; // cinza legível sobre fundo navy

const SERIF = "Cambria";
const SANS = "Calibri";

const W = 13.3; // LAYOUT_WIDE
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

/** Cartão com tinta de fundo — o motivo visual repetido nos decks. */
function cartao(pres, slide, { x, y, w, h, fill = WHITE, linha = GREY_LIGHT }) {
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

/** Linha de fecho em itálico, no rodapé de uma página clara. */
function fecho(slide, texto, cor = NAVY) {
  slide.addText(texto, {
    x: M, y: 6.55, w: W - 2 * M, h: 0.45,
    fontSize: 13.5, italic: true, color: cor, fontFace: SANS, isTextBox: true, margin: 0,
  });
}

module.exports = {
  NAVY, NAVY_MID, CORAL, CORAL_SOFT, OFFWHITE, WHITE, TEAL, GREY, GREY_LIGHT, GREY_ESCURO,
  SERIF, SANS, W, H, M,
  titulo, cartao, numerao, fecho,
};
