"""KOAIALA SYSTEM CHECK - valida o núcleo completo."""

from src.sense.registry import get_active_indicators
from src.database.connection import get_connection
from src.core.koaiala_engine import executar_koaiala


def main():
    print("=" * 60)
    print("KOAIALA SYSTEM CHECK")
    print("=" * 60)

    connection = get_connection()
    connection.close()

    indicadores = get_active_indicators()
    print("Indicadores registrados:", ", ".join(indicadores.keys()))

    resultado = executar_koaiala()
    if resultado.get("status") != "OK":
        print("STATUS FINAL: KOAIALA CORE REPROVADO")
        raise SystemExit(1)

    if not resultado.get("previsoes"):
        print("STATUS FINAL: KOAIALA CORE REPROVADO")
        raise SystemExit(1)

    if resultado.get("riscos", {}).get("status") != "OK":
        print("STATUS FINAL: KOAIALA CORE REPROVADO")
        raise SystemExit(1)

    print("Forecast: OK")
    print("Risk Engine: OK")
    print("Master Engine: OK")
    print("STATUS FINAL: KOAIALA CORE APROVADO ✓")


if __name__ == "__main__":
    main()
