# Instrumentação — como parar de balancear no escuro

Esta skill diz "meça X" o tempo inteiro. Esta referência é a contraparte: **como medir**, com o mínimo de trabalho possível.

O objetivo aqui não é montar uma stack de analytics. É fazer com que a próxima auditoria consiga escrever FATO onde hoje escreve HIPÓTESE. Para isso não é preciso data warehouse — é preciso uma tabela de eventos e cinco queries.

> **A regra que economiza mais tempo:** instrumente *antes* de precisar. Quando a pergunta aparece, o dado que responderia teria que ter sido coletado nas semanas anteriores. Não existe medir o passado.

## Índice

1. A tabela mínima
2. Os eventos que respondem quase tudo
3. Da pergunta ao evento
4. Coorte, sempre
5. Quanta amostra basta
6. O que não instrumentar
7. Quando não há telemetria nenhuma

---

## 1. A tabela mínima

Uma tabela. Não seis, não um pipeline, não um dashboard. Uma:

```
eventos(
  ts            timestamp,
  jogador_id    id,
  evento        texto,      -- 'gold_ganho', 'morreu', 'item_dropou', 'level_up'
  quantidade    numero,     -- quanto, quando faz sentido
  contexto      texto/json  -- onde, de quê, qual sistema, qual item
)
```

Três colunas fazem o trabalho pesado e são as que mais faltam quando alguém improvisa:

- **`contexto`** — sem ele você sabe que 40M de gold entraram e não sabe de onde. Um evento de economia sem a fonte é um número sem endereço: prova que existe problema e não diz onde.
- **`ts` com data de criação da conta acessível** — sem isso não existe análise por coorte, e sem coorte quase toda métrica mente (seção 4).
- **`quantidade` assinada** — ganho positivo, gasto negativo, mesma tabela. Faucet e sink saem da mesma query, e a soma é o net flow.

Se o jogo já tem log de servidor, muitas vezes dá para extrair isso sem escrever código novo. Vale checar antes de construir qualquer coisa.

## 2. Os eventos que respondem quase tudo

Ordenados por retorno. Os quatro primeiros cobrem a maioria das auditorias:

| Evento | Contexto que precisa junto | O que passa a ser mensurável |
|---|---|---|
| `recurso_ganho` / `recurso_gasto` | fonte ou destino, tipo de recurso | Net flow, faucets, sinks, inflação, custo de oportunidade, redundância de fontes |
| `sessao_inicio` / `sessao_fim` | duração, nível, o que fez | Retenção, duração de sessão, densidade de recompensa, T_loop |
| `progresso` (level up, milestone, quest) | tempo desde o anterior | Curva de progressão, walls, tempo por nível, onde o jogador para |
| `atividade_concluida` | qual, duração, resultado, recompensa | EV/h por atividade, dominância, conteúdo morto |
| `morte` / `falha` | causa, local, nível, perda | Dificuldade, wall, sink por penalidade, frustração |
| `item_obtido` / `item_usado` / `item_equipado` | id, fonte | Taxa de uso, conteúdo morto, discrepância entre poder real e percebido |
| `trade` / `mercado` | quem, o quê, preço | Preço real, arbitragem, multi-conta, bots |
| `compra_loja` | item, preço, moeda real | Funil, power gap, conversão |

Uma armadilha específica: **`item_obtido` sem `item_usado` é meio dado**. A pergunta de balanceamento quase nunca é "quantos dropou", é "quantos foram usados". Item que droga e apodrece no depósito conta como conteúdo morto, e só o par de eventos mostra isso.

## 3. Da pergunta ao evento

Vá da pergunta para o instrumento, nunca o contrário — instrumentar "tudo por via das dúvidas" gera volume que ninguém consulta:

| Pergunta da auditoria | Evento mínimo que responde |
|---|---|
| A economia infla? | `recurso_ganho`/`recurso_gasto` com fonte e destino, agregados por semana |
| Qual atividade domina? | `atividade_concluida` com duração e recompensa |
| Onde o jogador desiste? | `progresso` + último `sessao_fim` por jogador |
| Este item é forte ou só parece? | `item_equipado` cruzado com resultado de `atividade_concluida` |
| Este conteúdo está morto? | `atividade_concluida` por jogador ativo, últimos 30 dias |
| A fonte nova matou a antiga? | `recurso_ganho` por fonte, antes × depois do patch |
| O drop rate é o que o código diz? | contagem de `item_obtido` ÷ contagem de kills do mob |
| O jogador sabe o que está perseguindo? | **nenhum** — isto se pergunta a ele (seção 7) |

Essa última linha não é piada. Algumas das métricas mais importantes de design não são telemetria, e insistir em extraí-las de logs é como procurar chave debaixo do poste.

## 4. Coorte, sempre

A métrica agregada mente por construção quando a base cresce ou envelhece. Três exemplos que aparecem em todo projeto:

- **Gold médio por jogador caiu** — pode ser deflação, ou pode ser que entraram 300 jogadores novos com zero gold. Números opostos, mesma leitura.
- **Retenção D7 melhorou** — ou o jogo melhorou, ou a campanha de aquisição trouxe gente mais qualificada. Não dá para saber sem separar por origem e data de entrada.
- **Tempo médio por nível subiu** — ou virou wall, ou os veteranos estão em níveis mais altos e puxaram a média.

Portanto: **toda métrica sai por coorte de entrada** (semana em que o jogador criou a conta) e, quando o assunto é economia ou poder, **também por percentil** (p50, p90, p99). O p50 conta como está o jogo; o p90 conta o que vai quebrar; o p99 conta quem já quebrou.

## 5. Quanta amostra basta

Não precisa de estatística formal para não fazer besteira. Duas regras de bolso resolvem a maioria dos casos:

**Para taxas e proporções** (drop rate, % que usa um item, % que morre num boss), a margem de erro aproximada é:

```
margem ≈ 1 / raiz(n)
```

- n = 100 → ~10% de margem. Serve para ver se algo é 5% ou 50%. Não serve para decidir tuning fino.
- n = 400 → ~5%. Suficiente para a maioria das decisões de balanceamento.
- n = 2.500 → ~2%. Só vale a pena quando a decisão realmente depende dessa precisão.

**Para diferenças entre dois grupos** (a rota A rende mais que a B?), a pergunta útil é: a diferença observada é maior que a soma das duas margens? Se não for, você não mediu diferença, mediu ruído — e o relatório precisa dizer isso em vez de escolher um vencedor.

**Para eventos raros** (drop de 0,1%), a amostra necessária explode: para ver ~10 ocorrências você precisa de ~10.000 tentativas. Nesses casos, meça o **processo** (a tabela de loot no código, via leitura e teste unitário) em vez do **resultado** — é mais barato e mais confiável.

E o caso mais comum de todos: **quando a amostra não dá, diga que não dá.** "n = 12, insuficiente para concluir" é entregável. Concluir com n = 12 é inventar com aparência de rigor.

## 6. O que não instrumentar

Volume tem custo — em banco, em tick de servidor e em atenção. Evite:

- **Evento por frame ou por tick.** Amostre (1 a cada N) ou agregue no cliente antes de mandar.
- **Dado pessoal que a auditoria não usa.** Você precisa de `jogador_id`, não de nome, e-mail ou IP. Pseudônimo resolve tudo que a auditoria pede e evita virar um problema de outra natureza.
- **Métrica sem dono.** Se ninguém consegue dizer qual decisão aquele número mudaria, ele é ruído com custo de armazenamento. A pergunta antes de instrumentar qualquer coisa é: *"que decisão eu tomo diferente dependendo desse valor?"*

Ver `performance.md` antes de instrumentar qualquer coisa em loop quente: telemetria mal colocada já derrubou mais servidor que a mecânica que ela media.

## 7. Quando não há telemetria nenhuma

Situação normal em projeto pequeno, e não é desculpa para auditoria vazia. Existem quatro fontes de evidência baratas, em ordem crescente de esforço:

1. **Ler o código e a config.** Drop rate, fórmula, custo e cooldown são FATO sem precisar de telemetria — estão escritos. Boa parte das auditorias se resolve aqui.
2. **Perguntar aos jogadores.** Vinte respostas no Discord respondem coisas que log nenhum responde: *"o que você está tentando conseguir agora?"*, *"o que te fez parar de jogar na semana passada?"*, *"por que você não usa X?"*. Vinte é amostra ruim para percentual e amostra excelente para descobrir que existe um problema.
3. **Observar uma sessão.** Assistir três jogadores novos jogando por vinte minutos, calado, revela mais problema de legibilidade que um mês de métricas. Ver `legibilidade.md`.
4. **Simular em planilha.** Sem jogador, com os números do código. É o que o modo pré-mortem faz, e responde "o que acontece em 90 dias" antes de existirem 90 dias.

O que **não** vale é a quinta opção, que é a mais usada: decidir pela impressão de quem estava online ontem à noite.

---

**Fechando o ciclo:** toda auditoria que termina em "não temos dados" deve terminar também com o evento a instrumentar, a pergunta que ele responde e a amostra necessária. Assim a auditoria seguinte tem FATO onde esta teve HIPÓTESE — que é a única forma de o projeto ficar mais fácil de auditar com o tempo em vez de mais difícil.
