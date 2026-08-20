"""
KOAIALA BACKTEST 2.0

Validação temporal sem look-ahead.

Para cada indicador, cada ponto de corte usa somente a observação
imediatamente anterior e a observação do corte para produzir uma
direção. O próximo registro é usado exclusivamente como resultado
observado.

Também separa acertos por indicador e por direção prevista.
"""

from decimal import Decimal
from typing import Dict, List

from src.database.connection import get_connection


INDICADORES = [
    "SELIC_META",
    "IPCA",
    "IGP_M",
    "INPC",
]


def buscar_registros(indicador: str):
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


def direcao(anterior: Decimal, atual: Decimal) -> str:

    if atual > anterior:
        return "ALTA"

    if atual < anterior:
        return "QUEDA"

    return "ESTABILIDADE"


def avaliar_indicador(indicador: str) -> Dict:

    registros = buscar_registros(indicador)

    if len(registros) < 3:

        return {
            "status": "INSUFICIENTE",
            "indicador": indicador,
            "observacoes": len(registros),
            "avaliacoes": [],
        }

    avaliacoes: List[Dict] = []

    for i in range(1, len(registros) - 1):

        data_anterior, valor_anterior = registros[i - 1]
        data_corte, valor_corte = registros[i]
        data_resultado, valor_resultado = registros[i + 1]

        valor_anterior = Decimal(
            str(valor_anterior)
        )

        valor_corte = Decimal(
            str(valor_corte)
        )

        valor_resultado = Decimal(
            str(valor_resultado)
        )

        prevista = direcao(
            valor_anterior,
            valor_corte,
        )

        observada = direcao(
            valor_corte,
            valor_resultado,
        )

        avaliacoes.append(
            {
                "data_corte": data_corte,
                "data_resultado": data_resultado,
                "prevista": prevista,
                "observada": observada,
                "acerto": prevista == observada,
            }
        )

    total = len(avaliacoes)

    acertos = sum(
        1
        for item in avaliacoes
        if item["acerto"]
    )

    por_direcao = {}

    for sinal in (
        "ALTA",
        "QUEDA",
        "ESTABILIDADE",
    ):

        subset = [
            item
            for item in avaliacoes
            if item["prevista"] == sinal
        ]

        total_sinal = len(subset)

        acertos_sinal = sum(
            1
            for item in subset
            if item["acerto"]
        )

        por_direcao[sinal] = {
            "total": total_sinal,
            "acertos": acertos_sinal,
            "erros": total_sinal - acertos_sinal,
            "taxa": (
                round(
                    acertos_sinal / total_sinal,
                    4,
                )
                if total_sinal
                else None
            ),
        }

    return {
        "status": "OK",
        "indicador": indicador,
        "observacoes": len(registros),
        "avaliacoes": avaliacoes,
        "total": total,
        "acertos": acertos,
        "erros": total - acertos,
        "taxa": (
            round(acertos / total, 4)
            if total
            else 0.0
        ),
        "por_direcao": por_direcao,
    }


def executar() -> Dict:

    resultados = {}

    total = 0
    acertos = 0

    for indicador in INDICADORES:

        resultado = avaliar_indicador(
            indicador
        )

        resultados[indicador] = resultado

        if resultado["status"] == "OK":

            total += resultado["total"]
            acertos += resultado["acertos"]

    return {
        "status": "OK",
        "indicadores": resultados,
        "total": total,
        "acertos": acertos,
        "erros": total - acertos,
        "taxa": (
            round(acertos / total, 4)
            if total
            else 0.0
        ),
    }


def exibir(resultado: Dict):

    print("=" * 60)
    print("KOAIALA BACKTEST 2.0")
    print("=" * 60)

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
            f"{item['acertos']}/"
            f"{item['total']} "
            f"| taxa={item['taxa']:.2%}"
        )

        for sinal, dados in (
            item["por_direcao"].items()
        ):

            if dados["total"]:

                print(
                    f"  {sinal}: "
                    f"{dados['acertos']}/"
                    f"{dados['total']} "
                    f"| "
                    f"{dados['taxa']:.2%}"
                )

    print("-" * 60)

    print(
        f"TOTAL: "
        f"{resultado['acertos']}/"
        f"{resultado['total']} "
        f"| taxa={resultado['taxa']:.2%}"
    )

    print("=" * 60)


if __name__ == "__main__":
    exibir(executar())
