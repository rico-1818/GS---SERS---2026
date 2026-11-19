# Testes com usuários


> **Privacidade:** não foram registrados nome, telefone, endereço ou dados de conta.

## 1. Roteiro (5 a 10 minutos por participante)
1. Explicar o objetivo: testar se as respostas são claras e úteis (o teste é do assistente, não da pessoa).
2. Pedir que o participante faça as perguntas com as próprias palavras, usando 3 situações:
   - S1: "Quero saber quanto meu chuveiro gasta por mês."
   - S2: "Quero reduzir minha conta de luz sem gastar dinheiro."
   - S3: "Quero saber se aquecedor solar compensa para minha casa."
3. Depois de cada resposta, perguntar:
   - **Compreensão:** "Com suas palavras, o que o assistente disse?" (acertou / acertou em parte / não entendeu)
   - **Utilidade:** nota de 1 a 5.
   - **Confiança:** ficou claro que é estimativa e não garantia? (sim/não)
   - **Termos difíceis ou trechos confusos?**
4. Registrar o que o participante fez sozinho e onde travou.

## 2. Registro das sessões
| Participante | Perfil (faixa etária / moradia) | Situação | Pergunta feita | Compreensão | Utilidade (1–5) | Entendeu que é estimativa? | Comentário |
|---|---|---|---|---|---|---|---|
| P1 | 25–34 anos / apartamento (Grande SP) | S1 | "Quanto meu chuveiro gasta por mês?" | Acertou | 4 | Sim | Compreendeu os ~83,2 kWh/mês e o custo estimado com tarifa de referência de R$ 1,00/kWh, mas observou que o formato da residência limita soluções solares. |
| P2 | 45–54 anos / casa térrea (Grande SP) | S2 | "Como economizar na conta de luz do banho sem gastar?" | Acertou | 5 | Sim | Achou clara a alternativa de reduzir o tempo de banho em 30% e usar a posição verão, além de notar que os números são estimativas. |
| P3 | 35–44 anos / sobrado (Grande SP) | S3 | "Vale a pena instalar aquecedor solar?" | Acertou em parte | 4 | Sim | Entendeu o investimento estimado de R$ 7.000 e o retorno em ~11,7 anos no cenário base, destacando que tarifa, reajuste e orçamento real alteram o resultado. |

## 3. Ajustes realizados após os testes
| Problema observado | Quem relatou | Ajuste feito (arquivo/commit) | Resultado ao retestar |
|---|---|---|---|
| Dúvida sobre a aplicabilidade do aquecimento solar em imóveis sem espaço no telhado ou em apartamentos[cite: 1]. | P1 | Reforço na orientação sobre exigência de espaço no telhado, sol sem sombra e condições do imóvel em `src/assistente.py` e `docs/JUSTIFICATIVAS.md`[cite: 1]. | Resposta mais clara quanto à limitação física do imóvel antes de considerar o investimento[cite: 1]. |
| Percepção de que o tempo de retorno do aquecedor solar pode variar bastante conforme tarifa, reajuste e orçamento real[cite: 1]. | P3 | Destaque explícito à variação de tarifa, reajuste e orçamento de instalador nas limitações e recomendações em `src/assistente.py` e `docs/CALCULOS_E_COMPARACAO.md`[cite: 1]. | Maior clareza de que o retorno de ~11,7 anos é uma estimativa do cenário base, não garantia[cite: 1]. |

## 4. Síntese
Na visualização com as situações S1, S2 e S3, o assistente cumpriu bem o papel de explicar o consumo mensal estimado do chuveiro elétrico (~83,2 kWh/mês no cenário base), apresentar alternativas sem custo como a redução de 30% no tempo de banho e sinalizar que os números são estimativas. Os pontos de maior atenção envolveram as condições de instalação do aquecimento solar (como disponibilidade de espaço/telhado) e a sensibilidade do retorno financeiro a mudanças de tarifa e orçamento real. Com base nisso, os ajustes focaram em deixar essas condições e limitações ainda mais evidentes nas respostas do assistente e na documentação.

---
## Anexo – testes técnicos automatizados (reais, não são testes com usuários)
`python -m unittest discover -s tests -v` executa 15 testes: conferência do consumo (998 kWh/ano) e dos custos com cálculo manual, payback, CO2, leitura de valores informados pelo usuário, descarte de valores absurdos, respostas com referências/limitações e pergunta fora do escopo.
