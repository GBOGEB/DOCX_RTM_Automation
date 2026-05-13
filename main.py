#!/usr/bin/env python3
"""
Main RTM Automation Entry Point.

Standard mode (default):
    python main.py
    Process DOCX files in input/ and write converted output to output/.

Canonical extraction mode:
    python main.py --extract-canonical [--force]
    Read source files from canonical/inputs/, run all extractors, write
    versioned JSON artefacts to canonical/artefacts/, and update the
    extraction_manifest.json.  Idempotent by default — skips sources whose
    SHA-256 is already recorded in the manifest.  Pass --force to re-extract.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports (only needed in the relevant mode)
# ---------------------------------------------------------------------------

def _import_document_converter():
    try:
        from src.rtm.document_converter import run_document_conversion
        return run_document_conversion
    except ImportError:
        try:
            from document_converter import run_document_conversion  # type: ignore
            return run_document_conversion
        except ImportError:
            print("❌ Could not import document_converter module")
            print("Please ensure the RTM automation modules are available")
            sys.exit(1)


# ---------------------------------------------------------------------------
# Standard processing mode
# ---------------------------------------------------------------------------

def find_input_documents() -> list[Path]:
    """Find DOCX files to process in standard mode."""
    input_dirs = ["input", ".", "documents"]
    docx_files: list[Path] = []
    for input_dir in input_dirs:
        dir_path = Path(input_dir)
        if dir_path.exists():
            docx_files.extend(dir_path.glob("*.docx"))
    return docx_files


def run_standard_mode() -> int:
    """Process DOCX files through the existing document_converter pipeline."""
    run_document_conversion = _import_document_converter()

    print("🚀 RTM AUTOMATION SYSTEM")
    print("=" * 30)
    print("Starting document conversion process...\n")

    docx_files = find_input_documents()

    if not docx_files:
        print("⚠️  No DOCX files found for processing")
        print("\nSuggestions:")
        print("   • Place DOCX files in an 'input/' directory")
        print("   • Or place them in the current directory")
        print("   • Ensure files have .docx extension")
        return 1

    print(f"📄 Found {len(docx_files)} DOCX file(s) to process:")
    for docx_file in docx_files:
        print(f"   • {docx_file}")

    total_processed = 0
    total_errors = 0

    for docx_file in docx_files:
        print(f"\n🔄 Processing: {docx_file.name}")
        try:
            result = run_document_conversion(str(docx_file))
            if result:
                print(f"   ✅ Successfully processed: {docx_file.name}")
            else:
                print(f"   ⚠️  Processing completed with warnings: {docx_file.name}")
            total_processed += 1
        except Exception as exc:
            print(f"   ❌ Error processing {docx_file.name}: {exc}")
            total_errors += 1

    print(f"\n📊 PROCESSING SUMMARY")
    print("=" * 25)
    print(f"Files found:              {len(docx_files)}")
    print(f"Successfully processed:   {total_processed}")
    print(f"Errors:                   {total_errors}")

    if total_processed > 0:
        print(f"\n✅ RTM automation completed!")
        print(f"📁 Check 'output/' directory for results")
        output_dir = Path("output")
        if output_dir.exists():
            print(f"📊 Generated {len(list(output_dir.glob('*')))} output files")
        return 0

    print(f"\n❌ No files were successfully processed")
    return 1


# ---------------------------------------------------------------------------
# Canonical extraction mode
# ---------------------------------------------------------------------------

# Maps (file glob pattern, artefact_name) → extractor module import path + run fn
_EXTRACTORS: list[tuple[str, str, str, str]] = [
    # (glob_pattern,           artefact_name,       module_path,                         run_fn)
    ("*.docx",                 "master_requirements", "src.extractors.extract_master_docx", "run"),
    ("RTM*.xlsx",              "rtm_matrix",          "src.extractors.extract_rtm_excel",   "run"),
    ("OFFER_ITEMS*.xlsx",      "offer_items",          "src.extractors.extract_offer_excel", "run"),
    ("OFFER_TABLES*.pdf",      "offer_tables",         "src.extractors.extract_offer_pdf_tables", "run"),
]


def _import_extractor(module_path: str, fn_name: str):
    import importlib
    mod = importlib.import_module(module_path)
    return getattr(mod, fn_name)


def _resolve_source_file(inputs_dir: Path, glob_pattern: str, artefact_name: str) -> Path | None:
    """Return the single best-match source file for a given glob in inputs_dir."""
    matches = list(inputs_dir.glob(glob_pattern))
    if not matches:
        return None
    if len(matches) > 1:
        logger.warning(
            "Multiple files match '%s' for artefact '%s': %s — using first",
            glob_pattern, artefact_name, [m.name for m in matches],
        )
    return matches[0]


def run_canonical_extraction(force: bool = False) -> int:
    """
    One-time extraction pipeline:  canonical/inputs/ → canonical/artefacts/
    Idempotent unless --force is given.
    """
    from src.core.extraction_manifest import ExtractionManifest

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    repo_root = Path(__file__).parent
    inputs_dir = repo_root / "canonical" / "inputs"
    artefacts_dir = repo_root / "canonical" / "artefacts"

    print("🔬 CANONICAL EXTRACTION PIPELINE")
    print("=" * 40)
    print(f"   Inputs:    {inputs_dir}")
    print(f"   Artefacts: {artefacts_dir}\n")

    if not inputs_dir.exists():
        print(f"❌ Inputs directory not found: {inputs_dir}")
        print("   Create it and drop source files there, then re-run.")
        return 1

    manifest = ExtractionManifest()
    total_extracted = 0
    total_skipped = 0
    total_errors = 0

    for glob_pattern, artefact_name, module_path, fn_name in _EXTRACTORS:
        source_path = _resolve_source_file(inputs_dir, glob_pattern, artefact_name)
        if not source_path:
            print(f"   ⏭  No file matching '{glob_pattern}' for '{artefact_name}' — skipping")
            continue

        # Idempotency check
        if not force and manifest.is_already_extracted(source_path, artefact_name):
            print(f"   ✓  '{artefact_name}' already extracted — skipping (use --force to re-run)")
            total_skipped += 1
            continue

        # Determine versioned output path
        output_path = manifest.next_version_path(artefact_name, artefacts_dir)
        print(f"   🔄 Extracting '{artefact_name}' from {source_path.name} → {output_path.name}")

        try:
            run_fn = _import_extractor(module_path, fn_name)

            # PDF extractor takes (pdf_path, output_path); XLSX take optional sheet arg
            if source_path.suffix.lower() == ".pdf":
                run_fn(source_path, output_path)
            else:
                run_fn(source_path, output_path)

            manifest.record(
                source_path=source_path,
                artefact_name=artefact_name,
                output_path=output_path,
            )
            print(f"      ✅ Written to {output_path.name}")
            total_extracted += 1

        except Exception as exc:
            print(f"      ❌ Error: {exc}")
            logger.exception("Extraction failed for %s", artefact_name)
            total_errors += 1

    manifest.save()

    print(f"\n📊 EXTRACTION SUMMARY")
    print("=" * 25)
    print(f"Extracted:  {total_extracted}")
    print(f"Skipped:    {total_skipped}")
    print(f"Errors:     {total_errors}")

    if total_errors:
        print("\n⚠️  Some extractions failed — check logs above.")
        return 1

    print(f"\n✅ Canonical extraction complete.")
    print(f"   Next steps:")
    print(f"   1. python scripts/verify_canonical.py   # verify integrity")
    print(f"   2. python scripts/lock_canonical.py --tag  # lock + git tag")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="RTM Automation — document processing and canonical extraction"
    )
    parser.add_argument(
        "--extract-canonical",
        action="store_true",
        help=(
            "Run canonical extraction pipeline: read source files from "
            "canonical/inputs/, extract structured data, write versioned JSON "
            "artefacts to canonical/artefacts/."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --extract-canonical: re-extract even if SHA-256 already recorded.",
    )
    args = parser.parse_args()

    if args.extract_canonical:
        return run_canonical_extraction(force=args.force)
    return run_standard_mode()


if __name__ == "__main__":
    sys.exit(main())
