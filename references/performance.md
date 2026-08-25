# Custo de runtime e otimização

Todo sistema de jogo tem um preço em CPU, memória, rede, banco e frame time. Um design lindo que custa 40 ms por tick com 200 jogadores não é um design bom com um problema técnico — é um design ruim, porque a experiência que o jogador recebe é a do servidor engasgando.

A pergunta que governa esta seção:

> **"Funciona com 10 jogadores ou funciona com 10.000?"**

E a que vem logo depois: **onde o custo deixa de ser linear?**

## Índice

1. Como medir antes de opinar
2. Servidor / simulação
3. Rede e netcode
4. Banco de dados e persistência
5. Cliente e frame time
6. Memória
7. Padrões que quebram escala
8. Critérios de aceite de performance

---

## 1. Como medir antes de opinar

Performance é o domínio onde a intuição erra mais. A ordem correta é sempre: **medir → localizar → corrigir → medir de novo**. Otimizar sem profiler é reescrever código aleatoriamente e torcer.

O que exigir antes de aceitar qualquer afirmação de performance:

- **Baseline**: qual era o custo antes?
- **Unidade**: custo por quê — por jogador, por entidade, por tick, por requisição?
- **Carga**: com quantos simultâneos foi medido?
- **Distribuição**: média mente. Peça p95 e p99. O jogador reclama do p99, não da média.
- **Ferramenta**: profiler, contador manual, cronômetro no olho?

## 2. Servidor / simulação

- **Custo por tick.** Quanto tempo o tick leva com N jogadores/entidades? Se o tick estoura o intervalo (ex.: > 50 ms num tick de 20 Hz), o servidor entra em dívida e tudo atrasa em cascata.
- **Complexidade do loop.** `O(n²)` em interação entre entidades (todos contra todos, checagem de proximidade ingênua, AoE varrendo o mapa) funciona no teste com 10 e derrete com 500. Procure loops aninhados sobre coleções de entidades.
- **Escopo de atualização.** Entidades fora da visão de qualquer jogador precisam simular? Sistemas de spawn, IA e decay costumam rodar no mundo inteiro quando poderiam rodar só onde há observador.
- **Eventos sincronizados.** Daily reset, respawn global, evento de horário — tudo acontecendo no mesmo instante cria pico. Escalone.
- **Timers.** Milhares de timers individuais custam mais que uma varredura agendada. Verifique como o sistema agenda trabalho futuro.
- **Alocação em hot path.** Alocar por frame/tick gera pressão de GC (ou fragmentação) que aparece como stutter periódico, não como lentidão constante.

## 3. Rede e netcode

- **Bytes por jogador por segundo**, e como escala com densidade. O caso ruim não é o mapa cheio de gente, é o mapa cheio de gente **fazendo coisas ao mesmo tempo**.
- **Frequência de update vs. necessidade.** Posição a 20 Hz é necessário; inventário a 20 Hz é desperdício. Cada pacote precisa justificar sua frequência.
- **Interest management.** O servidor manda para o jogador só o que ele pode ver? Se manda tudo, o custo cresce com o quadrado da densidade — e ainda entrega informação que vira wallhack.
- **Confiança no cliente.** Toda decisão de gameplay validada no cliente é exploit esperando (ver `testes-e-exploits.md`). Reconciliação e predição do lado do cliente são legítimas; **autoridade** no cliente não é.
- **Tamanho de payload.** Serializar objeto inteiro quando mudou um campo é o desperdício mais comum e o mais fácil de corrigir (delta/dirty flags).
- **Latência percebida.** Input delay, favor do atirador, rollback. Meça o tempo entre input e feedback visual, não só o ping.

## 4. Banco de dados e persistência

- **Query por ação de jogador.** Se cada golpe, passo ou pickup toca o banco, o banco é o teto do jogo. Persistência deve ser periódica ou por evento significativo, não por microação.
- **N+1.** Carregar uma lista e depois consultar item por item. Clássico, invisível em dev com 3 registros, fatal com 30.000.
- **Índices.** Toda query em hot path precisa de índice compatível; toda escrita paga o custo de manter índices demais. Os dois extremos doem.
- **Transação longa.** Segurar transação enquanto se faz lógica de jogo trava linhas e serializa jogadores que nada têm a ver entre si.
- **Save de mundo.** Quanto tempo trava? Trava? Snapshot de mundo inteiro no mesmo instante é fonte clássica de freeze periódico.
- **Migração.** Toda mudança de schema ou de balanceamento precisa dizer o que acontece com os dados existentes.

## 5. Cliente e frame time

- **Frame budget.** 60 FPS = 16,6 ms por frame; 30 FPS = 33 ms. Todo sistema novo precisa declarar quanto do orçamento consome, incluindo o pior caso.
- **Draw calls e overdraw.** Muitas entidades, partículas e UI transparente empilhada. Efeito visual bonito que só aparece em raid é exatamente o que roda no pior momento possível.
- **UI.** Reflow/relayout a cada atualização de dado é um dos custos mais subestimados. Atualizar texto não deveria recalcular a árvore inteira.
- **Carregamento e stutter.** Carregar asset no meio do gameplay causa engasgo. Pré-carregue ou faça streaming.
- **Mobile:** adicione bateria, aquecimento (throttling) e tamanho do build. Um jogo que esquenta o aparelho perde sessão mesmo com FPS aceitável.

## 6. Memória

- **Crescimento ao longo da sessão.** Memória que só sobe é vazamento até prova em contrário. Meça em sessão longa, não em 5 minutos.
- **Custo por entidade.** Multiplique pelo máximo plausível de entidades, não pelo típico.
- **Caches sem limite.** Cache sem política de expiração é vazamento com nome bonito.
- **Assets duplicados** em memória por falta de compartilhamento de recurso.

## 7. Padrões que quebram escala

Estes aparecem repetidamente e valem verificação explícita:

| Padrão | Por que quebra |
|---|---|
| Loop `O(n²)` sobre entidades | Cresce com o quadrado da densidade; o teste com 10 nunca mostra |
| Busca linear por ID em lista | Barato uma vez, caro dentro do tick |
| Broadcast para todos os jogadores | Custo = jogadores × eventos; explode em evento de servidor |
| Persistência por microação | O banco vira o gargalo do gameplay |
| Recalcular estado derivado toda hora | Cachear com invalidação explícita resolve quase sempre |
| Polling em vez de evento | Gasta CPU perguntando "mudou?" para coisa que não mudou |
| String como chave em hot path | Comparação e hash em caminho crítico; use id numérico |
| Log verboso em produção | I/O síncrono no tick é engasgo garantido |
| Lock global | Serializa jogadores independentes; a máquina tem cores, o jogo não usa |

## 8. Critérios de aceite de performance

Como qualquer teste de aceite desta skill, precisa de número. Modelo:

> *"Tick médio ≤ 12 ms e p99 ≤ 25 ms com 500 jogadores simultâneos em zona de alta densidade; tráfego ≤ 8 KB/s por jogador; nenhuma query nova em hot path; memória estável (±5%) em sessão de 4 horas."*

E o critério que fecha: **um sistema que passa em balanceamento mas não passa em performance não está aprovado.** Diversão que só existe abaixo de 50 jogadores é diversão de demo, não de produto.
