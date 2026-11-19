# Cálculos e comparação das alternativas

> Arquivo gerado por `python src/gerar_resultados.py`. Não edite à mão: altere `dados/premissas.csv` e gere de novo.

## 1. Necessidade e período de referência
Aquecimento de água para banho em uma residência-modelo (4 pessoas) na Grande São Paulo, comparado em um período comum de **15 anos** (igual à vida útil assumida do sistema solar, sem valor residual).

## 2. Consumo atual (A0)
Energia = potência × tempo. Fórmula usada em `consumo_anual_kwh`:

`kWh/ano = (pessoas × banhos/dia × minutos/60) × dias/mês × [meses_inverno × P_inverno + (12 − meses_inverno) × P_verão] / 1000`

- Tempo de banho: 4 × 1 × 10 / 60 = 0,67 h/dia
- Soma potência×meses: 5×5.500 + 7×3.200 = 49.900 W·mês
- Resultado: **998,0 kWh/ano** (83,2 kWh/mês) ≈ R$ 998,00/ano a R$ 1,00/kWh

## 3. Alternativas
- **A0** situação atual (referência)
- **A1** eficiência: reduzir o tempo de banho em 30% (custo zero)
- **A2** fonte renovável: aquecimento solar com apoio elétrico, 70% de fração solar, R$ 7.000,00 de investimento
- **A3** combinação de A1 e A2

## 4. Resultados (tarifa R$ 1,00/kWh, reajuste 0%/ano)

| Alternativa | kWh/ano | Investimento | Custo total em 15 anos | Economia vs. A0 | Retorno | CO2 evitado (kg/ano) |
|---|---:|---:|---:|---:|---:|---:|
| A0 – Situação atual: chuveiro elétrico | 998 | R$ 0,00 | R$ 14.970,00 | R$ 0,00 | imediato | 0,0 |
| A1 – Eficiência: banhos mais curtos | 699 | R$ 0,00 | R$ 10.479,00 | R$ 4.491,00 | imediato | 11,5 |
| A2 – Renovável: aquecimento solar + apoio elétrico | 299 | R$ 7.000,00 | R$ 12.991,00 | R$ 1.979,00 | 11,7 anos | 26,9 |
| A3 – Combinação: banhos curtos + aquecimento solar | 210 | R$ 7.000,00 | R$ 11.643,70 | R$ 3.326,30 | 10,2 anos | 30,4 |

Custo total = investimento + reposições + Σ(energia + manutenção) no período. Retorno = payback simples (sem desconto).
CO2 = kWh × 38,5 kg/MWh ÷ 1000 (fator médio do SIN, MCTI 2023 [R2]).

## 5. Sensibilidade (A2 e A3)

| Tarifa (R$/kWh) | Reajuste/ano | Alt. | Retorno | Economia em 15 anos |
|---:|---:|---|---:|---:|
| 0,80 | 0% | A2 | 15,3 anos | R$ -116,80 |
| 0,80 | 0% | A3 | 13,2 anos | R$ 961,04 |
| 0,80 | 5% | A2 | 11,2 anos | R$ 3.559,83 |
| 0,80 | 5% | A3 | 10,1 anos | R$ 5.110,38 |
| 1,00 | 0% | A2 | 11,7 anos | R$ 1.979,00 |
| 1,00 | 0% | A3 | 10,2 anos | R$ 3.326,30 |
| 1,00 | 5% | A2 | 9,2 anos | R$ 6.574,78 |
| 1,00 | 5% | A3 | 8,3 anos | R$ 8.512,97 |
| 1,20 | 0% | A2 | 9,5 anos | R$ 4.074,80 |
| 1,20 | 0% | A3 | 8,3 anos | R$ 5.691,56 |
| 1,20 | 5% | A2 | 7,8 anos | R$ 9.589,74 |
| 1,20 | 5% | A3 | 7,0 anos | R$ 11.915,57 |

## 6. Como ler os resultados e limitações
- A1 não exige investimento e é a primeira medida em qualquer cenário testado.
- A viabilidade de A2 depende fortemente da tarifa, do reajuste e do orçamento real; veja a tabela de sensibilidade.
- O ganho em CO2 é pequeno porque a matriz elétrica brasileira já tem fator de emissão baixo.
- Dados marcados como `estimado` em `dados/premissas.csv` são hipóteses do grupo, não medições. Estimativas não são resultados garantidos.
- Não foram considerados: valor residual, taxa de desconto, tarifa social, tarifa branca, financiamento, queda de rendimento dos coletores.
