"""
KOAIALA PREDICTION 6.0 CHECK
"""

from src.backtest.prediction_v6 import executar


def main():
    print("=" * 70)
    print("KOAIALA PREDICTION 6.0 CHECK")
    print("=" * 70)

    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "PREDICTION 6.0 REPROVADO ✗"
        )
        raise SystemExit(1)

    print()

    for indicador, item in resultado["indicadores"].items():

        if item["status"] != "OK":
            print(
                f"{indicador}: "
                "DADOS INSUFICIENTES"
            )
            continue

        print(
            f"{indicador}: "
            f"MODELO {item['taxa_modelo']:.2%} | "
            f"BASELINE {item['taxa_baseline']:.2%} | "
            f"GANHO {item['ganho']:+.2%}"
        )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA PREDICTION 6.0 EXECUTADO ✓"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
