"""
KOAIALA VALIDATION 8.0 CHECK
"""

from src.backtest.validation_v8 import executar


def main():
    print("=" * 72)
    print("KOAIALA VALIDATION 8.0 CHECK")
    print("=" * 72)

    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "VALIDATION 8.0 REPROVADA ✗"
        )
        raise SystemExit(1)

    for indicador, item in (
        resultado["indicadores"].items()
    ):
        if item["status"] != "OK":
            continue

        print(
            f"{indicador}: "
            f"modelo={item['taxa']:.2%} | "
            f"baseline={item['taxa_baseline']:.2%} | "
            f"ganho={item['ganho']:+.2%}"
        )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA VALIDATION 8.0 EXECUTADA ✓"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
