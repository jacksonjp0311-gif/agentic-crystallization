[CmdletBinding()]
param(
 [ValidateSet('setup','test','verify','demo','reproduce','package','status','simulate')]
 [string]$Action='status',
 [string]$Python='python',
 [int]$StartSeed=90000,
 [int]$Worlds=1
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$priorPath=$env:PYTHONPATH
Push-Location $root
try {
 $OutputEncoding=New-Object System.Text.UTF8Encoding($false)
 $env:PYTHONIOENCODING='utf-8'
 $env:PYTHONDONTWRITEBYTECODE='1'
 $env:PYTHONPATH="$root;$root\src"
 $env:OPENBLAS_NUM_THREADS='1'
 New-Item -ItemType Directory -Force (Join-Path $root 'work') | Out-Null
 Add-Content -Encoding UTF8 (Join-Path $root 'work/operator.log') "$(Get-Date -Format o) $Action started"
 $venv=Join-Path $root '.venv\Scripts\python.exe'
 function Invoke-Python {
  & $script:runner @args
  if($LASTEXITCODE -ne 0){throw "Python command failed ($LASTEXITCODE): $args"}
 }
 $script:runner=$Python
 if($Action -eq 'setup') {
  if(!(Test-Path -LiteralPath $venv)){Invoke-Python -m venv .venv}
  $script:runner=$venv
  Invoke-Python -m pip install . build
 } else {
  if(Test-Path -LiteralPath $venv){$script:runner=$venv}
  switch($Action) {
   test {Invoke-Python -m unittest discover -s tests -v}
   verify {Invoke-Python scripts/research_verify.py}
   reproduce {Invoke-Python scripts/reproduce.py}
   package {Invoke-Python -m build; Invoke-Python scripts/package.py}
   status {
    & git status --short --branch
    if($LASTEXITCODE -ne 0){throw 'Git status failed'}
   }
   {$_ -in 'demo','simulate'} {
    if($Worlds -lt 1 -or $Worlds -gt 100){throw 'Worlds must be between 1 and 100'}
    $out='work/demo_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff')
    Invoke-Python -m agentic_crystallization.stage_p --out $out --start-seed $StartSeed --count $Worlds --max-age 4 --no-cue
   }
  }
 }
 Add-Content -Encoding UTF8 (Join-Path $root 'work/operator.log') "$(Get-Date -Format o) $Action passed"
} finally {
 $env:PYTHONPATH=$priorPath
 Pop-Location
}