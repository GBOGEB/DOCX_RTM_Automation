#!/usr/bin/env python
# Main entry point for DOCX RTM Automation

import os
import sys
from scripts.run_pipeline import run_pipeline

if __name__ == "__main__":
    # Change working directory to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the pipeline
    print("Starting DOCX RTM Automation pipeline...")
    success = run_pipeline()
    
    sys.exit(0 if success else 1)
