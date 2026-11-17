# Run from PowerShell: powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -ne "AMD64") {
    throw "This lab environment requires Windows x64."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = "$HOME\.local\bin;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw "uv installation failed. Restart PowerShell after installing uv, then rerun this script."
    }
}

# TensorFlow's native Windows wheels require the Microsoft C++ runtime.
if (-not (Test-Path "$env:WINDIR\System32\msvcp140_1.dll")) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "Install the x64 C++ runtime from https://aka.ms/vs/17/release/vc_redist.x64.exe and rerun this script."
    }
    winget install --id Microsoft.VCRedist.2015+.x64 --exact --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Microsoft C++ runtime installation failed." }
}

# UTF-8 is needed by the English/emoji/GloVe text files on Chinese Windows.
$env:PYTHONUTF8 = "1"
uv sync --locked
if ($LASTEXITCODE -ne 0) { throw "uv sync failed." }

uv run --locked python scripts/check_environment.py
if ($LASTEXITCODE -ne 0) { throw "Environment check failed; see the error above." }

uv run --locked python -m ipykernel install --user --name dls-labs --display-name "DLS Labs (uv Python 3.10)" --env PYTHONUTF8 1
if ($LASTEXITCODE -ne 0) { throw "Jupyter kernel registration failed." }

Write-Host "Ready. Open this repository in VS Code and select the DLS Labs (uv Python 3.10) notebook kernel."
