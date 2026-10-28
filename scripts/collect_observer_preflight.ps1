param([string]$HostAddress = '192.168.1.4', [switch]$AskPassword, [switch]$SupervisorOnly)
$ErrorActionPreference = 'Stop'
$cachedPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$scriptPath = Join-Path $PSScriptRoot 'collect_observer_preflight.py'
if (Test-Path -LiteralPath $cachedPython) { $executable = $cachedPython; $arguments = @('-B') }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $executable = 'py'; $arguments = @('-3', '-B') }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $executable = 'python'; $arguments = @('-B') }
else { throw 'Python 3 was not found on this laptop.' }
$arguments += @($scriptPath, '--host', $HostAddress)
if ($SupervisorOnly) { $arguments += '--supervisor-only' }
if ($AskPassword) { $arguments += '--ask-password' }
& $executable @arguments
exit $LASTEXITCODE
