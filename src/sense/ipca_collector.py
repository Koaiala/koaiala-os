"""
KOAIALA SENSE
Coletor de IPCA

Responsabilidade:
- Consultar o IPCA no serviço SGS do Banco Central
- Identificar a última observação disponível
- Salvar a observação no PostgreSQL
- Evitar duplicação de dados
"""

import requests
from decimal import Decimal

from src.database.connection import get_connection


INDICATOR_CODE = "IPCA"
SGS_SERIES = "433"

API_URL = (
    f"https://api.bcb.gov.br/dados/serie/"
    f"bcdata.sgs.{SGS_SERIES}/dados"
)


def buscar_ipca():
    """
    Consulta a série do IPCA no SGS.
    """

    response = requests.get(
        API_URL,
        params={"formato": "json"},
        headers={
            "Accept": "application/json",
            "User-Agent": "Koaiala-Sense/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def obter_ultima_observacao(dados):
    """
    Retorna a observação mais recente da série.
    """

    if not dados:
        raise ValueError("A API não retornou observações.")

    ultima = dados[-1]

    data = ultima["data"]
    valor = ultima["valor"]

    return data, Decimal(valor.replace(",", "."))


def salvar_observacao(data, valor):
    """
    Salva uma observação do IPCA no PostgreSQL.

    A operação:
    - localiza o indicador cadastrado;
    - recupera seus metadados;
    - verifica duplicidade;
    - grava a observação;
    - mantém integridade com economic_indicators.
    """

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        # --------------------------------------------------
        # 1. LOCALIZA O INDICADOR E SEUS METADADOS
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                code,
                name,
                source,
                unit
            FROM economic_indicators
            WHERE code = %s
            """,
            (INDICATOR_CODE,)
        )

        indicador = cursor.fetchone()

        if indicador is None:
            raise ValueError(
                f"Indicador {INDICATOR_CODE} não encontrado "
                "em economic_indicators."
            )

        indicator_id = indicador[0]
        indicator_code = indicador[1]
        indicator_name = indicador[2]
        source = indicador[3]
        unit = indicador[4]

        # --------------------------------------------------
        # 2. VERIFICA SE A OBSERVAÇÃO JÁ EXISTE
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM economic_observations
            WHERE indicator_id = %s
              AND observation_date = %s
            """,
            (indicator_id, data)
        )

        existente = cursor.fetchone()

        if existente:
            print(
                f"Observação já existente: "
                f"{data} = {valor}{unit}"
            )
            return False

        # --------------------------------------------------
        # 3. INSERE NOVA OBSERVAÇÃO
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO economic_observations (
                indicator_code,
                indicator_name,
                source,
                observation_date,
                value,
                unit,
                indicator_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                indicator_code,
                indicator_name,
                source,
                data,
                valor,
                unit,
                indicator_id
            )
        )

        connection.commit()

        print(
            f"Observação salva: "
            f"{data} = {valor}{unit}"
        )

        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()

def coletar_ipca():
    """
    Executa o processo completo de coleta do IPCA.
    """

    print("=" * 60)
    print("KOAIALA SENSE - IPCA")
    print("=" * 60)

    print("\nConsultando SGS...")

    dados = buscar_ipca()

    data, valor = obter_ultima_observacao(dados)

    print(f"Data: {data}")
    print(f"Valor: {valor}% a.m.")
    print("Fonte: Banco Central / IBGE")

    salvar_observacao(data, valor)

    print("\nStatus: COLETADO ✓")
    print("=" * 60)


def main():
    coletar_ipca()


if __name__ == "__main__":
    main()