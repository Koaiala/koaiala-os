"""
KOAIALA MASTER ENGINE

Ponto único de execução do núcleo analítico.

Fluxo:

Sense/Database
    ↓
Analysis
    ↓
Interpreter
    ↓
Scenario
    ↓
Forecast
    ↓
Decision
"""

from datetime import datetime
from typing import Dict

from src.insight.scenario_engine import construir_cenario
from src.forecast.forecast_engine import projetar_indicadores
from src.decision.decision_engine import construir_decisao
from src.risk.risk_engine import avaliar_riscos


def executar_koaiala() -> Dict:
    inicio = datetime.now()

    cenario = construir_cenario()

    if cenario.get("status") != "OK":
        return {
            "status": "ERRO",
            "etapa": "SCENARIO",
            "resultado": cenario,
        }

    previsoes = projetar_indicadores()

    riscos = avaliar_riscos(cenario, previsoes)

    decisao = construir_decisao(
        cenario,
        previsoes,
    )

    fim = datetime.now()

    return {
        "status": "OK",
        "timestamp": fim.isoformat(),
        "duracao_segundos": round(
            (fim - inicio).total_seconds(),
            4,
        ),
        "cenario": cenario,
        "previsoes": previsoes,
        "riscos": riscos,
        "decisao": decisao,
    }


def exibir_koaiala(resultado: Dict) -> None:
    print("=" * 70)
    print("KOAIALA OS — MASTER ENGINE")
    print("=" * 70)

    if resultado.get("status") != "OK":
        print("STATUS:", resultado.get("status"))
        print("ETAPA:", resultado.get("etapa"))
        print("RESULTADO:", resultado.get("resultado"))
        print("=" * 70)
        return

    cenario = resultado["cenario"]

    print(
        f"Indicadores analisados: "
        f"{cenario['total_indicadores']}"
    )

    print(
        f"Score macro: "
        f"{cenario['score']:.4f}"
    )

    print(
        f"Cenário: "
        f"{cenario['classificacao']}"
    )

    print(
        f"Confiança: "
        f"{cenario['confianca']['nivel']}"
    )

    print(
        f"Cobertura: "
        f"{cenario['confianca']['cobertura']:.0%}"
    )

    print("-" * 70)
    print("LEITURA")
    print(cenario["interpretacao"])

    print("-" * 70)
    print("CENÁRIOS")

    for nome in ("otimista", "base", "adverso"):
        dados = cenario["cenarios"][nome]
        print(
            f"{nome.upper()}: "
            f"{dados['participacao']:.0%}"
        )

    print("-" * 70)
    print("MAPA DE DECISÃO")

    for classe, dados in resultado["decisao"]["classes"].items():
        print(
            f"{classe}: "
            f"{dados['viés']}"
        )

    print("-" * 70)
    print(
        f"Tempo: "
        f"{resultado['duracao_segundos']:.4f}s"
    )

    print("=" * 70)


def main():
    resultado = executar_koaiala()
    exibir_koaiala(resultado)


if __name__ == "__main__":
    main()
