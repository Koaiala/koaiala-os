"""
KOAIALA SCENARIO ENGINE

Transforma as interpretações individuais dos indicadores em
um diagnóstico macroeconômico integrado.

O motor não produz probabilidades estatísticas. Os percentuais
de cenário são apenas uma distribuição indicativa para organizar
a tomada de decisão e devem ser tratados como hipóteses.
"""

from typing import Dict, List
from decimal import Decimal

from src.insight.analysis_engine import analisar_indicador
from src.insight.economic_interpreter import interpretar
from src.insight.economic_score import (
    calcular_score_economico,
    normalizar_sinal,
)


FALLBACK_INDICATORS = [
    "SELIC_META",
    "IPCA",
    "INPC",
    "IGP_M",
    "PIB",
    "DESEMPREGO",
    "CAMBIO",
]


def _get_indicator_codes() -> List[str]:
    try:
        from src.sense.registry import get_active_indicators

        indicadores = get_active_indicators()
        if indicadores:
            return list(indicadores.keys())
    except Exception:
        pass

    return FALLBACK_INDICATORS.copy()


def analisar_indicadores() -> Dict[str, Dict]:
    resultados = {}

    for codigo in _get_indicator_codes():
        try:
            analise = analisar_indicador(codigo)

            if analise.get("status") != "OK":
                resultados[codigo] = {
                    "status": "ERRO",
                    "mensagem": analise.get(
                        "mensagem",
                        "Erro ao analisar indicador."
                    ),
                }
                continue

            interpretacao = interpretar(analise)

            resultados[codigo] = {
                "status": "OK",
                "analise": analise,
                "interpretacao": interpretacao,
            }

        except Exception as error:
            resultados[codigo] = {
                "status": "ERRO",
                "mensagem": str(error),
            }

    return resultados


def _sinal_da_interpretacao(indicador: str, interpretacao: Dict) -> str:
    """
    Converte REDUÇÃO/ELEVAÇÃO + intensidade em sinal padronizado.
    """
    direcao = str(
        interpretacao.get("direcao", "ESTABILIDADE")
    ).upper()

    intensidade = str(
        interpretacao.get("intensidade", "")
    ).upper()

    forte = any(
        palavra in intensidade
        for palavra in ("FORTE", "MUITO FORTE")
    )

    if direcao in ("REDUÇÃO", "REDUCAO"):
        return "FORTE_QUEDA" if forte else "QUEDA"

    if direcao in ("ELEVAÇÃO", "ELEVACAO"):
        return "FORTE_ALTA" if forte else "ALTA"

    return "ESTABILIDADE"


def extrair_sinais(resultados: Dict[str, Dict]) -> Dict[str, str]:
    sinais = {}

    for codigo, resultado in resultados.items():
        if resultado.get("status") != "OK":
            continue

        interpretacao = resultado.get("interpretacao", {})
        sinais[codigo] = _sinal_da_interpretacao(
            codigo,
            interpretacao,
        )

    return sinais


def calcular_confianca_detalhada(
    resultados: Dict[str, Dict],
) -> Dict:
    pesos = {
        "ALTA": 1.0,
        "MODERADA": 0.6,
        "BAIXA": 0.3,
        "MUITO_BAIXA": 0.15,
        "INSUFICIENTE": 0.0,
    }

    valores = []

    for resultado in resultados.values():
        if resultado.get("status") != "OK":
            continue

        nivel = resultado["interpretacao"].get(
            "confianca",
            "BAIXA",
        )

        valores.append(
            pesos.get(nivel, 0.3)
        )

    if not valores:
        return {
            "nivel": "INSUFICIENTE",
            "score": 0.0,
            "indicadores_validos": 0,
        }

    score = sum(valores) / len(valores)

    # Cobertura também pesa na confiança.
    cobertura = len(valores) / len(
        _get_indicator_codes()
    )

    score_final = score * (0.5 + 0.5 * cobertura)

    if score_final >= 0.80:
        nivel = "ALTA"
    elif score_final >= 0.50:
        nivel = "MODERADA"
    elif score_final >= 0.25:
        nivel = "BAIXA"
    else:
        nivel = "MUITO_BAIXA"

    return {
        "nivel": nivel,
        "score": round(score_final, 4),
        "indicadores_validos": len(valores),
        "cobertura": round(cobertura, 4),
    }


def gerar_cenarios(
    score: float,
    confianca: Dict,
) -> Dict:
    """
    Distribuição indicativa, não estatística.
    """
    score = float(score)
    nivel = confianca.get("nivel", "BAIXA")

    if score >= 0.75:
        base = {"otimista": 0.55, "base": 0.30, "adverso": 0.15}
    elif score >= 0.25:
        base = {"otimista": 0.40, "base": 0.45, "adverso": 0.15}
    elif score > -0.25:
        base = {"otimista": 0.25, "base": 0.50, "adverso": 0.25}
    elif score > -0.75:
        base = {"otimista": 0.15, "base": 0.45, "adverso": 0.40}
    else:
        base = {"otimista": 0.15, "base": 0.30, "adverso": 0.55}

    if nivel in ("BAIXA", "MUITO_BAIXA", "INSUFICIENTE"):
        # Em baixa confiança, aproximamos as hipóteses da neutralidade.
        base["base"] += 0.10
        if base["otimista"] > base["adverso"]:
            base["otimista"] -= 0.05
            base["adverso"] -= 0.05
        else:
            base["otimista"] -= 0.05
            base["adverso"] -= 0.05

    total = sum(base.values())

    for chave in base:
        base[chave] = round(base[chave] / total, 4)

    return {
        "metodo": "distribuicao_indicativa_nao_estatistica",
        "otimista": {
            "participacao": base["otimista"],
            "descricao": (
                "Melhora das condições econômicas, "
                "com convergência favorável dos indicadores."
            ),
        },
        "base": {
            "participacao": base["base"],
            "descricao": (
                "Continuidade do comportamento atual, "
                "sem ruptura estrutural relevante."
            ),
        },
        "adverso": {
            "participacao": base["adverso"],
            "descricao": (
                "Piora das condições econômicas ou "
                "reversão dos sinais favoráveis."
            ),
        },
    }


def classificar_cenario(score: float) -> str:
    if score >= 1.25:
        return "MUITO_OTIMISTA"
    if score >= 0.50:
        return "OTIMISTA"
    if score >= 0.15:
        return "NEUTRO_FAVORAVEL"
    if score > -0.15:
        return "NEUTRO"
    if score > -0.50:
        return "NEUTRO_DESFAVORAVEL"
    if score > -1.25:
        return "ADVERSO"
    return "MUITO_ADVERSO"


def gerar_interpretacao(
    classificacao: str,
    score: float,
    sinais: Dict[str, str],
) -> str:
    favoraveis = sum(
        1 for sinal in sinais.values()
        if normalizar_sinal(sinal) in (
            "QUEDA",
            "FORTE_QUEDA",
            "FORTE_ALTA",
        )
    )

    total = len(sinais)

    if classificacao in ("MUITO_OTIMISTA", "OTIMISTA"):
        abertura = (
            "O conjunto de sinais disponíveis apresenta "
            "predominância favorável."
        )
    elif classificacao in ("ADVERSO", "MUITO_ADVERSO"):
        abertura = (
            "O conjunto de sinais disponíveis apresenta "
            "predominância desfavorável."
        )
    else:
        abertura = (
            "O conjunto de sinais disponíveis ainda não "
            "apresenta predominância suficientemente forte."
        )

    return (
        f"{abertura} Score normalizado: {score:.2f}. "
        f"Foram identificados {favoraveis} sinais favoráveis "
        f"entre {total} sinais válidos."
    )


def construir_cenario() -> Dict:
    resultados = analisar_indicadores()
    sinais = extrair_sinais(resultados)

    if not sinais:
        return {
            "status": "ERRO",
            "mensagem": "Nenhum indicador válido disponível.",
        }

    score = calcular_score_economico(sinais)
    confianca = calcular_confianca_detalhada(resultados)

    classificacao = classificar_cenario(
        score["score_normalizado"]
    )

    cenarios = gerar_cenarios(
        score["score_normalizado"],
        confianca,
    )

    interpretacao = gerar_interpretacao(
        classificacao,
        score["score_normalizado"],
        sinais,
    )

    return {
        "status": "OK",
        "score": score["score_normalizado"],
        "score_detalhado": score,
        "classificacao": classificacao,
        "confianca": confianca,
        "indicadores_analisados": list(sinais.keys()),
        "total_indicadores": len(sinais),
        "cenarios": cenarios,
        "interpretacao": interpretacao,
        "sinais": sinais,
        "indicadores": resultados,
    }


def exibir_cenario(resultado: Dict) -> None:
    print("=" * 60)
    print("KOAIALA SCENARIO ENGINE")
    print("=" * 60)

    if resultado.get("status") != "OK":
        print("STATUS:", resultado.get("status"))
        print("MENSAGEM:", resultado.get("mensagem"))
        print("=" * 60)
        return

    print(
        "Indicadores:",
        ", ".join(resultado["indicadores_analisados"]),
    )
    print(
        f"Score: {resultado['score']:.4f}"
    )
    print(
        f"Classificação: {resultado['classificacao']}"
    )
    print(
        f"Confiança: {resultado['confianca']['nivel']}"
    )
    print(
        f"Cobertura: "
        f"{resultado['confianca']['cobertura']:.0%}"
    )
    print("-" * 60)
    print("LEITURA:")
    print(resultado["interpretacao"])
    print("-" * 60)

    for nome in ("otimista", "base", "adverso"):
        cenario = resultado["cenarios"][nome]
        print(
            f"{nome.upper()}: "
            f"{cenario['participacao']:.0%} | "
            f"{cenario['descricao']}"
        )

    print("=" * 60)


def main():
    exibir_cenario(
        construir_cenario()
    )


if __name__ == "__main__":
    main()
