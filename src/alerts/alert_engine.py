"""
KOAIALA ALERT ENGINE 22.1

Motor de eventos operacionais.
Não altera Scenario, Prediction, Reconciliation ou Decision.
Recebe o ciclo já calculado e transforma fatos relevantes em alertas.

Severidade:
- CRITICO: divergência + múltiplos sinais ativos
- ALTO: divergência entre cenário atual e preditivo
- MODERADO: sinal preditivo ativo com ganho positivo
- INFO: nenhum evento relevante
"""

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Alert:
    code: str
    severity: str
    title: str
    message: str
    source: str

    def to_dict(self):
        return asdict(self)


def _active_signals(prediction: dict[str, Any]) -> list[str]:
    result = []
    for indicator, signal in prediction.get("sinais", {}).items():
        if signal.get("status") == "SINAL_ATIVO":
            result.append(indicator)
    return result


def avaliar(cycle: dict[str, Any]) -> dict[str, Any]:
    reconciliation = cycle.get("reconciliation", {})
    prediction = cycle.get("prediction", {})
    decision = cycle.get("decision", {})

    current = reconciliation.get("cenario_atual", "N/D")
    predictive = reconciliation.get("cenario_preditivo", "N/D")
    reconciliation_state = reconciliation.get(
        "reconciliacao", "N/D"
    )

    active = _active_signals(prediction)

    alerts: list[Alert] = []

    if reconciliation_state == "DIVERGENCIA":
        severity = "ALTO"
        if len(active) >= 3:
            severity = "CRITICO"

        alerts.append(
            Alert(
                code="RECONCILIATION_DIVERGENCE",
                severity=severity,
                title="Divergência entre cenário e previsão",
                message=(
                    f"Cenário atual {current} diverge da "
                    f"projeção {predictive}."
                ),
                source="RECONCILIATION",
            )
        )

    for indicator in active:
        signal = prediction.get("sinais", {}).get(
            indicator, {}
        )
        gain = signal.get("ganho_historico")

        if isinstance(gain, (int, float)) and gain > 0:
            alerts.append(
                Alert(
                    code=f"PREDICTIVE_SIGNAL_{indicator}",
                    severity="MODERADO",
                    title=f"Sinal preditivo ativo: {indicator}",
                    message=(
                        f"{indicator}: sinal="
                        f"{signal.get('sinal', 'N/D')}, "
                        f"confiança="
                        f"{signal.get('confianca', 'N/D')}, "
                        f"ganho vs baseline="
                        f"{gain * 100:+.2f} p.p."
                    ),
                    source="PREDICTION",
                )
            )

    if not alerts:
        alerts.append(
            Alert(
                code="NO_SIGNIFICANT_EVENT",
                severity="INFO",
                title="Nenhum evento relevante",
                message=(
                    "O ciclo atual não apresentou evento "
                    "que ultrapasse os critérios do Alert Engine."
                ),
                source="ALERT_ENGINE",
            )
        )

    # A postura da decisão é informação contextual, não uma nova regra.
    posture = decision.get("postura", "N/D")

    severity_rank = {
        "INFO": 0,
        "MODERADO": 1,
        "ALTO": 2,
        "CRITICO": 3,
    }

    highest = max(
        alerts,
        key=lambda item: severity_rank[item.severity],
    )

    return {
        "status": "OK",
        "total_alertas": len(alerts),
        "maior_severidade": highest.severity,
        "postura_contextual": posture,
        "alertas": [alert.to_dict() for alert in alerts],
    }
