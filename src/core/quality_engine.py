"""
KOAIALA QUALITY ENGINE

Valida a coerência estrutural do núcleo antes de considerar
um ciclo econômico confiável.
"""

from typing import Dict, List


def validar_cenario(cenario: Dict) -> List[str]:
    erros = []
    if cenario.get("status") != "OK":
        return ["Cenário não está OK."]

    cenarios = cenario.get("cenarios", {})
    participacoes = [
        cenarios.get(nome, {}).get("participacao")
        for nome in ("otimista", "base", "adverso")
    ]
    if any(valor is None for valor in participacoes):
        erros.append("Distribuição de cenários incompleta.")
    elif abs(sum(participacoes) - 1.0) > 0.0001:
        erros.append("Probabilidades indicativas não somam 100%.")

    cobertura = cenario.get("confianca", {}).get("cobertura", 0)
    if not 0 <= cobertura <= 1:
        erros.append("Cobertura fora do intervalo 0-100%.")

    return erros


def validar_previsoes(previsoes: Dict) -> List[str]:
    erros = []
    for indicador, dados in previsoes.items():
        if dados.get("status") != "OK":
            erros.append(f"Forecast inválido: {indicador}.")
            continue
        if not dados.get("projecoes"):
            erros.append(f"Sem projeções: {indicador}.")
    return erros


def validar_decisao(decisao: Dict) -> List[str]:
    erros = []
    if decisao.get("status") != "OK":
        return ["Decision Engine não está OK."]
    if not decisao.get("classes"):
        erros.append("Mapa de classes vazio.")
    return erros


def validar_sistema(resultado: Dict) -> Dict:
    erros = []
    avisos = []

    cenario = resultado.get("cenario", {})
    previsoes = resultado.get("previsoes", {})
    decisao = resultado.get("decisao", {})

    erros.extend(validar_cenario(cenario))
    erros.extend(validar_previsoes(previsoes))
    erros.extend(validar_decisao(decisao))

    cobertura = cenario.get("confianca", {}).get("cobertura", 0)
    if cobertura < 1:
        avisos.append("O universo macro ainda não possui cobertura total.")

    if len(previsoes) < cenario.get("total_indicadores", 0):
        avisos.append("Nem todos os indicadores possuem forecast válido.")

    return {
        "status": "OK" if not erros else "ERRO",
        "erros": erros,
        "avisos": avisos,
        "aprovado": not erros,
    }
