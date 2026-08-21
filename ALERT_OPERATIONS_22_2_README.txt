KOAIALA ALERT OPERATIONS 22.2

Objetivo:
Levar o Alert Engine para operação persistente.

Fluxo:
FULL CYCLE -> ALERT ENGINE -> ALERT STORAGE

Tabela criada:
koaiala_alerts

Testar:
python -m src.core.alert_operations_check

Executar manualmente:
python -m src.core.alert_operations

O módulo não altera os motores Scenario, Prediction,
Reconciliation ou Decision.
