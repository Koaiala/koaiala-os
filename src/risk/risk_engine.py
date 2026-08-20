"""
KOAIALA RISK ENGINE

Consolida sinais de inflação, juros, atividade e cobertura para
produzir um mapa de riscos macroeconômicos.
"""

from typing import Dict, List


def avaliar_riscos(cenario: Dict, previsoes: Dict) -> Dict:
    riscos: List[Dict] = []
    sinais = cenario.get("sinais", {})
    confianca = cenario.get("confianca", {}).get("nivel", "BAIXA")

    if confianca in ("BAIXA", "MUITO_BAIXA", "INSUFICIENTE"):
        riscos.append({"codigo": "BAIXA_CONFIANCA", "nivel": "ALTO", "descricao": "Cobertura ou persistência insuficiente para sustentar uma leitura estrutural."})

    ipca = sinais.get("IPCA")
    selic = sinais.get("SELIC_META")
    igpm = sinais.get("IGP_M")

    if ipca in ("ALTA", "FORTE_ALTA"):
        riscos.append({"codigo": "PRESSAO_INFLACIONARIA", "nivel": "ALTO", "descricao": "IPCA apresenta sinal de alta."})

    if igpm in ("ALTA", "FORTE_ALTA"):
        riscos.append({"codigo": "PRESSAO_DE_CUSTOS", "nivel": "MODERADO", "descricao": "IGP-M apresenta sinal de alta."})

    if selic in ("FORTE_ALTA", "ALTA"):
        riscos.append({"codigo": "APERTO_MONETARIO", "nivel": "MODERADO", "descricao": "Juros apresentam sinal de alta."})

    sinais_contraditorios = 0
    if ipca in ("QUEDA", "FORTE_QUEDA") and igpm in ("ALTA", "FORTE_ALTA"):
        sinais_contraditorios += 1
    if selic in ("QUEDA", "FORTE_QUEDA") and ipca in ("ALTA", "FORTE_ALTA"):
        sinais_contraditorios += 1

    if sinais_contraditorios:
        riscos.append({"codigo": "DIVERGENCIA_MACRO", "nivel": "MODERADO", "descricao": "Há sinais econômicos apontando em direções diferentes."})

    if not riscos:
        riscos.append({"codigo": "RISCO_BASE", "nivel": "BAIXO", "descricao": "Nenhum risco macro dominante foi detectado no conjunto disponível."})

    niveis = {"BAIXO": 1, "MODERADO": 2, "ALTO": 3}
    nivel_max = max((item["nivel"] for item in riscos), key=lambda x: niveis[x])

    return {
        "status": "OK",
        "nivel_geral": nivel_max,
        "riscos": riscos,
        "quantidade": len(riscos),
        "aviso": "Mapa de risco macroeconômico; não constitui recomendação individual de investimento.",
    }
