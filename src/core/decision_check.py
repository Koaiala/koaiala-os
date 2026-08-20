"""
KOAIALA DECISION CHECK 17.1
"""

from src.decision.decision_engine import executar, exibir


def main():
    resultado = executar()

    if resultado["status"] != "OK":
        raise SystemExit(
            "STATUS FINAL: KOAIALA DECISION 17.1 REPROVADA ✗"
        )

    exibir(resultado)


if __name__ == "__main__":
    main()
