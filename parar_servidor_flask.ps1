param(
    [int]$Port = 5000
)

$connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if (-not $connections) {
    Write-Host "Nenhum servidor está usando a porta $Port." -ForegroundColor Yellow
    exit 0
}

$processIds = $connections.OwningProcess | Sort-Object -Unique
$processes = foreach ($processId in $processIds) {
    Get-CimInstance Win32_Process -Filter "ProcessId = $processId" |
        Select-Object ProcessId, Name, CommandLine
}

Write-Host "Servidor encontrado na porta ${Port}:" -ForegroundColor Cyan
$processes | Format-Table -AutoSize

$answer = Read-Host "Finalizar esse processo? (S/N)"
if ($answer -notmatch '^[SsYy]$') {
    Write-Host 'Nenhum processo foi finalizado.' -ForegroundColor Yellow
    exit 0
}

foreach ($processId in $processIds) {
    Stop-Process -Id $processId -Force
    Write-Host "Processo $processId finalizado." -ForegroundColor Green
}
