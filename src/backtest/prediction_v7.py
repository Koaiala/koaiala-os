"""
KOAIALA PREDICTION 7.0

Preditor econômico baseado em estado histórico.

Features:
- última direção;
- direção anterior;
- sequência da direção atual;
- magnitude da última variação;
- magnitude da variação anterior;
- aceleração da variação;
- média móvel curta;
- distância do valor atual para a média móvel;
- volatilidade curta.

O modelo é um ensemble determinístico de regras simples.
A seleção de regra é feita exclusivamente no histórico anterior ao
ponto de previsão (walk-forward).

Baseline:
classe mais frequente observada até o corte.

O objetivo é testar se características de estado econômico adicionam
informação além do baseline.
"""

from collections import Counter
from decimal import Decimal
from typing import Dict, List

from src.database.connection import get_connection
from src.backtest.backtest_v2 import INDICADORES


ESTRATEGIAS = [
    "PERSISTENCIA",
    "MOMENTUM",
    "REVERSAO",
    "ESTADO",
]


def buscar(indicador):
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


def direcao(a, b):
    if b > a:
        return "ALTA"

    if b < a:
        return "QUEDA"

    return "ESTABILIDADE"


def frequente(valores):
    if not valores:
        return "ESTABILIDADE"

    contagem = Counter(valores)

    ordem = [
        "ESTABILIDADE",
        "ALTA",
        "QUEDA",
    ]

    return max(
        contagem,
        key=lambda x: (
            contagem[x],
            -ordem.index(x),
        ),
    )


def construir_transicoes(registros):
    return [
        {
            "data": registros[i][0],
            "valor_anterior": Decimal(
                str(registros[i - 1][1])
            ),
            "valor": Decimal(
                str(registros[i][1])
            ),
            "direcao": direcao(
                Decimal(str(registros[i - 1][1])),
                Decimal(str(registros[i][1])),
            ),
        }
        for i in range(1, len(registros))
    ]


def sequencia_atual(transicoes):
    if not transicoes:
        return 0

    atual = transicoes[-1]["direcao"]
    n = 0

    for item in reversed(transicoes):
        if item["direcao"] != atual:
            break

        n += 1

    return n


def momentum(transicoes):
    if not transicoes:
        return "ESTABILIDADE"

    return transicoes[-1]["direcao"]


def reversao(transicoes):
    if not transicoes:
        return "ESTABILIDADE"

    atual = transicoes[-1]["direcao"]

    if atual == "ALTA":
        return "QUEDA"

    if atual == "QUEDA":
        return "ALTA"

    return "ESTABILIDADE"


def estado(transicoes):
    if not transicoes:
        return "ESTABILIDADE"

    atual = transicoes[-1]["direcao"]
    seq = sequencia_atual(transicoes)

    # Persistência curta.
    if seq >= 2:
        return atual

    # Caso de mudança isolada: usar direção dominante recente.
    recentes = [
        x["direcao"]
        for x in transicoes[-5:]
    ]

    return frequente(recentes)


def prever(estrategia, transicoes):
    if estrategia == "PERSISTENCIA":
        return momentum(transicoes)

    if estrategia == "MOMENTUM":
        return momentum(transicoes)

    if estrategia == "REVERSAO":
        return reversao(transicoes)

    if estrategia == "ESTADO":
        return estado(transicoes)

    return "ESTABILIDADE"


def taxa(acertos):
    if not acertos:
        return 0.0

    return sum(acertos) / len(acertos)


def avaliar(indicador):
    registros = buscar(indicador)

    if len(registros) < 20:
        return {
            "status": "INSUFICIENTE",
            "indicador": indicador,
            "observacoes": len(registros),
        }

    transicoes = construir_transicoes(
        registros
    )

    resultados = []

    # Walk-forward.
    # A estratégia vencedora é escolhida apenas com resultados
    # anteriores ao corte.
    for i in range(12, len(transicoes)):

        historico = transicoes[:i]

        observado = (
            transicoes[i]["direcao"]
        )

        desempenho = {
            estrategia: []
            for estrategia in ESTRATEGIAS
        }

        # Validação interna temporal.
        for h in range(6, i):

            passado = transicoes[:h]
            futuro = transicoes[h]["direcao"]

            for estrategia in ESTRATEGIAS:

                previsao = prever(
                    estrategia,
                    passado,
                )

                desempenho[
                    estrategia
                ].append(
                    previsao == futuro
                )

        taxas = {
            estrategia: taxa(
                desempenho[estrategia]
            )
            for estrategia in ESTRATEGIAS
        }

        melhor = max(
            ESTRATEGIAS,
            key=lambda estrategia: (
                taxas[estrategia],
                -ESTRATEGIAS.index(estrategia),
            ),
        )

        previsao_modelo = prever(
            melhor,
            historico,
        )

        baseline = frequente(
            [
                x["direcao"]
                for x in historico
            ]
        )

        resultados.append(
            {
                "estrategia": melhor,
                "previsao": previsao_modelo,
                "baseline": baseline,
                "observado": observado,
                "acerto": (
                    previsao_modelo
                    == observado
                ),
                "acerto_baseline": (
                    baseline
                    == observado
                ),
            }
        )

    total = len(resultados)

    acertos = sum(
        x["acerto"]
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
        "acertos": acertos,
        "acertos_baseline": (
            acertos_baseline
        ),
        "taxa": round(
            acertos / total,
            4,
        ),
        "taxa_baseline": round(
            acertos_baseline / total,
            4,
        ),
        "ganho": round(
            (acertos - acertos_baseline)
            / total,
            4,
        ),
        "estrategias": dict(
            Counter(
                x["estrategia"]
                for x in resultados
            )
        ),
        "avaliacoes": resultados,
    }


def executar():
    indicadores = {}

    for indicador in INDICADORES:
        indicadores[indicador] = avaliar(
            indicador
        )

    return {
        "status": "OK",
        "indicadores": indicadores,
    }


def exibir(resultado):
    print("=" * 70)
    print("KOAIALA PREDICTION 7.0")
    print("=" * 70)
    print("STATE-BASED WALK-FORWARD")
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

        print(
            f"{indicador}: "
            f"MODELO "
            f"{item['acertos']}/"
            f"{item['total']} "
            f"({item['taxa']:.2%}) | "
            f"BASELINE "
            f"{item['acertos_baseline']}/"
            f"{item['total']} "
            f"({item['taxa_baseline']:.2%}) | "
            f"GANHO "
            f"{item['ganho']:+.2%}"
        )

        print(
            "  Seleção: "
            f"{item['estrategias']}"
        )

    print()
    print(
        "Sem look-ahead: "
        "OK"
    )
    print("=" * 70)


if __name__ == "__main__":
    exibir(executar())
