"""
KOAIALA OPERATIONAL ALERT INTEGRATION CHECK 22.3
"""

from src.core.operational_alert_cycle import executar


def main():
    print("=" * 76)
    print("KOAIALA OPERATIONAL ALERT INTEGRATION CHECK 22.3")
    print("=" * 76)

    result = executar()

    if result.get("status") != "OK":
        raise SystemExit(
            "INTEGRAÇÃO OPERACIONAL: FALHA"
        )

    alerts = result["alerts"]

    print("OPERATIONAL RUNNER: OK")
    print("ALERT ENGINE: OK")
    print("ALERT STORAGE: OK")
    print(
        f"DETECTADOS: {alerts['total_detectados']}"
    )
    print(
        f"PERSISTIDOS: {alerts['total_persistidos']}"
    )
    print(
        f"SEVERIDADE: {alerts['maior_severidade']}"
    )
    print("INTEGRAÇÃO: OK")
    print()
    print(
        "STATUS FINAL: "
        "KOAIALA OPERATIONAL ALERT "
        "INTEGRATION 22.3 APROVADA ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
