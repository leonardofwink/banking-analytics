/**
 * Anatomia de slide da defesa — Minto por dentro, negócio por fora.
 *
 * A estrutura vem de duas fontes que se completam:
 *
 *   **Barbara Minto** dá o esqueleto: o título de cada slide é a AFIRMAÇÃO
 *   que ele sustenta, não um rótulo. Quem lê só os títulos, em ordem, recebe
 *   o argumento inteiro.
 *
 *   **A apresentação do Renato** dá a moldura de negócio: uma coluna lateral
 *   que amarra cada página a uma exigência do enunciado ("o case pede") e
 *   antecipa a pergunta que a banca faria ali. A banca não precisa procurar
 *   onde cada requisito foi atendido, e a objeção chega já respondida.
 *
 * Um slide tem cinco zonas fixas:
 *
 *   kicker      rótulo curto da seção, em teal
 *   título      a afirmação, em serifada — o que Minto chama de "o topo"
 *   corpo       à esquerda, 7,9 polegadas
 *   lateral     à direita, 3,5 polegadas: o case pede + perguntas
 *   rodapé      o requisito do enunciado, a identificação e o número
 */

const C = require("./_comum");

const {
  NAVY, NAVY_MID, CORAL, CORAL_SOFT, OFFWHITE, WHITE, TEAL, GREY, GREY_LIGHT,
  GREY_ESCURO, SERIF, SANS, W, M,
} = C;

// As duas colunas. O corpo nunca invade a lateral.
const CORPO_L = 7.9;
const LATERAL_X = M + 8.65;
const LATERAL_L = 3.25;
const CORPO_Y = 1.95;

/**
 * Monta a moldura e devolve as coordenadas que o corpo pode usar.
 *
 * @param {object} pres      instância do pptxgenjs, para as formas
 * @param {object} s         o slide
 * @param {object} opts      kicker, titulo, casoPede, perguntas, rodape, numero
 * @returns {{x:number,y:number,w:number}} a área livre do corpo
 */
function moldura(pres, s, { kicker, titulo, casoPede, perguntas = [], rodape, numero }) {
  s.background = { color: OFFWHITE };

  s.addText(kicker.toUpperCase(), {
    x: M, y: 0.42, w: W - 2 * M, h: 0.28,
    fontSize: 11, bold: true, color: TEAL, fontFace: SANS, charSpacing: 2,
    isTextBox: true, margin: 0,
  });

  s.addText(titulo, {
    x: M, y: 0.72, w: W - 2 * M, h: 0.95,
    fontSize: 23, bold: true, color: NAVY, fontFace: SERIF, lineSpacing: 29,
    isTextBox: true, margin: 0,
  });

  s.addShape(pres.ShapeType.line, {
    x: M, y: 1.78, w: W - 2 * M, h: 0,
    line: { color: GREY_LIGHT, width: 1 },
  });

  // divisória entre corpo e lateral
  s.addShape(pres.ShapeType.line, {
    x: LATERAL_X - 0.35, y: CORPO_Y, w: 0, h: 4.3,
    line: { color: GREY_LIGHT, width: 1 },
  });

  let y = CORPO_Y;
  if (casoPede) {
    s.addText("O CASE PEDE", {
      x: LATERAL_X, y, w: LATERAL_L, h: 0.26,
      fontSize: 10, bold: true, color: TEAL, fontFace: SANS, charSpacing: 1.5,
      isTextBox: true, margin: 0,
    });
    s.addText(casoPede, {
      x: LATERAL_X, y: y + 0.3, w: LATERAL_L, h: 0.85,
      fontSize: 11, color: NAVY, fontFace: SANS, lineSpacing: 15,
      isTextBox: true, margin: 0,
    });
    y += 1.25;
  }

  perguntas.forEach((p) => {
    s.addText(p.q, {
      x: LATERAL_X, y, w: LATERAL_L, h: 0.5,
      fontSize: 11, bold: true, color: NAVY, fontFace: SANS, lineSpacing: 14,
      isTextBox: true, margin: 0,
    });
    const alturaQ = p.q.length > 46 ? 0.45 : 0.25;
    s.addText(p.a, {
      x: LATERAL_X, y: y + alturaQ, w: LATERAL_L, h: 0.9,
      fontSize: 10.5, color: GREY, fontFace: SANS, lineSpacing: 14,
      isTextBox: true, margin: 0,
    });
    y += alturaQ + (p.a.length > 150 ? 1.05 : 0.8);
  });

  if (rodape) {
    s.addText(rodape, {
      x: M, y: 6.48, w: W - 2 * M - 0.5, h: 0.3,
      fontSize: 10, color: CORAL, fontFace: SANS, isTextBox: true, margin: 0,
    });
  }
  s.addText("AutoCred · Política de crédito 2026 · Grupo 3", {
    x: M, y: 6.82, w: 8, h: 0.28,
    fontSize: 10, color: GREY, fontFace: SANS, isTextBox: true, margin: 0,
  });
  if (numero) {
    s.addText(String(numero), {
      x: W - M - 0.5, y: 6.82, w: 0.5, h: 0.28,
      fontSize: 10, color: GREY, fontFace: SANS, align: "right", isTextBox: true, margin: 0,
    });
  }

  return { x: M, y: CORPO_Y, w: CORPO_L };
}

/** Número grande com rótulo, do tamanho certo para a coluna do corpo. */
function destaque(s, { x, y, w, valor, rotulo, cor = NAVY, tamanho = 34 }) {
  s.addText(valor, {
    x, y, w, h: 0.55,
    fontSize: tamanho, bold: true, color: cor, fontFace: SERIF,
    isTextBox: true, margin: 0,
  });
  s.addText(rotulo, {
    x, y: y + 0.58, w, h: 0.75,
    fontSize: 11, color: GREY, fontFace: SANS, lineSpacing: 14,
    isTextBox: true, margin: 0,
  });
}

module.exports = { moldura, destaque, CORPO_L, LATERAL_X, LATERAL_L, CORPO_Y };
