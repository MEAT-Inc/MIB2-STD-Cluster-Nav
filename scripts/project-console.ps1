function Write-ProjectStatus {
    param([string]$Message, [ValidateSet('INFO','STEP','OK','WARN','ERROR')][string]$Level = 'STEP')
    $line = '[{0:HH:mm:ss}] [{1,-6}] {2}' -f (Get-Date), $Level, $Message
    $colors = @{ INFO='Cyan'; STEP='Blue'; OK='Green'; WARN='Yellow'; ERROR='Red' }
    if (-not [Console]::IsErrorRedirected -and -not (Test-Path Env:NO_COLOR) -and $env:TERM -ne 'dumb') {
        $previousColor = [Console]::ForegroundColor
        try { [Console]::ForegroundColor = $colors[$Level]; [Console]::Error.WriteLine($line) }
        finally { [Console]::ForegroundColor = $previousColor }
    } else { [Console]::Error.WriteLine($line) }
}

function Start-ProjectConsole {
    param([string]$Script, [string]$UseCase, [string]$Arguments, [string]$Version = '1.0')
    $script:previousConsoleDepth = $env:PROJECT_CONSOLE_DEPTH
    if (-not $env:PROJECT_CONSOLE_DEPTH -and -not [Console]::IsErrorRedirected) { Clear-Host }
    $env:PROJECT_CONSOLE_DEPTH = '1'
    if (-not $Arguments) { $Arguments = '(none)' }
    [Console]::Error.WriteLine("`n" + ('=' * 72))
    [Console]::Error.WriteLine("$(Split-Path -Leaf $Script) | version $Version")
    [Console]::Error.WriteLine("Arguments: $Arguments")
    [Console]::Error.WriteLine("Use case: $UseCase")
    [Console]::Error.WriteLine('=' * 72)
    Write-ProjectStatus 'Starting script.'
}

function Stop-ProjectConsole {
    param([switch]$Failed)
    if ($Failed) { Write-ProjectStatus 'Stopped with an error.' ERROR }
    else { Write-ProjectStatus 'Finished.' OK }
    $env:PROJECT_CONSOLE_DEPTH = $script:previousConsoleDepth
}
