"""
KOAIALA FINAL CYCLE CHECK 18.0
"""

from src.core.final_cycle_v18 import executar, exibir


def main():
    resultado = executar()

    if resultado["status"] != "OK":
        raise SystemExit(
            "STATUS FINAL: KOAIALA OS 1.0 REPROVADO ✗"
        )

    exibir(resultado)


if __name__ == "__main__":
    main()
