# Evals

A skill é avaliada contra um baseline: **o mesmo modelo, o mesmo prompt, sem skill nenhuma**. Sem essa comparação não dá para saber se a skill acrescenta alguma coisa ou se apenas gasta mais tokens dizendo o que o modelo já diria.

## Como rodar

Para cada eval em `evals.json`, duas execuções independentes e paralelas:

- **with_skill** — sessão limpa, a skill instalada, o prompt do eval como primeira mensagem;
- **without_skill** — sessão limpa, nenhuma skill, o mesmo prompt.

Registre de cada execução: a resposta literal, a contagem de palavras, o número de chamadas de ferramenta e o tempo. Depois avalie as `assertions` do eval uma a uma, à mão — assertion não é regex, é julgamento com critério escrito antes de ver a resposta.

Os alvos **0** e **1** rodam com um projeto de jogo real aberto no diretório de trabalho, porque parte do que eles testam é se a skill vai abrir o código. Os alvos **2** e **3** são autocontidos.

As saídas brutas das execuções ficam fora deste repositório; o que fica versionado são as definições (`evals.json`) e as conclusões (`benchmark.md`).

## O eval que mais importa

O **3 (controle negativo)** é o único que testa a skill contra o próprio viés. Os outros três perguntam "ela acha o problema?". Esse pergunta **"ela inventa problema quando não tem?"**.

O sistema descrito nele é saudável de propósito: fonte única, sink único, oito opções equivalentes, cadência que preenche o degrau de semana, loop fechado. A resposta correta é aprovar.

Uma ferramenta de review que precisa achar defeito para justificar a própria existência é pior que nenhuma — porque o DEV aprende a ignorá-la, e aí ela também não serve quando o defeito é real. Se algum dia a skill reprovar esse eval, o problema não é o eval.

## Regra de honestidade

O `benchmark.md` registra **o que o baseline fez melhor**, não só o que a skill fez melhor. Um benchmark que só mostra vitórias não é medição, é publicidade — e a skill inteira existe para não aceitar esse tipo de evidência dos outros.
