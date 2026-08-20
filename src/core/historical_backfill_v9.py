"""
KOAIALA HISTORICAL BACKFILL V9

Backfill histórico com séries SGS explícitas e confirmadas pelo
coletor já utilizado pelo Koaiala:

IPCA  = 433
INPC  = 188
IGP_M = 189

Não depende do formato interno do Registry.
"""

from src.sense.sgs_collector_v8 import coletar


INDICADORES = [
    {
        "code": "IPCA",
        "name": "IPCA",
        "source": "Banco Central do Brasil / IBGE",
        "sgs_series": 433,
        "unit": "%",
    },
    {
        "code": "INPC",
        "name": "INPC",
        "source": "Banco Central do Brasil / IBGE",
        "sgs_series": 188,
        "unit": "%",
    },
    {
        "code": "IGP_M",
        "name": "IGP-M",
        "source": "Banco Central do Brasil / FGV",
        "sgs_series": 189,
        "unit": "%",
    },
]


def main():

    print("=" * 60)
    print("KOAIALA HISTORICAL BACKFILL V9")
    print("=" * 60)

    falhas = 0

    for indicador in INDICADORES:

        print()

        try:
            resultado = coletar(
                indicador,
                anos=10,
            )

            print(
                f"{indicador['code']}: "
                f"{resultado['novos']} novos | "
                f"{resultado['existentes']} existentes"
            )

        except Exception as error:

            falhas += 1

            print(
                f"{indicador['code']}: ERRO - {error}"
            )

    print()
    print("-" * 60)
    print(
        f"Indicadores processados: "
        f"{len(INDICADORES)}"
    )
    print(f"Falhas: {falhas}")

    if falhas:
        print(
            "STATUS FINAL: "
            "BACKFILL V9 COM FALHAS ✗"
        )
        raise SystemExit(1)

    print(
        "STATUS FINAL: "
        "BACKFILL V9 APROVADO ✓"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
