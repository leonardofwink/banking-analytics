# Matriz de riscos — inerente → controles → residual

> A tradução prática da terminologia do [`GLOSSARIO.md`](GLOSSARIO.md#1-gestão-de-risco--o-eixo-inerente--controle--residual).
> **Status: modelo a preencher.** As linhas abaixo são *exemplos ilustrativos* para mostrar o formato — substitua pelos riscos reais quando o escopo da mentoria estiver definido, e apague o que não se aplicar.

## Como usar

Para cada risco identificado:

1. **Avalie o inerente primeiro**, fingindo que nenhum controle existe. Avaliar já olhando para os controles é o erro mais comum — subestima o inerente e faz a mitigação parecer desnecessária.
2. **Liste os controles que de fato operam** — não os que estão no manual. Controle que ninguém executa reduz risco em zero.
3. **Avalie o residual** com os controles funcionando.
4. **Compare com o apetite** e decida: aceitar, mitigar mais, transferir ou evitar.

### Escalas

**Probabilidade** e **Impacto**, de 1 a 5. O **nível** é o produto (1 a 25):

| Nível | Faixa | Leitura |
| ----- | ----- | ------- |
| 🟢 Baixo | 1–4 | Aceitar e monitorar |
| 🟡 Moderado | 5–9 | Aceitar com controle formalizado |
| 🟠 Alto | 10–15 | Mitigar — plano de ação com dono e prazo |
| 🔴 Crítico | 16–25 | Mitigar ou evitar — escalar à decisão |

> A escala é uma convenção do projeto, não uma verdade. O que importa é ser **a mesma** para todos os riscos — nota de risco só serve para comparar.

---

## Riscos do negócio (crédito)

| # | Risco | Inerente (P×I) | Controles / mitigadores existentes | Residual (P×I) | Resposta | Dono |
| - | ----- | -------------- | ---------------------------------- | -------------- | -------- | ---- |
| N1 | *(exemplo)* Concessão a cliente que não tem capacidade de pagamento | 4×4 = 16 🔴 | Política de crédito; score de aprovação com cutoff; consulta a bureau; comprovação de renda | 2×4 = 8 🟡 | Mitigar | |
| N2 | *(exemplo)* Concentração da carteira em um segmento/região | 3×5 = 15 🟠 | Limites de exposição por segmento; monitoramento mensal de concentração | 2×4 = 8 🟡 | Mitigar | |
| N3 | *(exemplo)* Provisão insuficiente para a perda realizada | 3×5 = 15 🟠 | Cálculo de ECL; backtesting da provisão vs. perda observada | | | |

## Riscos do modelo

> Risco de modelo é uma categoria própria e frequentemente esquecida: o modelo **é** um controle, e um controle que falha silenciosamente é pior que controle nenhum.

| # | Risco | Inerente (P×I) | Controles / mitigadores | Residual (P×I) | Resposta | Dono |
| - | ----- | -------------- | ----------------------- | -------------- | -------- | ---- |
| M1 | *(exemplo)* **Vazamento de informação** — variável da janela de performance entra na janela de observação, inflando a performance | 4×5 = 20 🔴 | Revisão explícita das janelas; validação out-of-time; desconfiar de IV > 0,5 | | Mitigar | |
| M2 | *(exemplo)* **Degradação do modelo** — a população muda e o score para de ordenar | 4×4 = 16 🔴 | Monitoramento de PSI e KS por safra; gatilho de recalibração | | Mitigar | |
| M3 | *(exemplo)* **Viés de seleção** — o modelo só viu quem foi aprovado | 5×3 = 15 🟠 | Reject inference; monitorar swap set | | | |
| M4 | *(exemplo)* **Variável proibida ou discriminatória** entra no modelo | 3×5 = 15 🟠 | Revisão da lista de variáveis candidatas; teste de proxy | | | |
| M5 | *(exemplo)* **Irreprodutibilidade** — ninguém consegue refazer o resultado | 4×3 = 12 🟠 | Semente fixa; pipeline versionado em git; dados reconstruíveis a partir dos scripts | | Mitigar | |

## Riscos do projeto (execução e dados)

| # | Risco | Inerente (P×I) | Controles / mitigadores | Residual (P×I) | Resposta | Dono |
| - | ----- | -------------- | ----------------------- | -------------- | -------- | ---- |
| P1 | *(exemplo)* **Vazamento de dado pessoal / sigilo bancário** — base com CPF vai parar no git ou é compartilhada indevidamente | 3×5 = 15 🔴 | `.gitignore` bloqueando todo formato de dado; regra crítica em `AGENTS.md`; anonimização na ingestão | 1×5 = 5 🟡 | Mitigar | Leonardo |
| P2 | *(exemplo)* Perda do trabalho por falha de máquina | 2×4 = 8 🟡 | Repositório remoto no GitHub; commits frequentes | | Mitigar | Leonardo |
| P3 | *(exemplo)* Escopo indefinido leva a retrabalho | 4×3 = 12 🟠 | PRD com decisões registradas; validar entendimento antes de implementar | | | |

---

## Riscos aceitos conscientemente

> Registrar aqui o que foi **decidido aceitar**, com quem decidiu e quando. Risco aceito sem registro vira, meses depois, "ninguém sabia".

| # | Risco | Por que aceitamos | Quem decidiu | Data | Revisar em |
| - | ----- | ----------------- | ------------ | ---- | ---------- |
| | | | | | |
