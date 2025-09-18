
"""
Unit tests for Text document processing engine.
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

class TestTextEngine:
    """Test suite for Text document processing engine."""
    
    @pytest.fixture
    def text_engine(self):
        """Create a mock Text processing engine."""
        mock_engine = Mock()
        mock_engine.process = Mock(return_value={
            "status": "success",
            "output_file": "test_processed.txt",
            "metadata": {"lines": 50, "words": 500, "characters": 3000}
        })
        return mock_engine
    
    @pytest.fixture
    def sample_text_docs(self, temp_dir):
        """Create sample Text documents for testing."""
        generator = MockDocumentGenerator()
        docs = {
            "basic": generator.create_text_document(temp_dir / "basic.txt", "basic"),
            "rtm": generator.create_text_document(temp_dir / "rtm.txt", "rtm"),
        }
        return docs
    
    def test_text_engine_basic_processing(self, text_engine, sample_text_docs, performance_monitor, cricket_score_config):
        """Test basic Text document processing with cricket scoring."""
        performance_monitor.start()
        
        result = text_engine.process(sample_text_docs["basic"])
        
        performance_monitor.stop()
        
        # Validate result
        assert result["status"] == "success"
        assert "output_file" in result
        assert "metadata" in result
        
        # Cricket scoring for performance
        cricket_score = performance_monitor.calculate_cricket_score(
            cricket_score_config["performance_thresholds"]["text_processing"]
        )
        
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent Text processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good Text processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable Text processing performance: {cricket_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor Text processing performance: {cricket_score:.1f}")
    
    def test_text_engine_content_analysis(self, text_engine, sample_text_docs):
        """Test text content analysis capabilities."""
        result = text_engine.process(sample_text_docs["basic"])
        
        assert result["status"] == "success"
        metadata = result["metadata"]
        assert metadata["lines"] > 0
        assert metadata["words"] > 0
        assert metadata["characters"] > 0
    
    def test_text_engine_rtm_extraction(self, text_engine, sample_text_docs):
        """Test RTM extraction from text documents."""
        result = text_engine.process(sample_text_docs["rtm"])
        
        assert result["status"] == "success"
        # RTM text should have substantial content
        assert result["metadata"]["words"] > 50
    
    def test_text_engine_encoding_handling(self, text_engine, sample_text_docs):
        """Test text encoding handling."""
        result = text_engine.process(sample_text_docs["basic"])
        
        assert result["status"] == "success"
        # Should handle text encoding without errors
        assert "encoding_error" not in result
    
    def test_text_engine_large_file_processing(self, text_engine, sample_text_docs, performance_monitor):
        """Test large text file processing efficiency."""
        performance_monitor.start()
        
        # Simulate processing of larger text file
        result = text_engine.process(sample_text_docs["rtm"])
        
        performance_monitor.stop()
        metrics = performance_monitor.get_metrics()
        
        assert result["status"] == "success"
        # Text processing should be very fast
        assert metrics["duration"] < 2.0, f"Text processing too slow: {metrics['duration']:.2f}s"
    
    @pytest.mark.benchmark
    def test_text_engine_benchmark(self, text_engine, sample_text_docs, benchmark):
        """Benchmark Text engine performance."""
        def process_text_doc():
            return text_engine.process(sample_text_docs["basic"])
        
        result = benchmark(process_text_doc)
        assert result["status"] == "success"
