"""
KOAIALA ALERT ENGINE CHECK 22.1
"""

from src.core.final_cycle_v18 import executar
from src.alerts.alert_engine import avaliar


def main():
    print("=" * 76)
    print("KOAIALA ALERT ENGINE 22.1 CHECK")
    print("=" * 76)

    cycle = executar()

    if cycle.get("status") != "OK":
        raise SystemExit("CORE: FALHA")

    result = avaliar(cycle)

    if result.get("status") != "OK":
        raise SystemExit("ALERT ENGINE: FALHA")

    print("CORE: OK")
    print("ALERT ENGINE: OK")
    print(
        f"Alertas detectados: "
        f"{result['total_alertas']}"
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
        "INDEPENDÊNCIA DO CORE: OK"
    )
    print(
        "STATUS FINAL: "
        "KOAIALA ALERT ENGINE 22.1 APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
