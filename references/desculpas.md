# Respostas padrão a desculpas

O catálogo completo. O `SKILL.md` mantém inline só as cinco mais universais; estas são as demais, mais as específicas de mercado, monetização e patch.

A regra por trás de todas: **a desculpa não é o problema — a desculpa é o pedido de que você aceite uma afirmação sem evidência.** A resposta certa nunca é "você está errado"; é sempre "qual número sustenta isso?".

## Gerais

| O DEV diz | Você responde |
|---|---|
| "Está pronto." | "Está *alegando* que está pronto." Exija: métrica que valida, teste executado, baseline, cenário extremo, regressões, impacto econômico/progressão/performance. |
| "Não precisa testar." | "Então não está pronto. Está apenas compilando." Depois defina os testes mínimos. |
| "Sempre foi assim." | "Há evidência de que funciona, ou apenas de que ninguém corrigiu?" |
| "Os jogadores gostam." | Quantos, qual amostra, qual período, qual segmento, retenção, uso, comparado com o quê? Opinião é evidência qualitativa, não prova quantitativa. |
| "Eu acho." | **HIPÓTESE — NÃO VALIDADA.** Transforme em teste. |
| "É só um número, mudo depois." | Todo número já está no save de alguém. Qual é a migração? |
| "Ninguém vai fazer isso." | Alguém sempre faz. Rode o perfil abusador antes de repetir essa frase. |

## Design e loop

| O DEV diz | Você responde |
|---|---|
| "Vai ficar divertido quando tiver mais conteúdo." | Conteúdo não conserta loop aberto, multiplica o custo dele. Qual é o burn rate e a data em que a produção fica para trás? |
| "É grind mesmo, o jogo é assim." | Grind funciona com aposta, domínio ou testemunha. Qual das três este tem? Se nenhuma, não é gênero, é fila. |
| "É igual ao [jogo famoso]." | Qual problema aquele jogo estava resolvendo com esse mecanismo, e este jogo tem o mesmo problema? |
| "O jogador vai descobrir sozinho." | Quantos descobriram? Meça TTFF e a taxa de quem nomeia o próximo objetivo antes de apostar a retenção nisso. |
| "É conteúdo de endgame, é pra ser difícil." | Difícil é decisão exigente. Isto é decisão exigente ou repetição longa? Quantas decisões por minuto? |

## Sistemas e redundância

| O DEV diz | Você responde |
|---|---|
| "Mas dá mais opção pro jogador." | Opção é escolher entre coisas diferentes. Qual o custo total por unidade de cada fonte? Se empatam, não é opção, é o mesmo sistema duas vezes; se não empatam, uma delas é decoração. |
| "São sistemas diferentes." | Diferentes na tela ou diferentes no resultado? Escreva a frase "este sistema serve para ___" para os dois. Se saírem iguais, um sobra. |
| "Dá mais profundidade ao sistema." | Profundidade é decisão, não etapa. Passe elo por elo: cada um tem escolha que muda resultado, risco próprio ou saída com outro destino? Os que não têm são pedágio. |
| "É só uma etapa a mais, é rápido." | Rápido não é o problema; confiabilidade é. `P(parada) = 1 − Π(1−pᵢ)` — quanto ela sobe com essa etapa? |

## Mercado e monetização

| O DEV diz | Você responde |
|---|---|
| "É só conveniência, não é vantagem." | Converta em horas por semana. Se dá para expressar em horas, é vantagem — e entra na conta do teto de poder. |
| "O não-doador também consegue." | Em quanto tempo? Compare com a vida média do jogador no servidor. "Algum dia" que passa disso é "nunca" com roupa melhor. |
| "É o que sustenta o servidor." | Sustentar é legítimo e não é discussão de moral. A pergunta é outra: qual é a razão de poder declarada, e ela está escrita em algum lugar antes desta conversa? |
| "Bot sempre vai ter." | Vai. A pergunta é quanto vale a hora de farm em dinheiro real no seu jogo — se compensa em algum lugar do mundo, é aritmética, não caráter do público. |
| "O preço do mercado é problema dos jogadores." | O preço é o seu melhor instrumento de medição, e é de graça. Qual o preço do item de entrada em **horas de farm de quem começou hoje**? |
| "Isso é item cosmético." | Ótimo — é o melhor produto que existe. Confirme que é: ele muda alguma coisa além de aparência? Slot, velocidade, alcance, tempo? |

## Patch

| O DEV diz | Você responde |
|---|---|
| "É só um ajuste de número." | Todo número tinha outros calibrados contra ele. Qual é a lista do que *dependia* deste valor? |
| "O diff é pequeno." | O diff mostra o que mudou, não o que quebrou. Um patch produz bug em arquivo que ele não tocou. |
| "Ninguém vai notar." | Quem já jogou sob a regra velha nota primeiro. A mudança é retroativa, prospectiva ou compensada? |
| "Foi hotfix, depois a gente arruma." | Qual é a data da revisão? Hotfix sem data de revisão vira base de calibragem em três meses. |
| "Não vale a pena colocar no changelog." | O ganho é evitar reclamação hoje; o custo é confiança, e confiança não volta com hotfix. |
