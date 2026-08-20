"""
KOAIALA
REGISTRY VALIDATOR

Validador estrutural dos indicadores cadastrados
no Indicator Registry.

Objetivo:

Garantir que um indicador esteja corretamente
configurado antes de entrar no processo de coleta.

Fluxo:

Registry
    ↓
Registry Validator
    ↓
Collector Engine
    ↓
Collector
"""


from src.sense.registry import (
    INDICATORS,
)

from src.sense.collector_engine import (
    obter_collector,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

REQUIRED_FIELDS = [
    "code",
    "name",
    "source",
    "source_code",
    "source_type",
    "unit",
    "frequency",
    "category",
    "description",
    "active",
]


SUPPORTED_SOURCE_TYPES = {
    "BCB_SGS",
}


SUPPORTED_FREQUENCIES = {
    "DIARIA",
    "MENSAL",
    "TRIMESTRAL",
    "ANUAL",
}


# ============================================================
# VALIDAÇÃO DE UM INDICADOR
# ============================================================

def validar_indicador(
    registry_code,
    indicador
):
    """
    Valida a configuração de um único indicador.

    Retorna um dicionário contendo:

        status
        codigo
        erros
        avisos
        collector
    """

    erros = []
    avisos = []

    # --------------------------------------------------------
    # Verificação básica
    # --------------------------------------------------------

    if not isinstance(
        indicador,
        dict
    ):

        return {
            "status": "ERRO",
            "codigo": registry_code,
            "erros": [
                "Configuração do indicador não é um dicionário."
            ],
            "avisos": [],
            "collector": None,
        }

    # --------------------------------------------------------
    # Campos obrigatórios
    # --------------------------------------------------------

    for campo in REQUIRED_FIELDS:

        if campo not in indicador:

            erros.append(
                f"Campo obrigatório ausente: '{campo}'."
            )

    # --------------------------------------------------------
    # Se faltarem campos estruturais,
    # algumas validações não podem continuar.
    # --------------------------------------------------------

    if erros:

        return {
            "status": "ERRO",
            "codigo": registry_code,
            "erros": erros,
            "avisos": avisos,
            "collector": None,
        }

    # --------------------------------------------------------
    # Código
    # --------------------------------------------------------

    if indicador["code"] != registry_code:

        erros.append(
            "O campo 'code' é diferente da chave "
            "utilizada no Registry."
        )

    # --------------------------------------------------------
    # Campos de texto
    # --------------------------------------------------------

    campos_texto = [
        "code",
        "name",
        "source",
        "source_code",
        "source_type",
        "unit",
        "frequency",
        "category",
        "description",
    ]

    for campo in campos_texto:

        valor = indicador.get(campo)

        if not isinstance(
            valor,
            str
        ):

            erros.append(
                f"O campo '{campo}' deve ser texto."
            )

        elif not valor.strip():

            erros.append(
                f"O campo '{campo}' não pode estar vazio."
            )

    # --------------------------------------------------------
    # Source Type
    # --------------------------------------------------------

    source_type = indicador.get(
        "source_type"
    )

    if source_type not in SUPPORTED_SOURCE_TYPES:

        erros.append(
            f"source_type '{source_type}' "
            "não é suportado."
        )

    # --------------------------------------------------------
    # Frequência
    # --------------------------------------------------------

    frequency = indicador.get(
        "frequency"
    )

    if frequency not in SUPPORTED_FREQUENCIES:

        erros.append(
            f"Frequência '{frequency}' "
            "não é suportada."
        )

    # --------------------------------------------------------
    # Active
    # --------------------------------------------------------

    if not isinstance(
        indicador["active"],
        bool
    ):

        erros.append(
            "O campo 'active' deve ser booleano."
        )

    # --------------------------------------------------------
    # Collector
    # --------------------------------------------------------

    collector_info = None

    if not erros:

        try:

            collector_info = obter_collector(
                indicador
            )

        except Exception as erro:

            erros.append(
                f"Collector não resolvido: {erro}"
            )

    # --------------------------------------------------------
    # Aviso para indicador inativo
    # --------------------------------------------------------

    if indicador["active"] is False:

        avisos.append(
            "Indicador está inativo."
        )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    if erros:

        status = "ERRO"

    else:

        status = "OK"

    return {
        "status": status,
        "codigo": registry_code,
        "erros": erros,
        "avisos": avisos,
        "collector": collector_info,
    }


# ============================================================
# VALIDAÇÃO DO REGISTRY COMPLETO
# ============================================================

def validar_registry():
    """
    Valida todos os indicadores cadastrados
    no Registry.

    Retorna um dicionário consolidado.
    """

    resultados = {}

    total = 0
    aprovados = 0
    rejeitados = 0

    print()
    print("=" * 60)
    print("KOAIALA REGISTRY VALIDATOR")
    print("=" * 60)

    # --------------------------------------------------------
    # Percorre o Registry
    # --------------------------------------------------------

    for codigo, indicador in INDICATORS.items():

        total += 1

        resultado = validar_indicador(
            codigo,
            indicador
        )

        resultados[codigo] = resultado

        if resultado["status"] == "OK":

            aprovados += 1

            print(
                f"✓ {codigo}: OK"
            )

        else:

            rejeitados += 1

            print(
                f"✗ {codigo}: ERRO"
            )

            for erro in resultado["erros"]:

                print(
                    f"    - {erro}"
                )

        for aviso in resultado["avisos"]:

            print(
                f"    AVISO: {aviso}"
            )

    # --------------------------------------------------------
    # Resumo
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 60)

    print(
        f"Indicadores analisados: {total}"
    )

    print(
        f"Aprovados: {aprovados}"
    )

    print(
        f"Rejeitados: {rejeitados}"
    )

    print("=" * 60)

    if rejeitados == 0:

        print(
            "STATUS FINAL: REGISTRY APROVADO ✓"
        )

    else:

        print(
            "STATUS FINAL: REGISTRY COM ERROS ✗"
        )

    print("=" * 60)

    return {
        "status": (
            "OK"
            if rejeitados == 0
            else "ERRO"
        ),
        "total": total,
        "aprovados": aprovados,
        "rejeitados": rejeitados,
        "indicadores": resultados,
    }


# ============================================================
# TESTE
# ============================================================

def main():

    resultado = validar_registry()

    if resultado["status"] == "OK":

        print(
            "\nRegistry pronto para coleta."
        )

    else:

        print(
            "\nCorrija os erros antes de "
            "prosseguir com a coleta."
        )


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    main()