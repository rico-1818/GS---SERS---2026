import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from assistente import CitizenAssistEnergia, extrair_ajustes  # noqa: E402
from energia_calc import avaliar, carregar_premissas, consumo_anual_kwh, payback_anos  # noqa: E402


class TestCalculos(unittest.TestCase):
    def setUp(self):
        self.p = carregar_premissas()

    def test_consumo_base_manual(self):
        # 4 pessoas x 10 min = 0,6667 h/dia x 30 = 20 h/mês; 5x5500 + 7x3200 = 49900 W.mês -> 998 kWh
        self.assertAlmostEqual(consumo_anual_kwh(self.p), 998.0, places=6)

    def test_a1_reduz_30_por_cento(self):
        r = avaliar(self.p)
        self.assertAlmostEqual(r["A1"].kwh_ano, 998 * 0.7, places=6)
        self.assertEqual(r["A1"].investimento, 0)

    def test_a2_fracao_solar(self):
        r = avaliar(self.p)
        self.assertAlmostEqual(r["A2"].kwh_ano, 998 * 0.3, places=6)

    def test_economia_horizonte_a2(self):
        # A0 = 14970; A2 = 7000 + 15*(299,4*1,00 + 100) = 12991
        r = avaliar(self.p)
        self.assertAlmostEqual(r["A0"].custo_total, 14970, places=4)
        self.assertAlmostEqual(r["A2"].custo_total, 12991, places=4)

    def test_payback_simples(self):
        # ganho/ano = 698,6 - 100 = 598,6 ; 7000/598,6 = 11,69
        self.assertAlmostEqual(avaliar(self.p)["A2"].payback, 7000 / 598.6, places=3)

    def test_payback_none_quando_ganho_negativo(self):
        p = replace(self.p, tarifa_kwh=0.1)
        self.assertIsNone(payback_anos(consumo_anual_kwh(p), consumo_anual_kwh(p, fracao_eletrica=0.3), 7000, 100, p))

    def test_co2(self):
        r = avaliar(self.p)
        self.assertAlmostEqual(r["A0"].co2_kg_ano, 998 * 0.0385, places=6)

    def test_tarifa_maior_encurta_payback(self):
        a = avaliar(replace(self.p, tarifa_kwh=1.2))["A2"].payback
        b = avaliar(self.p)["A2"].payback
        self.assertLess(a, b)


class TestAssistente(unittest.TestCase):
    def setUp(self):
        self.bot = CitizenAssistEnergia()

    def test_consumo_usa_calculo(self):
        r = self.bot.responder("Quanto meu chuveiro gasta por mês?")
        self.assertIn("83,2 kWh", r)
        self.assertIn("Limitações", r)
        self.assertIn("[R1]", r)

    def test_ajuste_do_usuario(self):
        p, aj, av = extrair_ajustes("3 pessoas, banho de 15 minutos, tarifa 0,90", self.bot.base)
        self.assertEqual((p.n_pessoas, p.duracao_banho_min, p.tarifa_kwh), (3, 15, 0.9))
        self.assertEqual(len(aj), 3)

    def test_valor_absurdo_ignorado(self):
        p, aj, av = extrair_ajustes("500 pessoas", self.bot.base)
        self.assertEqual(p.n_pessoas, 4)
        self.assertTrue(av)

    def test_comparacao_coerente_com_calculo(self):
        r = self.bot.responder("compare as alternativas")
        self.assertIn("A1", r)
        self.assertIn("Recomendação", r)
        a2 = avaliar(self.bot.base)["A2"]
        self.assertIn("11,7 anos", r)
        self.assertIsNotNone(a2.payback)

    def test_solar_nao_promete_garantia(self):
        r = self.bot.responder("vale a pena aquecedor solar?")
        self.assertIn("Nada aqui é economia garantida", r)

    def test_fora_de_escopo(self):
        r = self.bot.responder("Quanto custa uma pizza?")
        self.assertIn("Não entendi", r)

    def test_referencias(self):
        r = self.bot.responder("quais as referências?")
        for k in ("[R1]", "[R2]", "[R3]", "[R4]"):
            self.assertIn(k, r)

    def test_pre_teste_frases_informais(self):
        self.assertIn("Dica sem custo", self.bot.responder("minha conta de luz ta um absurdo, o que eu faço?"))
        self.assertIn("Impacto ambiental", self.bot.responder("chuveiro eletrico polui?"))
        self.assertIn("fotovoltaicos", self.bot.responder("painel solar compensa?"))
        self.assertIn("De nada", self.bot.responder("obrigado"))
        p, aj, _ = extrair_ajustes("tenho 2 pessoas e pago 0,75 por kwh", self.bot.base)
        self.assertEqual((p.n_pessoas, p.tarifa_kwh), (2, 0.75))


if __name__ == "__main__":
    unittest.main()
