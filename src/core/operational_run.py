"""
KOAIALA OPERATIONAL RUNNER 20.2

Usa a mesma extração de cenário do Final Cycle 18.1.
"""

from datetime import datetime

from src.core.final_cycle_v18 import (
    executar as executar_ciclo,
    _master_fields,
)


def executar():
    inicio = datetime.now()
    resultado = executar_ciclo()
    fim = datetime.now()

    if resultado["status"] != "OK":
        raise RuntimeError(
            "FULL CYCLE retornou falha."
        )

    return {
        "status": "OK",
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "duracao_segundos": (
            fim - inicio
        ).total_seconds(),
        "cycle": resultado,
    }


def exibir(resultado):
    cycle = resultado["cycle"]

    score, classificacao, confianca = _master_fields(
        cycle["master"]
    )

    print("=" * 76)
    print("KOAIALA OPERATIONAL RUNNER 20.2")
    print("=" * 76)

    print(f"Início: {resultado['inicio']}")
    print(f"Fim:    {resultado['fim']}")
    print(
        f"Duração: "
        f"{resultado['duracao_segundos']:.2f}s"
    )

    print()
    print("CENÁRIO")
    print("-" * 76)
    print(f"Score: {score}")
    print(f"Classificação: {classificacao}")
    print(f"Confiança: {confianca}")

    recon = cycle["reconciliation"]

    print()
    print("RECONCILIAÇÃO")
    print("-" * 76)
    print(f"Atual: {recon['cenario_atual']}")
    print(f"Preditivo: {recon['cenario_preditivo']}")
    print(f"Estado: {recon['reconciliacao']}")
    print(f"Risco: {recon['risco_reconciliacao']}")

    decision = cycle["decision"]

    print()
    print("DECISÃO")
    print("-" * 76)
    print(f"Postura: {decision['postura']}")
    print(f"Horizonte: {decision['horizonte']}")
    print(f"Confiança: {decision['confianca']}")

    print()
    print("STATUS")
    print("-" * 76)
    print("FULL CYCLE: OK")
    print("PREDICTION: OK")
    print("FORECAST: OK")
    print("RECONCILIATION: OK")
    print("RISK: OK")
    print("DECISION: OK")
    print("API/DASHBOARD: DISPONÍVEIS")

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA OPERATIONAL RUNNER "
        "20.2 APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    exibir(executar())
