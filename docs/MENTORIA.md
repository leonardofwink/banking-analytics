# Registro da mentoria

> Diário de bordo das aulas: conceito apresentado, decisão tomada, tarefa gerada.
> Anote **durante** a aula, mesmo que curto — o conceito que parece óbvio na hora vira dúvida três semanas depois, quando o código precisar dele.
>
> Formato de cada entrada: **o que foi apresentado** → **o que isso implica para o nosso projeto** → **pendência gerada**.

---

## 2026-09-12 — Aula 1: conceitos de risco e perda

### Terminologia de gestão de risco

Os três termos que estruturam o raciocínio (detalhe em [`GLOSSARIO.md`](GLOSSARIO.md#1-gestão-de-risco--o-eixo-inerente--controle--residual)):

- **Risco inerente** — o risco bruto, antes de qualquer controle.
- **Risco residual** — o que sobra depois dos controles. É o que a instituição de fato carrega.
- **Mitigar riscos** — reduzir probabilidade e/ou impacto. Uma das quatro respostas possíveis (evitar, mitigar, transferir, aceitar).

### Perda esperada

```
Perda esperada  =  PD (%)  ×  EAD (R$)  ×  LGD (%)
```

- **PD** — *probability of default*: chance de o cliente dar calote (%)
- **EAD** — *exposure at default*: quanto ele estará devendo nesse momento (R$)
- **LGD** — *loss given default*: fração dessa exposição que não se recupera (%)

**O que isso implica para o projeto:** a fórmula é o esqueleto de tudo que vem depois. Cada fator é um modelo separado, com fonte de dado e método próprios — e cada mitigador de crédito ataca um fator específico (score → PD · limite → EAD · garantia → LGD). Vale montar o pipeline com os três como módulos independentes desde o começo, mesmo que a mentoria só desenvolva a PD a fundo.

### Rentabilidade — ROE

```
ROE  =  (Receita − Perda)  /  Volume negociado
```

De cada real emprestado, quanto sobra depois de descontar a perda esperada.

**O que isso implica para o projeto:** é o fecho do raciocínio. A perda esperada não é o objetivo final — ela é um **insumo** da conta de rentabilidade. Consequência prática para a modelagem: o **cutoff** do score não deve ser escolhido para minimizar a perda, e sim para **maximizar o ROE** — recusar cliente demais derruba a perda e a receita junto. Um modelo avaliado só por KS/Gini responde metade da pergunta.

> Nota registrada no glossário: a fórmula da aula usa *volume negociado* no denominador, enquanto o ROE contábil clássico usa *patrimônio líquido*. As duas definições circulam com o mesmo nome — ao ler um número de ROE, confirmar qual é o denominador.

### Pendências geradas

- [ ] Confirmar com o professor se a mentoria vai modelar os três componentes ou só a PD.
- [ ] Confirmar se a otimização de cutoff por ROE entra no escopo do projeto.
- [ ] Registrar a **definição de default** adotada (90+? outro corte?) em [`PRD.md`](PRD.md) — muda todos os números.
- [ ] Descobrir qual base de dados será usada e sob quais condições (ver [`DICIONARIO_DADOS.md`](DICIONARIO_DADOS.md)).

---

<!--
## AAAA-MM-DD — Aula N: título

### Conceito apresentado

### O que isso implica para o projeto

### Pendências geradas

- [ ]
-->
