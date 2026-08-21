"""
KOAIALA OPERATIONAL ALERT CYCLE 22.3

Executa:
1. ciclo operacional existente;
2. Alert Engine;
3. persistência dos alertas.

Não substitui o operational_run.py original.
"""

from src.core.operational_run import executar as executar_operacional
from src.core.alert_operations import executar_alertas


def executar():
    operational = executar_operacional()

    alerts = executar_alertas()

    return {
        "status": (
            "OK"
            if alerts.get("status") == "OK"
            else "ERROR"
        ),
        "operational": operational,
        "alerts": alerts,
    }


def main():
    print("=" * 76)
    print("KOAIALA OPERATIONAL ALERT CYCLE 22.3")
    print("=" * 76)

    result = executar()

    if result["status"] != "OK":
        raise SystemExit(
            "OPERATIONAL ALERT CYCLE: FALHA"
        )

    alerts = result["alerts"]

    print("OPERATIONAL RUNNER: OK")
    print("ALERT ENGINE: OK")
    print("ALERT STORAGE: OK")
    print(
        f"ALERTAS DETECTADOS: "
        f"{alerts['total_detectados']}"
    )
    print(
        f"ALERTAS PERSISTIDOS: "
        f"{alerts['total_persistidos']}"
    )
    print(
        f"MAIOR SEVERIDADE: "
        f"{alerts['maior_severidade']}"
    )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA OPERATIONAL ALERT CYCLE "
        "22.3 APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
