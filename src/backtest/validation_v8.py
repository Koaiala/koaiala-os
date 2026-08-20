"""
KOAIALA VALIDATION 8.0

Validação rigorosa do Prediction 7.0:
- acurácia;
- baseline;
- ganho;
- desempenho por direção;
- matriz de confusão;
- blocos temporais;
- consistência do ganho.

Não altera o motor de produção.
"""

from collections import Counter, defaultdict

from src.backtest.prediction_v7 import avaliar
from src.backtest.backtest_v2 import INDICADORES


DIRECOES = ["ALTA", "QUEDA", "ESTABILIDADE"]


def matriz(avaliacoes):
    matriz = {
        prevista: {
            observada: 0
            for observada in DIRECOES
        }
        for prevista in DIRECOES
    }

    for item in avaliacoes:
        matriz[
            item["previsao"]
        ][
            item["observado"]
        ] += 1

    return matriz


def blocos(avaliacoes, quantidade=4):
    n = len(avaliacoes)

    if n == 0:
        return []

    tamanho = max(1, n // quantidade)
    resultado = []

    inicio = 0

    while inicio < n:
        fim = min(
            n,
            inicio + tamanho,
        )

        grupo = avaliacoes[inicio:fim]

        acertos = sum(
            x["acerto"]
            for x in grupo
        )

        baseline = sum(
            x["acerto_baseline"]
            for x in grupo
        )

        total = len(grupo)

        resultado.append(
            {
                "inicio": inicio + 1,
                "fim": inicio + total,
                "total": total,
                "modelo": (
                    acertos / total
                ),
                "baseline": (
                    baseline / total
                ),
                "ganho": (
                    acertos - baseline
                ) / total,
            }
        )

        inicio = fim

    return resultado


def avaliar_indicador(indicador):
    item = avaliar(indicador)

    if item["status"] != "OK":
        return item

    avaliacoes = item["avaliacoes"]

    modelo = item["taxa"]
    baseline = item["taxa_baseline"]

    ganhos = [
        int(x["acerto"])
        - int(x["acerto_baseline"])
        for x in avaliacoes
    ]

    media_ganho = (
        sum(ganhos) / len(ganhos)
        if ganhos
        else 0.0
    )

    # Ganho positivo em número de avaliações.
    vit_modelo = sum(
        1 for x in ganhos
        if x > 0
    )

    vit_baseline = sum(
        1 for x in ganhos
        if x < 0
    )

    empates = sum(
        1 for x in ganhos
        if x == 0
    )

    return {
        **item,
        "matriz": matriz(
            avaliacoes
        ),
        "blocos": blocos(
            avaliacoes
        ),
        "ganho_medio": media_ganho,
        "modelo_vence": vit_modelo,
        "baseline_vence": vit_baseline,
        "empates": empates,
    }


def executar():
    indicadores = {}

    for indicador in INDICADORES:
        indicadores[indicador] = (
            avaliar_indicador(indicador)
        )

    return {
        "status": "OK",
        "indicadores": indicadores,
    }


def exibir(resultado):
    print("=" * 72)
    print("KOAIALA VALIDATION 8.0")
    print("=" * 72)
    print("VALIDAÇÃO RIGOROSA DO PREDICTION 7.0")
    print()

    for indicador, item in (
        resultado["indicadores"].items()
    ):

        if item["status"] != "OK":
            print(
                f"{indicador}: "
                "DADOS INSUFICIENTES"
            )
            continue

        print(indicador)
        print(
            f"  Modelo:   "
            f"{item['acertos']}/"
            f"{item['total']} "
            f"| {item['taxa']:.2%}"
        )
        print(
            f"  Baseline: "
            f"{item['acertos_baseline']}/"
            f"{item['total']} "
            f"| {item['taxa_baseline']:.2%}"
        )
        print(
            f"  Ganho:    "
            f"{item['ganho']:+.2%}"
        )
        print(
            f"  Modelo vence: "
            f"{item['modelo_vence']} | "
            f"Baseline vence: "
            f"{item['baseline_vence']} | "
            f"Empates: "
            f"{item['empates']}"
        )

        print("  MATRIZ:")
        for prevista in DIRECOES:
            print(
                f"    {prevista}: "
                f"{item['matriz'][prevista]}"
            )

        print("  BLOCOS TEMPORAIS:")

        for bloco in item["blocos"]:
            print(
                f"    {bloco['inicio']:>3}-"
                f"{bloco['fim']:<3}: "
                f"modelo={bloco['modelo']:.2%} | "
                f"baseline={bloco['baseline']:.2%} | "
                f"ganho={bloco['ganho']:+.2%}"
            )

        print()

    print("=" * 72)
    print(
        "STATUS FINAL: "
        "KOAIALA VALIDATION 8.0 EXECUTADA ✓"
    )
    print("=" * 72)


if __name__ == "__main__":
    exibir(executar())
