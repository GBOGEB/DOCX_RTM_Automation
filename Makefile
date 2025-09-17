SHELL := /bin/bash

.PHONY: help init qa scaffold package ci-local clean scan-7d report-7d

help:
	@echo "Targets:"
	@echo "  init         - create venv, install tooling"
	@echo "  qa           - run all quality checks"
	@echo "  scaffold     - generate outline, baseline seed, machine docs"
	@echo "  scan-7d      - run 7-day metadata scan and update baseline candidate"
	@echo "  report-7d    - open or print the 7-day report path"
	@echo "  package      - build dist/orchestration_bundle.zip"
	@echo "  ci-local     - run CI-like pipeline locally"
	@echo "  clean        - remove build artifacts"

init:
	chmod +x scripts/bootstrap.sh || true
	./scripts/bootstrap.sh || true

qa:
	. .venv/bin/activate && pre-commit run --all-files

scaffold:
	. .venv/bin/activate && python tools/outline_to_md.py
	. .venv/bin/activate && python tools/baseline.py --init
	. .venv/bin/activate && python tools/pairwise_rank.py --example

scan-7d:
	. .venv/bin/activate && python tools/scan_7d.py

report-7d:
	@echo "Report: docs/SCAN_7D.md"

package:
	mkdir -p dist
	rm -f dist/orchestration_bundle.zip
	zip -r dist/orchestration_bundle.zip \
		pyproject.toml package.json .pre-commit-config.yaml .yamllint.yaml .markdownlint.yaml .editorconfig .gitignore \
		.github .devcontainer scripts tools docs agent baseline config

ci-local: qa package

clean:
	rm -rf dist __pycache__ .pytest_cache