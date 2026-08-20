"""
KOAIALA SENSE
OBSERVATION VALIDATOR

Validador genérico das observações econômicas coletadas
pelos collectors do Koaiala.

Responsabilidades:

- validar existência da data;
- validar existência do valor;
- validar formato da data;
- impedir datas futuras;
- validar valor numérico;
- validar unidade quando disponível;
- retornar erros de forma padronizada.

Este módulo não salva dados no banco.

Ele apenas responde:

    A observação é válida?

Retorno padrão:

    True, []

ou

    False, ["erro 1", "erro 2"]
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


# ============================================================
# CONFIGURAÇÕES
# ============================================================

FORMATOS_DATA = (
    "%d/%m/%Y",
    "%Y-%m-%d",
)


# ============================================================
# CONVERSÃO DA DATA
# ============================================================

def converter_data(data_observacao):
    """
    Converte uma data recebida pelo collector
    para um objeto datetime.date.

    Aceita:

        DD/MM/AAAA
        AAAA-MM-DD

    Retorna:

        date -> quando válida
        None -> quando inválida
    """

    if data_observacao is None:
        return None

    if isinstance(data_observacao, datetime):
        return data_observacao.date()

    if isinstance(data_observacao, date):
        return data_observacao

    valor = str(data_observacao).strip()

    for formato in FORMATOS_DATA:

        try:

            return datetime.strptime(
                valor,
                formato
            ).date()

        except ValueError:
            continue

    return None


# ============================================================
# VALIDAÇÃO DO VALOR
# ============================================================

def validar_valor(valor):
    """
    Verifica se o valor da observação é numérico.

    Aceita:

        int
        float
        Decimal
        string numérica

    Rejeita:

        None
        string vazia
        valores não numéricos

    Retorna:

        True  -> valor válido
        False -> valor inválido
    """

    if valor is None:
        return False

    if isinstance(valor, str):

        valor = valor.strip()

        if not valor:
            return False

    try:

        Decimal(str(valor))

        return True

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        return False


# ============================================================
# VALIDAÇÃO DA UNIDADE
# ============================================================

def validar_unidade(indicador, unidade_observacao=None):
    """
    Valida a unidade da observação quando ela estiver disponível.

    O Registry é considerado a fonte oficial da unidade
    esperada para o indicador.

    Caso a observação não forneça unidade, a validação
    não é considerada erro.

    Retorna:

        True  -> unidade válida ou não informada
        False -> unidade incompatível
    """

    if unidade_observacao is None:
        return True

    unidade_esperada = indicador.get("unit")

    if unidade_esperada is None:
        return True

    unidade_observacao = str(
        unidade_observacao
    ).strip()

    unidade_esperada = str(
        unidade_esperada
    ).strip()

    if not unidade_observacao:
        return True

    return unidade_observacao == unidade_esperada


# ============================================================
# VALIDAÇÃO GENÉRICA
# ============================================================

def validate_observation(
    observation,
    indicador
):
    """
    Valida uma observação econômica de forma genérica.

    Parâmetros:

        observation:
            dicionário recebido pelo collector.

        indicador:
            configuração do indicador proveniente
            do Registry.

    Retorno:

        (True, [])

    ou:

        (False, [lista de erros])
    """

    errors = []

    # --------------------------------------------------------
    # Validação básica dos parâmetros
    # --------------------------------------------------------

    if not isinstance(
        observation,
        dict
    ):

        return False, [
            "Observação inválida"
        ]

    if not isinstance(
        indicador,
        dict
    ):

        return False, [
            "Indicador inválido"
        ]

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    data = observation.get(
        "data"
    )

    if data is None or str(data).strip() == "":

        errors.append(
            "Data ausente"
        )

    else:

        observation_date = converter_data(
            data
        )

        if observation_date is None:

            errors.append(
                "Data em formato inválido"
            )

        else:

            # ------------------------------------------------
            # Impede dados futuros
            # ------------------------------------------------

            if observation_date > date.today():

                errors.append(
                    "Data futura"
                )

    # --------------------------------------------------------
    # Valor
    # --------------------------------------------------------

    valor = observation.get(
        "valor"
    )

    if valor is None or str(valor).strip() == "":

        errors.append(
            "Valor ausente"
        )

    elif not validar_valor(valor):

        errors.append(
            "Valor não numérico"
        )

    # --------------------------------------------------------
    # Unidade
    # --------------------------------------------------------

    unidade = observation.get(
        "unidade"
    )

    if unidade is None:

        unidade = observation.get(
            "unit"
        )

    if not validar_unidade(
        indicador,
        unidade
    ):

        errors.append(
            "Unidade incompatível"
        )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    if errors:

        return False, errors

    return True, []


# ============================================================
# TESTE
# ============================================================

def main():

    indicador = {
        "code": "IPCA",
        "name": "IPCA",
        "unit": "% a.m.",
    }

    observacao_valida = {
        "data": "13/08/2026",
        "valor": "0.07",
    }

    observacao_invalida = {
        "data": "13/08/2027",
        "valor": "abc",
    }

    print("=" * 60)
    print("KOAIALA OBSERVATION VALIDATOR")
    print("=" * 60)

    valido, erros = validate_observation(
        observacao_valida,
        indicador
    )

    print()
    print("TESTE 1 - OBSERVAÇÃO VÁLIDA")
    print(
        f"Resultado: {valido}"
    )
    print(
        f"Erros: {erros}"
    )

    valido, erros = validate_observation(
        observacao_invalida,
        indicador
    )

    print()
    print("TESTE 2 - OBSERVAÇÃO INVÁLIDA")
    print(
        f"Resultado: {valido}"
    )
    print(
        f"Erros: {erros}"
    )

    print()
    print("=" * 60)


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()