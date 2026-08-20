"""
KOAIALA PREDICTION 6.0

Walk-forward evaluation.

A estratégia é escolhida somente com base nas transições anteriores
ao corte. O período futuro nunca participa da escolha.

Estratégias:
- PERSISTENCIA
- BASELINE
- ROLLING_3
- ROLLING_5

O objetivo é medir se uma seleção adaptativa de estratégia supera
o baseline fora da amostra.
"""

from collections import Counter
from decimal import Decimal
from typing import Dict, List

from src.database.connection import get_connection
from src.backtest.backtest_v2 import INDICADORES


ESTRATEGIAS = [
    "PERSISTENCIA",
    "BASELINE",
    "ROLLING_3",
    "ROLLING_5",
]


def buscar(indicador: str):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT observation_date, value
            FROM economic_observations
            WHERE indicator_code = %s
            ORDER BY observation_date ASC
            """,
            (indicador,),
        )
        return cursor.fetchall()
    finally:
        connection.close()


def direcao(a: Decimal, b: Decimal) -> str:
    if b > a:
        return "ALTA"
    if b < a:
        return "QUEDA"
    return "ESTABILIDADE"


def frequente(valores: List[str]) -> str:
    if not valores:
        return "ESTABILIDADE"

    contagem = Counter(valores)
    ordem = ["ESTABILIDADE", "ALTA", "QUEDA"]

    return max(
        contagem,
        key=lambda x: (contagem[x], -ordem.index(x)),
    )


def previsao(
    estrategia: str,
    transicoes: List[str],
    ultima: str,
) -> str:

    if estrategia == "PERSISTENCIA":
        return ultima

    if estrategia == "BASELINE":
        return frequente(transicoes)

    if estrategia == "ROLLING_3":
        return frequente(transicoes[-3:])

    if estrategia == "ROLLING_5":
        return frequente(transicoes[-5:])

    return "ESTABILIDADE"


def avaliar(indicador: str) -> Dict:
    registros = buscar(indicador)

    if len(registros) < 7:
        return {
            "status": "INSUFICIENTE",
            "indicador": indicador,
        }

    resultados = []

    # Cada corte precisa de histórico suficiente para comparar estratégias.
    for i in range(6, len(registros) - 1):

        transicoes = [
            direcao(
                Decimal(str(registros[j - 1][1])),
                Decimal(str(registros[j][1])),
            )
            for j in range(1, i + 1)
        ]

        ultima = transicoes[-1]
        observado = direcao(
            Decimal(str(registros[i][1])),
            Decimal(str(registros[i + 1][1])),
        )

        # Seleção walk-forward:
        # usa apenas resultados anteriores ao corte.
        historico_estrategias = {
            estrategia: []
            for estrategia in ESTRATEGIAS
        }

        for h in range(6, i):
            transicoes_h = transicoes[:h]
            ultima_h = transicoes_h[-1]

            futuro_h = transicoes[h]

            for estrategia in ESTRATEGIAS:
                predicao_h = previsao(
                    estrategia,
                    transicoes_h,
                    ultima_h,
                )

                historico_estrategias[
                    estrategia
                ].append(
                    predicao_h == futuro_h
                )

        taxas = {}

        for estrategia, acertos in (
            historico_estrategias.items()
        ):
            taxas[estrategia] = (
                sum(acertos) / len(acertos)
                if acertos
                else 0.0
            )

        melhor = max(
            ESTRATEGIAS,
            key=lambda estrategia: (
                taxas[estrategia],
                -ESTRATEGIAS.index(estrategia),
            ),
        )

        predicao_modelo = previsao(
            melhor,
            transicoes,
            ultima,
        )

        predicao_baseline = previsao(
            "BASELINE",
            transicoes,
            ultima,
        )

        resultados.append(
            {
                "melhor_estrategia": melhor,
                "predicao_modelo": predicao_modelo,
                "predicao_baseline": predicao_baseline,
                "observado": observado,
                "acerto_modelo": (
                    predicao_modelo == observado
                ),
                "acerto_baseline": (
                    predicao_baseline == observado
                ),
            }
        )

    total = len(resultados)

    acertos_modelo = sum(
        x["acerto_modelo"]
        for x in resultados
    )

    acertos_baseline = sum(
        x["acerto_baseline"]
        for x in resultados
    )

    return {
        "status": "OK",
        "indicador": indicador,
        "total": total,
        "acertos_modelo": acertos_modelo,
        "acertos_baseline": acertos_baseline,
        "taxa_modelo": round(
            acertos_modelo / total,
            4,
        ),
        "taxa_baseline": round(
            acertos_baseline / total,
            4,
        ),
        "ganho": round(
            (acertos_modelo - acertos_baseline)
            / total,
            4,
        ),
        "avaliacoes": resultados,
    }


def executar() -> Dict:
    resultados = {}

    for indicador in INDICADORES:
        resultados[indicador] = avaliar(
            indicador
        )

    return {
        "status": "OK",
        "indicadores": resultados,
    }


def exibir(resultado: Dict):
    print("=" * 70)
    print("KOAIALA PREDICTION 6.0")
    print("=" * 70)
    print("WALK-FORWARD VALIDATION")
    print()

    for indicador, item in resultado["indicadores"].items():

        if item["status"] != "OK":
            print(
                f"{indicador}: "
                "DADOS INSUFICIENTES"
            )
            continue

        print(
            f"{indicador}: "
            f"MODELO={item['acertos_modelo']}/"
            f"{item['total']} "
            f"({item['taxa_modelo']:.2%}) | "
            f"BASELINE={item['acertos_baseline']}/"
            f"{item['total']} "
            f"({item['taxa_baseline']:.2%}) | "
            f"GANHO={item['ganho']:+.2%}"
        )

    print()
    print(
        "A seleção de estratégia foi feita "
        "somente com dados anteriores a cada corte."
    )
    print("=" * 70)


if __name__ == "__main__":
    exibir(executar())
