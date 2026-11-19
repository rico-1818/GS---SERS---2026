"""Executa o módulo Energia do Citizen Assist AI.

Uso:
  python src/main.py                       # modo interativo
  python src/main.py --pergunta "texto"   # uma pergunta
  python src/main.py --demo               # perguntas de exemplo (gera resultados/demo_assistente.txt)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assistente import CitizenAssistEnergia  # noqa: E402

DEMO = [
    "Quanto meu chuveiro gasta por mês?",
    "Somos 3 pessoas, banho de 15 minutos e a tarifa é 0,90. Quanto gasto?",
    "Como economizar no banho?",
    "Vale a pena instalar aquecedor solar?",
    "Compare as alternativas",
    "Qual o impacto ambiental?",
    "Quais as referências?",
    "Quanto custa uma pizza?",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pergunta")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    bot = CitizenAssistEnergia()
    if a.pergunta:
        print(bot.responder(a.pergunta))
    elif a.demo:
        saida = []
        for q in DEMO:
            saida.append(f"USUÁRIO: {q}\n\nASSISTENTE:\n{bot.responder(q)}\n" + "=" * 80)
        texto = "\n\n".join(saida)
        Path(__file__).resolve().parent.parent.joinpath("resultados", "demo_assistente.txt").write_text(texto, encoding="utf-8")
        print(texto)
    else:
        print(bot.responder("ajuda"))
        while True:
            try:
                q = input("\nVocê: ")
            except (EOFError, KeyboardInterrupt):
                break
            if q.strip().lower() in {"sair", "exit", "q"}:
                break
            print("\nAssistente:", bot.responder(q))


if __name__ == "__main__":
    main()
