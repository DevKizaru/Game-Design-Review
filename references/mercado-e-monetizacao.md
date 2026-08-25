# Mercado e monetização — a economia pelo lado de fora

`modelagem.md` trata a economia por dentro: quem cria recurso, quem destrói, qual o fluxo líquido. Esta referência trata o mesmo sistema pelo lado de fora — **o preço que o jogador vê** e **o dinheiro real que entra**.

Estão no mesmo arquivo de propósito. A loja define o teto do mercado, o mercado define o valor do que está na loja, e o RMT existe exatamente no espaço entre os dois. Auditar um dos três sozinho produz conclusão errada com aparência de rigor.

## Índice

1. O mercado é o instrumento de medição que você já tem
2. Formação de preço e o que cada padrão significa
3. Liquidez: existir no jogo não é existir no mercado
4. Bot e RMT: a oferta que você não criou
5. Loja de doação: o que dá para vender sem vender o jogo
6. Conveniência ou vantagem — a linha e o teste que a acha
7. Teto de poder pago: a conta que ninguém escreve
8. Onde os dois se encontram: o item pago e comerciável
9. Métricas e o que entregar no relatório

---

## 1. O mercado é o instrumento de medição que você já tem

Antes de pedir telemetria (`instrumentacao.md`), olhe o que já existe. Num jogo com trade entre jogadores, **todo problema de economia aparece como preço antes de aparecer como reclamação** — e o log de trades já está no banco.

O que o mercado responde de graça:

| Pergunta | O que ler |
|---|---|
| A inflação é real ou teórica? | Preço de um item de referência ao longo dos meses, não o total de moeda no servidor |
| Este item é conteúdo morto? | Anúncios ativos. Item que ninguém anuncia nem procura está morto, sem precisar de taxa de uso |
| Entrou uma torneira que eu não contei? | Preço caindo sem patch que justifique |
| Quanto vale uma hora de jogo aqui? | Razão preço ÷ tempo de farm do item. É o `--valor-hora` do `fontes`, medido pelos jogadores em vez de estimado por você |
| O jogador novo ainda entra? | Preço dos itens de entrada expresso em **horas de farm de quem começou hoje**, não em moeda |

Esta última é a mais importante e a menos feita. Preço em moeda não diz nada ao longo do tempo; preço em horas de farm do novato é comparável entre patches e é o número que decide se o servidor ainda recebe gente.

---

## 2. Formação de preço e o que cada padrão significa

O preço de equilíbrio de um item farmável tende a:

```
preço ≈ custo de oportunidade de farmá-lo + prêmio de conveniência − desconto de risco
```

Ou seja: o mercado converge para o `custo_total_por_unidade` da seção 10 de `modelagem.md`, calculado pelos jogadores, com mais precisão do que a sua planilha. Quando ele **não** converge, o desvio é o achado:

| Padrão observado | Leitura |
|---|---|
| Preço colado no valor do NPC | O NPC é o mercado. Teto de preço ativo — saudável **se** foi decisão declarada, sintoma se não foi |
| Preço bem abaixo do custo de farm | Existe oferta que não veio de farm: bot, dupe, drop mal calibrado ou recompensa de evento esquecida ligada |
| Preço subindo mais rápido que a renda do jogador médio | O jogador novo está sendo excluído. Meça em horas de farm, não em moeda |
| Preço estável e volume caindo | O item está saindo de uso. Sem preço se mexer, é fácil não perceber |
| Spread enorme entre compra e venda | Mercado ilíquido: o item na prática não tem preço, tem duas opiniões distantes |
| Preço que só sobe, nunca corrige | Não há sink suficiente para o item, ou ele virou reserva de valor — dinheiro disfarçado de item |

---

## 3. Liquidez: existir no jogo não é existir no mercado

Um item que o design assume que o jogador tem, mas que leva três semanas para aparecer à venda, **não existe** para efeito de progressão. Isso quebra qualquer curva calibrada supondo que ele estaria disponível.

Três medidas baratas:

- **Anúncios ativos** por item, por semana.
- **Tempo até vender** ao preço mediano. Se passa de dias, o item não é comerciável na prática.
- **O teste do jogador novo**: quanto tempo desde a criação da conta até conseguir comprar o item que a curva de progressão assume que ele terá naquele nível. Se a resposta é maior que o tempo que ele leva para chegar no nível, a curva está calibrada contra um item que não está lá.

---

## 4. Bot e RMT: a oferta que você não criou

Bot e RMT são o mesmo fenômeno visto em dois pontos: um cria oferta que você não desenhou, o outro a vende por dinheiro real.

**Como aparecem no mercado, antes de aparecerem em qualquer denúncia:**

- preço de um recurso caindo sem patch → oferta nova sem faucet novo;
- um item com volume alto e poucos vendedores distintos;
- atividade constante em horário e ritmo sem variação humana — isso é `instrumentacao.md`, não mercado, mas o mercado é quem levanta a suspeita.

**A conta que decide se você vai ter bot:**

```
valor_real_por_hora_de_farm = preço de RMT do recurso ÷ recurso farmado por hora
```

Se esse número compensa o salário-hora em algum lugar do mundo, **você vai ter bot** — não é questão de moral do seu público, é aritmética. A defesa não é só banir: é reduzir o valor real por hora (limitar o que é farmável sem atenção) ou aumentar o custo de operar (verificação, variação, presença humana exigida).

**O dano principal não é econômico, é de legitimidade.** O jogador honesto não abandona porque o preço subiu; abandona quando percebe que o preço é ditado por quem não está jogando. Isso é RISCO, não MÉTRICA — e deve ser rotulado assim no relatório.

**E o RMT precifica a sua loja.** Se o ouro do servidor sai mais barato no mercado paralelo do que na sua loja de doação, o RMT não é concorrente: ele é o teto do seu preço. Auditar a loja sem olhar o preço de RMT é auditar metade.

---

## 5. Loja de doação: o que dá para vender sem vender o jogo

Ordenado por dano crescente ao jogo:

| O que se vende | O que custa |
|---|---|
| **Cosmético** | Nada de balanceamento. Monetiza identidade e testemunha — o melhor produto que existe |
| **Conveniência** (slot, mula, guarda-volumes, viagem) | Pouco, **se** não converter em poder por hora. Ver seção 6 — quase sempre converte |
| **Tempo** (XP boost, velocidade, energia) | Poder por hora direto. Atinge a curva de progressão inteira, que foi calibrada sem ele |
| **Poder** (item, atributo, exclusivo) | Define o teto do servidor. A partir daqui, existe um segundo jogo |
| **Aleatório pago** (caixa, baú, roleta) | Tudo o que está acima, mais o problema de gacha (`modelagem.md`, seção 6) e o risco regulatório |

A pergunta que corta, e que vale mais que a tabela inteira:

> **O não-doador chega no mesmo lugar? Em quanto tempo?**

- "Chega em algumas semanas a mais" → é conveniência precificada. Legítimo.
- "Chega, mas em tempo que ninguém joga" → é vantagem com desculpa. Diga o número.
- "Não chega nunca" → não é loja, é assinatura de vantagem permanente, e o servidor passa a ter duas populações que não competem pelas mesmas coisas.

Nenhuma das três é proibida. **Todas as três precisam ser escolhidas de propósito e escritas** (`DEC-XXX`), porque cada uma implica um jogo diferente — e a terceira implica um jogo que precisa de PvP separado, ranking separado ou nenhum dos dois.

---

## 6. Conveniência ou vantagem — a linha e o teste que a acha

"É só conveniência" é a frase mais usada para aprovar venda de poder, e ela tem um teste objetivo:

> **Converta a compra em horas por semana. Se dá para expressar em horas, é vantagem.**

Dez slots a mais de inventário não são poder — até você multiplicar por vinte horas semanais de jogo e descobrir que economizam quatro viagens por sessão. Quatro horas por semana economizadas são quatro horas por semana de vantagem, e a curva de progressão não sabe distinguir a origem delas.

Isso não significa que conveniência não pode ser vendida. Significa que ela **entra na conta da seção 7 como poder**, em vez de ficar de fora sob um rótulo simpático.

Duas armadilhas específicas:

- **Conveniência composta.** Cada compra isolada é defensável; o pacote inteiro não. Some sempre o conjunto, nunca item a item — é o mesmo erro da matriz de fontes feita linha a linha.
- **Conveniência que vira requisito.** Se todo mundo compra, o design passa a ser calibrado supondo que o jogador tem, e a compra deixa de ser opcional sem que ninguém tenha decidido isso. Meça a **taxa de adoção**: acima de ~80%, aquilo não é loja, é parte do jogo cobrada à parte.

---

## 7. Teto de poder pago: a conta que ninguém escreve

Três números. Nenhum deles é difícil, e é justamente por isso que a ausência deles é um achado:

```
razão_de_poder   = poder do maior doador ÷ poder do não-doador com o mesmo tempo de jogo
tempo_de_alcance = horas que o não-doador leva para igualar o doador de hoje
fração_paga      = quanto do poder médio do servidor veio da loja
```

Não existe valor universalmente correto — existe valor **declarado**. O que a auditoria exige é que o número exista escrito antes do patch, não depois da reclamação.

Como referência de leitura (isto é convenção observada, não lei — rotule como OPINIÃO no relatório):

- razão até ~1,3 costuma ser lida pelos jogadores como conveniência;
- razão a partir de ~2,0 costuma ser lida como "dois jogos", e o PvP perde sentido junto;
- `tempo_de_alcance` maior que a vida média do jogador no servidor é o mesmo que "nunca", com aparência de "algum dia".

**Um servidor que não sabe dizer sua razão de poder já escolheu uma — só não sabe qual.**

---

## 8. Onde os dois se encontram: o item pago e comerciável

O ponto de encontro é um item comprado com dinheiro real que pode ser negociado entre jogadores. Isso não é erro — é a base do modelo de vários servidores grandes, e resolve um problema real (dá ao não-doador um caminho para o conteúdo pago). Mas muda a natureza da economia inteira, e precisa ser auditado como tal:

- **A loja vira a torneira principal.** Todo item do jogo passa a ser cotado, mentalmente, em moedas de doação. O preço da loja vira o piso de referência de tudo.
- **O RMT deixa de ser concorrente e vira revendedor.** Isso reduz o RMT bruto, e em troca coloca você como criador da oferta que ele distribui.
- **Todo ajuste de preço na loja é um patch de balanceamento** no servidor inteiro, e deve passar por `patch.md` como qualquer outro.
- **O grafo de conversão passa a ter uma aresta que entra de fora** (`modelagem.md`, seção 12). Verifique ciclos: se existe caminho de dinheiro real → item → moeda → item de loja, você fechou um circuito com uma torneira infinita numa ponta.

---

## 9. Métricas e o que entregar no relatório

| Métrica | Onde sai | Sem telemetria |
|---|---|---|
| Preço em horas de farm do novato | Log de trade ÷ rendimento medido | Amostra manual de anúncios por uma semana |
| Anúncios ativos e tempo até vender | Log de mercado | Contagem manual, dois pontos no tempo |
| Valor real por hora de farm | Preço de RMT observado | Consulta aos canais onde o seu jogo é revendido |
| Razão de poder pago | Comparação de dois personagens equivalentes | Simulação em planilha do pacote completo da loja |
| Taxa de adoção da conveniência | Eventos de compra ÷ ativos | Enquete, com a ressalva de amostra |
| Fração da economia que passa pela loja | Faturamento convertido em poder ÷ poder total | Não estime. Declare a lacuna |

No relatório, o mercado entra na seção **Impactos sistêmicos** e a loja entra em **Objetivo declarado vs. resultado real** — porque o objetivo declarado de uma loja quase nunca é o que ela produz depois de seis meses.

E vale a regra geral da skill, que aqui é fácil de esquecer porque o assunto é dinheiro: **monetização agressiva não é falha moral a ser denunciada, é decisão de produto a ser medida.** O que a auditoria cobra não é virtude, é o número e a decisão escrita.
