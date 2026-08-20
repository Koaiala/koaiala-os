"""
KOAIALA - ECONOMIC SCORE ENGINE

Agrega os sinais econômicos dos indicadores disponíveis.

O score normalizado varia de -2 a +2:
    +2 = forte impacto favorável
    +1 = impacto favorável
     0 = neutro
    -1 = impacto desfavorável
    -2 = forte impacto desfavorável

O peso utilizado é renormalizado quando nem todos os indicadores
estão disponíveis.
"""

from typing import Dict, List


# Pesos relativos do conjunto macro.
# A soma é 1.00, mas o motor renormaliza apenas os indicadores
# efetivamente disponíveis.
INDICATOR_WEIGHTS = {
    "SELIC_META": 0.20,
    "IPCA": 0.20,
    "INPC": 0.10,
    "IGP_M": 0.10,
    "PIB": 0.15,
    "DESEMPREGO": 0.10,
    "CAMBIO": 0.15,
}


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
    "INPC": {
        "FORTE_ALTA": -2,
        "ALTA": -1,
        "ESTABILIDADE": 0,
        "NEUTRO": 0,
        "QUEDA": 1,
        "FORTE_QUEDA": 2,
    },
    "IGP_M": {
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


SCENARIO_THRESHOLDS = {
    "MUITO_OTIMISTA": 1.25,
    "OTIMISTA": 0.50,
    "NEUTRO_SUPERIOR": 0.15,
    "NEUTRO_INFERIOR": -0.15,
    "ADVERSO": -0.50,
    "MUITO_ADVERSO": -1.25,
}


def normalizar_sinal(sinal: str) -> str:
    if not isinstance(sinal, str):
        return "NEUTRO"

    valor = sinal.upper().strip()

    aliases = {
        "ALTA FORTE": "FORTE_ALTA",
        "FORTE ALTA": "FORTE_ALTA",
        "FORTE_ALTA": "FORTE_ALTA",
        "ALTA": "ALTA",

        "QUEDA FORTE": "FORTE_QUEDA",
        "FORTE QUEDA": "FORTE_QUEDA",
        "FORTE_QUEDA": "FORTE_QUEDA",
        "QUEDA": "QUEDA",

        "REDUÇÃO": "QUEDA",
        "REDUCAO": "QUEDA",
        "REDUÇÃO FORTE": "FORTE_QUEDA",
        "REDUCAO FORTE": "FORTE_QUEDA",

        "ELEVAÇÃO": "ALTA",
        "ELEVACAO": "ALTA",
        "ELEVAÇÃO FORTE": "FORTE_ALTA",
        "ELEVACAO FORTE": "FORTE_ALTA",

        "ESTÁVEL": "ESTABILIDADE",
        "ESTAVEL": "ESTABILIDADE",
        "ESTABILIDADE": "ESTABILIDADE",
        "NEUTRO": "NEUTRO",
    }

    return aliases.get(valor, "NEUTRO")


def calcular_score_indicador(indicador: str, sinal: str) -> Dict:
    codigo = indicador.upper().strip()
    sinal_normalizado = normalizar_sinal(sinal)

    peso = INDICATOR_WEIGHTS.get(codigo, 0.0)
    direcoes = ECONOMIC_DIRECTION.get(codigo, {})
    score = direcoes.get(sinal_normalizado, 0)

    return {
        "indicador": codigo,
        "sinal": sinal_normalizado,
        "score": score,
        "peso": peso,
        "score_ponderado": score * peso,
    }


def classificar_score(score: float) -> str:
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


def calcular_confianca(sinais: Dict[str, str]) -> str:
    validos = sum(
        1 for indicador in sinais
        if indicador.upper().strip() in INDICATOR_WEIGHTS
    )

    if validos >= 6:
        return "ALTA"
    if validos >= 4:
        return "MODERADA"
    if validos >= 2:
        return "BAIXA"
    if validos == 1:
        return "MUITO_BAIXA"
    return "INSUFICIENTE"


def calcular_score_economico(sinais: Dict[str, str]) -> Dict:
    resultados: List[Dict] = []
    score_total = 0.0
    peso_utilizado = 0.0

    for indicador, sinal in sinais.items():
        resultado = calcular_score_indicador(indicador, sinal)

        if resultado["peso"] <= 0:
            continue

        resultados.append(resultado)
        score_total += resultado["score_ponderado"]
        peso_utilizado += resultado["peso"]

    if peso_utilizado > 0:
        score_normalizado = score_total / peso_utilizado
    else:
        score_normalizado = 0.0

    return {
        "score_total": round(score_total, 4),
        "score_normalizado": round(score_normalizado, 4),
        "peso_utilizado": round(peso_utilizado, 4),
        "cobertura": round(peso_utilizado, 4),
        "classificacao": classificar_score(score_normalizado),
        "confianca": calcular_confianca(sinais),
        "indicadores": resultados,
    }


def analisar_cenario_economico(sinais: Dict[str, str]) -> Dict:
    """
    Interface principal mantida compatível com o pipeline existente.
    """
    return calcular_score_economico(sinais)


def classificar_score_publico(score: float) -> str:
    """Alias explícito para consumidores externos."""
    return classificar_score(score)


def exibir_resultado(resultado: Dict) -> None:
    print("=" * 60)
    print("KOAIALA ECONOMIC SCORE")
    print("=" * 60)
    print(f"Score total: {resultado['score_total']:.4f}")
    print(f"Score normalizado: {resultado['score_normalizado']:.4f}")
    print(f"Classificação: {resultado['classificacao']}")
    print(f"Confiança: {resultado['confianca']}")
    print(f"Cobertura: {resultado['cobertura']:.0%}")
    print("-" * 60)

    for item in resultado["indicadores"]:
        print(
            f"{item['indicador']}: "
            f"{item['sinal']} | "
            f"impacto {item['score']:+d} | "
            f"peso {item['peso']:.0%} | "
            f"contribuição {item['score_ponderado']:+.4f}"
        )

    print("=" * 60)


def main():
    sinais = {
        "SELIC_META": "ESTABILIDADE",
        "IPCA": "QUEDA",
        "INPC": "QUEDA",
        "IGP_M": "QUEDA",
    }

    exibir_resultado(
        analisar_cenario_economico(sinais)
    )


if __name__ == "__main__":
    main()
