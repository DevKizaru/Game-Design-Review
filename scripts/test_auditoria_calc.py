#!/usr/bin/env python3
"""Testes da calculadora de auditoria.

Rode com:  python -m unittest discover -s scripts -v
       ou:  python scripts/test_auditoria_calc.py

Todo caso que falhou na auditoria da skill virou teste aqui. A regra e simples:
se um numero errado chegou a ser impresso alguma vez, ele tem um teste com nome.
"""

import math
import unittest

import auditoria_calc as ac


class TestSeverity(unittest.TestCase):

    def test_formula_bate_com_a_documentada(self):
        r = ac.calc_severity({"impacto": 10, "frequencia": 10, "exploracao": 10,
                              "persistencia": 10, "custo": 10})
        self.assertAlmostEqual(r["score"], 10.0)
        self.assertEqual(r["classe"], "CRITICO")

    def test_zero_e_aceitavel(self):
        r = ac.calc_severity({"impacto": 0, "frequencia": 0, "exploracao": 0,
                              "persistencia": 0, "custo": 0})
        self.assertAlmostEqual(r["score"], 0.0)
        self.assertEqual(r["classe"], "ACEITAVEL")

    def test_fronteiras_de_classe(self):
        # 8.5 e o piso de CRITICO; 8.49 ainda e GRAVE.
        self.assertEqual(ac.classificar(8.5), "CRITICO")
        self.assertEqual(ac.classificar(8.49), "GRAVE")
        self.assertEqual(ac.classificar(3.0), "ATENCAO")
        self.assertEqual(ac.classificar(2.99), "ACEITAVEL")

    def test_fora_da_escala_e_erro(self):
        with self.assertRaises(ValueError):
            ac.calc_severity({"impacto": 11, "frequencia": 0, "exploracao": 0,
                              "persistencia": 0, "custo": 0})
        with self.assertRaises(ValueError):
            ac.calc_severity({"impacto": -1, "frequencia": 0, "exploracao": 0,
                              "persistencia": 0, "custo": 0})


class TestOutcomesEModo(unittest.TestCase):
    """F1 da auditoria: tabela por peso produzia EV errado por 121x."""

    def test_tabela_por_peso_e_normalizada(self):
        brutos = ac.parse_outcomes("100:5,20:80,1:5000")
        norm = ac.normalize_outcomes(brutos)
        self.assertEqual(norm["modo"], "pesos")
        ev = ac.calc_ev(norm["probs"])["ev"]
        self.assertAlmostEqual(ev, 7100 / 121, places=6)   # 58.6777, nao 7100
        self.assertLess(ev, 60)

    def test_tabela_de_probabilidades_soma_1(self):
        brutos = ac.parse_outcomes("0.001:5000,0.05:120,0.949:3")
        norm = ac.normalize_outcomes(brutos)
        self.assertEqual(norm["modo"], "probabilidades")
        self.assertIsNone(norm["resto_implicito"])
        self.assertAlmostEqual(ac.calc_ev(norm["probs"])["ev"], 13.847, places=3)

    def test_tabela_incompleta_ganha_resultado_nada(self):
        # "0.001 de chance do item, resto nada" nao pode virar EV = 5000.
        brutos = ac.parse_outcomes("0.001:5000")
        norm = ac.normalize_outcomes(brutos)
        self.assertEqual(norm["modo"], "probabilidades")
        self.assertAlmostEqual(norm["resto_implicito"], 0.999)
        self.assertAlmostEqual(ac.calc_ev(norm["probs"])["ev"], 5.0)

    def test_linha_unica_ambigua_e_erro(self):
        # F6: uma linha com valor > 1 pode ser peso ou probabilidade invalida.
        with self.assertRaises(ValueError):
            ac.normalize_outcomes(ac.parse_outcomes("1.5:100"))

    def test_linha_unica_ambigua_resolvida_por_flag(self):
        norm = ac.normalize_outcomes(ac.parse_outcomes("1.5:100"), "weights")
        self.assertAlmostEqual(ac.calc_ev(norm["probs"])["ev"], 100.0)

    def test_probs_forcado_rejeita_valor_acima_de_1(self):
        with self.assertRaises(ValueError):
            ac.normalize_outcomes(ac.parse_outcomes("1.5:100"), "probs")

    def test_probs_forcado_rejeita_soma_acima_de_1(self):
        with self.assertRaises(ValueError):
            ac.normalize_outcomes(ac.parse_outcomes("0.6:10,0.6:20"), "probs")

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            ac.parse_outcomes("100")             # sem ':'
        with self.assertRaises(ValueError):
            ac.parse_outcomes("-1:100")          # peso negativo
        with self.assertRaises(ValueError):
            ac.parse_outcomes("0:100")           # soma zero
        with self.assertRaises(ValueError):
            ac.parse_outcomes("abc:100")         # nao numerico

    def test_probabilidade_soma_1_nao_e_confundida_com_peso(self):
        brutos = ac.parse_outcomes("0.5:10,0.5:20")
        self.assertEqual(ac.normalize_outcomes(brutos)["modo"], "probabilidades")


class TestEV(unittest.TestCase):

    def test_ev_variancia_e_extremos(self):
        r = ac.calc_ev([(0.5, 0.0), (0.5, 10.0)])
        self.assertAlmostEqual(r["ev"], 5.0)
        self.assertAlmostEqual(r["desvio"], 5.0)
        self.assertAlmostEqual(r["pior"], 0.0)
        self.assertAlmostEqual(r["melhor"], 10.0)

    def test_attempts_for_bate_com_a_formula_fechada(self):
        p = 0.01
        n = ac.attempts_for(p, 0.5)
        self.assertAlmostEqual(1 - (1 - p) ** n, 0.5, places=9)

    def test_attempts_for_com_certeza_e_um_pull(self):
        self.assertEqual(ac.attempts_for(1.0, 0.99), 1.0)

    def test_attempts_for_rejeita_p_invalido(self):
        for p in (0, -0.1, 1.5):
            with self.assertRaises(ValueError):
                ac.attempts_for(p, 0.5)


class TestSimulacao(unittest.TestCase):
    """F2 da auditoria: percentil de um sorteio isolado nao informava nada."""

    def test_percentis_sao_do_acumulado_da_sessao(self):
        probs = [(0.001, 5000.0), (0.999, 3.0)]
        s = ac.simulate_sessions(probs, draws_por_sessao=100, sessoes=3000, seed=7)
        # 100 sorteios a ~3 de base: a mediana tem de ficar na casa das centenas,
        # nao no valor de um unico sorteio.
        self.assertGreater(s["mediana"], 200)
        self.assertGreaterEqual(s["p90"], s["mediana"])
        self.assertGreaterEqual(s["p99"], s["p90"])

    def test_media_simulada_converge_para_o_ev(self):
        probs = [(0.5, 0.0), (0.5, 10.0)]
        s = ac.simulate_sessions(probs, draws_por_sessao=50, sessoes=4000, seed=1)
        self.assertAlmostEqual(s["media"], 250.0, delta=8.0)   # 50 * EV(5)

    def test_deterministico_com_a_mesma_seed(self):
        probs = [(0.3, 1.0), (0.7, 9.0)]
        a = ac.simulate_sessions(probs, 20, 200, seed=99)
        b = ac.simulate_sessions(probs, 20, 200, seed=99)
        self.assertEqual(a, b)


class TestNetflow(unittest.TestCase):

    def test_projecao_agregada(self):
        r = ac.calc_netflow(1200, 350, players=500, hours_per_day=3, stock=5_000_000)
        self.assertAlmostEqual(r["net_h"], 850)
        self.assertAlmostEqual(r["net_dia_total"], 1_275_000)
        self.assertAlmostEqual(r["projecao"][90], 5_000_000 + 1_275_000 * 90)
        self.assertEqual(r["estado"], "inflacionaria")

    def test_economia_zerada_nao_e_equilibrio(self):
        # F6: faucet=0 e sink=0 era descrito como "sinks acompanham os faucets".
        self.assertEqual(ac.calc_netflow(0, 0, 1, 1)["estado"], "economia_inexistente")

    def test_so_sink(self):
        self.assertEqual(ac.calc_netflow(0, 100, 1, 1)["estado"], "so_sink")

    def test_equilibrio_exato_e_deflacao(self):
        self.assertEqual(ac.calc_netflow(100, 100, 1, 1)["estado"], "equilibrio_exato")
        self.assertEqual(ac.calc_netflow(100, 150, 1, 1)["estado"], "deflacionaria")

    def test_absorcao_alta_nao_dispara_alerta(self):
        r = ac.calc_netflow(100, 80, 1, 1)
        self.assertEqual(r["estado"], "positiva_controlada")
        self.assertAlmostEqual(r["absorcao"], 0.8)


class TestTTK(unittest.TestCase):

    def test_reducao_percentual_equivale_ao_hp_efetivo(self):
        r = ac.calc_ttk(hp=5000, hit=260, reduction=0.35)
        # HP efetivo 5000/0.65 = 7692.31 com dano 260 -> mesmos 30 hits
        self.assertEqual(r["hits"], math.ceil(5000 / (260 * 0.65)))
        self.assertAlmostEqual(r["dano_medio"], 169.0)

    def test_reducao_plana_aplicada_depois_da_percentual(self):
        # F4: armadura subtrativa nao existia.
        r = ac.calc_ttk(hp=1000, hit=100, reduction=0.30, flat=20)
        self.assertAlmostEqual(r["dano_pos_pct"], 70.0)
        self.assertAlmostEqual(r["dano_mitigado"], 50.0)   # 70 - 20, nao 56
        self.assertEqual(r["hits"], 20)

    def test_reducao_plana_maior_que_o_hit_zera_dano(self):
        r = ac.calc_ttk(hp=1000, hit=10, flat=50)
        self.assertTrue(r["imune"])
        self.assertEqual(r["ttk"], float("inf"))

    def test_piso_de_dano_impede_imunidade(self):
        r = ac.calc_ttk(hp=1000, hit=10, flat=50, min_damage=1)
        self.assertFalse(r["imune"])
        self.assertAlmostEqual(r["dano_medio"], 1.0)
        self.assertEqual(r["hits"], 1000)

    def test_imunidade_total_e_caso_valido_nao_erro(self):
        # F6: --reduction 1.0 era rejeitado como erro de entrada.
        r = ac.calc_ttk(hp=100, hit=10, reduction=1.0)
        self.assertTrue(r["imune"])
        self.assertEqual(r["ttk"], float("inf"))

    def test_critico_entra_no_dano_medio(self):
        r = ac.calc_ttk(hp=1000, hit=100, crit=0.5, crit_mult=2.0)
        self.assertAlmostEqual(r["dano_medio"], 150.0)

    def test_uptime_reduz_dps_mas_nao_o_numero_de_hits(self):
        cheio = ac.calc_ttk(hp=1000, hit=100, hits_per_sec=1.0, uptime=1.0)
        meio = ac.calc_ttk(hp=1000, hit=100, hits_per_sec=1.0, uptime=0.5)
        self.assertEqual(cheio["hits"], meio["hits"])
        self.assertAlmostEqual(meio["ttk"], cheio["ttk"] * 2)

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            ac.calc_ttk(hp=0, hit=10)
        with self.assertRaises(ValueError):
            ac.calc_ttk(hp=100, hit=-1)
        with self.assertRaises(ValueError):
            ac.calc_ttk(hp=100, hit=10, reduction=1.5)
        with self.assertRaises(ValueError):
            ac.calc_ttk(hp=100, hit=10, crit=1.5)
        with self.assertRaises(ValueError):
            ac.calc_ttk(hp=100, hit=10, uptime=0)


class TestGacha(unittest.TestCase):

    def test_esperado_com_pity_bate_com_a_soma_direta(self):
        p, pity = 0.006, 90
        r = ac.calc_gacha(p, pity)
        direto = sum(k * p * (1 - p) ** (k - 1) for k in range(1, pity + 1))
        direto += pity * (1 - p) ** pity
        self.assertAlmostEqual(r["esperado"], direto, places=9)

    def test_pity_reduz_o_esperado_e_da_teto(self):
        r = ac.calc_gacha(0.006, 90)
        self.assertLess(r["esperado"], 1 / 0.006)
        self.assertEqual(r["pior_caso"], 90)

    def test_custo_medio_respeita_o_teto_do_pity(self):
        # Antes, custo medio (416) ficava acima do custo maximo (225).
        r = ac.calc_gacha(0.006, pity=90, price=2.5)
        self.assertLessEqual(r["custo_medio"], r["custo_max"])
        self.assertLessEqual(r["custo_p90"], r["custo_max"])

    def test_sem_pity_reporta_p99_e_nao_tem_teto(self):
        r = ac.calc_gacha(0.006, price=2.5)
        self.assertIsNone(r["custo_max"])
        self.assertGreater(r["custo_p99"], r["custo_p90"])

    def test_p_igual_a_1_nao_estoura(self):
        r = ac.calc_gacha(1.0)
        self.assertAlmostEqual(r["media_pulls"], 1.0)
        self.assertEqual(r["pulls_alvo"][0.99], 1.0)

    def test_p_invalido(self):
        for p in (0, -0.1, 1.5):
            with self.assertRaises(ValueError):
                ac.calc_gacha(p)
        with self.assertRaises(ValueError):
            ac.calc_gacha(0.5, pity=-1)


class TestProgressao(unittest.TestCase):

    def test_modelo_geometrico_bate_com_a_formula(self):
        self.assertAlmostEqual(ac.xp_do_nivel(1, 100, "geo", 1.2), 100)
        self.assertAlmostEqual(ac.xp_do_nivel(3, 100, "geo", 1.2), 144)

    def test_modelo_polinomial_e_linear(self):
        self.assertAlmostEqual(ac.xp_do_nivel(3, 100, "poly", 2), 900)
        self.assertAlmostEqual(ac.xp_do_nivel(3, 100, "linear", 0.5), 200)

    def test_modelo_invalido(self):
        with self.assertRaises(ValueError):
            ac.xp_do_nivel(1, 100, "exponencial-magica", 2)

    def test_tempo_total_soma_os_niveis(self):
        r = ac.calc_progressao(1, 4, base=100, modelo="geo", fator=2, xp_hora=100)
        # niveis 1,2,3 custam 100, 200, 400 -> 1h + 2h + 4h
        self.assertAlmostEqual(r["total_horas"], 7.0)
        self.assertEqual(len(r["niveis"]), 3)

    def test_renda_crescendo_junto_com_o_custo_nao_gera_wall(self):
        # Custo dobra por nivel e xp/h dobra junto: tempo por nivel constante.
        r = ac.calc_progressao(1, 10, base=100, modelo="geo", fator=2,
                               xp_hora=100, xp_hora_fator=2)
        self.assertEqual(r["walls"], [])
        horas = [x["horas"] for x in r["niveis"]]
        self.assertAlmostEqual(min(horas), max(horas))

    def test_custo_crescendo_mais_rapido_que_a_renda_gera_wall(self):
        r = ac.calc_progressao(1, 10, base=100, modelo="geo", fator=2,
                               xp_hora=100, xp_hora_fator=1.0)
        self.assertTrue(r["walls"])
        self.assertAlmostEqual(r["walls"][0]["razao"], 2.0)

    def test_cauda_concentra_tempo_em_curva_explosiva(self):
        r = ac.calc_progressao(1, 51, base=100, modelo="geo", fator=1.5,
                               xp_hora=100)
        self.assertGreater(r["fracao_cauda"], 0.5)

    def test_nivel_da_metade_do_tempo(self):
        r = ac.calc_progressao(1, 5, base=100, modelo="geo", fator=2, xp_hora=100)
        # 1h, 2h, 4h, 8h = 15h; metade (7.5h) cai dentro do nivel 4
        self.assertEqual(r["nivel_da_metade"], 4)

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            ac.calc_progressao(0, 10, base=100, xp_hora=100)
        with self.assertRaises(ValueError):
            ac.calc_progressao(10, 10, base=100, xp_hora=100)
        with self.assertRaises(ValueError):
            ac.calc_progressao(1, 10, base=0, xp_hora=100)
        with self.assertRaises(ValueError):
            ac.calc_progressao(1, 10, base=100, xp_hora=0)


class TestFontes(unittest.TestCase):

    def f(self, *specs):
        return ac.parse_fontes(list(specs))

    def test_uma_fonte_so_nao_e_redundancia(self):
        with self.assertRaises(ValueError):
            ac.parse_fontes(["farm:10:100"])

    def test_por_hora_zero_e_erro_com_orientacao(self):
        with self.assertRaises(ValueError) as ctx:
            ac.parse_fontes(["NPC:10:0", "farm:20:50"])
        self.assertIn("teto real", str(ctx.exception))

    def test_dominada_nos_dois_eixos_e_conteudo_morto(self):
        r = ac.calc_fontes(self.f("NPC:12:600", "ilha:20:40"))
        self.assertEqual([d["nome"] for d in r["dominadas"]], ["ilha"])

    def test_mais_barata_porem_mais_lenta_nao_e_dominada(self):
        # Trade-off legitimo: cada uma ganha em um eixo.
        r = ac.calc_fontes(self.f("ilha:0:40", "NPC:60:600"))
        self.assertEqual(r["dominadas"], [])
        self.assertEqual(len(r["fronteira"]), 2)

    def test_fontes_identicas_sao_redundancia_pura(self):
        r = ac.calc_fontes(self.f("base:35:120", "ilha:35:120"))
        self.assertEqual(r["gemeas"], [("base", "ilha")])

    def test_custo_total_soma_o_custo_de_oportunidade_da_hora(self):
        r = ac.calc_fontes(self.f("base:35:120", "NPC:60:600"), valor_hora=4000)
        base = [f for f in r["fronteira"] if f["nome"] == "base"][0]
        self.assertAlmostEqual(base["custo_total"], 35 + 4000 / 120.0)

    def test_empate_em_custo_total_e_redundancia_pratica(self):
        # Ninguem domina ninguem, mas o otimizador e indiferente:
        # e o caso que passa batido numa checagem de Pareto pura.
        r = ac.calc_fontes(self.f("base:35:120", "ilha:0:40", "NPC:60:600"),
                           valor_hora=4000)
        self.assertEqual(r["dominadas"], [])
        self.assertEqual(sorted(f["nome"] for f in r["empatadas"]), ["NPC", "base"])
        self.assertEqual([f["nome"] for f in r["fora_da_disputa"]], ["ilha"])

    def test_sem_valor_hora_nao_inventa_vencedora(self):
        r = ac.calc_fontes(self.f("base:35:120", "NPC:60:600"))
        self.assertIsNone(r["vencedora"])
        self.assertEqual(r["empatadas"], [])
        self.assertEqual(r["fora_da_disputa"], [])

    def test_escolha_falsa_quando_a_margem_estoura(self):
        r = ac.calc_fontes(self.f("boa:10:1000", "ruim:100:1000"), valor_hora=100)
        self.assertGreater(r["margem"], ac.MARGEM_ESCOLHA_FALSA)
        self.assertEqual(r["vencedora"]["nome"], "boa")

    def test_formato_invalido(self):
        for spec in ("base:35", "base:x:120", "base:-5:120", ":35:120"):
            with self.assertRaises(ValueError):
                ac.parse_fontes([spec, "outra:10:10"])


class TestParseDegraus(unittest.TestCase):

    def test_duracao_zero_marca_degrau_ausente(self):
        d = ac.parse_degraus("semana:0:nao")
        self.assertFalse(d[0]["presente"])
        self.assertFalse(d[0]["meta"])

    def test_traco_e_vazio_tambem_sao_ausencia(self):
        for txt in ("semana:-:nao", "semana::nao"):
            self.assertFalse(ac.parse_degraus(txt)[0]["presente"])

    def test_duracao_com_unidade_e_erro_explicito(self):
        # '12m' seria lido como 12 segundos por um parser descuidado: 60x errado.
        with self.assertRaises(ValueError) as ctx:
            ac.parse_degraus("medio:12m:sim")
        self.assertIn("SEGUNDOS", str(ctx.exception))

    def test_formato_invalido(self):
        for txt in ("sessao:3000", "sessao:3000:talvez", ":10:sim", ""):
            with self.assertRaises(ValueError):
                ac.parse_degraus(txt)


class TestLoop(unittest.TestCase):

    ESCADA = ("momento:2:sim,micro:45:sim,medio:720:nao,sessao:3000:sim,"
              "semana:0:nao,temporada:0:nao,vida:0:sim")

    def test_cobertura_conta_so_degrau_presente_com_meta(self):
        r = ac.calc_loop(ac.parse_degraus(self.ESCADA))
        # vida tem meta declarada mas nao existe: nao pode contar como coberto.
        self.assertAlmostEqual(r["cobertura"], 3 / 7.0)
        self.assertEqual([d["nome"] for d in r["ausentes"]],
                         ["semana", "temporada", "vida"])
        self.assertEqual([d["nome"] for d in r["sem_meta"]], ["medio"])

    def test_razoes_ignoram_degraus_ausentes(self):
        r = ac.calc_loop(ac.parse_degraus(self.ESCADA))
        self.assertEqual(len(r["razoes"]), 3)
        self.assertAlmostEqual(r["razoes"][0]["razao"], 22.5)

    def test_buraco_entre_degraus_e_sinalizado(self):
        r = ac.calc_loop(ac.parse_degraus("micro:60:sim,sessao:21600:sim"))
        self.assertTrue(r["razoes"][0]["buraco"])

    def test_degraus_quase_iguais_sao_sinalizados(self):
        r = ac.calc_loop(ac.parse_degraus("medio:720:sim,sessao:3000:sim"))
        self.assertTrue(r["razoes"][0]["redundante"])

    def test_densidade_de_recompensa(self):
        r = ac.calc_loop(ac.parse_degraus("sessao:3000:sim"),
                         recompensas_sessao=6, sessao_min=50)
        self.assertAlmostEqual(r["densidade"], 0.12)
        self.assertAlmostEqual(r["min_por_recompensa"], 50 / 6.0)

    def test_sem_dados_de_sessao_nao_inventa_densidade(self):
        r = ac.calc_loop(ac.parse_degraus("sessao:3000:sim"))
        self.assertIsNone(r["densidade"])

    def test_escada_completa_nao_reporta_falso_positivo(self):
        r = ac.calc_loop(ac.parse_degraus(
            "momento:2:sim,micro:45:sim,medio:900:sim,sessao:3600:sim,"
            "semana:86400:sim,temporada:2592000:sim,vida:31536000:sim"))
        self.assertEqual(r["ausentes"], [])
        self.assertEqual(r["sem_meta"], [])
        self.assertAlmostEqual(r["cobertura"], 1.0)


class TestConteudo(unittest.TestCase):

    def test_producao_mensal_vira_semanal_por_52_12(self):
        r = ac.calc_conteudo(40, 12, consumo_semana=25, producao_mes=6)
        # 6 h/mes = 1.3846 h/semana, nao 1.5: o mes tem 4.345 semanas.
        self.assertAlmostEqual(r["producao_semana"], 6 / (52 / 12.0))
        self.assertAlmostEqual(r["burn"], 25 / (6 / (52 / 12.0)))

    def test_esgotamento_desconta_a_producao_do_consumo(self):
        r = ac.calc_conteudo(40, 12, consumo_semana=25, producao_mes=6)
        liquido = 25 - 6 / (52 / 12.0)
        self.assertAlmostEqual(r["semanas_ate_secar"], 40 / liquido)

    def test_producao_maior_que_consumo_nao_seca(self):
        r = ac.calc_conteudo(40, 120, consumo_semana=4, producao_mes=30)
        self.assertEqual(r["semanas_ate_secar"], float("inf"))
        self.assertLess(r["burn"], 1.0)

    def test_sem_producao_burn_infinito_mas_data_finita(self):
        r = ac.calc_conteudo(20, 0, consumo_semana=10, producao_mes=0)
        self.assertEqual(r["burn"], float("inf"))
        self.assertAlmostEqual(r["semanas_ate_secar"], 2.0)

    def test_razao_evergreen(self):
        r = ac.calc_conteudo(40, 120, consumo_semana=4, producao_mes=30)
        self.assertAlmostEqual(r["razao_evergreen"], 0.75)

    def test_consumo_zero_e_erro(self):
        with self.assertRaises(ValueError):
            ac.calc_conteudo(40, 12, consumo_semana=0, producao_mes=6)


class TestParseElos(unittest.TestCase):

    def test_formato_completo(self):
        elos = ac.parse_elos("plantio:120:0.2:nao,cozinha:200:0.1:sim")
        self.assertEqual(len(elos), 2)
        self.assertEqual(elos[0]["nome"], "plantio")
        self.assertAlmostEqual(elos[0]["p_parado"], 0.2)
        self.assertFalse(elos[0]["decisao"])
        self.assertTrue(elos[1]["decisao"])

    def test_percentual_em_vez_de_fracao_e_recusado(self):
        # 15 em vez de 0.15 e o erro obvio; a mensagem tem que ensinar.
        with self.assertRaises(ValueError) as ctx:
            ac.parse_elos("a:10:15:nao,b:10:0.1:nao")
        self.assertIn("FRACAO", str(ctx.exception))

    def test_um_elo_so_nao_e_cadeia(self):
        with self.assertRaises(ValueError):
            ac.parse_elos("a:10:0.1:nao")

    def test_decisao_invalida_explica_o_teste(self):
        with self.assertRaises(ValueError) as ctx:
            ac.parse_elos("a:10:0.1:talvez,b:10:0.1:nao")
        self.assertIn("risco proprio", str(ctx.exception))

    def test_campos_faltando(self):
        with self.assertRaises(ValueError):
            ac.parse_elos("a:10:0.1,b:10:0.1:nao")


class TestCadeia(unittest.TestCase):

    def test_vazao_e_o_minimo_nao_a_media(self):
        elos = ac.parse_elos("a:120:0:sim,b:90:0:sim,c:200:0:sim")
        r = ac.calc_cadeia(elos)
        self.assertAlmostEqual(r["vazao"], 90.0)
        self.assertEqual(r["gargalo"]["nome"], "b")

    def test_falha_em_serie_tres_elos_a_15pct(self):
        # 1 - 0.85^3 = 0.385875 -> o numero citado na secao 11 e no SKILL.md
        elos = ac.parse_elos("a:10:0.15:sim,b:10:0.15:sim,c:10:0.15:sim")
        r = ac.calc_cadeia(elos)
        self.assertAlmostEqual(r["p_parada"], 0.385875)
        self.assertAlmostEqual(r["p_parada_fonte_unica"], 0.15)

    def test_confiabilidade_nunca_sobe_com_mais_elos(self):
        curta = ac.calc_cadeia(ac.parse_elos("a:10:0.1:sim,b:10:0.1:sim"))
        longa = ac.calc_cadeia(
            ac.parse_elos("a:10:0.1:sim,b:10:0.1:sim,c:10:0.05:sim"))
        self.assertGreater(longa["p_parada"], curta["p_parada"])

    def test_elo_perfeito_nao_muda_a_confiabilidade(self):
        r = ac.calc_cadeia(ac.parse_elos("a:10:0.2:sim,b:99:0:sim"))
        self.assertAlmostEqual(r["p_parada"], 0.2)

    def test_vazao_efetiva_desconta_a_parada(self):
        r = ac.calc_cadeia(ac.parse_elos("a:100:0.2:sim,b:100:0:sim"))
        self.assertAlmostEqual(r["vazao_efetiva"], 80.0)

    def test_pedagios_sao_os_elos_sem_decisao(self):
        r = ac.calc_cadeia(
            ac.parse_elos("a:10:0:nao,b:10:0:nao,c:10:0:sim"))
        self.assertEqual([e["nome"] for e in r["pedagios"]], ["a", "b"])

    def test_cadeia_toda_de_decisao_nao_tem_pedagio(self):
        r = ac.calc_cadeia(ac.parse_elos("a:10:0:sim,b:10:0:sim"))
        self.assertEqual(r["pedagios"], [])

    def test_piso_gratuito_promete_mais_do_que_entrega(self):
        # o achado: a cadeia parada nao trava o jogo, ela so entrega menos
        elos = ac.parse_elos("a:10:0.15:nao,b:10:0.15:nao,c:10:0.15:sim")
        r = ac.calc_cadeia(elos, piso=0.55)
        self.assertAlmostEqual(r["ganho_prometido"], 0.45)
        self.assertAlmostEqual(r["ganho_efetivo"], 0.45 * 0.614125)
        self.assertLess(r["ganho_efetivo"], r["ganho_prometido"])
        self.assertAlmostEqual(r["desempenho"], 0.55 + r["ganho_efetivo"])

    def test_piso_em_percentual_e_recusado(self):
        with self.assertRaises(ValueError):
            ac.calc_cadeia(ac.parse_elos("a:10:0:sim,b:10:0:sim"), piso=55)

    def test_sem_piso_nao_inventa_desempenho(self):
        r = ac.calc_cadeia(ac.parse_elos("a:10:0:sim,b:10:0:sim"))
        self.assertIsNone(r["desempenho"])
        self.assertIsNone(r["ganho_efetivo"])

    def test_atencao_vira_fracao_do_tempo_de_jogo(self):
        r = ac.calc_cadeia(ac.parse_elos("a:10:0:sim,b:10:0:sim"),
                           manutencao_min=42.0, horas_semana=14.0)
        self.assertAlmostEqual(r["atencao_pct"], 42.0 / 840.0)

    def test_faixa_de_coexistencia(self):
        elos = ac.parse_elos("a:10:0:sim,b:10:0:sim")
        acima = ac.calc_cadeia(elos, preco_cadeia=55, preco_teto=60)
        dentro = ac.calc_cadeia(elos, preco_cadeia=42, preco_teto=60)
        abaixo = ac.calc_cadeia(elos, preco_cadeia=20, preco_teto=60)
        lo, hi = ac.FAIXA_COEXISTENCIA
        self.assertGreater(acima["razao_preco"], hi)
        self.assertTrue(lo <= dentro["razao_preco"] <= hi)
        self.assertLess(abaixo["razao_preco"], lo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
