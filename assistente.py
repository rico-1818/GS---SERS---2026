"""Módulo Energia do Citizen Assist AI.

Assistente baseado em regras: reconhece a intenção da pergunta, recalcula os
resultados com src/energia_calc.py (nunca usa números fixos) e responde em
linguagem simples, citando referências e limitações.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

from energia_calc import Premissas, anos_txt, avaliar, brl, carregar_premissas, num

REFERENCIAS = {
    "R1": "ANEEL - reajuste tarifário anual 2026 da Enel SP (efeito médio 10,18%, vigência a partir de 4/7/2026). "
          "https://cenarioenergia.com.br/2026/06/30/aneel-aprova-reajuste-da-enel-sao-paulo-com-efeito-medio-de-1018/",
    "R2": "MCTI - fator médio de emissão do SIN em 2023: 38,5 kg CO2/MWh (noticiado pela Eixos). "
          "https://eixos.com.br/brasil-tem-menor-taxa-de-emissao-de-carbono-na-geracao-eletrica-em-onze-anos/",
    "R3": "A Gazeta - chuveiro na posição verão pode reduzir a conta em até 30%. "
          "https://www.agazeta.com.br/especiais/reportagens/chuveiro-na-posicao-verao-pode-reduzir-valor-da-conta-em-ate-30-0617",
    "R4": "Monitor do Mercado (2026) - aquecimento solar com reservatório de ~300 L: R$ 5.000 a R$ 9.000 em casa preparada. "
          "https://monitordomercado.com.br/economia-2/422211-quanto-custa-instalar-aquecimento-solar-de-agua-para-4-pessoas-em-2026-o-boiler-e-apenas-uma-parte-do-projeto/",
    "R5": "Consumidor Moderno - segundo Procel/Eletrobras, o chuveiro elétrico responde por ~7% da energia elétrica produzida no Brasil. "
          "https://consumidormoderno.com.br/energia-solar-termica-a-possivel-super-heroina-na-crise-energetica/",
    "R6": "ENTAC/ANTAC - estudo de aquecimento solar em baixa renda: retorno de ~137 meses com tarifa social. "
          "https://eventos.antac.org.br/index.php/entac/article/download/823/507/1660",
}

def limitacoes(p: Premissas) -> str:
    return (
        f"Limitações: são estimativas com premissas declaradas ({_pessoas(p.n_pessoas)}, banho de {num(p.duracao_banho_min)} min, "
        f"tarifa de referência de {brl(p.tarifa_kwh)}/kWh, {num(p.aq_solar_fracao_solar * 100)}% de fração solar, custo de instalação médio). "
        "Sua conta real, o equipamento que você tem, o clima e o orçamento de um instalador podem mudar bastante os valores. "
        "Nada aqui é economia garantida."
    )


def _pessoas(n: float) -> str:
    return "1 pessoa" if n == 1 else f"{num(n)} pessoas"


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def extrair_ajustes(texto: str, p: Premissas):
    """Lê pessoas, minutos de banho e tarifa citados na pergunta. Ignora valores absurdos."""
    t = _norm(texto)
    ajustes, avisos = {}, []

    def _f(s):
        return float(s.replace(",", "."))

    m = re.search(r"(\d+)\s*pessoas?", t)
    if m:
        v = _f(m.group(1))
        (ajustes.__setitem__("n_pessoas", v) if 1 <= v <= 20
         else avisos.append("Ignorei o número de pessoas (fora de 1 a 20)."))
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:min|minutos)", t)
    if m:
        v = _f(m.group(1))
        (ajustes.__setitem__("duracao_banho_min", v) if 1 <= v <= 60
         else avisos.append("Ignorei a duração do banho (fora de 1 a 60 min)."))
    m = (re.search(r"tarifa\D{0,15}(\d+(?:[.,]\d+)?)", t)
         or re.search(r"(\d+[.,]\d+)\s*(?:/|por|o)?\s*kwh", t))
    if m:
        v = _f(m.group(1))
        (ajustes.__setitem__("tarifa_kwh", v) if 0.1 <= v <= 5
         else avisos.append("Ignorei a tarifa (fora de R$ 0,10 a R$ 5,00 por kWh)."))
    return replace(p, **ajustes), ajustes, avisos


def _rodape(p, ajustes, avisos, refs):
    nomes = {"n_pessoas": "pessoas", "duracao_banho_min": "minutos por banho", "tarifa_kwh": "tarifa (R$/kWh)"}
    partes = []
    if ajustes:
        partes.append("Usei os valores que você informou: "
                      + ", ".join(f"{nomes[k]} = {num(v, 2) if k == 'tarifa_kwh' else num(v)}" for k, v in ajustes.items()) + ".")
    partes += avisos
    partes.append(limitacoes(p))
    partes.append("Referências: " + ", ".join(f"[{r}]" for r in refs) + " (lista completa: digite 'referências').")
    return "\n\n" + "\n".join(partes)


MENU = (
    "Olá! Sou o módulo de Energia do Citizen Assist AI. Ajudo a entender e reduzir o gasto com água quente "
    "do banho (chuveiro elétrico). Você pode perguntar, por exemplo:\n"
    "- Quanto meu chuveiro gasta por mês? (ex.: '3 pessoas, 12 minutos, tarifa 0,90')\n"
    "- Como economizar no banho?\n"
    "- Vale a pena instalar aquecedor solar?\n"
    "- Compare as alternativas.\n"
    "- E o impacto ambiental?\n"
    "- Quais são as referências e limitações?"
)


class CitizenAssistEnergia:
    def __init__(self, premissas: Premissas | None = None):
        self.base = premissas or carregar_premissas()

    def responder(self, texto: str) -> str:
        t = _norm(texto)
        if not t.strip():
            return MENU
        p, ajustes, avisos = extrair_ajustes(texto, self.base)
        r = avaliar(p)

        if re.search(r"referenc|fonte|bibliograf", t):
            linhas = [f"[{k}] {v}" for k, v in REFERENCIAS.items()]
            return ("Referências usadas (consultadas em 18/11/2026):\n" + "\n".join(linhas)
                    + "\n\nPremissas e origem de cada dado: dados/premissas.csv.\n" + limitacoes(p))
        if re.search(r"limita|garant|certeza|confi", t):
            return limitacoes(p) + "\n\nPremissas completas em dados/premissas.csv."
        if re.search(r"co2|carbono|ambient|emiss|sustent|clima|polui", t):
            a2 = r["A2"]
            return (f"Impacto ambiental (estimativa): seu chuveiro hoje consome cerca de {num(r['A0'].kwh_ano)} kWh/ano, "
                    f"o que equivale a ~{num(r['A0'].co2_kg_ano, 1)} kg de CO2/ano com o fator médio da rede brasileira "
                    f"({num(p.fator_emissao_tco2_mwh * 1000, 1)} kg CO2/MWh). O aquecimento solar evitaria ~{num(a2.co2_evitado_kg_ano, 1)} kg/ano. "
                    "É pouco porque a rede elétrica do Brasil já é majoritariamente renovável; o ganho ambiental maior é reduzir "
                    "consumo e pressão sobre a rede em horários de pico. Fabricação, instalação e descarte dos coletores também têm impacto "
                    "que não foi quantificado aqui." + _rodape(p, ajustes, avisos, ["R2", "R5"]))
        if re.search(r"compar|alternativ", t):
            return self._comparar(p, r) + _rodape(p, ajustes, avisos, ["R1", "R3", "R4", "R6"])
        if re.search(r"painel|fotovolt|placa solar", t):
            return ("Este módulo analisa o aquecimento solar de água (coletor + reservatório), que substitui o gasto elétrico do chuveiro. "
                    "Painéis fotovoltaicos (que geram eletricidade para a casa toda) não foram analisados aqui, e eu não tenho cálculo para eles. "
                    "Para saber como o aquecimento solar de água se compara, pergunte 'vale a pena aquecedor solar?'."
                    + _rodape(p, ajustes, avisos, ["R4"]))
        if re.search(r"solar|renov|aquecedor|boiler|coletor", t):
            a2 = r["A2"]
            vale = a2.payback is not None and a2.payback <= p.horizonte_anos
            return (f"Aquecimento solar (renovável) com apoio elétrico: o sol aquece a água em um reservatório e o chuveiro só complementa nos dias fracos. "
                    f"Com a hipótese de {num(p.aq_solar_fracao_solar * 100)}% da energia vindo do sol, o consumo do banho cairia de {num(r['A0'].kwh_ano)} para ~{num(a2.kwh_ano)} kWh/ano. "
                    f"Investimento estimado: {brl(a2.investimento)}; economia no 1º ano já descontando manutenção: {brl(a2.economia_ano1)}; "
                    f"retorno em ~{anos_txt(a2.payback)}. "
                    + (f"Dentro de {p.horizonte_anos} anos, no cenário informado, ele compensa (economia total de ~{brl(a2.economia_horizonte)})."
                       if vale else f"No cenário informado, ele NÃO se paga em {p.horizonte_anos} anos; só passa a compensar com mais uso de água quente, tarifa maior ou instalação mais barata.")
                    + " Exige espaço no telhado, sol sem sombra e orçamento de instalador." + _rodape(p, ajustes, avisos, ["R4", "R6"]))
        if re.search(r"economi|reduz|dica|habito|diminu|gastar menos|conta alta|absurd|conta .{0,15}(cara|alta)|o que (eu )?faco", t):
            a1 = r["A1"]
            return (f"Dica sem custo: reduzir o tempo de banho em {num(p.reducao_tempo_banho * 100)}% (de {num(p.duracao_banho_min)} para {num(p.duracao_banho_min * (1 - p.reducao_tempo_banho), 1)} min) "
                    f"poupa ~{num(r['A0'].kwh_ano - a1.kwh_ano)} kWh/ano, cerca de {brl(a1.economia_ano1)} por ano. "
                    "Use também a posição 'verão' sempre que o clima permitir (a fonte [R3] cita redução de até 30% na conta do chuveiro), "
                    "feche a torneira ao se ensaboar e confira se a fiação do chuveiro está adequada." + _rodape(p, ajustes, avisos, ["R3"]))
        if re.search(r"chuveiro|banho|kwh|energia|\bluz\b|consumo|eletric", t):
            a0 = r["A0"]
            return (f"Estimativa para {_pessoas(p.n_pessoas)} com banhos de {num(p.duracao_banho_min)} min: o chuveiro consome cerca de {num(a0.kwh_ano / 12, 1)} kWh por mês "
                    f"({num(a0.kwh_ano)} kWh/ano), o que custa em torno de {brl(a0.kwh_ano / 12 * p.tarifa_kwh)} por mês com tarifa de {brl(p.tarifa_kwh)}/kWh. "
                    f"Como calculei: energia (kWh) = potência (kW) x tempo de uso (h); usei {num(p.potencia_inverno_w)} W na posição inverno "
                    f"({num(p.meses_inverno)} meses/ano) e {num(p.potencia_verao_w)} W na posição verão. "
                    "Veja a etiqueta do seu chuveiro e a tarifa na sua conta para um valor mais próximo do real." + _rodape(p, ajustes, avisos, ["R1", "R5"]))
        if re.search(r"vale a pena|melhor|recomend", t):
            return self._comparar(p, r) + _rodape(p, ajustes, avisos, ["R1", "R3", "R4", "R6"])
        if re.search(r"\b(obrigad[oa]|valeu)\b", t):
            return "De nada! Se quiser, posso comparar as alternativas ou mostrar as referências."
        if re.search(r"\b(oi|ola|ajuda|menu|bom dia|boa tarde|boa noite)\b", t):
            return MENU
        return ("Não entendi sua pergunta e prefiro não chutar. Este módulo trata de gasto de energia no banho, formas de economizar, "
                "aquecimento solar, impacto ambiental, referências e limitações.\n\n" + MENU)

    @staticmethod
    def _comparar(p: Premissas, r) -> str:
        H = p.horizonte_anos
        linhas = [f"Comparação para o mesmo uso (banho, {_pessoas(p.n_pessoas)}), período de {H} anos, tarifa {brl(p.tarifa_kwh)}/kWh:"]
        for c in ("A0", "A1", "A2", "A3"):
            x = r[c]
            linhas.append(f"- {x.nome}: {num(x.kwh_ano)} kWh/ano; investimento {brl(x.investimento)}; custo total em {H} anos {brl(x.custo_total)}; "
                          f"economia vs. hoje {brl(x.economia_horizonte)}; retorno {anos_txt(x.payback)}; CO2 evitado {num(x.co2_evitado_kg_ano, 1)} kg/ano.")
        a1, a2, a3 = r["A1"], r["A2"], r["A3"]
        rec = [f"\nRecomendação: comece por A1 (custo zero, economia de ~{brl(a1.economia_ano1)}/ano)."]
        if a2.payback is not None and a2.payback <= H:
            melhor = "A3" if a3.economia_horizonte > a2.economia_horizonte else "A2"
            rec.append(f"O aquecimento solar compensa neste cenário (retorno em ~{anos_txt(a2.payback)}); a opção com maior economia em {H} anos é {melhor}.")
        else:
            rec.append(f"O aquecimento solar não se paga em {H} anos neste cenário ({anos_txt(a2.payback)}); só vale considerar se você usa mais água quente, "
                       "a tarifa for maior ou o orçamento for menor, ou ao reformar o telhado/instalação.")
        return "\n".join(linhas + rec)
