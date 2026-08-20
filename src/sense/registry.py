"""
KOAIALA SENSE
INDICATOR REGISTRY

Catálogo central dos indicadores econômicos
utilizados pelo Koaiala.

A ideia deste módulo é separar:

O QUE coletar
de
COMO coletar

O Registry define os metadados do indicador.

Os Collectors utilizam essas informações
para executar a coleta automaticamente.
"""

# ============================================================
# INDICADORES
# ============================================================

INDICATORS = {

    # ========================================================
    # POLÍTICA MONETÁRIA
    # ========================================================

    "SELIC_META": {

        "code": "SELIC_META",

        "name": "Selic Meta",

        "source": "Banco Central do Brasil",

        "source_code": "432",

        "source_type": "BCB_SGS",

        "unit": "% a.a.",

        "frequency": "DIARIA",

        "category": "JUROS",

        "description":
            "Taxa Selic Meta definida pelo Banco Central do Brasil.",

        "active": True,
    },


    # ========================================================
    # INFLAÇÃO
    # ========================================================

    "IPCA": {

        "code": "IPCA",

        "name": "IPCA",

        "source": "Banco Central do Brasil / IBGE",

        "source_code": "433",

        "source_type": "BCB_SGS",

        "unit": "% a.m.",

        "frequency": "MENSAL",

        "category": "INFLACAO",

        "description":
            "Índice Nacional de Preços ao Consumidor Amplo.",

        "active": True,
    },


    "IGP_M": {

        "code": "IGP_M",

        "name": "IGP-M",

        "source": "Banco Central do Brasil / FGV",

        "source_code": "189",

        "source_type": "BCB_SGS",

        "unit": "% a.m.",

        "frequency": "MENSAL",

        "category": "INFLACAO",

        "description":
            "Índice Geral de Preços - Mercado, "
            "calculado pela Fundação Getulio Vargas.",

        "active": True,
    },


    "INPC": {

        "code": "INPC",

        "name": "INPC",

        "source": "Banco Central do Brasil / IBGE",

        "source_code": "188",

        "source_type": "BCB_SGS",

        "unit": "% a.m.",

        "frequency": "MENSAL",

        "category": "INFLACAO",

        "description":
            "Índice Nacional de Preços ao Consumidor.",

        "active": True,
    },
}


# ============================================================
# FUNÇÕES DO REGISTRY
# ============================================================

def get_indicator(code):
    """
    Retorna a configuração de um indicador.
    """

    return INDICATORS.get(code)


def get_active_indicators():
    """
    Retorna somente os indicadores ativos.
    """

    return {
        code: config
        for code, config in INDICATORS.items()
        if config.get("active") is True
    }


def get_indicator_codes():
    """
    Retorna a lista de códigos dos indicadores ativos.
    """

    return list(
        get_active_indicators().keys()
    )


def indicator_exists(code):
    """
    Verifica se um indicador existe no Registry.
    """

    return code in INDICATORS


def print_registry():
    """
    Exibe os indicadores cadastrados.
    """

    print("=" * 60)
    print("KOAIALA INDICATOR REGISTRY")
    print("=" * 60)

    for code, config in get_active_indicators().items():

        print(
            f"{code} | "
            f"{config['name']} | "
            f"{config['source']} | "
            f"Série: {config['source_code']} | "
            f"{config['frequency']}"
        )

    print("=" * 60)


# ============================================================
# TESTE
# ============================================================

def main():

    print_registry()


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()