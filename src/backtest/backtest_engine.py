"""
KOAIALA BACKTEST ENGINE

Valida a direção histórica dos indicadores sem usar dados posteriores
ao ponto de corte. O núcleo 1.0 permanece intocado.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from src.database.connection import get_connection

INDICADORES = ["SELIC_META", "IPCA", "IGP_M", "INPC"]


def _buscar_registros(indicator_code: str):
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
            (indicator_code,),
        )

        return cursor.fetchall()

    finally:
        connection.close()


def _direcao(valor_anterior: Decimal, valor_atual: Decimal) -> str:
    if valor_atual > valor_anterior:
        return "ALTA"

    if valor_atual < valor_anterior:
        return "QUEDA"

    return "ESTABILIDADE"


def avaliar_indicador(indicator_code: str) -> Dict:
    registros = _buscar_registros(indicator_code)

    if len(registros) < 3:
        return {
            "status": "INSUFICIENTE",
            "indicador": indicator_code,
            "observacoes": len(registros),
            "avaliacoes": [],
        }

    avaliacoes: List[Dict] = []

    for indice in range(1, len(registros) - 1):

        _, valor_anterior = registros[indice - 1]
        data_corte, valor_corte = registros[indice]
        data_resultado, valor_resultado = registros[indice + 1]

        valor_anterior = Decimal(str(valor_anterior))
        valor_corte = Decimal(str(valor_corte))
        valor_resultado = Decimal(str(valor_resultado))

        direcao_prevista = _direcao(
            valor_anterior,
            valor_corte,
        )

        direcao_observada = _direcao(
            valor_corte,
            valor_resultado,
        )

        avaliacoes.append(
            {
                "data_corte": data_corte,
                "data_resultado": data_resultado,
                "valor_corte": valor_corte,
                "valor_resultado": valor_resultado,
                "direcao_prevista": direcao_prevista,
                "direcao_observada": direcao_observada,
                "acerto": (
                    direcao_prevista
                    == direcao_observada
                ),
            }
        )

    acertos = sum(
        1
        for avaliacao in avaliacoes
        if avaliacao["acerto"]
    )

    total = len(avaliacoes)

    return {
        "status": "OK",
        "indicador": indicator_code,
        "observacoes": len(registros),
        "avaliacoes": avaliacoes,
        "acertos": acertos,
        "erros": total - acertos,
        "total_avaliacoes": total,
        "taxa_acerto": (
            round(acertos / total, 4)
            if total
            else 0.0
        ),
    }


def executar_backtest(
    indicadores: Optional[List[str]] = None,
) -> Dict:

    indicadores = indicadores or INDICADORES

    resultados = {}

    total_avaliacoes = 0
    total_acertos = 0

    for indicador in indicadores:

        resultado = avaliar_indicador(
            indicador
        )

        resultados[indicador] = resultado

        if resultado["status"] == "OK":

            total_avaliacoes += (
                resultado["total_avaliacoes"]
            )

            total_acertos += (
                resultado["acertos"]
            )

    taxa = (
        total_acertos / total_avaliacoes
        if total_avaliacoes
        else 0.0
    )

    return {
        "status": "OK",
        "indicadores": resultados,
        "total_avaliacoes": total_avaliacoes,
        "acertos": total_acertos,
        "erros": (
            total_avaliacoes
            - total_acertos
        ),
        "taxa_acerto_agregada": round(
            taxa,
            4,
        ),
    }


def exibir_resultado(
    resultado: Dict,
) -> None:

    print("=" * 60)
    print("KOAIALA BACKTEST ENGINE")
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
            f"{item['total_avaliacoes']} "
            f"| taxa="
            f"{item['taxa_acerto']:.2%}"
        )

    print("-" * 60)

    print(
        f"AGREGADO: "
        f"{resultado['acertos']}/"
        f"{resultado['total_avaliacoes']} "
        f"| taxa="
        f"{resultado['taxa_acerto_agregada']:.2%}"
    )

    print("=" * 60)


def main():

    resultado = executar_backtest()

    exibir_resultado(
        resultado
    )


if __name__ == "__main__":
    main()
