"""KOAIALA OS - Hardening Check.

Valida contratos, entradas e respostas dos motores sem alterar o banco.
"""
from typing import Dict

from src.sense.registry import get_active_indicators, get_indicator
from src.insight.analysis_engine import analisar_indicador
from src.insight.scenario_engine import construir_cenario
from src.forecast.forecast_engine import projetar_indicadores
from src.risk.risk_engine import avaliar_riscos
from src.decision.decision_engine import construir_decisao
from src.core.koaiala_engine import executar_koaiala


def _ok(name: str):
    print(f"[OK] {name}")


def main():
    print("=" * 60)
    print("KOAIALA HARDENING CHECK")
    print("=" * 60)

    indicadores = get_active_indicators()
    assert indicadores, "Registry sem indicadores ativos"
    required = {"SELIC_META", "IPCA", "IGP_M", "INPC"}
    assert required.issubset(indicadores), "Indicadores essenciais ausentes"
    _ok("Registry")

    for codigo in required:
        cfg = get_indicator(codigo)
        assert cfg["source_code"], f"{codigo}: série ausente"
        assert cfg["active"] is True, f"{codigo}: indicador inativo"
    _ok("Metadados dos indicadores")

    for codigo in required:
        resultado = analisar_indicador(codigo)
        assert resultado.get("status") == "OK", f"Analysis falhou: {codigo}"
        assert resultado.get("total_observacoes", 0) >= 2, f"Dados insuficientes: {codigo}"
    _ok("Analysis Engine")

    cenario = construir_cenario()
    assert cenario.get("status") == "OK", "Scenario Engine falhou"
    assert cenario.get("total_indicadores", 0) > 0, "Cenário sem indicadores"
    assert 0 <= cenario.get("confianca", {}).get("cobertura", 0) <= 1
    _ok("Scenario Engine")

    previsoes = projetar_indicadores()
    assert isinstance(previsoes, dict) and previsoes, "Forecast sem resultados"
    for codigo, dados in previsoes.items():
        assert dados.get("status") == "OK", f"Forecast inválido: {codigo}"
        assert dados.get("projecoes"), f"Forecast sem projeções: {codigo}"
    _ok("Forecast Engine")

    riscos = avaliar_riscos(cenario, previsoes)
    assert riscos.get("status") == "OK", "Risk Engine falhou"
    assert riscos.get("nivel_geral") in {"BAIXO", "MODERADO", "ALTO"}
    _ok("Risk Engine")

    decisao = construir_decisao(cenario, previsoes)
    assert decisao.get("status") == "OK", "Decision Engine falhou"
    assert decisao.get("classes"), "Decision Engine sem classes"
    _ok("Decision Engine")

    ciclo = executar_koaiala()
    assert ciclo.get("status") == "OK", "Master Engine falhou"
    for etapa in ("cenario", "previsoes", "riscos", "decisao"):
        assert etapa in ciclo, f"Master sem etapa: {etapa}"
    _ok("Master Engine")

    print("=" * 60)
    print("STATUS FINAL: KOAIALA HARDENING APROVADO ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("=" * 60)
        print("STATUS FINAL: KOAIALA HARDENING REPROVADO ✗")
        print(f"ERRO: {exc}")
        print("=" * 60)
        raise SystemExit(1)
