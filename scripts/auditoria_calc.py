#!/usr/bin/env python3
"""Calculadora de auditoria de sistemas de jogo.

Uso rapido:
  python auditoria_calc.py severity --impacto 9 --frequencia 7 --exploracao 8 --persistencia 10 --custo 3
  python auditoria_calc.py ev --outcomes "100:5,20:80,1:5000"          # tabela por PESO
  python auditoria_calc.py ev --outcomes "0.001:5000,0.999:3" --per-hour 40
  python auditoria_calc.py netflow --faucet 1200 --sink 350 --players 500 --hours-per-day 3
  python auditoria_calc.py ttk --hp 5000 --hit 260 --reduction 0.35 --flat-reduction 40
  python auditoria_calc.py gacha --p 0.006 --pity 90 --price 2.5
  python auditoria_calc.py fontes --recurso food --valor-hora 4000 --fonte "farm na base:35:120" --fonte "farm na ilha:0:40" --fonte "NPC por gold:60:600"
  python auditoria_calc.py loop --degraus "momento:2:sim,micro:45:sim,medio:720:nao,sessao:3000:sim,semana:0:nao,temporada:0:nao,vida:0:sim" --recompensas-sessao 6 --sessao-min 50
  python auditoria_calc.py cadeia --recurso comida --elos "plantio:120:0.2:nao,fazenda:90:0.15:nao,cozinha:200:0.1:sim" --piso 0.55
  python auditoria_calc.py conteudo --perecivel-horas 40 --evergreen-horas 12 --consumo-semana 25 --producao-mes 6

Todas as saidas mostram a conta, nao so o resultado: o DEV precisa poder refazer
e discordar com numeros.

As funcoes calc_* sao puras (recebem numeros, devolvem dict) para poderem ser
testadas. Ver test_auditoria_calc.py.
"""

import argparse
import math
import random
import sys

SEP = "-" * 62
TOL = 1e-6


# --------------------------------------------------------------------------
# severity
# --------------------------------------------------------------------------

PESOS = {
    "impacto": 0.30,
    "frequencia": 0.20,
    "exploracao": 0.20,
    "persistencia": 0.20,
    "custo": 0.10,
}


def classificar(score):
    if score < 3.0:
        return "ACEITAVEL"
    if score < 5.0:
        return "ATENCAO"
    if score < 7.0:
        return "PROBLEMA"
    if score < 8.5:
        return "GRAVE"
    return "CRITICO"


def calc_severity(comps):
    for nome, v in comps.items():
        if not 0 <= v <= 10:
            raise ValueError("%s deve estar entre 0 e 10 (recebido %s)" % (nome, v))
    parcelas = {nome: v * PESOS[nome] for nome, v in comps.items()}
    total = sum(parcelas.values())
    return {"parcelas": parcelas, "score": total, "classe": classificar(total)}


def cmd_severity(a):
    comps = {
        "impacto": a.impacto,
        "frequencia": a.frequencia,
        "exploracao": a.exploracao,
        "persistencia": a.persistencia,
        "custo": a.custo,
    }
    r = calc_severity(comps)
    print("SEVERIDADE")
    print(SEP)
    for nome in PESOS:
        print("  %-13s %4.1f x %.2f = %5.2f"
              % (nome, comps[nome], PESOS[nome], r["parcelas"][nome]))
    print(SEP)
    print("  Severity = %.2f  ->  %s" % (r["score"], r["classe"]))
    if comps["exploracao"] >= 8 and comps["persistencia"] >= 8:
        print("\n  ALERTA: facil de explorar E permanente. O estoque ja gerado")
        print("  nao some sozinho - o plano de correcao precisa de deteccao e")
        print("  de decisao sobre o que ja entrou nos saves.")


# --------------------------------------------------------------------------
# ev
# --------------------------------------------------------------------------

def parse_outcomes(texto):
    """'100:5,20:80' -> [(100.0, 5.0), (20.0, 80.0)]  (numero bruto, valor)."""
    saida = []
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if ":" not in parte:
            raise ValueError("formato esperado 'peso_ou_prob:valor', recebido '%s'" % parte)
        n, v = parte.split(":", 1)
        try:
            n, v = float(n), float(v)
        except ValueError:
            raise ValueError("numeros invalidos em '%s'" % parte)
        if n < 0:
            raise ValueError("peso/probabilidade negativo em '%s'" % parte)
        saida.append((n, v))
    if not saida:
        raise ValueError("nenhum resultado informado em --outcomes")
    if sum(n for n, _ in saida) <= 0:
        raise ValueError("a soma dos pesos/probabilidades e zero")
    return saida


def normalize_outcomes(brutos, modo="auto"):
    """Decide se a tabela e de PESOS ou de PROBABILIDADES e normaliza.

    Regra (a ambiguidade aqui foi a origem de um EV errado por 121x):
      soma ~ 1  -> probabilidades
      soma < 1  -> probabilidades, com um resultado implicito 'nada' (valor 0)
      soma > 1  -> pesos, normalizados pela soma
    Tabela de UMA linha nao permite inferir o modo: exige --weights ou --probs.
    """
    soma = sum(n for n, _ in brutos)

    if modo == "probs":
        for n, _ in brutos:
            if not 0 < n <= 1:
                raise ValueError("com --probs, cada probabilidade deve estar em (0,1]; "
                                 "recebido %g" % n)
        if soma > 1 + TOL:
            raise ValueError("com --probs, a soma nao pode passar de 1 (soma=%.6f)" % soma)
        modo_usado = "probabilidades"
    elif modo == "weights":
        modo_usado = "pesos"
    else:
        if soma <= 1.0 + TOL:
            modo_usado = "probabilidades"
        elif len(brutos) == 1:
            raise ValueError(
                "tabela de uma linha com valor %g: impossivel inferir se e peso "
                "ou probabilidade. Use --weights ou --probs." % brutos[0][0])
        else:
            modo_usado = "pesos"

    if modo_usado == "pesos":
        probs = [(n / soma, v) for n, v in brutos]
        implicito = None
    else:
        probs = list(brutos)
        resto = 1.0 - soma
        implicito = resto if resto > TOL else None
        if implicito:
            probs = probs + [(implicito, 0.0)]

    return {"probs": probs, "modo": modo_usado, "soma_bruta": soma,
            "resto_implicito": implicito}


def calc_ev(probs):
    ev = sum(p * v for p, v in probs)
    var = sum(p * (v - ev) ** 2 for p, v in probs)
    dp = math.sqrt(var)
    return {
        "ev": ev,
        "variancia": var,
        "desvio": dp,
        "cv": (dp / abs(ev)) if ev else float("inf"),
        "pior": min(v for _, v in probs),
        "melhor": max(v for _, v in probs),
    }


def attempts_for(p, alvo):
    """Tentativas para atingir `alvo` de chance acumulada."""
    if not 0 < p <= 1:
        raise ValueError("p deve estar em (0,1]")
    if p == 1:
        return 1.0
    return math.log(1 - alvo) / math.log(1 - p)


def simulate_sessions(probs, draws_por_sessao, sessoes, seed=42):
    """Percentis do VALOR ACUMULADO por sessao (nao de um sorteio isolado)."""
    random.seed(seed)
    faixas, base = [], 0.0
    for p, v in probs:
        base += p
        faixas.append((base, v))
    totais = []
    for _ in range(sessoes):
        total = 0.0
        for _ in range(draws_por_sessao):
            r = random.random()
            for limite, v in faixas:
                if r <= limite:
                    total += v
                    break
            else:
                total += faixas[-1][1]
        totais.append(total)
    totais.sort()

    def pct(q):
        return totais[min(len(totais) - 1, max(0, int(q * len(totais))))]

    return {"p10": pct(0.10), "p25": pct(0.25), "mediana": pct(0.50),
            "p75": pct(0.75), "p90": pct(0.90), "p99": pct(0.99),
            "media": sum(totais) / len(totais)}


def cmd_ev(a):
    if a.weights and a.probs:
        raise ValueError("--weights e --probs sao mutuamente exclusivos")
    brutos = parse_outcomes(a.outcomes)
    modo = "weights" if a.weights else ("probs" if a.probs else "auto")
    norm = normalize_outcomes(brutos, modo)
    probs = norm["probs"]
    r = calc_ev(probs)

    print("VALOR ESPERADO")
    print(SEP)
    print("  Tabela interpretada como: %s (soma bruta = %.6g)"
          % (norm["modo"].upper(), norm["soma_bruta"]))
    if norm["modo"] == "pesos":
        print("  Pesos normalizados pela soma %.6g." % norm["soma_bruta"])
    if norm["resto_implicito"]:
        print("  Tabela incompleta: %.4f%% de chance de NADA (valor 0) foi assumida."
              % (norm["resto_implicito"] * 100))
        print("  Se o resto nao for 'nada', informe a linha que falta.")
    print(SEP)
    for p, v in probs:
        print("  p=%-10.6g valor=%-12.6g contribui %.4f" % (p, v, p * v))
    print(SEP)
    print("  EV            = %.4f" % r["ev"])
    print("  desvio padrao = %.4f" % r["desvio"])
    if r["ev"]:
        print("  CV (dp/EV)    = %.2f" % r["cv"])
        if r["cv"] > 2:
            print("  -> variancia alta: o EV medio nao descreve a experiencia real.")
            print("     Reporte tambem mediana e percentil 90 antes de aprovar.")
    print("  pior caso     = %.4f" % r["pior"])
    print("  melhor caso   = %.4f" % r["melhor"])
    if a.per_hour:
        print("  EV/hora       = %.4f  (%g tentativas/h)" % (r["ev"] * a.per_hour, a.per_hour))

    p_raro = min(p for p, _ in probs)
    if 0 < p_raro < 1:
        print(SEP)
        print("  Resultado mais raro (p=%.6g):" % p_raro)
        print("    media de tentativas ate o 1o sucesso = %.1f" % (1.0 / p_raro))
        for alvo in (0.5, 0.9, 0.99):
            n = attempts_for(p_raro, alvo)
            linha = "    tentativas para %2.0f%% de chance       = %.1f" % (alvo * 100, n)
            if a.per_hour:
                linha += "   (%.1f h)" % (n / a.per_hour)
            print(linha)
        if a.per_hour:
            print("    -> o percentil 90 e o jogador que voce perde. Compare com o")
            print("       tempo que ele leva para conseguir o item por outra via.")

    if a.sim_sessions:
        if not a.per_hour:
            raise ValueError("--sim-sessions exige --per-hour para saber quantos "
                             "sorteios cabem numa sessao")
        draws = max(1, int(round(a.per_hour * a.session_hours)))
        s = simulate_sessions(probs, draws, a.sim_sessions, a.seed)
        print(SEP)
        print("  Valor ACUMULADO por sessao de %.1f h (%d sorteios), %d sessoes:"
              % (a.session_hours, draws, a.sim_sessions))
        print("    media = %.2f" % s["media"])
        print("    p10 = %.2f | p25 = %.2f | mediana = %.2f | p75 = %.2f | p90 = %.2f | p99 = %.2f"
              % (s["p10"], s["p25"], s["mediana"], s["p75"], s["p90"], s["p99"]))
        if s["mediana"] and s["media"] / s["mediana"] > 1.5:
            print("    -> media muito acima da mediana: a maioria das sessoes rende")
            print("       menos que o 'esperado'. O EV esta sendo carregado pela cauda,")
            print("       e a cauda nao e quem paga a assinatura.")


# --------------------------------------------------------------------------
# netflow
# --------------------------------------------------------------------------

def calc_netflow(faucet, sink, players, hours_per_day, stock=0.0):
    net_h = faucet - sink
    net_dia_jogador = net_h * hours_per_day
    net_dia_total = net_dia_jogador * players
    projecao = {d: stock + net_dia_total * d for d in (1, 7, 30, 90)}
    if faucet <= 0 and sink <= 0:
        estado = "economia_inexistente"
    elif faucet <= 0:
        estado = "so_sink"
    elif net_h > 0:
        estado = "inflacionaria" if (sink / faucet) < 0.5 else "positiva_controlada"
    elif net_h == 0:
        estado = "equilibrio_exato"
    else:
        estado = "deflacionaria"
    return {"net_h": net_h, "net_dia_jogador": net_dia_jogador,
            "net_dia_total": net_dia_total, "projecao": projecao,
            "absorcao": (sink / faucet) if faucet > 0 else None, "estado": estado}


def cmd_netflow(a):
    r = calc_netflow(a.faucet, a.sink, a.players, a.hours_per_day, a.stock)
    print("NET FLOW DE ECONOMIA")
    print(SEP)
    print("  faucet/h por jogador  = %12.2f" % a.faucet)
    print("  sink/h  por jogador   = %12.2f" % a.sink)
    print("  net/h   por jogador   = %12.2f" % r["net_h"])
    print("  horas jogadas por dia = %12.2f" % a.hours_per_day)
    print("  jogadores ativos      = %12d" % a.players)
    print(SEP)
    print("  net/dia por jogador   = %12.2f" % r["net_dia_jogador"])
    print("  net/dia agregado      = %12.2f" % r["net_dia_total"])
    print(SEP)
    print("  Projecao de estoque (estoque inicial = %.2f):" % a.stock)
    for dias in (1, 7, 30, 90):
        linha = "    %3d dias: %18.2f" % (dias, r["projecao"][dias])
        if a.stock > 0:
            linha += "   (%+.1f%% vs. inicial)" % ((r["projecao"][dias] / a.stock - 1) * 100)
        print(linha)

    print(SEP)
    estado = r["estado"]
    if estado == "economia_inexistente":
        print("  Faucet e sink zerados. Isto NAO e equilibrio: e ausencia de")
        print("  instrumentacao. Meca antes de concluir qualquer coisa.")
    elif estado == "so_sink":
        print("  So existe sink e nenhum faucet: o recurso caminha para zero.")
        print("  Deflacao total trava craft, mercado e progressao.")
    elif estado == "equilibrio_exato":
        print("  Net flow exatamente zero. Verifique se e desenho ou coincidencia")
        print("  do numero medio - a distribuicao por percentil de jogador quase")
        print("  nunca fica zerada junto.")
    elif estado == "deflacionaria":
        print("  Sinks superam faucets. Cheque o outro lado do risco - deflacao")
        print("  e escassez travam o jogador novo.")
    else:
        print("  Sinks absorvem %.1f%% dos faucets." % (r["absorcao"] * 100))
        if estado == "inflacionaria":
            print("  ALERTA: menos de metade do que entra e destruido. Inflacao")
            print("  estrutural - o preco de mercado vai excluir o jogador novo,")
            print("  que e justamente quem sustenta a base.")
    print("\n  Lembrete: trade entre jogadores e TRANSFERENCIA, nao sink.")
    print("  Se algum 'sink' desta conta for mercado, refaca o numero.")
    print("  A projecao assume populacao constante: com churn ou crescimento,")
    print("  recalcule por coorte antes de citar o numero de 90 dias.")


# --------------------------------------------------------------------------
# ttk
# --------------------------------------------------------------------------

def calc_ttk(hp, hit, reduction=0.0, flat=0.0, hits_per_sec=1.0,
             crit=0.0, crit_mult=2.0, uptime=1.0, min_damage=0.0):
    """Mitigacao aplicada nesta ordem: percentual primeiro, plana depois.

    A ordem importa: 100 de dano com 30% e 20 de armadura da 50 nesta ordem e
    56 na ordem inversa. Se o jogo aplicar ao contrario, converta antes.
    """
    if hp <= 0:
        raise ValueError("--hp deve ser positivo")
    if hit < 0 or flat < 0:
        raise ValueError("dano e reducao plana nao podem ser negativos")
    if reduction > 1 + TOL:
        raise ValueError("--reduction acima de 1 nao faz sentido; use 1.0 para imunidade")
    if not 0 <= crit <= 1:
        raise ValueError("--crit deve ser fracao entre 0 e 1")
    if not 0 < uptime <= 1:
        raise ValueError("--uptime deve estar em (0,1]")
    if hits_per_sec <= 0:
        raise ValueError("--hits-per-sec deve ser positivo")

    dano_pos_pct = hit * (1 - reduction)
    dano_mitigado = max(min_damage, dano_pos_pct - flat)
    dano_medio = dano_mitigado * (1 + crit * (crit_mult - 1))
    dps = dano_medio * hits_per_sec * uptime

    if dano_medio <= 0:
        return {"dano_pos_pct": dano_pos_pct, "dano_mitigado": dano_mitigado,
                "dano_medio": 0.0, "dps": 0.0, "hits": float("inf"),
                "ttk": float("inf"), "imune": True}

    return {"dano_pos_pct": dano_pos_pct, "dano_mitigado": dano_mitigado,
            "dano_medio": dano_medio, "dps": dps,
            "hits": math.ceil(hp / dano_medio), "ttk": hp / dps, "imune": False}


def cmd_ttk(a):
    r = calc_ttk(a.hp, a.hit, a.reduction, a.flat_reduction, a.hits_per_sec,
                 a.crit, a.crit_mult, a.uptime, a.min_damage)
    print("TTK / DPS")
    print(SEP)
    print("  HP                    = %10.2f" % a.hp)
    print("  dano bruto por hit    = %10.2f" % a.hit)
    print("  reducao percentual    = %9.1f%%  -> %.2f"
          % (a.reduction * 100, r["dano_pos_pct"]))
    if a.flat_reduction or a.min_damage:
        print("  reducao plana         = %10.2f  -> %.2f (piso: %.2f)"
              % (a.flat_reduction, r["dano_mitigado"], a.min_damage))
        print("  (ordem aplicada: percentual, depois plana)")
    print("  crit %.0f%% x%.2f -> dano medio por hit = %.2f"
          % (a.crit * 100, a.crit_mult, r["dano_medio"]))
    print("  hits/s = %.2f | uptime = %.0f%%" % (a.hits_per_sec, a.uptime * 100))
    print(SEP)

    if r["imune"]:
        print("  DANO EFETIVO = 0  ->  TTK INFINITO (alvo imune).")
        print("  Caso extremo valido: confirme se o jogo permite essa combinacao")
        print("  de mitigacao. Imunidade acidental por stack de reducao e achado")
        print("  de auditoria, nao erro de entrada.")
        return

    print("  DPS efetivo           = %10.2f" % r["dps"])
    print("  hits necessarios      = %10d" % r["hits"])
    print("  TTK                   = %10.2f s" % r["ttk"])
    print(SEP)
    hits = r["hits"]
    print("  Breakpoint: com %d hits, o dano medio precisa ser >= %.2f"
          % (hits, a.hp / hits))
    if hits > 1:
        alvo = a.hp / (hits - 1)
        delta = (alvo / r["dano_medio"] - 1) * 100
        print("  Para matar em %d hits: dano medio >= %.2f  (+%.1f%%)"
              % (hits - 1, alvo, delta))
        print("  Ate esse ponto, ganho de dano NAO reduz o numero de hits -")
        print("  o balanceamento real acontece na fronteira do arredondamento.")
    if a.flat_reduction and r["dano_pos_pct"] > 0:
        perda = a.flat_reduction / r["dano_pos_pct"]
        print("  A reducao plana corta %.1f%% deste hit. Contra hits pequenos ela"
              % (perda * 100))
        print("  corta proporcionalmente mais: e o que mata builds de multi-hit.")


# --------------------------------------------------------------------------
# gacha
# --------------------------------------------------------------------------

def calc_gacha(p, pity=0, price=0.0):
    if not 0 < p <= 1:
        raise ValueError("--p deve estar em (0,1]")
    if pity < 0:
        raise ValueError("--pity nao pode ser negativo")

    r = {"p": p, "media_pulls": 1 / p}
    r["pulls_alvo"] = {alvo: attempts_for(p, alvo) for alvo in (0.5, 0.9, 0.99)}

    if pity:
        r["p_antes_pity"] = 1 - (1 - p) ** (pity - 1)
        # E[min(G, n)] = soma_{k=0}^{n-1} (1-p)^k = (1-(1-p)^n)/p
        r["esperado"] = (1 - (1 - p) ** pity) / p
        r["pior_caso"] = pity
    else:
        r["esperado"] = 1 / p
        r["pior_caso"] = None

    if price:
        n90 = r["pulls_alvo"][0.9]
        if pity:
            n90 = min(n90, pity)
        r["custo_medio"] = r["esperado"] * price
        r["custo_p90"] = n90 * price
        r["custo_max"] = pity * price if pity else None
        r["custo_p99"] = None if pity else r["pulls_alvo"][0.99] * price
    return r


def cmd_gacha(a):
    r = calc_gacha(a.p, a.pity, a.price)
    print("GACHA / PITY")
    print(SEP)
    print("  chance por pull       = %.6g (%.4f%%)" % (a.p, a.p * 100))
    print("  media de pulls ate o 1o sucesso = %.1f" % r["media_pulls"])
    for alvo in (0.5, 0.9, 0.99):
        print("  pulls para %2.0f%% de chance        = %.1f"
              % (alvo * 100, r["pulls_alvo"][alvo]))

    if a.pity:
        print(SEP)
        print("  pity hard em          = %d pulls" % a.pity)
        print("  chance de conseguir antes do pity = %.2f%%" % (r["p_antes_pity"] * 100))
        print("  pulls esperados com pity          = %.1f" % r["esperado"])
        print("  pior caso garantido               = %d pulls" % r["pior_caso"])
    else:
        print(SEP)
        print("  SEM PITY: a cauda e infinita. 1%% dos jogadores passa de %.0f pulls."
              % r["pulls_alvo"][0.99])
        print("  Se o item for necessario para progredir, isso e achado de")
        print("  auditoria, nao detalhe de tuning.")

    if a.price:
        print(SEP)
        print("  preco por pull         = %.2f" % a.price)
        print("  custo medio ate o alvo = %.2f" % r["custo_medio"])
        print("  custo no percentil 90  = %.2f" % r["custo_p90"])
        if r["custo_max"] is not None:
            print("  custo maximo (pity)    = %.2f" % r["custo_max"])
        else:
            print("  custo no percentil 99  = %.2f  (sem teto: a cauda continua)"
                  % r["custo_p99"])


# --------------------------------------------------------------------------
# progressao  (curva de xp, tempo por nivel e walls)
# --------------------------------------------------------------------------

FATOR_WALL = 1.5


def xp_do_nivel(n, base, modelo, fator):
    """Custo em XP para sair do nivel n para o n+1."""
    if modelo == "geo":
        return base * (fator ** (n - 1))
    if modelo == "poly":
        return base * (n ** fator)
    if modelo == "linear":
        return base * (1 + fator * (n - 1))
    raise ValueError("modelo deve ser geo, poly ou linear (recebido '%s')" % modelo)


def calc_progressao(nivel_min, nivel_max, base, modelo="geo", fator=1.15,
                    xp_hora=1.0, xp_hora_fator=1.0):
    if nivel_min < 1:
        raise ValueError("nivel_min deve ser >= 1")
    if nivel_max <= nivel_min:
        raise ValueError("nivel_max deve ser maior que nivel_min")
    if base <= 0:
        raise ValueError("xp base deve ser maior que zero")
    if xp_hora <= 0:
        raise ValueError("xp por hora deve ser maior que zero")

    niveis, acumulado = [], 0.0
    for n in range(nivel_min, nivel_max):
        custo = xp_do_nivel(n, base, modelo, fator)
        taxa = xp_hora * (xp_hora_fator ** (n - nivel_min))
        horas = custo / taxa
        acumulado += horas
        niveis.append({"nivel": n, "xp": custo, "xp_hora": taxa,
                       "horas": horas, "acumulado": acumulado})

    # Wall: o tempo por nivel dispara em relacao ao nivel anterior. Se o xp/h
    # cresce junto com o custo, nao ha wall - e por isso que a conta usa TEMPO,
    # nao XP. Curva de XP explosiva com renda explosiva e progressao estavel.
    walls = []
    for ant, atual in zip(niveis, niveis[1:]):
        razao = atual["horas"] / ant["horas"] if ant["horas"] > 0 else float("inf")
        if razao >= FATOR_WALL:
            walls.append({"nivel": atual["nivel"], "razao": razao,
                          "horas": atual["horas"]})

    total = acumulado
    # Cauda: quanto do tempo total mora nos ultimos 10% dos niveis.
    corte = max(1, int(len(niveis) * 0.10))
    cauda = sum(x["horas"] for x in niveis[-corte:])
    fracao_cauda = cauda / total if total > 0 else 0.0

    metade = None
    parcial = 0.0
    for x in niveis:
        parcial += x["horas"]
        if parcial >= total / 2.0:
            metade = x["nivel"]
            break

    return {"niveis": niveis, "total_horas": total, "walls": walls,
            "fracao_cauda": fracao_cauda, "niveis_cauda": corte,
            "nivel_da_metade": metade}


def cmd_progressao(a):
    r = calc_progressao(a.nivel_min, a.nivel_max, a.xp_base, a.modelo, a.fator,
                        a.xp_hora, a.xp_hora_fator)
    niveis = r["niveis"]
    print("CURVA DE PROGRESSAO  (modelo %s, fator %.4g)" % (a.modelo, a.fator))
    print(SEP)
    print("  %6s %14s %14s %10s %12s" %
          ("nivel", "xp p/ subir", "xp/hora", "horas", "acumulado"))

    # Com muitos niveis, amostra em vez de despejar 300 linhas.
    passo = 1 if len(niveis) <= 25 else max(1, len(niveis) // 20)
    for i, x in enumerate(niveis):
        if passo > 1 and i % passo and i != len(niveis) - 1:
            continue
        print("  %6d %14.0f %14.0f %10.2f %12.1f"
              % (x["nivel"], x["xp"], x["xp_hora"], x["horas"], x["acumulado"]))
    if passo > 1:
        print("  (amostrado 1 a cada %d niveis; total de %d niveis na faixa)"
              % (passo, len(niveis)))

    print(SEP)
    print("  tempo total %d -> %d = %.1f h (%.1f dias a 3h/dia)"
          % (a.nivel_min, a.nivel_max, r["total_horas"], r["total_horas"] / 3.0))
    print("  metade do tempo total ja foi gasta ao chegar no nivel %d"
          % r["nivel_da_metade"])
    print("  os ultimos %d niveis concentram %.1f%% do tempo total"
          % (r["niveis_cauda"], r["fracao_cauda"] * 100))

    print(SEP)
    if r["walls"]:
        print("  WALLS - niveis em que o TEMPO por nivel salta >= %.0f%%:"
              % ((FATOR_WALL - 1) * 100))
        for w in r["walls"][:10]:
            print("    nivel %-5d %.2fx o anterior (%.1f h nesse nivel)"
                  % (w["nivel"], w["razao"], w["horas"]))
        if len(r["walls"]) > 10:
            print("    (+%d walls nao listadas)" % (len(r["walls"]) - 10))
        print("  Wall so vira problema se nao houver recompensa correspondente")
        print("  nem rota alternativa. Cheque os dois antes de chamar de bug.")
    else:
        print("  Nenhum salto de tempo por nivel acima de %.0f%%: a curva de custo"
              % ((FATOR_WALL - 1) * 100))
        print("  e a de renda estao acompanhando uma a outra.")

    if a.xp_hora_fator == 1.0:
        print("\n  ATENCAO: xp/hora foi tratado como CONSTANTE em toda a faixa.")
        print("  Quase nenhum jogo funciona assim - o jogador fica mais forte e")
        print("  troca de spot. Rode de novo com --xp-hora-fator para nao acusar")
        print("  wall que so existe na planilha.")


# --------------------------------------------------------------------------
# fontes  (redundancia: varias portas para o mesmo recurso)
# --------------------------------------------------------------------------

MARGEM_ESCOLHA_FALSA = 0.20
MARGEM_ACHATADA = 0.10


def parse_fontes(lista):
    """['nome:custo_por_unidade:unidades_por_hora', ...] -> lista de dicts."""
    fontes = []
    for bruto in lista:
        partes = [p.strip() for p in bruto.split(":")]
        if len(partes) != 3:
            raise ValueError(
                "fonte '%s' deve ter o formato nome:custo_por_unidade:"
                "unidades_por_hora (ex: 'NPC:12:99999')" % bruto)
        nome, custo, por_hora = partes
        if not nome:
            raise ValueError("fonte sem nome em '%s'" % bruto)
        try:
            custo = float(custo)
            por_hora = float(por_hora)
        except ValueError:
            raise ValueError("numeros invalidos na fonte '%s'" % nome)
        if custo < 0:
            raise ValueError("custo negativo em '%s'" % nome)
        if por_hora <= 0:
            raise ValueError(
                "'%s' precisa de unidades_por_hora > 0. Fonte instantanea: "
                "use o teto real (quantas o jogador consegue por hora)." % nome)
        fontes.append({"nome": nome, "custo_unidade": custo, "por_hora": por_hora})
    if len(fontes) < 2:
        raise ValueError("informe ao menos 2 fontes - redundancia so existe a partir de 2")
    return fontes


def _domina(a, b):
    """a domina b: nao e pior em nenhum eixo e e melhor em pelo menos um."""
    return (a["custo_unidade"] <= b["custo_unidade"]
            and a["por_hora"] >= b["por_hora"]
            and (a["custo_unidade"] < b["custo_unidade"]
                 or a["por_hora"] > b["por_hora"]))


def calc_fontes(fontes, valor_hora=None):
    for f in fontes:
        f["custo_total"] = (f["custo_unidade"] + valor_hora / f["por_hora"]
                            if valor_hora is not None else None)

    dominadas, gemeas = [], []
    for b in fontes:
        if any(_domina(a, b) for a in fontes if a is not b):
            dominadas.append(b)
    for i, a in enumerate(fontes):
        for b in fontes[i + 1:]:
            if (abs(a["custo_unidade"] - b["custo_unidade"]) < TOL
                    and abs(a["por_hora"] - b["por_hora"]) < TOL):
                gemeas.append((a["nome"], b["nome"]))
    fronteira = [f for f in fontes if f not in dominadas]

    vencedora = margem = None
    empatadas, fora_da_disputa = [], []
    if valor_hora is not None:
        ordenadas = sorted(fontes, key=lambda f: f["custo_total"])
        vencedora = ordenadas[0]
        base = vencedora["custo_total"]
        margem = (ordenadas[1]["custo_total"] / base - 1) if base > 0 else float("inf")
        for f in ordenadas:
            delta = (f["custo_total"] / base - 1) if base > 0 else 0.0
            f["delta_vs_vencedora"] = delta
            # Empatadas: o otimizador e indiferente. Nao e escolha, e repeticao.
            if delta <= MARGEM_ACHATADA:
                empatadas.append(f)
            # Fora da disputa: nao e dominada nos dois eixos, mas o custo total
            # a tira do jogo. Morre igual, so que sem aparecer na checagem de Pareto.
            elif delta > MARGEM_ESCOLHA_FALSA:
                fora_da_disputa.append(f)

    return {"fronteira": fronteira, "dominadas": dominadas, "gemeas": gemeas,
            "vencedora": vencedora, "margem": margem,
            "empatadas": empatadas, "fora_da_disputa": fora_da_disputa}


def cmd_fontes(a):
    fontes = parse_fontes(a.fonte)
    r = calc_fontes(fontes, a.valor_hora)
    recurso = a.recurso or "o recurso"

    print("FONTES CONCORRENTES DE %s" % recurso.upper())
    print(SEP)
    cab = "  %-24s %14s %12s" % ("fonte", "custo/unidade", "un/hora")
    if a.valor_hora is not None:
        cab += " %14s" % "custo total/un"
    print(cab)
    for f in fontes:
        linha = "  %-24s %14.4f %12.2f" % (f["nome"], f["custo_unidade"], f["por_hora"])
        if a.valor_hora is not None:
            linha += " %14.4f" % f["custo_total"]
        if f in r["dominadas"]:
            linha += "   <-- DOMINADA"
        print(linha)

    if a.valor_hora is not None:
        print(SEP)
        print("  valor da hora do jogador = %.2f (custo de oportunidade)" % a.valor_hora)
        print("  custo total/unidade = custo direto + (valor_hora / un_por_hora)")
        print("  VENCEDORA: %s" % r["vencedora"]["nome"])
        if r["margem"] == float("inf"):
            print("  A segunda opcao custa infinitamente mais: nao ha escolha.")
        else:
            print("  A segunda melhor custa %+.1f%%." % (r["margem"] * 100))
            if r["margem"] > MARGEM_ESCOLHA_FALSA:
                print("  ESCOLHA FALSA: acima de %.0f%% de margem o otimizador nunca"
                      % (MARGEM_ESCOLHA_FALSA * 100))
                print("  olha para as outras. As demais fontes viram decoracao.")

    print(SEP)
    if r["gemeas"]:
        print("  REDUNDANCIA PURA - fontes com os mesmos dois numeros:")
        for x, y in r["gemeas"]:
            print("    %s == %s" % (x, y))
        print("  Nao ha trade-off nenhum: e o mesmo sistema escrito duas vezes,")
        print("  com o dobro de manutencao e o dobro de coisa para o jogador aprender.")
    if r["dominadas"]:
        print("  CONTEUDO MORTO - dominadas nos DOIS eixos (mais caras E mais lentas):")
        for f in r["dominadas"]:
            print("    - %s" % f["nome"])
        print("  Nenhum jogador informado usa essas. Ou some com elas, ou de a")
        print("  cada uma algo que as outras nao tem: risco, social, AFK, acesso.")
    if len(r["empatadas"]) > 1:
        print("  REDUNDANCIA PRATICA - %d fontes dentro de %.0f%% do custo total:"
              % (len(r["empatadas"]), MARGEM_ACHATADA * 100))
        for f in r["empatadas"]:
            print("    - %-24s (%+.1f%% vs. a melhor)"
                  % (f["nome"], f["delta_vs_vencedora"] * 100))
        print("  O otimizador e indiferente entre elas: isso NAO e trade-off, e o")
        print("  mesmo sistema escrito %d vezes. O jogador aprende %d fluxos para"
              % (len(r["empatadas"]), len(r["empatadas"])))
        print("  tomar uma decisao que nao muda nada, e o time mantem %d pipelines"
              % len(r["empatadas"]))
        print("  para um recurso so. Eleja UMA como canonica e de as outras uma")
        print("  funcao diferente (teto de preco, fonte AFK, emergencia) ou apague.")
    if r["fora_da_disputa"]:
        print("  FORA DA DISPUTA - nao sao dominadas nos dois eixos, mas o custo")
        print("  total as tira do jogo (acima de %.0f%% da melhor):"
              % (MARGEM_ESCOLHA_FALSA * 100))
        for f in r["fora_da_disputa"]:
            print("    - %-24s (%+.1f%%)" % (f["nome"], f["delta_vs_vencedora"] * 100))
        print("  Morrem igual as dominadas, so que sem aparecer na checagem de")
        print("  Pareto - por isso passam despercebidas em review de planilha.")
    if not r["dominadas"] and len(r["empatadas"]) <= 1 and not r["fora_da_disputa"] \
            and len(r["fronteira"]) > 1:
        print("  FRONTEIRA LEGITIMA (%d fontes, cada uma ganha em um eixo):"
              % len(r["fronteira"]))
        for f in r["fronteira"]:
            print("    - %s" % f["nome"])
        print("  Trade-off real existe. Confirme que o jogador CONSEGUE PERCEBER")
        print("  qual usar e quando - trade-off invisivel funciona igual a nenhum.")

    print("\n  Antes de citar estes numeros, responda tres perguntas:")
    print("  1. O que esta fonte da que nenhuma outra da?")
    print("  2. Qual fonte existente morre quando esta entrar?")
    print("  3. A moeda gasta aqui e a mesma que outra fonte produz ou consome?")
    print("     Se sim, ha um circuito: ou vira arbitragem, ou mata um sink.")


# --------------------------------------------------------------------------
# loop  (escada de loops)
# --------------------------------------------------------------------------

DEGRAUS_PADRAO = ["momento", "micro", "medio", "sessao", "semana", "temporada", "vida"]

DIAGNOSTICO_DEGRAU = {
    "momento": "A acao nucleo nao entrega nada por si so. O jogo e ruim no "
               "primeiro minuto e nenhuma recompensa distante conserta isso.",
    "micro": "Sem micro-ciclo o jogo fica entediante em ~5 minutos: nada "
             "acontece entre um clique e a proxima meta.",
    "medio": "Sem ciclo medio a sessao vira um bloco unico e sem ritmo; o "
             "jogador nao tem ponto natural para respirar nem para parar.",
    "sessao": "Sem degrau de sessao o jogador desliga sem nada para mostrar. "
              "Ele nao volta amanha porque hoje nao terminou nada.",
    "semana": "Sem degrau de semana nao existe motivo para abrir o jogo na "
              "terca. E o buraco que aparece como queda de D7.",
    "temporada": "Sem temporada o jogo tem fim silencioso: o veterano some e "
                 "nao ha evento agendado que o traga de volta.",
    "vida": "Sem objetivo de vida nao existe veterano, e sem veterano nao "
            "existe ninguem para o novato querer imitar.",
}

RAZAO_MIN = 5.0
RAZAO_MAX = 30.0


def parse_degraus(texto):
    """'nome:segundos:meta,...' -> lista de dicts. duracao 0 = degrau ausente."""
    itens = []
    for bruto in texto.split(","):
        bruto = bruto.strip()
        if not bruto:
            continue
        partes = [p.strip() for p in bruto.split(":")]
        if len(partes) != 3:
            raise ValueError(
                "degrau '%s' deve ter o formato nome:segundos:meta "
                "(ex: sessao:3000:sim)" % bruto)
        nome, dur, meta = partes
        if not nome:
            raise ValueError("degrau sem nome em '%s'" % bruto)
        try:
            segundos = float(dur) if dur not in ("", "-") else 0.0
        except ValueError:
            raise ValueError(
                "duracao de '%s' deve ser em SEGUNDOS (recebido '%s'). "
                "Converta antes: 12min = 720." % (nome, dur))
        if segundos < 0:
            raise ValueError("duracao negativa em '%s'" % nome)
        meta_norm = meta.lower()
        if meta_norm not in ("sim", "nao", "s", "n", "1", "0", "true", "false"):
            raise ValueError(
                "meta de '%s' deve ser sim/nao (recebido '%s')" % (nome, meta))
        tem_meta = meta_norm in ("sim", "s", "1", "true")
        itens.append({"nome": nome, "segundos": segundos, "meta": tem_meta,
                      "presente": segundos > 0})
    if not itens:
        raise ValueError("nenhum degrau informado")
    return itens


def fmt_dur(segundos):
    if segundos <= 0:
        return "ausente"
    if segundos < 90:
        return "%.0f s" % segundos
    if segundos < 5400:
        return "%.1f min" % (segundos / 60.0)
    if segundos < 86400 * 2:
        return "%.1f h" % (segundos / 3600.0)
    return "%.1f dias" % (segundos / 86400.0)


def calc_loop(degraus, recompensas_sessao=0, sessao_min=0.0, decisoes_min=None):
    presentes = [d for d in degraus if d["presente"]]
    ausentes = [d for d in degraus if not d["presente"]]
    sem_meta = [d for d in degraus if d["presente"] and not d["meta"]]

    razoes = []
    for anterior, atual in zip(presentes, presentes[1:]):
        r = atual["segundos"] / anterior["segundos"] if anterior["segundos"] else None
        razoes.append({"de": anterior["nome"], "para": atual["nome"], "razao": r,
                       "buraco": r is not None and r > RAZAO_MAX,
                       "redundante": r is not None and r < RAZAO_MIN})

    cobertura = sum(1 for d in degraus if d["presente"] and d["meta"]) / float(len(degraus))

    densidade = None
    min_por_recompensa = None
    if recompensas_sessao and sessao_min > 0:
        densidade = recompensas_sessao / sessao_min
        min_por_recompensa = sessao_min / recompensas_sessao

    return {"presentes": presentes, "ausentes": ausentes, "sem_meta": sem_meta,
            "razoes": razoes, "cobertura": cobertura, "densidade": densidade,
            "min_por_recompensa": min_por_recompensa, "decisoes_min": decisoes_min}


def cmd_loop(a):
    degraus = parse_degraus(a.degraus)
    r = calc_loop(degraus, a.recompensas_sessao, a.sessao_min, a.decisoes_min)

    print("ESCADA DE LOOPS")
    print(SEP)
    print("  %-14s %-12s %s" % ("degrau", "T_loop", "objetivo nomeavel"))
    for d in degraus:
        marca = "sim" if d["meta"] else "NAO"
        print("  %-14s %-12s %s" % (d["nome"], fmt_dur(d["segundos"]), marca))

    print(SEP)
    print("  cobertura da escada = %d/%d degraus com objetivo nomeavel (%.0f%%)"
          % (round(r["cobertura"] * len(degraus)), len(degraus), r["cobertura"] * 100))

    if r["razoes"]:
        print(SEP)
        print("  Razao entre degraus vizinhos (saudavel: %.0fx a %.0fx)"
              % (RAZAO_MIN, RAZAO_MAX))
        for z in r["razoes"]:
            tag = ""
            if z["buraco"]:
                tag = "   <-- BURACO"
            elif z["redundante"]:
                tag = "   <-- degraus quase iguais"
            print("    %-12s -> %-12s %8.1fx%s" % (z["de"], z["para"], z["razao"], tag))

    if r["densidade"] is not None:
        print(SEP)
        print("  densidade de recompensa = %.2f por minuto (1 a cada %.1f min)"
              % (r["densidade"], r["min_por_recompensa"]))
        if r["min_por_recompensa"] > 10:
            print("  ALERTA: mais de 10 min entre recompensas. No early game o")
            print("  jogador desiste antes de descobrir que a recompensa existe.")
    if r["decisoes_min"] is not None:
        print("  decisoes com consequencia = %.2f por minuto" % r["decisoes_min"])
        if r["decisoes_min"] < 0.1:
            print("  ALERTA: praticamente nenhuma decisao. Isso e trabalho, nao jogo.")

    print(SEP)
    if r["ausentes"]:
        print("  DEGRAUS AUSENTES - cada um e uma previsao de churn na escala dele:")
        for d in r["ausentes"]:
            chave = d["nome"].lower()
            texto = None
            for k, v in DIAGNOSTICO_DEGRAU.items():
                if chave.startswith(k):
                    texto = v
                    break
            print("    - %s: %s" % (d["nome"], texto or
                  "degrau vazio: nao ha objetivo nessa escala de tempo."))
    if r["sem_meta"]:
        print("  DEGRAUS SEM OBJETIVO NOMEAVEL (existem, mas o jogador nao sabe")
        print("  dizer o que persegue neles): %s"
              % ", ".join(d["nome"] for d in r["sem_meta"]))
        print("  Costuma ser o achado mais barato do relatorio: o objetivo em")
        print("  geral existe e so nao esta na tela.")
    if not r["ausentes"] and not r["sem_meta"]:
        print("  Escada completa: todo degrau existe e tem objetivo nomeavel.")
        print("  Diga isso com a mesma firmeza com que diria o contrario.")

    print("\n  Lembrete: T_loop e o tempo ate a RECOMPENSA, nao a duracao da")
    print("  atividade. E 'objetivo nomeavel' se mede perguntando ao jogador,")
    print("  nao lendo o GDD - marca saudavel: 70% sabem responder.")


# --------------------------------------------------------------------------
# conteudo  (fabrica de conteudo)
# --------------------------------------------------------------------------

SEMANAS_POR_MES = 52.0 / 12.0


def calc_conteudo(perecivel_h, evergreen_h, consumo_semana, producao_mes):
    if consumo_semana <= 0:
        raise ValueError("consumo semanal deve ser maior que zero")
    total = perecivel_h + evergreen_h
    razao_evergreen = (evergreen_h / total) if total > 0 else None
    producao_semana = producao_mes / SEMANAS_POR_MES
    burn = consumo_semana / producao_semana if producao_semana > 0 else float("inf")
    liquido = consumo_semana - producao_semana
    if liquido > 0:
        semanas = perecivel_h / liquido
    else:
        semanas = float("inf")
    return {"total": total, "razao_evergreen": razao_evergreen,
            "producao_semana": producao_semana, "burn": burn,
            "liquido_semana": liquido, "semanas_ate_secar": semanas}


def cmd_conteudo(a):
    r = calc_conteudo(a.perecivel_horas, a.evergreen_horas,
                      a.consumo_semana, a.producao_mes)
    print("FABRICA DE CONTEUDO")
    print(SEP)
    print("  conteudo perecivel disponivel = %8.1f h" % a.perecivel_horas)
    print("  conteudo evergreen disponivel = %8.1f h" % a.evergreen_horas)
    print("  consumo do jogador            = %8.1f h/semana" % a.consumo_semana)
    print("  producao do time              = %8.1f h/mes (%.2f h/semana)"
          % (a.producao_mes, r["producao_semana"]))
    print(SEP)
    if r["razao_evergreen"] is not None:
        print("  razao evergreen = %.2f  (evergreen / total)" % r["razao_evergreen"])
        if r["razao_evergreen"] < 0.5:
            print("  ALERTA: menos da metade do conteudo se regenera. Num jogo de")
            print("  servico isso e esteira: perecivel e tempero, evergreen e comida.")
    print("  burn rate = %.2fx  (consumo / producao)" % r["burn"])
    print(SEP)
    if r["semanas_ate_secar"] == float("inf"):
        print("  A producao acompanha o consumo (liquido = %+.2f h/semana)."
              % -r["liquido_semana"])
        print("  Confira se isso vale para o p90 e nao so para o jogador medio:")
        print("  quem consome 3x a media e quem escreve a resenha.")
    else:
        print("  O jogador consome %.2f h/semana a mais do que o time produz."
              % r["liquido_semana"])
        print("  ESTOQUE PERECIVEL SECA EM %.1f SEMANAS (~%.0f dias)."
              % (r["semanas_ate_secar"], r["semanas_ate_secar"] * 7))
        print("  Depois disso a retencao depende inteiramente do evergreen:")
        print("  %.1f h de conteudo que se regenera." % a.evergreen_horas)
    print("\n  Lembrete: ganhar essa corrida no braco nunca funcionou para")
    print("  ninguem. A saida e multiplicador de conteudo (itemizacao, PvP,")
    print("  economia entre jogadores, tiers, temporada/reset), nao mais quest.")
    print("  Ver references/design-e-loop.md, secao 4.")


# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# cadeia  (gargalo em serie: varias etapas obrigatorias para um recurso)
# --------------------------------------------------------------------------

FAIXA_COEXISTENCIA = (0.60, 0.85)


def parse_elos(texto):
    """'nome:unidades_por_hora:p_parado:decisao,...' -> lista de dicts."""
    elos = []
    for bruto in texto.split(","):
        bruto = bruto.strip()
        if not bruto:
            continue
        partes = [p.strip() for p in bruto.split(":")]
        if len(partes) != 4:
            raise ValueError(
                "elo '%s' deve ter o formato nome:unidades_por_hora:p_parado:"
                "decisao (ex: 'plantio:120:0.15:nao')" % bruto)
        nome, vazao, p_parado, decisao = partes
        if not nome:
            raise ValueError("elo sem nome em '%s'" % bruto)
        try:
            vazao = float(vazao)
            p_parado = float(p_parado)
        except ValueError:
            raise ValueError("numeros invalidos no elo '%s'" % nome)
        if vazao <= 0:
            raise ValueError("elo '%s' precisa de unidades_por_hora > 0" % nome)
        if not 0.0 <= p_parado < 1.0:
            raise ValueError(
                "p_parado de '%s' deve ser FRACAO entre 0 e 1 (recebido %s). "
                "15%% = 0.15." % (nome, p_parado))
        d = decisao.lower()
        if d not in ("sim", "nao", "s", "n", "1", "0", "true", "false"):
            raise ValueError(
                "decisao de '%s' deve ser sim/nao (recebido '%s'). Sim = o elo "
                "tem escolha que muda o resultado, risco proprio OU saida com "
                "outro destino alem do proximo elo." % (nome, decisao))
        elos.append({"nome": nome, "vazao": vazao, "p_parado": p_parado,
                     "decisao": d in ("sim", "s", "1", "true")})
    if len(elos) < 2:
        raise ValueError("informe ao menos 2 elos - cadeia so existe a partir de 2")
    return elos


def calc_cadeia(elos, piso=None, manutencao_min=None, horas_semana=None,
                preco_cadeia=None, preco_teto=None):
    # Vazao de uma serie e o elo mais fraco, nunca a media: otimizar fora do
    # gargalo rende exatamente zero.
    gargalo = min(elos, key=lambda e: e["vazao"])
    vazao = gargalo["vazao"]

    disponivel = 1.0
    for e in elos:
        disponivel *= (1.0 - e["p_parado"])
    p_parada = 1.0 - disponivel

    # Referencia honesta: a mesma coisa vinda de fonte unica carregaria so a
    # ociosidade do proprio gargalo.
    p_parada_fonte_unica = gargalo["p_parado"]

    pedagios = [e for e in elos if not e["decisao"]]
    vazao_efetiva = vazao * disponivel

    ganho_prometido = ganho_efetivo = desempenho = None
    if piso is not None:
        if not 0.0 <= piso < 1.0:
            raise ValueError("--piso deve ser fracao entre 0 e 1 (55%% = 0.55)")
        ganho_prometido = 1.0 - piso
        ganho_efetivo = ganho_prometido * disponivel
        desempenho = piso + ganho_efetivo

    atencao_pct = None
    if manutencao_min is not None and horas_semana:
        atencao_pct = manutencao_min / (horas_semana * 60.0)

    razao_preco = None
    if preco_cadeia is not None and preco_teto:
        razao_preco = preco_cadeia / float(preco_teto)

    return {"vazao": vazao, "gargalo": gargalo, "disponivel": disponivel,
            "p_parada": p_parada, "p_parada_fonte_unica": p_parada_fonte_unica,
            "pedagios": pedagios, "vazao_efetiva": vazao_efetiva,
            "ganho_prometido": ganho_prometido, "ganho_efetivo": ganho_efetivo,
            "desempenho": desempenho, "atencao_pct": atencao_pct,
            "razao_preco": razao_preco}


def cmd_cadeia(a):
    elos = parse_elos(a.elos)
    r = calc_cadeia(elos, a.piso, a.manutencao_min, a.horas_semana,
                    a.preco_cadeia, a.preco_teto)
    recurso = a.recurso or "o recurso"

    print("CADEIA EM SERIE ATE %s" % recurso.upper())
    print(SEP)
    print("  %-22s %12s %10s  %s" % ("elo", "un/hora", "p_parado", "decisao?"))
    for e in elos:
        marca = "sim" if e["decisao"] else "NAO -> PEDAGIO"
        tag = "   <-- GARGALO" if e is r["gargalo"] else ""
        print("  %-22s %12.2f %9.0f%%  %s%s"
              % (e["nome"], e["vazao"], e["p_parado"] * 100, marca, tag))

    print(SEP)
    print("  vazao da cadeia = min dos elos = %.2f un/hora (%s)"
          % (r["vazao"], r["gargalo"]["nome"]))
    print("  Todo balanceamento feito fora de '%s' rende zero."
          % r["gargalo"]["nome"])

    print(SEP)
    print("  P(cadeia parada) = 1 - produto de (1 - p_i) = %.1f%%"
          % (r["p_parada"] * 100))
    print("  Fonte unica com a mesma ociosidade do gargalo: %.1f%%"
          % (r["p_parada_fonte_unica"] * 100))
    print("  Cada elo a mais SO derruba a confiabilidade; ela nunca sobe.")
    print("  vazao efetiva = vazao x disponibilidade = %.2f un/hora"
          % r["vazao_efetiva"])

    if r["desempenho"] is not None:
        print(SEP)
        print("  Piso gratuito (o que o jogador mantem sem a cadeia) = %.0f%%"
              % ((r["desempenho"] - r["ganho_efetivo"]) * 100))
        print("  A cadeia PROMETE +%.0f pts e ENTREGA +%.0f pts (a linha para "
              "%.0f%% do tempo)."
              % (r["ganho_prometido"] * 100, r["ganho_efetivo"] * 100,
                 r["p_parada"] * 100))
        print("  desempenho esperado = %.0f%% do pleno" % (r["desempenho"] * 100))
        print("  PUNICAO DUPLA: com piso gratuito o jogador nao trava - ele cai")
        print("  para o piso E ainda sai do que fazia para consertar a linha.")

    if r["atencao_pct"] is not None:
        print(SEP)
        print("  custo de atencao = %.0f min/semana = %.1f%% do tempo de jogo"
              % (a.manutencao_min, r["atencao_pct"] * 100))
        if r["ganho_efetivo"] is not None and r["ganho_efetivo"] < 0.10:
            print("  ALERTA: manutencao real para menos de 10 pts de ganho. Na")
            print("  pratica o sistema e opcional - e o jogador vai declinar.")

    if r["razao_preco"] is not None:
        lo, hi = FAIXA_COEXISTENCIA
        print(SEP)
        print("  preco da cadeia / preco do teto = %.0f%% (faixa saudavel: "
              "%.0f%%-%.0f%%)" % (r["razao_preco"] * 100, lo * 100, hi * 100))
        if r["razao_preco"] > hi:
            print("  ACIMA DA FAIXA: o desconto nao paga a manutencao. A cadeia")
            print("  vira conteudo morto e todo mundo compra do NPC.")
        elif r["razao_preco"] < lo:
            print("  ABAIXO DA FAIXA: o NPC deixa de ser teto e vira decoracao.")
            print("  Some a rede de protecao do novato e o piso do mercado.")
        else:
            print("  Dentro da faixa: as duas fontes coexistem de verdade.")

    print(SEP)
    n, p = len(elos), len(r["pedagios"])
    if p:
        print("  PEDAGIOS (%d de %d elos): %s"
              % (p, n, ", ".join(e["nome"] for e in r["pedagios"])))
        print("  Um elo passa no teste se tem escolha que muda resultado, risco")
        print("  proprio OU saida com outro destino. Estes nao tem nenhum dos 3.")
        if p >= n - 1:
            print("  VEREDITO: cadeia de %d elos com %d pedagios e uma fonte unica"
                  % (n, p))
            print("  com %d telas de espera. Colapse os pedagios em custo do elo" % p)
            print("  que sobrar: nao ha decisao nenhuma ali para o jogador perder.")
    else:
        print("  Nenhum pedagio: todo elo adiciona decisao, risco ou valor.")
        print("  A cadeia e superficie de decisao, nao atrito. Diga isso com a")
        print("  mesma firmeza com que diria o contrario - mas P(parada) segue")
        print("  valendo: alguem do outro lado tem que estar pagando por ela.")


def main():
    ap = argparse.ArgumentParser(
        description="Calculadora de auditoria de sistemas de jogo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = ap.add_subparsers(dest="cmd")

    s = sub.add_parser("severity", help="score de severidade de um problema (0-10)")
    for nome in ("impacto", "frequencia", "exploracao", "persistencia", "custo"):
        s.add_argument("--" + nome, type=float, required=True, help="0 a 10")
    s.set_defaults(func=cmd_severity)

    s = sub.add_parser("ev", help="valor esperado, variancia e tempo ate o drop")
    s.add_argument("--outcomes", required=True,
                   help="lista 'peso_ou_prob:valor'. Ex: 100:5,20:80,1:5000")
    s.add_argument("--weights", action="store_true", help="forcar leitura como pesos")
    s.add_argument("--probs", action="store_true", help="forcar leitura como probabilidades")
    s.add_argument("--per-hour", type=float, default=0, help="tentativas por hora")
    s.add_argument("--sim-sessions", type=int, default=0,
                   help="simular N sessoes e dar percentis do valor ACUMULADO")
    s.add_argument("--session-hours", type=float, default=1.0, help="duracao da sessao")
    s.add_argument("--seed", type=int, default=42)
    s.set_defaults(func=cmd_ev)

    s = sub.add_parser("netflow", help="faucet vs sink e projecao de estoque")
    s.add_argument("--faucet", type=float, required=True, help="recurso criado/h por jogador")
    s.add_argument("--sink", type=float, required=True, help="recurso destruido/h por jogador")
    s.add_argument("--players", type=int, default=1, help="jogadores ativos")
    s.add_argument("--hours-per-day", type=float, default=1.0)
    s.add_argument("--stock", type=float, default=0.0, help="estoque inicial na economia")
    s.set_defaults(func=cmd_netflow)

    s = sub.add_parser("ttk", help="DPS efetivo, TTK e breakpoints de hits")
    s.add_argument("--hp", type=float, required=True)
    s.add_argument("--hit", type=float, required=True, help="dano bruto por hit")
    s.add_argument("--reduction", type=float, default=0.0,
                   help="reducao percentual, fracao (1.0 = imunidade)")
    s.add_argument("--flat-reduction", type=float, default=0.0,
                   help="armadura subtrativa por hit, aplicada apos a percentual")
    s.add_argument("--min-damage", type=float, default=0.0,
                   help="piso de dano por hit, se o jogo tiver um")
    s.add_argument("--hits-per-sec", type=float, default=1.0)
    s.add_argument("--crit", type=float, default=0.0, help="chance de critico, fracao")
    s.add_argument("--crit-mult", type=float, default=2.0)
    s.add_argument("--uptime", type=float, default=1.0, help="fracao do tempo atacando")
    s.set_defaults(func=cmd_ttk)

    s = sub.add_parser("gacha", help="pulls esperados, pity e custo")
    s.add_argument("--p", type=float, required=True, help="chance por pull, fracao")
    s.add_argument("--pity", type=int, default=0, help="pity hard em N pulls (0 = sem pity)")
    s.add_argument("--price", type=float, default=0.0, help="preco por pull")
    s.set_defaults(func=cmd_gacha)

    s = sub.add_parser("progressao", help="curva de xp, tempo por nivel e walls")
    s.add_argument("--nivel-min", type=int, required=True)
    s.add_argument("--nivel-max", type=int, required=True)
    s.add_argument("--xp-base", type=float, required=True,
                   help="xp para sair do nivel 1 para o 2")
    s.add_argument("--modelo", default="geo", choices=("geo", "poly", "linear"),
                   help="geo: base*fator^(n-1) | poly: base*n^fator | linear: base*(1+fator*(n-1))")
    s.add_argument("--fator", type=float, default=1.15,
                   help="fator da curva (geo: 1.15 = +15%%/nivel)")
    s.add_argument("--xp-hora", type=float, required=True,
                   help="xp por hora no nivel-min")
    s.add_argument("--xp-hora-fator", type=float, default=1.0,
                   help="crescimento do xp/hora por nivel (1.10 = +10%%/nivel)")
    s.set_defaults(func=cmd_progressao)

    s = sub.add_parser("fontes", help="redundancia: fontes concorrentes do mesmo recurso")
    s.add_argument("--fonte", action="append", required=True,
                   help="repita por fonte: 'nome:custo_por_unidade:unidades_por_hora'")
    s.add_argument("--recurso", default=None, help="nome do recurso (so rotulo)")
    s.add_argument("--valor-hora", type=float, default=None,
                   help="custo de oportunidade de 1 hora, na mesma moeda do custo")
    s.set_defaults(func=cmd_fontes)

    s = sub.add_parser("loop", help="escada de loops, buracos e densidade de recompensa")
    s.add_argument("--degraus", required=True,
                   help="lista 'nome:segundos:meta'. Duracao SEMPRE em segundos; "
                        "0 = degrau ausente. Ex: momento:2:sim,sessao:3000:nao")
    s.add_argument("--recompensas-sessao", type=float, default=0,
                   help="recompensas relevantes por sessao")
    s.add_argument("--sessao-min", type=float, default=0.0,
                   help="duracao da sessao em minutos")
    s.add_argument("--decisoes-min", type=float, default=None,
                   help="decisoes com consequencia por minuto")
    s.set_defaults(func=cmd_loop)

    s = sub.add_parser("conteudo", help="razao evergreen, burn rate e data de esgotamento")
    s.add_argument("--perecivel-horas", type=float, required=True,
                   help="horas de conteudo consumido uma unica vez")
    s.add_argument("--evergreen-horas", type=float, default=0.0,
                   help="horas de conteudo que se regenera")
    s.add_argument("--consumo-semana", type=float, required=True,
                   help="horas/semana consumidas pelo jogador alvo (use o p90)")
    s.add_argument("--producao-mes", type=float, default=0.0,
                   help="horas de conteudo perecivel produzidas por mes pelo time")
    s.set_defaults(func=cmd_conteudo)

    s = sub.add_parser("cadeia", help="gargalo em serie: vazao, P(parada) e pedagios")
    s.add_argument("--elos", required=True,
                   help="lista 'nome:unidades_por_hora:p_parado:decisao'. "
                        "p_parado e FRACAO (0.15 = 15%). decisao = sim/nao. "
                        "Ex: plantio:120:0.2:nao,fazenda:80:0.15:nao")
    s.add_argument("--recurso", default=None, help="nome do recurso (so rotulo)")
    s.add_argument("--piso", type=float, default=None,
                   help="fracao do desempenho mantida SEM a cadeia (0.55 = 55%)")
    s.add_argument("--manutencao-min", type=float, default=None,
                   help="minutos de atencao por semana que a cadeia cobra")
    s.add_argument("--horas-semana", type=float, default=None,
                   help="horas jogadas por semana, para converter atencao em %")
    s.add_argument("--preco-cadeia", type=float, default=None,
                   help="custo por unidade pela cadeia")
    s.add_argument("--preco-teto", type=float, default=None,
                   help="custo por unidade pela fonte-teto (NPC de preco fixo)")
    s.set_defaults(func=cmd_cadeia)

    a = ap.parse_args()
    if not getattr(a, "func", None):
        ap.print_help()
        return 1
    try:
        a.func(a)
    except ValueError as e:
        print("erro: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
