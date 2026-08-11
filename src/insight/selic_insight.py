from datetime import date
from decimal import Decimal

from src.database.connection import get_connection


def analisar_selic():
    """
    Analisa a série histórica da Selic Meta armazenada no PostgreSQL.

    Retorna:
        dict com os principais indicadores da análise.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
        WITH historico AS (
            SELECT
                observation_date,
                value,
                LAG(value) OVER (
                    ORDER BY observation_date
                ) AS valor_anterior
            FROM economic_observations
            WHERE indicator_code = 'SELIC_META'
        ),

        ultima_observacao AS (
            SELECT
                observation_date,
                value
            FROM historico
            ORDER BY observation_date DESC
            LIMIT 1
        ),

        ultima_mudanca AS (
            SELECT
                observation_date,
                valor_anterior,
                value
            FROM historico
            WHERE valor_anterior IS NOT NULL
              AND value <> valor_anterior
            ORDER BY observation_date DESC
            LIMIT 1
        ),

        total_mudancas AS (
            SELECT COUNT(*) AS quantidade
            FROM historico
            WHERE valor_anterior IS NOT NULL
              AND value <> valor_anterior
        )

        SELECT
            u.observation_date AS data_atual,
            u.value AS selic_atual,

            m.observation_date AS data_ultima_mudanca,
            m.valor_anterior,
            m.value AS valor_apos_mudanca,

            u.observation_date - m.observation_date
                AS dias_no_nivel,

            t.quantidade AS total_mudancas

        FROM ultima_observacao u
        CROSS JOIN ultima_mudanca m
        CROSS JOIN total_mudancas t;
        """

        cursor.execute(query)

        resultado = cursor.fetchone()

        if not resultado:
            raise RuntimeError(
                "Não foi possível obter dados da Selic."
            )

        (
            data_atual,
            selic_atual,
            data_ultima_mudanca,
            valor_anterior,
            valor_apos_mudanca,
            dias_no_nivel,
            total_mudancas
        ) = resultado

        if valor_apos_mudanca > valor_anterior:
            tendencia = "ALTA"

        elif valor_apos_mudanca < valor_anterior:
            tendencia = "QUEDA"

        else:
            tendencia = "ESTÁVEL"

        variacao_ultima_mudanca = (
            valor_apos_mudanca - valor_anterior
        )

        return {
            "data_atual": data_atual,
            "selic_atual": Decimal(selic_atual),
            "data_ultima_mudanca": data_ultima_mudanca,
            "valor_anterior": Decimal(valor_anterior),
            "valor_apos_mudanca": Decimal(valor_apos_mudanca),
            "dias_no_nivel": dias_no_nivel,
            "total_mudancas": total_mudancas,
            "tendencia": tendencia,
            "variacao_ultima_mudanca": Decimal(
                variacao_ultima_mudanca
            ),
        }

    finally:
        connection.close()


def exibir_insight():
    """
    Exibe a análise da Selic no terminal.
    """

    resultado = analisar_selic()

    print("=" * 60)
    print("KOAIALA INSIGHT")
    print("=" * 60)

    print("Indicador: SELIC META")

    print(
        f"Taxa atual: "
        f"{resultado['selic_atual']:.2f}% a.a."
    )

    print(
        f"Última alteração: "
        f"{resultado['data_ultima_mudanca'].strftime('%d/%m/%Y')}"
    )

    print(
        f"Taxa anterior: "
        f"{resultado['valor_anterior']:.2f}% a.a."
    )

    print(
        f"Taxa após alteração: "
        f"{resultado['valor_apos_mudanca']:.2f}% a.a."
    )

    print(
        f"Variação: "
        f"{resultado['variacao_ultima_mudanca']:+.2f} p.p."
    )

    print(
        f"Dias no nível atual: "
        f"{resultado['dias_no_nivel']}"
    )

    print(
        f"Mudanças identificadas: "
        f"{resultado['total_mudancas']}"
    )

    print(
        f"Tendência da última mudança: "
        f"{resultado['tendencia']}"
    )

    print("=" * 60)


if __name__ == "__main__":
    exibir_insight()