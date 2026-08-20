"""
KOAIALA VALIDATION 4.0 CHECK
"""

from src.backtest.backtest_v4 import executar


def main():
    print("=" * 60)
    print("KOAIALA VALIDATION 4.0 CHECK")
    print("=" * 60)

    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "VALIDAÇÃO 4.0 REPROVADA ✗"
        )
        raise SystemExit(1)

    print()
    print(
        f"Média modelo: "
        f"{resultado['media_modelo']:.2%}"
    )
    print(
        f"Média baseline: "
        f"{resultado['media_baseline']:.2%}"
    )
    print(
        f"Ganho médio: "
        f"{resultado['ganho_medio']:+.2%}"
    )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA VALIDATION 4.0 EXECUTADA ✓"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
