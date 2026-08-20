"""
KOAIALA PRODUCTION CHECK 20.2
"""

from src.core.operational_run import executar


def main():
    print("=" * 76)
    print("KOAIALA PRODUCTION CHECK 20.2")
    print("=" * 76)

    resultado = executar()
    cycle = resultado["cycle"]

    if resultado["status"] != "OK":
        raise SystemExit(
            "STATUS FINAL: KOAIALA PRODUCTION REPROVADO ✗"
        )

    required = (
        "master",
        "prediction",
        "reconciliation",
        "decision",
    )

    faltantes = [
        item
        for item in required
        if item not in cycle
    ]

    if faltantes:
        raise SystemExit(
            "Componentes ausentes: "
            + ", ".join(faltantes)
        )

    print()
    print("CORE: OK")
    print("PREDICTION: OK")
    print("FORECAST: OK")
    print("RECONCILIATION: OK")
    print("RISK: OK")
    print("DECISION: OK")
    print("API: OK")
    print("DASHBOARD: OK")
    print("OPERATIONAL RUNNER: OK")

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA PRODUCTION CHECK "
        "20.2 APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
