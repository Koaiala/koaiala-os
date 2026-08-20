"""
KOAIALA SENSE
SGS COLLECTOR

Collector genérico para indicadores econômicos
fornecidos pelo Sistema Gerenciador de Séries
Temporais (SGS) do Banco Central do Brasil.

O Registry define:
- qual indicador
- qual série
- qual fonte
- qual unidade
- qual frequência

O SGS Collector define:
- como consultar o SGS
- como interpretar os dados
- como validar as observações
- como salvar no PostgreSQL
- como evitar duplicidades
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import requests

from src.database.connection import get_connection
from src.validator.observation_validator import (
    validate_observation,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_URL = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.{codigo}/dados"
)

BASE_URL_ULTIMOS = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.{codigo}/dados/ultimos/{quantidade}"
)

TIMEOUT = 30


# ============================================================
# CONSULTA AO SGS
# ============================================================

def consultar_sgs(
    codigo,
    data_inicial=None,
    data_final=None,
    quantidade=None
):
    """
    Consulta uma série do BCB/SGS.

    Existem duas formas de consulta:

    1. Intervalo de datas
       Utilizado principalmente para indicadores diários.

    2. Últimos N registros
       Utilizado principalmente para indicadores mensais,
       trimestrais ou anuais.
    """

    headers = {
        "Accept": "application/json",
        "User-Agent": "Koaiala-Sense/1.0",
    }

    # --------------------------------------------------------
    # Últimos registros
    # --------------------------------------------------------

    if quantidade is not None:

        url = BASE_URL_ULTIMOS.format(
            codigo=codigo,
            quantidade=quantidade
        )

        params = {
            "formato": "json"
        }

    # --------------------------------------------------------
    # Intervalo de datas
    # --------------------------------------------------------

    else:

        url = BASE_URL.format(
            codigo=codigo
        )

        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "formato": "json",
        }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=TIMEOUT,
    )

    response.raise_for_status()

    dados = response.json()

    if not isinstance(dados, list):

        raise ValueError(
            "Resposta inesperada recebida do SGS."
        )

    return dados


# ============================================================
# CONVERSÃO DE DATA
# ============================================================

def converter_data(data):
    """
    Converte a data retornada pelo SGS
    para datetime.date.

    Formato esperado:

        DD/MM/YYYY
    """

    if not data:

        raise ValueError(
            "Data da observação não informada."
        )

    return datetime.strptime(
        data,
        "%d/%m/%Y"
    ).date()


# ============================================================
# CONVERSÃO DE VALOR
# ============================================================

def converter_valor(valor):
    """
    Converte o valor retornado pelo SGS
    para Decimal.
    """

    if valor is None:

        raise ValueError(
            "Valor da observação não informado."
        )

    return Decimal(
        str(valor).replace(",", ".")
    )


# ============================================================
# LOCALIZAÇÃO DO INDICADOR
# ============================================================

def obter_indicator_id(
    connection,
    codigo
):
    """
    Localiza o ID interno do indicador.

    Utiliza a conexão já aberta pelo processo
    de coleta.
    """

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM economic_indicators
            WHERE code = %s
            """,
            (codigo,)
        )

        resultado = cursor.fetchone()

        if resultado is None:

            raise ValueError(
                f"Indicador '{codigo}' não encontrado "
                "em economic_indicators."
            )

        return resultado[0]

    finally:

        if cursor is not None:
            cursor.close()


# ============================================================
# SALVAMENTO DA OBSERVAÇÃO
# ============================================================

def salvar_observacao(
    connection,
    indicator_id,
    indicador,
    data_observacao,
    valor
):
    """
    Salva uma observação no PostgreSQL.

    A proteção contra duplicidade é realizada
    pelo PostgreSQL através da restrição:

        uq_economic_observation

    sobre:

        indicator_code
        observation_date

    Retorna:

        True  -> novo registro salvo
        False -> registro já existente
    """

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO economic_observations (
                indicator_id,
                indicator_code,
                indicator_name,
                source,
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
            RETURNING id
            """,
            (
                indicator_id,
                indicador["code"],
                indicador["name"],
                indicador["source"],
                data_observacao,
                valor,
                indicador["unit"],
            )
        )

        resultado = cursor.fetchone()

        if resultado is None:

            return False

        return True

    finally:

        if cursor is not None:
            cursor.close()


# ============================================================
# COLETA GENÉRICA
# ============================================================

def coletar(indicador):
    """
    Executa a coleta genérica de um indicador SGS.

    A estratégia de coleta é definida pela frequência
    cadastrada no Registry.

    Frequências suportadas:

        DIARIA
        MENSAL
        TRIMESTRAL
        ANUAL
    """

    codigo = indicador["code"]
    nome = indicador["name"]
    source_code = indicador["source_code"]
    frequencia = indicador["frequency"]

    # --------------------------------------------------------
    # Configuração da coleta
    # --------------------------------------------------------

    hoje = date.today()

    data_inicial = None
    data_final = None
    quantidade = None

    # ========================================================
    # DIÁRIA
    # ========================================================

    if frequencia == "DIARIA":

        data_inicio = hoje - timedelta(
            days=7
        )

        data_inicial = data_inicio.strftime(
            "%d/%m/%Y"
        )

        data_final = hoje.strftime(
            "%d/%m/%Y"
        )

    # ========================================================
    # MENSAL
    # ========================================================

    elif frequencia == "MENSAL":

        quantidade = 12

    # ========================================================
    # TRIMESTRAL
    # ========================================================

    elif frequencia == "TRIMESTRAL":

        quantidade = 8

    # ========================================================
    # ANUAL
    # ========================================================

    elif frequencia == "ANUAL":

        quantidade = 5

    # ========================================================
    # FREQUÊNCIA NÃO SUPORTADA
    # ========================================================

    else:

        raise ValueError(
            f"Frequência '{frequencia}' não suportada "
            "pelo SGS Collector."
        )

    # --------------------------------------------------------
    # Cabeçalho
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("KOAIALA SENSE - SGS COLLECTOR")
    print("=" * 60)

    print(
        f"Indicador: {nome}"
    )

    print(
        f"Código: {codigo}"
    )

    print(
        f"Série SGS: {source_code}"
    )

    print(
        f"Frequência: {frequencia}"
    )

    print(
        f"Fonte: {indicador['source']}"
    )

    # --------------------------------------------------------
    # Informação da consulta
    # --------------------------------------------------------

    if quantidade is not None:

        print(
            f"Consulta: últimos "
            f"{quantidade} registros"
        )

    else:

        print(
            f"Período: "
            f"{data_inicial} até {data_final}"
        )

    # --------------------------------------------------------
    # Consulta ao SGS
    # --------------------------------------------------------

    dados = consultar_sgs(
        source_code,
        data_inicial=data_inicial,
        data_final=data_final,
        quantidade=quantidade
    )

    print(
        f"Observações recebidas: "
        f"{len(dados)}"
    )

    # ========================================================
    # CONEXÃO ÚNICA COM O BANCO
    # ========================================================

    connection = get_connection()

    try:

        # ----------------------------------------------------
        # Localiza o indicador uma única vez
        # ----------------------------------------------------

        indicator_id = obter_indicator_id(
            connection,
            codigo
        )

        # ----------------------------------------------------
        # Processamento
        # ----------------------------------------------------

        novas = 0
        existentes = 0
        rejeitadas = 0

        total = len(dados)

        for numero, item in enumerate(
            dados,
            start=1
        ):

            # ------------------------------------------------
            # VALIDAÇÃO DA OBSERVAÇÃO
            # ------------------------------------------------

            valido, erros = validate_observation(
                item,
                indicador
            )

            if not valido:

                rejeitadas += 1

                print(
                    f"[{numero}/{total}] "
                    f"REJEITADA | "
                    f"Data: {item.get('data')} | "
                    f"Valor: {item.get('valor')} | "
                    f"Erros: {erros}"
                )

                continue

            # ------------------------------------------------
            # CONVERSÃO
            # ------------------------------------------------

            data_observacao = converter_data(
                item["data"]
            )

            valor = converter_valor(
                item["valor"]
            )

            print(
                f"[{numero}/{total}] "
                f"{data_observacao} = {valor}"
            )

            # ------------------------------------------------
            # SALVAMENTO
            # ------------------------------------------------

            salva = salvar_observacao(
                connection,
                indicator_id,
                indicador,
                data_observacao,
                valor
            )

            if salva:

                novas += 1

            else:

                existentes += 1

        # ----------------------------------------------------
        # Confirma todas as operações
        # ----------------------------------------------------

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()

    # ========================================================
    # RESUMO
    # ========================================================

    print()
    print("=" * 60)
    print("RESUMO DA COLETA")
    print("=" * 60)

    print(
        f"Observações recebidas: "
        f"{len(dados)}"
    )

    print(
        f"Observações rejeitadas: "
        f"{rejeitadas}"
    )

    print(
        f"Novos registros salvos: "
        f"{novas}"
    )

    print(
        f"Registros já existentes: "
        f"{existentes}"
    )

    print("=" * 60)

    return {
        "status": "OK",
        "indicador": codigo,
        "serie": source_code,
        "frequencia": frequencia,
        "observacoes_recebidas": len(dados),
        "rejeitadas": rejeitadas,
        "novos": novas,
        "existentes": existentes,
    }


# ============================================================
# TESTE
# ============================================================

def main():

    print(
        "SGS Collector carregado com sucesso."
    )


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    main()