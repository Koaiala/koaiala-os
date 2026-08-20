"""
KOAIALA PREDICTIVE SIGNAL ENGINE 9.0

Camada de evidência preditiva.
Não substitui Scenario, Forecast, Risk ou Decision.

Usa o Prediction 7.0 já validado experimentalmente e transforma
sua saída em sinais estruturados que podem ser consumidos pelo
Master Engine.
"""

from src.backtest.prediction_v7 import avaliar
from src.backtest.backtest_v2 import INDICADORES


def _confianca(ganho):
    """
    Classificação conservadora baseada no ganho fora da amostra.
    Não representa probabilidade estatística.
    """

    if ganho >= 0.10:
        return "ALTA"

    if ganho >= 0.05:
        return "MODERADA"

    if ganho > 0:
        return "BAIXA"

    return "NENHUMA"


def _direcao_predominante(item):
    avaliacoes = item.get("avaliacoes", [])

    if not avaliacoes:
        return "ESTABILIDADE"

    ultimo = avaliacoes[-1]

    return ultimo["previsao"]


def gerar_sinal(indicador):
    resultado = avaliar(indicador)

    if resultado["status"] != "OK":
        return {
            "status": "INSUFICIENTE",
            "indicador": indicador,
        }

    ganho = float(resultado["ganho"])

    confianca = _confianca(ganho)

    if ganho <= 0:
        status_sinal = "SEM_VANTAGEM"
    else:
        status_sinal = "SINAL_ATIVO"

    return {
        "status": "OK",
        "indicador": indicador,
        "sinal": (
            _direcao_predominante(resultado)
            if ganho > 0
            else "NEUTRO"
        ),
        "status_sinal": status_sinal,
        "confianca": confianca,
        "ganho_historico": resultado["ganho"],
        "taxa_modelo": resultado["taxa"],
        "taxa_baseline": resultado["taxa_baseline"],
        "avaliacoes": resultado["total"],
        "fonte_modelo": "PREDICTION_7",
    }


def executar():
    sinais = {}

    for indicador in INDICADORES:
        sinais[indicador] = gerar_sinal(
            indicador
        )

    ativos = [
        item
        for item in sinais.values()
        if item.get("status_sinal")
        == "SINAL_ATIVO"
    ]

    return {
        "status": "OK",
        "fonte": "KOAIALA_PREDICTIVE_EVIDENCE",
        "sinais": sinais,
        "sinais_ativos": len(ativos),
    }


def exibir(resultado):
    print("=" * 70)
    print("KOAIALA PREDICTIVE EVIDENCE")
    print("=" * 70)

    for indicador, sinal in resultado["sinais"].items():

        if sinal["status"] != "OK":
            print(
                f"{indicador}: "
                "DADOS INSUFICIENTES"
            )
            continue

        print(
            f"{indicador}: "
            f"{sinal['sinal']} | "
            f"{sinal['status_sinal']} | "
            f"confiança={sinal['confianca']} | "
            f"ganho={sinal['ganho_historico']:+.2%}"
        )

    print("-" * 70)
    print(
        f"Sinais ativos: "
        f"{resultado['sinais_ativos']}"
    )
    print("=" * 70)


if __name__ == "__main__":
    exibir(executar())
