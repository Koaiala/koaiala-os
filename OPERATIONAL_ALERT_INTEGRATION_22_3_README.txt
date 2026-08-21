KOAIALA OPERATIONAL ALERT INTEGRATION 22.3

Objetivo:
Conectar o Operational Runner existente ao Alert Engine e ao
armazenamento PostgreSQL, sem substituir o operational_run.py.

Teste principal:
python -m src.core.operational_alert_integration_check

Execução:
python -m src.core.operational_alert_cycle

PowerShell:
powershell.exe -ExecutionPolicy Bypass -File "C:\PROJETOS\koaiala-os\ops\run_alert_cycle_now.ps1"

IMPORTANTE:
A tarefa agendada atual NÃO é alterada automaticamente por este pacote.
Primeiro valide o check 22.3. Depois fazemos a troca controlada do
comando da tarefa diária.
