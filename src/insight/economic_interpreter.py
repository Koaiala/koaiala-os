from decimal import Decimal


def interpretar(resultado):
    """
    Interpretador Econômico da Koaiala.

    Recebe o resultado produzido pelo Analysis Engine
    e transforma os dados quantitativos em uma interpretação
    econômica estruturada.

    Esta primeira versão é determinística:
    não utiliza IA generativa nem modelos estatísticos.
    """

    # ============================================================
    # 1. VERIFICAÇÃO DO RESULTADO
    # ============================================================

    if resultado.get("status") != "OK":

        return {
            "status": "ERRO",
            "mensagem": resultado.get(
                "mensagem",
                "Resultado de análise inválido."
            )
        }

    # ============================================================
    # 2. LEITURA DOS DADOS
    # ============================================================

    indicador = resultado["indicador"]

    valor_atual = Decimal(
        str(resultado["valor_atual"])
    )

    valor_anterior = resultado.get("valor_anterior")

    variacao_absoluta = resultado.get(
        "variacao_absoluta"
    )

    variacao_percentual = resultado.get(
        "variacao_percentual"
    )

    tendencia = resultado.get(
        "tendencia",
        "ESTÁVEL"
    )

    tendencia_historica = resultado.get(
        "tendencia_historica",
        "ESTÁVEL"
    )

    total_mudancas = resultado.get(
        "total_mudancas",
        0
    )

    dias_no_nivel = resultado.get(
        "dias_no_nivel",
        0
    )

    # ============================================================
    # 3. CLASSIFICAÇÃO DA DIREÇÃO
    # ============================================================

    if tendencia == "QUEDA":

        direcao = "REDUÇÃO"

    elif tendencia == "ALTA":

        direcao = "ELEVAÇÃO"

    else:

        direcao = "ESTABILIDADE"

    # ============================================================
    # 4. CLASSIFICAÇÃO DA INTENSIDADE
    # ============================================================

    intensidade = "BAIXA"

    if variacao_absoluta is not None:

        variacao = abs(
            Decimal(str(variacao_absoluta))
        )

        if variacao == 0:

            intensidade = "NENHUMA"

        elif variacao < Decimal("0.10"):

            intensidade = "MUITO BAIXA"

        elif variacao < Decimal("0.25"):

            intensidade = "BAIXA"

        elif variacao <= Decimal("0.50"):

            intensidade = "MODERADA"

        elif variacao <= Decimal("1.00"):

            intensidade = "ALTA"

        else:

            intensidade = "MUITO ALTA"

    # ============================================================
    # 5. CLASSIFICAÇÃO DA PERSISTÊNCIA
    # ============================================================

    if dias_no_nivel <= 1:

        persistencia = "MUITO RECENTE"

    elif dias_no_nivel <= 7:

        persistencia = "RECENTE"

    elif dias_no_nivel <= 30:

        persistencia = "PERSISTENTE"

    else:

        persistencia = "MUITO PERSISTENTE"

    # ============================================================
    # 6. RELAÇÃO ENTRE TENDÊNCIA ATUAL E HISTÓRICA
    # ============================================================

    coerencia_tendencia = "NEUTRA"

    if tendencia == tendencia_historica:

        if tendencia == "ESTÁVEL":
            coerencia_tendencia = "ESTÁVEL"

        else:
            coerencia_tendencia = "CONFIRMADA"

    else:

        coerencia_tendencia = "DIVERGENTE"

    # ============================================================
    # 7. CLASSIFICAÇÃO DO MOMENTO
    # ============================================================

    classificacao = "ESTABILIDADE"

    if tendencia == "QUEDA":

        if tendencia_historica == "QUEDA":

            classificacao = "FLEXIBILIZAÇÃO"

        else:

            classificacao = "INÍCIO DE FLEXIBILIZAÇÃO"

    elif tendencia == "ALTA":

        if tendencia_historica == "ALTA":

            classificacao = "APERTAMENTO"

        else:

            classificacao = "INÍCIO DE APERTAMENTO"

    else:

        if tendencia_historica == "QUEDA":

            classificacao = "ESTABILIZAÇÃO APÓS QUEDA"

        elif tendencia_historica == "ALTA":

            classificacao = "ESTABILIZAÇÃO APÓS ALTA"

        else:

            classificacao = "ESTABILIDADE"

    # ============================================================
    # 8. NÍVEL DE CONFIANÇA
    # ============================================================

    pontos = 0

    # Existência de histórico
    if resultado.get("total_observacoes", 0) >= 30:
        pontos += 2

    elif resultado.get("total_observacoes", 0) >= 10:
        pontos += 1

    # Existência de mudanças
    if total_mudancas >= 3:
        pontos += 2

    elif total_mudancas >= 1:
        pontos += 1

    # Coerência entre tendências
    if coerencia_tendencia == "CONFIRMADA":
        pontos += 2

    elif coerencia_tendencia == "DIVERGENTE":
        pontos -= 1

    # Persistência
    if dias_no_nivel >= 7:
        pontos += 2

    elif dias_no_nivel >= 3:
        pontos += 1

    # Limita a pontuação
    pontos = max(0, min(pontos, 8))

    if pontos >= 7:

        confianca = "ALTA"

    elif pontos >= 4:

        confianca = "MODERADA"

    else:

        confianca = "BAIXA"

    # ============================================================
    # 9. GERAÇÃO DA INTERPRETAÇÃO
    # ============================================================

    if indicador == "SELIC_META":

        if classificacao == "FLEXIBILIZAÇÃO":

            interpretacao = (
                "A taxa Selic apresenta sinais de flexibilização "
                "da política monetária, com a última alteração "
                "ocorrendo na direção de redução da taxa. "
                "A tendência histórica também aponta para queda, "
                "o que reforça a leitura de um ciclo de redução."
            )

        elif classificacao == "INÍCIO DE FLEXIBILIZAÇÃO":

            interpretacao = (
                "A Selic apresentou uma redução recente, porém "
                "a tendência histórica ainda não confirma "
                "claramente um ciclo sustentado de flexibilização "
                "monetária."
            )

        elif classificacao == "APERTAMENTO":

            interpretacao = (
                "A taxa Selic apresenta sinais de aperto monetário, "
                "com elevações recentes e tendência histórica "
                "também ascendente."
            )

        elif classificacao == "INÍCIO DE APERTAMENTO":

            interpretacao = (
                "A Selic apresentou uma elevação recente, porém "
                "a tendência histórica ainda não confirma "
                "claramente um ciclo sustentado de aperto monetário."
            )

        elif classificacao == "ESTABILIZAÇÃO APÓS QUEDA":

            interpretacao = (
                "A Selic encontra-se atualmente estável após um "
                "período de redução. O comportamento sugere uma "
                "pausa no processo de flexibilização, mas ainda "
                "não permite concluir que o ciclo de queda tenha "
                "terminado."
            )

        elif classificacao == "ESTABILIZAÇÃO APÓS ALTA":

            interpretacao = (
                "A Selic encontra-se atualmente estável após um "
                "período de elevação. O comportamento sugere uma "
                "pausa no processo de aperto monetário."
            )

        else:

            interpretacao = (
                "A Selic permanece estável, sem alteração recente "
                "que permita identificar uma mudança imediata na "
                "direção da política monetária."
            )

    else:

        if tendencia == "ALTA":

            interpretacao = (
                f"O indicador {indicador} apresenta movimento "
                "de elevação em sua observação mais recente."
            )

        elif tendencia == "QUEDA":

            interpretacao = (
                f"O indicador {indicador} apresenta movimento "
                "de redução em sua observação mais recente."
            )

        else:

            interpretacao = (
                f"O indicador {indicador} apresenta estabilidade "
                "em sua observação mais recente."
            )

    # ============================================================
    # 10. ALERTAS
    # ============================================================

    alertas = []

    if coerencia_tendencia == "DIVERGENTE":

        alertas.append(
            "A tendência atual diverge da tendência histórica."
        )

    if persistencia == "MUITO RECENTE":

        alertas.append(
            "A alteração é muito recente e requer novas "
            "observações para confirmação."
        )

    if confianca == "BAIXA":

        alertas.append(
            "O nível de confiança da interpretação é baixo."
        )

    # ============================================================
    # 11. RETORNO
    # ============================================================

    return {

        "status": "OK",

        "indicador": indicador,

        "valor_atual": valor_atual,

        "direcao": direcao,

        "intensidade": intensidade,

        "persistencia": persistencia,

        "coerencia_tendencia": coerencia_tendencia,

        "classificacao": classificacao,

        "confianca": confianca,

        "pontuacao_confianca": pontos,

        "interpretacao": interpretacao,

        "alertas": alertas,

        "dados_base": {

            "tendencia_atual": tendencia,

            "tendencia_historica": tendencia_historica,

            "dias_no_nivel": dias_no_nivel,

            "total_mudancas": total_mudancas,

            "variacao_absoluta": variacao_absoluta,

            "variacao_percentual": variacao_percentual
        }
    }


def exibir_interpretacao(resultado):
    """
    Exibe a interpretação econômica da Koaiala.
    """

    print("=" * 60)
    print("KOAIALA ECONOMIC INTERPRETER")
    print("=" * 60)

    if resultado.get("status") != "OK":

        print(
            f"Status: {resultado.get('status')}"
        )

        print(
            f"Mensagem: {resultado.get('mensagem')}"
        )

        print("=" * 60)

        return

    print(
        f"Indicador: {resultado['indicador']}"
    )

    print(
        f"Valor atual: {resultado['valor_atual']}"
    )

    print("-" * 60)

    print(
        f"Direção: {resultado['direcao']}"
    )

    print(
        f"Intensidade: {resultado['intensidade']}"
    )

    print(
        f"Persistência: {resultado['persistencia']}"
    )

    print(
        f"Coerência da tendência: "
        f"{resultado['coerencia_tendencia']}"
    )

    print("-" * 60)

    print(
        f"Classificação econômica: "
        f"{resultado['classificacao']}"
    )

    print(
        f"Confiança: "
        f"{resultado['confianca']}"
    )

    print(
        f"Pontuação de confiança: "
        f"{resultado['pontuacao_confianca']}/8"
    )

    print("-" * 60)

    print("INTERPRETAÇÃO:")

    print(
        resultado["interpretacao"]
    )

    # ========================================================
    # ALERTAS
    # ========================================================

    if resultado["alertas"]:

        print("-" * 60)

        print("ALERTAS:")

        for alerta in resultado["alertas"]:

            print(
                f"- {alerta}"
            )

    print("=" * 60)


def main():

    # --------------------------------------------------------
    # Por enquanto utilizamos a análise já existente da Selic.
    #
    # O próximo passo será integrar diretamente com o
    # Analysis Engine para automatizar todo o fluxo.
    # --------------------------------------------------------

    from src.insight.analysis_engine import analisar_indicador

    analise = analisar_indicador(
        "SELIC_META"
    )

    interpretacao = interpretar(
        analise
    )

    exibir_interpretacao(
        interpretacao
    )


if __name__ == "__main__":

    main()