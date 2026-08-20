"""
KOAIALA FULL CYCLE 15.0

Orquestra o Core existente + camada preditiva, sem sobrescrever
o full_cycle.py já aprovado.

Objetivo:
SENSE -> MASTER ENGINE -> PREDICTION -> SCENARIO -> FORECAST
-> CONSOLIDAÇÃO.

A camada preditiva é evidência complementar; não substitui o
Master Engine existente.
"""

from src.core.koaiala_engine import executar_koaiala
from src.predictive.signal_engine import executar as executar_prediction
from src.forecast.forecast_predictive import construir_forecast


def executar():
    master = executar_koaiala()
    predictive = executar_prediction()
    forecast = construir_forecast()

    if predictive["status"] != "OK":
        raise RuntimeError(
            "Camada preditiva indisponível."
        )

    if forecast["status"] != "OK":
        raise RuntimeError(
            "Forecast preditivo indisponível."
        )

    return {
        "status": "OK",
        "master": master,
        "predictive": predictive,
        "forecast": forecast,
    }


def _campo(obj, *nomes, default=None):
    if not isinstance(obj, dict):
        return default

    for nome in nomes:
        if nome in obj:
            return obj[nome]

    return default


def exibir(resultado):
    master = resultado["master"]
    predictive = resultado["predictive"]
    forecast = resultado["forecast"]

    print("=" * 72)
    print("KOAIALA OS — FULL CYCLE 15.0")
    print("=" * 72)

    print()
    print("[1] MASTER ENGINE")
    print("-" * 72)

    score = _campo(
        master,
        "score",
        "score_macro",
    )

    classificacao = _campo(
        master,
        "classificacao",
        "cenario",
        default="N/D",
    )

    confianca = _campo(
        master,
        "confianca",
        default="N/D",
    )

    print(f"Score: {score}")
    print(f"Cenário base: {classificacao}")
    print(f"Confiança: {confianca}")

    print()
    print("[2] EVIDÊNCIA PREDITIVA")
    print("-" * 72)

    for indicador, sinal in predictive["sinais"].items():

        if sinal.get("status") != "OK":
            print(
                f"{indicador}: INSUFICIENTE"
            )
            continue

        print(
            f"{indicador}: "
            f"{sinal['sinal']} | "
            f"{sinal['status_sinal']} | "
            f"confiança={sinal['confianca']} | "
            f"ganho={sinal['ganho_historico']:+.2%}"
        )

    print()
    print("[3] FORECAST")
    print("-" * 72)

    print(
        f"Cenário preditivo: "
        f"{forecast['cenario']}"
    )

    print(
        f"Curto prazo: "
        f"{forecast['curto_prazo']['direcao']}"
    )

    print(
        f"Médio prazo: "
        f"{forecast['medio_prazo']['direcao']}"
    )

    print(
        f"Confiança preditiva: "
        f"{forecast['confianca']}"
    )

    print()
    print("[4] CONSOLIDAÇÃO")
    print("-" * 72)

    cenario_master = str(
        classificacao or ""
    ).upper()

    cenario_pred = str(
        forecast["cenario"]
    ).upper()

    if (
        "INFLA" in cenario_pred
        or "PRESSAO" in cenario_pred
    ):
        alerta = (
            "PRESSÃO INFLACIONÁRIA "
            "DETECTADA PELA CAMADA PREDITIVA"
        )
    else:
        alerta = (
            "SEM PRESSÃO INFLACIONÁRIA "
            "PREDITIVA DOMINANTE"
        )

    print(
        f"Leitura estrutural: "
        f"{cenario_master}"
    )

    print(
        f"Leitura preditiva: "
        f"{cenario_pred}"
    )

    print(
        f"Alerta: {alerta}"
    )

    print()
    print(
        "O Master Engine permanece a fonte da "
        "decisão estrutural; o Prediction atua "
        "como evidência adicional."
    )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA FULL CYCLE 15.0 APROVADO ✓"
    )
    print("=" * 72)


if __name__ == "__main__":
    exibir(executar())
