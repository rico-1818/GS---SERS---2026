"""Cálculos de energia do Citizen Assist AI (módulo Energia).

Necessidade analisada: aquecimento de água para banho (chuveiro elétrico) em uma
residência-modelo na Grande São Paulo. Todas as premissas vêm de dados/premissas.csv.
Os valores marcados como 'estimado' são hipóteses declaradas, não medições.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, fields, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_PREMISSAS = RAIZ / "dados" / "premissas.csv"


@dataclass(frozen=True)
class Premissas:
    n_pessoas: float = 4
    banhos_dia_por_pessoa: float = 1
    duracao_banho_min: float = 10
    reducao_tempo_banho: float = 0.30
    potencia_inverno_w: float = 5500
    potencia_verao_w: float = 3200
    meses_inverno: float = 5
    dias_mes: float = 30
    tarifa_kwh: float = 1.00
    reajuste_tarifa_anual: float = 0.0
    aq_solar_investimento: float = 7000
    aq_solar_fracao_solar: float = 0.70
    aq_solar_manutencao_ano: float = 100
    aq_solar_vida_util_anos: float = 15
    horizonte_anos: int = 15
    fator_emissao_tco2_mwh: float = 0.0385


def carregar_premissas(caminho: Path = CAMINHO_PREMISSAS) -> Premissas:
    nomes = {f.name for f in fields(Premissas)}
    valores = {}
    with open(caminho, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if linha["id"] in nomes:
                valores[linha["id"]] = float(linha["valor"])
    if "horizonte_anos" in valores:
        valores["horizonte_anos"] = int(valores["horizonte_anos"])
    return Premissas(**valores)


def consumo_anual_kwh(p: Premissas, duracao_min: float | None = None,
                      fracao_eletrica: float = 1.0) -> float:
    """E = P x t. Horas de banho/dia x dias/mês x soma(potência x meses) / 1000."""
    dur = p.duracao_banho_min if duracao_min is None else duracao_min
    horas_dia = p.n_pessoas * p.banhos_dia_por_pessoa * dur / 60
    soma_w_meses = (p.meses_inverno * p.potencia_inverno_w
                    + (12 - p.meses_inverno) * p.potencia_verao_w)
    return horas_dia * p.dias_mes * soma_w_meses / 1000 * fracao_eletrica


def custo_energia_ano(kwh: float, p: Premissas, ano: int) -> float:
    return kwh * p.tarifa_kwh * (1 + p.reajuste_tarifa_anual) ** (ano - 1)


def custo_total(kwh: float, invest: float, manut: float, vida: float, p: Premissas) -> float:
    total = invest
    if invest > 0:
        total += max(0, math.ceil(p.horizonte_anos / vida) - 1) * invest  # reposições
    for ano in range(1, p.horizonte_anos + 1):
        total += custo_energia_ano(kwh, p, ano) + manut
    return total


def payback_anos(kwh_base: float, kwh_alt: float, invest: float, manut: float,
                 p: Premissas, max_anos: int = 40):
    """Payback simples (sem desconto). None se não recuperar em max_anos."""
    if invest <= 0:
        return 0.0
    acum = 0.0
    for ano in range(1, max_anos + 1):
        ganho = custo_energia_ano(kwh_base, p, ano) - custo_energia_ano(kwh_alt, p, ano) - manut
        if ganho > 0 and acum + ganho >= invest:
            return ano - 1 + (invest - acum) / ganho
        acum += ganho
    return None


@dataclass
class Resultado:
    codigo: str
    nome: str
    kwh_ano: float
    investimento: float
    manutencao_ano: float
    custo_total: float
    economia_horizonte: float
    economia_ano1: float
    payback: float | None
    co2_kg_ano: float
    co2_evitado_kg_ano: float


def avaliar(p: Premissas) -> dict[str, Resultado]:
    dur_red = p.duracao_banho_min * (1 - p.reducao_tempo_banho)
    fe = 1 - p.aq_solar_fracao_solar
    defs = [
        ("A0", "Situação atual: chuveiro elétrico", p.duracao_banho_min, 1.0, 0.0, 0.0),
        ("A1", "Eficiência: banhos mais curtos", dur_red, 1.0, 0.0, 0.0),
        ("A2", "Renovável: aquecimento solar + apoio elétrico", p.duracao_banho_min, fe,
         p.aq_solar_investimento, p.aq_solar_manutencao_ano),
        ("A3", "Combinação: banhos curtos + aquecimento solar", dur_red, fe,
         p.aq_solar_investimento, p.aq_solar_manutencao_ano),
    ]
    base_kwh = consumo_anual_kwh(p)
    base_total = custo_total(base_kwh, 0, 0, 99, p)
    res = {}
    for cod, nome, dur, frac, inv, man in defs:
        kwh = consumo_anual_kwh(p, dur, frac)
        tot = custo_total(kwh, inv, man, p.aq_solar_vida_util_anos, p)
        res[cod] = Resultado(
            cod, nome, kwh, inv, man, tot, base_total - tot,
            custo_energia_ano(base_kwh, p, 1) - custo_energia_ano(kwh, p, 1) - man,
            payback_anos(base_kwh, kwh, inv, man, p),
            kwh * p.fator_emissao_tco2_mwh, (base_kwh - kwh) * p.fator_emissao_tco2_mwh,
        )
    return res


def sensibilidade(p: Premissas, tarifas=(0.80, 1.00, 1.20), reajustes=(0.0, 0.05)):
    linhas = []
    for t in tarifas:
        for g in reajustes:
            r = avaliar(replace(p, tarifa_kwh=t, reajuste_tarifa_anual=g))
            for cod in ("A2", "A3"):
                linhas.append({"tarifa_kwh": t, "reajuste_anual": g, "alternativa": cod,
                               "payback_anos": r[cod].payback,
                               "economia_horizonte_rs": r[cod].economia_horizonte})
    return linhas


# ---------- formatação pt-BR ----------
def brl(x: float) -> str:
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def num(x: float, casas: int = 0) -> str:
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def anos_txt(x) -> str:
    return "não se paga em 40 anos" if x is None else ("imediato" if x == 0 else f"{num(x, 1)} anos")
