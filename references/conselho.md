# O Conselho

Dez especialistas independentes. Não ative todos por reflexo — ative os que o alvo justifica. Auditar um drop rate chama Balanceamento, Economia, Dados e QA; auditar um sistema de partida chama Arquiteto, Performance e Designer; auditar uma feature nova, um endgame ou um plano de conteúdo chama o Diretor de Loop e Conteúdo antes de todo mundo. O Advogado do Diabo entra **sempre** que houver veredito 🟠 ou 🔴, porque veredito duro sem contraditório é linchamento.

## Índice

1. Arquiteto de Sistemas
2. Especialista em Balanceamento
3. Economista do Jogo
4. Analista de Progressão
5. QA / Caçador de Exploits
6. Analista de Dados
7. Designer de Experiência
8. Engenheiro de Performance
9. Diretor de Loop e Conteúdo
10. Advogado do Diabo
11. Formato do debate
12. Votação

---

## 1. Arquiteto de Sistemas

Analisa dependências, acoplamento, loops sistêmicos, escalabilidade, interações entre sistemas, efeitos cascata, complexidade, dívida técnica e risco de manutenção.

> **"O que acontece quando esse sistema interage com os outros 20 sistemas que o DEV fingiu que não existiam?"**

Entrega obrigatória: a **matriz de dependências** no formato `Sistema auditado → sistemas afetados`. Exemplo: `Loot → Economia → Mercado → Progressão → Endgame`. Nenhum sistema com dependências relevantes pode ser julgado isoladamente.

Segunda entrega, curta e implacável: a **carta de identidade do sistema** — uma frase dizendo para que ele serve e o que deixa de existir no jogo se ele for apagado. Se dois sistemas produzem a mesma frase, um dos dois é redundante, e o Arquiteto é quem tem que dizer qual. É aqui que morre a proposta de dar uma terceira porta a um recurso que já tem duas: não por estar desbalanceada, mas por não ter identidade própria. Ver `modelagem.md`, seção 10.

Terceira entrega, e a que o Arquiteto costuma esquecer porque ela não parece acoplamento: **em série ou em paralelo?**. Se a proposta empilha etapas obrigatórias antes de um recurso — plantar para alimentar para criar para cozinhar — ele passa elo por elo com o teste *“decisão ou só um passo?”* e diz quantos elos são pedágio. Cada elo a mais derruba a confiabilidade da linha inteira e a vazão fica presa no elo mais lento, então esse é o único lugar do debate onde “profundidade de sistema” pode significar exatamente o oposto do que parece. Ver `modelagem.md`, seção 11.

## 2. Especialista em Balanceamento

Analisa DPS, TTK, HP, defesa, progressão, recompensas, custos, probabilidades, scaling, breakpoints, eficiência, power creep, conteúdo trivial e conteúdo impossível.

> **"Existe uma escolha realmente boa ou existe uma opção obviamente superior?"**

Entrega obrigatória: a lista de **breakpoints** e o veredito de **dominância** para cada conjunto de escolhas. Se não conseguir explicar em uma frase por que alguém escolheria a opção B, a opção B é decoração.

## 3. Economista do Jogo

Analisa inflação, geração e destruição de moeda, valor dos itens, drop rates, mercado, oferta/demanda, acumulação, velocidade de enriquecimento, impacto de bots, arbitragem e abuso de contas alternativas.

> **"Se 10.000 jogadores fizerem isso durante 90 dias, a economia sobrevive?"**

Entrega obrigatória: classificação de cada fonte como **faucet**, **sink** ou **transferência**, e o `Net Flow = Faucets − Sinks` projetado para 1, 7, 30 e 90 dias. Transferência entre jogadores não destrói recurso — não conte como sink; esse erro é responsável por metade das economias quebradas.

## 4. Analista de Progressão

Analisa onboarding, early/mid/late game, endgame, tempo até desbloqueios, gargalos, walls, sensação de crescimento, repetição e conteúdo obrigatório.

> **"O jogador está progredindo ou apenas trabalhando para preencher uma barra?"**

Entrega obrigatória: a curva `Poder do jogador × tempo` sobreposta a `Poder do conteúdo × tempo`, apontando plateau, wall, salto artificial, grind excessivo, progressão explosiva, conteúdo trivial e conteúdo impossível. Onde as curvas se cruzam errado, o jogador desinstala.

## 5. QA / Caçador de Exploits

Procura duplicação, loops infinitos, reset abuse, reward stacking, cooldown bypass, race conditions, abuso de reconnect/relog, multi-conta, manipulação de RNG, interações não previstas e combinações quebradas.

> **"Como um jogador mal-intencionado destruiria esse sistema em 30 minutos?"**

Entrega obrigatória: pelo menos uma tentativa **concreta** de quebrar o sistema, descrita passo a passo, mesmo que falhe. "Não achei exploits" só vale depois de descrever o que foi tentado. Catálogo completo em `testes-e-exploits.md`.

## 6. Analista de Dados

Define métricas, amostras, baseline, distribuição, outliers, correlações, experimentos A/B, intervalos de confiança e critérios de aprovação/reprovação.

> **"Qual número provaria que essa decisão está errada?"**

Entrega obrigatória: o **critério de falsificação**. Se ninguém consegue nomear o número que refutaria a decisão, a decisão não é técnica — é gosto pessoal com verniz. O Analista de Dados também é quem impede o conselho de brigar com dados inventados: quando faltar amostra, ele declara falta de amostra em vez de deixar o debate seguir no vácuo.

Quando o dado não existir, ele não encerra o assunto com "não temos dados": entrega **o evento a instrumentar, a pergunta que ele responde e a amostra necessária**, para que a auditoria seguinte tenha FATO onde esta teve HIPÓTESE. Ver `instrumentacao.md`.

## 7. Designer de Experiência

Analisa clareza, frustração, recompensa, agência, repetição, feedback, escolhas, sensação de justiça e a relação esforço × recompensa.

> **"O jogador está se divertindo ou apenas sendo condicionado a continuar?"**

Entrega obrigatória: o ponto onde a **estratégia ótima diverge da estratégia divertida**. Todo jogo em que jogar bem é chato perde os jogadores bons primeiro e os ruins depois.

Segunda entrega, quando houver escolha envolvida: o cruzamento de **poder real × taxa de uso**. Força medida e uso que não conversam significam problema de informação, não de valor — e é aqui que se evita o patch clássico de nerfar algo forte que ninguém usava. Quadrantes, sinais de ilegibilidade e como auditar sem telemetria em `legibilidade.md`.

## 8. Engenheiro de Performance

Analisa CPU, RAM, rede, banco de dados, queries, loops, frequência de eventos, concorrência, escalabilidade, spikes e latência.

> **"Funciona com 10 jogadores ou funciona com 10.000?"**

Entrega obrigatória: o custo por unidade (por jogador, por entidade, por tick) e onde ele deixa de ser linear. Detalhes por camada em `performance.md`.

## 9. Diretor de Loop e Conteúdo

Analisa o núcleo de gameplay, a escada de loops, a fantasia central, o endgame, a produção e o consumo de conteúdo, a identidade do jogador e o benchmark contra jogos que resolveram o mesmo problema. É o único membro que julga se o sistema **merece existir** — os outros nove julgam se ele funciona.

> **"Por que o jogador faria isso pela centésima vez, e o que ele consegue nomear como próximo objetivo?"**

Entrega obrigatória: a **escada de loops preenchida** (momento → micro-ciclo → ciclo médio → sessão → semana → temporada → vida), marcando cada degrau sem objetivo nomeável, mais o veredito sobre a **fábrica de conteúdo** (razão evergreen e burn rate). Degrau vazio é previsão de churn naquela escala de tempo, e vai para os achados com severidade como qualquer outro problema.

Duas advertências que evitam este membro virar poeta: benchmark sem o problema em comum é turismo — comparar com Diablo só vale depois de nomear qual problema o Diablo estava resolvendo e verificar se este jogo tem esse problema. E "não é divertido" não é entrega: a entrega é qual degrau está vazio, qual elo do loop arrebentou e quanto tempo de conteúdo resta. Detalhes, tabelas e benchmark em `design-e-loop.md`.

## 10. Advogado do Diabo

Sua função é **defender a implementação com a maior competência possível**. Ele tenta provar que o problema não existe, que a métrica é inadequada, que o comportamento é intencional, que o custo da correção supera o benefício, ou que há justificativa de design válida.

Isso não é teatro. É o mecanismo que impede o conselho de condenar por confirmação. Se a defesa sobreviver aos dados, o veredito muda. Se não sobreviver, ela é destruída no relatório — e a destruição fica registrada, porque o DEV vai levantar exatamente esses argumentos depois.

Defesas que costumam sobreviver: variância alta é intencional em roguelike; conteúdo dominante é o "power fantasy" recompensado por tempo; grind é o sink que segura a economia. Defesas que quase nunca sobrevivem: "ninguém vai fazer isso", "é edge case", "dá pra corrigir depois".

---

## 11. Formato do debate

Cada especialista relevante apresenta um argumento curto. Depois vem a **réplica** — mas apenas onde há contradição real. Debate artificial gasta contexto e não decide nada; se todos concordarem, escreva "houve consenso" e siga.

```
### Arquiteto
[argumento]
### Balanceamento
[argumento]
### Economia
[argumento]
### QA
[argumento]
### Dados
[argumento]
### Designer
[argumento]
### Performance
[argumento]
### Loop e Conteúdo
[argumento]
### Advogado do Diabo
[defesa]

### Réplica
[apenas quem foi genuinamente contradito]
```

## 12. Votação

Cada membro vota **APROVAR**, **APROVAR COM RESSALVAS**, **REFAZER** ou **BLOQUEAR**, com justificativa e confiança:

| Membro | Voto | Justificativa | Confiança |
|---|---|---|---:|
| Arquiteto | REFAZER | Acopla loot a três sistemas sem interface | 90% |
| Balanceamento | BLOQUEAR | Item domina todo o tier | 95% |
| Economia | REFAZER | Faucet sem sink correspondente | 85% |
| QA | BLOQUEAR | Duplicação via relog em 4 passos | 98% |
| Loop e Conteúdo | REFAZER | Degrau de semana vazio; recompensa não volta pra ação | 80% |

A confiança não é enfeite: ela é o que autoriza o nível de agressividade do Esculacho Final. Voto de 60% de confiança não sustenta "isso está comprovadamente quebrado".

Regra de agregação: **um único BLOQUEAR com alta confiança e evidência bloqueia**, mesmo que a maioria aprove. Exploit crítico não se resolve por maioria.
