"""
KOAIALA FORECAST PREDICTIVE CHECK 11.0
"""

from src.forecast.forecast_predictive import construir_forecast


def main():
    print("=" * 70)
    print("KOAIALA FORECAST PREDICTIVE CHECK")
    print("=" * 70)

    resultado = construir_forecast()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "FORECAST PREDICTIVE REPROVADO ✗"
        )
        raise SystemExit(1)

    print(
        f"Cenário: {resultado['cenario']}"
    )
    print(
        f"Curto prazo: "
        f"{resultado['curto_prazo']['direcao']}"
    )
    print(
        f"Médio prazo: "
        f"{resultado['medio_prazo']['direcao']}"
    )
    print(
        f"Confiança: "
        f"{resultado['confianca']}"
    )

    print()
    print(
        "Forecast preditivo construído "
        "a partir da camada Scenario."
    )
    print(
        "STATUS FINAL: "
        "KOAIALA FORECAST PREDICTIVE "
        "APROVADO ✓"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
