
"""
Load testing for document processing system.
"""

import pytest
import concurrent.futures
import time
from pathlib import Path
from unittest.mock import Mock
import sys

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.fixtures.mock_documents import create_all_mock_documents

class TestLoadTesting:
    """Load testing suite for document processing system."""
    
    @pytest.fixture
    def load_test_processor(self):
        """Create a mock processor for load testing."""
        mock_processor = Mock()
        
        def mock_process(file_path, delay=0.1):
            time.sleep(delay)  # Simulate processing time
            return {
                "status": "success",
                "file": str(file_path),
                "processing_time": delay,
                "memory_used": 50  # MB
            }
        
        mock_processor.process = mock_process
        return mock_processor
    
    @pytest.fixture
    def load_test_documents(self, temp_dir):
        """Create documents for load testing."""
        return create_all_mock_documents(temp_dir / "load_test_docs")
    
    def test_concurrent_processing_load(self, load_test_processor, load_test_documents, performance_monitor, cricket_score_config):
        """Test system under concurrent processing load."""
        performance_monitor.start()
        
        # Prepare files for concurrent processing
        all_files = []
        for doc_type, docs in load_test_documents.items():
            all_files.extend(docs.values())
        
        # Process files concurrently
        max_workers = 4
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(load_test_processor.process, file_path, 0.1): file_path 
                for file_path in all_files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'File {file_path} generated an exception: {exc}')
        
        performance_monitor.stop()
        
        # Validate concurrent processing results
        assert len(results) == len(all_files)
        successful_results = [r for r in results if r["status"] == "success"]
        assert len(successful_results) == len(all_files)
        
        # Cricket scoring for concurrent load
        metrics = performance_monitor.get_metrics()
        # Adjust thresholds for concurrent processing
        concurrent_thresholds = {
            "max_time": cricket_score_config["performance_thresholds"]["word_processing"]["max_time"] * 2,
            "max_memory": cricket_score_config["performance_thresholds"]["word_processing"]["max_memory"] * max_workers
        }
        
        cricket_score = performance_monitor.calculate_cricket_score(concurrent_thresholds)
        
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good concurrent processing performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable concurrent performance: {cricket_score:.1f}")
        else:
            pytest.fail(f"🏏 WICKET! Poor concurrent performance: {cricket_score:.1f}")
    
    def test_high_volume_processing(self, load_test_processor, load_test_documents, performance_monitor):
        """Test processing high volume of documents."""
        performance_monitor.start()
        
        # Create a large batch of files (simulate by processing same files multiple times)
        base_files = list(load_test_documents["word"].values())
        high_volume_batch = base_files * 10  # 10x multiplier for volume testing
        
        results = []
        batch_size = 5
        
        # Process in batches to simulate real-world scenarios
        for i in range(0, len(high_volume_batch), batch_size):
            batch = high_volume_batch[i:i+batch_size]
            batch_results = []
            
            for file_path in batch:
                result = load_test_processor.process(file_path, 0.05)  # Faster processing for volume
                batch_results.append(result)
            
            results.extend(batch_results)
        
        performance_monitor.stop()
        
        # Validate high volume processing
        assert len(results) == len(high_volume_batch)
        successful_results = [r for r in results if r["status"] == "success"]
        success_rate = len(successful_results) / len(results) * 100
        
        print(f"🏏 High volume processing success rate: {success_rate:.1f}%")
        assert success_rate >= 95, f"Success rate too low: {success_rate:.1f}%"
        
        # Performance validation
        metrics = performance_monitor.get_metrics()
        print(f"🏏 High volume processing time: {metrics['duration']:.2f}s for {len(high_volume_batch)} files")
        
        # Should maintain reasonable throughput
        throughput = len(high_volume_batch) / metrics['duration']
        print(f"🏏 Throughput: {throughput:.1f} files/second")
        assert throughput >= 5, f"Throughput too low: {throughput:.1f} files/second"
    
    def test_memory_pressure_handling(self, load_test_processor, load_test_documents, performance_monitor):
        """Test system behavior under memory pressure."""
        performance_monitor.start()
        
        # Simulate memory-intensive processing
        def memory_intensive_process(file_path):
            # Simulate higher memory usage
            result = load_test_processor.process(file_path, 0.2)
            result["memory_used"] = 200  # Simulate high memory usage
            return result
        
        files_to_process = list(load_test_documents["pdf"].values())  # PDFs typically use more memory
        results = []
        
        for file_path in files_to_process:
            result = memory_intensive_process(file_path)
            results.append(result)
        
        performance_monitor.stop()
        
        # Validate memory pressure handling
        assert len(results) == len(files_to_process)
        total_memory_used = sum(r["memory_used"] for r in results)
        
        print(f"🏏 Total memory used: {total_memory_used}MB")
        
        # System should handle memory pressure gracefully
        metrics = performance_monitor.get_metrics()
        print(f"🏏 Peak memory during pressure test: {metrics['peak_memory_mb']:.1f}MB")
        
        # Should not exceed reasonable limits
        assert metrics['peak_memory_mb'] <= 1000, f"Memory usage too high: {metrics['peak_memory_mb']:.1f}MB"
    
    def test_sustained_load_processing(self, load_test_processor, load_test_documents, performance_monitor):
        """Test sustained load processing over time."""
        performance_monitor.start()
        
        # Simulate sustained processing over multiple iterations
        iterations = 5
        files_per_iteration = list(load_test_documents["text"].values())  # Use fast-processing text files
        
        iteration_results = []
        
        for iteration in range(iterations):
            iteration_start = time.time()
            
            batch_results = []
            for file_path in files_per_iteration:
                result = load_test_processor.process(file_path, 0.1)
                batch_results.append(result)
            
            iteration_end = time.time()
            iteration_time = iteration_end - iteration_start
            
            iteration_results.append({
                "iteration": iteration + 1,
                "processing_time": iteration_time,
                "files_processed": len(batch_results),
                "success_count": len([r for r in batch_results if r["status"] == "success"])
            })
            
            print(f"🏏 Iteration {iteration + 1}: {iteration_time:.2f}s, {len(batch_results)} files")
        
        performance_monitor.stop()
        
        # Validate sustained performance
        avg_iteration_time = sum(r["processing_time"] for r in iteration_results) / len(iteration_results)
        total_files = sum(r["files_processed"] for r in iteration_results)
        total_success = sum(r["success_count"] for r in iteration_results)
        
        print(f"🏏 Average iteration time: {avg_iteration_time:.2f}s")
        print(f"🏏 Total files processed: {total_files}")
        print(f"🏏 Overall success rate: {(total_success/total_files)*100:.1f}%")
        
        # Performance should remain consistent across iterations
        iteration_times = [r["processing_time"] for r in iteration_results]
        time_variance = max(iteration_times) - min(iteration_times)
        
        print(f"🏏 Time variance across iterations: {time_variance:.2f}s")
        assert time_variance <= avg_iteration_time * 0.5, "Performance degraded significantly over time"
        
        # Success rate should remain high
        assert (total_success/total_files) >= 0.95, "Success rate degraded during sustained load"
    
    def test_resource_cleanup_under_load(self, load_test_processor, load_test_documents, performance_monitor):
        """Test resource cleanup under load conditions."""
        performance_monitor.start()
        
        initial_memory = performance_monitor.peak_memory
        
        # Process multiple batches and ensure cleanup
        for batch_num in range(3):
            batch_files = list(load_test_documents["word"].values())
            
            batch_results = []
            for file_path in batch_files:
                result = load_test_processor.process(file_path, 0.1)
                batch_results.append(result)
            
            # Simulate cleanup between batches
            time.sleep(0.1)
            
            print(f"🏏 Batch {batch_num + 1} completed: {len(batch_results)} files")
        
        performance_monitor.stop()
        
        # Validate resource cleanup
        final_memory = performance_monitor.peak_memory
        memory_growth = final_memory - initial_memory if initial_memory > 0 else final_memory
        
        print(f"🏏 Memory growth during load test: {memory_growth:.1f}MB")
        
        # Memory growth should be reasonable (not indicating memory leaks)
        assert memory_growth <= 200, f"Excessive memory growth: {memory_growth:.1f}MB"
    
    @pytest.mark.benchmark
    def test_load_testing_benchmark(self, load_test_processor, load_test_documents, benchmark):
        """Benchmark load testing scenarios."""
        files_to_process = list(load_test_documents["markdown"].values())
        
        def process_load_batch():
            results = []
            for file_path in files_to_process:
                result = load_test_processor.process(file_path, 0.05)
                results.append(result)
            return results
        
        results = benchmark(process_load_batch)
        assert len(results) == len(files_to_process)
        assert all(r["status"] == "success" for r in results)
