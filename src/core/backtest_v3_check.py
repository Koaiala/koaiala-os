"""
KOAIALA BACKTEST 3.0 CHECK
"""

from src.backtest.backtest_v3 import executar


def main():
    print("=" * 60)
    print("KOAIALA BACKTEST 3.0 CHECK")
    print("=" * 60)

    resultado = executar()

    if resultado["status"] != "OK":
        print("STATUS FINAL: BACKTEST 3.0 REPROVADO ✗")
        raise SystemExit(1)

    print(
        f"Média bruta: "
        f"{resultado['media_acuracia_bruta']:.2%}"
    )
    print(
        f"Média balanceada: "
        f"{resultado['media_acuracia_balanceada']:.2%}"
    )

    print(
        "STATUS FINAL: "
        "KOAIALA BACKTEST 3.0 EXECUTADO ✓"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
