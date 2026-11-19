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
| P1 |  | S1 |  |  |  |  |  |
| P1 |  | S2 |  |  |  |  |  |
| P1 |  | S3 |  |  |  |  |  |
| P2 |  |  |  |  |  |  |  |
| P3 |  |  |  |  |  |  |  |

## 3. Ajustes realizados após os testes
| Problema observado | Quem relatou | Ajuste feito (arquivo/commit) | Resultado ao retestar |
|---|---|---|---|
|  |  |  |  |

## 4. Síntese
*(Escrever após os testes: o que funcionou, o que foi confuso, o que mudou.)*

---
## Anexo – testes técnicos automatizados (reais, não são testes com usuários)
`python -m unittest discover -s tests -v` executa 15 testes: conferência do consumo (998 kWh/ano) e dos custos com cálculo manual, payback, CO2, leitura de valores informados pelo usuário, descarte de valores absurdos, respostas com referências/limitações e pergunta fora do escopo.
