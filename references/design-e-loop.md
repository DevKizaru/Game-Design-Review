# Design, loop e conteúdo — a auditoria que vem antes dos números

Balanceamento conserta um sistema ruim. Nenhuma planilha conserta um jogo que ninguém quer repetir.

Esta referência é a lente que falta quando o pedido não é *"esse drop rate está certo?"* e sim *"esse jogo funciona?"*. Ela responde três perguntas que a matemática sozinha não alcança:

> **O jogador quer repetir isso? Ele sabe o que está perseguindo agora? E vocês conseguem produzir conteúdo mais rápido do que ele consome?**

O rigor é o mesmo do resto da skill: **cada afirmação de design também sai com etiqueta e com número**. "O loop está chato" é OPINIÃO. "O loop fecha em 14 minutos, entrega 1 recompensa a cada 9 min e o jogador não consegue nomear o objetivo da semana" é MÉTRICA — e é isso que faz o DEV mexer no jogo em vez de discutir gosto.

## Índice

1. A escada de loops
2. Anatomia de um loop que fecha
3. Benchmark — o que cada escola resolveu
4. A fábrica de conteúdo
5. Fantasia, identidade e por que o jogador fica
6. Métricas de design (as que dão para medir)
7. Armadilhas de loop e conteúdo
8. Formato do relatório: VISÃO DE DESIGN
9. O teste de 5 perguntas

---

## 1. A escada de loops

Nenhum jogo grande tem *um* loop. Tem uma escada de loops encaixados, cada degrau ~5 a 30× mais longo que o de baixo, e **cada degrau precisa ter um objetivo que o jogador consiga nomear em voz alta**.

| Degrau | Duração típica | Diablo (ARPG) | Elden Ring (Souls) | Path of Exile | Escola OT (PxG / Poke Alliance / GLA) | Idle / incremental |
|---|---|---|---|---|---|---|
| **Momento** | 1–3 s | hit / dodge | trocar golpe, rolar | hit + trigger | hit no mob | tick de ganho |
| **Micro-ciclo** | 20–90 s | pack de elite | mini-boss, grupo | pack raro / breach | respawn do spot | encher a barra |
| **Ciclo médio** | 3–15 min | rift / dungeon | chegar na graça, abrir atalho | 1 mapa | limpar a hunt, voltar pra refill | comprar o upgrade |
| **Sessão** | 20–90 min | 5–10 rifts | 1 área ou 1 boss vencido | 8–15 mapas | 1–2 h de hunt + resupply + venda | subir 1 tier |
| **Semana** | — | boss semanal / cap | (não existe — e tudo bem) | progresso de atlas, boss de endgame | boss de respawn semanal, task, guild war | evento / desafio semanal |
| **Temporada** | 8–16 semanas | season + reset | NG+ | liga: 1 mecânica nova + reset | evento sazonal + cosmético exclusivo | prestígio / camada nova |
| **Vida** | meses/anos | build completo, ladder | platina, PvP, builds | build dos sonhos | level cap, highscore, guild dominante | número que estoura a tela |

**Como usar isto numa auditoria:** preencha a coluna do jogo auditado. Cada linha vazia é uma previsão de churn *naquela escala de tempo*.

- Sem degrau de **micro-ciclo**: o jogo é entediante em 5 minutos.
- Sem degrau de **sessão**: o jogador desliga sem nada para mostrar, e não volta amanhã.
- Sem degrau de **semana**: retenção D7 despenca; não existe motivo para abrir o jogo na terça.
- Sem degrau de **temporada**: o jogo tem fim silencioso — o veterano some e não há evento que o traga de volta.
- Sem degrau de **vida**: não existe veterano; ninguém tem o que exibir para o novato.

Também confira a **razão entre degraus**. Salto de 60 s direto para 6 horas é um buraco: o jogador percebe que "nada acontece" no meio. Razão saudável fica entre 5× e 30×.

## 2. Anatomia de um loop que fecha

Um loop só existe quando a recompensa **volta para dentro da ação**:

```
AÇÃO → RECOMPENSA → INVESTIMENTO → NOVA CAPACIDADE → AÇÃO melhor/mais rápida/mais ampla
```

Se a recompensa não muda a ação seguinte, não é loop, é uma fila. Quatro perguntas de corte:

1. **A ação é gostosa na primeira vez?** Se o núcleo (bater, andar, clicar, montar deck) já é ruim sozinho, nenhuma recompensa salva — só adia a desistência.
2. **A recompensa chega antes de a atenção acabar?** Recompensa de 40 minutos precisa de recompensas menores no meio, senão o jogador não descobre que ela existe.
3. **O investimento é uma escolha?** Recurso que só tem um destino não é investimento, é imposto. O momento "no que eu gasto isso?" é onde nasce build, identidade e conversa entre jogadores.
4. **A nova capacidade muda o que ele faz, ou só o número?** +8% de dano não é capacidade nova. Matar um pack inteiro de uma vez, alcançar um lugar antes inacessível ou abrir uma rota nova é.

**Teste da 100ª repetição.** Rode o loop mentalmente na centésima vez. O que sobrou? Se sobrou só o número subindo, o loop tem prazo de validade e você já sabe a data. O que segura a centésima repetição, nos jogos que duram, é sempre uma destas quatro coisas: **variação** (o pack é diferente), **aposta** (pode dropar *aquilo*), **domínio** (posso fazer melhor que ontem) ou **testemunha** (alguém vê o que eu conquistei).

## 3. Benchmark — o que cada escola resolveu

Não copie a estética, copie a **solução estrutural**. Cada um destes jogos resolveu um problema específico, e a solução é transferível.

### Diablo — a recompensa que faz quatro trabalhos

O loot é, ao mesmo tempo, recompensa, progressão, economia e definição de build. Um sistema só sustentando quatro pilares é a maior alavanca de conteúdo do gênero. Some a isso a **densidade**: o prazer não é matar um monstro, é a tela inteira explodir. E as **temporadas resetam tudo**, o que resolve inflação sem nenhum sink: a economia não é balanceada, é deletada de tempos em tempos.

**Transferível:** uma moeda de recompensa que alimenta poder + identidade + economia ao mesmo tempo · afixos combinatórios como multiplicador de conteúdo (o conteúdo novo vem da combinação, não de arte nova) · reset periódico como sink definitivo.

### Path of Exile — profundidade como produto e moeda que é insumo

A moeda **é** material de craft. Toda transação compete com um sink embutido — a economia se autorregula porque gastar é a mesma coisa que jogar. O endgame (atlas) é **configurado pelo jogador**: ele escolhe qual conteúdo quer ver mais, o que transforma o mesmo mapa em conteúdo diferente por pessoa. E cada liga entrega **uma mecânica nova + reset**; a mecânica que dá certo é absorvida pelo jogo base, então a biblioteca de conteúdo cresce para sempre sem o time refazer nada.

**Transferível:** moeda que é insumo (sink dentro da própria moeda) · endgame configurável pelo jogador · temporada = 1 mecânica nova + reset, com absorção do que sobrevive · conhecimento do sistema como forma legítima de progressão.

### Elden Ring — a curiosidade como recompensa e a válvula lateral

Não há esteira. A progressão real é **conhecimento e domínio do jogador**; o número sobe pouco. A recompensa por explorar é descobrir — e por isso o mapa é conteúdo, não cenário. A sacada estrutural mais roubável é a **válvula lateral**: travou no boss? Vá para outro lugar, volte mais forte. Isso mata a wall — a causa nº 1 de churn — sem baixar a dificuldade nem um ponto. E a morte custa (runas caídas), mas é **recuperável**: tensão sem desespero.

**Transferível:** sempre haver outra coisa a fazer quando o jogador trava · custo de morte recuperável em vez de punitivo · descoberta como recompensa (barata de produzir, cara de esquecer) · assumir que o jogo é finito em vez de fingir infinito com números maiores.

### Escola OT brasileira — PokeXGames, Poke Alliance, Grand Line Adventures

É a escola mais relevante para MMO e idle de nicho, e a mais mal copiada: quem copia pega o grind e esquece o que fazia o grind funcionar.

- **Identidade antes de mecânica.** O jogador não entra para "otimizar EV/h", entra para *ser* treinador, pirata, ninja. A fantasia licenciada entrega peso emocional de graça — um nome canônico já vem com significado que o time não precisou escrever.
- **Escolha inicial que marca a vida inteira.** Vocação, starter ou fruta define build, rota de hunt e — o mais importante — **dependência de outros jogadores**. Quem escolheu diferente de você vira alguém de quem você precisa.
- **Conteúdo = spot com EV conhecida.** Cada tier de nível ganha uma hunt com xp/h e gold/h próprios. É a fábrica de conteúdo mais barata que existe: um mapa novo mais uma tabela de loot viram semanas de jogo. E os jogadores *documentam os spots por você* — a wiki da comunidade é conteúdo de graça.
- **Portões como conteúdo.** Quest chain e task liberam o próximo tier. O portão é o objetivo nomeável da semana.
- **Escassez agendada.** Boss com respawn semanal cria evento social, competição de guild e motivo para logar num horário específico.
- **Grind com testemunha.** Highscore público, level visível, party obrigatória, chat global. Quatrocentas horas de clique sobrevivem porque **alguém vê**. Grind sozinho é emprego; grind assistido é status.
- **A morte é o sink.** Perder XP ou itens destrói recurso e dá tensão à hunt de rotina — dois problemas resolvidos com uma mecânica.
- **A loja vende tempo, conveniência, vaidade e acesso** (premium), não poder bruto direto — o suficiente para pagar o servidor sem transformar o highscore em extrato bancário.

**Transferível:** identidade e fantasia como retenção primária · escolha inicial que cria interdependência · spot com EV conhecida como unidade de conteúdo · respawn agendado como evento social · visibilidade pública do progresso · penalidade de morte fazendo o papel de sink.

### Como usar o benchmark sem virar macaco de imitação

Ao comparar, nomeie **o problema que o jogo de referência estava resolvendo** e verifique se o jogo auditado tem esse problema. Copiar liga de PoE para um jogo sem economia de trade é copiar o remédio errado. A frase que fecha uma comparação honesta é:

> *"X resolve [problema] com [mecanismo]. Este jogo tem [problema]? Se sim, o mecanismo cabe? Se não, por que estamos copiando?"*

## 4. A fábrica de conteúdo

A pergunta que quebra a maioria dos planos de conteúdo é aritmética, não criativa:

> **Quantas horas de conteúdo o seu jogador consome por semana, e quantas horas o seu time produz por mês?**

Um jogador dedicado consome 15–40 h/semana. Um time pequeno produz talvez 4–10 h de conteúdo perecível por mês. A conta não fecha — **nunca** fechou para ninguém. Todo jogo que dura resolveu isso da mesma forma: parou de tentar ganhar essa corrida no braço.

**Perecível** — consumido uma vez: quest de história, cutscene, dungeon autoral, boss de campanha, puzzle. Alto custo por hora de jogo, alto impacto emocional, valor quase zero na segunda vez.

**Evergreen** — regenera sozinho: sistemas, spots repetíveis, itemização, PvP, economia entre jogadores, geração procedural, tiers de dificuldade, social/guild, highscore, prestígio/reset.

A regra que sustenta um jogo de serviço:

> **Perecível é tempero e gatilho de retorno. Evergreen é a comida.**

**Multiplicadores de conteúdo** — onde investir tempo de dev para render mais horas de jogo por hora trabalhada, em ordem decrescente de alavancagem:

| Multiplicador | Por que rende | Custo |
|---|---|---|
| Itemização combinatória (afixos, mods) | Cada item novo interage com todos os antigos | Médio, e cai com o tempo |
| Economia entre jogadores | Os jogadores geram objetivos uns para os outros | Alto para acertar, quase zero para manter |
| PvP / competição | Oponente humano é conteúdo infinito e grátis | Alto em balanceamento |
| Tiers de dificuldade sobre conteúdo existente | Reaproveita 100% da arte | Baixo |
| Spot/zona nova com EV própria | Unidade de conteúdo mais barata do MMO | Baixo |
| Geração procedural | Variação sem arte nova | Alto no início |
| Reset / prestígio / temporada | Reaproveita o jogo inteiro e ainda faz papel de sink | Baixo |
| Social, guild, highscore | Transforma progresso em status | Baixo |
| Dungeon autoral / quest de história | — | **Altíssimo por hora de jogo** |

Quando o plano de conteúdo do DEV é uma fila de conteúdo autoral, o achado tem nome e número: **esteira de conteúdo**, com a data em que ele fica para trás. Calcule (`scripts/auditoria_calc.py conteudo`) e apresente a data.

## 5. Fantasia, identidade e por que o jogador fica

Loop explica por que ele joga hoje. Fantasia explica por que ele instalou. Identidade explica por que ele volta no mês que vem.

- **Fantasia central** — a frase que o jogador usaria para contar o jogo a um amigo. Se ela não existe, o marketing vai inventar uma que o jogo não entrega — e a nota 1 na loja nasce dessa diferença. Meça **TTFF (time to first fantasy)**: em quantos minutos ele faz a coisa que o trailer prometeu? Acima de ~15 min, ele desiste antes de descobrir.
- **Identidade** — "eu sou o cara do X". Nasce de escolha com consequência (vocação, classe, build, guild) e morre quando tudo é reversível de graça. Respec grátis e ilimitado é conveniência que apaga identidade; respec caro demais congela o jogador num erro. As duas pontas são achados.
- **Testemunha** — highscore, ranking, item visível, título, montaria. Progresso que ninguém vê vale metade.
- **O próximo objetivo** — o jogador saudável responde *"o que você está fazendo agora?"* em uma frase. Quando a resposta é "sei lá, jogando", ele está a poucos dias de parar. É a pergunta de retenção mais barata que existe e quase ninguém coleta.
- **Domínio** — o jogador precisa poder ficar melhor, não só mais forte. Jogo em que habilidade não importa perde exatamente os jogadores que fariam guia, vídeo e comunidade.
- **Pertencimento** — guild, party obrigatória, dependência entre vocações, mercado. O maior custo de saída de um MMO nunca foi o personagem; foram as pessoas.

E a honestidade que a skill exige: **jogos também dão certo por distribuição, comunidade, IP e sorte de momento**. Se o DEV está copiando o loop do PoE achando que o mecanismo sozinho explica o sucesso, isso é HIPÓTESE — e o número que falta é quanto do resultado da referência veio de estrutura e quanto veio de alcance.

## 6. Métricas de design (as que dão para medir)

Design não é o setor onde as métricas acabam. Todas estas são coletáveis:

| Métrica | Definição | Sinal de alerta |
|---|---|---|
| **T_loop por degrau** | Tempo entre início da ação e recompensa, em cada degrau | Buraco > 30× entre degraus vizinhos |
| **Cobertura da escada** | Degraus com objetivo nomeável ÷ 7 | Qualquer degrau vazio |
| **Densidade de recompensa** | Recompensas relevantes por minuto de sessão | < 1 a cada 10 min no early game |
| **Decisões por minuto** | Escolhas com consequência (input não conta) | ≈ 0 → é trabalho, não jogo |
| **TTFF** | Minutos até executar a fantasia central | > 15 min |
| **TTFC** | Minutos até a primeira escolha que marca o personagem | > 60 min, ou nunca |
| **Razão evergreen** | Horas evergreen ÷ horas totais de conteúdo | < 0,5 num jogo de serviço |
| **Burn rate de conteúdo** | Consumo semanal do p90 ÷ produção semanal do time | > 1 → existe data de esgotamento |
| **Meia-vida do conteúdo** | Dias até 50% dos ativos pararem de usar aquele conteúdo | Curta demais = perecível caro |
| **R_max (repetição até o tédio)** | Repetições até a frequência por sessão cair pela metade | Menor que o número exigido para progredir |
| **Taxa de resposta do "o que você está fazendo?"** | % de jogadores que nomeiam um objetivo atual | < 70% |

Ferramentas prontas, para não fazer conta no olho:

```bash
python "<dir-desta-skill>/scripts/auditoria_calc.py" loop --help
python "<dir-desta-skill>/scripts/auditoria_calc.py" conteudo --help
```

`loop` mede a escada (degraus sem objetivo, buracos entre degraus, densidade de recompensa). `conteudo` mede a fábrica (razão evergreen, burn rate, semanas até secar).

Quando o dado não existir — e no começo quase nunca existe — vale a regra geral da skill: declare a lacuna e defina o experimento mínimo. Para design, o experimento mínimo costuma ser ridiculamente barato: **pergunte a 20 jogadores o que eles estão perseguindo agora e conte quantos sabem responder.**

## 7. Armadilhas de loop e conteúdo

Nomeie pelo nome — é o que faz o DEV entender em vez de se defender:

- **Loop aberto** — a recompensa não volta para a ação. O jogador acumula algo que não muda o que ele faz.
- **Degrau morto** — falta objetivo numa escala de tempo. O churn acontece exatamente nessa escala.
- **Esteira de conteúdo** — a retenção depende de conteúdo autoral produzido mais devagar do que é consumido. Tem data de vencimento; calcule-a.
- **Endgame que é o early game com números maiores** — nada novo acontece, só mais zeros. O veterano não tem o que contar para o novato.
- **Fantasia não entregue** — o jogo promete comandar uma tripulação e entrega clicar num javali 4.000 vezes. Compare a promessa do material de divulgação com a primeira hora real.
- **Objetivo invisível** — o jogador não sabe dizer o que persegue. Frequentemente o objetivo existe e só não está na tela; é o achado mais barato de corrigir do catálogo inteiro.
- **Grind sem testemunha** — esforço longo sem visibilidade social. Sustenta-se em jogo solo com narrativa; não se sustenta em MMO.
- **Escolha de identidade sem consequência** — classe, vocação ou build que se troca a qualquer momento de graça. Vira menu, não identidade.
- **Válvula ausente** — travou, acabou. Sem rota alternativa, a wall vira desinstalação.
- **Sazonal que é só FOMO** — evento cujo único apelo é a punição por não participar. Traz o jogador de volta uma vez e o ensina a ressentir o jogo.
- **Reset sem consentimento** — apagar progresso funciona quando é combinado, cíclico e recompensado (temporada, prestígio); é traição quando é surpresa.
- **Cópia de mecanismo sem o problema** — importar liga, pity, atlas ou wipe de um jogo que tinha um problema que este jogo não tem.
- **Sistema sem identidade** — mais de um sistema respondendo a mesma frase "isto serve para ___". Do lado do jogador o sintoma é ter que aprender três fluxos para obter uma coisa; do lado do time é balancear o mesmo recurso três vezes por patch. A conta que prova está em `modelagem.md`, seção 10.

## 8. Formato do relatório: VISÃO DE DESIGN

Quando o alvo é o jogo, a feature nova ou o plano de conteúdo — e não uma fórmula —, use esta estrutura no lugar do relatório de auditoria padrão. Ela existe para forçar a conversa a sair de "eu acho legal" e chegar em degrau, número e data:

```
# VISÃO DE DESIGN — [JOGO / FEATURE]

## 1. Fantasia central
Uma frase, do ponto de vista do jogador. TTFF medido ou estimado.

## 2. Escada de loops
A tabela preenchida (momento → vida), com T_loop e o objetivo nomeável
de cada degrau. Degraus vazios marcados como achado.

## 3. O loop fecha?
Ação → recompensa → investimento → nova capacidade: onde a corrente arrebenta.
Teste da 100ª repetição: o que sobra (variação, aposta, domínio, testemunha).

## 4. Mapa de conteúdo
Evergreen × perecível, com horas. Burn rate e data de esgotamento.
Multiplicadores de conteúdo disponíveis e não usados.

## 5. Benchmark
Contra 2 ou 3 referências pertinentes, no formato
"X resolve [problema] com [mecanismo] — cabe aqui porque / não cabe porque".
Sem turismo: só referências que compartilham o problema.

## 6. Retenção e identidade
O que o jogador exibe, de quem ele depende, e o que ele responde quando
perguntam o que está fazendo agora.

## 7. Achados
Mesmo formato do resto da skill: etiqueta, severidade, mecanismo,
blast radius, correção mais barata.

## 8. Plano de conteúdo recomendado
Ordenado por horas de jogo entregues ÷ custo de produção.

## 9. Testes de aceite
Com número. Ex.: "TTFF ≤ 8 min; ao menos 1 objetivo nomeável em cada um
dos 7 degraus; razão evergreen ≥ 0,6 antes do lançamento."

# ESCULACHO FINAL
```

Para um pedido pequeno ("essa feature nova faz sentido?"), colapse: fantasia, degrau que ela ocupa, se fecha o loop, o que custa de conteúdo, veredito. Encher linguiça com seções vazias é o oposto do que esta skill faz.

## 9. O teste de 5 perguntas

Quando não houver tempo, dado nem paciência para o processo completo, estas cinco perguntas separam um jogo com futuro de uma planilha animada. Toda resposta ruim é um achado com endereço:

1. **Por que o jogador aperta o botão a 100ª vez?** (variação, aposta, domínio ou testemunha — se não for nenhuma, é fila)
2. **O que ele está perseguindo agora, em uma frase?** (e o mesmo para esta semana e este mês)
3. **A recompensa muda a próxima ação, ou só o número?**
4. **Quando ele trava, o que ele faz em vez de desinstalar?**
5. **Quem vê o que ele conquistou?**
## Como um achado de design deve parecer

Mesmo formato dos achados de sistema (`SKILL.md`): etiqueta, número, mecanismo, blast radius e correção mais barata — nessa ordem, porque é a ordem em que o DEV consegue agir. A diferença está na unidade medida.

Achado de design segue exatamente o mesmo rigor — a diferença está na unidade medida, não no nível de exigência:

> **D1 — Não existe objetivo na escala de semana** · Severity **6.80 · PROBLEMA** · MÉTRICA
>
> A escada de loops tem degraus até sessão (hunt de 50 min, fecha com level e loot vendido) e volta a existir só no de vida (level 300, highscore). Entre 1 hora e 6 meses não há nada que o jogador consiga nomear. Em 18 respostas coletadas no Discord para "o que você está fazendo essa semana?", 4 nomearam um objetivo (22%, contra a marca saudável de 70%).
>
> **Mecanismo:** todo conteúdo repetível é contínuo — hunt, task infinita, mercado. Nenhum é agendado nem esgotável, então nada cria a pergunta "já fiz isso essa semana?".
>
> **Blast radius:** alto. Contamina Retenção (D7), Social (não há motivo de coordenar horário) e Economia (nenhuma escassez agendada segurando preço de boss loot).
>
> **Correção mais barata:** dar respawn semanal a três bosses que já existem e um contador visível de "task da semana". Zero arte nova, zero sistema novo — usa conteúdo já produzido e cria o degrau que falta.

