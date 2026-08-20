"""
KOAIALA SENSE - SGS HISTORICAL COLLECTOR V8 FIX

Compatível com o formato atual do registry do Koaiala.
Resolve a série SGS por diferentes nomes de campo usados
na configuração existente.
"""

from datetime import date, timedelta
import json
import urllib.request

from src.database.connection import get_connection


SGS_URL = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.{serie}/dados"
)


def _campo(obj, *nomes, default=None):
    if isinstance(obj, dict):
        for nome in nomes:
            if nome in obj and obj[nome] not in (None, ""):
                return obj[nome]

    for nome in nomes:
        valor = getattr(obj, nome, None)
        if valor not in (None, ""):
            return valor

    return default


def _parse_date(valor):
    if isinstance(valor, date):
        return valor

    return date.fromisoformat(str(valor))


def _buscar_sgs(serie, data_inicio, data_fim):
    url = SGS_URL.format(serie=serie)

    url += (
        f"?dataInicial={data_inicio:%d/%m/%Y}"
        f"&dataFinal={data_fim:%d/%m/%Y}"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Koaiala/1.0",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def _data(item):
    texto = str(item["data"]).strip()

    if "/" in texto:
        dia, mes, ano = texto.split("/")
        return date(
            int(ano),
            int(mes),
            int(dia),
        )

    return date.fromisoformat(
        texto[:10]
    )


def _valor(item):
    return float(
        str(item["valor"]).replace(",", ".")
    )


def _salvar(indicador, observacoes):
    codigo = _campo(
        indicador,
        "code",
        "codigo",
        "indicator_code",
    )

    nome = _campo(
        indicador,
        "name",
        "nome",
        "indicator_name",
        default=codigo,
    )

    fonte = _campo(
        indicador,
        "source",
        "fonte",
        default="Banco Central do Brasil",
    )

    serie = _campo(
        indicador,
        "sgs_series",
        "sgs_serie",
        "serie_sgs",
        "series",
        "serie",
        "source_series",
    )

    unidade = _campo(
        indicador,
        "unit",
        "unidade",
        default="%",
    )

    connection = get_connection()

    novos = 0
    existentes = 0

    try:
        cursor = connection.cursor()

        for obs in observacoes:

            cursor.execute(
                """
                SELECT 1
                FROM economic_observations
                WHERE indicator_code = %s
                  AND observation_date = %s
                LIMIT 1
                """,
                (
                    codigo,
                    obs["data"],
                ),
            )

            if cursor.fetchone():
                existentes += 1
                continue

            cursor.execute(
                """
                INSERT INTO economic_observations (
                    indicator_code,
                    indicator_name,
                    source,
                    source_series,
                    observation_date,
                    value,
                    unit,
                    collected_at,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                """,
                (
                    codigo,
                    nome,
                    fonte,
                    str(serie),
                    obs["data"],
                    obs["valor"],
                    unidade,
                ),
            )

            novos += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return novos, existentes


def coletar(
    indicador,
    anos=10,
    data_inicio=None,
    data_fim=None,
):
    codigo = _campo(
        indicador,
        "code",
        "codigo",
        "indicator_code",
    )

    serie = _campo(
        indicador,
        "sgs_series",
        "sgs_serie",
        "serie_sgs",
        "series",
        "serie",
        "source_series",
    )

    if not serie:
        raise ValueError(
            f"Indicador {codigo} sem série SGS configurada. "
            "Verifique o registry."
        )

    data_fim = (
        _parse_date(data_fim)
        if data_fim is not None
        else date.today()
    )

    if data_inicio is not None:
        data_inicio = _parse_date(
            data_inicio
        )
    else:
        data_inicio = date(
            data_fim.year - int(anos),
            data_fim.month,
            data_fim.day,
        )

    print("=" * 60)
    print("KOAIALA SENSE - SGS HISTORICAL COLLECTOR V8")
    print("=" * 60)
    print(f"Indicador: {codigo}")
    print(f"Série SGS: {serie}")
    print(
        f"Período: "
        f"{data_inicio} -> {data_fim}"
    )

    dados = _buscar_sgs(
        str(serie),
        data_inicio,
        data_fim,
    )

    observacoes = []

    for item in dados:
        try:
            observacoes.append(
                {
                    "data": _data(item),
                    "valor": _valor(item),
                }
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

    observacoes.sort(
        key=lambda item: item["data"]
    )

    novos, existentes = _salvar(
        indicador,
        observacoes,
    )

    print(
        f"Observações recebidas: "
        f"{len(observacoes)}"
    )
    print(
        f"Novos registros salvos: {novos}"
    )
    print(
        f"Registros já existentes: "
        f"{existentes}"
    )

    return {
        "status": "OK",
        "indicador": codigo,
        "serie": str(serie),
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "observacoes_recebidas": len(
            observacoes
        ),
        "novos": novos,
        "existentes": existentes,
    }
