from decimal import Decimal

from src.insight.analysis_engine import analisar_indicador
from src.insight.economic_interpreter import interpretar


# ============================================================
# CONFIGURAÇÃO DOS INDICADORES
# ============================================================

INDICADORES = {
    "SELIC_META": {
        "peso": Decimal("1.0"),
        "grupo": "politica_monetaria"
    }
}


# ============================================================
# ANÁLISE INDIVIDUAL
# ============================================================

def analisar_indicadores():
    """
    Executa o Analysis Engine e o Economic Interpreter
    para todos os indicadores configurados.
    """

    resultados = {}

    for codigo, configuracao in INDICADORES.items():

        analise = analisar_indicador(codigo)

        if analise.get("status") != "OK":

            resultados[codigo] = {
                "status": "ERRO",
                "mensagem": analise.get(
                    "mensagem",
                    "Erro ao analisar indicador."
                )
            }

            continue

        interpretacao = interpretar(analise)

        resultados[codigo] = {
            "status": "OK",
            "peso": configuracao["peso"],
            "grupo": configuracao["grupo"],
            "analise": analise,
            "interpretacao": interpretacao
        }

    return resultados


# ============================================================
# CONVERSÃO DO SINAL ECONÔMICO
# ============================================================

def obter_sinal(indicador):
    """
    Converte a interpretação econômica em um sinal numérico.

    +1  = sinal expansionista/favorável
     0  = neutro
    -1  = sinal contracionista/desfavorável

    Para a Selic:
    QUEDA  -> +1
    ALTA   -> -1
    ESTÁVEL -> 0
    """

    interpretacao = indicador["interpretacao"]

    direcao = interpretacao.get(
        "direcao",
        "ESTABILIDADE"
    )

    if direcao == "REDUÇÃO":
        return Decimal("1")

    if direcao == "ELEVAÇÃO":
        return Decimal("-1")

    return Decimal("0")


# ============================================================
# CÁLCULO DO SCORE
# ============================================================

def calcular_score(resultados):
    """
    Calcula o score econômico agregado.

    O score varia de -1 a +1.

    +1 = conjunto de sinais expansionistas
     0 = cenário neutro
    -1 = conjunto de sinais contracionistas
    """

    soma_ponderada = Decimal("0")
    soma_pesos = Decimal("0")

    for codigo, resultado in resultados.items():

        if resultado.get("status") != "OK":
            continue

        peso = resultado["peso"]

        sinal = obter_sinal(resultado)

        soma_ponderada += sinal * peso
        soma_pesos += peso

    if soma_pesos == 0:

        return Decimal("0")

    score = soma_ponderada / soma_pesos

    return score


# ============================================================
# CLASSIFICAÇÃO DO CENÁRIO
# ============================================================

def classificar_cenario(score):
    """
    Classifica o cenário econômico agregado.
    """

    if score >= Decimal("0.50"):

        return "EXPANSIONISTA"

    if score >= Decimal("0.15"):

        return "LEVE EXPANSÃO"

    if score > Decimal("-0.15"):

        return "NEUTRO"

    if score > Decimal("-0.50"):

        return "LEVE CONTRAÇÃO"

    return "CONTRACIONISTA"


# ============================================================
# CONFIANÇA DO CENÁRIO
# ============================================================

def calcular_confianca(resultados):
    """
    Calcula uma confiança inicial baseada na qualidade
    das interpretações disponíveis.

    Esta não é uma probabilidade estatística.
    """

    indicadores_validos = 0
    soma_confianca = Decimal("0")

    mapa_confianca = {
        "ALTA": Decimal("1.0"),
        "MODERADA": Decimal("0.6"),
        "BAIXA": Decimal("0.3")
    }

    for resultado in resultados.values():

        if resultado.get("status") != "OK":
            continue

        indicadores_validos += 1

        confianca = resultado[
            "interpretacao"
        ].get(
            "confianca",
            "BAIXA"
        )

        soma_confianca += mapa_confianca.get(
            confianca,
            Decimal("0.3")
        )

    if indicadores_validos == 0:

        return {
            "nivel": "BAIXA",
            "score": Decimal("0")
        }

    score = (
        soma_confianca
        / Decimal(str(indicadores_validos))
    )

    if score >= Decimal("0.80"):

        nivel = "ALTA"

    elif score >= Decimal("0.50"):

        nivel = "MODERADA"

    else:

        nivel = "BAIXA"

    return {
        "nivel": nivel,
        "score": score
    }


# ============================================================
# CENÁRIOS ALTERNATIVOS
# ============================================================

def gerar_cenarios(score):
    """
    Gera três cenários estruturais.

    Importante:
    estes cenários ainda não representam probabilidades.
    São hipóteses qualitativas.
    """

    # --------------------------------------------------------
    # CENÁRIO EXPANSIONISTA
    # --------------------------------------------------------

    if score > Decimal("0"):

        expansionista = (
            "Cenário compatível com maior flexibilização "
            "das condições monetárias e financeiras."
        )

    else:

        expansionista = (
            "Cenário expansionista exigiria uma melhora "
            "dos sinais atualmente observados."
        )

    # --------------------------------------------------------
    # CENÁRIO BASE
    # --------------------------------------------------------

    base = (
        "Cenário de continuidade das condições econômicas "
        "atuais, sem mudança estrutural significativa."
    )

    # --------------------------------------------------------
    # CENÁRIO CONTRACIONISTA
    # --------------------------------------------------------

    if score < Decimal("0"):

        contracionista = (
            "Cenário compatível com maior restrição "
            "monetária e financeira."
        )

    else:

        contracionista = (
            "Cenário contracionista exigiria uma piora "
            "dos sinais atualmente observados."
        )

    return {

        "expansionista": expansionista,

        "base": base,

        "contracionista": contracionista
    }


# ============================================================
# GERAÇÃO DA LEITURA ECONÔMICA
# ============================================================

def gerar_interpretacao_cenario(
    classificacao,
    score,
    resultados
):
    """
    Produz uma interpretação textual do cenário agregado.
    """

    indicadores_validos = [
        codigo
        for codigo, resultado in resultados.items()
        if resultado.get("status") == "OK"
    ]

    if not indicadores_validos:

        return (
            "Não existem indicadores suficientes para "
            "produzir uma leitura econômica."
        )

    if classificacao == "EXPANSIONISTA":

        texto = (
            "Os sinais disponíveis apontam para um ambiente "
            "predominantemente expansionista."
        )

    elif classificacao == "LEVE EXPANSÃO":

        texto = (
            "Os sinais disponíveis apresentam viés "
            "levemente expansionista."
        )

    elif classificacao == "NEUTRO":

        texto = (
            "Os sinais disponíveis não apresentam "
            "predominância clara entre expansão e contração."
        )

    elif classificacao == "LEVE CONTRAÇÃO":

        texto = (
            "Os sinais disponíveis apresentam viés "
            "levemente contracionista."
        )

    else:

        texto = (
            "Os sinais disponíveis apontam para um ambiente "
            "predominantemente contracionista."
        )

    texto += (
        f" O score agregado calculado foi "
        f"{score:.2f}."
    )

    return texto


# ============================================================
# MOTOR PRINCIPAL
# ============================================================

def construir_cenario():
    """
    Executa o fluxo completo do Scenario Engine.
    """

    resultados = analisar_indicadores()

    indicadores_validos = [
        codigo
        for codigo, resultado in resultados.items()
        if resultado.get("status") == "OK"
    ]

    if not indicadores_validos:

        return {
            "status": "ERRO",
            "mensagem": (
                "Nenhum indicador válido disponível."
            )
        }

    score = calcular_score(resultados)

    classificacao = classificar_cenario(
        score
    )

    confianca = calcular_confianca(
        resultados
    )

    cenarios = gerar_cenarios(
        score
    )

    interpretacao = gerar_interpretacao_cenario(
        classificacao,
        score,
        resultados
    )

    return {

        "status": "OK",

        "score": score,

        "classificacao": classificacao,

        "confianca": confianca,

        "indicadores_analisados": (
            indicadores_validos
        ),

        "total_indicadores": len(
            indicadores_validos
        ),

        "cenarios": cenarios,

        "interpretacao": interpretacao,

        "indicadores": resultados
    }


# ============================================================
# EXIBIÇÃO
# ============================================================

def exibir_cenario(resultado):
    """
    Exibe o cenário econômico da Koaiala.
    """

    print("=" * 60)
    print("KOAIALA SCENARIO ENGINE")
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
        "Indicadores analisados: "
        f"{resultado['total_indicadores']}"
    )

    print(
        f"Indicadores: "
        f"{', '.join(resultado['indicadores_analisados'])}"
    )

    print("-" * 60)

    print(
        f"Score econômico: "
        f"{resultado['score']:.2f}"
    )

    print(
        f"Classificação: "
        f"{resultado['classificacao']}"
    )

    print(
        f"Confiança: "
        f"{resultado['confianca']['nivel']}"
    )

    print(
        f"Score de confiança: "
        f"{resultado['confianca']['score']:.2f}"
    )

    print("-" * 60)

    print("LEITURA ECONÔMICA:")

    print(
        resultado["interpretacao"]
    )

    print("-" * 60)

    print("CENÁRIOS:")

    print()

    print("EXPANSIONISTA:")
    print(
        resultado["cenarios"]["expansionista"]
    )

    print()

    print("BASE:")
    print(
        resultado["cenarios"]["base"]
    )

    print()

    print("CONTRACIONISTA:")
    print(
        resultado["cenarios"]["contracionista"]
    )

    print("-" * 60)

    print("SINAIS DOS INDICADORES:")

    for codigo, indicador in resultado[
        "indicadores"
    ].items():

        if indicador.get("status") != "OK":

            print(
                f"{codigo}: ERRO"
            )

            continue

        interpretacao = indicador[
            "interpretacao"
        ]

        sinal = obter_sinal(
            indicador
        )

        print(
            f"{codigo}: "
            f"{interpretacao['direcao']} "
            f"(sinal {sinal:+.0f})"
        )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    resultado = construir_cenario()

    exibir_cenario(
        resultado
    )


if __name__ == "__main__":

    main()