"""KOAIALA OS - Integration Check."""
import importlib

MODULES = [
    "src.database.connection",
    "src.sense.registry",
    "src.sense.sgs_collector",
    "src.sense.bcb_collector",
    "src.validator.observation_validator",
    "src.insight.analysis_engine",
    "src.insight.economic_interpreter",
    "src.insight.economic_score",
    "src.insight.scenario_engine",
    "src.forecast.forecast_engine",
    "src.risk.risk_engine",
    "src.decision.decision_engine",
    "src.core.koaiala_engine",
    "src.api.http_server",
    "src.web.dashboard_server",
]


def main():
    print("=" * 60)
    print("KOAIALA INTEGRATION CHECK")
    print("=" * 60)
    for name in MODULES:
        importlib.import_module(name)
        print(f"[OK] {name}")
    print("=" * 60)
    print("STATUS FINAL: KOAIALA INTEGRAÇÃO APROVADA ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("STATUS FINAL: KOAIALA INTEGRAÇÃO REPROVADA ✗")
        print(f"ERRO: {exc}")
        raise SystemExit(1)
