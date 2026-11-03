param()
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'project-console.ps1')
Start-ProjectConsole -Script $PSCommandPath -UseCase 'Run observer host, QNX, decoder, and packaging checks.' -Arguments (($PSBoundParameters.GetEnumerator() | ForEach-Object { '-{0}={1}' -f $_.Key,$_.Value }) -join ' ')
$consoleCompleted = $false
try {
    . (Join-Path $PSScriptRoot 'project-python.ps1')
    $projectRoot = Split-Path -Parent $PSScriptRoot
    Push-Location -LiteralPath $projectRoot
    try {
        Write-ProjectStatus 'Running Docker build/test phase.'
        docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:qemu sh native/observer/test-host.sh
        if ($LASTEXITCODE -ne 0) { throw 'Observer host tests failed.' }
        Write-ProjectStatus 'Running Docker build/test phase.'
        docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:qemu sh native/observer/test-qemu.sh
        if ($LASTEXITCODE -ne 0) { throw 'Observer QNX tests failed; inspect native/observer/build-qnx/qemu/qemu.log.' }
        Invoke-ProjectPython -B scripts/test_observer_decoder.py
        if ($LASTEXITCODE -ne 0) { throw 'Decoder tests failed.' }
        Invoke-ProjectPython -B scripts/package_delphi_observer.py
        if ($LASTEXITCODE -ne 0) { throw 'Observer packaging gate failed.' }
    } finally { Pop-Location }
    $consoleCompleted = $true
} finally { Stop-ProjectConsole -Failed:(-not $consoleCompleted) }
