# Modelagem — transformar sistema em número

Um sistema que você não consegue expressar em números você não consegue auditar; consegue no máximo ter uma impressão. Esta referência dá as fórmulas por domínio. Quando os dados existirem, calcule (use `scripts/auditoria_calc.py` para não errar aritmética). Quando não existirem, declare a lacuna e defina o experimento mínimo.

As métricas de **design e loop** — T_loop por degrau, densidade de recompensa, TTFF, razão evergreen, burn rate de conteúdo — moram em `design-e-loop.md`. Elas respondem a uma pergunta anterior a todas as daqui: se o sistema merece existir. Balancear com precisão um sistema que vive num degrau vazio da escada de loops é polir parafuso de carro sem motor.

## Índice

1. Combate
2. Economia
3. Loot e RNG
4. Progressão
5. Sistemas de tempo e cooldown
6. Monetização e gacha
7. Retenção
8. Custo de oportunidade
9. Power creep
10. Redundância: várias fontes para o mesmo recurso
11. Mapa de recursos e grafo de conversão
12. Quando faltam dados

---

## 1. Combate

| Métrica | Fórmula / definição |
|---|---|
| DPS efetivo | `dano_por_hit × hits_por_segundo × (1 + crit_chance × (crit_mult − 1)) × uptime` |
| TTK | `HP_efetivo / DPS_efetivo` |
| HP efetivo | `HP / (1 − redução_de_dano)` — mitigação percentual é multiplicativa; somar percentuais é o erro clássico |
| Burst | Dano máximo numa janela curta (o que decide PvP, não o DPS sustentado) |
| Dano recebido/min | Mede sustentabilidade; define se healing/pot é opcional ou obrigatório |
| Eficiência de recurso | `dano / mana` ou `dano / cooldown` — revela a skill que torna as outras inúteis |
| Scaling | Derivada do poder por nível/item; compare com o scaling do conteúdo |

**Uptime é o que quase todo mundo esquece.** Uma skill de 1000 de dano com 60 s de cooldown vale menos que uma de 200 sem cooldown. Sempre normalize por tempo antes de comparar.

**Breakpoints de combate:** compute quantos hits são necessários (`ceil(HP_efetivo / dano_por_hit)`). O balanceamento real acontece na fronteira do `ceil`: 1 ponto de dano pode valer 20% de TTK, ou zero. Liste onde estão essas fronteiras.

## 2. Economia

Classifique **toda** fonte:

- **Faucet** — cria recurso do nada (drop de mob, quest, daily, venda para NPC)
- **Sink** — destrói recurso (reparo, taxa, craft que consome, respawn pago, upgrade que queima)
- **Transferência** — move entre jogadores (mercado, trade). **Não é sink.**

```
Net Flow = Σ Faucets − Σ Sinks     (por jogador por hora, e agregado)
Estoque(t) = Estoque(0) + Net Flow × t × jogadores_ativos
```

Projete 1, 7, 30 e 90 dias. Um Net Flow positivo pequeno é normal (o jogo precisa crescer com a base). Um Net Flow que cresce com o poder do jogador é inflação garantida: quanto mais forte, mais gera, mais forte fica.

Métricas complementares: moeda/hora criada, moeda/hora destruída, custo médio/hora de jogar, lucro/hora, payback de investimento (quantas horas para um item se pagar) e velocidade de enriquecimento por percentil de jogador.

**Pergunta de corte:** *o jogador rico gasta em quê?* Se a resposta é "nada", o sink não existe e a moeda vira monopoly money — os preços de mercado sobem até excluir o jogador novo, que é quem sustenta a base.

## 3. Loot e RNG

```
EV = Σ (probabilidade_i × valor_i)
EV/hora = EV × kills_por_hora
Chance acumulada em n tentativas = 1 − (1 − p)^n
Tentativas para 50% de chance = ln(0.5) / ln(1 − p)
Tentativas para 90% de chance = ln(0.1) / ln(1 − p)
Média de tentativas até o primeiro sucesso = 1 / p
```

Nunca reporte só a chance. Reporte **EV, variância, pior caso, melhor caso, mediana e percentil 90**. Um drop de 0,1% tem média 1000 tentativas — mas 10% dos jogadores passarão de 2300 tentativas. Esses 10% desinstalam, e a média não vai contar isso para você.

**Pity/bad-luck protection** transforma distribuição geométrica (cauda infinita) em distribuição limitada. Quando não existe pity num item obrigatório para progredir, isso é achado, não detalhe.

**Diluição de tabela:** adicionar itens novos numa tabela de peso fixo reduz a chance de todos os outros. Todo patch que adiciona loot precisa mostrar a tabela antes/depois.

## 4. Progressão

| Métrica | O que revela |
|---|---|
| XP/hora por atividade | Qual atividade domina; as outras estão mortas |
| Tempo por nível | A curva; procure saltos que não têm recompensa correspondente |
| Tempo por milestone | Onde o jogador desiste |
| Custo por upgrade | Quando o custo cresce mais rápido que a renda, virou wall |
| Ganho marginal | `Δpoder / Δcusto` — quando cai demais, o upgrade é ilusório |
| Power delta | Diferença de poder entre jogador e conteúdo no mesmo instante |

Monte `Poder do jogador × tempo` contra `Poder do conteúdo × tempo`. Onde a curva do jogador fica muito acima: conteúdo trivial. Muito abaixo: wall. Paralela e colada demais por tempo demais: grind sem sensação de crescimento.

**Teste da hora perdida:** se o jogador parar de jogar por uma semana, quanto do progresso dele evapora e quanto tempo leva para recuperar? Sistemas que punem ausência têm retenção alta no papel e queima de jogador no longo prazo.

## 5. Sistemas de tempo e cooldown

Tempo médio, mínimo, máximo, frequência, uptime, downtime e recompensa/minuto. O que auditar:

- **Cooldown vs. duração**: se `duração ≥ cooldown`, o efeito tem 100% de uptime e deixa de ser decisão — vira estado permanente.
- **Loop fechado**: existe combinação que reduz o cooldown a ponto de tornar a habilidade infinita? Some todas as fontes de redução de cooldown e verifique o limite.
- **Timers reais vs. de sessão**: timers de horas do mundo real favorecem quem tem disponibilidade, não quem tem habilidade. Isso é decisão de design, não acidente — mas precisa ser declarada.
- **Sincronização**: eventos globais no mesmo minuto concentram carga (ver `performance.md`).

## 6. Monetização e gacha

```
EV por pull = Σ (p_i × valor_i)
Custo esperado até o alvo = preço_do_pull / p_alvo   (sem pity)
Com pity hard em N: custo_máximo = N × preço_do_pull
```

Audite: preço por unidade de poder, diferença de poder entre pagante e não pagante (`power gap`), tempo que o não pagante leva para alcançar o que o pagante compra, e se o funil paga **conveniência** ou **poder**. Vender conveniência preserva o jogo competitivo; vender poder transforma o ranking em extrato bancário.

Sinal vermelho objetivo: quando o `power gap` entre o percentil 50 dos pagantes e o percentil 90 dos não pagantes ultrapassa o intervalo em que o PvP/conteúdo cooperativo ainda funciona, o jogo perde a base não pagante — e com ela o público para quem os pagantes se exibem.

## 7. Retenção

D1, D7, D30, sessões/dia, duração de sessão, churn por segmento e por milestone. A pergunta que importa: **em qual passo específico o jogador some?** Retenção agregada esconde a resposta; retenção por milestone entrega o culpado.

Correlacione churn com os eventos do jogo: primeiro wipe, primeira wall, primeira derrota em PvP, primeiro item perdido. Se o pico de churn coincide com um sistema, esse sistema tem endereço.

## 8. Custo de oportunidade

Toda atividade compete com todas as outras pelo mesmo recurso escasso: o tempo do jogador.

```
Eficiência = recompensa / tempo   (XP/h, gold/h, valor de loot/h, progresso/min)
```

Compare todas as atividades na mesma unidade. Se A rende 2× B com o mesmo esforço, B precisa oferecer algo que A não oferece (variedade, risco, social, exclusividade). Se não oferece, B está morta — e o jogo é menor do que o mapa faz parecer.

## 9. Power creep

Compare versões históricas: o conteúdo novo invalida o antigo? O item novo é simplesmente melhor? O jogador precisa substituir tudo? O conteúdo antigo continua relevante?

```
Creep por patch = (poder_do_melhor_item_novo / poder_do_melhor_item_anterior) − 1
```

Acumule ao longo dos patches. Se a curva é exponencial, os números vão estourar o tipo de dado antes de estourar a paciência do designer — e aí vem a "compressão de stats", que é o eufemismo para admitir que o power creep venceu.

## 10. Redundância: várias fontes para o mesmo recurso

A pergunta mais barata de fazer e a mais cara de ignorar: **esse recurso já tem fonte?**

Quase toda proposta de sistema novo é, na verdade, uma porta nova para um recurso que já tem porta. Isso raramente é apresentado assim — vem como "um NPC que vende X", "um minigame que dá X", "uma daily que solta X" — e por isso passa por três reviews sem ninguém somar as fontes numa tabela só.

Monte a matriz antes de discutir qualquer valor:

| Fonte | Custo por unidade | Unidades por hora | O que ela oferece que as outras não oferecem |
|---|---|---|---|

A última coluna é a que decide. Se ela estiver vazia para alguma linha, essa fonte não é uma escolha: é um sistema duplicado com outro nome.

**Compare em custo total, não em preço.** O jogador não paga só o custo direto — paga também a hora que gastou:

```
custo_total_por_unidade = custo_direto + (valor_da_hora / unidades_por_hora)
```

Onde `valor_da_hora` é o custo de oportunidade real (o gold/h que ele ganharia fazendo a melhor atividade disponível). Sem isso, "de graça, mas lento" parece barato — e não é.

Três diagnósticos saem dessa conta, e só o primeiro costuma ser encontrado em review:

1. **Dominada nos dois eixos** — mais cara *e* mais lenta que outra. Conteúdo morto, sem discussão.
2. **Fora da disputa** — não é dominada, mas o custo total fica acima de ~20% da melhor. Morre igual, e é pior: não aparece numa checagem de dominância, então sobrevive ao review e morre só no servidor.
3. **Redundância prática** — duas ou mais fontes dentro de ~10% de custo total. O otimizador é indiferente, então **não existe decisão**. Isso não é trade-off, é o mesmo sistema escrito N vezes: N fluxos para o jogador aprender, N pipelines para o time manter, uma única coisa entregue.

Use `scripts/auditoria_calc.py fontes` — ela calcula a fronteira, marca as dominadas, as fora da disputa e as empatadas.

**Circuito de moeda.** Antes de aprovar qualquer fonte paga, verifique se a moeda gasta nela é a mesma que outra fonte do mesmo recurso consome ou produz. Se for, você fechou um circuito, e circuito tem só dois destinos:

- A fonte paga sai mais barata → a fonte original vira conteúdo morto **e** o sink que ela representava desaparece. O recurso que era destino do gold vira mais um jeito de gastar gold entre vários, e o preço de tudo se reajusta.
- A fonte paga sai mais cara → ninguém usa, e você entregou um NPC decorativo.

O caso intermediário — preço calibrado de propósito — é legítimo e tem nome: **teto de preço**. Um NPC que vende um recurso a um valor fixo define o preço máximo que ele pode ter no mercado entre jogadores. Isso estabiliza economia e protege o jogador novo. Mas é uma decisão de economia, não de conteúdo: precisa ser declarada como teto, precificada acima do farm eficiente, e auditada quando o farm mudar.

**Razões legítimas para uma segunda fonte existir** — todas exigem que a fonte ganhe em *outro eixo*, não no mesmo:

| Razão | O que a fonte nova precisa ter |
|---|---|
| Teto ou piso de preço | Preço fixo, deliberadamente acima do farm eficiente |
| Perfil diferente de jogador | Ganho AFK vs. ativo, solo vs. grupo, novo vs. veterano |
| Momento diferente | Emergência, early game, acesso antes do desbloqueio principal |
| Risco diferente | Mais rendimento com chance de perda |
| Função social | Exige grupo, trade ou guild — gera interação, não só recurso |

**O custo invisível de cada sistema a mais.** Além de manutenção, cada fonte nova entra na matriz de interações: com N sistemas tocando o mesmo recurso, existem N×(N−1)/2 pares para auditar a cada patch — e todo balanceamento futuro do recurso precisa ser feito N vezes. Três fontes para um recurso não custam o triplo: custam o triplo de código, o triplo de tuning e três vezes mais chance de um exploit nascer na costura entre elas.

## 11. Mapa de recursos e grafo de conversão

A seção anterior compara as portas de **um** recurso. Esta olha o jogo inteiro de uma vez — e é a checagem com melhor relação custo/benefício de toda a skill, porque cabe numa página e revela em segundos problemas que passam por três reviews.

**Passo 1 — liste todo recurso do jogo.** Moeda, materiais, consumíveis, energia, tickets, tempo, reputação, tudo que o jogador acumula ou gasta.

**Passo 2 — preencha uma linha por recurso:**

| Recurso | Faucets (quem cria) | Sinks (quem destrói) | Transferências | O rico gasta em quê? |
|---|---|---|---|---|

**Passo 3 — leia a tabela.** Cinco padrões saltam sem precisar de conta nenhuma:

- **Coluna de sinks vazia** → o recurso só acumula. Inflação garantida, é só questão de quando.
- **Coluna "o rico gasta em quê" vazia** → o recurso tem teto de utilidade. Passado esse teto ele vira monopoly money e o preço de mercado exclui o jogador novo.
- **Três ou mais faucets** → candidato a redundância. Aplique a seção 10.
- **Um sink só, e ele é opcional** → não é sink, é sugestão. Meça que fração dos jogadores realmente gasta ali.
- **Transferência classificada como sink** → erro clássico e fatal. Trade entre jogadores move recurso, não destrói. Metade das economias quebradas nasce dessa linha preenchida errado.

**Passo 4 — desenhe o grafo de conversão.** Liste toda conversão possível entre recursos, com a taxa:

```
gold --(NPC de food, 60g/un)--> food
food --(farm da base, 4,2k gold/h -> 120 food/h)--> food
minério --(craft)--> equipamento --(venda p/ NPC)--> gold
```

Duas coisas importam nesse grafo:

- **Ciclos.** Qualquer caminho que saia de um recurso e volte a ele é um circuito. Multiplique as taxas ao longo do ciclo: se o produto for **> 1**, existe arbitragem — dinheiro infinito, e o jogador vai achar antes de vocês. Se for **< 1** mas o ciclo existir mesmo assim, alguma etapa é conteúdo morto.
- **Caminhos paralelos.** Dois caminhos diferentes ligando os mesmos dois recursos são a definição de redundância. O jogador usa o de melhor taxa; o outro existe para constar.

Um ciclo com produto exatamente 1 e alguma perda de tempo é o caso saudável: é assim que se faz uma economia circular sem arbitragem.

**Quando refazer o mapa:** sempre que entrar recurso novo, conversão nova, NPC que compra ou vende, ou sistema de craft. É o único documento da auditoria que deve ficar permanentemente atualizado — todos os outros são fotografias, este é o mapa do terreno.

## 12. Quando faltam dados

Não invente. Entregue esta estrutura:

```
## Dados faltantes
[exatamente o que precisa ser coletado, com granularidade]
## Teste mínimo
[o menor experimento que decide a questão, com duração e amostra]
## Hipótese atual
[o que parece provável e por quê]
## Confiança
[0–100%]
```

Um "meça X durante Y com amostra Z" é entregável. Um número inventado é sabotagem com aparência de rigor.
