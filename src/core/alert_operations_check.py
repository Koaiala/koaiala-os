"""
KOAIALA ALERT OPERATIONS CHECK 22.2
"""

from src.core.alert_operations import executar_alertas
from src.alerts.alert_repository import get_recent_alerts


def main():
    print("=" * 76)
    print("KOAIALA ALERT OPERATIONS CHECK 22.2")
    print("=" * 76)

    result = executar_alertas()

    if result.get("status") != "OK":
        raise SystemExit(
            result.get("message", "Falha operacional.")
        )

    recent = get_recent_alerts(5)

    print("FULL CYCLE: OK")
    print("ALERT ENGINE: OK")
    print("ALERT STORAGE: OK")
    print(
        f"DETECTADOS: "
        f"{result['total_detectados']}"
    )
    print(
        f"PERSISTIDOS: "
        f"{result['total_persistidos']}"
    )
    print(
        f"REGISTROS RECENTES: "
        f"{len(recent)}"
    )

    if result["total_detectados"] == 0:
        raise SystemExit(
            "ALERT ENGINE: nenhum resultado retornado."
        )

    print("OPERATIONAL ALERTS: OK")
    print()
    print(
        "STATUS FINAL: "
        "KOAIALA ALERT OPERATIONS 22.2 APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
