"""
KOAIALA FULL CYCLE

Executa coleta, inteligência econômica, forecast e decision engine.
"""

from src.sense.collector_engine import executar_coleta
from src.core.koaiala_engine import executar_koaiala, exibir_koaiala


def main():
    print("=" * 70)
    print("KOAIALA OS — FULL CYCLE")
    print("=" * 70)

    print("\n[1] COLETA")
    executar_coleta()

    print("\n[2] INTELIGÊNCIA ECONÔMICA")
    resultado = executar_koaiala()
    exibir_koaiala(resultado)

    if resultado.get("status") != "OK":
        raise SystemExit(1)

    print("\nCICLO COMPLETO EXECUTADO ✓")


if __name__ == "__main__":
    main()
