function Invoke-ProjectPython {
    # An explicit interpreter path is optional; otherwise use the machine's PATH.
    if ($env:PYTHON) {
        $command = Get-Command $env:PYTHON -ErrorAction Stop
        $launcherArgs = @()
    } else {
        $command = Get-Command python3, python, py -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $command) { throw 'Install Python 3.10+ on PATH, or set PYTHON to its executable.' }
        $launcherArgs = if ($command.Name -in @('py', 'py.exe')) { @('-3') } else { @() }
    }
    & $command.Source @launcherArgs -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
    if ($LASTEXITCODE -ne 0) { throw 'The selected interpreter must be Python 3.10 or newer.' }
    & $command.Source @launcherArgs @args
    if ($LASTEXITCODE -ne 0) { throw "Python command failed with exit code $LASTEXITCODE." }
}
