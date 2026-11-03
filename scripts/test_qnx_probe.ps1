param([switch]$BuildToolchain, [switch]$BuildEmulator)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'project-console.ps1')
Start-ProjectConsole -Script $PSCommandPath -UseCase 'Build and validate the QNX loader probe.' -Arguments (($PSBoundParameters.GetEnumerator() | ForEach-Object { '-{0}={1}' -f $_.Key,$_.Value }) -join ' ')
$consoleCompleted = $false
try {
    . (Join-Path $PSScriptRoot 'project-python.ps1')
    $projectRoot = Split-Path -Parent $PSScriptRoot
    Push-Location -LiteralPath $projectRoot
    try {
        if ($BuildToolchain) {
            Invoke-ProjectPython -B scripts/build_qnx_toolchain.py
            if ($LASTEXITCODE -ne 0) { throw 'Compiler build failed; see .tools/qnx-toolchain-tar-build.log' }
        }
        if ($BuildEmulator) {
            Write-ProjectStatus 'Running Docker build/test phase.'
            docker build -f native/loader-probe/Qemu.Dockerfile -t delphi-qnx65:qemu native/loader-probe
            if ($LASTEXITCODE -ne 0) { throw 'Emulator image build failed.' }
        }
        Write-ProjectStatus 'Running Docker build/test phase.'
        docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:8.5 sh native/loader-probe/build.sh host
        if ($LASTEXITCODE -ne 0) { throw 'Host fixture failed.' }
        Write-ProjectStatus 'Running Docker build/test phase.'
        docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:qemu sh native/loader-probe/run-qemu.sh uip
        if ($LASTEXITCODE -ne 0) { throw 'QNX run-once negative control did not reproduce the expected failure.' }
        Write-ProjectStatus 'Running Docker build/test phase.'
        docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:qemu sh native/loader-probe/run-qemu.sh copy
        if ($LASTEXITCODE -ne 0) { throw 'QNX fixture failed; inspect native/loader-probe/build-qnx/qemu/qemu.log' }
    } finally { Pop-Location }
    $consoleCompleted = $true
} finally { Stop-ProjectConsole -Failed:(-not $consoleCompleted) }
