# Pré-teste interno (SIMULADO) — NÃO são testes com usuários

> **Atenção:** este arquivo registra uma simulação feita pelos desenvolvedores (com apoio de IA) usando frases informais escritas por nós. **Não houve participantes reais** e este registro **não substitui** `TESTES_COM_USUARIOS.md`. Serve para encontrar falhas técnicas antes dos testes reais.

## Frases testadas e problemas encontrados
| Frase simulada | Comportamento antes | Problema | Correção |
|---|---|---|---|
| "minha conta de luz ta um absurdo, o que eu faço?" | Respondeu consumo do chuveiro | Intenção errada; usuário queria dicas | Gatilhos de economia ampliados |
| "painel solar compensa?" | Respondeu aquecimento solar | Enganoso: painel é fotovoltaico, não analisado | Resposta explica o escopo e não inventa cálculo |
| "pago 0,75 por kwh" | Tarifa ignorada | Formato não reconhecido | Leitura de "X por kWh" |
| "chuveiro eletrico polui?" | Respondeu consumo | Intenção ambiental não reconhecida | Gatilho "polui" |
| "obrigado" | "Não entendi" | Resposta fria | Resposta de agradecimento |

Os demais casos ("o chuveiro gasta muito?", "tomo banho de 20 min…", "isso é garantido?", "qual a fonte disso") funcionaram. Cada correção tem teste em `tests/test_energia.py` (`test_pre_teste_frases_informais`).

## Limitação conhecida
O assistente é baseado em palavras-chave: frases muito diferentes das previstas caem na mensagem "não entendi". Isso deve ser observado nos testes com usuários reais.
