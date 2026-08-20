"""
KOAIALA BACKTEST CHECK
"""

from src.backtest.backtest_engine import (
    executar_backtest,
)


def main():

    print("=" * 60)
    print("KOAIALA BACKTEST CHECK")
    print("=" * 60)

    resultado = executar_backtest()

    if resultado["status"] != "OK":

        print(
            "STATUS FINAL: "
            "KOAIALA BACKTEST REPROVADO ✗"
        )

        raise SystemExit(1)

    if resultado["total_avaliacoes"] == 0:

        print(
            "STATUS FINAL: "
            "DADOS INSUFICIENTES"
        )

        raise SystemExit(2)

    print(
        f"Avaliações: "
        f"{resultado['total_avaliacoes']}"
    )

    print(
        f"Acertos: "
        f"{resultado['acertos']}"
    )

    print(
        f"Erros: "
        f"{resultado['erros']}"
    )

    print(
        f"Taxa agregada: "
        f"{resultado['taxa_acerto_agregada']:.2%}"
    )

    print(
        "STATUS FINAL: "
        "KOAIALA BACKTEST APROVADO ✓"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
