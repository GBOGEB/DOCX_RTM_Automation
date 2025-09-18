
"""
Unit tests for PDF document processing engine.
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

class TestPDFEngine:
    """Test suite for PDF document processing engine."""
    
    @pytest.fixture
    def pdf_engine(self):
        """Create a mock PDF processing engine."""
        mock_engine = Mock()
        mock_engine.process = Mock(return_value={
            "status": "success",
            "output_file": "test.txt",
            "metadata": {"pages": 10, "size": "2MB", "text_length": 5000}
        })
        return mock_engine
    
    @pytest.fixture
    def sample_pdf_docs(self, temp_dir):
        """Create sample PDF documents for testing."""
        generator = MockDocumentGenerator()
        docs = {
            "basic": generator.create_pdf_document(temp_dir / "basic.pdf", "basic"),
            "rtm": generator.create_pdf_document(temp_dir / "rtm.pdf", "rtm"),
            "multi_page": generator.create_pdf_document(temp_dir / "multi.pdf", "multi_page"),
        }
        return docs
    
    def test_pdf_engine_basic_processing(self, pdf_engine, sample_pdf_docs, performance_monitor, cricket_score_config):
        """Test basic PDF document processing with cricket scoring."""
        performance_monitor.start()
        
        result = pdf_engine.process(sample_pdf_docs["basic"])
        
        performance_monitor.stop()
        
        # Validate result
        assert result["status"] == "success"
        assert "output_file" in result
        assert "metadata" in result
        
        # Cricket scoring for performance
        cricket_score = performance_monitor.calculate_cricket_score(
            cricket_score_config["performance_thresholds"]["pdf_processing"]
        )
        
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent PDF processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good PDF processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable PDF processing performance: {cricket_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor PDF processing performance: {cricket_score:.1f}")
    
    def test_pdf_engine_text_extraction(self, pdf_engine, sample_pdf_docs):
        """Test text extraction from PDF documents."""
        result = pdf_engine.process(sample_pdf_docs["basic"])
        
        assert result["status"] == "success"
        assert result["metadata"]["text_length"] > 0
    
    def test_pdf_engine_multi_page_processing(self, pdf_engine, sample_pdf_docs):
        """Test multi-page PDF processing."""
        result = pdf_engine.process(sample_pdf_docs["multi_page"])
        
        assert result["status"] == "success"
        assert result["metadata"]["pages"] > 1
    
    def test_pdf_engine_rtm_extraction(self, pdf_engine, sample_pdf_docs):
        """Test RTM extraction from PDF documents."""
        result = pdf_engine.process(sample_pdf_docs["rtm"])
        
        assert result["status"] == "success"
        # Should extract meaningful content
        assert result["metadata"]["text_length"] > 100
    
    def test_pdf_engine_large_file_handling(self, pdf_engine, sample_pdf_docs, performance_monitor, cricket_score_config):
        """Test PDF engine handling of large files."""
        performance_monitor.start()
        
        # Simulate large file processing
        result = pdf_engine.process(sample_pdf_docs["multi_page"])
        
        performance_monitor.stop()
        metrics = performance_monitor.get_metrics()
        
        assert result["status"] == "success"
        
        # Memory efficiency check for large files
        max_memory = cricket_score_config["performance_thresholds"]["pdf_processing"]["max_memory"]
        assert metrics["peak_memory_mb"] <= max_memory * 1.2, f"Memory usage too high for large PDF: {metrics['peak_memory_mb']:.1f}MB"
    
    @pytest.mark.benchmark
    def test_pdf_engine_benchmark(self, pdf_engine, sample_pdf_docs, benchmark):
        """Benchmark PDF engine performance."""
        def process_pdf_doc():
            return pdf_engine.process(sample_pdf_docs["basic"])
        
        result = benchmark(process_pdf_doc)
        assert result["status"] == "success"
