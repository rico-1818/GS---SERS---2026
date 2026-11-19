"""Gera resultados/comparacao.csv, resultados/sensibilidade.csv e docs/CALCULOS_E_COMPARACAO.md
a partir de dados/premissas.csv. Rode: python src/gerar_resultados.py"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from energia_calc import RAIZ, anos_txt, avaliar, brl, carregar_premissas, consumo_anual_kwh, num, sensibilidade  # noqa: E402


def main():
    p = carregar_premissas()
    r = avaliar(p)
    with open(RAIZ / "resultados" / "comparacao.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["alternativa", "nome", "kwh_ano", "investimento_rs", "manutencao_ano_rs", "custo_total_rs",
                    "economia_horizonte_rs", "economia_ano1_rs", "payback_anos", "co2_kg_ano", "co2_evitado_kg_ano"])
        for x in r.values():
            w.writerow([x.codigo, x.nome, round(x.kwh_ano, 1), x.investimento, x.manutencao_ano, round(x.custo_total, 2),
                        round(x.economia_horizonte, 2), round(x.economia_ano1, 2),
                        "" if x.payback is None else round(x.payback, 1), round(x.co2_kg_ano, 1), round(x.co2_evitado_kg_ano, 1)])
    sens = sensibilidade(p)
    with open(RAIZ / "resultados" / "sensibilidade.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tarifa_kwh", "reajuste_anual", "alternativa", "payback_anos", "economia_horizonte_rs"])
        for s in sens:
            w.writerow([s["tarifa_kwh"], s["reajuste_anual"], s["alternativa"],
                        "" if s["payback_anos"] is None else round(s["payback_anos"], 1), round(s["economia_horizonte_rs"], 2)])

    H = p.horizonte_anos
    horas = p.n_pessoas * p.banhos_dia_por_pessoa * p.duracao_banho_min / 60
    md = [
        "# Cálculos e comparação das alternativas",
        "",
        "> Arquivo gerado por `python src/gerar_resultados.py`. Não edite à mão: altere `dados/premissas.csv` e gere de novo.",
        "",
        "## 1. Necessidade e período de referência",
        f"Aquecimento de água para banho em uma residência-modelo ({num(p.n_pessoas)} pessoas) na Grande São Paulo, "
        f"comparado em um período comum de **{H} anos** (igual à vida útil assumida do sistema solar, sem valor residual).",
        "",
        "## 2. Consumo atual (A0)",
        "Energia = potência × tempo. Fórmula usada em `consumo_anual_kwh`:",
        "",
        "`kWh/ano = (pessoas × banhos/dia × minutos/60) × dias/mês × [meses_inverno × P_inverno + (12 − meses_inverno) × P_verão] / 1000`",
        "",
        f"- Tempo de banho: {num(p.n_pessoas)} × {num(p.banhos_dia_por_pessoa)} × {num(p.duracao_banho_min)} / 60 = {num(horas, 2)} h/dia",
        f"- Soma potência×meses: {num(p.meses_inverno)}×{num(p.potencia_inverno_w)} + {num(12 - p.meses_inverno)}×{num(p.potencia_verao_w)} = "
        f"{num(p.meses_inverno * p.potencia_inverno_w + (12 - p.meses_inverno) * p.potencia_verao_w)} W·mês",
        f"- Resultado: **{num(consumo_anual_kwh(p), 1)} kWh/ano** ({num(consumo_anual_kwh(p) / 12, 1)} kWh/mês) ≈ {brl(consumo_anual_kwh(p) * p.tarifa_kwh)}/ano a {brl(p.tarifa_kwh)}/kWh",
        "",
        "## 3. Alternativas",
        "- **A0** situação atual (referência)",
        f"- **A1** eficiência: reduzir o tempo de banho em {num(p.reducao_tempo_banho * 100)}% (custo zero)",
        f"- **A2** fonte renovável: aquecimento solar com apoio elétrico, {num(p.aq_solar_fracao_solar * 100)}% de fração solar, {brl(p.aq_solar_investimento)} de investimento",
        "- **A3** combinação de A1 e A2",
        "",
        f"## 4. Resultados (tarifa {brl(p.tarifa_kwh)}/kWh, reajuste {num(p.reajuste_tarifa_anual * 100)}%/ano)",
        "",
        f"| Alternativa | kWh/ano | Investimento | Custo total em {H} anos | Economia vs. A0 | Retorno | CO2 evitado (kg/ano) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for x in r.values():
        md.append(f"| {x.codigo} – {x.nome} | {num(x.kwh_ano)} | {brl(x.investimento)} | {brl(x.custo_total)} | {brl(x.economia_horizonte)} | {anos_txt(x.payback)} | {num(x.co2_evitado_kg_ano, 1)} |")
    md += [
        "",
        "Custo total = investimento + reposições + Σ(energia + manutenção) no período. Retorno = payback simples (sem desconto).",
        f"CO2 = kWh × {num(p.fator_emissao_tco2_mwh * 1000, 1)} kg/MWh ÷ 1000 (fator médio do SIN, MCTI 2023 [R2]).",
        "",
        "## 5. Sensibilidade (A2 e A3)",
        "",
        "| Tarifa (R$/kWh) | Reajuste/ano | Alt. | Retorno | Economia em " + f"{H} anos |",
        "|---:|---:|---|---:|---:|",
    ]
    for s in sens:
        md.append(f"| {num(s['tarifa_kwh'], 2)} | {num(s['reajuste_anual'] * 100)}% | {s['alternativa']} | {anos_txt(s['payback_anos'])} | {brl(s['economia_horizonte_rs'])} |")
    md += [
        "",
        "## 6. Como ler os resultados e limitações",
        "- A1 não exige investimento e é a primeira medida em qualquer cenário testado.",
        "- A viabilidade de A2 depende fortemente da tarifa, do reajuste e do orçamento real; veja a tabela de sensibilidade.",
        "- O ganho em CO2 é pequeno porque a matriz elétrica brasileira já tem fator de emissão baixo.",
        "- Dados marcados como `estimado` em `dados/premissas.csv` são hipóteses do grupo, não medições. Estimativas não são resultados garantidos.",
        "- Não foram considerados: valor residual, taxa de desconto, tarifa social, tarifa branca, financiamento, queda de rendimento dos coletores.",
        "",
    ]
    (RAIZ / "docs" / "CALCULOS_E_COMPARACAO.md").write_text("\n".join(md), encoding="utf-8")
    print("Gerado: resultados/comparacao.csv, resultados/sensibilidade.csv, docs/CALCULOS_E_COMPARACAO.md")


if __name__ == "__main__":
    main()
