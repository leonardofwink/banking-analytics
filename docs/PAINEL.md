# O painel interativo

Um simulador de política de crédito sobre a Base C: mexe nas seis alavancas,
vê o ROI e os quatro guard-rails responderem, e destrincha qualquer uma das
5.000 propostas.

## Por que ele é fiel

O painel roda no navegador e **não tem como carregar o XGBoost**. A tentação
seria reimplementar o modelo em JavaScript e torcer para bater com o Python —
que é exatamente como se produzem dois números diferentes para a mesma
pergunta.

A saída foi outra: **pré-computar tudo no motor de verdade**. O
`25_dados_do_painel.py` varre 5.600 políticas com a mesma `banking.roi.simular`
que gerou os números do documento, nos três cenários, e grava a tabela. O
painel não calcula ROI — ele **consulta**. Quem abrir e não mexer em nada vê
11,33%, R$ 45,1 mi no pior caso e 6,33% de inadimplência, porque são os mesmos
números, não uma reprodução deles.

O que o JavaScript de fato calcula é só o detalhe de um contrato — parcela pela
Price, fator de EAD, LGD da tabela, perda esperada. São fórmulas fechadas e
tabelas de consulta, transcritas do `banking.perda` e do `banking.price`, com
os parâmetros exportados do mesmo Excel do professor.

## A grade

É a **mesma do S12** (`12_fronteira_roi_volume.py`), e isso é deliberado: o
documento e o deck dizem "5.600 políticas varridas", e um painel com grade
própria obrigaria a explicar dois números para a mesma afirmação.

| Alavanca | Valores | O padrão |
| -------- | ------- | -------- |
| Corte de score | 4, 5, 6, 7 | **5** |
| Taxa base | 1,50% a 3,00% a.m., de 0,25 em 0,25 | **1,50%** |
| Prêmio de risco (`k`) | 0 · 0,10 · 0,20 · 0,30 · 0,50 | **0,10** |
| Prazo ofertado | 24, 36, 48, 60 meses | **48** |
| Entrada mínima | 0% · 10% · 20% · 30% · 40% | **10%** |
| Escalonamento da entrada | 0 ou +4 pp por faixa pior | **0** |

4 × 7 × 5 × 4 × 5 × 2 = **5.600 políticas**, cada uma simulada nos três
cenários de aceite. A grade **contém** a política escolhida nos seis eixos — o
botão *Restaurar o nosso modelo* volta exatamente a ela.

> Mexeu na grade aqui, mexa no S12 também: os dois números têm de continuar
> sendo o mesmo número.

## O que cada parte mostra

**As métricas** trazem o valor simulado, o do nosso modelo embaixo, e a
diferença em pontos percentuais. Verde e vermelho seguem o sentido da métrica:
inadimplência que sobe é vermelha, volume que sobe é verde.

**A fronteira** é a nuvem inteira — uma marca por política, ROI contra volume
no cenário pessimista. A faixa vermelha à esquerda é a zona que o piso de R$ 40
milhões proíbe. Três marcas se destacam:

| | |
| - | - |
| 🔶 losango coral | a política que defendemos |
| 🔵 ponto teal | o cenário que você montou |
| 🎯 alvo verde | **o ótimo viável** — maior ROI entre as que passam nos quatro limites **nos três cenários** |

A distância entre o losango e o alvo é o preço que pagamos por folga no limite
de volume, e o painel a declara em pontos percentuais.

**As curvas** travam cinco alavancas e variam a sexta. A linha tracejada
coral é o nosso modelo; a sólida teal, o seu cenário. Enquanto nada for
alterado as duas coincidem — é assim que se vê que o simulador partiu do lugar
certo.

**A base C** lista as 5.000 propostas sob a política ativa, com busca por id,
ocupação e canal. A coluna de PD é a **re-escorada** com o LTV e o prazo que a
sua política oferta, não a do pedido.

**A cadeia de um contrato** percorre PD → EAD → LGD → perda esperada → preço
para a proposta selecionada, e diz o que a política fez com ela: se alongou o
prazo, se a entrada exigida mordeu, ou se a oferta bateu com o pedido.

## Como abrir

```
painel/index.html
```

Abra no navegador. Nada a instalar, nada a rodar: o `painel/dados.js` vem
versionado ao lado, e o painel funciona offline a partir de um clone.

> **Por que os dados estão no git.** Eles derivam da Base C — 5.000 propostas
> com renda, bureau e ocupação — e portanto cairiam na regra de não versionar
> dado. A exceção foi decidida em 25/09/2026 e está registrada no `.gitignore`
> e no `AGENTS.md`: a base é fictícia, é material do próprio desafio, o
> destinatário do repositório é o professor que a escreveu, e sem ela o painel
> não abre de um clone — que é o motivo de ele existir.

## Como regenerar

```powershell
.\scripts\py.cmd python\relatorios\25_dados_do_painel.py   # ~17 min: a varredura
.\scripts\py.cmd python\relatorios\26_tabelas_do_painel.py # anexa EAD/LGD, grava o .js
```

O segundo passo grava `painel/dados.js`, que define `window.DADOS`. É um
**script**, não um `fetch`: a versão publicada na web roda sob um CSP que
bloqueia requisições, e um `<script src>` de mesma origem passa.

A varredura guarda um cache em `outputs/painel/_grade.json`. Se ele existir e
tiver o tamanho da grade atual, os 17 minutos são pulados — apague o arquivo
para forçar a recontagem.

Ao fim, o `25` confere sozinho que o índice do padrão devolve 11,33% de ROI,
R$ 45,1 mi de volume pessimista e 6,33% de inadimplência. Se a conferência não
bater, a grade e o documento divergiram e o painel não deve ser publicado.
