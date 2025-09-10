
"""
Pytest configuration and fixtures for the document processing ecosystem.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Return the project root path."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir(project_root_path: Path) -> Path:
    """Return the test data directory."""
    return project_root_path / "tests" / "fixtures"

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def mock_input_dir(temp_dir: Path) -> Path:
    """Create a mock input directory structure."""
    input_dir = temp_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    return input_dir

@pytest.fixture
def mock_output_dir(temp_dir: Path) -> Path:
    """Create a mock output directory structure."""
    output_dir = temp_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture
def cricket_score_config() -> Dict[str, Any]:
    """Cricket scoring configuration for performance validation."""
    return {
        "performance_thresholds": {
            "word_processing": {"max_time": 5.0, "max_memory": 100},  # seconds, MB
            "excel_processing": {"max_time": 3.0, "max_memory": 80},
            "pdf_processing": {"max_time": 8.0, "max_memory": 150},
            "markdown_processing": {"max_time": 1.0, "max_memory": 50},
            "powerpoint_processing": {"max_time": 4.0, "max_memory": 120},
            "text_processing": {"max_time": 0.5, "max_memory": 30},
        },
        "quality_gates": {
            "min_coverage": 85,
            "max_complexity": 10,
            "max_line_length": 88,
            "min_test_score": 90,
        },
        "cricket_scoring": {
            "boundary_4": 85,  # Good performance threshold
            "boundary_6": 95,  # Excellent performance threshold
            "wicket": 70,      # Failure threshold
            "century": 100,    # Perfect score
        }
    }

@pytest.fixture
def mock_document_engines():
    """Mock document processing engines for testing."""
    engines = {}
    
    # Mock Word engine
    word_engine = Mock()
    word_engine.process.return_value = {
        "status": "success",
        "output_file": "test.md",
        "metadata": {"pages": 5, "words": 1000}
    }
    engines["word"] = word_engine
    
    # Mock Excel engine
    excel_engine = Mock()
    excel_engine.process.return_value = {
        "status": "success", 
        "output_file": "test.csv",
        "metadata": {"sheets": 3, "rows": 100}
    }
    engines["excel"] = excel_engine
    
    # Mock PDF engine
    pdf_engine = Mock()
    pdf_engine.process.return_value = {
        "status": "success",
        "output_file": "test.txt", 
        "metadata": {"pages": 10, "size": "2MB"}
    }
    engines["pdf"] = pdf_engine
    
    return engines

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DISABLE_EXTERNAL_CALLS", "true")

@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture for cricket scoring."""
    import time
    import psutil
    import threading
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.peak_memory = 0
            self.monitoring = False
            self.monitor_thread = None
            
        def start(self):
            self.start_time = time.time()
            self.peak_memory = 0
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_memory)
            self.monitor_thread.start()
            
        def stop(self):
            self.end_time = time.time()
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()
                
        def _monitor_memory(self):
            process = psutil.Process()
            while self.monitoring:
                try:
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.peak_memory = max(self.peak_memory, memory_mb)
                    time.sleep(0.1)
                except:
                    break
                    
        def get_metrics(self):
            duration = (self.end_time - self.start_time) if self.end_time else 0
            return {
                "duration": duration,
                "peak_memory_mb": self.peak_memory
            }
            
        def calculate_cricket_score(self, thresholds):
            metrics = self.get_metrics()
            time_score = 100 if metrics["duration"] <= thresholds["max_time"] else max(0, 100 - (metrics["duration"] - thresholds["max_time"]) * 10)
            memory_score = 100 if metrics["peak_memory_mb"] <= thresholds["max_memory"] else max(0, 100 - (metrics["peak_memory_mb"] - thresholds["max_memory"]) * 2)
            return min(100, (time_score + memory_score) / 2)
    
    return PerformanceMonitor()
