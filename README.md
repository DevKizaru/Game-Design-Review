# Game Design Review

**Uma skill de auditoria de sistemas de jogo para o [Claude Code](https://claude.com/claude-code).** Você apresenta um sistema — uma mecânica, um drop rate, uma curva de XP, uma economia, uma proposta de feature, um GDD inteiro — e recebe de volta uma análise com números, severidade pontuada, exploits testados, um veredito e um plano de correção priorizado por custo.

> *A quantitative game-system audit skill for Claude Code, written in Portuguese. It turns "is this balanced?" into expected value, time-to-kill, net flow, loop-ladder coverage, content burn rate and a scored severity — plus a verdict and the cheapest fix. See `SKILL.md`.*

O princípio que sustenta o resto: **crítica sem evidência não vale nada.** Quando o número não existe, a skill não chuta — ela diz qual número falta, qual é o experimento mínimo que o produz, e com quanta confiança está opinando enquanto isso.

---

## Instalação

```bash
git clone <este-repo> ~/.claude/skills/esculacho-de-dev-vagabundo
```

O nome da pasta precisa ser igual ao campo `name:` declarado no frontmatter do `SKILL.md`. Feito isso, a skill ativa sozinha quando o assunto for auditoria de sistema de jogo, ou sob demanda pelo nome.

Não há dependências: a calculadora é Python 3 puro, só biblioteca padrão.

---

## O que tem dentro

| Arquivo | O que faz |
|---|---|
| `SKILL.md` | O núcleo. Triagem do tamanho da resposta, processo de 7 passos, catálogo de armadilhas, fórmula de severidade, formato do relatório e registro de decisões |
| `references/modelagem.md` | As fórmulas por domínio: combate, economia, loot, progressão, gacha, retenção, power creep, **redundância (paralelo)**, **cadeia obrigatória (série)**, mapa de recursos e grafo de conversão |
| `references/design-e-loop.md` | A escada de loops, a anatomia do loop fechado, a fábrica de conteúdo, e o que Diablo, Path of Exile, Elden Ring e a escola OT brasileira resolveram — sempre como *problema resolvido → mecanismo transferível*, nunca como curiosidade |
| `references/conselho.md` | Os 10 especialistas que debatem o sistema, cada um com uma entrega obrigatória, mais um Advogado do Diabo encarregado de atacar o próprio relatório |
| `references/instrumentacao.md` | O que medir e como, para que "não temos dados" deixe de ser o fim da conversa |
| `references/legibilidade.md` | Poder real × taxa de uso. Um item forte que ninguém usa é falha de informação, e mexer no número ali costuma piorar |
| `references/mercado-e-monetizacao.md` | O mercado como instrumento de medição, formação de preço, liquidez, bot e RMT, loja de doação, a linha entre conveniência e vantagem, e o teto de poder pago |
| `references/patch.md` | Auditoria de mudança: o que estava calibrado contra o valor antigo, breakpoints atravessados, quem jogou sob a regra velha, e o relatório curto de patch |
| `references/desculpas.md` | O catálogo completo de respostas a desculpas, por domínio |
| `references/testes-e-exploits.md` | Perfis de jogador, casos-limite e a tentativa honesta de quebrar o sistema |
| `references/performance.md` | O custo de runtime que a planilha não mostra |
| `scripts/auditoria_calc.py` | A calculadora: 10 subcomandos, funções `calc_*` puras |
| `scripts/test_auditoria_calc.py` | 98 testes. A suíte existe porque uma versão anterior da ferramenta errou um EV por 121× |
| `exemplos/` | Uma auditoria de ponta a ponta, com os comandos da calculadora e as saídas reais — inclusive a seção do que a skill aprova |
| `evals/` | As definições dos evals e o benchmark contra o baseline sem skill, incluindo o que o baseline fez melhor |

---

## A calculadora

```bash
python scripts/auditoria_calc.py --help
```

| Subcomando | Responde |
|---|---|
| `severity` | Quão grave é o problema, numa escala que não aceita adjetivo |
| `ev` | Valor esperado, desvio, pior caso, tentativas até o drop, percentis por sessão |
| `netflow` | Faucet × sink e projeção de estoque em 1/7/30/90 dias |
| `ttk` | DPS efetivo, mitigação percentual e plana, breakpoints de hits |
| `gacha` | Pulls esperados, pity, chance acumulada, custo p90 e teto |
| `progressao` | Curva de XP, tempo por nível, walls e cauda até o cap |
| `fontes` | Redundância em **paralelo**: dominadas, fora da disputa, redundância prática — e o eixo de custo de atenção |
| `cadeia` | Gargalo em **série**: vazão, qual elo é o gargalo, P(cadeia parada), pedágios |
| `loop` | Escada de loops: degraus vazios, buracos entre degraus, densidade de recompensa |
| `conteudo` | Razão evergreen, burn rate e a data em que o conteúdo seca |

Exemplo — os dois erros topologicamente opostos que mais passam despercebidos em review:

```bash
# paralelo: N portas para o mesmo recurso. O otimizador escolhe uma
# e as outras viram decoração.
python scripts/auditoria_calc.py fontes --recurso comida --valor-hora 4000 \
  --fonte "NPC por gold:60:600:2" --fonte "cadeia da base:35:120:40"

# série: N etapas obrigatórias antes de uma porta só.
python scripts/auditoria_calc.py cadeia --recurso comida --piso 0.55 \
  --elos "plantio:120:0.20:nao,fazenda:90:0.15:nao,cozinha:200:0.10:sim"
```

O segundo comando mostra o que dificilmente se enxerga no olho: três elos com 15% de ociosidade cada dão **39% de chance de o jogador chegar e a linha estar parada**, contra 15% se a fonte fosse única. Confiabilidade em série só cai.

Rodando os testes:

```bash
cd scripts && python -m unittest test_auditoria_calc
```

---

## Exemplo completo

[`exemplos/refino-de-equipamento.md`](exemplos/refino-de-equipamento.md) traz uma auditoria inteira: a proposta como um DEV a escreveria, e o relatório que sai dela — com os comandos da calculadora, as saídas reais e as severidades verificáveis.

O achado principal do exemplo não está na curva de chances, que é onde a discussão naturalmente iria: está num NPC que parecia detalhe de conveniência e tornava o drop 66,6% mais caro que a compra. E a seção 8 do relatório lista, nominalmente, o que o sistema acerta — porque um relatório que só aponta problema faz o DEV consertar o que já funcionava.

---

## O que ela faz de diferente

**Escala a resposta ao alvo.** "Subi o drop de 2% pra 3,5%, tá bom?" recebe um número e uma conclusão, não um relatório de 15 seções. Tamanho da resposta e profundidade da investigação são eixos independentes: mesmo para responder uma linha, se há código ao alcance, ela lê o código.

**Rotula cada afirmação.** `FATO` / `MÉTRICA` / `HIPÓTESE` / `RISCO` / `OPINIÃO`. Quem lê sabe de imediato o que é medição e o que é palpite.

**Pontua em vez de adjetivar.** A severidade sai de impacto, frequência, facilidade de exploração, persistência e custo de correção — e o mesmo problema recebe a mesma nota amanhã.

**Avalia a proposta antes da implementação.** O modo pré-mortem custa uma frase. Depois de implementado, remover uma fonte duplicada custa save, economia e expectativa de jogador.

**Sabe aprovar.** Quando o sistema está certo, ela diz com a mesma firmeza com que diria o contrário. Uma análise que nunca aprova nada é tão inútil quanto uma que aprova tudo.

---

## Sobre o custo

A skill foi avaliada contra o baseline (Claude sem skill nenhuma, mesmos prompts, execuções independentes). O que o benchmark mostrou:

- Num alvo pequeno, ela respondeu em **306 palavras contra 840 do baseline** — a triagem funciona.
- Num caso de redundância sistêmica, o baseline **também acertou o diagnóstico**, em 625 palavras. O que a skill acrescentou foi a quantificação, o circuito de moeda, a tentativa concreta de exploit e os testes de aceite com número — ao custo de 4,6× mais palavras, 6× mais tempo e 2× mais tokens.

Ou seja: para uma decisão rápida, o baseline resolve. Para um sistema que vai ser implementado e não pode ser refeito em três meses, a skill resolve. Ela é cara de propósito, e a triagem existe justamente para escolher o modo certo.

---

## Licença

Uso livre. Copie, modifique, adapte ao seu jogo e redistribua para qualquer finalidade, inclusive comercial. Sem garantias.
