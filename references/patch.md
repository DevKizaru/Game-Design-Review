# Auditoria de patch — quando o número já está no save de alguém

O modo pré-mortem audita o que ainda não existe. A auditoria normal audita o que existe. Esta audita **a mudança** — e é provavelmente o pedido mais frequente que a skill vai receber, na forma *"mexi nesses números, o que quebra?"*.

O que a torna diferente das outras duas: o sistema já tem jogadores, já tem histórico e já tem outras coisas calibradas contra o valor antigo. Auditar um patch olhando só as linhas do diff é auditar o buraco e ignorar a parede.

---

## 1. O inventário do diff não é "o que mudou"

São três listas, e só a primeira está no diff:

| Lista | O que entra |
|---|---|
| **Mudou** | Os valores alterados. Fácil, está no diff |
| **Dependia** | Tudo que foi calibrado *tomando o valor antigo como referência*. Este é o inventário que ninguém faz |
| **Atravessou** | O que cruzou um limiar por causa da mudança. Ver seção 2 |

A segunda lista é o trabalho todo. A pergunta que a produz:

> **Quando esse número foi escolhido, o que mais foi escolhido junto por causa dele?**

O custo de uma poção foi definido olhando o gold/hora da zona. A zona mudou. O custo da poção não mudou — e agora está errado, sem que ninguém o tenha tocado. **Um patch produz bugs de balanceamento em arquivos que ele não modifica**, e é por isso que auditar patch por diff é insuficiente por construção.

---

## 2. Breakpoints atravessados

A pergunta é mecânica e vale a pena rodar sempre: **algum valor mudou de lado em relação a um limiar?**

- 2 hits viram 3 (ou 3 viram 2) — `auditoria_calc.py ttk` dá os breakpoints;
- o cooldown passou a caber (ou deixou de caber) dentro do loop;
- o custo passou a caber na renda de uma hora de farm;
- um nível deixou de ser wall, ou virou um — `auditoria_calc.py progressao`;
- uma fonte passou a dominar outra na matriz — `auditoria_calc.py fontes` antes e depois.

Breakpoint atravessado é o achado mais comum de patch e o mais barato de encontrar: são todos aritmética, e todos têm ferramenta.

---

## 3. Quem já jogou sob a regra velha

Todo patch cria duas populações, e a decisão sobre elas costuma ser tomada por omissão:

- **Quem já pagou o preço antigo.** Se o custo caiu, houve devolução? Se não houve, o veterano pagou mais pela mesma coisa — o que pode ser aceitável, desde que dito.
- **Quem já recebeu a recompensa antiga.** Se o ganho caiu, quem pegou antes tem vantagem permanente. Se subiu, quem pegou antes tem a versão pior para sempre.
- **Quem está no meio.** O jogador que começou um objetivo longo sob a regra velha e vai terminá-lo sob a nova. É o mais esquecido e o que mais reclama, com razão.

A pergunta que resolve as três:

> **A mudança é retroativa, prospectiva ou compensada?**

Escolher em silêncio é escolher "prospectiva" — e descobrir isso pelo fórum. Escrever a escolha custa uma linha e evita a conversa inteira.

---

## 4. O teste do patch anterior

Um patch isolado nunca parece power creep. A série, sim:

```
razão = valor novo ÷ valor anterior, patch a patch
```

Se a razão média dos últimos N patches for maior que 1 no eixo de poder, existe escada de inflação, e cada patch a mais encurta a vida do conteúdo antigo. Ver `modelagem.md`, seção 9. **O achado não é o patch atual — é a série**, e por isso ele só aparece para quem olha o histórico.

O mesmo vale na direção contrária: uma série de nerfs sucessivos no mesmo sistema não é balanceamento fino, é um sistema que ninguém entendeu ainda.

---

## 5. Regressão: o que era verdade e deixou de ser

É para isso que o **registro de decisões** existe. Toda entrada `DEC-XXX` tem a linha `Reabre se:` com condição numérica; um patch é exatamente o momento de reler essa linha.

Fluxo mínimo:

1. Liste as decisões cuja condição de reabertura foi tocada pelo patch.
2. Para cada uma, diga se reabriu ou não — **incluindo as que não reabriram**, porque isso também é informação.
3. Decisão reaberta vira achado com severidade, não nota de rodapé.

Sem registro de decisões, este passo é impossível e a auditoria de patch vira arqueologia. Se o projeto ainda não tem registro, **este é o achado**, e ele é mais grave que qualquer número do diff.

---

## 6. Formato do relatório de patch

Mais curto que a auditoria de sistema, de propósito — patch é frequente, e um formato caro não é usado:

```
# PATCH — [nome/versão]
## 1. O que mudou            (valor antigo → novo, por linha)
## 2. O que dependia disso   (calibrado contra o valor antigo)
## 3. Breakpoints atravessados
## 4. Populações afetadas    (retroativo / prospectivo / compensado)
## 5. Decisões reabertas     (DEC-XXX, incluindo as que não reabriram)
## 6. Risco de regressão     (e o teste que o pega antes do jogador)
## 7. Veredito               (subir / subir instrumentado / segurar)
```

O veredito **"subir instrumentado"** é o mais útil dos três e o menos usado: aprova o patch e nomeia as duas ou três métricas que precisam estar sendo coletadas quando ele entrar, para que a próxima auditoria não comece do zero (`instrumentacao.md`).

---

## 7. Armadilhas específicas de patch

- **Nerf em cascata** — o item nerfado era o contrapeso de outro. Nerfar A sem olhar B promove B a dominante sem que ninguém tenha tocado em B.
- **Buff que vira torneira** — aumentar recompensa é aumentar faucet. Rode `netflow` antes e depois; um buff de 20% num drop popular pode ser a maior entrada de moeda do servidor.
- **Correção de sintoma** — o preço subiu, então taparam o preço. A causa era a torneira nova de dois patches atrás. Sintoma corrigido é achado adiado com juros.
- **Mudança silenciosa** — valor alterado sem changelog. O ganho é evitar reclamação hoje; o custo é a confiança, que não volta com hotfix. Rotule como RISCO, não como MÉTRICA.
- **Hotfix que virou design** — o número emergencial de seis meses atrás nunca foi revisto e hoje é a base de outras calibragens. Todo hotfix precisa de data de revisão, ou vira dívida com aparência de decisão.
- **Patch que só o autor entende** — se ninguém além de quem escreveu consegue dizer o que muda para o jogador, o changelog não existe ainda, mesmo que o arquivo exista.
