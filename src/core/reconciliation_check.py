"""
KOAIALA RECONCILIATION CHECK 16.1
"""

from src.reconciliation.reconciliation_engine import (
    executar,
    exibir,
)


def main():
    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "RECONCILIATION 16.1 "
            "REPROVADA ✗"
        )
        raise SystemExit(1)

    exibir(resultado)


if __name__ == "__main__":
    main()
