"""
KOAIALA
ANALYSIS ENGINE

Motor quantitativo responsável por analisar as observações
econômicas armazenadas no PostgreSQL.

O Analysis Engine não interpreta o significado econômico
do indicador.

Ele responde perguntas quantitativas como:

    Qual é o valor atual?
    Qual era o valor anterior?
    Quanto variou?
    Qual é a tendência atual?
    Qual é a tendência de curto prazo?
    Qual é a tendência histórica?
    A tendência possui força ou é apenas uma oscilação?

A interpretação econômica é realizada posteriormente
pelo Economic Interpreter.
"""

from decimal import Decimal


from src.database.connection import get_connection


# ============================================================
# CONFIGURAÇÃO DA ANÁLISE
# ============================================================

SHORT_TERM_WINDOW = 5

HISTORICAL_WINDOW = 12


# ============================================================
# CLASSIFICAÇÃO DE TENDÊNCIA
# ============================================================

def classificar_tendencia(
    valores
):
    """
    Determina a tendência predominante de uma sequência.

    A classificação considera as variações entre
    observações consecutivas.

    Retorna:

        ALTA
        QUEDA
        ESTABILIDADE
    """

    if len(valores) < 2:
        return "ESTABILIDADE"

    altas = 0
    quedas = 0

    for i in range(
        1,
        len(valores)
    ):

        if valores[i] > valores[i - 1]:
            altas += 1

        elif valores[i] < valores[i - 1]:
            quedas += 1

    if altas > quedas:
        return "ALTA"

    if quedas > altas:
        return "QUEDA"

    return "ESTABILIDADE"


# ============================================================
# FORÇA DA TENDÊNCIA
# ============================================================

def calcular_forca_tendencia(
    valores
):
    """
    Calcula a força da tendência a partir da proporção
    de movimentos que apontam para a mesma direção.

    Retorna:

        MUITO_FRACA
        FRACA
        MODERADA
        FORTE
        MUITO_FORTE
    """

    if len(valores) < 2:
        return "MUITO_FRACA"

    movimentos = 0
    direcao_predominante = 0

    for i in range(
        1,
        len(valores)
    ):

        if valores[i] > valores[i - 1]:
            movimentos += 1
            direcao_predominante += 1

        elif valores[i] < valores[i - 1]:
            movimentos += 1
            direcao_predominante -= 1

    if movimentos == 0:
        return "MUITO_FRACA"

    intensidade = (
        abs(direcao_predominante)
        / movimentos
    )

    if intensidade >= Decimal("0.80"):
        return "MUITO_FORTE"

    if intensidade >= Decimal("0.60"):
        return "FORTE"

    if intensidade >= Decimal("0.40"):
        return "MODERADA"

    if intensidade >= Decimal("0.20"):
        return "FRACA"

    return "MUITO_FRACA"


# ============================================================
# MÉDIA DECIMAL
# ============================================================

def calcular_media(
    valores
):
    """
    Calcula a média mantendo Decimal.
    """

    if not valores:
        return Decimal("0")

    total = sum(
        valores,
        Decimal("0")
    )

    return (
        total
        / Decimal(
            str(len(valores))
        )
    )


# ============================================================
# ANÁLISE DE UM INDICADOR
# ============================================================

def analisar_indicador(
    indicator_code
):
    """
    Motor genérico de análise econômica da Koaiala.

    Recebe o código de um indicador e analisa seus dados
    armazenados na tabela economic_observations.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ====================================================
        # 1. BUSCA OS DADOS
        # ====================================================

        cursor.execute(
            """
            SELECT
                observation_date,
                value
            FROM economic_observations
            WHERE indicator_code = %s
            ORDER BY observation_date ASC
            """,
            (
                indicator_code,
            )
        )

        registros = cursor.fetchall()

        if not registros:

            return {
                "status": "ERRO",
                "mensagem":
                    f"Nenhum dado encontrado "
                    f"para {indicator_code}"
            }

        # ====================================================
        # 2. ORGANIZA OS DADOS
        # ====================================================

        datas = [
            registro[0]
            for registro in registros
        ]

        valores = [
            Decimal(
                str(registro[1])
            )
            for registro in registros
        ]

        data_atual = datas[-1]

        valor_atual = valores[-1]

        # ====================================================
        # 3. VALOR ANTERIOR
        # ====================================================

        valor_anterior = None

        data_anterior = None

        if len(valores) >= 2:

            valor_anterior = valores[-2]

            data_anterior = datas[-2]

        # ====================================================
        # 4. VARIAÇÃO ABSOLUTA
        # ====================================================

        variacao_absoluta = None

        if valor_anterior is not None:

            variacao_absoluta = (
                valor_atual
                - valor_anterior
            )

        # ====================================================
        # 5. VARIAÇÃO PERCENTUAL
        # ====================================================

        variacao_percentual = None

        if (
            valor_anterior is not None
            and valor_anterior != 0
        ):

            variacao_percentual = (
                (
                    valor_atual
                    - valor_anterior
                )
                / valor_anterior
            ) * Decimal("100")

        # ====================================================
        # 6. MÁXIMO, MÍNIMO E MÉDIA
        # ====================================================

        valor_maximo = max(
            valores
        )

        valor_minimo = min(
            valores
        )

        media = calcular_media(
            valores
        )

        # ====================================================
        # 7. CONTAGEM
        # ====================================================

        total_observacoes = len(
            valores
        )

        # ====================================================
        # 8. MUDANÇAS
        # ====================================================

        mudancas = []

        for i in range(
            1,
            len(valores)
        ):

            if valores[i] != valores[i - 1]:

                mudancas.append(
                    {
                        "data":
                            datas[i],

                        "valor_anterior":
                            valores[i - 1],

                        "novo_valor":
                            valores[i],

                        "variacao":
                            (
                                valores[i]
                                - valores[i - 1]
                            )
                    }
                )

        total_mudancas = len(
            mudancas
        )

        # ====================================================
        # 9. ÚLTIMA MUDANÇA
        # ====================================================

        ultima_mudanca = None

        if mudancas:

            ultima_mudanca = (
                mudancas[-1]
            )

        # ====================================================
        # 10. TENDÊNCIA ATUAL
        # ====================================================

        tendencia_atual = (
            "ESTABILIDADE"
        )

        if valor_anterior is not None:

            if (
                valor_atual
                > valor_anterior
            ):

                tendencia_atual = "ALTA"

            elif (
                valor_atual
                < valor_anterior
            ):

                tendencia_atual = "QUEDA"

        # Mantém compatibilidade
        # com o Economic Interpreter.

        tendencia = (
            tendencia_atual
        )

        # ====================================================
        # 11. TENDÊNCIA DE CURTO PRAZO
        # ====================================================

        quantidade_curta = min(
            SHORT_TERM_WINDOW,
            len(valores)
        )

        valores_curto_prazo = (
            valores[
                -quantidade_curta:
            ]
        )

        tendencia_curta = (
            classificar_tendencia(
                valores_curto_prazo
            )
        )

        forca_tendencia_curta = (
            calcular_forca_tendencia(
                valores_curto_prazo
            )
        )

        # ====================================================
        # 12. TENDÊNCIA HISTÓRICA
        # ====================================================

        quantidade_historica = min(
            HISTORICAL_WINDOW,
            len(valores)
        )

        valores_historicos = (
            valores[
                -quantidade_historica:
            ]
        )

        tendencia_historica = (
            classificar_tendencia(
                valores_historicos
            )
        )

        forca_tendencia_historica = (
            calcular_forca_tendencia(
                valores_historicos
            )
        )

        # ====================================================
        # 13. FORÇA GERAL DA TENDÊNCIA
        # ====================================================

        forca_tendencia = (
            forca_tendencia_curta
        )

        # ====================================================
        # 14. INÍCIO DO NÍVEL ATUAL
        # ====================================================

        data_inicio_nivel = (
            data_atual
        )

        for i in range(
            len(valores) - 2,
            -1,
            -1
        ):

            if (
                valores[i]
                == valor_atual
            ):

                data_inicio_nivel = (
                    datas[i]
                )

            else:

                break

        dias_no_nivel = (
            data_atual
            - data_inicio_nivel
        ).days

        # ====================================================
        # 15. RETORNO
        # ====================================================

        return {

            "status":
                "OK",

            "indicador":
                indicator_code,

            "data_atual":
                data_atual,

            "valor_atual":
                valor_atual,

            "data_anterior":
                data_anterior,

            "valor_anterior":
                valor_anterior,

            "variacao_absoluta":
                variacao_absoluta,

            "variacao_percentual":
                variacao_percentual,

            "valor_maximo":
                valor_maximo,

            "valor_minimo":
                valor_minimo,

            "media":
                media,

            "total_observacoes":
                total_observacoes,

            "total_mudancas":
                total_mudancas,

            "ultima_mudanca":
                ultima_mudanca,

            # --------------------------------------------
            # TENDÊNCIAS
            # --------------------------------------------

            "tendencia":
                tendencia,

            "tendencia_atual":
                tendencia_atual,

            "tendencia_curta":
                tendencia_curta,

            "tendencia_historica":
                tendencia_historica,

            "forca_tendencia":
                forca_tendencia,

            "forca_tendencia_curta":
                forca_tendencia_curta,

            "forca_tendencia_historica":
                forca_tendencia_historica,

            # --------------------------------------------
            # NÍVEL
            # --------------------------------------------

            "data_inicio_nivel":
                data_inicio_nivel,

            "dias_no_nivel":
                dias_no_nivel
        }

    finally:

        connection.close()


# ============================================================
# EXIBIÇÃO DA ANÁLISE
# ============================================================

def exibir_analise(
    resultado
):
    """
    Exibe a análise do indicador de forma organizada.
    """

    print("=" * 60)

    print(
        "KOAIALA ANALYSIS ENGINE"
    )

    print("=" * 60)

    if (
        resultado["status"]
        != "OK"
    ):

        print(
            f"Status: "
            f"{resultado['status']}"
        )

        print(
            f"Mensagem: "
            f"{resultado['mensagem']}"
        )

        print("=" * 60)

        return

    print(
        f"Indicador: "
        f"{resultado['indicador']}"
    )

    print("-" * 60)

    print(
        f"Data atual: "
        f"{resultado['data_atual'].strftime('%d/%m/%Y')}"
    )

    print(
        f"Valor atual: "
        f"{resultado['valor_atual']}"
    )

    if (
        resultado["data_anterior"]
    ):

        print(
            f"Data anterior: "
            f"{resultado['data_anterior'].strftime('%d/%m/%Y')}"
        )

        print(
            f"Valor anterior: "
            f"{resultado['valor_anterior']}"
        )

    print("-" * 60)

    if (
        resultado["variacao_absoluta"]
        is not None
    ):

        print(
            f"Variação absoluta: "
            f"{resultado['variacao_absoluta']}"
        )

    if (
        resultado["variacao_percentual"]
        is not None
    ):

        print(
            f"Variação percentual: "
            f"{resultado['variacao_percentual']:.4f}%"
        )

    print("-" * 60)

    print(
        f"Valor máximo: "
        f"{resultado['valor_maximo']}"
    )

    print(
        f"Valor mínimo: "
        f"{resultado['valor_minimo']}"
    )

    print(
        f"Média histórica: "
        f"{resultado['media']:.4f}"
    )

    print(
        f"Total de observações: "
        f"{resultado['total_observacoes']}"
    )

    print("-" * 60)

    print(
        f"Total de mudanças: "
        f"{resultado['total_mudancas']}"
    )

    if (
        resultado["ultima_mudanca"]
    ):

        mudanca = (
            resultado[
                "ultima_mudanca"
            ]
        )

        print(
            "Última mudança: "
            f"{mudanca['data'].strftime('%d/%m/%Y')}"
        )

        print(
            f"Valor anterior: "
            f"{mudanca['valor_anterior']}"
        )

        print(
            f"Novo valor: "
            f"{mudanca['novo_valor']}"
        )

        print(
            f"Variação: "
            f"{mudanca['variacao']}"
        )

    print("-" * 60)

    print(
        f"Tendência atual: "
        f"{resultado['tendencia_atual']}"
    )

    print(
        f"Tendência curta: "
        f"{resultado['tendencia_curta']}"
    )

    print(
        f"Tendência histórica: "
        f"{resultado['tendencia_historica']}"
    )

    print(
        f"Força da tendência: "
        f"{resultado['forca_tendencia']}"
    )

    print(
        f"Força curta: "
        f"{resultado['forca_tendencia_curta']}"
    )

    print(
        f"Força histórica: "
        f"{resultado['forca_tendencia_historica']}"
    )

    print(
        f"Data início do nível atual: "
        f"{resultado['data_inicio_nivel'].strftime('%d/%m/%Y')}"
    )

    print(
        f"Dias no nível atual: "
        f"{resultado['dias_no_nivel']}"
    )

    print("=" * 60)


# ============================================================
# TESTE
# ============================================================

def main():

    indicadores = [
        "SELIC_META",
        "IPCA",
        "INPC",
        "IGP_M",
    ]

    for indicador in indicadores:

        print()

        resultado = (
            analisar_indicador(
                indicador
            )
        )

        exibir_analise(
            resultado
        )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()