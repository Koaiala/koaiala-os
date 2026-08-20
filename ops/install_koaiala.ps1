# KOAIALA OS 1.0 - instalação operacional
# Execute em PowerShell como Administrador.

$ErrorActionPreference = "Stop"

$Project = "C:\PROJETOS\koaiala-os"
$TaskName = "\Koaiala\Koaiala OS Daily"
$Xml = Join-Path $Project "ops\koaiala_daily.xml"

if (-not (Test-Path $Project)) {
    throw "Projeto não encontrado: $Project"
}

if (-not (Test-Path (Join-Path $Project "run_koaiala.ps1"))) {
    throw "run_koaiala.ps1 não encontrado."
}

if (-not (Test-Path $Xml)) {
    throw "XML da tarefa não encontrado: $Xml"
}

Write-Host "Validando execução operacional..."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Project "run_koaiala.ps1")

Write-Host "Registrando tarefa..."
schtasks.exe /Create /TN $TaskName /XML $Xml /F | Out-Host

Write-Host ""
Write-Host "Tarefa instalada:"
Write-Host $TaskName
Write-Host ""
Write-Host "Teste manual da tarefa:"
Write-Host "schtasks.exe /Run /TN `"$TaskName`""
Write-Host ""
Write-Host "Consulta:"
Write-Host "schtasks.exe /Query /TN `"$TaskName`" /V /FO LIST"
