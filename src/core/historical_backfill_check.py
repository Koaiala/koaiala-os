"""
KOAIALA HISTORICAL BACKFILL CHECK
"""

from src.backfill.historical_backfill import executar


def main():
    print("=" * 60)
    print("KOAIALA HISTORICAL BACKFILL CHECK")
    print("=" * 60)

    resultados = executar()

    erros = [
        codigo
        for codigo, resultado in resultados.items()
        if resultado.get("status") == "ERRO"
    ]

    print()
    print("-" * 60)
    print(
        f"Indicadores processados: "
        f"{len(resultados)}"
    )
    print(
        f"Falhas: {len(erros)}"
    )

    if erros:
        print(
            "Indicadores com falha: "
            + ", ".join(erros)
        )
        print(
            "STATUS FINAL: "
            "BACKFILL COM FALHAS ✗"
        )
        raise SystemExit(1)

    print(
        "STATUS FINAL: "
        "BACKFILL EXECUTADO ✓"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
