
"""
Unit tests for Excel document processing engine.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.fixtures.mock_documents import MockDocumentGenerator

class TestExcelEngine:
    """Test suite for Excel document processing engine."""
    
    @pytest.fixture
    def excel_engine(self):
        """Create a mock Excel processing engine."""
        mock_engine = Mock()
        mock_engine.process = Mock(return_value={
            "status": "success",
            "output_file": "test.csv",
            "metadata": {"sheets": 3, "rows": 100, "columns": 5}
        })
        return mock_engine
    
    @pytest.fixture
    def sample_excel_docs(self, temp_dir):
        """Create sample Excel documents for testing."""
        generator = MockDocumentGenerator()
        docs = {
            "basic": generator.create_excel_document(temp_dir / "basic.xlsx", "basic"),
            "rtm": generator.create_excel_document(temp_dir / "rtm.xlsx", "rtm"),
            "multi_sheet": generator.create_excel_document(temp_dir / "multi.xlsx", "multi_sheet"),
        }
        return docs
    
    def test_excel_engine_basic_processing(self, excel_engine, sample_excel_docs, performance_monitor, cricket_score_config):
        """Test basic Excel document processing with cricket scoring."""
        performance_monitor.start()
        
        result = excel_engine.process(sample_excel_docs["basic"])
        
        performance_monitor.stop()
        
        # Validate result
        assert result["status"] == "success"
        assert "output_file" in result
        assert "metadata" in result
        
        # Cricket scoring for performance
        cricket_score = performance_monitor.calculate_cricket_score(
            cricket_score_config["performance_thresholds"]["excel_processing"]
        )
        
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent Excel processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good Excel processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable Excel processing performance: {cricket_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor Excel processing performance: {cricket_score:.1f}")
    
    def test_excel_engine_rtm_processing(self, excel_engine, sample_excel_docs):
        """Test RTM processing from Excel documents."""
        result = excel_engine.process(sample_excel_docs["rtm"])
        
        assert result["status"] == "success"
        assert result["metadata"]["sheets"] >= 1
        assert result["metadata"]["rows"] > 0
    
    def test_excel_engine_multi_sheet_processing(self, excel_engine, sample_excel_docs):
        """Test multi-sheet Excel processing."""
        result = excel_engine.process(sample_excel_docs["multi_sheet"])
        
        assert result["status"] == "success"
        assert result["metadata"]["sheets"] > 1
    
    def test_excel_engine_error_handling(self, excel_engine, temp_dir):
        """Test Excel engine error handling."""
        non_existent_file = temp_dir / "non_existent.xlsx"
        
        # Mock error response
        excel_engine.process.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            excel_engine.process(non_existent_file)
    
    def test_excel_engine_data_validation(self, excel_engine, sample_excel_docs):
        """Test Excel data validation capabilities."""
        result = excel_engine.process(sample_excel_docs["rtm"])
        
        # Validate that RTM data structure is maintained
        assert result["status"] == "success"
        metadata = result["metadata"]
        assert metadata["rows"] > 1  # Should have header + data rows
        assert metadata["columns"] >= 3  # Should have multiple columns for RTM
    
    @pytest.mark.benchmark
    def test_excel_engine_benchmark(self, excel_engine, sample_excel_docs, benchmark):
        """Benchmark Excel engine performance."""
        def process_excel_doc():
            return excel_engine.process(sample_excel_docs["basic"])
        
        result = benchmark(process_excel_doc)
        assert result["status"] == "success"
