#Requires -Version 7.0
$ErrorActionPreference = "Stop"

Write-Host "[bootstrap] Ensuring Python venv..."
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip wheel setuptools
pip install pre-commit ruff black isort pylint pytest requests pyyaml

Write-Host "[bootstrap] Setting up Node dev deps..."
if (Get-Command node -ErrorAction SilentlyContinue) {
  npm install
} else {
  Write-Warning "[bootstrap] Node not found; skipping npm install."
}

Write-Host "[bootstrap] Installing Go tools (optional)..."
if (Get-Command go -ErrorAction SilentlyContinue) {
  $env:GO111MODULE = "on"
  go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.59.1
}

Write-Host "[bootstrap] Registering pre-commit hooks..."
pre-commit install --install-hooks

Write-Host "[bootstrap] Done. Activate venv with: .\.venv\Scripts\Activate.ps1"