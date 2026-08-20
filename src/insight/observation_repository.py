"""
KOAIALA
OBSERVATION REPOSITORY

Camada responsável pela leitura das observações
econômicas armazenadas no PostgreSQL.

Responsabilidades:

- Buscar observações por indicador.
- Buscar a observação mais recente.
- Buscar histórico de um indicador.
- Buscar múltiplos indicadores.
- Isolar o restante do sistema dos detalhes SQL.

Esta camada NÃO:

- coleta dados externos;
- calcula indicadores;
- interpreta movimentos econômicos;
- calcula Economic Score;
- gera cenários.

Ela apenas fornece dados confiáveis para as
camadas superiores do Koaiala.
"""

from typing import Dict, List, Optional

from src.database.connection import get_connection


# ============================================================
# OBSERVAÇÕES DE UM INDICADOR
# ============================================================

def get_observations(
    indicator_code: str,
    limit: Optional[int] = None,
) -> List[Dict]:
    """
    Retorna observações de um indicador.

    As observações são ordenadas da mais recente
    para a mais antiga.

    Parâmetros:

        indicator_code:
            Código do indicador no Registry.

        limit:
            Quantidade máxima de observações.
            Se None, retorna todas.

    Retorno:

        Lista de dicionários.
    """

    connection = get_connection()

    cursor = None

    try:

        cursor = connection.cursor()

        query = """
            SELECT
                id,
                indicator_code,
                indicator_name,
                source,
                source_series,
                observation_date,
                value,
                unit,
                collected_at,
                created_at,
                indicator_id
            FROM economic_observations
            WHERE indicator_code = %s
            ORDER BY observation_date DESC
        """

        params = [indicator_code]

        if limit is not None:

            if limit <= 0:
                return []

            query += " LIMIT %s"

            params.append(limit)

        cursor.execute(
            query,
            tuple(params)
        )

        rows = cursor.fetchall()

        columns = [
            "id",
            "indicator_code",
            "indicator_name",
            "source",
            "source_series",
            "observation_date",
            "value",
            "unit",
            "collected_at",
            "created_at",
            "indicator_id",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()


# ============================================================
# OBSERVAÇÃO MAIS RECENTE
# ============================================================

def get_latest_observation(
    indicator_code: str,
) -> Optional[Dict]:
    """
    Retorna a observação mais recente de um indicador.

    Retorno:

        Dicionário com a observação mais recente.

        None caso não exista nenhuma observação.
    """

    observacoes = get_observations(
        indicator_code=indicator_code,
        limit=1,
    )

    if not observacoes:
        return None

    return observacoes[0]


# ============================================================
# HISTÓRICO
# ============================================================

def get_history(
    indicator_code: str,
    limit: int = 12,
) -> List[Dict]:
    """
    Retorna o histórico recente de um indicador.

    Por padrão, retorna as últimas 12 observações.

    A ordem é da mais recente para a mais antiga.
    """

    return get_observations(
        indicator_code=indicator_code,
        limit=limit,
    )


# ============================================================
# ÚLTIMO VALOR
# ============================================================

def get_latest_value(
    indicator_code: str,
):
    """
    Retorna somente o valor da observação mais recente.

    Retorno:

        Decimal ou None.
    """

    observacao = get_latest_observation(
        indicator_code
    )

    if observacao is None:
        return None

    return observacao["value"]


# ============================================================
# ÚLTIMA DATA
# ============================================================

def get_latest_date(
    indicator_code: str,
):
    """
    Retorna a data da observação mais recente.

    Retorno:

        date ou None.
    """

    observacao = get_latest_observation(
        indicator_code
    )

    if observacao is None:
        return None

    return observacao["observation_date"]


# ============================================================
# MÚLTIPLOS INDICADORES
# ============================================================

def get_latest_observations(
    indicator_codes: List[str],
) -> Dict[str, Optional[Dict]]:
    """
    Retorna a observação mais recente de vários indicadores.

    Exemplo:

        {
            "IPCA": {...},
            "INPC": {...},
            "IGP_M": {...}
        }
    """

    resultado = {}

    for codigo in indicator_codes:

        resultado[codigo] = get_latest_observation(
            codigo
        )

    return resultado


# ============================================================
# CONTAGEM DE OBSERVAÇÕES
# ============================================================

def count_observations(
    indicator_code: str,
) -> int:
    """
    Retorna a quantidade de observações armazenadas
    para determinado indicador.
    """

    connection = get_connection()

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM economic_observations
            WHERE indicator_code = %s
            """,
            (indicator_code,)
        )

        resultado = cursor.fetchone()

        return int(resultado[0])

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()


# ============================================================
# TESTE
# ============================================================

def main():

    print("=" * 60)
    print("KOAIALA OBSERVATION REPOSITORY")
    print("=" * 60)

    # --------------------------------------------------------
    # Teste IPCA
    # --------------------------------------------------------

    print()
    print("INDICADOR: IPCA")

    observacao = get_latest_observation(
        "IPCA"
    )

    print(
        f"Última observação: "
        f"{observacao}"
    )

    # --------------------------------------------------------
    # Teste INPC
    # --------------------------------------------------------

    print()
    print("INDICADOR: INPC")

    observacao = get_latest_observation(
        "INPC"
    )

    print(
        f"Última observação: "
        f"{observacao}"
    )

    # --------------------------------------------------------
    # Teste histórico
    # --------------------------------------------------------

    print()
    print("HISTÓRICO IPCA")

    historico = get_history(
        "IPCA",
        limit=3,
    )

    for observacao in historico:

        print(
            f"{observacao['observation_date']} "
            f"= "
            f"{observacao['value']}"
        )

    # --------------------------------------------------------
    # Teste contagem
    # --------------------------------------------------------

    print()
    print("CONTAGEM")

    quantidade = count_observations(
        "IPCA"
    )

    print(
        f"IPCA: {quantidade} observações"
    )

    print()
    print("=" * 60)
    print("REPOSITORY FUNCIONANDO ✓")
    print("=" * 60)


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()