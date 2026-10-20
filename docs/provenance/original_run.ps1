# Agentic Crystallization v2.4 -- one PowerShell entry point (PowerShell 5.1+).
[CmdletBinding()]
param(
    [ValidateSet('test','demo','simulate','verify')]
    [string]$Action = 'demo',
    [int]$StartSeed = 90000,
    [int]$Worlds = 3
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root
try {
    $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONPATH = Join-Path $root 'src'
    $env:OPENBLAS_NUM_THREADS = '1'
    Write-Host "Agentic Crystallization v2.4 | $Action | $root"
    if ($Action -eq 'test') {
        & python -m unittest discover -s tests -v
        if ($LASTEXITCODE -ne 0) { throw 'Unit tests failed' }
    }
    if ($Action -eq 'verify') {
        & python scripts/verify_package.py .
        if ($LASTEXITCODE -ne 0) { throw 'Package SHA256 verification failed' }
        & python scripts/verify_stage_p.py . --cohort stage_p_holdout
        if ($LASTEXITCODE -ne 0) { throw 'Stage P holdout verification failed' }
        & python scripts/verify_stage_p.py . --cohort stage_p_replication
        if ($LASTEXITCODE -ne 0) { throw 'Stage P replication verification failed' }
    }
    if ($Action -eq 'simulate') {
        if ($Worlds -lt 1) { throw 'Worlds must be positive' }
        $out = 'experiments/local_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
        & python -m agentic_crystallization.stage_p --out $out --start-seed $StartSeed --count $Worlds --max-age 4 --no-cue
        if ($LASTEXITCODE -ne 0) { throw 'Simulation failed' }
        Write-Host "New experiment: $out"
    }
    if ($Action -eq 'demo') {
        $out = 'experiments/local_demo_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
        & python -m agentic_crystallization.stage_p --out $out --start-seed $StartSeed --count 1 --max-age 4 --no-cue
        if ($LASTEXITCODE -ne 0) { throw 'Demo failed' }
        Write-Host "Demo receipts: $out"
    }
}
finally { Pop-Location }
