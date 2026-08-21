$ErrorActionPreference = "Stop"

$Project = "C:\PROJETOS\koaiala-os"
Set-Location $Project

Write-Host "============================================================"
Write-Host "KOAIALA OPERATIONAL ALERT CYCLE 22.3"
Write-Host "============================================================"

python -m src.core.operational_alert_cycle

if ($LASTEXITCODE -ne 0) {
    Write-Host "FALHA NO CICLO OPERACIONAL + ALERTAS"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "CICLO OPERACIONAL + ALERTAS CONCLUÍDO COM SUCESSO"
