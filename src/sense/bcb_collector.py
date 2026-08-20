"""
KOAIALA SENSE
BCB COLLECTOR

Collector específico para a Meta Selic.

Responsabilidades:

- consultar a série histórica da Selic Meta no BCB;
- validar cada observação através do Economic Validator;
- salvar observações no PostgreSQL;
- evitar duplicidades;
- retornar um resultado padronizado para o Collector Engine.

O Collector Engine define QUANDO executar.
Este collector define COMO coletar a Selic Meta.
"""

import requests

from datetime import date, datetime

from src.database.connection import get_connection
from src.validator.economic_validator import (
    validate_selic_observation,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BCB_URL = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.432/dados"
)

INDICATOR_CODE = "SELIC_META"
INDICATOR_NAME = "Selic Meta"
SOURCE = "Banco Central do Brasil"
SOURCE_SERIES = "432"
UNIT = "% a.a."

DATA_INICIAL_HISTORICA = "01/01/2026"


# ============================================================
# CONSULTA AO BANCO CENTRAL
# ============================================================

def get_selic_history(
    data_inicial,
    data_final,
):
    """
    Coleta a série histórica da Meta Selic
    dentro de um período específico.

    Parâmetros
    ----------
    data_inicial : str
        Data inicial no formato DD/MM/YYYY.

    data_final : str
        Data final no formato DD/MM/YYYY.

    Retorno
    -------
    list
        Lista de observações retornadas pelo BCB.
    """

    headers = {
        "User-Agent": "Koaiala-OS/0.1",
        "Accept": "application/json",
    }

    params = {
        "formato": "json",
        "dataInicial": data_inicial,
        "dataFinal": data_final,
    }

    response = requests.get(
        BCB_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    dados = response.json()

    if not isinstance(dados, list):
        raise ValueError(
            "Resposta inesperada recebida do Banco Central."
        )

    return dados


# ============================================================
# CONVERSÃO DE DATA
# ============================================================

def convert_observation_date(data):
    """
    Converte DD/MM/AAAA para objeto date.
    """

    if not data:
        raise ValueError(
            "Data da observação não informada."
        )

    return datetime.strptime(
        data,
        "%d/%m/%Y",
    ).date()


# ============================================================
# SALVAMENTO DA OBSERVAÇÃO
# ============================================================

def save_observation(observation):
    """
    Salva uma observação no PostgreSQL.

    A proteção contra duplicidade é realizada
    pelo PostgreSQL através da restrição:

        uq_economic_observation

    sobre:

        indicator_code
        observation_date

    Retorna
    -------

    True
        Registro inserido.

    False
        Registro já existente.
    """

    connection = get_connection()

    cursor = None

    try:

        query = """
            INSERT INTO economic_observations (
                indicator_code,
                indicator_name,
                source,
                source_series,
                observation_date,
                value,
                unit
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (
                indicator_code,
                observation_date
            )
            DO NOTHING
        """

        observation_date = convert_observation_date(
            observation["data"]
        )

        values = (
            INDICATOR_CODE,
            INDICATOR_NAME,
            SOURCE,
            SOURCE_SERIES,
            observation_date,
            observation["valor"],
            UNIT,
        )

        cursor = connection.cursor()

        cursor.execute(
            query,
            values,
        )

        connection.commit()

        return cursor.rowcount == 1

    except Exception:

        connection.rollback()

        raise

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()


# ============================================================
# COLLECTOR
# ============================================================

def coletar(indicador=None):
    """
    Interface padronizada do Collector Engine.

    Executa a coleta histórica da Selic Meta.

    O parâmetro indicador é opcional porque este é um
    collector específico.

    Isso permite que o collector seja executado tanto:

        coletar()

    quanto:

        coletar(indicador)
    """

    return main()


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    """
    Executa a coleta histórica da Selic Meta.

    Retorna um dicionário padronizado para o
    Collector Engine.
    """

    print("=" * 60)
    print("KOAIALA SENSE")
    print("COLETA HISTÓRICA — SELIC META")
    print("=" * 60)

    # --------------------------------------------------------
    # PERÍODO DA COLETA
    # --------------------------------------------------------

    data_inicial = DATA_INICIAL_HISTORICA

    data_final = date.today().strftime(
        "%d/%m/%Y"
    )

    print(
        f"Período: "
        f"{data_inicial} até {data_final}"
    )

    print(
        f"Fonte: {SOURCE}"
    )

    print()

    # --------------------------------------------------------
    # CONSULTA
    # --------------------------------------------------------

    dados = get_selic_history(
        data_inicial,
        data_final,
    )

    if not dados:

        print(
            "Nenhuma observação encontrada."
        )

        print("=" * 60)

        return {
            "status": "OK",
            "indicador": INDICATOR_CODE,
            "serie": SOURCE_SERIES,
            "frequencia": "DIARIA",
            "observacoes_recebidas": 0,
            "aprovados": 0,
            "rejeitados": 0,
            "novos": 0,
            "existentes": 0,
        }

    print(
        f"Observações recebidas: "
        f"{len(dados)}"
    )

    # --------------------------------------------------------
    # CONTADORES
    # --------------------------------------------------------

    aprovados = 0
    rejeitados = 0
    salvos = 0
    duplicados = 0

    # --------------------------------------------------------
    # PROCESSAMENTO DAS OBSERVAÇÕES
    # --------------------------------------------------------

    total = len(dados)

    for numero, observacao in enumerate(
        dados,
        start=1,
    ):

        valido, erros = (
            validate_selic_observation(
                observacao
            )
        )

        if not valido:

            rejeitados += 1

            print(
                f"[{numero}/{total}] "
                f"REJEITADO | "
                f"{observacao.get('data')} | "
                f"{erros}"
            )

            continue

        aprovados += 1

        salvo = save_observation(
            observacao
        )

        data_observacao = (
            observacao.get("data")
        )

        if salvo:

            salvos += 1

            print(
                f"[{numero}/{total}] "
                f"SALVO | "
                f"{data_observacao} | "
                f"{observacao.get('valor')}"
            )

        else:

            duplicados += 1

            print(
                f"[{numero}/{total}] "
                f"EXISTENTE | "
                f"{data_observacao} | "
                f"{observacao.get('valor')}"
            )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RESUMO DA COLETA")
    print("=" * 60)

    print(
        f"Observações recebidas: "
        f"{len(dados)}"
    )

    print(
        f"Aprovadas pelo Validator: "
        f"{aprovados}"
    )

    print(
        f"Rejeitadas: "
        f"{rejeitados}"
    )

    print(
        f"Novos registros salvos: "
        f"{salvos}"
    )

    print(
        f"Registros já existentes: "
        f"{duplicados}"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # RETORNO PADRONIZADO
    # --------------------------------------------------------

    return {
        "status": "OK",
        "indicador": INDICATOR_CODE,
        "serie": SOURCE_SERIES,
        "frequencia": "DIARIA",
        "observacoes_recebidas": len(dados),
        "aprovados": aprovados,
        "rejeitados": rejeitados,
        "novos": salvos,
        "existentes": duplicados,
    }


# ============================================================
# TESTE DIRETO
# ============================================================

if __name__ == "__main__":
    resultado = main()

    print()
    print(
        "RETORNO DO BCB COLLECTOR:"
    )

    print(
        repr(resultado)
    )