"""
KOAIALA HISTORICAL BACKFILL V8 FIX
"""

from src.sense.registry import get_indicator
from src.sense.sgs_collector_v8 import coletar

INDICADORES = [
    "IPCA",
    "INPC",
    "IGP_M",
]


def main():

    print("=" * 60)
    print("KOAIALA HISTORICAL BACKFILL V8 FIX")
    print("=" * 60)

    falhas = 0

    for codigo in INDICADORES:

        print()

        indicador = get_indicator(
            codigo
        )

        if not indicador:
            print(
                f"{codigo}: "
                "NÃO ENCONTRADO NO REGISTRY"
            )
            falhas += 1
            continue

        try:

            resultado = coletar(
                indicador,
                anos=10,
            )

            print(
                f"{codigo}: "
                f"{resultado['novos']} novos | "
                f"{resultado['existentes']} existentes"
            )

        except Exception as error:

            falhas += 1

            print(
                f"{codigo}: ERRO - {error}"
            )

    print()
    print("-" * 60)
    print(
        f"Indicadores processados: "
        f"{len(INDICADORES)}"
    )
    print(
        f"Falhas: {falhas}"
    )

    if falhas:
        print(
            "STATUS FINAL: "
            "BACKFILL V8 COM FALHAS ✗"
        )
        raise SystemExit(1)

    print(
        "STATUS FINAL: "
        "BACKFILL V8 APROVADO ✓"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
