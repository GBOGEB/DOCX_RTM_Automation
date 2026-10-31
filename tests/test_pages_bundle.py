"""Contract tests for the GitHub Pages source (.github/workflows/pages.yml).

The site is the github-pages Jekyll build of the repository root. With no index page and no
_config.yml, jekyll-readme-index renders README.md as the entry page, titled
"DOCX RTM Automation | DOCX_RTM_Automation". These tests pin that source shape.
Only the standard library and pytest are needed.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
JEKYLL_IMAGE_DIGEST = "sha256:6791ebfd912185ed59bfb5fb102664fa872496b79f87ff8b9cfba292a7345041"

README_HEADINGS = [
    "# DOCX RTM Automation",
    "## 1. Purpose",
    "## 2. Current implemented surfaces",
    "## 3. Quick start",
    "## 10. Roadmap policy",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_is_the_entry_page_with_its_headings():
    lines = [line.rstrip() for line in _read(ROOT / "README.md").splitlines()]
    assert lines[0] == "# DOCX RTM Automation"
    for heading in README_HEADINGS:
        assert heading in lines, heading


def test_nothing_shadows_readme_as_entry_page():
    # jekyll-readme-index only uses README.md when no root index exists; a _config.yml
    # would change the title/theme of what is live today.
    for name in ("index.md", "index.html", "index.markdown", "_config.yml", "_config.yaml"):
        assert not (ROOT / name).exists(), name


def test_single_pages_workflow_builds_repo_root_with_pinned_jekyll_image():
    text = _read(WORKFLOWS / "pages.yml")
    assert "INPUT_SOURCE=./ " in text
    assert "INPUT_DESTINATION=_site" in text
    assert f"ghcr.io/actions/jekyll-build-pages@{JEKYLL_IMAGE_DIGEST}" in text
    assert "artifact-path: _site" in text
    assert "environment: production" in text


def test_racing_starter_workflows_are_gone():
    assert not (WORKFLOWS / "jekyll-gh-pages.yml").exists()
    assert not (WORKFLOWS / "static.yml").exists()
    others = [p.name for p in WORKFLOWS.glob("*.y*ml") if p.name != "pages.yml"]
    for name in others:
        assert "deploy-pages" not in _read(WORKFLOWS / name), name
