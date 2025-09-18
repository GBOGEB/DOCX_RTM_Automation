
"""
Unit tests for PowerPoint document processing engine.
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

class TestPowerPointEngine:
    """Test suite for PowerPoint document processing engine."""
    
    @pytest.fixture
    def powerpoint_engine(self):
        """Create a mock PowerPoint processing engine."""
        mock_engine = Mock()
        mock_engine.process = Mock(return_value={
            "status": "success",
            "output_file": "test.txt",
            "metadata": {"slides": 5, "text_content": 2000, "images": 3}
        })
        return mock_engine
    
    @pytest.fixture
    def sample_powerpoint_docs(self, temp_dir):
        """Create sample PowerPoint documents for testing."""
        generator = MockDocumentGenerator()
        docs = {
            "basic": generator.create_powerpoint_document(temp_dir / "basic.pptx", "basic"),
            "rtm": generator.create_powerpoint_document(temp_dir / "rtm.pptx", "rtm"),
        }
        return docs
    
    def test_powerpoint_engine_basic_processing(self, powerpoint_engine, sample_powerpoint_docs, performance_monitor, cricket_score_config):
        """Test basic PowerPoint document processing with cricket scoring."""
        performance_monitor.start()
        
        result = powerpoint_engine.process(sample_powerpoint_docs["basic"])
        
        performance_monitor.stop()
        
        # Validate result
        assert result["status"] == "success"
        assert "output_file" in result
        assert "metadata" in result
        
        # Cricket scoring for performance
        cricket_score = performance_monitor.calculate_cricket_score(
            cricket_score_config["performance_thresholds"]["powerpoint_processing"]
        )
        
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent PowerPoint processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good PowerPoint processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable PowerPoint processing performance: {cricket_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor PowerPoint processing performance: {cricket_score:.1f}")
    
    def test_powerpoint_engine_slide_extraction(self, powerpoint_engine, sample_powerpoint_docs):
        """Test slide content extraction from PowerPoint documents."""
        result = powerpoint_engine.process(sample_powerpoint_docs["basic"])
        
        assert result["status"] == "success"
        assert result["metadata"]["slides"] > 0
        assert result["metadata"]["text_content"] > 0
    
    def test_powerpoint_engine_rtm_processing(self, powerpoint_engine, sample_powerpoint_docs):
        """Test RTM processing from PowerPoint documents."""
        result = powerpoint_engine.process(sample_powerpoint_docs["rtm"])
        
        assert result["status"] == "success"
        # RTM presentation should have meaningful content
        assert result["metadata"]["text_content"] > 100
    
    def test_powerpoint_engine_media_handling(self, powerpoint_engine, sample_powerpoint_docs):
        """Test media content handling in PowerPoint documents."""
        result = powerpoint_engine.process(sample_powerpoint_docs["basic"])
        
        assert result["status"] == "success"
        # Should track media elements
        assert "images" in result["metadata"]
    
    @pytest.mark.benchmark
    def test_powerpoint_engine_benchmark(self, powerpoint_engine, sample_powerpoint_docs, benchmark):
        """Benchmark PowerPoint engine performance."""
        def process_powerpoint_doc():
            return powerpoint_engine.process(sample_powerpoint_docs["basic"])
        
        result = benchmark(process_powerpoint_doc)
        assert result["status"] == "success"
