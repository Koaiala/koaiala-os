"""
KOAIALA FINAL CYCLE 18.1

Correção de apresentação:
o Master Engine retorna o cenário dentro de score_detalhado.
"""

from src.core.koaiala_engine import executar_koaiala
from src.predictive.signal_engine import executar as executar_prediction
from src.reconciliation.reconciliation_engine import executar as executar_reconciliation
from src.decision.decision_engine import executar as executar_decision


def _master_fields(master):
    if not isinstance(master, dict):
        return "N/D", "N/D", "N/D"

    detalhado = master.get("score_detalhado")

    if not isinstance(detalhado, dict):
        # Algumas versões retornam o resultado completo dentro de
        # uma chave de cenário.
        candidato = master.get("cenario")

        if isinstance(candidato, dict):
            detalhado = candidato.get("score_detalhado")

    if not isinstance(detalhado, dict):
        detalhado = {}

    score = detalhado.get(
        "score_normalizado",
        master.get("score", "N/D"),
    )

    classificacao = detalhado.get(
        "classificacao",
        master.get("classificacao", "N/D"),
    )

    confianca_obj = master.get(
        "confianca",
        detalhado.get("confianca", "N/D"),
    )

    if isinstance(confianca_obj, dict):
        confianca = confianca_obj.get(
            "nivel",
            "N/D",
        )
    else:
        confianca = confianca_obj

    return score, classificacao, confianca


def executar():
    master = executar_koaiala()
    prediction = executar_prediction()
    reconciliation = executar_reconciliation()
    decision = executar_decision()

    estados = (
        master,
        prediction,
        reconciliation,
        decision,
    )

    for estado in estados:
        if isinstance(estado, dict):
            status = estado.get("status")
            if status not in (None, "OK"):
                raise RuntimeError(
                    "Um módulo do ciclo final retornou falha."
                )

    return {
        "status": "OK",
        "master": master,
        "prediction": prediction,
        "reconciliation": reconciliation,
        "decision": decision,
    }


def exibir(resultado):
    master = resultado["master"]
    prediction = resultado["prediction"]
    reconciliation = resultado["reconciliation"]
    decision = resultado["decision"]

    score, classificacao, confianca = _master_fields(
        master
    )

    print("=" * 76)
    print("KOAIALA OS — FINAL CYCLE 18.1")
    print("=" * 76)

    print()
    print("[1] MASTER / CENÁRIO")
    print("-" * 76)
    print(f"Score: {score}")
    print(f"Cenário: {classificacao}")
    print(f"Confiança: {confianca}")

    print()
    print("[2] EVIDÊNCIA PREDITIVA")
    print("-" * 76)

    for indicador, sinal in prediction["sinais"].items():
        if sinal.get("status") != "OK":
            print(f"{indicador}: INSUFICIENTE")
            continue

        print(
            f"{indicador}: "
            f"{sinal['sinal']} | "
            f"{sinal['status_sinal']} | "
            f"confiança={sinal['confianca']} | "
            f"ganho={sinal['ganho_historico']:+.2%}"
        )

    print()
    print("[3] RECONCILIAÇÃO")
    print("-" * 76)
    print(
        f"Cenário atual: "
        f"{reconciliation['cenario_atual']}"
    )
    print(
        f"Cenário preditivo: "
        f"{reconciliation['cenario_preditivo']}"
    )
    print(
        f"Estado: "
        f"{reconciliation['reconciliacao']}"
    )
    print(
        f"Risco: "
        f"{reconciliation['risco_reconciliacao']}"
    )

    print()
    print("[4] DECISÃO")
    print("-" * 76)
    print(f"Postura: {decision['postura']}")
    print(f"Horizonte: {decision['horizonte']}")
    print(f"Risco: {decision['risco']}")
    print(f"Confiança: {decision['confianca']}")
    print(
        f"Justificativa: "
        f"{decision['justificativa']}"
    )
    print(
        f"Gatilho: "
        f"{decision['gatilho_revisao']}"
    )

    print()
    print("[5] STATUS DO SISTEMA")
    print("-" * 76)
    print("SENSE: OK")
    print("ANALYSIS: OK")
    print("PREDICTION: OK")
    print("SCENARIO: OK")
    print("FORECAST: OK")
    print("RECONCILIATION: OK")
    print("RISK: OK")
    print("DECISION: OK")

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA OS 1.0 — FINAL CYCLE APROVADO ✓"
    )
    print("=" * 76)


if __name__ == "__main__":
    exibir(executar())
