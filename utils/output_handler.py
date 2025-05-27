import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Union, Optional

class OutputHandler:
    """Handler for managing output files and logging"""

    def __init__(self, output_dir: str):
        """Initialize the output handler"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Set up logging
        log_file = os.path.join(output_dir, f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("dmaic_workflow")
        self.interaction_history = []

    def log_info(self, message: str):
        """Log informational message"""
        self.logger.info(message)

    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def log_interaction(self, question: str, response: str):
        """Log an interaction with the DMAIC system"""
        self.interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response
        })
        self.logger.info(f"Q: {question[:50]}... | R: {response[:50]}...")

    def save_results(self, results: Dict[str, Any], filename: str) -> str:
        """Save results to a JSON file"""
        output_path = os.path.join(self.output_dir, filename)

        # Add interaction history to results
        full_output = {
            "results": results,
            "interaction_history": self.interaction_history,
            "timestamp": datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            # Handle different file formats
            if filename.endswith('.json'):
                json.dump(full_output, f, indent=2, ensure_ascii=False)
            elif filename.endswith(('.md', '.markdown')):
                f.write(results.get('report_content', str(results)))
            elif filename.endswith('.yml') or filename.endswith('.yaml'):
                import yaml
                yaml.dump(full_output, f, default_flow_style=False)
            else:
                # Default to JSON
                json.dump(full_output, f, indent=2, ensure_ascii=False)

        self.log_info(f"Results saved to {output_path}")
        return output_path
