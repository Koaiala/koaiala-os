"""
KOAIALA - ECONOMIC SCORE ENGINE

Transforma movimentos dos indicadores econômicos em
impactos econômicos padronizados e calcula um score
agregado para o Scenario Engine.

Escala interna:

+2 = forte impacto favorável
+1 = impacto favorável
 0 = neutro
-1 = impacto desfavorável
-2 = forte impacto desfavorável
"""

from typing import Dict, List


# ============================================================
# PESOS DOS INDICADORES
# ============================================================

INDICATOR_WEIGHTS = {
    "SELIC_META": 0.20,
    "IPCA": 0.20,
    "PIB": 0.25,
    "DESEMPREGO": 0.20,
    "CAMBIO": 0.15,
}


# ============================================================
# DIREÇÃO ECONÔMICA
#
# "ALTA" e "QUEDA" não possuem o mesmo significado
# econômico para todos os indicadores.
#
# Exemplo:
#
# IPCA ↓       -> geralmente favorável
# PIB ↓        -> desfavorável
# Desemprego ↓ -> favorável
# ============================================================

ECONOMIC_DIRECTION = {

    "SELIC_META": {
        "FORTE_ALTA": -2,
        "ALTA": -1,
        "ESTABILIDADE": 0,
        "NEUTRO": 0,
        "QUEDA": 1,
        "FORTE_QUEDA": 2,
    },

    "IPCA": {
        "FORTE_ALTA": -2,
        "ALTA": -1,
        "ESTABILIDADE": 0,
        "NEUTRO": 0,
        "QUEDA": 1,
        "FORTE_QUEDA": 2,
    },

    "PIB": {
        "FORTE_ALTA": 2,
        "ALTA": 1,
        "ESTABILIDADE": 0,
        "NEUTRO": 0,
        "QUEDA": -1,
        "FORTE_QUEDA": -2,
    },

    "DESEMPREGO": {
        "FORTE_ALTA": -2,
        "ALTA": -1,
        "ESTABILIDADE": 0,
        "NEUTRO": 0,
        "QUEDA": 1,
        "FORTE_QUEDA": 2,
    },

    "CAMBIO": {
        "FORTE_ALTA": -1,
        "ALTA": -1,
        "ESTABILIDADE": 0,
        "NEUTRO": 0,
        "QUEDA": 1,
        "FORTE_QUEDA": 1,
    },
}


# ============================================================
# CLASSIFICAÇÃO DO SCORE
# ============================================================

SCENARIO_THRESHOLDS = {
    "MUITO_OTIMISTA": 1.25,
    "OTIMISTA": 0.50,
    "NEUTRO_SUPERIOR": 0.15,
    "NEUTRO_INFERIOR": -0.15,
    "ADVERSO": -0.50,
    "MUITO_ADVERSO": -1.25,
}


# ============================================================
# NORMALIZAÇÃO DO SINAL
# ============================================================

def normalizar_sinal(sinal: str) -> str:
    """
    Normaliza o texto recebido pelo motor.
    """

    if not isinstance(sinal, str):
        return "NEUTRO"

    sinal = sinal.upper().strip()

    aliases = {
        "ALTA FORTE": "FORTE_ALTA",
        "FORTE ALTA": "FORTE_ALTA",
        "ALTA": "ALTA",

        "QUEDA FORTE": "FORTE_QUEDA",
        "FORTE QUEDA": "FORTE_QUEDA",
        "QUEDA": "QUEDA",

        "ESTAVEL": "ESTABILIDADE",
        "ESTÁVEL": "ESTABILIDADE",
        "ESTABILIDADE": "ESTABILIDADE",

        "NEUTRO": "NEUTRO",
    }

    return aliases.get(sinal, "NEUTRO")


# ============================================================
# SCORE ECONÔMICO DO INDICADOR
# ============================================================

def calcular_score_indicador(
    indicador: str,
    sinal: str
) -> Dict:

    indicador = indicador.upper().strip()

    sinal_normalizado = normalizar_sinal(sinal)

    peso = INDICATOR_WEIGHTS.get(indicador, 0)

    direcoes = ECONOMIC_DIRECTION.get(
        indicador,
        {}
    )

    score = direcoes.get(
        sinal_normalizado,
        0
    )

    score_ponderado = score * peso

    return {
        "indicador": indicador,
        "sinal": sinal_normalizado,
        "score": score,
        "peso": peso,
        "score_ponderado": score_ponderado,
    }


# ============================================================
# SCORE ECONÔMICO AGREGADO
# ============================================================

def calcular_score_economico(
    sinais: Dict[str, str]
) -> Dict:

    resultados: List[Dict] = []

    score_total = 0.0
    peso_utilizado = 0.0

    for indicador, sinal in sinais.items():

        resultado = calcular_score_indicador(
            indicador,
            sinal
        )

        # Ignora indicadores desconhecidos
        # que não possuem peso configurado.
        if resultado["peso"] <= 0:
            continue

        resultados.append(resultado)

        score_total += resultado["score_ponderado"]

        peso_utilizado += resultado["peso"]

    # --------------------------------------------------------
    # NORMALIZAÇÃO
    # --------------------------------------------------------

    if peso_utilizado > 0:

        score_normalizado = (
            score_total / peso_utilizado
        )

    else:

        score_normalizado = 0.0

    classificacao = classificar_score(
        score_normalizado
    )

    return {
        "score_total": round(
            score_total,
            4
        ),

        "score_normalizado": round(
            score_normalizado,
            4
        ),

        "peso_utilizado": round(
            peso_utilizado,
            4
        ),

        "classificacao": classificacao,

        "indicadores": resultados,
    }


# ============================================================
# CLASSIFICAÇÃO DO CENÁRIO
# ============================================================

def classificar_score(score: float) -> str:
    """
    Classifica o ambiente econômico a partir do score.
    """

    if score >= SCENARIO_THRESHOLDS["MUITO_OTIMISTA"]:
        return "MUITO_OTIMISTA"

    if score >= SCENARIO_THRESHOLDS["OTIMISTA"]:
        return "OTIMISTA"

    if score >= SCENARIO_THRESHOLDS["NEUTRO_SUPERIOR"]:
        return "NEUTRO_FAVORAVEL"

    if score > SCENARIO_THRESHOLDS["NEUTRO_INFERIOR"]:
        return "NEUTRO"

    if score > SCENARIO_THRESHOLDS["ADVERSO"]:
        return "NEUTRO_DESFAVORAVEL"

    if score > SCENARIO_THRESHOLDS["MUITO_ADVERSO"]:
        return "ADVERSO"

    return "MUITO_ADVERSO"


# ============================================================
# CONFIANÇA
# ============================================================

def calcular_confianca(
    sinais: Dict[str, str]
) -> str:

    indicadores_validos = 0

    for indicador in sinais:

        if indicador.upper().strip() in INDICATOR_WEIGHTS:
            indicadores_validos += 1

    if indicadores_validos >= 5:
        return "ALTA"

    if indicadores_validos >= 3:
        return "MODERADA"

    if indicadores_validos >= 1:
        return "BAIXA"

    return "INSUFICIENTE"


# ============================================================
# ANÁLISE COMPLETA
# ============================================================

def analisar_cenario_economico(
    sinais: Dict[str, str]
) -> Dict:

    resultado_score = calcular_score_economico(
        sinais
    )

    confianca = calcular_confianca(
        sinais
    )

    return {

        "score_total":
            resultado_score["score_total"],

        "score_normalizado":
            resultado_score["score_normalizado"],

        "classificacao":
            resultado_score["classificacao"],

        "confianca":
            confianca,

        "indicadores":
            resultado_score["indicadores"],
    }


# ============================================================
# EXIBIÇÃO DO RESULTADO
# ============================================================

def exibir_resultado(
    resultado: Dict
):

    print("=" * 60)
    print("KOAIALA ECONOMIC SCORE")
    print("=" * 60)

    print(
        f"Score total: "
        f"{resultado['score_total']:.4f}"
    )

    print(
        f"Score normalizado: "
        f"{resultado['score_normalizado']:.4f}"
    )

    print(
        f"Classificação: "
        f"{resultado['classificacao']}"
    )

    print(
        f"Confiança: "
        f"{resultado['confianca']}"
    )

    print("-" * 60)
    print("INDICADORES")
    print("-" * 60)

    for indicador in resultado["indicadores"]:

        impacto = indicador["score_ponderado"]

        print(
            f"{indicador['indicador']}: "
            f"{indicador['sinal']} | "
            f"Impacto econômico: "
            f"{indicador['score']:+d} | "
            f"Peso: "
            f"{indicador['peso']:.0%} | "
            f"Contribuição: "
            f"{impacto:+.4f}"
        )

    print("=" * 60)


# ============================================================
# TESTE
# ============================================================

def main():

    # --------------------------------------------------------
    # CENÁRIO DE TESTE
    #
    # SELIC       -> estabilidade
    # IPCA        -> queda
    # PIB         -> alta
    # Desemprego  -> queda
    # Câmbio      -> estabilidade
    # --------------------------------------------------------

    sinais_teste = {

        "SELIC_META":
            "ESTABILIDADE",

        "IPCA":
            "QUEDA",

        "PIB":
            "ALTA",

        "DESEMPREGO":
            "QUEDA",

        "CAMBIO":
            "ESTABILIDADE",
    }

    resultado = analisar_cenario_economico(
        sinais_teste
    )

    exibir_resultado(
        resultado
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()