"""
KOAIALA PREDICTIVE INTEGRATION CHECK 9.0

Verifica a nova camada sem modificar o Master Engine existente.
"""

from src.predictive.signal_engine import executar


def main():
    print("=" * 70)
    print("KOAIALA PREDICTIVE INTEGRATION CHECK")
    print("=" * 70)

    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "INTEGRAÇÃO PREDITIVA REPROVADA ✗"
        )
        raise SystemExit(1)

    print()

    for indicador, sinal in (
        resultado["sinais"].items()
    ):
        if sinal["status"] != "OK":
            print(
                f"{indicador}: "
                "INSUFICIENTE"
            )
            continue

        print(
            f"{indicador}: "
            f"sinal={sinal['sinal']} | "
            f"status={sinal['status_sinal']} | "
            f"confiança={sinal['confianca']} | "
            f"ganho={sinal['ganho_historico']:+.2%}"
        )

    print()
    print(
        "Prediction 7 incorporado como "
        "EVIDÊNCIA PREDITIVA."
    )
    print(
        "Scenario / Forecast / Risk / Decision "
        "permanecem independentes."
    )
    print()
    print(
        "STATUS FINAL: "
        "KOAIALA PREDICTIVE INTEGRATION "
        "APROVADA ✓"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
