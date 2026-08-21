"""
KOAIALA ALERT OPERATIONS 22.2

Executa o ciclo já existente, avalia eventos e persiste
os alertas. Nenhuma decisão econômica é criada aqui.
"""

from src.core.final_cycle_v18 import executar
from src.alerts.alert_engine import avaliar
from src.alerts.alert_repository import (
    ensure_alert_table,
    save_alerts,
    get_recent_alerts,
)


def executar_alertas():
    cycle = executar()

    if cycle.get("status") != "OK":
        return {
            "status": "ERROR",
            "message": "FULL CYCLE não retornou OK.",
        }

    result = avaliar(cycle)

    if result.get("status") != "OK":
        return {
            "status": "ERROR",
            "message": "Alert Engine não retornou OK.",
        }

    ensure_alert_table()
    alerts = result.get("alertas", [])

    # INFO não representa evento acionável e não precisa
    # poluir o histórico operacional.
    persistable = [
        alert
        for alert in alerts
        if alert.get("severity") != "INFO"
    ]

    if persistable:
        save_alerts(persistable)

    return {
        "status": "OK",
        "total_detectados": len(alerts),
        "total_persistidos": len(persistable),
        "maior_severidade": result.get(
            "maior_severidade",
            "INFO",
        ),
        "alertas": alerts,
    }


def main():
    print("=" * 76)
    print("KOAIALA ALERT OPERATIONS 22.2")
    print("=" * 76)

    result = executar_alertas()

    if result["status"] != "OK":
        raise SystemExit(result["message"])

    print("FULL CYCLE: OK")
    print("ALERT ENGINE: OK")
    print("ALERT STORAGE: OK")
    print(
        f"Alertas detectados: "
        f"{result['total_detectados']}"
    )
    print(
        f"Alertas persistidos: "
        f"{result['total_persistidos']}"
    )
    print(
        f"Maior severidade: "
        f"{result['maior_severidade']}"
    )

    for alert in result["alertas"]:
        print(
            f"[{alert['severity']}] "
            f"{alert['code']} — "
            f"{alert['title']}"
        )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA ALERT OPERATIONS 22.2 APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
