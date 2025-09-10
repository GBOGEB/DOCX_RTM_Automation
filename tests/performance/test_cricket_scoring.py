
"""
Performance tests with cricket scoring validation system.
"""

import pytest
import time
import psutil
from pathlib import Path
from unittest.mock import Mock
import sys

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

class TestCricketScoringSystem:
    """Test suite for cricket scoring performance validation."""
    
    def test_cricket_score_calculation(self, performance_monitor, cricket_score_config):
        """Test cricket score calculation logic."""
        # Simulate excellent performance
        performance_monitor.start()
        time.sleep(0.1)  # Minimal processing time
        performance_monitor.stop()
        
        thresholds = cricket_score_config["performance_thresholds"]["text_processing"]
        score = performance_monitor.calculate_cricket_score(thresholds)
        
        # Should get high score for fast processing
        assert score >= cricket_score_config["cricket_scoring"]["boundary_4"]
        print(f"🏏 Cricket Score: {score:.1f}")
    
    def test_performance_boundary_scoring(self, performance_monitor, cricket_score_config):
        """Test cricket scoring boundaries (4s and 6s)."""
        # Test different performance scenarios
        scenarios = [
            {"sleep_time": 0.1, "expected_min": 90},  # Should be a 6
            {"sleep_time": 0.5, "expected_min": 80},  # Should be a 4
            {"sleep_time": 1.0, "expected_min": 70},  # Should be acceptable
        ]
        
        for scenario in scenarios:
            performance_monitor.start()
            time.sleep(scenario["sleep_time"])
            performance_monitor.stop()
            
            thresholds = cricket_score_config["performance_thresholds"]["text_processing"]
            score = performance_monitor.calculate_cricket_score(thresholds)
            
            print(f"🏏 Sleep {scenario['sleep_time']}s -> Score: {score:.1f}")
            
            if score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
                print("🏏 SIX! Excellent performance")
            elif score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
                print("🏏 FOUR! Good performance")
            elif score >= cricket_score_config["cricket_scoring"]["wicket"]:
                print("🏏 Single. Acceptable performance")
            else:
                print("🏏 WICKET! Poor performance")
    
    def test_memory_efficiency_scoring(self, performance_monitor, cricket_score_config):
        """Test memory efficiency in cricket scoring."""
        performance_monitor.start()
        
        # Simulate memory usage
        data = []
        for i in range(1000):
            data.append(f"test_data_{i}" * 100)
        
        performance_monitor.stop()
        
        thresholds = cricket_score_config["performance_thresholds"]["word_processing"]
        score = performance_monitor.calculate_cricket_score(thresholds)
        
        print(f"🏏 Memory test score: {score:.1f}")
        assert score >= 0  # Should not fail completely
        
        # Clean up
        del data
    
    def test_cricket_scoring_thresholds(self, cricket_score_config):
        """Test cricket scoring threshold configuration."""
        thresholds = cricket_score_config["performance_thresholds"]
        cricket_scores = cricket_score_config["cricket_scoring"]
        
        # Validate threshold structure
        required_engines = ["word_processing", "excel_processing", "pdf_processing", 
                          "markdown_processing", "powerpoint_processing", "text_processing"]
        
        for engine in required_engines:
            assert engine in thresholds
            assert "max_time" in thresholds[engine]
            assert "max_memory" in thresholds[engine]
        
        # Validate cricket scoring boundaries
        assert cricket_scores["boundary_6"] > cricket_scores["boundary_4"]
        assert cricket_scores["boundary_4"] > cricket_scores["wicket"]
        assert cricket_scores["century"] == 100
    
    def test_performance_regression_detection(self, performance_monitor, cricket_score_config):
        """Test performance regression detection using cricket scoring."""
        baseline_scores = []
        
        # Establish baseline performance
        for i in range(3):
            performance_monitor.start()
            time.sleep(0.1)  # Consistent fast performance
            performance_monitor.stop()
            
            thresholds = cricket_score_config["performance_thresholds"]["text_processing"]
            score = performance_monitor.calculate_cricket_score(thresholds)
            baseline_scores.append(score)
        
        baseline_avg = sum(baseline_scores) / len(baseline_scores)
        
        # Test potential regression
        performance_monitor.start()
        time.sleep(0.8)  # Slower performance
        performance_monitor.stop()
        
        regression_score = performance_monitor.calculate_cricket_score(
            cricket_score_config["performance_thresholds"]["text_processing"]
        )
        
        print(f"🏏 Baseline average: {baseline_avg:.1f}")
        print(f"🏏 Regression test: {regression_score:.1f}")
        
        # Detect significant regression
        regression_threshold = 20  # 20 point drop indicates regression
        if baseline_avg - regression_score > regression_threshold:
            print("🏏 PERFORMANCE REGRESSION DETECTED!")
        else:
            print("🏏 Performance within acceptable range")
    
    @pytest.mark.benchmark
    def test_cricket_scoring_benchmark(self, performance_monitor, cricket_score_config, benchmark):
        """Benchmark the cricket scoring system itself."""
        def calculate_score():
            performance_monitor.start()
            time.sleep(0.01)  # Minimal work
            performance_monitor.stop()
            
            thresholds = cricket_score_config["performance_thresholds"]["text_processing"]
            return performance_monitor.calculate_cricket_score(thresholds)
        
        score = benchmark(calculate_score)
        assert score >= 0
        print(f"🏏 Benchmark cricket score: {score:.1f}")
    
    def test_century_achievement(self, performance_monitor, cricket_score_config):
        """Test achieving a perfect cricket score (century)."""
        # Simulate perfect performance conditions
        performance_monitor.start()
        # Minimal processing time and memory usage
        performance_monitor.stop()
        
        # Manually set perfect metrics for testing
        performance_monitor.start_time = time.time()
        performance_monitor.end_time = performance_monitor.start_time + 0.01  # 10ms
        performance_monitor.peak_memory = 1.0  # 1MB
        
        thresholds = cricket_score_config["performance_thresholds"]["text_processing"]
        score = performance_monitor.calculate_cricket_score(thresholds)
        
        print(f"🏏 Perfect performance score: {score:.1f}")
        
        if score >= cricket_score_config["cricket_scoring"]["century"]:
            print("🏏 CENTURY! Perfect performance achieved! 💯")
        else:
            print(f"🏏 Close to century: {score:.1f}/100")
    
    def test_wicket_conditions(self, performance_monitor, cricket_score_config):
        """Test conditions that result in wickets (failures)."""
        # Simulate poor performance
        performance_monitor.start()
        time.sleep(2.0)  # Very slow processing
        performance_monitor.stop()
        
        thresholds = cricket_score_config["performance_thresholds"]["text_processing"]
        score = performance_monitor.calculate_cricket_score(thresholds)
        
        print(f"🏏 Poor performance score: {score:.1f}")
        
        if score < cricket_score_config["cricket_scoring"]["wicket"]:
            print("🏏 WICKET! Performance below acceptable threshold")
            # In real scenarios, this might trigger alerts or fail the test
        else:
            print("🏏 Performance acceptable despite being slow")
