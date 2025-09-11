#!/usr/bin/env bash
set -euo pipefail

echo "[bootstrap] Ensuring Python venv..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
pip install pre-commit ruff black isort pylint pytest requests pyyaml

echo "[bootstrap] Setting up Node dev deps..."
if command -v node >/dev/null 2>&1; then
  npm install
else
  echo "[bootstrap] Node not found; skipping npm install."
fi

echo "[bootstrap] Installing Go tools (optional)..."
if command -v go >/dev/null 2>&1; then
  GO111MODULE=on go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.59.1
fi

echo "[bootstrap] Registering pre-commit hooks..."
pre-commit install --install-hooks

echo "[bootstrap] Done. Activate venv with: source .venv/bin/activate"