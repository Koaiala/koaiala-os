"""
KOAIALA FORECAST ENGINE

Projeção técnica, transparente e conservadora dos indicadores.
Não é previsão estatística nem recomendação de investimento.
"""

from decimal import Decimal
from statistics import mean
from typing import Dict, List, Optional

from src.database.connection import get_connection

HORIZONTES = {"CURTO": 1, "MEDIO": 3, "LONGO": 6}


def buscar_historico(indicador: str, limite: int = 24) -> List[Dict]:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT observation_date, value
            FROM (
                SELECT observation_date, value
                FROM economic_observations
                WHERE indicator_code = %s
                ORDER BY observation_date DESC
                LIMIT %s
            ) AS ultimos
            ORDER BY observation_date ASC
            """,
            (indicador, limite),
        )
        registros = cursor.fetchall()
        return [
            {"data": row[0], "valor": Decimal(str(row[1]))}
            for row in registros
        ]
    finally:
        connection.close()


def _regressao_linear(valores: List[float]) -> float:
    if len(valores) < 2:
        return 0.0
    x = list(range(len(valores)))
    xm, ym = mean(x), mean(valores)
    den = sum((v - xm) ** 2 for v in x)
    if den == 0:
        return 0.0
    return sum((xi - xm) * (yi - ym) for xi, yi in zip(x, valores)) / den


def _forca(inclinacao: float, escala: float) -> str:
    razao = abs(inclinacao) / max(escala, 0.01)
    if razao >= 1.0:
        return "MUITO_FORTE"
    if razao >= 0.5:
        return "FORTE"
    if razao >= 0.2:
        return "MODERADA"
    if razao > 0.05:
        return "FRACA"
    return "MUITO_FRACA"


def projetar_indicador(indicador: str, horizontes: Optional[Dict[str, int]] = None) -> Dict:
    historico = buscar_historico(indicador)
    if not historico:
        return {"status": "ERRO", "indicador": indicador, "mensagem": "Nenhuma observação disponível."}

    valores = [float(x["valor"]) for x in historico]
    atual = valores[-1]
    janela = min(6, len(valores))
    recentes = valores[-janela:]
    media_recente = mean(recentes)
    inclinacao = _regressao_linear(recentes)
    escala = max(abs(atual), abs(media_recente), 0.01)
    tendencia = "ALTA" if inclinacao > 0 else "QUEDA" if inclinacao < 0 else "ESTABILIDADE"
    forca = _forca(inclinacao, escala)

    if horizontes is None:
        horizontes = HORIZONTES

    projecoes = {}
    volatilidade = 0.0
    if len(recentes) >= 2:
        diffs = [recentes[i] - recentes[i - 1] for i in range(1, len(recentes))]
        volatilidade = (mean([d * d for d in diffs]) ** 0.5)

    for nome, passos in horizontes.items():
        tendencia_valor = atual + inclinacao * passos
        projetado = 0.70 * tendencia_valor + 0.30 * media_recente
        margem = volatilidade * (passos ** 0.5)
        limite_inf = min(valores) if len(valores) < 6 else min(min(valores), projetado - margem)
        limite_sup = max(valores) if len(valores) < 6 else max(max(valores), projetado + margem)
        projecoes[nome] = {
            "passos": passos,
            "valor_projetado": round(projetado, 6),
            "intervalo_tecnico": {
                "inferior": round(limite_inf, 6),
                "superior": round(limite_sup, 6),
            },
        }

    confianca = "ALTA" if len(historico) >= 18 and forca != "MUITO_FRACA" else "MODERADA" if len(historico) >= 6 else "BAIXA"

    return {
        "status": "OK",
        "indicador": indicador,
        "data_atual": historico[-1]["data"],
        "valor_atual": historico[-1]["valor"],
        "observacoes": len(historico),
        "media_recente": round(media_recente, 6),
        "inclinacao": round(inclinacao, 8),
        "tendencia": tendencia,
        "forca_tendencia": forca,
        "volatilidade_recente": round(volatilidade, 6),
        "confianca": confianca,
        "projecoes": projecoes,
        "metodo": "regressao_linear_recente_70_porcento_mais_reversao_media_30_porcento",
    }


def projetar_indicadores(indicadores: Optional[List[str]] = None) -> Dict:
    if indicadores is None:
        from src.sense.registry import get_indicator_codes
        indicadores = get_indicator_codes()
    return {
        indicador: resultado
        for indicador in indicadores
        if (resultado := projetar_indicador(indicador)).get("status") == "OK"
    }


def exibir_previsoes(resultado: Dict) -> None:
    print("=" * 60)
    print("KOAIALA FORECAST ENGINE")
    print("=" * 60)
    for indicador, dados in resultado.items():
        print(f"\n{indicador} | Atual: {dados['valor_atual']} | Tendência: {dados['tendencia']} | Confiança: {dados['confianca']}")
        for horizonte, previsao in dados["projecoes"].items():
            print(f"  {horizonte}: {previsao['valor_projetado']:.4f} | faixa técnica {previsao['intervalo_tecnico']['inferior']:.4f}–{previsao['intervalo_tecnico']['superior']:.4f}")
    print("=" * 60)


def main():
    exibir_previsoes(projetar_indicadores())


if __name__ == "__main__":
    main()
