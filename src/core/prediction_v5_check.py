"""
KOAIALA PREDICTION 5.0 CHECK
"""

from src.backtest.prediction_v5 import executar


def main():
    print("=" * 70)
    print("KOAIALA PREDICTION 5.0 CHECK")
    print("=" * 70)

    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "PREDICTION 5.0 REPROVADO ✗"
        )
        raise SystemExit(1)

    print()
    print(
        "Experimento executado sem look-ahead."
    )
    print(
        "STATUS FINAL: "
        "KOAIALA PREDICTION 5.0 EXECUTADO ✓"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
