from decimal import Decimal
from statistics import mean

from src.database.connection import get_connection


def analisar_indicador(indicator_code):
    """
    Motor genérico de análise econômica da Koaiala.

    Recebe o código de um indicador e analisa seus dados
    armazenados na tabela economic_observations.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # ============================================================
        # 1. BUSCA OS DADOS DO INDICADOR
        # ============================================================

        cursor.execute(
            """
            SELECT
                observation_date,
                value
            FROM economic_observations
            WHERE indicator_code = %s
            ORDER BY observation_date ASC
            """,
            (indicator_code,)
        )

        registros = cursor.fetchall()

        if not registros:
            return {
                "status": "ERRO",
                "mensagem": f"Nenhum dado encontrado para {indicator_code}"
            }

        # ============================================================
        # 2. ORGANIZA OS DADOS
        # ============================================================

        datas = [registro[0] for registro in registros]
        valores = [Decimal(str(registro[1])) for registro in registros]

        data_atual = datas[-1]
        valor_atual = valores[-1]

        # ============================================================
        # 3. VALOR ANTERIOR
        # ============================================================

        valor_anterior = None
        data_anterior = None

        if len(valores) >= 2:
            valor_anterior = valores[-2]
            data_anterior = datas[-2]

        # ============================================================
        # 4. VARIAÇÃO ABSOLUTA
        # ============================================================

        variacao_absoluta = None

        if valor_anterior is not None:
            variacao_absoluta = valor_atual - valor_anterior

        # ============================================================
        # 5. VARIAÇÃO PERCENTUAL
        # ============================================================

        variacao_percentual = None

        if valor_anterior is not None and valor_anterior != 0:
            variacao_percentual = (
                (valor_atual - valor_anterior)
                / valor_anterior
            ) * Decimal("100")

        # ============================================================
        # 6. MÁXIMO, MÍNIMO E MÉDIA
        # ============================================================

        valor_maximo = max(valores)
        valor_minimo = min(valores)

        media = Decimal(
            str(mean(float(valor) for valor in valores))
        )

        # ============================================================
        # 7. CONTAGEM DE OBSERVAÇÕES
        # ============================================================

        total_observacoes = len(valores)

        # ============================================================
        # 8. IDENTIFICA MUDANÇAS
        # ============================================================

        mudancas = []

        for i in range(1, len(valores)):

            if valores[i] != valores[i - 1]:

                mudancas.append(
                    {
                        "data": datas[i],
                        "valor_anterior": valores[i - 1],
                        "novo_valor": valores[i],
                        "variacao": valores[i] - valores[i - 1]
                    }
                )

        total_mudancas = len(mudancas)

        # ============================================================
        # 9. ÚLTIMA MUDANÇA
        # ============================================================

        ultima_mudanca = None

        if mudancas:
            ultima_mudanca = mudancas[-1]

        # ============================================================
        # 10. TENDÊNCIA
        # ============================================================

        tendencia = "ESTÁVEL"

        if valor_anterior is not None:

            if valor_atual > valor_anterior:
                tendencia = "ALTA"

            elif valor_atual < valor_anterior:
                tendencia = "QUEDA"

        # ============================================================
        # 11. DIAS NO NÍVEL ATUAL
        # ============================================================

        data_inicio_nivel = data_atual

        for i in range(len(valores) - 2, -1, -1):

            if valores[i] == valor_atual:
                data_inicio_nivel = datas[i]

            else:
                break

        dias_no_nivel = (
            data_atual - data_inicio_nivel
        ).days

        # ============================================================
        # 12. TENDÊNCIA HISTÓRICA
        # ============================================================

        tendencia_historica = "ESTÁVEL"

        if len(valores) >= 2:

            primeiro_valor = valores[0]

            if valor_atual > primeiro_valor:
                tendencia_historica = "ALTA"

            elif valor_atual < primeiro_valor:
                tendencia_historica = "QUEDA"

        # ============================================================
        # 13. RETORNO DA ANÁLISE
        # ============================================================

        return {
            "status": "OK",

            "indicador": indicator_code,

            "data_atual": data_atual,
            "valor_atual": valor_atual,

            "data_anterior": data_anterior,
            "valor_anterior": valor_anterior,

            "variacao_absoluta": variacao_absoluta,
            "variacao_percentual": variacao_percentual,

            "valor_maximo": valor_maximo,
            "valor_minimo": valor_minimo,
            "media": media,

            "total_observacoes": total_observacoes,

            "total_mudancas": total_mudancas,
            "ultima_mudanca": ultima_mudanca,

            "tendencia": tendencia,
            "tendencia_historica": tendencia_historica,

            "data_inicio_nivel": data_inicio_nivel,
            "dias_no_nivel": dias_no_nivel
        }

    finally:

        connection.close()


def exibir_analise(resultado):
    """
    Exibe a análise do indicador de forma organizada.
    """

    print("=" * 60)
    print("KOAIALA ANALYSIS ENGINE")
    print("=" * 60)

    if resultado["status"] != "OK":

        print(f"Status: {resultado['status']}")
        print(f"Mensagem: {resultado['mensagem']}")

        print("=" * 60)

        return

    print(f"Indicador: {resultado['indicador']}")
    print("-" * 60)

    print(
        f"Data atual: "
        f"{resultado['data_atual'].strftime('%d/%m/%Y')}"
    )

    print(
        f"Valor atual: "
        f"{resultado['valor_atual']}"
    )

    if resultado["data_anterior"]:

        print(
            f"Data anterior: "
            f"{resultado['data_anterior'].strftime('%d/%m/%Y')}"
        )

        print(
            f"Valor anterior: "
            f"{resultado['valor_anterior']}"
        )

    print("-" * 60)

    if resultado["variacao_absoluta"] is not None:

        print(
            f"Variação absoluta: "
            f"{resultado['variacao_absoluta']}"
        )

    if resultado["variacao_percentual"] is not None:

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

    if resultado["ultima_mudanca"]:

        mudanca = resultado["ultima_mudanca"]

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
        f"{resultado['tendencia']}"
    )

    print(
        f"Tendência histórica: "
        f"{resultado['tendencia_historica']}"
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


def main():

    resultado = analisar_indicador("SELIC_META")

    exibir_analise(resultado)


if __name__ == "__main__":
    main()