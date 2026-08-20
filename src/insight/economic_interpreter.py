"""
KOAIALA
ECONOMIC INTERPRETER

Transforma os resultados quantitativos do Analysis Engine
em uma interpretação econômica estruturada.

A interpretação depende do significado econômico de cada
indicador e considera:

    - tendência atual
    - tendência de curto prazo
    - força da tendência
    - tendência histórica
    - força histórica
    - persistência
    - coerência

Esta camada é determinística.

Não utiliza IA generativa nem modelos estatísticos.
"""

from decimal import Decimal


# ============================================================
# CONFIGURAÇÃO ECONÔMICA DOS INDICADORES
# ============================================================

INDICATOR_INTERPRETATIONS = {

    "SELIC_META": {
        "QUEDA": "FLEXIBILIZACAO_MONETARIA",
        "ALTA": "APERTO_MONETARIO",
        "ESTÁVEL": "ESTABILIDADE_MONETARIA",
        "ESTAVEL": "ESTABILIDADE_MONETARIA",
        "ESTABILIDADE": "ESTABILIDADE_MONETARIA",
    },

    "IPCA": {
        "QUEDA": "DESINFLACAO",
        "ALTA": "ACELERACAO_INFLACIONARIA",
        "ESTÁVEL": "ESTABILIDADE_INFLACIONARIA",
        "ESTAVEL": "ESTABILIDADE_INFLACIONARIA",
        "ESTABILIDADE": "ESTABILIDADE_INFLACIONARIA",
    },

    "INPC": {
        "QUEDA": "DESINFLACAO",
        "ALTA": "ACELERACAO_INFLACIONARIA",
        "ESTÁVEL": "ESTABILIDADE_INFLACIONARIA",
        "ESTAVEL": "ESTABILIDADE_INFLACIONARIA",
        "ESTABILIDADE": "ESTABILIDADE_INFLACIONARIA",
    },

    "IGP_M": {
        "QUEDA": "DESINFLACAO",
        "ALTA": "ACELERACAO_INFLACIONARIA",
        "ESTÁVEL": "ESTABILIDADE_INFLACIONARIA",
        "ESTAVEL": "ESTABILIDADE_INFLACIONARIA",
        "ESTABILIDADE": "ESTABILIDADE_INFLACIONARIA",
    },

    "PIB": {
        "QUEDA": "DESACELERACAO_ECONOMICA",
        "ALTA": "EXPANSAO_ECONOMICA",
        "ESTÁVEL": "ESTABILIDADE_ECONOMICA",
        "ESTAVEL": "ESTABILIDADE_ECONOMICA",
        "ESTABILIDADE": "ESTABILIDADE_ECONOMICA",
    },

    "DESEMPREGO": {
        "QUEDA": "MELHORA_MERCADO_TRABALHO",
        "ALTA": "DETERIORACAO_MERCADO_TRABALHO",
        "ESTÁVEL": "ESTABILIDADE_MERCADO_TRABALHO",
        "ESTAVEL": "ESTABILIDADE_MERCADO_TRABALHO",
        "ESTABILIDADE": "ESTABILIDADE_MERCADO_TRABALHO",
    },

    "CAMBIO": {
        "QUEDA": "APRECIACAO_CAMBIAL",
        "ALTA": "DEPRECIACAO_CAMBIAL",
        "ESTÁVEL": "ESTABILIDADE_CAMBIAL",
        "ESTAVEL": "ESTABILIDADE_CAMBIAL",
        "ESTABILIDADE": "ESTABILIDADE_CAMBIAL",
    },
}


# ============================================================
# NORMALIZAÇÃO DA TENDÊNCIA
# ============================================================

def normalizar_tendencia(tendencia):

    if not isinstance(
        tendencia,
        str
    ):
        return "ESTABILIDADE"

    tendencia = (
        tendencia
        .upper()
        .strip()
    )

    if tendencia in (
        "ESTÁVEL",
        "ESTAVEL",
        "ESTABILIDADE",
    ):
        return "ESTABILIDADE"

    if tendencia == "ALTA":
        return "ALTA"

    if tendencia == "QUEDA":
        return "QUEDA"

    return "ESTABILIDADE"


# ============================================================
# NORMALIZAÇÃO DA FORÇA
# ============================================================

def normalizar_forca(forca):

    if not isinstance(
        forca,
        str
    ):
        return "MUITO_FRACA"

    return (
        forca
        .upper()
        .strip()
        .replace(" ", "_")
    )


# ============================================================
# DIREÇÃO
# ============================================================

def classificar_direcao(tendencia):

    tendencia = normalizar_tendencia(
        tendencia
    )

    if tendencia == "QUEDA":
        return "REDUÇÃO"

    if tendencia == "ALTA":
        return "ELEVAÇÃO"

    return "ESTABILIDADE"


# ============================================================
# INTENSIDADE
# ============================================================

def classificar_intensidade(
    variacao_absoluta
):

    if variacao_absoluta is None:
        return "BAIXA"

    variacao = abs(
        Decimal(
            str(
                variacao_absoluta
            )
        )
    )

    if variacao == 0:
        return "NENHUMA"

    if variacao < Decimal("0.10"):
        return "MUITO BAIXA"

    if variacao < Decimal("0.25"):
        return "BAIXA"

    if variacao <= Decimal("0.50"):
        return "MODERADA"

    if variacao <= Decimal("1.00"):
        return "ALTA"

    return "MUITO ALTA"


# ============================================================
# PERSISTÊNCIA
# ============================================================

def classificar_persistencia(
    dias_no_nivel
):

    if dias_no_nivel is None:
        dias_no_nivel = 0

    if dias_no_nivel <= 1:
        return "MUITO RECENTE"

    if dias_no_nivel <= 7:
        return "RECENTE"

    if dias_no_nivel <= 30:
        return "PERSISTENTE"

    return "MUITO PERSISTENTE"


# ============================================================
# COERÊNCIA
# ============================================================

def classificar_coerencia(
    tendencia_atual,
    tendencia_curta,
    tendencia_historica
):

    atual = normalizar_tendencia(
        tendencia_atual
    )

    curta = normalizar_tendencia(
        tendencia_curta
    )

    historica = normalizar_tendencia(
        tendencia_historica
    )

    if (
        atual == curta
        and curta == historica
    ):

        return "CONFIRMADA"

    if (
        atual == curta
        and historica == "ESTABILIDADE"
    ):

        return "RECENTE"

    if (
        atual != curta
    ):

        return "DIVERGENTE"

    return "PARCIAL"


# ============================================================
# CLASSIFICAÇÃO DA SELIC
# ============================================================

def classificar_selic(
    tendencia_atual,
    tendencia_curta,
    tendencia_historica,
    forca_historica
):

    atual = normalizar_tendencia(
        tendencia_atual
    )

    curta = normalizar_tendencia(
        tendencia_curta
    )

    historica = normalizar_tendencia(
        tendencia_historica
    )

    forca = normalizar_forca(
        forca_historica
    )

    if (
        atual == "QUEDA"
        and curta == "QUEDA"
    ):

        if historica == "QUEDA":
            return "FLEXIBILIZACAO"

        return "INICIO_DE_FLEXIBILIZACAO"

    if (
        atual == "ALTA"
        and curta == "ALTA"
    ):

        if historica == "ALTA":
            return "APERTAMENTO"

        return "INICIO_DE_APERTAMENTO"

    if (
        atual == "ESTABILIDADE"
        and curta == "ESTABILIDADE"
    ):

        if (
            historica == "QUEDA"
            and forca in (
                "FORTE",
                "MUITO_FORTE",
            )
        ):

            return "ESTABILIZACAO_APOS_QUEDA"

        if (
            historica == "ALTA"
            and forca in (
                "FORTE",
                "MUITO_FORTE",
            )
        ):

            return "ESTABILIZACAO_APOS_ALTA"

        return "ESTABILIDADE"

    return "MOVIMENTO_INDEFINIDO"


# ============================================================
# CLASSIFICAÇÃO DA INFLAÇÃO
# ============================================================

def classificar_inflacao(
    tendencia_atual,
    tendencia_curta,
    tendencia_historica,
    forca_curta
):

    atual = normalizar_tendencia(
        tendencia_atual
    )

    curta = normalizar_tendencia(
        tendencia_curta
    )

    historica = normalizar_tendencia(
        tendencia_historica
    )

    forca = normalizar_forca(
        forca_curta
    )

    # --------------------------------------------------------
    # DESINFLAÇÃO
    # --------------------------------------------------------

    if (
        atual == "QUEDA"
        and curta == "QUEDA"
    ):

        if (
            historica == "QUEDA"
            and forca in (
                "MODERADA",
                "FORTE",
                "MUITO_FORTE",
            )
        ):

            return "DESINFLACAO_CONFIRMADA"

        return "INICIO_DE_DESINFLACAO"

    # --------------------------------------------------------
    # ACELERAÇÃO
    # --------------------------------------------------------

    if (
        atual == "ALTA"
        and curta == "ALTA"
    ):

        if historica == "ALTA":

            return "ACELERACAO_INFLACIONARIA"

        return "INICIO_DE_ACELERACAO_INFLACIONARIA"

    # --------------------------------------------------------
    # ESTABILIDADE
    # --------------------------------------------------------

    if atual == "ESTABILIDADE":

        if historica == "QUEDA":
            return "ESTABILIZACAO_APOS_DESINFLACAO"

        if historica == "ALTA":
            return "ESTABILIZACAO_APOS_ACELERACAO"

        return "ESTABILIDADE_INFLACIONARIA"

    return "MOVIMENTO_INDEFINIDO"


# ============================================================
# CLASSIFICAÇÃO ECONÔMICA
# ============================================================

def classificar_momento(
    indicador,
    tendencia_atual,
    tendencia_curta,
    tendencia_historica,
    forca_tendencia_curta,
    forca_tendencia_historica
):

    indicador = (
        indicador
        .upper()
        .strip()
    )

    if indicador == "SELIC_META":

        return classificar_selic(
            tendencia_atual,
            tendencia_curta,
            tendencia_historica,
            forca_tendencia_historica
        )

    if indicador in (
        "IPCA",
        "INPC",
        "IGP_M",
    ):

        return classificar_inflacao(
            tendencia_atual,
            tendencia_curta,
            tendencia_historica,
            forca_tendencia_curta
        )

    # --------------------------------------------------------
    # PIB
    # --------------------------------------------------------

    if indicador == "PIB":

        atual = normalizar_tendencia(
            tendencia_atual
        )

        curta = normalizar_tendencia(
            tendencia_curta
        )

        historica = normalizar_tendencia(
            tendencia_historica
        )

        if (
            atual == "ALTA"
            and curta == "ALTA"
        ):

            if historica == "ALTA":
                return "EXPANSAO_CONFIRMADA"

            return "INICIO_DE_EXPANSAO"

        if (
            atual == "QUEDA"
            and curta == "QUEDA"
        ):

            if historica == "QUEDA":
                return "DESACELERACAO_CONFIRMADA"

            return "INICIO_DE_DESACELERACAO"

        return "ESTABILIDADE_ECONOMICA"

    # --------------------------------------------------------
    # DESEMPREGO
    # --------------------------------------------------------

    if indicador == "DESEMPREGO":

        atual = normalizar_tendencia(
            tendencia_atual
        )

        curta = normalizar_tendencia(
            tendencia_curta
        )

        historica = normalizar_tendencia(
            tendencia_historica
        )

        if (
            atual == "QUEDA"
            and curta == "QUEDA"
        ):

            if historica == "QUEDA":
                return "MELHORA_MERCADO_TRABALHO"

            return "INICIO_DE_MELHORA_MERCADO_TRABALHO"

        if (
            atual == "ALTA"
            and curta == "ALTA"
        ):

            if historica == "ALTA":
                return "DETERIORACAO_MERCADO_TRABALHO"

            return "INICIO_DE_DETERIORACAO_MERCADO_TRABALHO"

        return "ESTABILIDADE_MERCADO_TRABALHO"

    # --------------------------------------------------------
    # CÂMBIO
    # --------------------------------------------------------

    if indicador == "CAMBIO":

        atual = normalizar_tendencia(
            tendencia_atual
        )

        curta = normalizar_tendencia(
            tendencia_curta
        )

        historica = normalizar_tendencia(
            tendencia_historica
        )

        if (
            atual == "ALTA"
            and curta == "ALTA"
        ):

            if historica == "ALTA":
                return "DEPRECIACAO_CAMBIAL"

            return "INICIO_DE_DEPRECIACAO_CAMBIAL"

        if (
            atual == "QUEDA"
            and curta == "QUEDA"
        ):

            if historica == "QUEDA":
                return "APRECIACAO_CAMBIAL"

            return "INICIO_DE_APRECIACAO_CAMBIAL"

        return "ESTABILIDADE_CAMBIAL"

    return "INDICADOR_NAO_CONFIGURADO"


# ============================================================
# INTERPRETAÇÃO TEXTUAL
# ============================================================

def gerar_interpretacao(
    indicador,
    classificacao,
    tendencia_atual,
    tendencia_curta,
    tendencia_historica,
    forca_tendencia_curta
):

    indicador = (
        indicador
        .upper()
        .strip()
    )

    forca = normalizar_forca(
        forca_tendencia_curta
    )

    # --------------------------------------------------------
    # SELIC
    # --------------------------------------------------------

    if indicador == "SELIC_META":

        mensagens = {

            "FLEXIBILIZACAO":
                "A Selic apresenta redução recente e "
                "continuidade da tendência de queda, "
                "compatível com um ciclo de flexibilização "
                "da política monetária.",

            "INICIO_DE_FLEXIBILIZACAO":
                "A Selic apresenta redução recente, mas "
                "a tendência histórica ainda não confirma "
                "claramente um ciclo sustentado de "
                "flexibilização.",

            "APERTAMENTO":
                "A Selic apresenta elevação recente e "
                "continuidade da tendência de alta, "
                "compatível com aperto da política monetária.",

            "INICIO_DE_APERTAMENTO":
                "A Selic apresentou elevação recente, mas "
                "a tendência histórica ainda não confirma "
                "claramente um ciclo sustentado de aperto.",

            "ESTABILIZACAO_APOS_QUEDA":
                "A Selic encontra-se estável após um ciclo "
                "de redução, indicando uma pausa na "
                "flexibilização monetária.",

            "ESTABILIZACAO_APOS_ALTA":
                "A Selic encontra-se estável após um ciclo "
                "de elevação, indicando uma pausa no "
                "aperto monetário.",

            "ESTABILIDADE":
                "A Selic permanece estável, sem evidência "
                "de alteração recente na direção da "
                "política monetária.",

            "MOVIMENTO_INDEFINIDO":
                "A Selic apresenta movimentos recentes "
                "sem direção suficientemente consistente "
                "para caracterizar um novo ciclo.",
        }

        return mensagens.get(
            classificacao,
            "A Selic apresenta comportamento "
            "sem classificação específica."
        )

    # --------------------------------------------------------
    # INFLAÇÃO
    # --------------------------------------------------------

    if indicador in (
        "IPCA",
        "INPC",
        "IGP_M",
    ):

        mensagens = {

            "DESINFLACAO_CONFIRMADA":
                f"O {indicador} apresenta redução recente "
                "e continuidade da tendência de queda, "
                "com evidências compatíveis com um processo "
                "de desinflação.",

            "INICIO_DE_DESINFLACAO":
                f"O {indicador} apresenta redução recente "
                f"com força {forca}, mas a tendência histórica "
                "não confirma ainda uma trajetória estrutural "
                "de desinflação.",

            "ACELERACAO_INFLACIONARIA":
                f"O {indicador} apresenta elevação recente "
                "e continuidade histórica de alta, "
                "caracterizando aceleração inflacionária.",

            "INICIO_DE_ACELERACAO_INFLACIONARIA":
                f"O {indicador} apresenta elevação recente, "
                "mas ainda não há confirmação suficiente "
                "de uma aceleração inflacionária estrutural.",

            "ESTABILIZACAO_APOS_DESINFLACAO":
                f"O {indicador} encontra-se estável após "
                "um período de redução.",

            "ESTABILIZACAO_APOS_ACELERACAO":
                f"O {indicador} encontra-se estável após "
                "um período de elevação.",

            "ESTABILIDADE_INFLACIONARIA":
                f"O {indicador} apresenta estabilidade "
                "sem uma direção predominante clara.",

            "MOVIMENTO_INDEFINIDO":
                f"O {indicador} apresenta movimentos "
                "recentes sem direção suficientemente "
                "consistente.",
        }

        return mensagens.get(
            classificacao,
            f"O {indicador} apresenta comportamento "
            "sem classificação específica."
        )

    # --------------------------------------------------------
    # PIB
    # --------------------------------------------------------

    if indicador == "PIB":

        if classificacao == "EXPANSAO_CONFIRMADA":

            return (
                "O PIB apresenta expansão recente e "
                "continuidade histórica, compatível com "
                "um processo de crescimento econômico."
            )

        if classificacao == "INICIO_DE_EXPANSAO":

            return (
                "O PIB apresenta melhora recente, mas "
                "a tendência histórica ainda não confirma "
                "uma expansão econômica sustentada."
            )

        if classificacao == "DESACELERACAO_CONFIRMADA":

            return (
                "O PIB apresenta redução recente e "
                "continuidade histórica de queda, "
                "compatível com desaceleração econômica."
            )

        if classificacao == "INICIO_DE_DESACELERACAO":

            return (
                "O PIB apresenta redução recente, mas "
                "a tendência histórica ainda não confirma "
                "uma desaceleração sustentada."
            )

        return (
            "O PIB não apresenta direção suficientemente "
            "consistente para caracterizar expansão ou "
            "desaceleração."
        )

    # --------------------------------------------------------
    # DESEMPREGO
    # --------------------------------------------------------

    if indicador == "DESEMPREGO":

        if classificacao == "MELHORA_MERCADO_TRABALHO":

            return (
                "O desemprego apresenta redução recente "
                "e continuidade histórica, compatível "
                "com melhora do mercado de trabalho."
            )

        if classificacao == "INICIO_DE_MELHORA_MERCADO_TRABALHO":

            return (
                "O desemprego apresenta redução recente, "
                "mas a tendência histórica ainda não "
                "confirma uma melhora sustentada."
            )

        if classificacao == "DETERIORACAO_MERCADO_TRABALHO":

            return (
                "O desemprego apresenta elevação recente "
                "e continuidade histórica, compatível "
                "com deterioração do mercado de trabalho."
            )

        if classificacao == "INICIO_DE_DETERIORACAO_MERCADO_TRABALHO":

            return (
                "O desemprego apresenta elevação recente, "
                "mas a tendência histórica ainda não "
                "confirma deterioração sustentada."
            )

        return (
            "O desemprego apresenta estabilidade "
            "ou ausência de direção suficientemente "
            "consistente."
        )

    # --------------------------------------------------------
    # CÂMBIO
    # --------------------------------------------------------

    if indicador == "CAMBIO":

        if classificacao == "DEPRECIACAO_CAMBIAL":

            return (
                "O câmbio apresenta elevação recente "
                "e continuidade histórica, compatível "
                "com depreciação cambial."
            )

        if classificacao == "INICIO_DE_DEPRECIACAO_CAMBIAL":

            return (
                "O câmbio apresenta elevação recente, "
                "mas a tendência histórica ainda não "
                "confirma uma depreciação sustentada."
            )

        if classificacao == "APRECIACAO_CAMBIAL":

            return (
                "O câmbio apresenta redução recente "
                "e continuidade histórica, compatível "
                "com apreciação cambial."
            )

        if classificacao == "INICIO_DE_APRECIACAO_CAMBIAL":

            return (
                "O câmbio apresenta redução recente, "
                "mas a tendência histórica ainda não "
                "confirma uma apreciação sustentada."
            )

        return (
            "O câmbio apresenta estabilidade ou "
            "movimento sem direção suficientemente "
            "consistente."
        )

    return (
        f"O indicador {indicador} apresenta "
        "comportamento que requer análise adicional."
    )


# ============================================================
# INTERPRETAÇÃO PRINCIPAL
# ============================================================

def interpretar(
    resultado
):

    if resultado.get(
        "status"
    ) != "OK":

        return {
            "status": "ERRO",
            "mensagem":
                resultado.get(
                    "mensagem",
                    "Resultado de análise inválido."
                )
        }

    indicador = resultado[
        "indicador"
    ]

    valor_atual = Decimal(
        str(
            resultado[
                "valor_atual"
            ]
        )
    )

    variacao_absoluta = (
        resultado.get(
            "variacao_absoluta"
        )
    )

    variacao_percentual = (
        resultado.get(
            "variacao_percentual"
        )
    )

    tendencia_atual = (
        resultado.get(
            "tendencia_atual",
            resultado.get(
                "tendencia",
                "ESTABILIDADE"
            )
        )
    )

    tendencia_curta = (
        resultado.get(
            "tendencia_curta",
            tendencia_atual
        )
    )

    tendencia_historica = (
        resultado.get(
            "tendencia_historica",
            "ESTABILIDADE"
        )
    )

    forca_tendencia = (
        resultado.get(
            "forca_tendencia",
            "MUITO_FRACA"
        )
    )

    forca_tendencia_curta = (
        resultado.get(
            "forca_tendencia_curta",
            forca_tendencia
        )
    )

    forca_tendencia_historica = (
        resultado.get(
            "forca_tendencia_historica",
            "MUITO_FRACA"
        )
    )

    total_mudancas = (
        resultado.get(
            "total_mudancas",
            0
        )
    )

    dias_no_nivel = (
        resultado.get(
            "dias_no_nivel",
            0
        )
    )

    total_observacoes = (
        resultado.get(
            "total_observacoes",
            0
        )
    )

    # ========================================================
    # NORMALIZAÇÃO
    # ========================================================

    tendencia_atual = (
        normalizar_tendencia(
            tendencia_atual
        )
    )

    tendencia_curta = (
        normalizar_tendencia(
            tendencia_curta
        )
    )

    tendencia_historica = (
        normalizar_tendencia(
            tendencia_historica
        )
    )

    forca_tendencia_curta = (
        normalizar_forca(
            forca_tendencia_curta
        )
    )

    forca_tendencia_historica = (
        normalizar_forca(
            forca_tendencia_historica
        )
    )

    # ========================================================
    # CLASSIFICAÇÕES
    # ========================================================

    direcao = classificar_direcao(
        tendencia_atual
    )

    intensidade = classificar_intensidade(
        variacao_absoluta
    )

    persistencia = classificar_persistencia(
        dias_no_nivel
    )

    coerencia_tendencia = (
        classificar_coerencia(
            tendencia_atual,
            tendencia_curta,
            tendencia_historica
        )
    )

    classificacao = classificar_momento(
        indicador,
        tendencia_atual,
        tendencia_curta,
        tendencia_historica,
        forca_tendencia_curta,
        forca_tendencia_historica
    )

    # ========================================================
    # CONFIANÇA
    # ========================================================

    pontos = 0

    # Base de dados
    if total_observacoes >= 30:
        pontos += 2

    elif total_observacoes >= 10:
        pontos += 1

    # Mudanças observadas
    if total_mudancas >= 3:
        pontos += 2

    elif total_mudancas >= 1:
        pontos += 1

    # Tendência atual e curta concordantes
    if (
        tendencia_atual
        == tendencia_curta
    ):

        pontos += 2

    # Tendência curta forte
    if forca_tendencia_curta in (
        "FORTE",
        "MUITO_FORTE",
    ):

        pontos += 2

    elif forca_tendencia_curta == "MODERADA":

        pontos += 1

    # Histórico divergente reduz confiança
    if (
        tendencia_historica
        not in (
            tendencia_curta,
            "ESTABILIDADE",
        )
    ):

        pontos -= 1

    pontos = max(
        0,
        min(
            pontos,
            9
        )
    )

    if pontos >= 7:
        confianca = "ALTA"

    elif pontos >= 4:
        confianca = "MODERADA"

    else:
        confianca = "BAIXA"

    # ========================================================
    # INTERPRETAÇÃO
    # ========================================================

    interpretacao = gerar_interpretacao(
        indicador,
        classificacao,
        tendencia_atual,
        tendencia_curta,
        tendencia_historica,
        forca_tendencia_curta
    )

    # ========================================================
    # ALERTAS
    # ========================================================

    alertas = []

    if (
        tendencia_atual
        != tendencia_curta
    ):

        alertas.append(
            "A tendência atual diverge da "
            "tendência de curto prazo."
        )

    if (
        tendencia_historica
        not in (
            tendencia_curta,
            "ESTABILIDADE",
        )
    ):

        alertas.append(
            "A tendência histórica diverge "
            "da tendência recente."
        )

    if persistencia == "MUITO RECENTE":

        alertas.append(
            "A alteração é muito recente e "
            "requer novas observações para confirmação."
        )

    if confianca == "BAIXA":

        alertas.append(
            "O nível de confiança da interpretação "
            "é baixo."
        )

    # ========================================================
    # RETORNO
    # ========================================================

    return {

        "status":
            "OK",

        "indicador":
            indicador,

        "valor_atual":
            valor_atual,

        "direcao":
            direcao,

        "intensidade":
            intensidade,

        "persistencia":
            persistencia,

        "coerencia_tendencia":
            coerencia_tendencia,

        "classificacao":
            classificacao,

        "confianca":
            confianca,

        "pontuacao_confianca":
            pontos,

        "interpretacao":
            interpretacao,

        "alertas":
            alertas,

        "dados_base": {

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

            "dias_no_nivel":
                dias_no_nivel,

            "total_mudancas":
                total_mudancas,

            "variacao_absoluta":
                variacao_absoluta,

            "variacao_percentual":
                variacao_percentual,
        }
    }


# ============================================================
# EXIBIÇÃO
# ============================================================

def exibir_interpretacao(
    resultado
):

    print("=" * 60)

    print(
        "KOAIALA ECONOMIC INTERPRETER"
    )

    print("=" * 60)

    if (
        resultado.get(
            "status"
        )
        != "OK"
    ):

        print(
            f"Status: "
            f"{resultado.get('status')}"
        )

        print(
            f"Mensagem: "
            f"{resultado.get('mensagem')}"
        )

        print("=" * 60)

        return

    print(
        f"Indicador: "
        f"{resultado['indicador']}"
    )

    print(
        f"Valor atual: "
        f"{resultado['valor_atual']}"
    )

    print("-" * 60)

    print(
        f"Direção: "
        f"{resultado['direcao']}"
    )

    print(
        f"Intensidade: "
        f"{resultado['intensidade']}"
    )

    print(
        f"Persistência: "
        f"{resultado['persistencia']}"
    )

    print(
        f"Coerência: "
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
        f"Pontuação: "
        f"{resultado['pontuacao_confianca']}/9"
    )

    print("-" * 60)

    print(
        "INTERPRETAÇÃO:"
    )

    print(
        resultado["interpretacao"]
    )

    if resultado["alertas"]:

        print("-" * 60)

        print(
            "ALERTAS:"
        )

        for alerta in (
            resultado["alertas"]
        ):

            print(
                f"- {alerta}"
            )

    print("=" * 60)


# ============================================================
# TESTE
# ============================================================

def main():

    from src.insight.analysis_engine import (
        analisar_indicador
    )

    indicadores = [
        "SELIC_META",
        "IPCA",
        "INPC",
        "IGP_M",
    ]

    print("=" * 60)

    print(
        "KOAIALA ECONOMIC INTERPRETER"
    )

    print("=" * 60)

    for indicador in indicadores:

        print()

        print(
            f"ANALISANDO: {indicador}"
        )

        print()

        analise = (
            analisar_indicador(
                indicador
            )
        )

        interpretacao = (
            interpretar(
                analise
            )
        )

        exibir_interpretacao(
            interpretacao
        )

    print()

    print("=" * 60)

    print(
        "INTERPRETER FUNCIONANDO ✓"
    )

    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()