import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CONSUMER_PATH = REPO / "src" / "bridges" / "data_rich_document_consumer.py"
BUILDER_PATH = REPO / "scripts" / "build_data_rich_reference_docx.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


consumer = load_module("data_rich_document_consumer", CONSUMER_PATH)
builder = load_module("build_data_rich_reference_docx", BUILDER_PATH)


class DataRichDocumentConsumerTests(unittest.TestCase):
    def manifest(self, markdown_hash):
        return {
            "schema": consumer.MANIFEST_SCHEMA,
            "source": {
                "document_id": "ADR-001",
                "document_version": "1.0.0",
                "semantic_ssot": "JSON",
                "git_repo": "GBOGEB/document-organization-system",
                "git_ref": "SOURCE-SHA",
                "path": "contracts/data_rich_document/examples/adr-001.json",
                "sha256": "0" * 64,
            },
            "projection": {
                "format": "MARKDOWN",
                "sha256": markdown_hash,
                "heading_contract": {
                    "maximum_heading_level": 3,
                    "numbering": "TEMPLATE_MANAGED",
                    "heading_text_contains_numbers": False,
                    "style_map": {
                        "1": "Heading 1",
                        "2": "Heading 2",
                        "3": "Heading 3",
                    },
                },
                "section_count": 3,
                "requirement_count": 0,
            },
            "docx_rtm_consumer": {
                "repo": consumer.CONSUMER_REPO,
                "forbidden_numbering_filter": "config/filters/extend_headings.lua",
            },
            "section_map": [
                {
                    "section_id": "SEC-001",
                    "title": "Context",
                    "heading_level": 1,
                },
                {
                    "section_id": "SEC-002",
                    "title": "Details",
                    "heading_level": 2,
                },
                {
                    "section_id": "SEC-003",
                    "title": "Decision",
                    "heading_level": 3,
                },
            ],
            "relations": [],
            "external_references": [],
            "authority": {
                "rendered_output_authoritative": False,
                "authority_transfer": False,
                "engineering_credit": False,
                "compliance_credit": False,
                "semantic_changes_allowed_in_consumer": False,
            },
        }

    def test_reference_builder_has_heading_1_to_3_numbering(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp) / "reference.docx"
            builder.build_reference_docx(ref)
            proof = consumer.inspect_numbering_contract(ref)
            self.assertEqual(proof["status"], "PASS")
            self.assertEqual(proof["styles"]["Heading1"]["ilvl"], "0")
            self.assertEqual(proof["styles"]["Heading2"]["ilvl"], "1")
            self.assertEqual(proof["styles"]["Heading3"]["ilvl"], "2")
            self.assertEqual(proof["levels"]["0"]["lvl_text"], "%1")
            self.assertEqual(proof["levels"]["1"]["lvl_text"], "%1.%2")
            self.assertEqual(proof["levels"]["2"]["lvl_text"], "%1.%2.%3")

    def test_manifest_validation_accepts_exact_hash_and_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "input.md"
            md.write_text("# Context\n", encoding="utf-8")
            digest = hashlib.sha256(md.read_bytes()).hexdigest()
            manifest = self.manifest(digest)
            consumer.validate_manifest(manifest, md, "SOURCE-SHA")

    def test_manifest_validation_rejects_markdown_hash_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "input.md"
            md.write_text("# Context\n", encoding="utf-8")
            manifest = self.manifest("f" * 64)
            with self.assertRaisesRegex(consumer.ConsumerError, "hash mismatch"):
                consumer.validate_manifest(manifest, md, "SOURCE-SHA")

    def test_manifest_validation_rejects_source_ref_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "input.md"
            md.write_text("# Context\n", encoding="utf-8")
            digest = hashlib.sha256(md.read_bytes()).hexdigest()
            manifest = self.manifest(digest)
            with self.assertRaisesRegex(consumer.ConsumerError, "source git ref mismatch"):
                consumer.validate_manifest(manifest, md, "OTHER-SHA")

    def test_manifest_validation_rejects_authority_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "input.md"
            md.write_text("# Context\n", encoding="utf-8")
            digest = hashlib.sha256(md.read_bytes()).hexdigest()
            manifest = self.manifest(digest)
            manifest["authority"]["rendered_output_authoritative"] = True
            with self.assertRaisesRegex(consumer.ConsumerError, "authority guard"):
                consumer.validate_manifest(manifest, md, "SOURCE-SHA")

    def test_manifest_validation_rejects_numbering_filter_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "input.md"
            md.write_text("# Context\n", encoding="utf-8")
            digest = hashlib.sha256(md.read_bytes()).hexdigest()
            manifest = self.manifest(digest)
            manifest["docx_rtm_consumer"]["forbidden_numbering_filter"] = None
            with self.assertRaisesRegex(consumer.ConsumerError, "forbid"):
                consumer.validate_manifest(manifest, md, "SOURCE-SHA")


if __name__ == "__main__":
    unittest.main()
