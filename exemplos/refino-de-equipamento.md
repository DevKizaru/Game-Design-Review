# Exemplo trabalhado — sistema de refino de equipamento

Uma auditoria de ponta a ponta: a proposta como um DEV a escreveria, e o relatório inteiro que sai dela. Os números não são ilustrativos — todos saem de `scripts/auditoria_calc.py`, e os comandos estão no texto para você conferir.

O sistema é genérico de propósito (refino de equipamento é praticamente universal em MMO/OT). O objetivo é mostrar o formato, o uso das ferramentas e o tipo de achado que a skill produz — inclusive **o que ela aprova**.

---

## A proposta, como chegou

> Sistema de refino: equipamento vai de +0 a +10. Cada tentativa consome 1 pedra de refino e 5.000 de gold.
> Chances: +1 a +3 são 100%. Depois: +4 = 70%, +5 = 60%, +6 = 50%, +7 = 40%, +8 = 30%, +9 = 25%, +10 = 20%.
> Falha de +7 para cima destrói o equipamento.
> Cada nível de refino dá +4% de ataque.
> A pedra dropa na hunt de nível alto (mais ou menos 9 por hora) e também tem um NPC na cidade vendendo a 8.000 cada.

Contexto que precisou ser perguntado antes de qualquer conta: **gold por hora do jogador-alvo = 120.000**. Sem esse número, "8.000 por pedra" não significa nada.

---

# AUDITORIA — REFINO DE EQUIPAMENTO

## 1. Resumo executivo

O refino resolve um problema real e resolve bem: é um sink de gold que **cresce junto com o poder do jogador**, que é exatamente o tipo de dreno que uma economia madura precisa e quase nunca tem. Esse mérito é do desenho e está mantido no veredito.

O problema não está na curva de chances. Está no NPC. Ele torna o drop de pedra irrelevante (**+66,6% de custo total**, muito acima do limiar de escolha falsa) e transforma o refino, que deveria consumir tempo *e* gold, num sistema que consome só gold. Junto com a destruição sem teto acima de +7, isso produz um sistema cujo custo real é ilimitado e cuja única variável que o jogador controla é quanto gold ele tem.

**Veredito: 🟠 REFAZER — escopo pequeno.** Duas mudanças resolvem, nenhuma delas mexe em save.

## 2. Objetivo declarado vs. resultado real

| Declarado | Real |
|---|---|
| Dar um objetivo de longo prazo ao equipamento | ✅ Entrega. É o degrau de semana/temporada, e ele existia vazio |
| Consumir gold do jogador veterano | ✅ Entrega, e é o melhor achado positivo do sistema |
| Dar valor à hunt de nível alto (drop da pedra) | ❌ **Não entrega.** O NPC torna o drop desnecessário — ver P1 |
| Criar tensão de risco no refino alto | ⚠️ Entrega tensão, mas sem teto — ver P2 |

## 3. Como o sistema funciona

`AÇÃO` refinar → `RECOMPENSA` +4% de ataque por nível → `INVESTIMENTO` pedra + gold → `NOVA CAPACIDADE` hunt melhor → `AÇÃO melhor` mais gold para refinar. **O loop fecha** — que é mais do que se pode dizer da maioria dos sistemas de refino, onde a recompensa não volta para dentro da ação.

## 4. Enquadramento no loop

Degrau de **semana a temporada**, evergreen (regenera com cada item novo), com objetivo nomeável ("levar minha arma a +7"). Ocupa um degrau que costuma ser o mais vazio da escada. Isso é mérito, e sustenta boa parte do veredito.

## 5. Métricas e modelo

**Pedras esperadas para levar um item de +3 a +10**, somando a esperança geométrica de cada passo (1/p):

```
1/0,70 + 1/0,60 + 1/0,50 + 1/0,40 + 1/0,30 + 1/0,25 + 1/0,20
= 1,43 + 1,67 + 2,00 + 2,50 + 3,33 + 4,00 + 5,00 = 19,9 pedras
```

`MÉTRICA` ≈ **20 pedras e 100.000 de gold** para um +10 — **ignorando a destruição**. Com destruição acima de +7, o custo esperado é uma cadeia de Markov que a calculadora não faz; o ponto é que 20 pedras já é o **piso otimista**, e o piso otimista já é o problema.

Só o último passo, o +9 → +10:

```bash
python scripts/auditoria_calc.py gacha --p 0.20 --price 8000
```

```
media de pulls ate o 1o sucesso = 5.0
pulls para 90% de chance        = 10.3
pulls para 99% de chance        = 20.6
SEM PITY: a cauda e infinita. 1% dos jogadores passa de 21 pulls.
custo medio ate o alvo = 40000.00
```

`FATO` O jogador mediano gasta 5 pedras nesse passo. O percentil 99 gasta 21 — **quatro vezes mais que o mediano, na mesma mecânica**. Sem destruição isso seria só variância alta; com destruição, cada uma dessas 21 falhas apagou um item.

## 6. Resultados dos testes (por perfil)

| Perfil | O que acontece |
|---|---|
| **Casual** | Para em +6, onde a destruição começa. Comportamento correto e saudável |
| **Otimizador** | Compra pedra do NPC, ignora a hunt, refina até o gold acabar. Nunca vê o drop |
| **Abusador** | Refina item barato até +6 (sem risco de destruição) e revende. Ver P3 |
| **Longo prazo** | Todo o gold excedente vira refino. É o comportamento desejado, e ele funciona |

## 7. Problemas encontrados

### P1 · Severidade 7,00 · GRAVE · `MÉTRICA`

`severity --impacto 8 --frequencia 9 --exploracao 3 --persistencia 9 --custo 4`

**O NPC de pedras torna o drop conteúdo morto e converte o refino num sink exclusivamente de gold.**

```bash
python scripts/auditoria_calc.py fontes --recurso "pedra de refino" --valor-hora 120000 \
  --fonte "drop na hunt:0:9" --fonte "NPC da cidade:8000:99999"
```

```
  fonte                     custo/unidade      un/hora custo total/un
  drop na hunt                     0.0000         9.00     13333.3333
  NPC da cidade                 8000.0000     99999.00      8001.2000
  VENCEDORA: NPC da cidade
  A segunda melhor custa +66.6%.
  ESCOLHA FALSA: acima de 20% de margem o otimizador nunca
  olha para as outras. As demais fontes viram decoracao.
```

`FATO` Farmar a pedra custa **13.333 de gold equivalente**; comprá-la custa **8.001**. Farmar é 66,6% mais caro. O drop não é uma alternativa mais lenta — é uma alternativa pior nos dois sentidos, e nenhum jogador que saiba fazer a conta vai usá-la.

Três consequências, e a terceira é a que dói:

1. O objetivo declarado "dar valor à hunt de alto nível" não acontece.
2. O sistema deixa de consumir tempo e passa a consumir só gold — some a metade do custo que segurava o ritmo.
3. Existe **circuito**: gold → pedra → refino, e o refino aumenta o gold/hora. Enquanto o gold/hora crescer mais rápido que o preço fixo do NPC, o refino fica progressivamente mais barato para quem já refinou. `RISCO` de bola de neve.

**Correção mais barata:** o preço do NPC precisa ficar *acima* do custo de farmar, não abaixo — é a diferença entre teto de preço e substituto. Com 120.000/h e 9 pedras/h, o farm custa 13.333; um NPC a **20.000** vira rede de segurança sem virar atalho, e a hunt volta a ser a fonte principal. Não mexe em save, é uma linha de config.

### P2 · Severidade 6,40 · PROBLEMA · `RISCO`

`severity --impacto 9 --frequencia 6 --exploracao 2 --persistencia 9 --custo 3`

**Destruição sem teto acima de +7 produz custo esperado ilimitado num sistema de progressão.**

O jogador do percentil 99 não gasta "um pouco mais": ele perde 21 itens. Isso é aceitável em sistema opcional e cosmético, e não é aceitável em sistema que dá +4% de ataque por nível — porque aí ele deixou de ser opcional.

**Correção mais barata:** não remova a destruição, ela é a tensão do sistema. Coloque **piso**: falha acima de +7 volta o item para +6 em vez de destruir, e a destruição fica só para +10, com item de proteção comprável. O EV muda pouco; a cauda deixa de ser infinita.

### P3 · Severidade 4,20 · ATENÇÃO · `HIPÓTESE`

`severity --impacto 4 --frequencia 5 --exploracao 6 --persistencia 3 --custo 2`

**Refino até +6 é livre de risco, o que permite fabricar itens +6 baratos em série para revenda.**

Não é exploit grave — é margem previsível. Vira problema se o mercado de +6 competir com a hunt que deveria fornecer os itens. `MÉTRICA` a coletar: fração dos itens +6 no mercado que vieram de refino em vez de drop.

### P4 · Severidade 3,60 · ATENÇÃO · `RISCO`

`severity --impacto 5 --frequencia 7 --exploracao 1 --persistencia 2 --custo 1`

**Legibilidade: a chance de destruição precisa estar na tela, no momento da decisão.**

Ver `references/legibilidade.md`. Um jogador que descobre a destruição perdendo o item não teve uma experiência de risco — teve uma experiência de armadilha, e a diferença entre as duas é inteiramente de informação.

## 8. O que está certo, e por quê

Dito com a mesma firmeza dos problemas acima:

- **É um sink que cresce com o poder.** A maioria das economias tem só drenos de valor fixo, que viram irrelevantes conforme o jogador enriquece. Este acompanha. Mantenha.
- **O loop fecha.** A recompensa (+4% de ataque) volta para dentro da ação (mais gold/hora para refinar de novo). Isso não é automático — muitos sistemas de refino são becos sem saída.
- **A curva de chances está bem-feita.** 100% até +3 dá vitória garantida ao novato; a queda é gradual; o salto de risco coincide com o salto de custo. Não mexa nela.

## 9. Veredito

**🟠 REFAZER — escopo pequeno.** Duas linhas de configuração:

1. Preço do NPC de 8.000 → **20.000** (acima do custo de farm, e declarado como teto de preço, não como fonte).
2. Falha acima de +7 rebaixa para +6 em vez de destruir; destruição só no +10, com proteção comprável.

Nenhuma das duas toca save de jogador, e ambas podem ser revertidas se a medição desmentir.

## 10. Testes de aceite

1. Após o ajuste, `fontes` mostra o drop como vencedora, com o NPC entre +20% e +60% acima. *(Roda em 10 segundos, é a prova de P1.)*
2. Fração das pedras adquiridas via NPC abaixo de 35% em 30 dias.
3. Percentil 99 de itens destruídos por jogador ≤ 3 em 30 dias.
4. Taxa de uso da hunt de alto nível sobe em relação à semana anterior ao patch — se não subir, o objetivo declarado continua não sendo entregue e o problema não era só preço.

## 11. Registro de decisões

```
DEC-014 · 2026-08-25 · NPC de pedra de refino é teto de preço, não fonte
Sustentado por: farm custa 13.333 de gold equivalente (120k/h, 9 pedras/h);
                NPC a 20.000 fica 50% acima, dentro da faixa de teto.
Reabre se:      gold/hora do alvo passar de 180.000, OU o drop cair
                abaixo de 6 pedras/h, OU a fração comprada no NPC
                passar de 35%.
```

---

## O que este exemplo demonstra

- **Um número vindo de fora decidiu tudo.** Sem o gold/hora do jogador, "8.000 por pedra" é opinião. A primeira coisa que a auditoria fez foi pedir o número que faltava.
- **O achado principal não estava na curva.** A discussão natural seria sobre as porcentagens de sucesso — e elas estão certas. O problema estava num NPC que parecia detalhe de conveniência.
- **Duas linhas de config resolveram.** Nem tudo que é GRAVE é caro. A severidade mede o dano, não o tamanho da obra.
- **O relatório aprova o que está certo, nominalmente.** Se ele só listasse problemas, a próxima recomendação teria menos peso — e a seção 8 é o que impede o DEV de "consertar" o que já funcionava.
