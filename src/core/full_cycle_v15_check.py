"""
KOAIALA FULL CYCLE 15.0 CHECK
"""

from src.core.full_cycle_v15 import executar, exibir


def main():
    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "KOAIALA FULL CYCLE 15.0 "
            "REPROVADO ✗"
        )
        raise SystemExit(1)

    exibir(resultado)


if __name__ == "__main__":
    main()
