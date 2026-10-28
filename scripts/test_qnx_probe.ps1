param([switch]$BuildToolchain, [switch]$BuildEmulator)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    if ($BuildToolchain) {
        $pythonPath = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        & $pythonPath -B scripts/build_qnx_toolchain.py
        if ($LASTEXITCODE -ne 0) { throw 'Compiler build failed; see .tools/qnx-toolchain-tar-build.log' }
    }
    if ($BuildEmulator) {
        docker build -f native/loader-probe/Qemu.Dockerfile -t delphi-qnx65:qemu native/loader-probe
        if ($LASTEXITCODE -ne 0) { throw 'Emulator image build failed.' }
    }
    docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:8.5 sh native/loader-probe/build.sh host
    if ($LASTEXITCODE -ne 0) { throw 'Host fixture failed.' }
    docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:qemu sh native/loader-probe/run-qemu.sh uip
    if ($LASTEXITCODE -ne 0) { throw 'QNX run-once negative control did not reproduce the expected failure.' }
    docker run --rm --network none --mount "type=bind,source=$projectRoot,target=/src" --workdir /src delphi-qnx65:qemu sh native/loader-probe/run-qemu.sh copy
    if ($LASTEXITCODE -ne 0) { throw 'QNX fixture failed; inspect native/loader-probe/build-qnx/qemu/qemu.log' }
} finally { Pop-Location }
