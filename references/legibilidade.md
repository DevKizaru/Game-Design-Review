# Legibilidade — o sistema que o jogador consegue ler

Um sistema perfeitamente balanceado que o jogador não entende falha exatamente como um sistema desbalanceado. A diferença é que o desbalanceado aparece na planilha e o ilegível não — ele aparece como "esse item é lixo" no chat sobre um item que a matemática diz ser o melhor do tier.

Esta referência é o material de apoio do **Designer de Experiência**, e a pergunta que a governa é:

> **O jogador consegue prever o resultado da escolha dele antes de fazê-la, e entender o que aconteceu depois?**

Repare que não é *"o jogador sabe jogar?"*. Legibilidade não é tutorial, não é dificuldade e não é dar tudo mastigado — jogo pode ter segredo, descoberta e profundidade. O que não pode é a informação necessária para uma decisão **não existir em lugar nenhum** no momento em que a decisão é tomada.

## Índice

1. As quatro perguntas
2. Poder real × poder percebido — a métrica que salva de nerf errado
3. Sinais de ilegibilidade
4. Feedback: imediato, diferido e ausente
5. O que esconder e o que mostrar
6. Métricas de legibilidade
7. Como auditar sem telemetria

---

## 1. As quatro perguntas

Todo sistema tem que responder estas quatro para o jogador. Falha em qualquer uma é achado, com severidade como qualquer outro:

1. **O que aconteceu?** — o resultado é visível? Tomou 400 de dano ou "morreu do nada"?
2. **Por quê?** — a causa é atribuível? Ele entende que morreu porque a resistência dele era baixa, ou acha que o jogo é injusto?
3. **O que eu deveria fazer diferente?** — existe ação corretiva descobrível? Se a resposta honesta é "ler a wiki", o sistema está terceirizando design para a comunidade.
4. **O que muda se eu escolher X em vez de Y?** — a comparação é possível *antes* de investir? Se o jogador só descobre depois de gastar o recurso, não houve escolha, houve aposta.

A pergunta 4 é a que mais falha em RPG e MMO, e é a mais cara: sistemas de build, craft e upgrade que só revelam o resultado depois do investimento irreversível transformam progressão em roleta e geram o pedido de respec que vira o próximo problema de design.

## 2. Poder real × poder percebido — a métrica que salva de nerf errado

Este é o instrumento mais valioso desta referência, e o mais ignorado.

Cruze **força medida** (DPS, EV/h, taxa de vitória) com **taxa de uso real**. Quatro quadrantes, quatro diagnósticos completamente diferentes:

| | Muito usado | Pouco usado |
|---|---|---|
| **Forte** | Dominância. Problema de balanceamento — nerf é a resposta certa. | **Problema de legibilidade.** O item é bom e ninguém percebe. Nerfar aqui é erro grosseiro. |
| **Fraco** | **Problema de legibilidade.** Parece bom, não é — armadilha para novato. Buff ou clareza. | Conteúdo morto. Ou some, ou dá um propósito. |

Os dois quadrantes de legibilidade são onde nascem os piores patches da indústria: **nerfar algo forte que ninguém usa** (o item some de vez e o problema real nem foi tocado) e **buffar algo fraco que todo mundo usa** (a armadilha fica pior). Antes de mexer em qualquer número, olhe a taxa de uso. Se força e uso não conversam, o problema não é o número.

Frase que resume: *"quando a força e o uso divergem, o bug está na informação, não no valor."*

## 3. Sinais de ilegibilidade

Nenhum deles precisa de telemetria para ser notado, e todos são evidência forte:

- **A comunidade escreveu uma planilha para jogar.** Calculadora de dano, simulador de build, tabela de spots. Isso é elogio à profundidade *e* atestado de que o jogo não mostra o que precisa mostrar. A planilha é a UI que faltou.
- **A pergunta mais repetida no chat é sobre uma mecânica que existe há meses.** Se a resposta está na wiki e ninguém acha, a wiki não é documentação, é curativo.
- **Jogador pede buff do que já é forte** (ver seção 2).
- **Ninguém sabe explicar por que perdeu.** Em PvP, "esse cara é hacker" costuma significar "não consigo ver o que me matou".
- **O tutorial precisa explicar algo que o jogo poderia mostrar.** Texto explicando o que uma barra significaria se fosse desenhada direito é dívida de design paga com paciência do jogador.
- **Existe uma "build óbvia" que só quem lê fórum conhece.** A informação existe, mas fora do jogo — o que separa jogadores por acesso à comunidade, não por habilidade.

## 4. Feedback: imediato, diferido e ausente

Toda ação precisa de retorno, e o prazo do retorno define o que ele precisa entregar:

- **Imediato (< 1 s)** — som, número, animação, tremor. É o que faz a ação *ser gostosa* (ver `design-e-loop.md`, seção 2). Sua ausência não confunde: entedia.
- **Diferido (minutos a sessões)** — progresso, curva, comparação com antes. Precisa ser **acumulável e visível**: barra, contador, histórico. Sem isso o jogador não percebe que progrediu, e progresso não percebido tem valor zero.
- **Ausente** — o jogador investe e nunca descobre se valeu. É o pior dos três e o mais comum em sistemas de longo prazo: upgrades de porcentagem pequena, buffs passivos, stats escondidos. Se você não consegue mostrar o efeito, questione se o efeito deveria existir.

Regra prática: **efeito que não dá para mostrar é efeito que não dá para valorizar.** Um bônus de +2% invisível custa o mesmo tempo de desenvolvimento que um +10% visível e entrega uma fração do valor percebido — e valor percebido é o que decide se o jogador continua investindo.

## 5. O que esconder e o que mostrar

Nem tudo deve ser exposto. A régua:

**Mostre** — o que é necessário para decidir agora: custo, efeito comparável, requisito, consequência de falhar, o que a escolha impede depois. E **sempre** mostre o que é irreversível como irreversível, antes de confirmar.

**Pode esconder** — o que é conteúdo em si: localização de segredo, próximo passo de uma quest de investigação, identidade de um boss, drop raro cuja graça é a surpresa. Aqui o desconhecido é o produto.

**Nunca esconda** — a regra que o jogador precisa saber para não ser punido. Dano que não se anuncia, penalidade não avisada, requisito descoberto após o gasto. Isso não é dificuldade, é emboscada, e é a diferença entre "morri porque errei" e "morri porque o jogo não me contou".

O teste que separa os três: *o jogador teria decidido diferente se soubesse?* Se sim e você escondeu, você não criou desafio — criou uma pegadinha que ele só vence na segunda vez, depois de perder algo.

## 6. Métricas de legibilidade

Sim, isso se mede:

| Métrica | Definição | Sinal de alerta |
|---|---|---|
| **Divergência força × uso** | Correlação entre poder medido e taxa de uso | Correlação baixa ou negativa |
| **Tempo até entender** | Minutos até o jogador usar a mecânica corretamente | Muito acima do previsto, ou nunca |
| **Taxa de arrependimento** | % que pede reset/respec/refund após uma escolha | Alta = a escolha não era legível antes |
| **Dependência de fonte externa** | % que consulta wiki/fórum para jogar | Alta = a UI terceirizou informação |
| **Atribuição de causa** | % que explica corretamente por que perdeu/falhou | < 50% num sistema central |
| **Uso da opção ótima** | % dos jogadores informados usando a melhor build | Muito baixo = ninguém descobriu |

A primeira é a mais barata e a que mais evita estrago: ela só precisa de dois números que o jogo provavelmente já tem.

## 7. Como auditar sem telemetria

Três instrumentos, todos baratos, em ordem de retorno:

1. **Assista três jogadores novos por vinte minutos, calado.** Não explique nada, não responda perguntas, anote toda vez que a pessoa hesita, abre o menu errado ou pergunta algo em voz alta. É o método mais barato e mais brutal de auditoria de legibilidade que existe, e ele funciona com n = 3 porque você não está medindo percentual, está encontrando defeito.
2. **Peça para alguém explicar o sistema de volta.** Se um jogador com 50 horas não consegue descrever como o cálculo funciona em três frases, o sistema não é profundo, é opaco.
3. **Leia as perguntas repetidas.** Discord e chat são log de legibilidade gratuito. A pergunta que aparece toda semana é um item de UI que faltou, e ela já vem com a frequência embutida.

E o de sempre: se o achado for de legibilidade, a correção mais barata quase nunca é mexer no balanceamento. É mostrar um número que já existe.
