import requests

from datetime import date, datetime

from src.database.connection import get_connection
from src.validator.economic_validator import validate_selic_observation


BCB_URL = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.432/dados"
)


def get_selic_history(data_inicial, data_final):
    """
    Coleta a série histórica da Meta Selic
    dentro de um período específico.
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

    return response.json()


def convert_observation_date(data):
    """
    Converte DD/MM/AAAA para objeto date.
    """

    return datetime.strptime(
        data,
        "%d/%m/%Y"
    ).date()


def save_observation(observation):
    """
    Salva uma observação no PostgreSQL.

    Retorna:

        True  -> registro inserido
        False -> registro já existia
    """

    connection = get_connection()

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
        ON CONFLICT (indicator_code, observation_date)
        DO NOTHING
    """

    observation_date = convert_observation_date(
        observation["data"]
    )

    values = (
        "SELIC_META",
        "Selic Meta",
        "Banco Central do Brasil",
        "432",
        observation_date,
        observation["valor"],
        "% a.a.",
    )

    cursor = connection.cursor()

    cursor.execute(query, values)

    connection.commit()

    salvo = cursor.rowcount == 1

    cursor.close()
    connection.close()

    return salvo


def main():

    print("=" * 60)
    print("KOAIALA SENSE")
    print("COLETA HISTÓRICA — SELIC META")
    print("=" * 60)

    # --------------------------------------------------
    # PERÍODO DA COLETA
    # --------------------------------------------------

    data_inicial = "01/01/2026"

    data_final = date.today().strftime("%d/%m/%Y")

    print(f"Período: {data_inicial} até {data_final}")
    print("Fonte: Banco Central do Brasil")
    print()

    try:

        dados = get_selic_history(
            data_inicial,
            data_final
        )

        if not dados:

            print("Nenhuma observação encontrada.")
            print("=" * 60)

            return

        print(
            f"Observações recebidas: {len(dados)}"
        )

        aprovados = 0
        rejeitados = 0
        salvos = 0
        duplicados = 0

        # --------------------------------------------------
        # PROCESSAMENTO DAS OBSERVAÇÕES
        # --------------------------------------------------

        for observacao in dados:

            valido, erros = validate_selic_observation(
                observacao
            )

            if not valido:

                rejeitados += 1

                print(
                    f"REJEITADO | "
                    f"{observacao.get('data')} | "
                    f"{erros}"
                )

                continue

            aprovados += 1

            salvo = save_observation(
                observacao
            )

            if salvo:

                salvos += 1

            else:

                duplicados += 1

        # --------------------------------------------------
        # RESUMO
        # --------------------------------------------------

        print()
        print("=" * 60)
        print("RESUMO DA COLETA")
        print("=" * 60)

        print(
            f"Observações recebidas: {len(dados)}"
        )

        print(
            f"Aprovadas pelo Validator: {aprovados}"
        )

        print(
            f"Rejeitadas: {rejeitados}"
        )

        print(
            f"Novos registros salvos: {salvos}"
        )

        print(
            f"Registros já existentes: {duplicados}"
        )

        print("=" * 60)

    except requests.RequestException as error:

        print(
            "Erro na comunicação com o Banco Central."
        )

        print(
            f"Detalhes: {error}"
        )

    except Exception as error:

        print(
            "Erro inesperado na Koaiala."
        )

        print(
            f"Detalhes: {error}"
        )


if __name__ == "__main__":
    main()