# Citizen Assist AI – Módulo Energia
**Global Solution – Soluções em Energias Renováveis e Sustentáveis | Ciência da Computação – 1CC**

## Integrantes
| Nome completo | RM |
|---|---|
| Ricardo Algazi | 569600 |
| Vinicius Molena | 571270 |

## Público e problema
**Público:** famílias de residências urbanas na Grande São Paulo (distribuidora Enel SP) que usam chuveiro elétrico. A residência-modelo tem 4 pessoas.
**Problema:** o chuveiro elétrico é um dos maiores consumidores de eletricidade em casa (o Procel/Eletrobras estima ~7% de toda a energia elétrica produzida no país [R5]) e muitas famílias não sabem quanto ele custa nem quais alternativas realmente compensam.
**Como o assistente ajuda:** responde em linguagem simples quanto o banho gasta, como economizar sem custo, se vale a pena instalar aquecimento solar e qual o impacto ambiental, sempre com cálculo, referências e limitações.

## Funcionalidades de energia
O assistente (`src/assistente.py`) reconhece perguntas e **recalcula** tudo a partir de `dados/premissas.csv` com `src/energia_calc.py` (nenhum número fixo nas respostas):

| Pergunta de exemplo | O que o assistente faz |
|---|---|
| "Quanto meu chuveiro gasta por mês?" | Calcula kWh e R$ (E = P × t). Aceita "3 pessoas", "12 minutos", "tarifa 0,90". |
| "Como economizar no banho?" | Alternativa A1 (banhos mais curtos, custo zero). |
| "Vale a pena instalar aquecedor solar?" | Alternativa A2 (renovável): investimento, economia, retorno. |
| "Compare as alternativas" | Tabela A0–A3 para o mesmo uso e período (15 anos) + recomendação coerente com os cálculos. |
| "Qual o impacto ambiental?" | CO2 estimado com o fator médio do SIN. |
| "Quais as referências?" / "limitações?" | Lista fontes e condições das estimativas. |
| Pergunta fora do escopo | Diz que não entendeu em vez de inventar resposta. |

## Como executar (Python 3.9+, sem bibliotecas externas)
```bash
python src/main.py                       # conversa interativa (digite "sair" para encerrar)
python src/main.py --pergunta "Vale a pena instalar aquecedor solar?"
python src/main.py --demo                # gera resultados/demo_assistente.txt
python src/gerar_resultados.py           # regenera tabelas e docs/CALCULOS_E_COMPARACAO.md
python -m unittest discover -s tests -v  # testes automatizados (15 testes)
```

## Estrutura
```
dados/premissas.csv              dados, unidades, tipo (estimado/público/convenção) e origem
src/energia_calc.py              cálculos de energia, custo, retorno e CO2
src/assistente.py                assistente (intenções + respostas + referências + limitações)
src/main.py                      interface de linha de comando
src/gerar_resultados.py          gera tabelas e relatório de cálculos
tests/test_energia.py            testes automatizados dos cálculos e do assistente
resultados/                      comparacao.csv, sensibilidade.csv, demo_assistente.txt
docs/CALCULOS_E_COMPARACAO.md    cálculos passo a passo e comparação das alternativas
docs/JUSTIFICATIVAS.md           custos, viabilidade e impactos ambientais
docs/REFERENCIAS.md              fontes verificáveis
docs/TESTES_COM_USUARIOS.md      roteiro e registro dos testes com usuários
docs/ROTEIRO_VIDEO.md            roteiro do vídeo (até 3 min)
```

## Resultado resumido (cenário base)
Para 4 pessoas, banho de 10 min e tarifa de referência de R$ 1,00/kWh, o chuveiro consome ~998 kWh/ano (~R$ 998/ano). Banhos 30% mais curtos economizam ~R$ 299/ano sem custo. O aquecimento solar (R$ 7.000 estimados) se paga em ~11,7 anos neste cenário e depende muito de tarifa, reajuste e orçamento real (ver sensibilidade). O ganho de CO2 é pequeno porque a matriz elétrica brasileira já é de baixo carbono.

## Limitações (importante)
Todos os valores marcados como `estimado` em `dados/premissas.csv` são **hipóteses**, não medições. Tarifa, potência do chuveiro, fração solar e custo de instalação variam. Os resultados **não são economia garantida**. Nada foi validado com projeto de instalador nem com medições reais.
