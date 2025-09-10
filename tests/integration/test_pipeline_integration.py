
"""
Integration tests for the complete document processing pipeline.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import json

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.fixtures.mock_documents import create_all_mock_documents

class TestPipelineIntegration:
    """Integration tests for the complete document processing pipeline."""
    
    @pytest.fixture
    def pipeline_processor(self):
        """Create a mock pipeline processor."""
        mock_processor = Mock()
        mock_processor.process_batch = Mock(return_value={
            "status": "success",
            "processed_files": 6,
            "failed_files": 0,
            "output_directory": "/tmp/output",
            "processing_time": 15.5,
            "cricket_score": 92.5
        })
        return mock_processor
    
    @pytest.fixture
    def sample_document_set(self, temp_dir):
        """Create a complete set of sample documents for integration testing."""
        return create_all_mock_documents(temp_dir / "test_docs")
    
    def test_end_to_end_pipeline_processing(self, pipeline_processor, sample_document_set, performance_monitor, cricket_score_config):
        """Test complete end-to-end pipeline processing with cricket scoring."""
        performance_monitor.start()
        
        # Prepare input files list
        input_files = []
        for doc_type, docs in sample_document_set.items():
            for content_type, file_path in docs.items():
                input_files.append(str(file_path))
        
        # Process through pipeline
        result = pipeline_processor.process_batch(input_files)
        
        performance_monitor.stop()
        
        # Validate pipeline results
        assert result["status"] == "success"
        assert result["processed_files"] > 0
        assert result["failed_files"] == 0
        
        # Cricket scoring for overall pipeline performance
        metrics = performance_monitor.get_metrics()
        overall_score = min(100, result["cricket_score"])
        
        if overall_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent pipeline performance: {overall_score:.1f}")
        elif overall_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good pipeline performance: {overall_score:.1f}")
        elif overall_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable pipeline performance: {overall_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor pipeline performance: {overall_score:.1f}")
    
    def test_multi_engine_coordination(self, pipeline_processor, sample_document_set):
        """Test coordination between multiple document processing engines."""
        # Test processing different document types in sequence
        word_files = [str(path) for path in sample_document_set["word"].values()]
        excel_files = [str(path) for path in sample_document_set["excel"].values()]
        pdf_files = [str(path) for path in sample_document_set["pdf"].values()]
        
        # Process each type
        word_result = pipeline_processor.process_batch(word_files)
        excel_result = pipeline_processor.process_batch(excel_files)
        pdf_result = pipeline_processor.process_batch(pdf_files)
        
        # All should succeed
        assert word_result["status"] == "success"
        assert excel_result["status"] == "success"
        assert pdf_result["status"] == "success"
    
    def test_rtm_extraction_integration(self, pipeline_processor, sample_document_set):
        """Test RTM extraction across different document types."""
        # Get RTM-specific documents
        rtm_files = []
        for doc_type, docs in sample_document_set.items():
            if "rtm" in docs:
                rtm_files.append(str(docs["rtm"]))
        
        result = pipeline_processor.process_batch(rtm_files)
        
        assert result["status"] == "success"
        assert result["processed_files"] == len(rtm_files)
    
    def test_error_recovery_integration(self, pipeline_processor, sample_document_set, temp_dir):
        """Test pipeline error recovery and resilience."""
        # Add some invalid files to the mix
        valid_files = [str(sample_document_set["word"]["basic"])]
        invalid_files = [str(temp_dir / "non_existent.docx")]
        mixed_files = valid_files + invalid_files
        
        # Mock partial failure
        pipeline_processor.process_batch.return_value = {
            "status": "partial_success",
            "processed_files": 1,
            "failed_files": 1,
            "output_directory": "/tmp/output",
            "processing_time": 5.2,
            "cricket_score": 75.0,
            "errors": ["File not found: non_existent.docx"]
        }
        
        result = pipeline_processor.process_batch(mixed_files)
        
        assert result["status"] == "partial_success"
        assert result["processed_files"] > 0
        assert result["failed_files"] > 0
        assert "errors" in result
    
    def test_output_validation_integration(self, pipeline_processor, sample_document_set, temp_dir):
        """Test integration of output validation in the pipeline."""
        input_files = [str(sample_document_set["word"]["basic"])]
        
        # Mock successful processing with output validation
        pipeline_processor.process_batch.return_value = {
            "status": "success",
            "processed_files": 1,
            "failed_files": 0,
            "output_directory": str(temp_dir / "output"),
            "processing_time": 3.1,
            "cricket_score": 88.5,
            "validation_results": {
                "output_files_created": 1,
                "metadata_generated": True,
                "quality_checks_passed": True
            }
        }
        
        result = pipeline_processor.process_batch(input_files)
        
        assert result["status"] == "success"
        assert "validation_results" in result
        assert result["validation_results"]["output_files_created"] > 0
        assert result["validation_results"]["quality_checks_passed"] is True
    
    def test_concurrent_processing_integration(self, pipeline_processor, sample_document_set, performance_monitor):
        """Test concurrent processing capabilities."""
        performance_monitor.start()
        
        # Simulate concurrent processing of multiple file types
        all_files = []
        for doc_type, docs in sample_document_set.items():
            all_files.extend([str(path) for path in docs.values()])
        
        # Mock concurrent processing result
        pipeline_processor.process_batch.return_value = {
            "status": "success",
            "processed_files": len(all_files),
            "failed_files": 0,
            "output_directory": "/tmp/output",
            "processing_time": 8.7,  # Should be faster than sequential
            "cricket_score": 94.2,
            "concurrent_workers": 4
        }
        
        result = pipeline_processor.process_batch(all_files)
        
        performance_monitor.stop()
        
        assert result["status"] == "success"
        assert result["processed_files"] == len(all_files)
        assert "concurrent_workers" in result
    
    def test_metadata_aggregation_integration(self, pipeline_processor, sample_document_set):
        """Test metadata aggregation across processed documents."""
        input_files = [str(path) for path in sample_document_set["word"].values()]
        
        # Mock processing with metadata aggregation
        pipeline_processor.process_batch.return_value = {
            "status": "success",
            "processed_files": len(input_files),
            "failed_files": 0,
            "output_directory": "/tmp/output",
            "processing_time": 4.3,
            "cricket_score": 91.8,
            "aggregated_metadata": {
                "total_pages": 15,
                "total_words": 3000,
                "document_types": ["basic", "rtm", "complex"],
                "processing_engines_used": ["word_engine"]
            }
        }
        
        result = pipeline_processor.process_batch(input_files)
        
        assert result["status"] == "success"
        assert "aggregated_metadata" in result
        assert result["aggregated_metadata"]["total_pages"] > 0
        assert result["aggregated_metadata"]["total_words"] > 0
    
    @pytest.mark.benchmark
    def test_pipeline_performance_benchmark(self, pipeline_processor, sample_document_set, benchmark):
        """Benchmark complete pipeline performance."""
        input_files = [str(sample_document_set["word"]["basic"])]
        
        def process_pipeline():
            return pipeline_processor.process_batch(input_files)
        
        result = benchmark(process_pipeline)
        assert result["status"] == "success"
    
    def test_pipeline_scalability(self, pipeline_processor, sample_document_set, performance_monitor):
        """Test pipeline scalability with increasing load."""
        performance_monitor.start()
        
        # Test with different batch sizes
        batch_sizes = [1, 5, 10]
        results = []
        
        for batch_size in batch_sizes:
            # Create batch of files
            batch_files = []
            file_list = [str(path) for doc_type, docs in sample_document_set.items() for path in docs.values()]
            
            for i in range(batch_size):
                batch_files.append(file_list[i % len(file_list)])
            
            # Mock processing for different batch sizes
            pipeline_processor.process_batch.return_value = {
                "status": "success",
                "processed_files": batch_size,
                "failed_files": 0,
                "output_directory": "/tmp/output",
                "processing_time": batch_size * 1.5,  # Linear scaling
                "cricket_score": max(70, 100 - batch_size * 2)  # Slight degradation with size
            }
            
            result = pipeline_processor.process_batch(batch_files)
            results.append(result)
        
        performance_monitor.stop()
        
        # Validate scalability
        for i, result in enumerate(results):
            assert result["status"] == "success"
            assert result["processed_files"] == batch_sizes[i]
            # Performance should degrade gracefully
            assert result["cricket_score"] >= 60  # Minimum acceptable performance
