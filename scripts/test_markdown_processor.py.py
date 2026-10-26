#!/usr/bin/env python
import sys
import importlib.util
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Import the module with the exact filename
module_path = Path(parent_dir) / "WORD round trip_250520_1519.py"
spec = importlib.util.spec_from_file_location("word_module", module_path)
word_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(word_module)

# Now access the functions
parse_markdown = word_module.parse_markdown
validate_markdown = word_module.validate_markdown
write_json = word_module.write_json
write_yaml = word_module.write_yaml
generate_global_config = word_module.generate_global_config

# Rest of your test code...
