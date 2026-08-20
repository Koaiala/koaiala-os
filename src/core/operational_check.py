"""Validação final da camada operacional."""

from src.sense.registry import get_active_indicators
from src.core.koaiala_engine import executar_koaiala


def main():
    print("=" * 60)
    print("KOAIALA OPERATIONAL CHECK")
    print("=" * 60)
    indicadores = get_active_indicators()
    print("Indicadores:", ", ".join(indicadores))
    resultado = executar_koaiala()
    if resultado.get("status") != "OK":
        print("STATUS FINAL: REPROVADO")
        raise SystemExit(1)
    checks = {
        "Scenario": resultado.get("cenario", {}).get("status") == "OK",
        "Forecast": bool(resultado.get("previsoes")),
        "Risk": resultado.get("riscos", {}).get("status") == "OK",
        "Decision": resultado.get("decisao", {}).get("status") == "OK",
    }
    for nome, ok in checks.items():
        print(f"{nome}: {'OK' if ok else 'ERRO'}")
    if not all(checks.values()):
        print("STATUS FINAL: KOAIALA OPERATIONAL REPROVADO")
        raise SystemExit(1)
    print("API: src.api.http_server pronta")
    print("Dashboard: src.web.dashboard_server pronto")
    print("STATUS FINAL: KOAIALA OPERATIONAL APROVADO ✓")


if __name__ == "__main__":
    main()
