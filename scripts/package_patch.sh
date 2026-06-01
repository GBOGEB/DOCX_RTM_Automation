#!/usr/bin/env bash
#
# package_patch.sh - Assemble the handover bundle for the federated artifact
# ownership patch package.
#
# The canonical source of truth is the single self-contained patch markdown file
# under patches/. This script stages that file together with its derived
# supporting artifacts into a bundle directory and (optionally) zips it.
#
# Usage:
#   scripts/package_patch.sh            # stage bundle under dist/handover_bundle/
#   scripts/package_patch.sh --zip      # also produce dist/handover_bundle.zip
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PATCH_FILE="patches/2026-06-01_federated-artifact-ownership_v0.1.patch.md"
BUNDLE_DIR="dist/handover_bundle"
ZIP_PATH="dist/handover_bundle.zip"

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "ERROR: canonical patch file not found: $PATCH_FILE" >&2
  exit 1
fi

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/patches" "$BUNDLE_DIR/manifest" "$BUNDLE_DIR/handover"

cp "$PATCH_FILE" "$BUNDLE_DIR/patches/"
[[ -f manifest/artifact-topology.yaml ]] && cp manifest/artifact-topology.yaml "$BUNDLE_DIR/manifest/"
[[ -f handover/README.md ]] && cp handover/README.md "$BUNDLE_DIR/handover/"

echo "Staged handover bundle at: $BUNDLE_DIR"

if [[ "${1:-}" == "--zip" ]]; then
  rm -f "$ZIP_PATH"
  (cd dist && zip -r "handover_bundle.zip" "handover_bundle" >/dev/null)
  echo "Created zip: $ZIP_PATH"
fi
