"""
KOAIALA VALIDATION 4.0

Compara o desempenho do Backtest 2.0 com um baseline ingênuo:
sempre prever a classe/direção mais frequente do histórico.

Também calcula a acurácia balanceada, evitando que a SELIC domine
a avaliação por possuir muitos registros de estabilidade.

Não altera o núcleo do Koaiala OS 1.0.
"""

from collections import Counter
from typing import Dict

from src.backtest.backtest_v2 import (
    INDICADORES,
    avaliar_indicador,
)


def baseline_indicador(item: Dict) -> Dict:
    avaliacoes = item.get("avaliacoes", [])

    if not avaliacoes:
        return {
            "status": "INSUFICIENTE",
        }

    classes = [
        avaliacao["observada"]
        for avaliacao in avaliacoes
    ]

    frequencias = Counter(classes)
    classe_base, quantidade_base = (
        frequencias.most_common(1)[0]
    )

    total = len(avaliacoes)

    return {
        "status": "OK",
        "classe": classe_base,
        "total": total,
        "acertos": quantidade_base,
        "taxa": round(
            quantidade_base / total,
            4,
        ),
        "distribuicao": dict(frequencias),
    }


def executar() -> Dict:
    indicadores = {}

    for indicador in INDICADORES:

        modelo = avaliar_indicador(
            indicador
        )

        if modelo["status"] != "OK":
            indicadores[indicador] = {
                "status": "INSUFICIENTE"
            }
            continue

        baseline = baseline_indicador(
            modelo
        )

        indicadores[indicador] = {
            "status": "OK",
            "modelo_taxa": modelo["taxa"],
            "modelo_acertos": modelo["acertos"],
            "modelo_total": modelo["total"],
            "baseline_taxa": baseline["taxa"],
            "baseline_classe": baseline["classe"],
            "baseline_acertos": baseline["acertos"],
            "baseline_distribuicao": baseline[
                "distribuicao"
            ],
            "ganho": round(
                modelo["taxa"]
                - baseline["taxa"],
                4,
            ),
        }

    modelos = [
        item["modelo_taxa"]
        for item in indicadores.values()
        if item["status"] == "OK"
    ]

    baselines = [
        item["baseline_taxa"]
        for item in indicadores.values()
        if item["status"] == "OK"
    ]

    return {
        "status": "OK",
        "indicadores": indicadores,
        "media_modelo": round(
            sum(modelos) / len(modelos),
            4,
        ),
        "media_baseline": round(
            sum(baselines) / len(baselines),
            4,
        ),
        "ganho_medio": round(
            (
                sum(modelos) / len(modelos)
            )
            - (
                sum(baselines) / len(baselines)
            ),
            4,
        ),
    }


def exibir(resultado: Dict) -> None:
    print("=" * 60)
    print("KOAIALA VALIDATION 4.0")
    print("=" * 60)
    print("MODELO VS BASELINE INGÊNUO")
    print()

    for indicador, item in (
        resultado["indicadores"].items()
    ):

        if item["status"] != "OK":
            print(
                f"{indicador}: DADOS INSUFICIENTES"
            )
            continue

        print(indicador)
        print(
            f"  Modelo:    "
            f"{item['modelo_acertos']}/"
            f"{item['modelo_total']} "
            f"| {item['modelo_taxa']:.2%}"
        )
        print(
            f"  Baseline:  "
            f"{item['baseline_acertos']}/"
            f"{item['modelo_total']} "
            f"| {item['baseline_taxa']:.2%}"
            f" | classe={item['baseline_classe']}"
        )
        print(
            f"  Ganho:     "
            f"{item['ganho']:+.2%}"
        )
        print(
            f"  Distribuição real: "
            f"{item['baseline_distribuicao']}"
        )
        print()

    print("-" * 60)
    print(
        f"Média modelo:   "
        f"{resultado['media_modelo']:.2%}"
    )
    print(
        f"Média baseline: "
        f"{resultado['media_baseline']:.2%}"
    )
    print(
        f"Ganho médio:    "
        f"{resultado['ganho_medio']:+.2%}"
    )
    print("=" * 60)


if __name__ == "__main__":
    exibir(executar())
