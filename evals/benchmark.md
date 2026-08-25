# Benchmark

## Iteration 2

Rodada focada em dois itens: confirmar a correção do triage (eval 0) e estrear o controle negativo (evals 3 e 4). Baseline não foi re-executado — o da iteration 1 continua válido para os alvos que não mudaram.

| Eval | Palavras | Tool calls | Veredito | Pior severidade | Assertions |
|---|---:|---:|---|---:|---|
| 0 · alvo pequeno | 653 | **36** | 🟠 REFAZER | não pontuou | 5/6 |
| 3 · sistema sem decisão | 1435 | 11 | 🟠 REFAZER | 6,30 | 4/5 |
| 4 · controle negativo | 2025 | 8 | 🟡 RESSALVAS | 7,30 | 6/7 |

### Eval 0 — a regressão da iteration 1 está morta

Este era o item aberto desde a iteration 1, quando o bloco de triage que eu tinha acabado de escrever colapsou dois eixos independentes e a skill respondeu sem abrir o repositório — perdendo, para o baseline, um achado que o baseline encontrou.

| | iteration 1 | iteration 2 |
|---|---:|---:|
| Palavras | 306 | 653 |
| Tool calls | 5 | **36** |
| Leu o código do projeto | **não** | sim |
| Achou o modificador de ritmo | não | sim |

E foi muito além do achado que se perdera: descobriu que **a criatura citada não existe no repositório**, mapeou as duas famílias de loot do jogo (128 entradas de baú com 4 casas decimais derivadas, 91 de material todas em 0,15 geradas por script), encontrou o ponto de saturação em que aumentar a chance deixa de ter qualquer efeito, e viu que o script de regeneração apagaria o valor editado à mão na próxima rodada.

**A assertion que falhou: 653 palavras contra um limite de 500.** Fica registrada como falha. Dá para argumentar que a régua é que está errada — a resposta cresceu porque a investigação encontrou mais, e cortar para caber em 500 significaria omitir que a entidade não existe. Mas mover a régua depois de ver o resultado é exatamente o que esta skill não aceita dos outros, então a falha fica. A pergunta em aberto para a próxima iteração é se o teto deve ser em palavras ou em estrutura.

**Lacuna encontrada:** a resposta emitiu 🟠 REFAZER sem pontuar severidade nenhuma. Corrigido no `SKILL.md`: em resposta curta, ou pontua o achado principal, ou não emite veredito formal.

### Eval 3 — o eval estava errado, e mesmo assim achou um defeito

Escrito para ser controle negativo. **Não era**: evitando as armadilhas que a skill já conhece (redundância, dominância, degrau vazio), o sistema caiu em outra — 8 afixos equivalentes com re-roll ilimitado e uma moeda sem uso alternativo produzem zero decisão. A skill diagnosticou isso corretamente:

> *"Perfil abusador: não achei exploit, porque não há decisão para explorar. O jogo ótimo é trivial e idêntico em todos os perfis. Quando o comportamento ótimo é o mesmo nos seis perfis, você não tem um sistema, tem um botão com cooldown semanal."*

**O defeito real que ele expôs:** pior achado **6,30 (PROBLEMA)** e veredito **🟠 REFAZER**. Fui verificar: o `SKILL.md` definia as quatro classes de severidade numa seção e os quatro vereditos em outra, e **nunca ligava as duas**. O veredito era escolhido no olho — e cinco achados na tela *parecem* reprovação mesmo quando nenhum passa de 6,3.

Essa é a máquina de falso positivo: o veredito passa a medir o esforço do auditor em vez da saúde do sistema, porque qualquer sistema auditado com atenção suficiente acumula cinco achados.

**Correção:** tabela explícita ligando pior severidade a veredito, com a regra de que **o veredito é função do pior achado, não da quantidade de achados**, mais duas exceções que só valem se declaradas em voz alta (dano irreversível e sistema sem decisão). A segunda legitima exatamente o veredito que este eval deu — desde que dito, em vez de escorregado.

O eval foi reclassificado como teste **positivo** para a armadilha "sistema sem decisão", que ele passa muito bem.

### Eval 4 — a correção funcionou na execução seguinte

Veredito **🟡 APROVADO COM RESSALVAS** com pior achado **7,30 (GRAVE)** — e a justificativa citou a tabela nova literalmente: *"a correção mais barata resolve em configuração, por isso RESSALVAS e não REFAZER"*. É a linha da tabela sendo aplicada, não uma coincidência.

Reconheceu **cinco** acertos do sistema, nominalmente, incluindo que a dispersão apertada no boss é deliberada e que o DEV mediu de verdade (benchmark de boss, benchmark de pack e log de mortes real). A assertion de "não tratar 100/92/78 como dominância" passou.

**A assertion que falhou: pior achado 7,30, acima do teto de 7,0.** E aqui a falha é minha de novo — o achado é matemática verificável:

```
ponto de igualdade entre alvo único e área = (100−92) ÷ (240−92) = 8/148 = 5,41%
```

Acima de 5,4% do tempo de combate em grupo, o talento de área domina o de alvo único. Não existe MMO abaixo disso. Eu tinha posto o bônus de área generoso demais contra uma penalidade de alvo único pequena demais, e criei a dominância que o eval deveria não ter.

## A conclusão honesta sobre o controle negativo

**Duas tentativas, dois sistemas com defeito real.** Isso significa que, até aqui, **não está provado que a skill não exagera** — está provado que projetar um sistema genuinamente saudável é mais difícil do que projetar um que pareça saudável, o que já é informação útil, mas não é o que o eval queria medir.

O que *está* provado:

- ela aprova quando a régua manda aprovar, e cita a régua ao fazer isso;
- ela nomeia o que está certo, com detalhe, sem que seja pedido;
- ela não recomendou sistema novo em nenhum dos dois;
- todos os achados vieram com conta que dá para refazer — e as duas que eu refiz, conferiram.

O que **falta**: um sistema saudável que sobreviva a uma auditoria. Até existir um, este é o item aberto da suíte, e ele fica escrito aqui em vez de ser resolvido baixando a régua.

---

## Iteration 1

Baseline: `without_skill` (sem skill nenhuma). Mesmos prompts, mesmo modelo, execuções independentes e paralelas.

| Eval | Config | Palavras | Ferramentas | Tempo | Tokens |
|---|---|---:|---:|---:|---:|
| 0 · alvo pequeno | with_skill | **306** | 5 | 76 s | 62k |
| 0 · alvo pequeno | without_skill | 840 | 13 | 223 s | 59k |
| 1 · redundância | with_skill | **2891** | 15 | 393 s | 96k |
| 1 · redundância | without_skill | 625 | 2 | 62 s | 47k |
| 2 · loop/retenção | with_skill | **2214** | 13 | 317 s | 91k |
| 2 · loop/retenção | without_skill | 1022 | 2 | 88 s | 48k |

### O que ficou provado

**O triage funciona e a resposta escala com o alvo.** Este era o risco número um (relatório de 15 seções para pergunta de uma linha) e não se materializou.

**Os formatos foram escolhidos sem ambiguidade.** Eval 1 → AUDITORIA em pré-mortem. Eval 2 → VISÃO DE DESIGN. Eval 0 → número e conclusão.

**As referências foram usadas, não decoraram.** No eval 2 o achado de severidade mais alta citou a tabela de eventos de `instrumentacao.md`; no eval 1, um achado de legibilidade e o circuito de conversão de `modelagem.md`.

**A regra de substituição de eixo foi aplicada e declarada.** O eval 2 trocou "facilidade de exploração" por "facilidade de o problema passar despercebido" **e avisou que trocou**.

### O que ficou derrubado

**A skill não é o que produz o diagnóstico de redundância.** O baseline do eval 1, em 625 palavras e 2 chamadas de ferramenta, chegou sozinho a "três fontes para o mesmo item, uma vence e as outras viram conteúdo morto" — e chegou bem. O que a skill acrescentou foi quantificação, o circuito de moeda, o teto de preço não declarado, o exploit concreto e os testes de aceite com número.

Isso é valor real, e custou **4,6× mais palavras, 6× mais tempo e 2× mais tokens**. Para a decisão rápida, o baseline resolve. Para o sistema que vai ser implementado e não pode ser refeito em três meses, a skill resolve.

**Achado contra a própria skill: o bloco de triage causou uma regressão no eval 0.** O baseline foi ler o código do projeto e encontrou um modificador de ritmo que a versão com skill não viu, porque não abriu o repositório — 5 chamadas contra 13. Causa: o triage colapsou dois eixos independentes, tamanho do relatório e profundidade da investigação. Corrigido, e **confirmado corrigido na iteration 2**.
