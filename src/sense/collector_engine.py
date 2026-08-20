"""
KOAIALA SENSE
COLLECTOR ENGINE

Motor central responsável por executar os coletores
dos indicadores econômicos cadastrados no Registry.

O Registry define:

    O QUE coletar

O Collector Engine define:

    QUAL MOTOR DE COLETA utilizar

Os collectors definem:

    COMO coletar

Arquitetura:

    Registry
        ↓
    Collector Engine
        ↓
    Collector específico ou genérico
        ↓
    Banco de dados
"""

from importlib import import_module

from src.sense.registry import (
    get_active_indicators,
    get_indicator,
)


# ============================================================
# CONFIGURAÇÃO DOS COLLECTORS ESPECÍFICOS
# ============================================================

COLLECTOR_MAP = {

    # --------------------------------------------------------
    # Banco Central - collector histórico específico
    # --------------------------------------------------------

    "SELIC_META": {
        "module": "src.sense.bcb_collector",
        "function": "coletar",
        "pass_indicator": False,
    },

}


# ============================================================
# RESOLUÇÃO DO COLLECTOR
# ============================================================

def obter_collector(indicador):
    """
    Determina automaticamente qual collector deve
    ser utilizado para determinado indicador.

    Prioridade:

    1. Collector explicitamente configurado
       no COLLECTOR_MAP.

    2. Collector genérico baseado no source_type.

    Atualmente:

        BCB_SGS -> sgs_collector
    """

    codigo = indicador["code"]

    # --------------------------------------------------------
    # Collector específico
    # --------------------------------------------------------

    if codigo in COLLECTOR_MAP:

        return COLLECTOR_MAP[codigo]

    # --------------------------------------------------------
    # Collector genérico SGS
    # --------------------------------------------------------

    source_type = indicador.get(
        "source_type"
    )

    if source_type == "BCB_SGS":

        return {
            "module": "src.sense.sgs_collector",
            "function": "coletar",
            "pass_indicator": True,
        }

    # --------------------------------------------------------
    # Nenhum collector encontrado
    # --------------------------------------------------------

    raise ValueError(
        f"Nenhum collector configurado para "
        f"o indicador '{codigo}'."
    )


# ============================================================
# EXECUÇÃO DE UM COLLECTOR
# ============================================================

def executar_collector(codigo):
    """
    Executa o collector associado a um indicador.

    O indicador é localizado no Registry e,
    posteriormente, o Collector Engine determina
    automaticamente qual motor deve ser utilizado.
    """

    # --------------------------------------------------------
    # Localiza indicador
    # --------------------------------------------------------

    indicador = get_indicator(
        codigo
    )

    if indicador is None:

        raise ValueError(
            f"Indicador '{codigo}' não está cadastrado "
            "no Registry."
        )

    # --------------------------------------------------------
    # Garante que o código esteja disponível
    # dentro da configuração do indicador
    # --------------------------------------------------------

    indicador_execucao = dict(
        indicador
    )

    indicador_execucao["code"] = codigo

    # --------------------------------------------------------
    # Localiza collector
    # --------------------------------------------------------

    collector = obter_collector(
        indicador_execucao
    )

    # --------------------------------------------------------
    # Importa módulo dinamicamente
    # --------------------------------------------------------

    try:

        module = import_module(
            collector["module"]
        )

    except Exception as erro:

        raise ImportError(
            f"Não foi possível carregar o collector "
            f"'{collector['module']}' para o indicador "
            f"'{codigo}'. Erro: {erro}"
        ) from erro

    # --------------------------------------------------------
    # Localiza função
    # --------------------------------------------------------

    function_name = collector[
        "function"
    ]

    if not hasattr(
        module,
        function_name
    ):

        raise AttributeError(
            f"O módulo '{collector['module']}' "
            f"não possui a função '{function_name}'."
        )

    function = getattr(
        module,
        function_name
    )

    # --------------------------------------------------------
    # Identificação
    # --------------------------------------------------------

    print()
    print(
        f"Executando collector: {codigo}"
    )

    print(
        f"Collector: "
        f"{collector['module']}"
    )

    # --------------------------------------------------------
    # Execução
    # --------------------------------------------------------

    if collector.get(
        "pass_indicator",
        False
    ):

        return function(
            indicador_execucao
        )

    return function()


# ============================================================
# EXECUÇÃO DE TODOS OS INDICADORES
# ============================================================

def executar_coleta():
    """
    Executa todos os indicadores ativos
    cadastrados no Registry.

    Cada indicador é processado
    independentemente.

    Um erro em um indicador não interrompe
    a coleta dos demais.
    """

    indicadores = (
        get_active_indicators()
    )

    resultados = {}

    # --------------------------------------------------------
    # Cabeçalho
    # --------------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "KOAIALA COLLECTOR ENGINE"
    )

    print(
        "=" * 60
    )

    print(
        f"Indicadores ativos: "
        f"{len(indicadores)}"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Execução
    # --------------------------------------------------------

    for codigo in indicadores:

        try:

            resultado = executar_collector(
                codigo
            )

            resultados[codigo] = {
                "status": "OK",
                "resultado": resultado,
            }

        except Exception as erro:

            print()
            print(
                f"ERRO no collector "
                f"{codigo}: {erro}"
            )

            resultados[codigo] = {
                "status": "ERRO",
                "erro": str(erro),
            }

    # --------------------------------------------------------
    # Resultado final
    # --------------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "RESULTADO DA COLETA"
    )

    print(
        "=" * 60
    )

    for codigo, resultado in (
        resultados.items()
    ):

        print(
            f"{codigo}: "
            f"{resultado['status']}"
        )

    print(
        "=" * 60
    )

    return resultados


# ============================================================
# TESTE
# ============================================================

def main():

    executar_coleta()


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    main()