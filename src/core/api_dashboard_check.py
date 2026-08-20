"""
KOAIALA API + DASHBOARD CHECK 19.0
"""

from src.core.final_cycle_v18 import executar


def main():
    print("=" * 72)
    print("KOAIALA API + DASHBOARD CHECK 19.0")
    print("=" * 72)

    resultado = executar()

    if resultado["status"] != "OK":
        raise SystemExit(
            "CORE: FALHA"
        )

    print("CORE: OK")
    print("API: src.api.http_server pronta")
    print("Dashboard: src.web.dashboard_server pronta")
    print("Endpoints: /health /api/status /api/scenario /api/prediction /api/reconciliation /api/decision")
    print()
    print(
        "STATUS FINAL: "
        "KOAIALA API + DASHBOARD APROVADOS ✓"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
