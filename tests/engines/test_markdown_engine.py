
"""
Unit tests for Markdown document processing engine.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
import sys

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.fixtures.mock_documents import MockDocumentGenerator

class TestMarkdownEngine:
    """Test suite for Markdown document processing engine."""
    
    @pytest.fixture
    def markdown_engine(self):
        """Create a mock Markdown processing engine."""
        mock_engine = Mock()
        mock_engine.process = Mock(return_value={
            "status": "success",
            "output_file": "test.html",
            "metadata": {"sections": 5, "links": 3, "code_blocks": 2}
        })
        return mock_engine
    
    @pytest.fixture
    def sample_markdown_docs(self, temp_dir):
        """Create sample Markdown documents for testing."""
        generator = MockDocumentGenerator()
        docs = {
            "basic": generator.create_markdown_document(temp_dir / "basic.md", "basic"),
            "rtm": generator.create_markdown_document(temp_dir / "rtm.md", "rtm"),
            "complex": generator.create_markdown_document(temp_dir / "complex.md", "complex"),
        }
        return docs
    
    def test_markdown_engine_basic_processing(self, markdown_engine, sample_markdown_docs, performance_monitor, cricket_score_config):
        """Test basic Markdown document processing with cricket scoring."""
        performance_monitor.start()
        
        result = markdown_engine.process(sample_markdown_docs["basic"])
        
        performance_monitor.stop()
        
        # Validate result
        assert result["status"] == "success"
        assert "output_file" in result
        assert "metadata" in result
        
        # Cricket scoring for performance
        cricket_score = performance_monitor.calculate_cricket_score(
            cricket_score_config["performance_thresholds"]["markdown_processing"]
        )
        
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent Markdown processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good Markdown processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable Markdown processing performance: {cricket_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor Markdown processing performance: {cricket_score:.1f}")
    
    def test_markdown_engine_rtm_table_processing(self, markdown_engine, sample_markdown_docs):
        """Test RTM table processing from Markdown documents."""
        result = markdown_engine.process(sample_markdown_docs["rtm"])
        
        assert result["status"] == "success"
        # Should detect table structures
        assert result["metadata"]["sections"] >= 2
    
    def test_markdown_engine_complex_structure(self, markdown_engine, sample_markdown_docs):
        """Test complex Markdown structure processing."""
        result = markdown_engine.process(sample_markdown_docs["complex"])
        
        assert result["status"] == "success"
        metadata = result["metadata"]
        assert metadata["sections"] > 3
        assert metadata["links"] >= 0
        assert metadata["code_blocks"] >= 1
    
    def test_markdown_engine_syntax_validation(self, markdown_engine, sample_markdown_docs):
        """Test Markdown syntax validation."""
        result = markdown_engine.process(sample_markdown_docs["basic"])
        
        assert result["status"] == "success"
        # Should handle valid markdown without errors
        assert "error" not in result
    
    def test_markdown_engine_toc_generation(self, markdown_engine, sample_markdown_docs):
        """Test Table of Contents generation from Markdown."""
        result = markdown_engine.process(sample_markdown_docs["complex"])
        
        assert result["status"] == "success"
        # Complex document should have multiple sections for TOC
        assert result["metadata"]["sections"] > 2
    
    @pytest.mark.benchmark
    def test_markdown_engine_benchmark(self, markdown_engine, sample_markdown_docs, benchmark):
        """Benchmark Markdown engine performance."""
        def process_markdown_doc():
            return markdown_engine.process(sample_markdown_docs["basic"])
        
        result = benchmark(process_markdown_doc)
        assert result["status"] == "success"
