"""
KOAIALA SCENARIO PREDICTIVE CHECK 10.0
"""

from src.scenario.scenario_predictive import (
    construir_cenario_preditivo,
)


def main():
    print("=" * 70)
    print("KOAIALA SCENARIO PREDICTIVE CHECK")
    print("=" * 70)

    resultado = construir_cenario_preditivo()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "SCENARIO PREDICTIVE REPROVADO ✗"
        )
        raise SystemExit(1)

    print(
        f"Direção: {resultado['direcao']}"
    )
    print(
        f"Força: {resultado['forca']}"
    )
    print(
        f"Sinais ativos: "
        f"{resultado['sinais_ativos']}"
    )

    print()
    print(
        "Evidência preditiva integrada "
        "ao Scenario como camada complementar."
    )
    print(
        "STATUS FINAL: "
        "KOAIALA SCENARIO PREDICTIVE "
        "APROVADO ✓"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
